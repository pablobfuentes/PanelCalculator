"""Panel Calculator — Streamlit entry point."""

import importlib
import os

import streamlit as st

# Streamlit keeps imported modules in memory across reruns. Reload on each run so
# layout changes apply without a manual server restart (skip during pytest).
if os.environ.get("PANEL_CALCULATOR_SKIP_RELOAD") != "1":
    import core.models as _models
    import core.layout as _layout
    import core.visualization as _visualization

    importlib.reload(_models)
    importlib.reload(_layout)
    importlib.reload(_visualization)

from core.layout import (
    accumulate_grid,
    collect_alley_rects,
    fit_to_area,
    grid_bbox,
    parallel_alley_gap_labels,
)
from core.models import DEFAULT_MID_CLAMP_GAP_M, LayoutConfig, PanelSpec
from core.visualization import build_layout_figure


def _layout_config(
    *,
    mid_clamp_gap: float,
    alley_width: float,
    alley_reach: int,
    max_area_x: float,
    max_area_y: float,
) -> LayoutConfig:
    """Build LayoutConfig even if Streamlit still has a stale dataclass cached."""
    base_kwargs = {
        "mid_clamp_gap": mid_clamp_gap,
        "alley_width": alley_width,
        "max_area_x": max_area_x,
        "max_area_y": max_area_y,
    }
    try:
        return LayoutConfig(**base_kwargs, alley_reach=alley_reach)
    except TypeError:
        config = LayoutConfig(**base_kwargs)
        config.alley_reach = alley_reach
        return config


st.set_page_config(page_title="Panel Calculator", layout="wide")
st.title("Panel Calculator")
st.caption("Phase 2 demo — layout geometry and Plotly canvas. Full UI (columns, wind, BOM) comes in Phase 4.")

with st.sidebar:
    st.header("Panel")
    length = st.number_input("Length (m)", min_value=0.1, value=2.0, step=0.1)
    width = st.number_input("Width (m)", min_value=0.1, value=1.0, step=0.1)
    weight = st.number_input("Weight (kg)", min_value=0.1, value=25.0, step=0.5)
    tilt = st.number_input("Tilt (°)", min_value=0.0, max_value=90.0, value=10.0, step=1.0)

    st.header("Layout")
    mid_clamp_in = st.number_input('Mid-clamp gap (in)', min_value=0.0, value=1.0, step=0.25)
    alley_width = st.number_input("Alley width (m)", min_value=0.1, value=1.0, step=0.1)
    alley_reach = st.number_input("Alley reach (panels)", min_value=2, max_value=4, value=2, step=1)
    max_area_x = st.number_input("Max area X (m)", min_value=1.0, value=12.0, step=0.5)
    max_area_y = st.number_input("Max area Y (m)", min_value=1.0, value=8.0, step=0.5)

    st.header("Grid mode")
    use_fit = st.checkbox("Auto-fit to max area", value=True)
    if not use_fit:
        num_pairs = st.number_input("Pairs per row", min_value=0, value=3, step=1)
        num_rows = st.number_input("Rows", min_value=0, value=2, step=1)

panel = PanelSpec(length=length, width=width, weight=weight, tilt_angle=tilt)
config = _layout_config(
    mid_clamp_gap=mid_clamp_in * 0.0254 if mid_clamp_in else DEFAULT_MID_CLAMP_GAP_M,
    alley_width=alley_width,
    alley_reach=int(alley_reach),
    max_area_x=max_area_x,
    max_area_y=max_area_y,
)

if use_fit:
    layout = fit_to_area(panel, config)
    num_pairs = layout.num_pairs_per_row
    num_rows = layout.num_rows
    panel_count = len(layout.rectangles)
else:
    num_pairs = int(num_pairs)
    num_rows = int(num_rows)
    panel_count = len(accumulate_grid(panel, config, num_pairs, num_rows))

panels = accumulate_grid(panel, config, num_pairs, num_rows)
alleys = collect_alley_rects(panel, config, num_pairs, num_rows)
bbox = grid_bbox(panels + alleys)
alley_gap_labels = parallel_alley_gap_labels(num_pairs * 2, config.alley_reach)
spine_alleys = [a for a in alleys if a[1] == 0.0 and a[3] <= config.alley_width + 1e-9]
parallel_alleys = [a for a in alleys if a[3] > config.alley_width + 1e-9]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Panels", panel_count)
col2.metric("Pairs / row", num_pairs)
col3.metric("Rows", num_rows)
col4.metric("Alley reach", f"{config.alley_reach} panels")
col5.metric("Layout size", f"{bbox[2]:.1f} × {bbox[3]:.1f} m")

if alley_gap_labels:
    st.caption(
        f"Edge spine (1): bottom row · "
        f"Parallel alleys ({len(parallel_alleys)}): columns {', '.join(alley_gap_labels)}"
    )
else:
    st.caption("Edge spine only — no parallel alleys needed for this row width.")

if panel_count == 0:
    st.warning("No panels fit in the max area with these settings. Increase max area or reduce panel size.")
else:
    fig = build_layout_figure(panel, config, num_pairs, num_rows)
    st.plotly_chart(fig, width="stretch")

with st.expander("Legend"):
    st.markdown(
        """
        - **Blue** — solar panels
        - **Dark red** — edge spine (one horizontal alley at the bottom)
        - **Light red** — parallel service alleys between panel columns
        - **Green dashed** — layout bounding box
        - **Gray dotted** — max allowed footprint
        """
    )
