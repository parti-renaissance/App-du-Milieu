"""
Schemas
"""
from enum import Enum
from pydantic import BaseModel, Field


class Contact(BaseModel):
    id: int = Field(..., title="identifiant unique")
    adherent_id: int = Field(None, title="id de l'adhérent s'il est dans notre base")
    genre: str = Field(None, title="Homme,Femme,Autre")
    prenom: str = Field(None, title="Nom du contact")
    nom: str = Field(None, title="Prénom du contact")
    email: str = Field(..., title="addresse email")
    sub_email: str = Field(None, title="Liste des abonnements aux newsletters")
    telephones: str = Field(None, title="Numeros de téléphone (il peut y en avoir plusieurs)")
    sub_tel: str = Field(None, title="Accepte ou non de recevoir des SMS / MMS")
    code_postal: str = Field(None, title="Code postal du contact")
    code_commune: str = Field(None, title="Code INSEE de la commune du contact")
    commune: str = Field(None, title="Commune du contact")
    code_departement: str = Field(None, title="Code INSEE du département du contact")
    departement: str = Field(None, title="Département du contact")
    code_region: str = Field(None, title="Code INSEE de la région du contact")
    region: str = Field(None, title="Région du contact")
    centres_interet: str = Field(None, title="Array de la liste des centres d'intérêt renseignés")
    typeforms: str = Field(None, title="Liste des typeforms auxquel à participer le contact")

    class Config:
        orm_mode = True


class Interests_choices(str, Enum):
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

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Gender(str, Enum):
    homme = 'Homme'
    femme = 'Femme'
    autre = 'Autre'
    
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
