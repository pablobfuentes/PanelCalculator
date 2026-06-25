"""Main view navigation helpers for Streamlit session state."""

from __future__ import annotations

import streamlit as st

PENDING_MAIN_VIEW_KEY = "_pending_main_view"


def apply_pending_main_view() -> None:
    """Apply a deferred view switch before the main_view radio is drawn."""
    pending = st.session_state.pop(PENDING_MAIN_VIEW_KEY, None)
    if pending is not None:
        st.session_state.main_view = pending


def request_main_view(view: str) -> None:
    """Switch main view on the next rerun (safe with keyed widgets)."""
    st.session_state[PENDING_MAIN_VIEW_KEY] = view
    st.rerun()
