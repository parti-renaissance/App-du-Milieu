"""
Endpoints de notre api
"""
from datetime import datetime
from sqlalchemy.orm import Session, contains_eager, joinedload
from sqlalchemy import func, DateTime
from app.models.models_enmarche import AdherentMessages, Adherents, CandidateManagedArea
from app.models.models_enmarche import MailChimpCampaign, MailChimpCampaignReport
from app.models.models_enmarche import GeoZone, GeoCity, GeoDepartment
from app.crud.enmarche import get_candidate_zone



async def get_campaign_reports(
    db: Session,
    uuid: str,
    since: DateTime = datetime(2021, 3, 1)):
    if (zone := get_candidate_zone(db, uuid)) is None:
        return None
    
    referent_reports = await get_candidate_reports(db, zone, since)
    return referent_reports

async def get_referent_reports(
    db: Session,
    zone: GeoZone,
    since: DateTime):

    return db.query(MailChimpCampaign) \
        .options(joinedload(MailChimpCampaign.message)) \
        .options(joinedload(MailChimpCampaign.report)) \
        .filter(AdherentMessages.type == 'referent') \
        .filter(AdherentMessages.sent_at >= since) \
        .all()


async def get_candidate_reports(
    db: Session,
    zone: GeoZone,
    since: DateTime):
    print('zone.id:', zone.id)
    print('since:', since)


    return db.query(MailChimpCampaign) \
        .join(MailChimpCampaign.message) \
        .filter(AdherentMessages.status == 'sent') \
        .filter(AdherentMessages.type.in_(['candidate', 'candidate_jecoute'])) \
        .filter(AdherentMessages.sent_at >= since) \
        .join(MailChimpCampaign.report) \
        .options(contains_eager(MailChimpCampaign.message)) \
        .options(contains_eager(MailChimpCampaign.report)) \
        .join(AdherentMessages.author) \
        .join(Adherents.candidate_managed_area.and_(CandidateManagedArea.zone_id == zone.id)) \
        .all()
