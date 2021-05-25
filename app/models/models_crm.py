"""
SQLAlchemy de notre base de données CRM
"""
from sqlalchemy import Column, Integer, Float, String, Boolean, Date, DateTime

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
    centres_interet = Column(String, nullable=True)
    adherent_id = Column(Integer, nullable=True)
    email = Column(String, nullable=False, unique=True)
    email_subscriptions = Column(String, nullable=True)
    telephones = Column(String, nullable=True)
    typeforms = Column(String, nullable=True)

    def serialize(self):
        """ Print pour le call /contacts/ """
        return {
            'Genre': self.genre,
            'Prénom': self.prenom,
            'Nom': self.nom,
            'Abonné_email': self.sub_email,
            'Abonné_tel': self.sub_tel,
            'Code_postal': self.code_postal,
            'Code_commune': self.code_commune,
            'Commune': self.commune,
            'Code_département': self.code_departement,
            'Département': self.departement,
            'Code_région': self.code_region,
            'Région': self.region,
            'Centres_d\'intérêt': self.centres_interet
        }


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
