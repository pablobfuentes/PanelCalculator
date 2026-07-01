"""Tributary column resolution for the web API (no Streamlit)."""

from __future__ import annotations

from core.columns import apply_obstacle_exclusions, resolve_columns
from core.layout import Rect
from core.tributary import (
    compute_tributary_zones,
    enrich_tributary_loads,
    parse_obstacle_zones,
)
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
