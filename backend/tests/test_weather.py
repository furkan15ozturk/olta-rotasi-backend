from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.weather import normalize, HOURLY, DAILY, TR
import pytest


def fixture():
    start = datetime(2026, 10, 13, tzinfo=TR)
    timestamps = [start + timedelta(hours=i) for i in range(-24, 168)]
    return {
        'utc_offset_seconds': 10800,
        'latitude': 38.4, 'longitude': 26.6,
        'hourly': {'time': [t.strftime('%Y-%m-%dT%H:%M') for t in timestamps], **{k: [float(i) for i in range(192)] for k in HOURLY}},
        'hourly_units': {k: unit for k, (_, unit) in HOURLY.items()},
        'daily': {'time': [(start + timedelta(days=i)).date().isoformat() for i in range(-1, 7)], **{k: [10] * 8 for k in DAILY}},
        'daily_units': {k: unit for k, (_, unit) in DAILY.items()},
    }


def test_local_dates_future_hours_and_pressure_difference():
    raw = fixture()
    raw['hourly']['wind_speed_10m'][35] = None
    now = datetime(2026, 10, 13, 7, 30, tzinfo=timezone.utc)  # 10:30 TR
    result = normalize(raw, now)
    assert len(result['days']) == 7
    first = result['days'][0]['hours'][0]
    assert first['time'] == '2026-10-13T11:00:00+03:00'
    assert first['pressure_change_3h_hpa'] == 3.0
    assert first['wind_kmh'] is None
    assert result['model_run_at'] is None
    assert result['catch_probability'] is None


def test_invalid_units_and_missing_series_rejected():
    raw = fixture()
    raw['hourly_units']['wind_speed_10m'] = 'm/s'
    with pytest.raises(ValueError):
        normalize(raw, datetime(2026, 10, 13, tzinfo=TR))
    raw = fixture()
    raw['hourly']['pressure_msl'].pop()
    with pytest.raises(ValueError):
        normalize(raw, datetime(2026, 10, 13, tzinfo=TR))


def test_pressure_missing_does_not_become_zero():
    raw = fixture()
    raw['hourly']['pressure_msl'][24] = None
    result = normalize(raw, datetime(2026, 10, 13, 3, tzinfo=TR))
    assert result['days'][0]['hours'][0]['pressure_change_3h_hpa'] is None


def test_forecast_endpoint_errors_and_coordinate_validation(monkeypatch):
    client = TestClient(app)
    assert client.post('/v1/forecast', json={'latitude': 26, 'longitude': 38}).status_code == 422
    def fail(*args):
        raise TimeoutError()
    monkeypatch.setattr('app.weather.lookup_weather', fail)
    assert client.post('/v1/forecast', json={'latitude': 38.35, 'longitude': 26.65}).status_code == 503
