"""
Endpoints de notre api
"""
from datetime import datetime
from sqlalchemy.orm import Session, contains_eager, joinedload
from sqlalchemy import func, DateTime
from app.models.models_enmarche import AdherentMessages, Adherents, CandidateManagedArea
from app.models.models_enmarche import MailChimpCampaign
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
        .all()
