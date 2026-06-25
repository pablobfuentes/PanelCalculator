"""Phase 3 tab — tributary area computation (3.1)."""

from __future__ import annotations

import streamlit as st

from core.tributary import (
    DEFAULT_COLUMN_SPACING_M,
    compute_tributary_zones,
    default_columns,
    enrich_tributary_loads,
    panel_field_bbox,
    total_panel_area,
    tributary_partition_valid,
)
from core.visualization import build_layout_figure
from ui.layout_state import layout_from_snapshot


def render_phase3_tab() -> None:
    st.subheader("Phase 3 — Tributary areas")
    st.caption("Assign each structural column a rectangular catchment over the panel field.")

    if not st.session_state.get("setup_accepted") or "setup_snapshot" not in st.session_state:
        st.info(
            "Complete **Setup**, configure a valid layout, then click "
            "**Accept layout → Phase 3** before working here."
        )
        return

    layout = layout_from_snapshot(st.session_state.setup_snapshot)
    if layout.panel_count == 0:
        st.warning("Accepted layout has no panels. Return to **Setup** and fix the configuration.")
        return

    column_spacing = st.number_input(
        "Column spacing (m)",
        min_value=0.5,
        value=DEFAULT_COLUMN_SPACING_M,
        step=0.5,
        help="Default structural column spacing along the panel field width.",
        key="phase3_column_spacing",
    )

    panel_field = panel_field_bbox(layout.panels)
    columns = default_columns(panel_field, spacing=column_spacing)
    zoned_columns = enrich_tributary_loads(
        compute_tributary_zones(columns, layout.panels),
        layout.panel,
    )
    panel_area = total_panel_area(layout.panels)
    assigned_area = sum(column.tributary_area_m2 for column in zoned_columns)
    partition_ok = tributary_partition_valid(zoned_columns, layout.panels)
    total_load_kn = sum(column.estimated_load_kn for column in zoned_columns)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Columns", len(zoned_columns))
    m2.metric("Panel area", f"{panel_area:.2f} m²")
    m3.metric("Tributary sum", f"{assigned_area:.2f} m²")
    m4.metric("Est. dead load", f"{total_load_kn:.2f} kN")
    m5.metric("Partition check", "PASS" if partition_ok else "FAIL")

    if partition_ok:
        st.success("Tributary zones cover the full panel area with no gaps or overlaps.")
    else:
        st.error(
            f"Tributary areas do not match panel area "
            f"(Δ {abs(assigned_area - panel_area):.4f} m²). Review column spacing."
        )

    st.markdown("#### Tributary overlay")
    fig = build_layout_figure(
        layout.panel,
        layout.config,
        layout.num_pairs_per_row,
        layout.num_rows,
        tributary_columns=zoned_columns,
        title="Panel layout — tributary zones",
    )
    st.plotly_chart(fig, width="stretch")

    with st.expander("Legend"):
        st.markdown(
            """
            - **Green → amber → red** — tributary zones (darker = higher estimated load)
            - **Black triangles** — column positions along the edge spine
            - Hover a zone for column ID, tributary area (m²), and estimated load (kN)
            """
        )

    st.markdown("#### Column tributary areas")
    st.dataframe(
        [
            {
                "Column": column.column_id,
                "X (m)": round(column.x, 3),
                "Tributary X₀ (m)": round(column.tributary_rect[0], 3) if column.tributary_rect else None,
                "Width (m)": round(column.tributary_rect[2], 3) if column.tributary_rect else None,
                "Area (m²)": round(column.tributary_area_m2, 3),
                "Est. load (kN)": round(column.estimated_load_kn, 3),
            }
            for column in zoned_columns
        ],
        width="stretch",
        hide_index=True,
    )

    st.caption(
        "Return to **Setup** any time to change panel geometry, alleys, or grid size. "
        "Re-accept the layout to refresh these results."
    )
