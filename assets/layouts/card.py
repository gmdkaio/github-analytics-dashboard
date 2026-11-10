"""Profile Card layout: header, 4 KPI tiles, top 5 languages | lifecycle + most starred."""
from .common import Canvas, fmt_date, ramp, spark_points, stage_color, ellipsize

W = 1200
PAD_X, PAD_T, PAD_B, GAP = 56, 44, 36, 30


def render(s, t, path, gradients=True):
    H = 660 if gradients else 600
    c = Canvas(W, H, t["bg"])
    R = ramp(t)
    inner = W - 2 * PAD_X

    # --- header ---------------------------------------------------------
    c.text(PAD_X, PAD_T + 12, f"GITHUB.COM/{s.user.upper()}", 12, "semibold", t["muted"])
    c.runs(PAD_X, PAD_T + 53, [("GitHub ", t["text"]), ("Analytics", t["hero"])], 34, "heavy")
    c.text(W - PAD_X, PAD_T + 57, f"Snapshot {fmt_date(s.now)} · forks excluded", 13,
           color=t["muted"], ha="right")

    # --- KPI tiles --------------------------------------------------------
    top = PAD_T + 62 + GAP
    tw = (inner - 3 * 16) / 4
    th = 123 if gradients else 117
    num_dy = 53 if gradients else 50
    lab_dy = 85 if gradients else 79
    sub_dy = 102 if gradients else 96
    pub_stars = [r["stars"] for r in s.leaderboard[:5]]
    tiles = [
        (s.total, t["text"], "Repositories", f"{s.public} public · {s.private} private",
         [v for _, v in s.cum_by_year]),
        (s.stars, t["c2"], "Stars", f"{s.star_conc}% on one repo", None),
        (s.live, t["accent"], "Live repos",
         f"{s.live_pct}% · last push by month" if gradients else f"{s.live_pct}% pushed in last 90 days",
         [v for _, v in s.push_12m]),
        (s.created_ytd, t["hero"], f"Created in {s.year}",
         f"{s.ytd_pct}% of portfolio · YTD by month" if gradients else f"{s.ytd_pct}% of the portfolio, YTD",
         [v for _, v in s.new_by_month]),
    ]
    for i, (num, color, label, sub, series) in enumerate(tiles):
        x = PAD_X + i * (tw + 16)
        c.rect(x, top, tw, th, r=14, fc=t["panel"], ec=t["border"], lw=1)
        c.text(x + 20, top + num_dy, str(num), 40, "heavy", t["text"] if gradients else color)
        c.text(x + 20, top + lab_dy, label, 13, "semibold", t["text"])
        c.text(x + 20, top + sub_dy, sub, 12, color=t["muted"])
        if not gradients:
            continue
        sx, sy = x + tw - 20 - 112, top + 18
        if series is None:  # stars: 5 mini bars, top public repos
            peak = max(pub_stars or [0]) or 1
            bx = x + tw - 20 - (5 * 14 + 4 * 4)
            for j, v in enumerate(pub_stars):
                h = round(v / peak * 44)
                if h:
                    c.gradient(bx + j * 18, sy + 44 - h, 14, h, t["hero"], t["c5"],
                               angle=180, r=min(3, h / 2), z=3)
        else:
            c.area_gradient(spark_points(series, 112, 44), sx, sy, 112, 44, t["hero"])

    # --- bottom: two columns that end on the same line ----------------------
    btop = top + th + GAP
    bbot = H - PAD_B
    lw_ = (inner - 48) * 1.3 / 2.3
    lx, rx = PAD_X, PAD_X + lw_ + 48
    rw = inner - lw_ - 48

    # left: top 5 languages
    c.text(lx, btop + 14, f"Top {len(s.langs)} languages", 15, "bold", t["text"])
    c.text(lx + lw_, btop + 14, f"share of {s.classified} repos", 12, color=t["muted"], ha="right")
    segs = [(l["n"], R[i]) for i, l in enumerate(s.langs)]
    if s.other["n"]:
        segs.append((s.other["n"], t["border"]))
    _segmented_bar(c, lx, btop + 34, lw_, 12, segs)

    foot = ""
    if s.other["n"]:
        each = ", 1 repo each" if s.other["all_single"] else ""
        foot = (f"+{s.other['count']} others{each} ({s.other['pct']}%): "
                + ", ".join(s.other["names"]))
        foot = ellipsize(foot, lw_, 12)
        c.text(lx, bbot - 3, foot, 12, color=t["muted"])

    rows_top, rows_bot = btop + 66, bbot - 33
    n_rows = len(s.langs)
    bar_x = lx + 170 + 14
    bar_w = lw_ - 170 - 40 - 44 - 3 * 14
    bar_h = 8 if gradients else 6
    peak = s.langs[0]["n"] if s.langs else 1
    for i, l in enumerate(s.langs):
        cy = rows_top + 9 + (i * (rows_bot - rows_top - 18) / (n_rows - 1) if n_rows > 1 else 0)
        c.rect(lx, cy - 5, 10, 10, r=3, fc=R[i], z=2)
        c.text(lx + 20, cy + 5, l["name"], 14, "semibold", t["text"])
        c.rect(bar_x, cy - bar_h / 2, bar_w, bar_h, r=bar_h / 2, fc=t["track"], z=2)
        fw = l["n"] / peak * bar_w
        if gradients:
            c.gradient(bar_x, cy - bar_h / 2, fw, bar_h, t["track"], R[i], r=bar_h / 2, z=3)
        else:
            c.rect(bar_x, cy - bar_h / 2, fw, bar_h, r=bar_h / 2, fc=R[i], z=3)
        c.text(bar_x + bar_w + 14 + 40, cy + 5, str(l["n"]), 14, color=t["muted"], ha="right")
        c.text(lx + lw_, cy + 5, f"{l['pct']}%", 14, "bold", t["text"], ha="right")

    # right: lifecycle
    c.text(rx, btop + 14, "Lifecycle", 15, "bold", t["text"])
    stage_cols = [(n, stage_color(t, st)) for st, n in s.stages]
    _segmented_bar(c, rx, btop + 30, rw, 12, stage_cols)
    x = rx
    for st, n in s.stages:
        c.circle(x + 4, btop + 62, 4, stage_color(t, st))
        x = c.runs(x + 16, btop + 67, [(st, t["text"])], 13, gap=8)
        x = c.runs(x, btop + 67, [(str(n), t["muted"])], 13) + 20

    # right: most starred, spread so the last card sits on the bottom line
    c.text(rx, btop + 108, "Most starred", 15, "bold", t["text"])
    top3 = s.leaderboard[:3]
    card_h = 48 if gradients else 37
    n = len(top3)
    gap = min((bbot - btop - 122 - n * card_h) / (n - 1), 40) if n > 1 else 0
    first = bbot - n * card_h - gap * (n - 1)
    peak_s = top3[0]["stars"] if top3 and top3[0]["stars"] else 1
    for i, r in enumerate(top3):
        y = first + i * (card_h + gap)
        c.rect(rx, y, rw, card_h, r=10, fc=t["panel"], ec=t["border"], lw=1)
        name_x = rx + 14
        if not gradients:
            k = s.lang_rank(r["language"])
            c.circle(rx + 18, y + card_h / 2, 4, R[k] if k is not None else t["muted"])
            name_x = rx + 32
        base = y + 10 + 13 if gradients else y + card_h / 2 + 5
        c.text(rx + rw - 14, base, f"★ {r['stars']}", 14, "bold",
               t["text"] if gradients else t["c2"], ha="right")
        name = ellipsize(r["name"], rw - (name_x - rx) - 80, 14, "semibold")
        c.text(name_x, base, name, 14, "semibold", t["text"], url=r["url"])
        if gradients:
            ly = y + 10 + 17 + 8
            c.rect(rx + 14, ly, rw - 28, 3, r=1.5, fc=t["track"], z=2)
            c.gradient(rx + 14, ly, (rw - 28) * r["stars"] / peak_s, 3,
                       t["track"], t["hero"], r=1.5, z=3)

    c.save(path)


def _segmented_bar(c, x, y, w, h, segs):
    """Rounded bar split into segments with 2 px gaps."""
    total = sum(n for n, _ in segs)
    if not total:
        return
    clip = c._box(x, y, w, h, h / 2)
    avail = w - 2 * (len(segs) - 1)
    cx = x
    for n, color in segs:
        sw = n / total * avail
        p = c.rect(cx, y, sw, h, fc=color, z=2)
        p.set_clip_path(clip)
        cx += sw + 2
