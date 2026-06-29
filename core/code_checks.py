"""Structural code checks on FEA member results (Phase 5.4)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from core.fea import MemberForces
from core.sections import MaterialSections, SteelSection

DEFAULT_DEFLECTION_LIMIT_DENOMINATOR = 240.0
BENDING_ALLOWANCE_FACTOR = 0.66
WARN_UTILIZATION_THRESHOLD = 0.80

CheckStatus = Literal["PASS", "WARN", "FAIL"]


@dataclass(frozen=True)
class CodeCheckResult:
    """Utilization and status for one member and load combination."""

    element_id: str
    element_type: str
    combo_id: str
    member_length_m: float
    fb_mpa: float
    fb_allow_mpa: float
    bending_utilization: float
    deflection_m: float
    deflection_allow_m: float
    deflection_utilization: float
    governing_utilization: float
    governing_check: str
    status: CheckStatus


def section_for_element_type(
    element_type: str, materials: MaterialSections
) -> SteelSection:
    if element_type == "post":
        return materials.ptr_post
    if element_type == "chord":
        return materials.truss_chord
    return materials.secondary_beam


def section_modulus_m3(section: SteelSection) -> float:
    sx = section.Sx
    if sx is not None and sx > 0:
        return sx
    if section.outer_depth_m is not None and section.outer_depth_m > 0:
        return 2.0 * section.Ix / section.outer_depth_m
    raise ValueError(f"Cannot derive Sx for section {section.name!r}")


def bending_stress_mpa(moment_knm: float, section: SteelSection) -> float:
    """Bending stress fb = M / S (MPa)."""
    sx = section_modulus_m3(section)
    moment_nm = moment_knm * 1000.0
    return moment_nm / sx / 1_000_000.0


def allowable_bending_stress_mpa(fy_mpa: float) -> float:
    return BENDING_ALLOWANCE_FACTOR * fy_mpa


def allowable_deflection_m(member_length_m: float, *, denominator: float) -> float:
    if member_length_m <= 0:
        raise ValueError("member_length_m must be positive")
    return member_length_m / denominator


def utilization_ratio(demand: float, capacity: float) -> float:
    if capacity <= 0:
        return float("inf") if demand > 0 else 0.0
    return demand / capacity


def classify_status(utilization: float) -> CheckStatus:
    if utilization > 1.0:
        return "FAIL"
    if utilization > WARN_UTILIZATION_THRESHOLD:
        return "WARN"
    return "PASS"


def evaluate_member_check(
    row: MemberForces,
    *,
    materials: MaterialSections,
    deflection_limit_denominator: float = DEFAULT_DEFLECTION_LIMIT_DENOMINATOR,
) -> CodeCheckResult:
    """Check bending and deflection for one FEA result row."""
    section = section_for_element_type(row.element_type, materials)
    fb = bending_stress_mpa(row.max_moment_knm, section)
    fb_allow = allowable_bending_stress_mpa(section.Fy)
    bend_util = utilization_ratio(fb, fb_allow)

    delta_allow = allowable_deflection_m(
        row.member_length_m, denominator=deflection_limit_denominator
    )
    defl_util = utilization_ratio(row.max_deflection_m, delta_allow)

    if bend_util >= defl_util:
        governing_util = bend_util
        governing_check = "bending"
    else:
        governing_util = defl_util
        governing_check = "deflection"

    return CodeCheckResult(
        element_id=row.element_id,
        element_type=row.element_type,
        combo_id=row.combo_id,
        member_length_m=row.member_length_m,
        fb_mpa=fb,
        fb_allow_mpa=fb_allow,
        bending_utilization=bend_util,
        deflection_m=row.max_deflection_m,
        deflection_allow_m=delta_allow,
        deflection_utilization=defl_util,
        governing_utilization=governing_util,
        governing_check=governing_check,
        status=classify_status(governing_util),
    )


def evaluate_code_checks(
    results: tuple[MemberForces, ...],
    *,
    materials: MaterialSections,
    deflection_limit_denominator: float = DEFAULT_DEFLECTION_LIMIT_DENOMINATOR,
) -> tuple[CodeCheckResult, ...]:
    return tuple(
        evaluate_member_check(
            row,
            materials=materials,
            deflection_limit_denominator=deflection_limit_denominator,
        )
        for row in results
    )


def code_check_rows(checks: tuple[CodeCheckResult, ...]) -> list[dict[str, object]]:
    return [
        {
            "Element": check.element_id,
            "Type": check.element_type,
            "Combo": check.combo_id,
            "fb (MPa)": round(check.fb_mpa, 2),
            "fb allow (MPa)": round(check.fb_allow_mpa, 2),
            "δ (m)": round(check.deflection_m, 5),
            "δ allow (m)": round(check.deflection_allow_m, 5),
            "Utilization": round(check.governing_utilization, 3),
            "Governs": check.governing_check,
            "Status": check.status,
        }
        for check in checks
    ]
