from astropy.coordinates import EarthLocation
import astropy.units as u
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

        # get sensor types
        value_types = []
        for code in settings.WEATHER_SENSORS:
            try:
                a = SensorType.objects.get(code=code)
                value_types.append(a)
            except SensorType.DoesNotExist:
                pass
        plot_types = []
        for code in settings.WEATHER_PLOTS:
            try:
                plot_types.append(SensorType.objects.get(code=code))
            except SensorType.DoesNotExist:
                pass

        # get location
        location = EarthLocation(lon=settings.OBSERVER_LOCATION['longitude'] * u.deg,
                                 lat=settings.OBSERVER_LOCATION['latitude'] * u.deg,
                                 height=settings.OBSERVER_LOCATION['elevation'] * u.m)

        # lon and lat
        lon = location.lon.to_string(sep='°\'"', precision=1)
        lon = lon[1:] + ' W' if lon[0] == '-' else lon + ' E'
        lat = location.lat.to_string(sep='°\'"', precision=1)
        lat = lat[1:] + ' S' if lat[0] == '-' else lat + ' N'

        # get next sunrise and sunset
        #now = Time.now()
        #observer = Observer(location=location)
        #sunrise = observer.sun_rise_time(now).to_datetime(pytz.UTC)
        #sunset = observer.sun_set_time(now).to_datetime(pytz.UTC)

        # return it
        return {
            'site': settings.OBSERVER_NAME,
            'title': settings.WINDOW_TITLE,
            'value_types': value_types,
            'plot_types': plot_types,
            'location': {
                'longitude': lon,
                'latitude': lat,
                'elevation': location.height.value
            },
            'sunrise': None,
            'sunset': None
        }


class SensorsView(TemplateView):
    template_name = "sensors.html"

    def get_context_data(self, *args, **kwargs):
        return {'title': settings.WINDOW_TITLE + ' (sensors)'}


class Documentation(TemplateView):
    template_name = "documentation.html"

    def get_context_data(self, *args, **kwargs):
        return {'title': settings.WINDOW_TITLE + ' (documentation)'}
