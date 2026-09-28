"""Registre des connecteurs : un par équipement ou service."""

from .base import BaseConnector, ConnectorError, RestInventoryConnector
from .cisco import CiscoConnector
from .grafana import GrafanaConnector
from .jabra import JabraConnector
from .lenovo import LenovoConnector
from .neat import NeatConnector
from .ochno import OchnoConnector
from .poly import PolyConnector
from .sony import SonyConnector
from .sylphony import SylphonyConnector
from .teams import TeamsRoomsConnector
from .teams_pro import TeamsRoomsProConnector
from .zebrix import ZebrixConnector

REGISTRY: dict[str, type[BaseConnector]] = {
    c.vendor: c
    for c in (
        TeamsRoomsConnector, TeamsRoomsProConnector, GrafanaConnector, CiscoConnector, NeatConnector,
        JabraConnector, PolyConnector, SonyConnector, LenovoConnector, OchnoConnector, ZebrixConnector,
        SylphonyConnector,
    )
}

__all__ = ["BaseConnector", "ConnectorError", "RestInventoryConnector", "REGISTRY"]
