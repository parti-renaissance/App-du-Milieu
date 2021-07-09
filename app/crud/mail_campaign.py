"""
Endpoints de notre api
"""
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session, Query
from sqlalchemy import func
from sqlalchemy.sql.functions import coalesce
from app.crud.enmarche import get_child
from app.models.models_enmarche import AdherentMessages, Adherents, CandidateManagedArea
from app.models.models_enmarche import AdherentMessageFilters, ReferentTags, ReferentManagedAreasTags
from app.models.models_enmarche import MailChimpCampaign, MailChimpCampaignReport
from app.models.models_enmarche import GeoZone


def filter_role(
    db: Session,
    query: Query,
    zones: List[GeoZone],
    role: str):
    all_zones = [[zone.id] + [child.id for child in get_child(db, zone)] for zone in zones]
    all_zones = [item for sublist in all_zones for item in sublist]
    
    if role == 'referent':
        return query.join(Adherents.managed_area) \
            .join(ReferentManagedAreasTags.referent_tag) \
            .join(ReferentTags.zone.and_(GeoZone.id.in_(all_zones)))

    if role in ['deputy', 'senator']:
        return query.join(AdherentMessages.filter) \
            .join(AdherentMessageFilters.referent_tag) \
            .join(ReferentTags.zone.and_(GeoZone.id.in_(all_zones)))
            
    if role == 'candidate':
        return query.join(AdherentMessages.filter) \
            .join(AdherentMessageFilters.zone.and_(GeoZone.id.in_(all_zones)))
    return query


async def get_campaign_reports(
    db: Session,
    zone: GeoZone,
    since: datetime,
    role: str):

    query = db.query(
            MailChimpCampaign.id.label('id'), \
            AdherentMessages.sent_at.label('date'), \
            (Adherents.first_name + ' ' + Adherents.last_name).label('auteur'), \
            AdherentMessages.subject.label('titre'), \
            MailChimpCampaignReport.email_sent.label('nbEmails'), \
            MailChimpCampaignReport.open_unique.label('nbOuvertures'), \
            func.round(MailChimpCampaignReport.open_unique / MailChimpCampaignReport.email_sent, 4).label('txOuverture'), \
            MailChimpCampaignReport.click_unique.label('nbCliques'), \
            func.round(MailChimpCampaignReport.click_unique / MailChimpCampaignReport.email_sent, 4).label('txClique'), \
            MailChimpCampaignReport.unsubscribed.label('nbDesabonnements'), \
            func.round(MailChimpCampaignReport.unsubscribed / MailChimpCampaignReport.email_sent, 4).label('txDesabonnement')) \
        .join(MailChimpCampaign.message) \
        .filter(AdherentMessages.status == 'sent') \
        .filter(AdherentMessages.type == role) \
        .filter(AdherentMessages.sent_at >= since) \
        .join(MailChimpCampaign.report) \
        .join(AdherentMessages.author)
    
    query = filter_role(db, query, [zone], role)

    return {
        'zone': zone.name,
        'depuis': since,
        'campagnes': query.order_by(AdherentMessages.sent_at.desc()).all()
    }


async def get_mail_ratios(
    db: Session,
    scope: dict,
    since: datetime):

    query = db.query(func.count(MailChimpCampaign.id).label('nbCampagnes'), \
            coalesce(func.round(func.sum(MailChimpCampaignReport.open_unique) / func.sum(MailChimpCampaignReport.email_sent), 4), 0).label('txOuverture'), \
            coalesce(func.round(func.sum(MailChimpCampaignReport.click_unique) / func.sum(MailChimpCampaignReport.email_sent), 4), 0).label('txClique'), \
            coalesce(func.round(func.sum(MailChimpCampaignReport.unsubscribed) / func.sum(MailChimpCampaignReport.email_sent), 4), 0).label('txDesabonnement')) \
        .select_from(MailChimpCampaignReport) \
        .join(MailChimpCampaignReport.mailchimp_campaign) \
        .join(MailChimpCampaign.message.and_( \
            AdherentMessages.type == scope['code'], \
            AdherentMessages.sent_at >= since)) \
        .join(AdherentMessages.author)
    
    res = filter_role(db, query, scope['zones'], scope['code']).first()

    nat = db.query(
            func.round(func.sum(MailChimpCampaignReport.open_unique) / func.sum(MailChimpCampaignReport.email_sent), 4).label('txOuverture'), \
            func.round(func.sum(MailChimpCampaignReport.click_unique) / func.sum(MailChimpCampaignReport.email_sent), 4).label('txClique'), \
            func.round(func.sum(MailChimpCampaignReport.unsubscribed) / func.sum(MailChimpCampaignReport.email_sent), 4).label('txDesabonnement')) \
        .select_from(MailChimpCampaignReport) \
        .join(MailChimpCampaignReport.mailchimp_campaign) \
        .join(MailChimpCampaign.message.and_( \
            AdherentMessages.type == scope['code'])) \
        .first()

    return {'local': res, 'national': nat}
