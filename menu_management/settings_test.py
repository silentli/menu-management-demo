from .settings import *

# Override database settings for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'menu_management_test',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5433',
        'TEST': {
            'NAME': 'menu_management_test',
        },
    }
}

# Test-specific settings
DEBUG = False
SECRET_KEY = 'test-secret-key'
STAFF_PASSWORD = 'test_staff_password' 