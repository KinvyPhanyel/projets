import unittest
from advanced import Snapshots
from pathlib import Path
import tempfile


class Tests(unittest.TestCase):
    def setUp(self):
        self.s = Snapshots()

    def tearDown(self):
        self.s.close()

    def test_deduplicate_and_restore_bytes(self):
        self.s.create("v1", {"a": b"hello", "sub/b": b"hello"})
        self.s.create("v2", {"a": b"changed"})
        self.assertEqual(self.s.stats(), {"snapshots": 2, "unique_blobs": 2, "file_references": 3})
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "restored"
            self.assertEqual(self.s.restore("v1", target), 2)
            self.assertEqual((target / "sub/b").read_bytes(), b"hello")
            with self.assertRaises(ValueError):
                self.s.restore("v1", target)

    def test_corruption_detected_before_restore(self):
        self.s.create("v1", {"a": b"hello"})
        self.s.db.execute("UPDATE blobs SET data=?", (b"corrupt",))
        self.s.db.commit()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "restored"
            with self.assertRaises(ValueError):
                self.s.restore("v1", target)
            self.assertFalse(target.exists())

    def test_path_traversal_rejected(self):
        for name in ["../escape", "/absolute", "a/../b", "./a"]:
            with self.assertRaises(ValueError):
                self.s.create("bad", {name: b"data"})
        self.assertEqual(self.s.stats()["snapshots"], 0)


class PortablePaths(unittest.TestCase):
    def test_null_and_windows_paths_rejected(self):
        for name in ["a\\b", "C:/escape", "bad" + chr(0) + "name"]:
            with self.assertRaises(ValueError):
                Snapshots.safe_path(name)

    def test_file_cannot_be_its_own_parent(self):
        service = Snapshots()
        try:
            with self.assertRaises(ValueError):
                service.create("bad", {"a": b"data", "a/b": b"data"})
            self.assertEqual(service.stats()["snapshots"], 0)
        finally:
            service.close()


if __name__ == "__main__":
    unittest.main()
