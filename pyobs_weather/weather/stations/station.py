from pyobs_weather.weather.models import Value


class WeatherStation:
    @staticmethod
    def _add_value(sensor, time, value):
        if Value.objects.filter(sensor=sensor, time=time).count() == 0:
            Value.objects.create(sensor=sensor, time=time, value=value)
