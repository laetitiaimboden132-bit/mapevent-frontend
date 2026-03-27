"""
Import open-data cities from backend/sources_list.json.

Usage:
- python import_opendatasoft_cities.py --opendatasoft-only
- python import_opendatasoft_cities.py --direct-json-only
- python import_opendatasoft_cities.py  (both modes)
"""

import argparse
import io
import json
import re
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

import requests

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding="utf-8",
        errors="replace",
        line_buffering=True,
    )

API_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
SOURCES_PATH = Path(__file__).resolve().parents[2] / "backend" / "sources_list.json"
TIMEOUT = 60
BATCH_SIZE = 100
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MapEventBot/1.0; +https://mapevent.world)",
    "Accept": "application/json,text/plain,*/*",
}


def decode_events(payload):
    if isinstance(payload, dict) and "k" in payload and "d" in payload:
        keys = payload["k"]
        return [dict(zip(keys, row)) for row in payload["d"]]
    if isinstance(payload, list):
        return payload
    return payload.get("events", [])


def strip_html(text):
    if not text:
        return ""
    txt = re.sub(r"<[^>]+>", " ", str(text))
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt[:1200]


def normalize_date(raw):
    s = str(raw or "").strip()
    if not s:
        return ""
    return s[:10]


def event_key(title, event_date):
    t = re.sub(r"\s+", " ", (title or "").strip().lower())
    return (t, (event_date or "").strip())


def assign_categories(title, description):
    text = f"{title or ''} {description or ''}".lower()
    categories = []
    if any(k in text for k in ["concert", "musique", "music", "jazz", "rock", "dj"]):
        categories.append("Musique > Concert")
    if any(k in text for k in ["theatre", "théâtre", "teatro", "spectacle", "show", "danse"]):
        categories.append("Culture > Spectacle")
    if any(k in text for k in ["expo", "exposition", "museum", "museo", "gallery", "galerie"]):
        categories.append("Culture > Exposition")
    if any(k in text for k in ["cinema", "cine", "film"]):
        categories.append("Culture > Cinéma")
    if "festival" in text:
        categories.append("Festival")
    if not categories:
        categories.append("Culture")
    return list(dict.fromkeys(categories))


def parse_lat_lng(record):
    direct_pairs = [
        ("latitude", "longitude"),
        ("lat", "lon"),
        ("lat", "lng"),
        ("location_latitude", "location_longitude"),
    ]
    for lat_key, lon_key in direct_pairs:
        if lat_key in record and lon_key in record:
            try:
                return float(record[lat_key]), float(record[lon_key])
            except Exception:
                pass

    pt = record.get("geo_point_2d")
    if isinstance(pt, dict) and "lat" in pt and "lon" in pt:
        try:
            return float(pt["lat"]), float(pt["lon"])
        except Exception:
            pass

    loc = record.get("location") or record.get("location_coordinates")
    if isinstance(loc, dict):
        for lk in ("latitude", "lat"):
            for ok in ("longitude", "lon", "lng"):
                if lk in loc and ok in loc:
                    try:
                        return float(loc[lk]), float(loc[ok])
                    except Exception:
                        pass
    if isinstance(loc, str) and "," in loc:
        parts = [x.strip() for x in loc.split(",")]
        if len(parts) >= 2:
            try:
                a = float(parts[0])
                b = float(parts[1])
                if -90 <= a <= 90 and -180 <= b <= 180:
                    return a, b
                if -90 <= b <= 90 and -180 <= a <= 180:
                    return b, a
            except Exception:
                pass

    geom = record.get("geometry")
    if isinstance(geom, dict):
        coords = geom.get("coordinates")
        if isinstance(coords, list) and len(coords) >= 2:
            try:
                lon = float(coords[0])
                lat = float(coords[1])
                return lat, lon
            except Exception:
                pass
    return None, None


def extract_first(record, keys):
    for key in keys:
        val = record.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def extract_title(record):
    return extract_first(
        record,
        [
            "title",
            "title_fr",
            "name",
            "event_name",
            "nom",
            "libelle",
            "summary",
        ],
    )


def extract_description(record):
    val = extract_first(
        record,
        [
            "description",
            "description_fr",
            "longdescription_fr",
            "body",
            "details",
            "resume",
            "summary",
        ],
    )
    return strip_html(val)


def extract_date(record):
    candidates = [
        "dtstart",
        "start_date",
        "firstdate_begin",
        "date_start",
        "date_debut",
        "begin",
        "start",
        "date",
        "event_date",
    ]
    for key in candidates:
        val = normalize_date(record.get(key))
        if val:
            return val
    return ""


