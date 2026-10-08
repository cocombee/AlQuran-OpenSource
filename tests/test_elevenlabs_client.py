# SPDX-License-Identifier: MIT
"""Offline tests: never call a paid service or read real credentials."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("elevenlabs_client", Path(__file__).resolve().parents[1] / "tools/elevenlabs_client.py")
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)

class AuditionStorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.repo = self.root / "repository"
        self.repo.mkdir()
        self.prompt = self.repo / "approved.txt"
        self.prompt.write_text("Synthetic narration for an offline test.", encoding="utf-8")
        self.auditions = self.root / "temporary auditions"
        self.auditions.mkdir()
        patcher = patch.object(client, "TASK_ROOT", self.repo)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_external_audition_has_private_receipt_and_one_request(self):
        prefix = self.auditions / "take"
        with patch.object(client, "request", return_value=(b"synthetic audio", {"content-type": "audio/mpeg", "request-id": "synthetic"})) as request:
            result = client.audition(self.prompt, prefix, 1)
        request.assert_called_once()
        self.assertEqual(result["human_approval"], "pending")
        self.assertEqual(Path(result["takes"][0]["file"]).read_bytes(), b"synthetic audio")
        saved = json.loads(Path(str(prefix) + " - API Receipt.json").read_text())
        self.assertEqual(saved["takes"], result["takes"])
        self.assertEqual(saved["prompt_file"], str(self.prompt))

    def test_in_repository_output_is_rejected_before_request(self):
        with patch.object(client, "request") as request:
            with self.assertRaisesRegex(RuntimeError, "outside the repository"):
                client.audition(self.prompt, self.repo / "audition", 1)
        request.assert_not_called()

    def test_existing_receipt_is_not_overwritten(self):
        prefix = self.auditions / "take"
        receipt = Path(str(prefix) + " - API Receipt.json")
        receipt.write_text("preserve me")
        with patch.object(client, "request") as request:
            with self.assertRaisesRegex(RuntimeError, "already exists"):
                client.audition(self.prompt, prefix, 1)
        request.assert_not_called()
        self.assertEqual(receipt.read_text(), "preserve me")

    def test_failure_does_not_retry_and_retains_pending_receipt(self):
        prefix = self.auditions / "take"
        with patch.object(client, "request", side_effect=RuntimeError("synthetic network failure")) as request:
            with self.assertRaisesRegex(RuntimeError, "network failure"):
                client.audition(self.prompt, prefix, 1)
        request.assert_called_once()
        saved = json.loads(Path(str(prefix) + " - API Receipt.json").read_text())
        self.assertEqual(saved["takes"], [])
        self.assertEqual(saved["human_approval"], "pending")

    def test_multiple_paid_takes_rejected_even_via_python_api(self):
        with patch.object(client, "request") as request:
            with self.assertRaisesRegex(RuntimeError, "exactly one"):
                client.audition(self.prompt, self.auditions / "take", 2)
        request.assert_not_called()

if __name__ == "__main__":
    unittest.main()
