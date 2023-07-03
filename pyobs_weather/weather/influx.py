from influxdb_client import InfluxDBClient, Point

from pyobs_weather.settings import (
    INFLUXDB_URL,
    INFLUXDB_ORG,
    INFLUXDB_TOKEN,
    INFLUXDB_BUCKET,
    INFLUXDB_BUCKET_5MIN,
)

# TODO: Bucket als function argument bei allen. Influx Werte hierher, statt settings?


def get_value(station_code, sensor_code, avg=False):
    bucket = INFLUXDB_BUCKET_5MIN if avg else INFLUXDB_BUCKET
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query = f"""
        from(bucket:"{bucket}")
            |> range(start: -10m)\
            |> filter(fn:(r) => r._measurement == "{station_code}")
            |> filter(fn: (r) => r["_field"] == "{sensor_code}")
            |> last()
        """
    result = client.query_api().query(org=INFLUXDB_ORG, query=query)
    value = result.to_values(columns=("_time", "_value"))

    return (
        value[0] if len(value) > 0 else None
    )  # [[]] -> [], where return_value[0] = time and return_value[1] = value


def get_list_from_influx(
    station_code, sensor_code, start, end
):  # TODO geeigneten Namen finden
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query = f"""
        from(bucket:"{INFLUXDB_BUCKET_5MIN}")
            |> range(start: {start}, stop: {end})\
            |> filter(fn:(r) => r._measurement == "{station_code}")
            |> filter(fn: (r) => r["_field"] == "{sensor_code}")
        """
    result = client.query_api().query(org=INFLUXDB_ORG, query=query)
    return result.to_values(columns=("_time", "_value"))


def write_value(station_code, sensor_code, time, value, avg=False):
    bucket = INFLUXDB_BUCKET_5MIN if avg else INFLUXDB_BUCKET

    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = client.write_api()
    p = Point(station_code).field(sensor_code, value).time(time)
    write_api.write(bucket=bucket, record=p)


def write_current(station_code, sensor_code, time, value, avg=False):
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = client.write_api()
    p = Point(station_code).field(sensor_code, value).time(time)
    write_api.write(bucket=INFLUXDB_BUCKET_CURRENT, record=p)


def get_current(station_code, sensor_code):
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query = f"""
        from(bucket:"{INFLUXDB_BUCKET_CURRENT}")
            |> range(start: -10m)\
            |> filter(fn:(r) => r._measurement == "{station_code}")
            |> filter(fn: (r) => r["_field"] == "{sensor_code}")
            |> last()
        """
    result = client.query_api().query(org=INFLUXDB_ORG, query=query)
    value = result.to_values(columns=("_time", "_value"))

    return value[0] if len(value) > 0 else None
