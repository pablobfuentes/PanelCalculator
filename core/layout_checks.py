"""Layout-stage preliminary checks — rules of thumb, no chosen sections."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from core.bom import ROW_Y_TOLERANCE_M
from core.columns import DEFAULT_COLUMN_SPACING_M, Column, active_columns
from core.fea import DEFAULT_LIVE_LOAD_KN_M2

ElementType = Literal["column", "beam"]
PreliminaryStatus = Literal["PASS", "WARN", "FAIL"]

# Layout rule of thumb: ~two column bays at default grid spacing, minus end clearance.
# Not a code limit — full span design happens in Structure with chosen sections.
_DEFAULT_MAX_BEAM_SPAN_M = 2.0 * DEFAULT_COLUMN_SPACING_M - 1.0


@dataclass(frozen=True)
class LayoutRules:
    """Generic limits for layout-stage screening (not section-specific)."""

    deflection_limit_denominator: float = 240.0
    assumed_beam_ei_nm2: float = 5.0e6
    assumed_column_capacity_kn: float = 30.0
    assumed_beam_moment_capacity_knm: float = 15.0
    max_recommended_beam_span_m: float = _DEFAULT_MAX_BEAM_SPAN_M
    live_load_kn_m2: float = DEFAULT_LIVE_LOAD_KN_M2
    gravity_factor_d: float = 1.2
    gravity_factor_l: float = 1.6
    warn_utilization: float = 0.80


@dataclass(frozen=True)
class CalcVariable:
    name: str
    symbol: str
    value: float
    unit: str


@dataclass(frozen=True)
class CalcStep:
    label: str
    formula: str
    expression: str
    result: str


@dataclass(frozen=True)
class CheckDetail:
    variables: tuple[CalcVariable, ...]
    steps: tuple[CalcStep, ...]
    verdict: str


@dataclass(frozen=True)
class CheckItem:
    check_id: str
    label: str
    value: float
    limit: float
    unit: str
    passed: bool
    detail: CheckDetail | None = None


@dataclass(frozen=True)
class LayoutElement:
    element_id: str
    element_type: ElementType
    name: str
    x: float
    y: float
    x2: float | None = None
    y2: float | None = None
    span_m: float = 0.0
    dead_load_kn: float = 0.0
    live_load_kn: float = 0.0
    factored_load_kn: float = 0.0
    max_moment_knm: float = 0.0
    max_deflection_m: float = 0.0
    deflection_limit_m: float = 0.0
    max_torsion_knm: float = 0.0
    preliminary_status: PreliminaryStatus = "PASS"
    checks: tuple[CheckItem, ...] = ()
    overall_pass: bool = True


def _group_rows(columns: list[Column]) -> list[list[Column]]:
    rows: list[list[Column]] = []
    for column in sorted(columns, key=lambda item: (item.y, item.x)):
        y_key = round(column.y / ROW_Y_TOLERANCE_M)
        if not rows or round(rows[-1][0].y / ROW_Y_TOLERANCE_M) != y_key:
            rows.append([column])
        else:
            rows[-1].append(column)
    for row in rows:
        row.sort(key=lambda item: item.x)
    return rows


def _group_columns(columns: list[Column]) -> list[list[Column]]:
    """Group active columns that share the same X coordinate (column lines along Y)."""
    cols: list[list[Column]] = []
    for column in sorted(columns, key=lambda item: (item.x, item.y)):
        x_key = round(column.x / ROW_Y_TOLERANCE_M)
        if not cols or round(cols[-1][0].x / ROW_Y_TOLERANCE_M) != x_key:
            cols.append([column])
        else:
            cols[-1].append(column)
    for col_line in cols:
        col_line.sort(key=lambda item: item.y)
    return cols


def derive_layout_elements(
    columns: list[Column],
    *,
    rules: LayoutRules | None = None,
) -> tuple[LayoutElement, ...]:
    """Build column and beam logical members with preliminary checks."""
    rules = rules or LayoutRules()
    elements: list[LayoutElement] = []

    for column in columns:
        if column.excluded:
            continue
        elements.append(_check_column(column, rules))

    beam_index = 1
    active = active_columns(columns)
    for row in _group_rows(active):
        for start, end in zip(row, row[1:]):
            span = end.x - start.x
            if span <= 1e-6:
                continue
            beam_id = f"BM-H{beam_index:02d}"
            beam_index += 1
            elements.append(_check_beam(beam_id, start, end, span, rules))

    for col_line in _group_columns(active):
        for start, end in zip(col_line, col_line[1:]):
            span = end.y - start.y
            if span <= 1e-6:
                continue
            beam_id = f"BM-V{beam_index:02d}"
            beam_index += 1
            elements.append(_check_beam(beam_id, start, end, span, rules))

    return tuple(elements)


def _factored_gravity_kn(dead_kn: float, live_kn: float, rules: LayoutRules) -> float:
    return rules.gravity_factor_d * dead_kn + rules.gravity_factor_l * live_kn


def _column_axial_detail(
    column: Column,
    rules: LayoutRules,
    dead_kn: float,
    live_kn: float,
    factored: float,
    passed: bool,
) -> CheckDetail:
    trib = column.tributary_area_m2
    return CheckDetail(
        variables=(
            CalcVariable("Tributary area", "A_t", round(trib, 3), "m²"),
            CalcVariable("Dead load", "D", round(dead_kn, 3), "kN"),
            CalcVariable("Live load intensity", "q_L", rules.live_load_kn_m2, "kN/m²"),
            CalcVariable("Live load", "L", round(live_kn, 3), "kN"),
            CalcVariable("Gravity factor (dead)", "γ_D", rules.gravity_factor_d, "—"),
            CalcVariable("Gravity factor (live)", "γ_L", rules.gravity_factor_l, "—"),
            CalcVariable("Assumed capacity", "P_cap", rules.assumed_column_capacity_kn, "kN"),
        ),
        steps=(
            CalcStep(
                "Live load from tributary",
                "L = A_t × q_L",
                f"{trib:.3f} × {rules.live_load_kn_m2:.2f}",
                f"{live_kn:.3f} kN",
            ),
            CalcStep(
                "Factored axial load",
                "P_f = γ_D·D + γ_L·L",
                f"{rules.gravity_factor_d:.1f}×{dead_kn:.3f} + {rules.gravity_factor_l:.1f}×{live_kn:.3f}",
                f"{factored:.3f} kN",
            ),
            CalcStep(
                "Capacity screening",
                "P_f ≤ P_cap",
                f"{factored:.3f} ≤ {rules.assumed_column_capacity_kn:.1f}",
                "PASS" if passed else "FAIL",
            ),
        ),
        verdict=(
            "Factored gravity load is within the assumed column capacity."
            if passed
            else "Factored gravity load exceeds the assumed column capacity — choose a heavier section in Structure."
        ),
    )


def _beam_span_detail(
    span: float,
    limit: float,
    passed: bool,
    *,
    column_spacing_m: float = DEFAULT_COLUMN_SPACING_M,
) -> CheckDetail:
    return CheckDetail(
        variables=(
            CalcVariable("Beam span", "L", round(span, 3), "m"),
            CalcVariable("Recommended max span", "L_max", limit, "m"),
            CalcVariable("Default column spacing", "s_col", column_spacing_m, "m"),
        ),
        steps=(
            CalcStep(
                "Layout rule of thumb",
                "L_max = 2·s_col − 1 m",
                f"2 × {column_spacing_m:.1f} − 1",
                f"{limit:.1f} m",
            ),
            CalcStep(
                "Span check",
                "L ≤ L_max",
                f"{span:.3f} ≤ {limit:.1f}",
                "PASS" if passed else "FAIL",
            ),
        ),
        verdict=(
            "Span is within the recommended limit for preliminary layout "
            f"(~two {column_spacing_m:.1f} m bays, not a code check)."
            if passed
            else "Span exceeds the recommended maximum — consider adding columns or reducing bay spacing."
        ),
    )


def _beam_moment_detail(
    start: Column,
    end: Column,
    span: float,
    rules: LayoutRules,
    dead_kn: float,
    live_kn: float,
    factored: float,
    w_kn_m: float,
    moment_knm: float,
    passed: bool,
) -> CheckDetail:
    trib_avg = (start.tributary_area_m2 + end.tributary_area_m2) / 2.0
    return CheckDetail(
        variables=(
            CalcVariable("Span", "L", round(span, 3), "m"),
            CalcVariable("Avg. tributary area", "A_t,avg", round(trib_avg, 3), "m²"),
            CalcVariable("Dead load (mid-span)", "D", round(dead_kn, 3), "kN"),
            CalcVariable("Live load intensity", "q_L", rules.live_load_kn_m2, "kN/m²"),
            CalcVariable("Live load (mid-span)", "L", round(live_kn, 3), "kN"),
            CalcVariable("Factored load", "P_f", round(factored, 3), "kN"),
            CalcVariable("Factored line load", "w", round(w_kn_m, 4), "kN/m"),
            CalcVariable("Assumed moment capacity", "M_cap", rules.assumed_beam_moment_capacity_knm, "kN·m"),
        ),
        steps=(
            CalcStep(
                "Mid-span dead load",
                "D = (D₁ + D₂) / 2",
                f"({start.estimated_load_kn:.3f} + {end.estimated_load_kn:.3f}) / 2",
                f"{dead_kn:.3f} kN",
            ),
            CalcStep(
                "Mid-span live load",
                "L = A_t,avg × q_L",
                f"{trib_avg:.3f} × {rules.live_load_kn_m2:.2f}",
                f"{live_kn:.3f} kN",
            ),
            CalcStep(
                "Factored gravity",
                "P_f = γ_D·D + γ_L·L",
                f"{rules.gravity_factor_d:.1f}×{dead_kn:.3f} + {rules.gravity_factor_l:.1f}×{live_kn:.3f}",
                f"{factored:.3f} kN",
            ),
            CalcStep(
                "Uniform line load",
                "w = P_f / L",
                f"{factored:.3f} / {span:.3f}",
                f"{w_kn_m:.4f} kN/m",
            ),
            CalcStep(
                "Simply supported moment",
                "M = w·L² / 8",
                f"{w_kn_m:.4f} × {span:.3f}² / 8",
                f"{moment_knm:.3f} kN·m",
            ),
            CalcStep(
                "Moment capacity",
                "M ≤ M_cap",
                f"{moment_knm:.3f} ≤ {rules.assumed_beam_moment_capacity_knm:.1f}",
                "PASS" if passed else "FAIL",
            ),
        ),
        verdict=(
            "Estimated bending moment is within the assumed beam capacity."
            if passed
            else "Estimated bending moment exceeds the assumed capacity — verify section in Structure."
        ),
    )


def _beam_deflection_detail(
    span: float,
    rules: LayoutRules,
    w_kn_m: float,
    deflection_m: float,
    deflection_limit: float,
    passed: bool,
) -> CheckDetail:
    w_n_m = w_kn_m * 1000.0
    ei = rules.assumed_beam_ei_nm2
    denom = rules.deflection_limit_denominator
    return CheckDetail(
        variables=(
            CalcVariable("Span", "L", round(span, 3), "m"),
            CalcVariable("Line load", "w", round(w_kn_m, 4), "kN/m"),
            CalcVariable("Line load (SI)", "w", round(w_n_m, 2), "N/m"),
            CalcVariable("Assumed EI", "EI", ei, "N·m²"),
            CalcVariable("Deflection limit", "δ_lim", round(deflection_limit, 5), "m"),
            CalcVariable("Limit denominator", "n", denom, "—"),
        ),
        steps=(
            CalcStep(
                "Convert line load",
                "w [N/m] = w [kN/m] × 1000",
                f"{w_kn_m:.4f} × 1000",
                f"{w_n_m:.2f} N/m",
            ),
            CalcStep(
                "Simply supported deflection",
                "δ = 5·w·L⁴ / (384·EI)",
                f"5 × {w_n_m:.2f} × {span:.3f}⁴ / (384 × {ei:.2e})",
                f"{deflection_m:.5f} m",
            ),
            CalcStep(
                "Allowable deflection",
                f"δ_lim = L / {denom:.0f}",
                f"{span:.3f} / {denom:.0f}",
                f"{deflection_limit:.5f} m",
            ),
            CalcStep(
                "Deflection check",
                "δ ≤ δ_lim",
                f"{deflection_m:.5f} ≤ {deflection_limit:.5f}",
                "PASS" if passed else "FAIL",
            ),
        ),
        verdict=(
            f"Estimated deflection is within L/{denom:.0f} for preliminary screening."
            if passed
            else f"Estimated deflection exceeds L/{denom:.0f} — increase stiffness or reduce span."
        ),
    )


def _status_from_checks(checks: tuple[CheckItem, ...]) -> PreliminaryStatus:
    if not checks:
        return "PASS"
    if all(item.passed for item in checks):
        return "PASS"
    failed = [item for item in checks if not item.passed]
    for item in failed:
        if item.value > item.limit * LayoutRules().warn_utilization:
            return "FAIL"
    return "FAIL"


def _check_column(column: Column, rules: LayoutRules) -> LayoutElement:
    dead_kn = column.estimated_load_kn
    live_kn = column.tributary_area_m2 * rules.live_load_kn_m2
    factored = _factored_gravity_kn(dead_kn, live_kn, rules)

    axial_passed = factored <= rules.assumed_column_capacity_kn
    axial_detail = _column_axial_detail(column, rules, dead_kn, live_kn, factored, axial_passed)
    axial_check = CheckItem(
        check_id="factored_axial",
        label="Factored axial load (gravity)",
        value=round(factored, 3),
        limit=rules.assumed_column_capacity_kn,
        unit="kN",
        passed=axial_passed,
        detail=axial_detail,
    )
    checks = (axial_check,)
    status: PreliminaryStatus = "PASS" if axial_check.passed else "FAIL"
    if not axial_check.passed and factored <= rules.assumed_column_capacity_kn / rules.warn_utilization:
        status = "WARN"

    return LayoutElement(
        element_id=f"COL-{column.column_id}",
        element_type="column",
        name=f"Column {column.column_id}",
        x=column.x,
        y=column.y,
        span_m=0.0,
        dead_load_kn=dead_kn,
        live_load_kn=live_kn,
        factored_load_kn=factored,
        max_moment_knm=0.0,
        max_deflection_m=0.0,
        deflection_limit_m=0.0,
        max_torsion_knm=0.0,
        preliminary_status=status,
        checks=checks,
        overall_pass=status == "PASS",
    )


def _check_beam(
    beam_id: str,
    start: Column,
    end: Column,
    span: float,
    rules: LayoutRules,
) -> LayoutElement:
    dead_kn = (start.estimated_load_kn + end.estimated_load_kn) / 2.0
    live_area = (start.tributary_area_m2 + end.tributary_area_m2) / 2.0
    live_kn = live_area * rules.live_load_kn_m2
    factored = _factored_gravity_kn(dead_kn, live_kn, rules)

    w_kn_m = factored / span if span > 0 else 0.0
    moment_knm = w_kn_m * span**2 / 8.0
    deflection_limit = span / rules.deflection_limit_denominator
    w_n_m = w_kn_m * 1000.0
    deflection_m = (
        5.0 * w_n_m * span**4 / (384.0 * rules.assumed_beam_ei_nm2)
        if rules.assumed_beam_ei_nm2 > 0
        else 0.0
    )

    checks_list: list[CheckItem] = [
        CheckItem(
            check_id="span_max",
            label="Span vs recommended max",
            value=round(span, 3),
            limit=rules.max_recommended_beam_span_m,
            unit="m",
            passed=span <= rules.max_recommended_beam_span_m,
            detail=_beam_span_detail(
                span,
                rules.max_recommended_beam_span_m,
                span <= rules.max_recommended_beam_span_m,
            ),
        ),
        CheckItem(
            check_id="moment",
            label="Est. moment (1.2D+1.6L, wL²/8)",
            value=round(moment_knm, 3),
            limit=rules.assumed_beam_moment_capacity_knm,
            unit="kN·m",
            passed=moment_knm <= rules.assumed_beam_moment_capacity_knm,
            detail=_beam_moment_detail(
                start,
                end,
                span,
                rules,
                dead_kn,
                live_kn,
                factored,
                w_kn_m,
                moment_knm,
                moment_knm <= rules.assumed_beam_moment_capacity_knm,
            ),
        ),
        CheckItem(
            check_id="deflection",
            label="Est. deflection vs L/240",
            value=round(deflection_m, 5),
            limit=round(deflection_limit, 5),
            unit="m",
            passed=deflection_m <= deflection_limit,
            detail=_beam_deflection_detail(
                span,
                rules,
                w_kn_m,
                deflection_m,
                deflection_limit,
                deflection_m <= deflection_limit,
            ),
        ),
    ]
    checks = tuple(checks_list)
    all_pass = all(item.passed for item in checks)
    status: PreliminaryStatus = "PASS" if all_pass else "FAIL"
    if not all_pass:
        worst = max(
            (item.value / item.limit if item.limit > 0 else 0.0 for item in checks_list),
            default=0.0,
        )
        if worst <= 1.0 / rules.warn_utilization:
            status = "WARN"

    return LayoutElement(
        element_id=beam_id,
        element_type="beam",
        name=beam_id,
        x=start.x,
        y=start.y,
        x2=end.x,
        y2=end.y,
        span_m=span,
        dead_load_kn=dead_kn,
        live_load_kn=live_kn,
        factored_load_kn=factored,
        max_moment_knm=moment_knm,
        max_deflection_m=deflection_m,
        deflection_limit_m=deflection_limit,
        max_torsion_knm=0.0,
        preliminary_status=status,
        checks=checks,
        overall_pass=all_pass,
    )


def layout_summary_metrics(elements: tuple[LayoutElement, ...]) -> dict[str, int | float]:
    passing = sum(1 for element in elements if element.overall_pass)
    total = len(elements)
    return {
        "element_count": total,
        "elements_passing": passing,
        "beam_count": sum(1 for element in elements if element.element_type == "beam"),
        "beam_length_m": sum(element.span_m for element in elements if element.element_type == "beam"),
        "total_dead_kn": sum(element.dead_load_kn for element in elements if element.element_type == "column"),
        "total_live_kn": sum(element.live_load_kn for element in elements if element.element_type == "column"),
    }


def _detail_to_dict(detail: CheckDetail | None) -> dict | None:
    if detail is None:
        return None
    return {
        "variables": [
            {
                "name": variable.name,
                "symbol": variable.symbol,
                "value": variable.value,
                "unit": variable.unit,
            }
            for variable in detail.variables
        ],
        "steps": [
            {
                "label": step.label,
                "formula": step.formula,
                "expression": step.expression,
                "result": step.result,
            }
            for step in detail.steps
        ],
        "verdict": detail.verdict,
    }


def element_to_api_dict(element: LayoutElement) -> dict:
    return {
        "element_id": element.element_id,
        "element_type": element.element_type,
        "name": element.name,
        "x": element.x,
        "y": element.y,
        "x2": element.x2,
        "y2": element.y2,
        "span_m": element.span_m,
        "dead_load_kn": element.dead_load_kn,
        "live_load_kn": element.live_load_kn,
        "factored_load_kn": element.factored_load_kn,
        "max_moment_knm": element.max_moment_knm,
        "max_deflection_m": element.max_deflection_m,
        "deflection_limit_m": element.deflection_limit_m,
        "max_torsion_knm": element.max_torsion_knm,
        "preliminary_status": element.preliminary_status,
        "overall_pass": element.overall_pass,
        "checks": [
            {
                "check_id": check.check_id,
                "label": check.label,
                "value": check.value,
                "limit": check.limit,
                "unit": check.unit,
                "passed": check.passed,
                "detail": _detail_to_dict(check.detail),
            }
            for check in element.checks
        ],
    }
