"""Schemas."""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class InterestsChoices(str, Enum):
    economie = "economie"
    agriculture = "agriculture"
    sante = "sante"
    education = "education"
    culture = "culture"
    numerique = "numerique"
    emploi = "emploi"
    environement = "environement"
    social = "social"
    europe = "europe"
    international = "international"
    justice = "justice"
    jeunesse = "jeunesse"
    institution = "institution"
    egalite = "egalite"
    securite = "securite"
    territoire = "territoire"
    logement = "logement"
    sport = "sport"
    vide = ""

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))[:-1]


class Gender(str, Enum):
    homme = "Homme"
    femme = "Femme"
    autre = "Autre"
    vide = ""

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))[:-1]


class AdherentName(BaseModel):
    #adherent_id: int = Field(alias="id")
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class JecouteSurvey(BaseModel):
    name: str
    created_at: datetime
    updated_at: datetime
    survey_author: Optional[AdherentName] = Field(alias="survey_author")

    class Config:
        orm_mode = True


class JecouteDataSurvey(BaseModel):
    posted_at: datetime
    author: Optional[AdherentName] = Field(alias="author")
    survey: JecouteSurvey = Field(alias="survey")

    class Config:
        orm_mode = True


class JemarcheDataSurvey(BaseModel):
    id: int
    postal_code: Optional[str]
    gender: Optional[str]
    age_range: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    data_survey: Optional[JecouteDataSurvey] = Field(alias="data_survey")

    class Config:
        orm_mode = True


class JemarcheDataSurveyOut(BaseModel):
    zone_name: str
    latitude: float
    longitude: float
    survey_datas: List[JemarcheDataSurvey]

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%d/%m/%y à %H:%M")}
        orm_mode = True


class RatioReport(BaseModel):
    txOuverture: Optional[float]
    txClique: Optional[float]
    txDesabonnement: Optional[float]


class LocalRatioReport(RatioReport):
    nbCampagnes: int


class IntegerReport(BaseModel):
    nbOuvertures: int
    nbCliques: int
    nbDesabonnements: int


class MailReport(RatioReport, IntegerReport):
    date: datetime
    auteur: str
    titre: str
    nbEmails: int


class MailReportOut(BaseModel):
    zone: str
    depuis: datetime
    campagnes: List[MailReport]

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%d/%m/%y")}
        orm_mode = True


class MailRatiosOut(BaseModel):
    zone: str
    depuis: datetime
    local: LocalRatioReport
    national: RatioReport

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%d/%m/%y")}
        orm_mode = True


class ElectionOut(BaseModel):
    election: str
    departement: str
    commune: str
    commune_libelle: str
    bureau: str
    inscrits: int
    votants: int
    blancs: Optional[int] = None
    exprimes: int
    numero_panneau: Optional[int] = None
    nom_liste: Optional[str] = None
    voix: int
    circonscription: Optional[int] = None
    sexe: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    tour: Optional[int] = None
    nuance: Optional[str] = None
    num_dep_binome_candidat: Optional[int] = None
    canton: Optional[str] = None
    canton_libelle: Optional[str] = None
    composition_binome: Optional[str] = None
