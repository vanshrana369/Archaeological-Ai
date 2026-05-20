"""
Fetches known archaeological sites from:
  - Pleiades  (bulk JSON download from atlantides.org)
  - OpenContext (paginated REST API)

Output: data/known_sites.json  — list of normalized site dicts:
  {
    "id":           str,
    "name":         str,
    "lat":          float | None,
    "lon":          float | None,
    "country":      str | None,
    "period":       str | None,        # e.g. "archaic, classical, hellenistic-republican"
    "start_year":   int | None,        # earliest known year (negative = BCE)
    "end_year":     int | None,        # latest known year
    "place_type":   str | None,        # e.g. "settlement", "temple", "fort"
    "civilization": str | None,
    "source":       "pleiades" | "opencontext"
  }
"""

import gzip
import io
import json
import os
import time
from pathlib import Path

import requests
from tqdm import tqdm

DATA_DIR = Path(__file__).parent.parent / "data"
OUT_FILE = DATA_DIR / "known_sites.json"

PLEIADES_URL = (
    "https://atlantides.org/downloads/pleiades/json/pleiades-places-latest.json.gz"
)
OPENCONTEXT_URL = "https://opencontext.org/subjects/.json"
OPENCONTEXT_ROWS = 200  # max per page


# ---------------------------------------------------------------------------
# Pleiades
# ---------------------------------------------------------------------------

def fetch_pleiades() -> list[dict]:
    print("Fetching Pleiades bulk download (this may take a minute)...")
    resp = requests.get(PLEIADES_URL, stream=True, timeout=120)
    resp.raise_for_status()

    total = int(resp.headers.get("content-length", 0))
    chunks = []
    with tqdm(total=total, unit="B", unit_scale=True, desc="Downloading") as bar:
        for chunk in resp.iter_content(chunk_size=65536):
            chunks.append(chunk)
            bar.update(len(chunk))

    raw = gzip.decompress(b"".join(chunks))
    data = json.loads(raw)

    # The bulk export wraps everything under "@graph"
    places = data.get("@graph", data) if isinstance(data, dict) else data

    sites = []
    for place in places:
        coords = _pleiades_coords(place)
        start_yr, end_yr = _pleiades_dates(place)
        sites.append(
            {
                "id": f"pleiades:{place.get('id', '')}",
                "name": place.get("title") or place.get("name", ""),
                "lat": coords[0],
                "lon": coords[1],
                "country": None,
                "period": _pleiades_period(place),
                "start_year": start_yr,
                "end_year": end_yr,
                "place_type": ", ".join(place.get("placeTypes", [])) or None,
                "civilization": None,
                "source": "pleiades",
            }
        )

    print(f"  Pleiades: {len(sites):,} sites loaded")
    return sites


def _pleiades_coords(place: dict) -> tuple[float | None, float | None]:
    # Representative point is the most reliable field
    rp = place.get("reprPoint")
    if rp and len(rp) == 2:
        try:
            return float(rp[1]), float(rp[0])  # [lon, lat] → (lat, lon)
        except (TypeError, ValueError):
            pass

    # Fall back to bbox centre
    bbox = place.get("bbox")
    if bbox and len(bbox) == 4:
        try:
            return (bbox[1] + bbox[3]) / 2, (bbox[0] + bbox[2]) / 2
        except (TypeError, ValueError):
            pass

    return None, None


def _pleiades_period(place: dict) -> str | None:
    periods: set[str] = set()
    for loc in place.get("locations", []):
        for att in loc.get("attestations", []):
            tp = att.get("timePeriod")
            if tp:
                periods.add(tp)
    for name in place.get("names", []):
        for att in name.get("attestations", []):
            tp = att.get("timePeriod")
            if tp:
                periods.add(tp)
    return ", ".join(sorted(periods)) if periods else None


def _pleiades_dates(place: dict) -> tuple[int | None, int | None]:
    starts = [loc["start"] for loc in place.get("locations", []) if loc.get("start") is not None]
    ends = [loc["end"] for loc in place.get("locations", []) if loc.get("end") is not None]
    return (min(starts) if starts else None, max(ends) if ends else None)


# ---------------------------------------------------------------------------
# OpenContext
# ---------------------------------------------------------------------------

def fetch_opencontext() -> list[dict]:
    print("Fetching OpenContext sites (paginated)...")
    sites = []
    start = 0

    while True:
        params = {
            "type": "site",
            "rows": OPENCONTEXT_ROWS,
            "start": start,
            "format": "json",
        }
        try:
            resp = requests.get(OPENCONTEXT_URL, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            print(f"  OpenContext request failed at start={start}: {exc}")
            break

        results = data.get("results", [])
        if not results:
            break

        for item in results:
            geo = item.get("geometry", {}) or {}
            coords = geo.get("coordinates")
            lat = lon = None
            if coords and len(coords) == 2:
                try:
                    lon, lat = float(coords[0]), float(coords[1])
                except (TypeError, ValueError):
                    pass

            props = item.get("properties", {}) or {}
            sites.append(
                {
                    "id": f"opencontext:{item.get('uri', str(start + len(sites)))}",
                    "name": props.get("label") or item.get("label", ""),
                    "lat": lat,
                    "lon": lon,
                    "country": props.get("country") or _oc_context(props, "country"),
                    "period": _oc_context(props, "period"),
                    "start_year": None,
                    "end_year": None,
                    "place_type": None,
                    "civilization": _oc_context(props, "culture"),
                    "source": "opencontext",
                }
            )

        total = data.get("numFound", 0)
        start += len(results)
        print(f"  OpenContext: {start}/{total} fetched", end="\r")

        if start >= total:
            break

        time.sleep(0.3)  # be polite to the API

    print(f"\n  OpenContext: {len(sites):,} sites loaded")
    return sites


def _oc_context(props: dict, key: str) -> str | None:
    val = props.get(key)
    if isinstance(val, list):
        return val[0] if val else None
    return val or None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(sources: list[str] | None = None):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sources = sources or ["pleiades", "opencontext"]
    all_sites: list[dict] = []

    if "pleiades" in sources:
        all_sites.extend(fetch_pleiades())

    if "opencontext" in sources:
        all_sites.extend(fetch_opencontext())

    # Deduplicate by id (shouldn't overlap, but defensive)
    seen: set[str] = set()
    deduped = []
    for s in all_sites:
        if s["id"] not in seen:
            seen.add(s["id"])
            deduped.append(s)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(deduped, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(deduped):,} sites -> {OUT_FILE}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch known archaeological sites")
    parser.add_argument(
        "--sources",
        nargs="+",
        choices=["pleiades", "opencontext"],
        default=["pleiades", "opencontext"],
        help="Which sources to fetch (default: both)",
    )
    args = parser.parse_args()
    run(sources=args.sources)
