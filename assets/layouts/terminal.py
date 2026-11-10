"""Terminal layout: monospace text, block-glyph bars."""
import calendar

from .common import TOP_N, Canvas, ellipsize, ramp, stage_color

W, H = 1200, 700
PX, PT = 44, 36
LINE = 14 * 1.55
CH = 14 * 0.6          # JetBrains Mono advance width at 14 px
MONO = "JetBrains Mono"


def shade(n):
    return "·" if n == 0 else "░" if n <= 2 else "▒" if n <= 3 else "▓" if n <= 6 else "█"


def render(s, t, path, gradients=True):
    c = Canvas(W, H, t["bg"], family=MONO)
    R = ramp(t)
    prompt = [(f"{s.user}@github", t["hero"]), (":~$", t["muted"])]

    # --- prompt -------------------------------------------------------------
    y = PT + 16
    c.runs(PX, y, prompt + [(f" gh-analytics --top-langs {TOP_N} --exclude-forks", t["text"])], 14)
    y += LINE + 4
    c.text(PX, y, f"snapshot {s.now:%Y-%m-%d} · {s.total} repos scanned · {s.archived} archived",
           14, color=t["muted"])

    # --- KPI strip ------------------------------------------------------------
    top = PT + 2 * LINE + 4 + 22
    cw, ch = (W - 2 * PX) / 5, 82
    c.rect(PX, top, W - 2 * PX, ch, ec=t["border"], lw=1)
    cells = [
        (str(s.total), t["hero"], "repos"),
        (str(s.stars), t["c2"], "stars"),
        (str(s.live), t["accent"], "live (<90d)"),
        (f"{s.public}/{s.private}", t["text"], "public/private"),
        (str(s.pushed_month), t["c3"], f"pushed in {calendar.month_abbr[s.now.month]}"),
    ]
    for i, (num, color, label) in enumerate(cells):
        x = PX + i * cw
        if i:
            c.ax.plot([x, x], [top, top + ch], color=t["border"], lw=1, zorder=2)
        c.text(x + 18, top + 14 + 27, num, 30, "heavy", color)
        c.text(x + 18, top + 63, label, 12, color=t["muted"])

    # --- languages | lifecycle + last push -------------------------------------
    ctop = top + ch + 22
    lw_ = (W - 2 * PX - 48) * 1.15 / 2.15
    lx, rx = PX, PX + lw_ + 48

    def heading(x, y, title, note=""):
        end = c.runs(x, y, [(title, t["text"], "heavy")], 14)
        if note:
            c.text(end + CH, y, note, 14, color=t["muted"])

    heading(lx, ctop + 16, "## LANGUAGES", f"top {len(s.langs)} of {s.classified}")
    peak = s.langs[0]["n"] if s.langs else 1
    rows = [(l["name"], "█" * max(1, round(l["n"] / peak * 24)), R[i], l["n"], l["pct"], t["text"])
            for i, l in enumerate(s.langs)]
    if s.other["n"]:
        rows.append((f"other ({s.other['count']})", "░" * max(1, round(s.other["n"] / peak * 24)),
                     t["muted"], s.other["n"], s.other["pct"], t["muted"]))
    y = ctop + 16 + LINE + 6
    for name, blocks, color, n, p, name_color in rows:
        c.text(lx, y, name, 14, color=name_color)
        c.text(lx + 180, y, blocks, 14, color=color)
        c.text(lx + lw_ - 58, y, str(n), 14, color=name_color, ha="right")
        c.text(lx + lw_, y, f"{p}%", 14, color=t["muted"], ha="right")
        y += LINE + 4
    left_end = y

    heading(rx, ctop + 16, "## LIFECYCLE")
    peak_st = max([n for _, n in s.stages] or [1])
    y = ctop + 16 + LINE + 6
    for st, n in s.stages:
        c.text(rx, y, st.lower(), 14, color=t["text"])
        c.text(rx + 130, y, "█" * round(n / peak_st * 20), 14, color=stage_color(t, st))
        c.text(W - PX, y, str(n), 14, color=t["text"], ha="right")
        y += LINE + 4

    y += 18 - 4
    heading(rx, y + 16, "## LAST PUSH", "repos by month, 12m")
    gy = y + 16 + LINE + 6
    for i, (label, n) in enumerate(s.push_12m):
        cx = rx + i * 40 + 17
        c.text(cx, gy + 20, shade(n), 26, color=t["muted"] if n == 0 else t["hero"], ha="center")
        c.text(cx, gy + 38, label, 11, color=t["muted"], ha="center")
    right_end = gy + 46

    # --- most starred ---------------------------------------------------------
    y = max(left_end, right_end) + 22
    heading(PX, y, "## MOST STARRED")
    y += LINE + 6
    sq_x = PX + 36 + 320 + 120 + 140 + 40
    max_sq = int((W - PX - 70 - sq_x) / CH)
    for i, r in enumerate(s.leaderboard[:5]):
        k = s.lang_rank(r["language"])
        c.text(PX, y, f"{i + 1}.", 14, color=t["muted"])
        c.text(PX + 46, y, ellipsize(r["name"], 320, 14, "semibold", MONO), 14, "semibold",
               t["text"], url=r["url"])
        c.text(PX + 376, y, (r["language"] or "-").lower(), 14,
               color=R[k] if k is not None else t["muted"])
        c.text(PX + 506, y, f"[{r['stage'].lower()}]", 14, color=stage_color(t, r["stage"]))
        c.text(sq_x, y, "■" * min(r["stars"], max_sq), 14, color=t["c2"])
        c.text(W - PX, y, f"★{r['stars']}", 14, "semibold", t["text"], ha="right")
        y += LINE + 2

    y = max(y + 10, min(y + 10 + 2 * LINE, H - PT - 4))  # two blank lines, kept inside the padding
    end = c.runs(PX, y, prompt, 14)
    c.rect(end + CH, y - 14, 9, 17, fc=t["hero"], z=3)

    c.save(path)
