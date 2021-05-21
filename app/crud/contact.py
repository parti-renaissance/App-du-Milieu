"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from app.database.database_crm import engine_crm

from app.models.models_crm import Contact
from app.schemas import schemas
from app.crud.enmarche import get_candidate_zone


def get_contacts(db: Session, uuid: str):
    if (zone := get_candidate_zone(db, uuid)) is None:
        return None
    filter_zone = {'departement': zone.name} if zone.type == 'department' else {zone.type: zone.name}

    query = db.query(Contact).filter_by(**filter_zone).limit(10).statement
    columns = [column.name for column in inspect(Contact).c]

    with engine_crm.connect() as conn:
        cursor = conn.execute(query)
        contacts = [dict(zip(columns.pop(0), record.pop(0))).pop(0) for record in cursor]

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
