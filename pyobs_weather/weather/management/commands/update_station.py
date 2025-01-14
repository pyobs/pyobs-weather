import json

from django.core.management.base import BaseCommand
from pyobs_weather.weather.models import Station
from pyobs_weather.weather.stations import Observer
from pyobs_weather.weather.utils import get_class


class Command(BaseCommand):
    help = "Update station manually"

    def add_arguments(self, parser):
        parser.add_argument("station", type=str, help="Name of station")

    def handle(self, *args, **options):
        # create station
        station = Station.objects.get(code=options["station"])

        # not active?
        if not station.active:
            return

        # get class and update station
        kls = get_class(station.class_name)
        obj = kls(**json.loads(station.kwargs), station=station)
        obj.update()
