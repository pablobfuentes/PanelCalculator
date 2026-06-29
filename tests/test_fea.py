"""Tests for frame FEA (Phase 5.3)."""

import pytest

from core.columns import Column
from core.fea import (
    build_frame_model,
    design_wind_pressure_kn_m2,
    extract_member_results,
    run_frame_analysis,
)
from core.loads import load_combinations
from core.models import PanelSpec, WindConfig
from core.sections import default_material_sections
from core.tributary import enrich_tributary_loads, compute_tributary_zones


@pytest.fixture
def panel() -> PanelSpec:
    return PanelSpec(length=2.0, width=1.0, weight=25.0, tilt_angle=10.0)


@pytest.fixture
def wind() -> WindConfig:
    return WindConfig(wind_speed_kmh=120.0, exposure_category="B")


def _zoned_columns(panel: PanelSpec, coords: list[tuple[float, float]]) -> list[Column]:
    columns = [
        Column(column_id=f"C{index}", x=x, y=y)
        for index, (x, y) in enumerate(coords, start=1)
    ]
    panels = [(x - 0.5, y - 0.5, 1.0, 2.0) for x, y in coords]
    return enrich_tributary_loads(compute_tributary_zones(columns, panels), panel)


def test_design_wind_pressure_increases_with_speed():
    low = design_wind_pressure_kn_m2(80.0, "B")
    high = design_wind_pressure_kn_m2(160.0, "B")
    assert high > low


def test_build_frame_model_posts_and_chords():
    panel = PanelSpec(length=2.0, width=1.0, weight=25.0, tilt_angle=10.0)
    columns = _zoned_columns(
        panel, [(0.0, 0.0), (5.0, 0.0), (10.0, 0.0)]
    )
    model, member_types = build_frame_model(
        columns,
        column_height_m=2.5,
        materials=default_material_sections(),
        panel=panel,
        wind=WindConfig(),
    )
    assert len(model.nodes) == 6
    assert sum(1 for t in member_types.values() if t == "post") == 3
    assert sum(1 for t in member_types.values() if t == "chord") == 2
    assert len(load_combinations()) == len(model.load_combos)


def test_run_frame_analysis_all_combos(panel: PanelSpec, wind: WindConfig):
    columns = _zoned_columns(panel, [(0.0, 0.0), (5.0, 0.0)])
    result = run_frame_analysis(
        columns,
        column_height_m=3.0,
        materials=default_material_sections(),
        panel=panel,
        wind=wind,
    )
    assert result.solved
    assert result.member_count == 3  # 2 posts + 1 chord
    combo_ids = {row.combo_id for row in result.results}
    assert combo_ids == {"LC1", "LC2", "LC3"}
    post_lc1 = [r for r in result.results if r.element_id == "P_C1" and r.combo_id == "LC1"][0]
    assert post_lc1.max_axial_kn > 0


def test_extract_member_results_after_analyze(panel: PanelSpec, wind: WindConfig):
    columns = _zoned_columns(panel, [(0.0, 0.0), (5.0, 0.0)])
    model, member_types = build_frame_model(
        columns,
        column_height_m=3.0,
        materials=default_material_sections(),
        panel=panel,
        wind=wind,
    )
    model.analyze(check_stability=True)
    rows = extract_member_results(model, member_types)
    assert len(rows) == len(member_types) * len(load_combinations())


def test_run_frame_analysis_no_active_columns(panel: PanelSpec, wind: WindConfig):
    result = run_frame_analysis(
        [],
        column_height_m=3.0,
        materials=default_material_sections(),
        panel=panel,
        wind=wind,
    )
    assert not result.solved
    assert result.error
