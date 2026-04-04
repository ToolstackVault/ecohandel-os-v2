#!/usr/bin/env python3
"""Validate EcoHandel OS API endpoints"""
import json, urllib.request, urllib.error, sys
from datetime import datetime, timezone

BASE = "http://127.0.0.1:5555"
ENDPOINTS = [
    ("GET", "/health", None),
    ("GET", "/queue", None),
    ("GET", "/queue/items", None),
    ("GET", "/campaigns/stats", None),
    ("GET", "/dashboard", None),
    ("GET", "/agents/status", None),
    ("GET", "/workflows", None),
    ("GET", "/workflows/history", None),
    ("GET", "/activity", None),
]

results = []
ok_count = 0
fail_count = 0

for method, path, _ in ENDPOINTS:
    url = BASE + path
    try:
        req = urllib.request.Request(url, method=method)
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())
            results.append({
                "endpoint": path,
                "method": method,
                "status": resp.status,
                "ok": True,
                "response_type": type(body).__name__,
                "data_sample": str(body)[:200] if isinstance(body, dict) else str(body)[:200]
            })
            ok_count += 1
            print(f"  ✅ {path} → {resp.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        results.append({
            "endpoint": path,
            "method": method,
            "status": e.code,
            "ok": e.code == 200,
            "error_type": "HTTPError",
            "error_body": body[:200]
        })
        if e.code == 401:
            print(f"  🔒 {path} → {e.code} (auth required - expected)")
            ok_count += 1  # Auth-required is OK
        else:
            print(f"  ❌ {path} → {e.code}")
            fail_count += 1
    except Exception as e:
        results.append({
            "endpoint": path,
            "method": method,
            "ok": False,
            "error_type": type(e).__name__,
            "error_msg": str(e)[:200]
        })
        print(f"  ❌ {path} → ERROR: {e}")
        fail_count += 1

validation = {
    "run_at": datetime.now(timezone.utc).isoformat(),
    "total": len(ENDPOINTS),
    "ok": ok_count,
    "failed": fail_count,
    "results": results
}

output_path = "/var/www/html/control.ecohandel.nl/data/api_validation.json"
with open(output_path, "w") as f:
    json.dump(validation, f, indent=2)

print(f"\n✅ API Validation: {ok_count}/{len(ENDPOINTS)} endpoints OK")
print(f"   Results saved to: {output_path}")
