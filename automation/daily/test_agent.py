"""Isolated Git integration tests; all remotes are temporary local directories."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from datetime import datetime
from zoneinfo import ZoneInfo
import agent


def command(*args, cwd=None):
    return subprocess.run(
        list(map(str, args)), cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.state = self.root / "state"
        command("git", "init", "--initial-branch=portfolio-projets", self.repo)
        command("git", "config", "user.name", "Fixture", cwd=self.repo)
        command("git", "config", "user.email", "fixture@example.invalid", cwd=self.repo)
        (self.repo / "source.py").write_text('print("fixture")\n')
        command("git", "add", "source.py", cwd=self.repo)
        command("git", "commit", "-m", "Fixture source", cwd=self.repo)
        self.config = self.root / "config.json"
        self.config.write_text(
            json.dumps(
                {
                    "repository": str(self.repo),
                    "state_directory": str(self.state),
                    "author_name": "Maintenance Test",
                    "author_email": "fixture@example.invalid",
                }
            )
        )
        self.now = datetime(2026, 10, 30, 12, tzinfo=ZoneInfo("Africa/Douala"))
        self.result = {
            "status": "passed",
            "projects_checked": 22,
            "unit_tests_passed": 72,
            "lab_tests_passed": 8,
            "result_sha256": "test",
        }

    def tearDown(self):
        self.tmp.cleanup()

    def count(self):
        return int(command("git", "rev-list", "--count", "HEAD", cwd=self.repo))

    def remote(self):
        bare = self.root / "remote.git"
        command("git", "init", "--bare", bare)
        command("git", "remote", "add", "origin", bare, cwd=self.repo)
        command("git", "push", "origin", "portfolio-projets", cwd=self.repo)
        return bare

    def test_once_per_day_and_source_revision(self):
        with patch.object(agent, "execute_checks", return_value=self.result) as checks:
            self.assertEqual(agent.run(self.config, offline=True, now=self.now), 0)
            self.assertEqual(agent.run(self.config, offline=True, now=self.now), 0)
            self.assertEqual(checks.call_count, 1)
            self.assertEqual(self.count(), 2)
            report = json.loads((self.repo / "maintenance/daily/2026-10-30.json").read_text())
            self.assertEqual(report["checks"]["projects_checked"], 22)
            self.assertEqual(command("git", "status", "--porcelain", cwd=self.repo), "")

    def test_dirty_checkout_is_preserved(self):
        (self.repo / "source.py").write_text("user changes")
        with self.assertRaises(agent.AgentError):
            agent.run(self.config, offline=True, now=self.now)
        self.assertEqual((self.repo / "source.py").read_text(), "user changes")
        self.assertEqual(self.count(), 1)

    def test_failed_check_is_reported_and_not_empty_committed(self):
        failed = {"status": "failed", "reason": "checks_failed", "exit_code": 1}
        with patch.object(agent, "execute_checks", return_value=failed):
            self.assertEqual(agent.run(self.config, offline=True, now=self.now), 20)
            self.assertEqual(agent.run(self.config, offline=True, now=self.now), 20)
        self.assertEqual(self.count(), 2)
        self.assertEqual(
            json.loads((self.repo / "maintenance/daily/2026-10-30.json").read_text())["checks"][
                "status"
            ],
            "failed",
        )

    def test_pending_push_is_retried_without_duplicate_commit(self):
        bare = self.remote()
        with patch.object(agent, "execute_checks", return_value=self.result):
            with patch.object(agent, "push", side_effect=agent.AgentError("network failure")):
                with self.assertRaises(agent.AgentError):
                    agent.run(self.config, now=self.now)
        self.assertEqual(self.count(), 2)
        with patch.object(agent, "execute_checks") as checks:
            self.assertEqual(agent.run(self.config, now=self.now), 0)
            checks.assert_not_called()
        self.assertEqual(
            command("git", "rev-parse", "HEAD", cwd=self.repo),
            command("git", "rev-parse", "refs/heads/portfolio-projets", cwd=bare),
        )

    def test_unknown_local_commit_is_never_pushed(self):
        self.remote()
        (self.repo / "source.py").write_text("unreviewed")
        command("git", "add", "source.py", cwd=self.repo)
        command("git", "commit", "-m", "Local source change", cwd=self.repo)
        with self.assertRaises(agent.AgentError):
            agent.run(self.config, now=self.now)

    def test_report_retention(self):
        reportdir = self.repo / "maintenance/daily"
        reportdir.mkdir(parents=True)
        (reportdir / "2025-01-01.json").write_text("{}")
        command("git", "add", "maintenance", cwd=self.repo)
        command("git", "commit", "-m", "Old report", cwd=self.repo)
        with patch.object(agent, "execute_checks", return_value=self.result):
            agent.run(self.config, offline=True, now=self.now)
        self.assertFalse((reportdir / "2025-01-01.json").exists())
        self.assertTrue((reportdir / "2026-10-30.json").exists())

    def test_lock_prevents_second_run(self):
        with agent.lock(self.state):
            with patch.object(agent, "execute_checks") as checks:
                self.assertEqual(agent.run(self.config, offline=True, now=self.now), 0)
                checks.assert_not_called()

    def test_real_checker_runs_and_validates_output(self):
        folder = self.repo / "automation"
        folder.mkdir()
        (folder / "check_portfolio.py").write_text(
            'import json,sys\nfrom pathlib import Path\nPath(sys.argv[2]).write_text(json.dumps({"status":"passed","projects_checked":22,"unit_tests_passed":72,"lab_tests_passed":8}))\n'
        )
        self.state.mkdir()
        result = agent.execute_checks(self.repo, self.state)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(len(result["result_sha256"]), 64)

    def test_divergence_does_not_rebase_or_force_push(self):
        bare = self.remote()
        with patch.object(agent, "execute_checks", return_value=self.result):
            agent.run(self.config, offline=True, now=self.now)
        other = self.root / "other"
        command("git", "clone", "--branch", "portfolio-projets", bare, other)
        command("git", "config", "user.name", "Other", cwd=other)
        command("git", "config", "user.email", "other@example.invalid", cwd=other)
        (other / "source.py").write_text("remote change")
        command("git", "add", "source.py", cwd=other)
        command("git", "commit", "-m", "Remote source change", cwd=other)
        command("git", "push", "origin", "portfolio-projets", cwd=other)
        old = command("git", "rev-parse", "HEAD", cwd=self.repo)
        with self.assertRaises(agent.AgentError):
            agent.run(self.config, now=self.now)
        self.assertEqual(command("git", "rev-parse", "HEAD", cwd=self.repo), old)

    def test_timeout_stops_checker(self):
        folder = self.repo / "automation"
        folder.mkdir()
        (folder / "check_portfolio.py").write_text("import time\ntime.sleep(60)\n")
        self.state.mkdir()
        self.assertEqual(
            agent.execute_checks(self.repo, self.state, timeout=0.05)["reason"], "check_timeout"
        )

    def test_missing_report_is_not_a_pass(self):
        folder = self.repo / "automation"
        folder.mkdir()
        (folder / "check_portfolio.py").write_text('print("not a verification report")\n')
        self.state.mkdir()
        self.assertEqual(
            agent.execute_checks(self.repo, self.state)["reason"], "invalid_check_report"
        )

    def test_reverted_source_commits_are_not_published(self):
        self.remote()
        original = (self.repo / "source.py").read_text()
        for text in ["temporary change", original]:
            (self.repo / "source.py").write_text(text)
            command("git", "add", "source.py", cwd=self.repo)
            command("git", "commit", "-m", "Local change", cwd=self.repo)
        with self.assertRaises(agent.AgentError):
            agent.run(self.config, now=self.now)


if __name__ == "__main__":
    unittest.main()
