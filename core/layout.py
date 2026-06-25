"""Panel layout geometry: pairs, rows, grids, and area fitting."""

from dataclasses import dataclass

from core.models import LayoutConfig, PanelSpec

LAYOUT_API_VERSION = 3  # bump when alley/spine geometry changes

Rect = tuple[float, float, float, float]  # x, y, width, height


@dataclass(frozen=True)
class GridLayout:
    """Result of fitting panels into the max layout footprint."""

    rectangles: tuple[Rect, ...]
    num_pairs_per_row: int
    num_rows: int
    bbox: Rect


def _pair_width(panel: PanelSpec, config: LayoutConfig) -> float:
    return 2 * panel.width + config.mid_clamp_gap


def compute_alley_positions(num_cols: int, reach: int) -> list[int]:
    """
    Return 0-based panel column indices after which a parallel alley is placed.

    Each alley covers `reach` panels to its left and `reach` panels to its right.
    The panel columns are partitioned into groups of 2 * reach, and the alley is
    placed at the midpoint of each group.
    """
    if num_cols < 0:
        raise ValueError("num_cols must be non-negative")
    if reach < 2 or reach > 4:
        raise ValueError("reach must be between 2 and 4 panels")

    group_size = 2 * reach
    alleys: list[int] = []
    for group_start in range(0, num_cols, group_size):
        alley_after = group_start + reach - 1
        if alley_after >= num_cols - 1:
            break
        alleys.append(alley_after)
    return alleys


def parallel_alley_gap_labels(num_cols: int, reach: int) -> list[str]:
    """Human-readable gap labels like '3-4' for UI display."""
    return [f"{column + 1}-{column + 2}" for column in compute_alley_positions(num_cols, reach)]


def _panels_in_pair(
    panel: PanelSpec,
    config: LayoutConfig,
    origin_x: float = 0.0,
    origin_y: float = 0.0,
) -> list[Rect]:
    gap = config.mid_clamp_gap
    return [
        (origin_x, origin_y, panel.width, panel.length),
        (origin_x + panel.width + gap, origin_y, panel.width, panel.length),
    ]


def pair_panels(
    panel: PanelSpec,
    config: LayoutConfig,
    origin_x: float = 0.0,
    origin_y: float = 0.0,
) -> Rect:
    """Return the bounding box for two side-by-side panels plus mid-clamp gap."""
    return (
        origin_x,
        origin_y,
        _pair_width(panel, config),
        panel.length,
    )


def _row_panel_extent_x(num_pairs: int, panel: PanelSpec, config: LayoutConfig) -> float:
    """Panel field width along X (parallel alleys included, spine excluded)."""
    if num_pairs <= 0:
        return 0.0
    num_cols = num_pairs * 2
    alley_count = len(compute_alley_positions(num_cols, config.alley_reach))
    regular_gap_count = num_cols - 1 - alley_count
    return (
        num_cols * panel.width
        + regular_gap_count * config.mid_clamp_gap
        + alley_count * config.alley_width
    )


def _grid_extent_x(num_pairs: int, panel: PanelSpec, config: LayoutConfig) -> float:
    """Full layout width across panel columns and parallel alleys."""
    if num_pairs <= 0:
        return 0.0
    return _row_panel_extent_x(num_pairs, panel, config)


def _grid_extent_y(num_rows: int, panel: PanelSpec, config: LayoutConfig) -> float:
    """Full layout depth: one edge spine plus stacked panel rows."""
    if num_rows <= 0:
        return 0.0
    return config.alley_width + num_rows * panel.length


def layout_bbox(
    panel: PanelSpec,
    config: LayoutConfig,
    num_pairs_per_row: int,
    num_rows: int,
) -> Rect:
    """Bounding box of the full layout including perimeter edge alleys."""
    return (
        0.0,
        0.0,
        _grid_extent_x(num_pairs_per_row, panel, config),
        _grid_extent_y(num_rows, panel, config),
    )


def accumulate_row(
    panel: PanelSpec,
    config: LayoutConfig,
    num_pairs: int,
    origin_x: float = 0.0,
    origin_y: float = 0.0,
) -> list[Rect]:
    """Place panel pairs along X; insert parallel alleys at reach-based column positions."""
    if num_pairs < 0:
        raise ValueError("num_pairs must be non-negative")

    rectangles: list[Rect] = []
    x = origin_x
    num_cols = num_pairs * 2
    alley_positions = set(compute_alley_positions(num_pairs * 2, config.alley_reach))
    for column_index in range(num_cols):
        rectangles.append((x, origin_y, panel.width, panel.length))
        x += panel.width

        if column_index == num_cols - 1:
            continue
        if column_index in alley_positions:
            x += config.alley_width
        else:
            x += config.mid_clamp_gap
    return rectangles


def accumulate_grid(
    panel: PanelSpec,
    config: LayoutConfig,
    num_pairs_per_row: int,
    num_rows: int,
) -> list[Rect]:
    """Stack rows along Y, leaving the bottom edge clear for the perpendicular spine."""
    if num_pairs_per_row < 0 or num_rows < 0:
        raise ValueError("num_pairs_per_row and num_rows must be non-negative")

    rectangles: list[Rect] = []
    for row_index in range(num_rows):
        origin_y = config.alley_width + row_index * panel.length
        row_rects = accumulate_row(
            panel,
            config,
            num_pairs_per_row,
            origin_x=0.0,
            origin_y=origin_y,
        )
        rectangles.extend(row_rects)
    return rectangles


