from pyobs_weather.weather.models import Value


class Valid:
    def __init__(self):
        pass

    def __call__(self, sensor):
        # get last value
        value = Value.objects.filter(sensor=sensor).order_by('-time').first()

        # are we good?
        is_good = value is not None and value.value is not None

        # return it
        return is_good
