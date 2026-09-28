"""Authentification de l'exporteur : Basic Auth, mot de passe haché, anti force brute.

Le mot de passe ne vit jamais dans le code : il vient de l'environnement
(ou d'un coffre qui alimente l'environnement), de préférence sous forme de
hachage PBKDF2 produit par ``python -m mtr_agent.exporter hacher-mot-de-passe``.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import threading
import time
from dataclasses import dataclass, field

ALGO = "pbkdf2_sha256"
ITERATIONS = 600_000


def hacher_mot_de_passe(mot_de_passe: str, iterations: int = ITERATIONS) -> str:
    sel = secrets.token_hex(16)
    empreinte = hashlib.pbkdf2_hmac("sha256", mot_de_passe.encode(), sel.encode(), iterations)
    return f"{ALGO}${iterations}${sel}${empreinte.hex()}"


def verifier_hachage(mot_de_passe: str, hachage: str) -> bool:
    try:
        algo, iterations, sel, attendu = hachage.split("$")
        if algo != ALGO:
            return False
        calcule = hashlib.pbkdf2_hmac("sha256", mot_de_passe.encode(), sel.encode(), int(iterations))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(calcule.hex(), attendu)


class ConfigurationInvalide(RuntimeError):
    pass


@dataclass
class Identifiants:
    utilisateur: str
    hachage: str
    # Cache des mots de passe déjà vérifiés : évite de relancer PBKDF2 à chaque
    # scrape (toutes les 15 s) tout en gardant un hachage lent contre le vol.
    _valides: set = field(default_factory=set, repr=False)

    @classmethod
    def depuis_environnement(cls, env: dict | None = None) -> "Identifiants":
        env = os.environ if env is None else env
        utilisateur = env.get("MTR_EXPORTER_USER", "prometheus")
        hachage = env.get("MTR_EXPORTER_PASSWORD_HASH", "").strip()
        clair = env.get("MTR_EXPORTER_PASSWORD", "")
        if not hachage and clair:
            if len(clair) < 12:
                raise ConfigurationInvalide("MTR_EXPORTER_PASSWORD doit faire au moins 12 caractères.")
            hachage = hacher_mot_de_passe(clair, iterations=100_000)
        if not hachage:
            raise ConfigurationInvalide(
                "Aucun mot de passe configuré : définissez MTR_EXPORTER_PASSWORD_HASH "
                "(recommandé) ou MTR_EXPORTER_PASSWORD. L'exporteur refuse de démarrer sans."
            )
        if not hachage.startswith(ALGO + "$"):
            raise ConfigurationInvalide("MTR_EXPORTER_PASSWORD_HASH n'est pas un hachage pbkdf2_sha256 valide.")
        return cls(utilisateur=utilisateur, hachage=hachage)

    def verifier_entete(self, entete: str | None) -> bool:
        if not entete or not entete.startswith("Basic "):
            return False
        try:
            brut = base64.b64decode(entete[6:], validate=True).decode()
            utilisateur, mot_de_passe = brut.split(":", 1)
        except (ValueError, UnicodeDecodeError):
            return False
        ok_utilisateur = hmac.compare_digest(utilisateur.encode(), self.utilisateur.encode())
        cle = hashlib.sha256(brut.encode()).digest()
        if cle in self._valides:
            return ok_utilisateur
        ok_mdp = verifier_hachage(mot_de_passe, self.hachage)
        if ok_utilisateur and ok_mdp:
            self._valides.add(cle)
        return ok_utilisateur and ok_mdp


class LimiteurTentatives:
    """Bloque une adresse IP après trop d'échecs d'authentification."""

    def __init__(self, max_echecs: int = 5, fenetre_s: float = 300, blocage_s: float = 900) -> None:
        self.max_echecs = max_echecs
        self.fenetre_s = fenetre_s
        self.blocage_s = blocage_s
        self._echecs: dict[str, list[float]] = {}
        self._bloques: dict[str, float] = {}
        self._verrou = threading.Lock()

    def est_bloque(self, ip: str) -> bool:
        with self._verrou:
            fin = self._bloques.get(ip)
            if fin is None:
                return False
            if time.monotonic() >= fin:
                del self._bloques[ip]
                return False
            return True

    def echec(self, ip: str) -> None:
        maintenant = time.monotonic()
        with self._verrou:
            recents = [t for t in self._echecs.get(ip, []) if maintenant - t < self.fenetre_s]
            recents.append(maintenant)
            if len(recents) >= self.max_echecs:
                self._bloques[ip] = maintenant + self.blocage_s
                recents = []
            self._echecs[ip] = recents

    def succes(self, ip: str) -> None:
        with self._verrou:
            self._echecs.pop(ip, None)
