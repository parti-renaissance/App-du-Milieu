"""
Endpoints de notre api
"""
from sqlalchemy.orm import Session

from app.models.models_crm import Contact
from app.schemas import schemas
from app.database.database_crm import engine_crm

from json import loads
import io
import pandas as pd


def get_contacts(db: Session, filter_zone: dict):
    columns = [
        'Genre',
        'Prénom',
        'Nom',
        'Abonné_email',
        'Abonné_tel',
        'Code_postal',
        'Code_commune',
        'Commune',
        'Code_département',
        'Département',
        'Code_région',
        'Région',
        'Centres_d\'intérêt'
    ]

    query = str(db.query(Contact).filter_by(**filter_zone)
                .statement.compile(compile_kwargs={"literal_binds": True})) \
        .replace('contacts.id, ', '', 1)

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
    df.sub_email.replace({'t': True, 'f': False}, inplace=True)
    df.sub_tel.replace({'t': True, 'f': False}, inplace=True)
    df.columns = columns

    """ metadata list of choices """
    interests = {'interestsChoices': schemas.InterestsChoices.list()}
    gender = {'genderChoices': schemas.Gender.list()}

    return {
        'totalItems': len(df.index),
        **interests,
        **gender,
        'contacts': loads(df.to_json(orient='records', force_ascii=False))
    }


def get_number_of_contacts(db: Session, filter_zone: dict):
    return {
        'adherentCount': db.query(Contact).filter_by(**filter_zone).count(),
        'zoneName': list(filter_zone.values())[0]
    }
