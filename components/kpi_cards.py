"""
components/kpi_cards.py
-----------------------
Reusable KPI / metric card components rendered with Streamlit columns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import streamlit as st

from utils.formatters import fmt_k


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class KPICard:
    """Data model for a single KPI metric card."""
    label: str
    value: str | int | float
    icon: str = "📊"
    delta: Optional[str] = None
    delta_colour: str = "normal"   # "normal" | "inverse" | "off"
    help_text: Optional[str] = None
    format_fn: Optional[callable] = None

    def display_value(self) -> str:
        if self.format_fn:
            return self.format_fn(self.value)
        if isinstance(self.value, (int, float)):
            return fmt_k(self.value)
        return str(self.value)


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------

def render_kpi_row(cards: list[KPICard], cols: Optional[int] = None) -> None:
    """
    Render a horizontal row of KPI cards.

    Parameters
    ----------
    cards : list[KPICard]
        Cards to display.
    cols : int, optional
        Number of columns. Defaults to ``len(cards)``.
    """
    n = cols or len(cards)
    columns = st.columns(n)
    for i, card in enumerate(cards):
        with columns[i % n]:
            _render_single(card)


def _render_single(card: KPICard) -> None:
    """Render one KPI card using Streamlit metric."""
    st.metric(
        label=f"{card.icon}  {card.label}",
        value=card.display_value(),
        delta=card.delta,
        delta_color=card.delta_colour,
        help=card.help_text,
    )


def render_kpi_grid(cards: list[KPICard], cols_per_row: int = 4) -> None:
    """
    Render cards in a grid layout, wrapping after ``cols_per_row`` columns.

    Parameters
    ----------
    cards : list[KPICard]
        All KPI cards to display.
    cols_per_row : int
        Maximum columns per row.
    """
    for start in range(0, len(cards), cols_per_row):
        chunk = cards[start: start + cols_per_row]
        cols = st.columns(len(chunk))
        for col, card in zip(cols, chunk):
            with col:
                _render_single(card)
