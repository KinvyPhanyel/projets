import unittest
from advanced import Warehouse


class Tests(unittest.TestCase):
    def setUp(self):
        self.s = Warehouse()
        self.s.apply("r", "sku", 10, "a")

    def tearDown(self):
        self.s.close()

    def test_atomic_transfer_and_replay(self):
        self.assertTrue(self.s.apply("t", "sku", 4, "b", "a"))
        self.assertFalse(self.s.apply("t", "sku", 4, "b", "a"))
        self.assertEqual([r["quantity"] for r in self.s.snapshot()["stock"]], [6, 4])
        self.assertEqual(len(self.s.snapshot()["audit"]), 3)

    def test_insufficient_transfer_rolls_back_destination(self):
        before = self.s.snapshot()
        with self.assertRaises(ValueError):
            self.s.apply("t", "sku", 11, "b", "a")
        self.assertEqual(self.s.snapshot(), before)

    def test_idempotency_conflict(self):
        with self.assertRaises(ValueError):
            self.s.apply("r", "sku", 11, "a")


if __name__ == "__main__":
    unittest.main()
