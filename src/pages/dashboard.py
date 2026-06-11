"""Page principale du dashboard : layout, figures et callbacks.

Cette page assemble les composants réutilisables et définit les deux callbacks
qui rendent l'interface dynamique :

* :func:`update_kpis` — met à jour les cartes KPI selon la période ;
* :func:`render_tab` — rend l'onglet actif (séries, carte, histogramme, table).

Pour **ajouter un graphique**, il suffit d'écrire une fonction ``build_*`` et de
l'appeler dans une nouvelle branche de :func:`render_tab` (et d'ajouter l'onglet
correspondant dans :func:`build_tabs`).
"""

from __future__ import annotations

import warnings

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dash_table, dcc, html

# La carte utilise locationmode="country names", parfaitement adapté aux noms
# de pays du jeu OWID. Plotly émet un DeprecationWarning annonçant un futur
# changement : on le neutralise pour garder la console propre (exigence de la
# consigne), le rendu actuel restant correct.
warnings.filterwarnings(
    "ignore", message=".*locationmode.*", category=DeprecationWarning
)
# dash_table.DataTable est marqué déprécié dans Dash 4 mais reste pleinement
# fonctionnel ; on neutralise l'avertissement pour ne rien afficher en console.
warnings.filterwarnings(
    "ignore", message="(?s).*DataTable.*", category=DeprecationWarning
)

import config
from src.components.controls import build_controls
from src.components.footer import build_footer
from src.components.header import build_header
from src.components.kpi import make_kpi_card
from src.utils.common_functions import (
    get_snapshot,
    load_cleaned,
    split_world_countries,
)


# --------------------------------------------------------------------------- #
# Construction du layout
# --------------------------------------------------------------------------- #


def build_tabs() -> dbc.Tabs:
    """Construit la barre d'onglets du dashboard.

    Returns:
        Le composant ``dbc.Tabs`` listant les quatre vues.
    """
    return dbc.Tabs([
        dbc.Tab(label="📈 Séries temporelles", tab_id="tab-ts"),
        dbc.Tab(label="🗺️ Carte mondiale", tab_id="tab-map"),
        dbc.Tab(label="📊 Histogramme", tab_id="tab-hist"),
        dbc.Tab(label="📋 Données", tab_id="tab-data"),
    ], id="tabs", active_tab="tab-ts", className="mb-3")


def build_layout() -> dbc.Container:
    """Assemble le layout complet de la page.

    Lit les données (mises en cache) pour alimenter les contrôles, puis
    empile en-tête, KPI, contrôles, onglets et pied de page.

    Returns:
        Le conteneur racine de l'application.
    """
    data = load_cleaned()
    countries_df, _ = split_world_countries(data)
    countries = sorted(countries_df["country"].unique())
    date_min, date_max = countries_df["date"].min(), countries_df["date"].max()

    return dbc.Container([
        build_header(),
        dbc.Row(id="kpi-row", className="mb-4 g-3"),
        build_controls(countries, date_min, date_max),
        build_tabs(),
        html.Div(id="tab-content"),
        build_footer(),
    ], fluid=True)


# --------------------------------------------------------------------------- #
# Constructeurs de figures
# --------------------------------------------------------------------------- #


def build_timeseries(dff: pd.DataFrame, selected: list[str]) -> dbc.Container:
    """Construit les deux séries temporelles pour les pays sélectionnés.

    Args:
        dff: Données filtrées sur la période.
        selected: Liste des pays à tracer.

    Returns:
        Un conteneur avec les deux courbes côte à côte.
    """
    dff_sel = dff[dff["country"].isin(selected)]
    fig_new = px.line(
        dff_sel, x="date", y="new_cases_per_million", color="country",
        labels={"new_cases_per_million": "Cas / million", "date": "",
                "country": "Pays"},
        title="Nouveaux cas par million", template=config.DARK_TEMPLATE,
    )
    fig_cum = px.line(
        dff_sel, x="date", y="total_cases_per_million", color="country",
        labels={"total_cases_per_million": "Cas cumulés / million",
                "date": "", "country": "Pays"},
        title="Cas cumulés par million", template=config.DARK_TEMPLATE,
    )
    return dbc.Container(dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_new), md=6),
        dbc.Col(dcc.Graph(figure=fig_cum), md=6),
    ]))


def build_choropleth(snap: pd.DataFrame, metric: str) -> go.Figure:
    """Construit la carte choroplèthe d'un indicateur.

    Args:
        snap: Une ligne par pays (dernière date de la période).
        metric: Colonne numérique à représenter.

    Returns:
        La figure Plotly de la carte.
    """
    label = config.METRICS.get(metric, metric)
    fig = px.choropleth(
        snap, locations="country", locationmode="country names",
        color=metric, hover_name="country",
        hover_data=["total_cases", "total_deaths"],
        color_continuous_scale="YlOrRd", labels={metric: label},
        title=f"{label} (dernière date de la période)",
        template=config.DARK_TEMPLATE,
    )
    fig.update_layout(geo=dict(bgcolor="rgba(0,0,0,0)"))
    return fig


