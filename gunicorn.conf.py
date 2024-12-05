import os
import multiprocessing

from utils.env_helper import load_env_variables

MAX_TIMEOUT = 120

if os.getenv('LAYER') == 'DEV':
    max_workers = 1
else:
    # Optimal recommendation from gunicorn
    max_workers = (2 * multiprocessing.cpu_count()) + 1


load_env_variables()

wsgi_app = 'cupboard_backend.wsgi'
workers = max_workers
timeout = MAX_TIMEOUT
bind = '{address}:{port}'.format(
    address=os.getenv('DJANGO_ADDRESS'),
    port=os.getenv('DJANGO_PORT')
)
