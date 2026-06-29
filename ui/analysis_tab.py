"""Analysis tab — tributary areas and full design canvas (Phase 3 + 4)."""

from __future__ import annotations

import streamlit as st

from core.fea import fea_result_rows, run_frame_analysis
from core.code_checks import evaluate_code_checks
from core.bom import compute_bom
from core.columns import active_columns, column_spacings, panel_field_bbox
from core.tributary import (
    total_panel_area,
    tributary_partition_valid,
)
from ui.bom_panel import render_bom_panel
from ui.code_check_panel import render_code_check_table
from ui.canvas import build_tributary_columns, render_layout_canvas
from ui.layout_state import bom_panel_count, layout_from_snapshot
from ui.session_store import hydrate_widgets, persist_widgets
from ui.sidebar_inputs import SidebarInputs


def render_analysis_tab(inputs: SidebarInputs) -> None:
    st.subheader("Analysis")
    st.caption(
        "Column grid, tributary areas, and wind inputs. "
        "Switch to **Setup** in the main view to change the panel layout."
    )

    if not st.session_state.get("setup_accepted") or "setup_snapshot" not in st.session_state:
        st.info(
            "Complete **Setup**, configure a valid layout, then click "
            "**Accept layout → continue** before working here."
        )
        return

    if st.session_state.pop("show_accepted_message", False):
        st.success("Layout accepted. You are now in **Analysis**.")

    layout = layout_from_snapshot(st.session_state.setup_snapshot)
    if layout.panel_count == 0:
        st.warning("Accepted layout has no panels. Return to **Setup** and fix the configuration.")
        return

    field = panel_field_bbox(layout.panels)
    spacing_x, spacing_y = column_spacings(
        field, inputs.column_count_x, inputs.column_count_y
    )

    w1, w2, w3, w4 = st.columns(4)
    w1.metric("Wind speed", f"{inputs.wind.wind_speed_kmh:.0f} km/h")
    w2.metric("Exposure", inputs.wind.exposure_category)
    w3.metric("Spacing X", f"{spacing_x:.2f} m")
    w4.metric("Spacing Y", f"{spacing_y:.2f} m")

    st.markdown("#### Column placement")
    col_left, col_right = st.columns(2)
    hydrate_widgets(["column_overrides_input", "obstacle_zones_input"])
    with col_left:
        st.text_area(
            "Custom column coordinates",
            height=120,
            placeholder="x, y  (one per line)\n# or: id, x, y\n2.5, 1.5",
            help="Leave empty to use the auto 2D grid. Non-empty replaces the default grid.",
            key="column_overrides_input",
        )
    with col_right:
        st.text_area(
            "Obstacle zones",
            height=120,
            placeholder="x, y, width, height  (one per line)\n3.0, 2.0, 1.0, 1.0",
            help="Columns inside an obstacle are flagged red and excluded from tributary/FEA.",
            key="obstacle_zones_input",
        )
    persist_widgets(["column_overrides_input", "obstacle_zones_input"])
    column_overrides = str(st.session_state.persist_column_overrides)
    obstacle_zones = str(st.session_state.persist_obstacle_zones)

    parse_error = None
    try:
        zoned_columns, obstacles = build_tributary_columns(
            layout,
            column_count_x=inputs.column_count_x,
            column_count_y=inputs.column_count_y,
            column_overrides_text=column_overrides,
            obstacle_zones_text=obstacle_zones,
        )
    except ValueError as exc:
        parse_error = str(exc)
        zoned_columns, obstacles = [], []

    if parse_error:
        st.error(parse_error)
        return

    active = active_columns(zoned_columns)
    panel_area = total_panel_area(layout.panels)
    assigned_area = sum(column.tributary_area_m2 for column in active)
    partition_ok = tributary_partition_valid(zoned_columns, layout.panels)
    total_load_kn = sum(column.estimated_load_kn for column in active)

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Columns", len(zoned_columns))
    m2.metric("Active", len(active))
    m3.metric("Panel area", f"{panel_area:.2f} m²")
    m4.metric("Tributary sum", f"{assigned_area:.2f} m²")
    m5.metric("Est. dead load", f"{total_load_kn:.2f} kN")
    m6.metric("Partition", "PASS" if partition_ok else "FAIL")

    if partition_ok:
        st.success("Active tributary zones cover the full panel area.")
    else:
        st.error(
            f"Tributary areas do not match panel area "
            f"(Δ {abs(assigned_area - panel_area):.4f} m²). "
            "Check spacing, overrides, or obstacles."
        )

    st.markdown("#### Design canvas")
    canvas_col, bom_col = st.columns([3, 1], gap="medium")
    with canvas_col:
        render_layout_canvas(
            layout,
            column_count_x=inputs.column_count_x,
            column_count_y=inputs.column_count_y,
            column_overrides_text=column_overrides,
            obstacle_zones_text=obstacle_zones,
            show_tributary=True,
            title="Panel layout — grid, columns, tributary",
        )
        with st.expander("Legend"):
            st.markdown(
                """
                - **Blue** — solar panels
                - **Dark red** — edge spine · **Light red** — parallel alleys
                - **Green → amber → red** — tributary cells (hover for load)
                - **Dark triangles** — active columns · **Red triangles** — excluded (obstacle)
                - **Red dashed boxes** — obstacle zones
                """
            )

    with bom_col:
        bom = compute_bom(
            panel_count=bom_panel_count(
                layout,
                live_locked=inputs.panels_locked,
                live_locked_count=inputs.target_panels,
            ),
            columns=zoned_columns,
            column_height_m=inputs.column_height_m,
            materials=inputs.materials,
        )
        render_bom_panel(bom)

    st.markdown("#### Column tributary areas")
    st.dataframe(
        [
            {
                "Column": column.column_id,
                "X (m)": round(column.x, 3),
                "Y (m)": round(column.y, 3),
                "Custom": column.is_custom,
                "Excluded": column.excluded,
                "Area (m²)": round(column.tributary_area_m2, 3),
                "Est. load (kN)": round(column.estimated_load_kn, 3),
            }
            for column in zoned_columns
        ],
        width="stretch",
        hide_index=True,
    )

    st.markdown("#### FEA results")
    st.caption(
        "PyNite 3D frame: fixed post bases, tributary dead/live/wind at post tops, "
        "chord members between columns. Results per load combination (Phase 5.3)."
    )
    if not partition_ok:
        st.warning("Fix tributary partition before running FEA.")
    elif not active:
        st.info("No active columns — add columns or remove obstacles.")
    else:
        fea = run_frame_analysis(
            zoned_columns,
            column_height_m=inputs.column_height_m,
            materials=inputs.materials,
            panel=layout.panel,
            wind=inputs.wind,
        )
        if not fea.solved:
            st.error(fea.error or "FEA solver failed.")
        else:
            f1, f2, f3 = st.columns(3)
            f1.metric("Nodes", fea.node_count)
            f2.metric("Members", fea.member_count)
            f3.metric("Combinations", len({r.combo_id for r in fea.results}))
            st.dataframe(fea_result_rows(fea), width="stretch", hide_index=True)

            st.markdown("#### Code checks")
            checks = evaluate_code_checks(fea.results, materials=inputs.materials)
            render_code_check_table(checks)
