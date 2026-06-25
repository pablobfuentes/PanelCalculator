"""Setup tab — panel layout configuration and acceptance."""

from __future__ import annotations

import streamlit as st

from core.layout import parallel_alley_gap_labels
from ui.canvas import render_layout_canvas
from ui.layout_state import bom_panel_count, layout_footprint_hash, snapshot_from_layout
from ui.navigation import request_main_view
from ui.sidebar_inputs import SidebarInputs, VIEW_ANALYSIS, resolve_layout_from_inputs


def render_setup_tab(inputs: SidebarInputs) -> None:
    st.subheader("Setup")
    st.caption(
        "Configure panel geometry, alleys, and grid size. "
        "Accept the layout when ready to continue to tributary and load analysis."
    )

    layout = resolve_layout_from_inputs(inputs)

    alley_gap_labels = parallel_alley_gap_labels(
        layout.num_pairs_per_row * 2, layout.config.alley_reach
    )
    parallel_alleys = [a for a in layout.alleys if a[3] > layout.config.alley_width + 1e-9]

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric(
        "Panels",
        bom_panel_count(
            layout,
            live_locked=inputs.panels_locked,
            live_locked_count=inputs.target_panels,
        ),
    )
    col2.metric("Pairs / row", layout.num_pairs_per_row)
    col3.metric("Rows", layout.num_rows)
    col4.metric("Alley reach", f"{layout.config.alley_reach} panels")
    col5.metric("Layout size", f"{layout.bbox[2]:.1f} × {layout.bbox[3]:.1f} m")
    col6.metric("Panel lock", "On" if inputs.panels_locked else "Off")

    if alley_gap_labels:
        st.caption(
            f"Edge spine (1): bottom row · "
            f"Parallel alleys ({len(parallel_alleys)}): columns {', '.join(alley_gap_labels)}"
        )
    else:
        st.caption("Edge spine only — no parallel alleys needed for this row width.")

    if layout.panel_count == 0:
        _render_empty_layout_warning(layout, inputs.target_panels)
        st.session_state.setup_accepted = False
        return

    render_layout_canvas(
        layout,
        show_tributary=False,
        title="Panel layout — setup preview",
    )

    with st.expander("Legend"):
        st.markdown(
            """
            - **Blue** — solar panels
            - **Dark red** — edge spine (one horizontal alley at the bottom)
            - **Light red** — parallel service alleys between panel columns
            - **Green dashed** — layout bounding box
            - **Gray dotted** — max allowed footprint
            """
        )

    current_hash = layout_footprint_hash(layout)
    if st.session_state.get("accepted_layout_hash") not in (None, current_hash):
        st.warning("Layout changed since last acceptance. Re-accept to refresh analysis tabs.")

    accept_col, _ = st.columns([1, 3])
    with accept_col:
        if st.button("Accept layout → continue", type="primary", width="stretch"):
            st.session_state.setup_accepted = True
            st.session_state.setup_snapshot = snapshot_from_layout(layout)
            st.session_state.accepted_layout_hash = current_hash
            st.session_state.pop("_column_counts_seeded", None)
            st.session_state.project_wind = {
                "wind_speed_kmh": inputs.wind.wind_speed_kmh,
                "exposure_category": inputs.wind.exposure_category,
            }
            st.session_state.show_accepted_message = True
            request_main_view(VIEW_ANALYSIS)


def _render_empty_layout_warning(layout, target_panels: int) -> None:
    if layout.panels_locked:
        if target_panels % 2 != 0:
            st.warning(
                f"{target_panels} panels cannot form a rectangular pair grid "
                "(count must be even). Unlock or choose an even total."
            )
        else:
            st.warning(
                f"{target_panels} panels do not fit in "
                f"{layout.config.max_area_x:.1f} × {layout.config.max_area_y:.1f} m. "
                "Increase max area, reduce panel size, or lower the locked count."
            )
    else:
        st.warning(
            "No panels fit in the max area with these settings. "
            "Increase max area or reduce panel size."
        )
