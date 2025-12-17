from __future__ import annotations

import base64
from dataclasses import dataclass
from email.message import EmailMessage, Message
from email.parser import BytesParser
from email.policy import default
from typing import Any, Dict, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class ConvertedEmail:
    subject: str
    body_text: Optional[str]
    body_html: Optional[str]
    attachments: List[Dict[str, Any]]


def parse_email(raw_bytes: bytes) -> EmailMessage:
    return BytesParser(policy=default).parsebytes(raw_bytes)


def to_hyvor_payload(
    *,
    envelope_from: str,
    envelope_to: Sequence[str],
    raw_bytes: bytes,
) -> Dict[str, Any]:
    msg = parse_email(raw_bytes)
    subject = _subject(msg)
    body_text, body_html = _bodies(msg)
    attachments = _attachments(msg)

    payload: Dict[str, Any] = {
        "from": envelope_from,
        "to": list(envelope_to),
        "subject": subject,
    }
    _maybe_set(payload, "body_text", body_text)
    _maybe_set(payload, "body_html", body_html)
    if attachments:
        payload["attachments"] = attachments
    return payload


def _subject(msg: EmailMessage) -> str:
    value = msg.get("subject")
    return "" if value is None else str(value)


def _bodies(msg: EmailMessage) -> Tuple[Optional[str], Optional[str]]:
    if msg.is_multipart():
        return _bodies_multipart(msg)
    return _bodies_single(msg)


def _bodies_single(msg: EmailMessage) -> Tuple[Optional[str], Optional[str]]:
    ctype = msg.get_content_type()
    text = _safe_get_text(msg)
    if ctype == "text/html":
        return None, text
    if ctype == "text/plain":
        return text, None
    return None, None


def _bodies_multipart(msg: EmailMessage) -> Tuple[Optional[str], Optional[str]]:
    text = _first_text(msg, "text/plain")
    html = _first_text(msg, "text/html")
    return text, html


def _first_text(msg: EmailMessage, want: str) -> Optional[str]:
    for part in msg.walk():
        if _is_body_candidate(part, want):
            return _safe_get_text(part)
    return None


def _is_body_candidate(part: Message, want: str) -> bool:
    if part.get_content_type() != want:
        return False
    disp = (part.get("Content-Disposition") or "").lower()
    return "attachment" not in disp


def _safe_get_text(part: Message) -> Optional[str]:
    try:
        return part.get_content()
    except (LookupError, UnicodeDecodeError):
        return None


def _attachments(msg: EmailMessage) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for part in msg.walk():
        if _is_attachment(part):
            items.append(_attachment_obj(part))
    return items


def _is_attachment(part: Message) -> bool:
    if part.is_multipart():
        return False
    disp = (part.get("Content-Disposition") or "").lower()
    if "attachment" in disp:
        return True
    return _is_non_body_inline(part)


def _is_non_body_inline(part: Message) -> bool:
    ctype = part.get_content_type()
    if ctype in {"text/plain", "text/html"}:
        return False
    return True


def _attachment_obj(part: Message) -> Dict[str, Any]:
    data = _payload_bytes(part)
    name = _filename(part)
    ctype = part.get_content_type()
    return {
        "content": base64.b64encode(data).decode("ascii"),
        "name": name,
        "content_type": ctype,
    }


def _payload_bytes(part: Message) -> bytes:
    payload = part.get_payload(decode=True)
    return b"" if payload is None else payload


def _filename(part: Message) -> str:
    name = part.get_filename()
    return "attachment" if name is None else str(name)


def _maybe_set(payload: Dict[str, Any], key: str, value: Optional[str]) -> None:
    if value is not None and value != "":
        payload[key] = value