def build_histogram(snap: pd.DataFrame, metric: str) -> go.Figure:
    """Construit l'histogramme de la distribution d'un indicateur entre pays.

    Args:
        snap: Une ligne par pays (dernière date de la période).
        metric: Colonne numérique à représenter.

    Returns:
        La figure Plotly de l'histogramme.
    """
    label = config.METRICS.get(metric, metric)
    fig = px.histogram(
        snap, x=metric, nbins=40, labels={metric: label},
        title=f"Distribution de « {label} » entre pays",
        template=config.DARK_TEMPLATE,
    )
    fig.update_layout(yaxis_title="Nombre de pays", bargap=0.05)
    return fig


def build_table(snap: pd.DataFrame) -> dash_table.DataTable:
    """Construit le tableau triable des dernières valeurs par pays.

    Args:
        snap: Une ligne par pays (dernière date de la période).

    Returns:
        Le composant ``DataTable``.
    """
    cols = ["country", "date", "total_cases", "total_deaths",
            "total_cases_per_million", "total_deaths_per_million"]
    snap_d = snap[cols].copy()
    snap_d["date"] = snap_d["date"].dt.strftime("%Y-%m-%d")
    for col in cols[2:]:
        snap_d[col] = snap_d[col].round(2)
    return dash_table.DataTable(
        data=snap_d.to_dict("records"),
        columns=[{"name": c, "id": c} for c in cols],
        page_size=20, sort_action="native",
        style_table={"overflowX": "auto"},
        style_header={"backgroundColor": "#303030", "color": "white",
                      "fontWeight": "bold"},
        style_cell={"backgroundColor": "#222", "color": "white",
                    "border": "1px solid #444", "textAlign": "left",
                    "padding": "8px"},
    )


# --------------------------------------------------------------------------- #
# Callbacks
# --------------------------------------------------------------------------- #

_NO_DATA = dbc.Alert("Aucune donnée sur la période choisie.", color="warning")


@callback(Output("kpi-row", "children"), Input("date-range", "end_date"))
def update_kpis(end_date: str | None) -> list:
    """Met à jour les cartes KPI selon la date de fin sélectionnée.

    Args:
        end_date: Date de fin (chaîne ISO fournie par le DatePickerRange).

    Returns:
        La liste des colonnes contenant les cartes KPI, ou une liste vide.
    """
    if end_date is None:
        return []
    _, world = split_world_countries(load_cleaned())
    # Conversion explicite str -> Timestamp pour comparer à une colonne datetime.
    end = pd.to_datetime(end_date)
    filtered = world[world["date"] <= end].sort_values("date")
    if filtered.empty:
        return []
    row = filtered.iloc[-1]
    n_countries = load_cleaned()["country"].nunique()
    return [
        dbc.Col(make_kpi_card("Total cas",
                              f"{row['total_cases']:,.0f}", "info"), md=4),
        dbc.Col(make_kpi_card("Total décès",
                              f"{row['total_deaths']:,.0f}", "danger"), md=4),
        dbc.Col(make_kpi_card("Pays suivis",
                              f"{n_countries}", "success"), md=4),
    ]


@callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab"),
    Input("country-select", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("metric-select", "value"),
)
def render_tab(
    active_tab: str,
    selected: list[str] | None,
    start: str | None,
    end: str | None,
    metric: str,
) -> object:
    """Rend le contenu de l'onglet actif en fonction des filtres.

    Args:
        active_tab: Identifiant de l'onglet sélectionné.
        selected: Pays choisis (séries temporelles).
        start: Date de début de la période (chaîne ISO).
        end: Date de fin de la période (chaîne ISO).
        metric: Colonne numérique à représenter (carte & histogramme).

    Returns:
        Un composant Dash correspondant à l'onglet demandé.
    """
    selected = selected or []
    countries_df, _ = split_world_countries(load_cleaned())

    # Conversion explicite des bornes en Timestamp pour un filtrage fiable.
    start_ts = pd.to_datetime(start) if start else countries_df["date"].min()
    end_ts = pd.to_datetime(end) if end else countries_df["date"].max()
    dff = countries_df[(countries_df["date"] >= start_ts)
                       & (countries_df["date"] <= end_ts)]

    if active_tab == "tab-ts":
        if not selected:
            return dbc.Alert("Veuillez sélectionner au moins un pays.",
                             color="info")
        return build_timeseries(dff, selected)

    if active_tab == "tab-map":
        snap = get_snapshot(dff)
        if snap.empty:
            return _NO_DATA
        return dbc.Container(dbc.Row(dbc.Col(
            dcc.Graph(figure=build_choropleth(snap, metric)))))

    if active_tab == "tab-hist":
        snap = get_snapshot(dff)
        if snap.empty:
            return _NO_DATA
        return dbc.Container(dbc.Row(dbc.Col(
            dcc.Graph(figure=build_histogram(snap, metric)))))

    if active_tab == "tab-data":
        snap = get_snapshot(dff)
        if snap.empty:
            return _NO_DATA
        return dbc.Container([
            html.H5("Données par pays (dernière date)", className="mb-3"),
            build_table(snap),
        ])

    return html.P("Sélectionnez un onglet.")
