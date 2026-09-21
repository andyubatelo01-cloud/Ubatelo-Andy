"""Fournisseurs de modèles de langage.

- `AnthropicProvider` : Claude via le SDK officiel (sorties structurées).
- `TemplateProvider` : mode hors-ligne déterministe (aucune donnée ne quitte le serveur).

Règle de minimisation : les agents n'envoient JAMAIS la liste des membres ni leurs
coordonnées au modèle. Seuls l'événement, le style, le nom du public et la demande
du pasteur sont transmis.
"""
from __future__ import annotations

import logging
from typing import TypeVar

from pydantic import BaseModel

from ..config import get_settings

logger = logging.getLogger("bureau.llm")
T = TypeVar("T", bound=BaseModel)


class LLMProvider:
    name = "base"

    def available(self) -> bool:
        return True

    def generate_text(self, system: str, prompt: str) -> str:  # pragma: no cover - interface
        raise NotImplementedError

    def generate_structured(self, system: str, prompt: str, schema: type[T]) -> T | None:  # pragma: no cover - interface
        raise NotImplementedError


class TemplateProvider(LLMProvider):
    """Ne fait aucun appel réseau : les agents disposent de gabarits français intégrés."""

    name = "template"

    def generate_text(self, system: str, prompt: str) -> str:
        return ""

    def generate_structured(self, system: str, prompt: str, schema: type[T]) -> T | None:
        return None


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, model: str | None = None):
        s = get_settings()
        self.model = model or s.llm_model
        self._client = None
        self.api_key = s.anthropic_api_key

    def available(self) -> bool:
        return bool(self.api_key)

    def _get_client(self):
        if self._client is None:
            import anthropic

            self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    def generate_text(self, system: str, prompt: str) -> str:
        client = self._get_client()
        response = client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            thinking={"type": "adaptive"},
            output_config={"effort": "medium"},
        )
        if response.stop_reason == "refusal":
            logger.warning("Le modèle a refusé la demande.")
            return ""
        return "".join(block.text for block in response.content if block.type == "text").strip()

    def generate_structured(self, system: str, prompt: str, schema: type[T]) -> T | None:
        client = self._get_client()
        response = client.messages.parse(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            output_format=schema,
            thinking={"type": "adaptive"},
            output_config={"effort": "medium"},
        )
        if response.stop_reason == "refusal":
            return None
        return response.parsed_output


_provider: LLMProvider | None = None


def get_provider() -> LLMProvider:
    global _provider
    if _provider is None:
        s = get_settings()
        if s.llm_provider.lower() == "anthropic":
            candidate = AnthropicProvider()
            if candidate.available():
                _provider = candidate
            else:
                logger.warning("LLM_PROVIDER=anthropic mais ANTHROPIC_API_KEY absent : bascule en mode gabarits.")
                _provider = TemplateProvider()
        else:
            _provider = TemplateProvider()
    return _provider


def set_provider(provider: LLMProvider | None) -> None:
    global _provider
    _provider = provider
