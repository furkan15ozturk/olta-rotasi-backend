import os
from datetime import datetime
from enum import Enum

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from .catalog import SPECIES

app = FastAPI(title="OltaRotası API", version="0.1.0")
REGIONS = ["izmir", "urla", "foca", "cesme", "seferihisar"]


class Region(str, Enum):
    izmir = "izmir"
    urla = "urla"
    foca = "foca"
    cesme = "cesme"
    seferihisar = "seferihisar"


class SearchRequest(BaseModel):
    species_id: str
    region: Region
    starts_at: datetime
    ends_at: datetime

    @field_validator("species_id")
    @classmethod
    def known_species(cls, value):
        if value not in {s["id"] for s in SPECIES}:
            raise ValueError("Unknown species")
        return value

    @field_validator("starts_at", "ends_at")
    @classmethod
    def timezone_required(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timezone offset is required")
        return value


@app.get("/health")
def health():
    return {"status": "ok", "service": "olta-rotasi", "version": "0.1.0"}


@app.get("/ready")
def ready():
    try:
        with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=3) as conn:
            conn.execute("SELECT PostGIS_Version()").fetchone()
    except (KeyError, psycopg.Error):
        raise HTTPException(503, "Database is not ready") from None
    return {"status": "ok", "habitat_data": "unavailable"}


@app.get("/v1/species")
def species():
    return {"items": SPECIES, "order": "presentation_not_catch_frequency"}


@app.get("/v1/regions")
def regions():
    return {"items": REGIONS, "coverage": "izmir_pilot"}


@app.post("/v1/search")
def search(request: SearchRequest):
    if request.ends_at <= request.starts_at:
        raise HTTPException(422, "ends_at must be after starts_at")
    return {
        "status": "data_unavailable",
        "message": "Pilot bölgenin mera ve çevresel verileri henüz bağlı değil.",
        "query": request.model_dump(mode="json"),
        "items": [],
        "conditions": {
            key: {"status": "unavailable", "value": None}
            for key in ["weather", "wind", "pressure", "pressure_trend", "moon", "sea_temperature", "waves", "currents"]
        },
        "catch_probability": None,
    }


class PointRequest(BaseModel):
    latitude: float
    longitude: float

    @field_validator('latitude')
    @classmethod
    def pilot_latitude(cls, value):
        if not 37.7 <= value <= 39.2:
            raise ValueError('Outside Izmir pilot latitude')
        return value

    @field_validator('longitude')
    @classmethod
    def pilot_longitude(cls, value):
        if not 25.9 <= value <= 27.5:
            raise ValueError('Outside Izmir pilot longitude')
        return value


@app.post('/v1/point')
def point_details(request: PointRequest):
    from .bathymetry import lookup_depth
    from urllib.error import URLError
    try:
        depth = lookup_depth(request.latitude, request.longitude)
    except (URLError, TimeoutError, OSError, ValueError, KeyError):
        raise HTTPException(503, 'Depth source temporarily unavailable') from None
    return {
        'query': request.model_dump(),
        'bathymetry': depth,
        'habitat': {'status': 'unavailable', 'class': None},
        'catch_probability': None,
    }


@app.post('/v1/forecast')
def forecast(request: PointRequest):
    from .weather import lookup_weather
    from urllib.error import URLError
    try:
        result = lookup_weather(request.latitude, request.longitude)
    except (URLError, TimeoutError, OSError, ValueError, KeyError, TypeError):
        raise HTTPException(503, 'Weather source temporarily unavailable') from None
    return {'query': request.model_dump(), 'forecast': result}
