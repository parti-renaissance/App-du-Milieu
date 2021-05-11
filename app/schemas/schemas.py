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
    survey_id: int = Field(alias="id")
    survey_author_id: Optional[str]
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.date().strftime("%d/%m/%y")}
        orm_mode = True


class JecouteDataSurvey(BaseModel):
    id: int
    author_id: Optional[str]
    posted_at: datetime
    postal_code: Optional[str]
    age_range: Optional[str]
    gender: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    survey: JecouteSurvey = Field(alias="jecoute_survey")

    class Config:
        json_encoders = {datetime: lambda v: v.date().strftime("%d/%m/%y")}
        orm_mode = True
