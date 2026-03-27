import importlib.util
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import requests

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
REPORT_PATH = Path("frontend/scraper/full_map_audit_report.json")
UA = {"User-Agent": "MapEventAI-FullAudit/1.0"}

ELECTRO_CAT_RE = re.compile(r"(electronic|electronique|électronique|techno)", re.I)
ELECTRO_TEXT_RE = re.compile(
    r"(techno|electronic|electro|electronique|électronique|\bdj\b|house|trance|psytrance|drum\s*&?\s*bass|dnb|dubstep|rave)",
    re.I,
)
JAZZ_TEXT_RE = re.compile(r"(jazz|latin jazz|soul|funk|blues)", re.I)
OPEN_DAY_TEXT_RE = re.compile(r"(portes ouvertes|jpo|open day|lyc[ée]e|coll[èe]ge|universit[ée])", re.I)
ATELIER_KIDS_RE = re.compile(r"(atelier|workshop).*(enfant|kids|jeunesse)|((enfant|kids|jeunesse).*(atelier|workshop))", re.I)


def load_valid_paths():
    spec = importlib.util.spec_from_file_location(
        "event_validator", "c:/MapEventAI_NEW/_lambda_src/unzipped/backend/event_validator.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.VALID_CATEGORY_PATHS


def strip_html(text):
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_source_text(url):
    if not url:
        return ""
    try:
        r = requests.get(url, timeout=(4, 8), headers=UA)
        if r.status_code != 200:
            return ""
        html = r.text
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
        return strip_html(html[:12000])
    except Exception:
        return ""


def main():
    valid = load_valid_paths()
    data = requests.get(f"{API}/events?limit=50000", timeout=180).json()
    keys = data["k"]
    idx = {k: i for i, k in enumerate(keys)}
    rows = data["d"]

    issues = {
        "empty_category": [],
        "invalid_category": [],
        "false_electronic": [],
        "jazz_with_electronic": [],
        "open_day_with_music_or_electro": [],
        "kids_workshop_with_electronic": [],
    }

    # Prefilter events that may need source-text analysis.
    source_candidates = []
    for r in rows:
        title = r[idx["title"]] or ""
        location = r[idx["location"]] or ""
        source_url = r[idx["source_url"]] or ""
        cats = r[idx["categories"]] or []
        if isinstance(cats, str):
            try:
                cats = json.loads(cats)
            except Exception:
                cats = [cats]
        cleaned = [c for c in cats if isinstance(c, str) and c.strip()]

        if not cleaned:
            issues["empty_category"].append(
                {"id": int(r[idx["id"]]), "title": title, "source_url": source_url}
            )
            continue

        invalid = [c for c in cleaned if c not in valid]
        if invalid:
            issues["invalid_category"].append(
                {
                    "id": int(r[idx["id"]]),
                    "title": title,
                    "invalid": invalid[:3],
                    "categories": cleaned[:3],
                    "source_url": source_url,
                }
            )

        joined = " | ".join(cleaned)
        if ELECTRO_CAT_RE.search(joined) or "Music" in joined:
            source_candidates.append(
                {
                    "id": int(r[idx["id"]]),
                    "title": title,
                    "location": location,
                    "source_url": source_url,
                    "categories": cleaned[:3],
                }
            )

    # Fetch source text in parallel for candidate checks.
    cache = {}

    def analyze_candidate(ev):
        src = ev["source_url"]
        if src in cache:
            text = cache[src]
        else:
            text = fetch_source_text(src)
            cache[src] = text
        merged = f"{ev['title']} {ev['location']} {text}".lower()
        cats_joined = " | ".join(ev["categories"]).lower()

        out = []
        has_electro_cat = bool(ELECTRO_CAT_RE.search(cats_joined))
        has_electro_text = bool(ELECTRO_TEXT_RE.search(merged))
        has_jazz_text = bool(JAZZ_TEXT_RE.search(merged))
        has_open_day = bool(OPEN_DAY_TEXT_RE.search(merged))
        has_kids_workshop = bool(ATELIER_KIDS_RE.search(merged))

        if has_electro_cat and not has_electro_text:
            out.append("false_electronic")
        if has_electro_cat and has_jazz_text and not has_electro_text:
            out.append("jazz_with_electronic")
        if has_open_day and ("music" in cats_joined or has_electro_cat):
            out.append("open_day_with_music_or_electro")
        if has_kids_workshop and has_electro_cat:
            out.append("kids_workshop_with_electronic")
        return ev, out, merged[:260]

    done = 0
    with ThreadPoolExecutor(max_workers=20) as ex:
        for ev, flags, excerpt in ex.map(analyze_candidate, source_candidates):
            done += 1
            if done % 500 == 0:
                print(f"analyzed_candidates={done}/{len(source_candidates)}")
            for flag in flags:
                issues[flag].append(
                    {
                        "id": ev["id"],
                        "title": ev["title"],
                        "categories": ev["categories"],
                        "source_url": ev["source_url"],
                        "excerpt": excerpt,
                    }
                )

    summary = {k: len(v) for k, v in issues.items()}
    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "events_total": len(rows),
        "source_candidates": len(source_candidates),
        "summary": summary,
        "samples": {k: v[:50] for k, v in issues.items()},
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    print(f"report={REPORT_PATH}")


if __name__ == "__main__":
    main()
