"""Tests for structural code checks (Phase 5.4)."""

import pytest

from core.code_checks import (
    allowable_bending_stress_mpa,
    classify_status,
    evaluate_member_check,
    utilization_ratio,
)
from core.fea import MemberForces
from core.sections import default_material_sections


def _member_row(**kwargs) -> MemberForces:
    defaults = dict(
        element_id="P_C1",
        element_type="post",
        combo_id="LC1",
        max_moment_knm=1.0,
        max_axial_kn=5.0,
        max_deflection_m=0.001,
        member_length_m=3.0,
    )
    defaults.update(kwargs)
    return MemberForces(**defaults)


def test_allowable_bending_is_066_fy():
    assert allowable_bending_stress_mpa(250.0) == pytest.approx(165.0)


def test_classify_status_thresholds():
    assert classify_status(0.5) == "PASS"
    assert classify_status(0.85) == "WARN"
    assert classify_status(1.1) == "FAIL"


def test_evaluate_member_check_deflection_governs():
    materials = default_material_sections()
    row = _member_row(max_moment_knm=0.0, max_deflection_m=0.02, member_length_m=3.0)
    check = evaluate_member_check(row, materials=materials)
    assert check.governing_check == "deflection"
    assert check.deflection_allow_m == pytest.approx(3.0 / 240.0)


def test_high_moment_fails_bending():
    materials = default_material_sections()
    row = _member_row(max_moment_knm=500.0, max_deflection_m=0.0)
    check = evaluate_member_check(row, materials=materials)
    assert check.status == "FAIL"
    assert check.bending_utilization > 1.0
