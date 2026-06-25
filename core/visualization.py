"""Plotly visualization for panel layouts."""

from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go

from core.layout import (
    Rect,
    accumulate_grid,
    collect_alley_rects,
    grid_bbox,
)
from core.models import LayoutConfig, PanelSpec
from core.tributary import Column

PANEL_FILL = "rgba(46, 134, 193, 0.85)"
PANEL_LINE = "#1a5276"
ALLEY_FILL = "rgba(231, 76, 60, 0.35)"
ALLEY_LINE = "#c0392b"
SPINE_FILL = "rgba(192, 57, 43, 0.45)"
SPINE_LINE = "#922b21"
BBOX_LINE = "#27ae60"
MAX_AREA_LINE = "rgba(127, 140, 141, 0.8)"
OBSTACLE_FILL = "rgba(231, 76, 60, 0.25)"
OBSTACLE_LINE = "#c0392b"
COLUMN_ACTIVE_COLOR = "#2c3e50"
COLUMN_EXCLUDED_COLOR = "#e74c3c"
AXIS_PADDING_M = 0.25
FIGURE_WIDTH = 900
FIGURE_HEIGHT = 700
# Approximate drawable plot area inside the figure (margins + legend).
PLOT_WIDTH_RATIO = 0.82
PLOT_HEIGHT_RATIO = 0.75


def _axis_upper_limit(max_extent: float) -> float:
    """Positive axis limit with a small margin; keep origin at (0, 0)."""
    if max_extent <= 0:
        return 1.0
    return max_extent + AXIS_PADDING_M


def _non_negative_axis_limits(
    x_max: float,
    y_max: float,
    *,
    fig_width: int = FIGURE_WIDTH,
    fig_height: int = FIGURE_HEIGHT,
) -> tuple[float, float]:
    """
    Return axis upper bounds starting at zero.

    When equal scale is enforced, Plotly may pad the shorter data axis into
    negative space. Extend only the positive direction to match plot aspect.
    """
    x_upper = _axis_upper_limit(x_max)
    y_upper = _axis_upper_limit(y_max)
    plot_aspect = (fig_width * PLOT_WIDTH_RATIO) / (fig_height * PLOT_HEIGHT_RATIO)
    data_aspect = x_upper / y_upper
    if data_aspect < plot_aspect:
        x_upper = y_upper * plot_aspect
    elif data_aspect > plot_aspect:
        y_upper = x_upper / plot_aspect
    return x_upper, y_upper


def _load_intensity_color(t: float, *, alpha: float = 0.42) -> str:
    """Map normalized load intensity to light green → amber → red."""
    t = max(0.0, min(1.0, t))
    if t <= 0.5:
        blend = t / 0.5
        red = int(144 + (255 - 144) * blend)
        green = int(238 + (191 - 238) * blend)
        blue = int(144 + (0 - 144) * blend)
    else:
        blend = (t - 0.5) / 0.5
        red = int(255 + (220 - 255) * blend)
        green = int(191 + (53 - 191) * blend)
        blue = int(0 + (69 - 0) * blend)
    return f"rgba({red},{green},{blue},{alpha})"


def _add_tributary_zone(
    fig: go.Figure,
    column: Column,
    *,
    fillcolor: str,
    showlegend: bool,
) -> None:
    if column.tributary_rect is None:
        return
    x, y, w, h = column.tributary_rect
    fig.add_shape(
        type="rect",
        x0=x,
        y0=y,
        x1=x + w,
        y1=y + h,
        fillcolor=fillcolor,
        line=dict(color="rgba(80, 80, 80, 0.6)", width=1, dash="dot"),
        layer="below",
    )
    fig.add_trace(
        go.Scatter(
            x=[x + w / 2],
            y=[y + h / 2],
            mode="markers",
            marker=dict(size=0.1, opacity=0),
            name="Tributary zone",
            legendgroup="tributary",
            showlegend=showlegend,
            customdata=[[column.column_id, column.tributary_area_m2, column.estimated_load_kn]],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Tributary area: %{customdata[1]:.2f} m²<br>"
                "Estimated load: %{customdata[2]:.2f} kN"
                "<extra></extra>"
            ),
        )
    )


def _apply_figure_axes(fig: go.Figure, x_max: float, y_max: float) -> None:
    x_upper, y_upper = _non_negative_axis_limits(x_max, y_max)
    fig.update_xaxes(
        title_text="X (m)",
        scaleanchor="y",
        scaleratio=1,
        range=[0, x_upper],
        autorange=False,
        constrain="domain",
        zeroline=True,
        showline=True,
        linewidth=1,
        linecolor="#333",
    )
    fig.update_yaxes(
        title_text="Y (m)",
        range=[0, y_upper],
        autorange=False,
        constrain="domain",
        zeroline=True,
        showline=True,
        linewidth=1,
        linecolor="#333",
    )
    fig.update_layout(
        template="plotly_white",
        width=FIGURE_WIDTH,
        height=FIGURE_HEIGHT,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
    )


def _add_rect(
    fig: go.Figure,
    rect: Rect,
    *,
    fillcolor: str,
    line_color: str,
    line_width: int = 1,
    line_dash: str = "solid",
    legend_group: str,
    showlegend: bool,
    name: str,
) -> None:
    x, y, w, h = rect
    fig.add_shape(
        type="rect",
        x0=x,
        y0=y,
        x1=x + w,
        y1=y + h,
        fillcolor=fillcolor,
        line=dict(color=line_color, width=line_width, dash=line_dash),
        layer="below",
    )
    fig.add_trace(
        go.Scatter(
            x=[x + w / 2],
            y=[y + h / 2],
            mode="markers",
            marker=dict(size=0.1, opacity=0),
            name=name,
            legendgroup=legend_group,
            showlegend=showlegend,
            hoverinfo="skip",
        )
    )


