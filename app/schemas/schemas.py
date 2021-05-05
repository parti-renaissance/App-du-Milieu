"""
Schemas
"""
from enum import Enum


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
