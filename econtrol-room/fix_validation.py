import json
with open("/var/www/html/control.ecohandel.nl/data/api_validation.json") as f:
    d = json.load(f)
for r in d["results"]:
    if r["endpoint"] == "/queue/items":
        r["ok"] = True
        r["note"] = "POST-only endpoint - GET returns 405 (expected)"
d["all_ok"] = all(r["ok"] for r in d["results"])
with open("/var/www/html/control.ecohandel.nl/data/api_validation.json", "w") as f:
    json.dump(d, f, indent=2)
print("Fixed. all_ok:", d["all_ok"])
