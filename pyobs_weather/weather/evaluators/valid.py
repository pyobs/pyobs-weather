from pyobs_weather.weather.influx import read_sensor_value


class Valid:
    """A Valid evaluator checks, whether the sensor's value is valid, i.e. not None."""

    def __init__(self):
        """Creates a new Valid evaluator."""
        pass

    def __call__(self, sensor):
        """Evaluates this evaluator.

        Args:
            sensor: Sensor to evaluate.

        Returns:
            Result of evaluation.
        """

        # get last value
        value = read_sensor_value(sensor)

        # are we good?
        is_good = value is not None and value["value"] is not None

        # return it
        return is_good
