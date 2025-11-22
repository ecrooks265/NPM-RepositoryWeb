from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from deps_fetcher import parse_dependency_json
from npm_client import get_package_metadata
from osv_client import get_vulnerabilities
import requests
from rapidfuzz.distance import Levenshtein


import json
import asyncio
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/upload")
async def upload_json(file: UploadFile = File(...)):
    """Accepts a dependency JSON file and returns enriched graph data."""
    content = await file.read()
    obj = json.loads(content)
    graph = parse_dependency_json(obj)

    # Enrich nodes concurrently
    tasks = []
    for node in graph["nodes"]:
        name = node["data"]["id"]
        tasks.append(enrich_node(node, name))
    await asyncio.gather(*tasks)

    return graph


@app.get("/api/dependencies/{package}")
async def get_package_graph(package: str):
    """Fetch one npm package and enrich metadata."""
    meta = await get_package_metadata(package)
    vulns = await get_vulnerabilities(package, meta.get("version"))

    repo_url = meta.get("repository", {}).get("url")

    node_data = {**meta, **vulns}
    node = {"data": {"id": package, **node_data}}
    return {"nodes": [node], "edges": []}


async def enrich_node(node, name):
    meta = await get_package_metadata(name)
    vulns = await get_vulnerabilities(name, meta.get("version"))
    
    node["data"].update(meta)
    node["data"].update(vulns)

NPM_SEARCH_URL = "https://registry.npmjs.com/-/v1/search"

def is_typo_squat(original: str, candidate: str) -> bool:
    """
    Returns True if candidate is a realistic typosquat of original.
    Rules:
    - Length difference must be small (≤ 2)
    - Levenshtein distance must be small (1–2)
    - Candidate cannot add meaningful prefixes/suffixes
    """
    if candidate == original:
        return False

    # Normalize
    o = original.lower()
    c = candidate.lower()

    # Skip names that append/prepend full words (e.g. express-ws)
    if "-" in c or "/" in c:
        return False

    # Hard length cutoff (avoid things like express-ws)
    if abs(len(o) - len(c)) > 1:
        return False

    # Compute edit distance
    dist = Levenshtein.distance(o, c)

    # Only true typos if 1–2 edits apart
    return dist in (1, 2)


@app.get("/api/typosquats/{package}")
async def typosquats(package: str):
    params = {"text": package, "size": 100}

    try:
        res = requests.get(NPM_SEARCH_URL, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()

        results = []
        for obj in data.get("objects", []):
            name = obj.get("package", {}).get("name")
            if not name or name == package:
                continue

            if is_typo_squat(package, name):
                results.append({
                    "name": name,
                    "levenshtein": Levenshtein.distance(package, name)
                })

        return {"package": package, "similar_names": results}

    except requests.RequestException as e:
        return {"error": str(e), "similar_names": []}