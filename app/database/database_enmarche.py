from os import environ
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import as_declarative

# Local
# engine_read_only = create_engine('sqlite:///local_database/enmarche.db')


# GCP
CLOUDSQL_USER = environ["DB_USER"]
CLOUDSQL_PASS = environ["DB_PASS"]
CLOUDSQL_READ = environ["DB_READ"]
CLOUDSQL_CONN = environ["CLOUDSQL_CONN"]

engine_read_only = create_engine(
    URL(
        drivername="mysql+pymysql",
        username=CLOUDSQL_USER,
        password=CLOUDSQL_PASS,
        database=CLOUDSQL_READ,
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
class Base:
    def __init__(self):
        metadata.create_all(bind=engine_read_only)
    pass