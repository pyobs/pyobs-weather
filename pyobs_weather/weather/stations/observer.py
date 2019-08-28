import logging
from astropy.coordinates import EarthLocation, get_sun, AltAz
import astropy.units as u
import pytz
from astropy.time import Time
from django.conf import settings

from pyobs_weather.weather.models import Value, Sensor, SensorType

log = logging.getLogger(__name__)


class Observer:
    @staticmethod
    def create_sensors(station):
        # get or create types
        type_sunalt, _ = SensorType.objects.get_or_create(code='sunalt', name='Solar altitude', unit='°', average=False)

        # get or create sensors
        Sensor.objects.get_or_create(station=station, type=type_sunalt)

    def update(self, station):
        log.info('Updating observer info %s...' % station.code)

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
        Value.objects.get_or_create(sensor=Sensor.objects.get(station=station, type__code='sunalt'),
                                    time=time.to_datetime(pytz.UTC), value=sun_altaz.alt.degree)
