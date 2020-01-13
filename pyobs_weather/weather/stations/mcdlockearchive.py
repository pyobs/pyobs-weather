import time
import logging
import pytz
from astropy.time import Time
import requests

from .station import WeatherStation
from ..models import SensorType, Sensor

log = logging.getLogger(__name__)


class McDonaldLockeArchive(WeatherStation):
    def __init__(self, fields: dict, url: str = 'http://weather.as.utexas.edu/cgi-bin/weather/weather-data.pl',
                 *args, **kwargs):
        """Creates a new McDonald Archive station.

        Args:
            fields: Dictionary with field->SensorType data,
                        e.g. {'cloud-Sky-ambient': {code="skytemp", name="Temperature", unit="C"}}
            time_offset: Offset in seconds to add to current time to get UTC.
        """
        WeatherStation.__init__(self, *args, **kwargs)
        self.fields = fields
        self.url = url
        print(fields)

    def create_sensors(self):
        """Create all sensors."""

        # loop all fields
        for field, typ in self.fields.items():
            if 'name' in typ and 'unit' in typ:
                # get or create sensor type
                sensor_type, _ = SensorType.objects.get_or_create(code=typ['code'], name=typ['name'], unit=typ['unit'])

                # get or create sensor
                Sensor.objects.get_or_create(station=self._station, type=sensor_type)

            else:
                self._add_sensor(typ['code'])

    def update(self):
        log.info('Updating McDonald Locke Archive %s...' % self._station.code)

        # create payload for request
        endtime = time.time()
        starttime = endtime - 600
        payload = {
            'starttime': starttime,
            'endtime': endtime,
            'header_list': list(self.fields.keys()),
            'log': 'No',
            'down_load': 'Download'
        }

        # do request
        r = requests.post("http://weather.as.utexas.edu/cgi-bin/weather/weather-data.pl", data=payload)

        # check code
        if r.status_code != 200:
            logging.error('Could not connect to McDonald weather archive.')
            return

        # split lines
        lines = r.content.decode('utf-8').strip().split('\n')

        # get columns and replace first '-' in name by '+'
        columns = lines[0].split(',')
        for i in range(1, len(columns)):
            columns[i] = columns[i].replace('-', '+', 1)

        # loop lines and store latest value
        values = {}
        for line in lines[1:]:
            # split
            s = line.split(',')

            # get time
            t = Time(s[0]).to_datetime(pytz.UTC)

            # loop columns
            for i, col in enumerate(columns[1:], 1):
                # got something?
                if len(s[i].strip()) > 0:
                    # store it
                    values[col] = (t, float(s[i]))

        print(values)

        # store values
        for field, (t, val) in values.items():
            # get code
            code = self.fields[field]['code']

            # add value
            self._add_value(code, t, val)


__all__ = ['McDonaldLockeArchive']
