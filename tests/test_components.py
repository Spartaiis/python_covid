"""Tests des composants d'interface et des constructeurs de figures."""

from __future__ import annotations

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

import config
from src.components.header import build_header
from src.components.kpi import make_kpi_card
from src.pages.dashboard import build_histogram, build_choropleth


def _snapshot() -> pd.DataFrame:
    """Snapshot synthétique d'un pays par ligne."""
    return pd.DataFrame({
        "country": ["France", "Germany", "Brazil"],
        "total_cases": [100, 200, 300],
        "total_deaths": [1, 2, 3],
        "total_cases_per_million": [10.0, 20.0, 30.0],
    })


def test_make_kpi_card_returns_card() -> None:
    """make_kpi_card renvoie une carte Bootstrap."""
    card = make_kpi_card("Titre", "42", "info")
    assert isinstance(card, dbc.Card)


def test_build_header_returns_row() -> None:
    """build_header renvoie une ligne Bootstrap."""
    assert isinstance(build_header(), dbc.Row)


def test_build_histogram_is_figure() -> None:
    """build_histogram produit une figure Plotly valide."""
    fig = build_histogram(_snapshot(), "total_cases_per_million")
    assert isinstance(fig, go.Figure)


def test_build_choropleth_is_figure() -> None:
    """build_choropleth produit une figure Plotly valide."""
    fig = build_choropleth(_snapshot(), "total_cases_per_million")
    assert isinstance(fig, go.Figure)
    # L'indicateur est bien un libellé connu de la configuration.
    assert "total_cases_per_million" in config.METRICS
