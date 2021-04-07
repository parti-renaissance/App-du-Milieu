"""
SQLAlchemy de notre base de données
"""
from sqlalchemy import Column, Integer, String

from app.database import Base

# import datetime
# 'tim': int ((self.tim - datetime.datetime (1970, 1, 1)).total_seconds ()),


class Contact(Base):
    """ Table contacts """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    adherent_id = Column(Integer, nullable=True)
    genre = Column(String, nullable=True)
    prenom = Column(String, nullable=True)
    nom = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    sub_email = Column(String, nullable=True)
    telephones = Column(String, nullable=True)
    sub_tel = Column(String, nullable=True)
    code_postal = Column(String, nullable=True)
    centres_interet = Column(String, nullable=True)
    typeforms = Column(String, nullable=True)

    def serialize(self):
        """ Print pour le call /contacts/ """
        return {
            'id': self.id,
            'Genre': self.genre,
            'Prénom': self.prenom,
            'Nom': self.nom,
            'Code_postal': self.code_postal,
            'Abonné_email': self.sub_email,
            'Abonné_tel': self.sub_tel,
            'Centres_d\'intérêt': self.centres_interet
        }

    def details(self):
        """ Print pour les calls individuels """
        return {
            'id': self.id,
            'Genre': self.genre,
            'Prénom': self.prenom,
            'Nom': self.nom,
            'email': self.email,
            'Abonné_email': self.sub_email,
            'Téléphone': self.telephones,
            'Abonné_tel': self.sub_tel,
            'Code_postal': self.code_postal,
            'Centres_d\'intérêt': self.centres_interet,
            'Typeforms': self.typeforms
        }

    def postal_code(self, cp: str):
        """ Match ou non un code postal """
        length = len(cp)
        if length not in (2,3,5):
            # raise erreur wrong code postal ?
            return False
        return self.code_postal[:length] == cp


    def __repr__(self):
        return '<id {}>'.format(self.id)
