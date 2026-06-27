"""charts/map_charts.py — Choropleth and geo charts."""
from __future__ import annotations
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import config


def choropleth_jobs(
    df: pd.DataFrame, value_col: str = "Job Count",
    title: str = "", height: int | None = None,
) -> go.Figure:
    plot_df = df.copy()
    plot_df["ISO3"] = plot_df[config.COL_COUNTRY].map(config.COUNTRY_ISO3)
    plot_df = plot_df.dropna(subset=["ISO3"])

    fig = px.choropleth(
        plot_df, locations="ISO3", color=value_col,
        hover_name=config.COL_COUNTRY,
        color_continuous_scale=["#E8E0FF", "#A78BFA", "#6C3FC5", "#2D1060"],
        title=title, projection="natural earth",
    )
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" + value_col + ": %{z:,}<extra></extra>",
        marker=dict(line=dict(color="white", width=0.5)),
    )
    fig.update_geos(
        showcoastlines=True, coastlinecolor="#CBD5E1",
        showland=True, landcolor="#F8FAFC",
        showocean=True, oceancolor="#EFF6FF",
        showframe=False, showcountries=True, countrycolor="#E2E8F0",
    )
    fig.update_layout(
        coloraxis_colorbar=dict(title=dict(text=value_col), thickness=12, tickformat=","),
        margin=dict(l=0, r=0, t=40 if title else 0, b=0),
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        height=height,
    )
    return fig
