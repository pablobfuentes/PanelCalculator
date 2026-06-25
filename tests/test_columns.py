"""Tests for column placement (Phase 4.2)."""

import pytest

from core.columns import (
    Column,
    apply_obstacle_exclusions,
    axis_positions_from_count,
    count_from_spacing,
    default_columns,
    even_axis_positions,
    parse_column_overrides,
    parse_obstacle_zones,
    resolve_columns,
    spacing_from_count,
)
from core.layout import accumulate_grid
from core.models import LayoutConfig, PanelSpec
from core.tributary import compute_tributary_zones, panel_field_bbox, tributary_partition_valid


@pytest.fixture
def panel() -> PanelSpec:
    return PanelSpec(length=2.0, width=1.0, weight=25.0, tilt_angle=10.0)


@pytest.fixture
def config() -> LayoutConfig:
    return LayoutConfig(mid_clamp_gap=0.1, alley_width=1.0, max_area_x=12.0, max_area_y=8.0)


def test_even_axis_positions_include_endpoints():
    assert even_axis_positions(0.0, 10.0, 3.5) == pytest.approx([0.0, 10.0 / 3, 20.0 / 3, 10.0])


def test_spacing_from_count_matches_even_distribution():
    assert spacing_from_count(10.0, 4) == pytest.approx(10.0 / 3)
    assert axis_positions_from_count(0.0, 10.0, 4) == pytest.approx(
        [0.0, 10.0 / 3, 20.0 / 3, 10.0]
    )


def test_count_from_spacing_round_trip():
    extent = 11.43
    spacing = 3.5
    count = count_from_spacing(extent, spacing)
    assert spacing_from_count(extent, count) == pytest.approx(extent / (count - 1))


def test_default_columns_2d_grid():
    field = (0.0, 1.0, 10.0, 7.0)
    columns = default_columns(field, count_x=3, count_y=3)
    xs = sorted({column.x for column in columns})
    ys = sorted({column.y for column in columns})
    assert xs == pytest.approx([0.0, 5.0, 10.0])
    assert len(ys) >= 2
    assert columns[0].y == pytest.approx(1.0)
    assert columns[-1].y == pytest.approx(8.0)
    assert len(columns) == len(xs) * len(ys)


def test_parse_column_overrides_xy_and_id():
    text = "2.0, 1.5\nP1, 4.0, 3.0"
    columns = parse_column_overrides(text)
    assert columns[0] == Column(column_id="C1", x=2.0, y=1.5, is_custom=True)
    assert columns[1] == Column(column_id="P1", x=4.0, y=3.0, is_custom=True)


def test_parse_obstacle_zones():
    zones = parse_obstacle_zones("1, 2, 3, 4")
    assert zones == [(1.0, 2.0, 3.0, 4.0)]


def test_obstacle_excludes_columns_inside_zone():
    columns = [
        Column(column_id="C1", x=1.0, y=1.0),
        Column(column_id="C2", x=5.0, y=5.0),
    ]
    flagged = apply_obstacle_exclusions(columns, [(0.5, 0.5, 2.0, 2.0)])
    assert flagged[0].excluded
    assert not flagged[1].excluded


def test_resolve_columns_uses_overrides_when_provided(panel: PanelSpec, config: LayoutConfig):
    panels = accumulate_grid(panel, config, num_pairs_per_row=2, num_rows=1)
    columns = resolve_columns(panels, count_x=3, count_y=2, overrides_text="1.0, 2.0")
    assert len(columns) == 1
    assert columns[0].x == pytest.approx(1.0)
    assert columns[0].is_custom


def test_2d_tributary_partition_with_grid(panel: PanelSpec, config: LayoutConfig):
    panels = accumulate_grid(panel, config, num_pairs_per_row=3, num_rows=2)
    field = panel_field_bbox(panels)
    columns = default_columns(field, count_x=3, count_y=3)
    zoned = compute_tributary_zones(columns, panels)
    assert tributary_partition_valid(zoned, panels)
    assert len({(c.tributary_rect[2], c.tributary_rect[3]) for c in zoned}) > 1
