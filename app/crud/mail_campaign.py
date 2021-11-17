"""Endpoints de notre api."""
from datetime import datetime
from typing import List

from app.crud.enmarche import get_child
from app.models.models_enmarche import (
    AdherentMessageFilters,
    AdherentMessages,
    Adherents,
    GeoZone,
    MailChimpCampaign,
    MailChimpCampaignReport,
    ReferentManagedAreasTags,
    ReferentTags,
)
from sqlalchemy import func
from sqlalchemy.orm import Query, Session
from sqlalchemy.sql.functions import coalesce


def filter_role(db: Session, query: Query, zones: List[GeoZone], role: str):
    """This function adds geozone filter to query

    Allow to filter database
    according to implemented roles
    """
    if role not in ("referent", "deputy", "senator", "candidate"):
        return query

    all_zones = [
        [zone.id] + [child.id for child in get_child(db, zone)] for zone in zones
    ]
    all_zones = [item for sublist in all_zones for item in sublist]

    if role == "referent":
        return (
            query.join(Adherents.managed_area)
            .join(ReferentManagedAreasTags.referent_tag)
            .join(ReferentTags.zone.and_(GeoZone.id.in_(all_zones)))
        )

    if role in {"deputy", "senator"}:
        return (
            query.join(AdherentMessages.filter)
            .join(AdherentMessageFilters.referent_tag)
            .join(ReferentTags.zone.and_(GeoZone.id.in_(all_zones)))
        )

    #if role in {"candidate"}:
    return query.join(AdherentMessages.filter).join(
        AdherentMessageFilters.zone.and_(GeoZone.id.in_(all_zones))
    )


async def get_campaign_reports(db: Session, zone: GeoZone, since: datetime, role: str):
    """Method to CRUD /campaign/reports"""
    query = (
        db.query(
            MailChimpCampaign.id.label("id"),
            AdherentMessages.sent_at.label("date"),
            (Adherents.first_name + " " + Adherents.last_name).label("auteur"),
            AdherentMessages.subject.label("titre"),
            MailChimpCampaignReport.email_sent.label("nbEmails"),
            MailChimpCampaignReport.open_unique.label("nbOuvertures"),
            func.round(
                MailChimpCampaignReport.open_unique
                / MailChimpCampaignReport.email_sent,
                4,
            ).label("txOuverture"),
            MailChimpCampaignReport.click_unique.label("nbCliques"),
            func.round(
                MailChimpCampaignReport.click_unique
                / MailChimpCampaignReport.email_sent,
                4,
            ).label("txClique"),
            MailChimpCampaignReport.unsubscribed.label("nbDesabonnements"),
            func.round(
                MailChimpCampaignReport.unsubscribed
                / MailChimpCampaignReport.email_sent,
                4,
            ).label("txDesabonnement"),
        )
        .join(MailChimpCampaign.message)
        .filter(AdherentMessages.status == "sent")
        .filter(AdherentMessages.sent_at >= since)
        .join(MailChimpCampaign.report)
        .join(AdherentMessages.author)
    )
    if role != "national":
        query = query.filter(AdherentMessages.type == role)

    query = filter_role(db, query, [zone], role)

    return {
        "zone": zone.name,
        "depuis": since,
        "campagnes": query.order_by(AdherentMessages.sent_at.desc()).all(),
    }


async def get_mail_ratios(db: Session, zone: GeoZone, since: datetime, role: str):
    """Method to CRUD /campaign/reportsRatios"""
    query = (
        db.query(
            func.count(MailChimpCampaign.id).label("nbCampagnes"),
            coalesce(
                func.round(
                    func.sum(MailChimpCampaignReport.open_unique)
                    / func.sum(MailChimpCampaignReport.email_sent),
                    4,
                ),
                0,
            ).label("txOuverture"),
            coalesce(
                func.round(
                    func.sum(MailChimpCampaignReport.click_unique)
                    / func.sum(MailChimpCampaignReport.email_sent),
                    4,
                ),
                0,
            ).label("txClique"),
            coalesce(
                func.round(
                    func.sum(MailChimpCampaignReport.unsubscribed)
                    / func.sum(MailChimpCampaignReport.email_sent),
                    4,
                ),
                0,
            ).label("txDesabonnement"),
        )
        .select_from(MailChimpCampaignReport)
        .join(MailChimpCampaignReport.mailchimp_campaign)
        .join(MailChimpCampaign.message)
        .filter(AdherentMessages.status == "sent")
        .filter(AdherentMessages.sent_at >= since)
        .join(AdherentMessages.author)
    )

    if role == "national":
        return {"local": query.first(), "national": query.first()}

    query = query.filter(AdherentMessages.type == role)
    res = {"national": query.first()}

    # filtre sur la zone locale
    query = filter_role(db, query, zone, role)

    return {"local": query.first(), **res}
