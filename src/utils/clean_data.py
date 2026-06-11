"""Nettoyage des données.

Lit la table ``raw`` de la base SQLite, nettoie et sélectionne les colonnes
utiles, puis écrit le résultat dans la table ``cleaned``.

Utilisation en ligne de commande ::

    python -m src.utils.clean_data
"""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

import config


def load_raw(
    db_path: Path = config.DB_PATH,
    table: str = config.RAW_TABLE,
) -> pd.DataFrame:
    """Charge les données brutes depuis la table ``raw``.

    Args:
        db_path: Chemin de la base SQLite.
        table: Nom de la table source.

    Returns:
        Le DataFrame des données brutes.
    """
    with closing(sqlite3.connect(db_path)) as conn:
        return pd.read_sql_query(f"SELECT * FROM {table}", conn)


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    """Nettoie et sélectionne les données pour le dashboard.

    Étapes :

    1. conversion de la colonne ``date`` en ``datetime`` ;
    2. sélection des seules colonnes utiles (:data:`config.CLEANED_COLUMNS`) ;
    3. remplacement des valeurs manquantes par 0 (absence de cas/décès
       rapporté à cette date) ;
    4. tri par pays puis par date.

    Args:
        raw: Données brutes issues de la table ``raw``.

    Returns:
        Le DataFrame nettoyé, prêt à être stocké et consommé par le dashboard.
    """
    data = raw.copy()
    data["date"] = pd.to_datetime(data["date"])

    # On ne conserve que les colonnes réellement utilisées (base allégée).
    data = data[config.CLEANED_COLUMNS]

    numeric_cols = data.select_dtypes(include="number").columns
    data[numeric_cols] = data[numeric_cols].fillna(0)

    return data.sort_values(["country", "date"]).reset_index(drop=True)


def store_cleaned(
    data: pd.DataFrame,
    db_path: Path = config.DB_PATH,
    table: str = config.CLEANED_TABLE,
) -> int:
    """Écrit les données nettoyées dans la table ``cleaned``.

    Args:
        data: Données nettoyées.
        db_path: Chemin de la base SQLite.
        table: Nom de la table de destination.

    Returns:
        Le nombre de lignes écrites.
    """
    with closing(sqlite3.connect(db_path)) as conn:
        data.to_sql(table, conn, if_exists="replace", index=False,
                    chunksize=50_000)
        conn.commit()
    print(f"{len(data):,} lignes écrites dans la table '{table}'.")
    return len(data)


def main() -> None:
    """Charge la table ``raw``, la nettoie et remplit la table ``cleaned``."""
    raw = load_raw()
    cleaned = clean(raw)
    store_cleaned(cleaned)


if __name__ == "__main__":
    main()
