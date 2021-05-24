from os import environ
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import as_declarative

# Local
# engine_crm = create_engine('sqlite:///local_database/enmarche_crm.db')


# GCP
CLOUDSQL_USER_PG = environ["DB_USER"]
CLOUDSQL_PASS_PG = environ["DB_PASS"]
CLOUDSQL_NAME_PG = environ["DB_NAME"]
CLOUDSQL_CONN_PG = environ["CLOUDSQL_CONN"]

engine_crm = create_engine(
    URL(
        drivername="postgresql+psycopg2",
        username=CLOUDSQL_USER_PG,
        password=CLOUDSQL_PASS_PG,
        database=CLOUDSQL_NAME_PG,
        query={
            "unix_socket": "/cloudsql/{}".format(CLOUDSQL_CONN_PG)
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
