"""
Endpoints de notre api
"""
from datetime import datetime
from sqlalchemy.orm import Session, joinedload, load_only
from sqlalchemy import func, DateTime
from app.models.models_enmarche import AdherentMessages, Adherents, CandidateManagedArea
from app.models.models_enmarche import MailChimpCampaign, MailChimpCampaignReport
from app.models.models_enmarche import GeoZone


async def get_candidate_reports(
    db: Session,
    zone: GeoZone,
    since: DateTime = datetime(2021, 3, 1)):

    return db.query(MailChimpCampaign) \
        .join(MailChimpCampaign.message) \
        .filter(AdherentMessages.status == 'sent') \
        .filter(AdherentMessages.type.in_(['candidate', 'candidate_jecoute'])) \
        .filter(AdherentMessages.sent_at >= since) \
        .join(MailChimpCampaign.report) \
        .options(joinedload(MailChimpCampaign.message)) \
        .options(joinedload(MailChimpCampaign.report)) \
        .join(AdherentMessages.author) \
        .join(Adherents.candidate_managed_area.and_(CandidateManagedArea.zone_id == zone.id)) \
        .order_by(AdherentMessages.sent_at.desc()) \
        .all()

async def get_mail_ratios(
    db: Session,
    zone: GeoZone,
    since: DateTime = datetime(2021, 3, 1)):

    res = db.query(func.count(MailChimpCampaign.id).label('nb_campagnes'), \
            (func.sum(MailChimpCampaignReport.open_unique) / func.sum(MailChimpCampaignReport.email_sent)).label('taux_ouverture'), \
            (func.sum(MailChimpCampaignReport.unsubscribed) / func.sum(MailChimpCampaignReport.email_sent)).label('taux_désabonnement')) \
        .select_from(MailChimpCampaignReport) \
        .join(MailChimpCampaignReport.mailchimp_campaign) \
        .join(MailChimpCampaign.message.and_( \
            AdherentMessages.type.in_(['candidate', 'candidate_jecoute']), \
            AdherentMessages.sent_at >= since)) \
        .join(AdherentMessages.author) \
        .join(Adherents.candidate_managed_area.and_(CandidateManagedArea.zone_id == zone.id)) \
        .first()

    nat = db.query(
            (func.sum(MailChimpCampaignReport.open_unique) / func.sum(MailChimpCampaignReport.email_sent)).label('taux_ouverture_nat'), \
            (func.sum(MailChimpCampaignReport.unsubscribed) / func.sum(MailChimpCampaignReport.email_sent)).label('taux_désabonnement_nat')) \
        .select_from(MailChimpCampaignReport) \
        .join(MailChimpCampaignReport.mailchimp_campaign) \
        .join(MailChimpCampaign.message.and_( \
            AdherentMessages.type.in_(['candidate', 'candidate_jecoute']))) \
        .first()

    return (res, nat)