import logging
import os

import MySQLdb
import pytz
from astropy.time import Time, TimeDelta
import astropy.units as u

from pyobs_weather.weather.models import Sensor, SensorType
from .station import WeatherStation

log = logging.getLogger(__name__)


class CSV(WeatherStation):
    """The CSV weather station reads current weather information from a CSV file."""

    def __init__(self, filename: str, columns: dict, time: int = 0, time_offset: int = 0, separator: str = ',',
                 *args, **kwargs):
        """Creates a new weather station that reads its data from a CSV file.

        A typical JSON configuration for this weather station might look like this:

        |  {
        |      "time": 0,
        |      "fields": {
        |          1: {"code": "temp", "name": "Temperature", "unit": "°C"},
        |          2: {"code": "humid", "name": "Relative humidity", "unit": "%"},
        |          5: {"code": "dewpoint", "name": "Dew point", "unit": "°C"},
        |          7: {"code": "windspeed", "name": "Wind speed", "unit": "km/h"},
        |      }
        |  }

        Args:
            time: Column containing time.
            fields: Dictionary with column->SensorType data,
                        e.g. {column: {code="temp", name="Temperature", unit="C"}}
                    column: column number
                    code: field code
                    name: field name
                    unit: field unit
                    bool_true: if given, evaluate value to 1 if equal to this, otherwise 0
                    bool_false: if given, evaluate value to 0 if equal to this, otherwise 1
            time_offset: Offset in seconds to add to current time to get UTC.
            separator: CSV field separator.
        """
        WeatherStation.__init__(self, *args, **kwargs)
        self.filename = filename
        self.time = time
        self.time_offset = time_offset
        self.columns = columns
        self.separator = separator

    def create_sensors(self):
        """Entry point for creating sensors for this station.

        New sensors are created based on the configuration."""

        # loop all fields
        for field, typ in self.columns.items():
            if 'name' in typ and 'unit' in typ:
                # get or create sensor type
                sensor_type, _ = SensorType.objects.get_or_create(code=typ['code'], name=typ['name'], unit=typ['unit'])
            else:
                sensor_type = self._add_sensor(typ['code'])

            # get or create sensor
            Sensor.objects.get_or_create(station=self._station, type=sensor_type)

    def update(self):
        """Entry point for updating sensor values for this station.

        This method reads the last line of the given file and interprets it."""
        log.info('Updating Database station %s...' % self._station.code)

        # read last line of file
        line = self._read_last_line(self.filename)

        # nothing?
        if line is None:
            logging.error('Could not read line from CSV file.')
            return

        # split it
        fields = line.split(self.separator)
        print(fields)

        # get time
        time = (Time(fields[self.time]) + TimeDelta(self.time_offset * u.second)).to_datetime(pytz.UTC)

        # other values
        for c, cfg in self.columns.items():
            # column
            col = int(c)

            # get value
            value = float(fields[col])

            # boolean?
            if 'bool_true' in cfg:
                value = 1 if cfg['bool_true'] == value else 0
            elif 'bool_false' in cfg:
                value = 0 if cfg['bool_false'] == value else 1

            # add value
            self._add_value(cfg['code'], time, value)

    @staticmethod
    def _read_last_line(filename: str) -> str:
        """Reads the last line from the given file.

        Args:
            filename: Name of file to read from.

        Returns:
            Last line in given file.
        """

        # open file
        with open(filename, 'rb') as f:
            # seek end
            f.seek(-2, os.SEEK_END)

            # find last line break
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)

            # return lone
            return f.readline().decode()


__all__ = ['CSV']
