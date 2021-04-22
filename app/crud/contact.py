"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session

from typing import Optional
from app.models.models_crm import Contact
from app.models.models_enmarche import Adherents, CandidateManagedArea, GeoRegion, GeoZone
from app.schemas import schemas
from app.dependencies import CommonQueryParams

import time

def get_contacts(db: Session, commons: CommonQueryParams, adherent: Adherents):
    start_time = time.time()
    adherent_region = get_candidate_region(db, adherent)
    if adherent_region is None:
        return None

    filter_query = {'code_region': adherent_region.get_code()}
    if commons.code_postal:
        filter_query = {**filter_query, 'code_postal': commons.code_postal}
    if commons.code_departement:
        filter_query = {**filter_query, 'code_departement': commons.code_departement}

    contacts = {'contacts' : [contact.serialize() for contact in
            db.query(Contact).filter_by(**filter_query).all()]}
    print("contacts.serialize --- %s seconds ---" % (time.time() - start_time))

    """ metadata list of choices """
    interests = {'interests_choices': schemas.Interests_choices.list()}
    gender = {'gender_choices': schemas.Gender.list()}

    return {
        'total_items': len(contacts['contacts']),
        **interests,
        **gender,
        **contacts
        }


def get_contact(db: Session, id: int, adherent: Adherents) -> Contact:
    adherent_region = get_candidate_region(db, adherent)
    if adherent_region is None:
        return None

    filter_query = {'code_region': adherent_region.get_code()}
    filter_query = {**filter_query, 'id': id}
    return db.query(Contact) \
             .filter_by(**filter_query) \
             .first()


def me(db: Session, uuid: str) -> Adherents:
    adherent = db.query(Adherents) \
                 .filter(Adherents.uuid == uuid) \
                 .first()
    if adherent is None:
        return None
    return adherent


def get_candidate_region(db: Session, adherent: Adherents):
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

    geoRegion = db.query(GeoRegion) \
                .filter(GeoRegion.code == geoZone.get_code()) \
                .first()
    if geoRegion is None:
        return None

    return geoRegion
