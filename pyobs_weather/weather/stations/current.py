import logging
from datetime import datetime, timedelta
import numpy as np
import pytz

from .station import WeatherStation


log = logging.getLogger(__name__)


class Current(WeatherStation):
    def create_sensors(self):
        pass

    def update(self):
        from pyobs_weather.weather.models import SensorType, Sensor, Value
        log.info('Updating current...')

        # get now
        now = datetime.utcnow().astimezone(pytz.UTC)

        # loop all sensor types
        for sensor_type in SensorType.objects.all():
            values = []

            # loop all sensors of that type
            for sensor in Sensor.objects.filter(type=sensor_type, station__active=True):
                # skip average and current
                if sensor.station.code in ['average', 'current']:
                    continue

                # get latest value of that sensor
                value = Value.objects.filter(sensor=sensor).order_by('-time').first()

                # valid?
                if value is not None and value.value is not None:
                    # and not too old?
                    if value.time > now - timedelta(minutes=10):
                        # add it
                        values.append(value.value)

            # calculate average
            avg = np.mean(values) if values else None

            # and store it
            sensor = self._add_sensor(sensor_type.code)
            Value.objects.get_or_create(sensor=sensor, time=now, value=avg)


__all__ = ['Current']
