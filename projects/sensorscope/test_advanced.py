import unittest
from advanced import detect_stream


class Tests(unittest.TestCase):
    def events(self, values, sensor="a"):
        return [
            {"sensor": sensor, "timestamp": f"2026-10-30T10:00:{i:02}Z", "value": v}
            for i, v in enumerate(values)
        ]

    def test_open_and_recover(self):
        result = detect_stream(self.events([20, 20, 20, 50, 50, 20, 20]))
        self.assertEqual([a["event"] for a in result["alerts"]], ["opened", "recovered"])
        self.assertNotIn(50, result["baselines"]["a"])

    def test_sensor_isolation(self):
        result = detect_stream(self.events([20] * 3) + self.events([90] * 3, "b"))
        self.assertEqual(result["alerts"], [])
        self.assertEqual(result["baselines"]["b"], [90] * 3)

    def test_duplicate_timestamp_rejected(self):
        events = self.events([20])
        events += events
        with self.assertRaises(ValueError):
            detect_stream(events)


if __name__ == "__main__":
    unittest.main()
