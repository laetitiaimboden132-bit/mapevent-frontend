#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construit une base de prospects organisateurs depuis les JSON déjà présents.

Sortie:
- frontend/scraper/organizer_prospects_prioritized.json
"""

import json
import os
import re
from pathlib import Path

from email_registry import is_blocked_email, was_already_sent

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILES = [
    BASE_DIR / "emails_organisateurs" / "TOUS_LES_EMAILS.json",
    BASE_DIR / "all_organizer_emails.json",
    BASE_DIR / "organizer_emails_new.json",
]

OUTPUT_FILE_STRICT = BASE_DIR / "organizer_prospects_prioritized.json"
OUTPUT_FILE_BROAD = BASE_DIR / "organizer_prospects_broad.json"

EMAIL_RE = re.compile(r"(?i)^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}$")

TYPE_KEYWORDS = {
    "club": ["club", "night", "dj", "soirée", "soiree", "party", "electro", "techno"],
    "bar": ["bar", "cocktail", "pub", "taproom"],
    "salle_culturelle": ["théâtre", "theatre", "salle", "auditorium", "arena", "comédie", "comedie"],
    "festival": ["festival", "open air", "jazz", "ciné", "cine", "arts vivants"],
    "musee_galerie": ["musée", "musee", "galerie", "exposition", "vernissage"],
}


def normalize_email(email: str) -> str:
    e = (email or "").strip().lower()
    e = e.strip(".,;:()[]<>\"'")
    return e


def classify(text: str) -> str:
    t = (text or "").lower()
    for label, kws in TYPE_KEYWORDS.items():
        if any(k in t for k in kws):
            return label
    return "autre_event"


def iter_rows(path: Path):
    if not path.exists():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                email = item.get("email")
                title = item.get("title") or item.get("event") or ""
                source_url = item.get("source_url") or ""
                source_name = item.get("source_name") or ""
                yield email, title, source_url, source_name
            elif isinstance(item, list) and len(item) >= 2:
                title = str(item[0] or "")
                email = str(item[1] or "")
                yield email, title, "", ""


def main():
    by_email_strict = {}
    by_email_broad = {}
    scanned = 0

    for f in INPUT_FILES:
        for email, title, source_url, source_name in iter_rows(f):
            scanned += 1
            e = normalize_email(email)
            if not e or not EMAIL_RE.match(e):
                continue

            if was_already_sent(e):
                continue

            txt = f"{title} {source_name} {source_url}"
            candidate = {
                "email": e,
                "title": title,
                "source_url": source_url,
                "source_name": source_name,
                "type": classify(txt),
            }

            # Broad: toutes adresses valides jamais contactées.
            row_b = by_email_broad.get(e)
            if row_b is None:
                by_email_broad[e] = candidate
            else:
                cur_score_b = len((row_b.get("title") or "")) + len((row_b.get("source_url") or ""))
                new_score_b = len(title or "") + len(source_url or "")
                if new_score_b > cur_score_b:
                    by_email_broad[e] = candidate

            # Strict: passe aussi les règles anti-génériques/anti-concurrents.
            blocked, _ = is_blocked_email(e)
            if blocked:
                continue
            row_s = by_email_strict.get(e)
            if row_s is None:
                by_email_strict[e] = candidate
            else:
                cur_score_s = len((row_s.get("title") or "")) + len((row_s.get("source_url") or ""))
                new_score_s = len(title or "") + len(source_url or "")
                if new_score_s > cur_score_s:
                    by_email_strict[e] = candidate

    rows_strict = list(by_email_strict.values())
    rows_broad = list(by_email_broad.values())
    type_order = {
        "club": 0,
        "bar": 1,
        "salle_culturelle": 2,
        "festival": 3,
        "musee_galerie": 4,
        "autre_event": 5,
    }
    rows_strict.sort(key=lambda r: (type_order.get(r.get("type"), 9), r.get("email", "")))
    rows_broad.sort(key=lambda r: (type_order.get(r.get("type"), 9), r.get("email", "")))

    OUTPUT_FILE_STRICT.write_text(json.dumps(rows_strict, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_FILE_BROAD.write_text(json.dumps(rows_broad, ensure_ascii=False, indent=2), encoding="utf-8")

    counts_strict = {}
    for r in rows_strict:
        t = r.get("type", "autre_event")
        counts_strict[t] = counts_strict.get(t, 0) + 1

    counts_broad = {}
    for r in rows_broad:
        t = r.get("type", "autre_event")
        counts_broad[t] = counts_broad.get(t, 0) + 1

    print(f"Scanned rows: {scanned}")
    print(f"Strict prospects: {len(rows_strict)}")
    print(f"Strict by type: {counts_strict}")
    print(f"Broad prospects: {len(rows_broad)}")
    print(f"Broad by type: {counts_broad}")
    print(f"Output strict: {OUTPUT_FILE_STRICT}")
    print(f"Output broad: {OUTPUT_FILE_BROAD}")


if __name__ == "__main__":
    main()
