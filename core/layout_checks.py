"""Layout-stage preliminary checks — rules of thumb, no chosen sections."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from core.bom import ROW_Y_TOLERANCE_M
from core.columns import Column, active_columns
from core.fea import DEFAULT_LIVE_LOAD_KN_M2

ElementType = Literal["column", "beam"]
PreliminaryStatus = Literal["PASS", "WARN", "FAIL"]


@dataclass(frozen=True)
class LayoutRules:
    """Generic limits for layout-stage screening (not section-specific)."""

    deflection_limit_denominator: float = 240.0
    assumed_beam_ei_nm2: float = 5.0e6
    assumed_column_capacity_kn: float = 30.0
    assumed_beam_moment_capacity_knm: float = 15.0
    max_recommended_beam_span_m: float = 6.0
    live_load_kn_m2: float = DEFAULT_LIVE_LOAD_KN_M2
    gravity_factor_d: float = 1.2
    gravity_factor_l: float = 1.6
    warn_utilization: float = 0.80


@dataclass(frozen=True)
class CheckItem:
    label: str
    value: float
    limit: float
    unit: str
    passed: bool


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

    axial_check = CheckItem(
        label="Factored axial load (gravity)",
        value=round(factored, 3),
        limit=rules.assumed_column_capacity_kn,
        unit="kN",
        passed=factored <= rules.assumed_column_capacity_kn,
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
            label="Span vs recommended max",
            value=round(span, 3),
            limit=rules.max_recommended_beam_span_m,
            unit="m",
            passed=span <= rules.max_recommended_beam_span_m,
        ),
        CheckItem(
            label="Est. moment (1.2D+1.6L, wL²/8)",
            value=round(moment_knm, 3),
            limit=rules.assumed_beam_moment_capacity_knm,
            unit="kN·m",
            passed=moment_knm <= rules.assumed_beam_moment_capacity_knm,
        ),
        CheckItem(
            label="Est. deflection vs L/240",
            value=round(deflection_m, 5),
            limit=round(deflection_limit, 5),
            unit="m",
            passed=deflection_m <= deflection_limit,
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
                "label": check.label,
                "value": check.value,
                "limit": check.limit,
                "unit": check.unit,
                "passed": check.passed,
            }
            for check in element.checks
        ],
    }
