"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session

from app.models.models_enmarche import Adherents, CandidateManagedArea, GeoZone


def me(db: Session, uuid: str) -> Adherents:
    if adherent := db.query(Adherents) \
                         .filter(Adherents.uuid == uuid) \
                         .first():
        return adherent


def get_candidate_zone(db: Session, uuid: str):
    return db.query(GeoZone) \
             .join(CandidateManagedArea) \
             .join(Adherents) \
             .filter(Adherents.uuid == uuid) \
             .first()
