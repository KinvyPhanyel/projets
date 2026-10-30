import unittest
from advanced import bellman_ford


class Tests(unittest.TestCase):
    def test_negative_edge_and_blocked_node(self):
        graph = {"a": {"b": 4, "c": 9}, "b": {"c": -1}, "c": {}}
        self.assertEqual(bellman_ford(graph, "a", "c")["cost"], 3)
        self.assertEqual(bellman_ford(graph, "a", "c", ["b"])["cost"], 9)

    def test_relevant_negative_cycle(self):
        with self.assertRaises(ValueError):
            bellman_ford({"a": {"b": 1}, "b": {"b": -1, "c": 1}, "c": {}}, "a", "c")

    def test_irrelevant_cycle_and_unreachable(self):
        graph = {"a": {"b": 1, "c": 3}, "b": {"b": -1}, "c": {}, "d": {}}
        self.assertEqual(bellman_ford(graph, "a", "c")["cost"], 3)
        self.assertIsNone(bellman_ford(graph, "a", "d")["cost"])


if __name__ == "__main__":
    unittest.main()
