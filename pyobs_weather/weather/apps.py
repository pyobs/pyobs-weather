from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'pyobs_weather.weather'

    def ready(self):
        from pyobs_weather.settings import USE_INFLUX
        if USE_INFLUX:
            from . import influx
            influx.get_client()