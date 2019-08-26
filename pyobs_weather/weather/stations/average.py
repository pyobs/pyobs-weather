import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytz


log = logging.getLogger(__name__)


class Average:
    @staticmethod
    def update(station_id):
        from pyobs_weather.weather.models import Station, Value
        log.info('Updating averages...')

        # get now
        now = datetime.utcnow().astimezone(pytz.UTC)

        # define fields
        fields = ['temp', 'humid', 'press', 'winddir', 'windspeed', 'rain', 'skytemp', 'dewpoint', 'particles']

        # loop all stations
        values = pd.DataFrame({k: [] for k in fields + ['weight']})
        for station in Station.objects.all():
            # exclude 'average' and 'current'
            if station.code in ['average', 'current']:
                continue

            # query all data from the last 5 minutes
            qs = Weather.objects.filter(station=station, time__gte=now - timedelta(minutes=6))
            q = qs.values(*fields)
            df = pd.DataFrame.from_records(q)

            # average
            mean = df.mean()
            mean['weight'] = station.weight

            # append to values
            values = values.append(mean, ignore_index=True)

        # calculate mean of values
        mean = values.mean().to_dict()

        # write to database
        v = {k: None if np.isnan(v) else v for k, v in mean.items() if k in fields}
        w = Weather(station_id=station_id, time=now, **v)
        w.save()
