"""FRED API client + percentile — stdlib only."""
import json, urllib.request, urllib.parse

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"

def fetch_series(series_id, api_key, limit=800, timeout=20):
    """Return list of (date, float) descending by date. Skips '.' missing values."""
    qs = urllib.parse.urlencode({
        "series_id": series_id, "api_key": api_key, "file_type": "json",
        "sort_order": "desc", "limit": limit,
    })
    with urllib.request.urlopen(f"{FRED_URL}?{qs}", timeout=timeout) as r:
        data = json.load(r)
    out = []
    for o in data.get("observations", []):
        v = o.get("value")
        if v in (".", "", None): continue
        try: out.append((o["date"], float(v)))
        except ValueError: pass
    return out

def percentile_high(series, window=756):
    """Rank latest value vs trailing window. High value -> high percentile."""
    if not series: return None, None
    vals = [v for _, v in series[:window]]
    latest = vals[0]
    rank = sum(1 for v in vals if v <= latest) / len(vals) * 100
    return latest, round(rank, 1)

def spread_percentile(hy_series, ig_series, window=756):
    """Percentile of (hy - ig) spread. Aligns by date."""
    if not hy_series or not ig_series: return None, None
    ig_map = dict(ig_series)
    spread = [(d, hy - ig_map[d]) for d, hy in hy_series if d in ig_map]
    return percentile_high(spread, window)
