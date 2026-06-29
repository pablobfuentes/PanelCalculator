"""Materials tab — steel sections and load combinations (Phase 5.1–5.2)."""

from __future__ import annotations

import streamlit as st

from core.loads import load_combination_rows
from core.material_library import library_table_row
from core.sections import base_plate_summary_row, section_summary_row
from ui.material_catalogue_io import render_catalogue_import_export
from ui.material_library_state import get_library
from ui.materials_state import material_sections_from_session


def render_materials_tab() -> None:
    st.subheader("Materials")
    st.caption(
        "Steel section properties and factored load combinations for FEA (Phase 5.3). "
        "Edit section values in the sidebar."
    )

    st.info(
        "**Section units:** A in m² · Ix in **m⁴** (not mm⁴) · Fy in MPa · "
        "Mass = A × 7850 kg/m³."
    )

    materials = material_sections_from_session()
    rows = [
        section_summary_row("PTR post (4×4)", materials.ptr_post),
        section_summary_row("Secondary beam", materials.secondary_beam),
        section_summary_row("Truss chord", materials.truss_chord),
        base_plate_summary_row("Base plate", materials.base_plate),
    ]

    st.markdown("#### Section catalog")
    st.caption("Active profiles assigned to each structural role (see Live BOM ⚙ for assignments).")
    st.dataframe(
        [
            {
                "Role": row["Role"],
                "Section": row["Section"],
                "A (m²)": (
                    f"{row['A (m²)']:.6f}" if "A (m²)" in row else "—"
                ),
                "Ix (m⁴)": (
                    f"{row['Ix (m⁴)']:.3e}" if "Ix (m⁴)" in row else "—"
                ),
                "Fy (MPa)": f"{row['Fy (MPa)']:.0f}",
                "Sx (m³)": (
                    f"{row['Sx (m³)']:.3e}"
                    if row.get("Sx (m³)") is not None
                    else "—"
                ),
                "Mass": (
                    f"{row['Mass (kg/m)']:.2f} kg/m"
                    if "Mass (kg/m)" in row
                    else f"{row['Mass (kg/ea)']:.2f} kg/ea"
                ),
            }
            for row in rows
        ],
        width="stretch",
        hide_index=True,
    )

    st.markdown("#### Profile library")
    st.dataframe(
        [library_table_row(profile) for profile in get_library()],
        width="stretch",
        hide_index=True,
    )

    with st.expander("Import / export catalogue (CSV)"):
        render_catalogue_import_export(key_prefix="materials_tab")

    with st.expander("Catalog notes"):
        st.markdown(
            """
            Default sections are converted from **AISC** imperial tables to SI:

            - **PTR post** — HSS4×4×¼ (A500 Gr. B)
            - **Secondary beam** — HSS3×2×¼
            - **Truss chord** — L2×2×¼ angle

            For IMCA metric tubes, enter catalog values in the sidebar. Convert **Ix**
            to m⁴ (divide mm⁴ by 10¹²).
            """
        )

    st.markdown("#### Load combinations")
    st.caption(
        "Factored combinations per CFE practice — audit before running the solver. "
        "**D** = dead (panel self-weight), **L** = live/maintenance, **W** = wind (NTC-Viento 2020)."
    )
    st.dataframe(load_combination_rows(), width="stretch", hide_index=True)
