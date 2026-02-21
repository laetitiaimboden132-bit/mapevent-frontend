"""Debug import Genève - tester avec 1 event"""
import requests, sys, io, json

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# Un seul event de test
payload = [{
    'title': 'Salon International de l\'Automobile de Genève 2026',
    'description': 'Le salon automobile le plus prestigieux au monde.',
    'date': '2026-03-05',
    'end_date': '2026-03-15',
    'time': '--:--',
    'location': 'Palexpo, Route François-Peyrot 30, 1218 Le Grand-Saconnex',
    'city': 'Genève',
    'latitude': 46.2358,
    'longitude': 6.1114,
    'categories': ['Culture > Expositions'],
    'source_url': 'https://www.gims.swiss/',
    'organizer_email': 'info@gims.swiss',
    'validation_status': 'pending'
}]

print("Envoi de 1 event test...")
r = requests.post(f'{API_URL}/api/events/scraped/batch',
                 json={'events': payload, 'send_emails': False},
                 headers={"Content-Type": "application/json"},
                 timeout=30)

print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")
