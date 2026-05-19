import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback

# Chargement et nettoyage 

df = pd.read_csv("cases_deaths.csv", parse_dates=["date"])
df = df.sort_values(["country", "date"]).reset_index(drop=True)
numeric_cols = df.select_dtypes(include="number").columns
df[numeric_cols] = df[numeric_cols].fillna(0)

# Exclure les agrégats régionaux (liste partielle)
REGIONS = [
    "Africa", "Asia", "Europe", "North America",
    "South America", "Oceania", "World",
    "High-income countries", "Low-income countries",
    "Lower-middle-income countries", "Upper-middle-income countries",
]
df_country = df[~df["country"].isin(REGIONS)].copy()
countries = sorted(df_country["country"].unique())

# Application Dash
app = Dash(__name__)
app.title = "COVID-19 Dashboard"

app.layout = html.Div([
    html.H1("COVID-19 — Dashboard", style={"textAlign": "center"}),

    html.Div([
        html.Label("Sélectionner un pays :"),
        dcc.Dropdown(
            id="country-select",
            options=[{"label": c, "value": c} for c in countries],
            value="France",
            clearable=False,
        ),
    ], style={"width": "40%", "margin": "auto"}),

    html.Br(),

    dcc.Graph(id="cases-chart"),
    dcc.Graph(id="deaths-chart"),
])


@callback(
    Output("cases-chart", "figure"),
    Output("deaths-chart", "figure"),
    Input("country-select", "value"),
)
def update_charts(country):
    dff = df_country[df_country["country"] == country]

    fig1 = px.line(
        dff, x="date", y="new_cases_per_million",
        title=f"Nouveaux cas par million — {country}",
        labels={"new_cases_per_million": "Cas / million", "date": ""},
    )
    fig2 = px.line(
        dff, x="date", y="new_deaths_per_million",
        title=f"Nouveaux décès par million — {country}",
        labels={"new_deaths_per_million": "Décès / million", "date": ""},
    )
    return fig1, fig2


if __name__ == "__main__":
    app.run(debug=True, port=8050)
