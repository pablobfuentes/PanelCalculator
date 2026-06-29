"""BOM material profile settings modal."""

from __future__ import annotations

import streamlit as st

from core.material_library import (
    ELEMENT_ROLES,
    ROLE_LABELS,
    MaterialProfile,
    library_table_row,
    new_profile_id,
    profiles_for_role,
)
from ui.material_catalogue_io import render_catalogue_import_export
from ui.material_library_state import (
    get_assignments,
    get_library,
    set_assignments,
    set_library,
    sync_assignments_to_legacy_persist,
)


@st.dialog("Material profiles", width="large")
def bom_material_settings_dialog() -> None:
    """Select profiles per element role and manage the in-memory library."""
    library = get_library()
    draft_assignments = dict(get_assignments())

    st.markdown("**Assigned profiles**")
    st.caption("Choose which library entry applies to each structural element.")

    for role in ELEMENT_ROLES:
        options = profiles_for_role(library, role)
        if not options:
            st.warning(f"No library entries for {ROLE_LABELS[role]}. Add one below.")
            continue
        labels = [profile.name for profile in options]
        ids = [profile.id for profile in options]
        current_id = draft_assignments.get(role)
        index = ids.index(current_id) if current_id in ids else 0
        choice = st.selectbox(
            ROLE_LABELS[role],
            options=labels,
            index=index,
            key=f"bom_dialog_assign_{role}",
        )
        draft_assignments[role] = ids[labels.index(choice)]

    st.divider()
    st.markdown("**Library**")
    st.caption("All profiles available for assignment. Add custom sections or base plates.")
    st.dataframe(
        [library_table_row(profile) for profile in library],
        width="stretch",
        hide_index=True,
    )

    with st.expander("Import / export catalogue (CSV)"):
        render_catalogue_import_export(key_prefix="bom_dialog")

    with st.expander("Add library entry"):
        entry_kind = st.selectbox(
            "Type",
            options=["Section", "Base plate"],
            key="bom_dialog_new_kind",
        )
        new_name = st.text_input("Name", key="bom_dialog_new_name", placeholder="e.g. HSS 4×4×¼")
        new_fy = st.number_input("Fy (MPa)", min_value=1.0, step=5.0, key="bom_dialog_new_fy")

        if entry_kind == "Section":
            new_a = st.number_input(
                "A (m²)",
                min_value=1e-6,
                format="%.6f",
                step=1e-5,
                key="bom_dialog_new_a",
            )
            new_ix = st.number_input(
                "Ix (m⁴)",
                min_value=1e-12,
                format="%.3e",
                step=1e-7,
                key="bom_dialog_new_ix",
            )
            new_depth = st.number_input(
                "Outer depth (m)",
                min_value=0.0,
                format="%.4f",
                step=0.001,
                key="bom_dialog_new_depth",
                help="Optional — used for section modulus in code checks.",
            )
            if st.button("Add section", key="bom_dialog_add_section"):
                if not new_name.strip():
                    st.error("Name is required.")
                else:
                    depth = new_depth if new_depth > 0 else None
                    library.append(
                        MaterialProfile(
                            id=new_profile_id(),
                            name=new_name.strip(),
                            kind="section",
                            A=float(new_a),
                            Ix=float(new_ix),
                            Fy=float(new_fy),
                            outer_depth_m=depth,
                        )
                    )
                    set_library(library)
                    st.rerun()
        else:
            new_area = st.number_input(
                "Plate area (m²)",
                min_value=1e-6,
                format="%.4f",
                step=0.001,
                key="bom_dialog_new_area",
            )
            new_thickness = st.number_input(
                "Thickness (m)",
                min_value=1e-4,
                format="%.4f",
                step=0.001,
                key="bom_dialog_new_thickness",
            )
            if st.button("Add base plate", key="bom_dialog_add_plate"):
                if not new_name.strip():
                    st.error("Name is required.")
                else:
                    library.append(
                        MaterialProfile(
                            id=new_profile_id(),
                            name=new_name.strip(),
                            kind="base_plate",
                            Fy=float(new_fy),
                            plate_area_m2=float(new_area),
                            plate_thickness_m=float(new_thickness),
                        )
                    )
                    set_library(library)
                    st.rerun()

    st.divider()
    accept_col, cancel_col = st.columns(2)
    with accept_col:
        if st.button("Accept", type="primary", width="stretch", key="bom_dialog_accept"):
            set_assignments(draft_assignments)
            sync_assignments_to_legacy_persist(draft_assignments, library)
            st.rerun()
    with cancel_col:
        if st.button("Cancel", width="stretch", key="bom_dialog_cancel"):
            st.rerun()


def render_bom_settings_button() -> None:
    if st.button(
        "⚙",
        key="bom_material_settings",
        help="Material profiles & library",
        width="stretch",
    ):
        bom_material_settings_dialog()
