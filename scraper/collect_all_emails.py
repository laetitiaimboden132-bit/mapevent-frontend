"""
Collecter tous les emails organisateurs depuis les fichiers scrapés.
"""
import json, sys, io, os

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

all_emails = {}

# Fichier tempslibre
for fname in ['scraped_tempslibre_v2.json', 'scraped_hautesavoie.json', 'organizer_emails_new.json']:
    if os.path.exists(fname):
        with open(fname, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    email = item.get('organizer_email', '')
                    title = item.get('title', '')
                    if email and '@' in email:
                        all_emails[email] = title
                elif isinstance(item, (list, tuple)) and len(item) >= 2:
                    title, email = item[0], item[1]
                    if email and '@' in email:
                        all_emails[email] = title
        
        print(f"{fname}: trouvé {sum(1 for v in all_emails.values() if v)} emails")

# Sauvegarder
output = [{'email': email, 'event': title} for email, title in all_emails.items()]
with open('all_organizer_emails.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nTOTAL EMAILS UNIQUES: {len(output)}")
for item in output[:10]:
    print(f"  {item['email']}: {item['event'][:40]}")
if len(output) > 10:
    print(f"  ... et {len(output) - 10} autres")

print(f"\nSauvegardé dans all_organizer_emails.json")
