import logging
from datetime import datetime
import pytz
from astropy.time import Time
import requests

from pyobs_weather.weather.models import Value, Sensor, SensorType

log = logging.getLogger(__name__)


class Monet:
    def __init__(self, url='https://monet.as.utexas.edu/?type=1min'):
        self._url = url

    @staticmethod
    def create_sensors(station):
        # get or create types
        type_temp, _ = SensorType.objects.get_or_create(code='temp', name='Temperature', unit='°C')
        type_humid, _ = SensorType.objects.get_or_create(code='humid', name='Relative humidity', unit='%')
        type_winddir, _ = SensorType.objects.get_or_create(code='winddir', name='Wind dir', unit='°E of N')
        type_windspeed, _ = SensorType.objects.get_or_create(code='windspeed', name='Wind speed', unit='km/h')
        type_rain, _ = SensorType.objects.get_or_create(code='rain', name='Raining', unit='0/1')

        # get or create sensors
        Sensor.objects.get_or_create(station=station, type=type_temp)
        Sensor.objects.get_or_create(station=station, type=type_humid)
        Sensor.objects.get_or_create(station=station, type=type_winddir)
        Sensor.objects.get_or_create(station=station, type=type_windspeed)
        Sensor.objects.get_or_create(station=station, type=type_rain)

    def update(self, station):
        log.info('Updating MONET station %s...' % station.code)

        # do request
        r = requests.get(self._url)

        # check code
        if r.status_code != 200:
            logging.error('Could not connect to McDonald weather station.')
            return

        # get weather
        weather = r.json()

        # get time
        time = Time(weather['time']).to_datetime(pytz.UTC)

        # got all values, now add them
        Value.objects.get_or_create(sensor=Sensor.objects.get(station=station, type__code='temp'),
                                    time=time, value=weather['temp'])
        Value.objects.get_or_create(sensor=Sensor.objects.get(station=station, type__code='humid'),
                                    time=time, value=weather['humid'])
        Value.objects.get_or_create(sensor=Sensor.objects.get(station=station, type__code='winddir'),
                                    time=time, value=weather['winddir'])
        Value.objects.get_or_create(sensor=Sensor.objects.get(station=station, type__code='windspeed'),
                                    time=time, value=weather['windspeed'])
        Value.objects.get_or_create(sensor=Sensor.objects.get(station=station, type__code='rain'),
                                    time=time, value=weather['rain'])
