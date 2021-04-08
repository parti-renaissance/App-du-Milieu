"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session

from app import models, schemas


def get_contacts(db: Session, skip: int = 0, limit: int = 100):
    return [
        contact.serialize() for contact in 
        db.query(models.Contact).offset(skip).limit(limit).all()
    ]


def get_contact(db: Session, id: int):
    return db.query(models.Contact).filter(models.Contact.id == id).first()


def get_contacts_by_postal_code(db: Session, cp: str, skip: int = 0, limit: int = 100):
    return [
        contact.serialize() for contact in
        db.query(models.Contact).offset(skip).limit(limit).all()
        if contact.postal_code(cp)
    ]
