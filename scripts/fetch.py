"""Fetch raw weather data for every group/spot into one JSON file. No AI, no judgement.

Usage: python3 scripts/fetch.py [--out raw/] [--now 2026-11-02T12:00:00Z]

Reads spots/<group>/_group.md and spots/<group>/<spot>.md front matter, then downloads:
NWS forecast discussion, NWS gridpoint forecast at each launch, winds aloft (Open-Meteo GFS
pressure levels), TAFs, METAR pressure, station observations. Writes raw/<run-id>.json and prints its path.

Everything is converted to knots. Every request is recorded in `sources` with ok/error,
so a failed fetch is visible in the report instead of silently missing.
"""
import argparse
import datetime as dt
import json
import math
import os
import re
import sys
import urllib.request
from zoneinfo import ZoneInfo

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "huginn/0.1 (https://github.com/bgrozev/huginn)"
KMH_TO_KT = 1 / 1.852
# Daylight-ish hours kept from the hourly grid forecast (local time).
HOUR_FROM, HOUR_TO = 5, 21
# Pressure levels for winds aloft (Open-Meteo, GFS): ~5,000 / ~10,000 / ~14,000 ft MSL.
ALOFT_LEVELS_HPA = (850, 700, 600)
GRID_FIELDS = {
    # NWS grid name -> (output key, converter)
    "windDirection": ("dir_deg", lambda v: round(v)),
    "windSpeed": ("speed_kt", lambda v: round(v * KMH_TO_KT)),
    "windGust": ("gust_kt", lambda v: round(v * KMH_TO_KT)),
    "probabilityOfPrecipitation": ("precip_pct", round),
    "probabilityOfThunder": ("thunder_pct", round),
    "skyCover": ("sky_pct", round),
    "mixingHeight": ("mixing_height_ft", lambda v: round(v * 3.28084)),
    "transportWindDirection": ("transport_dir_deg", round),
    "transportWindSpeed": ("transport_kt", lambda v: round(v * KMH_TO_KT)),
}


class Fetcher:
    def __init__(self):
        self.sources = []

    def get(self, label, url, kind="json"):
        """GET a URL; record it in sources. Returns parsed body or None on failure."""
        rec = {"label": label, "url": url, "fetched_at": iso(now_utc()), "ok": False}
        self.sources.append(rec)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/geo+json,application/json,text/plain"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
            rec["ok"] = True
            return json.loads(body) if kind == "json" else body
        except Exception as e:  # noqa: BLE001 — any failure is recorded, not fatal
            rec["error"] = f"{type(e).__name__}: {e}"[:200]
            print(f"WARN {label}: {rec['error']}", file=sys.stderr)
            return None


_NOW = None


def now_utc():
    return _NOW or dt.datetime.now(dt.timezone.utc)


def iso(t):
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_front_matter(path):
    with open(path) as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise ValueError(f"{path}: no front matter")
    return yaml.safe_load(m.group(1))


# ---------- time slots & sun ----------

def sun_times(date, lat, lon, tz):
    """Sunrise/sunset (NOAA approximation, ±2 min) as local datetimes."""
    n = date.timetuple().tm_yday
    gamma = 2 * math.pi / 365 * (n - 1)
    eqtime = 229.18 * (0.000075 + 0.001868 * math.cos(gamma) - 0.032077 * math.sin(gamma)
                       - 0.014615 * math.cos(2 * gamma) - 0.040849 * math.sin(2 * gamma))
    decl = (0.006918 - 0.399912 * math.cos(gamma) + 0.070257 * math.sin(gamma) - 0.006758 * math.cos(2 * gamma)
            + 0.000907 * math.sin(2 * gamma) - 0.002697 * math.cos(3 * gamma) + 0.00148 * math.sin(3 * gamma))
    ha = math.degrees(math.acos(math.cos(math.radians(90.833)) / (math.cos(math.radians(lat)) * math.cos(decl))
                                - math.tan(math.radians(lat)) * math.tan(decl)))
    midnight = dt.datetime(date.year, date.month, date.day, tzinfo=dt.timezone.utc)
    rise = midnight + dt.timedelta(minutes=720 - 4 * (lon + ha) - eqtime)
    sset = midnight + dt.timedelta(minutes=720 - 4 * (lon - ha) - eqtime)
    return rise.astimezone(tz), sset.astimezone(tz)


def make_slots(now, tz, lat, lon):
    """Six AM/PM slots starting with the first one that isn't over.
    AM = sunrise–12:00, PM = 12:00–sunset (local)."""
    local_now = now.astimezone(tz)
    slots, day, d_index = [], local_now.date(), 1
    while len(slots) < 6:
        rise, sset = sun_times(day, lat, lon, tz)
        noon = dt.datetime(day.year, day.month, day.day, 12, tzinfo=tz)
        for part, start, end in (("am", rise, noon), ("pm", noon, sset)):
            if end <= local_now or len(slots) == 6:
                continue
            slots.append({
                "id": f"d{d_index}-{part}", "date": day.isoformat(), "part": part,
                "label": f"{day.strftime('%a')} {part.upper()}",
                "basis": "forecast", "starts_at": iso(start), "ends_at": iso(end),
            })
        day += dt.timedelta(days=1)
        d_index += 1
    slots[0]["basis"] = "forecast+obs"
    return slots