def extract_end_date(record):
    for key in ["dtend", "end_date", "firstdate_end", "date_end", "end"]:
        val = normalize_date(record.get(key))
        if val:
            return val
    return None


def extract_location(record):
    location = extract_first(
        record,
        [
            "location",
            "event-location",
            "location_name",
            "place",
            "venue",
            "address",
            "location_address",
            "lieu",
            "adresse",
            "where",
        ],
    )
    city = extract_first(record, ["location_city", "city", "town", "commune"])
    if location and city and city.lower() not in location.lower():
        return f"{location}, {city}"
    return location or city or "Centre-ville"


def extract_source_url(record, fallback):
    url = extract_first(record, ["source_url", "canonicalurl", "url", "link", "web", "ical"])
    if not url:
        uid = extract_first(record, ["uid", "id", "event_id", "slug"])
        if uid:
            return f"{fallback.rstrip('/')}/event/{uid}"
        return fallback
    if url.startswith("http"):
        return url
    return urljoin(fallback.rstrip("/") + "/", url.lstrip("/"))


def fetch_existing_sets():
    r = requests.get(f"{API_URL}/api/events", timeout=120)
    r.raise_for_status()
    events = decode_events(r.json())
    keys = set()
    urls = set()
    for ev in events:
        keys.add(event_key(ev.get("title", ""), ev.get("date", "")))
        src = (ev.get("source_url") or "").strip().lower()
        if src:
            urls.add(src)
    return keys, urls


def import_batches(events):
    imported = 0
    for i in range(0, len(events), BATCH_SIZE):
        batch = events[i : i + BATCH_SIZE]
        resp = requests.post(f"{API_URL}/api/events/scraped/batch", json={"events": batch}, timeout=90)
        if resp.status_code == 200:
            imported += len(batch)
            print(f"    Batch {i // BATCH_SIZE + 1}: {len(batch)} importés (total {imported})")
        else:
            print(f"    Batch {i // BATCH_SIZE + 1}: ERREUR {resp.status_code} {resp.text[:250]}")
        time.sleep(0.2)
    return imported


def parse_records_from_payload(payload):
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    if isinstance(payload.get("results"), list):
        return payload["results"]
    if isinstance(payload.get("records"), list):
        recs = payload["records"]
        # ODS v1 records format: [{"fields": {...}}]
        if recs and isinstance(recs[0], dict) and isinstance(recs[0].get("fields"), dict):
            return [r["fields"] for r in recs if isinstance(r.get("fields"), dict)]
        return recs
    result = payload.get("result")
    if isinstance(result, dict) and isinstance(result.get("records"), list):
        return result["records"]
    return []


def fetch_ods_dataset_records(base, dataset, rows):
    url = f"{base.rstrip('/')}/api/explore/v2.1/catalog/datasets/{dataset}/records"
    out = []
    limit = min(int(rows or 100), 100)
    offset = 0
    while True:
        req_url = f"{url}?limit={limit}&offset={offset}"
        try:
            r = requests.get(req_url, timeout=TIMEOUT)
        except Exception:
            return None if offset == 0 else out
        if r.status_code != 200:
            return None if offset == 0 else out
        chunk = parse_records_from_payload(r.json())
        if not chunk:
            break
        out.extend(chunk)
        offset += len(chunk)
        if len(chunk) < limit or offset >= rows:
            break
    return out


def discover_ods_datasets(base, limit=20):
    url = f"{base.rstrip('/')}/api/explore/v2.1/catalog/datasets"
    candidates = []
    keywords = ("event", "agenda", "evenement", "festival", "culture")
    for offset in (0, 100):
        try:
            req_url = f"{url}?limit=100&offset={offset}&select=dataset_id"
            r = requests.get(req_url, timeout=TIMEOUT)
        except Exception:
            continue
        if r.status_code != 200:
            continue
        results = r.json().get("results", [])
        for row in results:
            ds = (row.get("dataset_id") or "").strip()
            if ds:
                candidates.append(ds)
    candidates = list(dict.fromkeys(candidates))
    candidates = [ds for ds in candidates if any(k in ds.lower() for k in keywords)]
    if limit and len(candidates) > limit:
        candidates = candidates[:limit]
    return candidates


