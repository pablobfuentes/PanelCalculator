"""Tests for tributary area computation."""

import pytest

from core.layout import accumulate_grid
from core.models import LayoutConfig, PanelSpec
from core.tributary import (
    compute_tributary_zones,
    default_columns,
    enrich_tributary_loads,
    panel_field_bbox,
    total_panel_area,
    tributary_partition_valid,
)


@pytest.fixture
def panel() -> PanelSpec:
    return PanelSpec(length=2.0, width=1.0, weight=25.0, tilt_angle=10.0)


@pytest.fixture
def config() -> LayoutConfig:
    return LayoutConfig(mid_clamp_gap=0.1, alley_width=1.0, max_area_x=12.0, max_area_y=8.0)


def test_default_columns_spans_panel_field_width():
    field = (0.0, 1.0, 10.0, 6.0)
    columns = default_columns(field, spacing=3.5)
    assert columns[0].x == 0.0
    assert columns[-1].x == pytest.approx(10.0)
    assert len(columns) >= 2


def test_compute_tributary_zones_partition_panel_area(panel: PanelSpec, config: LayoutConfig):
    panels = accumulate_grid(panel, config, num_pairs_per_row=3, num_rows=2)
    field = panel_field_bbox(panels)
    columns = default_columns(field, spacing=3.5)
    zoned = compute_tributary_zones(columns, panels)

    assert len(zoned) == len(columns)
    assert all(column.tributary_rect is not None for column in zoned)
    assert tributary_partition_valid(zoned, panels)
    assert sum(column.tributary_area_m2 for column in zoned) == pytest.approx(
        total_panel_area(panels)
    )


def test_tributary_strips_are_non_overlapping(panel: PanelSpec, config: LayoutConfig):
    panels = accumulate_grid(panel, config, num_pairs_per_row=4, num_rows=2)
    field = panel_field_bbox(panels)
    zoned = compute_tributary_zones(default_columns(field, spacing=2.0), panels)

    widths = sum(column.tributary_rect[2] for column in zoned if column.tributary_rect)
    assert widths == pytest.approx(field[2])


def test_compute_tributary_zones_empty_panels_returns_zero_area():
    columns = default_columns((0.0, 0.0, 6.0, 4.0), spacing=3.0)
    zoned = compute_tributary_zones(columns, [])
    assert all(column.tributary_area_m2 == 0.0 for column in zoned)


def test_enrich_tributary_loads_scales_with_area(panel: PanelSpec, config: LayoutConfig):
    panels = accumulate_grid(panel, config, num_pairs_per_row=3, num_rows=2)
    field = panel_field_bbox(panels)
    zoned = compute_tributary_zones(default_columns(field, spacing=3.5), panels)
    loaded = enrich_tributary_loads(zoned, panel)

    assert all(column.estimated_load_kn > 0 for column in loaded)
    assert sum(column.estimated_load_kn for column in loaded) == pytest.approx(
        panel.weight * len(panels) * 9.80665 / 1000.0,
        rel=1e-4,
    )


def test_estimated_dead_load_kn_zero_area(panel: PanelSpec):
    from core.tributary import estimated_dead_load_kn

    assert estimated_dead_load_kn(0.0, panel) == 0.0


def test_tributary_rect_stored_on_column(panel: PanelSpec, config: LayoutConfig):
    panels = accumulate_grid(panel, config, num_pairs_per_row=2, num_rows=1)
    field = panel_field_bbox(panels)
    zoned = compute_tributary_zones(default_columns(field, spacing=4.0), panels)
    first = zoned[0]
    assert first.tributary_rect is not None
    assert first.tributary_rect[1] == pytest.approx(field[1])
    assert first.tributary_rect[3] == pytest.approx(field[3])
