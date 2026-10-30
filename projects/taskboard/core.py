"""Workflow de tâches : SQLite, concurrence optimiste et journal d'audit."""

import json
import sqlite3

TRANSITIONS = {
    "todo": {"doing"},
    "doing": {"todo", "review"},
    "review": {"doing", "done"},
    "done": set(),
}


class TaskBoard:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(
            """CREATE TABLE IF NOT EXISTS tasks(
            id TEXT PRIMARY KEY, title TEXT NOT NULL, owner TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'todo', version INTEGER NOT NULL DEFAULT 1);
            CREATE TABLE IF NOT EXISTS audit(
            seq INTEGER PRIMARY KEY, task_id TEXT NOT NULL, actor TEXT NOT NULL,
            action TEXT NOT NULL, payload TEXT NOT NULL);"""
        )

    def apply(self, command):
        actor = command.get("actor", "").strip()
        if not actor:
            raise ValueError("Actor requis")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            task_id = command["id"]
            if command["action"] == "create":
                title = command["title"].strip()
                owner = command.get("owner", actor).strip()
                if not title or not owner or not task_id:
                    raise ValueError("id, titre et responsable requis")
                self.db.execute(
                    "INSERT INTO tasks(id,title,owner) VALUES(?,?,?)", (task_id, title, owner)
                )
            elif command["action"] == "transition":
                task = self.db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
                if task is None:
                    raise ValueError("Tâche inconnue")
                if task["version"] != command["version"]:
                    raise ValueError("Version périmée")
                target = command["status"]
                if target not in TRANSITIONS[task["status"]]:
                    raise ValueError("Transition interdite")
                self.db.execute(
                    "UPDATE tasks SET status=?,version=version+1 WHERE id=?", (target, task_id)
                )
            else:
                raise ValueError("Action inconnue")
            self.db.execute(
                "INSERT INTO audit(task_id,actor,action,payload) VALUES(?,?,?,?)",
                (task_id, actor, command["action"], json.dumps(command, sort_keys=True)),
            )
            self.db.commit()
        except sqlite3.IntegrityError as error:
            self.db.rollback()
            raise ValueError("Identifiant déjà utilisé") from error
        except Exception:
            self.db.rollback()
            raise
        return dict(self.db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone())

    def snapshot(self):
        return {
            "tasks": [dict(r) for r in self.db.execute("SELECT * FROM tasks ORDER BY id")],
            "audit": [dict(r) for r in self.db.execute("SELECT * FROM audit ORDER BY seq")],
        }

    def close(self):
        self.db.close()


def run(request, db=":memory:"):
    board = TaskBoard(db)
    try:
        for command in request["commands"]:
            board.apply(command)
        return board.snapshot()
    finally:
        board.close()
