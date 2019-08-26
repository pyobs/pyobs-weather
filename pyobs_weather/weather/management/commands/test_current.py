from django.core.management.base import BaseCommand
from pyobs_weather.weather.models import Station
from pyobs_weather.weather.stations import Current


class Command(BaseCommand):
    help = 'Test current station'

    def handle(self, *args, **options):
        # create station
        station = Station.objects.get(code='current')

        # add types
        Current.update(station)