def build_layout_figure(
    panel: PanelSpec,
    config: LayoutConfig,
    num_pairs_per_row: int,
    num_rows: int,
    *,
    show_max_area: bool = True,
    tributary_columns: list[Column] | None = None,
    obstacle_zones: list[Rect] | None = None,
    title: str = "Panel layout",
) -> go.Figure:
    """Build a Plotly figure with panels, alleys, optional tributary overlay, and bbox."""
    panels = accumulate_grid(panel, config, num_pairs_per_row, num_rows)
    alleys = collect_alley_rects(panel, config, num_pairs_per_row, num_rows)
    bbox = grid_bbox(panels + alleys)

    fig = go.Figure()

    for index, rect in enumerate(panels):
        _add_rect(
            fig,
            rect,
            fillcolor=PANEL_FILL,
            line_color=PANEL_LINE,
            legend_group="panels",
            showlegend=index == 0,
            name="Panel",
        )

    spine_legend_shown = False
    parallel_legend_shown = False
    for rect in alleys:
        is_spine = rect[1] == 0.0 and rect[3] <= config.alley_width + 1e-9
        if is_spine:
            showlegend = not spine_legend_shown
            spine_legend_shown = True
        else:
            showlegend = not parallel_legend_shown
            parallel_legend_shown = True
        _add_rect(
            fig,
            rect,
            fillcolor=SPINE_FILL if is_spine else ALLEY_FILL,
            line_color=SPINE_LINE if is_spine else ALLEY_LINE,
            legend_group="spine" if is_spine else "alleys",
            showlegend=showlegend,
            name="Edge spine" if is_spine else "Parallel alley",
        )

    if tributary_columns:
        loads = [
            column.estimated_load_kn
            for column in tributary_columns
            if not column.excluded and column.tributary_area_m2 > 0
        ]
        min_load = min(loads) if loads else 0.0
        max_load = max(loads) if loads else 0.0
        tributary_legend_shown = False
        for column in tributary_columns:
            if column.excluded or column.tributary_rect is None:
                continue
            if max_load > min_load:
                intensity = (column.estimated_load_kn - min_load) / (max_load - min_load)
            else:
                intensity = 0.0
            _add_tributary_zone(
                fig,
                column,
                fillcolor=_load_intensity_color(intensity),
                showlegend=not tributary_legend_shown,
            )
            tributary_legend_shown = True

        active_legend_shown = False
        excluded_legend_shown = False
        for column in tributary_columns:
            is_excluded = column.excluded
            fig.add_trace(
                go.Scatter(
                    x=[column.x],
                    y=[column.y],
                    mode="markers",
                    marker=dict(
                        symbol="triangle-up",
                        size=10,
                        color=COLUMN_EXCLUDED_COLOR if is_excluded else COLUMN_ACTIVE_COLOR,
                    ),
                    name="Excluded column" if is_excluded else "Column",
                    legendgroup="columns_excluded" if is_excluded else "columns_active",
                    showlegend=(
                        (not excluded_legend_shown)
                        if is_excluded
                        else (not active_legend_shown)
                    ),
                    hovertemplate=(
                        f"<b>{column.column_id}</b>"
                        f"{' (excluded)' if is_excluded else ''}<br>"
                        f"X: {column.x:.2f} m<br>"
                        f"Y: {column.y:.2f} m"
                        "<extra></extra>"
                    ),
                )
            )
            if is_excluded:
                excluded_legend_shown = True
            else:
                active_legend_shown = True

    if obstacle_zones:
        obstacle_legend_shown = False
        for index, rect in enumerate(obstacle_zones):
            _add_rect(
                fig,
                rect,
                fillcolor=OBSTACLE_FILL,
                line_color=OBSTACLE_LINE,
                line_width=2,
                line_dash="dash",
                legend_group="obstacles",
                showlegend=not obstacle_legend_shown,
                name="Obstacle zone",
            )
            obstacle_legend_shown = True

    bx, by, bw, bh = bbox
    if bw > 0 and bh > 0:
        _add_rect(
            fig,
            bbox,
            fillcolor="rgba(0,0,0,0)",
            line_color=BBOX_LINE,
            line_width=2,
            line_dash="dash",
            legend_group="bbox",
            showlegend=True,
            name="Layout bbox",
        )

    if show_max_area:
        max_rect = (0.0, 0.0, config.max_area_x, config.max_area_y)
        _add_rect(
            fig,
            max_rect,
            fillcolor="rgba(0,0,0,0)",
            line_color=MAX_AREA_LINE,
            line_width=2,
            line_dash="dot",
            legend_group="max_area",
            showlegend=True,
            name="Max area",
        )
        x_max = max(bx + bw, config.max_area_x)
        y_max = max(by + bh, config.max_area_y)
    else:
        x_max = bx + bw
        y_max = by + bh

    _apply_figure_axes(fig, x_max, y_max)
    fig.update_layout(title=title)
    return fig


def save_layout_figure(
    figure: go.Figure,
    path: str | Path,
) -> Path:
    """Write an interactive HTML figure to disk."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(str(output), include_plotlyjs="cdn")
    return output
