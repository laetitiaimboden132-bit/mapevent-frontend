"""
Consolider TOUS les emails: Valais + Vaud + Genève
"""
import csv, sys, io, re, os

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

def clean_email(raw):
    raw = raw.strip().lower()
    if '@' not in raw or len(raw) < 5:
        return None
    
    # Extraire l'email valide
    m = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', raw)
    if not m:
        return None
    
    email = m.group(1).lower()
    
    # Filtrer
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return None
    if any(x in email for x in ['noreply', 'no-reply', 'example.com', 'test.com', 'sentry',
                                  'wixpress', 'googleapis', '.png', '.jpg', 'bootstrap',
                                  'wordpress', 'script', 'jquery', 'cookie']):
        return None
    
    return email

# Lire tous les fichiers CSV d'emails
email_files = [
    'emails_organisateurs/emails.csv',
    'emails_organisateurs/emails_Vaud.csv',
    'emails_organisateurs/emails_Vaud_real.csv',
    'emails_organisateurs/emails_Vaud_v2.csv',
    'emails_organisateurs/emails_Vaud_v3.csv',
    'emails_organisateurs/emails_Geneve.csv',
    'emails_organisateurs/emails_Geneve_v2.csv',
    'emails_organisateurs/TOUS_EMAILS_FINAL.csv',
]

all_emails = {}  # email -> {event, source, region}

for filepath in email_files:
    if not os.path.exists(filepath):
        continue
    
    region = 'Valais'
    if 'Vaud' in filepath:
        region = 'Vaud'
    elif 'Geneve' in filepath or 'Genève' in filepath:
        region = 'Genève'
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)  # Skip header
            
            for row in reader:
                if not row:
                    continue
                raw_email = row[0] if len(row) > 0 else ''
                event = row[1] if len(row) > 1 else ''
                source = row[2] if len(row) > 2 else filepath
                
                email = clean_email(raw_email)
                if email and email not in all_emails:
                    all_emails[email] = {
                        'event': event,
                        'source': source,
                        'region': region
                    }
        
        found = sum(1 for e in all_emails.values() if e['region'] == region)
        print(f"  {filepath}: {found} unique emails ({region})")
    except Exception as ex:
        print(f"  {filepath}: ERREUR - {str(ex)[:50]}")

print(f"\nTOTAL EMAILS UNIQUES: {len(all_emails)}")

# Compter par région
by_region = {}
for email, info in all_emails.items():
    r = info['region']
    by_region[r] = by_region.get(r, 0) + 1

for r, cnt in sorted(by_region.items()):
    print(f"  {r}: {cnt}")

# Sauvegarder le fichier final consolidé
output = 'emails_organisateurs/TOUS_EMAILS_COMPLET.csv'
with open(output, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['email', 'event', 'source', 'region'])
    for email, info in sorted(all_emails.items()):
        writer.writerow([email, info['event'], info['source'], info['region']])

print(f"\nSauvegardé dans {output}")
