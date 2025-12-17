from __future__ import annotations

from dataclasses import dataclass
import os


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return default if value is None else value


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Config:
    hyvor_base_url: str
    hyvor_api_key: str
    smtp_listen_host: str
    smtp_listen_port: int
    smtp_require_tls: bool
    log_level: str

    @staticmethod
    def from_env() -> "Config":
        return Config(
            hyvor_base_url=_env("HYVOR_BASE_URL", "https://hyvor.wardcrew.com"),
            hyvor_api_key=_env("HYVOR_API_KEY", ""),
            smtp_listen_host=_env("SMTP_LISTEN_HOST", "0.0.0.0"),
            smtp_listen_port=_env_int("SMTP_LISTEN_PORT", 2525),
            smtp_require_tls=_env_bool("SMTP_REQUIRE_TLS", False),
            log_level=_env("LOG_LEVEL", "INFO"),
        )
