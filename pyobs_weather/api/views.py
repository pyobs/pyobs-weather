import pytz
from astropy.time import Time, TimeDelta
import astropy.units as u
from django.db.models import F
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render

from pyobs_weather.weather.models import Station, Sensor, Value, SensorType


def stations_list(request):
    # get list of stations and return them
    stations = Station.objects.values('name', 'code')
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
    average = Station.objects.get(code='average')
    if average is None:
        return HttpResponseNotFound('Could not access average weather.')

    # loop all sensors
    data = {}
    for sensor in Sensor.objects.all():
        # create, if necessary
        if sensor.type.code not in data:
            data[sensor.type.code] = {
                'code': sensor.type.code,
                'name': sensor.type.name,
                'unit': sensor.type.unit,
                'good': True,
                'value': None
            }

        # set it
        data[sensor.type.code]['good'] = sensor.good and data[sensor.type.code]['good']

        # is average sensor?
        if sensor.station == average:
            # get latest value
            value = Value.objects.filter(sensor=sensor).order_by('-time').first()

            # set it
            data[sensor.type.code]['value'] = None if value is None else value.value

    # get list of sensors
    sensors = sorted(data.values(), key=lambda d: d['code'])

    # totally good?
    good = True
    for sensor in sensors:
        good = good and sensor['good']

    # return all
    return JsonResponse({
        'good': good,
        'sensors': list(sensors)
    })


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
        start = Time(start)
        end = Time(end)
    else:
        end = Time.now()
        start = end - TimeDelta(1 * u.day)

    # loop all sensors of that type
    stations = []
    for sensor in Sensor.objects.filter(type=st):
        # get data
        values = Value.objects.filter(sensor=sensor,
                                      time__gte=start.to_datetime(pytz.UTC),
                                      time__lte=end.to_datetime(pytz.UTC)).order_by('-time').values('time', 'value')

        # store it
        stations.append({
            'code': sensor.station.code,
            'name': sensor.station.name,
            'color': sensor.station.color,
            'data': list(values)
        })

    return JsonResponse(stations, safe=False)
