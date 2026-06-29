"""3D frame FEA for column grid and tributary loads (Phase 5.3)."""

from __future__ import annotations

from dataclasses import dataclass

from Pynite import FEModel3D

from core.bom import ROW_Y_TOLERANCE_M
from core.columns import Column, active_columns
from core.loads import load_combinations
from core.models import PanelSpec, WindConfig
from core.sections import MaterialSections, SteelSection

STEEL_E_MPA = 200_000.0
STEEL_G_MPA = 77_000.0
STEEL_NU = 0.3
DEFAULT_LIVE_LOAD_KN_M2 = 0.25

# Exposure multipliers (simplified NTC-Viento 2020 design wind pressure).
_WIND_EXPOSURE_FACTOR: dict[str, float] = {
    "A": 0.85,
    "B": 1.0,
    "C": 1.15,
    "D": 1.30,
}


@dataclass(frozen=True)
class MemberForces:
    """Peak member forces for one load combination."""

    element_id: str
    element_type: str
    combo_id: str
    max_moment_knm: float
    max_axial_kn: float
    max_deflection_m: float
    member_length_m: float


@dataclass(frozen=True)
class FEAAnalysisResult:
    """Solver output for the racking frame."""

    results: tuple[MemberForces, ...]
    node_count: int
    member_count: int
    error: str | None = None

    @property
    def solved(self) -> bool:
        return self.error is None and bool(self.results)


def design_wind_pressure_kn_m2(wind_speed_kmh: float, exposure_category: str) -> float:
    """Simplified design wind pressure (kN/m²) from basic speed and exposure."""
    if wind_speed_kmh <= 0:
        raise ValueError("wind_speed_kmh must be positive")
    factor = _WIND_EXPOSURE_FACTOR.get(exposure_category, 1.0)
    v_ms = wind_speed_kmh / 3.6
    q_kn_m2 = 0.5 * 1.25 * v_ms**2 / 1000.0
    return q_kn_m2 * factor


def estimate_live_load_kn(tributary_area_m2: float) -> float:
    return tributary_area_m2 * DEFAULT_LIVE_LOAD_KN_M2


def estimate_wind_load_kn(column: Column, wind: WindConfig) -> float:
    pressure = design_wind_pressure_kn_m2(
        wind.wind_speed_kmh, wind.exposure_category
    )
    return column.tributary_area_m2 * pressure


def _group_rows(columns: list[Column]) -> list[list[Column]]:
    rows: list[list[Column]] = []
    for column in sorted(columns, key=lambda item: (item.y, item.x)):
        y_key = round(column.y / ROW_Y_TOLERANCE_M)
        if not rows or round(rows[-1][0].y / ROW_Y_TOLERANCE_M) != y_key:
            rows.append([column])
        else:
            rows[-1].append(column)
    return [sorted(row, key=lambda item: item.x) for row in rows]


def _pynite_section_name(section: SteelSection, role: str) -> str:
    return f"SEC_{role}"


def _register_section(model: FEModel3D, section: SteelSection, role: str) -> str:
    name = _pynite_section_name(section, role)
    if name not in model.sections:
        j = section.Ix / 2.0
        model.add_section(name, section.A, section.Ix, section.Ix, j)
    return name


def _node_deflection_m(model: FEModel3D, node_id: str, combo_id: str) -> float:
    node = model.nodes[node_id]
    return max(
        abs(node.DX.get(combo_id, 0.0)),
        abs(node.DY.get(combo_id, 0.0)),
        abs(node.DZ.get(combo_id, 0.0)),
    )


def _member_peak_moment_knm(member, combo_id: str) -> float:
    peak = 0.0
    for axis in ("Mx", "My", "Mz"):
        peak = max(
            peak,
            abs(member.max_moment(axis, combo_id)),
            abs(member.min_moment(axis, combo_id)),
        )
    return peak


def _member_peak_axial_kn(member, combo_id: str) -> float:
    return max(
        abs(member.max_axial(combo_id)),
        abs(member.min_axial(combo_id)),
    )


def _member_length_m(model: FEModel3D, member) -> float:
    i_name = member.i_node.name if hasattr(member.i_node, "name") else str(member.i_node)
    j_name = member.j_node.name if hasattr(member.j_node, "name") else str(member.j_node)
    ni = model.nodes[i_name]
    nj = model.nodes[j_name]
    dx = nj.X - ni.X
    dy = nj.Y - ni.Y
    dz = nj.Z - ni.Z
    return float((dx**2 + dy**2 + dz**2) ** 0.5)


def _member_peak_deflection_m(model: FEModel3D, member, combo_id: str) -> float:
    i_name = member.i_node.name if hasattr(member.i_node, "name") else str(member.i_node)
    j_name = member.j_node.name if hasattr(member.j_node, "name") else str(member.j_node)
    return max(
        _node_deflection_m(model, i_name, combo_id),
        _node_deflection_m(model, j_name, combo_id),
    )


