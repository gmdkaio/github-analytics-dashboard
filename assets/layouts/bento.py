"""Bento Grid layout: 4-column grid of tiles."""
import math

from .common import Canvas, ellipsize, fmt_date, ramp, stage_color

W, H = 1200, 840
PAD, GAP, COL = 40, 16, (1200 - 80 - 3 * 16) / 4
HEAD = "Space Grotesk"


def render(s, t, path, gradients=True):
    c = Canvas(W, H, t["bg"])
    R = ramp(t)

    def tile(col, row, cols, rows):
        x = PAD + col * (COL + GAP)
        y = grid_top + sum(row_h[:row]) + row * GAP
        w = cols * COL + (cols - 1) * GAP
        h = sum(row_h[row:row + rows]) + (rows - 1) * GAP
        if gradients:
            c.gradient(x, y, w, h, t["card"], t["bg"], angle=160, r=18)
            c.rect(x, y, w, h, r=18, ec=t["border"], lw=1, z=2)
        else:
            c.rect(x, y, w, h, r=18, fc=t["panel"], ec=t["border"], lw=1)
        return x, y, w, h

    def bar(x, y, w, h, frac, color):
        c.rect(x, y, w, h, r=h / 2, fc=t["track"], z=3)
        if gradients:
            c.gradient(x, y, w * frac, h, t["track"], color, r=h / 2, z=4)
        else:
            c.rect(x, y, w * frac, h, r=h / 2, fc=color, z=4)

    # --- header ---------------------------------------------------------
    c.runs(PAD, PAD + 29, [(f"{s.user} ", t["text"]), ("/ analytics", t["hero"])], 30, "bold", HEAD)
    pills = [(f"{s.total} repos", t["text"]), (f"{s.public} public · {s.private} private", t["text"]),
             (fmt_date(s.now), t["muted"])]
    x = W - PAD
    for label, color in reversed(pills):
        pw = c.width(label, 12, "semibold") + 24
        x -= pw
        c.rect(x, PAD + 5, pw, 27, r=13.5, ec=t["border"], lw=1)
        c.text(x + 12, PAD + 23, label, 12, "semibold", color)
        x -= 8

    grid_top = PAD + 38 + 20
    row_h = [172, 172, H - PAD - grid_top - 2 * 172 - 2 * GAP]

    # --- top 5 languages (2 x 2) -----------------------------------------
    x, y, w, h = tile(0, 0, 2, 2)
    c.text(x + 24, y + 24 + 17, f"Top {len(s.langs)} languages", 18, "semibold", t["text"], family=HEAD)
    c.text(x + w - 24, y + 24 + 17, "repos · stars · live", 12, color=t["muted"], ha="right")
    row_hgt = 32
    area_top, area_bot = y + 24 + 22 + 16, y + h - 24 - 15 - 16
    n = max(len(s.langs), 1)
    row_gap = min(14, (area_bot - area_top - n * row_hgt) / max(n - 1, 1))
    block = n * row_hgt + (n - 1) * row_gap
    ry = area_top + (area_bot - area_top - block) / 2
    bw = w - 48 - 2 * 46 - 2 * 12
    peak = s.langs[0]["n"] if s.langs else 1
    for i, l in enumerate(s.langs):
        yy = ry + i * (row_hgt + row_gap)
        c.text(x + 24, yy + 12, l["name"], 13, "semibold", t["text"])
        c.text(x + 24 + bw, yy + 12, f"{l['n']} · {l['pct']}%", 13, color=t["muted"], ha="right")
        bar(x + 24, yy + 22, bw, 10, l["n"] / peak, R[i])
        c.text(x + w - 24 - 46 - 12, yy + 24, f"★ {l['stars']}", 13, "semibold", t["text"], ha="right")
        c.text(x + w - 24, yy + 24, str(l["live"]), 13, "semibold", t["accent"], ha="right")
    if s.other["n"]:
        c.text(x + 24, y + h - 24 - 3,
               f"Other {s.other['count']} languages = {s.other['pct']}% of {s.classified} classified repos",
               12, color=t["muted"])

    # --- stars --------------------------------------------------------------
    x, y, w, h = tile(2, 0, 1, 1)
    c.text(x + 22, y + 22 + 13, "Stars", 13, "semibold", t["muted"])
    c.text(x + 22, y + h / 2 + 22, str(s.stars), 56, "bold", t["hero"], family=HEAD)
    if s.leaderboard:
        top = s.leaderboard[0]
        c.text(x + 22, y + h - 22 - 3,
               ellipsize(f"{top['stars']} on {top['name']}", w - 44, 12), 12, color=t["muted"])

    # --- live ring ------------------------------------------------------------
    x, y, w, h = tile(3, 0, 1, 1)
    r_cx, r_cy = x + 22 + 48, y + h / 2
    frac = s.live / s.total if s.total else 0
    c.ring(r_cx, r_cy, 38.4, frac, t["accent"], t["c4"] if gradients else t["accent"], t["track"], 12)
    tx = x + 22 + 96 + 16
    c.text(tx, r_cy - 8, str(s.live), 36, "bold", t["text"], family=HEAD)
    c.text(tx, r_cy + 14, "Live", 13, "semibold", t["text"])
    c.text(tx, r_cy + 31, f"{s.live_pct}% · pushed <90d", 12, color=t["muted"])

    # --- lifecycle waffle --------------------------------------------------
    x, y, w, h = tile(2, 1, 2, 1)
    per = max(math.ceil(s.total / 45), 1)
    unit = "repo" if per == 1 else f"{per} repos"
    c.text(x + 22, y + 22 + 14, f"Lifecycle · one square per {unit}", 16, "semibold", t["text"], family=HEAD)
    lx = x + w - 22
    for st, n in reversed(s.stages):
        label = f"{st} {n}"
        lx -= c.width(label, 12)
        c.text(lx, y + 22 + 14, label, 12, color=t["text"])
        lx -= 14
        c.rect(lx, y + 22 + 6, 8, 8, r=2, fc=stage_color(t, st), z=3)
        lx -= 14
    cells = [stage_color(t, st) for st, n in s.stages for _ in range(math.ceil(n / per))]
    cw = (w - 44 - 14 * 6) / 15
    rows = max(math.ceil(len(cells) / 15), 1)
    gy = y + 22 + 20 + 14
    ch = min(26, (y + h - 22 - gy - (rows - 1) * 6) / rows)
    for i, color in enumerate(cells):
        c.rect(x + 22 + (i % 15) * (cw + 6), gy + (i // 15) * (ch + 6), cw, ch,
               r=min(5, ch / 3), fc=color, z=3)

    # --- new repos per month ------------------------------------------------
    x, y, w, h = tile(0, 2, 2, 1)
    months = s.new_by_month
    peak_i = max(range(len(months)), key=lambda i: months[i][1])
    peak_label, peak_n = months[peak_i]
    c.text(x + 24, y + 24 + 14, f"New repos per month, {s.year}", 16, "semibold", t["text"], family=HEAD)
    note = f"{s.created_ytd} YTD" + (f" · peak {peak_label} ({peak_n})" if peak_n else "")
    c.text(x + w - 24, y + 24 + 14, note, 12, color=t["muted"], ha="right")
    base = y + h - 24 - 14 - 6       # bottom of the bars
    max_h = base - (y + 24 + 20 + 14) - 17 - 6
    mw = (w - 48 - (len(months) - 1) * 10) / len(months)
    for i, (label, n) in enumerate(months):
        mx = x + 24 + i * (mw + 10)
        bh = max(4, n / (peak_n or 1) * max_h)
        if gradients:
            c0, c1 = (t["hero"], t["c4"]) if i == peak_i and peak_n else (t["c3"], t["track"])
            c.gradient(mx, base - bh, mw, bh, c0, c1, angle=180, r=min(6, mw / 2), z=3)
        else:
            c.rect(mx, base - bh, mw, bh, r=min(6, mw / 2),
                   fc=t["hero"] if i == peak_i and peak_n else t["c3"], z=3)
        c.text(mx + mw / 2, base - bh - 6, str(n), 11, "semibold", t["text"], ha="center")
        c.text(mx + mw / 2, base + 6 + 11, label, 11, color=t["muted"], ha="center")

    # --- leaderboard ----------------------------------------------------------
    x, y, w, h = tile(2, 2, 2, 1)
    c.text(x + 24, y + 24 + 14, "Leaderboard", 16, "semibold", t["text"], family=HEAD)
    ry = y + 24 + 20 + 4 + 10
    for i, r in enumerate(s.leaderboard[:5]):
        yy = ry + i * 43
        c.ax.plot([x + 24, x + w - 24], [yy, yy], color=t["border"], lw=1, zorder=3)
        base = yy + 8 + 14
        c.text(x + 24, base, str(i + 1), 13, "bold", t["muted"])
        k = s.lang_rank(r["language"])
        c.circle(x + 24 + 32 + 4, base - 4.5, 4, R[k] if k is not None else t["muted"], z=4)
        pill_x = x + w - 24 - 52 - 10 - 96
        name_x = x + 24 + 32 + 16
        c.text(name_x, base, ellipsize(r["name"], pill_x - 10 - name_x, 13, "semibold"),
               13, "semibold", t["text"], url=r["url"])
        sc = stage_color(t, r["stage"])
        pw = c.width(r["stage"], 11, "semibold") + 16
        c.rect(pill_x, base - 14, pw, 20, r=10, ec=sc, lw=1, z=3)
        c.text(pill_x + 8, base, r["stage"], 11, "semibold", sc)
        c.text(x + w - 24, base, f"★ {r['stars']}", 13, "bold", t["text"], ha="right")

    c.save(path)
