from pyobs_weather.weather.models import Value


class SchmittTrigger:
    def __init__(self, good, bad):
        self._good = good
        self._bad = bad

    def __call__(self, sensor):
        # get last value
        value = Value.objects.filter(sensor=sensor).order_by('-time').first()

        # are we good?
        if sensor.good is True or sensor.good is None:
            # if current value of sensor is good, we must be above bad to become bad
            is_good = value.value <= self._bad
        else:
            # if current value of sensor is not good, we must be below good to become bad
            is_good = value.value >= self._good

        # since when?
        since = 0

        # return it
        return is_good, since
