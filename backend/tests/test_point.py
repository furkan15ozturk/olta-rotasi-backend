from fastapi.testclient import TestClient
from app.main import app
from app.bathymetry import parse_sample

client = TestClient(app)


def test_depth_and_missing_data_are_distinct():
    def sample(value, flag='1'):
        return f'latitude,longitude,elevation,interpolation_flag\ndegrees_north,degrees_east,m,\n38.35,26.65,{value},{flag}\n'
    assert parse_sample(sample('-22.94'))['depth_m'] == 22.9
    assert parse_sample(sample('-22.94'))['interpolated'] is True
    assert parse_sample(sample('NaN'))['status'] == 'no_data'
    assert parse_sample(sample('5'))['depth_m'] is None
    assert parse_sample(sample('-4', 'NaN'))['interpolated'] is None


def test_coordinates_and_unavailable_source(monkeypatch):
    for query in [{'latitude': 26.6, 'longitude': 38.3}, {'latitude': 90, 'longitude': 26.6}]:
        assert client.post('/v1/point', json=query).status_code == 422
    def fail(*args):
        raise TimeoutError()
    monkeypatch.setattr('app.bathymetry.lookup_depth', fail)
    assert client.post('/v1/point', json={'latitude': 38.35, 'longitude': 26.65}).status_code == 503


def test_real_point_contract_keeps_unknown_habitat(monkeypatch):
    monkeypatch.setattr('app.bathymetry.lookup_depth', lambda *args: {'status': 'sea', 'depth_m': 12.3, 'interpolated': True})
    body = client.post('/v1/point', json={'latitude': 38.35, 'longitude': 26.65}).json()
    assert body['query']['longitude'] == 26.65
    assert body['bathymetry']['depth_m'] == 12.3
    assert body['habitat']['class'] is None
    assert body['catch_probability'] is None
