import unittest
from core import Policy


class Tests(unittest.TestCase):
    def test_inheritance_and_deny(self):
        s = Policy(
            {"reader": [], "admin": ["reader"]},
            [
                {"role": "reader", "action": "read", "resource": "*", "effect": "allow"},
                {"role": "*", "action": "*", "resource": "secret", "effect": "deny"},
            ],
        )
        self.assertTrue(s.decide(["admin"], "read", "public", {})["allowed"])
        self.assertEqual(s.decide(["admin"], "read", "secret", {})["reason"], "explicit_deny")

    def test_missing_attribute_defaults_to_deny(self):
        s = Policy(
            {"r": []},
            [
                {
                    "role": "r",
                    "action": "*",
                    "resource": "*",
                    "effect": "allow",
                    "conditions": [{"attribute": "team", "op": "eq", "value": None}],
                }
            ],
        )
        self.assertFalse(s.decide(["r"], "read", "x", {})["allowed"])

    def test_cycle_rejected(self):
        with self.assertRaises(ValueError):
            Policy({"a": ["b"], "b": ["a"]}, [])


if __name__ == "__main__":
    unittest.main()
