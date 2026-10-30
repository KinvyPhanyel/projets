import unittest
from core import EventStore


class Tests(unittest.TestCase):
    def setUp(self):
        self.s = EventStore()

    def tearDown(self):
        self.s.close()

    def test_projection_and_conflict(self):
        self.s.append("a", 0, [{"type": "deposit", "amount": 100}])
        with self.assertRaises(ValueError):
            self.s.append("a", 0, [{"type": "withdraw", "amount": 20}])
        self.s.append("a", 1, [{"type": "withdraw", "amount": 20}])
        self.assertEqual(self.s.project("a"), 80)

    def test_tamper_detection(self):
        self.s.append("a", 0, [{"type": "deposit", "amount": 100}])
        self.s.db.execute("UPDATE events SET payload='{}'")
        self.assertFalse(self.s.verify("a"))
        with self.assertRaises(ValueError):
            self.s.project("a")

    def test_stream_independence(self):
        self.s.append("a", 0, [{"type": "deposit", "amount": 10}])
        self.s.append("b", 0, [{"type": "deposit", "amount": 20}])
        self.assertEqual(self.s.project("a"), 10)
        self.assertEqual(self.s.project("b"), 20)


if __name__ == "__main__":
    unittest.main()
