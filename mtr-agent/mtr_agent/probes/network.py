"""Sondes réseau : perte de paquets, latence, gigue et échecs de connexion TCP.

``tcp_probe`` ne demande aucun privilège : chaque tentative est une ouverture de
connexion TCP chronométrée. ``ping`` utilise la commande système quand l'ICMP
est autorisé ; ``parse_ping_output`` en extrait les mesures.
"""

from __future__ import annotations

import re
import socket
import statistics
import subprocess
import time
from dataclasses import dataclass, field
from typing import Callable



@dataclass
class NetworkProbeResult:
    target: str
    sent: int
    rtts_ms: list[float] = field(default_factory=list)
    method: str = "tcp"

    @property
    def failures(self) -> int:
        return self.sent - len(self.rtts_ms)

    @property
    def loss_percent(self) -> float:
        return 100.0 * self.failures / self.sent if self.sent else 100.0

    @property
    def latency_ms(self) -> float | None:
        return statistics.fmean(self.rtts_ms) if self.rtts_ms else None

    @property
    def jitter_ms(self) -> float | None:
        """Moyenne des écarts entre mesures successives (esprit RFC 3550)."""
        if len(self.rtts_ms) < 2:
            return None
        return statistics.fmean(abs(b - a) for a, b in zip(self.rtts_ms, self.rtts_ms[1:]))


def tcp_probe(host: str, port: int, attempts: int = 5, timeout: float = 2.0,
              connect: Callable[..., socket.socket] = socket.create_connection,
              clock: Callable[[], float] = time.perf_counter) -> NetworkProbeResult:
    result = NetworkProbeResult(f"{host}:{port}", attempts)
    for _ in range(attempts):
        start = clock()
        try:
            sock = connect((host, port), timeout=timeout)
        except OSError:
            continue
        result.rtts_ms.append((clock() - start) * 1000.0)
        sock.close()
    return result


_RTT = re.compile(r"time[=<]([\d.]+)\s*ms")
_SENT = re.compile(r"(\d+) packets transmitted")


def parse_ping_output(target: str, output: str) -> NetworkProbeResult:
    sent_match = _SENT.search(output)
    rtts = [float(x) for x in _RTT.findall(output)]
    sent = int(sent_match.group(1)) if sent_match else len(rtts)
    return NetworkProbeResult(target, sent, rtts, method="icmp")


def ping(host: str, count: int = 5, timeout: float = 2.0) -> NetworkProbeResult:
    proc = subprocess.run(["ping", "-n", "-c", str(count), "-W", str(int(timeout)), host],
                          capture_output=True, text=True, timeout=count * (timeout + 1) + 5)
    return parse_ping_output(host, proc.stdout)
