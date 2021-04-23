"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session

from typing import Optional
from app.models import Contact, Adherents, CandidateManagedArea, GeoZone
from app import Schemas

import numpy as np


def get_contacts(db: Session, adherent: Adherents):
    zone = get_candidate_zone(db, adherent)
    if zone is None:
        return None

    filter_zone = {
        'region': 'code_region',
        'department': 'code_departement',
        'city': 'code_commune'
    }.get(zone.get_type(), None)
    if filter_zone is None:
        return None
    filter_zone = {filter_zone: zone.get_code()}

    contacts = np.array([contact.serialize() for contact in
            db.query(Contact).filter_by(**filter_zone).all()])

    """ metadata list of choices """
    interests = {'interests_choices': schemas.Interests_choices.list()}
    gender = {'gender_choices': schemas.Gender.list()}

    return {
        'total_items': len(contacts),
        **interests,
        **gender,
        'contacts': [*contacts]
        }


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
