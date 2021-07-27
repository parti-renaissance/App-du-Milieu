"""Endpoints elections."""
import io
import unicodedata
from sqlalchemy.orm import Session
from app.database.database_crm import engine_crm
from fastapi import HTTPException
import pandas as pd


dict_base = {
    'Municipales 2020': 'nuance',
    'Départementales 2015': 'nuance',
    'Départementales 2021': 'nuance',
    'Législatives 2017': 'nuance',
    'Régionales 2015': 'nuance',
    'Régionales 2021': 'nuance',
    'Européennes 2014': 'nuance',
    'Européennes 2019': 'nom_liste',
    'Présidentielles 2017': 'nuance'
}
"""Always returned information by election"""


dict_detail = {
    'Municipales 2020': 'nom, prenom',
    'Départementales 2015': 'composition_binome',
    'Départementales 2021': 'composition_binome',
    'Législatives 2017': 'nom, prenom',
    'Régionales 2015': 'nom, prenom',
    'Régionales 2021': 'nom, prenom',
    'Européennes 2014': 'nom, prenom',
    'Européennes 2019': None,
    'Présidentielles 2017': 'nom, prenom'
}
"""Detailled returned information by election"""


dict_maillage = {
    'bureau': 0,
    'commune': 1,
    'canton': 2,
    'circonscription': 3,
    'departement': 4,
    'region': 5,
    'national': 6
    }
"""Hierarchical level of territorial division"""


dict_election = {
    'Municipales': 1,
    'Départementales': 2,
    'Législatives': 3,
    'Régionales': 5,
    'Européennes': 6,
    'Présidentielles': 6
}
"""Election type with the level of division where we use detailled datas"""


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')


def format_table(election, tour):
    return strip_accents(election).replace(' ', '_').lower() + (
      f'_t{tour}' if election not in ('Européennes 2014', 'Européennes 2019') else '')


def get_participation(
    db: Session,
    scope: dict,
    election: str,
    tour: int,
    maillage: str,
    code_zone: str) -> pd.DataFrame:
    """1er endpoint: Participation

    Retourne les informations de participations pour l'election
    et la zone selectionnee
    """
    # pour le moment pas de scope, pas d'utilisation de db: Session (orm)
    query_participation = f'''
        select distinct
          election,
          tour,
          {maillage},
          cast(sum(inscrits) as integer) as inscrits,
          cast(sum(votants) as integer) as votants,
          cast(sum(exprimes) as integer) as exprimes
        from (
          select distinct
            election,
            tour,
            {maillage},
            inscrits,
            votants,
            exprimes
          from elections
          where {maillage} = '{code_zone}'
            and election = '{election}'
            and tour = '{tour}'
        ) bureau_election
        where {maillage} = '{code_zone}'
          and election = '{election}'
          and tour = '{tour}'
        group by
          election,
          tour,
          {maillage}
        '''

    copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(
        query=query_participation, head="HEADER")
    conn = engine_crm.raw_connection()
    cur = conn.cursor()
    store = io.StringIO()
    cur.copy_expert(copy_sql, store)
    store.seek(0)
    cur.close()
    conn.close()
    df = pd.read_csv(store, encoding='utf-8')

    return df


def ElectionAgregat(election: str, division: str):
    type_election = election.split()[0]
    if type_election not in dict_election.keys():
        raise HTTPException(status_code=400, detail=f'No data for election {election}')
    if division not in dict_maillage.keys():
        raise HTTPException(status_code=400, detail=f'The division {division} is not available yet')
    if dict_maillage[division] <= dict_election[type_election]:
        return dict_base[election] \
               + (', ' + dict_detail[election] if dict_detail[election] else '')
    return dict_base[election]


def get_election_nuance_color(election: str) -> pd.DataFrame:
    query = f'''
    select
      nuance_candidat as nuance,
      nuance_binome as nuance,
      nuance_liste as nuance,
      nom_liste,
      code_couleur
    from elections_nuances_couleurs
    where election = '{election}'
    '''

    with engine_crm.connect() as connection:
        df = pd.read_sql(query, connection).dropna(axis=1)

    return df


