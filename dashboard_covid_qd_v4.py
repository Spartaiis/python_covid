"""
Version 4 — Dashboard complet (tous les onglets, rendu simplifié)
Objectif : intégrer tous les onglets de la version finale, sans encore
           le mode hebdo/7j, ni la courbe normalisée depuis le 100e cas.
           Le scatter et le classement sont également en version basique.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dash import Dash, dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc

pio.templates["plotly_dark"].data.scatter = [go.Scatter(marker=dict())]

# ── Chargement et nettoyage ───────────────────────────────────────────────────

df = pd.read_csv("cases_deaths.csv", parse_dates=["date"])

REGIONS = [
    "Africa", "Asia", "Asia excl. China", "Europe", "European Union (27)",
    "High-income countries", "Low-income countries", "Lower-middle-income countries",
    "North America", "Oceania", "South America", "Upper-middle-income countries",
    "World", "World excl. China", "World excl. China and South Korea",
    "World excl. China, South Korea, Japan and Singapore",
    "American Samoa", "Guam", "Northern Mariana Islands", "Puerto Rico",
    "United States Virgin Islands",
    "Anguilla", "Bermuda", "British Virgin Islands", "Cayman Islands",
    "Falkland Islands", "Gibraltar", "Montserrat", "Pitcairn",
    "Saint Helena", "Turks and Caicos Islands",
    "Guernsey", "Isle of Man", "Jersey",
    "French Guiana", "French Polynesia", "Guadeloupe", "Martinique",
    "Mayotte", "New Caledonia", "Reunion", "Saint Barthelemy",
    "Saint Martin (French part)", "Saint Pierre and Miquelon", "Wallis and Futuna",
    "Aruba", "Bonaire Sint Eustatius and Saba", "Curacao", "Sint Maarten (Dutch part)",
    "Cook Islands", "Faroe Islands", "Greenland", "Kosovo", "Niue",
    "Palestine", "Tokelau",
]

df = df.sort_values(["country", "date"]).reset_index(drop=True)
numeric_cols = df.select_dtypes(include="number").columns
df[numeric_cols] = df[numeric_cols].fillna(0)

df_country = df[~df["country"].isin(REGIONS)].copy()
df_world = df[df["country"] == "World"].copy()

countries = sorted(df_country["country"].unique())
date_min, date_max = df_country["date"].min(), df_country["date"].max()

DARK_TEMPLATE = "plotly_dark"


def get_snapshot(dff):
    last = dff.groupby("country")["date"].max().reset_index(name="last_date")
    snap = dff.merge(last, on="country")
    return snap[snap["date"] == snap["last_date"]].drop(columns="last_date")


# ── App Dash ──────────────────────────────────────────────────────────────────

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "COVID-19 Dashboard"


def make_kpi_card(title, value, color="primary"):
    return dbc.Card(dbc.CardBody([
        html.H6(title, className="card-title text-muted mb-1"),
        html.H3(value, className=f"text-{color} mb-0"),
    ]), className="shadow-sm")


# ── Layout ────────────────────────────────────────────────────────────────────

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("🦠 COVID-19 — Dashboard Mondial", className="text-center my-4"))),
    dbc.Row(id="kpi-row", className="mb-4 g-3"),

    dbc.Row([
        dbc.Col([
            html.Label("Pays sélectionnés", className="fw-bold"),
            dcc.Dropdown(
                id="country-select",
                options=[{"label": c, "value": c} for c in countries],
                value=["France", "Germany", "United States", "Brazil", "India"],
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
    ], className="mb-4"),

    dbc.Tabs([
        dbc.Tab(label=" Séries temporelles", tab_id="tab-ts"),
        dbc.Tab(label=" Carte mondiale",     tab_id="tab-map"),
        dbc.Tab(label=" Classements",         tab_id="tab-rank"),
        dbc.Tab(label=" Comparaison",         tab_id="tab-compare"),
        dbc.Tab(label=" Scatter",             tab_id="tab-scatter"),
        dbc.Tab(label=" Données",             tab_id="tab-data"),
    ], id="tabs", active_tab="tab-ts", className="mb-3"),
    dcc.Loading(
        id="loading", type="dot",
        children=html.Div(id="tab-content"),
        color="#0dcaf0",
    ),
    html.Hr(),
    html.P("Source : Our World in Data — COVID-19 Dataset",
           className="text-center text-muted small"),
], fluid=True)


# ── Callbacks ─────────────────────────────────────────────────────────────────

@callback(Output("kpi-row", "children"), Input("date-range", "end_date"))
def update_kpis(end_date):
    filtered = df_world[df_world["date"] <= end_date].sort_values("date")
    if filtered.empty:
        return [dbc.Col(make_kpi_card("Données", "Aucune", "secondary"), md=12)]
    w = filtered.iloc[-1]
    return [
        dbc.Col(make_kpi_card("Total cas",   f"{w['total_cases']:,.0f}",  "info"),    md=4),
        dbc.Col(make_kpi_card("Total décès", f"{w['total_deaths']:,.0f}", "danger"),  md=4),
        dbc.Col(make_kpi_card("Pays suivis", f"{len(countries)}",         "success"), md=4),
    ]


@callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab"),
    Input("country-select", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def render_tab(active_tab, selected, start, end):
    selected = selected or []
    dff = df_country[(df_country["date"] >= start) & (df_country["date"] <= end)]
    if active_tab == "tab-ts":
        return _render_timeseries(dff, selected)
    if active_tab == "tab-map":
        return _render_map(dff)
    if active_tab == "tab-rank":
        return _render_rankings(dff)
    if active_tab == "tab-compare":
        return _render_compare(dff, selected)
    if active_tab == "tab-scatter":
        return _render_scatter(dff)
    if active_tab == "tab-data":
        return _render_data_table(dff)
    return html.P("Sélectionnez un onglet.")


# ── Tab renderers ─────────────────────────────────────────────────────────────

def _render_timeseries(dff, selected):
    if not selected:
        return dbc.Alert("Veuillez sélectionner au moins un pays.", color="info")
    dff_sel = dff[dff["country"].isin(selected)]

    fig1 = px.line(dff_sel, x="date", y="new_cases_per_million", color="country",
                   render_mode="svg",
                   labels={"new_cases_per_million": "Cas / million", "date": "", "country": "Pays"},
                   title="Nouveaux cas par million", template=DARK_TEMPLATE)
    fig2 = px.line(dff_sel, x="date", y="new_deaths_per_million", color="country",
                   render_mode="svg",
                   labels={"new_deaths_per_million": "Décès / million", "date": "", "country": "Pays"},
                   title="Nouveaux décès par million", template=DARK_TEMPLATE)
    fig3 = px.line(dff_sel, x="date", y="total_cases_per_million", color="country",
                   render_mode="svg",
                   labels={"total_cases_per_million": "Cas cumulés / million", "date": "", "country": "Pays"},
                   title="Cas cumulés par million", template=DARK_TEMPLATE)
    fig4 = px.line(dff_sel, x="date", y="cfr", color="country",
                   render_mode="svg",
                   labels={"cfr": "CFR (%)", "date": "", "country": "Pays"},
                   title="Taux de létalité (CFR)", template=DARK_TEMPLATE)
    return dbc.Container([
        dbc.Row([dbc.Col(dcc.Graph(figure=fig1), md=6), dbc.Col(dcc.Graph(figure=fig2), md=6)]),
        dbc.Row([dbc.Col(dcc.Graph(figure=fig3), md=6), dbc.Col(dcc.Graph(figure=fig4), md=6)]),
    ])


def _render_map(dff):
    snap = get_snapshot(dff)
    fig1 = px.choropleth(snap, locations="country", locationmode="country names",
                         color="total_cases_per_million", hover_name="country",
                         hover_data=["total_cases", "total_deaths", "cfr"],
                         color_continuous_scale="YlOrRd",
                         title="Total cas par million", template=DARK_TEMPLATE)
    fig1.update_layout(geo=dict(bgcolor="rgba(0,0,0,0)"))
    fig2 = px.choropleth(snap, locations="country", locationmode="country names",
                         color="total_deaths_per_million", hover_name="country",
                         hover_data=["total_deaths", "total_cases", "cfr"],
                         color_continuous_scale="Reds",
                         title="Total décès par million", template=DARK_TEMPLATE)
    fig2.update_layout(geo=dict(bgcolor="rgba(0,0,0,0)"))
    return dbc.Container([
        dbc.Row(dbc.Col(dcc.Graph(figure=fig1))),
        dbc.Row(dbc.Col(dcc.Graph(figure=fig2)), className="mt-3"),
    ])


def _render_rankings(dff):
    snap = get_snapshot(dff)

    top_c = snap.nlargest(20, "total_cases_per_million")
    fig1 = px.bar(top_c, x="total_cases_per_million", y="country", orientation="h",
                  color="total_deaths_per_million", color_continuous_scale="Blues",
                  labels={"total_cases_per_million": "Cas / million", "country": ""},
                  title="Top 20 — Cas par million", template=DARK_TEMPLATE)
    fig1.update_layout(yaxis=dict(autorange="reversed"))

    top_d = snap.nlargest(20, "total_deaths_per_million")
    fig2 = px.bar(top_d, x="total_deaths_per_million", y="country", orientation="h",
                  color="total_cases_per_million", color_continuous_scale="Reds",
                  labels={"total_deaths_per_million": "Décès / million", "country": ""},
                  title="Top 20 — Décès par million", template=DARK_TEMPLATE)
    fig2.update_layout(yaxis=dict(autorange="reversed"))

    return dbc.Container([
        dbc.Row([dbc.Col(dcc.Graph(figure=fig1), md=6),
                 dbc.Col(dcc.Graph(figure=fig2), md=6)]),
    ])


def _render_compare(dff, selected):
    if not selected or len(selected) < 2:
        return dbc.Alert("Sélectionnez au moins 2 pays pour comparer.", color="info")
    dff_sel = dff[dff["country"].isin(selected)]

    fig1 = px.line(dff_sel, x="date", y="new_cases_per_million", color="country",
                   render_mode="svg",
                   labels={"new_cases_per_million": "Cas / million", "date": "", "country": "Pays"},
                   title="Comparaison — Cas", template=DARK_TEMPLATE)
    fig2 = px.line(dff_sel, x="date", y="new_deaths_per_million", color="country",
                   render_mode="svg",
                   labels={"new_deaths_per_million": "Décès / million", "date": "", "country": "Pays"},
                   title="Comparaison — Décès", template=DARK_TEMPLATE)
    return dbc.Container([
        dbc.Row([dbc.Col(dcc.Graph(figure=fig1), md=6),
                 dbc.Col(dcc.Graph(figure=fig2), md=6)]),
    ])


def _render_scatter(dff):
    snap = get_snapshot(dff)
    snap = snap[snap["total_cases_per_million"] > 0]
    fig = px.scatter(snap, x="total_cases_per_million", y="total_deaths_per_million",
                     hover_name="country", size="total_cases", size_max=40,
                     color="cfr", color_continuous_scale="Viridis",
                     log_x=True, log_y=True,
                     labels={"total_cases_per_million": "Cas / million (log)",
                             "total_deaths_per_million": "Décès / million (log)",
                             "cfr": "CFR (%)"},
                     title="Cas vs Décès par million (log)", template=DARK_TEMPLATE)
    return dbc.Container(dbc.Row(dbc.Col(dcc.Graph(figure=fig))))


def _render_data_table(dff):
    snap = get_snapshot(dff)
    cols = ["country", "date", "total_cases", "total_deaths",
            "total_cases_per_million", "total_deaths_per_million", "cfr"]
    snap_d = snap[cols].copy()
    snap_d["date"] = snap_d["date"].dt.strftime("%Y-%m-%d")
    for c in cols[2:]:
        snap_d[c] = snap_d[c].round(2)
    table = dash_table.DataTable(
        data=snap_d.to_dict("records"),
        columns=[{"name": c, "id": c} for c in cols],
        page_size=20, sort_action="native", filter_action="native",
        style_table={"overflowX": "auto"},
        style_header={"backgroundColor": "#303030", "color": "white", "fontWeight": "bold"},
        style_cell={"backgroundColor": "#222", "color": "white", "border": "1px solid #444",
                    "textAlign": "left", "padding": "8px"},
        style_filter={"backgroundColor": "#333", "color": "white"},
    )
    return dbc.Container([html.H5("Données par pays (dernière date)", className="mb-3"), table])


# ── Point d'entrée ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=8050)
