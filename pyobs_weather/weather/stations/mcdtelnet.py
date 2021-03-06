import logging
from telnetlib import Telnet
from datetime import datetime

from .station import WeatherStation

log = logging.getLogger(__name__)


class McDonaldTelnet(WeatherStation):
    """The McDonaldTelnet weather station reads current weather information via telnet."""

    def __init__(self, host: str = 'weather.as.utexas.edu', port: int = 55410, *args, **kwargs):
        """Creates a new McDonald weather station accessed via telnet.

        Args:
            host: Host to connect to.
            port: Port to connect to.
        """
        WeatherStation.__init__(self, *args, **kwargs)
        self._host = host
        self._port = port

    def create_sensors(self):
        """Entry point for creating sensors for this station.

        These sensors are created:

        - temp

        - skytemp

        - windspeed

        - rain"""
        self._add_sensor('temp')
        self._add_sensor('skytemp')
        self._add_sensor('windspeed')
        self._add_sensor('rain')

    def update(self):
        """Entry point for updating sensor values for this station.

        This method connects to the Mt. Locke weather server via telnet and extracts the latest values."""
        log.info('Updating McDonald Locke telnet%s...' % self._station.code)

        # read data
        with Telnet(self._host, self._port) as tn:
            res = tn.read_all().strip().decode('utf-8')

        # split lines
        lines = res.split('\n')

        # get time: there is a timestamp at the end of first line
        time = datetime.fromtimestamp(int(lines[0].split()[-1]))

        # get other values
        values = {}
        for line in lines[2:]:
            s = line.split(':')
            values[s[0].strip()] = float(s[1])

        # add values
        self._add_value('temp', time, (values['Ambient'] - 32) / 1.8)
        self._add_value('skytemp', time, values['Sky-ambient'] / 1.8)
        self._add_value('windspeed', time, values['Wind Speed'] / 1.609344)
        self._add_value('rain', time, values['Rain'])


__all__ = ['McDonaldTelnet']
