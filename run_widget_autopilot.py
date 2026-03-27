import json
import re
import smtplib
from datetime import datetime, UTC
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


MANUAL_SENT_EMAILS = {
    "contact@rochefort-ocean.com",
    "accueil@antibesjuanlespins.com",
    "mairie.toulouse-evenementiel@mairie-toulouse.fr",
    "accueil@toulouse-metropole.fr",
}


def slugify_city(name: str) -> str:
    mapping = {
        "Antibes / Juan-les-Pins": "antibes",
        "Yverdon-les-Bains": "yverdon",
        "Geneve": "geneve",
    }
    return mapping.get(name, name.lower().replace(" ", "-").replace("'", ""))


def infer_lang_from_slug_or_email(slug: str, email: str) -> str:
    german_slugs = {
        "zurich",
        "basel",
        "berne",
        "luzern",
        "winterthur",
        "aarau",
        "schaffhausen",
        "thun",
        "zug",
        "st-gallen",
        "berlin",
    }
    english_slugs = {"helsinki"}
    dutch_slugs = {"gent", "antwerpen"}
    if slug in german_slugs:
        return "de"
    if slug in english_slugs:
        return "en"
    if slug in dutch_slugs:
        return "nl"
    if email.endswith(".de") or email.endswith(".at"):
        return "de"
    return "fr"


def load_contacts_by_slug() -> dict[str, dict]:
    contacts: dict[str, dict] = {}

    # Main campaign recipients (cities only, no media)
    campaign = Path("send_widget_campaign.py").read_text(encoding="utf-8")
    blocks = re.findall(r"\{[^{}]+\}", campaign)
    for block in blocks:
        if '"media": True' in block:
            continue
        to_m = re.search(r'"to":\s*"([^"]+)"', block)
        city_m = re.search(r'"city":\s*"([^"]+)"', block)
        slug_m = re.search(r'"slug":\s*"([^"]+)"', block)
        lang_m = re.search(r'"lang":\s*"([^"]+)"', block)
        if not (to_m and city_m and slug_m):
            continue
        email = to_m.group(1).strip().lower()
        city = city_m.group(1).strip()
        slug = slug_m.group(1).strip()
        lang = (lang_m.group(1).strip() if lang_m else infer_lang_from_slug_or_email(slug, email))
        contacts[slug] = {"email": email, "city": city, "lang": lang}

    # Extra contacts file (new cities)
    extra = json.loads(Path("tourism_offices_contact_emails.json").read_text(encoding="utf-8"))
    for row in extra:
        email = (row.get("email") or "").strip().lower()
        city = (row.get("city") or "").strip()
        if email and city:
            slug = slugify_city(city)
            contacts[slug] = {
                "email": email,
                "city": city,
                "lang": infer_lang_from_slug_or_email(slug, email),
            }

    return contacts


def load_sent_emails() -> set[str]:
    sent = set(MANUAL_SENT_EMAILS)
    for file_name in ["widget_municipal_log.json", "widget_premium_log.json"]:
        p = Path(file_name)
        if not p.exists():
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        for row in data:
            if row.get("status") == "sent" and row.get("to"):
                sent.add(row["to"].strip().lower())

    # Prior campaign file = already contacted list.
    campaign_text = Path("send_widget_campaign.py").read_text(encoding="utf-8")
    for email in re.findall(r'"to":\s*"([^"]+)"', campaign_text):
        sent.add(email.strip().lower())

    return sent


def build_mail(city: str, slug: str, events: int, demo_url: str, lang: str):
    if lang == "de":
        subject = f"Verbesserung Kategorien und Themes - MapEvent Widget ({city})"
        line = "Gern passen wir diese Demo an Ihre Anforderungen an."
        text = (
            f"Zeigen Sie Veranstaltungen in {city} auf Ihrer Stadtseite.\n"
            "Kostenlos.\n\n"
            f"Demo {city}: {demo_url}\n"
            "Dark / Light / Natural direkt im Widget umschaltbar.\n\n"
            f"Aktuell sichtbare Events in {city}: {events}\n\n"
            f"{line}\n\n"
            "Freundliche Gruesse,\nMapEvent\nhttps://mapevent.world\n"
        )
        title = f"Veranstaltungen in {city} auf Ihrer Webseite anzeigen."
        cta = "Widget live ansehen"
    elif lang == "en":
        subject = f"Category and theme improvements - MapEvent Widget ({city})"
        line = "We can adapt this demo to your exact needs."
        text = (
            f"Show events in {city} on your city website.\n"
            "For free.\n\n"
            f"Demo {city}: {demo_url}\n"
            "Dark / Light / Natural switch directly inside the widget.\n\n"
            f"Currently visible events in {city}: {events}\n\n"
            f"{line}\n\n"
            "Best regards,\nMapEvent\nhttps://mapevent.world\n"
        )
        title = f"Show {city} events on your website."
        cta = "Open live widget"
    elif lang == "nl":
        subject = f"Verbetering categorieen en thema's - MapEvent Widget ({city})"
        line = "We passen deze demo graag aan uw noden aan."
        text = (
            f"Toon evenementen in {city} op uw stadswebsite.\n"
            "Gratis.\n\n"
            f"Demo {city}: {demo_url}\n"
            "Dark / Light / Natural direct in de widget.\n\n"
            f"Huidig zichtbare events in {city}: {events}\n\n"
            f"{line}\n\n"
            "Met vriendelijke groet,\nMapEvent\nhttps://mapevent.world\n"
        )
        title = f"Toon evenementen in {city} op uw website."
        cta = "Open live widget"
    else:
        subject = f"amélioration catégories et thèmes Map Event World - {city}"
        line = (
            "Nous restons à votre écoute pour adapter cette démo à vos besoins, "
            "avec par exemple un tri par catégories directement dans le widget."
        )
        text = (
            f"Affichez les événements de {city} sur le site de la ville de {city}.\n"
            "Gratuitement.\n\n"
            f"Démo {city}: {demo_url}\n"
            "Dark / Light / Naturel modifiables directement dans le widget.\n\n"
            "Tout est inclus gratuitement:\n"
            "- Carte interactive avec clusters\n"
            "- Pointeurs catégories\n"
            "- Adresse et description complètes\n"
            "- Sélecteur de thème intégré\n\n"
            f"Nous avons actuellement {events} événements visibles pour {city}.\n\n"
            f"{line}\n\n"
            "Cordialement,\n"
            "MapEvent - La carte mondiale des événements\n"
            "https://mapevent.world\n"
            "Facebook: https://www.facebook.com/profile.php?id=61575803734811\n"
            "mapeventworld@gmail.com\n"
        )
        title = f"Affichez les événements de {city} sur le site de la ville de {city}."
        cta = "Ouvrir le widget (thèmes live)"

    html = f"""<!doctype html><html><body style="font-family:Segoe UI,Arial,sans-serif;background:#0f172a;color:#e2e8f0;padding:20px;">
<div style="max-width:640px;margin:0 auto;background:#1e293b;border:1px solid #334155;border-radius:12px;padding:22px;">
<h2 style="margin:0 0 10px;color:#f1f5f9;">{title}</h2>
<p><a href="{demo_url}" style="color:#22d3ee;">{cta}</a></p>
<p style="color:#cbd5e1;">{line}</p>
<hr style="border-color:#334155;">
<p style="font-size:12px;color:#94a3b8;">MapEvent<br>
<a href="https://mapevent.world" style="color:#22d3ee;">https://mapevent.world</a><br>
<a href="mailto:mapeventworld@gmail.com" style="color:#22d3ee;">mapeventworld@gmail.com</a></p>
</div></body></html>"""
    return subject, text, html


