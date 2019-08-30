from pyobs_weather.weather.models import Value


class SchmittTrigger:
    def __init__(self, good, bad):
        self._good = good
        self._bad = bad

    def __call__(self, sensor):
        # get last value
        value = Value.objects.filter(sensor=sensor).order_by('-time').first()

        # are we good?
        if sensor.id == 4:
            print(['schmitt', sensor.good, value.value, self._bad, self._good])
        if sensor.good is True or sensor.good is None:
            # if current value of sensor is good, we must be below bad to stay good
            is_good = value.value < self._bad
        else:
            # if current value of sensor is not good, we must be below good to become good
            is_good = value.value < self._good

        # return it
        return is_good