def make_api_events(records, source_name, source_base, existing_keys, existing_urls):
    today = date.today().isoformat()
    out = []
    for rec in records:
        if not isinstance(rec, dict):
            continue
        title = extract_title(rec)
        if not title or len(title) < 3:
            continue
        start_date = extract_date(rec)
        if not start_date or start_date < today:
            continue
        lat, lng = parse_lat_lng(rec)
        if lat is None or lng is None:
            continue
        location = extract_location(rec)
        source_url = extract_source_url(rec, source_base)
        key = event_key(title, start_date)
        if key in existing_keys:
            continue
        if source_url.lower() in existing_urls:
            continue
        description = extract_description(rec)
        api_event = {
            "title": title[:220],
            "description": description,
            "date": start_date,
            "end_date": extract_end_date(rec),
            "time": None,
            "end_time": None,
            "location": location[:300],
            "latitude": lat,
            "longitude": lng,
            "categories": assign_categories(title, description),
            "source_url": source_url,
            "organizer_name": source_name,
            "validation_status": "auto_validated",
        }
        out.append(api_event)
        existing_keys.add(key)
        existing_urls.add(source_url.lower())
    return out


def run_opendatasoft(sources, existing_keys, existing_urls):
    total = 0
    print("\n=== IMPORT OPENDATASOFT ===")
    for src in sources:
        name = src.get("name", "ODS Source")
        base = src.get("base") or src.get("url")
        dataset = src.get("dataset")
        rows = int(src.get("rows") or 500)
        if not base:
            continue
        print(f"\n- {name}")
        records = []
        if dataset:
            fetched = fetch_ods_dataset_records(base, dataset, rows)
            if fetched is not None:
                records = fetched
            else:
                print(f"  Dataset configuré introuvable: {dataset}. Tentative découverte...")
                for cand in discover_ods_datasets(base):
                    fetched = fetch_ods_dataset_records(base, cand, rows)
                    if fetched:
                        print(f"  Dataset trouvé automatiquement: {cand}")
                        records = fetched
                        break

        if not records:
            print("  Aucun enregistrement exploitable.")
            continue

        print(f"  Enregistrements source: {len(records)}")
        api_events = make_api_events(records, name, base, existing_keys, existing_urls)
        print(f"  Nouveaux events valides: {len(api_events)}")
        if api_events:
            total += import_batches(api_events)
    return total


def run_direct_json(sources, existing_keys, existing_urls):
    total = 0
    print("\n=== IMPORT DIRECT JSON (AUTRES VILLES) ===")
    for src in sources:
        name = src.get("name", "Direct JSON Source")
        export_url = src.get("export_url")
        base = src.get("url") or export_url or ""
        if not export_url:
            continue
        print(f"\n- {name}")
        try:
            r = requests.get(export_url, headers=HTTP_HEADERS, timeout=TIMEOUT)
        except Exception as exc:
            print(f"  Erreur réseau: {exc}")
            continue
        if r.status_code != 200:
            print(f"  HTTP {r.status_code}")
            continue
        try:
            payload = r.json()
        except Exception:
            print("  JSON invalide.")
            continue
        records = parse_records_from_payload(payload)
        if not records:
            print("  Pas de records reconnus.")
            continue
        print(f"  Enregistrements source: {len(records)}")
        api_events = make_api_events(records, name, base, existing_keys, existing_urls)
        print(f"  Nouveaux events valides: {len(api_events)}")
        if api_events:
            total += import_batches(api_events)
    return total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--opendatasoft-only", action="store_true")
    parser.add_argument("--direct-json-only", action="store_true")
    args = parser.parse_args()

    if args.opendatasoft_only and args.direct_json_only:
        raise SystemExit("Choisir un seul mode à la fois.")

    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    ods_sources = [s for s in sources if s.get("type") == "opendatasoft"]
    direct_json_sources = [s for s in sources if s.get("type") == "direct_json" and s.get("export_url")]

    # Priorité Europe demandée dans le plan.
    prio_names = [
        "Dortmund Events",
        "Bremen Events",
        "Hannover Events",
        "Groningen Events",
        "Bologna Events",
        "Firenze Events",
        "Zaragoza Events",
        "Santander Events",
        "Palermo Events",
        "Cascais Events",
        "Coimbra Events",
    ]
    direct_json_sources.sort(key=lambda s: (s.get("name") not in prio_names, s.get("name", "")))

    print("=" * 70)
    print("IMPORT OPENDATA CITIES - dedup + import batch")
    print("=" * 70)
    existing_keys, existing_urls = fetch_existing_sets()
    print(f"Base existante: {len(existing_keys)} signatures titre+date, {len(existing_urls)} URLs")

    total_imported = 0
    if not args.direct_json_only:
        total_imported += run_opendatasoft(ods_sources, existing_keys, existing_urls)
    if not args.opendatasoft_only:
        total_imported += run_direct_json(direct_json_sources, existing_keys, existing_urls)

    print("\n" + "=" * 70)
    print(f"Import global terminé. Total importé: {total_imported}")
    print("=" * 70)


if __name__ == "__main__":
    main()
