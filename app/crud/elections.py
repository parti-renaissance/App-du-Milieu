"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session

from app.models.models_crm import Elections
from app.models.models_enmarche import GeoZone, GeoZoneParent
from app.database.database_crm import engine_crm
from app.crud.enmarche import get_child_code

from json import loads
from itertools import chain
import io
import pandas as pd


available_elections = [
    'Départementales 2015',
    'Européennes 2014',
    'Européennes 2019',
    'Législatives 2017',
    'Municipales 2020',
    'Présidentielles 2017',
    'Régionales 2015'
]


def get_elections(
        election: str,
        tour: int,
        zone: GeoZone,
        db: Session):
    columns = [
        'election',
        'departement',
        'commune',
        'commune_libelle',
        'bureau',
        'inscrits',
        'votants',
        'blancs',
        'exprimes',
        'numero_panneau',
        'nom_liste',
        'voix',
        'circonscription',
        'sexe',
        'nom',
        'prenom',
        'tour',
        'nuance',
        'num_dep_binome_candidat',
        'canton',
        'canton_libelle',
        'composition_binome'
    ]

    election_filter = {'election': election}
    election_filter = {
        'tour': tour,
        **election_filter} if tour else election_filter

    child_codes = list(chain(*get_child_code(db, zone, 'department')))

    query = str(db.query(Elections)
                .filter_by(**election_filter)
                .filter(Elections.departement.in_(child_codes))
                .statement.compile(compile_kwargs={"literal_binds": True}))

    copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(
        query=query, head="HEADER")
    conn = engine_crm.raw_connection()
    cur = conn.cursor()
    store = io.StringIO()
    cur.copy_expert(copy_sql, store)
    store.seek(0)
    df = pd.read_csv(store, encoding='utf-8')
    df.columns = columns

    return loads(df.to_json(orient='records', force_ascii=False))
