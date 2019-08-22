import logging
from django.db import models
from django_celery_beat.models import CrontabSchedule, IntervalSchedule, PeriodicTask

log = logging.getLogger(__name__)


class Station(models.Model):
    """A weather station."""
    code = models.CharField('Code for weather station.', max_length=10, unique=True)
    name = models.CharField('Name of weather station.', max_length=50)
    module = models.CharField('Python module with an update() method to use for station.', max_length=50)
    crontab = models.ForeignKey(CrontabSchedule, on_delete=models.CASCADE, blank=True, null=True)
    interval = models.ForeignKey(IntervalSchedule, on_delete=models.CASCADE, blank=True, null=True)
    weight = models.FloatField('Weight for station in global average', default=1)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # if exists, delete old schedule
        try:
            # get current database object
            old = Station.objects.get(id=self.id)
            print("old", old)

            # find PeriodicTask and delete it
            try:
                print("delete")
                PeriodicTask.objects.filter(name=old.name).delete()
            except PeriodicTask.DoesNotExist:
                print("not deleted")
                pass

        except Station.DoesNotExist:
            print("no old")
            pass

        # actually save model
        models.Model.save(self, *args, **kwargs)

        # update periodic task
        PeriodicTask.objects.get_or_create(
            crontab=self.crontab,
            interval=self.interval,
            name=self.name,
            task='pyobs_weather.main.tasks.update_stations',
            args='["%s"]' % self.code
        )


class Weather(models.Model):
    """A line of weather information."""
    time = models.DateTimeField('Date and time of weather information')
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    temp = models.FloatField('Temperature in C', null=True, default=None)
    humid = models.FloatField('Humidity in percent', null=True, default=None)
    press = models.FloatField('Pressure in hPa', null=True, default=None)
    winddir = models.FloatField('Wind direction in degrees azimuth', null=True, default=None)
    windspeed = models.FloatField('Wind speed in km/h', null=True, default=None)
    rain = models.BooleanField('Raining', null=True, default=None)
    skytemp = models.FloatField('Sky  temperature in C', null=True, default=None)
    dewpoint = models.FloatField('Dew point in C', null=True, default=None)
    particles = models.FloatField('Particle count in particles per cubic m', null=True, default=None)


