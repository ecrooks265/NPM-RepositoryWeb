from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from deps_fetcher import build_graph
import asyncio

app = FastAPI(title="NPM Dependency Web API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CACHE = {}
CACHE_LOCK = asyncio.Lock()

@app.get("/api/dependencies/{package_name}")
async def get_dependencies(package_name: str, depth: int = 2):
    key = f"{package_name}@{depth}"
    async with CACHE_LOCK:
        if key in CACHE:
            return CACHE[key]
    try:
        graph = await build_graph(package_name, max_depth=depth)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    async with CACHE_LOCK:
        CACHE[key] = graph
    return graph

@app.get("/api/ping")
async def ping():
    return {"status": "ok"}
