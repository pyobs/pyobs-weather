from django.core.management.base import BaseCommand
from astropy.time import Time

from pyobs_weather.weather.models import GoodWeather


class Command(BaseCommand):
    help = 'Dump good weather status to command line as CSV'

    def handle(self, *args, **options):
        # header
        print('datetime,good')

        # loop good status
        for good in GoodWeather.objects.order_by('time').all():
            t = Time(good.time)
            print(f'{t.isot},{good.good}')
