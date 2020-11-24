import logging
from astropy.coordinates import EarthLocation, get_sun, AltAz
import astropy.units as u
import pytz
from astropy.time import Time
from django.conf import settings

from .station import WeatherStation
from ..models import Value, Sensor

log = logging.getLogger(__name__)


class Observer(WeatherStation):
    """The Observer calculates the current solar altitude.

    No configuration required."""

    def create_sensors(self):
        """Entry point for creating sensors for this station.

        Only one sensor is created:

        - sunalt"""
        self._add_sensor('sunalt')

    def _get_latest_value(self, code):
        """Returns latest value from the :ref:`Current` station for a given sensor type.

        Args:
            code: Sensor type to fetch latest value for.

        Returns:
            Latest value.
        """

        # get sensor
        try:
            sensor = Sensor.objects.get(station__code='current', type__code=code)
        except Sensor.DoesNotExist:
            # sensor doesn't exist
            return

        # get its latest value
        val = Value.objects.filter(sensor=sensor).latest('time')

        # return its value
        return val.value

    def update(self):
        """Entry point for updating sensor values for this station.

        This method fetches the current Temperature, Pressure and Relative Humidity from the
        :ref:`Current <pyobs_weather.weather.stations.Current>` station and uses those to calculate the current solar altitude,
        which it stores in a sensor."""
        log.info('Updating observer info %s...' % self._station.code)

        # get latest values for temp, press and humid
        temp = self._get_latest_value('temp')
        press = self._get_latest_value('press')
        humid = self._get_latest_value('humid')

        # get location
        location = EarthLocation(lon=settings.OBSERVER_LOCATION['longitude'] * u.deg,
                                 lat=settings.OBSERVER_LOCATION['latitude'] * u.deg,
                                 height=settings.OBSERVER_LOCATION['elevation'] * u.m)

        # get sun coordinates
        time = Time.now()
        sun = get_sun(time)

        # create alt/az frame
        altaz_frame = AltAz(location=location,
                            obstime=time,
                            pressure=press * u.hPa if press is not None else None,
                            temperature=temp * u.deg_C if temp is not None else None,
                            relative_humidity=humid)

        # convert to alt/az
        sun_altaz = sun.transform_to(altaz_frame)

        # store it
        self._add_value('sunalt', time.to_datetime(pytz.UTC), sun_altaz.alt.degree)


__all__ = ['Observer']
