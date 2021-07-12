"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.models_enmarche import Adherents, CandidateManagedArea, GeoZone, GeoZoneParent


def me(db: Session, uuid: str) -> Adherents:
    if adherent := db.query(Adherents) \
        .filter(Adherents.uuid == uuid) \
            .first():
        return adherent


def get_candidate_zone(db: Session, uuid: str):
    return db.query(GeoZone) .join(
        CandidateManagedArea,
        CandidateManagedArea.zone_id == GeoZone.id) .join(
        Adherents,
        Adherents.candidate_managed_area_id == CandidateManagedArea.id) .filter(
            Adherents.uuid == uuid) .first()


def get_child_code(db: Session, parent: GeoZone, type: str):
    if parent.type == type:
        return parent

    return db.query(GeoZone.code) \
        .join(GeoZoneParent, and_(
            GeoZoneParent.child_id == GeoZone.id,
            GeoZoneParent.parent_id == parent.id)) \
        .filter(GeoZone.type == type) \
        .all()
