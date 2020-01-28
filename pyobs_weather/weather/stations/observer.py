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
    def create_sensors(self):
        self._add_sensor('sunalt')

    def _get_latest_value(self, code):
        # get sensor
        sensor = Sensor.objects.get(station__code='current', type__code=code)

        # get its latest value
        val = Value.objects.filter(sensor=sensor).latest('time')

        # return its value
        return val.value

    def update(self):
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
        altaz_frame = AltAz(location=location, obstime=time,
                            pressure=press * u.hPa, temperature=temp * u.deg_C, relative_humidity=humid)

        # convert to alt/az
        sun_altaz = sun.transform_to(altaz_frame)

        # store it
        self._add_value('sunalt', time.to_datetime(pytz.UTC), sun_altaz.alt.degree)


__all__ = ['Observer']
