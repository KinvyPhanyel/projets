import unittest
from core import Ledger


class Tests(unittest.TestCase):
    def setUp(self):
        self.s = Ledger()
        self.entries = [{"account": "cash", "amount": 100}, {"account": "capital", "amount": -100}]

    def tearDown(self):
        self.s.close()

    def test_balance_and_idempotence(self):
        self.assertTrue(self.s.post("a", self.entries))
        self.assertFalse(self.s.post("a", self.entries))
        self.assertEqual(self.s.balances(), {"capital": -100, "cash": 100})

    def test_reversal(self):
        self.s.post("a", self.entries)
        self.s.reverse("a", "rev")
        self.s.reverse("a", "rev")
        self.assertEqual(self.s.balances(), {"capital": 0, "cash": 0})

    def test_reject_unbalanced_and_float(self):
        for entries in [
            [{"account": "a", "amount": 1}, {"account": "b", "amount": -2}],
            [{"account": "a", "amount": 1.0}, {"account": "b", "amount": -1}],
        ]:
            with self.assertRaises(ValueError):
                self.s.post("bad", entries)
        self.assertEqual(self.s.balances(), {})


if __name__ == "__main__":
    unittest.main()