def collect_row_alley_rects(
    panel: PanelSpec,
    config: LayoutConfig,
    num_pairs: int,
    origin_x: float = 0.0,
    origin_y: float = 0.0,
) -> list[Rect]:
    """Return parallel alley rectangles for one row (single-row height)."""
    if num_pairs < 0:
        raise ValueError("num_pairs must be non-negative")

    alleys: list[Rect] = []
    x = origin_x
    num_cols = num_pairs * 2
    alley_positions = set(compute_alley_positions(num_cols, config.alley_reach))
    for column_index in range(num_cols):
        x += panel.width
        if column_index == num_cols - 1:
            continue
        if column_index in alley_positions:
            alleys.append((x, origin_y, config.alley_width, panel.length))
            x += config.alley_width
        else:
            x += config.mid_clamp_gap
    return alleys


def collect_alley_rects(
    panel: PanelSpec,
    config: LayoutConfig,
    num_pairs_per_row: int,
    num_rows: int,
) -> list[Rect]:
    """Return service alleys: reach-based parallel alleys plus one edge spine."""
    if num_pairs_per_row < 0 or num_rows < 0:
        raise ValueError("num_pairs_per_row and num_rows must be non-negative")
    if num_pairs_per_row == 0 or num_rows == 0:
        return []

    grid_width = _grid_extent_x(num_pairs_per_row, panel, config)
    panel_field_height = num_rows * panel.length
    alleys: list[Rect] = [(0.0, 0.0, grid_width, config.alley_width)]

    row_alleys = collect_row_alley_rects(
        panel,
        config,
        num_pairs_per_row,
        origin_x=0.0,
        origin_y=config.alley_width,
    )
    alleys.extend((x, config.alley_width, w, panel_field_height) for x, _, w, _ in row_alleys)

    return alleys


def grid_bbox(rectangles: list[Rect]) -> Rect:
    """Axis-aligned bounding box for a list of rectangles."""
    if not rectangles:
        return (0.0, 0.0, 0.0, 0.0)
    max_x = max(x + w for x, _, w, _ in rectangles)
    max_y = max(y + h for _, y, _, h in rectangles)
    return (0.0, 0.0, max_x, max_y)


def _max_pairs_for_width(panel: PanelSpec, config: LayoutConfig) -> int:
    limit = config.max_area_x
    count = 0
    while _grid_extent_x(count + 1, panel, config) <= limit + 1e-9:
        count += 1
    return count


def _max_rows_for_height(panel: PanelSpec, config: LayoutConfig) -> int:
    limit = config.max_area_y
    count = 0
    while _grid_extent_y(count + 1, panel, config) <= limit + 1e-9:
        count += 1
    return count


def _panel_grid_factorizations(target_panels: int) -> list[tuple[int, int]]:
    """
    Return (num_pairs_per_row, num_rows) layouts for exactly target_panels.

    Each row holds an even number of panels (paired columns).
    """
    if target_panels <= 0 or target_panels % 2 != 0:
        return []

    pair_rows = target_panels // 2
    options: list[tuple[int, int]] = []
    for num_pairs in range(1, pair_rows + 1):
        if pair_rows % num_pairs != 0:
            continue
        num_rows = pair_rows // num_pairs
        options.append((num_pairs, num_rows))
    return options


def fit_to_panel_count(
    panel: PanelSpec,
    config: LayoutConfig,
    target_panels: int,
) -> GridLayout:
    """Pick a rectangular pair grid with exactly target_panels that fits max area."""
    if target_panels <= 0:
        return GridLayout(
            rectangles=(),
            num_pairs_per_row=0,
            num_rows=0,
            bbox=(0.0, 0.0, 0.0, 0.0),
        )

    best: tuple[int, int] | None = None
    best_footprint = -1.0
    for num_pairs, num_rows in _panel_grid_factorizations(target_panels):
        bbox = layout_bbox(panel, config, num_pairs, num_rows)
        if bbox[2] > config.max_area_x + 1e-9 or bbox[3] > config.max_area_y + 1e-9:
            continue
        footprint = bbox[2] * bbox[3]
        if footprint > best_footprint + 1e-9 or (
            abs(footprint - best_footprint) <= 1e-9
            and best is not None
            and num_pairs > best[0]
        ):
            best = (num_pairs, num_rows)
            best_footprint = footprint

    if best is None:
        return GridLayout(
            rectangles=(),
            num_pairs_per_row=0,
            num_rows=0,
            bbox=(0.0, 0.0, 0.0, 0.0),
        )

    num_pairs, num_rows = best
    rectangles = accumulate_grid(panel, config, num_pairs, num_rows)
    bbox = layout_bbox(panel, config, num_pairs, num_rows)
    return GridLayout(
        rectangles=tuple(rectangles),
        num_pairs_per_row=num_pairs,
        num_rows=num_rows,
        bbox=bbox,
    )


def fit_to_area(panel: PanelSpec, config: LayoutConfig) -> GridLayout:
    """Reduce row/pair counts until the grid fits within max_area_x × max_area_y."""
    max_pairs = _max_pairs_for_width(panel, config)
    max_rows = _max_rows_for_height(panel, config)

    for num_rows in range(max_rows, 0, -1):
        for num_pairs in range(max_pairs, 0, -1):
            rectangles = accumulate_grid(panel, config, num_pairs, num_rows)
            bbox = layout_bbox(panel, config, num_pairs, num_rows)
            if bbox[2] <= config.max_area_x + 1e-9 and bbox[3] <= config.max_area_y + 1e-9:
                return GridLayout(
                    rectangles=tuple(rectangles),
                    num_pairs_per_row=num_pairs,
                    num_rows=num_rows,
                    bbox=bbox,
                )

    return GridLayout(
        rectangles=(),
        num_pairs_per_row=0,
        num_rows=0,
        bbox=(0.0, 0.0, 0.0, 0.0),
    )
