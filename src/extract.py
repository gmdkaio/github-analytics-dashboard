import requests
from config import BASE_URL, HEADERS

def get_repositories():
    url = f"{BASE_URL}/user/repos"

    params = {
        "per_page": 100,
        "page": 1
    }

    repos = []

    while True:
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()

        if not data:
            break

        repos.extend(data)
        params["page"] += 1

    return repos
