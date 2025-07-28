import os

from django.apps import AppConfig


class PostConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'post'

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':
            from .beat_setup import create_periodic_task
            create_periodic_task()
