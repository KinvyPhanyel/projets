import unittest
from core import TaskBoard


class Tests(unittest.TestCase):
    def setUp(self):
        self.s = TaskBoard()

    def tearDown(self):
        self.s.close()

    def create(self):
        self.s.apply({"action": "create", "id": "t", "title": "Task", "actor": "a"})

    def test_workflow_and_audit(self):
        self.create()
        for version, status in enumerate(["doing", "review", "done"], 1):
            result = self.s.apply(
                {
                    "action": "transition",
                    "id": "t",
                    "version": version,
                    "status": status,
                    "actor": "a",
                }
            )
        self.assertEqual(result["version"], 4)
        self.assertEqual(len(self.s.snapshot()["audit"]), 4)

    def test_stale_version_rollback(self):
        self.create()
        with self.assertRaises(ValueError):
            self.s.apply(
                {"action": "transition", "id": "t", "version": 0, "status": "doing", "actor": "a"}
            )
        self.assertEqual(len(self.s.snapshot()["audit"]), 1)
        self.assertEqual(self.s.snapshot()["tasks"][0]["status"], "todo")

    def test_illegal_transition(self):
        self.create()
        with self.assertRaises(ValueError):
            self.s.apply(
                {"action": "transition", "id": "t", "version": 1, "status": "done", "actor": "a"}
            )


class PersistentVersions(unittest.TestCase):
    def test_versions_between_connections(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "board.db")
            first = TaskBoard(path)
            second = TaskBoard(path)
            try:
                first.apply({"action": "create", "id": "t", "title": "Task", "actor": "a"})
                first.apply(
                    {
                        "action": "transition",
                        "id": "t",
                        "version": 1,
                        "status": "doing",
                        "actor": "a",
                    }
                )
                with self.assertRaises(ValueError):
                    second.apply(
                        {
                            "action": "transition",
                            "id": "t",
                            "version": 1,
                            "status": "doing",
                            "actor": "b",
                        }
                    )
                self.assertEqual(second.snapshot()["tasks"][0]["version"], 2)
                self.assertEqual(len(second.snapshot()["audit"]), 2)
            finally:
                first.close()
                second.close()


if __name__ == "__main__":
    unittest.main()
