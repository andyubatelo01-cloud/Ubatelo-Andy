"""Socle commun des agents du Bureau d'IA."""
from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from ..models import AgentRun
from .llm import LLMProvider, get_provider

CHARTER = (
    "Tu fais partie du Bureau d'IA d'une communauté chrétienne francophone. "
    "Tu assistes le pasteur : tu prépares, tu proposes, tu n'envoies jamais. "
    "Tu ne prétends jamais connaître l'état spirituel, émotionnel ou médical d'une personne. "
    "Tu travailles uniquement à partir des informations explicitement fournies. "
    "Tu écris en français, de façon claire, courte et naturelle. "
    "Tu n'inventes ni date, ni lieu, ni horaire : si une information manque, tu la demandes."
)


@dataclass
class AgentResult:
    agent: str
    summary: str
    data: dict = field(default_factory=dict)
    missing_info: list[str] = field(default_factory=list)
    campaign_refs: list[str] = field(default_factory=list)
    task_ids: list[int] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "agent": self.agent,
            "summary": self.summary,
            "data": self.data,
            "missing_info": self.missing_info,
            "campaign_refs": self.campaign_refs,
            "task_ids": self.task_ids,
        }


class Agent:
    name = "AGENT"
    icon = "🤖"
    description = ""

    def __init__(self, db: Session, actor: str = "", provider: LLMProvider | None = None):
        self.db = db
        self.actor = actor or self.name
        self.llm = provider or get_provider()

    def trace(self, command: str, intent: str, result: AgentResult) -> None:
        self.db.add(AgentRun(agent=self.name, command=command[:2000], intent=intent, result=result.as_dict(), provider=self.llm.name, actor=self.actor))
        self.db.flush()
