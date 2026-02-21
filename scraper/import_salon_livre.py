"""
Import Salon du Livre Genève 2026 - faux positif dans le doublon checker
Source: salondulivre.ch + geneve.ch/agenda + palexpo.ch
"""
import requests, sys, io, json, time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

event = {
    'title': 'Salon du Livre de Genève 2026',
    'location': 'Palexpo, Route François-Peyrot 30, 1218 Le Grand-Saconnex',
    'date': '2026-03-18',
    'end_date': '2026-03-22',
    'time': '09:30',
    'end_time': '19:00',
    'description': '40e édition du Salon du Livre de Genève à Palexpo. Entrée gratuite sur inscription. Plus de 200 exposants, centaines d\'auteurs, dédicaces, débats et animations. Invités d\'honneur : Laure Adler, Patrick Chappatte, Hélène Dorion et Douglas Kennedy.',
    'categories': ["Culture", "Exposition", "Littérature"],
    'source_url': 'https://www.salondulivre.ch/',
    'organizer_name': 'Salon du Livre de Genève',
    'latitude': 46.2339,
    'longitude': 6.1138,
    'status': 'auto_validated'
}

r = requests.post(f'{API_URL}/api/events/scraped/batch', json={'events': [event]}, timeout=30)
print(f"Status: {r.status_code}")
print(r.json())

time.sleep(1)
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
all_ev = data if isinstance(data, list) else data.get('events', [])
print(f"TOTAL: {len(all_ev)}")
