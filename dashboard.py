import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc

df = pd.read_csv("cases_deaths.csv", parse_dates=["date"])

REGIONS = [
    "Africa", "Asia", "Asia excl. China", "Europe", "European Union (27)",
    "High-income countries", "Low-income countries", "Lower-middle-income countries",
    "North America", "Oceania", "South America", "Upper-middle-income countries",
    "World", "World excl. China", "World excl. China and South Korea",
    "World excl. China, South Korea, Japan and Singapore",
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
    """Dernière ligne disponible par pays."""
    last = dff.groupby("country")["date"].max().reset_index(name="last_date")
    snap = dff.merge(last, on="country")
    return snap[snap["date"] == snap["last_date"]].drop(columns="last_date")



app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "COVID-19 Dashboard"


def make_kpi_card(title, value, color="primary"):
    return dbc.Card(dbc.CardBody([
        html.H6(title, className="card-title text-muted mb-1"),
        html.H3(value, className=f"text-{color} mb-0"),
    ]), className="shadow-sm")


app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("COVID-19 — Dashboard Mondial", className="text-center my-4"))),
    dbc.Row(id="kpi-row", className="mb-4 g-3"),

    # Contrôles
    dbc.Row([
        dbc.Col([
            html.Label("Pays sélectionnés", className="fw-bold"),
            dcc.Dropdown(
                id="country-select",
                options=[{"label": c, "value": c} for c in countries],
                value=["France", "Germany", "United States", "Brazil"],
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
        dbc.Tab(label="📈 Séries temporelles", tab_id="tab-ts"),
        dbc.Tab(label="🗺️ Carte mondiale",     tab_id="tab-map"),
        dbc.Tab(label="📋 Données",             tab_id="tab-data"),
    ], id="tabs", active_tab="tab-ts", className="mb-3"),
    html.Div(id="tab-content"),

    html.Hr(),
    html.P("Source : Our World in Data — COVID-19 Dataset",
           className="text-center text-muted small"),
], fluid=True)


@callback(Output("kpi-row", "children"), Input("date-range", "end_date"))
def update_kpis(end_date):
    filtered = df_world[df_world["date"] <= end_date].sort_values("date")
    if filtered.empty:
        return []
    w = filtered.iloc[-1]
    return [
        dbc.Col(make_kpi_card("Total cas",    f"{w['total_cases']:,.0f}",  "info"),    md=4),
        dbc.Col(make_kpi_card("Total décès",  f"{w['total_deaths']:,.0f}", "danger"),  md=4),
        dbc.Col(make_kpi_card("Pays suivis",  f"{len(countries)}",         "success"), md=4),
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
        if not selected:
            return dbc.Alert("Veuillez sélectionner au moins un pays.", color="info")
        dff_sel = dff[dff["country"].isin(selected)]
        fig1 = px.line(dff_sel, x="date", y="new_cases_per_million", color="country",
                       labels={"new_cases_per_million": "Cas / million", "date": "", "country": "Pays"},
                       title="Nouveaux cas par million", template=DARK_TEMPLATE)
        fig2 = px.line(dff_sel, x="date", y="total_cases_per_million", color="country",
                       labels={"total_cases_per_million": "Cas cumulés / million", "date": "", "country": "Pays"},
                       title="Cas cumulés par million", template=DARK_TEMPLATE)
        return dbc.Container([
            dbc.Row([dbc.Col(dcc.Graph(figure=fig1), md=6),
                     dbc.Col(dcc.Graph(figure=fig2), md=6)]),
        ])

    if active_tab == "tab-map":
        snap = get_snapshot(dff)
        fig = px.choropleth(
            snap, locations="country", locationmode="country names",
            color="total_cases_per_million", hover_name="country",
            hover_data=["total_cases", "total_deaths"],
            color_continuous_scale="YlOrRd",
            title="Total cas par million", template=DARK_TEMPLATE,
        )
        fig.update_layout(geo=dict(bgcolor="rgba(0,0,0,0)"))
        return dbc.Container(dbc.Row(dbc.Col(dcc.Graph(figure=fig))))

    if active_tab == "tab-data":
        snap = get_snapshot(dff)
        cols = ["country", "date", "total_cases", "total_deaths",
                "total_cases_per_million", "total_deaths_per_million"]
        snap_d = snap[cols].copy()
        snap_d["date"] = snap_d["date"].dt.strftime("%Y-%m-%d")
        for c in cols[2:]:
            snap_d[c] = snap_d[c].round(2)
        table = dash_table.DataTable(
            data=snap_d.to_dict("records"),
            columns=[{"name": c, "id": c} for c in cols],
            page_size=20, sort_action="native",
            style_table={"overflowX": "auto"},
            style_header={"backgroundColor": "#303030", "color": "white", "fontWeight": "bold"},
            style_cell={"backgroundColor": "#222", "color": "white", "border": "1px solid #444",
                        "textAlign": "left", "padding": "8px"},
        )
        return dbc.Container([html.H5("Données par pays (dernière date)", className="mb-3"), table])

    return html.P("Sélectionnez un onglet.")


if __name__ == "__main__":
    app.run(debug=True, port=8050)
