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
        from pyobs_weather.weather.influx import get_value, write_value
        from pyobs_weather.weather.models import SensorType, Sensor
        log.info('Updating averages...')

        # get now and since
        now = datetime.utcnow().astimezone(pytz.UTC)

        # loop all sensor types
        for sensor_type in SensorType.objects.filter(average=True):
            values = []

            # skip those that we don't want to calculate averages for
            if not sensor_type.average:
                continue

            # loop all sensors of that type
            for sensor in Sensor.objects.filter(type=sensor_type, average=True, station__active=True):
                # get average value for this sensor for last 5:30 minutes
                value = get_value(sensor.station.code, sensor.type.code, avg=True)

                # valid?
                if value is not None and value[1] is not None:
                    # add it
                    values.append(value[1])

            # calculate average of all sensors
            avg = np.nanmean(values) if values else None

            # and store it
            sensor = self._add_sensor(sensor_type.code)
            station_code = self._station.code
            write_value(station_code, sensor_type.code, now, avg, avg=True)



__all__ = ['Average']
