import logging
from datetime import datetime

import pytz
from astropy.time import Time
import requests

from pyobs_weather.celery import app


log = logging.getLogger(__name__)


@app.task
def update():
    from pyobs_weather.main.models import Weather

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
    time = Time(now.strftime('%Y-%m-%d') + ' ' + s[0] + ':00')

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

    # got all values, now try to find in database
    if Weather.objects.filter(station='mcd_locke', time=time.to_datetime(pytz.UTC)).count() > 0:
        return

    # add it
    w = Weather()
    w.time = time.to_datetime(pytz.UTC)
    w.station = 'mcd_locke'
    w.temp = temp
    w.humid = humid
    w.dewpoint = dew_pt
    w.press = press
    w.winddir = wind_dir
    w.windspeed = wind_speed
    w.particles = particles
    w.rain = rain
    w.save()
