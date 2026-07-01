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
from core.layout_checks import LayoutElement
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
COLUMN_MARKER_BORDER = "#F5A623"
COLUMN_MARKER_BORDER_WIDTH = 2
COLUMN_MARKER_OUTLINE = "#FFFFFF"
COLUMN_MARKER_OUTLINE_WIDTH = 2.5
COLUMN_MARKER_SIZE = 16
PRELIMINARY_PASS_COLOR = "#2ecc71"
PRELIMINARY_WARN_COLOR = "#f39c12"
PRELIMINARY_FAIL_COLOR = "#e74c3c"
BEAM_LINE_WIDTH = 4
BEAM_HIT_MARKER_SIZE = 22

# SolarForge dark canvas palette
DARK_PANEL_FILL = "rgba(59, 125, 216, 0.88)"
DARK_PANEL_LINE = "#5BB8F5"
DARK_ALLEY_FILL = "rgba(245, 163, 35, 0.55)"
DARK_ALLEY_LINE = "#F5A623"
DARK_SPINE_FILL = "rgba(245, 163, 35, 0.40)"
DARK_SPINE_LINE = "#F5A623"
DARK_BBOX_LINE = "rgba(91, 184, 245, 0.45)"
DARK_MAX_AREA_LINE = "rgba(122, 132, 153, 0.55)"
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


def max_area_pill_percents(
    max_area_x: float,
    max_area_y: float,
    axis_x_max: float,
    axis_y_max: float,
    *,
    fig_width: float,
    fig_height: float,
    margin_l: float = 24,
    margin_r: float = 24,
    margin_t: float = 24,
    margin_b: float = 24,
    pill_gap_px: float = 10,
) -> dict[str, float]:
    """
    Percent positions (0–100) within the Plotly chart box for ↔ / ↕ pills.

    Pills sit just outside the dotted max-area rectangle: width pill centered
    on its top edge, height pill centered on its right edge.
    """
    x_upper, y_upper = _non_negative_axis_limits(
        axis_x_max, axis_y_max, fig_width=int(fig_width), fig_height=int(fig_height)
    )
    inner_w = max(fig_width - margin_l - margin_r, 1)
    inner_h = max(fig_height - margin_t - margin_b, 1)
    plot_aspect = inner_w / inner_h
    data_aspect = x_upper / y_upper if y_upper > 0 else 1.0

    if data_aspect > plot_aspect:
        used_w = inner_w
        used_h = inner_w / data_aspect
        pad_x = 0.0
        pad_y = (inner_h - used_h) / 2
    else:
        used_h = inner_h
        used_w = inner_h * data_aspect
        pad_x = (inner_w - used_w) / 2
        pad_y = 0.0

    max_x_frac = max_area_x / x_upper if x_upper > 0 else 1.0
    max_y_frac = max_area_y / y_upper if y_upper > 0 else 1.0

    origin_x = margin_l + pad_x
    origin_y = margin_t + pad_y

    # Anchor on top edge (center) and right edge (center); gap keeps pill outside dotted line.
    w_left = origin_x + max_x_frac * used_w / 2
    w_top = origin_y + (1.0 - max_y_frac) * used_h - pill_gap_px

    h_left = origin_x + max_x_frac * used_w + pill_gap_px
    h_top = origin_y + (1.0 - max_y_frac / 2) * used_h

    return {
        "w_left": max(0.0, min(100.0, 100 * w_left / fig_width)),
        "w_top": max(0.0, min(100.0, 100 * w_top / fig_height)),
        "h_left": max(0.0, min(100.0, 100 * h_left / fig_width)),
        "h_top": max(0.0, min(100.0, 100 * h_top / fig_height)),
    }


def figure_axis_max_for_max_area(
    max_area_x: float,
    max_area_y: float,
    layout_bbox: tuple[float, float, float, float],
) -> tuple[float, float]:
    """Match build_layout_figure axis extents when show_max_area is True."""
    _, _, bw, bh = layout_bbox
    return max(bw, max_area_x), max(bh, max_area_y)


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


