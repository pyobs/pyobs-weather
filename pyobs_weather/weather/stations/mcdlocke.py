import logging
from datetime import datetime
import pytz
from astropy.time import Time
import requests

from .station import WeatherStation
from pyobs_weather.weather.models import Value, Sensor, SensorType

log = logging.getLogger(__name__)


class McDonaldLocke(WeatherStation):
    @staticmethod
    def create_sensors(station):
        # get or create types
        type_temp, _ = SensorType.objects.get_or_create(code='temp', name='Temperature', unit='°C')
        type_humid, _ = SensorType.objects.get_or_create(code='humid', name='Relative humidity', unit='%')
        type_press, _ = SensorType.objects.get_or_create(code='press', name='Pressure', unit='hPa')
        type_winddir, _ = SensorType.objects.get_or_create(code='winddir', name='Wind dir', unit='°E of N')
        type_windspeed, _ = SensorType.objects.get_or_create(code='windspeed', name='Wind speed', unit='km/h')
        type_particles, _ = SensorType.objects.get_or_create(code='particles', name='Particle count', unit='ppcm')
        type_rain, _ = SensorType.objects.get_or_create(code='rain', name='Raining', unit='0/1')

        # get or create sensors
        Sensor.objects.get_or_create(station=station, type=type_temp)
        Sensor.objects.get_or_create(station=station, type=type_humid)
        Sensor.objects.get_or_create(station=station, type=type_press)
        Sensor.objects.get_or_create(station=station, type=type_winddir)
        Sensor.objects.get_or_create(station=station, type=type_windspeed)
        Sensor.objects.get_or_create(station=station, type=type_particles)
        Sensor.objects.get_or_create(station=station, type=type_rain)

    @staticmethod
    def update(station):
        log.info('Updating McDonald Locke station %s...' % station.code)

        # do request
        r = requests.get('http://weather.as.utexas.edu/latest_5min.dat')

        # check code
        if r.status_code != 200:
            logging.error('Could not connect to McDonald weather station.')
            return

        # split lines
        lines = [l.strip() for l in r.text.split('\n')]

        # do checks
        # 1st line is title
        if 'Mt. LOCKE LOCAL WEATHER' not in lines[0]:
            log.error('First line does not contain "Mt. LOCKE LOCAL WEATHER')
            return

        # 2nd line is date
        if 'Current Date GMT' not in lines[1]:
            log.error('No date given in response from server.')
            return
        # strip line and capitalize first letter of month
        date = lines[1][18:21] + lines[1][21].upper() + lines[1][22:]
        # compare with today
        now = datetime.utcnow()
        if now.strftime('%d-%b-%Y') != date:
            log.error('Weather data from server not for today.')
            return

        # 3rd, 4th, and 5th lines
        if lines[2] != '|TEMP.|HUMID|DEW PT.| BAROM | WIND_DIR | WIND SPEED  | PARTICLE |  RAIN':
            log.error('Column headers do not match.')
            return
        if lines[3] != 'TIME  | avg | avg |  avg  | PRESS | avg stdev| avg max min |  COUNT   |  Y/N':
            log.error('Column headers do not match.')
            return
        if lines[4] != '-[GMT]-|-[F]-|-[%]-|--[F]--|[In.Hg]|---[Az]---|----[MPH]----|--[ppcf]--|[on/off]':
            log.error('Units do not match.')
            return

        # finally, 6th line is current weather
        s = [l.strip() for l in lines[5].split('|')]

        # time is easy, just concatenate date and time
        time = Time(now.strftime('%Y-%m-%d') + ' ' + s[0] + ':00').to_datetime(pytz.UTC)

        # convert temp from °F to °C
        try:
            temp = (float(s[1]) - 32) / 1.8
        except ValueError:
            temp = None

        # humidity
        try:
            humid = float(s[2])
        except ValueError:
            humid = None

        # dew point, given in °F, convert to °C
        try:
            dew_pt = (float(s[3]) - 32) / 1.8
        except ValueError:
            dew_pt = None

        # pressure, convert from inHg to hPa
        try:
            press = float(s[4]) * 33.86389
        except ValueError:
            press = None

        # wind dir, given as "avg ~ std"
        try:
            tmp = s[5].split('~')
            wind_dir = float(tmp[0])
        except ValueError:
            wind_dir = None

        # wind speed, given as "avg max min", convert from mph to kmh
        try:
            tmp = s[6].split()
            wind_speed = float(tmp[1]) / 1.609344
        except ValueError:
            wind_speed = None

        # particle count, convert from particles per ft³ to particles per m³
        try:
            particles = float(s[7]) * 3.2808 ** 3
        except ValueError:
            particles = None

        # rain
        rain = s[8] == 'Y'

        # got all values, now add them
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='temp'),
                                  time=time, value=temp)
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='humid'),
                                  time=time, value=humid)
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='press'),
                                  time=time, value=press)
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='winddir'),
                                  time=time, value=wind_dir)
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='windspeed'),
                                  time=time, value=wind_speed)
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='particles'),
                                  time=time, value=particles)
        WeatherStation._add_value(sensor=Sensor.objects.get(station=station, type__code='rain'),
                                  time=time, value=rain)
