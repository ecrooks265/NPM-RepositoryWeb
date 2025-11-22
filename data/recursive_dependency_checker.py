import json
import requests
from tqdm import tqdm
from functools import lru_cache
import time

NPM_INFO_URL = "https://registry.npmjs.org"
INPUT_FILE = "typosquat_audit.json"
OUTPUT_FILE = "dependency_audit.json"


# -------------------------------
# Fetch npm metadata with caching
# -------------------------------

@lru_cache(maxsize=None)
def fetch_package(name):
    """Fetch metadata with caching to avoid duplicate HTTP calls."""
    try:
        res = requests.get(f"{NPM_INFO_URL}/{name}", timeout=10)
        if res.status_code != 200:
            return None
        return res.json()
    except requests.RequestException:
        return None


def extract_dependencies(pkg_data):
    """Return dependency list from latest version."""
    if not pkg_data:
        return []

    latest = pkg_data.get("dist-tags", {}).get("latest")
    if not latest:
        return []

    version_meta = pkg_data.get("versions", {}).get(latest, {})
    deps = version_meta.get("dependencies", {})

    return list(deps.keys())


# ------------------------------------
# Recursive dependency crawler
# ------------------------------------

def crawl_dependencies(root_name, graph, visited):
    """
    Recursively explore dependencies.
    graph[root_name] = list of direct dependencies.
    visited ensures we do not loop.
    """
    if root_name in visited:
        return

    visited.add(root_name)

    pkg_data = fetch_package(root_name)
    deps = extract_dependencies(pkg_data)
    graph[root_name] = deps

    for dep in deps:
        crawl_dependencies(dep, graph, visited)


def main():
    # Load suspicious packages
    with open(INPUT_FILE) as f:
        audit_data = json.load(f)

    target_packages = list(audit_data.keys())
    print(f"[INFO] Found {len(target_packages)} packages to analyze recursively.")

    dependency_graph = {}
    visited = set()

    # Crawl each package
    for pkg in tqdm(target_packages, desc="Crawling dependencies"):
        crawl_dependencies(pkg, dependency_graph, visited)
        time.sleep(0.05)  # Avoid hammering npm registry

    # Now collect metadata for EVERYTHING discovered
    print(f"[INFO] Fetching metadata for {len(visited)} total packages...")

    meta = {}
    for pkg in tqdm(sorted(visited)):
        pkg_data = fetch_package(pkg)
        meta[pkg] = pkg_data or {"error": "Package not found"}

    # reverse graph: which packages depend on this package?
    reverse_dependencies = {}
    for parent, children in dependency_graph.items():
        for child in children:
            reverse_dependencies.setdefault(child, []).append(parent)

    output = {
        "roots_analyzed": target_packages,
        "dependency_graph": dependency_graph,
        "reverse_dependencies": reverse_dependencies,
        "metadata": meta
    }

    # Save results
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"[INFO] Full recursive dependency audit saved → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
