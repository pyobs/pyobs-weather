import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from pyobs_weather.weather.models import Sensor, SensorType, Station


class _TestStationHandler:
    """Minimal station handler for tests.

    Station.save() calls get_class(class_name)(station=...).create_sensors(), and every real
    handler lives under pyobs_weather.weather.stations, whose __init__.py unconditionally
    imports mcdtelnet -- which imports the stdlib telnetlib module, removed in Python 3.13. That's
    a pre-existing bug unrelated to this endpoint, so this handler stays outside that package
    entirely rather than depending on a fix for it.
    """

    def __init__(self, station, **kwargs):
        self._station = station

    def create_sensors(self):
        for code, name, unit in [
            ("temp", "Temperature", "°C"),
            ("humid", "Relative humidity", "%"),
        ]:
            sensor_type, _ = SensorType.objects.get_or_create(code=code, defaults={"name": name, "unit": unit})
            Sensor.objects.get_or_create(station=self._station, type=sensor_type)


class MeViewTests(TestCase):
    def test_anonymous_user_is_not_authenticated(self):
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"authenticated": False, "username": None})

    def test_logged_in_user_is_authenticated(self):
        user = User.objects.create_user(username="someone", password="secret")
        self.client.force_login(user)

        response = self.client.get(reverse("me"))

        self.assertEqual(json.loads(response.content), {"authenticated": True, "username": "someone"})


class HistoryExportViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.station = Station.objects.create(
            code="teststation",
            name="Test Station",
            class_name="pyobs_weather.api.tests._TestStationHandler",
            history=True,
            active=True,
        )
        cls.no_history_station = Station.objects.create(
            code="nohistory",
            name="No History Station",
            class_name="pyobs_weather.api.tests._TestStationHandler",
            history=False,
            active=True,
        )

    def _login(self):
        user = User.objects.create_user(username="someone", password="secret")
        self.client.force_login(user)

    def _url(self, code):
        return reverse("history_export", args=[code])

    def test_anonymous_user_gets_401(self):
        response = self.client.get(self._url("teststation"), {"start": "2026-01-01", "end": "2026-01-02"})
        self.assertEqual(response.status_code, 401)

    def test_missing_dates_returns_400(self):
        self._login()
        response = self.client.get(self._url("teststation"))
        self.assertEqual(response.status_code, 400)

    def test_station_without_history_returns_404(self):
        self._login()
        response = self.client.get(self._url("nohistory"), {"start": "2026-01-01", "end": "2026-01-02"})
        self.assertEqual(response.status_code, 404)

    def test_unknown_station_returns_404(self):
        self._login()
        response = self.client.get(self._url("doesnotexist"), {"start": "2026-01-01", "end": "2026-01-02"})
        self.assertEqual(response.status_code, 404)

    @patch("pyobs_weather.api.views.read_sensor_values")
    def test_authenticated_user_gets_rounded_csv_with_blanks_for_missing_data(self, mock_read):
        # only "temp" has any data -- every other active sensor (humid/winddir/windspeed/press/
        # rain) should still get a column, just with blank cells, not be dropped or error
        def fake_read(sensor, start, end, agg_type="mean"):
            if sensor.type.code != "temp":
                return []
            return [{"time": "2026-01-01T00:00:00Z", "value": {"mean": 12.3456, "min": 12.0, "max": 12.5}[agg_type]}]

        mock_read.side_effect = fake_read
        self._login()

        response = self.client.get(self._url("teststation"), {"start": "2026-01-01", "end": "2026-01-02"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn('attachment; filename="teststation_2026-01-01_2026-01-02.csv"', response["Content-Disposition"])

        content = b"".join(response.streaming_content).decode()
        rows = [line.split(",") for line in content.strip().split("\r\n")]
        header, data_row = rows[0], rows[1]

        self.assertEqual(len(rows), 2)  # header + one timestamp row
        self.assertEqual(data_row[0], "2026-01-01T00:00:00Z")
        self.assertEqual(data_row[header.index("temp_mean")], "12.35")  # rounded to 2 decimals
        self.assertEqual(data_row[header.index("humid_mean")], "")  # no data -> blank, not dropped
