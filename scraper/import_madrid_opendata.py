"""
Fix Madrid coordinates by replacing old madrid.es imports with official open data.

Plan step:
1) Delete existing madrid.es events (bad fallback coordinates).
2) Re-import from official datos.madrid.es dataset with real coordinates.
"""

import io
import re
import sys
import time
from datetime import date
from urllib.parse import urlparse

import requests

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding="utf-8",
        errors="replace",
        line_buffering=True,
    )

API_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
MADRID_DATASET_URL = "https://datos.madrid.es/egob/catalogo/300107-0-agenda-actividades-eventos.json"
BAD_DOMAINS = {"madrid.es", "www.madrid.es"}
BATCH_SIZE = 100
TIMEOUT = 120


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
    cleaned = re.sub(r"<[^>]+>", " ", str(text))
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:1200]


def extract_domain(url):
    if not url:
        return ""
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def event_key(title, event_date):
    t = re.sub(r"\s+", " ", (title or "").strip().lower())
    d = (event_date or "").strip()
    return (t, d)


def assign_categories(title, description):
    text = f"{title or ''} {description or ''}".lower()
    categories = []
    if any(k in text for k in ["concert", "musique", "jazz", "rock", "electro", "orquesta"]):
        categories.append("Musique > Concert")
    if any(k in text for k in ["teatro", "théâtre", "spectacle", "danza", "danse"]):
        categories.append("Culture > Spectacle")
    if any(k in text for k in ["exposición", "exposition", "museum", "museo"]):
        categories.append("Culture > Exposition")
    if any(k in text for k in ["cine", "cinema", "film", "película"]):
        categories.append("Culture > Cinéma")
    if "festival" in text:
        categories.append("Festival")
    if not categories:
        categories.append("Culture")
    return list(dict.fromkeys(categories))


def build_location(event):
    event_location = (event.get("event-location") or "").strip()
    address = event.get("address") or {}
    area = address.get("area") or {}
    street = (area.get("street-address") or "").strip()
    postal_code = (area.get("postal-code") or "").strip()
    locality = (area.get("locality") or "Madrid").strip()

    parts = []
    if event_location:
        parts.append(event_location)
    if street:
        parts.append(street)
    city_line = " ".join(x for x in [postal_code, locality] if x).strip()
    if city_line:
        parts.append(city_line)
    if not parts:
        parts.append("Madrid, Spain")
    return ", ".join(parts)


def fetch_existing_events():
    print("Récupération des events existants...")
    r = requests.get(f"{API_URL}/api/events", timeout=TIMEOUT)
    r.raise_for_status()
    events = decode_events(r.json())
    print(f"Total events actuels: {len(events)}")
    return events


def delete_old_madrid_events(events):
    to_delete = []
    for ev in events:
        domain = extract_domain(ev.get("source_url") or "")
        if domain in BAD_DOMAINS:
            ev_id = ev.get("id")
            if ev_id:
                to_delete.append(ev_id)

    print(f"Events madrid.es à supprimer: {len(to_delete)}")
    if not to_delete:
        return 0

    deleted = 0
    for i in range(0, len(to_delete), BATCH_SIZE):
        batch = to_delete[i : i + BATCH_SIZE]
        resp = requests.post(
            f"{API_URL}/api/events/delete-by-ids",
            json={"ids": batch, "reason": "Madrid reimport with official coordinates"},
            timeout=60,
        )
        if resp.status_code == 200:
            deleted += len(batch)
            print(f"  Batch {i // BATCH_SIZE + 1}: {len(batch)} supprimés (total {deleted})")
        else:
            print(f"  Batch {i // BATCH_SIZE + 1}: ERREUR {resp.status_code} {resp.text[:200]}")
        time.sleep(0.3)
    return deleted


def build_existing_sets(events):
    by_key = set()
    by_source = set()
    for ev in events:
        by_key.add(event_key(ev.get("title", ""), ev.get("date", "")))
        source_url = (ev.get("source_url") or "").strip().lower()
        if source_url:
            by_source.add(source_url)
    return by_key, by_source


def import_madrid():
    print("Téléchargement du dataset officiel Madrid...")
    r = requests.get(MADRID_DATASET_URL, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    graph = data.get("@graph", [])
    print(f"Items dataset: {len(graph)}")

    existing_after_delete = fetch_existing_events()
    existing_keys, existing_sources = build_existing_sets(existing_after_delete)

    payload = []
    today = date.today().isoformat()
    for item in graph:
        if "title" not in item:
            continue
        coords = item.get("location") or {}
        lat = coords.get("latitude")
        lng = coords.get("longitude")
        if lat is None or lng is None:
            continue
        try:
            lat = float(lat)
            lng = float(lng)
        except Exception:
            continue

        title = (item.get("title") or "").strip()
        if not title:
            continue
        start_date = str(item.get("dtstart") or "")[:10]
        if not start_date or start_date < today:
            continue

        source_url = (item.get("link") or "").strip()
        key = event_key(title, start_date)
        if key in existing_keys:
            continue
        if source_url and source_url.lower() in existing_sources:
            continue

        description = strip_html(item.get("description"))
        location = build_location(item)
        categories = assign_categories(title, description)
        organizer = ((item.get("organization") or {}).get("organization-name") or "").strip()

        payload.append(
            {
                "title": title,
                "description": description,
                "date": start_date,
                "end_date": str(item.get("dtend") or "")[:10] or None,
                "time": None,
                "end_time": None,
                "location": location,
                "latitude": lat,
                "longitude": lng,
                "categories": categories,
                "source_url": source_url,
                "organizer_name": organizer,
                "validation_status": "auto_validated",
            }
        )
        existing_keys.add(key)
        if source_url:
            existing_sources.add(source_url.lower())

    print(f"Events Madrid à importer: {len(payload)}")
    if not payload:
        return 0

    imported = 0
    for i in range(0, len(payload), BATCH_SIZE):
        batch = payload[i : i + BATCH_SIZE]
        resp = requests.post(
            f"{API_URL}/api/events/scraped/batch",
            json={"events": batch},
            timeout=90,
        )
        if resp.status_code == 200:
            imported += len(batch)
            print(f"  Batch import {i // BATCH_SIZE + 1}: {len(batch)} (total {imported})")
        else:
            print(f"  Batch import {i // BATCH_SIZE + 1}: ERREUR {resp.status_code} {resp.text[:250]}")
        time.sleep(0.3)
    return imported


if __name__ == "__main__":
    print("=" * 70)
    print("FIX MADRID - suppression anciennes coordonnées + réimport open data")
    print("=" * 70)
    all_events = fetch_existing_events()
    deleted_count = delete_old_madrid_events(all_events)
    imported_count = import_madrid()
    print("\n" + "=" * 70)
    print(f"Terminé. Supprimés: {deleted_count} | Importés: {imported_count}")
    print("=" * 70)
