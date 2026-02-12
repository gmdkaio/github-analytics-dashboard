# GitHub Analytics Dashboard

Automated data pipeline that fetches repository data from the GitHub API and generates data visualizations.

## Dashboard Preview

![GitHub Analytics Dashboard](data/github_dashboard.svg)

## Features

- Automated ETL pipeline for GitHub repository data
- Professional dark-themed dashboard with multiple visualizations
- Repository growth timeline analysis
- Language distribution breakdown
- Recent activity tracking
- Size and push frequency analytics

## Project Structure

```
github-analytics-dashboard/
├── src/
│   ├── config.py       # Environment configuration
│   ├── extract.py      # GitHub API data extraction
│   ├── transform.py    # Data processing and enrichment
│   └── main.py         # Pipeline orchestration
├── assets/
│   └── dashboard.py    # Visualization generation
├── data/               # Generated outputs
├── notebooks/          # Data exploration
└── requirements.txt    # Python dependencies
```

## Installation

1. Clone the repository
```bash
git clone <repository-url>
cd github-analytics-dashboard
```

2. Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables

Create a `.env` file in the project root:
```env
GITHUB_TOKEN=your_personal_access_token
USERNAME=your_github_username
```

To generate a GitHub token:
- Go to GitHub Settings > Developer settings > Personal access tokens
- Create a token with `repo` scope for private repositories
- Copy the token to your `.env` file

## Usage

```bash
cd src
python main.py
```

The pipeline will:
1. Fetch all repositories from your GitHub account
2. Process and enrich the data with calculated metrics
3. Generate visualizations and save outputs to `data/`

## Output Files

- `data/github_repos_clean.csv` - Processed repository data
- `data/github_dashboard.svg` - Analytics dashboard visualization

## Data Metrics

The pipeline calculates:
- Total repositories and active status
- Star and language counts
- Repository size and age
- Days since last push
- Activity classification (active: pushed within 90 days)

## License

MIT License

---

## Auto-Update with GitHub Actions

This repository includes a GitHub Action that automatically updates the dashboard daily at midnight UTC.

**Manual Trigger:** Go to Actions tab → "Update GitHub Analytics Dashboard" → Run workflow

**Schedule:** Daily at 00:00 UTC (configurable in `.github/workflows/update-dashboard.yml`)

## Using in Your GitHub Profile

To display this dashboard in your GitHub profile README:

1. Make sure this repository is public
2. Enable GitHub Actions in repository settings
3. Add to your profile README (replace `YOUR_USERNAME` and `REPO_NAME`):

```markdown
![GitHub Analytics](https://raw.githubusercontent.com/YOUR_USERNAME/REPO_NAME/main/data/github_dashboard.svg)
```

The dashboard will automatically update daily via GitHub Actions.
