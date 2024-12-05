#!/bin/sh

# run any outstanding migrations
python3 manage.py migrate --no-input || exit 1

# start the server using gunicorn
gunicorn

wait