# -*- coding: utf-8 -*-
"""
Initialise le registre email avec TOUS les emails déjà envoyés.
Scanne les fichiers JSON de candidats + la liste hardcodée de send_35_promo.py
pour pré-remplir promo_emails_sent.json et éviter tout futur doublon.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from email_registry import mark_as_sent, get_sent_count, was_already_sent

print(f"Registre actuel: {get_sent_count()} emails")

# 1. Les 5 premiers organizers (send_5_test_emails + send_5_gmail_smtp)
try:
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, 'selected_5_organizers.json'), 'r', encoding='utf-8') as f:
        for c in json.load(f):
            email = c.get('email', '').strip().lower()
            if email and not was_already_sent(email):
                mark_as_sent(email, script="send_5_init", context=c.get('title', ''))
                print(f"  + {email} (5 organizers)")
except FileNotFoundError:
    print("  selected_5_organizers.json non trouve")

# 2. Les 25 suivants (send_25_more)
try:
    with open(os.path.join(base, 'selected_25_more.json'), 'r', encoding='utf-8') as f:
        for c in json.load(f):
            email = c.get('email', '').strip().lower()
            if email and not was_already_sent(email):
                mark_as_sent(email, script="send_25_init", context=c.get('title', ''))
                print(f"  + {email} (25 more)")
except FileNotFoundError:
    print("  selected_25_more.json non trouve")

# 3. Les 35 promos (send_35_promo.py - liste hardcodée)
promo_35 = [
    "info@montreux-riviera.com", "info@fribourgtourisme.ch", "info@neuchateltourisme.ch",
    "info@juratourisme.ch", "info@biel-bienne.ch", "info@interlaken.ch",
    "info@ticino.ch", "info@luzern.com", "info@zuerich.com", "info@basel.com",
    "info@lyon-france.com", "info@bordeaux-tourisme.com", "info@nantes-tourisme.com",
    "info@toulouse-tourisme.com", "info@marseille-tourisme.com", "info@nice-tourisme.com",
    "info@strasbourg.eu", "contact@lilleattractions.com", "info@montpellier-tourisme.fr",
    "info@rennes-tourisme.com", "info@visitberlin.de", "info@visithelsinki.fi",
    "info@esmadrid.com", "info@mtl.org", "info@nycgo.com",
    "contact@openagenda.com", "info@eventbrite.fr", "hello@shotgun.live",
    "contact@mapstr.com", "hello@billetweb.fr", "info@sortiraparis.com",
    "redaction@leprogres.fr", "contact@timeout.fr", "info@infoconcert.com",
    "contact@digitick.com",
]
for email in promo_35:
    if not was_already_sent(email):
        mark_as_sent(email, script="send_35_promo_init", context="promo 35")
        print(f"  + {email} (35 promo)")

# 4. Les opendata emails
opendata = [
    "opendata@switzerland.com", "opendata@bfs.admin.ch", "info@valais.ch",
    "info@vaud-promotion.ch", "info@lausanne-tourisme.ch",
    "billetterie-culture@geneve.ch", "info@opendata.ch", "contact@openagenda.com",
]
for email in opendata:
    if not was_already_sent(email):
        mark_as_sent(email, script="send_opendata_init", context="opendata request")
        print(f"  + {email} (opendata)")

# 5. Les 35 promo_emails (send_35_promo_emails.py) - via TOUS_LES_EMAILS.json
try:
    tous_path = os.path.join(base, 'emails_organisateurs', 'TOUS_LES_EMAILS.json')
    if not os.path.exists(tous_path):
        tous_path = os.path.join(base, '..', 'emails_organisateurs', 'TOUS_LES_EMAILS.json')
    with open(tous_path, 'r', encoding='utf-8') as f:
        tous = json.load(f)
    # On ne sait pas exactement lesquels ont été envoyés, mais on marque les 35 premiers
    # qui ont un email valide (c'est le TARGET_COUNT du script)
    count = 0
    for entry in tous:
        email = (entry.get('email') or '').strip().lower()
        if email and '@' in email and not was_already_sent(email):
            mark_as_sent(email, script="send_35_promo_emails_init", context=entry.get('source_url', ''))
            print(f"  + {email} (35 promo emails)")
            count += 1
            if count >= 35:
                break
except FileNotFoundError:
    print("  TOUS_LES_EMAILS.json non trouve")

print(f"\nRegistre final: {get_sent_count()} emails uniques")
print("Anti-doublons pret!")
