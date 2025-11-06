import asyncio
from typing import Dict, List, Set
import httpx

NPM_REGISTRY = "https://registry.npmjs.org/"

async def fetch_package_metadata(client: httpx.AsyncClient, package_name: str) -> Dict:
    url = NPM_REGISTRY + package_name
    resp = await client.get(url, timeout=30.0)
    if resp.status_code != 200:
        raise ValueError(f"Failed to fetch {package_name}: {resp.status_code}")
    return resp.json()

async def get_latest_dependencies(client: httpx.AsyncClient, package_name: str) -> Dict[str, str]:
    data = await fetch_package_metadata(client, package_name)
    latest_tag = data.get("dist-tags", {}).get("latest")
    version_info = data.get("versions", {}).get(latest_tag, {})
    deps = version_info.get("dependencies", {}) or {}
    return deps

async def build_graph(start_pkg: str, max_depth: int = 2, concurrency: int = 10) -> Dict:
    seen: Set[str] = set()
    nodes: Dict[str, Dict] = {}
    edges: List[Dict] = []

    queue: asyncio.Queue = asyncio.Queue()
    await queue.put((start_pkg, 0))

    async with httpx.AsyncClient() as client:
        sem = asyncio.Semaphore(concurrency)

        async def worker():
            while not queue.empty():
                pkg, depth = await queue.get()
                if pkg in seen:
                    queue.task_done()
                    continue
                seen.add(pkg)
                try:
                    async with sem:
                        deps = await get_latest_dependencies(client, pkg)
                except Exception as e:
                    nodes[pkg] = {"id": pkg, "label": pkg, "error": str(e)}
                    queue.task_done()
                    continue

                nodes[pkg] = {"id": pkg, "label": pkg, "depth": depth, "degree": len(deps)}

                for dep in deps.keys():
                    edges.append({"from": pkg, "to": dep})
                    if dep not in seen and depth + 1 <= max_depth:
                        await queue.put((dep, depth + 1))
                queue.task_done()

        workers = [asyncio.create_task(worker()) for _ in range(concurrency)]
        await queue.join()
        for w in workers:
            w.cancel()

    return {"nodes": list(nodes.values()), "edges": edges}

if __name__ == "__main__":
    import sys, json
    pkg = sys.argv[1] if len(sys.argv) > 1 else "express"
    graph = asyncio.run(build_graph(pkg, max_depth=2))
    print(json.dumps(graph, indent=2))
