from pyobs_weather.main.models import Weather


class SchmittTrigger:
    def __init__(self, good, bad):
        self._good = good
        self._bad = bad

    def __call__(self, station, sensor):
        # get last value
        value = Weather.objects.filter(station=station).order_by('-time').values(sensor).first()

        # evaluate it
