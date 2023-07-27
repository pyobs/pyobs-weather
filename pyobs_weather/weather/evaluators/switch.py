from pyobs_weather.weather.influx import read_sensor_value


class Switch:
    """A simple Switch that changes its value whenever a given threshold is reached."""

    def __init__(self, threshold: float, invert: bool = False):
        """Creates a new Switch.

        The switch evaluates to True (False, if invert is True), if its value is smaller than the given threshold.

        Args:
            threshold: Threshold for switch.
            invert: If True, invert result of evaluation.
        """
        self._threshold = threshold
        self._invert = invert

    def __call__(self, sensor):
        """Evaluates this evaluator.

        Args:
            sensor: Sensor to evaluate.

        Returns:
            Result of evaluation.
        """

        # get last value
        value = read_sensor_value(sensor)

        # non-existing values are always bad
        if value is None or value["value"] is None:
            return False

        # are we good?
        is_good = value["value"] < self._threshold

        # invert?
        if self._invert:
            is_good = not is_good

        # return it
        return is_good

    def areas(self) -> list:
        """Returns list of areas for plot."""

        return [{"type": "danger", "min" if self._invert else "max": self._threshold}]
