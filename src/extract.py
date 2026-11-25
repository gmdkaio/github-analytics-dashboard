import requests
import logging
from config import BASE_URL, HEADERS

logger = logging.getLogger(__name__)


def get_repositories():
    url = f"{BASE_URL}/user/repos"
    params = {"per_page": 100, "page": 1, "affiliation": "owner"}  # not org or collaborator repos
    repos = []

    while True:
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not data:
                break

            repos.extend(data)
            logger.info(f"Fetched page {params['page']}: {len(data)} repos")
            params["page"] += 1
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                logger.error("Authentication failed. Check GITHUB_TOKEN")
            elif response.status_code == 403:
                logger.error("Rate limit exceeded")
            else:
                logger.error(f"HTTP error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise

    logger.info(f"Total repositories: {len(repos)}")
    for repo in repos:
        if repo.get("fork"):
            repo["contributed"] = merged_upstream(repo)
    return repos


def merged_upstream(fork):
    """True if the parent is public and the fork's owner got a PR merged into it."""
    detail = requests.get(fork["url"], headers=HEADERS, timeout=30)
    detail.raise_for_status()
    parent = detail.json().get("parent") or {}
    if not parent or parent.get("private"):
        return False
    q = f"is:pr is:merged author:{fork['owner']['login']} repo:{parent['full_name']}"
    search = requests.get(f"{BASE_URL}/search/issues", headers=HEADERS,
                          params={"q": q, "per_page": 1}, timeout=30)
    search.raise_for_status()
    return search.json()["total_count"] > 0
