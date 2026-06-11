"""Composant carte d'indicateur clé (KPI)."""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html


def make_kpi_card(title: str, value: str, color: str = "primary") -> dbc.Card:
    """Construit une carte d'indicateur clé (KPI).

    Args:
        title: Intitulé de l'indicateur.
        value: Valeur déjà formatée à afficher.
        color: Couleur Bootstrap du texte de la valeur (``info``, ``danger``…).

    Returns:
        Un composant ``dbc.Card`` prêt à insérer dans une colonne.
    """
    return dbc.Card(dbc.CardBody([
        html.H6(title, className="card-title text-muted mb-1"),
        html.H3(value, className=f"text-{color} mb-0"),
    ]), className="shadow-sm")
