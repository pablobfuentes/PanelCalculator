"""Shared layout resolution and session snapshot helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from core.layout import (
    accumulate_grid,
    collect_alley_rects,
    fit_to_area,
    fit_to_panel_count,
    grid_bbox,
)
from core.models import DEFAULT_MID_CLAMP_GAP_M, LayoutConfig, PanelSpec


@dataclass
class ResolvedLayout:
    """Fully resolved panel grid used by Setup and Phase 3."""

    panel: PanelSpec
    config: LayoutConfig
    num_pairs_per_row: int
    num_rows: int
    panel_count: int
    panels_locked: bool
    locked_panel_count: int
    use_fit: bool
    panels: list
    alleys: list
    bbox: tuple[float, float, float, float]


def layout_config_from_inputs(
    *,
    mid_clamp_in: float,
    alley_width: float,
    alley_reach: int,
    max_area_x: float,
    max_area_y: float,
) -> LayoutConfig:
    base_kwargs = {
        "mid_clamp_gap": mid_clamp_in * 0.0254 if mid_clamp_in else DEFAULT_MID_CLAMP_GAP_M,
        "alley_width": alley_width,
        "max_area_x": max_area_x,
        "max_area_y": max_area_y,
    }
    try:
        return LayoutConfig(**base_kwargs, alley_reach=alley_reach)
    except TypeError:
        config = LayoutConfig(**base_kwargs)
        config.alley_reach = alley_reach
        return config


def default_panel_count(panel: PanelSpec, config: LayoutConfig, use_fit: bool) -> int:
    if not use_fit:
        return 12
    layout = fit_to_area(panel, config)
    count = len(layout.rectangles)
    if count < 2:
        return 2
    if count % 2 != 0:
        return count - 1
    return count


def resolve_layout(
    *,
    panel: PanelSpec,
    config: LayoutConfig,
    use_fit: bool,
    panels_locked: bool,
    target_panels: int,
    num_pairs_manual: int,
    num_rows_manual: int,
) -> ResolvedLayout:
    if panels_locked:
        grid = fit_to_panel_count(panel, config, target_panels)
        num_pairs = grid.num_pairs_per_row
        num_rows = grid.num_rows
        panel_count = len(grid.rectangles)
    elif use_fit:
        grid = fit_to_area(panel, config)
        num_pairs = grid.num_pairs_per_row
        num_rows = grid.num_rows
        panel_count = len(grid.rectangles)
    else:
        num_pairs = int(num_pairs_manual)
        num_rows = int(num_rows_manual)
        panel_count = len(accumulate_grid(panel, config, num_pairs, num_rows))

    panels = accumulate_grid(panel, config, num_pairs, num_rows)
    alleys = collect_alley_rects(panel, config, num_pairs, num_rows)
    bbox = grid_bbox(panels + alleys)

    return ResolvedLayout(
        panel=panel,
        config=config,
        num_pairs_per_row=num_pairs,
        num_rows=num_rows,
        panel_count=panel_count,
        panels_locked=panels_locked,
        locked_panel_count=target_panels if panels_locked else 0,
        use_fit=use_fit,
        panels=panels,
        alleys=alleys,
        bbox=bbox,
    )


def snapshot_from_layout(layout: ResolvedLayout) -> dict[str, Any]:
    return {
        "panel": asdict(layout.panel),
        "config": asdict(layout.config),
        "num_pairs_per_row": layout.num_pairs_per_row,
        "num_rows": layout.num_rows,
        "panel_count": layout.panel_count,
        "panels_locked": layout.panels_locked,
        "locked_panel_count": layout.locked_panel_count,
        "use_fit": layout.use_fit,
    }


def layout_from_snapshot(data: dict[str, Any]) -> ResolvedLayout:
    panel = PanelSpec(**data["panel"])
    config = LayoutConfig(**data["config"])
    num_pairs = int(data["num_pairs_per_row"])
    num_rows = int(data["num_rows"])
    panels = accumulate_grid(panel, config, num_pairs, num_rows)
    alleys = collect_alley_rects(panel, config, num_pairs, num_rows)
    return ResolvedLayout(
        panel=panel,
        config=config,
        num_pairs_per_row=num_pairs,
        num_rows=num_rows,
        panel_count=int(data["panel_count"]),
        panels_locked=bool(data["panels_locked"]),
        locked_panel_count=int(data.get("locked_panel_count", 0)),
        use_fit=bool(data["use_fit"]),
        panels=panels,
        alleys=alleys,
        bbox=grid_bbox(panels + alleys),
    )


def layout_footprint_hash(layout: ResolvedLayout) -> str:
    return (
        f"{layout.panel_count}:{layout.num_pairs_per_row}:{layout.num_rows}:"
        f"{layout.bbox[2]:.4f}:{layout.bbox[3]:.4f}:"
        f"{layout.config.alley_reach}:{layout.config.max_area_x:.4f}:"
        f"{layout.config.max_area_y:.4f}"
    )
