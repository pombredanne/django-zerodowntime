DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'zerodowntime',
    'tests.safe_migrations',
]

SECRET_KEY = 'spam-spam-spam-spam'

SILENCED_SYSTEM_CHECKS = ('1_7.W001',)
