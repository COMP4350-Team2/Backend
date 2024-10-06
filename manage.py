#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from dotenv import load_dotenv
from django.core.management.commands.runserver import Command as runserver


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cupboard_backend.settings')

    # Reads the .env file and loads the values
    load_dotenv()

    # Set mock environment variables
    os.environ.setdefault('MOCK_KEY', 'cupboard_secret')
    os.environ.setdefault('MOCK_DOMAIN', 'my-domain.ca.auth0.com')
    os.environ.setdefault('MOCK_API_IDENTIFIER', 'https://api.example.com')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Override default port for `runserver` command, use 8000 if not set
    runserver.default_port = os.getenv('DJANGO_PORT', '8000')

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
