"""List all users for promo emails."""
import requests, json
API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

r = requests.get(f"{API}/admin/list-users", timeout=15)
d = r.json()
print(f"Status: {r.status_code}, Count: {d.get('count', 0)}")
for u in d.get("users", []):
    email = u.get("email", "")
    username = u.get("username", "")
    name = f"{u.get('first_name', '') or ''} {u.get('last_name', '') or ''}".strip()
    created = u.get("created_at", "")
    print(f"  {email:40s} | {username:15s} | {name:20s} | {created}")
