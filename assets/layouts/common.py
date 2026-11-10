"""Shared data rules, drawing helpers and fonts for all layouts.

Every layout draws on a Canvas: one axes covering the whole figure, in pixel
coordinates with y growing downward (like HTML), so the mockups' sizes and
spacing translate directly. Font sizes in points equal pixels here because the
figure is sized at 72 units per inch and the SVG size is rewritten to px.
"""
import calendar
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.collections import LineCollection
from matplotlib.colors import to_rgba
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Circle, FancyBboxPatch, Polygon
from matplotlib.textpath import TextToPath

sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
from palettes import THEMES, stage_color  # noqa: E402,F401

for _f in Path(__file__).parent.parent.joinpath("fonts").glob("*.ttf"):
    font_manager.fontManager.addfont(str(_f))
# Weights without an exact file (Space Grotesk has no SemiBold) resolve to the
# nearest one, which is what we want; matplotlib warns on every lookup.
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

# DejaVu Sans ships with matplotlib and covers the glyphs the layout fonts
# lack (★ in JetBrains Mono, block elements in Inter).
FALLBACK = "DejaVu Sans"

# How many languages to list before the rest go into "Other". Colors repeat
# after 5. The card fits about 10 rows, bento and terminal about 7.
TOP_N = 5

# Languages left out of the language list. They tend to show up as a side
# effect of a repo (a build config, a docs page) rather than as its primary
# language. Set FILTERED_LANGS = set() to count everything.
FILTERED_LANGS = {"HTML", "CSS", "JavaScript"}

# Leaderboards list public repos only, because the SVG is meant for a public
# README. Set to True to include private repos too.
SHOW_PRIVATE = False

STAGE_ORDER = ["Live", "In progress", "Stub", "Archived"]


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------

def pct(a, b):
    """Whole percent, half rounded up."""
    return int(a * 100 / b + 0.5) if b else 0


@dataclass
class Snapshot:
    user: str
    now: pd.Timestamp
    total: int
    public: int
    private: int
    stars: int
    live: int
    archived: int
    year: int
    created_ytd: int
    pushed_month: int
    star_conc: int          # % of all stars on the most starred repo
    classified: int         # repos counted for languages
    langs: list             # top TOP_N: dicts name, n, pct, stars, live
    other: dict             # n, pct, names
    stages: list            # (stage, n), STAGE_ORDER, zeros dropped
    new_by_month: list      # (label, n), Jan..current month of this year
    push_12m: list          # (label, n), trailing 12 months
    cum_by_year: list       # (year, cumulative repos)
    leaderboard: list       # by stars: dicts name, url, stars, language, stage

    @property
    def live_pct(self):
        return pct(self.live, self.total)

    @property
    def ytd_pct(self):
        return pct(self.created_ytd, self.total)

    def lang_rank(self, language):
        """Index into the color ramp for a listed language, or None."""
        for i, l in enumerate(self.langs):
            if l["name"] == language:
                return i
        return None


def top_languages(df):
    """Top TOP_N languages by repo count; ties by total stars, then name."""
    d = df[df["language"].notna() & ~df["language"].isin(FILTERED_LANGS)]
    g = (
        d.groupby("language")
        .agg(n=("name", "size"), stars=("stars", "sum"),
             live=("stage", lambda s: int((s == "Live").sum())))
        .reset_index()
        .sort_values(["n", "stars", "language"], ascending=[False, False, True])
    )
    classified = len(d)
    top, rest = g.head(TOP_N), g.iloc[TOP_N:]
    langs = [
        {"name": r.language, "n": int(r.n), "pct": pct(r.n, classified),
         "stars": int(r.stars), "live": int(r.live)}
        for r in top.itertuples()
    ]
    other = {"n": int(rest["n"].sum()), "pct": pct(rest["n"].sum(), classified),
             "names": list(rest["language"]), "count": len(rest),
             "all_single": bool(len(rest)) and bool((rest["n"] == 1).all())}
    return langs, other, classified


