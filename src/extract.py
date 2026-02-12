import requests
import logging
from config import BASE_URL, HEADERS

logger = logging.getLogger(__name__)


def get_repositories():
    url = f"{BASE_URL}/user/repos"
    params = {"per_page": 100, "page": 1}
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
    return repos
