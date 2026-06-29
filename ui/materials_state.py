"""Load and save material section properties from session state."""

from __future__ import annotations

import streamlit as st

from core.sections import MaterialSections
from ui.material_library_state import (
    init_material_library,
    material_sections_from_library,
    sync_sidebar_edits_to_library,
)
from ui.session_store import init_session_defaults

MATERIAL_WIDGET_PERSIST: dict[str, str] = {
    "mat_ptr_a": "persist_sec_ptr_a",
    "mat_ptr_ix": "persist_sec_ptr_ix",
    "mat_ptr_fy": "persist_sec_ptr_fy",
    "mat_beam_a": "persist_sec_beam_a",
    "mat_beam_ix": "persist_sec_beam_ix",
    "mat_beam_fy": "persist_sec_beam_fy",
    "mat_chord_a": "persist_sec_chord_a",
    "mat_chord_ix": "persist_sec_chord_ix",
    "mat_chord_fy": "persist_sec_chord_fy",
}


def material_sections_from_session() -> MaterialSections:
    """Build section catalog from library role assignments."""
    init_session_defaults()
    init_material_library()
    return material_sections_from_library()


def persist_material_widgets() -> None:
    """Copy material widget values to persist keys and sync library."""
    for widget_key, persist_key in MATERIAL_WIDGET_PERSIST.items():
        if widget_key in st.session_state:
            st.session_state[persist_key] = st.session_state[widget_key]
    sync_sidebar_edits_to_library()


def hydrate_material_widgets() -> None:
    """Seed material widgets from persist keys when remounting Materials view."""
    init_material_library()
    materials = material_sections_from_library()
    defaults = {
        "mat_ptr_a": materials.ptr_post.A,
        "mat_ptr_ix": materials.ptr_post.Ix,
        "mat_ptr_fy": materials.ptr_post.Fy,
        "mat_beam_a": materials.secondary_beam.A,
        "mat_beam_ix": materials.secondary_beam.Ix,
        "mat_beam_fy": materials.secondary_beam.Fy,
        "mat_chord_a": materials.truss_chord.A,
        "mat_chord_ix": materials.truss_chord.Ix,
        "mat_chord_fy": materials.truss_chord.Fy,
    }
    for widget_key, value in defaults.items():
        if widget_key not in st.session_state:
            persist_key = MATERIAL_WIDGET_PERSIST[widget_key]
            if persist_key in st.session_state:
                st.session_state[widget_key] = st.session_state[persist_key]
            else:
                st.session_state[widget_key] = value
