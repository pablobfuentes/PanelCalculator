"""Game-like navigation shell — stepper and content wrappers."""

from __future__ import annotations

import streamlit as st

from ui.sidebar_inputs import VIEW_ANALYSIS, VIEW_MATERIALS, VIEW_SETUP

STEP_SETUP = "Setup"
STEP_LAYOUT = "Layout"
STEP_STRUCTURE = "Structure"
STEP_MATERIALS = "Materials"
STEP_RESULTS = "Results"

STEPS: tuple[str, ...] = (
    STEP_SETUP,
    STEP_LAYOUT,
    STEP_STRUCTURE,
    STEP_MATERIALS,
    STEP_RESULTS,
)

VIEW_TO_STEP = {
    VIEW_SETUP: STEP_SETUP,
    VIEW_ANALYSIS: STEP_STRUCTURE,
    VIEW_MATERIALS: STEP_MATERIALS,
}


def _active_step(active_view: str) -> str:
    return VIEW_TO_STEP.get(active_view, STEP_SETUP)


def _step_index(label: str) -> int:
    return STEPS.index(label)


def _step_state(label: str, active_view: str, layout_accepted: bool) -> str:
    if label == STEP_RESULTS:
        return "locked"

    active_step = _active_step(active_view)
    active_idx = _step_index(active_step)
    idx = _step_index(label)

    if idx < active_idx:
        return "done"
    if idx == active_idx:
        return "active"
    if not layout_accepted and idx > _step_index(STEP_SETUP):
        return "locked"
    return "locked"


def _step_icon(label: str, state: str) -> str:
    if state == "done":
        return "✓"
    return str(_step_index(label) + 1)


def render_app_header() -> None:
    st.markdown(
        """
        <div class="sf-header">
          <p class="sf-title">Solar<span>Forge</span></p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stepper(active_view: str) -> None:
    """Visual-only 5-step progress bar."""
    layout_accepted = bool(st.session_state.get("setup_accepted"))
    active_step = _active_step(active_view)
    parts = ['<div class="sf-stepper-wrap"><nav class="sf-stepper" aria-label="Progress">']
    for index, label in enumerate(STEPS):
        state = _step_state(label, active_view, layout_accepted)
        icon = _step_icon(label, state)
        parts.append(
            f'<div class="sf-step {state}">'
            f'<div class="sf-step-icon">{icon}</div>{label}</div>'
        )
        if index < len(STEPS) - 1:
            connector_done = _step_index(label) < _step_index(active_step)
            cls = " sf-step-connector-done" if connector_done else ""
            parts.append(f'<div class="sf-step-connector{cls}"></div>')
    parts.append("</nav></div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_game_shell(title: str, caption: str = "") -> None:
    cap_html = f'<p class="sf-shell-caption">{caption}</p>' if caption else ""
    st.markdown(
        f'<div class="sf-shell"><p class="sf-shell-title">{title}</p>{cap_html}',
        unsafe_allow_html=True,
    )


def close_game_shell() -> None:
    st.markdown("</div>", unsafe_allow_html=True)