def build_frame_model(
    columns: list[Column],
    *,
    column_height_m: float,
    materials: MaterialSections,
    panel: PanelSpec,
    wind: WindConfig,
) -> tuple[FEModel3D, dict[str, str]]:
    """Build PyNite model: pinned post bases, chord members along X at top."""
    active = active_columns(columns)
    if not active:
        raise ValueError("No active columns for FEA")
    if column_height_m <= 0:
        raise ValueError("column_height_m must be positive")

    model = FEModel3D()
    model.add_material("Steel", STEEL_E_MPA, STEEL_G_MPA, STEEL_NU, 0.0)
    ptr_sec = _register_section(model, materials.ptr_post, "ptr")
    chord_sec = _register_section(model, materials.truss_chord, "chord")

    member_types: dict[str, str] = {}
    node_top: dict[str, str] = {}

    for column in active:
        base_id = f"B_{column.column_id}"
        top_id = f"T_{column.column_id}"
        node_top[column.column_id] = top_id
        # Plan: layout x → X, layout y → Z, vertical → Y.
        model.add_node(base_id, column.x, 0.0, column.y)
        model.add_node(top_id, column.x, column_height_m, column.y)
        model.def_support(base_id, True, True, True, True, True, True)

        post_id = f"P_{column.column_id}"
        model.add_member(post_id, base_id, top_id, "Steel", ptr_sec)
        member_types[post_id] = "post"

        dead_kn = column.estimated_load_kn
        live_kn = estimate_live_load_kn(column.tributary_area_m2)
        wind_kn = estimate_wind_load_kn(column, wind)
        if dead_kn > 0:
            model.add_node_load(top_id, "FY", -dead_kn, "D")
        if live_kn > 0:
            model.add_node_load(top_id, "FY", -live_kn, "L")
        if wind_kn > 0:
            model.add_node_load(top_id, "FX", wind_kn, "W")

    chord_index = 1
    for row in _group_rows(active):
        for left, right in zip(row, row[1:]):
            left_top = node_top[left.column_id]
            right_top = node_top[right.column_id]
            chord_id = f"C{chord_index}"
            chord_index += 1
            model.add_member(chord_id, left_top, right_top, "Steel", chord_sec)
            member_types[chord_id] = "chord"

    for combo in load_combinations():
        model.add_load_combo(
            combo.combo_id,
            {"D": combo.factor_D, "L": combo.factor_L, "W": combo.factor_W},
        )

    return model, member_types


def extract_member_results(
    model: FEModel3D,
    member_types: dict[str, str],
) -> tuple[MemberForces, ...]:
    """Read peak forces per member and load combination."""
    rows: list[MemberForces] = []
    for combo in load_combinations():
        for member_id, element_type in member_types.items():
            member = model.members[member_id]
            rows.append(
                MemberForces(
                    element_id=member_id,
                    element_type=element_type,
                    combo_id=combo.combo_id,
                    max_moment_knm=_member_peak_moment_knm(member, combo.combo_id),
                    max_axial_kn=_member_peak_axial_kn(member, combo.combo_id),
                    max_deflection_m=_member_peak_deflection_m(
                        model, member, combo.combo_id
                    ),
                    member_length_m=_member_length_m(model, member),
                )
            )
    return tuple(rows)


def run_frame_analysis(
    columns: list[Column],
    *,
    column_height_m: float,
    materials: MaterialSections,
    panel: PanelSpec,
    wind: WindConfig,
) -> FEAAnalysisResult:
    """Build frame, solve all load combinations, return peak member results."""
    try:
        model, member_types = build_frame_model(
            columns,
            column_height_m=column_height_m,
            materials=materials,
            panel=panel,
            wind=wind,
        )
        model.analyze(check_stability=True)
        results = extract_member_results(model, member_types)
        return FEAAnalysisResult(
            results=results,
            node_count=len(model.nodes),
            member_count=len(model.members),
        )
    except Exception as exc:
        return FEAAnalysisResult(
            results=(),
            node_count=0,
            member_count=0,
            error=str(exc),
        )


def fea_result_rows(result: FEAAnalysisResult) -> list[dict[str, object]]:
    """Flatten FEA output for Streamlit tables."""
    return [
        {
            "Element": row.element_id,
            "Type": row.element_type,
            "Combo": row.combo_id,
            "M max (kN·m)": round(row.max_moment_knm, 3),
            "P max (kN)": round(row.max_axial_kn, 3),
            "δ max (m)": round(row.max_deflection_m, 5),
        }
        for row in result.results
    ]