def _apply_figure_axes(
    fig: go.Figure,
    x_max: float,
    y_max: float,
    *,
    dark_theme: bool = False,
    game_canvas: bool = False,
    fig_width: int = FIGURE_WIDTH,
    fig_height: int = FIGURE_HEIGHT,
) -> None:
    x_upper, y_upper = _non_negative_axis_limits(
        x_max, y_max, fig_width=fig_width, fig_height=fig_height
    )
    grid_color = "rgba(255,255,255,0.04)" if dark_theme else "rgba(15,23,42,0.06)"
    line_color = "rgba(255,255,255,0.12)" if dark_theme else "rgba(15,23,42,0.18)"
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
        linecolor=line_color,
        gridcolor=grid_color,
        showgrid=dark_theme,
    )
    fig.update_yaxes(
        title_text="Y (m)",
        range=[0, y_upper],
        autorange=False,
        constrain="domain",
        zeroline=True,
        showline=True,
        linewidth=1,
        linecolor=line_color,
        gridcolor=grid_color,
        showgrid=dark_theme,
    )
    if dark_theme or game_canvas:
        font_color = "#E8EAF0" if dark_theme else "#1A1F2E"
        plot_margin = (
            dict(l=24, r=52, t=42, b=24) if game_canvas else dict(l=24, r=24, t=24, b=24)
        )
        fig.update_layout(
            template="plotly_dark" if dark_theme else "plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            autosize=True,
            height=fig_height,
            showlegend=False,
            title_text="",
            font=dict(color=font_color, family="Inter, sans-serif"),
            margin=plot_margin,
        )
        fig.update_xaxes(
            visible=False, showgrid=False, zeroline=False, showticklabels=False, title_text=""
        )
        fig.update_yaxes(
            visible=False, showgrid=False, zeroline=False, showticklabels=False, title_text=""
        )
    else:
        fig.update_layout(
            template="plotly_white",
            width=fig_width,
            height=fig_height,
            showlegend=False,
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


def _column_marker_dict(fill_color: str) -> dict:
    """High-contrast column triangle for the dark game canvas."""
    return dict(
        symbol="triangle-up",
        size=COLUMN_MARKER_SIZE,
        color=fill_color,
        opacity=1.0,
        line=dict(
            color=COLUMN_MARKER_OUTLINE,
            width=COLUMN_MARKER_OUTLINE_WIDTH,
        ),
    )


def _column_marker_trace_kwargs(fill_color: str) -> dict:
    """Marker + selection styles so columns never fade on click."""
    return {
        "marker": _column_marker_dict(fill_color),
        "unselected": {"marker": {"opacity": 1.0}},
        "selected": {"marker": {"opacity": 1.0}},
    }


def _preliminary_color(status: str) -> str:
    return {
        "PASS": PRELIMINARY_PASS_COLOR,
        "WARN": PRELIMINARY_WARN_COLOR,
        "FAIL": PRELIMINARY_FAIL_COLOR,
    }.get(status, COLUMN_ACTIVE_COLOR)


def _element_hover_footer() -> str:
    return "<br><i>Click for full report</i><extra></extra>"


def _add_layout_element_traces(
    fig: go.Figure,
    layout_elements: list[LayoutElement],
    tributary_columns: list[Column] | None,
) -> None:
    """Draw columns and beams with preliminary status colors and click ids."""
    column_legend = False
    beam_legend = False

    for element in layout_elements:
        color = _preliminary_color(element.preliminary_status)
        if element.element_type == "beam" and element.x2 is not None and element.y2 is not None:
            mid_x = (element.x + element.x2) / 2.0
            mid_y = (element.y + element.y2) / 2.0
            hover = (
                f"<b>{element.name}</b><br>"
                f"Span: {element.span_m:.2f} m<br>"
                f"From ({element.x:.2f}, {element.y:.2f}) → "
                f"({element.x2:.2f}, {element.y2:.2f})<br>"
                f"Preliminary: {element.preliminary_status}"
                + _element_hover_footer()
            )
            fig.add_trace(
                go.Scatter(
                    x=[element.x, element.x2],
                    y=[element.y, element.y2],
                    mode="lines",
                    line=dict(color=color, width=BEAM_LINE_WIDTH),
                    name="Beam",
                    legendgroup="beams",
                    showlegend=not beam_legend,
                    hoverinfo="skip",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=[mid_x],
                    y=[mid_y],
                    mode="markers",
                    marker=dict(
                        size=BEAM_HIT_MARKER_SIZE,
                        color=color,
                        symbol="circle",
                        opacity=0.35,
                        line=dict(color=COLUMN_MARKER_BORDER, width=1),
                    ),
                    name="Beam",
                    legendgroup=f"beam-hit-{element.element_id}",
                    showlegend=False,
                    customdata=[[element.element_id]],
                    hovertemplate=hover,
                )
            )
            beam_legend = True
        elif element.element_type == "column":
            fig.add_trace(
                go.Scatter(
                    x=[element.x],
                    y=[element.y],
                    mode="markers",
                    name="Column",
                    legendgroup="columns_active",
                    showlegend=not column_legend,
                    customdata=[[element.element_id]],
                    hovertemplate=(
                        f"<b>{element.name}</b><br>"
                        f"X: {element.x:.2f} m<br>"
                        f"Y: {element.y:.2f} m<br>"
                        f"Preliminary: {element.preliminary_status}"
                        + _element_hover_footer()
                    ),
                    **_column_marker_trace_kwargs(color),
                )
            )
            column_legend = True

    if tributary_columns:
        excluded_legend = False
        for column in tributary_columns:
            if not column.excluded:
                continue
            fig.add_trace(
                go.Scatter(
                    x=[column.x],
                    y=[column.y],
                    mode="markers",
                    name="Excluded column",
                    legendgroup="columns_excluded",
                    showlegend=not excluded_legend,
                    hovertemplate=(
                        f"<b>{column.column_id}</b> (excluded)<br>"
                        f"X: {column.x:.2f} m<br>"
                        f"Y: {column.y:.2f} m"
                        "<extra></extra>"
                    ),
                    **_column_marker_trace_kwargs(COLUMN_EXCLUDED_COLOR),
                )
            )
            excluded_legend = True


def build_layout_figure(
    panel: PanelSpec,
    config: LayoutConfig,
    num_pairs_per_row: int,
    num_rows: int,
    *,
    show_max_area: bool = True,
    tributary_columns: list[Column] | None = None,
    layout_elements: list[LayoutElement] | None = None,
    obstacle_zones: list[Rect] | None = None,
    title: str = "Panel layout",
    dark_theme: bool = False,
    game_canvas: bool = False,
    figure_height: int = FIGURE_HEIGHT,
) -> go.Figure:
    """Build a Plotly figure with panels, alleys, optional tributary overlay, and bbox."""
    panels = accumulate_grid(panel, config, num_pairs_per_row, num_rows)
    alleys = collect_alley_rects(panel, config, num_pairs_per_row, num_rows)
    bbox = grid_bbox(panels + alleys)

    panel_fill = DARK_PANEL_FILL if dark_theme else PANEL_FILL
    panel_line = DARK_PANEL_LINE if dark_theme else PANEL_LINE
    alley_fill = DARK_ALLEY_FILL if dark_theme else ALLEY_FILL
    alley_line = DARK_ALLEY_LINE if dark_theme else ALLEY_LINE
    spine_fill = DARK_SPINE_FILL if dark_theme else SPINE_FILL
    spine_line = DARK_SPINE_LINE if dark_theme else SPINE_LINE
    bbox_line = DARK_BBOX_LINE if dark_theme else BBOX_LINE
    max_area_line = DARK_MAX_AREA_LINE if dark_theme else MAX_AREA_LINE

    fig = go.Figure()

    for rect in panels:
        _add_rect(
            fig,
            rect,
            fillcolor=panel_fill,
            line_color=panel_line,
            legend_group="panels",
            showlegend=False,
            name="Panel",
        )

    parallel_alley_index = 0
    for rect in alleys:
        is_spine = rect[1] == 0.0 and rect[3] <= config.alley_width + 1e-9
        _add_rect(
            fig,
            rect,
            fillcolor=spine_fill if is_spine else alley_fill,
            line_color=spine_line if is_spine else alley_line,
            legend_group="spine" if is_spine else "alleys",
            showlegend=False,
            name="Edge spine" if is_spine else "Parallel alley",
        )
        if dark_theme:
            x, y, w, h = rect
            cx, cy = x + w / 2, y + h / 2
            if is_spine:
                fig.add_annotation(
                    x=cx,
                    y=cy,
                    text="SPINE ALLEY — EDGE ACCESS",
                    showarrow=False,
                    font=dict(size=10, color="#F5A623", family="Rajdhani"),
                    bgcolor="rgba(0,0,0,0)",
                )
            else:
                parallel_alley_index += 1
                fig.add_annotation(
                    x=cx,
                    y=cy,
                    text=f"A{parallel_alley_index}",
                    showarrow=False,
                    textangle=-90,
                    font=dict(size=9, color="#F5A623", family="Rajdhani"),
                    bgcolor="rgba(0,0,0,0)",
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

        if layout_elements:
            _add_layout_element_traces(fig, layout_elements, tributary_columns)
        else:
            active_legend_shown = False
            excluded_legend_shown = False
            for column in tributary_columns:
                is_excluded = column.excluded
                fig.add_trace(
                    go.Scatter(
                        x=[column.x],
                        y=[column.y],
                        mode="markers",
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
                        **_column_marker_trace_kwargs(
                            COLUMN_EXCLUDED_COLOR if is_excluded else COLUMN_ACTIVE_COLOR
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
            line_color=bbox_line,
            line_width=2,
            line_dash="dash",
            legend_group="bbox",
            showlegend=False,
            name="Layout bbox",
        )

    if show_max_area:
        max_rect = (0.0, 0.0, config.max_area_x, config.max_area_y)
        _add_rect(
            fig,
            max_rect,
            fillcolor="rgba(0,0,0,0)",
            line_color=max_area_line,
            line_width=2,
            line_dash="dot",
            legend_group="max_area",
            showlegend=False,
            name="Max area",
        )
        x_max = max(bx + bw, config.max_area_x)
        y_max = max(by + bh, config.max_area_y)
    else:
        x_max = bx + bw
        y_max = by + bh

    _apply_figure_axes(
        fig,
        x_max,
        y_max,
        dark_theme=dark_theme,
        game_canvas=game_canvas,
        fig_height=figure_height,
    )
    if title:
        fig.update_layout(title=title)
    elif dark_theme or game_canvas:
        fig.update_layout(title_text="")
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
