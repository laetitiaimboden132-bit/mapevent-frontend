#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Retri massif prioritaire Valais + Suisse romande
- Lit les descriptifs sources (quand dispo)
- Corrige les catégories avec règles strictes
- Génère un rapport qualité (dont événements > 14 jours)
"""

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
BATCH = 80
MAX_WORKERS = 14


ROMANDIE_MARKERS = [
    "valais", "vaud", "genève", "geneve", "fribourg", "neuchâtel", "neuchatel", "jura",
    "sierre", "sion", "martigny", "monthey", "verbier", "lausanne", "nyon", "morges",
    "vevey", "montreux", "yverdon", "fribourg", "bulle", "delémont", "delemont", "la chaux-de-fonds",
    "vouvry", "collombey", "aigle", "romandie",
]


def strip_html(txt: str) -> str:
    s = txt or ""
    s = re.sub(r"<script[^>]*>.*?</script>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<style[^>]*>.*?</style>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def fetch_source_text(url: str) -> str:
    if not url:
        return ""
    try:
        r = requests.get(
            url,
            timeout=(4, 10),
            headers={"User-Agent": "MapEventAI-RomandieLeader/1.0"},
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
        metas = []
        for pat in (
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
            r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
        ):
            metas.extend(re.findall(pat, html, flags=re.I))
        meta_text = strip_html(" ".join(metas))
        if len(meta_text) > 20:
            return meta_text
        return strip_html(html[:30000])
    except Exception:
        return ""


def in_romandie(item) -> bool:
    blob = " ".join(
        [
            str(item.get("title", "")),
            str(item.get("location", "")),
            str(item.get("source_url", "")),
        ]
    ).lower()
    return any(m in blob for m in ROMANDIE_MARKERS)


def parse_date(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s)[:10])
    except Exception:
        return None


def classify(text: str):
    t = (text or "").lower()
    confidence = 0

    if re.search(r"(d[ée]jeuner|repas|brunch|gastronomi|culinaire|d[ée]gustation|food truck|restauration)", t):
        return ["Food & Drinks"], "food", 5

    if re.search(r"(jeu de r[oô]le|\bjdr\b|roleplay|soir[ée]e jeux|jeux? de soci[ée]t[ée]|ludique|quiz|blind test|karaoke)", t):
        if re.search(r"(initiation|atelier|d[ée]couverte)", t):
            return ["Culture > Ateliers"], "games-workshop", 5
        return ["Loisirs & Animation > Jeux & Soirées > Soirée jeux"], "games", 4

    if re.search(r"(n[ée] pour lire|ne pour lire|conte|lecture|biblioth[èe]que|m[ée]diath[èe]que)", t):
        if re.search(r"(petite enfance|b[ée]b[ée]s?|famille|enfants?)", t):
            return ["Famille & Enfants > Activités > Conte / Lecture"], "reading-family", 5
        return ["Culture > Littérature & Conte"], "reading-culture", 4

    if re.search(r"(th[ée][aâ]tre|mise en sc[eè]ne|compagnie|spectacle|lecture sc[ée]nique)", t):
        return ["Arts Vivants > Théâtre"], "theatre", 4
    if re.search(r"(exposition|vernissage|galerie|mus[ée]e|photographie|peinture|sculpture)", t):
        return ["Culture > Expositions"], "expo", 4
    if re.search(r"(atelier|workshop|masterclass|initiation)", t):
        return ["Culture > Ateliers"], "atelier", 3
    if re.search(r"(conf[ée]rence|d[ée]bat|table ronde|rencontre)", t):
        return ["Culture > Conférences & Rencontres"], "conference", 3
    if re.search(r"(cin[ée]ma|film|projection|court-m[ée]trage)", t):
        return ["Culture > Cinéma & Projections"], "cinema", 4
    if re.search(r"(festival|open air|f[êe]te|salon)", t):
        return ["Festivals & Grandes Fêtes"], "festival", 3
    if re.search(r"(concert|live|dj|lineup|musique|music|electro|techno|house|trance|jazz|rock|rap)", t):
        return ["Music"], "music", 2
    if re.search(r"(sport|football|tennis|rugby|basket|trail|randonn[ée]e|course)", t):
        return ["Sport > Terrestre"], "sport", 3

    return [], "uncertain", confidence


def target_event(item):
    cats = item.get("categories") or []
    if not isinstance(cats, list):
        cats = []
    title = (item.get("title") or "").lower()
    loc = (item.get("location") or "").lower()
    src = (item.get("source_url") or "").lower()

    weak = (
        len(cats) == 0
        or cats == ["Music"]
        or cats == ["Culture"]
        or "Autre" in cats
        or "Music > Autre" in cats
    )

    suspicious_title = any(x in title for x in ("déjeuner", "dejeuner", "jeu de rôle", "jeu de role", "né pour lire", "ne pour lire", "happyland"))
    regional = in_romandie({"title": title, "location": loc, "source_url": src})
    return regional and (weak or suspicious_title)


def fetch_events():
    r = requests.get(f"{API}/events?limit=50000", timeout=180)
    r.raise_for_status()
    data = r.json()
    keys = data["k"]
    idx = {k: i for i, k in enumerate(keys)}
    out = []
    for row in data["d"]:
        cats = row[idx["categories"]] if idx.get("categories") is not None else []
        out.append(
            {
                "id": int(row[idx["id"]]),
                "title": row[idx["title"]] or "",
                "location": row[idx["location"]] or "",
                "date": row[idx["date"]],
                "end_date": row[idx["end_date"]],
                "categories": cats if isinstance(cats, list) else [],
                "source_url": row[idx["source_url"]] or "",
            }
        )
    return out


def apply_category_updates(updates):
    done = 0
    for i in range(0, len(updates), BATCH):
        batch = updates[i : i + BATCH]
        payload = {"updates": [{"id": u["id"], "categories": u["categories"]} for u in batch]}
        r = requests.post(f"{API}/admin/fix-categories", json=payload, timeout=120)
        if r.status_code == 200:
            done += r.json().get("updated", 0)
        print(f"fix-categories batch={i//BATCH + 1} status={r.status_code}")
        time.sleep(0.15)
    return done


def main():
    events = fetch_events()
    print(f"events_total={len(events)}")

    targets = [e for e in events if target_event(e)]
    print(f"targets_romandie={len(targets)}")

    now = datetime.now()
    long_range = []
    updates = []
    uncertain = []

    def process(e):
        date = parse_date(e.get("date"))
        end_date = parse_date(e.get("end_date")) or date
        if date and end_date:
            delta = (end_date - date).days
            if delta > 14:
                long_range.append(
                    {
                        "id": e["id"],
                        "title": e["title"],
                        "date": e["date"],
                        "end_date": e["end_date"],
                        "days_span": delta,
                    }
                )
        src_txt = fetch_source_text(e.get("source_url"))
        text = f"{e.get('title','')} {e.get('location','')} {src_txt}"
        cats, reason, conf = classify(text)
        old = e.get("categories", [])
        if conf >= 3 and cats and cats != old:
            return {
                "id": e["id"],
                "title": e["title"],
                "old_categories": old,
                "categories": cats,
                "reason": reason,
                "confidence": conf,
            }
        if conf == 0:
            return {
                "id": e["id"],
                "title": e["title"],
                "old_categories": old,
                "reason": reason,
            }
        return None

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        i = 0
        for out in ex.map(process, targets):
            i += 1
            if out:
                if out.get("categories"):
                    updates.append(out)
                else:
                    uncertain.append(out)
            if i % 200 == 0:
                print(f"processed={i}/{len(targets)} updates={len(updates)} uncertain={len(uncertain)}")

    print(f"updates_planned={len(updates)}")
    applied = apply_category_updates(updates) if updates else 0
    print(f"updates_applied={applied}")

    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "focus": "valais_suisse_romande",
        "events_total": len(events),
        "targets_romandie": len(targets),
        "updates_planned": len(updates),
        "updates_applied": applied,
        "uncertain_count": len(uncertain),
        "long_range_count": len(long_range),
        "sample_updates": updates[:120],
        "sample_uncertain": uncertain[:120],
        "long_range_sample": long_range[:120],
    }
    path = "c:/MapEventAI_NEW/frontend/scraper/reclassify_romandie_leader_report.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"report={path}")


if __name__ == "__main__":
    main()

