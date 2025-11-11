import httpx

async def get_vulnerabilities(package_name: str, version: str | None = None):
    url = "https://api.osv.dev/v1/query"
    payload = {
        "package": {"name": package_name, "ecosystem": "npm"}
    }
    if version:
        payload["version"] = version

    async with httpx.AsyncClient() as client:
        r = await client.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            return {"vulnerability_count": 0, "vulnerabilities": []}
        data = r.json()
        vulns = data.get("vulns", [])
        return {
            "vulnerability_count": len(vulns),
            "vulnerabilities": [
                {"id": v.get("id"), "summary": v.get("summary")}
                for v in vulns
            ]
        }
