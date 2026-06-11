"""Tests des fonctions d'accès et de transformation des données."""

from __future__ import annotations

import pandas as pd

import config
from src.utils.common_functions import get_snapshot, split_world_countries


def _sample() -> pd.DataFrame:
    """Petit jeu de données synthétique pour les tests."""
    return pd.DataFrame({
        "country": ["France", "France", "World", "Africa"],
        "date": pd.to_datetime(
            ["2021-01-01", "2021-01-02", "2021-01-02", "2021-01-02"]
        ),
        "total_cases": [10, 20, 100, 30],
    })


def test_get_snapshot_keeps_last_row_per_country() -> None:
    """get_snapshot ne garde que la dernière date de chaque pays."""
    snap = get_snapshot(_sample())
    france = snap[snap["country"] == "France"]
    assert len(france) == 1
    assert france.iloc[0]["total_cases"] == 20


def test_get_snapshot_empty_input() -> None:
    """Un DataFrame vide en entrée renvoie un DataFrame vide."""
    empty = _sample().iloc[0:0]
    assert get_snapshot(empty).empty


def test_split_world_countries() -> None:
    """split sépare bien les pays réels de l'agrégat mondial."""
    countries, world = split_world_countries(_sample())
    # "World" et "Africa" sont des agrégats -> exclus des pays.
    assert set(countries["country"]) == {"France"}
    assert set(world["country"]) == {"World"}
    # Cohérence avec la configuration.
    assert "World" in config.REGIONS
