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
    if (
        os.getenv('DJANGO_SETTINGS_MODULE') == ''
        or os.getenv('DJANGO_SETTINGS_MODULE') is None
    ):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'cupboard_backend.settings'

    if (
        os.getenv('DJANGO_SECRET_KEY') == ''
        or os.getenv('DJANGO_SECRET_KEY') is None
    ):
        os.environ['DJANGO_SECRET_KEY'] = 'django-insecure-{}'.format(generate_secret())

    if os.getenv('DJANGO_PORT') == '' or os.getenv('DJANGO_PORT') is None:
        os.environ['DJANGO_PORT'] = '6060'

    if os.getenv('REACT_CLIENT_ORIGIN_URL') == '' or os.getenv('REACT_CLIENT_ORIGIN_URL') is None:
        os.environ['REACT_CLIENT_ORIGIN_URL'] = 'http://localhost:8080'

    if os.getenv('CUPBOARD_TEST_CLIENT_ID') == '' or os.getenv('CUPBOARD_TEST_CLIENT_ID') is None:
        os.environ['CUPBOARD_TEST_CLIENT_ID'] = ''

    if (
        os.getenv('CUPBOARD_TEST_CLIENT_SECRET') == ''
        or os.getenv('CUPBOARD_TEST_CLIENT_SECRET') is None
    ):
        os.environ['CUPBOARD_TEST_CLIENT_SECRET'] = ''

    if os.getenv('DEV_LAYER') == '' or os.getenv('DEV_LAYER') is None:
        os.environ['DEV_LAYER'] = 'mock'

    if os.getenv('DEBUG_ENABLE') == '' or os.getenv('DEBUG_ENABLE') is None:
        os.environ['DEBUG_ENABLE'] = 'true'

    if os.getenv('TEST_RUN') == '' or os.getenv('TEST_RUN') is None:
        os.environ['TEST_RUN'] = 'true'

    if os.getenv('TEST_KEY') == '' or os.getenv('TEST_KEY') is None:
        os.environ['TEST_KEY'] = 'cupboard_secret'

    if (
        os.getenv('AUTHLIB_INSECURE_TRANSPORT') == ''
        or os.getenv('AUTHLIB_INSECURE_TRANSPORT') is None
    ):
        os.environ['AUTHLIB_INSECURE_TRANSPORT'] = 'true'

    if os.getenv('AUTH0_DOMAIN') == '' or os.getenv('AUTH0_DOMAIN') is None:
        os.environ['AUTH0_DOMAIN'] = 'my-domain.ca.auth0.com'

    if os.getenv('AUTH0_API_IDENTIFIER') == '' or os.getenv('AUTH0_API_IDENTIFIER') is None:
        os.environ['AUTH0_API_IDENTIFIER'] = 'https://api.example.com'

    if os.getenv('DB_NAME') == '' or os.getenv('DB_NAME') is None:
        os.environ['DB_NAME'] = 'DCupboardDB'

    if os.getenv('DB_TEST_NAME') == '' or os.getenv('DB_TEST_NAME') is None:
        os.environ['DB_TEST_NAME'] = 'test_DCupboardDB'

    if os.getenv('MONGO_URL') == '' or os.getenv('MONGO_URL') is None:
        os.environ['MONGO_URL'] = ''

    print('DB_NAME: "{}"'.format(os.getenv('DB_NAME')))
