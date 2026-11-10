"""Render the README pictures from the saved CSV.

Run from the repo root: python scripts/readme_previews.py
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from assets.dashboard import create_dashboard  # noqa: E402
from assets.layouts.common import THEMES  # noqa: E402

OUT = ROOT / ".github" / "assets"
df = pd.read_csv(ROOT / "data" / "github_repos_clean.csv")

(OUT / "layouts").mkdir(parents=True, exist_ok=True)
(OUT / "themes").mkdir(parents=True, exist_ok=True)
for layout in ("card", "bento", "terminal"):
    create_dashboard(df, str(OUT / "layouts" / f"{layout}.svg"), layout=layout)
create_dashboard(df, str(OUT / "layouts" / "card-flat.svg"), layout="card", gradients=False)
for theme in THEMES:
    create_dashboard(df, str(OUT / "themes" / f"{theme}.svg"), layout="card", theme=theme)

# every layout in every theme, to compare
(OUT / "outputs").mkdir(parents=True, exist_ok=True)
for layout in ("card", "bento", "terminal"):
    for theme in THEMES:
        create_dashboard(df, str(OUT / "outputs" / f"{layout}-{theme}.svg"), layout=layout, theme=theme)
