import csv
import json
import re
from pathlib import Path


INPUT_CSV = Path("scraper/emails_organisateurs/TOUS_EMAILS_FINAL.csv")
OUTPUT_CLEAN = Path("scraper/emails_organisateurs/TOUS_EMAILS_FINAL_CLEAN_MAX.csv")
OUTPUT_REVIEW = Path("scraper/emails_organisateurs/TOUS_EMAILS_REVIEW.csv")
OUTPUT_SUMMARY = Path("scraper/emails_organisateurs/TOUS_EMAILS_CLEAN_SUMMARY.json")

EMAIL_RX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
DIGITS_STREAK_RX = re.compile(r"\d{5,}")
LOCAL_ALLOWED_RX = re.compile(r"^[A-Za-z0-9._%+-]+$")
TOKEN_HINTS = [
    "info",
    "contact",
    "billetterie",
    "reservation",
    "culture",
    "festival",
    "admin",
    "shop",
    "hello",
    "events",
]


def choose_local_candidate(local: str) -> tuple[str, str]:
    local = local.strip().lower()
    candidates = [local]

    # Keep segments from known hint tokens (often present in valid local-part).
    for token in TOKEN_HINTS:
        i = local.rfind(token)
        if i > 0:
            candidates.append(local[i:])

    # Remove numeric prefixes if present.
    candidates.append(re.sub(r"^\d+", "", local))

    scored: list[tuple[int, str]] = []
    for cand in candidates:
        cand = cand.strip(".-_")
        if not cand:
            continue
        if not LOCAL_ALLOWED_RX.match(cand):
            continue
        score = 0
        if 3 <= len(cand) <= 32:
            score += 5
        if "." in cand:
            score += 2
        if "www" not in cand:
            score += 2
        if not DIGITS_STREAK_RX.search(cand):
            score += 2
        # Prefer candidate that starts with a letter.
        if cand[0].isalpha():
            score += 2
        scored.append((score, cand))

    if not scored:
        return local, "unfixed"
    best = sorted(scored, key=lambda x: (-x[0], len(x[1])))[0][1]
    if best != local:
        return best, "fixed"
    return best, "unchanged"


def normalize_email(raw_email: str) -> tuple[str, str]:
    raw = (raw_email or "").strip().lower()
    raw = raw.replace(" ", "")
    if "@" not in raw:
        return raw, "invalid_no_at"
    if raw.count("@") > 1:
        # Keep only last mailbox part after last @ as salvage.
        raw = raw.split("@", 1)[0] + "@" + raw.rsplit("@", 1)[1]

    local, domain = raw.split("@", 1)
    domain = domain.strip(".")
    local2, state = choose_local_candidate(local)
    normalized = f"{local2}@{domain}"

    if not EMAIL_RX.match(normalized):
        return normalized, "invalid_format"

    suspicious = False
    if len(local2) > 32:
        suspicious = True
    if DIGITS_STREAK_RX.search(local2):
        suspicious = True
    if local2.startswith("www") or "www." in local2:
        suspicious = True

    if suspicious:
        return normalized, "suspicious"
    return normalized, state


def main():
    rows = list(csv.DictReader(INPUT_CSV.read_text(encoding="utf-8").splitlines()))
    clean_rows = []
    review_rows = []
    seen = set()

    counters = {
        "input_rows": len(rows),
        "clean_kept": 0,
        "review_rows": 0,
        "fixed": 0,
        "invalid_no_at": 0,
        "invalid_format": 0,
        "suspicious": 0,
        "duplicates_removed": 0,
    }

    for r in rows:
        email_raw = (r.get("email") or "").strip()
        email_norm, status = normalize_email(email_raw)
        row = {
            "email": email_norm,
            "event_title": (r.get("event_title") or "").strip(),
            "source_url": (r.get("source_url") or "").strip(),
            "canton": (r.get("canton") or "").strip(),
            "original_email": email_raw,
            "status": status,
        }

        if status == "fixed":
            counters["fixed"] += 1
        if status in {"invalid_no_at", "invalid_format", "suspicious"}:
            counters[status] += 1
            review_rows.append(row)
            continue

        if email_norm in seen:
            counters["duplicates_removed"] += 1
            continue
        seen.add(email_norm)
        clean_rows.append(row)

    counters["clean_kept"] = len(clean_rows)
    counters["review_rows"] = len(review_rows)

    # Write clean file with standard columns for campaign scripts.
    with OUTPUT_CLEAN.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["email", "event_title", "source_url", "canton"])
        w.writeheader()
        for r in clean_rows:
            w.writerow(
                {
                    "email": r["email"],
                    "event_title": r["event_title"],
                    "source_url": r["source_url"],
                    "canton": r["canton"],
                }
            )

    with OUTPUT_REVIEW.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "original_email",
                "email",
                "status",
                "event_title",
                "source_url",
                "canton",
            ],
        )
        w.writeheader()
        for r in review_rows:
            w.writerow(
                {
                    "original_email": r["original_email"],
                    "email": r["email"],
                    "status": r["status"],
                    "event_title": r["event_title"],
                    "source_url": r["source_url"],
                    "canton": r["canton"],
                }
            )

    OUTPUT_SUMMARY.write_text(json.dumps(counters, indent=2, ensure_ascii=False), encoding="utf-8")

    print("CLEAN_KEPT", counters["clean_kept"])
    print("REVIEW_ROWS", counters["review_rows"])
    print("FIXED", counters["fixed"])
    print("DUPLICATES_REMOVED", counters["duplicates_removed"])
    print("OUT_CLEAN", OUTPUT_CLEAN)
    print("OUT_REVIEW", OUTPUT_REVIEW)
    print("OUT_SUMMARY", OUTPUT_SUMMARY)


if __name__ == "__main__":
    main()
