import importlib
import logging

from pyobs_weather.celery import app


log = logging.getLogger(__name__)


@app.task
def update_stations(station_code: str):
    from pyobs_weather.main.models import Station
    log.info('Updating station %s...' % station_code)

    # get station
    station = Station.objects.get(code=station_code)

    # get module and update method
    module = importlib.import_module(station.module)
    update_func = getattr(module, 'update')

    # run it
    update_func(station.id)
