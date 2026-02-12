import logging
from pathlib import Path

from config import CSV_OUTPUT, DASHBOARD_OUTPUT
from extract import get_repositories
from transform import repos_to_dataframe

import sys
sys.path.append(str(Path(__file__).parent.parent))
from assets.dashboard import create_dashboard

logger = logging.getLogger(__name__)


def main():
    Path(CSV_OUTPUT).parent.mkdir(parents=True, exist_ok=True)
    
    logger.info("Fetching repositories...")
    repos = get_repositories()
    
    if not repos:
        logger.warning("No repositories found")
        return
    
    logger.info("Transforming data...")
    df = repos_to_dataframe(repos)
    
    logger.info(f"Saving to {CSV_OUTPUT}")
    df.to_csv(CSV_OUTPUT, index=False)
    
    logger.info("Generating dashboard...")
    create_dashboard(df, output_path=DASHBOARD_OUTPUT)
    logger.info(f"✓ Complete! {DASHBOARD_OUTPUT}")


if __name__ == "__main__":
    main()
