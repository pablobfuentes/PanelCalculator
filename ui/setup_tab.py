"""Setup tab — game-style layout builder (SolarForge)."""

from __future__ import annotations

import streamlit as st

from ui.canvas import render_layout_canvas
from ui.layout_state import layout_footprint_hash, snapshot_from_layout
from ui.navigation import request_main_view
from ui.panel_catalog import sync_selected_to_legacy_persist
from ui.setup_controls import (
    render_dimension_bubbles,
    render_setup_hud,
    render_setup_left_panel,
)
from ui.sidebar_inputs import SidebarInputs, VIEW_ANALYSIS, resolve_layout_from_inputs
from ui.theme import is_dark_theme


def render_setup_tab(inputs: SidebarInputs) -> None:
    st.markdown('<span class="sf-layout-view"></span>', unsafe_allow_html=True)
    st.markdown('<div class="sf-setup-stage">', unsafe_allow_html=True)
    sync_selected_to_legacy_persist()
    layout = resolve_layout_from_inputs(inputs)

    left_col, canvas_col = st.columns([1, 5], gap="small")

    with left_col:
        st.markdown('<span class="sf-left-rail-root"></span>', unsafe_allow_html=True)
        render_setup_left_panel(inputs, layout)

    with canvas_col:
        st.markdown('<span class="sf-canvas-col-root"></span>', unsafe_allow_html=True)
        if layout.panel_count == 0:
            _render_empty_layout_warning(layout, inputs.target_panels)
            st.session_state.setup_accepted = False
        else:
            render_layout_canvas(
                layout,
                show_tributary=False,
                title="",
                dark_theme=is_dark_theme(),
                game_canvas=True,
                figure_height=520,
            )
            render_dimension_bubbles(layout=layout, figure_height=520)

    can_proceed = layout.panel_count > 0
    if render_setup_hud(can_proceed=can_proceed):
        current_hash = layout_footprint_hash(layout)
        st.session_state.setup_accepted = True
        st.session_state.setup_snapshot = snapshot_from_layout(layout)
        st.session_state.accepted_layout_hash = current_hash
        st.session_state.pop("_column_counts_seeded", None)
        st.session_state.project_wind = {
            "wind_speed_kmh": inputs.wind.wind_speed_kmh,
            "exposure_category": inputs.wind.exposure_category,
        }
        st.session_state.show_accepted_message = True
        st.session_state.sf_toast = "Moving to Structure →"
        request_main_view(VIEW_ANALYSIS)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_empty_layout_warning(layout, target_panels: int) -> None:
    if layout.panels_locked:
        if target_panels % 2 != 0:
            st.warning("Panel count must be even for a pair grid.")
        else:
            st.warning("Panels do not fit — widen ↔ or ↕ working area.")
    else:
        st.warning("No panels fit — widen ↔ or ↕ working area.")
