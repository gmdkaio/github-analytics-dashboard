import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = os.getenv("USERNAME")

if not GITHUB_TOKEN:
    logging.error("GITHUB_TOKEN not found in .env file")
    raise ValueError("GITHUB_TOKEN is required")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

BASE_URL = "https://api.github.com"

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CSV_OUTPUT = str(DATA_DIR / "github_repos_clean.csv")
DASHBOARD_OUTPUT = str(DATA_DIR / "github_dashboard.svg")
