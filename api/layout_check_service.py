"""Layout-stage check API — tributary, preliminary rules, no FEA."""

from __future__ import annotations

from api.schemas import (
    LayoutCheckMetricsOut,
    LayoutCheckRequest,
    LayoutCheckResponse,
    LayoutElementCheckOut,
    LayoutElementOut,
    LayoutSummaryOut,
)
from api.tributary import build_tributary_columns
from core.columns import active_columns, column_spacings, panel_field_bbox
from core.layout_checks import (
    LayoutRules,
    derive_layout_elements,
    element_to_api_dict,
    layout_summary_metrics,
)
from core.tributary import total_panel_area, tributary_partition_valid
from core.visualization import build_layout_figure
from ui.layout_state import layout_from_snapshot


def _snapshot_dict(req: LayoutCheckRequest) -> dict:
    snap = req.snapshot
    return {
        "panel": snap.panel.model_dump(),
        "config": snap.config.model_dump(),
        "num_pairs_per_row": snap.num_pairs_per_row,
        "num_rows": snap.num_rows,
        "panel_count": snap.panel_count,
        "panels_locked": snap.panels_locked,
        "locked_panel_count": snap.locked_panel_count,
        "use_fit": snap.use_fit,
    }


def _rules_dict(rules: LayoutRules) -> dict[str, float]:
    return {
        "deflection_limit_denominator": rules.deflection_limit_denominator,
        "max_recommended_beam_span_m": rules.max_recommended_beam_span_m,
        "live_load_kn_m2": rules.live_load_kn_m2,
        "assumed_column_capacity_kn": rules.assumed_column_capacity_kn,
        "assumed_beam_moment_capacity_knm": rules.assumed_beam_moment_capacity_knm,
    }


def compute_layout_check(req: LayoutCheckRequest) -> LayoutCheckResponse:
    layout = layout_from_snapshot(_snapshot_dict(req))
    rules = LayoutRules()
    field = panel_field_bbox(layout.panels)
    _, _, field_width, field_height = field
    spacing_x, spacing_y = column_spacings(field, req.column_count_x, req.column_count_y)

    parse_error: str | None = None
    zoned_columns: list = []
    obstacles: list = []
    try:
        zoned_columns, obstacles = build_tributary_columns(
            layout,
            column_count_x=req.column_count_x,
            column_count_y=req.column_count_y,
            column_overrides_text=req.column_overrides,
            obstacle_zones_text=req.obstacle_zones,
        )
    except ValueError as exc:
        parse_error = str(exc)

    active = active_columns(zoned_columns)
    panel_area = total_panel_area(layout.panels)
    assigned_area = sum(column.tributary_area_m2 for column in active)
    partition_ok = tributary_partition_valid(zoned_columns, layout.panels) if zoned_columns else False

    elements = derive_layout_elements(zoned_columns, rules=rules) if zoned_columns else ()
    summary_extra = layout_summary_metrics(elements)

    fig = build_layout_figure(
        layout.panel,
        layout.config,
        layout.num_pairs_per_row,
        layout.num_rows,
        tributary_columns=zoned_columns if zoned_columns else None,
        layout_elements=list(elements) if elements else None,
        obstacle_zones=obstacles if obstacles else None,
        title="",
        dark_theme=True,
        game_canvas=True,
        figure_height=720,
    )
    fig.update_layout(margin=dict(l=24, r=24, t=24, b=24), showlegend=False)

    element_out = [
        LayoutElementOut(
            element_id=item["element_id"],
            element_type=item["element_type"],
            name=item["name"],
            x=item["x"],
            y=item["y"],
            x2=item["x2"],
            y2=item["y2"],
            span_m=item["span_m"],
            dead_load_kn=item["dead_load_kn"],
            live_load_kn=item["live_load_kn"],
            factored_load_kn=item["factored_load_kn"],
            max_moment_knm=item["max_moment_knm"],
            max_deflection_m=item["max_deflection_m"],
            deflection_limit_m=item["deflection_limit_m"],
            max_torsion_knm=item["max_torsion_knm"],
            preliminary_status=item["preliminary_status"],
            overall_pass=item["overall_pass"],
            checks=[LayoutElementCheckOut(**check) for check in item["checks"]],
        )
        for item in (element_to_api_dict(element) for element in elements)
    ]

    return LayoutCheckResponse(
        metrics=LayoutCheckMetricsOut(
            spacing_x=spacing_x,
            spacing_y=spacing_y,
            field_width=field_width,
            field_height=field_height,
            panel_count=layout.panel_count,
            column_count=len(zoned_columns),
            active_count=len(active),
            beam_count=int(summary_extra["beam_count"]),
            beam_length_m=float(summary_extra["beam_length_m"]),
            panel_area_m2=panel_area,
            tributary_area_m2=assigned_area,
            total_dead_kn=float(summary_extra["total_dead_kn"]),
            total_live_kn=float(summary_extra["total_live_kn"]),
            partition_ok=partition_ok,
            elements_passing=int(summary_extra["elements_passing"]),
            element_count=int(summary_extra["element_count"]),
            parse_error=parse_error,
        ),
        summary=LayoutSummaryOut(
            panel_count=layout.panel_count,
            column_count=len(zoned_columns),
            active_column_count=len(active),
            beam_count=int(summary_extra["beam_count"]),
            beam_length_m=float(summary_extra["beam_length_m"]),
            total_dead_kn=float(summary_extra["total_dead_kn"]),
            total_live_kn=float(summary_extra["total_live_kn"]),
        ),
        elements=element_out,
        figure=fig.to_plotly_json(),
        rules=_rules_dict(rules),
    )
