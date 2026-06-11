"""Composant des contrôles interactifs (pays, période, indicateur)."""

from __future__ import annotations

import datetime as dt

import dash_bootstrap_components as dbc
from dash import dcc, html

import config


def build_controls(
    countries: list[str],
    date_min: dt.date | dt.datetime,
    date_max: dt.date | dt.datetime,
) -> html.Div:
    """Construit la zone de contrôles du dashboard.

    Args:
        countries: Liste triée des pays sélectionnables.
        date_min: Borne basse autorisée pour la période.
        date_max: Borne haute autorisée pour la période.

    Returns:
        Un conteneur regroupant les sélecteurs de pays, de période et
        d'indicateur.
    """
    country_period = dbc.Row([
        dbc.Col([
            html.Label("Pays sélectionnés", className="fw-bold"),
            dcc.Dropdown(
                id="country-select",
                options=[{"label": c, "value": c} for c in countries],
                value=config.DEFAULT_COUNTRIES,
                multi=True, placeholder="Choisir un ou plusieurs pays…",
            ),
        ], md=6),
        dbc.Col([
            html.Label("Période", className="fw-bold"),
            dcc.DatePickerRange(
                id="date-range",
                min_date_allowed=date_min, max_date_allowed=date_max,
                start_date=date_min, end_date=date_max,
                display_format="DD/MM/YYYY",
            ),
        ], md=6),
    ], className="mb-4")

    metric = dbc.Row(dbc.Col([
        html.Label("Indicateur (carte & histogramme)", className="fw-bold"),
        dcc.Dropdown(
            id="metric-select",
            options=[{"label": lbl, "value": col}
                     for col, lbl in config.METRICS.items()],
            value="total_cases_per_million", clearable=False,
        ),
    ], md=6), className="mb-4")

    return html.Div([country_period, metric])
