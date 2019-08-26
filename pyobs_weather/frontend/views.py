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

        # return it
        print(values)
        return {'current': values}
