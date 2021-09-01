"""Endpoints de notre api."""
import base64
import json
from collections import defaultdict
from enum import Enum

from fastapi import HTTPException
from app.models.models_enmarche import GeoZone, GeoZoneParent
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.resources.strings import NO_GEOZONE


class GeoTypes(str, Enum):
    """GeoTypes geres en base

    On ajoute ici les colonnes implementees
    dans la table contact pour pouvoir filtrer dessus
    """

    borough = "arrondissement_commune"
    # canton = 'canton'
    city = "commune"
    # city_community = 'communaute_de_communes'
    # consular_district = 'circonscription_consulaire'
    # country = 'pays'
    department = "departement"
    district = "circonscription"
    # foreign_district = 'circonscription_des_FDE'
    region = "region"
    country = "pays"


dict_geoZone_Hierarchy = {    
    "borough": 0,
    "city": 1,
    "city_community": 2,
    "district": 3,
    "foreign_district": 3,
    "consular_district": 3,
    "canton": 4,
    "department": 5,
    "region": 6,
    "country": 7,
}


def getGeoType(s: str):
    """Fonction d'equivalence GeoType - Nom colonne

    Retourne le nom equivalent a la colonne
    de la table contact d'un type de GeoZone
    """
    for t in GeoTypes:
        if t.name == s:
            return t.value
    return False


def scope2dict(scope: dict, name: bool = False):
    """Fonction de formatage d'un dictionary scope

    Transforme {'code':'roles', 'zones':[Liste de GeoZone]}
    en dict utilisable par sqlalchemy pour filtrer les zones
    """
    res = defaultdict(list)
    for sub in scope["zones"]:
        if geotype := getGeoType(sub.type):
            if name:
                res[geotype].append(sub.name)
            else:
                res["code_" + geotype].append(sub.code)

    return res


def decode_scopes(db: Session, scope: str):
    """Fonction qui decode le scope en base64

    Recupere le X-Scope du header et le decode en base64
    Transforme les zones en GeoZone
    """
    base64_bytes = scope.encode("latin1")
    scope_bytes = base64.b64decode(base64_bytes)
    scope_string = scope_bytes.decode("latin1")
    scope_dict = json.loads(scope_string)

    res_zone = [
        db.query(GeoZone).filter(GeoZone.uuid == zone["uuid"]).first()
        for zone in scope_dict["zones"]
    ]

    if res_zone == [None]:
        raise HTTPException(status_code=400, detail=NO_GEOZONE)
    return {"code": scope_dict["code"], "zones": res_zone}


def get_child(db: Session, zone: GeoZone, typeCible: str = None):
    if zone.type == typeCible:
        return [zone]

    try:
        lookingForChild = dict_geoZone_Hierarchy[zone.type] >= dict_geoZone_Hierarchy[typeCible]
    except:
        lookingForChild = True

    query = db.query(GeoZone).join(
        GeoZoneParent,
        and_(
            GeoZoneParent.child_id == (GeoZone.id if lookingForChild else zone.id),
            GeoZoneParent.parent_id == (zone.id if lookingForChild else GeoZone.id)
        ),
    )

    if typeCible:
        query = query.filter(GeoZone.type == typeCible)

    return query.all()
