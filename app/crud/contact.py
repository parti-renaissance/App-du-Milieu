"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session

from app.models.models_crm import Contact
from app.models.models_enmarche import Adherents
from app.schemas import schemas
from app.crud.enmarche import get_candidate_zone
import numpy as np


def get_contacts(db: Session, adherent: Adherents):
    zone = get_candidate_zone(db, adherent)

    filter_zone = {zone.type: zone.name}

    contacts = np.array([contact.serialize() for contact in
            db.query(Contact).filter_by(**filter_zone).all()])

    """ metadata list of choices """
    interests = {'interestsChoices': schemas.Interests_choices.list()}
    gender = {'genderChoices': schemas.Gender.list()}

    return {
        'totalItems': len(contacts),
        **interests,
        **gender,
        'contacts': [*contacts]
        }


def get_number_of_contacts(db: Session, adherent: Adherents):
    zone = get_candidate_zone(db, adherent)
    filter_zone = {zone.type: zone.name}

    return {
        'adherentCount': db.query(Contact).filter_by(**filter_zone).count(),
        'zoneName': zone.name
    }
