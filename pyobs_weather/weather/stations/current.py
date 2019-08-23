import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytz


log = logging.getLogger(__name__)


def update(station_id):
    from pyobs_weather.weather.models import Station, Weather
    log.info('Updating current...')

    # get now
    now = datetime.utcnow().astimezone(pytz.UTC)

    # define fields
    fields = ['temp', 'humid', 'press', 'winddir', 'windspeed', 'rain', 'skytemp', 'dewpoint', 'particles']

    # loop all stations
    values = pd.DataFrame({k: [] for k in fields})
    for station in Station.objects.all():
        # exclude 'average' and 'current'
        if station.code in ['average', 'current']:
            continue

        # get last data point
        latest = Weather.objects.filter(station=station).order_by('-time').first()

        # too old?
        too_old = latest.time < now - timedelta(minutes=10)

        # fill fields
        latest_dict = {f: None if too_old else getattr(latest, f) for f in fields}

        # append to values
        values = values.append(pd.Series(latest_dict), ignore_index=True)

    # calculate mean of values
    mean = values.mean().to_dict()

    # write to database
    v = {k: None if np.isnan(v) else v for k, v in mean.items() if k in fields}
    w = Weather(station_id=station_id, time=now, **v)
    w.save()
