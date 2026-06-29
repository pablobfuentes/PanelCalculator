"""Modal to add a new panel type."""

from __future__ import annotations

import streamlit as st

from ui.panel_catalog import DEFAULT_COLORS, add_panel_type, set_selected_panel_key

SWATCH_COLORS = (
    "#E74C3C",
    "#9B59B6",
    "#F39C12",
    "#1ABC9C",
    "#E91E63",
    "#3B7DD8",
    "#3ECF8E",
)


@st.dialog("New panel type", width="small")
def new_panel_type_dialog() -> None:
    st.markdown("Define a module for the layout catalog.")
    name = st.text_input("Panel name", placeholder="e.g. Panel C", key="dlg_panel_name")
    c1, c2 = st.columns(2)
    with c1:
        length = st.number_input("Length (m)", min_value=0.1, step=0.01, value=2.0, key="dlg_len")
    with c2:
        width = st.number_input("Width (m)", min_value=0.1, step=0.01, value=1.0, key="dlg_wid")
    c3, c4 = st.columns(2)
    with c3:
        weight = st.number_input("Weight (kg)", min_value=0.1, step=0.5, value=20.0, key="dlg_kg")
    with c4:
        watt_peak = st.number_input("Watt-peak (Wp)", min_value=0.0, step=10.0, value=400.0, key="dlg_wp")

    st.caption("Panel color")
    swatch_cols = st.columns(len(SWATCH_COLORS))
    if "dlg_panel_color" not in st.session_state:
        st.session_state.dlg_panel_color = SWATCH_COLORS[0]
    for index, color in enumerate(SWATCH_COLORS):
        with swatch_cols[index]:
            if st.button(
                "●",
                key=f"dlg_swatch_{index}",
                help=color,
                width="stretch",
            ):
                st.session_state.dlg_panel_color = color
    selected_color = st.session_state.dlg_panel_color
    st.markdown(
        f'<div style="width:100%;height:8px;border-radius:4px;background:{selected_color};'
        f'box-shadow:0 0 8px {selected_color}55;"></div>',
        unsafe_allow_html=True,
    )

    btn1, btn2 = st.columns(2)
    with btn1:
        if st.button("Cancel", width="stretch"):
            st.rerun()
    with btn2:
        if st.button("Add panel", type="primary", width="stretch"):
            try:
                panel = add_panel_type(
                    name=name or "New panel",
                    length=float(length),
                    width=float(width),
                    weight=float(weight),
                    watt_peak=float(watt_peak),
                    color=selected_color,
                )
                set_selected_panel_key(panel.key)
                st.session_state.sf_toast = f"{panel.name} added!"
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
