"""
Endpoints de notre api
"""
from collections import defaultdict
from enum import Enum
import base64
import json

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.models_enmarche import GeoZone, GeoZoneParent


class GeoTypes(str, Enum):
    '''
        On ajoute ici les colonnes implementees dans la table contact pour pouvoir filtrer dessus
    '''
    #borough = 'arrondissement'
    #canton = 'canton'
    city = 'commune'
    #city_community = 'communaute_de_communes'
    #consular_district = 'circonscription_consulaire'
    #country = 'pays'
    department = 'departement'
    #district = 'circonscription'
    #foreign_district = 'circonscription_des_FDE'
    region = 'region'


def getGeoType(s: str):
    '''
        Retourne le nom equivalent a la colonne de la table contact d'un type de GeoZone
    '''
    for t in GeoTypes:
        if t.name == s:
            return t.value
    return False


def scope2dict(scope: dict, name: bool = False):
    '''
        Transforme {'code':'roles', 'zones':[Liste de GeoZone]}
        en dict utilisable par sqlalchemy pour filtrer les zones
    '''
    res = defaultdict(list)
    for sub in scope['zones']:
        if (type := getGeoType(sub.type)):
            if name:
                res[type].append(sub.name)
            else:
                res['code_'+type].append(sub.code)

    return res


def decode_scopes(db: Session, scope: str):
    '''
        Recupere le X-Scope du header et le decode en base64
    '''
    base64_bytes = scope.encode("latin1")
    scope_bytes = base64.b64decode(base64_bytes)
    scope_string = scope_bytes.decode("latin1")  
    scope_dict = json.loads(scope_string)

    res_zone = []
    for zone in scope_dict['zones']:
        res_zone = [*res_zone,
            db.query(GeoZone) \
              .filter(GeoZone.uuid == zone['uuid']) \
              .first()]
    return {'code':scope_dict['code'], 'zones':res_zone}


def get_child(db: Session, parent: GeoZone, type: str = None):
    if parent.type == type:
        return parent

    query = db.query(GeoZone) \
        .join(GeoZoneParent, and_(
            GeoZoneParent.child_id  == GeoZone.id,
            GeoZoneParent.parent_id == parent.id))
    
    if type:
        query = query.filter(GeoZone.type == type)
    
    return query.all()

