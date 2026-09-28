"""Un test par connecteur, avec réponses API simulées (aucun appel réseau)."""

from __future__ import annotations

import json

from mtr_agent.connectors import REGISTRY
from mtr_agent.connectors.cisco import CiscoConnector
from mtr_agent.connectors.grafana import GrafanaConnector
from mtr_agent.connectors.jabra import JabraConnector
from mtr_agent.connectors.lenovo import LenovoConnector
from mtr_agent.connectors.neat import NeatConnector
from mtr_agent.connectors.ochno import OchnoConnector
from mtr_agent.connectors.poly import PolyConnector
from mtr_agent.connectors.sony import SonyConnector
from mtr_agent.connectors.sylphony import SylphonyConnector
from mtr_agent.connectors.teams import TeamsRoomsConnector
from mtr_agent.connectors.teams_pro import TeamsRoomsProConnector
from mtr_agent.connectors.zebrix import ZebrixConnector
from mtr_agent.http_client import HttpResponse
from mtr_agent.models import Health

from .conftest import rpc_response

GRAPH_CREDS = {"tenant_id": "t1", "client_id": "c1", "client_secret": "s3cr3t"}
TOKEN_URL = "https://login.microsoftonline.com/t1/oauth2/v2.0/token"
GRAPH = "https://graph.microsoft.com/v1.0"


def by_id(devices):
    return {d.device_id: d for d in devices}


def test_registry_has_one_connector_per_equipment():
    assert set(REGISTRY) == {"teams", "teams_pro", "grafana", "cisco", "neat", "jabra", "poly", "sony",
                             "lenovo", "ochno", "zebrix", "sylphony"}


def test_teams_rooms_lists_devices_with_pagination(http):
    http.add("POST", TOKEN_URL, {"access_token": "tok", "expires_in": 3600})
    http.add("GET", f"{GRAPH}/teamwork/devices", {
        "value": [{"id": "d1", "deviceType": "teamsRoom", "healthStatus": "healthy",
                   "hardwareDetail": {"manufacturer": "Lenovo", "model": "ThinkSmart Core"},
                   "currentUser": {"displayName": "Salle Mirabeau"}}],
        "@odata.nextLink": f"{GRAPH}/teamwork/devices?page=2",
    })
    http.add("GET", f"{GRAPH}/teamwork/devices?page=2", {
        "value": [{"id": "d2", "deviceType": "touchConsole", "healthStatus": "offline"}]})

    result = TeamsRoomsConnector(GRAPH_CREDS, http).collect()

    assert result.up, result.errors
    devs = by_id(result.devices)
    assert devs["d1"].health is Health.HEALTHY and devs["d1"].online
    assert devs["d1"].room == "Salle Mirabeau" and devs["d1"].model == "Lenovo ThinkSmart Core"
    assert devs["d2"].health is Health.OFFLINE and not devs["d2"].online
    # le jeton est demandé une seule fois et envoyé à Graph
    assert sum(c["url"] == TOKEN_URL for c in http.calls) == 1
    assert http.calls[1]["headers"]["Authorization"] == "Bearer tok"


def test_teams_pro_reads_health_and_flags_missing_peripheral(http):
    http.add("POST", TOKEN_URL, {"access_token": "tok"})
    http.add("GET", f"{GRAPH}/teamwork/devices", {"value": [
        {"id": "r1", "deviceType": "teamsRoom", "healthStatus": "healthy"},
        {"id": "p1", "deviceType": "touchConsole", "healthStatus": "healthy"},
    ]})
    http.add("GET", f"{GRAPH}/teamwork/devices/r1/health", {
        "connection": {"connectionStatus": "connected"},
        "peripheralsHealth": {
            "roomCameraHealth": {"isOptional": False, "connection": {"connectionStatus": "disconnected"}},
            "microphoneHealth": {"isOptional": False, "connection": {"connectionStatus": "connected"}},
            "roomDisplayHealthCollection": [{"isOptional": False, "connection": {"connectionStatus": "connected"}}],
        },
        "loginStatus": {"teamsConnection": {"connectionStatus": "connected"},
                        "exchangeConnection": {"connectionStatus": "connected"}},
    })

    result = TeamsRoomsProConnector(GRAPH_CREDS, http).collect()

    assert result.up, result.errors
    assert [d.device_id for d in result.devices] == ["r1"]  # seules les salles
    room = result.devices[0]
    assert room.peripherals == {"roomCamera": False, "microphone": True, "roomDisplay1": True}
    assert room.health is Health.DEGRADED


