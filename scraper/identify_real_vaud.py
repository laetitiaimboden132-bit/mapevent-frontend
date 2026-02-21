"""
Identifier les events Vaud VRAIMENT scrapés vs les fabriqués
Les vrais = URLs de tempslibre.ch, vaud.ch, montreuxriviera.com
Les faux = URLs inventées sur des sites de villes qui redirigent
"""
import requests, sys, io, json

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
evts = data if isinstance(data, list) else data.get('events', [])

# Domaines de vrais sites d'événements (pas des pages villes)
REAL_DOMAINS = [
    'tempslibre.ch',
    'montreuxriviera.com',
    'vaud.ch/tourisme',
    'myvaud.ch',
    'elysee.ch',
]

# Domaines Valais
VALAIS_DOMAINS = [
    'valais.ch',
    'culture-valais.ch',
    'culturevalais.ch',
    'sierre.ch',
    'sion.ch',
]

real_vaud = []
fake_vaud = []
valais = []
other = []

for e in evts:
    url = e.get('source_url', '')
    if not url:
        other.append(e)
        continue
    
    is_valais = any(d in url for d in VALAIS_DOMAINS)
    is_real = any(d in url for d in REAL_DOMAINS)
    
    if is_valais:
        valais.append(e)
    elif is_real:
        real_vaud.append(e)
    else:
        fake_vaud.append(e)

print(f"=== CLASSIFICATION ===")
print(f"  Valais: {len(valais)}")
print(f"  Vaud VRAIS (tempslibre, etc): {len(real_vaud)}")
print(f"  Vaud FAUX (URLs inventées): {len(fake_vaud)}")
print(f"  Autres (sans URL): {len(other)}")

print(f"\n=== VAUD VRAIS ({len(real_vaud)}) ===")
for e in real_vaud:
    print(f"  ID:{e['id']} | {e['title'][:50]} | {e.get('source_url','')[:80]}")

print(f"\n=== IDs VAUD FAUX à supprimer ({len(fake_vaud)}) ===")
fake_ids = [e['id'] for e in fake_vaud]

# Sauvegarder
with open('vaud_fake_ids.json', 'w') as f:
    json.dump({'fake_ids': fake_ids, 'count': len(fake_ids)}, f)
print(f"Sauvegardé {len(fake_ids)} IDs dans vaud_fake_ids.json")

# Afficher les 30 premiers faux pour vérifier
print(f"\n=== Échantillon FAUX (30 premiers) ===")
for e in fake_vaud[:30]:
    print(f"  ID:{e['id']} | {e['title'][:40]} | {e.get('source_url','')[:70]}")
