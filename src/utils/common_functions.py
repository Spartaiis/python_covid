"""Fonctions d'accès et de transformation partagées par le dashboard."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

import config

# Cache mémoire du DataFrame nettoyé : la base n'est lue qu'une seule fois,
# au premier appel (les callbacks Dash réutilisent ensuite l'objet en mémoire).
_CACHE: dict[str, pd.DataFrame] = {}


def load_cleaned(
    db_path: Path = config.DB_PATH,
    table: str = config.CLEANED_TABLE,
) -> pd.DataFrame:
    """Charge (et met en cache) les données nettoyées depuis SQLite.

    Args:
        db_path: Chemin de la base SQLite.
        table: Nom de la table à lire.

    Returns:
        Le DataFrame nettoyé, avec la colonne ``date`` typée ``datetime``.

    Raises:
        FileNotFoundError: Si la base de données n'existe pas encore.
    """
    if "df" in _CACHE:
        return _CACHE["df"]

    if not db_path.exists():
        raise FileNotFoundError(
            f"Base de données introuvable : {db_path}. "
            "Lancez d'abord get_data.py puis clean_data.py "
            "(ou simplement 'python main.py' qui la construit au besoin)."
        )

    # closing() garantit la fermeture (le context manager de sqlite3 ne gère
    # que la transaction, pas la fermeture de la connexion).
    with closing(sqlite3.connect(db_path)) as conn:
        data = pd.read_sql_query(
            f"SELECT * FROM {table}", conn, parse_dates=["date"]
        )
    _CACHE["df"] = data
    return data


def split_world_countries(
    data: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Sépare les pays réels de l'agrégat mondial.

    Args:
        data: DataFrame nettoyé complet.

    Returns:
        Un couple ``(pays_reels, monde)`` où ``pays_reels`` exclut les
        agrégats (:data:`config.REGIONS`) et ``monde`` ne contient que la
        ligne « World ».
    """
    countries = data[~data["country"].isin(config.REGIONS)].copy()
    world = data[data["country"] == "World"].copy()
    return countries, world


def get_snapshot(dff: pd.DataFrame) -> pd.DataFrame:
    """Retourne la dernière ligne disponible pour chaque pays.

    Args:
        dff: Sous-ensemble du DataFrame (déjà filtré sur une période).

    Returns:
        Une ligne par pays correspondant à sa date la plus récente. Un
        DataFrame vide en entrée renvoie un DataFrame vide.
    """
    if dff.empty:
        return dff
    last = dff.groupby("country")["date"].max().reset_index(name="last_date")
    snap = dff.merge(last, on="country")
    return snap[snap["date"] == snap["last_date"]].drop(columns="last_date")
