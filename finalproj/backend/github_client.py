# github_client.py
import aiohttp
import re
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Optional but recommended for higher rate limits
async def extract_github_repo_url(npm_meta):
    """Extract GitHub repo 'user/repo' from npm metadata if available."""
    repo_info = npm_meta.get("repository", {})
    url = repo_info.get("url", "") or ""
    match = re.search(r"github\.com[:/](?P<user>[^/]+)/(?P<repo>[^/.]+)", url)
    if match:
        return f"{match.group('user')}/{match.group('repo')}"
    return None

async def get_github_repo_data(repo_slug):
    """Fetch contributors and metadata from GitHub."""
    if not repo_slug:
        return {}

    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    async with aiohttp.ClientSession(headers=headers) as session:
        repo_url = f"https://api.github.com/repos/{repo_slug}"
        contrib_url = f"{repo_url}/contributors"

        async with session.get(repo_url) as r1:
            repo_meta = await r1.json()

        async with session.get(contrib_url) as r2:
            contribs = await r2.json()

        return {
            "repo": {
                "name": repo_meta.get("full_name"),
                "html_url": repo_meta.get("html_url"),
                "stars": repo_meta.get("stargazers_count", 0),
                "forks": repo_meta.get("forks_count", 0),
                "contributors": [
                    {
                        "login": c.get("login"),
                        "html_url": c.get("html_url"),
                        "avatar_url": c.get("avatar_url"),
                        "contributions": c.get("contributions"),
                    }
                    for c in contribs if isinstance(c, dict)
                ],
            }
        }
