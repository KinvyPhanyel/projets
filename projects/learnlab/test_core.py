import unittest
from core import Logistic, split, metrics


class Tests(unittest.TestCase):
    def test_learning_and_constant_column(self):
        model = Logistic(epochs=500).fit([[-2, 1], [-1, 1], [1, 1], [2, 1]], [0, 0, 1, 1])
        p = model.predict_proba([[-2, 1], [2, 1]])
        self.assertLess(p[0], 0.2)
        self.assertGreater(p[1], 0.8)
        self.assertEqual(model.scale[1], 1)

    def test_split_reproducible_and_no_overlap(self):
        x = [[i] for i in range(8)]
        y = [0] * 4 + [1] * 4
        a = split(x, y)
        self.assertEqual(a, split(x, y))
        self.assertFalse({r[0] for r in a[0]} & {r[0] for r in a[2]})
        self.assertEqual(set(a[1]), {0, 1})
        self.assertEqual(set(a[3]), {0, 1})

    def test_metrics_and_reject_bad_input(self):
        result = metrics([0, 1], [0.1, 0.9])
        self.assertEqual(result["accuracy"], 1)
        with self.assertRaises(ValueError):
            Logistic().fit([[float("nan")], [1]], [0, 1])


if __name__ == "__main__":
    unittest.main()
