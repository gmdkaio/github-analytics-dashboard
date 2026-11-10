import pandas as pd
import logging

logger = logging.getLogger(__name__)


# A repo's status comes from one of these GitHub topics, set by hand on the
# repo page. Untagged repos have no status and stay out of the lifecycle charts.
STATUS_TOPICS = {"wip": "In progress", "paused": "Paused", "finished": "Finished", "dropped": "Dropped"}


def lifecycle(r):
    for topic, stage in STATUS_TOPICS.items():
        if topic in r["topics"]:
            return stage
    return None


def repos_to_dataframe(repos):
    if not repos:
        logger.warning("No repositories to transform")
        return pd.DataFrame()

    records = []
    for repo in repos:
        records.append({
            "name": repo.get("name"),
            "url": repo.get("html_url"),
            "private": repo.get("private"),
            "language": repo.get("language"),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "open_issues": repo.get("open_issues_count", 0),
            "size_kb": repo.get("size", 0),
            "archived": repo.get("archived", False),
            "created_at": repo.get("created_at"),
            "pushed_at": repo.get("pushed_at"),
            "fork": repo.get("fork", False),
            "description": repo.get("description") or "",
            "is_template": repo.get("is_template", False),
            "topics": repo.get("topics", []),
            "has_license": repo.get("license") is not None,
        })

    df = pd.DataFrame(records)
    logger.info(f"DataFrame: {len(df)} repositories")

    df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    df["pushed_at"] = pd.to_datetime(df["pushed_at"], utc=True)

    now = pd.Timestamp.now(tz="UTC")
    df["days_since_last_push"] = (now - df["pushed_at"]).dt.days
    df["is_active"] = df["days_since_last_push"] < 90

    # Exclude forks: this dashboard reports on the user's own work, not
    # repos they merely forked from someone else.
    forks_dropped = int(df["fork"].sum())
    df = df[~df["fork"]].reset_index(drop=True)
    if forks_dropped:
        logger.info(f"Excluded {forks_dropped} forked repositories")

    df["stage"] = df.apply(lifecycle, axis=1)

    logger.info(f"Live repos (pushed <90d): {df['is_active'].sum()}/{len(df)}")
    logger.info(f"Lifecycle: {df['stage'].value_counts().to_dict()}")
    return df
