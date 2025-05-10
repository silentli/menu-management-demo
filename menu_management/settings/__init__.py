"""
Settings package initialization.
"""

import os

# Use base settings by default
from .base import *

# Override with production settings if DJANGO_ENV is set to 'production'
if os.environ.get('DJANGO_ENV') == 'production':
    from .production import *
