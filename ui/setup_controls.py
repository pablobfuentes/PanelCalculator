"""Game-style setup controls — left panel, HUD, dimension bubbles."""

from __future__ import annotations

import streamlit as st

from ui.hud_tooltips import (
    alley_width_tooltip_svg,
    gap_tooltip_svg,
    reach_tooltip_svg,
    spine_tooltip_svg,
)
from ui.layout_state import ResolvedLayout
from ui.panel_catalog import (
    get_panel_catalog,
    get_selected_panel_key,
    set_selected_panel_key,
    sync_selected_to_legacy_persist,
)
from ui.panel_type_dialog import new_panel_type_dialog
from ui.session_store import SETUP_WIDGET_KEYS, get_persist, hydrate_widgets, persist_panel_lock_state, persist_widgets
from ui.sidebar_inputs import SidebarInputs


def _adjust_persist(
    persist_key: str,
    widget_key: str | None,
    delta: float,
    *,
    minimum: float,
    maximum: float,
    step: float,
) -> None:
    current = float(get_persist(persist_key))
    new_value = current + delta * step
    new_value = round(new_value / step) * step if step > 0 else new_value
    new_value = max(minimum, min(maximum, new_value))
    st.session_state[persist_key] = new_value
    if widget_key and widget_key in st.session_state:
        st.session_state[widget_key] = new_value


def _show_toast() -> None:
    message = st.session_state.pop("sf_toast", None)
    if message:
        st.toast(message, icon="✅")


def _hex_rgba(hex_color: str, alpha: float) -> str:
    value = hex_color.lstrip("#")
    if len(value) != 6:
        return f"rgba(91,184,245,{alpha})"
    red = int(value[0:2], 16)
    green = int(value[2:4], 16)
    blue = int(value[4:6], 16)
    return f"rgba({red},{green},{blue},{alpha})"


def _inject_panel_type_square_styles(catalog, selected_key: str) -> None:
    """Color-coded 32×32 panel type squares with glow on selection."""
    row = (
        'div[data-testid="stHorizontalBlock"]:has(.sf-panel-type-row-marker)'
        ':not(:has(.sf-left-rail-root)) > div[data-testid="stColumn"]'
    )
    rules: list[str] = []
    for index, panel in enumerate(catalog, start=1):
        active = panel.key == selected_key
        background = _hex_rgba(panel.color, 0.22 if active else 0.18)
        border = panel.color if active else _hex_rgba(panel.color, 0.55)
        glow = (
            f"box-shadow: 0 0 14px {_hex_rgba(panel.color, 0.45)} !important;"
            if active
            else ""
        )
        rules.append(
            f"{row}:nth-child({index}) button {{"
            f"background: {background} !important; "
            f"border: 1.5px solid {border} !important; "
            f"color: {panel.color} !important; {glow} }}"
        )
    add_index = len(catalog) + 1
    rules.append(
        f"{row}:nth-child({add_index}) button {{"
        "background: #1E2640 !important; "
        "border: 1.5px dashed rgba(255,255,255,0.13) !important; "
        "color: #7A8499 !important; font-size: 20px !important; "
        "font-weight: 300 !important; box-shadow: none !important; }}"
        f"{row}:nth-child({add_index}) button:hover {{"
        "border-color: #F5A623 !important; color: #F5A623 !important; }}"
    )
    st.markdown(f"<style>{''.join(rules)}</style>", unsafe_allow_html=True)


