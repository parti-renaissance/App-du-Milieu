from os import environ
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.log import echo_property

# Local
# engine_crm = create_engine('sqlite:///local_database/enmarche_crm.db')


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
            "host": "/cloudsql/{}/.s.PGSQL.5432".format(CLOUDSQL_CONN)
        }
    ),
    pool_size=5,
    pool_timeout=30,
    pool_recycle=1800,
    max_overflow=2,
    echo=True
)

@as_declarative()
class CRM:
    def __init__(self):
        metadata.create_all(bind=engine_crm)
    pass
