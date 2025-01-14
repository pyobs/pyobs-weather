import logging
import pytz
from astropy.time import Time
import requests

from .station import WeatherStation

log = logging.getLogger(__name__)


class LCO(WeatherStation):
    """LCO weather station."""

    def __init__(self, url, *args, **kwargs):
        """Initializes a new LCO weather station.

        Format of weather station data:

            2023/10/02T18:44:34 18.4 26.2 -1.4 26.9 0 0 -28.1 149
            date-time, temperature(degC), humidity(%), dewPoint (degC), windspeed (km/h), wetness (0=false),
            rain (0=false), Sky Temperature - AmbientTemperature (degC), daylightADU

        Args:
            url: URL of LCO weather station.
        """

        WeatherStation.__init__(self, *args, **kwargs)
        self._url = url

    def create_sensors(self):
        """Entry point for creating sensors for this station."""
        self._add_sensor("temp")
        self._add_sensor("humid")
        self._add_sensor("dewpoint")
        self._add_sensor("windspeed")
        self._add_sensor("rain")
        self._add_sensor("skytemp")

    def update(self):
        """Entry point for updating sensor values for this station.

        This method reads the current weather information from Monet weather homepage.
        """
        log.info("Updating LCO station %s..." % self._station.code)

        # do request
        r = requests.get(self._url)

        # check code
        if r.status_code != 200:
            logging.error("Could not connect to McDonald weather station.")
            return

        # get weather
        weather = r.text.strip().split()

        # get time
        time = Time(weather[0]).to_datetime(pytz.UTC)

        # sensors
        values = [
            ("temp", float(weather[1])),
            ("humid", float(weather[2])),
            ("dewpoint", float(weather[3])),
            ("windspeed", float(weather[4])),
            ("rain", float(weather[6])),
            ("skytemp", float(weather[7])),
        ]

        # add
        self._add_values(time, values)


__all__ = ["LCO"]
