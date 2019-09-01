from pyobs_weather.weather.models import Value


class WeatherStation:
    @staticmethod
    def _add_value(sensor, time, value):
        try:
            Value.objects.get(sensor=sensor, time=time)
        except Value.DoesNotExist:
            Value.objects.create(sensor=sensor, time=time, value=value)
