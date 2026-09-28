"""Client HTTP minimal (bibliothèque standard) et interface injectable.

Les connecteurs reçoivent un objet respectant ``HttpClient`` : en production
``UrllibHttpClient``, en test un faux client qui renvoie des réponses simulées.
La vérification TLS n'est jamais désactivée.
"""

from __future__ import annotations

import json as _json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol


@dataclass
class HttpResponse:
    status: int
    body: bytes = b""
    headers: Mapping[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    def json(self) -> Any:
        return _json.loads(self.body.decode("utf-8")) if self.body else None


class HttpClient(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        data: Mapping[str, str] | None = None,
        json: Any = None,
        timeout: float = 10.0,
    ) -> HttpResponse: ...


def build_url(url: str, params: Mapping[str, Any] | None) -> str:
    if not params:
        return url
    sep = "&" if urllib.parse.urlparse(url).query else "?"
    return url + sep + urllib.parse.urlencode(params)


class UrllibHttpClient:
    """Implémentation par défaut, sans dépendance externe."""

    def __init__(self, ca_file: str | None = None) -> None:
        self._ssl = ssl.create_default_context(cafile=ca_file)

    def request(self, method, url, *, headers=None, params=None, data=None, json=None, timeout=10.0):
        body: bytes | None = None
        hdrs = dict(headers or {})
        if json is not None:
            body = _json.dumps(json).encode("utf-8")
            hdrs.setdefault("Content-Type", "application/json")
        elif data is not None:
            body = urllib.parse.urlencode(data).encode("utf-8")
            hdrs.setdefault("Content-Type", "application/x-www-form-urlencoded")
        req = urllib.request.Request(build_url(url, params), data=body, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=self._ssl) as resp:
                return HttpResponse(resp.status, resp.read(), dict(resp.headers))
        except urllib.error.HTTPError as exc:
            return HttpResponse(exc.code, exc.read() or b"", dict(exc.headers or {}))
