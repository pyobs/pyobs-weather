from influxdb_client import InfluxDBClient, Point
from datetime import datetime

from pyobs_weather.settings import INFLUXDB_URL, INFLUXDB_ORG, INFLUXDB_TOKEN, INFLUXDB_BUCKET, INFLUXDB_BUCKET_5MIN, INFLUXDB_BUCKET_CURRENT, USE_INFLUX
from pyobs_weather.weather.models import Station, Sensor, Value, SensorType

#------------------------
# general functions
#------------------------
def get_value(sensor):
    value = None
    if USE_INFLUX:
        value = influx_getv(sensor)
    else:
        temp = psql_getv(sensor)
        if temp is not None:
            value = {'time': temp.time, 'value': temp.value}
    return value


def get_list(sensor, start, end):
    values = []
    if USE_INFLUX:
        values = influx_getlist(sensor, start, end)
    else:
        values = list(psql_getlist(sensor, start, end))
    return values


def write_value(sensor, time, value):
    if USE_INFLUX:
        influx_write(sensor, time, value)
    else:
        psql_write(sensor, time, value)


#------------------------
# Postgresql functions
#------------------------
def psql_getv(sensor):
    return Value.objects.filter(sensor=sensor).order_by('-time').first()

def psql_getlist(sensor, start, end):
    return Value.objects.filter(sensor=sensor, time__gte=start, time__lte=end).order_by('-time').values('time', 'value')

def psql_write(sensor, time, value):
    Value.objects.get_or_create(sensor=sensor, time=time, value=value)


#------------------------
# InfluxDB functions
#------------------------
def influx_getv(sensor):
    bucket = get_bucket(sensor.station.code)

    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query = f"""
        from(bucket:"{bucket}")
            |> range(start: -10m)\
            |> filter(fn:(r) => r._measurement == "{sensor.station.code}")
            |> filter(fn: (r) => r["_field"] == "{sensor.type.code}")
            |> last()
        """
    result = client.query_api().query(org=INFLUXDB_ORG, query=query)
    value = result.to_values(columns=('_time','_value'))

    return {'time': value[0][0].strftime("%Y-%m-%dT%H:%M:%S.%fZ"), 'value': value[0][1]} if len(value) > 0 else None


def influx_getlist(sensor, start, end):
    bucket = get_bucket(sensor.station.code)

    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query = f"""
        from(bucket:"{bucket}")
            |> range(start: {start.timestamp()}, stop: {end.timestamp()})\
            |> filter(fn:(r) => r._measurement == "{sensor.station.code}")
            |> filter(fn: (r) => r["_field"] == "{sensor.type.code}")
        """
    result = client.query_api().query(org=INFLUXDB_ORG, query=query)
    temp = result.to_values(columns=('_time','_value'))

    values = []
    for value in temp:
        values.append({"time": value[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ"), "value": value[1]})

    return values


def influx_write(sensor, time, value):
    bucket = get_bucket(sensor.station.code)

    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = client.write_api()
    p = Point(sensor.station.code).field(sensor.type.code, value).time(time)
    write_api.write(bucket=bucket, record=p)

# helping function to determine which bucket to use
def get_bucket(sensor_code):
    bucket = None
    if sensor_code == 'average':
        bucket = INFLUXDB_BUCKET_5MIN
    elif sensor_code == 'current':
        bucket = INFLUXDB_BUCKET_CURRENT
    else:
        bucket = INFLUXDB_BUCKET
    return bucket