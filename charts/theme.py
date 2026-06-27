"""
charts/theme.py
---------------
Premium Plotly theme — navy/violet/cyan/coral enterprise design system.
"""
from __future__ import annotations
import plotly.graph_objects as go
import plotly.io as pio
import config


def register_theme() -> None:
    """Register the 'ati_theme' Plotly template globally."""
    pio.templates["ati_theme"] = go.layout.Template(
        layout=go.Layout(
            font=dict(
                family="'Inter', 'Segoe UI', 'SF Pro Display', sans-serif",
                color=config.COLORS["text_primary"],
                size=12,
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#FAFBFF",
            colorway=config.CHART_PALETTE,
            title=dict(
                font=dict(size=15, color=config.COLORS["primary"], family="'Inter', sans-serif"),
                x=0.02,
                pad=dict(t=8),
            ),
            legend=dict(
                bgcolor="rgba(255,255,255,0.92)",
                bordercolor=config.COLORS["border"],
                borderwidth=1,
                font=dict(size=11),
                itemsizing="constant",
            ),
            xaxis=dict(
                gridcolor="#EEF2FF",
                linecolor=config.COLORS["border"],
                tickfont=dict(size=11, color=config.COLORS["text_muted"]),
                title_font=dict(size=12, color=config.COLORS["text_muted"]),
                zeroline=False,
            ),
            yaxis=dict(
                gridcolor="#EEF2FF",
                linecolor=config.COLORS["border"],
                tickfont=dict(size=11, color=config.COLORS["text_muted"]),
                title_font=dict(size=12, color=config.COLORS["text_muted"]),
                zeroline=False,
            ),
            margin=dict(l=16, r=16, t=52, b=16),
            hoverlabel=dict(
                bgcolor=config.COLORS["primary"],
                font_color="#FFFFFF",
                font_size=12,
                bordercolor=config.COLORS["secondary"],
                namelength=-1,
            ),
            colorscale=dict(
                sequential=[[0, "#E8E0FF"], [0.5, "#6C3FC5"], [1, "#2D1060"]],
                diverging=[[0, "#00B4D8"], [0.5, "#FFFFFF"], [1, "#6C3FC5"]],
            ),
            modebar=dict(
                bgcolor="rgba(0,0,0,0)",
                color=config.COLORS["text_muted"],
                activecolor=config.COLORS["secondary"],
            ),
        )
    )
    pio.templates.default = "ati_theme"
