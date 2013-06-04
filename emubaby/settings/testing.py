from emubaby.settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '/tmp/emubaby_test.db',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

ORG_NAME = "MindSnacks"

TEST_RUNNER = 'rainbowtests.RainbowTestSuiteRunner'

SOUTH_TESTS_MIGRATE = False