from os import environ
from dotenv import load_dotenv

load_dotenv()

DATABASE_CRM = {
    'DRIVER': environ.get("DB_DRIVER_CRM", None),
    'USER': environ.get("DB_USER_CRM", None),
    'PASS': environ.get("DB_PASS_CRM", None),
    'NAME': environ.get("DB_NAME_CRM", None),
    'HOST': environ.get("DB_HOST_CRM", None),
    'PORT': environ.get("DB_PORT_CRM", None)
}

DATABASE = {
    'DRIVER': environ.get("DB_DRIVER", None),
    'USER': environ.get("DB_USER", None),
    'PASS': environ.get("DB_PASS", None),
    'NAME': environ.get("DB_NAME", None),
    'HOST': environ.get("DB_HOST", None),
    'PORT': environ.get("DB_PORT", None)
}
