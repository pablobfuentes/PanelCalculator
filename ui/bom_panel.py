"""Live BOM sidebar panel (Phase 4.3)."""

from __future__ import annotations

import streamlit as st

from core.bom import BomResult
from ui.bom_settings_dialog import render_bom_settings_button


def render_bom_panel(bom: BomResult) -> None:
    """Render BOM metrics beside the design canvas."""
    header_col, settings_col = st.columns([5, 1])
    with header_col:
        st.markdown("#### Live BOM")
    with settings_col:
        render_bom_settings_button()
    st.caption("Updates with layout, column grid, and material profiles.")

    st.metric("Panels", bom.panel_count)
    st.metric("Columns (active)", bom.active_column_count)
    if bom.column_count != bom.active_column_count:
        st.caption(f"{bom.column_count} total ({bom.column_count - bom.active_column_count} excluded)")

    st.metric("PTR 4×4", f"{bom.ptr_total_length_m:.1f} m")
    st.metric("Truss chords", f"{bom.truss_chord_length_m:.1f} m")
    st.metric("Base plates", bom.base_plate_count)
    st.metric("Est. steel", f"{bom.steel_tonnage:.2f} t")

    with st.expander("BOM detail"):
        st.dataframe(
            [
                {
                    "Item": line.item,
                    "Qty": round(line.quantity, 3),
                    "Unit": line.unit,
                    "Note": line.note,
                }
                for line in bom.lines
            ],
            width="stretch",
            hide_index=True,
        )
