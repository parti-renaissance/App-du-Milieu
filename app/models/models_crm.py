"""
SQLAlchemy de notre base de données CRM
"""
from sqlalchemy import Column, Integer, Float, String, Boolean, Date, ARRAY

from app.database import CRM


class Contact(CRM):
    """ Table contacts """
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    genre = Column(String, nullable=True)
    prenom = Column(String, nullable=True)
    nom = Column(String, nullable=True)
    sub_email = Column(Boolean, nullable=True)
    sub_tel = Column(Boolean, nullable=True)
    code_postal = Column(String, nullable=True)
    code_commune = Column(String, nullable=True)
    commune = Column(String, nullable=True)
    code_departement = Column(String, nullable=True)
    departement = Column(String, nullable=True)
    code_region = Column(String, nullable=True)
    region = Column(String, nullable=True)
    centres_interet = Column(ARRAY(String), nullable=True)


class ContactInDb(Contact):
    adherent_id = Column(Integer, nullable=True)
    email = Column(String, nullable=False, unique=True)
    email_subscriptions = Column(ARRAY(String), nullable=True)
    telephones = Column(String, nullable=True)
    typeforms = Column(ARRAY(String), nullable=True)


class Downloads(CRM):
    """ Table crm_downloads """
    __tablename__ = 'crm_downloads'

    index = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    zone_type = Column(String, nullable=False)
    zone_name = Column(String, nullable=False)
    unique_user = Column(Integer, nullable=False)
    downloadsPer1000 = Column(Float, nullable=False)


class Users(CRM):
    """ Table crm_usage """
    __tablename__ = 'crm_usage'

    index = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    zone_type = Column(String, nullable=False)
    zone_name = Column(String, nullable=False)
    unique_user = Column(Integer, nullable=False)
