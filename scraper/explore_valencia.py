import requests, json

HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}

# Download Valencia IVC JSON
url = "https://dadesobertes.gva.es/dataset/25cc4d21-e1dd-4d05-b057-dbcc44d4338c/resource/15084e00-c416-4b4d-b229-7a06f4bf07b0/download"
print(f"Downloading: {url}")
r = requests.get(url, headers=HEADERS, timeout=30)
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('content-type')}")

if r.status_code == 200:
    try:
        data = r.json()
        if isinstance(data, list):
            print(f"Type: list, len={len(data)}")
            if data:
                print(f"Keys: {list(data[0].keys())}")
                print(f"Sample:\n{json.dumps(data[0], indent=2, ensure_ascii=False)[:2000]}")
        elif isinstance(data, dict):
            print(f"Type: dict, keys={list(data.keys())[:10]}")
            for k in ["result", "results", "records", "features", "data"]:
                if k in data:
                    items = data[k]
                    print(f"  {k}: len={len(items)}")
                    if isinstance(items, list) and items:
                        print(f"  Keys: {list(items[0].keys())}")
                        print(f"  Sample:\n{json.dumps(items[0], indent=2, ensure_ascii=False)[:2000]}")
                    break
            else:
                print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
    except:
        print(f"Not JSON. First 1000 chars:\n{r.text[:1000]}")
