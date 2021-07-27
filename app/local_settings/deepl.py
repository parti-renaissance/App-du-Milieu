from os import environ
from dotenv import load_dotenv

load_dotenv()

DEEPL = {
    'DEEP_IA_KEY': environ.get("DEEP_IA_KEY", None),
    'DEEPL_KEY': environ.get("DEEPL_KEY", None)
}
