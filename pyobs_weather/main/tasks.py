import importlib
import logging
from datetime import datetime, timedelta
import pandas as pd
import pytz

from pyobs_weather.celery import app


log = logging.getLogger(__name__)


@app.task
def update_stations(station_code: str):
    from pyobs_weather.main.models import Station

    # get station
    station = Station.objects.get(code=station_code)

    # get module and update method
    module = importlib.import_module(station.module)
    update_func = getattr(module, 'update')

    # run it
    update_func(station.id)


@app.task
def update_averages():
    from pyobs_weather.main.models import Station, Weather

    # get now
    now = datetime.utcnow().astimezone(pytz.UTC)

    # define fields
    fields = ['temp', 'humid', 'press', 'winddir', 'windspeed', 'rain', 'skytemp', 'dewpoint', 'particles']

    # loop all stations
    values = pd.DataFrame({k: [] for k in fields + ['weight']})
    for station in Station.objects.all():
        # query all data from the last 5 minutes
        qs = Weather.objects.filter(station=station, time__gte=now - timedelta(minutes=5))
        q = qs.values(*fields)
        df = pd.DataFrame.from_records(q)

        # average
        mean = df.mean()
        mean['weight'] = station.weight

        # append to values
        values = values.append(mean, ignore_index=True)

    print(values)