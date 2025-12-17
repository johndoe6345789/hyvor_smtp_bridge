from __future__ import annotations

import logging
from typing import Any, Sequence

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import Envelope, Session

from .email_convert import to_hyvor_payload
from .hyvor_client import HyvorClient, make_idempotency_key


LOG = logging.getLogger(__name__)


class BridgeHandler:
    def __init__(self, client: HyvorClient) -> None:
        self._client = client

    async def handle_DATA(
        self,
        server: Any,
        session: Session,
        envelope: Envelope,
    ) -> str:
        return _handle(self._client, envelope.mail_from, envelope.rcpt_tos, envelope.content)


def start_smtp_server(host: str, port: int, handler: BridgeHandler) -> Controller:
    controller = Controller(handler, hostname=host, port=port, decode_data=False)
    controller.start()
    return controller


def _handle(client: HyvorClient, mail_from: str, rcpt_tos: Sequence[str], data: bytes) -> str:
    rcpt_hash = ",".join(sorted(rcpt_tos))
    idem = make_idempotency_key(data, rcpt_hash)
    payload = to_hyvor_payload(envelope_from=mail_from, envelope_to=rcpt_tos, raw_bytes=data)
    resp = client.send(payload, idem)
    if 200 <= resp.status_code < 300:
        LOG.info("Forwarded via Hyvor Relay: %s -> %s (%s)", mail_from, rcpt_tos, resp.status_code)
        return "250 OK (queued)"
    LOG.error("Hyvor Relay error: %s %s", resp.status_code, resp.text[:500])
    return "451 Requested action aborted: local error in processing"
