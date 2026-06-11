"""Point d'entrée du dashboard COVID-19.

Lancement ::

    python main.py

Au démarrage, si la base SQLite n'existe pas encore, elle est construite
automatiquement (récupération via get_data.py puis nettoyage via
clean_data.py) afin que le dashboard soit fonctionnel à la première tentative.
"""

from __future__ import annotations

import config
from src.utils import clean_data, get_data


def ensure_database() -> None:
    """Construit la base SQLite si elle est absente.

    Garantit la présence des tables ``raw`` et ``cleaned`` avant le lancement
    du dashboard, pour qu'il s'exécute même sur une machine vierge.
    """
    if config.DB_PATH.exists():
        return
    print("Base de données absente : construction initiale…")
    get_data.main()
    clean_data.main()


def main() -> None:
    """Prépare les données puis démarre le serveur Dash."""
    ensure_database()
    # Import différé : la base doit exister avant le chargement des données.
    from src.app import create_app

    app = create_app()
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()
