import logging
from django.db import models

log = logging.getLogger(__name__)


class Weather(models.Model):
    """A line of weather information."""
    time = models.DateTimeField('Date and time of weather information')
    station = models.CharField('Name of weather station', max_length=10)
    temp = models.FloatField('Temperature in C', null=True, default=None)
    humid = models.FloatField('Humidity in percent', null=True, default=None)
    press = models.FloatField('Pressure in hPa', null=True, default=None)
    winddir = models.FloatField('Wind direction in degrees azimuth', null=True, default=None)
    windspeed = models.FloatField('Wind speed in km/h', null=True, default=None)
    rain = models.BooleanField('Raining', null=True, default=None)
    skytemp = models.FloatField('Sky  temperature in C', null=True, default=None)
    dewpoint = models.FloatField('Dew point in C', null=True, default=None)
    particles = models.FloatField('Particle count in particles per cubic m', null=True, default=None)
