import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = eval(os.environ.get('DEBUG', 'False'))

if eval(os.environ.get('LOAD_PROD_SETTINGS', 'False')):
    from .settings_production import *
else:
    from .settings_development import *