def snapshot(df, now=None):
    df = df.copy()
    now = now or pd.Timestamp.now(tz="UTC")
    created = pd.to_datetime(df["created_at"], utc=True)
    pushed = pd.to_datetime(df["pushed_at"], utc=True)
    private = df["private"].fillna(True).astype(bool)  # unknown counts as private

    stars = int(df["stars"].sum())
    langs, other, classified = top_languages(df)

    counts = df["stage"].value_counts()
    stages = [(s, int(counts[s])) for s in STAGE_ORDER if counts.get(s, 0)]

    this_year = created[created.dt.year == now.year]
    new_by_month = [
        (calendar.month_abbr[m], int((this_year.dt.month == m).sum()))
        for m in range(1, now.month + 1)
    ]

    push_12m = []
    for k in range(11, -1, -1):
        p = (now - pd.DateOffset(months=k))
        n = int(((pushed.dt.year == p.year) & (pushed.dt.month == p.month)).sum())
        push_12m.append((calendar.month_abbr[p.month], n))

    per_year = created.dt.year.value_counts().sort_index()
    years = range(int(per_year.index.min()), now.year + 1) if len(per_year) else []
    cum, running = [], 0
    for y in years:
        running += int(per_year.get(y, 0))
        cum.append((y, running))

    board = df if SHOW_PRIVATE else df[~private]
    board = board.sort_values(["stars", "name"], ascending=[False, True])
    leaderboard = [
        {"name": r.name, "url": r.url, "stars": int(r.stars),
         "language": r.language if isinstance(r.language, str) else None,
         "stage": r.stage}
        for r in board.itertuples()
    ]

    user = ""
    if len(df):
        m = re.match(r"https://github\.com/([^/]+)/", str(df["url"].iloc[0]))
        user = m.group(1) if m else ""

    return Snapshot(
        user=user, now=now, total=len(df), public=int((~private).sum()),
        private=int(private.sum()), stars=stars,
        live=int((df["stage"] == "Live").sum()),
        archived=int(df["archived"].astype(bool).sum()),
        year=now.year, created_ytd=len(this_year),
        pushed_month=int(((pushed.dt.year == now.year) & (pushed.dt.month == now.month)).sum()),
        star_conc=pct(df["stars"].max(), stars) if len(df) else 0,
        classified=classified, langs=langs, other=other, stages=stages,
        new_by_month=new_by_month, push_12m=push_12m, cum_by_year=cum,
        leaderboard=leaderboard,
    )


def theme(name):
    t = dict(THEMES[name])
    t.setdefault("track", t["border"])
    return t


def ramp(t):
    """One color per listed language, cycling through hero and c2..c5."""
    base = [t["hero"], t["c2"], t["c3"], t["c4"], t["c5"]]
    return [base[i % 5] for i in range(max(TOP_N, 5))]


# --------------------------------------------------------------------------
# Drawing
# --------------------------------------------------------------------------

_ttp = TextToPath()


def font(family, weight="normal", size=12):
    return FontProperties(family=[family, FALLBACK], weight=weight, size=size)


def text_width(s, size, weight="normal", family="Inter"):
    w, _, _ = _ttp.get_text_width_height_descent(s, font(family, weight, size), ismath=False)
    return w


def ellipsize(s, max_w, size, weight="normal", family="Inter"):
    if text_width(s, size, weight, family) <= max_w:
        return s
    while s and text_width(s + "…", size, weight, family) > max_w:
        s = s[:-1]
    return s + "…"


def spark_points(vals, w, h):
    """Sparkline points inside a w x h box (top-left origin), as in the mockup."""
    vals = list(vals) or [0]
    if len(vals) == 1:
        vals = vals * 2
    top = max(vals) or 1
    step = w / (len(vals) - 1)
    return [(i * step, h - 2 - v / top * (h - 6)) for i, v in enumerate(vals)]


