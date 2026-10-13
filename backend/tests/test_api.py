from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
QUERY = dict(species_id="sea_bass", region="urla", starts_at="2026-10-15T05:00:00+03:00", ends_at="2026-10-15T10:00:00+03:00")


def test_search_does_not_invent_data():
    response = client.post('/v1/search', json=QUERY)
    assert response.status_code == 200
    body = response.json()
    assert body['status'] == 'data_unavailable'
    assert body['items'] == []
    assert body['catch_probability'] is None
    assert body['conditions']['pressure']['value'] is None


def test_bad_species_and_region_rejected():
    for update in [dict(species_id='unknown'), dict(region='istanbul')]:
        assert client.post('/v1/search', json=QUERY | update).status_code == 422


def test_timezone_and_time_order_required():
    for update in [dict(starts_at='2026-10-15T05:00:00'), dict(ends_at=QUERY['starts_at'])]:
        assert client.post('/v1/search', json=QUERY | update).status_code == 422


def test_species_and_readiness(monkeypatch):
    assert len(client.get('/v1/species').json()['items']) == 8
    monkeypatch.delenv('DATABASE_URL', raising=False)
    assert client.get('/ready').status_code == 503
    assert client.get('/health').status_code == 200
