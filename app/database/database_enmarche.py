from os import environ

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import as_declarative

"""
# local
from app.settings import DATABASE as DB_SETTINGS
engine_read_only = create_engine(
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
CLOUDSQL_USER = environ["DB_USER"]
CLOUDSQL_PASS = environ["DB_PASS"]
CLOUDSQL_READ = environ["DB_READ"]
CLOUDSQL_CONN = environ["CLOUDSQL_CONN"]

engine_read_only = create_engine(
    URL.create(
        drivername="mysql+pymysql",
        username=CLOUDSQL_USER,
        password=CLOUDSQL_PASS,
        database=CLOUDSQL_READ,
        query={"unix_socket": "/cloudsql/{}".format(CLOUDSQL_CONN)},
    ),
    pool_size=5,
    pool_timeout=30,
    pool_recycle=1800,
    max_overflow=2,
)


@as_declarative()
class Base:
    pass
