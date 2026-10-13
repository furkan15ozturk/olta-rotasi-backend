"""EMODnet nearest-grid lookup; elevation is LAT-referenced, not live depth."""
import csv
import io
import math
from datetime import datetime, timezone
from urllib.parse import quote
from urllib.request import Request, urlopen

BASE = 'https://erddap.emodnet.eu/erddap/griddap/bathymetry_dtm_2024.csv?'


def parse_sample(text):
    rows = list(csv.DictReader(io.StringIO(text)))
    if len(rows) != 2:
        raise ValueError('Expected units plus one grid sample')
    sample = rows[1]
    elevation = float(sample['elevation'])
    if not math.isfinite(elevation):
        return {'status': 'no_data', 'depth_m': None}
    flag = float(sample['interpolation_flag'])
    return {
        'status': 'sea' if elevation < 0 else 'non_negative_elevation',
        'depth_m': round(-elevation, 1) if elevation < 0 else None,
        'elevation_m': elevation,
        'sample_latitude': float(sample['latitude']),
        'sample_longitude': float(sample['longitude']),
        'interpolated': bool(flag) if flag in (0, 1) else None,
    }


def lookup_depth(latitude, longitude):
    dims = f'[({latitude})][({longitude})]'
    url = BASE + quote('elevation' + dims + ',interpolation_flag' + dims, safe='(),:')
    request = Request(url, headers={'User-Agent': 'OltaRotasi/0.1 (https://github.com/furkan15ozturk/olta-rotasi-backend)'})
    with urlopen(request, timeout=12) as response:
        result = parse_sample(response.read(20000).decode('utf-8'))
    return result | {
        'source': 'EMODnet Bathymetry DTM 2024',
        'source_url': 'https://emodnet.ec.europa.eu/en/bathymetry',
        'grid_spacing_degrees': 1 / 960,
        'vertical_reference': 'Lowest Astronomical Tide',
        'retrieved_at': datetime.now(timezone.utc).isoformat(),
    }
