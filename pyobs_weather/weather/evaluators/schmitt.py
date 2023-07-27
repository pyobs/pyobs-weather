from pyobs_weather.weather.influx import read_sensor_value


class SchmittTrigger:
    """A Schmitt trigger only changes its value when certain thresholds are reached."""

    def __init__(self, good: float, bad: float):
        """Creates a new Schmitt Trigger.

        For the example of a humidity sensor with good=80 and bad=85, this evaluates to False, when the value rises
        above 85, but only returns to True, when it goes below 80 again.

        Args:
            good: Value must be smaller than this to become good.
            bad: Value must be larger than this to become bad.
        """
        self._good = good
        self._bad = bad

    def __call__(self, sensor):
        """Evaluates this evaluator.

        Args:
            sensor: Sensor to evaluate.

        Returns:
            Result of evaluation.
        """

        # get last value
        # value = Value.objects.filter(sensor=sensor).order_by('-time').first()
        value = read_sensor_value(sensor)

        # non-existing values are always bad
        if value is None or value["value"] is None:
            return False

        # are we good?
        if sensor.good is True or sensor.good is None:
            # if current value of sensor is good, we must be below bad to stay good
            is_good = value["value"] < self._bad
        else:
            # if current value of sensor is not good, we must be below good to become good
            is_good = value["value"] < self._good

        # return it
        return is_good

    def areas(self) -> list:
        """Returns list of areas for plot."""

        return [
            # bad
            {"type": "danger", "min" if self._bad > self._good else "max": self._bad},
            # in between
            {
                "type": "warning",
                "min": self._bad if self._bad < self._good else self._good,
                "max": self._bad if self._bad > self._good else self._good,
            },
        ]
