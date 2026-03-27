#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Recatégorisation live "safe" :
- Corrige les catégories existantes de la map
- Ne supprime aucun événement
- N'applique que des corrections à confiance élevée
"""

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor

import requests

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
BATCH_SIZE = 100
MAX_WORKERS = 12


def strip_html(txt: str) -> str:
    s = txt or ""
    s = re.sub(r"<script[^>]*>.*?</script>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<style[^>]*>.*?</style>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def fetch_source_text(url: str) -> str:
    if not url:
        return ""
    try:
        r = requests.get(
            url,
            timeout=(4, 8),
            headers={"User-Agent": "MapEventAI-ProReclass/1.0"},
        )
        if r.status_code != 200:
            return ""
        html = r.text
        # OpenAgenda
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
        if m:
            try:
                data = json.loads(m.group(1))
                pp = data.get("props", {}).get("pageProps", {})
                ev = pp.get("event", {}) or {}
                td = ev.get("title", {})
                dd = ev.get("description", ev.get("longDescription", {}))
                title = td.get("fr") or td.get("en") or ""
                desc = dd.get("fr") or dd.get("en") or ""
                if title or desc:
                    return f"{title} {strip_html(desc)}"
            except Exception:
                pass
        # fallback meta/html
        metas = []
        for pat in (
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
            r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
        ):
            metas.extend(re.findall(pat, html, flags=re.I))
        meta_text = strip_html(" ".join(metas))
        if len(meta_text) > 20:
            return meta_text
        return strip_html(html[:24000])
    except Exception:
        return ""


def classify(text: str):
    t = (text or "").lower()

    # FOOD
    if re.search(r"(d[ée]jeuner|repas|brunch|gastronomi|culinaire|d[ée]gustation|food truck|restauration)", t):
        return ["Food & Drinks"], "food"

    # GAMES
    if re.search(r"(jeu de r[oô]le|\bjdr\b|roleplay|soir[ée]e jeux|jeux? de soci[ée]t[ée]|ludique|quiz|blind test|karaoke)", t):
        if re.search(r"(initiation|atelier|d[ée]couverte)", t):
            return ["Culture > Ateliers"], "games-workshop"
        return ["Loisirs & Animation > Jeux & Soirées > Soirée jeux"], "games"

    # READING / FAMILY
    if re.search(r"(n[ée] pour lire|ne pour lire|conte|lecture|biblioth[èe]que|m[ée]diath[èe]que)", t):
        if re.search(r"(petite enfance|b[ée]b[ée]s?|famille|enfants?)", t):
            return ["Famille & Enfants > Activités > Conte / Lecture"], "reading-family"
        return ["Culture > Littérature & Conte"], "reading-culture"

    # THEATRE / ARTS
    if re.search(r"(th[ée][aâ]tre|mise en sc[eè]ne|compagnie|spectacle|lecture sc[ée]nique)", t):
        return ["Arts Vivants > Théâtre"], "theatre"
    if re.search(r"(exposition|vernissage|galerie|mus[ée]e|photographie|peinture|sculpture)", t):
        return ["Culture > Expositions"], "expo"
    if re.search(r"(atelier|workshop|masterclass|initiation)", t):
        return ["Culture > Ateliers"], "atelier"
    if re.search(r"(conf[ée]rence|d[ée]bat|table ronde|rencontre)", t):
        return ["Culture > Conférences & Rencontres"], "conference"
    if re.search(r"(cin[ée]ma|film|projection|court-m[ée]trage)", t):
        return ["Culture > Cinéma & Projections"], "cinema"
    if re.search(r"(sport|football|tennis|rugby|basket|trail|randonn[ée]e|course)", t):
        return ["Sport > Terrestre"], "sport"

    return [], "uncertain"


def is_weak_category(cats):
    if not cats:
        return True
    weak = {
        "Music",
        "Culture",
        "Sport",
        "Food & Drinks",
        "Famille & Enfants",
        "Loisirs & Animation",
        "Autre",
        "Music > Autre",
    }
    if any((c or "").strip() in weak for c in cats):
        return True
    # Les mauvaises sorties observées: lecture/jeux/food classés en Music.
    if len(cats) == 1 and cats[0] == "Music":
        return True
    return False


def fetch_events():
    r = requests.get(f"{API}/events?limit=50000", timeout=180)
    r.raise_for_status()
    data = r.json()
    keys = data["k"]
    idx = {k: i for i, k in enumerate(keys)}
    return data["d"], idx


def process_row(row, idx):
    event_id = int(row[idx["id"]])
    title = (row[idx["title"]] or "").strip()
    location = (row[idx["location"]] or "").strip()
    source_url = (row[idx["source_url"]] or "").strip()
    old_cats = row[idx["categories"]] or []
    if not isinstance(old_cats, list):
        old_cats = []

    if not is_weak_category(old_cats):
        return None

    base_text = f"{title} {location}"
    source_text = fetch_source_text(source_url) if source_url else ""
    full_text = f"{base_text} {source_text}"
    new_cats, reason = classify(full_text)
    if not new_cats:
        return None
    if new_cats == old_cats:
        return None

    return {
        "id": event_id,
        "categories": new_cats,
        "old_categories": old_cats,
        "title": title,
        "reason": reason,
    }


def apply_updates(updates):
    done = 0
    for i in range(0, len(updates), BATCH_SIZE):
        batch = [{"id": u["id"], "categories": u["categories"]} for u in updates[i : i + BATCH_SIZE]]
        r = requests.post(f"{API}/admin/fix-categories", json={"updates": batch}, timeout=120)
        if r.status_code == 200:
            done += r.json().get("updated", 0)
        print(f"batch {i//BATCH_SIZE + 1}: {r.status_code}")
        time.sleep(0.15)
    return done


def main():
    rows, idx = fetch_events()
    print(f"events_loaded={len(rows)}")

    updates = []
    scanned = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        for out in ex.map(lambda r: process_row(r, idx), rows):
            scanned += 1
            if out:
                updates.append(out)
            if scanned % 2000 == 0:
                print(f"scanned={scanned} updates_ready={len(updates)}")

    print(f"updates_final={len(updates)}")
    done = apply_updates(updates) if updates else 0
    print(f"applied={done}")

    log = {
        "scanned": scanned,
        "updates_planned": len(updates),
        "applied": done,
        "sample": updates[:100],
    }
    with open("c:/MapEventAI_NEW/frontend/scraper/reclassify_live_map_pro_safe_log.json", "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print("log_written=c:/MapEventAI_NEW/frontend/scraper/reclassify_live_map_pro_safe_log.json")


if __name__ == "__main__":
    main()

