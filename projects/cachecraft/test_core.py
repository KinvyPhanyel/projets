import unittest
from core import Cache
from concurrent.futures import ThreadPoolExecutor
import threading


class Tests(unittest.TestCase):
    def test_lru_weight_and_expiration(self):
        now = [0]
        s = Cache(2, 10, clock=lambda: now[0])
        s.put("a", 1)
        s.put("b", 2)
        s.get_or_load("a", lambda: 99)
        s.put("c", 3)
        self.assertEqual(s.snapshot()["keys_lru_to_mru"], ["a", "c"])
        now[0] = 10
        self.assertEqual(s.snapshot()["weight"], 0)

    def test_single_flight(self):
        s = Cache()
        start = threading.Event()
        release = threading.Event()
        calls = []

        def loader():
            calls.append(1)
            start.set()
            if not release.wait(3):
                raise RuntimeError("test timeout")
            return 42

        with ThreadPoolExecutor(max_workers=8) as pool:
            first = pool.submit(s.get_or_load, "x", loader)
            self.assertTrue(start.wait(3))
            others = [pool.submit(s.get_or_load, "x", loader) for _ in range(7)]
            release.set()
            self.assertEqual(first.result(), 42)
            self.assertTrue(all(f.result() == 42 for f in others))
        self.assertEqual(len(calls), 1)

    def test_failed_load_can_retry(self):
        s = Cache()
        with self.assertRaises(ValueError):
            s.get_or_load("x", lambda: (_ for _ in ()).throw(ValueError("failure")))
        self.assertEqual(s.get_or_load("x", lambda: 7), 7)


if __name__ == "__main__":
    unittest.main()
