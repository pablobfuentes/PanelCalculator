"""Main Plotly canvas helpers — Phase 4.1.3."""

from __future__ import annotations

import streamlit as st

from core.columns import apply_obstacle_exclusions, resolve_columns
from core.layout import Rect
from core.tributary import (
    compute_tributary_zones,
    enrich_tributary_loads,
    parse_obstacle_zones,
)
from core.visualization import build_layout_figure
from ui.layout_state import ResolvedLayout


def build_tributary_columns(
    layout: ResolvedLayout,
    *,
    column_count_x: int,
    column_count_y: int,
    column_overrides_text: str = "",
    obstacle_zones_text: str = "",
) -> tuple[list, list[Rect]]:
    """Compute zoned columns with loads; return (columns, obstacle_rects)."""
    obstacles = (
        parse_obstacle_zones(obstacle_zones_text) if obstacle_zones_text.strip() else []
    )
    columns = resolve_columns(
        layout.panels,
        count_x=column_count_x,
        count_y=column_count_y,
        overrides_text=column_overrides_text,
    )
    columns = apply_obstacle_exclusions(columns, obstacles)
    zoned = enrich_tributary_loads(
        compute_tributary_zones(columns, layout.panels),
        layout.panel,
    )
    return zoned, obstacles


def render_layout_canvas(
    layout: ResolvedLayout,
    *,
    column_count_x: int | None = None,
    column_count_y: int | None = None,
    column_overrides_text: str = "",
    obstacle_zones_text: str = "",
    show_tributary: bool,
    title: str,
) -> tuple[list | None, list[Rect]]:
    """Interactive Plotly canvas: grid, optional columns + tributary overlay."""
    tributary_columns = None
    obstacles: list[Rect] = []
    if show_tributary and layout.panel_count > 0 and column_count_x and column_count_y:
        tributary_columns, obstacles = build_tributary_columns(
            layout,
            column_count_x=column_count_x,
            column_count_y=column_count_y,
            column_overrides_text=column_overrides_text,
            obstacle_zones_text=obstacle_zones_text,
        )

    fig = build_layout_figure(
        layout.panel,
        layout.config,
        layout.num_pairs_per_row,
        layout.num_rows,
        tributary_columns=tributary_columns,
        obstacle_zones=obstacles if obstacles else None,
        title=title,
    )
    st.plotly_chart(fig, width="stretch")
    return tributary_columns, obstacles
