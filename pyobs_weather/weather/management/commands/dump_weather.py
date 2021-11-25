from astropy.time import Time
from django.core.management.base import BaseCommand
from django_celery_beat.schedulers import CrontabSchedule, IntervalSchedule, PeriodicTask

from pyobs_weather.weather.models import Station, Value, SensorType


class Command(BaseCommand):
    help = 'Init pyobs-weather'

    def add_arguments(self, parser):
        parser.add_argument('-s', '--start', type=str, help='Start date to dump')
        parser.add_argument('-e', '--end', type=str, help='End date to dump')

    def handle(self, start: str, end: str, *args, **options):
        # get average station
        station = Station.objects.filter(code='average').first()

        # get all sensor types and print header
        sensor_types = [st.code for st in SensorType.objects.all()]
        print('datetime,' + ','.join(sensor_types))

        # get all timestamps for station in range
        query = Value.objects.filter(sensor__station=station)
        if start is not None:
            query = query.filter(time__gte=start)
        if end is not None:
            query = query.filter(time__lte=end)
        timestamps = query.order_by('time').values_list('time', flat=True)

        # now loop all times
        for t in timestamps:
            # get all values
            values = dict(Value.objects.filter(sensor__station=station, time=t)
                          .values_list('sensor__type__code', 'value').all())

            # dump it in correct order
            line = Time(t).isot
            for st in sensor_types:
                line += ','
                if st in values and values[st] is not None:
                    line += str(values[st])
            print(line)
