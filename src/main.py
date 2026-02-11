from extract import get_repositories

repos = get_repositories()

print(f"\nTotal repositories: {len(repos)}\n")

for repo in repos:
    print(
        f"Name: {repo['name']}\n"
        f"Private: {repo['private']}\n"
        f"Language: {repo['language']}\n"
        f"Stars: {repo['stargazers_count']}\n"
        f"Forks: {repo['forks_count']}\n"
        f"Created: {repo['created_at']}\n"
        f"{'-'*40}"
    )
