from pyobs_weather.weather.models import Value


class Boolean:
    """A Boolean evaluator is True, if its value is not equal 0."""

    def __init__(self, invert: bool = False):
        """Creates a new Boolean evaluator.

        Args:
            invert: If True, the result of this evaluator is inverted.
        """
        self._invert = invert

    def __call__(self, sensor):
        """Evaluates this evaluator.

        Args:
            sensor: Sensor to evaluate.

        Returns:
            Result of evaluation.
        """

        # get last value
        value = Value.objects.filter(sensor=sensor).order_by('-time').first()

        # non-existing values are always bad
        if value is None or value.value is None:
            return False

        # are we good?
        is_good = value.value is True or value.value != 0
        if self._invert:
            is_good = not is_good

        # return it
        return is_good

    def areas(self) -> list:
        """Returns list of areas for plot."""

        return [{
            'type': 'danger',
            'min': 0.5 if self._invert else 0.,
            'max': 1.0 if self._invert else 0.5
        }]
