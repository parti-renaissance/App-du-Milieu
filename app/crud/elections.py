"""Endpoints elections."""
import io
import unicodedata
from typing import Literal
from sqlalchemy.orm import Session
from app.database.database_crm import engine_crm
from fastapi import HTTPException
from psycopg2 import sql, connect
import pandas as pd


DIVISION = Literal[
    'region',
    'departement',
    'circonscription',
    'canton',
    'commune',
    'bureau'
]

ELECTION = Literal[
    'Municipales 2020',
    'Départementales 2015',
    'Départementales 2021',
    'Législatives 2017',
    'Régionales 2015',
    'Régionales 2021',
    'Européennes 2014',
    'Européennes 2019',
    'Présidentielles 2017'
]

dict_base = {
    'Municipales 2020': ('nuance',),
    'Départementales 2015': ('nuance',),
    'Départementales 2021': ('nuance',),
    'Législatives 2017': ('nuance',),
    'Régionales 2015': ('nuance',),
    'Régionales 2021': ('nuance',),
    'Européennes 2014': ('nuance',),
    'Européennes 2019': ('nom_liste',),
    'Présidentielles 2017': ('nuance',)
}
"""Always returned information by election"""


dict_detail = {
    'Municipales 2020': ('nom', 'prenom',),
    'Départementales 2015': ('composition_binome',),
    'Départementales 2021': ('composition_binome',),
    'Législatives 2017': ('nom', 'prenom',),
    'Régionales 2015': ('nom', 'prenom',),
    'Régionales 2021': ('nom', 'prenom',),
    'Européennes 2014': ('nom', 'prenom',),
    'Européennes 2019': (),
    'Présidentielles 2017': ('nom', 'prenom',)
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


def safe_query(query: str) -> pd.DataFrame:
    with engine_crm.raw_connection().cursor() as cursor:
        try:
            cursor.execute(query)
            names = [x[0] for x in cursor.description]
            rows = cursor.fetchall()
            return pd.DataFrame( rows, columns=names)
        finally:
            if cursor is not None:
                cursor.close()


def fast_query(query: str) -> pd.DataFrame:
    copy_sql = f"COPY ({query}) TO STDOUT WITH CSV HEADER"
    with engine_crm.raw_connection().cursor() as cursor:
        store = io.StringIO()
        cursor.copy_expert(copy_sql, store)
        store.seek(0)
        cursor.close()
    return pd.read_csv(store, encoding='utf-8')


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
    if election not in dict_base.keys():
        return pd.DataFrame()

    # pour le moment pas de scope, pas d'utilisation de db: Session (orm)
    query = sql.SQL("""
        select distinct
          election,
          tour,
          {division},
          cast(sum(inscrits) as integer) as inscrits,
          cast(sum(votants) as integer) as votants,
          cast(sum(exprimes) as integer) as exprimes
        from {table}
        where {division} = {zone}
        group by
          election,
          tour,
          {division}
        """).format(
          division = sql.Identifier(maillage),
          table = sql.Identifier('election_bureau_' + format_table(election, tour)),
          zone = sql.Literal(code_zone),
        )

    return safe_query(query)


def ElectionAgregat(election: str, division: str):
    type_election = election.split()[0]
    if type_election not in dict_election.keys():
        raise HTTPException(status_code=400, detail=f'No data for election {election}')
    if division not in dict_maillage.keys():
        raise HTTPException(status_code=400, detail=f'The division {division} is not available yet')
    if dict_maillage[division] <= dict_election[type_election]:
        return dict_base[election] + dict_detail[election]
    return dict_base[election]


def get_nuance_color(election: str) -> pd.DataFrame:
    query = sql.SQL("""
        select
          nuance,
          nom_liste,
          code_couleur
        from elections_nuances_couleurs_v2
        where election = {election}
        """).format(
          election = sql.Literal(election),
        )

    return safe_query(query).dropna(how='all', axis=1)


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
    if election not in dict_base.keys():
        return pd.DataFrame()

    # pour le moment pas de scope, pas d'utilisation de db: Session (orm)
    query = sql.SQL("""
        select distinct
          election,
          {agregat},
          cast(sum(voix) as integer) as voix
        from elections
        where {division} = {zone}
          and election = {election}
          and tour = {tour}
        group by
          election,
          {agregat}
        order by
          voix desc
        """).format(
          agregat = sql.SQL(', ').join(map(
              sql.Identifier, ElectionAgregat(election, maillage))),
          division = sql.Identifier(maillage),
          zone = sql.Literal(code_zone),
          election = sql.Literal(election),
          tour = sql.Literal(tour),
        )

    df = safe_query(query)
    if df.empty:
        return df

    df = df.merge(get_nuance_color(election), how='left')
    df.code_couleur.fillna('#FFFFFF', inplace=True)

    return df


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
    query = sql.SQL("""
        select distinct on ({division})
          election,
          {division} as code,
          {agregat},
          first_value(voix) OVER wnd
        FROM (
          select
            election,
            {division},
            {agregat},
            cast(sum(voix) as integer) as voix
          from {table_name}
          group by
            election,
            {division},
            {agregat}
        ) table_groupby
        window wnd as (
          partition by {division} order by voix desc
          rows between unbounded preceding and unbounded following
        )
        """).format(
          agregat = sql.SQL(', ').join(map(
              sql.Identifier, ElectionAgregat(election, maillage))),
          division = sql.Identifier(maillage),
          table_name = sql.Identifier('elections_' + format_table(election, tour)),
        )

    df = safe_query(query).merge(
        get_nuance_color(election),
        how='left')[['code', dict_base[election][0], 'code_couleur']]
    df.code_couleur.fillna('#FFFFFF', inplace=True)

    return df


def get_compatible_nuance(
    db: Session,
    scope: dict,
    election: str,
    nuance_liste: str):
    if election not in dict_base.keys():
        return None
        
    # get nuance / nom_liste and color for the election
    df = get_nuance_color(election)

    # retrieve the color if matched 
    df_color = df.loc[df[dict_base[election][0]] == nuance_liste, 'code_couleur']
    if df_color.empty:
        return None
    color = df_color.iloc[0]

    # retrieve all match for the color
    compatible_nuance = df.loc[df.code_couleur == color, dict_base[election][0]].tolist()
    
    return {'code_couleur': color, 'compatibles': compatible_nuance}


def get_density(
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

    query = sql.SQL("""
    select 
      elections.code,
      elections.voix,
      participation.exprimes
      -- ROUND(voix/exprimes, 3) as voix
    from (
      select
        election,
        {division} as code,
        cast(sum(voix) as integer) as voix
      from {table_elections}
      where {nuance_liste} in ({compatibles})
      group by
        election,
        {division}
    ) elections
    inner join (
      select 
        election,
        tour,
        {division} as code,
        cast(sum(inscrits) as integer) as inscrits,
        cast(sum(votants) as integer) as votants,
        cast(sum(exprimes) as integer) as exprimes
      from {table_bureau}
      group by
        election,
        tour,
        {division}
    ) participation 
      on participation.code = elections.code
    """).format(
      division = sql.Identifier(maillage),
      table_elections = sql.Identifier('elections_' + format_table(election, tour)),
      nuance_liste = sql.Identifier(dict_base[election][0]),
      compatibles = sql.SQL(', ').join(map(sql.Literal, nuances_compatibles['compatibles'])),
      table_bureau = sql.Identifier('election_bureau_' + format_table(election, tour))
    )

    df = safe_query(query)
    df['%voix'] = round(df.voix / df.exprimes, 3)
    return df
