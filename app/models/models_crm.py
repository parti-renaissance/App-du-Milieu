"""
SQLAlchemy de notre base de données CRM
"""
from sqlalchemy import Column, SmallInteger, Integer, Float, String, Boolean, Date, ARRAY

from app.database import CRM


class Contact(CRM):
    """ Table contacts """
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    genre = Column(String, nullable=True)
    prenom = Column(String, nullable=True)
    nom = Column(String, nullable=True)
    email_subscriptions = Column(ARRAY(String), nullable=True)
    sub_tel = Column(Boolean, nullable=True)
    code_postal = Column(String, nullable=True)
    code_commune = Column(String, nullable=True)
    commune = Column(String, nullable=True)
    code_arrondissement_commune = Column(String, nullable=True)
    arrondissement_commune = Column(String, nullable=True)
    code_departement = Column(String, nullable=True)
    departement = Column(String, nullable=True)
    code_region = Column(String, nullable=True)
    region = Column(String, nullable=True)
    code_circonscription = Column(String, nullable=True)
    circonscription = Column(String, nullable=True)
    centres_interet = Column(ARRAY(String), nullable=True)


class ContactInDb(Contact):
    adherent_id = Column(Integer, nullable=True)
    email = Column(String, nullable=False, unique=True)
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


class Elections(CRM):
    """ Table elections """
    __tablename__ = 'elections'

    election = Column(String, nullable=False, index=True)
    departement = Column(String, nullable=False)
    commune = Column(String, nullable=False)
    commune_libelle = Column(String, nullable=False)
    bureau = Column(String, nullable=False)
    inscrits = Column(Integer, nullable=False)
    votants = Column(Integer, nullable=False)
    blancs = Column(Integer, nullable=False)
    exprimes = Column(Integer, nullable=False)
    numero_panneau = Column(Integer, nullable=True)
    nom_liste = Column(String, nullable=True)
    voix = Column(Integer, nullable=False)
    circonscription = Column(Integer, nullable=True)
    sexe = Column(String, nullable=True)
    nom = Column(String, nullable=True)
    prenom = Column(String, nullable=True)
    tour = Column(SmallInteger, nullable=True)
    nuance = Column(String, nullable=True)
    num_dep_binome_candidat = Column(Integer, nullable=True)
    canton = Column(String, nullable=True)
    canton_libelle = Column(String, nullable=True)
    composition_binome = Column(String, nullable=True)

    __mapper_args__ = {
        'primary_key':[
            election,
            departement,
            commune,
            bureau,
            nom_liste,
            sexe,
            nom,
            prenom,
            num_dep_binome_candidat,
            tour
        ]
    }
