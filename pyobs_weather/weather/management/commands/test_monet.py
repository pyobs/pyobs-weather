from django.core.management.base import BaseCommand
from pyobs_weather.weather.models import Station
from pyobs_weather.weather.stations import Monet


class Command(BaseCommand):
    help = 'Test monet station'

    def handle(self, *args, **options):
        # create station
        station = Station.objects.get(code='monet')

        # add types
        Monet.update(station)
