import requests
import json
from tqdm import tqdm
from pathlib import Path
import time

NPM_INFO_URL = "https://registry.npmjs.org"
ALL_PACKAGES_FILE = "all_package_names.txt"
OUTPUT_FILE = "all_packages_audit.json"

def fetch_package_info(name):
    """Fetch full metadata for a package from the npm registry."""
    try:
        res = requests.get(f"{NPM_INFO_URL}/{name}", timeout=10)
        if res.status_code != 200:
            return None
        return res.json()
    except requests.RequestException:
        return None

def extract_audit_features(name, data):
    """Extract the fields similar to your previous audit."""
    if not data:
        return {"name": name, "error": "Package not found"}

    time_info = data.get("time", {})
    versions = list(data.get("versions", {}).keys())
    maintainers = data.get("maintainers", [])
    latest = data.get("dist-tags", {}).get("latest")
    latest_meta = data.get("versions", {}).get(latest, {}) if latest else {}

    return {
        "name": name,
        "latest_version": latest,
        "created": time_info.get("created"),
        "modified": time_info.get("modified"),
        "num_versions": len(versions),
        "num_maintainers": len(maintainers),
        "maintainers": [m.get("name") for m in maintainers],
        "description": latest_meta.get("description"),
        "keywords": latest_meta.get("keywords"),
        "has_readme": "readme" in data,
        "readme_length": len(data.get("readme", "")),
        "dependencies_count": len(latest_meta.get("dependencies", {}) or {}),
        "dist_size": latest_meta.get("dist", {}).get("unpackedSize", None),
        "repository": latest_meta.get("repository", {}),
    }

def main():
    if not Path(ALL_PACKAGES_FILE).exists():
        print(f"[ERROR] {ALL_PACKAGES_FILE} not found.")
        return

    with open(ALL_PACKAGES_FILE) as f:
        all_packages = [line.strip() for line in f if line.strip()]

    audit_results = {}

    print(f"[INFO] Auditing {len(all_packages)} packages...")

    for pkg in tqdm(all_packages, desc="Fetching package info"):
        data = fetch_package_info(pkg)
        audit_results[pkg] = extract_audit_features(pkg, data)
        time.sleep(0.025)  # small delay to reduce rate-limiting issues

    # Save results
    with open(OUTPUT_FILE, "w") as f:
        json.dump(audit_results, f, indent=2)

    print(f"[INFO] Audit complete → saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
