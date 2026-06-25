"""Column placement: 2D grid, overrides, and obstacle exclusion."""

from __future__ import annotations

from dataclasses import dataclass, replace

from core.layout import Rect, grid_bbox

DEFAULT_COLUMN_SPACING_M = 3.5
MIN_COLUMN_COUNT = 2


@dataclass(frozen=True)
class Column:
    """Structural column position and tributary catchment."""

    column_id: str
    x: float
    y: float = 0.0
    tributary_rect: Rect | None = None
    tributary_area_m2: float = 0.0
    estimated_load_kn: float = 0.0
    excluded: bool = False
    is_custom: bool = False


def panel_field_bbox(panel_rects: list[Rect]) -> Rect:
    """Axis-aligned bounds of the panel rectangles (excludes alleys)."""
    return grid_bbox(panel_rects)


def count_from_spacing(extent: float, spacing: float) -> int:
    """Derive an even column count that approximates the requested spacing."""
    if spacing <= 0:
        raise ValueError("spacing must be positive")
    if extent <= 1e-9:
        return MIN_COLUMN_COUNT
    return max(MIN_COLUMN_COUNT, int(round(extent / spacing)) + 1)


def spacing_from_count(extent: float, count: int) -> float:
    """Even spacing between column centres when count columns span the extent."""
    if count < MIN_COLUMN_COUNT:
        raise ValueError(f"count must be >= {MIN_COLUMN_COUNT}")
    if extent <= 1e-9:
        return 0.0
    return extent / (count - 1)


def axis_positions_from_count(origin: float, extent: float, count: int) -> list[float]:
    """Evenly spaced positions from origin to origin+extent (inclusive endpoints)."""
    if count < MIN_COLUMN_COUNT:
        raise ValueError(f"count must be >= {MIN_COLUMN_COUNT}")
    if extent <= 1e-9:
        return []
    return [origin + extent * index / (count - 1) for index in range(count)]


def even_axis_positions(origin: float, extent: float, spacing: float) -> list[float]:
    """Evenly spaced positions matching a target spacing (legacy helper)."""
    return axis_positions_from_count(origin, extent, count_from_spacing(extent, spacing))


def column_spacings(
    panel_field: Rect,
    count_x: int,
    count_y: int,
) -> tuple[float, float]:
    """Actual centre-to-centre spacing for the chosen column counts."""
    _, _, width, height = panel_field
    return spacing_from_count(width, count_x), spacing_from_count(height, count_y)


def default_columns(
    panel_field: Rect,
    count_x: int = MIN_COLUMN_COUNT,
    count_y: int = MIN_COLUMN_COUNT,
) -> list[Column]:
    """Place columns on a 2D grid with even X and Y spacing over the panel field."""
    fx, fy, fw, fh = panel_field
    xs = axis_positions_from_count(fx, fw, count_x)
    ys = axis_positions_from_count(fy, fh, count_y)

    columns: list[Column] = []
    index = 1
    for y in ys:
        for x in xs:
            columns.append(Column(column_id=f"C{index}", x=x, y=y))
            index += 1
    return columns


def parse_column_overrides(text: str) -> list[Column]:
    """
    Parse custom column coordinates from text.

    Each non-empty line: ``x, y`` or ``id, x, y`` (metres).
    """
    columns: list[Column] = []
    auto_id = 1
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = [part.strip() for part in stripped.replace(";", ",").split(",")]
        if len(parts) == 2:
            column_id = f"C{auto_id}"
            x, y = float(parts[0]), float(parts[1])
        elif len(parts) == 3:
            column_id, x, y = parts[0], float(parts[1]), float(parts[2])
        else:
            raise ValueError(
                f"Invalid column line {line!r}: expected 'x, y' or 'id, x, y'"
            )
        columns.append(Column(column_id=column_id, x=x, y=y, is_custom=True))
        auto_id += 1
    return columns


def parse_obstacle_zones(text: str) -> list[Rect]:
    """Parse obstacle boxes: each line ``x, y, width, height`` (metres)."""
    zones: list[Rect] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = [part.strip() for part in stripped.replace(";", ",").split(",")]
        if len(parts) != 4:
            raise ValueError(
                f"Invalid obstacle line {line!r}: expected 'x, y, width, height'"
            )
        x, y, width, height = (
            float(parts[0]),
            float(parts[1]),
            float(parts[2]),
            float(parts[3]),
        )
        if width <= 0 or height <= 0:
            raise ValueError(f"Obstacle width and height must be positive: {line!r}")
        zones.append((x, y, width, height))
    return zones


def point_inside_rect(x: float, y: float, rect: Rect) -> bool:
    rx, ry, rw, rh = rect
    return rx <= x <= rx + rw + 1e-9 and ry <= y <= ry + rh + 1e-9


def apply_obstacle_exclusions(columns: list[Column], obstacles: list[Rect]) -> list[Column]:
    """Flag columns whose plan position falls inside an obstacle zone."""
    if not obstacles:
        return columns
    return [
        replace(
            column,
            excluded=any(point_inside_rect(column.x, column.y, zone) for zone in obstacles),
        )
        for column in columns
    ]


def resolve_columns(
    panel_rects: list[Rect],
    *,
    count_x: int = MIN_COLUMN_COUNT,
    count_y: int = MIN_COLUMN_COUNT,
    overrides_text: str = "",
) -> list[Column]:
    """Build default 2D grid or replace with parsed custom coordinates."""
    field = panel_field_bbox(panel_rects)
    if overrides_text.strip():
        return parse_column_overrides(overrides_text)
    return default_columns(field, count_x=count_x, count_y=count_y)


def active_columns(columns: list[Column]) -> list[Column]:
    """Columns that participate in tributary partitioning and FEA."""
    return [column for column in columns if not column.excluded]
