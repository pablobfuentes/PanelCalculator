"""Tests for tributary area computation."""

import pytest

from core.columns import count_from_spacing, default_columns, panel_field_bbox
from core.layout import accumulate_grid
from core.models import LayoutConfig, PanelSpec
from core.tributary import (
    active_columns,
    compute_tributary_zones,
    enrich_tributary_loads,
    total_panel_area,
    tributary_partition_valid,
)


@pytest.fixture
def panel() -> PanelSpec:
    return PanelSpec(length=2.0, width=1.0, weight=25.0, tilt_angle=10.0)


@pytest.fixture
def config() -> LayoutConfig:
    return LayoutConfig(mid_clamp_gap=0.1, alley_width=1.0, max_area_x=12.0, max_area_y=8.0)


def test_default_columns_2d_spans_panel_field():
    field = (0.0, 1.0, 10.0, 6.0)
    columns = default_columns(field, count_x=3, count_y=3)
    assert min(column.x for column in columns) == pytest.approx(0.0)
    assert max(column.x for column in columns) == pytest.approx(10.0)
    assert min(column.y for column in columns) == pytest.approx(1.0)
    assert max(column.y for column in columns) == pytest.approx(7.0)
    assert len(columns) > 2


def test_compute_tributary_zones_partition_panel_area(panel: PanelSpec, config: LayoutConfig):
    panels = accumulate_grid(panel, config, num_pairs_per_row=3, num_rows=2)
    field = panel_field_bbox(panels)
    columns = default_columns(
        field,
        count_x=count_from_spacing(field[2], 3.5),
        count_y=count_from_spacing(field[3], 3.5),
    )
    zoned = compute_tributary_zones(columns, panels)

    assert len(zoned) == len(columns)
    assert all(column.tributary_rect is not None for column in active_columns(zoned))
    assert tributary_partition_valid(zoned, panels)
    assert sum(column.tributary_area_m2 for column in active_columns(zoned)) == pytest.approx(
        total_panel_area(panels)
    )


def test_excluded_columns_have_zero_tributary(panel: PanelSpec, config: LayoutConfig):
    from core.columns import Column, apply_obstacle_exclusions

    panels = accumulate_grid(panel, config, num_pairs_per_row=2, num_rows=1)
    field = panel_field_bbox(panels)
    columns = default_columns(
        field,
        count_x=count_from_spacing(field[2], 5.0),
        count_y=count_from_spacing(field[3], 5.0),
    )
    columns = apply_obstacle_exclusions(columns, [(0.0, field[1], 1.0, 1.0)])
    zoned = compute_tributary_zones(columns, panels)
    excluded = [column for column in zoned if column.excluded]
    assert excluded
    assert all(column.tributary_area_m2 == 0.0 for column in excluded)


def test_compute_tributary_zones_empty_panels_returns_zero_area():
    columns = default_columns((0.0, 0.0, 6.0, 4.0), count_x=3, count_y=2)
    zoned = compute_tributary_zones(columns, [])
    assert all(column.tributary_area_m2 == 0.0 for column in zoned)


def test_enrich_tributary_loads_scales_with_area(panel: PanelSpec, config: LayoutConfig):
    panels = accumulate_grid(panel, config, num_pairs_per_row=3, num_rows=2)
    field = panel_field_bbox(panels)
    zoned = compute_tributary_zones(
        default_columns(field, count_x=count_from_spacing(field[2], 3.5), count_y=count_from_spacing(field[3], 3.5)),
        panels,
    )
    loaded = enrich_tributary_loads(zoned, panel)

    assert all(column.estimated_load_kn > 0 for column in active_columns(loaded))
    assert sum(column.estimated_load_kn for column in active_columns(loaded)) == pytest.approx(
        panel.weight * len(panels) * 9.80665 / 1000.0,
        rel=1e-4,
    )


def test_estimated_dead_load_kn_zero_area(panel: PanelSpec):
    from core.tributary import estimated_dead_load_kn

    assert estimated_dead_load_kn(0.0, panel) == 0.0


def test_tributary_cells_are_2d_rectangles(panel: PanelSpec, config: LayoutConfig):
    panels = accumulate_grid(panel, config, num_pairs_per_row=2, num_rows=2)
    field = panel_field_bbox(panels)
    zoned = compute_tributary_zones(
        default_columns(
            field,
            count_x=count_from_spacing(field[2], 4.0),
            count_y=count_from_spacing(field[3], 4.0),
        ),
        panels,
    )
    first = active_columns(zoned)[0]
    assert first.tributary_rect is not None
    _, _, width, height = first.tributary_rect
    assert width > 0
    assert height > 0
    assert height < field[3]
