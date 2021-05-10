"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session

from app.models.models_crm import Contact
from app.models.models_enmarche import Adherents
from app.schemas import schemas
from app.crud.enmarche import get_candidate_zone


def get_contacts(db: Session, uuid: str):
    if (zone := get_candidate_zone(db, uuid)) is None:
        return None
    filter_zone = {'departement': zone.name} if zone.type == 'department' else {zone.type: zone.name}

    contacts = [contact.serialize() for contact in
            db.query(Contact).filter_by(**filter_zone).all()]

    """ metadata list of choices """
    interests = {'interestsChoices': schemas.InterestsChoices.list()}
    gender = {'genderChoices': schemas.Gender.list()}

    return {
        'totalItems': len(contacts),
        **interests,
        **gender,
        'contacts': contacts
        }


def get_number_of_contacts(db: Session, uuid: str):
    if (zone := get_candidate_zone(db, uuid)) is None:
        return None
    filter_zone = {'departement': zone.name} if zone.type == 'department' else {zone.type: zone.name}

    return {
        'adherentCount': db.query(Contact).filter_by(**filter_zone).count(),
        'zoneName': zone.name
    }
