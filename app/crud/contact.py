"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session

from app.models.models_crm import Contact
from app.schemas import schemas


def get_contacts(db: Session, filter_zone: dict):
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


def get_number_of_contacts(db: Session, filter_zone: dict):
    return {
        'adherentCount': db.query(Contact).filter_by(**filter_zone).count(),
        'zoneName': list(filter_zone.values())[0]
    }
