"""Regional marine grid and calculated astronomy; never a catch probability."""
import json
import os
import time
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from math import radians, sin, cos, asin, sqrt
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import astronomy
from .weather import TR, numeric, archive_forecast

FIELDS = {
    'wave_height': ('wave_height_m', 'm'),
    'wave_period': ('wave_period_s', 's'),
    'wave_direction': ('wave_from_deg', '°'),
    'sea_surface_temperature': ('sea_temperature_c', '°C'),
    'ocean_current_velocity': ('current_kmh', 'km/h'),
    'ocean_current_direction': ('current_to_deg', '°'),
}


def distance_km(lat1, lon1, lat2, lon2):
    a, b = radians(lat1), radians(lat2)
    h = sin((b-a)/2)**2 + cos(a)*cos(b)*sin(radians(lon2-lon1)/2)**2
    return round(6371 * 2 * asin(sqrt(min(1, h))), 1)


def astronomy_for_day(date, latitude, longitude):
    start = datetime.fromisoformat(date).replace(tzinfo=TR)
    noon = start + timedelta(hours=12)
    astro_start = astronomy.Time.Parse(start.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))
    astro_noon = astronomy.Time.Parse(noon.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))
    observer = astronomy.Observer(latitude, longitude, 0)
    def event(body, direction):
        found = astronomy.SearchRiseSet(body, observer, direction, astro_start, 1)
        if found is None:
            return None
        stamp = found.Utc().replace(tzinfo=timezone.utc).astimezone(TR)
        return stamp.isoformat() if start <= stamp < start + timedelta(days=1) else None
    return {
        'phase_degrees': round(astronomy.MoonPhase(astro_noon), 2),
        'illumination_percent': round(100 * astronomy.Illumination(astronomy.Body.Moon, astro_noon).phase_fraction, 1),
        'phase_at': noon.isoformat(),
        'moonrise': event(astronomy.Body.Moon, astronomy.Direction.Rise),
        'moonset': event(astronomy.Body.Moon, astronomy.Direction.Set),
        'sunrise': event(astronomy.Body.Sun, astronomy.Direction.Rise),
        'sunset': event(astronomy.Body.Sun, astronomy.Direction.Set),
        'source': 'Astronomy Engine 2.1.19',
    }


def normalize_marine(raw, now, latitude, longitude):
    if raw.get('utc_offset_seconds') != 10800:
        raise ValueError('Unexpected marine timezone')
    timestamps = raw['hourly']['time']
    if not timestamps or timestamps != sorted(set(timestamps)):
        raise ValueError('Invalid marine times')
    for source, (_, unit) in FIELDS.items():
        if raw['hourly_units'].get(source) != unit or len(raw['hourly'][source]) != len(timestamps):
            raise ValueError('Invalid marine units or series')
    start = now.astimezone(TR).date()
    days = []
    for offset in range(7):
        date = (start + timedelta(days=offset)).isoformat()
        rows = []
        for i, value in enumerate(timestamps):
            stamp = datetime.fromisoformat(value).replace(tzinfo=TR)
            if stamp < now or stamp.date().isoformat() != date:
                continue
            rows.append({'time': stamp.isoformat(), **{
                target: numeric(raw['hourly'][source][i]) for source, (target, _) in FIELDS.items()
            }})
        days.append({'date': date, 'hours': rows, 'astronomy': astronomy_for_day(date, latitude, longitude)})
    return {
        'status': 'available', 'timezone': 'Europe/Istanbul', 'days': days,
        'model_grid': {'latitude': raw['latitude'], 'longitude': raw['longitude'],
                       'distance_km': distance_km(latitude, longitude, raw['latitude'], raw['longitude'])},
        'source': 'Open-Meteo Marine · DWD / Météo-France / Copernicus Marine',
        'source_url': 'https://open-meteo.com/en/docs/marine-weather-api',
        'license': 'CC BY 4.0', 'model_run_at': None,
        'catch_probability': None,
    }


@lru_cache(maxsize=128)
def _fetch_marine(latitude, longitude, bucket):
    params = {'latitude': latitude, 'longitude': longitude, 'timezone': 'Europe/Istanbul',
              'forecast_days': 7, 'hourly': ','.join(FIELDS), 'cell_selection': 'sea'}
    key = os.environ.get('OPEN_METEO_API_KEY')
    host = 'https://customer-marine-api.open-meteo.com' if key else 'https://marine-api.open-meteo.com'
    if key:
        params['apikey'] = key
    with urlopen(Request(host + '/v1/marine?' + urlencode(params), headers={'User-Agent': 'OltaRotasi/0.1'}), timeout=12) as response:
        raw = json.loads(response.read(500000))
    fetched = datetime.now(timezone.utc)
    normalize_marine(raw, fetched, latitude, longitude)
    archived = archive_forecast(latitude, longitude, fetched, raw, provider='open-meteo-marine')
    return raw, fetched, archived


def lookup_marine(latitude, longitude):
    raw, fetched, archived = _fetch_marine(latitude, longitude, int(time.time() // 900))
    return normalize_marine(raw, datetime.now(timezone.utc), latitude, longitude) | {
        'forecast_retrieved_at': fetched.isoformat(), 'archive_status': archived,
    }
