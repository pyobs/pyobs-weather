REST API Reference
###################

Mounted under ``/api/``, unauthenticated, all endpoints return JSON.

Config
******

``GET /api/config/`` — site name, window title, root URL, app version, the configured
``value_types``/``plot_types`` (see :doc:`configuration`), and the observer location. This is what
the Vue frontend bootstraps itself from.

Current weather
****************

``GET /api/current/`` — current values for all sensor types, and whether each is "good"::

    $ http https://weather.example.com/api/current/

    {
        "time": "2020-02-13T10:44:29.302Z",
        "good": false,
        "sensors": {
            "humid": {"good": true, "value": 15.75},
            "skytemp": {"good": false, "value": -19.43},
            "windspeed": {"good": true, "value": 32.21}
        }
    }

A sensor's ``good`` is ``null`` if it has no evaluator attached (see :doc:`architecture`); the
top-level ``good`` is the AND of every non-null sensor.

Stations
********

``GET /api/stations/`` — list of active stations (``code``, ``name``).

``GET /api/stations/<station_code>/`` — that station's sensors, each with its latest value and
timestamp.

``GET /api/stations/<station_code>/<sensor_code>/`` — a single sensor's latest value, plus
``good``, ``since``, and ``unit``.

``GET /api/sensors/`` — flat list of every active sensor across every station, with station/type
metadata, latest value, and evaluator limit areas (used to shade plots) inlined.

History
*******

``GET /api/history/`` — list of sensor-type codes that have history available.

``GET /api/history/<sensor_type>/`` — history for one sensor type across all history-enabled
stations, from InfluxDB. Accepts ``start``/``end`` query params (default: last 24h)::

    $ http https://weather.example.com/api/history/temp/

    {
        "stations": [
            {
                "code": "monet",
                "name": "MONET",
                "color": "#...",
                "data": [
                    {"time": "2020-02-13T10:50:00Z", "value": 25.7, "min": 25.1, "max": 26.0}
                ]
            }
        ],
        "areas": [...]
    }

``areas`` are the evaluator-defined danger/warning bands for the synthetic "Average" station's
sensor of this type (see :doc:`evaluators/index`), used to shade the plot.

``GET /api/history/goodweather/`` — good/bad status changes over the last 24h, as
``[{"time": ..., "good": ...}, ...]``.

Timeline
********

``GET /api/timeline/`` — sunset, -12° (astronomical) twilight at sunset, -12° twilight at
sunrise, and sunrise, for the observer location, as ISO timestamps — used to shade day/night on
the frontend's plots.
