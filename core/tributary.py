"""Tributary area model for structural columns under a panel field."""

from __future__ import annotations

from dataclasses import dataclass, replace

from core.layout import Rect, grid_bbox
from core.models import PanelSpec

DEFAULT_COLUMN_SPACING_M = 3.5
GRAVITY_M_S2 = 9.80665


@dataclass(frozen=True)
class Column:
    """Structural column position and tributary catchment."""

    column_id: str
    x: float
    y: float = 0.0
    tributary_rect: Rect | None = None
    tributary_area_m2: float = 0.0
    estimated_load_kn: float = 0.0


def panel_field_bbox(panel_rects: list[Rect]) -> Rect:
    """Axis-aligned bounds of the panel rectangles (excludes alleys)."""
    return grid_bbox(panel_rects)


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
            estimated_load_kn=estimated_dead_load_kn(column.tributary_area_m2, panel),
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


def default_columns(panel_field: Rect, spacing: float = DEFAULT_COLUMN_SPACING_M) -> list[Column]:
    """Place columns along X at equal spacing within the panel field width."""
    if spacing <= 0:
        raise ValueError("spacing must be positive")

    _, _, width, _ = panel_field
    if width <= 0:
        return []

    positions: list[float] = []
    x = 0.0
    while x < width - 1e-9:
        positions.append(x)
        x += spacing
    if not positions or abs(positions[-1] - width) > 1e-6:
        positions.append(width)

    return [
        Column(column_id=f"C{index}", x=position, y=0.0)
        for index, position in enumerate(positions, start=1)
    ]


def compute_tributary_zones(
    columns: list[Column],
    panel_rects: list[Rect],
) -> list[Column]:
    """
    Assign each column a rectangular tributary strip across the panel field.

    Strips are bounded by midpoints between adjacent column X positions and
    clipped to the panel field. Tributary area counts only panel rectangle overlap.
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
    sorted_columns = sorted(columns, key=lambda column: column.x)

    boundaries = [fx]
    for left, right in zip(sorted_columns, sorted_columns[1:]):
        boundaries.append((left.x + right.x) / 2.0)
    boundaries.append(fx + fw)

    zoned: list[Column] = []
    for index, column in enumerate(sorted_columns):
        x0 = boundaries[index]
        x1 = boundaries[index + 1]
        strip: Rect = (x0, fy, x1 - x0, fh)
        area = sum(_intersection_area(strip, panel_rect) for panel_rect in panel_rects)
        zoned.append(
            replace(
                column,
                tributary_rect=strip,
                tributary_area_m2=area,
            )
        )
    return zoned


def tributary_partition_valid(columns: list[Column], panel_rects: list[Rect]) -> bool:
    """True when tributary areas sum to total panel area (no gaps or double-count)."""
    if not panel_rects:
        return all(column.tributary_area_m2 == 0.0 for column in columns)
    assigned = sum(column.tributary_area_m2 for column in columns)
    return abs(assigned - total_panel_area(panel_rects)) <= 1e-6
