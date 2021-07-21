"""Endpoints de notre api."""
from json import loads
import io
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.crud.enmarche import scope2dict
from app.models.models_crm import Contact
from app.schemas import schemas
from app.database.database_crm import engine_crm

import pandas as pd


class EmailSubscriptions(str, Enum):
    """Tableau des équivalent role - subscription_type"""
    # local_host = 'subscribed_emails_local_host'
    # national = 'subscribed_emails_movement_information'
    # newsletter = 'subscribed_emails_weekly_letter'
    referent = 'subscribed_emails_referents'
    # project_host = 'citizen_project_host_email'
    # citizen_project = 'subscribed_emails_citizen_project_creation'
    deputy = 'deputy_email'
    candidate = 'candidate_email'
    senator = 'senator_email'


def isSubscribed(role: str, subs: list):
    """Retourne le subscription_type en fonction du role"""
    if subs is not None:
        for t in EmailSubscriptions:
            if t.name == role:
                return t.value in subs
    return False


def get_contacts(db: Session, scope: dict):
    columns = [
        'Genre',
        'Prénom',
        'Nom',
        'Abonné_email',
        'Abonné_tel',
        'Code_postal',
        'Code_commune',
        'Commune',
        'Code_arrondissement_commune',
        'Arrondissement_commune',
        'Code_département',
        'Département',
        'Code_région',
        'Région',
        'Code_circonscription',
        'Circonscription',
        'Centres_d\'intérêt'
    ]

    filter_zone = scope2dict(scope)
    query = db.query(Contact).filter(or_(getattr(Contact, k).in_(v)
                                         for k, v in filter_zone.items()))

    query = str(
        query.statement.compile(
            compile_kwargs={
                "literal_binds": True})) .replace(
        'contacts.id, ',
        '',
        1)

    copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(
        query=query, head="HEADER")
    conn = engine_crm.raw_connection()
    cur = conn.cursor()
    store = io.StringIO()
    cur.copy_expert(copy_sql, store)
    store.seek(0)
    df = pd.read_csv(store, encoding='utf-8')
    # reformat some datas
    df.centres_interet = df.centres_interet.str.replace(
        '[{}"]', '', regex=True).str.split(',')
    df.email_subscriptions = df.email_subscriptions.fillna('')
    df.email_subscriptions = df.email_subscriptions.str.replace(
        '[{}"]', '', regex=True).str.split(',')
    df.email_subscriptions = df.email_subscriptions.transform(
        lambda x: isSubscribed(scope['code'], x))
    df.sub_tel.replace({'t': True, 'f': False}, inplace=True)
    df.columns = columns
    # not implemented in front yet
    df.drop(columns=['Code_circonscription', 'Circonscription'], inplace=True)
    df.drop(columns=['Code_arrondissement_commune', 'Arrondissement_commune'], inplace=True)

    """metadata list of choices"""
    interests = {'interestsChoices': schemas.InterestsChoices.list()}
    gender = {'genderChoices': schemas.Gender.list()}

    return {
        'totalItems': len(df.index),
        **interests,
        **gender,
        'contacts': loads(df.to_json(orient='records', force_ascii=False))
    }


def get_contacts_v01(
    db: Session,
    scope: dict,
    skip: int,
    limit: int
):
    limit = min(limit, 1000)
    limit = max(limit, 100)
    skip = max(skip, 0)

    columns = [
        'Genre',
        'Prénom',
        'Nom',
        'Abonné_email',
        'Abonné_tel',
        'Code_postal',
        'Code_commune',
        'Commune',
        'Code_arrondissement_commune',
        'Arrondissement_commune',
        'Code_département',
        'Département',
        'Code_région',
        'Région',
        'Code_circonscription',
        'Circonscription',
        'Centres_d\'intérêt'
    ]

    filter_zone = scope2dict(scope)
    query = db.query(Contact).filter(or_(getattr(Contact, k).in_(v)
                                         for k, v in filter_zone.items()))

    totalItems = query.count()

    query = str(
        query.offset(skip).limit(limit).statement.compile(
            compile_kwargs={
                "literal_binds": True})) .replace(
        'contacts.id, ',
        '',
        1)

    copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(
        query=query, head="HEADER")
    conn = engine_crm.raw_connection()
    cur = conn.cursor()
    store = io.StringIO()
    cur.copy_expert(copy_sql, store)
    store.seek(0)
    df = pd.read_csv(store, encoding='utf-8')
    # reformat some datas
    df.centres_interet = df.centres_interet.str.replace(
        '[{}"]', '', regex=True).str.split(',')
    df.email_subscriptions = df.email_subscriptions.fillna('')
    df.email_subscriptions = df.email_subscriptions.str.replace(
        '[{}"]', '', regex=True).str.split(',')
    df.email_subscriptions = df.email_subscriptions.transform(
        lambda x: isSubscribed(scope['code'], x))
    df.sub_tel.replace({'t': True, 'f': False}, inplace=True)
    df.columns = columns
    # not implemented in front yet
    df.drop(columns=['Code_circonscription', 'Circonscription'], inplace=True)
    df.drop(columns=['Code_arrondissement_commune', 'Arrondissement_commune'], inplace=True)

    """metadata list of choices"""
    interests = {'interestsChoices': schemas.InterestsChoices.list()}
    gender = {'genderChoices': schemas.Gender.list()}

    return {
        'totalItems': totalItems,
        **interests,
        **gender,
        'contacts': loads(df.to_json(orient='records', force_ascii=False))
    }


def get_number_of_contacts(db: Session, scope: dict):
    filter_zone = scope2dict(scope)

    query = db.query(Contact).filter(or_(getattr(Contact, k).in_(v)
                                         for k, v in filter_zone.items()))

    zones = []
    for k, v in scope2dict(scope, name=True).items():
        zones.append({'zone_type': k, 'zone_name': [v]})

    return {
        'adherentCount': query.count(),
        'zones': zones
    }
