"""Bill of materials estimates for panel racking (Phase 4.3)."""

from __future__ import annotations

from dataclasses import dataclass

from core.columns import Column, active_columns

# Placeholder section weights (kg/m) — replace with SteelSection in Phase 5.
PTR_4X4_KG_PER_M = 23.0
TRUSS_CHORD_KG_PER_M = 8.5

DEFAULT_POST_EMBEDMENT_M = 0.6
DEFAULT_COLUMN_HEIGHT_M = 2.5
ROW_Y_TOLERANCE_M = 0.05

# Warren truss: top + bottom chord per horizontal bay.
CHORDS_PER_TRUSS_BAY = 2


@dataclass(frozen=True)
class BomLine:
    """Single BOM row for display."""

    item: str
    quantity: float
    unit: str
    note: str = ""


@dataclass(frozen=True)
class BomResult:
    """Live BOM summary for the current layout and column grid."""

    panel_count: int
    column_count: int
    active_column_count: int
    ptr_total_length_m: float
    truss_chord_length_m: float
    base_plate_count: int
    steel_tonnage: float
    lines: tuple[BomLine, ...]


def ptr_length_m(column_height_m: float, *, embedment_m: float = DEFAULT_POST_EMBEDMENT_M) -> float:
    """Total PTR stock length per post (column height + embedment)."""
    if column_height_m <= 0:
        raise ValueError("column_height_m must be positive")
    return column_height_m + embedment_m


def horizontal_truss_spans(
    columns: list[Column],
    *,
    y_tolerance: float = ROW_Y_TOLERANCE_M,
) -> list[float]:
    """Centre-to-centre spans between adjacent columns on each Y row."""
    active = active_columns(columns)
    if len(active) < 2:
        return []

    rows: list[list[Column]] = []
    for column in sorted(active, key=lambda item: (item.y, item.x)):
        y_key = round(column.y / y_tolerance)
        if not rows or round(rows[-1][0].y / y_tolerance) != y_key:
            rows.append([column])
        else:
            rows[-1].append(column)

    spans: list[float] = []
    for row in rows:
        ordered = sorted(row, key=lambda item: item.x)
        for index in range(1, len(ordered)):
            span = ordered[index].x - ordered[index - 1].x
            if span > 1e-6:
                spans.append(span)
    return spans


def truss_chord_length_m(columns: list[Column]) -> float:
    """Sum of truss chord steel along all horizontal bays (top + bottom)."""
    return CHORDS_PER_TRUSS_BAY * sum(horizontal_truss_spans(columns))


def steel_tonnage(ptr_length_m: float, chord_length_m: float) -> float:
    """Estimated structural steel mass (tonnes)."""
    mass_kg = (
        ptr_length_m * PTR_4X4_KG_PER_M + chord_length_m * TRUSS_CHORD_KG_PER_M
    )
    return mass_kg / 1000.0


def compute_bom(
    *,
    panel_count: int,
    columns: list[Column],
    column_height_m: float,
) -> BomResult:
    """Compute live BOM from layout panels and resolved column grid."""
    active = active_columns(columns)
    active_count = len(active)
    per_post = ptr_length_m(column_height_m)
    ptr_total = active_count * per_post
    chord_total = truss_chord_length_m(columns)
    tonnage = steel_tonnage(ptr_total, chord_total)

    lines = (
        BomLine("Panels", float(panel_count), "ea"),
        BomLine("Columns (total)", float(len(columns)), "ea"),
        BomLine("Columns (active)", float(active_count), "ea"),
        BomLine("PTR 4×4 length", ptr_total, "m", note=f"{per_post:.2f} m per active post"),
        BomLine("Truss chord length", chord_total, "m", note="Top + bottom chord per bay"),
        BomLine("Base plates", float(active_count), "ea", note="One per active column"),
        BomLine("Est. steel tonnage", tonnage, "t", note="PTR + chord (placeholder weights)"),
    )

    return BomResult(
        panel_count=panel_count,
        column_count=len(columns),
        active_column_count=active_count,
        ptr_total_length_m=ptr_total,
        truss_chord_length_m=chord_total,
        base_plate_count=active_count,
        steel_tonnage=tonnage,
        lines=lines,
    )
