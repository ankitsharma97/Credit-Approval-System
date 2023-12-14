# credit_app/__init__.py
from __future__ import absolute_import, unicode_literals

# Import the Celery application instance created in celery.py
from .celery import app as celery_app

__all__ = ('celery_app',)
