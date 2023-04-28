from django.apps import AppConfig


# from django.apps import AppConfig
class MainConfig(AppConfig):
    name = 'main'
    def ready(self):
        from . import signals