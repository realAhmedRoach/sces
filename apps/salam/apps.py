from django.apps import AppConfig


class SalamConfig(AppConfig):
    name = 'apps.salam'

    def ready(self):
        import apps.salam.signals  # noqa
