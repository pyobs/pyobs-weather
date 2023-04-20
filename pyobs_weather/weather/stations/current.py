import logging
from datetime import datetime, timedelta
import numpy as np
import pytz

from .station import WeatherStation


log = logging.getLogger(__name__)


class Current(WeatherStation):
    """The Current weather station requests all values from all other weather stations and just averages the lates
    values for all sensor types.

    This station gets configured by the *initweather* script and is running in an interval every 10 seconds.

    All sensors of this station that are vital for operation should have
    :ref:`Valid <pyobs_weather.weather.evaluators.Valid>` evaluators attached to them."""

    def create_sensors(self):
        """Entry point for creating sensors for this station.

        No sensors created here, that all happens on-the-fly in update()."""
        pass

    def update(self):
        """Entry point for updating sensor values for this station.

        This method loops all sensor types and fetches all related sensors from all stations and calculates
        averages of the latest values, which it stores in sensors of the same type. Values from other stations are
        only used if they are not older than 10 minutes.
        """
        from pyobs_weather.weather.influx import get_value, write_current
        from pyobs_weather.weather.models import SensorType, Sensor
        log.info('Updating current...')

        # get now
        now = datetime.utcnow().astimezone(pytz.UTC)

        # loop all sensor types
        for sensor_type in SensorType.objects.all():
            values = []

            # loop all sensors of that type
            for sensor in Sensor.objects.filter(type=sensor_type, average=True, station__active=True):
                # skip average and current
                if sensor.station.code in ['average', 'current']:
                    continue

                # get latest value of that sensor
                value = get_value(sensor.station.code, sensor.type.code)

                # valid?
                if value is not None and value[1] is not None:
                    values.append(value[1])

            # calculate average
            avg = np.mean(values) if values else None

            # and store it
            sensor = self._add_sensor(sensor_type.code)
            station_code = self._station.code
            write_current(station_code, sensor_type.code, now, avg)


__all__ = ['Current']
