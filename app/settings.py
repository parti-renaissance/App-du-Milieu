"""
Settings to connect to the databases
"""
from os import environ
from dotenv import load_dotenv

load_dotenv()

DATABASE_CRM = {
    'DRIVER': environ["DB_DRIVER_CRM"],
    'USER': environ["DB_USER_CRM"],
    'PASS': environ["DB_PASS_CRM"],
    'NAME': environ["DB_NAME_CRM"],
    'HOST': environ["DB_HOST_CRM"],
    'PORT': environ["DB_PORT_CRM"]
}

DATABASE = {
    'DRIVER': environ["DB_DRIVER"],
    'USER': environ["DB_USER"],
    'PASS': environ["DB_PASS"],
    'NAME': environ["DB_NAME"],
    'HOST': environ["DB_HOST"],
    'PORT': environ["DB_PORT"]
}
