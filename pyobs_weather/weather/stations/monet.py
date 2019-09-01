import logging
from datetime import datetime
import pytz
from astropy.time import Time
import requests

from .station import WeatherStation
from pyobs_weather.weather.models import Value, Sensor, SensorType

log = logging.getLogger(__name__)


class Monet(WeatherStation):
    def __init__(self, url='https://monet.as.utexas.edu/', current=False):
        self._url = url
        self._curent = current

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
        if self._curent:
            self._update_current(station)
        else:
            self._update_average(station)

    def _update_current(self, station):
        # do request
        r = requests.get(self._url + '?type=current')

        # check code
        if r.status_code != 200:
            logging.error('Could not connect to McDonald weather station.')
            return

        # get weather
        weather = r.json()

        # get time
        time = Time(weather['time']).to_datetime(pytz.UTC)

        # got all values, now add them
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='temp'),
                                  time=time, value=weather['temp'])
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='humid'),
                                  time=time, value=weather['humid'])
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='winddir'),
                                  time=time, value=weather['winddir'])
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='windspeed'),
                                  time=time, value=weather['windspeed'])
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='rain'),
                                  time=time, value=weather['rain'])

    def _update_average(self, station):
        # do request
        r = requests.get(self._url + '?type=1min')

        # check code
        if r.status_code != 200:
            logging.error('Could not connect to McDonald weather station.')
            return

        # get weather
        weather = r.json()

        # get time
        time = Time(weather['time']).to_datetime(pytz.UTC)

        # got all values, now add them
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='temp'),
                                  time=time, value=weather['temp']['avg'])
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='humid'),
                                  time=time, value=weather['humid']['avg'])
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='winddir'),
                                  time=time, value=weather['winddir']['avg'])
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='windspeed'),
                                  time=time, value=weather['windspeed']['avg'])
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='rain'),
                                  time=time, value=weather['rain']['max'])
