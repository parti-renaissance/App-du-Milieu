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
    centres_interet: str = None
    typeforms: str = None

    class Config:
        orm_mode = True
