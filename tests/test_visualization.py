"""Tests for layout visualization and complete Phase 2.3 coverage."""

from pathlib import Path

import plotly.graph_objects as go
import pytest

from core.layout import (
    collect_alley_rects,
    collect_row_alley_rects,
    grid_bbox,
)
from core.models import LayoutConfig, PanelSpec
from core.visualization import build_layout_figure, save_layout_figure

REFERENCE_PAIRS = 3
REFERENCE_ROWS = 2


@pytest.fixture
def panel() -> PanelSpec:
    return PanelSpec(length=2.0, width=1.0, weight=25.0, tilt_angle=10.0)


@pytest.fixture
def config() -> LayoutConfig:
    return LayoutConfig(
        mid_clamp_gap=0.1,
        alley_width=1.0,
        max_area_x=12.0,
        max_area_y=8.0,
    )


def test_collect_row_alley_rects_three_pairs(panel: PanelSpec, config: LayoutConfig):
    alleys = collect_row_alley_rects(panel, config, num_pairs=3)
    assert alleys == [(2.1, 0.0, 1.0, 2.0)]


def test_collect_alley_rects_three_rows_has_columns_and_edges_no_horizontal_gaps(
    panel: PanelSpec, config: LayoutConfig
):
    alleys = collect_alley_rects(panel, config, num_pairs_per_row=3, num_rows=3)
    assert (0.0, 0.0, 7.4, 1.0) in alleys
    assert (2.1, 1.0, 1.0, 6.0) in alleys
    assert len([a for a in alleys if a[3] == 1.0 and a[2] > 1.0]) == 1


def test_collect_alley_rects_two_rows_perimeter_and_column(
    panel: PanelSpec, config: LayoutConfig
):
    alleys = collect_alley_rects(panel, config, num_pairs_per_row=3, num_rows=2)
    assert alleys == [
        (0.0, 0.0, 7.4, 1.0),
        (2.1, 1.0, 1.0, 4.0),
    ]


def test_build_layout_figure_with_tributary_overlay(panel: PanelSpec, config: LayoutConfig):
    from core.tributary import compute_tributary_zones, default_columns, enrich_tributary_loads, panel_field_bbox
    from core.layout import accumulate_grid
    from core.visualization import build_layout_figure

    panels = accumulate_grid(panel, config, REFERENCE_PAIRS, REFERENCE_ROWS)
    field = panel_field_bbox(panels)
    columns = enrich_tributary_loads(
        compute_tributary_zones(default_columns(field, spacing=3.5), panels),
        panel,
    )
    fig = build_layout_figure(
        panel, config, REFERENCE_PAIRS, REFERENCE_ROWS, tributary_columns=columns
    )
    tributary_traces = [t for t in fig.data if t.legendgroup == "tributary"]
    column_traces = [t for t in fig.data if t.legendgroup == "columns"]
    assert len(tributary_traces) == len(columns)
    assert len(column_traces) == len(columns)
    assert tributary_traces[0].hovertemplate is not None


def test_load_intensity_color_endpoints():
    from core.visualization import _load_intensity_color

    assert "144" in _load_intensity_color(0.0)
    assert "220" in _load_intensity_color(1.0)


def test_build_layout_figure_reference_layout(panel: PanelSpec, config: LayoutConfig):
    fig = build_layout_figure(panel, config, REFERENCE_PAIRS, REFERENCE_ROWS)
    assert isinstance(fig, go.Figure)
    assert fig.layout.xaxis.range[0] == 0
    assert fig.layout.yaxis.range[0] == 0
    assert fig.layout.xaxis.constrain == "domain"
    assert fig.layout.yaxis.constrain == "domain"

    panels = [s for s in fig.layout.shapes if s.fillcolor == "rgba(46, 134, 193, 0.85)"]
    alleys = [
        s
        for s in fig.layout.shapes
        if s.fillcolor in ("rgba(231, 76, 60, 0.35)", "rgba(192, 57, 43, 0.45)")
    ]
    bbox_shapes = [
        s
        for s in fig.layout.shapes
        if s.line.color == "#27ae60" and getattr(s.line, "dash", None) == "dash"
    ]

    assert len(panels) == REFERENCE_PAIRS * REFERENCE_ROWS * 2
    assert len(alleys) == 2  # one edge spine + one parallel alley
    assert len(bbox_shapes) == 1

    panel_shapes = [(shape.x0, shape.y0, shape.x1 - shape.x0, shape.y1 - shape.y0) for shape in panels]
    alley_shapes = [(shape.x0, shape.y0, shape.x1 - shape.x0, shape.y1 - shape.y0) for shape in alleys]
    expected = grid_bbox(panel_shapes + alley_shapes)
    bbox_shape = bbox_shapes[0]
    assert bbox_shape.x1 == pytest.approx(expected[2])
    assert bbox_shape.y1 == pytest.approx(expected[3])


def test_save_reference_layout_html(panel: PanelSpec, config: LayoutConfig, tmp_path: Path):
    fig = build_layout_figure(panel, config, REFERENCE_PAIRS, REFERENCE_ROWS)
    output = save_layout_figure(fig, tmp_path / "reference_layout.html")
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "plotly" in content.lower()
    assert "Panel layout" in content


def test_write_project_reference_layout(panel: PanelSpec, config: LayoutConfig):
    """Generate outputs/reference_layout.html for manual visual confirmation."""
    fig = build_layout_figure(panel, config, REFERENCE_PAIRS, REFERENCE_ROWS)
    output = save_layout_figure(fig, Path("outputs/reference_layout.html"))
    assert output.exists()
