from typing import List, Tuple, Optional
from influxdb_client import InfluxDBClient, Point
from datetime import datetime
from influxdb_client.client.write_api import SYNCHRONOUS

from pyobs_weather.settings import (
    INFLUXDB_URL,
    INFLUXDB_ORG,
    INFLUXDB_TOKEN,
    INFLUXDB_BUCKET,
    INFLUXDB_BUCKET_5MIN,
)
from pyobs_weather.weather.models import Station, Sensor


def read_sensor_value(sensor):
    with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
        query = f"""
            from(bucket:"{INFLUXDB_BUCKET}")
                |> range(start: -5m)\
                |> filter(fn:(r) => r._measurement == "{sensor.station.code}")
                |> filter(fn:(r) => r._field == "{sensor.type.code}")
                |> last()
            """
        result = client.query_api().query(org=INFLUXDB_ORG, query=query)
        value = result.to_values(columns=["_time", "_value"])

        return {"time": value[0][0], "value": value[0][1]} if len(value) > 0 else None


def read_sensor_values(sensor, start, end, agg_type: str = "mean"):
    with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
        query = f"""
            from(bucket:"{INFLUXDB_BUCKET_5MIN}")
                |> range(start: {start.strftime('%Y-%m-%dT%H:%M:%SZ')}, stop: {end.strftime('%Y-%m-%dT%H:%M:%SZ')})\
                |> filter(fn:(r) => r._measurement == "{sensor.station.code}")
                |> filter(fn:(r) => r.agg_type == "{agg_type}")            
                |> filter(fn:(r) => r._field == "{sensor.type.code}")
            """
        result = client.query_api().query(org=INFLUXDB_ORG, query=query)
        temp = result.to_values(columns=["_time", "_value"])

        values = []
        for value in temp:
            values.append({"time": value[0].strftime("%Y-%m-%dT%H:%M:%SZ"), "value": value[1]})

        return values


def write_sensor_value(sensor: Sensor, time: datetime, value: float, station: Optional[str] = None):
    """Write single value to influx.

    Args:
        sensor: Sensor to write value for.
        time: Time of sensor reading.
        value: Value of reading.
    """

    # if station name is None, set it to sensor station code
    if station is None:
        station = sensor.station.code

    # connect to db and write
    with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        p = Point(station).field(sensor.type.code, value).time(time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=p)


def write_sensor_values(time: datetime, station: Station, values: List[Tuple[str, float]]) -> None:
    """Write a whole set of measurements to influx.

    Args:
        time: Time of measurements.
        station: Station to write for.
        values: List of [str, float] tuples with sensor readings.

    Returns:

    """
    with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        p = Point(station.code)
        for sensor, value in values:
            p = p.field(sensor, value)
        p = p.time(time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=p)
