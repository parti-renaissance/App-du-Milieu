from os import environ
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Local
# SQLALCHEMY_DATABASE_URL = "sqlite:///test_contacts.db"

# GCP
CLOUDSQL_USER = environ["DB_USER"]
CLOUDSQL_PASS = environ["DB_PASS"]
CLOUDSQL_NAME = environ["DB_NAME"]
CLOUDSQL_CONN = environ["CLOUD_SQL_CONNECTION_NAME"]

engine = create_engine(
    URL(
        drivername="mysql+pymysql",
        username=CLOUDSQL_USER,
        password=CLOUDSQL_PASS,
        database=CLOUDSQL_NAME,
        query={
            "unix_socket": "/cloudsql/{}".format(CLOUDSQL_CONN)
        }
    ),
    connect_args={"check_same_thread": False},
    pool_size=5,
    pool_timeout=30,
    pool_recycle=1800,
    max_overflow=2
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