def test_cisco_maps_webex_status_and_workspace(http):
    http.add("GET", "https://webexapis.com/v1/workspaces", {"items": [{"id": "w1", "displayName": "Salle Mirabeau"}]})
    http.add("GET", "https://webexapis.com/v1/devices", {"items": [
        {"id": "c1", "displayName": "Room Bar", "product": "Cisco Room Bar", "software": "RoomOS 11.20",
         "workspaceId": "w1", "connectionStatus": "connected", "errorCodes": []},
        {"id": "c2", "displayName": "Desk", "connectionStatus": "connected", "errorCodes": ["mic"]},
        {"id": "c3", "displayName": "Board", "connectionStatus": "disconnected"},
    ]})

    devs = by_id(CiscoConnector({"token": "tok"}, http).collect().devices)

    assert devs["c1"].health is Health.HEALTHY and devs["c1"].room == "Salle Mirabeau"
    assert devs["c2"].health is Health.DEGRADED and devs["c2"].online
    assert devs["c3"].health is Health.OFFLINE and not devs["c3"].online


def test_neat_pulse_endpoints(http):
    http.add("GET", "https://api.pulse.neat.no/v1/orgs/org1/endpoints", {"endpoints": [
        {"id": "n1", "name": "Neat Bar", "roomName": "Mirabeau", "model": "Neat Bar Pro", "firmwareVersion": "NFA1.2",
         "connected": True, "cpuUsage": 31.5, "memoryUsage": 62,
         "peripherals": [{"name": "Neat Pad", "connected": True}]},
        {"id": "n2", "name": "Neat Board", "connected": False},
    ]})

    result = NeatConnector({"token": "k", "org_id": "org1"}, http).collect()

    devs = by_id(result.devices)
    assert devs["n1"].online and devs["n1"].cpu_percent == 31.5 and devs["n1"].memory_percent == 62
    assert devs["n1"].peripherals == {"Neat Pad": True}
    assert not devs["n2"].online and devs["n2"].health is Health.OFFLINE


def test_jabra_follows_next_link_and_sends_subscription_key(http):
    base = "https://jabra.example"
    http.add("GET", f"{base}/devices", {"devices": [{"id": "j1", "status": "online", "productName": "PanaCast 50"}],
                                        "nextLink": f"{base}/devices?p=2"})
    http.add("GET", f"{base}/devices?p=2", {"devices": [{"id": "j2", "status": "offline"}]})

    result = JabraConnector({"base_url": base, "token": "t", "subscription_key": "sk"}, http).collect()

    devs = by_id(result.devices)
    assert devs["j1"].online and devs["j1"].model == "PanaCast 50"
    assert not devs["j2"].online
    assert http.calls[0]["headers"]["Ocp-Apim-Subscription-Key"] == "sk"


def test_poly_lens_graphql(http):
    http.add("POST", "https://login.lens.poly.com/oauth/token", {"access_token": "pt"})
    pages = iter([
        {"data": {"deviceSearch": {"edges": [{"node": {"id": "p1", "name": "Studio X50", "connected": True,
                                                       "hardwareModel": "Studio X50", "softwareVersion": "4.1",
                                                       "room": {"name": "Mirabeau"}}}],
                                   "pageInfo": {"nextToken": "n2", "hasNextPage": True}}}},
        {"data": {"deviceSearch": {"edges": [{"node": {"id": "p2", "name": "TC10", "connected": False}}],
                                   "pageInfo": {"nextToken": None, "hasNextPage": False}}}},
    ])
    http.add("POST", "https://api.silica-prod01.io.lens.poly.com/graphql",
             lambda call: HttpResponse(200, json.dumps(next(pages)).encode()))

    result = PolyConnector({"client_id": "c", "client_secret": "s"}, http).collect()

    devs = by_id(result.devices)
    assert devs["p1"].online and devs["p1"].room == "Mirabeau"
    assert devs["p2"].health is Health.OFFLINE
    graphql_calls = [c for c in http.calls if c["url"].endswith("/graphql")]
    assert graphql_calls[1]["json"]["variables"] == {"next": "n2"}


def test_grafana_health(http):
    http.add("GET", "https://grafana.example/api/health", {"database": "ok", "version": "11.2.0"})

    dev = GrafanaConnector({"base_url": "https://grafana.example/"}, http).collect().devices[0]

    assert dev.device_id == "grafana.example" and dev.firmware == "11.2.0"
    assert dev.health is Health.HEALTHY and dev.peripherals == {"database": True}


