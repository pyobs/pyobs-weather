import logging
import pytz
from astropy.time import Time
import requests

from .station import WeatherStation

log = logging.getLogger(__name__)


class ReadOnly(WeatherStation):
    """A read-only weather station that only shows existing values."""

    def __init__(self, *args, **kwargs):
        """Initializes a new read-only weather station."""
        WeatherStation.__init__(self, *args, **kwargs)

    def create_sensors(self):
        """Entry point for creating sensors for this station.

        These sensors are created:

            - temp
            - humid
            - winddir
            - windspeed
            - press
            - rain
        """
        self._add_sensor("temp")
        self._add_sensor("humid")
        self._add_sensor("winddir")
        self._add_sensor("windspeed")
        self._add_sensor("press")
        self._add_sensor("rain")


__all__ = ["ReadOnly"]