def render_setup_left_panel(inputs: SidebarInputs, layout: ResolvedLayout) -> None:
    """Panel type selector, selected card, count lock, footprint."""
    _show_toast()
    catalog = get_panel_catalog()
    selected_key = get_selected_panel_key()
    selected = next(p for p in catalog if p.key == selected_key)
    panel_count = layout.panel_count if layout.panel_count else inputs.target_panels
    footprint_w, footprint_h = layout.bbox[2], layout.bbox[3]
    footprint_area = footprint_w * footprint_h if layout.panel_count else 0.0
    locked = inputs.panels_locked

    _inject_panel_type_square_styles(catalog, selected_key)

    # Panel type row — color squares + add button
    st.markdown('<div class="sf-section-head">Panel type</div>', unsafe_allow_html=True)
    type_cols = st.columns(len(catalog) + 1, gap=None)
    for idx, (panel, col) in enumerate(zip(catalog, type_cols)):
        with col:
            if idx == 0:
                st.markdown('<span class="sf-panel-type-row-marker"></span>', unsafe_allow_html=True)
            if st.button(
                panel.key,
                key=f"sf_panel_type_{panel.key}",
                type="secondary",
                help=panel.name,
            ):
                if panel.key != selected_key:
                    set_selected_panel_key(panel.key)
                    sync_selected_to_legacy_persist()
                    st.rerun()
    with type_cols[-1]:
        if st.button("+", key="sf_panel_type_add", type="secondary", help="Add panel type"):
            new_panel_type_dialog()

    # Selected panel card (read-only stats)
    icon_bg = _hex_rgba(selected.color, 0.2)
    icon_border = _hex_rgba(selected.color, 0.45)
    st.markdown(
        f"""
        <div class="sf-panel-section">
          <div class="sf-section-label">Selected panel</div>
          <div class="sf-panel-card">
            <div class="sf-panel-card-icon" style="background:{icon_bg};border:1.5px solid {icon_border};color:{selected.color}">☀</div>
            <div class="sf-panel-name" style="color:{selected.color}">{selected.name}</div>
            <div class="sf-panel-stats">
              <div class="sf-stat-row"><span class="sf-stat-key">Length</span>
                <span class="sf-stat-val">{selected.length:.1f} m</span></div>
              <div class="sf-stat-row"><span class="sf-stat-key">Width</span>
                <span class="sf-stat-val">{selected.width:.1f} m</span></div>
              <div class="sf-stat-row"><span class="sf-stat-key">Weight</span>
                <span class="sf-stat-val">{selected.weight:.0f} kg</span></div>
              <div class="sf-stat-row"><span class="sf-stat-key">Watt-peak</span>
                <span class="sf-stat-val">{selected.watt_peak:.0f} Wp</span></div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Total panels + lock
    st.markdown('<div class="sf-section-head">Total panels</div>', unsafe_allow_html=True)
    count_c, lock_c = st.columns([6, 1], gap="small")
    with count_c:
        st.markdown(
            f"""
            <span class="sf-count-lock-marker"></span>
            <div>
              <div class="sf-count-num">{panel_count}</div>
              <div class="sf-count-label">panels fit</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with lock_c:
        lock_icon = "🔒" if locked else "🔓"
        lock_help = "Unlock panel count" if locked else "Lock panel count"
        if st.button(lock_icon, key="sf_lock_panels", help=lock_help):
            if locked:
                st.session_state.panels_locked = False
                st.session_state.sf_toast = "Panel count unlocked"
            else:
                st.session_state.panels_locked = True
                st.session_state.locked_panel_count = panel_count
                st.session_state.persist_panels_value = panel_count
                st.session_state.sf_toast = "Panel count locked"
            st.session_state.persist_panels_locked = st.session_state.panels_locked
            st.session_state.persist_locked_panel_count = int(
                st.session_state.get("locked_panel_count", panel_count)
            )
            persist_panel_lock_state()
            st.rerun()
    if locked:
        hydrate_widgets(["sb_panels_value"])
        st.session_state.sb_panels_value = int(st.session_state.get("locked_panel_count", panel_count))
        st.session_state.persist_panels_value = st.session_state.sb_panels_value
        st.session_state.persist_locked_panel_count = st.session_state.sb_panels_value
        persist_widgets(["sb_panels_value"])

    # Footprint
    st.markdown(
        f"""
        <div class="sf-panel-section">
          <div class="sf-section-label">Footprint</div>
          <div class="sf-area-box">
            <div class="sf-area-label">Panels + alleys</div>
            <div class="sf-area-val">{footprint_w:.1f} × {footprint_h:.1f} m</div>
            <div class="sf-area-sub">{footprint_area:.1f} m²</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Auto-fit toggle
    st.markdown('<div class="sf-panel-section sf-autofit-section">', unsafe_allow_html=True)
    hydrate_widgets(["sb_use_fit", "sb_num_pairs", "sb_num_rows"])
    st.checkbox("Auto-fit to max area", key="sb_use_fit")
    if not st.session_state.get("sb_use_fit", True):
        r1, r2 = st.columns(2)
        with r1:
            st.number_input("Pairs / row", min_value=0, step=1, key="sb_num_pairs")
        with r2:
            st.number_input("Rows", min_value=0, step=1, key="sb_num_rows")
    keys = list(SETUP_WIDGET_KEYS)
    if st.session_state.get("sb_use_fit", True):
        keys = [k for k in keys if k not in ("sb_num_pairs", "sb_num_rows")]
    persist_widgets(keys)


def render_dimension_bubbles() -> None:
    """Floating ↔ / ↕ max-area controls on the canvas edges."""
    hydrate_widgets(["sb_max_x", "sb_max_y"])
    w_col, h_col = st.columns(2, gap="small")

    def _dim_pill(slot_cls: str, arrow: str, widget_key: str, label: str) -> None:
        st.markdown(f'<span class="sf-dim-row-marker {slot_cls}"></span>', unsafe_allow_html=True)
        arrow_c, val_c, unit_c = st.columns([0.5, 1.0, 0.5], gap="small")
        with arrow_c:
            st.markdown(f'<span class="sf-dim-arrow">{arrow}</span>', unsafe_allow_html=True)
        with val_c:
            st.number_input(
                label,
                min_value=1.0,
                step=0.5,
                key=widget_key,
                label_visibility="collapsed",
            )
        with unit_c:
            st.markdown('<span class="sf-dim-unit">m</span>', unsafe_allow_html=True)

    with w_col:
        _dim_pill("sf-dim-w", "↔", "sb_max_x", "Canvas width (m)")
    with h_col:
        _dim_pill("sf-dim-h", "↕", "sb_max_y", "Canvas height (m)")

    persist_widgets(["sb_max_x", "sb_max_y"])


def _hud_var_column(
    label: str,
    *,
    persist_key: str,
    widget_key: str,
    unit: str,
    minimum: float,
    maximum: float,
    step: float,
    marker_key: str,
    tooltip_svg: str,
    tooltip_text: str,
    accent: bool = False,
    min_width: str = "108px",
) -> None:
    accent_cls = " amber" if accent else ""
    val = float(get_persist(persist_key))
    display = int(val) if step == 1 and val == int(val) else (f"{val:.1f}" if step < 1 else f"{val:.0f}")
    val_cls = "sf-hud-val-display amber" if accent else "sf-hud-val-display"

    st.markdown(
        f"""
        <div class="sf-hud-cell" style="min-width:{min_width}">
          <div class="sf-hud-label{accent_cls}">{label} <span class="info-dot">i</span></div>
          <div class="sf-hud-tooltip">{tooltip_svg}<div class="sf-hud-tooltip-label">{tooltip_text}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<span class="sf-hud-controls-marker"></span>', unsafe_allow_html=True)
    m, v, u, p = st.columns([1, 2, 1, 1], gap="small")
    with m:
        if st.button("−", key=f"hud_minus_{marker_key}"):
            _adjust_persist(persist_key, widget_key, -1, minimum=minimum, maximum=maximum, step=step)
            st.rerun()
    with v:
        st.markdown(f'<div class="{val_cls}">{display}</div>', unsafe_allow_html=True)
    with u:
        st.markdown(f'<div class="sf-hud-unit">{unit}</div>', unsafe_allow_html=True)
    with p:
        if st.button("+", key=f"hud_plus_{marker_key}"):
            _adjust_persist(persist_key, widget_key, 1, minimum=minimum, maximum=maximum, step=step)
            st.rerun()


def render_setup_hud(*, can_proceed: bool) -> bool:
    """Bottom HUD — returns True if NEXT was pressed."""
    hydrate_widgets(["sb_mid_clamp", "sb_alley_reach", "sb_alley_w"])
    spine_edge = str(get_persist("persist_spine_edge"))

    gap = float(get_persist("persist_mid_clamp"))
    reach = int(get_persist("persist_alley_reach"))
    alley_w = float(get_persist("persist_alley_w"))

    cols = st.columns([1.05, 1.15, 1.0, 0.95, 0.72], gap="small")

    with cols[0]:
        st.markdown('<span class="sf-hud-bar-marker"></span>', unsafe_allow_html=True)
        _hud_var_column(
            "Gap",
            persist_key="persist_mid_clamp",
            widget_key="sb_mid_clamp",
            unit="in",
            minimum=0.0,
            maximum=4.0,
            step=0.25,
            marker_key="gap",
            tooltip_svg=gap_tooltip_svg(gap),
            tooltip_text="Space between two panels at the mid-clamp",
        )
    with cols[1]:
        _hud_var_column(
            "Alley reach",
            persist_key="persist_alley_reach",
            widget_key="sb_alley_reach",
            unit="panels",
            minimum=2,
            maximum=4,
            step=1,
            marker_key="reach",
            tooltip_svg=reach_tooltip_svg(reach),
            tooltip_text="Max distance from any panel to the nearest alley",
            accent=True,
            min_width="124px",
        )
    with cols[2]:
        _hud_var_column(
            "Alley W",
            persist_key="persist_alley_w",
            widget_key="sb_alley_w",
            unit="m",
            minimum=0.1,
            maximum=3.0,
            step=0.1,
            marker_key="alley_w",
            tooltip_svg=alley_width_tooltip_svg(alley_w),
            tooltip_text="Width of each maintenance walkway between panels",
        )
    with cols[3]:
        st.markdown(
            f"""
            <div class="sf-hud-cell" style="min-width:112px">
              <div class="sf-hud-label">Spine edge <span class="info-dot">i</span></div>
              <div class="sf-hud-tooltip">{spine_tooltip_svg(spine_edge)}
                <div class="sf-hud-tooltip-label">The spine alley runs along this edge</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<span class="sf-hud-spine-marker"></span>', unsafe_allow_html=True)
        next_edge = "top" if spine_edge == "bottom" else "bottom"
        if st.button(spine_edge.upper(), key="sf_spine_toggle", width="stretch"):
            st.session_state.persist_spine_edge = next_edge
            st.session_state.sf_toast = f"Spine edge: {next_edge.upper()}"
            st.rerun()
    with cols[4]:
        st.markdown('<span class="sf-hud-proceed-marker"></span>', unsafe_allow_html=True)
        proceed = st.button("→\nNEXT", type="primary", disabled=not can_proceed, key="sf_hud_next", width="stretch")

    persist_widgets(["sb_mid_clamp", "sb_alley_reach", "sb_alley_w"])
    return proceed
