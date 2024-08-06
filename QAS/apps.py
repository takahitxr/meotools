from django.apps import AppConfig


class QASConfig(AppConfig):
    name = 'QAS'

    def ready(self):
        import QAS.signals