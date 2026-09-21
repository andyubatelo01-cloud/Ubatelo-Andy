"""Bureau d'IA : les sept agents et leur chef d'orchestre."""
from .analytics import AnalyticsAgent
from .berger import BergerAgent
from .communication import CommunicationAgent
from .directeur import AGENT_ROSTER, DirecteurAgent
from .events_agent import EventsAgent
from .membres_agent import MembresAgent
from .sarah import SarahAgent

__all__ = ["AGENT_ROSTER", "AnalyticsAgent", "BergerAgent", "CommunicationAgent", "DirecteurAgent", "EventsAgent", "MembresAgent", "SarahAgent"]
