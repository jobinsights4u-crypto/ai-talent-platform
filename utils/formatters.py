"""
utils/formatters.py
-------------------
Pure formatting functions — no Streamlit or Plotly imports.
"""

from __future__ import annotations

import math


def fmt_number(value: float | int, decimals: int = 0) -> str:
    """Format a number with thousand separators."""
    if math.isnan(value):
        return "N/A"
    return f"{value:,.{decimals}f}"


def fmt_currency(value: float, currency: str = "USD", decimals: int = 0) -> str:
    """Format a value as a currency string."""
    symbols = {
        "USD": "$", "GBP": "£", "EUR": "€", "INR": "₹",
        "JPY": "¥", "CNY": "¥", "BRL": "R$",
    }
    sym = symbols.get(currency.upper(), f"{currency} ")
    return f"{sym}{value:,.{decimals}f}"


def fmt_k(value: float) -> str:
    """Format large numbers with K / M suffixes."""
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(int(value))


def fmt_pct(value: float, decimals: int = 1) -> str:
    """Format a fraction (0–1) as a percentage string."""
    return f"{value * 100:.{decimals}f}%"


def fmt_delta(current: float, previous: float) -> str:
    """Return a delta string like '+12.3%' or '-4.5%'."""
    if previous == 0:
        return "N/A"
    pct = (current - previous) / previous * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"


def truncate(text: str, max_len: int = 60) -> str:
    """Truncate a string with an ellipsis."""
    return text if len(text) <= max_len else text[: max_len - 1] + "…"
