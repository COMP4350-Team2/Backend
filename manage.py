#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from django.core.management.commands.runserver import Command as runserver

from utils.env_helper import load_env_variables


def main():
    """Run administrative tasks."""
    # Reads the .env file and loads all the values
    load_env_variables()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Override default port for `runserver` command
    runserver.default_addr = os.getenv('DJANGO_ADDRESS')
    runserver.default_port = os.getenv('DJANGO_PORT')
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
