import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = eval(os.environ.get('DEBUG', 'False'))

if eval(os.environ.get('NONDJANGO_DEBUG', 'False')) or DEBUG:
    from .settings_development import *
else:
    from .settings_production import *