"""
Dashboard color themes.

Each theme provides: bg, panel, card, border, text, muted, hero, c2-c5, accent, private.
`hero` and `c2..c5` are the categorical ramp used for treemap/leaderboard/composition
colors (in priority order); `accent` highlights the lifecycle "Live" state; `private`
marks private repos.

To add a new theme, copy one of the blocks below, tweak the hex values, and give it
a key. It becomes selectable immediately via DASHBOARD_THEME=<key>.
"""

THEMES = {
    "divergence": {
        "bg": "#100C08", "panel": "#1A1410", "card": "#221A12", "border": "#2E2620",
        "text": "#D8C7A8", "muted": "#8C7B63",
        "hero": "#FFB000", "c2": "#B5471B", "c3": "#7A2E12", "c4": "#5C4326", "c5": "#6B6157",
        "accent": "#2F6E6A", "private": "#7A2E12",
    },
    "lab": {
        "bg": "#0D1316", "panel": "#131A1E", "card": "#1C252A", "border": "#2C3A3F",
        "text": "#D6D9C8", "muted": "#7E8A82",
        "hero": "#6FA981", "c2": "#E8A317", "c3": "#A8432E", "c4": "#3E7C6A", "c5": "#5E6E6A",
        "accent": "#E8A317", "private": "#A8432E",
    },
    "github": {
        "bg": "#0D1117", "panel": "#161B22", "card": "#21262D", "border": "#30363D",
        "text": "#C9D1D9", "muted": "#8B949E",
        "hero": "#58A6FF", "c2": "#3FB950", "c3": "#A371F7", "c4": "#F0883E", "c5": "#6E7681",
        "accent": "#3FB950", "private": "#A371F7",
    },
}

DEFAULT_THEME = "divergence"