def test_sony_bravia_power_states_and_unreachable_display(http):
    info = {"model": "FW-65BZ40L", "serial": "123", "generation": "5.6.0"}
    http.add("POST", "http://10.0.0.10/sony/system",
             lambda call: rpc_response({"status": "active"} if call["json"]["method"] == "getPowerStatus"
                                       else info)(call))
    http.add("POST", "http://10.0.0.11/sony/system",
             lambda call: rpc_response({"status": "standby"} if call["json"]["method"] == "getPowerStatus"
                                       else info)(call))
    http.add("POST", "http://10.0.0.12/sony/system", status=403, body={})

    result = SonyConnector({"hosts": "10.0.0.10, 10.0.0.11,10.0.0.12", "psk": "0000"}, http).collect()

    devs = by_id(result.devices)
    assert devs["10.0.0.10"].health is Health.HEALTHY and devs["10.0.0.10"].model == "FW-65BZ40L"
    assert devs["10.0.0.11"].health is Health.DEGRADED and devs["10.0.0.11"].online
    assert devs["10.0.0.12"].health is Health.OFFLINE and not devs["10.0.0.12"].online
    assert http.calls[0]["headers"]["X-Auth-PSK"] == "0000"


def test_lenovo_thinksmart(http):
    http.add("GET", "https://tsm.example/api/v1/devices", {"data": [
        {"deviceId": "l1", "deviceName": "Core", "status": "Online", "healthState": "Warning", "cpuUsage": "12"},
        {"deviceId": "l2", "deviceName": "Hub", "status": "Offline"},
    ]})

    devs = by_id(LenovoConnector({"base_url": "https://tsm.example", "token": "t"}, http).collect().devices)

    assert devs["l1"].online and devs["l1"].health is Health.DEGRADED and devs["l1"].cpu_percent == 12.0
    assert devs["l2"].health is Health.OFFLINE


def test_ochno_hub_and_ports(http):
    http.add("GET", "https://ochno.example/api/v1/devices", {"devices": [
        {"id": "o1", "name": "Hub", "room": {"name": "Mirabeau"}, "online": True,
         "ports": [{"name": "HDMI 1", "online": True}, {"name": "USB-C", "online": False}]},
    ]})

    dev = OchnoConnector({"base_url": "https://ochno.example", "token": "t"}, http).collect().devices[0]

    assert dev.room == "Mirabeau" and dev.online
    assert dev.peripherals == {"HDMI 1": True, "USB-C": False}


def test_zebrix_players(http):
    http.add("GET", "https://zebrix.example/api/v1/players", {"data": [
        {"id": "z1", "name": "Écran accueil", "status": "playing", "cpu_usage": 40},
        {"id": "z2", "name": "Écran couloir", "status": "offline"},
    ], "next": None})

    devs = by_id(ZebrixConnector({"base_url": "https://zebrix.example", "token": "t"}, http).collect().devices)

    assert devs["z1"].online and devs["z1"].cpu_percent == 40.0
    assert not devs["z2"].online


def test_sylphony_alarm_levels(http):
    http.add("GET", "https://sylphony.example/api/v1/devices", {"items": [
        {"id": "s1", "label": "Codec", "state": "up", "alarm": "major", "metrics": {"cpu": 90, "memory": 70}},
        {"id": "s2", "label": "Capteur", "state": "down"},
    ]})

    devs = by_id(SylphonyConnector({"base_url": "https://sylphony.example", "token": "t"}, http).collect().devices)

    assert devs["s1"].health is Health.CRITICAL and devs["s1"].memory_percent == 70.0
    assert devs["s2"].health is Health.OFFLINE


# -- comportements communs ------------------------------------------------------

def test_missing_settings_reported_without_network(http):
    result = GrafanaConnector({}, http).collect()
    assert not result.up and "base_url" in result.errors[0]
    assert http.calls == []


def test_http_error_is_captured_and_does_not_leak_secret(http):
    http.add("GET", "https://webexapis.com/v1/workspaces", {}, status=401)
    result = CiscoConnector({"token": "super-secret"}, http).collect()
    assert not result.up and "HTTP 401" in result.errors[0]
    assert "super-secret" not in result.errors[0]
    assert "super-secret" not in repr(CiscoConnector({"token": "super-secret"}, http))


def test_from_env_reads_prefixed_variables(http):
    env = {"MTR_GRAFANA_BASE_URL": "https://g.example", "MTR_GRAFANA_TOKEN": "t", "OTHER": "x"}
    conn = GrafanaConnector.from_env(env, http)
    assert conn.settings == {"base_url": "https://g.example", "token": "t"}
