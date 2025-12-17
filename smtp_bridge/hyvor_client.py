from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import time
from typing import Any, Dict, Optional

import requests


@dataclass(frozen=True)
class HyvorClient:
    base_url: str
    api_key: str
    timeout_s: float = 10.0
    retries: int = 3

    def send(self, payload: Dict[str, Any], idem_key: str) -> requests.Response:
        url = _send_url(self.base_url)
        headers = _headers(self.api_key, idem_key)
        return _post_with_retries(
            url=url,
            headers=headers,
            json_payload=payload,
            timeout_s=self.timeout_s,
            retries=self.retries,
        )


def make_idempotency_key(message_bytes: bytes, rcpt_hash: str) -> str:
    digest = hashlib.sha256(message_bytes + rcpt_hash.encode("utf-8")).hexdigest()
    return f"smtp-bridge-{digest}"


def _send_url(base_url: str) -> str:
    trimmed = base_url.rstrip("/")
    return f"{trimmed}/api/console/sends"


def _headers(api_key: str, idem_key: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Idempotency-Key": idem_key,
    }


def _post_with_retries(
    *,
    url: str,
    headers: Dict[str, str],
    json_payload: Dict[str, Any],
    timeout_s: float,
    retries: int,
) -> requests.Response:
    last: Optional[requests.Response] = None
    for attempt in range(retries):
        last = requests.post(
            url,
            headers=headers,
            data=json.dumps(json_payload),
            timeout=timeout_s,
        )
        if _ok(last.status_code):
            return last
        if not _retryable(last.status_code):
            return last
        time.sleep(_backoff_s(attempt))
    return last if last is not None else _never(last)


def _ok(code: int) -> bool:
    return 200 <= code < 300


def _retryable(code: int) -> bool:
    return code == 429 or 500 <= code < 600


def _backoff_s(attempt: int) -> float:
    return [0.5, 1.0, 2.0, 4.0][min(attempt, 3)]


def _never(value: Optional[requests.Response]) -> requests.Response:
    raise RuntimeError("unreachable: response should never be None")
