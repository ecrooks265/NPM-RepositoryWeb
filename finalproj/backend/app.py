from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from deps_fetcher import parse_dependency_json
from npm_client import get_package_metadata
from osv_client import get_vulnerabilities
from github_client import extract_github_repo_url, get_github_repo_data
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
    github_data = await github_client.enrich_from_repo_url(repo_url) if repo_url else None

    node_data = {**meta, **vulns}
    if github_data:
        node_data["github"] = github_data

    node = {"data": {"id": package, **node_data}}
    return {"nodes": [node], "edges": []}


async def enrich_node(node, name):
    meta = await get_package_metadata(name)
    vulns = await get_vulnerabilities(name, meta.get("version"))
    github_repo_slug = await extract_github_repo_url(meta)
    github_data = await get_github_repo_data(github_repo_slug)
    
    node["data"].update(meta)
    node["data"].update(vulns)
    node["data"]["github"] = github_data



NPM_SEARCH_URL = "https://registry.npmjs.com/-/v1/search"

@app.get("/api/typosquats/{package}")
async def typosquats(package: str):
    """
    Search NPM registry for similar package names.
    This uses the official search API to find packages that may be typosquatting.
    """
    params = {
        "text": package,
        "size": 50  # adjust number of results if needed
    }
    try:
        res = requests.get(NPM_SEARCH_URL, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        results = []

        for pkg in data.get("objects", []):
            name = pkg.get("package", {}).get("name")
            if name and name != package:
                results.append(name)

        return {"package": package, "similar_names": results}

    except requests.RequestException as e:
        return {"error": str(e), "similar_names": []}