"""Création et configuration de l'application Dash.

Le module ``src.pages.dashboard`` est importé pour enregistrer ses callbacks
(via le décorateur ``@callback``) ; :func:`create_app` instancie ensuite
l'application et lui attache le layout.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import Dash

from src.pages import dashboard as dashboard_page


def create_app() -> Dash:
    """Instancie l'application Dash, son thème et son layout.

    Returns:
        L'instance ``Dash`` prête à être lancée.
    """
    app = Dash(
        __name__,
        external_stylesheets=[dbc.themes.DARKLY],
        title="COVID-19 Dashboard",
    )
    app.layout = dashboard_page.build_layout()
    return app
