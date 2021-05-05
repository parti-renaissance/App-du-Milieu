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


def get_candidate_zone(db: Session, adherent: Adherents):
    if adherent is None:
        raise Exception('Adherent not found')

    managedArea = db.query(CandidateManagedArea) \
                    .filter(CandidateManagedArea.id == adherent.get_candidate_managed_area()) \
                    .first()
    if managedArea is None:
        raise Exception('No managed area found')

    geoZone = db.query(GeoZone) \
                .filter(GeoZone.id == managedArea.get_zone_id()) \
                .first()
    if geoZone is None:
        raise Exception('Geo_zone not found')
    return geoZone
