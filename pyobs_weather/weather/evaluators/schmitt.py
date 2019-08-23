from pyobs_weather.weather.models import Weather


class SchmittTrigger:
    def __init__(self, good, bad):
        self._good = good
        self._bad = bad

    def __call__(self, station, sensor):
        # get last value
        tmp = Weather.objects.filter(station=station).order_by('-time').values(sensor.type.code).first()
        value = tmp[sensor.type.code]

        # are we good?
        if sensor.good is True or sensor.good is None:
            # if current value of sensor is good, we must be above bad to become bad
            is_good = value <= self._bad
        else:
            # if current value of sensor is not good, we must be below good to become bad
            is_good = value >= self._good

        # since when?
        since = 0

        # return it
        return is_good, since
