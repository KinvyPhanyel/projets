import unittest
from core import TokenBuckets
from concurrent.futures import ThreadPoolExecutor


class Tests(unittest.TestCase):
    def test_refill_and_client_isolation(self):
        now = [0]
        s = TokenBuckets(1, 2, clock=lambda: now[0])
        self.assertTrue(s.acquire("a")["allowed"])
        self.assertFalse(s.acquire("a")["allowed"])
        self.assertTrue(s.acquire("b")["allowed"])
        now[0] = 0.5
        self.assertTrue(s.acquire("a")["allowed"])

    def test_atomic_concurrent_debit(self):
        s = TokenBuckets(5, 1, clock=lambda: 0)
        with ThreadPoolExecutor(max_workers=16) as p:
            decisions = list(p.map(lambda _: s.acquire("a")["allowed"], range(50)))
        self.assertEqual(sum(decisions), 5)

    def test_no_eviction_of_depleted_client(self):
        s = TokenBuckets(1, 1, clock=lambda: 0, max_clients=1)
        s.acquire("a")
        self.assertEqual(s.acquire("b")["reason"], "client_capacity")
        self.assertFalse(s.acquire("a")["allowed"])


if __name__ == "__main__":
    unittest.main()
