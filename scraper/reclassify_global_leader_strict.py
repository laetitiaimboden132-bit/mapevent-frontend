#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FULL MAP - Reclassify Leader Strict
Objectif:
- Recatégoriser toute la map selon le descriptif source réel
- Supprimer les non-events évidents
- Supprimer les events à durée > 14 jours (anti-saisonnier)
- Éviter les mauvais mappings (ex: festival rock -> conférence)
"""

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
FETCH_LIMIT = 50000
MAX_WORKERS = 14
BATCH_UPDATES = 80
BATCH_DELETES = 80


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
            headers={"User-Agent": "MapEventAI-GlobalLeaderStrict/1.0"},
        )
        if r.status_code != 200:
            return ""
        html = r.text

        # OpenAgenda JSON
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


def parse_day(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s)[:10])
    except Exception:
        return None


def category_domain(cat: str) -> str:
    c = (cat or "").lower()
    if any(k in c for k in ("music", "musique", "electro", "techno", "house", "trance", "jazz", "rock", "rap")):
        return "music"
    if any(k in c for k in ("culture", "exposition", "atelier", "conférence", "conference", "cinéma", "cinema", "littérature", "litterature")):
        return "culture"
    if any(k in c for k in ("arts vivants", "théâtre", "theatre", "danse", "cirque")):
        return "arts"
    if any(k in c for k in ("food", "drink", "gastronomie", "dégust", "degust")):
        return "food"
    if any(k in c for k in ("sport", "trail", "football", "tennis", "rugby", "basket")):
        return "sport"
    if any(k in c for k in ("famille", "enfants", "kids")):
        return "family"
    if any(k in c for k in ("jeux", "soirée jeux", "soiree jeux", "loisirs")):
        return "games"
    return "other"


def classify(text: str):
    t = (text or "").lower()

    # Non-events (suppression)
    if re.search(r"(emploi|recrut|poste\b|cdi\b|cdd\b|job dating|candidature)", t):
        return None, "non_event_recruitment", 5
    if re.search(r"(à louer|a louer|immobilier|location saisonni|appartement|hébergement permanent|hebergement permanent)", t):
        return None, "non_event_rental", 5
    if re.search(r"(horaires d'ouverture|ouvert tous les jours|parc d'attractions|parc d’attractions|centre de loisirs|activité permanente)", t) and not re.search(r"(date|du\s+\d|jusqu'au|jusqu’au|édition|festival|concert|spectacle)", t):
        return None, "non_event_permanent_place", 5

    # Food
    if re.search(r"(déjeuner|dejeuner|repas|brunch|gastronomi|culinaire|dégustation|degustation|food truck|restauration)", t):
        return ["Food & Drinks"], "food", 5

    # Games
    if re.search(r"(jeu de rôle|jeu de role|\bjdr\b|roleplay|soirée jeux|soiree jeux|jeux de société|jeux de societe|ludique|quiz|blind test|karaoke)", t):
        if re.search(r"(initiation|atelier|découverte|decouverte)", t):
            return ["Culture > Ateliers"], "games_workshop", 5
        return ["Loisirs & Animation > Jeux & Soirées > Soirée jeux"], "games", 4

    # Reading / family
    if re.search(r"(né pour lire|ne pour lire|conte|lecture|bibliothèque|bibliotheque|médiathèque|mediatheque)", t):
        if re.search(r"(petite enfance|bébé|bebe|famille|enfants?)", t):
            return ["Famille & Enfants > Activités > Conte / Lecture"], "reading_family", 5
        return ["Culture > Littérature & Conte"], "reading_culture", 4

    # Arts / culture
    if re.search(r"(théâtre|theatre|mise en scène|mise en scene|compagnie|spectacle|lecture scénique|lecture scenique)", t):
        return ["Arts Vivants > Théâtre"], "theatre", 5
    if re.search(r"(exposition|vernissage|galerie|musée|musee|photographie|peinture|sculpture)", t):
        return ["Culture > Expositions"], "expo", 5
    if re.search(r"(atelier|workshop|masterclass|initiation)", t):
        return ["Culture > Ateliers"], "atelier", 4
    if re.search(r"(conférence|conference|débat|debat|table ronde|rencontre)", t):
        return ["Culture > Conférences & Rencontres"], "conference", 4
    if re.search(r"(cinéma|cinema|film|projection|court-métrage|court-metrage)", t):
        return ["Culture > Cinéma & Projections"], "cinema", 4
    if re.search(r"(visite guidée|visite guidee|patrimoine|historique)", t):
        return ["Culture > Visites & Patrimoine"], "heritage", 4

    # Music
    if re.search(r"(festival rock|rock festival|concert rock|metal fest|festival metal)", t):
        return ["Music > Rock / Metal > Rock"], "music_rock_festival", 5
    if re.search(r"(concert|dj|lineup|line-up|live|soirée|soiree|rave|club|musique|music|techno|house|trance|jazz|rock|rap|hip-hop|hip hop|electro|electronic)", t):
        return ["Music"], "music", 3

    # Sport
    if re.search(r"(sport|match|tournoi|course|running|trail|randonnée|randonnee|football|basket|tennis|rugby|natation|ski|snowboard)", t):
        return ["Sport > Terrestre"], "sport", 4

    # Family generic
    if re.search(r"(enfant|kids|famille|marionnettes|goûter|gouter)", t):
        return ["Famille & Enfants"], "family", 3

    return [], "uncertain", 0


def fetch_events():
    r = requests.get(f"{API}/events?limit={FETCH_LIMIT}", timeout=200)
    r.raise_for_status()
    payload = r.json()
    keys = payload["k"]
    idx = {k: i for i, k in enumerate(keys)}
    events = []
    for row in payload["d"]:
        cats = row[idx["categories"]] if idx.get("categories") is not None else []
        events.append(
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
    return events


def should_process(e):
    cats = e.get("categories") or []
    weak = (
        not cats
        or cats == ["Music"]
        or cats == ["Culture"]
        or any(c in ("Autre", "Music > Autre") for c in cats)
    )
    title = (e.get("title") or "").lower()
    suspicious = any(x in title for x in ("happyland", "déjeuner", "dejeuner", "né pour lire", "ne pour lire", "jeu de rôle", "jeu de role"))
    return weak or suspicious


def process_one(e):
    start = parse_day(e.get("date"))
    end = parse_day(e.get("end_date")) or start
    if start and end:
        span = (end - start).days
        if span > 14:
            return {"action": "delete", "id": e["id"], "reason": "duration_gt_14_days", "title": e["title"], "span": span}

    src_txt = fetch_source_text(e.get("source_url"))
    text = f"{e.get('title','')} {e.get('location','')} {src_txt}"
    inferred, reason, conf = classify(text)
    old = e.get("categories", [])

    if inferred is None:
        return {"action": "delete", "id": e["id"], "reason": reason, "title": e["title"]}

    if inferred and conf >= 4:
        old_dom = category_domain(old[0]) if old else "other"
        new_dom = category_domain(inferred[0])
        # Corriger aussi les mismatches de domaine
        if inferred != old or old_dom != new_dom:
            return {
                "action": "update",
                "id": e["id"],
                "categories": inferred,
                "reason": reason,
                "confidence": conf,
                "title": e["title"],
                "old_categories": old,
            }

    return {"action": "skip", "id": e["id"], "reason": reason}


def push_updates(updates):
    done = 0
    for i in range(0, len(updates), BATCH_UPDATES):
        batch = updates[i : i + BATCH_UPDATES]
        payload = {"updates": [{"id": x["id"], "categories": x["categories"]} for x in batch]}
        r = requests.post(f"{API}/admin/fix-categories", json=payload, timeout=120)
        if r.status_code == 200:
            done += r.json().get("updated", 0)
        print(f"fix-categories batch={i//BATCH_UPDATES + 1} status={r.status_code}")
        time.sleep(0.15)
    return done


def push_deletes(delete_ids):
    done = 0
    for i in range(0, len(delete_ids), BATCH_DELETES):
        batch = delete_ids[i : i + BATCH_DELETES]
        r = requests.post(f"{API}/admin/delete-events", json={"ids": batch}, timeout=120)
        if r.status_code == 200:
            done += r.json().get("deleted", 0)
        print(f"delete-events batch={i//BATCH_DELETES + 1} status={r.status_code}")
        time.sleep(0.15)
    return done


def main():
    events = fetch_events()
    print(f"events_total={len(events)}")

    targets = [e for e in events if should_process(e)]
    print(f"targets={len(targets)}")

    updates = []
    deletes = []
    skipped = 0
    processed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        for out in ex.map(process_one, targets):
            processed += 1
            if out["action"] == "update":
                updates.append(out)
            elif out["action"] == "delete":
                deletes.append(out)
            else:
                skipped += 1
            if processed % 300 == 0:
                print(f"processed={processed}/{len(targets)} updates={len(updates)} deletes={len(deletes)} skipped={skipped}")

    delete_ids = [d["id"] for d in deletes]
    print(f"updates_planned={len(updates)} deletes_planned={len(delete_ids)}")

    updated_done = push_updates(updates) if updates else 0
    deleted_done = push_deletes(delete_ids) if delete_ids else 0

    report = {
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "events_total": len(events),
        "targets": len(targets),
        "updates_planned": len(updates),
        "deletes_planned": len(delete_ids),
        "updated_done": updated_done,
        "deleted_done": deleted_done,
        "skipped": skipped,
        "sample_updates": updates[:150],
        "sample_deletes": deletes[:150],
    }

    out = "c:/MapEventAI_NEW/frontend/scraper/reclassify_global_leader_strict_report.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"report={out}")


if __name__ == "__main__":
    main()

