#!/usr/bin/env python3
"""Validate all EcoHandel OS API endpoints."""
import json, urllib.request, urllib.error

BASE = "http://127.0.0.1:5555"
AUTH = "milan", "ecohandel2026"
import base64
creds = base64.b64encode(b"milan:ecohandel2026").decode()

def api_get(path):
    url = f"{BASE}{path}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Basic {creds}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read()), resp.status
    except Exception as e:
        return {"error": str(e)}, 0

endpoints = [
    ("/health", 200),
    ("/queue", 200),
    ("/queue/items", 200),
    ("/campaigns/stats", 200),
    ("/dashboard", 200),
    ("/agents/status", 200),
    ("/workflows", 200),
    ("/workflows/history", 200),
    ("/activity", 200),
]

results = []
for path, expected in endpoints:
    data, status = api_get(path)
    ok = status == expected
    results.append({"endpoint": path, "expected": expected, "got": status, "ok": ok})
    print(f"{'✅' if ok else '❌'} {path}: {status} (expected {expected})")

all_ok = all(r["ok"] for r in results)

# Save results
output = {
    "validated_at": __import__("datetime").datetime.now().isoformat(),
    "all_ok": all_ok,
    "results": results,
}
with open("/var/www/html/control.ecohandel.nl/data/api_validation.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\n{'ALL OK ✅' if all_ok else 'SOME FAILED ❌'}")
print(f"Results saved to: /var/www/html/control.ecohandel.nl/data/api_validation.json")
