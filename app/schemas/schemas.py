"""
Schemas
"""
from enum import Enum
from typing import List, Set, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class InterestsChoices(str, Enum):
    economie = 'economie'
    agriculture = 'agriculture'
    sante = 'sante'
    education = 'education'
    culture = 'culture'
    numerique = 'numerique'
    emploi = 'emploi'
    environement = 'environement'
    social = 'social'
    europe = 'europe'
    international = 'international'
    justice = 'justice'
    jeunesse = 'jeunesse'
    institution = 'institution'
    egalite = 'egalite'
    securite = 'securite'
    territoire = 'territoire'
    logement = 'logement'
    sport = 'sport'
    vide = ''

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))[:-1]


class Gender(str, Enum):
    homme = 'Homme'
    femme = 'Femme'
    autre = 'Autre'
    vide = ''
    
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))[:-1]


""" Marche mais ralenti le call api ...
class Contact(BaseModel):
    Genre: str = Field(alias="genre")
    Prénom: str = Field(alias="prenom")
    Nom: str = Field(alias="nom")
    Abonné_email: bool = Field(alias="sub_email")
    Abonné_tel: bool = Field(alias="sub_tel")
    Code_postal: str = Field(alias="code_postal")
    Code_commune: str = Field(alias="code_commune")
    Commune: str = Field(alias="commune")
    Code_département: str = Field(alias="code_departement")
    Département: str = Field(alias="departement")
    Code_région: str = Field(alias="code_region")
    Région: str = Field(alias="region")
    Centres_intérêt: Set[InterestsChoices] = Field(alias="centres_interet")

    class Config:
        orm_mode = True


class ContactOut(BaseModel):
    totalItems: int
    interestsChoices: Set[InterestsChoices]
    genderChoices: Set[Gender]
    contacts: List[Contact]

    class Config:
        orm_mode = True
"""


class JecouteSurvey(BaseModel):
    author_id: str
    survey_id: str
    posted_at: datetime
    postal_code: str
    age_range: str
    gender: str
    latitude: float
    longitude: float

    class Config:
        orm_mode = True