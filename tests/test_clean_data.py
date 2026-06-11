"""Tests du nettoyage des données et du stockage SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

import config
from src.utils import clean_data, get_data


def _raw_sample() -> pd.DataFrame:
    """Données brutes synthétiques (dates en texte, valeurs manquantes)."""
    base = {col: [1.0, None] for col in config.CLEANED_COLUMNS}
    base["country"] = ["France", "Germany"]
    base["date"] = ["2021-01-02", "2021-01-01"]
    return pd.DataFrame(base)


def test_clean_fills_na_and_sorts() -> None:
    """clean() remplit les NaN par 0, garde les colonnes et trie."""
    cleaned = clean_data.clean(_raw_sample())

    # Colonnes attendues exactement.
    assert list(cleaned.columns) == config.CLEANED_COLUMNS
    # Plus aucune valeur manquante.
    assert not cleaned.isna().any().any()
    # Tri par pays puis date : France avant Germany.
    assert list(cleaned["country"]) == ["France", "Germany"]
    # La date est bien typée datetime.
    assert pd.api.types.is_datetime64_any_dtype(cleaned["date"])


def test_store_and_load_roundtrip(tmp_path: Path) -> None:
    """store_raw_data écrit une table relisible par load_raw."""
    csv_path = tmp_path / "sample.csv"
    db_path = tmp_path / "db.sqlite"
    _raw_sample().to_csv(csv_path, index=False)

    n = get_data.store_raw_data(csv_path, db_path, config.RAW_TABLE)
    assert n == 2

    with sqlite3.connect(db_path) as conn:
        reloaded = pd.read_sql_query(
            f"SELECT * FROM {config.RAW_TABLE}", conn
        )
    assert len(reloaded) == 2
