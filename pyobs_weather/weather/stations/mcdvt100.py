import logging
import re
from datetime import datetime
import pytz
from astropy.time import Time
import requests

from .station import WeatherStation

log = logging.getLogger(__name__)


def parse_val(val: str, number: bool = True):
    warning = False

    # do we have escape sequences?
    escape = re.compile('(\x1b\[|\x9b)[^@-_]*[@-_]|\x1b[@-_]', re.I)
    if escape.search(val):
        # yes, replace them and set warning
        warning = True
        val = escape.sub("", val)

    # to float
    if number:
        try:
            val = float(val)
        except ValueError:
            val = None

    return val, warning


class McDonaldVt100(WeatherStation):
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
        # 2nd line is title
        if 'MT. LOCKE WEATHER TOWER  +  NWS RADAR WARNINGS' not in lines[1]:
            log.error('Second line does not contain "MT. LOCKE WEATHER TOWER  +  NWS RADAR WARNINGS')
            return

        # 1st line is date
        ds = lines[0][20:].strip().split()
        date_line = f"{ds[2]} {ds[1]} {ds[5]} {ds[3]}"
        dt = datetime.datetime.strptime(date_line, "%d %b %Y %H:%M:%S").astimezone(pytz.timezone('US/Central'))

        # compare with today
        now = datetime.datetime.now(pytz.timezone('US/Central'))
        if dt.date() != now.date():
            log.error('Weather data from server not for today.')
            return

        # 3rd, 4th, and 5th lines
        if lines[3].strip() != 'DATE       TIME | TEMP  RH  DEWPT|WIND GUST WDIR|PRESSURE|DUST|RAIN':
            log.error('Column headers do not match.')
            return
        if lines[4].strip() != 'YYYY-MM-DD UTC  | DEG_F  %  DEG_F|MPH  MPH  DEG |INCH_HG |KCNT|Y?N':
            log.error('Units do not match.')
            return

        # finally, 6th line is current weather
        s = [l.strip() for l in lines[5].split()]

        # time is easy, just concatenate date and time
        time = datetime.datetime.strptime(f"{s[0]} {s[1]}:00", "%Y-%m-%d %H:%M:%S")

        # warning
        warning = False

        # convert temp from °F to °C
        temp, warn = parse_val(s[2])
        temp = (temp - 32) / 1.8
        warning |= warn

        # humidity
        humid, warn = parse_val(s[3])
        # warning |= warn

        # dew point, given in °F, convert to °C
        dew_pt, warn = parse_val(s[4])
        dew_pt = (dew_pt - 32) / 1.8
        warning |= warn

        # wind speed, convert from mph to kmh
        wind_speed, warn = parse_val(s[5])
        wind_speed /= 1.609344
        warning |= warn

        # wind dir
        wind_dir, warn = parse_val(s[6])
        warning |= warn

        # pressure, convert from inHg to hPa
        press, warn = parse_val(s[8])
        press *= 33.86389
        warning |= warn

        # particle count, convert from kilo particles per ft³ to particles per m³
        particles, warn = parse_val(s[9])
        particles *= 3.2808 * 3 * 1000
        warning |= warn

        # rain
        val, warn = parse_val(s[10], number=False)
        rain = val != 'N'
        warning |= warn

        # got all values, now add them
        self._add_value('temp', time, temp)
        self._add_value('humid', time, humid)
        self._add_value('press', time, press)
        self._add_value('winddir', time, wind_dir)
        self._add_value('windspeed', time, wind_speed)
        self._add_value('particles', time, particles)
        self._add_value('rain', time, rain)


__all__ = ['McDonaldVt100']
