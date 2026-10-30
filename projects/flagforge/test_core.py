import unittest
from core import FlagEngine


class Tests(unittest.TestCase):
    def test_rollout_endpoints_and_stability(self):
        self.assertFalse(FlagEngine({"f": {"rollout": 0}}).evaluate("f", "a", {})["value"])
        e = FlagEngine({"f": {"rollout": 100}})
        self.assertTrue(e.evaluate("f", "a", {})["value"])
        self.assertEqual(e.evaluate("f", "a", {}), e.evaluate("f", "a", {}))

    def test_rule_and_disabled_precedence(self):
        rules = [{"attribute": "plan", "op": "eq", "value": "beta", "result": True}]
        self.assertTrue(
            FlagEngine({"f": {"rollout": 0, "rules": rules}}).evaluate("f", "a", {"plan": "beta"})[
                "value"
            ]
        )
        self.assertFalse(
            FlagEngine({"f": {"enabled": False, "rules": rules}}).evaluate(
                "f", "a", {"plan": "beta"}
            )["value"]
        )

    def test_unknown_and_invalid(self):
        self.assertEqual(FlagEngine({}).evaluate("missing", "a", {})["reason"], "unknown_flag")
        with self.assertRaises(ValueError):
            FlagEngine({"f": {"rollout": 101}})


if __name__ == "__main__":
    unittest.main()
