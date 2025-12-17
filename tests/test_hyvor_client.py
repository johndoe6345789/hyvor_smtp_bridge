from __future__ import annotations

import json
import unittest
from unittest.mock import Mock, patch

from smtp_bridge.hyvor_client import HyvorClient


class TestHyvorClient(unittest.TestCase):
    @patch("smtp_bridge.hyvor_client.requests.post")
    def test_send_builds_request(self, post: Mock) -> None:
        resp = Mock()
        resp.status_code = 200
        resp.text = "ok"
        post.return_value = resp

        client = HyvorClient(base_url="https://hyvor.wardcrew.com", api_key="KEY")
        out = client.send({"from": "a", "to": ["b"]}, "idem")

        self.assertIs(out, resp)
        args, kwargs = post.call_args
        self.assertTrue(args[0].endswith("/api/console/sends"))
        self.assertIn("Authorization", kwargs["headers"])
        self.assertEqual(kwargs["headers"]["X-Idempotency-Key"], "idem")
        self.assertEqual(json.loads(kwargs["data"])["from"], "a")
