"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session

from typing import Optional
from app import models, schemas
from app.dependencies import CommonQueryParams


def get_contacts(db: Session, commons: CommonQueryParams):
    filter_query = {}
    if commons.code_postal:
        filter_query.update({'code_postal': commons.code_postal})
    if commons.code_departement:
        filter_query.update({'code_departement': commons.code_departement})
    if commons.code_region:
        filter_query.update({'code_region': commons.code_region})

    return [contact.serialize() for contact in
            db.query(models.Contact).filter_by(**filter_query).all()]


def get_contact(db: Session, id: int):
    return db.query(models.Contact).filter(models.Contact.id == id).first()
