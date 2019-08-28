import logging
import MySQLdb


log = logging.getLogger(__name__)


class MySQL:
    def __init__(self, connect, fields):
        """Creates a new Database station.

        Args:
            connect: Dictionary with fields required by MySQLd.connect
            fields: Dictionary with field->SensorType data,
                        e.g. {table.column: {code="temp", name="Temperature", unit="C"}}
        """
        self.connect = connect
        self.fields = fields

    def create_sensors(self, station):
        # loop all fields
        types = {}
        for field, typ in self.fields.items():
            print(typ['code'], typ['name'], typ['unit'])

            # get or create sensor type
            # sensor_type = SensorType.objects.get_or_create(code=typ['code'], name=typ['name'], unit=typ['unit'])

            # get or create sensor
            # Sensor.objects.get_or_create(station=station, type=sensor_type)

    def update(self, station):
        log.info('Updating Database station %s...' % station.code)

        # connect to DB
        MySQLdb.connect(**self.connect)
