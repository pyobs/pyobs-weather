from django.core.management.base import BaseCommand
from pyobs_weather.weather.models import Station
from pyobs_weather.weather.stations import MySQL


class Command(BaseCommand):
    help = 'Test mysql station'

    def handle(self, *args, **options):
        # create station
        station = Station.objects.get(code='mysql')

        # add types
        MySQL.update(station)
