"""
Test settings for menu_management project.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from .base import *

# Load environment variables from .env.test file
env_path = Path(__file__).resolve().parent / 'env' / '.env.test'
load_dotenv(dotenv_path=env_path)

# Test-specific settings
DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'test-secret-key')
STAFF_PASSWORD = os.environ.get('STAFF_PASSWORD', 'test_staff_password')

# Test database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'menu_management_test'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5433'),
        'TEST': {
            'NAME': os.environ.get('POSTGRES_DB', 'menu_management_test'),
        },
    }
}
