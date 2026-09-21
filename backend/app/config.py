"""Configuration centrale du Bureau du Pasteur.

Toutes les valeurs proviennent des variables d'environnement (ou d'un fichier .env).
Aucun secret n'est codé en dur.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Général
    app_name: str = "Bureau du Pasteur"
    app_env: str = "development"
    secret_key: str = "dev-secret-change-me"
    timezone: str = "Europe/Paris"
    base_url: str = "http://localhost:8000"

    # Base de données
    database_url: str = "sqlite:///./data/bureau.db"

    # Compte administrateur initial
    admin_email: str = "pasteur@exemple.org"
    admin_password: str = "changez-moi"
    admin_name: str = "Pasteur"
    pastor_phone: str = ""

    # IA
    llm_provider: str = "template"  # template | anthropic
    anthropic_api_key: str = ""
    llm_model: str = "claude-opus-5"

    # Canaux
    sms_provider: str = "console"
    whatsapp_provider: str = "console"
    email_provider: str = "console"
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_sms_from: str = ""
    twilio_whatsapp_from: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "bureau@exemple.org"

    # Règles de validation
    double_confirmation_threshold: int = Field(default=100, ge=1)
    approval_link_ttl_hours: int = Field(default=48, ge=1)
    sms_unit_cost_eur: float = 0.07
    daily_briefing_hour: int = Field(default=7, ge=0, le=23)
    scheduler_enabled: bool = True
    scheduler_interval_seconds: int = 60

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
