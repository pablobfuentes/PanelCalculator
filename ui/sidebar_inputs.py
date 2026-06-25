"""Unified Streamlit sidebar — tab-aware Phase 4.1+ inputs."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from core.columns import (
    DEFAULT_COLUMN_SPACING_M,
    MIN_COLUMN_COUNT,
    count_from_spacing,
    panel_field_bbox,
    spacing_from_count,
)
from core.models import (
    LayoutConfig,
    PanelSpec,
    WindConfig,
    WIND_EXPOSURE_CATEGORIES,
)
from core.wind import exposure_label
from ui.layout_state import (
    layout_config_from_inputs,
    layout_from_snapshot,
    resolve_layout,
)
from ui.session_store import (
    ANALYSIS_WIDGET_KEYS,
    SETUP_WIDGET_KEYS,
    get_persist,
    hydrate_panel_lock_state,
    hydrate_widgets,
    init_session_defaults,
    persist_panel_lock_state,
    persist_widgets,
    reset_app_session,
)

EXPOSURE_DESCRIPTIONS_SHORT: dict[str, str] = {
    "A": "Dense urban centers; buildings mostly > 15 m.",
    "B": "Urban, suburban, or wooded terrain.",
    "C": "Open country with scattered obstructions.",
    "D": "Flat unobstructed coastal exposure.",
}

VIEW_SETUP = "Setup"
VIEW_ANALYSIS = "Analysis"


@dataclass
class SidebarInputs:
    """Inputs for the active main view."""

    panel: PanelSpec
    config: LayoutConfig
    wind: WindConfig
    column_count_x: int
    column_count_y: int
    column_height_m: float
    use_fit: bool
    num_pairs_manual: int
    num_rows_manual: int
    target_panels: int
    panels_locked: bool


def _panel_from_session() -> PanelSpec:
    return PanelSpec(
        length=float(get_persist("persist_length")),
        width=float(get_persist("persist_width")),
        weight=float(get_persist("persist_weight")),
        tilt_angle=float(get_persist("persist_tilt")),
    )


def _config_from_session() -> LayoutConfig:
    return layout_config_from_inputs(
        mid_clamp_in=float(get_persist("persist_mid_clamp")),
        alley_width=float(get_persist("persist_alley_w")),
        alley_reach=int(get_persist("persist_alley_reach")),
        max_area_x=float(get_persist("persist_max_x")),
        max_area_y=float(get_persist("persist_max_y")),
    )


def _seed_column_counts(field_width: float, field_height: float) -> None:
    if st.session_state.get("_column_counts_seeded"):
        return
    if "sb_column_spacing" in st.session_state:
        st.session_state.persist_column_count_x = count_from_spacing(
            field_width, float(st.session_state.sb_column_spacing)
        )
    else:
        st.session_state.persist_column_count_x = count_from_spacing(
            field_width, DEFAULT_COLUMN_SPACING_M
        )
    if "sb_column_spacing_y" in st.session_state:
        st.session_state.persist_column_count_y = count_from_spacing(
            field_height, float(st.session_state.sb_column_spacing_y)
        )
    else:
        st.session_state.persist_column_count_y = count_from_spacing(
            field_height, DEFAULT_COLUMN_SPACING_M
        )
    st.session_state._column_counts_seeded = True


def render_sidebar(active_view: str) -> SidebarInputs:
    """Render sidebar sections for the active main view."""
    init_session_defaults()
    hydrate_panel_lock_state()
    setup_accepted = bool(st.session_state.get("setup_accepted"))
    show_setup_fields = active_view == VIEW_SETUP
    show_analysis_fields = active_view == VIEW_ANALYSIS and setup_accepted
    panels_locked = bool(st.session_state.panels_locked)

    with st.sidebar:
        st.caption(f"**{active_view}**")

        if show_setup_fields:
            hydrate_widgets(SETUP_WIDGET_KEYS)

            st.header("Panel")
            st.number_input(
                "Length (m)", min_value=0.1, step=0.1, key="sb_length"
            )
            st.number_input("Width (m)", min_value=0.1, step=0.1, key="sb_width")
            st.number_input(
                "Weight (kg)", min_value=0.1, step=0.5, key="sb_weight"
            )
            st.number_input(
                "Tilt (°)", min_value=0.0, max_value=90.0, step=1.0, key="sb_tilt"
            )

            st.header("Layout")
            st.number_input(
                'Mid-clamp gap (in)', min_value=0.0, step=0.25, key="sb_mid_clamp"
            )
            st.number_input(
                "Alley width (m)", min_value=0.1, step=0.1, key="sb_alley_w"
            )
            st.number_input(
                "Alley reach (panels)",
                min_value=2,
                max_value=4,
                step=1,
                key="sb_alley_reach",
            )
            st.number_input(
                "Max area X (m)", min_value=1.0, step=0.5, key="sb_max_x"
            )
            st.number_input(
                "Max area Y (m)", min_value=1.0, step=0.5, key="sb_max_y"
            )

            st.header("Grid mode")
            st.checkbox("Auto-fit to max area", key="sb_use_fit")
            rendered_setup_keys = list(SETUP_WIDGET_KEYS)
            if not st.session_state.sb_use_fit:
                st.number_input(
                    "Pairs per row", min_value=0, step=1, key="sb_num_pairs"
                )
                st.number_input("Rows", min_value=0, step=1, key="sb_num_rows")
            else:
                rendered_setup_keys = [
                    key for key in SETUP_WIDGET_KEYS if key not in ("sb_num_pairs", "sb_num_rows")
                ]

            if panels_locked:
                st.session_state.sb_panels_value = int(st.session_state.locked_panel_count)

            st.header("Panel count")
            panels_col, lock_col = st.columns([4, 1])
            with panels_col:
                st.number_input(
                    "Panels",
                    min_value=2,
                    step=2,
                    key="sb_panels_value",
                    help="Total panels in a rectangular grid (even count). "
                    "Lock to fit this count within the max area.",
                )
            with lock_col:
                st.write("")
                lock_icon = "🔒" if panels_locked else "🔓"
                lock_help = "Unlock panel count" if panels_locked else "Lock panel count"
                if st.button(
                    lock_icon,
                    width="stretch",
                    key="sb_lock_panels",
                    help=lock_help,
                ):
                    if panels_locked:
                        st.session_state.panels_locked = False
                    else:
                        st.session_state.panels_locked = True
                        st.session_state.locked_panel_count = int(
                            st.session_state.sb_panels_value
                        )
                        st.session_state.persist_panels_value = (
                            st.session_state.locked_panel_count
                        )
                    persist_panel_lock_state()

            persist_widgets(rendered_setup_keys + ["sb_panels_value"])
            persist_panel_lock_state()

        if active_view == VIEW_ANALYSIS and not setup_accepted:
            st.info("Accept a layout in **Setup** to unlock Structure and Wind inputs.")

        if show_analysis_fields:
            layout = layout_from_snapshot(st.session_state.setup_snapshot)
            field = panel_field_bbox(layout.panels)
            _, _, field_width, field_height = field
            _seed_column_counts(field_width, field_height)

            hydrate_widgets(ANALYSIS_WIDGET_KEYS)

            st.header("Structure")
            st.number_input(
                "Column height (m)",
                min_value=0.1,
                step=0.1,
                key="sb_column_height",
                help="Above-grade PTR 4×4 height per column (embedment added in BOM).",
            )

            x_col, x_spacing_col = st.columns([3, 2])
            with x_col:
                st.number_input(
                    "Columns along X",
                    min_value=MIN_COLUMN_COUNT,
                    step=1,
                    key="sb_column_count_x",
                    help="Number of column lines across the panel field width.",
                )
            with x_spacing_col:
                st.write("")
                st.caption(
                    f"**{spacing_from_count(field_width, int(st.session_state.sb_column_count_x)):.2f} m** spacing"
                )

            y_col, y_spacing_col = st.columns([3, 2])
            with y_col:
                st.number_input(
                    "Columns along Y",
                    min_value=MIN_COLUMN_COUNT,
                    step=1,
                    key="sb_column_count_y",
                    help="Number of column lines along the panel field depth.",
                )
            with y_spacing_col:
                st.write("")
                st.caption(
                    f"**{spacing_from_count(field_height, int(st.session_state.sb_column_count_y)):.2f} m** spacing"
                )

            st.header("Wind (NTC-Viento 2020)")
            st.number_input(
                "Wind speed (km/h)",
                min_value=1.0,
                step=5.0,
                key="sb_wind_speed",
                help="Basic wind speed V_b for the site per CFE NTC-Viento 2020.",
            )
            st.selectbox(
                "Exposure category",
                options=list(WIND_EXPOSURE_CATEGORIES),
                format_func=exposure_label,
                key="sb_wind_exposure",
            )
            st.caption(
                EXPOSURE_DESCRIPTIONS_SHORT[str(st.session_state.sb_wind_exposure)]
            )

            persist_widgets(ANALYSIS_WIDGET_KEYS)

        if show_analysis_fields and bool(get_persist("persist_panels_locked")):
            st.caption(
                f"Panel count **locked** at {int(get_persist('persist_locked_panel_count'))} panels"
            )

        st.divider()
        if st.button("Reset session", type="secondary", width="stretch", key="sb_reset"):
            reset_app_session()
            st.rerun()

    persist_panel_lock_state()

    panel = _panel_from_session()
    config = _config_from_session()
    use_fit = bool(get_persist("persist_use_fit"))
    num_pairs_manual = int(get_persist("persist_num_pairs"))
    num_rows_manual = int(get_persist("persist_num_rows"))
    panels_value = int(get_persist("persist_panels_value"))
    column_count_x = int(get_persist("persist_column_count_x"))
    column_count_y = int(get_persist("persist_column_count_y"))
    column_height_m = float(get_persist("persist_column_height"))
    wind = _wind_config(
        wind_speed_kmh=float(get_persist("persist_wind_speed")),
        exposure_category=str(get_persist("persist_wind_exposure")),
    )

    target_panels = (
        int(get_persist("persist_locked_panel_count"))
        if bool(get_persist("persist_panels_locked"))
        else panels_value
    )

    panels_locked = bool(get_persist("persist_panels_locked"))

    return SidebarInputs(
        panel=panel,
        config=config,
        wind=wind,
        column_count_x=column_count_x,
        column_count_y=column_count_y,
        column_height_m=column_height_m,
        use_fit=use_fit,
        num_pairs_manual=num_pairs_manual,
        num_rows_manual=num_rows_manual,
        target_panels=target_panels,
        panels_locked=panels_locked,
    )


def _wind_config(*, wind_speed_kmh: float, exposure_category: str) -> WindConfig:
    try:
        return WindConfig(
            wind_speed_kmh=float(wind_speed_kmh),
            exposure_category=exposure_category,
        )
    except TypeError:
        wind = WindConfig()
        wind.wind_speed_kmh = float(wind_speed_kmh)
        wind.exposure_category = exposure_category
        return wind


def resolve_layout_from_inputs(inputs: SidebarInputs):
    """Build a ResolvedLayout from sidebar inputs."""
    return resolve_layout(
        panel=inputs.panel,
        config=inputs.config,
        use_fit=inputs.use_fit,
        panels_locked=inputs.panels_locked,
        target_panels=inputs.target_panels,
        num_pairs_manual=inputs.num_pairs_manual,
        num_rows_manual=inputs.num_rows_manual,
    )
