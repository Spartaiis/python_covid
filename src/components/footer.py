"""Composant pied de page (source des données)."""

from __future__ import annotations

from dash import html


def build_footer() -> html.Div:
    """Construit le pied de page mentionnant la source des données.

    Returns:
        Un conteneur avec la ligne de séparation et la mention de source.
    """
    return html.Div([
        html.Hr(),
        html.P(
            "Source : Our World in Data — COVID-19 Dataset",
            className="text-center text-muted small",
        ),
    ])
