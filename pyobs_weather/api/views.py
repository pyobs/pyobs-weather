from datetime import datetime, timedelta
import dateutil.parser
from astroplan import Observer
from astropy.coordinates import EarthLocation
from astropy.time import Time, TimeDelta
import astropy.units as u
from django.conf import settings
from django.db.models import F
from django.http import JsonResponse, HttpResponseNotFound
import numpy as np

from pyobs_weather.weather import evaluators
from pyobs_weather.weather.models import Station, Sensor, Value, SensorType, GoodWeather
from pyobs_weather.weather.tasks import create_evaluator


def stations_list(request):
    # get list of stations and return them
    stations = Station.objects.filter(active=True).values('name', 'code')
    return JsonResponse(list(stations), safe=False)


def station_detail(request, station_code):
    # get station
    station = Station.objects.get(code=station_code)
    if station is None:
        return HttpResponseNotFound("Station not found.")

    # get list of sensors
    sensors = []
    for sensor in Sensor.objects.filter(station=station):
        # get latest value
        value = Value.objects.filter(sensor=sensor).order_by('-time').first()

        # append
        sensors.append({
            'name': sensor.type.name,
            'code': sensor.type.code,
            'value': None if value is None else value.value,
            'time': None if value is None else value.time
        })

    # return all
    return JsonResponse({
        'name': station.name,
        'code': station.code,
        'sensors': list(sensors)
    })


def sensor_detail(request, station_code, sensor_code):
    # get station and sensor
    station = Station.objects.get(code=station_code)
    if station is None:
        return HttpResponseNotFound("Station not found.")
    sensor = Sensor.objects.get(type__code=sensor_code, station=station)
    if sensor is None:
        return HttpResponseNotFound("Sensor not found.")

    # get latest value
    value = Value.objects.filter(sensor=sensor).order_by('-time').first()

    # return it
    return JsonResponse({
        'name': sensor.type.name,
        'code': sensor.type.code,
        'value': None if value is None else value.value,
        'unit': sensor.type.unit,
        'time': None if value is None else value.time,
        'good': sensor.good,
        'since': sensor.since
    })


def current(request):
    # get average station
    station = Station.objects.get(code='current')
    if station is None:
        return HttpResponseNotFound('Could not access current weather.')

    # loop all sensors
    sensors = {}
    time = None
    for sensor in Sensor.objects.filter(station__active=True):
        # create, if necessary
        if sensor.type.code not in sensors:
            sensors[sensor.type.code] = {
                'good': None,
                'value': None
            }

        # set it
        if sensor.good is not None:
            # if current value is None, set it with new one, otherwise and it
            if sensors[sensor.type.code]['good'] is None:
                sensors[sensor.type.code]['good'] = sensor.good
            else:
                sensors[sensor.type.code]['good'] = sensor.good and sensors[sensor.type.code]['good']

        # is average sensor?
        if sensor.station == station:
            # get latest value
            value = Value.objects.filter(sensor=sensor).order_by('-time').first()

            # set it
            sensors[sensor.type.code]['value'] = None if value is None else value.value
            time = value.time

    # totally good?
    good = True
    for sensor in sensors.values():
        if sensor['good'] is not None:
            good = good and sensor['good']

    # return all
    return JsonResponse({
        'time': time,
        'good': good,
        'sensors': sensors
    })


def history_types(request):
    # loop sensors
    qs = Sensor.objects.filter(station__history=True).values('type__code')
    types = list(set(v['type__code'] for v in qs))
    return JsonResponse(types, safe=False)


def history(request, sensor_type):
    # get sensor_type
    st = SensorType.objects.get(code=sensor_type)
    if st is None:
        return HttpResponseNotFound('Could not find sensor type.')

    # start and end
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)

    # parse
    if start is not None and end is not None:
        start = dateutil.parser.parse(start)
        end = dateutil.parser.parse(end)
    else:
        end = datetime.utcnow()
        start = end - timedelta(days=1)

    # loop all sensors of that type
    stations = []
    areas = []
    for sensor in Sensor.objects.filter(type=st, station__history=True, station__active=True):
        # get data
        values = Value.objects.filter(sensor=sensor, time__gte=start, time__lte=end)\
            .order_by('-time').values('time', 'value')

        # got average sensor?
        if sensor.station.code == 'average':
            # loop all evaluators for this sensor to define coloured areas in plot
            for evaluator in sensor.evaluators.all():
                # get evaluator
                eva = create_evaluator(evaluator)

                # add areas
                if hasattr(eva, 'areas'):
                    areas.extend(eva.areas())

        # store it
        stations.append({
            'code': sensor.station.code,
            'name': sensor.station.name,
            'color': sensor.station.color,
            'data': list(values),
            'areas': areas
        })

    return JsonResponse({'stations': stations, 'areas': areas}, safe=False)


def sensors(request):
    # get all sensors
    data = Sensor.objects.filter(station__active=True)

    # add station and type
    data = data.annotate(station_code=F('station__code'), station_name=F('station__name'))
    data = data.annotate(type_code=F('type__code'), type_name=F('type__name'), unit=F('type__unit'))

    # order
    data = data.order_by('station_name', 'type_name')

    # get values
    values = list(data.values())

    # add latest value
    for i, sensor in enumerate(data):
        val = Value.objects.filter(sensor=sensor).order_by('-time').first()
        values[i]['value'] = None if val is None else val.value

    # return all
    return JsonResponse(values, safe=False)


def timeline(request):
    # get location
    location = EarthLocation(lon=settings.OBSERVER_LOCATION['longitude'] * u.deg,
                             lat=settings.OBSERVER_LOCATION['latitude'] * u.deg,
                             height=settings.OBSERVER_LOCATION['elevation'] * u.m)

    # get observer and now
    now = Time.now()
    observer = Observer(location=location)

    # night or day?
    is_day = observer.sun_altaz(now).alt.degree > 0.

    # get sunset to start with
    sunset = observer.sun_set_time(now, which='next' if is_day else 'previous')

    # list of events
    events = []
    events.append(sunset.isot)

    # twilight at sunset
    sunset_twilight = observer.sun_set_time(sunset, which='next', horizon=-12. * u.deg)
    events.append(sunset_twilight.isot)

    # twilight at sunrise
    sunrise_twilight = observer.sun_rise_time(sunset_twilight, which='next', horizon=-12. * u.deg)
    events.append(sunrise_twilight.isot)

    # sunrise
    sunrise = observer.sun_rise_time(sunset_twilight, which='next')
    events.append(sunrise.isot)

    # return all
    return JsonResponse({'time': now.isot, 'events': events})


def good_weather(request):
    # get changes in status from last 24 hours
    changes = [{'time': g.time, 'good': g.good}
               for g in GoodWeather.objects.filter(time__gt=datetime.utcnow() - timedelta(days=1)).all()]

    # get location
    location = EarthLocation(lon=settings.OBSERVER_LOCATION['longitude'] * u.deg,
                             lat=settings.OBSERVER_LOCATION['latitude'] * u.deg,
                             height=settings.OBSERVER_LOCATION['elevation'] * u.m)

    # get observer and now
    now = Time.now()
    observer = Observer(location=location)

    # get solar elevation for last 12 hours
    times = [now - TimeDelta((1. - x) * u.day) for x in np.linspace(0, 1, 100)]
    sun = [s.alt.degree for s in observer.sun_altaz(times)]

    # return all
    return JsonResponse({'changes': changes, 'sun': {'time': [t.isot for t in times], 'alt': sun}})
