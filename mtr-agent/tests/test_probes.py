from __future__ import annotations

from itertools import count

import pytest

from mtr_agent.http_client import HttpResponse
from mtr_agent.probes import parse_ping_output, probe_http, tcp_probe


def fake_clock(step: float):
    ticks = count()
    return lambda: next(ticks) * step


def test_http_probe_measures_availability_time_and_throughput(http):
    http.add("GET", "https://room.example/", lambda call: HttpResponse(200, b"x" * 1000))
    res = probe_http("https://room.example/", http, clock=fake_clock(0.5))
    assert res.available and res.status == 200
    assert res.response_time_seconds == 0.5 and res.throughput_bytes_per_second == 2000


def test_http_probe_unreachable(http):
    res = probe_http("https://down.example/", http)
    assert not res.available and res.status is None


def test_tcp_probe_loss_latency_jitter():
    outcomes = iter([True, False, True, True])

    class Sock:
        def close(self):
            pass

    def connect(addr, timeout):
        if not next(outcomes):
            raise OSError("refused")
        return Sock()

    times = iter([0, 0.010, 1, 2, 2.030, 3, 3.020])  # 10 ms, échec, 30 ms, 20 ms
    res = tcp_probe("10.0.0.1", 443, attempts=4, connect=connect, clock=lambda: next(times))
    assert res.failures == 1 and res.loss_percent == 25.0
    assert res.latency_ms == pytest.approx(20.0)
    assert res.jitter_ms == pytest.approx(15.0)


def test_parse_ping_output():
    out = """PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
64 bytes from 10.0.0.1: icmp_seq=1 ttl=64 time=1.20 ms
64 bytes from 10.0.0.1: icmp_seq=3 ttl=64 time=1.60 ms

--- 10.0.0.1 ping statistics ---
3 packets transmitted, 2 received, 33.3333% packet loss, time 2003ms
"""
    res = parse_ping_output("10.0.0.1", out)
    assert res.sent == 3 and res.failures == 1
    assert res.latency_ms == pytest.approx(1.4) and res.jitter_ms == pytest.approx(0.4)
