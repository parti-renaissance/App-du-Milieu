import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DATABASE_HOST = os.environ.get("DB_HOST")
DATABASE_NAME = os.environ.get("DB_NAME")
DATABASE_USER = os.environ.get("DB_USER")
DATABASE_PASSWORD = os.environ.get("DB_PASS")
