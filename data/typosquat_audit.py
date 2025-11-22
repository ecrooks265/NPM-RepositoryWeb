import json
import requests
from tqdm import tqdm

NPM_INFO_URL = "https://registry.npmjs.org"

ALL_PACKAGES_FILE = "all_package_names.txt"  # local cached list
OUTPUT_FILE = "typosquat_audit.json"


# -----------------------------
# Typosquat detection rules
# -----------------------------
from rapidfuzz.distance import Levenshtein

def is_typo_squat(original: str, candidate: str) -> bool:
    if candidate == original:
        return False

    o = original.lower()
    c = candidate.lower()

    banned_prefixes = ("@types/", "@nestjs/", "@nx/", "@vitejs/", "@angular/")

    if c.startswith(banned_prefixes) or o.startswith(banned_prefixes):
        return False

    if "-" in c or "/" in c:
        return False

    if abs(len(o) - len(c)) > 1:
        return False

    dist = Levenshtein.distance(o, c)
    if dist not in (1, 2):
        return False

    set_o = set(o)
    set_c = set(c)
    overlap = len(set_o & set_c) / max(len(set_o), 1)
    if overlap < 0.7:
        return False

    return True


# -----------------------------
# Audit functions
# -----------------------------
def fetch_package_info(name):
    try:
        res = requests.get(f"{NPM_INFO_URL}/{name}", timeout=10)
        if res.status_code != 200:
            return None
        return res.json()
    except requests.RequestException:
        return None


def extract_audit_features(name, data):
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


# -----------------------------
# Main auditing logic
# -----------------------------
def audit_typosquats(target_packages_file=ALL_PACKAGES_FILE):
    # Load all NPM package names locally
    with open(target_packages_file) as f:
        all_packages = [line.strip() for line in f]

    # Load your original target packages to check for typosquats
    # For demo purposes, let's assume you have a list
    target_packages = ["express", "react", "lodash"]  # replace with your Excel loader if needed

    # Generate candidate typosquats from the full registry
    typosquat_candidates = {}
    for pkg in tqdm(target_packages, desc="Scanning for typosquats"):
        matches = [c for c in all_packages if is_typo_squat(pkg, c)]
        if matches:
            typosquat_candidates[pkg] = matches

    print(f"[INFO] Found {sum(len(v) for v in typosquat_candidates.values())} potential typosquats.")

    # Audit all found typosquats
    audit_results = {}
    all_candidates = set()
    for matches in typosquat_candidates.values():
        all_candidates.update(matches)

    print(f"[INFO] Auditing {len(all_candidates)} potential typosquat packages...")
    for pkg in tqdm(sorted(all_candidates), desc="Auditing packages"):
        metadata = fetch_package_info(pkg)
        audit_results[pkg] = extract_audit_features(pkg, metadata)

    # Save results
    with open(OUTPUT_FILE, "w") as f:
        json.dump(audit_results, f, indent=2)
    print(f"[INFO] Audit complete → saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    audit_typosquats()
