import logging
from datetime import datetime, timedelta
import pandas as pd
import pytz


log = logging.getLogger(__name__)


def update(station_id, current=False):
    from pyobs_weather.main.models import Station, Weather, CurrentAverage
    log.info('Updating averages...')

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

    # calculate mean of values
    mean = values.mean().to_dict()

    # write to database
    v = {k: v for k, v in mean.items() if k in fields}
    w = Weather(station_id=station_id, time=now, **v)
    w.save()