# ---------- NWS gridpoint ----------

def parse_valid_time(s):
    """'2026-11-02T12:00:00+00:00/PT3H' -> (start, hours)."""
    start, dur = s.split("/")
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?", dur)
    hours = int(m.group(1) or 0) * 24 + int(m.group(2) or 0)
    return dt.datetime.fromisoformat(start), max(hours, 1)


def grid_hourly(grid, tz, first_day, last_day):
    """Expand NWS grid series to hourly rows (local HOUR_FROM..HOUR_TO, first_day..last_day)."""
    rows = {}
    props = grid["properties"]
    for name, (key, conv) in GRID_FIELDS.items():
        for v in (props.get(name) or {}).get("values", []):
            if v["value"] is None:
                continue
            start, hours = parse_valid_time(v["validTime"])
            for h in range(hours):
                t = (start + dt.timedelta(hours=h)).astimezone(tz)
                if not (first_day <= t.date() <= last_day and HOUR_FROM <= t.hour <= HOUR_TO):
                    continue
                rows.setdefault(t, {"time": t.isoformat()})[key] = conv(v["value"])
    return [rows[t] for t in sorted(rows)]


# ---------- winds aloft (Open-Meteo pressure levels) ----------

def aloft_url(lat, lon, tz_name):
    fields = []
    for p in ALOFT_LEVELS_HPA:
        fields += [f"wind_speed_{p}hPa", f"wind_direction_{p}hPa", f"geopotential_height_{p}hPa"]
    return (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            f"&hourly={','.join(fields)}&wind_speed_unit=kn&timezone={tz_name.replace('/', '%2F')}"
            f"&forecast_days=5&models=gfs_seamless")


def aloft_hourly(data, tz, first_day, last_day):
    """Hourly rows {time, levels: {'700mb': {alt_ft, dir_deg, speed_kt}}} within the slot days."""
    h = data["hourly"]
    rows = []
    for i, t in enumerate(h["time"]):
        lt = dt.datetime.fromisoformat(t).replace(tzinfo=tz)
        if not (first_day <= lt.date() <= last_day and HOUR_FROM <= lt.hour <= HOUR_TO):
            continue
        levels = {}
        for p in ALOFT_LEVELS_HPA:
            sp, d, z = (h.get(f"{k}_{p}hPa", [None] * len(h["time"]))[i]
                        for k in ("wind_speed", "wind_direction", "geopotential_height"))
            if sp is None:
                continue
            levels[f"{p}mb"] = {"alt_ft": None if z is None else int(round(z * 3.28084, -2)),
                                "dir_deg": None if d is None else round(d), "speed_kt": round(sp)}
        rows.append({"time": lt.isoformat(), "levels": levels})
    return rows


# ---------- observations ----------

def slim_obs(features, limit=6):
    out = []
    for f in features[:limit]:
        p = f["properties"]
        kt = lambda q: None if (p.get(q) or {}).get("value") is None else round(p[q]["value"] * KMH_TO_KT)
        out.append({
            "time": p.get("timestamp"),
            "dir_deg": None if p["windDirection"]["value"] is None else round(p["windDirection"]["value"]),
            "speed_kt": kt("windSpeed"),
            "gust_kt": kt("windGust"),
            "slp_mb": None if (p.get("seaLevelPressure") or {}).get("value") is None
            else round(p["seaLevelPressure"]["value"] / 100, 1),
            "text": p.get("textDescription"),
        })
    return out


# ---------- main ----------

