import unittest
from advanced import BM25


class Tests(unittest.TestCase):
    def setUp(self):
        self.s = BM25(
            {"a": "data pipeline security", "b": "data security pipeline", "c": "network"}
        )

    def test_phrase_and_conjunction(self):
        self.assertEqual([r["document"] for r in self.s.search('"data pipeline"')], ["a"])
        self.assertEqual(len(self.s.search("data security", mode="and")), 2)
        self.assertEqual(self.s.search("data absent", mode="and"), [])

    def test_export_and_restore(self):
        restored = BM25.restore(self.s.export())
        self.assertEqual(restored.search("pipeline"), self.s.search("pipeline"))

    def test_empty_and_unknown(self):
        self.assertEqual(self.s.search(""), [])
        self.assertEqual(self.s.search("unknown"), [])


if __name__ == "__main__":
    unittest.main()
