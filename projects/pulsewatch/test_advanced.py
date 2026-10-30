import unittest
from advanced import monitor


class Tests(unittest.TestCase):
    def test_retry_recovers_and_preserves_order(self):
        counts = {}

        def fake(url, timeout):
            counts[url] = counts.get(url, 0) + 1
            return {
                "healthy": counts[url] == 2,
                "status": 200 if counts[url] == 2 else 503,
                "latency_ms": 2,
                "error": None,
            }

        result = monitor(["a", "b"], probe_fn=fake, sleep=lambda _: None)
        self.assertEqual(result["summary"]["healthy"], 2)
        self.assertEqual([r["attempts"] for r in result["targets"]], [2, 2])
        self.assertEqual([r["url"] for r in result["targets"]], ["a", "b"])

    def test_no_retry_after_success(self):
        fake = lambda url, t: {"healthy": True, "status": 200, "latency_ms": 4, "error": None}
        self.assertEqual(monitor(["a"], probe_fn=fake)["targets"][0]["attempts"], 1)

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            monitor(["a"], workers=0)


if __name__ == "__main__":
    unittest.main()
