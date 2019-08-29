from pyobs_weather.weather.models import Value


class Switch:
    def __init__(self, value, invert=False):
        self._value = value
        self._invert = invert

    def __call__(self, sensor):
        # get last value
        value = Value.objects.filter(sensor=sensor).order_by('-time').first()

        # are we good?
        is_good = value.value < self._value

        # invert?
        if self._invert:
            is_good = not is_good

        # return it
        return is_good
