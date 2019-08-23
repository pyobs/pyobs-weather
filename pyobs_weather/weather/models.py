import json
import logging
from django.db import models
from django_celery_beat.models import CrontabSchedule, IntervalSchedule, PeriodicTask


log = logging.getLogger(__name__)


class Evaluator(models.Model):
    """A sensor evaluator."""
    name = models.CharField('Name of evaluator', max_length=15, unique=True)
    class_name = models.CharField('Python class to call', max_length=50)
    kwargs = models.CharField('JSON encoded kwargs to pass to constructor.', max_length=50, blank=True, null=True)

    def __str__(self):
        params = ['%s=%s' % (k, str(v)) for k, v in json.loads(self.kwargs).items()] if self.kwargs else ''
        return self.name + ': ' + self.class_name + '(' + ', '.join(params) + ')'


class Station(models.Model):
    """A weather station."""
    code = models.CharField('Code for weather station.', max_length=10, unique=True)
    name = models.CharField('Name of weather station.', max_length=50)
    module = models.CharField('Python module with an update() method to use for station.', max_length=50)
    crontab = models.ForeignKey(CrontabSchedule, on_delete=models.CASCADE, blank=True, null=True)
    interval = models.ForeignKey(IntervalSchedule, on_delete=models.CASCADE, blank=True, null=True)
    weight = models.FloatField('Weight for station in global average', default=1)
    history = models.BooleanField('Whether to keep more than one point.', default=True)
    active = models.BooleanField('Whether station is currently active.', default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
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

        # actually save model
        models.Model.save(self, *args, **kwargs)


class SensorType(models.Model):
    """A sensor type."""
    code = models.CharField('Code for sensor type', max_length=10, unique=True)
    name = models.CharField('Name of sensor type', max_length=50)
    unit = models.CharField('Unit for value', max_length=5)

    def __str__(self):
        return '%s (%s)' % (self.name, self.code)


class Sensor(models.Model):
    """A sensor."""
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    type = models.ForeignKey(SensorType, on_delete=models.CASCADE)
    evaluators = models.ManyToManyField(Evaluator)
    good = models.BooleanField('Whether the evaluators currently claim this sensor to be good', blank=True, null=True)
    since = models.DateTimeField('Time the good parameter last changed', blank=True, null=True)
    delay_good = models.IntegerField('Delay in seconds before switching to good weather.', default=0)
    delay_bad = models.IntegerField('Delay in seconds before switching to bad weather.', default=0)
    bad_since = models.DateTimeField('Time of last bad sensor value', blank=True, null=True)
    good_since = models.DateTimeField('Time of last good sensor value', blank=True, null=True)
    active = models.BooleanField('Whether evaluator is currently active', default=True)

    def __str__(self):
        return self.station.name + ': ' + self.type.name

    class Meta:
        unique_together = ('station', 'type')


class Weather(models.Model):
    """A line of weather information."""
    time = models.DateTimeField('Date and time of weather information')
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    temp = models.FloatField('Temperature in C', null=True, blank=True)
    humid = models.FloatField('Humidity in percent', null=True, blank=True)
    press = models.FloatField('Pressure in hPa', null=True, blank=True)
    winddir = models.FloatField('Wind direction in degrees azimuth', null=True, blank=True)
    windspeed = models.FloatField('Wind speed in km/h', null=True, blank=True)
    rain = models.BooleanField('Raining', null=True, blank=True)
    skytemp = models.FloatField('Sky  temperature in C', null=True, blank=True)
    dewpoint = models.FloatField('Dew point in C', null=True, blank=True)
    particles = models.FloatField('Particle count in particles per cubic m', null=True, blank=True)

    def save(self, *args, **kwargs):
        # actually save model
        models.Model.save(self, *args, **kwargs)

        # if station doesn't want to keep history, delete old
        if not self.station.history:
            Weather.objects.filter(time__lt=self.time, station=self.station).delete()
