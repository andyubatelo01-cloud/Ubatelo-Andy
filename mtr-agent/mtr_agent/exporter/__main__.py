"""Point d'entrée : ``python -m mtr_agent.exporter [--simulation]``.

Variables d'environnement :
  MTR_EXPORTER_USER            utilisateur Basic Auth (défaut : prometheus)
  MTR_EXPORTER_PASSWORD_HASH   hachage pbkdf2 (recommandé)
  MTR_EXPORTER_PASSWORD        mot de passe en clair (dev uniquement, 12 caractères min.)
  MTR_EXPORTER_HOST            adresse d'écoute (défaut : 127.0.0.1)
  MTR_EXPORTER_PORT            port (défaut : 9469)
  MTR_EXPORTER_TLS_CERT/KEY    certificat et clé TLS (conseillé hors localhost)
"""

from __future__ import annotations

import argparse
import getpass
import logging
import os
import sys

from .securite import ConfigurationInvalide, Identifiants, hacher_mot_de_passe
from .serveur import creer_serveur


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="mtr_agent.exporter", description="Exporteur Prometheus des salles MTR.")
    sous = p.add_subparsers(dest="commande")
    sous.add_parser("hacher-mot-de-passe", help="Produit la valeur de MTR_EXPORTER_PASSWORD_HASH.")
    p.add_argument("--simulation", action="store_true", help="Sert des données simulées (aucun équipement interrogé).")
    p.add_argument("--hote", default=os.environ.get("MTR_EXPORTER_HOST", "127.0.0.1"))
    p.add_argument("--port", type=int, default=int(os.environ.get("MTR_EXPORTER_PORT", "9469")))
    args = p.parse_args(argv)

    if args.commande == "hacher-mot-de-passe":
        mdp = getpass.getpass("Mot de passe : ")
        if len(mdp) < 12 or mdp != getpass.getpass("Confirmation : "):
            print("Mots de passe différents ou trop courts (12 caractères min.).", file=sys.stderr)
            return 1
        print(hacher_mot_de_passe(mdp))
        return 0

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    try:
        ids = Identifiants.depuis_environnement()
    except ConfigurationInvalide as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 2

    if not args.simulation:
        # Branchement des connecteurs réels à venir : l'exporteur attend une
        # SourceMesures (voir model.py). Pas de repli silencieux sur la simulation.
        print("Aucune source réelle branchée pour l'instant : relancez avec --simulation.", file=sys.stderr)
        return 2

    from .simulation import SimulateurMesures

    serveur = creer_serveur(
        SimulateurMesures(), ids, hote=args.hote, port=args.port,
        cert=os.environ.get("MTR_EXPORTER_TLS_CERT"), cle=os.environ.get("MTR_EXPORTER_TLS_KEY"),
    )
    schema = "https" if os.environ.get("MTR_EXPORTER_TLS_CERT") else "http"
    logging.info("Exporteur (simulation) sur %s://%s:%d/metrics", schema, args.hote, args.port)
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        serveur.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
