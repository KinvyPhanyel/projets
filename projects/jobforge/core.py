"""File de travaux à livraison au moins une fois, avec baux clôturables."""

import json
import math
import sqlite3
import uuid


class Queue:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS jobs(
        id TEXT PRIMARY KEY, payload TEXT NOT NULL, status TEXT NOT NULL,
        attempts INTEGER NOT NULL, max_attempts INTEGER NOT NULL,
        available REAL NOT NULL, lease_until REAL, token TEXT, error TEXT)"""
        )

    def enqueue(self, identifier, payload, max_attempts=3):
        if not identifier or type(max_attempts) is not int or max_attempts < 1:
            raise ValueError("Identifiant et nombre de tentatives valides requis")
        encoded = json.dumps(payload, sort_keys=True, allow_nan=False)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            old = self.db.execute(
                "SELECT payload,max_attempts FROM jobs WHERE id=?", (identifier,)
            ).fetchone()
            if old and (old["payload"] != encoded or old["max_attempts"] != max_attempts):
                raise ValueError("Identifiant déjà associé à un autre travail")
            if not old:
                self.db.execute(
                    "INSERT INTO jobs VALUES(?,?,'pending',0,?,0,NULL,NULL,NULL)",
                    (identifier, encoded, max_attempts),
                )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def claim(self, now, lease=30):
        if not math.isfinite(now) or not math.isfinite(lease) or lease <= 0:
            raise ValueError("Heure finie et bail positif requis")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            self.db.execute(
                "UPDATE jobs SET status='dead',token=NULL WHERE status='running' AND lease_until<=? AND attempts>=max_attempts",
                (now,),
            )
            self.db.execute(
                "UPDATE jobs SET status='pending',token=NULL WHERE status='running' AND lease_until<=? AND attempts<max_attempts",
                (now,),
            )
            row = self.db.execute(
                "SELECT * FROM jobs WHERE status='pending' AND available<=? ORDER BY available,id LIMIT 1",
                (now,),
            ).fetchone()
            if not row:
                self.db.commit()
                return None
            token = uuid.uuid4().hex
            self.db.execute(
                "UPDATE jobs SET status='running',attempts=attempts+1,lease_until=?,token=? WHERE id=?",
                (now + lease, token, row["id"]),
            )
            result = dict(self.db.execute("SELECT * FROM jobs WHERE id=?", (row["id"],)).fetchone())
            result["payload"] = json.loads(result["payload"])
            self.db.commit()
            return result
        except Exception:
            self.db.rollback()
            raise

    def finish(self, identifier, token, now, error=None):
        if not math.isfinite(now) or (error is not None and not isinstance(error, str)):
            raise ValueError("Heure ou erreur invalides")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute("SELECT * FROM jobs WHERE id=?", (identifier,)).fetchone()
            if (
                not row
                or row["status"] != "running"
                or row["token"] != token
                or row["lease_until"] <= now
            ):
                raise ValueError("Bail expiré ou jeton obsolète")
            status = (
                "done"
                if error is None
                else ("dead" if row["attempts"] >= row["max_attempts"] else "pending")
            )
            available = now + (2 ** min(row["attempts"] - 1, 16) if error is not None else 0)
            self.db.execute(
                "UPDATE jobs SET status=?,available=?,error=?,token=NULL,lease_until=NULL WHERE id=?",
                (status, available, error, identifier),
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def snapshot(self):
        return [
            dict(r)
            for r in self.db.execute(
                "SELECT id,status,attempts,max_attempts,available,error FROM jobs ORDER BY id"
            )
        ]

    def close(self):
        self.db.close()


def run(request, db=":memory:"):
    queue = Queue(db)
    claimed = {}
    try:
        for c in request["commands"]:
            if c["action"] == "enqueue":
                queue.enqueue(c["id"], c["payload"], c.get("max_attempts", 3))
            elif c["action"] == "claim":
                job = queue.claim(c["at"], c.get("lease", 30))
                if job:
                    claimed[job["id"]] = job["token"]
            elif c["action"] == "finish":
                queue.finish(c["id"], claimed[c["id"]], c["at"], c.get("error"))
            else:
                raise ValueError("Action inconnue")
        return {"jobs": queue.snapshot()}
    finally:
        queue.close()
