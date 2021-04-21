from os import environ
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import sessionmaker

# Local
# engine_crm = create_engine('sqlite:///local_database/enmarche_crm.db')
# engine_read_only = create_engine('sqlite:///local_database/enmarche.db')


# GCP
CLOUDSQL_USER = environ["DB_USER"]
CLOUDSQL_PASS = environ["DB_PASS"]
CLOUDSQL_READ = environ["DB_READ"]
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
class CRM:
    pass

@as_declarative()
class Base:
    pass

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False)
SessionLocal.configure(binds={CRM: engine_crm, Base: engine_read_only})
