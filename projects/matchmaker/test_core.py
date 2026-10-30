import unittest
from core import Matcher


class Tests(unittest.TestCase):
    def test_stable_solution_and_blocking_verifier(self):
        s = Matcher(
            {"a": ["x", "y"], "b": ["x", "y"]}, {"x": ["b", "a"], "y": ["a", "b"]}, {"x": 1, "y": 1}
        )
        result = s.solve()
        self.assertEqual(result["assignments"], {"a": "y", "b": "x"})
        self.assertEqual(result["blocking_pairs"], [])
        self.assertIn(["b", "x"], s.blocking({"a": "x", "b": "y"}))

    def test_unacceptable_and_zero_capacity(self):
        s = Matcher({"a": ["x"]}, {"x": []}, {"x": 1})
        self.assertIsNone(s.solve()["assignments"]["a"])
        s = Matcher({"a": ["x"]}, {"x": ["a"]}, {"x": 0})
        self.assertIsNone(s.solve()["assignments"]["a"])

    def test_duplicate_preference_rejected(self):
        with self.assertRaises(ValueError):
            Matcher({"a": ["x", "x"]}, {"x": ["a"]}, {"x": 1})


if __name__ == "__main__":
    unittest.main()
