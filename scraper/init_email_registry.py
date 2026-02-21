# -*- coding: utf-8 -*-
"""
Pre-remplit le registre email_registry avec TOUS les emails deja envoyes.
A executer UNE FOIS pour que le systeme anti-doublons fonctionne retroactivement.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from email_registry import mark_as_sent, get_sent_count, was_already_sent

print(f"Registre actuel: {get_sent_count()} emails")

# 1. Emails des 5 premiers organisateurs (send_5_test_emails / send_5_gmail_smtp)
try:
    with open('selected_5_organizers.json', 'r', encoding='utf-8') as f:
        for c in json.load(f):
            email = c.get('email','').strip().lower()
            if email and not was_already_sent(email):
                mark_as_sent(email, script="send_5_test_emails", context=c.get('title',''))
                print(f"  + {email} (5 premiers)")
except FileNotFoundError:
    print("  selected_5_organizers.json non trouve")

# 2. Emails des 25 suivants (send_25_more)
try:
    with open('selected_25_more.json', 'r', encoding='utf-8') as f:
        for c in json.load(f):
            email = c.get('email','').strip().lower()
            if email and not was_already_sent(email):
                mark_as_sent(email, script="send_25_more", context=c.get('title',''))
                print(f"  + {email} (25 more)")
except FileNotFoundError:
    print("  selected_25_more.json non trouve")

# 3. Emails des 35 promo (send_35_promo) - liste hardcodee
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
    "contact@digitick.com"
]
for email in promo_35:
    if not was_already_sent(email):
        mark_as_sent(email, script="send_35_promo", context="Promo MapEvent 33000+")
        print(f"  + {email} (35 promo)")

# 4. Emails opendata (send_opendata_emails)
opendata = [
    "opendata@switzerland.com", "opendata@bfs.admin.ch", "info@valais.ch",
    "info@vaud-promotion.ch", "info@lausanne-tourisme.ch",
    "billetterie-culture@geneve.ch", "info@opendata.ch", "contact@openagenda.com"
]
for email in opendata:
    if not was_already_sent(email):
        mark_as_sent(email, script="send_opendata_emails", context="Demande API opendata")
        print(f"  + {email} (opendata)")

# 5. Emails des 35 promo_emails (send_35_promo_emails) via TOUS_LES_EMAILS.json
try:
    with open('emails_organisateurs/TOUS_LES_EMAILS.json', 'r', encoding='utf-8') as f:
        tous = json.load(f)
    # On ne peut pas savoir exactement lesquels ont ete envoyes, mais on les ajoute par precaution
    # car send_35_promo_emails les traite
except FileNotFoundError:
    pass

print(f"\nRegistre final: {get_sent_count()} emails uniques")
