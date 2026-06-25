"""Tributary area model for structural columns under a panel field."""

from __future__ import annotations

from dataclasses import replace

from core.columns import (
    Column,
    DEFAULT_COLUMN_SPACING_M,
    active_columns,
    apply_obstacle_exclusions,
    default_columns,
    even_axis_positions,
    panel_field_bbox,
    parse_column_overrides,
    parse_obstacle_zones,
    resolve_columns,
)
from core.layout import Rect
from core.models import PanelSpec

GRAVITY_M_S2 = 9.80665

__all__ = [
    "Column",
    "DEFAULT_COLUMN_SPACING_M",
    "active_columns",
    "apply_obstacle_exclusions",
    "compute_tributary_zones",
    "default_columns",
    "enrich_tributary_loads",
    "estimated_dead_load_kn",
    "even_axis_positions",
    "panel_field_bbox",
    "parse_column_overrides",
    "parse_obstacle_zones",
    "resolve_columns",
    "total_panel_area",
    "tributary_partition_valid",
]


def total_panel_area(panel_rects: list[Rect]) -> float:
    """Sum of individual panel rectangle areas."""
    return sum(width * height for _, _, width, height in panel_rects)


def panel_weight_per_area_kg_m2(panel: PanelSpec) -> float:
    """Panel mass per plan area (kg/m²)."""
    area = panel.width * panel.length
    if area <= 0:
        return 0.0
    return panel.weight / area


def estimated_dead_load_kn(tributary_area_m2: float, panel: PanelSpec) -> float:
    """Estimate tributary dead load from panel weight over the catchment area."""
    weight_kg = tributary_area_m2 * panel_weight_per_area_kg_m2(panel)
    return weight_kg * GRAVITY_M_S2 / 1000.0


def enrich_tributary_loads(columns: list[Column], panel: PanelSpec) -> list[Column]:
    """Attach estimated dead load (kN) to each column tributary zone."""
    return [
        replace(
            column,
            estimated_load_kn=0.0
            if column.excluded
            else estimated_dead_load_kn(column.tributary_area_m2, panel),
        )
        for column in columns
    ]


def _intersection_area(a: Rect, b: Rect) -> float:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    x0 = max(ax, bx)
    y0 = max(ay, by)
    x1 = min(ax + aw, bx + bw)
    y1 = min(ay + ah, by + bh)
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return (x1 - x0) * (y1 - y0)


def _cell_boundaries(coords: list[float], start: float, end: float) -> list[tuple[float, float]]:
    bounds: list[tuple[float, float]] = []
    for index, coord in enumerate(coords):
        left = start if index == 0 else (coords[index - 1] + coord) / 2.0
        right = end if index == len(coords) - 1 else (coord + coords[index + 1]) / 2.0
        bounds.append((left, right))
    return bounds


def _coord_index(value: float, coords: list[float]) -> int:
    for index, coord in enumerate(coords):
        if abs(coord - value) <= 1e-6:
            return index
    raise ValueError(f"Column coordinate {value} not found in grid axes {coords}")


def compute_tributary_zones(
    columns: list[Column],
    panel_rects: list[Rect],
) -> list[Column]:
    """
    Assign each active column a rectangular tributary cell over the panel field.

    Cells are bounded by midplanes between adjacent column lines in X and Y.
    Excluded columns receive zero area.
    """
    if not columns:
        return []
    if not panel_rects:
        return [
            replace(column, tributary_rect=None, tributary_area_m2=0.0)
            for column in columns
        ]

    field = panel_field_bbox(panel_rects)
    fx, fy, fw, fh = field
    active = active_columns(columns)
    if not active:
        return [
            replace(column, tributary_rect=None, tributary_area_m2=0.0)
            for column in columns
        ]

    unique_x = sorted({column.x for column in active})
    unique_y = sorted({column.y for column in active})
    x_bounds = _cell_boundaries(unique_x, fx, fx + fw)
    y_bounds = _cell_boundaries(unique_y, fy, fy + fh)

    zoned_by_id: dict[str, Column] = {}
    for column in active:
        xi = _coord_index(column.x, unique_x)
        yi = _coord_index(column.y, unique_y)
        x0, x1 = x_bounds[xi]
        y0, y1 = y_bounds[yi]
        cell: Rect = (x0, y0, x1 - x0, y1 - y0)
        area = sum(_intersection_area(cell, panel_rect) for panel_rect in panel_rects)
        zoned_by_id[column.column_id] = replace(
            column,
            tributary_rect=cell,
            tributary_area_m2=area,
        )

    return [
        replace(
            column,
            tributary_rect=None,
            tributary_area_m2=0.0,
        )
        if column.excluded
        else zoned_by_id[column.column_id]
        for column in columns
    ]


def tributary_partition_valid(columns: list[Column], panel_rects: list[Rect]) -> bool:
    """True when active tributary areas sum to total panel area."""
    if not panel_rects:
        return all(column.tributary_area_m2 == 0.0 for column in columns)
    assigned = sum(column.tributary_area_m2 for column in active_columns(columns))
    return abs(assigned - total_panel_area(panel_rects)) <= 1e-6
