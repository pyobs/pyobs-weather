import logging
from datetime import datetime, timedelta
from django.db import models
import numpy as np
import pytz

from .station import WeatherStation


log = logging.getLogger(__name__)


class Average(WeatherStation):
    """The Average weather station requests all values from all other weather stations and calculates 5-minutes
    averages for all sensor types.

    This station gets configured by the *initweather* script and is running on a crontab every 5 minutes.
    """

    def create_sensors(self):
        """Entry point for creating sensors for this station.

        No sensors created here, that all happens on-the-fly in update()."""
        pass

    def update(self):
        """Entry point for updating sensor values for this station.

        This method loops all sensor types and fetches all related sensors from all stations and calculates
        5-minutes averages, which it stores in sensors of the same type.
        """
        from pyobs_weather.weather.dbfunctions import write_value, get_list
        from pyobs_weather.weather.models import SensorType, Sensor, Value
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
            for sensor in Sensor.objects.filter(type=sensor_type, average=True, station__active=True):
                # get average value for this sensor for last 5:30 minutes
                #value = Value.objects.filter(sensor=sensor, time__gte=since).aggregate(models.Avg('value'))
                #idk how to translate aggregate(models.Avg('value'))
                temp = get_list(sensor=sensor, start=since, end=now)
                value = {'value': None}

                check = False
                sum = 0
                if temp is not None:
                    for val in temp:
                        if val['value'] is None:
                            continue
                        check = True
                        sum = sum + val['value']

                if check and temp is not None:
                    value['value'] = sum / len(temp)
                                      
                # valid?
                if value is not None and value['value'] is not None:
                    # add it
                    values.append(value['value'])

            # calculate average of all sensors
            avg = np.nanmean(values) if values else None

            # and store it
            sensor = self._add_sensor(sensor_type.code)
            write_value(sensor=sensor, time=now, value=avg)


__all__ = ['Average']
