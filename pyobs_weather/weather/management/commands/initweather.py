from django.core.management.base import BaseCommand
from django_celery_beat.schedulers import IntervalSchedule, PeriodicTask

from pyobs_weather.settings import INFLUXDB_MEASUREMENT_AVERAGE
from pyobs_weather.weather.models import Station, Evaluator


class Command(BaseCommand):
    help = "Init pyobs-weather"

    def handle(self, *args, **options):
        # create average station
        interval, _ = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)
        if Station.objects.filter(code=INFLUXDB_MEASUREMENT_AVERAGE).count() == 0:
            Station.objects.get_or_create(
                code=INFLUXDB_MEASUREMENT_AVERAGE,
                name="Average values",
                class_name="pyobs_weather.weather.stations.Average",
                interval=interval,
            )

        # create observer station
        interval, _ = IntervalSchedule.objects.get_or_create(every=30, period=IntervalSchedule.SECONDS)
        interval.save()
        if Station.objects.filter(code="observer").count() == 0:
            Station.objects.get_or_create(
                code="observer",
                name="Observer",
                class_name="pyobs_weather.weather.stations.Observer",
                interval=interval,
                history=False,
            )

        # create interval for evaluation
        interval, _ = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS)
        PeriodicTask.objects.get_or_create(
            interval=interval,
            name="Evaluate sensor goodness",
            task="pyobs_weather.weather.tasks.evaluate",
        )

        # add some default evaluators
        Evaluator.objects.get_or_create(
            name="humid",
            class_name="pyobs_weather.weather.evaluators.SchmittTrigger",
            kwargs='{"good": 80, "bad": 85}',
        )
        Evaluator.objects.get_or_create(
            name="windspeed",
            class_name="pyobs_weather.weather.evaluators.SchmittTrigger",
            kwargs='{"good": 35, "bad": 45}',
        )
        Evaluator.objects.get_or_create(
            name="rain",
            class_name="pyobs_weather.weather.evaluators.Boolean",
            kwargs='{"invert": true}',
        )
        Evaluator.objects.get_or_create(
            name="valid",
            class_name="pyobs_weather.weather.evaluators.Valid",
            kwargs="{}",
        )
        Evaluator.objects.get_or_create(
            name="night",
            class_name="pyobs_weather.weather.evaluators.Switch",
            kwargs='{"threshold": 0}',
        )
