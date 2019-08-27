import json

from django.core.management.base import BaseCommand
from pyobs_weather.weather.models import Station
from pyobs_weather.weather.stations import Observer


class Command(BaseCommand):
    help = 'Test observer station'

    def handle(self, *args, **options):
        # create station
        station = Station.objects.get(code='observer')

        # add types
        obs = Observer(**json.loads(station.kwargs))
        obs.update(station)