def send_email(server, user: str, to_addr: str, subject: str, text: str, html: str):
    msg = MIMEMultipart("alternative")
    msg["From"] = f"MapEvent <{user}>"
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg["Reply-To"] = user
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    server.sendmail(user, [to_addr], msg.as_string())


def main():
    send_mode = "--send" in __import__("sys").argv
    report = json.loads(Path("widget_send_eligibility_report.json").read_text(encoding="utf-8"))
    contacts = load_contacts_by_slug()
    sent_emails = load_sent_emails()

    unsent_eligible = []
    for row in report["eligible"]:
        slug = row["slug"]
        contact = contacts.get(slug)
        if not contact:
            continue
        email = contact.get("email", "")
        if not email or email in sent_emails:
            continue
        unsent_eligible.append(
            {
                "slug": slug,
                "email": email,
                "city": contact.get("city", slug.replace("-", " ").title()),
                "lang": contact.get("lang", infer_lang_from_slug_or_email(slug, email)),
                "events": row["events"],
                "required_events": row["required_events"],
                "coverage_ratio_vs_threshold": row["coverage_ratio_vs_threshold"],
            }
        )

    # Enrichment priority: near threshold (>= 80% of required), with a known contact.
    enrich_queue = []
    for row in report["below_threshold"]:
        slug = row["slug"]
        contact = contacts.get(slug)
        if not contact:
            continue
        email = contact.get("email", "")
        ratio = row["coverage_ratio_vs_threshold"]
        if ratio >= 0.8:
            missing = max(row["required_events"] - row["events"], 0)
            enrich_queue.append(
                {
                    "slug": slug,
                    "email": email,
                    "lang": contact.get("lang", infer_lang_from_slug_or_email(slug, email)),
                    "events": row["events"],
                    "required_events": row["required_events"],
                    "missing_events_to_send": missing,
                    "coverage_ratio_vs_threshold": ratio,
                }
            )

    enrich_queue.sort(key=lambda x: x["missing_events_to_send"])

    sent_now = []
    if send_mode and unsent_eligible:
        user = "mapeventworld@gmail.com"
        app_password = "oxta novu unxj jizx".replace(" ", "")
        run_tag = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user, app_password)
            for row in unsent_eligible:
                slug = row["slug"]
                city = row.get("city", slug.replace("-", " ").title())
                lang = row.get("lang", "fr")
                demo_url = f"https://mapevent.world/widget-promo.html?city={slug}&_v={run_tag}"
                s1, t1, h1 = build_mail(city, slug, row["events"], demo_url, lang)
                send_email(server, user, row["email"], s1, t1, h1)
                sent_now.append(
                    {"slug": slug, "email": row["email"], "lang": lang, "subject": s1}
                )

    status = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "send_mode": send_mode,
        "policy_threshold_per_100k": report["policy"]["threshold_per_100k"],
        "unsent_eligible_count": len(unsent_eligible),
        "unsent_eligible": unsent_eligible,
        "enrichment_priority_count": len(enrich_queue),
        "enrichment_priority": enrich_queue,
        "sent_now_count": len(sent_now),
        "sent_now": sent_now,
    }
    Path("widget_autopilot_status.json").write_text(
        json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("UNSENT_ELIGIBLE", len(unsent_eligible))
    print("ENRICHMENT_QUEUE", len(enrich_queue))
    print("SENT_NOW", len(sent_now))
    print("STATUS_FILE", "widget_autopilot_status.json")
    if enrich_queue:
        top = enrich_queue[:5]
        for row in top:
            print(
                f"ENRICH_TOP | {row['slug']} | missing={row['missing_events_to_send']} | ratio={row['coverage_ratio_vs_threshold']}"
            )


if __name__ == "__main__":
    main()
