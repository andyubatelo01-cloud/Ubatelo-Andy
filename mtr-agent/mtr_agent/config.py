"""Configuration lue uniquement depuis l'environnement (ou un coffre qui l'alimente).

Aucun secret n'est écrit dans le code. Chaque connecteur lit ses réglages sous le
préfixe ``MTR_<VENDOR>_`` ; par exemple ``MTR_GRAFANA_URL`` et ``MTR_GRAFANA_TOKEN``.
"""

from __future__ import annotations

import os
from typing import Mapping

SECRET_HINTS = ("secret", "token", "password", "psk", "key")


def vendor_settings(vendor: str, env: Mapping[str, str] | None = None) -> dict[str, str]:
    """Renvoie les variables ``MTR_<VENDOR>_*`` sous forme ``{clé_minuscule: valeur}``."""
    env = os.environ if env is None else env
    prefix = f"MTR_{vendor.upper()}_"
    return {k[len(prefix):].lower(): v for k, v in env.items() if k.startswith(prefix) and v != ""}


def mask(settings: Mapping[str, str]) -> dict[str, str]:
    """Copie affichable (journaux) : les valeurs sensibles sont masquées."""
    return {k: ("***" if any(h in k for h in SECRET_HINTS) else v) for k, v in settings.items()}
