from pyobs_weather.main.models import Weather


class Boolean:
    def __init__(self, invert=False):
        self._invert = invert

    def __call__(self, station, sensor):
        # get last value
        tmp = Weather.objects.filter(station=station).order_by('-time').values(sensor.type.code).first()
        value = tmp[sensor.type.code]

        # are we good?
        is_good = value
        if self._invert:
            is_good = not is_good

        # since when?
        since = 0

        # return it
        return is_good, since
