import os

from dotenv import load_dotenv
from django.core.management.utils import get_random_secret_key


def generate_secret() -> str:
    """
    Generates the DJANGO_SECRET_KEY

    Returns:
        Newly generated DJANGO secret key
    """
    secret_key = get_random_secret_key()
    return secret_key


def load_env_variables():
    """
    Loads Environment variables from .env file
    """
    # Reads the .env file and loads the values
    load_dotenv()

    # Sets default Django settings module
    os.environ['DJANGO_SETTINGS_MODULE'] = 'cupboard_backend.settings'
