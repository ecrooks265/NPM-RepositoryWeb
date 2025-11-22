import requests
import json
from pathlib import Path

LIMIT = 10000
headers = {"npm-replication-opt-in": "true"}
all_packages = []

# Cache file path
CACHE_FILE = "all_packages.json"

# If cache exists, load it instead of downloading
if Path(CACHE_FILE).exists():
    print(f"[INFO] Loading cached package list from {CACHE_FILE}")
    with open(CACHE_FILE) as f:
        all_packages = json.load(f)
else:
    print("[INFO] Downloading NPM registry package list...")

    # first batch
    res = requests.get(f"https://replicate.npmjs.com/registry/_all_docs?limit={LIMIT}", headers=headers)
    res.raise_for_status()
    data = res.json()
    rows = data['rows']
    all_packages.extend(rows)

    while True:
        last_key = rows[-1]['key']
        params = {"limit": LIMIT, "startkey": json.dumps(last_key)}
        res = requests.get("https://replicate.npmjs.com/registry/_all_docs", params=params, headers=headers)
        res.raise_for_status()
        rows = res.json()['rows']

        # Sanity check for duplicates
        if rows[0]['key'] != last_key:
            raise ValueError(f"Expected first row key {last_key} but got {rows[0]['key']}")

        if len(rows) == 1:
            break

        all_packages.extend(rows[1:])  # skip duplicate first row
        print(f"[INFO] Total packages fetched: {len(all_packages)}")

    # Save to JSON for future use
    with open(CACHE_FILE, "w") as f:
        json.dump(all_packages, f)
    print(f"[INFO] Package list saved to {CACHE_FILE}")

# Extract just package names (the 'id' field) for your typosquat scanner
all_package_names = [row['id'] for row in all_packages]
print(f"[INFO] Total package names available for scanning: {len(all_package_names)}")

# Optionally, save just names to a separate file
with open("all_package_names.txt", "w") as f:
    for name in all_package_names:
        f.write(name + "\n")