class Canvas:
    def __init__(self, w, h, bg, family="Inter"):
        plt.rcParams["svg.fonttype"] = "path"
        self.w, self.h, self.bg, self.family = w, h, bg, family
        self.fig = plt.figure(figsize=(w / 72, h / 72), dpi=72, facecolor=bg)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, w)
        self.ax.set_ylim(h, 0)
        self.ax.axis("off")

    def _box(self, x, y, w, h, r):
        style = f"round,pad=0,rounding_size={min(r, w / 2, h / 2)}" if r else "square,pad=0"
        return FancyBboxPatch((x, y), w, h, boxstyle=style, transform=self.ax.transData)

    def rect(self, x, y, w, h, r=0, fc="none", ec="none", lw=0, z=1):
        p = self._box(x, y, w, h, r)
        p.set(facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z)
        self.ax.add_patch(p)
        return p

    def circle(self, cx, cy, r, color, z=2):
        self.ax.add_patch(Circle((cx, cy), r, color=color, lw=0, zorder=z))

    def gradient(self, x, y, w, h, c0, c1, angle=90, r=0, a0=1.0, a1=1.0, clip=None, z=1):
        """Fill a box with a two-stop gradient. angle follows CSS:
        90 = left to right, 180 = top to bottom, 160 = mostly down, a bit right."""
        if w <= 0 or h <= 0:
            return
        n = 96
        X, Y = np.meshgrid(np.linspace(0, w, n), np.linspace(0, h, n))
        a = np.deg2rad(angle)
        t = X * np.sin(a) - Y * np.cos(a)
        span = t.max() - t.min()
        t = (t - t.min()) / span if span else np.zeros_like(t)
        rgba = ((1 - t)[..., None] * np.array(to_rgba(c0, a0))
                + t[..., None] * np.array(to_rgba(c1, a1)))
        im = self.ax.imshow(rgba, extent=[x, x + w, y + h, y], origin="upper",
                            interpolation="bilinear", aspect="auto", zorder=z)
        im.set_clip_path(clip if clip is not None else self._box(x, y, w, h, r))

    def area_gradient(self, pts, x, y, w, h, color):
        """Sparkline: 2 px line, area under it fading from 50% alpha to 0."""
        px = [(x + a, y + b) for a, b in pts]
        poly = Polygon(px + [(x + w, y + h), (x, y + h)], closed=True, transform=self.ax.transData)
        self.gradient(x, y, w, h, color, color, angle=180, a0=0.5, a1=0, clip=poly, z=3)
        self.ax.plot([p[0] for p in px], [p[1] for p in px], color=color, lw=2,
                     solid_joinstyle="round", solid_capstyle="round", zorder=4)

    def ring(self, cx, cy, r, frac, c0, c1, track, lw):
        """Progress ring from 12 o'clock, clockwise, diagonal stroke gradient."""
        th = np.linspace(0, 2 * np.pi, 200)
        self.ax.plot(cx + r * np.sin(th), cy - r * np.cos(th), color=track, lw=lw, zorder=2)
        if frac <= 0:
            return
        th = np.linspace(0, 2 * np.pi * min(frac, 1), max(int(200 * frac), 2))
        xs, ys = cx + r * np.sin(th), cy - r * np.cos(th)
        segs = [[(xs[i], ys[i]), (xs[i + 1], ys[i + 1])] for i in range(len(xs) - 1)]
        mid = [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in segs]
        # position along the top-left -> bottom-right diagonal of the ring's box
        ts = [min(max(((mx - cx + r) + (my - cy + r)) / (4 * r), 0), 1) for mx, my in mid]
        c0, c1 = np.array(to_rgba(c0)), np.array(to_rgba(c1))
        cols = [(1 - t) * c0 + t * c1 for t in ts]
        self.ax.add_collection(LineCollection(segs, colors=cols, linewidths=lw,
                                              capstyle="round", zorder=3))

    def text(self, x, y, s, size=12, weight="normal", color=None, ha="left",
             family=None, url=None):
        """Text with its baseline at y."""
        t = self.ax.text(x, y, s, fontproperties=font(family or self.family, weight, size),
                         color=color, ha=ha, va="baseline", zorder=5)
        if url:
            t.set_url(url)
        return t

    def width(self, s, size, weight="normal", family=None):
        return text_width(s, size, weight, family or self.family)

    def runs(self, x, y, parts, size, weight="normal", family=None, gap=0):
        """Draw consecutive text runs [(text, color[, weight])] on one baseline."""
        for p in parts:
            s, color = p[0], p[1]
            wt = p[2] if len(p) > 2 else weight
            self.text(x, y, s, size, wt, color, family=family)
            x += self.width(s, size, wt, family) + gap
        return x

    def save(self, path):
        self.ax.set_xlim(0, self.w)
        self.ax.set_ylim(self.h, 0)
        fmt = Path(path).suffix.lstrip(".") or "svg"
        self.fig.savefig(path, format=fmt, facecolor=self.bg,
                         dpi=72 if fmt == "png" else 144, bbox_inches=None)
        plt.close(self.fig)
        if fmt == "svg":
            # matplotlib writes the size in pt; one unit is one px in our layout
            svg = Path(path).read_text(encoding="utf-8")
            svg = re.sub(r'width="[\d.]+pt" height="[\d.]+pt"',
                         f'width="{self.w}" height="{self.h}"', svg, count=1)
            Path(path).write_text(svg, encoding="utf-8")


def fmt_date(ts):
    return f"{ts.day} {calendar.month_abbr[ts.month]} {ts.year}"
