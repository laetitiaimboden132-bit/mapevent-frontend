import json
import math
from pathlib import Path


# Baseline populations used by the policy (city proper).
PARIS_POPULATION = 2_102_650
GENEVE_POPULATION = 203_856


# Population table used for campaign qualification.
# Priority: internal campaign values when available, then stable estimates.
POPULATION_BY_SLUG = {
    "paris": PARIS_POPULATION,
    "geneve": GENEVE_POPULATION,
    "toulouse": 504_078,
    "marseille": 873_076,
    "lyon": 522_250,
    "bordeaux": 265_328,
    "nantes": 323_204,
    "strasbourg": 290_576,
    "lille": 236_710,
    "montpellier": 302_454,
    "rennes": 225_081,
    "rouen": 116_641,
    "nice": 348_085,
    "perpignan": 119_656,
    "grenoble": 157_650,
    "annecy": 130_721,
    "metz": 120_874,
    "dijon": 160_000,
    "reims": 183_000,
    "tours": 136_000,
    "toulon": 180_000,
    "clermont-ferrand": 148_000,
    "cannes": 75_000,
    "ajaccio": 72_000,
    "bayonne": 52_000,
    "antibes": 75_000,
    "niort": 59_000,
    "cherbourg": 79_000,
    "rochefort": 24_000,
    "biarritz": 26_000,
    "beziers": 78_000,
    "sete": 44_000,
    "narbonne": 56_000,
    "vannes": 54_000,
    "lorient": 57_000,
    "hyeres": 56_000,
    "senlis": 16_000,
    "auxerre": 35_000,
    "troyes": 61_000,
    "chalon-sur-saone": 45_000,
    "macon": 34_000,
    "bourges": 64_000,
    "saint-malo": 46_000,
    "colmar": 70_000,
    "lausanne": 141_418,
    "nyon": 23_000,
    "morges": 17_000,
    "yverdon": 30_000,
    "neuchatel": 45_000,
    "fribourg": 38_000,
    "basel": 175_000,
    "berlin": 3_700_000,
    "helsinki": 684_000,
    "biel": 55_000,
}


def load_events_by_slug(widget_data_dir: Path) -> dict[str, int]:
    result: dict[str, int] = {}
    for file_path in sorted(widget_data_dir.glob("*.json")):
        data = json.loads(file_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            count = len(data)
        else:
            count = len(data.get("events", []))
        result[file_path.stem] = count
    return result


def main():
    base_dir = Path(__file__).resolve().parent
    widget_data_dir = base_dir / "public" / "widget-data"
    events_by_slug = load_events_by_slug(widget_data_dir)

    paris_events = events_by_slug["paris"]
    geneve_events = events_by_slug["geneve"]

    paris_rate = paris_events / PARIS_POPULATION
    geneve_rate = geneve_events / GENEVE_POPULATION
    base_rate = min(paris_rate, geneve_rate)
    min_send_rate = base_rate * 0.8  # Allowed: up to 20% lower than Paris/Geneve prorata.

    eligible = []
    below_threshold = []
    missing_population = []

    for slug, events in sorted(events_by_slug.items()):
        population = POPULATION_BY_SLUG.get(slug)
        if not population:
            missing_population.append(
                {"slug": slug, "events": events, "status": "missing_population"}
            )
            continue

        required_events = math.ceil(population * min_send_rate)
        ratio = events / required_events if required_events else 0.0
        row = {
            "slug": slug,
            "events": events,
            "population": population,
            "required_events": required_events,
            "coverage_ratio_vs_threshold": round(ratio, 3),
        }

        if events >= required_events:
            row["status"] = "eligible"
            eligible.append(row)
        else:
            row["status"] = "below_threshold"
            below_threshold.append(row)

    report = {
        "policy": {
            "reference_cities": ["paris", "geneve"],
            "paris_events": paris_events,
            "geneve_events": geneve_events,
            "paris_population": PARIS_POPULATION,
            "geneve_population": GENEVE_POPULATION,
            "paris_rate": round(paris_rate, 8),
            "geneve_rate": round(geneve_rate, 8),
            "base_rate_min_of_paris_geneve": round(base_rate, 8),
            "min_send_rate_after_20pct_tolerance": round(min_send_rate, 8),
            "threshold_per_100k": round(min_send_rate * 100_000, 1),
        },
        "summary": {
            "total_widget_cities": len(events_by_slug),
            "eligible_count": len(eligible),
            "below_threshold_count": len(below_threshold),
            "missing_population_count": len(missing_population),
        },
        "eligible": sorted(eligible, key=lambda x: x["coverage_ratio_vs_threshold"], reverse=True),
        "below_threshold": sorted(
            below_threshold, key=lambda x: x["coverage_ratio_vs_threshold"]
        ),
        "missing_population": sorted(missing_population, key=lambda x: x["events"], reverse=True),
    }

    out_path = base_dir / "widget_send_eligibility_report.json"
    out_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("POLICY_THRESHOLD_PER_100K", report["policy"]["threshold_per_100k"])
    print("TOTAL", report["summary"]["total_widget_cities"])
    print("ELIGIBLE", report["summary"]["eligible_count"])
    print("BELOW", report["summary"]["below_threshold_count"])
    print("MISSING_POP", report["summary"]["missing_population_count"])
    print("REPORT", out_path)


if __name__ == "__main__":
    main()
