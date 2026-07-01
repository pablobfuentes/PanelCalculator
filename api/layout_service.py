"""Layout computation for the web API."""

from __future__ import annotations

from api.catalog import PanelTypeDefinition, catalog_by_key
from api.schemas import AlleyOut, LayoutRequest, LayoutResponse, LayoutSnapshotOut, LayoutStatsOut, PanelSpecOut, LayoutConfigOut, PanelTypeOut, RectOut
from core.visualization import figure_axis_max_for_max_area, _non_negative_axis_limits
from ui.layout_state import layout_config_from_inputs, resolve_layout, snapshot_from_layout


def _rect(x: float, y: float, w: float, h: float) -> RectOut:
    return RectOut(x=x, y=y, w=w, h=h)


def _panel_out(panel: PanelTypeDefinition) -> PanelTypeOut:
    return PanelTypeOut(
        key=panel.key,
        name=panel.name,
        length=panel.length,
        width=panel.width,
        weight=panel.weight,
        watt_peak=panel.watt_peak,
        color=panel.color,
        tilt_angle=panel.tilt_angle,
    )


def compute_layout(req: LayoutRequest) -> LayoutResponse:
    if req.panel is not None:
        panel_def = PanelTypeDefinition(
            key=req.panel.key,
            name=req.panel.name,
            length=req.panel.length,
            width=req.panel.width,
            weight=req.panel.weight,
            watt_peak=req.panel.watt_peak,
            color=req.panel.color,
            tilt_angle=req.panel.tilt_angle,
        )
    else:
        catalog = catalog_by_key()
        if req.panel_key not in catalog:
            raise ValueError(f"Unknown panel key: {req.panel_key}")
        panel_def = catalog[req.panel_key]
    panel = panel_def.to_panel_spec()
    config = layout_config_from_inputs(
        mid_clamp_in=req.mid_clamp_in,
        alley_width=req.alley_width,
        alley_reach=req.alley_reach,
        max_area_x=req.max_area_x,
        max_area_y=req.max_area_y,
    )

    layout = resolve_layout(
        panel=panel,
        config=config,
        use_fit=req.use_fit,
        panels_locked=req.panels_locked,
        target_panels=req.target_panels,
        num_pairs_manual=req.num_pairs_manual,
        num_rows_manual=req.num_rows_manual,
    )

    bx, by, bw, bh = layout.bbox
    axis_x, axis_y = figure_axis_max_for_max_area(
        config.max_area_x, config.max_area_y, layout.bbox
    )
    x_upper, y_upper = _non_negative_axis_limits(axis_x, axis_y, fig_width=900, fig_height=520)

    panels = [_rect(x, y, w, h) for x, y, w, h in layout.panels]

    parallel_index = 0
    alleys: list[AlleyOut] = []
    for x, y, w, h in layout.alleys:
        is_spine = y == 0.0 and h <= config.alley_width + 1e-9
        if is_spine:
            alleys.append(
                AlleyOut(x=x, y=y, w=w, h=h, kind="spine", label="SPINE ALLEY — EDGE ACCESS")
            )
        else:
            parallel_index += 1
            alleys.append(
                AlleyOut(x=x, y=y, w=w, h=h, kind="parallel", label=f"A{parallel_index}")
            )

    fits = layout.panel_count > 0
    message = None
    if not fits:
        message = "No panels fit — widen ↔ or ↕ working area."

    snap = snapshot_from_layout(layout)
    snapshot = LayoutSnapshotOut(
        panel=PanelSpecOut(**snap["panel"]),
        config=LayoutConfigOut(**snap["config"]),
        num_pairs_per_row=snap["num_pairs_per_row"],
        num_rows=snap["num_rows"],
        panel_count=snap["panel_count"],
        panels_locked=snap["panels_locked"],
        locked_panel_count=snap["locked_panel_count"],
        use_fit=snap["use_fit"],
    )

    return LayoutResponse(
        panels=panels,
        alleys=alleys,
        max_area=_rect(0.0, 0.0, config.max_area_x, config.max_area_y),
        bbox=_rect(bx, by, bw, bh),
        axis=_rect(0.0, 0.0, x_upper, y_upper),
        panel=_panel_out(panel_def),
        stats=LayoutStatsOut(
            panel_count=layout.panel_count,
            num_pairs_per_row=layout.num_pairs_per_row,
            num_rows=layout.num_rows,
            footprint_w=bw,
            footprint_h=bh,
            footprint_area=bw * bh,
            fits=fits,
            message=message,
        ),
        snapshot=snapshot,
    )
