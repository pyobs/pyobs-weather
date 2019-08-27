import json
import logging
from django.db import models
from django_celery_beat.models import CrontabSchedule, IntervalSchedule, PeriodicTask

from pyobs_weather.weather.utils import get_class

log = logging.getLogger(__name__)


class Evaluator(models.Model):
    """A sensor evaluator."""
    name = models.CharField('Name of evaluator', max_length=15, unique=True)
    class_name = models.CharField('Python class to call', max_length=50)
    kwargs = models.CharField('JSON encoded kwargs to pass to constructor', max_length=50, blank=True, null=True)

    def __str__(self):
        params = ['%s=%s' % (k, str(v)) for k, v in json.loads(self.kwargs).items()] if self.kwargs else ''
        return self.name + ': ' + self.class_name + '(' + ', '.join(params) + ')'


class Station(models.Model):
    """A weather station."""
    code = models.CharField('Code for weather station', max_length=10, unique=True)
    name = models.CharField('Name of weather station', max_length=50)
    class_name = models.CharField('Name of Python class to handle station', max_length=100)
    kwargs = models.CharField('JSON encoded kwargs used when instantiating Python class', max_length=100, default='{}')
    crontab = models.ForeignKey(CrontabSchedule, on_delete=models.CASCADE, blank=True, null=True)
    interval = models.ForeignKey(IntervalSchedule, on_delete=models.CASCADE, blank=True, null=True)
    weight = models.FloatField('Weight for station in global average', default=1)
    history = models.BooleanField('Whether to keep more than one point', default=True)
    active = models.BooleanField('Whether station is currently active', default=True)
    plot = models.BooleanField('Add station to plots', default=True)
    color = models.CharField('Plot color', max_length=10, default='black')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # actually save model
        models.Model.save(self, *args, **kwargs)

        # create sensors for station
        station_class = get_class(self.class_name)
        station_class.create_sensors(self)

        # if exists, delete old schedule
        try:
            # get current database object
            old = Station.objects.get(id=self.id)

            # find PeriodicTask and delete it
            try:
                PeriodicTask.objects.filter(name=old.name).delete()
            except PeriodicTask.DoesNotExist:
                pass

        except Station.DoesNotExist:
            pass

        # update periodic task
        PeriodicTask.objects.get_or_create(
            crontab=self.crontab,
            interval=self.interval,
            name=self.name,
            task='pyobs_weather.weather.tasks.update_stations',
            args='["%s"]' % self.code
        )


class SensorType(models.Model):
    """A sensor type."""
    code = models.CharField('Code for sensor type', max_length=10, unique=True)
    name = models.CharField('Name of sensor type', max_length=50)
    unit = models.CharField('Unit for value', max_length=5)
    average = models.BooleanField('Calculate average for this type', default=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.code)


class Sensor(models.Model):
    """A sensor."""
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    type = models.ForeignKey(SensorType, on_delete=models.CASCADE)
    evaluators = models.ManyToManyField(Evaluator, blank=True)
    good = models.BooleanField('Whether its current value was evaluated as good', blank=True, null=True)
    since = models.DateTimeField('Time the good parameter last changed', blank=True, null=True)
    delay_good = models.IntegerField('Delay in seconds before switching to good weather', default=0)
    delay_bad = models.IntegerField('Delay in seconds before switching to bad weather', default=0)
    bad_since = models.DateTimeField('Time of last bad sensor value', blank=True, null=True)
    good_since = models.DateTimeField('Time of last good sensor value', blank=True, null=True)
    active = models.BooleanField('Whether evaluator is currently active', default=True)

    def __str__(self):
        return self.station.name + ': ' + self.type.name

    class Meta:
        unique_together = ('station', 'type')


class Value(models.Model):
    """A single value from a sensor."""
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    time = models.DateTimeField('Date and time when value was measured')
    value = models.FloatField('Measured value', null=True, blank=True)

    def save(self, *args, **kwargs):
        # actually save model
        models.Model.save(self, *args, **kwargs)

        # if station doesn't want to keep history, delete old
        if not self.sensor.station.history:
            Value.objects.filter(time__lt=self.time, sensor=self.sensor).delete()
