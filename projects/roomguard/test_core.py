import unittest
from core import Reservations


class Tests(unittest.TestCase):
    def setUp(self):
        self.s = Reservations()

    def tearDown(self):
        self.s.close()

    def reserve(self, id="r", start="09", end="10"):
        return self.s.reserve(
            id, "room", "alice", f"2026-11-01T{start}:00:00Z", f"2026-11-01T{end}:00:00Z"
        )

    def test_adjacent_and_overlap(self):
        self.reserve()
        self.reserve("r2", "10", "11")
        with self.assertRaises(ValueError):
            self.reserve("r3", "09", "11")
        self.assertEqual(len(self.s.list()), 2)

    def test_cancel_and_retry(self):
        self.reserve()
        self.reserve()
        self.assertEqual(len(self.s.list()), 1)
        with self.assertRaises(ValueError):
            self.s.cancel("r", "bob")
        self.s.cancel("r", "alice")
        self.reserve("r2")
        self.assertEqual(sum(r["active"] for r in self.s.list()), 1)

    def test_content_conflict_and_timezone(self):
        self.reserve()
        with self.assertRaises(ValueError):
            self.reserve("r", "10", "11")
        with self.assertRaises(ValueError):
            self.s.reserve("x", "room", "a", "2026-11-01T11:00", "2026-11-01T12:00")


class ConcurrentReservations(unittest.TestCase):
    def test_two_writers_cannot_double_book(self):
        import tempfile
        import threading
        from pathlib import Path
        from concurrent.futures import ThreadPoolExecutor

        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "rooms.db")
            init = Reservations(path)
            init.close()
            barrier = threading.Barrier(2)

            def reserve(identifier):
                service = Reservations(path)
                try:
                    barrier.wait(timeout=3)
                    service.reserve(
                        identifier, "room", "alice", "2026-11-01T09:00Z", "2026-11-01T10:00Z"
                    )
                    return True
                except ValueError:
                    return False
                finally:
                    service.close()

            with ThreadPoolExecutor(max_workers=2) as pool:
                self.assertEqual(sum(pool.map(reserve, ["a", "b"])), 1)


if __name__ == "__main__":
    unittest.main()
