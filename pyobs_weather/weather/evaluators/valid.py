from pyobs_weather.weather.models import Weather


class Valid:
    def __init__(self):
        pass

    def __call__(self, station, sensor):
        # get last value
        tmp = Weather.objects.filter(station=station).order_by('-time').values(sensor.type.code).first()
        value = tmp[sensor.type.code]

        # are we good?
        is_good = value is not None

        # since when?
        since = 0

        # return it
        return is_good, since
