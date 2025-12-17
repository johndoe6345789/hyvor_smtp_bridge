from __future__ import annotations

import logging


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=_level(level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _level(level: str) -> int:
    value = level.strip().upper()
    return getattr(logging, value, logging.INFO)
