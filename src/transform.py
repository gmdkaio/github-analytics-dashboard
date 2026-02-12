import pandas as pd
import logging

logger = logging.getLogger(__name__)


def repos_to_dataframe(repos):
    if not repos:
        logger.warning("No repositories to transform")
        return pd.DataFrame()

    records = []
    for repo in repos:
        records.append({
            "name": repo.get("name"),
            "private": repo.get("private"),
            "language": repo.get("language"),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "open_issues": repo.get("open_issues_count", 0),
            "size_kb": repo.get("size", 0),
            "archived": repo.get("archived", False),
            "created_at": repo.get("created_at"),
            "pushed_at": repo.get("pushed_at")
        })

    df = pd.DataFrame(records)
    logger.info(f"DataFrame: {len(df)} repositories")

    df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    df["pushed_at"] = pd.to_datetime(df["pushed_at"], utc=True)
    df["size_mb"] = df["size_kb"] / 1024
    df["year_created"] = df["created_at"].dt.year

    now = pd.Timestamp.now(tz="UTC")
    df["days_since_last_push"] = (now - df["pushed_at"]).dt.days
    df["is_active"] = df["days_since_last_push"] < 90
    
    logger.info(f"Active repos: {df['is_active'].sum()}/{len(df)}")
    return df
