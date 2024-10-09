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
    # Reads the .env file and loads the values
    load_dotenv()

    # Set defaults for all the environment variables in case user doesn't have
    # .env file
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cupboard_backend.settings')
    os.environ.setdefault('DJANGO_SECRET_KEY', 'django-insecure-{}'.format(generate_secret()))
    os.environ.setdefault('DJANGO_PORT', '8000')
    os.environ.setdefault('REACT_CLIENT_ORIGIN_URL', 'http://localhost:8080')
    os.environ.setdefault('CUPBOARD_TEST_CLIENT_ID', '')
    os.environ.setdefault('CUPBOARD_TEST_CLIENT_SECRET', '')
    os.environ.setdefault('DEV_LAYER', 'mock')
    os.environ.setdefault('DEBUG_ENABLE', 'true')
    os.environ.setdefault('TEST_RUN', 'true')
    os.environ.setdefault('TEST_KEY', 'cupboard_secret')
    os.environ.setdefault('AUTHLIB_INSECURE_TRANSPORT', 'true')
    os.environ.setdefault('AUTH0_DOMAIN', 'my-domain.ca.auth0.com')
    os.environ.setdefault('AUTH0_API_IDENTIFIER', 'https://api.example.com')
    os.environ.setdefault('MONGO_URL', '')
