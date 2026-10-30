import unittest
from core import Queue


class Tests(unittest.TestCase):
    def setUp(self):
        self.s = Queue()

    def tearDown(self):
        self.s.close()

    def test_retry_and_dead_letter(self):
        self.s.enqueue("a", {}, 2)
        first = self.s.claim(0)
        self.s.finish("a", first["token"], 1, "error")
        self.assertIsNone(self.s.claim(1))
        second = self.s.claim(2)
        self.s.finish("a", second["token"], 3, "again")
        self.assertEqual(self.s.snapshot()[0]["status"], "dead")

    def test_stale_lease_rejected(self):
        self.s.enqueue("a", {})
        first = self.s.claim(0, 1)
        second = self.s.claim(1, 5)
        with self.assertRaises(ValueError):
            self.s.finish("a", first["token"], 2)
        self.s.finish("a", second["token"], 2)
        self.assertEqual(self.s.snapshot()[0]["status"], "done")

    def test_enqueue_idempotence(self):
        self.s.enqueue("a", {"n": 1})
        self.s.enqueue("a", {"n": 1})
        with self.assertRaises(ValueError):
            self.s.enqueue("a", {"n": 2})
        self.assertEqual(len(self.s.snapshot()), 1)


class ConcurrentQueue(unittest.TestCase):
    def test_one_active_claim_between_connections(self):
        import tempfile
        import threading
        from pathlib import Path
        from concurrent.futures import ThreadPoolExecutor

        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "jobs.db")
            init = Queue(path)
            init.enqueue("a", {})
            init.close()
            barrier = threading.Barrier(2)

            def claim(_):
                service = Queue(path)
                try:
                    barrier.wait(timeout=3)
                    return service.claim(0)
                finally:
                    service.close()

            with ThreadPoolExecutor(max_workers=2) as pool:
                self.assertEqual(sum(row is not None for row in pool.map(claim, range(2))), 1)

    def test_nonfinite_time_rejected(self):
        queue = Queue()
        try:
            with self.assertRaises(ValueError):
                queue.claim(float("nan"))
        finally:
            queue.close()


if __name__ == "__main__":
    unittest.main()
