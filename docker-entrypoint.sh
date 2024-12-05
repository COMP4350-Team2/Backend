#!/bin/sh

# collect all static files to the root directory
python3 manage.py collectstatic --no-input || exit 1

# run any outstanding migrations
python3 manage.py migrate --no-input || exit 1

# start the server using gunicorn
gunicorn

wait