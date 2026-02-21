"""
Nettoyage V2 - correction des emails malformés
Problèmes:
1. Préfixes numériques: 28info@, 33info@, etc.
2. URLs collées: www.site.chbilletterie@, morges-sous-rire.chinfo@
3. Suffixes invalides: @nendaz.chcontactinformations
4. Ville + email: cransinfo@, payernecontact@, montreuxinfo@
"""
import sys, io, re, csv

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

def deep_clean_email(raw):
    """Nettoyage en profondeur d'un email"""
    raw = raw.strip().lower()
    if '@' not in raw:
        return None
    
    local, domain = raw.rsplit('@', 1)
    
    # 1. Nettoyer le domaine - supprimer tout après le TLD
    # ex: "nendaz.chcontactinformations" -> "nendaz.ch"
    # ex: "nendaz.chr" -> "nendaz.ch" (si r est un suffixe parasite)
    domain_clean = re.match(r'([a-zA-Z0-9.-]+\.(ch|com|org|net|world|fr|de|it))', domain)
    if not domain_clean:
        return None
    domain = domain_clean.group(1)
    
    # 2. Nettoyer le local part
    # Supprimer les préfixes numériques: "28info" -> "info"
    local = re.sub(r'^\d+', '', local)
    
    # Supprimer les URLs collées avant: "www.site.chbilletterie" -> "billetterie"
    if '.ch' in local or '.com' in local:
        # Trouver la dernière partie après .ch ou .com
        parts = re.split(r'\.(?:ch|com|org)', local)
        if len(parts) > 1:
            local = parts[-1]
    
    # Supprimer "www." au début
    local = re.sub(r'^www\..*\.', '', local)
    
    # Supprimer les noms de villes collés avant des mots clés
    city_prefixes = [
        'lausanne', 'montreux', 'nyon', 'morges', 'vevey', 'aigle',
        'payerne', 'crans', 'villars-sur-ollon', 'monthey',
        'morges-sous-rire', 'saint-legier'
    ]
    for city in city_prefixes:
        if local.startswith(city) and len(local) > len(city):
            rest = local[len(city):]
            if rest and rest[0].isalpha():
                local = rest
                break
    
    if not local or not domain:
        return None
    
    email = f"{local}@{domain}"
    
    # Validation finale
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return None
    
    # Filtrer les emails système
    if any(x in email for x in ['noreply', 'no-reply', 'example.com', 'sentry.io']):
        return None
    
    return email

# Lire le fichier consolidé
all_cleaned = {}
corrections = []

with open('emails_organisateurs/TOUS_EMAILS_PROPRES.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if len(row) < 4:
            continue
        raw_email = row[0]
        title = row[1]
        url = row[2]
        canton = row[3]
        
        clean = deep_clean_email(raw_email)
        if clean:
            if clean != raw_email:
                corrections.append((raw_email, clean))
            if clean not in all_cleaned:
                all_cleaned[clean] = {'title': title, 'url': url, 'canton': canton}
        else:
            corrections.append((raw_email, 'SUPPRIMÉ'))

print(f"CORRECTIONS:")
for old, new in corrections:
    print(f"  {old:<55} -> {new}")

print(f"\nEmails propres: {len(all_cleaned)}")

# Sauvegarder
with open('emails_organisateurs/TOUS_EMAILS_FINAL.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['email', 'event_title', 'source_url', 'canton'])
    for email, info in sorted(all_cleaned.items()):
        writer.writerow([email, info['title'], info['url'], info['canton']])

print(f"\nSauvegardé dans emails_organisateurs/TOUS_EMAILS_FINAL.csv")

# Résumé
valais_count = sum(1 for v in all_cleaned.values() if v['canton'] == 'Valais')
vaud_count = sum(1 for v in all_cleaned.values() if v['canton'] == 'Vaud')
print(f"\n=== RÉSUMÉ FINAL ===")
print(f"  Valais: {valais_count} emails")
print(f"  Vaud: {vaud_count} emails")
print(f"  TOTAL: {len(all_cleaned)} emails uniques propres")

print(f"\n=== LISTE FINALE ({len(all_cleaned)}) ===")
for i, (email, info) in enumerate(sorted(all_cleaned.items()), 1):
    print(f"  {i:3d}. {email:<45} | {info['canton']:6} | {info['title'][:40]}")
