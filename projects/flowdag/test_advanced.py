import unittest
from advanced import execute


class Tests(unittest.TestCase):
    def test_dependency_outputs(self):
        result = execute({"a": [], "b": ["a"]}, {"a": lambda _: 3, "b": lambda x: x["a"] * 2})
        self.assertEqual(result["outputs"]["b"], 6)
        self.assertEqual(result["states"], {"a": "done", "b": "done"})

    def test_retry_and_skip(self):
        count = [0]

        def fail(_):
            count[0] += 1
            raise ValueError("failure")

        result = execute(
            {"a": [], "b": ["a"], "c": []},
            {"a": fail, "b": lambda _: 0, "c": lambda _: 7},
            retries=1,
        )
        self.assertEqual(count[0], 2)
        self.assertEqual(result["states"], {"a": "failed", "b": "skipped", "c": "done"})

    def test_cycle_rejected_before_handlers(self):
        calls = []
        with self.assertRaises(ValueError):
            execute({"a": ["a"]}, {"a": lambda _: calls.append(1)})
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
