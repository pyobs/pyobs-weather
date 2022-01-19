import logging
import pytz
import requests
import dateutil.parser

from pyobs_weather.weather.models import Sensor, SensorType
from .station import WeatherStation

log = logging.getLogger(__name__)


class JSON(WeatherStation):
    """The JSON weather station reads current weather information from a JSON file."""

    def __init__(self, url: str, fields: dict, time: str = 'time', timezone: str = None, *args, **kwargs):
        """Creates a new weather station that reads its data from a CSV file.

        A typical JSON configuration for this weather station might look like this:

        for c in ['ambientTemperature', 'relativeHumidityPercentage', 'windSpeed',
                  'skyMinusAmbientTemperature', 'rainSensor']:

        |  {
        |      "url": "http://example.com/some.json",
        |      "time": "time",
        |      "fields": {
        |              "ambientTemperature": {"code": "temp", "name": "Temperature", "unit": "°C"},
        |              "relativeHumidityPercentage": {"code": "humid", "name": "Relative humidity", "unit": "%"},
        |              "windSpeed": {"code": "windspeed", "name": "Wind speed", "unit": "km/h"},
        |              "skyMinusAmbientTemperature": {"code": "skytemp", "name": "Rel sky temperature", "unit": "°C"},
        |              "rainSensor": {"code": "rain", "name": "Raining", "unit": ""}
        |      }
        |  }

        Args:
            time: Field containing time.
            fields: Dictionary with column->SensorType data,
                        e.g. {field: {code="temp", name="Temperature", unit="C"}}
                    keyword: json keyword
                    code: field code
                    name: field name
                    unit: field unit
                    bool_true: if given, evaluate value to 1 if equal to this, otherwise 0
                    bool_false: if given, evaluate value to 0 if equal to this, otherwise 1
            timezone: Timezone for datetime in file. If None, try to parse automatically.
            separator: CSV field separator.
        """
        WeatherStation.__init__(self, *args, **kwargs)
        self.url = url
        self.time = time
        self.timezone = None if timezone is None else pytz.timezone(timezone)
        self.fields = fields

    def create_sensors(self):
        """Entry point for creating sensors for this station.

        New sensors are created based on the configuration."""

        # loop all fields
        for field, typ in self.fields.items():
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

        # read data
        res = requests.get(self.url)
        if res.status_code != 200:
            log.warning('Could not fetch JSON.')
            return
        weather = res.json()

        # parse time
        time = dateutil.parser.isoparse(weather[self.time])

        # timezone?
        if self.timezone is not None:
            # calculate timezone offset and subtract it
            time -= self.timezone.utcoffset(time)
            time = time.replace(tzinfo=pytz.utc)
        else:
            # need to convert to UTC?
            if time.tzinfo is not None:
                time = time.astimezone(pytz.utc)

        # other values
        for field, cfg in self.fields.items():
            # add value
            self._add_value(cfg['code'], time, weather[field])


__all__ = ['JSON']
