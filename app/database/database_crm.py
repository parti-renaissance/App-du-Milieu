from os import environ
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import as_declarative

# Local
# engine_crm = create_engine('sqlite:///local_database/enmarche_crm.db')


# GCP
CLOUDSQL_USER = environ["DB_USER"]
CLOUDSQL_PASS = environ["DB_PASS"]
CLOUDSQL_NAME = environ["DB_NAME"]
CLOUDSQL_CONN = environ["CLOUDSQL_CONN"]

engine_crm = create_engine(
    URL(
        drivername="mysql+pymysql",
        username=CLOUDSQL_USER,
        password=CLOUDSQL_PASS,
        database=CLOUDSQL_NAME,
        query={
            "unix_socket": "/cloudsql/{}".format(CLOUDSQL_CONN)
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
