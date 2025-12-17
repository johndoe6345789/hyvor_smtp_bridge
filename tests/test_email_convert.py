from __future__ import annotations

import base64
import unittest
from email.message import EmailMessage

from smtp_bridge.email_convert import to_hyvor_payload


class TestEmailConvert(unittest.TestCase):
    def test_plain_text(self) -> None:
        msg = EmailMessage()
        msg["Subject"] = "Hi"
        msg.set_content("Hello")
        raw = msg.as_bytes()

        payload = to_hyvor_payload(
            envelope_from="[email protected]",
            envelope_to=["[email protected]"],
            raw_bytes=raw,
        )
        self.assertEqual(payload["subject"], "Hi")
        self.assertEqual(payload["body_text"].strip(), "Hello")
        self.assertNotIn("body_html", payload)

    def test_html_and_attachment(self) -> None:
        msg = EmailMessage()
        msg["Subject"] = "Test"
        msg.set_content("Plain")
        msg.add_alternative("<b>HTML</b>", subtype="html")
        msg.add_attachment(b"DATA", maintype="application", subtype="octet-stream", filename="a.bin")
        raw = msg.as_bytes()

        payload = to_hyvor_payload(
            envelope_from="[email protected]",
            envelope_to=["[email protected]"],
            raw_bytes=raw,
        )
        self.assertIn("body_text", payload)
        self.assertIn("body_html", payload)
        self.assertIn("attachments", payload)
        att = payload["attachments"][0]
        self.assertEqual(att["name"], "a.bin")
        self.assertEqual(base64.b64decode(att["content"]), b"DATA")
