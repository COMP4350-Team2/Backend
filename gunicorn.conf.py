import os
import multiprocessing

from utils.env_helper import load_env_variables

MAX_TIMEOUT = 120

if os.getenv('LAYER') == 'DEV':
    max_workers = 1
else:
    max_workers = multiprocessing.cpu_count()


load_env_variables()

wsgi_app = 'cupboard_backend.wsgi'
workers = max_workers
timeout = MAX_TIMEOUT
bind = f'{os.getenv('DJANGO_ADDRESS')}:{os.getenv('DJANGO_PORT')}'
