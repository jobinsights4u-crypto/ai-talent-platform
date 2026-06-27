"""
charts/misc_charts.py
---------------------
Pie/donut, treemap, line, box, scatter, histogram, heatmap factories
with enhanced labels and hover info.
"""
from __future__ import annotations
from typing import Optional, Sequence
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import config


def donut_chart(
    labels: Sequence[str],
    values: Sequence[float],
    title: str = "",
    hole: float = 0.55,
    colours: Optional[Sequence[str]] = None,
    height: Optional[int] = None,
    show_total: bool = True,
) -> go.Figure:
    """Donut chart with total in the center."""
    total = sum(values)
    fig = go.Figure(go.Pie(
        labels=list(labels), values=list(values),
        hole=hole,
        marker=dict(
            colors=list(colours or config.CHART_PALETTE),
            line=dict(color="white", width=2),
        ),
        textinfo="percent",
        textfont=dict(size=12, color="white"),
        insidetextorientation="auto",
        hovertemplate="<b>%{label}</b><br>%{value:,} (%{percent})<extra></extra>",
        sort=False,
    ))
    if show_total:
        fig.update_layout(annotations=[dict(
            text=f"<b>{int(total):,}</b><br><span style='font-size:11px;color:#64748B'>Total</span>",
            x=0.5, y=0.5, font=dict(size=20, color=config.COLORS["primary"]),
            showarrow=False,
        )])
    fig.update_layout(
        title=title, showlegend=True,
        legend=dict(orientation="v", y=0.5, x=1.05, font=dict(size=11)),
        margin=dict(t=40 if title else 12, b=12, l=12, r=12),
        height=height,
    )
    return fig


def line_chart(
    df: pd.DataFrame,
    x_col: str, y_col: str,
    title: str = "",
    color_col: Optional[str] = None,
    x_label: str = "", y_label: str = "",
    markers: bool = True,
    smooth: bool = True,
    height: Optional[int] = None,
) -> go.Figure:
    """Line chart with smooth curves and clear markers."""
    fig = px.line(
        df, x=x_col, y=y_col, color=color_col, title=title,
        markers=markers,
        color_discrete_sequence=config.CHART_PALETTE,
        labels={x_col: x_label or x_col, y_col: y_label or y_col, color_col or "": ""},
    )
    if smooth:
        fig.update_traces(line=dict(shape="spline", smoothing=0.6, width=2.5),
                          marker=dict(size=6, line=dict(width=2, color="white")))
    fig.update_layout(
        margin=dict(t=40 if title else 16, l=10, r=10, b=30),
        legend=dict(orientation="h", y=-0.18, x=0),
        hovermode="x unified",
        height=height,
    )
    return fig


def box_plot(
    df: pd.DataFrame,
    x_col: str, y_col: str,
    title: str = "",
    color_col: Optional[str] = None,
    log_y: bool = False,
    height: Optional[int] = None,
) -> go.Figure:
    """Box plot with point overlay."""
    fig = px.box(
        df, x=x_col, y=y_col, color=color_col or x_col, title=title,
        color_discrete_sequence=config.CHART_PALETTE,
        log_y=log_y, points="outliers",
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(t=40 if title else 16, l=10, r=10, b=30),
        height=height,
    )
    fig.update_xaxes(tickangle=-30)
    return fig


def treemap_chart(
    df: pd.DataFrame,
    path_cols: Sequence[str],
    value_col: str,
    title: str = "",
    height: Optional[int] = None,
) -> go.Figure:
    """Hierarchical treemap."""
    fig = px.treemap(
        df, path=[px.Constant("All")] + list(path_cols),
        values=value_col,
        color=value_col,
        color_continuous_scale=["#E8E0FF", "#6C3FC5", "#2D1060"],
        title=title,
    )
    fig.update_traces(
        textinfo="label+value+percent parent",
        textfont=dict(size=12, color="white"),
        hovertemplate="<b>%{label}</b><br>Jobs: %{value:,}<br>%{percentParent:.1%} of parent<extra></extra>",
    )
    fig.update_layout(
        margin=dict(t=40 if title else 16, l=10, r=10, b=10),
        coloraxis_colorbar=dict(title=dict(text="Jobs"), thickness=12),
        height=height,
    )
    return fig


def histogram_chart(
    df: pd.DataFrame,
    x_col: str,
    title: str = "",
    nbins: int = 40,
    color_col: Optional[str] = None,
    log_x: bool = False,
    height: Optional[int] = None,
) -> go.Figure:
    """Distribution histogram."""
    fig = px.histogram(
        df, x=x_col, nbins=nbins, color=color_col, title=title,
        color_discrete_sequence=[config.COLORS["secondary"]],
        log_x=log_x, opacity=0.88,
    )
    fig.update_layout(
        bargap=0.04, showlegend=color_col is not None,
        margin=dict(t=40 if title else 16, l=10, r=10, b=30),
        height=height,
    )
    fig.update_traces(hovertemplate="Range: %{x}<br>Count: %{y:,}<extra></extra>")
    return fig


def heatmap_chart(
    pivot: pd.DataFrame,
    title: str = "",
    x_label: str = "", y_label: str = "",
    colorscale: str = "Purples",
    text_auto: bool = True,
    height: Optional[int] = None,
) -> go.Figure:
    """Heatmap from a pivot DataFrame."""
    fig = px.imshow(
        pivot, title=title,
        color_continuous_scale=colorscale,
        text_auto=".0f" if text_auto else False,
        labels=dict(x=x_label, y=y_label, color="Jobs"),
        aspect="auto",
    )
    fig.update_layout(
        margin=dict(t=40 if title else 16, l=10, r=10, b=30),
        coloraxis_colorbar=dict(title=dict(text="Jobs"), thickness=12),
        height=height,
    )
    fig.update_traces(hovertemplate="%{y} × %{x}<br>Jobs: %{z:,}<extra></extra>")
    fig.update_xaxes(tickangle=-35)
    return fig


def scatter_chart(
    df: pd.DataFrame,
    x_col: str, y_col: str,
    title: str = "",
    color_col: Optional[str] = None,
    size_col: Optional[str] = None,
    hover_col: Optional[str] = None,
    log_x: bool = False, log_y: bool = False,
    height: Optional[int] = None,
) -> go.Figure:
    """Scatter plot."""
    fig = px.scatter(
        df, x=x_col, y=y_col, color=color_col, size=size_col,
        hover_name=hover_col, title=title,
        color_discrete_sequence=config.CHART_PALETTE,
        log_x=log_x, log_y=log_y, opacity=0.78,
    )
    fig.update_layout(
        margin=dict(t=40 if title else 16, l=10, r=10, b=30),
        height=height,
    )
    return fig
