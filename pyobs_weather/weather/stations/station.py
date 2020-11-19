from pyobs_weather.weather.models import Value, Station, SensorType, Sensor

SENSOR_TYPES = dict(
    temp=dict(code='temp', name='Temperature', unit='°C'),
    humid=dict(code='humid', name='Relative humidity', unit='%'),
    press=dict(code='press', name='Pressure', unit='hPa'),
    winddir=dict(code='winddir', name='Wind dir', unit='°E of N'),
    windspeed=dict(code='windspeed', name='Wind speed', unit='km/h'),
    particles=dict(code='particles', name='Particle count', unit='ppcm'),
    rain=dict(code='rain', name='Raining', unit=''),
    skytemp=dict(code='skytemp', name='Rel sky temperature', unit='°C'),
    sunalt=dict(code='sunalt', name='Solar altitude', unit='°', average=False)
)


class WeatherStation:
    def __init__(self, station: Station, *args, **kwargs):
        self._station = station

    def _add_sensor(self, sensor_code):
        """Add a sensor type and a sensor, if necessary.

        Args:
            sensor_code: Code of sensor type to add.
        """

        # does sensor type exist?
        try:
            # get it
            sensor_type = SensorType.objects.get(code=sensor_code)

        except SensorType.DoesNotExist:
            # do we have a description?
            if sensor_code not in SENSOR_TYPES:
                raise ValueError('Unknown sensor type: %s' % sensor_code)

            # add it
            sensor_type = SensorType.objects.create(**SENSOR_TYPES[sensor_code])

        # now add sensor itself
        sensor, _ = Sensor.objects.get_or_create(station=self._station, type=sensor_type)

        # return it
        return sensor

    def _add_value(self, sensor_code, time, value):
        """Add a value for the given sensor

        Args:
            sensor_code: Code for sensor
            time: Time of measurement
            value: Measured value
        """

        # get sensor
        sensor = Sensor.objects.get(station=self._station, type__code=sensor_code)

        # create value
        Value.objects.get_or_create(sensor=sensor, time=time, defaults={'value': value})


__all__ = ['WeatherStation']
