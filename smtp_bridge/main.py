from __future__ import annotations

import os
import signal
import time
from typing import Optional

from .config import Config
from .hyvor_client import HyvorClient
from .logging_setup import configure_logging
from .smtp_server import BridgeHandler, start_smtp_server


def main() -> int:
    cfg = Config.from_env()
    configure_logging(cfg.log_level)
    _require(cfg.hyvor_api_key, "HYVOR_API_KEY is required")

    client = HyvorClient(base_url=cfg.hyvor_base_url, api_key=cfg.hyvor_api_key)
    handler = BridgeHandler(client)
    controller = start_smtp_server(cfg.smtp_listen_host, cfg.smtp_listen_port, handler)

    _install_signal_handlers(controller)
    _idle_forever()
    return 0


def _require(value: str, msg: str) -> None:
    if value.strip() == "":
        raise SystemExit(msg)


def _install_signal_handlers(controller: object) -> None:
    def stop(*_: object) -> None:
        getattr(controller, "stop")()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)


def _idle_forever() -> None:
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    raise SystemExit(main())
