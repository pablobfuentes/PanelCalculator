"""Tests for live BOM (Phase 4.3)."""

import pytest

from core.bom import (
    compute_bom,
    horizontal_truss_spans,
    ptr_length_m,
    truss_chord_length_m,
)
from core.columns import Column
from core.models import LayoutConfig, PanelSpec
from ui.layout_state import ResolvedLayout, bom_panel_count


@pytest.fixture
def panel() -> PanelSpec:
    return PanelSpec(length=2.0, width=1.0, weight=25.0, tilt_angle=10.0)


def test_ptr_length_includes_embedment():
    assert ptr_length_m(2.5) == pytest.approx(3.1)


def test_horizontal_truss_spans_regular_grid():
    columns = [
        Column(column_id="C1", x=0.0, y=0.0),
        Column(column_id="C2", x=5.0, y=0.0),
        Column(column_id="C3", x=10.0, y=0.0),
        Column(column_id="C4", x=0.0, y=4.0),
        Column(column_id="C5", x=5.0, y=4.0),
        Column(column_id="C6", x=10.0, y=4.0),
    ]
    assert horizontal_truss_spans(columns) == pytest.approx([5.0, 5.0, 5.0, 5.0])
    assert truss_chord_length_m(columns) == pytest.approx(40.0)


def test_compute_bom_active_columns_only():
    columns = [
        Column(column_id="C1", x=0.0, y=0.0),
        Column(column_id="C2", x=5.0, y=0.0, excluded=True),
        Column(column_id="C3", x=10.0, y=0.0),
    ]
    bom = compute_bom(panel_count=12, columns=columns, column_height_m=2.5)

    assert bom.panel_count == 12
    assert bom.column_count == 3
    assert bom.active_column_count == 2
    assert bom.base_plate_count == 2
    assert bom.ptr_total_length_m == pytest.approx(2 * ptr_length_m(2.5))
    assert bom.truss_chord_length_m == pytest.approx(20.0)
    assert bom.steel_tonnage > 0


def test_bom_panel_count_uses_locked_target(panel: PanelSpec):
    config = LayoutConfig()
    layout = ResolvedLayout(
        panel=panel,
        config=config,
        num_pairs_per_row=3,
        num_rows=2,
        panel_count=24,
        panels_locked=True,
        locked_panel_count=12,
        use_fit=True,
        panels=[],
        alleys=[],
        bbox=(0.0, 0.0, 10.0, 8.0),
    )
    assert bom_panel_count(layout) == 12
    assert bom_panel_count(layout, live_locked=True, live_locked_count=8) == 8
