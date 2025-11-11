from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from deps_fetcher import parse_dependency_json
from npm_client import get_package_metadata
from osv_client import get_vulnerabilities
import json
import asyncio

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
    node = {"data": {"id": package, **meta, **vulns}}
    return {"nodes": [node], "edges": []}


async def enrich_node(node, name):
    meta = await get_package_metadata(name)
    vulns = await get_vulnerabilities(name, meta.get("version"))
    node["data"].update(meta)
    node["data"].update(vulns)
