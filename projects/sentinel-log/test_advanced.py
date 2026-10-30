import unittest
from advanced import correlate


class Tests(unittest.TestCase):
    def event(self, i, user="alice", status="failed"):
        return {
            "timestamp": f"2026-10-30T10:00:{i:02}Z",
            "ip": "192.0.2.10",
            "user": user,
            "status": status,
        }

    def test_correlated_rules(self):
        events = [self.event(0), self.event(1), self.event(2), self.event(3, status="success")]
        result = correlate(list(reversed(events)))
        self.assertEqual(
            [a["rule"] for a in result["alerts"]], ["brute_force", "success_after_failures"]
        )

    def test_spray_and_trusted(self):
        events = [self.event(i, str(i)) for i in range(3)]
        self.assertEqual(correlate(events)["alerts"][0]["rule"], "password_spray")
        self.assertEqual(correlate(events, trusted=["192.0.2.0/24"])["events_ignored"], 3)

    def test_window_expires(self):
        self.assertEqual(correlate([self.event(i) for i in (0, 10, 20)], window=5)["alerts"], [])


if __name__ == "__main__":
    unittest.main()
