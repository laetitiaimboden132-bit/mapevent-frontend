"""
Import Barcelona open data events (CC BY 4.0) with deduplication.
"""

import io
import re
import sys
import time
from datetime import date

import requests

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding="utf-8",
        errors="replace",
        line_buffering=True,
    )

API_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
BARCELONA_URL = (
    "https://opendata-ajuntament.barcelona.cat/data/dataset/"
    "a25e60cd-3083-4252-9fce-81f733871cb1/resource/"
    "da9e71de-0f8e-417d-928a-56380bfd0231/download"
)
BATCH_SIZE = 100
TIMEOUT = 180


def decode_events(payload):
    if isinstance(payload, dict) and "k" in payload and "d" in payload:
        keys = payload["k"]
        return [dict(zip(keys, row)) for row in payload["d"]]
    if isinstance(payload, list):
        return payload
    return payload.get("events", [])


def event_key(title, event_date):
    t = re.sub(r"\s+", " ", (title or "").strip().lower())
    d = (event_date or "").strip()
    return (t, d)


def strip_html(text):
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", " ", str(text))
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:1200]


def assign_categories(title, description):
    text = f"{title or ''} {description or ''}".lower()
    categories = []
    if any(k in text for k in ["concert", "música", "musica", "jazz", "rock", "dj"]):
        categories.append("Musique > Concert")
    if any(k in text for k in ["teatre", "teatro", "théâtre", "espectacle", "danza"]):
        categories.append("Culture > Spectacle")
    if any(k in text for k in ["exposició", "exposición", "exposition", "museu", "museo"]):
        categories.append("Culture > Exposition")
    if any(k in text for k in ["cinema", "cine", "film"]):
        categories.append("Culture > Cinéma")
    if "festival" in text:
        categories.append("Festival")
    if not categories:
        categories.append("Culture")
    return list(dict.fromkeys(categories))


def get_first_url_from_values(values):
    if not isinstance(values, list):
        return ""
    for row in values:
        if not isinstance(row, dict):
            continue
        for key in ("url_value", "value", "char_value"):
            url = (row.get(key) or "").strip()
            if isinstance(url, str) and url.startswith("http"):
                return url
    return ""


def build_location(item):
    addresses = item.get("addresses") or []
    if not isinstance(addresses, list) or not addresses:
        return "Barcelona, Spain"
    main = addresses[0]
    if not isinstance(main, dict):
        return "Barcelona, Spain"
    place = (main.get("place") or "").strip()
    roadtype = (main.get("roadtype_name") or "").strip()
    address_name = (main.get("address_name") or "").strip()
    n1 = (str(main.get("street_number_1") or "")).strip()
    zip_code = (str(main.get("zip_code") or "")).strip()
    town = (main.get("town") or "Barcelona").strip()

    street = " ".join(x for x in [roadtype, address_name, n1] if x).strip()
    parts = [x for x in [place, street] if x]
    city_line = " ".join(x for x in [zip_code, town] if x).strip()
    if city_line:
        parts.append(city_line)
    if not parts:
        parts.append("Barcelona, Spain")
    return ", ".join(parts)


def extract_lat_lng(item):
    geo = item.get("geo_epgs_4326_latlon") or {}
    if isinstance(geo, dict):
        lat = geo.get("lat")
        lng = geo.get("lon")
        if lat is not None and lng is not None:
            try:
                return float(lat), float(lng)
            except Exception:
                pass

    addresses = item.get("addresses") or []
    if isinstance(addresses, list):
        for addr in addresses:
            g = (addr or {}).get("location_4326_latlon") or {}
            geometries = g.get("geometries") or []
            if geometries:
                coords = (geometries[0] or {}).get("coordinates") or []
                if len(coords) >= 2:
                    try:
                        return float(coords[1]), float(coords[0])
                    except Exception:
                        continue
    return None, None


def fetch_existing_sets():
    r = requests.get(f"{API_URL}/api/events", timeout=120)
    r.raise_for_status()
    events = decode_events(r.json())
    keys = set()
    urls = set()
    for ev in events:
        keys.add(event_key(ev.get("title", ""), ev.get("date", "")))
        source_url = (ev.get("source_url") or "").strip().lower()
        if source_url:
            urls.add(source_url)
    return keys, urls


def main():
    print("=" * 70)
    print("IMPORT BARCELONA OPENDATA")
    print("=" * 70)
    print("Téléchargement dataset Barcelona (CC BY 4.0)...")
    r = requests.get(BARCELONA_URL, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    print(f"Items reçus: {len(data) if isinstance(data, list) else 0}")

    existing_keys, existing_urls = fetch_existing_sets()
    today = date.today().isoformat()

    to_import = []
    for item in data if isinstance(data, list) else []:
        title = (item.get("name") or item.get("title") or "").strip()
        if not title:
            continue

        start_date = str(item.get("start_date") or "")[:10]
        if not start_date or start_date < today:
            continue

        lat, lng = extract_lat_lng(item)
        if lat is None or lng is None:
            continue

        description = strip_html(item.get("body") or "")
        source_url = get_first_url_from_values(item.get("values")) or (item.get("ical") or "")
        source_url = (source_url or "").strip()
        if not source_url:
            source_url = f"https://www.barcelona.cat/{item.get('register_id', '')}".rstrip("/")

        key = event_key(title, start_date)
        if key in existing_keys:
            continue
        if source_url and source_url.lower() in existing_urls:
            continue

        to_import.append(
            {
                "title": title,
                "description": description,
                "date": start_date,
                "end_date": str(item.get("end_date") or "")[:10] or None,
                "time": None,
                "end_time": None,
                "location": build_location(item),
                "latitude": lat,
                "longitude": lng,
                "categories": assign_categories(title, description),
                "source_url": source_url,
                "organizer_name": (item.get("core_type_name") or "Ajuntament de Barcelona").strip(),
                "validation_status": "auto_validated",
            }
        )
        existing_keys.add(key)
        existing_urls.add(source_url.lower())

    print(f"Events Barcelona à importer: {len(to_import)}")
    if not to_import:
        print("Rien à importer.")
        return

    imported = 0
    for i in range(0, len(to_import), BATCH_SIZE):
        batch = to_import[i : i + BATCH_SIZE]
        resp = requests.post(
            f"{API_URL}/api/events/scraped/batch",
            json={"events": batch},
            timeout=90,
        )
        if resp.status_code == 200:
            imported += len(batch)
            print(f"  Batch {i // BATCH_SIZE + 1}: {len(batch)} importés (total {imported})")
        else:
            print(f"  Batch {i // BATCH_SIZE + 1}: ERREUR {resp.status_code} {resp.text[:250]}")
        time.sleep(0.3)

    print(f"Import terminé. Total importé: {imported}")


if __name__ == "__main__":
    main()
