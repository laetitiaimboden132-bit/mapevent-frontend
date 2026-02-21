"""
Nettoyer et consolider TOUS les emails (Valais + Vaud)
Supprimer les emails malformés et doublons
"""
import sys, io, re, csv

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

def clean_email(raw):
    """Nettoyer un email malformé"""
    raw = raw.strip()
    if not raw or '@' not in raw:
        return None
    
    # Trouver le vrai email dans le texte
    # Pattern: extraire juste la partie email
    m = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', raw)
    if m:
        email = m.group(1).lower()
        # Vérifier que c'est valide
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            # Filtrer les emails système
            if not any(x in email for x in ['noreply', 'no-reply', 'example.com', 'test.com', 'sentry.io']):
                return email
    return None

# Lire Valais emails
valais_emails = {}
try:
    with open('emails_organisateurs/emails.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:
                raw_email = row[0]
                title = row[1] if len(row) > 1 else ''
                url = row[2] if len(row) > 2 else ''
                
                clean = clean_email(raw_email)
                if clean and clean not in valais_emails:
                    valais_emails[clean] = {'title': title, 'url': url, 'source': 'Valais'}
except Exception as ex:
    print(f"Erreur lecture emails Valais: {ex}")

print(f"Emails Valais propres: {len(valais_emails)}")

# Lire Vaud emails V3
vaud_emails = {}
try:
    with open('emails_organisateurs/emails_Vaud_v3.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:
                title = row[0]
                raw_email = row[1]
                url = row[2] if len(row) > 2 else ''
                
                clean = clean_email(raw_email)
                if clean and clean not in vaud_emails:
                    vaud_emails[clean] = {'title': title, 'url': url, 'source': 'Vaud'}
except Exception as ex:
    print(f"Erreur lecture emails Vaud V3: {ex}")

print(f"Emails Vaud propres: {len(vaud_emails)}")

# Lire les anciens Vaud emails aussi
try:
    with open('emails_organisateurs/emails_Vaud.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:
                title = row[0]
                raw_email = row[1]
                url = row[2] if len(row) > 2 else ''
                
                clean = clean_email(raw_email)
                if clean and clean not in vaud_emails:
                    vaud_emails[clean] = {'title': title, 'url': url, 'source': 'Vaud'}
except Exception as ex:
    pass

try:
    with open('emails_organisateurs/emails_Vaud_real.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:
                title = row[0]
                raw_email = row[1]
                url = row[2] if len(row) > 2 else ''
                
                clean = clean_email(raw_email)
                if clean and clean not in vaud_emails:
                    vaud_emails[clean] = {'title': title, 'url': url, 'source': 'Vaud'}
except Exception as ex:
    pass

print(f"Emails Vaud total propres: {len(vaud_emails)}")

# Consolider
all_emails = {}
for email, info in valais_emails.items():
    all_emails[email] = info
for email, info in vaud_emails.items():
    if email not in all_emails:
        all_emails[email] = info

print(f"\nTOTAL emails uniques propres: {len(all_emails)}")

# Sauvegarder le fichier consolidé
with open('emails_organisateurs/TOUS_EMAILS_PROPRES.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['email', 'event_title', 'source_url', 'canton'])
    for email, info in sorted(all_emails.items()):
        writer.writerow([email, info['title'], info['url'], info['source']])

print(f"Sauvegardé dans emails_organisateurs/TOUS_EMAILS_PROPRES.csv")

# Afficher la liste
print(f"\n=== TOUS LES EMAILS ({len(all_emails)}) ===")
for i, (email, info) in enumerate(sorted(all_emails.items()), 1):
    print(f"  {i:3d}. {email:<45} | {info['source']:6} | {info['title'][:40]}")
