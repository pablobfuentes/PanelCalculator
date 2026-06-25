"""Tests for panel layout functions."""

import pytest

from core.layout import (
    GridLayout,
    accumulate_grid,
    accumulate_row,
    compute_alley_positions,
    collect_alley_rects,
    parallel_alley_gap_labels,
    fit_to_area,
    fit_to_panel_count,
    grid_bbox,
    layout_bbox,
    pair_panels,
)
from core.models import LayoutConfig, PanelSpec


@pytest.fixture
def panel() -> PanelSpec:
    return PanelSpec(length=2.0, width=1.0, weight=25.0, tilt_angle=10.0)


@pytest.fixture
def config() -> LayoutConfig:
    return LayoutConfig(mid_clamp_gap=0.1, alley_width=1.0, max_area_x=50.0, max_area_y=50.0)


def test_pair_panels_bbox(panel: PanelSpec, config: LayoutConfig):
    assert pair_panels(panel, config) == (0.0, 0.0, 2.1, 2.0)


def test_pair_panels_with_origin(panel: PanelSpec, config: LayoutConfig):
    assert pair_panels(panel, config, origin_x=3.0, origin_y=4.0) == (3.0, 4.0, 2.1, 2.0)


def test_accumulate_row_one_pair(panel: PanelSpec, config: LayoutConfig):
    rects = accumulate_row(panel, config, num_pairs=1)
    assert rects == [(0.0, 0.0, 1.0, 2.0), (1.1, 0.0, 1.0, 2.0)]


def test_accumulate_row_two_pairs_no_alley(panel: PanelSpec, config: LayoutConfig):
    rects = accumulate_row(panel, config, num_pairs=2)
    assert len(rects) == 4
    assert rects[0] == (0.0, 0.0, 1.0, 2.0)
    assert rects[1] == (1.1, 0.0, 1.0, 2.0)
    assert rects[2] == (3.1, 0.0, 1.0, 2.0)
    assert rects[3] == pytest.approx((4.2, 0.0, 1.0, 2.0))
    assert grid_bbox(rects) == pytest.approx((0.0, 0.0, 5.2, 2.0))


def test_accumulate_row_three_pairs_inserts_alley(panel: PanelSpec, config: LayoutConfig):
    rects = accumulate_row(panel, config, num_pairs=3)
    assert len(rects) == 6
    assert rects[4] == pytest.approx((5.3, 0.0, 1.0, 2.0))
    assert grid_bbox(rects) == pytest.approx((0.0, 0.0, 7.4, 2.0))


def test_accumulate_grid_two_rows(panel: PanelSpec, config: LayoutConfig):
    rects = accumulate_grid(panel, config, num_pairs_per_row=1, num_rows=2)
    assert len(rects) == 4
    assert rects[0] == (0.0, 1.0, 1.0, 2.0)
    assert rects[2] == (0.0, 3.0, 1.0, 2.0)
    assert layout_bbox(panel, config, 1, 2) == pytest.approx((0.0, 0.0, 2.1, 5.0))


def test_accumulate_grid_three_rows_stack_without_horizontal_alleys(
    panel: PanelSpec, config: LayoutConfig
):
    rects = accumulate_grid(panel, config, num_pairs_per_row=1, num_rows=3)
    assert len(rects) == 6
    assert rects[4] == (0.0, 5.0, 1.0, 2.0)
    assert layout_bbox(panel, config, 1, 3) == pytest.approx((0.0, 0.0, 2.1, 7.0))
    row_origins = sorted({rect[1] for rect in rects})
    assert row_origins == [config.alley_width + row * panel.length for row in range(3)]


def test_fit_to_area_returns_largest_layout(panel: PanelSpec):
    config = LayoutConfig(
        mid_clamp_gap=0.1,
        alley_width=1.0,
        max_area_x=5.0,
        max_area_y=5.0,
    )
    result = fit_to_area(panel, config)
    assert isinstance(result, GridLayout)
    assert result.num_pairs_per_row == 1
    assert result.num_rows == 2
    assert len(result.rectangles) == 4
    assert result.bbox[2] <= config.max_area_x
    assert result.bbox[3] <= config.max_area_y


def test_fit_to_area_too_small_returns_empty(panel: PanelSpec):
    config = LayoutConfig(max_area_x=1.0, max_area_y=1.0)
    result = fit_to_area(panel, config)
    assert result.num_pairs_per_row == 0
    assert result.num_rows == 0
    assert result.rectangles == ()


def test_panel_grid_factorizations_twelve_panels():
    from core.layout import _panel_grid_factorizations

    assert _panel_grid_factorizations(12) == [(1, 6), (2, 3), (3, 2), (6, 1)]


def test_fit_to_panel_count_twelve_panels_in_default_area(panel: PanelSpec):
    config = LayoutConfig(
        mid_clamp_gap=0.1,
        alley_width=1.0,
        max_area_x=12.0,
        max_area_y=8.0,
    )
    result = fit_to_panel_count(panel, config, 12)
    assert len(result.rectangles) == 12
    assert result.num_pairs_per_row * 2 * result.num_rows == 12
    assert result.bbox[2] <= config.max_area_x
    assert result.bbox[3] <= config.max_area_y


