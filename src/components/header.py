"""Composant en-tête (titre + ligne de KPI)."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html


def build_header() -> dbc.Row:
    """Construit le titre principal du dashboard.

    Returns:
        Une ligne Bootstrap contenant le titre.
    """
    return dbc.Row(dbc.Col(html.H1(
        "COVID-19 — Dashboard Mondial", className="text-center my-4"
    )))
