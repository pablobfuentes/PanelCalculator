"""Pydantic request/response models for the SolarForge API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RectOut(BaseModel):
    x: float
    y: float
    w: float
    h: float


class AlleyOut(RectOut):
    kind: Literal["spine", "parallel"]
    label: str | None = None


class PanelTypeOut(BaseModel):
    key: str
    name: str
    length: float
    width: float
    weight: float
    watt_peak: float
    color: str
    tilt_angle: float = 10.0


class LayoutRequest(BaseModel):
    panel_key: str = "A"
    panel: PanelTypeOut | None = None
    max_area_x: float = Field(12.0, gt=0)
    max_area_y: float = Field(8.0, gt=0)
    mid_clamp_in: float = Field(1.0, ge=0)
    alley_width: float = Field(1.0, gt=0)
    alley_reach: int = Field(2, ge=2, le=4)
    spine_edge: Literal["top", "bottom"] = "bottom"
    use_fit: bool = True
    panels_locked: bool = False
    target_panels: int = Field(12, ge=0)
    num_pairs_manual: int = Field(3, ge=0)
    num_rows_manual: int = Field(2, ge=0)


class LayoutStatsOut(BaseModel):
    panel_count: int
    num_pairs_per_row: int
    num_rows: int
    footprint_w: float
    footprint_h: float
    footprint_area: float
    fits: bool
    message: str | None = None


class PanelSpecOut(BaseModel):
    length: float
    width: float
    weight: float
    tilt_angle: float


class LayoutConfigOut(BaseModel):
    mid_clamp_gap: float
    alley_width: float
    alley_reach: int
    max_area_x: float
    max_area_y: float


class LayoutSnapshotOut(BaseModel):
    panel: PanelSpecOut
    config: LayoutConfigOut
    num_pairs_per_row: int
    num_rows: int
    panel_count: int
    panels_locked: bool
    locked_panel_count: int = 0
    use_fit: bool


class LayoutResponse(BaseModel):
    panels: list[RectOut]
    alleys: list[AlleyOut]
    max_area: RectOut
    bbox: RectOut
    axis: RectOut
    panel: PanelTypeOut
    stats: LayoutStatsOut
    snapshot: LayoutSnapshotOut


class StructureRequest(BaseModel):
    """Deprecated alias — use LayoutCheckRequest."""

    snapshot: LayoutSnapshotOut
    column_count_x: int = Field(2, ge=2)
    column_count_y: int = Field(2, ge=2)
    column_height_m: float = Field(2.5, gt=0)
    wind_speed_kmh: float = Field(120.0, gt=0)
    wind_exposure: str = "B"
    column_overrides: str = ""
    obstacle_zones: str = ""
    panels_locked: bool = False
    locked_panel_count: int = Field(0, ge=0)


class LayoutCheckRequest(BaseModel):
    snapshot: LayoutSnapshotOut
    column_count_x: int = Field(2, ge=2)
    column_count_y: int = Field(2, ge=2)
    column_height_m: float = Field(2.5, gt=0)
    column_overrides: str = ""
    obstacle_zones: str = ""
    panels_locked: bool = False
    locked_panel_count: int = Field(0, ge=0)


class LayoutCalcVariableOut(BaseModel):
    name: str
    symbol: str
    value: float
    unit: str


class LayoutCalcStepOut(BaseModel):
    label: str
    formula: str
    expression: str
    result: str


class LayoutCheckDetailOut(BaseModel):
    variables: list[LayoutCalcVariableOut]
    steps: list[LayoutCalcStepOut]
    verdict: str


class LayoutElementCheckOut(BaseModel):
    check_id: str
    label: str
    value: float
    limit: float
    unit: str
    passed: bool
    detail: LayoutCheckDetailOut | None = None


class LayoutElementOut(BaseModel):
    element_id: str
    element_type: str
    name: str
    x: float
    y: float
    x2: float | None = None
    y2: float | None = None
    span_m: float
    dead_load_kn: float
    live_load_kn: float
    factored_load_kn: float
    max_moment_knm: float
    max_deflection_m: float
    deflection_limit_m: float
    max_torsion_knm: float
    preliminary_status: str
    overall_pass: bool
    checks: list[LayoutElementCheckOut]


class LayoutCheckMetricsOut(BaseModel):
    spacing_x: float
    spacing_y: float
    field_width: float
    field_height: float
    panel_count: int
    column_count: int
    active_count: int
    beam_count: int
    beam_length_m: float
    panel_area_m2: float
    tributary_area_m2: float
    total_dead_kn: float
    total_live_kn: float
    partition_ok: bool
    elements_passing: int
    element_count: int
    parse_error: str | None = None


class LayoutSummaryOut(BaseModel):
    panel_count: int
    column_count: int
    active_column_count: int
    beam_count: int
    beam_length_m: float
    total_dead_kn: float
    total_live_kn: float


class LayoutCheckResponse(BaseModel):
    metrics: LayoutCheckMetricsOut
    summary: LayoutSummaryOut
    elements: list[LayoutElementOut]
    figure: dict[str, object]
    rules: dict[str, float]


class StructureMetricsOut(BaseModel):
    wind_speed_kmh: float
    wind_exposure: str
    spacing_x: float
    spacing_y: float
    field_width: float
    field_height: float
    column_count: int
    active_count: int
    panel_area_m2: float
    tributary_area_m2: float
    estimated_load_kn: float
    partition_ok: bool
    parse_error: str | None = None


class ColumnOut(BaseModel):
    column_id: str
    x: float
    y: float
    is_custom: bool
    excluded: bool
    tributary_area_m2: float
    estimated_load_kn: float


class BomLineOut(BaseModel):
    item: str
    quantity: float
    unit: str
    note: str = ""


class BomSummaryOut(BaseModel):
    panel_count: int
    column_count: int
    active_column_count: int
    ptr_total_length_m: float
    truss_chord_length_m: float
    base_plate_count: int
    steel_tonnage: float
    lines: list[BomLineOut]


class FeaSummaryOut(BaseModel):
    solved: bool
    error: str | None = None
    node_count: int = 0
    member_count: int = 0
    combination_count: int = 0
    rows: list[dict[str, object]] = Field(default_factory=list)


class CodeCheckSummaryOut(BaseModel):
    rows: list[dict[str, object]] = Field(default_factory=list)
    pass_count: int = 0
    warn_count: int = 0
    fail_count: int = 0


class StructureResponse(BaseModel):
    metrics: StructureMetricsOut
    columns: list[ColumnOut]
    bom: BomSummaryOut
    figure: dict[str, object]
    fea: FeaSummaryOut | None = None
    code_checks: CodeCheckSummaryOut | None = None
