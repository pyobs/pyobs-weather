from astropy.coordinates import EarthLocation
from django.conf import settings
from django.views.generic import TemplateView

from pyobs_weather.weather.models import Station, SensorType, Sensor, Value


class OverView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, *args, **kwargs):
        # get average weather station
        station = Station.objects.get(code='average')

        # loop all sensor types
        values = []
        for sensor_type in SensorType.objects.all():
            # loop all sensors for this station and of this type
            for sensor in Sensor.objects.filter(station=station, type=sensor_type):
                # get latest value
                values.append(Value.objects.filter(sensor=sensor).order_by('-time').first())

        # get location
        if type(settings.OBSERVER_LOCATION) == str:
            location = EarthLocation.of_site(settings.OBSERVER_LOCATION)
        else:
            location = EarthLocation(**settings.OBSERVER_LOCATION)

        # lon and lat
        lon = location.longitude.to_string(sep='°\'"', precision=1)
        lon = lon[1:] + ' W' if lon[0] == '-' else lon + ' E'
        lat = location.latitude.to_string(sep='°\'"', precision=1)
        lat = lat[1:] + ' S' if lat[0] == '-' else lat + ' N'

        # return it
        return {
            'current': values,
            'site': settings.OBSERVER_NAME,
            'location': {
                'longitude': lon,
                'latitude': lat,
                'elevation': location.height.value
            }
        }


class Documentation(TemplateView):
    template_name = "documentation.html"
