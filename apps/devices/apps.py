from django.apps import AppConfig
import threading
import os

class DevicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.devices'
    verbose_name = 'Devices'

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true' and threading.current_thread().name == "MainThread":
            from .scheduler import start
            start()