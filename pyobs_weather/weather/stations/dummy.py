import logging
from random import random, randint
import datetime


from .station import WeatherStation

log = logging.getLogger(__name__)


class Dummy(WeatherStation):

    def __init__(self, *args, **kwargs):
        WeatherStation.__init__(self, *args, **kwargs)

    def create_sensors(self):
        self._add_sensor('temp')
        self._add_sensor('humid')
        self._add_sensor('winddir')
        self._add_sensor('windspeed')
        self._add_sensor('press')
        self._add_sensor('rain')

    def update(self):
        log.info('Updating Dummy station %s...' % self._station.code)
        time = datetime.datetime.now()

        self._add_value('temp', time, round(40*random(),1))
        self._add_value('humid', time, round(100*random(),1))
        self._add_value('winddir', time, round(360*random(),1))
        self._add_value('windspeed', time, round(40*random(),1))
        self._add_value('press', time, 970.0 + round(100*random(),1))
        self._add_value('rain', time, randint(0,1))

__all__ = ['Dummy']