def get_results(
    db: Session,
    scope: dict,
    election: str,
    tour: int,
    maillage: str,
    code_zone: str) -> pd.DataFrame:
    """1er endpoint bis: Results

    Retourne les resultats pour l'election et la zone selectionnee
    """
    # pour le moment pas de scope, pas d'utilisation de db: Session (orm)
    agregat = ElectionAgregat(election, maillage)

    query_resultats = f'''
        select distinct
          election,
          {agregat},
          cast(sum(voix) as integer) as voix
        from elections
        where {maillage} = '{code_zone}'
          and election = '{election}'
          and tour = '{tour}'
        group by
          election,
          {agregat}
        order by
          voix desc
        '''

    copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(
        query=query_resultats, head="HEADER")
    conn = engine_crm.raw_connection()
    cur = conn.cursor()
    store = io.StringIO()
    cur.copy_expert(copy_sql, store)
    store.seek(0)
    cur.close()
    conn.close()
    df = pd.read_csv(store, encoding='utf-8')

    return df.merge(get_election_nuance_color(election), how='left')


def get_colors(
    db: Session,
    scope: dict,
    election: str,
    tour: int,
    maillage: str) -> pd.DataFrame:
    """2eme endpoint: Couleurs

    Retourne les couleurs de la liste/candidat arrivé
    premier au tour de l'election par division
    """
    if election not in dict_base.keys():
        return pd.DataFrame()

    # pour le moment pas de scope, pas d'utilisation de db: Session (orm)
    agregat = ElectionAgregat(election, maillage)

    query_color = f'''
    select distinct on ({maillage})
      election,
      {maillage} as code,
      {agregat},
      first_value(voix) OVER wnd
    FROM (
      select
        election,
        {maillage},
        {agregat},
        cast(sum(voix) as integer) as voix
      from elections_{format_table(election, tour)}
      group by
        election,
        {maillage},
        {agregat}
    ) table_groupby
    window wnd as (
      partition by {maillage} order by voix desc
      rows between unbounded preceding and unbounded following
    )
    '''

    copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(
        query=query_color, head="HEADER")
    conn = engine_crm.raw_connection()
    cur = conn.cursor()
    store = io.StringIO()
    cur.copy_expert(copy_sql, store)
    store.seek(0)
    df = pd.read_csv(store, encoding='utf-8')
    cur.close()
    conn.close()

    return df.merge(
        get_election_nuance_color(election),
        how='left')[['code', dict_base[election], 'code_couleur']]


def get_compatible_nuance(
    db: Session,
    scope: dict,
    election: str,
    nuance_liste: str):
    if election not in dict_base.keys():
        return None
        
    # get nuance / nom_liste and color for the election
    df = get_election_nuance_color(election)

    # retrieve the color if matched 
    df_color = df.loc[df[dict_base[election]] == nuance_liste, 'code_couleur']
    if df_color.empty:
        return None
    color = df_color.iloc[0]

    # retrieve all match for the color
    compatible_nuance = df.loc[df.code_couleur == color, dict_base[election]].tolist()
    
    return {'code_couleur': color, 'compatibles': compatible_nuance}


def get_nuance_results(
    db: Session,
    scope: dict,
    election: str,
    tour: int,
    maillage: str,
    nuance: str) -> pd.DataFrame:
    """3eme endpoint: Couleurs pour les "compatibles" avec la nuance

    Retourne la couleur principale et cumul du nombre de voix
    pour le groupe de listes compatibles (agrégées par couleur)
    """
    # pour le moment pas de scope, pas d'utilisation de db: Session (orm)
    if not (nuances_compatibles := get_compatible_nuance(db, scope, election, nuance)):
        return pd.DataFrame()

    query_color = f'''
    select distinct
      election,
      {maillage} as code,
      cast(sum(voix) as integer) as voix
    from elections_{format_table(election, tour)}
    where {dict_base[election]} in ({str(nuances_compatibles['compatibles']).strip('[]')})
    group by
      election,
      {maillage}
    '''

    copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(
        query=query_color, head="HEADER")
    conn = engine_crm.raw_connection()
    cur = conn.cursor()
    store = io.StringIO()
    cur.copy_expert(copy_sql, store)
    store.seek(0)
    cur.close()
    conn.close()
    df = pd.read_csv(store, encoding='utf-8')

    return df.drop(columns='election')

