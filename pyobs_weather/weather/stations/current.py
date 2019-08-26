import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytz


log = logging.getLogger(__name__)


class Current:
    @staticmethod
    def update(station):
        from pyobs_weather.weather.models import Station, SensorType, Sensor, Value
        log.info('Updating current...')

        # get now
        now = datetime.utcnow().astimezone(pytz.UTC)

        # loop all sensor types
        for sensor_type in SensorType.objects.all():
            values = []

            # loop all sensors of that type
            for sensor in Sensor.objects.filter(type=sensor_type):
                # get latest value of that sensor
                value = Value.objects.filter(sensor=sensor).order_by('-time').first()

                # valid?
                if value is not None and value.value is not None:
                    # and not too old?
                    if value.time > now - timedelta(minutes=10):
                        # add it
                        values.append(value.value)

            # calculate average
            avg = np.nanmean(values) if values else None

            # and store it
            sensor, _ = Sensor.objects.get_or_create(station=station, type=sensor_type)
            Value.objects.get_or_create(sensor=sensor, time=now, value=avg, good=avg is not None)
