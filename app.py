"""Panel Calculator — Streamlit entry point."""

import importlib
import os

import streamlit as st

# Streamlit keeps imported modules in memory across reruns. Reload on each run so
# layout changes apply without a manual server restart (skip during pytest).
if os.environ.get("PANEL_CALCULATOR_SKIP_RELOAD") != "1":
    import core.models as _models
    import core.layout as _layout
    import core.tributary as _tributary
    import core.visualization as _visualization

    importlib.reload(_models)
    importlib.reload(_layout)
    importlib.reload(_tributary)
    importlib.reload(_visualization)

from ui.phase3_tab import render_phase3_tab
from ui.setup_tab import render_setup_tab

if "setup_accepted" not in st.session_state:
    st.session_state.setup_accepted = False

st.set_page_config(page_title="Panel Calculator", layout="wide")
st.title("Panel Calculator")
st.caption("Setup → Phase 3 tributary model. Visual overlays and wind loads come in later phases.")

setup_tab, phase3_tab = st.tabs(["Setup", "Phase 3 — Tributary"])

with setup_tab:
    render_setup_tab()

with phase3_tab:
    render_phase3_tab()
