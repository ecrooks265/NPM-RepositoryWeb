import httpx

async def get_package_metadata(package_name: str):
    """Fetch maintainer and version info from npm registry."""
    url = f"https://registry.npmjs.org/{package_name}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=10)
        if r.status_code != 200:
            return {"maintainers": [], "maintainer_count": 0, "version": None}
        data = r.json()
        latest = data.get("dist-tags", {}).get("latest")
        version_info = data.get("versions", {}).get(latest, {})
        maintainers = [m["name"] for m in version_info.get("maintainers", [])]
        return {
            "version": latest,
            "maintainers": maintainers,
            "maintainer_count": len(maintainers)
        }
