import logging
import pytz
from astropy.time import Time
import requests

from .station import WeatherStation

log = logging.getLogger(__name__)


class Monet(WeatherStation):
    def __init__(self, url='https://monet.as.utexas.edu/', current=False, *args, **kwargs):
        WeatherStation.__init__(self, *args, **kwargs)
        self._url = url
        self._curent = current

    def create_sensors(self):
        self._add_sensor('temp')
        self._add_sensor('humid')
        self._add_sensor('winddir')
        self._add_sensor('windspeed')
        self._add_sensor('press')
        self._add_sensor('rain')

    def update(self):
        log.info('Updating MONET station %s...' % self._station.code)
        if self._curent:
            self._update_current()
        else:
            self._update_average()

    def _update_current(self):
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
        self._add_value('temp', time, weather['temp'])
        self._add_value('humid', time, weather['humid'])
        self._add_value('winddir', time, weather['winddir'])
        self._add_value('windspeed', time, weather['windspeed'])
        self._add_value('press', time, weather['press'])
        self._add_value('rain', time, weather['rain'])

    def _update_average(self):
        # do request
        r = requests.get(self._url + '?type=5min')

        # check code
        if r.status_code != 200:
            logging.error('Could not connect to McDonald weather station.')
            return

        # get weather
        weather = r.json()

        # get time
        time = Time(weather['time']).to_datetime(pytz.UTC)

        # got all values, now add them
        self._add_value('temp', time, weather['temp']['avg'])
        self._add_value('humid', time, weather['humid']['avg'])
        self._add_value('winddir', time, weather['winddir']['avg'])
        self._add_value('windspeed', time, weather['windspeed']['avg'])
        self._add_value('press', time, weather['press']['avg'])
        self._add_value('rain', time, weather['rain']['max'])


__all__ = ['Monet']
