from django.apps import AppConfig

class APIAppConfig(AppConfig):

    name = 'api'
    verbose_name = 'Application Programming Interfaces'

    def ready(self):
        import core