def fetch_group(fx, group_dir, now):
    g = read_front_matter(os.path.join(group_dir, "_group.md"))
    tz = ZoneInfo(g["timezone"])
    c = g["centroid"]
    slots = make_slots(now, tz, c["lat"], c["lon"])
    first_day = dt.date.fromisoformat(slots[0]["date"])
    last_day = dt.date.fromisoformat(slots[-1]["date"])
    out = {"id": g["id"], "name": g["name"], "timezone": g["timezone"], "slots": slots}

    out["sun"] = []
    d = first_day
    while d <= last_day:
        rise, sset = sun_times(d, c["lat"], c["lon"], tz)
        out["sun"].append({"date": d.isoformat(), "sunrise": rise.strftime("%H:%M"), "sunset": sset.strftime("%H:%M")})
        d += dt.timedelta(days=1)

    # Forecast discussion
    wfo = g["wfo"]
    lst = fx.get(f"NWS forecast discussion list ({wfo})", f"https://api.weather.gov/products/types/AFD/locations/{wfo}")
    out["afd"] = None
    if lst and lst.get("@graph"):
        pid = lst["@graph"][0]["id"]
        prod = fx.get(f"NWS forecast discussion ({wfo})", f"https://api.weather.gov/products/{pid}")
        if prod:
            out["afd"] = {"issued": prod.get("issuanceTime"), "text": prod.get("productText"),
                          "page": g.get("afd_url")}

    # Winds aloft (the aviationweather.gov FD tables were discontinued with the NAM in 2026)
    data = fx.get("Winds aloft forecast (Open-Meteo GFS)", aloft_url(c["lat"], c["lon"], g["timezone"]))
    out["winds_aloft"] = {"model": "GFS via Open-Meteo", "hourly": aloft_hourly(data, tz, first_day, last_day) if data else []}

    # TAFs
    ids = ",".join(g["taf_airports"])
    tafs = fx.get(f"Airport forecasts ({ids})", f"https://aviationweather.gov/api/data/taf?ids={ids}&format=json")
    out["tafs"] = []
    for t in tafs or []:
        out["tafs"].append({
            "station": t.get("icaoId"), "raw": t.get("rawTAF"),
            "periods": [{
                "from": iso(dt.datetime.fromtimestamp(p["timeFrom"], dt.timezone.utc)),
                "to": iso(dt.datetime.fromtimestamp(p["timeTo"], dt.timezone.utc)),
                "change": p.get("fcstChange"), "probability": p.get("probability"),
                "dir_deg": p.get("wdir") if isinstance(p.get("wdir"), int) else None,
                "speed_kt": p.get("wspd"), "gust_kt": p.get("wgst"), "weather": p.get("wxString"),
            } for p in t.get("fcsts", [])],
        })

    # Pressure trend from METARs (NWS station obs often lack sea-level pressure)
    ref = g.get("pressure_reference")
    out["pressure"] = None
    if ref:
        metars = fx.get(f"Airport observations ({ref}, 24 h)",
                        f"https://aviationweather.gov/api/data/metar?ids={ref}&format=json&hours=24")
        series = [{"time": iso(dt.datetime.fromtimestamp(m["obsTime"], dt.timezone.utc)),
                   "slp_mb": m.get("slp"), "altim_mb": m.get("altim")} for m in (metars or [])]
        out["pressure"] = {"station": ref, "series": series[:24]}

    # Observations
    out["observations"] = []
    for st in g.get("observation_stations", []):
        data = fx.get(f"Observations — {st['name']} ({st['id']})",
                      f"https://api.weather.gov/stations/{st['id']}/observations?limit=6")
        obs = slim_obs(data.get("features", [])) if data else []
        out["observations"].append({"id": st["id"], "name": st["name"], "chart_url": st.get("url"), "obs": obs})

    # Spots: hourly gridpoint forecast at each launch
    out["spots"] = []
    for sid in g["spots"]:
        s = read_front_matter(os.path.join(group_dir, f"{sid}.md"))
        la = s["launch"]
        pts = fx.get(f"NWS grid lookup — {s['name']}", f"https://api.weather.gov/points/{la['lat']},{la['lon']}")
        hourly, grid_url = [], None
        if pts:
            grid_url = pts["properties"]["forecastGridData"]
            grid = fx.get(f"NWS hourly forecast — {s['name']} launch", grid_url)
            if grid:
                hourly = grid_hourly(grid, tz, first_day, last_day)
        out["spots"].append({"id": sid, "name": s["name"], "meta": s, "grid_url": grid_url, "hourly": hourly})
    return out


def main():
    global _NOW
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "raw"))
    ap.add_argument("--now", help="override current time (UTC ISO), for testing")
    args = ap.parse_args()
    if args.now:
        _NOW = dt.datetime.fromisoformat(args.now.replace("Z", "+00:00"))
    now = now_utc()
    run_id = now.strftime("%Y-%m-%dT%H%MZ")

    fx = Fetcher()
    groups = []
    spots_root = os.path.join(ROOT, "spots")
    for name in sorted(os.listdir(spots_root)):
        gdir = os.path.join(spots_root, name)
        if os.path.isfile(os.path.join(gdir, "_group.md")):
            groups.append(fetch_group(fx, gdir, now))

    raw = {"run_id": run_id, "generated_at": iso(now), "activity": "speedflying", "groups": groups, "sources": fx.sources}
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, f"{run_id}.json")
    with open(path, "w") as f:
        json.dump(raw, f, indent=1, ensure_ascii=False)
    failed = [s["label"] for s in fx.sources if not s["ok"]]
    print(path)
    print(f"{len(fx.sources)} fetches, {len(failed)} failed{': ' + ', '.join(failed) if failed else ''}", file=sys.stderr)
    # Without the forecast discussion or any spot forecast there is nothing to assess.
    if any(g["afd"] is None or not any(s["hourly"] for s in g["spots"]) for g in groups):
        sys.exit(2)


if __name__ == "__main__":
    main()
