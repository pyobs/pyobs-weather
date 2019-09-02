import logging
from astropy.coordinates import EarthLocation, get_sun, AltAz
import astropy.units as u
import pytz
from astropy.time import Time
from django.conf import settings

from .station import WeatherStation

log = logging.getLogger(__name__)


class Observer(WeatherStation):
    def create_sensors(self):
        self._add_sensor('sunalt')

    def update(self):
        log.info('Updating observer info %s...' % self._station.code)

        # get location
        location = EarthLocation(lon=settings.OBSERVER_LOCATION['longitude'] * u.deg,
                                 lat=settings.OBSERVER_LOCATION['latitude'] * u.deg,
                                 height=settings.OBSERVER_LOCATION['elevation'] * u.m)

        # get sun coordinates
        time = Time.now()
        sun = get_sun(time)

        # create alt/az frame
        altaz_frame = AltAz(location=location, obstime=time,)

        # convert to alt/az
        sun_altaz = sun.transform_to(altaz_frame)

        # store it
        self._add_value('sunalt', time.to_datetime(pytz.UTC), sun_altaz.alt.degree)


__all__ = ['Observer']
