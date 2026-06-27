"""
charts/bar_charts.py
--------------------
Premium bar chart factories with gradient fills, value labels,
and clear hover templates.
"""
from __future__ import annotations
from typing import Optional, Sequence
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import config


def horizontal_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "",
    colour: Optional[str] = None,
    top_n: int = 20,
    x_label: str = "",
    y_label: str = "",
    text_format: str = "{:,}",
    gradient: bool = False,
    height: Optional[int] = None,
) -> go.Figure:
    """Horizontal bar with value labels and optional gradient colouring."""
    plot_df = df.nlargest(top_n, x_col) if len(df) > top_n else df.copy()
    plot_df = plot_df.sort_values(x_col, ascending=True)

    if gradient:
        marker = dict(
            color=plot_df[x_col],
            colorscale=[[0, "#A78BFA"], [1, "#6C3FC5"]],
            showscale=False,
        )
    else:
        marker = dict(color=colour or config.COLORS["secondary"])

    fig = go.Figure(go.Bar(
        x=plot_df[x_col],
        y=plot_df[y_col],
        orientation="h",
        marker=marker,
        text=[text_format.format(int(v)) for v in plot_df[x_col]],
        textposition="outside",
        textfont=dict(size=11, color=config.COLORS["text_primary"]),
        cliponaxis=False,
        hovertemplate=f"<b>%{{y}}</b><br>{x_label or x_col}: %{{x:,}}<extra></extra>",
    ))
    fig.update_layout(
        title=title,
        xaxis_title=x_label, yaxis_title=y_label,
        showlegend=False,
        margin=dict(l=10, r=60, t=40 if title else 16, b=30),
        height=height,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#EEF2FF")
    return fig


def vertical_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "",
    colour: Optional[str] = None,
    top_n: int = 20,
    x_label: str = "",
    y_label: str = "",
    text_format: str = "{:,}",
    height: Optional[int] = None,
) -> go.Figure:
    """Vertical bar with value labels above each bar."""
    plot_df = df.nlargest(top_n, y_col) if len(df) > top_n else df.copy()
    plot_df = plot_df.sort_values(y_col, ascending=False)

    fig = go.Figure(go.Bar(
        x=plot_df[x_col],
        y=plot_df[y_col],
        marker=dict(color=colour or config.COLORS["primary"]),
        text=[text_format.format(int(v)) for v in plot_df[y_col]],
        textposition="outside",
        textfont=dict(size=11, color=config.COLORS["text_primary"]),
        hovertemplate=f"<b>%{{x}}</b><br>{y_label or y_col}: %{{y:,}}<extra></extra>",
    ))
    fig.update_layout(
        title=title, xaxis_title=x_label, yaxis_title=y_label,
        showlegend=False,
        margin=dict(l=10, r=10, t=40 if title else 16, b=30),
        height=height,
    )
    fig.update_yaxes(showgrid=True, gridcolor="#EEF2FF")
    return fig


def grouped_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str,
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    barmode: str = "group",
    palette: Optional[Sequence[str]] = None,
    height: Optional[int] = None,
) -> go.Figure:
    """Grouped / stacked multi-series bar chart."""
    fig = px.bar(
        df, x=x_col, y=y_col, color=color_col,
        barmode=barmode, title=title,
        color_discrete_sequence=palette or config.CHART_PALETTE,
        labels={x_col: x_label or x_col, y_col: y_label or y_col, color_col: ""},
    )
    fig.update_layout(
        margin=dict(t=40 if title else 16, l=10, r=10, b=30),
        legend=dict(orientation="h", y=-0.18, x=0),
        height=height,
    )
    fig.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:,}<extra></extra>")
    return fig


def diverging_bar(
    df: pd.DataFrame,
    label_col: str,
    value_col: str,
    title: str = "",
    height: Optional[int] = None,
) -> go.Figure:
    """Bar chart where positive values are green-violet and negative are blue."""
    plot_df = df.sort_values(value_col, ascending=True)
    colours = [
        config.COLORS["accent"] if v > 50 else
        config.COLORS["warning"] if v > 0 else
        config.COLORS["info"]
        for v in plot_df[value_col]
    ]
    fig = go.Figure(go.Bar(
        x=plot_df[value_col], y=plot_df[label_col],
        orientation="h", marker=dict(color=colours),
        text=[f"{v:+.0f}%" for v in plot_df[value_col]],
        textposition="outside",
        textfont=dict(size=11, color=config.COLORS["text_primary"]),
        cliponaxis=False,
        hovertemplate=f"<b>%{{y}}</b><br>Change: %{{x:+.1f}}%<extra></extra>",
    ))
    fig.update_layout(
        title=title, showlegend=False,
        margin=dict(l=10, r=60, t=40 if title else 16, b=30),
        xaxis_title="Change (%)", yaxis_title="",
        height=height,
    )
    return fig
