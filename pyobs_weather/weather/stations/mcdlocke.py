import logging
from datetime import datetime
import pytz
from astropy.time import Time
import requests

from .station import WeatherStation

log = logging.getLogger(__name__)


class McDonaldLocke(WeatherStation):
    """The McDonaldLocke weather station reads current weather information from the Mt. Lock weather page at
    http://weather.as.utexas.edu/latest_5min.dat.

    It does not require any configuration.
    """

    def create_sensors(self):
        """Entry point for creating sensors for this station.

        Sensors created by this station are:

        - temp

        - humid

        - winddir

        - windspeed

        - particles

        - rain
        """
        self._add_sensor('temp')
        self._add_sensor('humid')
        self._add_sensor('press')
        self._add_sensor('winddir')
        self._add_sensor('windspeed')
        self._add_sensor('particles')
        self._add_sensor('rain')

    def update(self):
        """Entry point for updating sensor values for this station.

        This method reads the Mt. Locke weather page and extracts the latest values."""
        log.info('Updating McDonald Locke station %s...' % self._station.code)

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
        self._add_value('temp', time, temp)
        self._add_value('humid', time, humid)
        self._add_value('press', time, press)
        self._add_value('winddir', time, wind_dir)
        self._add_value('windspeed', time, wind_speed)
        self._add_value('particles', time, particles)
        self._add_value('rain', time, rain)


__all__ = ['McDonaldLocke']
