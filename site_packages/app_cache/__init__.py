from django.core.exceptions import ImproperlyConfigured
from django import VERSION

if VERSION[0]<1 and VERSION[1]<7:
    raise ImproperlyConfigured("""
        The app_config required 1.7 or higher version of django.
        """)

from .core import AppCache