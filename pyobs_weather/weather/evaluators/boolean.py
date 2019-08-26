from pyobs_weather.weather.models import Value


class Boolean:
    def __init__(self, invert=False):
        self._invert = invert

    def __call__(self, sensor):
        # get last value
        value = Value.objects.filter(sensor=sensor).order_by('-time').first()

        # are we good?
        is_good = value.value is True or value.value == 1
        if self._invert:
            is_good = not is_good

        # since when?
        since = 0

        # return it
        return is_good, since
