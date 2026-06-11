"""
Version 1 — Exploration des données
Objectif : charger le CSV, comprendre sa structure, produire
           quelques graphiques statiques avec Plotly.
"""

import pandas as pd
import plotly.express as px

# Chargement

df = pd.read_csv("cases_deaths.csv", parse_dates=["date"])

print("Dimensions :", df.shape)
print("Colonnes :", df.columns.tolist())
print()
print(df.head())
print()
print("Valeurs manquantes (top 10) :")
print(df.isnull().sum().sort_values(ascending=False).head(10))

# Nettoyage minimal

df = df.sort_values(["country", "date"]).reset_index(drop=True)
numeric_cols = df.select_dtypes(include="number").columns
df[numeric_cols] = df[numeric_cols].fillna(0)

# Quelques statistiques 

print("\nPays disponibles :", df["country"].nunique())
print("Période :", df["date"].min().date(), "→", df["date"].max().date())

# Graphiques statiques en France 
df_france = df[df["country"] == "France"].copy()

fig1 = px.line(
    df_france,
    x="date",
    y="new_cases_per_million",
    title="Nouveaux cas par million — France",
    labels={"new_cases_per_million": "Cas / million", "date": ""},
)
fig1.show()

fig2 = px.line(
    df_france,
    x="date",
    y="total_cases",
    title="Cas cumulés — France",
    labels={"total_cases": "Total cas", "date": ""},
)
fig2.show()

fig3 = px.line(
    df_france,
    x="date",
    y="cfr",
    title="Taux de létalité (CFR) — France",
    labels={"cfr": "CFR (%)", "date": ""},
)
fig3.show()

#  Comparaison rapide entre plusieurs pays 

pays_test = ["France", "Germany", "United States", "Brazil"]
df_test = df[df["country"].isin(pays_test)]

fig4 = px.line(
    df_test,
    x="date",
    y="new_cases_per_million",
    color="country",
    title="Nouveaux cas par million — comparaison",
    labels={"new_cases_per_million": "Cas / million", "date": "", "country": "Pays"},
)
fig4.show()
