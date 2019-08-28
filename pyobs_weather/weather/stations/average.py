import logging
from datetime import datetime, timedelta
from django.db import models
import numpy as np
import pandas as pd
import pytz


log = logging.getLogger(__name__)


class Average:
    @staticmethod
    def create_sensors(station):
        pass

    @staticmethod
    def update(station):
        from pyobs_weather.weather.models import Station, SensorType, Sensor, Value
        log.info('Updating averages...')

        # get now and since
        now = datetime.utcnow().astimezone(pytz.UTC)
        since = now - timedelta(minutes=5, seconds=30)

        # loop all sensor types
        for sensor_type in SensorType.objects.filter(average=True):
            values = []

            # skip those that we don't want to calculate averages for
            if not sensor_type.average:
                continue

            # loop all sensors of that type
            for sensor in Sensor.objects.filter(type=sensor_type, station__active=True):
                # get average value for this sensor for last 5:30 minutes
                value = Value.objects.filter(sensor=sensor, time__gte=since).aggregate(models.Avg('value'))

                # valid?
                if value is not None and value['value__avg'] is not None:
                    # add it
                    values.append(value['value__avg'])

            # calculate average of all sensors
            avg = np.nanmean(values) if values else None

            # and store it
            sensor, _ = Sensor.objects.get_or_create(station=station, type=sensor_type)
            Value.objects.get_or_create(sensor=sensor, time=now, value=avg)
