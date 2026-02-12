import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import logging
import re

logger = logging.getLogger(__name__)


def create_dashboard(df: pd.DataFrame, output_path: str = "github_dashboard.svg"):
    BG = "#0d1117"
    PANEL = "#161b22"
    CARD = "#21262d"
    BORDER = "#30363d"
    TEXT = "#c9d1d9"
    TEXT_MUTED = "#8b949e"
    BLUE = "#58a6ff"
    GREEN = "#3fb950"
    YELLOW = "#e3b341"
    PURPLE = "#a371f7"
    ORANGE = "#f0883e"
    PINK = "#db61a2"

    sns.set_theme(style="dark")
    plt.rcParams.update({
        "figure.facecolor": BG,
        "axes.facecolor": PANEL,
        "axes.edgecolor": BORDER,
        "axes.labelcolor": TEXT,
        "xtick.color": TEXT,
        "ytick.color": TEXT,
        "text.color": TEXT,
        "grid.color": BORDER,
        "axes.titleweight": "bold",
        "font.size": 10,
        "font.family": "sans-serif",
    })

    df = df.copy()

    total_repos = len(df)
    active_repos = int(df["is_active"].sum())
    inactive_repos = total_repos - active_repos
    total_stars = int(df["stars"].sum())
    total_languages = int(df["language"].nunique())
    private_repos = int(df["private"].sum())
    public_repos = total_repos - private_repos

    repos_per_year = (
        df.groupby("year_created")
        .size()
        .reset_index(name="count")
        .sort_values("year_created")
    )

    lang_counts = (
        df[df["language"].notna()]
        .groupby("language")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(8)
    )

    fig = plt.figure(figsize=(20, 14), facecolor=BG)
    gs = fig.add_gridspec(5, 6, height_ratios=[1.2, 1.5, 1.5, 1.5, 1.5], 
                          hspace=0.5, wspace=0.35, top=0.93, bottom=0.05, 
                          left=0.05, right=0.95)

    def create_kpi_card(ax, value, label, color):
        ax.axis("off")
        rect = FancyBboxPatch((0.08, 0.15), 0.84, 0.7, 
                              boxstyle="round,pad=0.08",
                              facecolor=CARD, edgecolor=color, 
                              linewidth=2.5, transform=ax.transAxes)
        ax.add_patch(rect)
        
        ax.text(0.5, 0.55, str(value), ha="center", va="center",
                fontsize=36, weight="bold", color=color, transform=ax.transAxes)
        ax.text(0.5, 0.28, label, ha="center", va="center",
                fontsize=12, color=TEXT_MUTED, weight="600", transform=ax.transAxes)

    ax_kpi1 = fig.add_subplot(gs[0, 0:2])
    create_kpi_card(ax_kpi1, total_repos, "TOTAL REPOS", BLUE)
    
    ax_kpi2 = fig.add_subplot(gs[0, 2:4])
    create_kpi_card(ax_kpi2, active_repos, "ACTIVE", GREEN)
    
    ax_kpi3 = fig.add_subplot(gs[0, 4])
    create_kpi_card(ax_kpi3, total_stars, "STARS", YELLOW)
    
    ax_kpi4 = fig.add_subplot(gs[0, 5])
    create_kpi_card(ax_kpi4, total_languages, "LANGUAGES", PURPLE)

    ax1 = fig.add_subplot(gs[1, :])
    ax1.plot(repos_per_year["year_created"], repos_per_year["count"],
             marker="o", linewidth=3.5, markersize=10, color=BLUE, 
             markerfacecolor=BLUE, markeredgecolor=BG, markeredgewidth=2)
    ax1.fill_between(repos_per_year["year_created"], repos_per_year["count"], 
                     alpha=0.2, color=BLUE)
    ax1.set_title("Repository Growth Timeline", fontsize=15, pad=15, weight="bold")
    ax1.set_xlabel("Year", fontsize=11, weight="600")
    ax1.set_ylabel("Repositories", fontsize=11, weight="600")
    ax1.grid(alpha=0.2, linestyle='--')

    ax2 = fig.add_subplot(gs[2:4, 0:2])
    colors = [BLUE, GREEN, PURPLE, ORANGE, YELLOW, PINK, "#bc4c00", "#8957e5"]
    wedges, texts, autotexts = ax2.pie(
        lang_counts["count"], 
        labels=lang_counts["language"],
        colors=colors[:len(lang_counts)],
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.82,
        wedgeprops=dict(width=0.5, edgecolor=BG, linewidth=2),
        textprops={'color': TEXT, 'fontsize': 11, 'weight': '600'}
    )
    for autotext in autotexts:
        autotext.set_color(BG)
        autotext.set_fontsize(11)
        autotext.set_weight('bold')
    ax2.set_title("Language Distribution", fontsize=15, pad=15, weight="bold")

    # Professional table for recently updated repos
    ax3 = fig.add_subplot(gs[2:4, 2:4])
    ax3.axis('off')
    
    # Get top 5 recent repos with URL if available
    cols_to_select = ['name', 'days_since_last_push']
    if 'url' in df.columns:
        cols_to_select.insert(1, 'url')
    
    recent_repos = df.nsmallest(5, 'days_since_last_push')[cols_to_select].copy()
    
    # Title
    ax3.text(0.5, 0.95, "Most Recently Updated", ha='center', fontsize=16, 
            weight='bold', color=TEXT, transform=ax3.transAxes)
    
    # Column headers
    header_y = 0.87
    ax3.text(0.08, header_y, "Name", fontsize=13, weight='bold', color=TEXT_MUTED, transform=ax3.transAxes)
    ax3.text(0.92, header_y, "Last Update", fontsize=13, weight='bold', color=TEXT_MUTED, transform=ax3.transAxes, ha='right')
    
    # Header line
    ax3.plot([0.08, 0.92], [header_y - 0.025, header_y - 0.025], color=BORDER, linewidth=2, transform=ax3.transAxes)
    
    # Table rows
    row_height = 0.14
    start_y = header_y - 0.08
    
    for i, (_, row) in enumerate(recent_repos.iterrows()):
        y_pos = start_y - (i * row_height)
        
        # Subtle separator line
        if i > 0:
            ax3.plot([0.08, 0.92], [y_pos + 0.07, y_pos + 0.07], color=BORDER, linewidth=0.5, alpha=0.3, transform=ax3.transAxes)
        
        # Name
        ax3.text(0.08, y_pos, row['name'], fontsize=12, weight='600', 
                color=TEXT, transform=ax3.transAxes, va='center')
        
        # Last update
        days = int(row['days_since_last_push'])
        if days == 0:
            time_text = "Today"
        elif days == 1:
            time_text = "1 day ago"
        else:
            time_text = f"{days} days ago"
        ax3.text(0.92, y_pos, time_text, fontsize=12,
                color=TEXT_MUTED, transform=ax3.transAxes, va='center', ha='right')
    
    # Professional table for top starred repos
    ax7 = fig.add_subplot(gs[2:4, 4:6])
    ax7.axis('off')
    
    # Get top 5 starred repos with URL if available
    cols_to_select_stars = ['name', 'stars']
    if 'url' in df.columns:
        cols_to_select_stars.insert(1, 'url')
    
    top_starred = df.nlargest(5, 'stars')[cols_to_select_stars].copy()
    
    # Title
    ax7.text(0.5, 0.95, "Top Repos by Stars", ha='center', fontsize=16, 
            weight='bold', color=TEXT, transform=ax7.transAxes)
    
    # Column headers
    header_y = 0.87
    ax7.text(0.08, header_y, "Name", fontsize=13, weight='bold', color=TEXT_MUTED, transform=ax7.transAxes)
    ax7.text(0.92, header_y, "Stars", fontsize=13, weight='bold', color=TEXT_MUTED, transform=ax7.transAxes, ha='right')
    
    # Header line
    ax7.plot([0.08, 0.92], [header_y - 0.025, header_y - 0.025], color=BORDER, linewidth=2, transform=ax7.transAxes)
    
    # Table rows
    row_height = 0.14
    start_y = header_y - 0.08
    
    for i, (_, row) in enumerate(top_starred.iterrows()):
        y_pos = start_y - (i * row_height)
        
        # Subtle separator line
        if i > 0:
            ax7.plot([0.08, 0.92], [y_pos + 0.07, y_pos + 0.07], color=BORDER, linewidth=0.5, alpha=0.3, transform=ax7.transAxes)
        
        # Name
        ax7.text(0.08, y_pos, row['name'], fontsize=12, weight='600', 
                color=TEXT, transform=ax7.transAxes, va='center')
        
        # Stars with icon
        ax7.text(0.92, y_pos, f"★ {int(row['stars'])}", fontsize=12, 
                color=YELLOW, transform=ax7.transAxes, va='center', ha='right')

    ax4 = fig.add_subplot(gs[4, 0:2])
    sns.histplot(df["size_mb"], bins=15, kde=True, color=PURPLE, 
                 ax=ax4, edgecolor=BG, linewidth=1.5, alpha=0.8)
    ax4.set_title("Size Distribution", fontsize=15, pad=15, weight="bold")
    ax4.set_xlabel("Size (MB)", fontsize=11, weight="600")
    ax4.set_ylabel("Repos", fontsize=11, weight="600")
    ax4.grid(alpha=0.2)

    ax6 = fig.add_subplot(gs[4, 2:4])
    sns.histplot(df["stars"], bins=10, kde=True, color=YELLOW, 
                 ax=ax6, edgecolor=BG, linewidth=1.5, alpha=0.8)
    ax6.set_title("Stars Distribution", fontsize=15, pad=15, weight="bold")
    ax6.set_xlabel("Stars", fontsize=11, weight="600")
    ax6.set_ylabel("Repos", fontsize=11, weight="600")
    ax6.grid(alpha=0.2)

    ax5 = fig.add_subplot(gs[4, 4:6])
    sns.histplot(df["days_since_last_push"], bins=20, kde=True,
                 color=ORANGE, ax=ax5, edgecolor=BG, linewidth=1.5, alpha=0.8)
    ax5.set_title("Days Since Push", fontsize=15, pad=15, weight="bold")
    ax5.set_xlabel("Days", fontsize=11, weight="600")
    ax5.set_ylabel("Repos", fontsize=11, weight="600")
    ax5.grid(alpha=0.2)

    for ax in [ax1, ax2, ax3, ax4, ax5, ax6, ax7]:
        ax.set_facecolor(PANEL)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(BORDER)
        ax.spines["bottom"].set_color(BORDER)
        ax.tick_params(colors=TEXT)

    fig.suptitle("GitHub Analytics", fontsize=32, weight="bold", 
                 color=TEXT, y=0.98, fontfamily='sans-serif')

    plt.savefig(output_path, format="svg", facecolor=fig.get_facecolor(), 
                bbox_inches='tight', pad_inches=0.3)
    plt.close()

    # Post-process SVG to add clickable links
    add_clickable_links(output_path, recent_repos, top_starred)

    logger.info(f"Dashboard saved to {output_path}")


def add_clickable_links(svg_path: str, recent_repos: pd.DataFrame, top_starred: pd.DataFrame):
    """Add clickable hyperlinks to repository names in the SVG"""
    if 'url' not in recent_repos.columns and 'url' not in top_starred.columns:
        logger.warning("URL column not found, skipping clickable links")
        return
    
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    
    # Combine both dataframes for linking
    all_repos = pd.concat([recent_repos, top_starred]).drop_duplicates(subset=['name'])
    
    for _, row in all_repos.iterrows():
        repo_name = row['name']
        repo_url = row['url']
        
        # Find text elements containing the repo name
        # Match the exact repo name in text elements
        pattern = f'(<text[^>]*>)({re.escape(repo_name)})(</text>)'
        
        # Replace with linked version - using xlink:href for SVG compatibility
        replacement = f'<a xlink:href="{repo_url}" target="_blank">\\1\\2\\3</a>'
        svg_content = re.sub(pattern, replacement, svg_content, count=1)
    
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    logger.info(f"Added clickable links to {len(all_repos)} repositories")
