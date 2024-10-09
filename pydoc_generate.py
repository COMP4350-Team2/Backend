import pydoc
import django
from utils.env_helper import load_env_variables

# Running command: python pydoc_generate.py -w cupboard_app.views

# Reads the .env file and loads all the values
load_env_variables()
# Prepare Django before executing pydoc command
django.setup()

# Now executing pydoc
pydoc.cli()

print('Remember to remove the data section of the generated pydoc before committing.')
