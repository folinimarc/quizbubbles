import os

print('-----------------')
print('-- DEVELOPMENT --')
print('-----------------')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = True
SECRET_KEY = 'ftmn@^l6akz2-il4wrcl@q2@i*k_8kj&b2(j+$h9pv&ygq4%z7'
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# EMAIL BACKEND
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'mail')

# recaptcha
SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']