"""
Endpoints de notre api
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from sqlalchemy import func
from app.models.models_enmarche import AdherentMessages, Adherents, CandidateManagedArea
from app.models.models_enmarche import MailChimpCampaign, MailChimpCampaignReport
from app.models.models_enmarche import GeoZone


async def get_candidate_reports(
        db: Session,
        zone: GeoZone,
        since: datetime):

    return {
        'zone': zone.name,
        'depuis': since,
        'campagnes': db.query(
            MailChimpCampaign.id.label('id'),
            AdherentMessages.sent_at.label('date'),
            (Adherents.first_name + ' ' + Adherents.last_name).label('auteur'),
            AdherentMessages.subject.label('titre'),
            MailChimpCampaignReport.email_sent.label('nbEmails'),
            MailChimpCampaignReport.open_unique.label('nbOuvertures'),
            func.round(
                MailChimpCampaignReport.open_unique / MailChimpCampaignReport.email_sent,
                4).label('txOuverture'),
            MailChimpCampaignReport.click_unique.label('nbCliques'),
            func.round(
                MailChimpCampaignReport.click_unique / MailChimpCampaignReport.email_sent,
                4).label('txClique'),
            MailChimpCampaignReport.unsubscribed.label('nbDesabonnements'),
            func.round(
                    MailChimpCampaignReport.unsubscribed / MailChimpCampaignReport.email_sent,
                    4).label('txDesabonnement')) .join(
                        MailChimpCampaign.message) .filter(
                            AdherentMessages.status == 'sent') .filter(
                                AdherentMessages.type.in_(
                                    [
                                        'candidate',
                                        'candidate_jecoute'])) .filter(
                                            AdherentMessages.sent_at >= since) .join(
                                                MailChimpCampaign.report) .join(
                                                    AdherentMessages.author) .join(
                                                        Adherents.candidate_managed_area.and_(
                                                            CandidateManagedArea.zone_id == zone.id)) .order_by(
                                                                AdherentMessages.sent_at.desc()) .all()}


async def get_mail_ratios(
        db: Session,
        zone: GeoZone,
        since: datetime):

    res = db.query(
        func.count(
            MailChimpCampaign.id).label('nbCampagnes'),
        func.round(
            func.sum(
                MailChimpCampaignReport.open_unique) /
            func.sum(
                MailChimpCampaignReport.email_sent),
            4).label('txOuverture'),
        func.round(
            func.sum(
                MailChimpCampaignReport.click_unique) /
            func.sum(
                MailChimpCampaignReport.email_sent),
            4).label('txClique'),
        func.round(
            func.sum(
                MailChimpCampaignReport.unsubscribed) /
            func.sum(
                MailChimpCampaignReport.email_sent),
            4).label('txDesabonnement')) .select_from(MailChimpCampaignReport) .join(
        MailChimpCampaignReport.mailchimp_campaign) .join(
        MailChimpCampaign.message.and_(
            AdherentMessages.type.in_(
                [
                    'candidate',
                    'candidate_jecoute']),
            AdherentMessages.sent_at >= since)) .join(
        AdherentMessages.author) .join(
        Adherents.candidate_managed_area.and_(
            CandidateManagedArea.zone_id == zone.id)) .first()

    nat = db.query(
        func.round(
            func.sum(
                MailChimpCampaignReport.open_unique) /
            func.sum(
                MailChimpCampaignReport.email_sent),
            4).label('txOuverture'),
        func.round(
            func.sum(
                MailChimpCampaignReport.click_unique) /
            func.sum(
                MailChimpCampaignReport.email_sent),
            4).label('txClique'),
        func.round(
            func.sum(
                MailChimpCampaignReport.unsubscribed) /
            func.sum(
                MailChimpCampaignReport.email_sent),
            4).label('txDesabonnement')) .select_from(MailChimpCampaignReport) .join(
        MailChimpCampaignReport.mailchimp_campaign) .join(
        MailChimpCampaign.message.and_(
            AdherentMessages.type.in_(
                [
                    'candidate',
                    'candidate_jecoute']))) .first()

    return {'local': res, 'national': nat}
