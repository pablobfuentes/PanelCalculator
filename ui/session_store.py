"""Session defaults and reset for Panel Calculator.

Streamlit deletes widget-bound session keys when a widget is not rendered on a run.
All user inputs are stored under ``persist_*`` keys; sidebar widgets are hydrated
from and saved back to those keys only while visible.
"""

from __future__ import annotations

import streamlit as st

from core.bom import DEFAULT_COLUMN_HEIGHT_M
from core.columns import MIN_COLUMN_COUNT
from core.models import DEFAULT_WIND_EXPOSURE, DEFAULT_WIND_SPEED_KMH
from core.sections import default_material_sections

VIEW_SETUP = "Setup"

_section_defaults = default_material_sections()

PERSIST_DEFAULTS: dict[str, object] = {
    "persist_length": 2.0,
    "persist_width": 1.0,
    "persist_weight": 25.0,
    "persist_tilt": 10.0,
    "persist_mid_clamp": 1.0,
    "persist_alley_w": 1.0,
    "persist_alley_reach": 2,
    "persist_max_x": 12.0,
    "persist_max_y": 8.0,
    "persist_use_fit": True,
    "persist_num_pairs": 3,
    "persist_num_rows": 2,
    "persist_panels_value": 12,
    "persist_panels_locked": False,
    "persist_locked_panel_count": 12,
    "persist_column_height": DEFAULT_COLUMN_HEIGHT_M,
    "persist_column_count_x": MIN_COLUMN_COUNT,
    "persist_column_count_y": MIN_COLUMN_COUNT,
    "persist_wind_speed": DEFAULT_WIND_SPEED_KMH,
    "persist_wind_exposure": DEFAULT_WIND_EXPOSURE,
    "persist_column_overrides": "",
    "persist_obstacle_zones": "",
    "persist_sec_ptr_a": _section_defaults.ptr_post.A,
    "persist_sec_ptr_ix": _section_defaults.ptr_post.Ix,
    "persist_sec_ptr_fy": _section_defaults.ptr_post.Fy,
    "persist_sec_beam_a": _section_defaults.secondary_beam.A,
    "persist_sec_beam_ix": _section_defaults.secondary_beam.Ix,
    "persist_sec_beam_fy": _section_defaults.secondary_beam.Fy,
    "persist_sec_chord_a": _section_defaults.truss_chord.A,
    "persist_sec_chord_ix": _section_defaults.truss_chord.Ix,
    "persist_sec_chord_fy": _section_defaults.truss_chord.Fy,
}

# Ephemeral widget keys -> durable persist keys
WIDGET_TO_PERSIST: dict[str, str] = {
    "sb_length": "persist_length",
    "sb_width": "persist_width",
    "sb_weight": "persist_weight",
    "sb_tilt": "persist_tilt",
    "sb_mid_clamp": "persist_mid_clamp",
    "sb_alley_w": "persist_alley_w",
    "sb_alley_reach": "persist_alley_reach",
    "sb_max_x": "persist_max_x",
    "sb_max_y": "persist_max_y",
    "sb_use_fit": "persist_use_fit",
    "sb_num_pairs": "persist_num_pairs",
    "sb_num_rows": "persist_num_rows",
    "sb_panels_value": "persist_panels_value",
    "sb_column_height": "persist_column_height",
    "sb_column_count_x": "persist_column_count_x",
    "sb_column_count_y": "persist_column_count_y",
    "sb_wind_speed": "persist_wind_speed",
    "sb_wind_exposure": "persist_wind_exposure",
    "column_overrides_input": "persist_column_overrides",
    "obstacle_zones_input": "persist_obstacle_zones",
}

SETUP_WIDGET_KEYS: tuple[str, ...] = (
    "sb_length",
    "sb_width",
    "sb_weight",
    "sb_tilt",
    "sb_mid_clamp",
    "sb_alley_w",
    "sb_alley_reach",
    "sb_max_x",
    "sb_max_y",
    "sb_use_fit",
    "sb_num_pairs",
    "sb_num_rows",
    "sb_panels_value",
)

ANALYSIS_WIDGET_KEYS: tuple[str, ...] = (
    "sb_column_height",
    "sb_column_count_x",
    "sb_column_count_y",
    "sb_wind_speed",
    "sb_wind_exposure",
)

APP_DEFAULTS: dict[str, object] = {
    "setup_accepted": False,
    "main_view": VIEW_SETUP,
}


def _migrate_legacy_widget_keys() -> None:
    """One-time copy from old sb_* keys if persist keys were never written."""
    for widget_key, persist_key in WIDGET_TO_PERSIST.items():
        if persist_key not in st.session_state and widget_key in st.session_state:
            st.session_state[persist_key] = st.session_state[widget_key]
    for legacy, persist in (
        ("column_overrides_text", "persist_column_overrides"),
        ("obstacle_zones_text", "persist_obstacle_zones"),
    ):
        if persist not in st.session_state and legacy in st.session_state:
            st.session_state[persist] = st.session_state[legacy]


def init_session_defaults() -> None:
    """Ensure durable keys exist without overwriting user values."""
    _migrate_legacy_widget_keys()
    _migrate_legacy_lock_keys()
    for key, value in APP_DEFAULTS.items():
        st.session_state.setdefault(key, value)
    for key, value in PERSIST_DEFAULTS.items():
        st.session_state.setdefault(key, value)


def _migrate_legacy_lock_keys() -> None:
    if "persist_panels_locked" not in st.session_state:
        if "panels_locked" in st.session_state:
            st.session_state.persist_panels_locked = st.session_state.panels_locked
    if "persist_locked_panel_count" not in st.session_state:
        if "locked_panel_count" in st.session_state:
            st.session_state.persist_locked_panel_count = st.session_state.locked_panel_count


def hydrate_panel_lock_state() -> None:
    """Apply durable lock state (used on every view)."""
    init_session_defaults()
    st.session_state.panels_locked = bool(st.session_state.persist_panels_locked)
    st.session_state.locked_panel_count = int(st.session_state.persist_locked_panel_count)


def persist_panel_lock_state() -> None:
    """Save lock state to durable keys."""
    if "panels_locked" in st.session_state:
        st.session_state.persist_panels_locked = bool(st.session_state.panels_locked)
    if "locked_panel_count" in st.session_state:
        st.session_state.persist_locked_panel_count = int(st.session_state.locked_panel_count)


def hydrate_widgets(widget_keys: tuple[str, ...] | list[str]) -> None:
    """Seed widget keys from persist storage when widgets were unmounted (view switch).

    Only runs when the widget key is absent — never overwrite an in-flight edit on
    the same view, which would revert the user's change on every rerun.
    """
    for widget_key in widget_keys:
        if widget_key in st.session_state:
            continue
        persist_key = WIDGET_TO_PERSIST[widget_key]
        st.session_state[widget_key] = st.session_state[persist_key]


def persist_widgets(widget_keys: tuple[str, ...] | list[str]) -> None:
    """Copy widget values into persist keys after rendering."""
    for widget_key in widget_keys:
        if widget_key in st.session_state:
            persist_key = WIDGET_TO_PERSIST[widget_key]
            st.session_state[persist_key] = st.session_state[widget_key]


def get_persist(key: str) -> object:
    """Read a durable session value."""
    init_session_defaults()
    return st.session_state[key]


def reset_app_session() -> None:
    """Clear session state and restore defaults (full app reset)."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_defaults()
    st.session_state.main_view = VIEW_SETUP
