"""
SQLAlchemy de notre base de données
"""
from sqlalchemy import Column, Integer, String, UniqueConstraint

from app.database import CRM, Base

# import datetime
# 'tim': int ((self.tim - datetime.datetime (1970, 1, 1)).total_seconds ()),


class Contact(CRM):
    """ Table contacts """
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    adherent_id = Column(Integer, nullable=True)
    genre = Column(String, nullable=True)
    prenom = Column(String, nullable=True)
    nom = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    sub_email = Column(String, nullable=True)
    telephones = Column(String, nullable=True)
    sub_tel = Column(String, nullable=True)
    centres_interet = Column(String, nullable=True)
    code_postal = Column(String, nullable=True)
    code_commune = Column(String, nullable=True)
    commune = Column(String, nullable=True)
    code_departement = Column(String, nullable=True)
    departement = Column(String, nullable=True)
    code_region = Column(String, nullable=True)
    region = Column(String, nullable=True)
    typeforms = Column(String, nullable=True)


    def serialize(self):
        """ Print pour le call /contacts/ """
        return {
            'id': self.id,
            'Genre': self.genre,
            'Prénom': self.prenom,
            'Nom': self.nom,
            'Abonné_email': True if self.sub_email is not None else False,
            'Abonné_tel': True if self.sub_tel else False,
            'Code_postal': self.code_postal,
            'Code_commune': self.code_commune,
            'Commune': self.commune,
            'Code_département': self.code_departement,
            'Département': self.departement,
            'Code_région': self.code_region,
            'Région': self.region,
            'Centres_d\'intérêt': [] if self.centres_interet is None else self.centres_interet.split(',')
        }


    def details(self):
        """ Print pour les calls individuels """
        return {
            'id': self.id,
            'adherent_id': self.adherent_id,
            'Genre': self.genre,
            'Prénom': self.prenom,
            'Nom': self.nom,
            'email': self.email,
            'Abonné_email': self.sub_email,
            'Téléphone': self.telephones,
            'Abonné_tel': self.sub_tel,
            'Code_postal': self.code_postal,
            'Code_commune': self.code_commune,
            'Commune': self.commune,
            'Code_département': self.code_departement,
            'Département': self.departement,
            'Code_région': self.code_region,
            'Région': self.region,
            'Centres_d\'intérêt': [] if self.centres_interet is None else self.centres_interet.split(','),
            'Typeforms': [] if self.typeforms is None else self.typeforms.split(',')
        }


    def __repr__(self):
        return '<id {}>'.format(self.id)


class Adherents(Base):
    """ Table adherents id/uuid """
    __tablename__ = 'adherents'

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    candidate_managed_area_id = Column(Integer)


    def get_candidate_managed_area(self):
        return self.candidate_managed_area_id


class CandidateManagedArea(Base):
    """ Table candidate_managed_area pour retrouver la zone_id """
    __tablename__ = 'candidate_managed_area'

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, nullable=False)


    def get_zone_id(self):
        return self.zone_id


class GeoZone(Base):
    """ Table candidate_managed_area pour retrouver la zone_id """
    __tablename__ = 'geo_zone'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(255), nullable=False)
    code = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    
    UniqueConstraint('code', 'type', name='geo_zone_code_type_unique')


    def get_code(self):
        return self.code


class GeoRegion(Base):
    """ Table candidate_managed_area pour retrouver la zone_id """
    __tablename__ = 'geo_region'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)


    def get_code(self):
        return self.code


    def get_name(self):
        return self.name
