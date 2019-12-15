import logging
import MySQLdb
import pytz
from astropy.time import Time, TimeDelta
import astropy.units as u

from pyobs_weather.weather.models import Sensor, SensorType
from .station import WeatherStation

log = logging.getLogger(__name__)


class MySQL(WeatherStation):
    def __init__(self, connect, table, fields, time: str = 'time', time_offset: int = 0, *args, **kwargs):
        """Creates a new Database station.

        Args:
            connect: Dictionary with fields required by MySQLd.connect
            table: Database table.
            time: Name of column containing time.
            fields: Dictionary with field->SensorType data,
                        e.g. {column: {code="temp", name="Temperature", unit="C"}}
                    column: table column
                    code: field code
                    name: field name
                    unit: field unit
                    bool_true: if given, evaluate value to 1 if equal to this, otherwise 0
                    bool_false: if given, evaluate value to 0 if equal to this, otherwise 1
            time_offset: Offset in seconds to add to current time to get UTC.
        """
        WeatherStation.__init__(self, *args, **kwargs)
        self.connect = connect
        self.table = table
        self.time = time
        self.time_offset = time_offset
        self.fields = fields

    def create_sensors(self):
        # loop all fields
        for field, typ in self.fields.items():
            if 'name' in typ and 'unit' in typ:
                # get or create sensor type
                sensor_type, _ = SensorType.objects.get_or_create(code=typ['code'], name=typ['name'], unit=typ['unit'])
            else:
                sensor_type = self._add_sensor(typ['code'])

            # get or create sensor
            Sensor.objects.get_or_create(station=self._station, type=sensor_type)

    def update(self):
        log.info('Updating Database station %s...' % self._station.code)

        # connect to DB
        db = MySQLdb.connect(**self.connect)

        # get all columns to query
        columns = [self.time] + list(self.fields.keys())

        # build query
        sql = 'SELECT %s FROM %s ORDER BY %s DESC LIMIT 1' % (','.join(columns), self.table, self.time)

        # and query
        cur = db.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        cur.close()

        # nothing?
        if row is None:
            logging.error('Result from database is empty.')
            return

        # evaluate row
        time = (Time(row[0]) + TimeDelta(self.time_offset * u.second)).to_datetime(pytz.UTC)

        # other values
        for cfg, value in zip(self.fields.values(), row[1:]):
            # boolean?
            if 'bool_true' in cfg:
                value = 1 if cfg['bool_true'] == value else 0
            elif 'bool_false' in cfg:
                value = 0 if cfg['bool_false'] == value else 1

            # add value
            self._add_value(cfg['code'], time, value)


__all__ = ['MySQL']
