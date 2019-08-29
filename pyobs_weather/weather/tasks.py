import importlib
import json
import logging
from datetime import datetime

import pytz

from pyobs_weather.celery import app
from pyobs_weather.weather.utils import get_class

log = logging.getLogger(__name__)


@app.task
def update_stations(station_code: str):
    from pyobs_weather.weather.models import Station

    # get station
    station = Station.objects.get(code=station_code)

    # not active?
    if not station.active:
        return

    # get class and update station
    kls = get_class(station.class_name)
    obj = kls(**json.loads(station.kwargs))
    obj.update(station)


def create_evaluator(evaluator):
    # get module and class name
    module = evaluator.class_name[:evaluator.class_name.rfind('.')]
    class_name = evaluator.class_name[evaluator.class_name.rfind('.') + 1:]

    # import
    kls = getattr(importlib.import_module(module), class_name)

    # instantiate and store
    kwargs = {} if evaluator.kwargs is None else json.loads(evaluator.kwargs)
    return kls(**kwargs)


@app.task
def evaluate():
    from pyobs_weather.weather.models import Station

    # get now
    now = datetime.utcnow()

    # loop all stations
    for station in Station.objects.all():
        # loop all sensors at station
        for sensor in station.sensor_set.all():
            # init good
            is_good = True

            # evaluate all evaluators
            was_evaluated = False
            for evaluator in sensor.evaluators.all():
                # get evaluator
                eva = create_evaluator(evaluator)

                # and evaluate
                res = eva(sensor)
                is_good = is_good and res
                was_evaluated = True

            # has not been evaluated?
            if not was_evaluated:
                # reset is_good
                is_good = None

            # status changed?
            if is_good != sensor.good:
                # reset good/bad since
                sensor.bad_since = None
                sensor.good_since = None
                if is_good is True:
                    sensor.good_since = now
                elif is_good is False:
                    sensor.bad_since = now

            # if there's a delay, we may want to switch back
            if sensor.good and sensor.bad_since and (now - sensor.bad_since).total_seconds() < sensor.delay_bad:
                is_good = sensor.good
            if not sensor.good and sensor.good_since and (now - sensor.good_since).total_seconds() < sensor.delay_bad:
                is_good = sensor.good

            # did status still change?
            if is_good is not None and is_good != sensor.good:
                # then store time
                sensor.since = datetime.utcnow().astimezone(pytz.UTC)

            # store it
            sensor.good = is_good
            sensor.save()
