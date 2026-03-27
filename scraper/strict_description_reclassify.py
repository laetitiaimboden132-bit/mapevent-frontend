import importlib.util
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
BLACKLIST_PATH = Path("frontend/scraper/opendata_event_blacklist.json")
UA = {"User-Agent": "MapEventAI-StrictClassifier/1.0"}
APPLY_BATCH_SIZE = 50


def load_valid_paths():
    spec = importlib.util.spec_from_file_location(
        "event_validator", "c:/MapEventAI_NEW/_lambda_src/unzipped/backend/event_validator.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.VALID_CATEGORY_PATHS


def strip_html(s):
    s = re.sub(r"<script[^>]*>.*?</script>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<style[^>]*>.*?</style>", " ", s, flags=re.I | re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def fetch_source_text(url):
    if not url or not isinstance(url, str):
        return ""
    try:
        r = requests.get(url, timeout=(4, 8), headers=UA)
        if r.status_code != 200:
            return ""
        html = r.text
        # OpenAgenda: extraire en priorité __NEXT_DATA__
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
        # Fallback HTML: meta description / og:description souvent plus utile que le shell JS.
        metas = []
        for pat in (
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
            r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
            r'"description"\s*:\s*"([^"]+)"',
        ):
            metas.extend(re.findall(pat, html, flags=re.I))
        meta_text = " ".join(metas)
        cleaned_meta = strip_html(meta_text)
        if cleaned_meta and len(cleaned_meta) > 30:
            return cleaned_meta
        return strip_html(html[:20000])
    except Exception:
        return ""


def classify_from_text(text):
    t = (text or "").lower()

    # Non-events -> suppression
    if re.search(r"(recrut|emploi|poste\b|cdi\b|cdd\b|job dating|insertion professionnelle)", t):
        return None, "non-event: recruitment"
    if re.search(r"(\bà\s+louer\b|\ba\s+louer\b|immobilier|location saisonni|appartement)", t):
        return None, "non-event: rental"
    if re.search(r"(\bg[iî]te\b|auberge|h[ôo]tel|chalet|r[ée]sidence|centre de vacances)", t) and re.search(
        r"(catalogue|nuit[ée]e|couchage|r[ée]servation|hebergement|hébergement)", t
    ):
        return None, "non-event: accommodation"

    # FOOD / REPAS (évite les faux "Music" sur déjeuner, brunch, etc.)
    if re.search(r"(d[ée]jeuner|repas|brunch|gastronomi|cuisine|culinaire|d[ée]gustation|food truck|restauration)", t):
        return ["Food & Drinks"], "food"

    # JEUX (plateau, jdr, quiz, ludique...)
    if re.search(r"(jeu de r[oô]le|\bjdr\b|roleplay|soir[ée]e jeux|jeux? de soci[ée]t[ée]|ludique|quiz|blind test|karaoke)", t):
        if re.search(r"(initiation|atelier|d[ée]couverte)", t):
            return ["Culture > Ateliers"], "games-workshop"
        return ["Loisirs & Animation > Jeux & Soirées > Soirée jeux"], "games"

    # LECTURE / PETITE ENFANCE
    if re.search(r"(n[ée] pour lire|conte|lecture|biblioth[èe]que|m[ée]diath[èe]que|petite enfance|b[ée]b[ée]s?)", t):
        if re.search(r"(petite enfance|b[ée]b[ée]s?|famille|enfants?)", t):
            return ["Famille & Enfants > Activités > Conte / Lecture"], "reading-family"
        return ["Culture > Littérature & Conte"], "reading-culture"

    # Description-first priority: récit/témoignage + mise en scène => théâtre
    if re.search(r"(r[ée]cit|t[ée]moignage|mise en sc[eè]ne|compagnie|spectacle|th[ée][aâ]tre)", t):
        return ["Arts Vivants > Théâtre"], "theatre"
    if re.search(r"(exposition|vernissage|galerie|mus[ée]e|photographie|peinture|sculpture)", t):
        return ["Culture > Expositions"], "expo"
    if re.search(r"(atelier|workshop|masterclass|initiation)", t):
        return ["Culture > Ateliers"], "atelier"
    if re.search(r"(conf[ée]rence|d[ée]bat|table ronde|rencontre)", t):
        return ["Culture > Conférences & Rencontres"], "conference"
    if re.search(r"(portes ouvertes|jpo\b|open day|journ[ée]e d[ée]couverte|forum|salon d'orientation|orientation)", t):
        return ["Culture > Conférences & Rencontres", "Culture > Visites & Patrimoine"], "open-day"
    if re.search(r"(parentalit[ée]|b[ée]b[ée]|petite enfance|familles?)", t):
        return ["Famille & Enfants"], "family-parenting"
    if re.search(r"(astronomie|planetarium|plan[ée]tarium|m[ée]t[ée]orites?)", t):
        return ["Culture > Conférences & Rencontres"], "astronomy"
    if re.search(r"(num[ée]rique|digital|informatique|web|internet)", t):
        if re.search(r"(atelier|initiation|d[ée]couverte|formation|apprendre)", t):
            return ["Culture > Ateliers"], "digital-workshop"
        return ["Culture > Conférences & Rencontres"], "digital-conference"
    if re.search(r"(cin[ée]ma|film|projection|court-m[ée]trage)", t):
        return ["Culture > Cinéma & Projections"], "cinema"
    if re.search(r"(visite guid[ée]e|patrimoine|historique)", t):
        return ["Culture > Visites & Patrimoine"], "visite"
    if re.search(r"(lecture|conte|po[ée]sie|auteur|litt[ée]rature)", t):
        return ["Culture > Littérature & Conte"], "litterature"
    if re.search(r"(danse|ballet|chor[ée]graph)", t):
        return ["Arts Vivants > Danse"], "danse"
    # =========================
    # MUSIQUE - niveaux précis
    # =========================
    if re.search(r"(jazz|latin jazz|smooth jazz|fusion jazz|blues|soul|funk)", t):
        if re.search(r"latin jazz", t):
            return ["Music > Jazz / Soul / Funk > Jazz"], "music-jazz"
        if re.search(r"blues", t):
            return ["Music > Jazz / Soul / Funk > Blues"], "music-blues"
        if re.search(r"soul", t):
            return ["Music > Jazz / Soul / Funk > Soul"], "music-soul"
        if re.search(r"funk", t):
            return ["Music > Jazz / Soul / Funk > Funk"], "music-funk"
        return ["Music > Jazz / Soul / Funk > Jazz"], "music-jazz"

    # Electro doit être MUSICAL, pas techno/électronique au sens technologie.
    electro_music_signal = re.search(
        r"(dj\b|set\b|soir[ée]e?|concert|festival|club|dancefloor|lineup|live|musique|music|rave|afterparty|open air)",
        t,
    )
    electro_style = re.search(
        r"(techno|acid techno|minimal techno|hard techno|industrial techno|melodic techno|dub techno|"
        r"house|deep house|electro house|tech house|progressive house|trance|psytrance|goa|full on|"
        r"drum\s*&?\s*bass|dnb|dubstep|hardstyle|hardcore|gabber)",
        t,
    )
    tech_context = re.search(
        r"(atelier num[ée]rique|robotique|arduino|capteur|circuit|electronique|technologie|coding|programmation)",
        t,
    )
    if electro_style and electro_music_signal and not tech_context:
        if re.search(r"acid techno", t):
            return ["Music > Electronic > Techno > Acid Techno"], "music-electro-techno-acid"
        if re.search(r"minimal techno", t):
            return ["Music > Electronic > Techno > Minimal Techno"], "music-electro-techno-minimal"
        if re.search(r"(hard techno|industrial techno)", t):
            return ["Music > Electronic > Techno > Hard Techno"], "music-electro-techno-hard"
        if re.search(r"melodic techno", t):
            return ["Music > Electronic > Techno > Melodic Techno"], "music-electro-techno-melodic"
        if re.search(r"(deep house)", t):
            return ["Music > Electronic > House > Deep House"], "music-electro-house-deep"
        if re.search(r"(tech house)", t):
            return ["Music > Electronic > House > Tech House"], "music-electro-house-tech"
        if re.search(r"(electro house)", t):
            return ["Music > Electronic > House > Electro House"], "music-electro-house-electro"
        if re.search(r"(progressive house)", t):
            return ["Music > Electronic > House > Progressive House"], "music-electro-house-progressive"
        if re.search(r"(psytrance|goa|full on)", t):
            return ["Music > Electronic > Trance > Psytrance"], "music-electro-trance-psy"
        if re.search(r"(drum\\s*&?\\s*bass|dnb)", t):
            return ["Music > Electronic > Drum & Bass > Liquid DnB"], "music-electro-dnb"
        if re.search(r"(dubstep)", t):
            return ["Music > Electronic > Bass Music > Dubstep"], "music-electro-dubstep"
        if re.search(r"(hardstyle|hardcore|gabber)", t):
            return ["Music > Electronic > Hard Music > Hardstyle"], "music-electro-hard"
        return ["Music > Electronic"], "music-electro"

    # Instruments sans style clair -> Music générique
    if re.search(r"(piano|guitare|guitar|violon|violoncelle|fl[ûu]te|saxophone|trompette|percussions?|harpe|instrumental)", t):
        if not re.search(r"(jazz|rock|metal|rap|hip-hop|techno|house|trance|electro|electronic|classique|folk|pop)", t):
            return ["Music"], "music-fallback-instrument"

    # Genres musicaux non-electro
    if re.search(r"(metal|black metal|death metal|thrash metal)", t):
        return ["Music > Rock / Metal > Metal"], "music-metal"
    if re.search(r"(rock|indie rock|punk rock|garage rock|grunge)", t):
        return ["Music > Rock / Metal > Rock"], "music-rock"
    if re.search(r"(rap|hip-hop|trap|drill|rnb|grime)", t):
        return ["Music > Urban"], "music-urban"
    if re.search(r"(folk|acoustic|bluegrass|country)", t):
        return ["Music > Folk / Acoustic"], "music-folk"
    if re.search(r"(op[eé]ra|orchestre symphonique|concerto|sonate|baroque|classique)", t):
        return ["Music > Classique"], "music-classic"
    if re.search(r"(concert|musique|music|live|orchestre|r[ée]cital)", t):
        return ["Music"], "music"
    if re.search(r"(course|trail|randonn[ée]e|marathon|sport|football|tennis|rugby|basket|cycl)", t):
        return ["Sport > Terrestre"], "sport"
    if re.search(r"(enfant|famille|kids|jeunesse|marionnette)", t):
        return ["Famille & Enfants"], "famille"
    if re.search(r"(festival|open air|f[êe]te|salon)", t):
        return ["Festivals & Grandes Fêtes"], "festival"
    if re.search(r"(march[ée] |brocante|vide-grenier|foire)", t):
        return ["Loisirs & Animation > Défilés & Fêtes > Marché"], "marche"
    if re.search(r"(nature|jardin|plein air|botanique)", t):
        return ["Nature & Plein Air"], "nature"
    if re.search(r"(networking|startup|meetup|business|s[ée]minaire)", t):
        return ["Business & Communauté"], "business"
    if re.search(r"(bien-[êe]tre|m[ée]ditation|sophrologie|spa|yoga)", t):
        return ["Bien-être"], "wellness"

    # IMPORTANT: ne plus forcer "Music" par défaut.
    # Mieux vaut quarantaine/review qu'une mauvaise catégorie systématique.
    return [], "uncertain"


def load_blacklist():
    if BLACKLIST_PATH.exists():
        try:
            return json.loads(BLACKLIST_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {"ids": [], "source_urls": [], "items": []}
    return {"ids": [], "source_urls": [], "items": []}


def save_blacklist(data):
    BLACKLIST_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def push_updates(updates):
    if not updates:
        return 0
    done = 0
    for i in range(0, len(updates), APPLY_BATCH_SIZE):
        batch = updates[i : i + APPLY_BATCH_SIZE]
        resp = requests.post(f"{API}/admin/fix-categories", json={"updates": batch}, timeout=120)
        if resp.status_code == 200:
            done += resp.json().get("updated", 0)
        print(f"fix-categories batch {i//APPLY_BATCH_SIZE + 1}: {resp.status_code}")
    return done


def push_deletes(delete_ids):
    if not delete_ids:
        return 0
    done = 0
    for i in range(0, len(delete_ids), APPLY_BATCH_SIZE):
        batch = delete_ids[i : i + APPLY_BATCH_SIZE]
        resp = requests.post(f"{API}/admin/delete-events", json={"ids": batch}, timeout=120)
        if resp.status_code == 200:
            done += resp.json().get("deleted", 0)
        print(f"delete-events batch {i//APPLY_BATCH_SIZE + 1}: {resp.status_code}")
    return done


def main():
    valid = load_valid_paths()
    data = requests.get(f"{API}/events?limit=50000", timeout=180).json()
    keys = data["k"]
    idx = {k: i for i, k in enumerate(keys)}
    rows = data["d"]

    updates = []
    delete_ids = []
    quarantine_ids = []
    blacklist = load_blacklist()

    total = 0
    fetched_details = 0
    done_updates = 0
    done_deleted = 0
    # Analyse complète: tous les events pour tri global qualité
    invalid_rows = rows

    def process_row(r):
        event_id = int(r[idx["id"]])
        title = r[idx["title"]] or ""
        location = r[idx["location"]] or ""
        source_url = r[idx["source_url"]] or ""

        quick_text = f"{title} {location}"
        source_text = fetch_source_text(source_url) if source_url else ""
        if not source_text:
            # Si la source est muette, on tente quand même un tri par titre+lieu
            # pour limiter les quarantaines inutiles.
            guess_cats, guess_reason = classify_from_text(quick_text)
            if guess_cats is None:
                return {
                    "kind": "delete",
                    "id": event_id,
                    "title": title,
                    "source_url": source_url,
                    "reason": f"{guess_reason}-title-only",
                    "excerpt": quick_text[:260],
                    "fetched": 0,
                }
            if guess_cats:
                safe_guess = [c for c in guess_cats if c in valid][:3]
                if safe_guess:
                    return {
                        "kind": "update",
                        "id": event_id,
                        "categories": safe_guess,
                        "fetched": 0,
                    }
            return {
                "kind": "quarantine",
                "id": event_id,
                "title": title,
                "source_url": source_url,
                "reason": "uncertain-no-description",
                "excerpt": quick_text[:260],
                "fetched": 0,
            }

        text = f"{quick_text} {source_text}"
        new_cats, reason = classify_from_text(text)
        excerpt = (source_text or quick_text or "")[:260]

        if new_cats is None:
            return {
                "kind": "delete",
                "id": event_id,
                "title": title,
                "source_url": source_url,
                "reason": reason,
                "excerpt": excerpt,
                "fetched": 1,
            }
        if not new_cats:
            return {
                "kind": "quarantine",
                "id": event_id,
                "title": title,
                "source_url": source_url,
                "reason": "uncertain",
                "excerpt": excerpt,
                "fetched": 1,
            }
        safe = [c for c in new_cats if c in valid][:3]
        return {
            "kind": "update",
            "id": event_id,
            "categories": safe,
            "fetched": 1,
        }

    chunk_size = 300
    max_workers = 16
    for i in range(0, len(invalid_rows), chunk_size):
        chunk = invalid_rows[i : i + chunk_size]
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            for out in ex.map(process_row, chunk):
                total += 1
                fetched_details += out.get("fetched", 0)
                kind = out["kind"]
                if kind == "update":
                    updates.append({"id": out["id"], "categories": out["categories"]})
                elif kind == "delete":
                    delete_ids.append(out["id"])
                    blacklist["ids"].append(out["id"])
                    if out.get("source_url"):
                        blacklist["source_urls"].append(out["source_url"])
                    blacklist["items"].append(
                        {
                            "id": out["id"],
                            "title": out.get("title", ""),
                            "source_url": out.get("source_url", ""),
                            "reason": out.get("reason", "delete"),
                            "excerpt": out.get("excerpt", ""),
                        }
                    )
                else:
                    quarantine_ids.append(out["id"])
                    blacklist["ids"].append(out["id"])
                    if out.get("source_url"):
                        blacklist["source_urls"].append(out["source_url"])
                    blacklist["items"].append(
                        {
                            "id": out["id"],
                            "title": out.get("title", ""),
                            "source_url": out.get("source_url", ""),
                            "reason": out.get("reason", "uncertain"),
                            "excerpt": out.get("excerpt", ""),
                        }
                    )

        print(
            f"processed={total} updates={len(updates)} deletes={len(delete_ids)} "
            f"quarantine={len(quarantine_ids)} fetched_details={fetched_details}"
        )
        # Flush incrémental à chaque chunk.
        done_updates += push_updates(updates)
        done_deleted += push_deletes(delete_ids)
        updates.clear()
        delete_ids.clear()
        time.sleep(0.05)

    # dedupe blacklist
    blacklist["ids"] = sorted(set(int(x) for x in blacklist.get("ids", [])))
    blacklist["source_urls"] = sorted(set(x for x in blacklist.get("source_urls", []) if x))
    save_blacklist(blacklist)

    # Flush final
    done_updates += push_updates(updates)
    done_deleted += push_deletes(delete_ids)

    print(
        json.dumps(
            {
                "invalid_seen": total,
                "planned_updates": len(updates),
                "planned_deletes": len(delete_ids),
                "planned_quarantine": len(quarantine_ids),
                "done_updates": done_updates,
                "done_deleted": done_deleted,
                "blacklist_ids": len(blacklist["ids"]),
                "blacklist_urls": len(blacklist["source_urls"]),
                "fetched_details": fetched_details,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
