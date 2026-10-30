"""HTTP integration checks for the local project lab."""

import http.client
import json
from pathlib import Path
import threading
import unittest
from serve_lab import create_server

ROOT = Path(__file__).resolve().parents[1]


class LabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(0)
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()
        cls.scenarios = json.loads((ROOT / "site/scenarios.json").read_text())

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join()

    def request(self, body, headers=None, path="/api/run"):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=15)
        try:
            connection.request(
                "POST", path, body, headers=headers or {"Content-Type": "application/json"}
            )
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_all_22_projects_execute_via_http(self):
        self.assertEqual(len(self.scenarios), 22)
        for slug, scenario in self.scenarios.items():
            with self.subTest(project=slug):
                code, payload = self.request(json.dumps({"project": slug, "scenario": scenario}))
                self.assertEqual(code, 200, payload)
                self.assertIsInstance(payload["result"], dict)

    def test_unknown_project_and_traversal_rejected(self):
        for slug in ["missing", "../../automation/serve_lab"]:
            code, _ = self.request(json.dumps({"project": slug, "scenario": {}}))
            self.assertEqual(code, 400)

    def test_cross_origin_and_host_rejected(self):
        body = json.dumps({"project": "taskboard", "scenario": {"commands": []}})
        code, _ = self.request(
            body, {"Content-Type": "application/json", "Origin": "https://example.com"}
        )
        self.assertEqual(code, 403)
        code, _ = self.request(body, {"Content-Type": "application/json", "Host": "example.com"})
        self.assertEqual(code, 403)

    def test_form_content_type_rejected(self):
        code, _ = self.request("{}", {"Content-Type": "text/plain"})
        self.assertEqual(code, 415)

    def test_invalid_json_and_size_rejected(self):
        code, _ = self.request("{bad")
        self.assertEqual(code, 400)
        code, _ = self.request("x" * 512001)
        self.assertEqual(code, 413)

    def test_business_error_has_no_traceback(self):
        body = {
            "project": "ledgercore",
            "scenario": {
                "commands": [
                    {
                        "action": "post",
                        "id": "x",
                        "entries": [{"account": "a", "amount": 1}, {"account": "b", "amount": -2}],
                    }
                ]
            },
        }
        code, payload = self.request(json.dumps(body))
        self.assertEqual(code, 422)
        self.assertIn("déséquilibrée", payload["error"])
        self.assertNotIn("Traceback", payload["error"])

    def test_pulsewatch_uses_only_fixed_local_targets(self):
        body = {
            "project": "pulsewatch",
            "scenario": {"targets": ["https://example.invalid/"], "attempts": 1},
        }
        code, payload = self.request(json.dumps(body))
        self.assertEqual(code, 200)
        targets = payload["result"]["targets"]
        self.assertEqual(payload["result"]["summary"]["healthy"], 1)
        self.assertTrue(all(t["url"].startswith("http://127.0.0.1:") for t in targets))

    def test_static_catalogue_served(self):
        for path in ["/", "/projects.json", "/scenarios.json", "/demo-results.json"]:
            connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
            try:
                connection.request("GET", path)
                response = connection.getresponse()
                content = response.read()
                self.assertEqual(response.status, 200)
                self.assertTrue(content)
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
