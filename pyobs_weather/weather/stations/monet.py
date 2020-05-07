import logging
import pytz
from astropy.time import Time
import requests

from .station import WeatherStation

log = logging.getLogger(__name__)


class Monet(WeatherStation):
    """The Monet weather station reads current weather information from a ThiesWS weather station."""

    def __init__(self, url='https://monet.as.utexas.edu/', current=False, *args, **kwargs):
        """Initializes a new Monet weather station.

        The URLs should be:

        - https://monet.saao.ac.za/ for Monet/S

        - https://monet.as.utexas.edu/ for Monet/N

        Args:
            url: URL of Monet weather station.
            current: If True, latest values are fetched, otherwise a 5-minute average.
        """

        WeatherStation.__init__(self, *args, **kwargs)
        self._url = url
        self._current = current

    def create_sensors(self):
        """Entry point for creating sensors for this station.

        These sensors are created:

        - temp

        - humid

        - winddir

        - windspeed

        - press

        - rain"""
        self._add_sensor('temp')
        self._add_sensor('humid')
        self._add_sensor('winddir')
        self._add_sensor('windspeed')
        self._add_sensor('press')
        self._add_sensor('rain')

    def update(self):
        """Entry point for updating sensor values for this station.

        This method reads the current weather information from Monet weather homepage."""
        log.info('Updating MONET station %s...' % self._station.code)
        if self._current:
            self._update_current()
        else:
            self._update_average()

    def _update_current(self):
        """Fetch and update latest values."""

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
        #self._add_value('press', time, weather['press'])
        self._add_value('rain', time, weather['rain'])

    def _update_average(self):
        """Fetch and update average values."""

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
        #self._add_value('press', time, weather['press']['avg'])
        self._add_value('rain', time, weather['rain']['max'])


__all__ = ['Monet']
