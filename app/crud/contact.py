"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session

from typing import Optional
from app.models.models_crm import Contact
from app.models.models_enmarche import Adherents
from app.schemas import schemas
from app.crud.enmarche import me, get_candidate_zone
import numpy as np


def get_contacts(db: Session, adherent: Adherents):
    zone = get_candidate_zone(db, adherent)
    if zone is None:
        return None

    filter_zone = {zone.type: zone.name}

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
