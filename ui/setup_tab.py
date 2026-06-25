"""Setup tab — panel layout configuration and acceptance."""

from __future__ import annotations

import streamlit as st

from core.layout import parallel_alley_gap_labels
from core.visualization import build_layout_figure
from ui.layout_state import (
    default_panel_count,
    layout_config_from_inputs,
    layout_footprint_hash,
    resolve_layout,
    snapshot_from_layout,
)


def render_setup_tab() -> None:
    st.subheader("Setup")
    st.caption(
        "Configure panel geometry, alleys, and grid size. "
        "Accept the layout when ready to compute tributary areas in Phase 3."
    )

    if "panels_locked" not in st.session_state:
        st.session_state.panels_locked = False
    if "locked_panel_count" not in st.session_state:
        st.session_state.locked_panel_count = 12

    with st.sidebar:
        st.header("Panel")
        length = st.number_input("Length (m)", min_value=0.1, value=2.0, step=0.1, key="setup_length")
        width = st.number_input("Width (m)", min_value=0.1, value=1.0, step=0.1, key="setup_width")
        weight = st.number_input("Weight (kg)", min_value=0.1, value=25.0, step=0.5, key="setup_weight")
        tilt = st.number_input("Tilt (°)", min_value=0.0, max_value=90.0, value=10.0, step=1.0, key="setup_tilt")

        st.header("Layout")
        mid_clamp_in = st.number_input(
            'Mid-clamp gap (in)', min_value=0.0, value=1.0, step=0.25, key="setup_mid_clamp"
        )
        alley_width = st.number_input("Alley width (m)", min_value=0.1, value=1.0, step=0.1, key="setup_alley_w")
        alley_reach = st.number_input(
            "Alley reach (panels)", min_value=2, max_value=4, value=2, step=1, key="setup_alley_reach"
        )
        max_area_x = st.number_input("Max area X (m)", min_value=1.0, value=12.0, step=0.5, key="setup_max_x")
        max_area_y = st.number_input("Max area Y (m)", min_value=1.0, value=8.0, step=0.5, key="setup_max_y")

        st.header("Grid mode")
        use_fit = st.checkbox("Auto-fit to max area", value=True, key="setup_use_fit")
        num_pairs_manual = 3
        num_rows_manual = 2
        if not use_fit:
            num_pairs_manual = st.number_input(
                "Pairs per row", min_value=0, value=3, step=1, key="setup_num_pairs"
            )
            num_rows_manual = st.number_input("Rows", min_value=0, value=2, step=1, key="setup_num_rows")

    from core.models import PanelSpec

    panel = PanelSpec(length=length, width=width, weight=weight, tilt_angle=tilt)
    config = layout_config_from_inputs(
        mid_clamp_in=mid_clamp_in,
        alley_width=alley_width,
        alley_reach=int(alley_reach),
        max_area_x=max_area_x,
        max_area_y=max_area_y,
    )
    default_panels = default_panel_count(panel, config, use_fit)

    with st.sidebar:
        st.header("Panel count")
        panels_col, lock_col = st.columns([4, 1])
        with panels_col:
            panels_value = st.number_input(
                "Panels",
                min_value=2,
                step=2,
                value=(
                    st.session_state.locked_panel_count
                    if st.session_state.panels_locked
                    else default_panels
                ),
                key="setup_panels_value",
                help="Total panels in a rectangular grid (even count). "
                "Lock to fit this count within the max area.",
            )
        with lock_col:
            st.write("")
            lock_label = "Unlock" if st.session_state.panels_locked else "Lock value"
            if st.button(lock_label, width="stretch", key="setup_lock_panels"):
                if st.session_state.panels_locked:
                    st.session_state.panels_locked = False
                else:
                    st.session_state.panels_locked = True
                    st.session_state.locked_panel_count = int(panels_value)

    target_panels = int(
        st.session_state.locked_panel_count if st.session_state.panels_locked else panels_value
    )
    layout = resolve_layout(
        panel=panel,
        config=config,
        use_fit=use_fit,
        panels_locked=st.session_state.panels_locked,
        target_panels=target_panels,
        num_pairs_manual=num_pairs_manual,
        num_rows_manual=num_rows_manual,
    )

    alley_gap_labels = parallel_alley_gap_labels(
        layout.num_pairs_per_row * 2, layout.config.alley_reach
    )
    parallel_alleys = [a for a in layout.alleys if a[3] > layout.config.alley_width + 1e-9]

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Panels", layout.panel_count)
    col2.metric("Pairs / row", layout.num_pairs_per_row)
    col3.metric("Rows", layout.num_rows)
    col4.metric("Alley reach", f"{layout.config.alley_reach} panels")
    col5.metric("Layout size", f"{layout.bbox[2]:.1f} × {layout.bbox[3]:.1f} m")
    col6.metric("Panel lock", "On" if layout.panels_locked else "Off")

    if alley_gap_labels:
        st.caption(
            f"Edge spine (1): bottom row · "
            f"Parallel alleys ({len(parallel_alleys)}): columns {', '.join(alley_gap_labels)}"
        )
    else:
        st.caption("Edge spine only — no parallel alleys needed for this row width.")

    if layout.panel_count == 0:
        _render_empty_layout_warning(layout, target_panels)
        st.session_state.setup_accepted = False
        return

    fig = build_layout_figure(
        layout.panel,
        layout.config,
        layout.num_pairs_per_row,
        layout.num_rows,
    )
    st.plotly_chart(fig, width="stretch")

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
        st.warning("Layout changed since last acceptance. Re-accept to refresh Phase 3.")

    accept_col, _ = st.columns([1, 3])
    with accept_col:
        if st.button("Accept layout → Phase 3", type="primary", width="stretch"):
            st.session_state.setup_accepted = True
            st.session_state.setup_snapshot = snapshot_from_layout(layout)
            st.session_state.accepted_layout_hash = current_hash
            st.success("Layout accepted. Open the **Phase 3 — Tributary** tab to continue.")


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
