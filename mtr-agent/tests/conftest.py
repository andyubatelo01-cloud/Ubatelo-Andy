"""Faux client HTTP : chaque test déclare les réponses API simulées."""

from __future__ import annotations

import json
from typing import Any, Callable

import pytest

from mtr_agent.http_client import HttpResponse


class FakeHttp:
    def __init__(self) -> None:
        self.routes: dict[tuple[str, str], Any] = {}
        self.calls: list[dict[str, Any]] = []

    def add(self, method: str, url: str, body: Any = None, status: int = 200) -> "FakeHttp":
        self.routes[(method, url)] = body if callable(body) else HttpResponse(status, json.dumps(body).encode())
        return self

    def request(self, method, url, *, headers=None, params=None, data=None, json=None, timeout=10.0):
        call = dict(method=method, url=url, headers=dict(headers or {}), params=params, data=data, json=json)
        self.calls.append(call)
        route = self.routes.get((method, url))
        if route is None:
            raise ConnectionError(f"aucune réponse simulée pour {method} {url}")
        return route(call) if callable(route) else route


@pytest.fixture
def http() -> FakeHttp:
    return FakeHttp()


def rpc_response(result: Any) -> Callable[[dict], HttpResponse]:
    return lambda call: HttpResponse(200, json.dumps({"result": [result], "id": 1}).encode())
