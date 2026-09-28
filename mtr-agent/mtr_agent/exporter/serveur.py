"""Serveur HTTP de l'exporteur : ``/metrics`` protégé par mot de passe."""

from __future__ import annotations

import ipaddress
import logging
import ssl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest

from .collecteur import CollecteurMTR
from .model import SourceMesures
from .securite import Identifiants, LimiteurTentatives

log = logging.getLogger(__name__)


def construire_registre(source: SourceMesures) -> CollectorRegistry:
    registre = CollectorRegistry(auto_describe=False)
    registre.register(CollecteurMTR(source))
    return registre


def _fabrique_gestionnaire(registre: CollectorRegistry, ids: Identifiants, limiteur: LimiteurTentatives):
    class Gestionnaire(BaseHTTPRequestHandler):
        server_version = "mtr-exporter"
        sys_version = ""

        def do_GET(self) -> None:  # noqa: N802
            chemin = self.path.split("?", 1)[0]
            if chemin == "/healthz":
                return self._repondre(200, b"ok\n", "text/plain; charset=utf-8")
            if chemin != "/metrics":
                return self._repondre(404, b"introuvable\n", "text/plain; charset=utf-8")

            ip = self.client_address[0]
            if limiteur.est_bloque(ip):
                log.warning("Accès refusé (IP bloquée) : %s", ip)
                return self._repondre(429, b"trop de tentatives\n", "text/plain; charset=utf-8")
            if not ids.verifier_entete(self.headers.get("Authorization")):
                limiteur.echec(ip)
                log.warning("Échec d'authentification depuis %s", ip)
                return self._repondre(
                    401, b"authentification requise\n", "text/plain; charset=utf-8",
                    {"WWW-Authenticate": 'Basic realm="mtr-exporter", charset="UTF-8"'},
                )
            limiteur.succes(ip)
            return self._repondre(200, generate_latest(registre), CONTENT_TYPE_LATEST)

        def do_POST(self) -> None:  # noqa: N802
            self._repondre(405, b"methode non autorisee\n", "text/plain; charset=utf-8", {"Allow": "GET"})

        do_PUT = do_DELETE = do_PATCH = do_POST

        def _repondre(self, code: int, corps: bytes, type_: str, entetes: dict | None = None) -> None:
            self.send_response(code)
            self.send_header("Content-Type", type_)
            self.send_header("Content-Length", str(len(corps)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            for k, v in (entetes or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(corps)

        def log_message(self, fmt: str, *args) -> None:
            log.debug("%s - %s", self.address_string(), fmt % args)

    return Gestionnaire


def creer_serveur(
    source: SourceMesures,
    ids: Identifiants,
    hote: str = "127.0.0.1",
    port: int = 9469,
    cert: str | None = None,
    cle: str | None = None,
) -> ThreadingHTTPServer:
    registre = construire_registre(source)
    serveur = ThreadingHTTPServer((hote, port), _fabrique_gestionnaire(registre, ids, LimiteurTentatives()))
    serveur.daemon_threads = True
    if cert and cle:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain(cert, cle)
        serveur.socket = ctx.wrap_socket(serveur.socket, server_side=True)
    elif not _est_local(hote):
        log.warning(
            "L'exporteur écoute sur %s sans TLS : le mot de passe circule en clair. "
            "Définissez MTR_EXPORTER_TLS_CERT et MTR_EXPORTER_TLS_KEY.", hote,
        )
    return serveur


def _est_local(hote: str) -> bool:
    try:
        return ipaddress.ip_address(hote).is_loopback
    except ValueError:
        return hote == "localhost"
