"""Sonde HTTP : disponibilité, temps de réponse et débit."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

from ..http_client import HttpClient, UrllibHttpClient


@dataclass
class HttpProbeResult:
    target: str
    available: bool
    status: int | None
    response_time_seconds: float
    bytes_received: int

    @property
    def throughput_bytes_per_second(self) -> float:
        return self.bytes_received / self.response_time_seconds if self.response_time_seconds > 0 else 0.0


def probe_http(url: str, http: HttpClient | None = None, timeout: float = 10.0,
               clock: Callable[[], float] = time.perf_counter) -> HttpProbeResult:
    http = http or UrllibHttpClient()
    start = clock()
    try:
        resp = http.request("GET", url, timeout=timeout)
    except Exception:
        return HttpProbeResult(url, False, None, clock() - start, 0)
    elapsed = clock() - start
    return HttpProbeResult(url, resp.status < 400, resp.status, elapsed, len(resp.body))
