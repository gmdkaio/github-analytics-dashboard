import logging

import pandas as pd

from .layouts import bento, card, terminal
from .layouts.common import THEMES, snapshot, theme as load_theme

logger = logging.getLogger(__name__)

# layout key -> (renderer, default theme)
LAYOUTS = {
    "card": (card.render, "redline"),
    "bento": (bento.render, "mono"),
    "terminal": (terminal.render, "phosphor"),
}


def create_dashboard(df: pd.DataFrame, output_path: str = "github_dashboard.svg",
                     theme: str = "", layout: str = "card", gradients: bool = True):
    if layout not in LAYOUTS:
        raise ValueError(f"Unknown layout {layout!r}, expected one of {', '.join(LAYOUTS)}")
    render, default_theme = LAYOUTS[layout]
    if theme and theme not in THEMES:
        raise ValueError(f"Unknown theme {theme!r}, expected one of {', '.join(THEMES)}")
    theme = theme or default_theme

    render(snapshot(df), load_theme(theme), output_path, gradients=gradients)
    logger.info(f"Dashboard saved to {output_path} (layout={layout}, theme={theme}, gradients={gradients})")