def test_fit_to_panel_count_odd_count_returns_empty(panel: PanelSpec, config: LayoutConfig):
    result = fit_to_panel_count(panel, config, 11)
    assert result.num_pairs_per_row == 0
    assert result.rectangles == ()


def test_fit_to_panel_count_too_large_returns_empty(panel: PanelSpec):
    config = LayoutConfig(max_area_x=5.0, max_area_y=5.0)
    result = fit_to_panel_count(panel, config, 24)
    assert result.rectangles == ()


def test_accumulate_row_rejects_negative_pairs(panel: PanelSpec, config: LayoutConfig):
    with pytest.raises(ValueError):
        accumulate_row(panel, config, num_pairs=-1)


def test_accumulate_grid_rejects_negative_counts(panel: PanelSpec, config: LayoutConfig):
    with pytest.raises(ValueError):
        accumulate_grid(panel, config, num_pairs_per_row=-1, num_rows=1)


def test_layout_bbox_includes_perimeter_alleys(panel: PanelSpec, config: LayoutConfig):
    assert layout_bbox(panel, config, num_pairs_per_row=2, num_rows=2) == (
        0.0,
        0.0,
        5.2,
        5.0,
    )


def test_compute_alley_positions_reach_two_eight_columns():
    assert compute_alley_positions(num_cols=8, reach=2) == [1, 5]


def test_compute_alley_positions_reach_three_twelve_columns():
    assert compute_alley_positions(num_cols=12, reach=3) == [2, 8]


def test_parallel_alley_gap_labels_reach_three_twelve_columns():
    assert parallel_alley_gap_labels(num_cols=12, reach=3) == ["3-4", "9-10"]


def test_compute_alley_positions_does_not_add_trailing_alley():
    assert compute_alley_positions(num_cols=4, reach=4) == []


def test_all_panel_columns_are_within_reach_of_parallel_alley():
    num_cols = 8
    reach = 2
    alley_positions = compute_alley_positions(num_cols, reach)
    assert all(
        any(abs(column - alley_after - 0.5) <= reach for alley_after in alley_positions)
        for column in range(num_cols)
    )


def test_collect_alley_rects_has_one_spine_and_minimal_parallel_alleys(
    panel: PanelSpec, config: LayoutConfig
):
    alleys = collect_alley_rects(panel, config, num_pairs_per_row=4, num_rows=2)
    spine = [rect for rect in alleys if rect[1] == 0.0 and rect[3] == config.alley_width]
    parallel = [rect for rect in alleys if rect[3] > config.alley_width]
    assert len(spine) == 1
    assert len(parallel) == 2
    assert all(rect[1] == config.alley_width for rect in parallel)


def test_collect_alley_rects_only_one_horizontal_spine(panel: PanelSpec, config: LayoutConfig):
    alleys = collect_alley_rects(panel, config, num_pairs_per_row=6, num_rows=8)
    horizontal = [
        rect
        for rect in alleys
        if rect[3] <= config.alley_width + 1e-9 and rect[2] > config.alley_width
    ]
    vertical = [rect for rect in alleys if rect[3] > config.alley_width + 1e-9]
    assert len(horizontal) == 1
    assert horizontal[0][1] == 0.0
    assert len(vertical) == len(compute_alley_positions(12, config.alley_reach))


def test_alley_positions_change_with_reach(panel: PanelSpec):
    config = LayoutConfig(mid_clamp_gap=0.1, alley_width=0.9, alley_reach=2)
    alleys_r2 = collect_alley_rects(panel, config, num_pairs_per_row=6, num_rows=2)
    parallel_r2 = [a for a in alleys_r2 if a[3] > config.alley_width]

    config = LayoutConfig(mid_clamp_gap=0.1, alley_width=0.9, alley_reach=4)
    alleys_r4 = collect_alley_rects(panel, config, num_pairs_per_row=6, num_rows=2)
    parallel_r4 = [a for a in alleys_r4 if a[3] > config.alley_width]

    assert len(parallel_r2) == 3
    assert len(parallel_r4) == 1
    assert [a[0] for a in parallel_r2] != [a[0] for a in parallel_r4]


def test_reach_three_six_pairs_places_alleys_between_columns_three_four_and_nine_ten(
    panel: PanelSpec,
):
    config = LayoutConfig(
        mid_clamp_gap=0.1,
        alley_width=0.9,
        alley_reach=3,
        max_area_x=50.0,
        max_area_y=50.0,
    )
    alleys = collect_alley_rects(panel, config, num_pairs_per_row=6, num_rows=8)
    parallel = [rect for rect in alleys if rect[3] > config.alley_width]
    expected = [(3.2, 0.9, 0.9, 16.0), (10.6, 0.9, 0.9, 16.0)]
    assert len(parallel) == len(expected)
    for actual, expected_rect in zip(parallel, expected):
        assert actual == pytest.approx(expected_rect)
