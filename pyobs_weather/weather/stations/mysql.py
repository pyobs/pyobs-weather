import logging
import MySQLdb
import pytz
from astropy.time import Time

from pyobs_weather.weather.models import Value, Sensor, SensorType

log = logging.getLogger(__name__)


class MySQL:
    def __init__(self, connect, table, time, fields):
        """Creates a new Database station.

        Args:
            connect: Dictionary with fields required by MySQLd.connect
            table: Database table.
            time: Name of column containing time.
            fields: Dictionary with field->SensorType data,
                        e.g. {table.column: {code="temp", name="Temperature", unit="C"}}
        """
        self.connect = connect
        self.table = table
        self.time = time
        self.fields = fields

    def create_sensors(self, station):
        # loop all fields
        types = {}
        for field, typ in self.fields.items():
            # get or create sensor type
            sensor_type, _ = SensorType.objects.get_or_create(code=typ['code'], name=typ['name'], unit=typ['unit'])

            # get or create sensor
            Sensor.objects.get_or_create(station=station, type=sensor_type)

    def update(self, station):
        log.info('Updating Database station %s...' % station.code)

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

        # evaluate row
        time = Time(row[0]).to_datetime(pytz.UTC)

        # other values
        values = {columns[i]: row[i] for i in range(1, len(columns))}

        # set values
        for key, val in values.items():
            Value.objects.get_or_create(sensor=Sensor.objects.get(station=station, type__code=key),
                                        time=time, value=val)
