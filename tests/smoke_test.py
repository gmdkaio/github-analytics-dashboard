"""Render every layout x theme from a small fixed dataset and check the output.

Run from the repo root: python tests/smoke_test.py
"""
import re
import sys
import tempfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from assets.dashboard import LAYOUTS, create_dashboard  # noqa: E402
from assets.layouts.common import SHOW_PRIVATE, THEMES, TOP_N, top_languages  # noqa: E402

year = pd.Timestamp.now(tz="UTC").year
# name, private, language, stars, stage, created year
REPOS = [
    ("secret-project", True, "Python", 50, "Live", year),
    ("py-one", False, "Python", 3, "Live", year),
    ("py-two", False, "Python", 0, "Stub", year - 2),
    ("go-one", False, "Go", 4, "In progress", year - 1),
    ("go-two", False, "Go", 1, "Live", year),
    ("rust-one", False, "Rust", 1, "Stub", year - 3),
    ("rust-two", True, "Rust", 0, "Live", year),
    ("ada-one", False, "Ada", 9, "In progress", year - 1),
    ("c-one", False, "C", 9, "Live", year),
    ("zig-one", False, "Zig", 9, "Archived", year - 2),
    ("site", False, "HTML", 2, "Live", year),
    ("notes", False, None, 0, "Stub", year - 1),
]
df = pd.DataFrame(
    [{"name": n, "url": f"https://github.com/someone/{n}", "private": p, "language": lang,
      "stars": s, "stage": st, "archived": st == "Archived",
      "created_at": f"{y}-01-15 10:00:00+00:00", "pushed_at": f"{y}-01-20 10:00:00+00:00"}
     for n, p, lang, s, st, y in REPOS]
)

# count, then stars, then name; HTML filtered, no-language dropped
names = [l["name"] for l in top_languages(df)[0]]
assert names == ["Python", "Go", "Rust", "Ada", "C", "Zig"][:TOP_N], names

private = df.loc[df["private"], "name"].tolist()
runs = [(l, t, True) for l in LAYOUTS for t in THEMES] + [(l, "", False) for l in LAYOUTS]

with tempfile.TemporaryDirectory() as tmp:
    for layout, theme, gradients in runs:
        out = Path(tmp) / f"{layout}-{theme}-{gradients}.svg"
        create_dashboard(df, str(out), theme=theme, layout=layout, gradients=gradients)
        svg = out.read_text(encoding="utf-8")
        assert re.search(r'<svg[^>]* width="1200" ', svg), f"{out.name}: width is not 1200"
        assert "ada-one" in svg, f"{out.name}: top public repo missing"
        for name in private if not SHOW_PRIVATE else []:
            assert name not in svg, f"{out.name}: private repo {name!r} in SVG"

print(f"ok: {len(runs)} renders")
