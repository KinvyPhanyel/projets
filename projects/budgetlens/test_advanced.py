import unittest
from advanced import monthly


class Tests(unittest.TestCase):
    def test_refund_and_month_filter(self):
        rows = [
            {"date": "2026-10-01", "amount": "10.10", "kind": "expense", "category": "food"},
            {"date": "2026-10-02", "amount": "0.10", "kind": "refund", "category": "food"},
            {"date": "2026-11-01", "amount": "999", "kind": "expense", "category": "food"},
        ]
        result = monthly(rows, {"food": "20"}, "2026-10-15")
        self.assertEqual(result["net_expenses"], "10.00")
        self.assertEqual(result["included_transactions"], 2)
        self.assertEqual(result["categories"][0]["projected_month_end"], "20.67")

    def test_leap_year_projection(self):
        rows = [{"date": "2024-02-01", "amount": "10", "kind": "expense", "category": "food"}]
        self.assertEqual(
            monthly(rows, {}, "2024-02-10")["categories"][0]["projected_month_end"], "29.00"
        )

    def test_invalid_precision(self):
        with self.assertRaises(ValueError):
            monthly([], {"food": "1.001"}, "2026-10-15")


if __name__ == "__main__":
    unittest.main()
