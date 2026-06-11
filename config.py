"""Configuration centrale du projet.

Rassemble tous les paramètres « globaux » : chemins de fichiers, pointeurs vers
les ressources de données, paramètres de la base SQLite et constantes
métier utilisées par le dashboard. Tous les autres modules importent ces
valeurs plutôt que de les coder en dur.
"""

from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------- #
# Chemins (tous résolus relativement à la racine du projet)
# --------------------------------------------------------------------------- #

BASE_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = BASE_DIR / "data"
RAW_DIR: Path = DATA_DIR / "raw"
DB_PATH: Path = DATA_DIR / "db.sqlite"

# Fichier brut téléchargé par get_data.py (stocké dans data/raw/).
RAW_FILENAME: str = "cases_deaths.csv"
RAW_CSV_PATH: Path = RAW_DIR / RAW_FILENAME

# CSV éventuellement déjà présent à la racine (machine de développement) :
# sert de repli hors-ligne si le téléchargement échoue.
LOCAL_FALLBACK_CSV: Path = BASE_DIR / RAW_FILENAME

# --------------------------------------------------------------------------- #
# Source de données (Open Data — Our World in Data, COVID-19)
# --------------------------------------------------------------------------- #

DATA_URL: str = (
    "https://catalog.ourworldindata.org/garden/covid/latest/"
    "cases_deaths/cases_deaths.csv"
)

# --------------------------------------------------------------------------- #
# Base de données SQLite
# --------------------------------------------------------------------------- #

RAW_TABLE: str = "raw"          # données brutes, sans modification
CLEANED_TABLE: str = "cleaned"  # données nettoyées et sélectionnées

# Colonnes conservées dans la table "cleaned" (les seules utiles au dashboard).
CLEANED_COLUMNS: list[str] = [
    "country",
    "date",
    "total_cases",
    "total_deaths",
    "new_cases_per_million",
    "new_deaths_per_million",
    "total_cases_per_million",
    "total_deaths_per_million",
]

# --------------------------------------------------------------------------- #
# Constantes métier (dashboard)
# --------------------------------------------------------------------------- #

# Agrégats géographiques / économiques de la colonne "country" : ils ne sont
# pas des pays réels et doivent être exclus des cartes et histogrammes.
REGIONS: frozenset[str] = frozenset({
    "Africa", "Asia", "Asia excl. China", "Europe", "European Union (27)",
    "High-income countries", "Low-income countries",
    "Lower-middle-income countries", "North America", "Oceania",
    "South America", "Upper-middle-income countries", "World",
    "World excl. China", "World excl. China and South Korea",
    "World excl. China, South Korea, Japan and Singapore",
})

# Indicateurs numériques (non catégoriels) proposés à l'utilisateur.
# Clé = nom de colonne, valeur = libellé affiché dans l'interface.
METRICS: dict[str, str] = {
    "total_cases_per_million": "Cas cumulés / million",
    "total_deaths_per_million": "Décès cumulés / million",
    "new_cases_per_million": "Nouveaux cas / million",
    "new_deaths_per_million": "Nouveaux décès / million",
}

# Pays sélectionnés par défaut dans les séries temporelles.
DEFAULT_COUNTRIES: list[str] = ["France", "Germany", "United States", "Brazil"]

# Template graphique commun (thème sombre, cohérent avec le thème Bootstrap).
DARK_TEMPLATE: str = "plotly_dark"

# --------------------------------------------------------------------------- #
# Serveur Dash
# --------------------------------------------------------------------------- #

SERVER_HOST: str = "127.0.0.1"
SERVER_PORT: int = 8050
DEBUG: bool = False  # False pour l'évaluation (pas de rechargement à chaud)
