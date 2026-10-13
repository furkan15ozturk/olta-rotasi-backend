"""Seven-day forecast with UTC+3 times, source units and as-retrieved archive."""
import json
import math
import os
import time
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import psycopg
from psycopg.types.json import Jsonb

TR = timezone(timedelta(hours=3))
HOURLY = {
    'temperature_2m': ('temperature_c', '°C'),
    'wind_speed_10m': ('wind_kmh', 'km/h'),
    'wind_gusts_10m': ('gust_kmh', 'km/h'),
    'wind_direction_10m': ('wind_direction_deg', '°'),
    'pressure_msl': ('pressure_hpa', 'hPa'),
    'precipitation_probability': ('rain_probability_percent', '%'),
    'precipitation': ('precipitation_mm', 'mm'),
    'cloud_cover': ('cloud_percent', '%'),
    'weather_code': ('weather_code', 'wmo code'),
}
DAILY = {
    'temperature_2m_max': ('temperature_max_c', '°C'),
    'temperature_2m_min': ('temperature_min_c', '°C'),
    'wind_speed_10m_max': ('wind_max_kmh', 'km/h'),
    'precipitation_probability_max': ('rain_probability_max_percent', '%'),
    'weather_code': ('weather_code', 'wmo code'),
}


def numeric(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) else None


def normalize(raw, now):
    if raw.get('utc_offset_seconds') != 10800:
        raise ValueError('Unexpected timezone offset')
    for section, fields in [('hourly', HOURLY), ('daily', DAILY)]:
        times = raw[section]['time']
        if not times or times != sorted(set(times)):
            raise ValueError('Missing or unordered forecast times')
        for source, (_, unit) in fields.items():
            if raw[section + '_units'].get(source) != unit or len(raw[section][source]) != len(times):
                raise ValueError('Unexpected units or series length')
    start = now.astimezone(TR).date()
    wanted_dates = [(start + timedelta(days=i)).isoformat() for i in range(7)]
    hourly = raw['hourly']
    times = [datetime.fromisoformat(t).replace(tzinfo=TR) for t in hourly['time']]
    pressures = {t: numeric(hourly['pressure_msl'][i]) for i, t in enumerate(times)}
    hours = []
    for i, stamp in enumerate(times):
        if stamp < now or stamp.date().isoformat() not in wanted_dates:
            continue
        row = {'time': stamp.isoformat()}
        row.update({target: numeric(hourly[source][i]) for source, (target, _) in HOURLY.items()})
        prev = pressures.get(stamp - timedelta(hours=3))
        current = row['pressure_hpa']
        row['pressure_change_3h_hpa'] = round(current - prev, 1) if prev is not None and current is not None else None
        hours.append(row)
    days = []
    for i, date in enumerate(raw['daily']['time']):
        if date not in wanted_dates:
            continue
        row = {'date': date, 'hours': [h for h in hours if h['time'][:10] == date]}
        row.update({target: numeric(raw['daily'][source][i]) for source, (target, _) in DAILY.items()})
        days.append(row)
    if [d['date'] for d in days] != wanted_dates:
        raise ValueError('Seven local days required')
    return {
        'status': 'available', 'timezone': 'Europe/Istanbul', 'days': days,
        'model_grid': {'latitude': raw.get('latitude'), 'longitude': raw.get('longitude')},
        'source': 'Open-Meteo', 'source_url': 'https://open-meteo.com/',
        'license': 'CC BY 4.0', 'forecast_retrieved_at': now.astimezone(timezone.utc).isoformat(),
        'model_run_at': None,
        'catch_probability': None,
    }


def archive_forecast(latitude, longitude, retrieved_at, raw, provider='open-meteo'):
    try:
        with psycopg.connect(os.environ['DATABASE_URL'], connect_timeout=3) as connection:
            connection.execute('''CREATE TABLE IF NOT EXISTS forecast_snapshots (
                id bigserial PRIMARY KEY, latitude double precision NOT NULL,
                longitude double precision NOT NULL, retrieved_at timestamptz NOT NULL,
                provider text NOT NULL, payload jsonb NOT NULL)''')
            connection.execute('INSERT INTO forecast_snapshots(latitude, longitude, retrieved_at, provider, payload) VALUES (%s,%s,%s,%s,%s)',
                               (latitude, longitude, retrieved_at, provider, Jsonb(raw)))
        return 'stored'
    except (KeyError, psycopg.Error):
        return 'unavailable'


@lru_cache(maxsize=128)
def _fetch(latitude, longitude, bucket):
    params = {
        'latitude': latitude, 'longitude': longitude,
        'timezone': 'Europe/Istanbul', 'forecast_days': 7, 'past_days': 1,
        'hourly': ','.join(HOURLY), 'daily': ','.join(DAILY),
        'wind_speed_unit': 'kmh', 'cell_selection': 'nearest',
    }
    key = os.environ.get('OPEN_METEO_API_KEY')
    host = 'https://customer-api.open-meteo.com' if key else 'https://api.open-meteo.com'
    if key:
        params['apikey'] = key
    request = Request(host + '/v1/forecast?' + urlencode(params), headers={'User-Agent': 'OltaRotasi/0.1'})
    with urlopen(request, timeout=12) as response:
        raw = json.loads(response.read(500000))
    fetched = datetime.now(timezone.utc)
    # Check the contract before persisting a valid snapshot.
    normalize(raw, fetched)
    archive_status = archive_forecast(latitude, longitude, fetched, raw)
    return raw, fetched, archive_status


def lookup_weather(latitude, longitude):
    raw, fetched, archived = _fetch(latitude, longitude, int(time.time() // 900))
    result = normalize(raw, datetime.now(timezone.utc))
    result['forecast_retrieved_at'] = fetched.isoformat()
    result['archive_status'] = archived
    return result
