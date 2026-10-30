import unittest
from advanced import pipeline


class Tests(unittest.TestCase):
    def setUp(self):
        self.schema = {
            "id": {"type": "text", "lowercase": True},
            "value": {"type": "number", "min": 0},
        }

    def test_normalize_deduplicate_and_quality(self):
        result = pipeline(
            [{"id": " A ", "value": 1}, {"id": "a", "value": 2}, {"id": "b", "value": "NaN"}],
            self.schema,
            "id",
        )
        self.assertEqual(result["quality"]["valid"], 1)
        self.assertEqual(result["quality"]["invalid"], 2)
        self.assertEqual(result["accepted"][0], {"id": "a", "value": 1.0})

    def test_invalid_row_does_not_reserve_key(self):
        result = pipeline([{"id": "a", "value": -1}, {"id": "a", "value": 1}], self.schema, "id")
        self.assertEqual(result["quality"]["valid"], 1)

    def test_empty_quality(self):
        self.assertIsNone(pipeline([], self.schema, "id")["quality"]["valid_ratio"])


if __name__ == "__main__":
    unittest.main()
