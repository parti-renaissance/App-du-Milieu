"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session

from typing import Optional
from app.models.models_enmarche import Adherents, CandidateManagedArea, GeoZone


def me(db: Session, uuid: str) -> Adherents:
    adherent = db.query(Adherents) \
                 .filter(Adherents.uuid == uuid) \
                 .first()
    if adherent is None:
        return None
    return adherent


def get_candidate_zone(db: Session, adherent: Adherents):
    if adherent is None:
        return None

    managedArea = db.query(CandidateManagedArea) \
                    .filter(CandidateManagedArea.id == adherent.get_candidate_managed_area()) \
                    .first()
    if managedArea is None:
        return None

    geoZone = db.query(GeoZone) \
                .filter(GeoZone.id == managedArea.get_zone_id()) \
                .first()
    if geoZone is None:
        return None

    return geoZone


def total_adherents(db: Session):
    return {'total_adherents': db.query(Adherents).count()}