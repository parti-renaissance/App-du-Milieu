from os import environ
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import as_declarative

"""
# local
from app.settings import DATABASE_CRM as DB_SETTINGS
engine_crm = create_engine(
    URL.create(
        drivername=DB_SETTINGS['DRIVER'],
        username=DB_SETTINGS['USER'],
        password=DB_SETTINGS['PASS'],
        database=DB_SETTINGS['NAME'],
        host=DB_SETTINGS['HOST'],
        port=DB_SETTINGS['PORT']
    )
)
"""
# GCP
CLOUDSQL_USER = environ["DB_USER_PG"]
CLOUDSQL_PASS = environ["DB_PASS_PG"]
CLOUDSQL_NAME = environ["DB_NAME_PG"]
CLOUDSQL_CONN = environ["CLOUDSQL_CONN_PG"]

engine_crm = create_engine(
    URL.create(
        drivername="postgresql+psycopg2",
        username=CLOUDSQL_USER,
        password=CLOUDSQL_PASS,
        database=CLOUDSQL_NAME,
        query={
            "host": "/cloudsql/{}".format(CLOUDSQL_CONN)
        }
    ),
    pool_size=5,
    pool_timeout=30,
    pool_recycle=1800,
    max_overflow=2
)

@as_declarative()
class CRM:
    def __init__(self):
        metadata.create_all(bind=engine_crm)
    pass
