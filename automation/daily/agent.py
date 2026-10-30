"""Daily portfolio checks and truthful maintenance reports; no empty commits."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import time
from zoneinfo import ZoneInfo

CHECK_FAILED = 20
INFRA_FAILED = 1


class AgentError(RuntimeError):
    pass


def git(repo, *args, timeout=45):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_SSH_COMMAND="ssh -o BatchMode=yes")
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise AgentError("Délai Git dépassé") from error
    if result.returncode:
        # Never echo remote URLs, credential helper errors, or tokens into reports.
        raise AgentError("Échec Git : " + args[0] + " (voir authentification et état du dépôt)")
    return result.stdout.strip()


def load_config(path):
    cfg = json.loads(Path(path).read_text())
    repo = Path(cfg["repository"]).expanduser().resolve()
    state = Path(cfg["state_directory"]).expanduser().resolve()
    if not repo.is_dir() or not (repo / ".git").exists():
        raise AgentError("Un clone Git dédié est requis")
    if state == repo or repo in state.parents:
        raise AgentError("Le dossier d’état doit être hors du dépôt")
    branch = cfg.get("branch", "portfolio-projets")
    if not isinstance(branch, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9/_-]*", branch):
        raise AgentError("Branche invalide")
    if ".." in branch or branch.endswith("/") or "//" in branch:
        raise AgentError("Branche invalide")
    name = cfg.get("author_name", "").strip()
    email = cfg.get("author_email", "").strip()
    if not name or "\n" in name or not re.fullmatch(r"[^\s<>]+@[^\s<>]+", email):
        raise AgentError("Nom et adresse Git associés au compte requis")
    timezone = ZoneInfo(cfg.get("timezone", "Africa/Douala"))
    retain = cfg.get("retention_days", 90)
    if type(retain) is not int or not 7 <= retain <= 365:
        raise AgentError("Rétention entre 7 et 365 jours requise")
    return {
        **cfg,
        "repository": repo,
        "state_directory": state,
        "branch": branch,
        "author_name": name,
        "author_email": email,
        "timezone": timezone,
        "retention_days": retain,
    }


@contextmanager
def lock(state):
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (state / "agent.lock").open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
        else:
            try:
                yield True
            finally:
                fcntl.flock(stream, fcntl.LOCK_UN)


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(data, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def check_repository(repo, branch):
    if git(repo, "rev-parse", "--show-toplevel") != str(repo):
        raise AgentError("La racine Git doit correspondre au clone configuré")
    if git(repo, "status", "--porcelain", "--untracked-files=all"):
        raise AgentError("Clone modifié : arrêt sans écraser les fichiers")
    if git(repo, "branch", "--show-current") != branch:
        raise AgentError("Branche locale différente de la configuration")


def synchronize(repo, branch):
    check_repository(repo, branch)
    git(repo, "fetch", "--no-tags", "origin", branch)
    remote = git(repo, "rev-parse", "FETCH_HEAD")
    ahead = int(git(repo, "rev-list", "--count", remote + "..HEAD"))
    behind = int(git(repo, "rev-list", "--count", "HEAD.." + remote))
    if ahead and behind:
        raise AgentError("Historique divergent : intervention requise, aucun reset ni force-push")
    if ahead:
        # A previous push may have failed. Never publish arbitrary local commits.
        for commit in git(repo, "rev-list", remote + "..HEAD").splitlines():
            changed = git(
                repo, "diff-tree", "--no-commit-id", "--name-only", "-r", commit
            ).splitlines()
            subject = git(repo, "show", "-s", "--format=%s", commit)
            if (
                not changed
                or not subject.startswith("chore(maintenance): verify portfolio on ")
                or any(
                    not re.fullmatch(r"maintenance/daily/\d{4}-\d{2}-\d{2}\.json", p)
                    for p in changed
                )
            ):
                raise AgentError("Commits locaux non reconnus : publication refusée")
        push(repo, branch)
    elif behind:
        git(repo, "merge", "--ff-only", remote)


def push(repo, branch):
    git(repo, "push", "origin", "HEAD:refs/heads/" + branch)


def execute_checks(repo, state, timeout=300):
    """Timeout kills the whole check process group, including nested test workers."""
    with tempfile.TemporaryDirectory(dir=state) as temp:
        output = Path(temp) / "results.json"
        log_path = state / "last-check.log"
        with log_path.open("w") as log:
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(repo / "automation/check_portfolio.py"),
                    "--output",
                    str(output),
                ],
                cwd=repo,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
            )
            try:
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                return {"status": "failed", "reason": "check_timeout"}
        if code:
            return {"status": "failed", "reason": "checks_failed", "exit_code": code}
        try:
            result = json.loads(output.read_text())
            required = ["projects_checked", "unit_tests_passed", "lab_tests_passed"]
            if result["status"] != "passed" or any(
                type(result[k]) is not int or result[k] < 1 for k in required
            ):
                raise ValueError("Incomplete checks")
            return {
                "status": "passed",
                **{k: result[k] for k in required},
                "result_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                **(
                    {"maintenance_tests_passed": result["maintenance_tests_passed"]}
                    if "maintenance_tests_passed" in result
                    else {}
                ),
            }
        except (ValueError, KeyError, OSError):
            return {"status": "failed", "reason": "invalid_check_report"}


def record_report(repo, day, source, checks, retention, author):
    folder = repo / "maintenance/daily"
    target = folder / (day + ".json")
    identity = {
        "day": day,
        "source_commit": source,
        "automation": "portfolio-maintenance",
        "checks": checks,
    }
    # No timestamps/counters whose only purpose would be to force a new commit.
    if target.exists() and json.loads(target.read_text()) == identity:
        return False
    atomic_json(target, identity)
    cutoff = datetime.strptime(day, "%Y-%m-%d").date() - timedelta(days=retention - 1)
    for path in folder.glob("*.json"):
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}\.json", path.name):
            try:
                date = datetime.strptime(path.stem, "%Y-%m-%d").date()
            except ValueError:
                continue
            if date < cutoff:
                path.unlink()
    git(repo, "add", "--", "maintenance/daily")
    if not git(repo, "diff", "--cached", "--name-only"):
        return False
    staged = git(repo, "diff", "--cached", "--name-only").splitlines()
    if any(not re.fullmatch(r"maintenance/daily/\d{4}-\d{2}-\d{2}\.json", name) for name in staged):
        raise AgentError("Fichier hors rapport dans l’index : commit refusé")
    name, email = author
    git(
        repo,
        "-c",
        "user.name=" + name,
        "-c",
        "user.email=" + email,
        "commit",
        "-m",
        f"chore(maintenance): verify portfolio on {day}",
    )
    return True


def run(config, offline=False, now=None):
    cfg = load_config(config)
    state = cfg["state_directory"]
    repo = cfg["repository"]
    branch = cfg["branch"]
    with lock(state) as acquired:
        if not acquired:
            print("Une exécution est déjà active ; aucune nouvelle tâche lancée.")
            return 0
        check_repository(repo, branch)
        if not offline:
            synchronize(repo, branch)
        source = git(repo, "log", "-1", "--format=%H", "--", ".", ":(exclude)maintenance/daily")
        day = (now or datetime.now(cfg["timezone"])).astimezone(cfg["timezone"]).date().isoformat()
        today = repo / "maintenance/daily" / (day + ".json")
        if today.exists():
            previous = json.loads(today.read_text())
            if (
                previous.get("source_commit") == source
                and previous.get("checks", {}).get("status") == "passed"
            ):
                atomic_json(
                    state / "last-run.json",
                    {"day": day, "status": "already_verified", "published": not offline},
                )
                return 0
        started = time.monotonic()
        checks = execute_checks(repo, state)
        # A check must not modify source files. Reports are the only writable Git scope.
        check_repository(repo, branch)
        committed = record_report(
            repo,
            day,
            source,
            checks,
            cfg["retention_days"],
            (cfg["author_name"], cfg["author_email"]),
        )
        if not offline:
            push(repo, branch)
        atomic_json(
            state / "last-run.json",
            {
                "day": day,
                "status": checks["status"],
                "committed": committed,
                "published": not offline,
                "duration_seconds": round(time.monotonic() - started, 2),
            },
        )
        print(
            json.dumps(
                {
                    "day": day,
                    "status": checks["status"],
                    "committed": committed,
                    "published": not offline,
                },
                ensure_ascii=False,
            )
        )
        return 0 if checks["status"] == "passed" else CHECK_FAILED


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument(
        "--offline", action="store_true", help="Valider et committer localement, sans réseau"
    )
    args = parser.parse_args()
    try:
        raise SystemExit(run(args.config, args.offline))
    except (AgentError, OSError, ValueError, KeyError) as error:
        print("Agent interrompu : " + str(error), file=sys.stderr)
        raise SystemExit(INFRA_FAILED)
