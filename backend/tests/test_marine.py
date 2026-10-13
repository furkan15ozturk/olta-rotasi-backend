from datetime import datetime, timedelta
from app.marine import astronomy_for_day, normalize_marine, FIELDS
from app.weather import TR
import astronomy
import pytest


def test_astronomy_quarter_and_local_event_dates():
    # Independent definition: phase angle at computed exact quarter is 90 degrees.
    event = astronomy.SearchMoonPhase(90, astronomy.Time.Parse('2026-10-01T00:00:00Z'), 35)
    assert abs(astronomy.MoonPhase(event) - 90) < 0.001
    row = astronomy_for_day('2026-10-13', 38.35, 26.65)
    assert 0 <= row['illumination_percent'] <= 100
    for key in ['moonrise', 'moonset', 'sunrise', 'sunset']:
        if row[key] is not None:
            assert row[key].startswith('2026-10-13T')
            assert row[key].endswith('+03:00')
    assert datetime.fromisoformat(row['sunrise']) < datetime.fromisoformat(row['sunset'])


def fixture():
    start = datetime(2026, 10, 13, tzinfo=TR)
    return {'utc_offset_seconds': 10800, 'latitude': 38.2, 'longitude': 26.6,
            'hourly': {'time': [(start+timedelta(hours=i)).strftime('%Y-%m-%dT%H:%M') for i in range(168)], **{key: [None]*168 for key in FIELDS}},
            'hourly_units': {key: unit for key, (_, unit) in FIELDS.items()}}


def test_seven_days_missing_sea_data_and_grid_distance():
    result = normalize_marine(fixture(), datetime(2026, 10, 13, 13, 30, tzinfo=TR), 38.35, 26.65)
    assert len(result['days']) == 7
    assert result['days'][0]['hours'][0]['time'] == '2026-10-13T14:00:00+03:00'
    assert result['days'][0]['hours'][0]['wave_height_m'] is None
    assert result['model_grid']['distance_km'] > 10
    assert result['catch_probability'] is None


def test_velocity_units_cannot_be_mixed():
    raw = fixture()
    raw['hourly_units']['ocean_current_velocity'] = 'm/s'
    with pytest.raises(ValueError):
        normalize_marine(raw, datetime(2026, 10, 13, tzinfo=TR), 38.35, 26.65)


def test_marine_endpoint_source_failure_and_unknown_habitat(monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    def fail(*args):
        raise TimeoutError()
    monkeypatch.setattr('app.marine.lookup_marine', fail)
    assert client.post('/v1/marine', json={'latitude': 38.35, 'longitude': 26.65}).status_code == 503
    assert client.post('/v1/marine', json={'latitude': 26.65, 'longitude': 38.35}).status_code == 422
