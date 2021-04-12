"""
Schemas
"""
from pydantic import BaseModel

class Contact(BaseModel):
    id: int
    adherent_id: int = None
    genre: str = None
    prenom: str = None
    nom: str = None
    email: str
    sub_email: str = None
    telephones: str = None
    sub_tel: str = None
    code_postal: str = None
    code_commune: str = None
    commune: str = None
    code_departement: str = None
    departement: str = None
    code_region: str = None
    region: str = None
    centres_interet: str = None
    typeforms: str = None

    class Config:
        orm_mode = True
