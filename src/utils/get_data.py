"""Récupération des données brutes.

Télécharge le jeu de données COVID-19 « Our World in Data » depuis l'URL
définie dans :mod:`config`, le stocke tel quel dans ``data/raw/`` puis le
charge, sans modification, dans la table ``raw`` de la base SQLite.

Utilisation en ligne de commande ::

    python -m src.utils.get_data
"""

from __future__ import annotations

import shutil
import sqlite3
import urllib.request
from contextlib import closing
from pathlib import Path

import pandas as pd

import config


def download_raw_data(
    url: str = config.DATA_URL,
    dest: Path = config.RAW_CSV_PATH,
    *,
    force: bool = False,
) -> Path:
    """Télécharge le fichier brut et l'enregistre dans ``data/raw/``.

    En cas d'échec réseau, le fichier local de repli
    (:data:`config.LOCAL_FALLBACK_CSV`) est utilisé s'il existe, ce qui permet
    de reconstruire la base hors-ligne sur la machine de développement.

    Args:
        url: URL de la ressource Open Data.
        dest: Chemin de destination du fichier brut.
        force: Si ``True``, retélécharge même si le fichier existe déjà.

    Returns:
        Le chemin du fichier brut téléchargé.

    Raises:
        RuntimeError: Si le téléchargement échoue et qu'aucun repli n'existe.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)

    # On évite de retélécharger un fichier déjà présent (gain de temps).
    if dest.exists() and not force:
        return dest

    try:
        print(f"Téléchargement des données depuis {url} …")
        urllib.request.urlretrieve(url, dest)  # noqa: S310 (URL de confiance)
        print(f"Données enregistrées dans {dest}")
        return dest
    except OSError as err:
        # Repli hors-ligne : on copie le CSV local s'il est disponible.
        if config.LOCAL_FALLBACK_CSV.exists():
            print(f"Téléchargement impossible ({err}). "
                  f"Utilisation du fichier local {config.LOCAL_FALLBACK_CSV}.")
            shutil.copy(config.LOCAL_FALLBACK_CSV, dest)
            return dest
        raise RuntimeError(
            f"Impossible de récupérer les données ({err}) et aucun fichier "
            f"de repli n'a été trouvé à {config.LOCAL_FALLBACK_CSV}."
        ) from err


def store_raw_data(
    csv_path: Path = config.RAW_CSV_PATH,
    db_path: Path = config.DB_PATH,
    table: str = config.RAW_TABLE,
) -> int:
    """Charge le CSV brut dans la table ``raw`` de la base SQLite.

    Les données sont insérées sans transformation (conformément à l'exigence
    « données brutes, sans modification »).

    Args:
        csv_path: Chemin du fichier CSV brut.
        db_path: Chemin de la base SQLite.
        table: Nom de la table de destination.

    Returns:
        Le nombre de lignes insérées.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(csv_path)

    # sqlite3.Connection est nativement supporté par pandas pour SQLite.
    with closing(sqlite3.connect(db_path)) as conn:
        data.to_sql(table, conn, if_exists="replace", index=False,
                    chunksize=50_000)
        conn.commit()
    print(f"{len(data):,} lignes écrites dans la table '{table}'.")
    return len(data)


def main() -> None:
    """Télécharge les données puis les stocke dans la table ``raw``."""
    csv_path = download_raw_data()
    store_raw_data(csv_path)


if __name__ == "__main__":
    main()
