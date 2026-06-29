"""Panel Calculator — Streamlit entry point."""

import importlib
import os

import streamlit as st

# Streamlit keeps imported modules in memory across reruns. Reload in dependency
# order so downstream modules always see the latest symbols (skip during pytest).
if os.environ.get("PANEL_CALCULATOR_SKIP_RELOAD") != "1":
    import core.wind as _wind

    importlib.reload(_wind)

    import core.sections as _sections
    import core.loads as _loads
    import core.models as _models
    import core.layout as _layout
    import core.columns as _columns

    importlib.reload(_sections)
    importlib.reload(_loads)
    importlib.reload(_models)
    importlib.reload(_layout)
    importlib.reload(_columns)

    import core.bom as _bom
    import core.code_checks as _code_checks
    import core.fea as _fea
    import core.material_library as _material_library
    import core.material_library_csv as _material_library_csv
    import core.reference_fea as _reference_fea
    import core.tributary as _tributary
    import core.visualization as _visualization

    importlib.reload(_bom)
    importlib.reload(_code_checks)
    importlib.reload(_fea)
    importlib.reload(_material_library)
    importlib.reload(_material_library_csv)
    importlib.reload(_reference_fea)
    importlib.reload(_tributary)
    importlib.reload(_visualization)
    importlib.reload(_wind)

    import ui.layout_state as _layout_state
    import ui.bom_panel as _bom_panel
    import ui.bom_settings_dialog as _bom_settings_dialog
    import ui.code_check_panel as _code_check_panel
    import ui.canvas as _canvas
    import ui.material_catalogue_io as _material_catalogue_io
    import ui.material_library_state as _material_library_state
    import ui.materials_state as _materials_state
    import ui.materials_tab as _materials_tab
    import ui.navigation as _navigation
    import ui.session_store as _session_store
    import ui.sidebar_inputs as _sidebar_inputs
    import ui.setup_tab as _setup_tab
    import ui.analysis_tab as _analysis_tab

    importlib.reload(_layout_state)
    importlib.reload(_bom_panel)
    importlib.reload(_bom_settings_dialog)
    importlib.reload(_code_check_panel)
    importlib.reload(_canvas)
    importlib.reload(_material_catalogue_io)
    importlib.reload(_material_library_state)
    importlib.reload(_materials_state)
    importlib.reload(_materials_tab)
    importlib.reload(_navigation)
    importlib.reload(_session_store)
    importlib.reload(_sidebar_inputs)
    importlib.reload(_setup_tab)
    importlib.reload(_analysis_tab)

from ui.materials_tab import render_materials_tab
from ui.navigation import apply_pending_main_view
from ui.analysis_tab import render_analysis_tab
from ui.setup_tab import render_setup_tab
from ui.session_store import init_session_defaults
from ui.sidebar_inputs import VIEW_ANALYSIS, VIEW_MATERIALS, VIEW_SETUP, render_sidebar

if "setup_accepted" not in st.session_state:
    st.session_state.setup_accepted = False
init_session_defaults()
if "main_view" not in st.session_state:
    st.session_state.main_view = VIEW_SETUP

st.set_page_config(page_title="Panel Calculator", layout="wide")
st.title("Panel Calculator")
st.caption(
    "Setup panel layout, then analyze tributary zones with wind inputs (CFE NTC-Viento 2020)."
)

apply_pending_main_view()

active_view = st.radio(
    "View",
    [VIEW_SETUP, VIEW_ANALYSIS, VIEW_MATERIALS],
    horizontal=True,
    key="main_view",
    label_visibility="collapsed",
)

inputs = render_sidebar(active_view)

if active_view == VIEW_SETUP:
    render_setup_tab(inputs)
elif active_view == VIEW_ANALYSIS:
    render_analysis_tab(inputs)
else:
    render_materials_tab()
