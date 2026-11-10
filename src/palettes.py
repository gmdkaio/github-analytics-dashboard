"""
Dashboard color themes.

Each theme provides: bg, panel, card, border, text, muted, hero, c2-c5, accent, private.
`hero` and `c2..c5` are the categorical ramp used for the top 5 languages (rank order),
leaderboard dots and composition colors; `accent` highlights the lifecycle "Live" state;
`private` marks private repos.

Optional keys (new):
  track  -> background of empty bar/progress tracks (falls back to `border`)
  prog   -> lifecycle "In progress" color (falls back to `hero`)
  stub   -> lifecycle "Stub" color (falls back to `muted`)

To add a new theme, copy one of the blocks below, tweak the hex values, and give it
a key. It becomes selectable immediately via DASHBOARD_THEME=<key>.
"""

THEMES = {
    # --- Original themes -------------------------------------------------
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

    # --- New themes (redesign) -------------------------------------------
    # Cool slate, ice-blue lead. Used by the Profile Card layout.
    "frost": {
        "bg": "#0E141B", "panel": "#141B24", "card": "#1A232E", "border": "#283442",
        "text": "#DCE4EC", "muted": "#8696A7",
        "hero": "#7CC4F2", "c2": "#F2B872", "c3": "#B394E8", "c4": "#E8798A", "c5": "#CFCB7A",
        "accent": "#5FD3A3", "private": "#B394E8", "track": "#202B37",
    },
    # Black > grey > white, no hue. Used by the Bento Grid layout (with gradients).
    "mono": {
        "bg": "#0A0A0A", "panel": "#121212", "card": "#181818", "border": "#262626",
        "text": "#F2F2F2", "muted": "#8C8C8C",
        "hero": "#FFFFFF", "c2": "#C4C4C4", "c3": "#969696", "c4": "#6B6B6B", "c5": "#4D4D4D",
        "accent": "#FFFFFF", "private": "#969696", "track": "#1E1E1E",
        "prog": "#A6A6A6", "stub": "#4D4D4D",
    },
    # CRT green on near-black. Used by the Terminal layout.
    "phosphor": {
        "bg": "#070C08", "panel": "#0C140D", "card": "#101B12", "border": "#1D3020",
        "text": "#B9F5B4", "muted": "#6E9F68",
        "hero": "#39FF7A", "c2": "#FFB940", "c3": "#3FD0FF", "c4": "#C38BFF", "c5": "#FF5F87",
        "accent": "#39FF7A", "private": "#FFB940", "track": "#142416",
    },
    # Neutral black, lime lead, loud accents.
    "graphite": {
        "bg": "#101010", "panel": "#171717", "card": "#1E1E1E", "border": "#2D2D2D",
        "text": "#EDEDED", "muted": "#9B9B9B",
        "hero": "#C6F24E", "c2": "#FF7A45", "c3": "#F25EA3", "c4": "#B98CFF", "c5": "#F2D24E",
        "accent": "#4EC9F2", "private": "#FF7A45", "track": "#262626",
    },
    # Deep plum, coral lead, mint for Live.
    "dusk": {
        "bg": "#140F1C", "panel": "#1C1528", "card": "#241B33", "border": "#33284A",
        "text": "#EDE6F7", "muted": "#A397B8",
        "hero": "#FF8A65", "c2": "#B69CFF", "c3": "#FFD166", "c4": "#7AA2FF", "c5": "#F47FB8",
        "accent": "#6EE7C8", "private": "#B69CFF", "track": "#2A2140",
    },
    # Light theme for GitHub light mode.
    "daylight": {
        "bg": "#F4F5F7", "panel": "#FFFFFF", "card": "#FFFFFF", "border": "#DCE0E6",
        "text": "#14181E", "muted": "#5A6371",
        "hero": "#2B59C3", "c2": "#E07A1F", "c3": "#8A55D6", "c4": "#D2436B", "c5": "#C9A227",
        "accent": "#1E8E5A", "private": "#8A55D6", "track": "#E8EBEF",
    },

    # --- Anime / cyberpunk ------------------------------------------------
    # Red terminal with nixie-tube amber, after the Steins;Gate divergence meter.
    "worldline": {
        "bg": "#0B0505", "panel": "#140A0A", "card": "#1C0E0E", "border": "#3A1618",
        "text": "#F2DCD2", "muted": "#9C716A",
        "hero": "#FF3B3B", "c2": "#FFB03A", "c3": "#B81D31", "c4": "#6FB7B0", "c5": "#7D5C54",
        "accent": "#FF8A1F", "private": "#B81D31", "track": "#211012",
    },
    # Night-city neon on deep blue, sampled from Cyberpunk: Edgerunners (season 1).
    "edgerunner": {
        "bg": "#03060F", "panel": "#071226", "card": "#0B1A33", "border": "#1B2D52",
        "text": "#E6FBFF", "muted": "#7A93B8",
        "hero": "#FAFF00", "c2": "#FF2BD6", "c3": "#00E5FF", "c4": "#8A5CFF", "c5": "#3E6FA8",
        "accent": "#00F0FF", "private": "#FF2BD6", "track": "#0E1E3A",
    },
    # Netrunning HUD from Cyberpunk: Edgerunners: coral-red panels on dark teal,
    # peach code cells, Lucy's lavender, David's yellow, the green CALL button for Live.
    "redline": {
        "bg": "#0C1214", "panel": "#121A1D", "card": "#18222A", "border": "#4A2A2E",
        "text": "#F6E6E1", "muted": "#8E9C9E",
        "hero": "#FF4A4A", "c2": "#FFB4A2", "c3": "#C9B8F0", "c4": "#FFD23F", "c5": "#B0303A",
        "accent": "#3DDC84", "private": "#C9B8F0", "track": "#1E2A2E",
    },
}


DEFAULT_THEME = "divergence"


def stage_color(theme: dict, stage: str) -> str:
    """Lifecycle color with fallbacks for themes that don't define prog/stub."""
    if stage == "Live":
        return theme["accent"]
    if stage == "In progress":
        return theme.get("prog", theme["hero"])
    if stage == "Archived":
        return theme["c4"]
    return theme.get("stub", theme["muted"])
