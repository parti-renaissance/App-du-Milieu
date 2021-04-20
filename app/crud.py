"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session

from typing import Optional
from app import models, schemas
from app.dependencies import CommonQueryParams


def get_contacts(db: Session, commons: CommonQueryParams, adherent: models.Adherents):
    adherent_region = get_candidate_region(db, adherent)
    if adherent_region is None:
        return None

    filter_query = {'code_region': adherent_region.get_code()}
    if commons.code_postal:
        filter_query = {**filter_query, 'code_postal': commons.code_postal}
    if commons.code_departement:
        filter_query = {**filter_query, 'code_departement': commons.code_departement}

    contacts = {'contacts' : [contact.serialize() for contact in
            db.query(models.Contact).filter_by(**filter_query).all()]}

    """ metadata list of choices """
    interests = {'interests_choices': schemas.Interests_choices.list()}
    gender = {'gender_choices': schemas.Gender.list()}

    return {
        'total_items': len(contacts['contacts']),
        **interests,
        **gender,
        **contacts
        }


def get_contact(db: Session, id: int, adherent: models.Adherents) -> models.Contact:
    adherent_region = get_candidate_region(db, adherent)
    if adherent_region is None:
        return None

    filter_query = {'code_region': adherent_region.get_code()}
    filter_query = {**filter_query, 'id': id}
    return db.query(models.Contact) \
             .filter_by(**filter_query) \
             .first()


def me(db: Session, uuid: str) -> models.Adherents:
    adherent = db.query(models.Adherents) \
                 .filter(models.Adherents.uuid == uuid) \
                 .first()
    if adherent is None:
        return None
    return adherent


def get_candidate_region(db: Session, adherent: models.Adherents):
    if adherent is None:
        return None

    managedArea = db.query(models.CandidateManagedArea) \
                    .filter(models.CandidateManagedArea.id == adherent.get_candidate_managed_area()) \
                    .first()
    if managedArea is None:
        return None

    geoZone = db.query(models.GeoZone) \
                .filter(models.GeoZone.id == managedArea.get_zone_id()) \
                .first()
    if geoZone is None:
        return None

    geoRegion = db.query(models.GeoRegion) \
                .filter(models.GeoRegion.code == geoZone.get_code()) \
                .first()
    if geoRegion is None:
        return None

    return geoRegion
