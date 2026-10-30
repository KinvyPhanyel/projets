"""Journal append-only par convention, avec vérification de sa chaîne d'empreintes."""

import hashlib
import json
import sqlite3

ZERO = "0" * 64


def digest(stream, version, payload, previous):
    canonical = json.dumps(
        [stream, version, payload, previous], ensure_ascii=False, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


class EventStore:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS events(
        seq INTEGER PRIMARY KEY, stream TEXT NOT NULL, version INTEGER NOT NULL,
        payload TEXT NOT NULL, previous TEXT NOT NULL, hash TEXT NOT NULL,
        UNIQUE(stream,version))"""
        )

    def append(self, stream, expected_version, payloads):
        if (
            not isinstance(stream, str)
            or not stream
            or type(expected_version) is not int
            or expected_version < 0
            or not payloads
        ):
            raise ValueError("Stream, version attendue et événements requis")
        serialized = [
            json.dumps(
                p, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")
            )
            for p in payloads
        ]
        self.db.execute("BEGIN IMMEDIATE")
        try:
            tail = self.db.execute(
                "SELECT version,hash FROM events WHERE stream=? ORDER BY version DESC LIMIT 1",
                (stream,),
            ).fetchone()
            version, previous = (tail["version"], tail["hash"]) if tail else (0, ZERO)
            if version != expected_version:
                raise ValueError("Conflit de version")
            for payload in serialized:
                version += 1
                hashed = digest(stream, version, payload, previous)
                self.db.execute(
                    "INSERT INTO events(stream,version,payload,previous,hash) VALUES(?,?,?,?,?)",
                    (stream, version, payload, previous, hashed),
                )
                previous = hashed
            self.db.commit()
            return version
        except Exception:
            self.db.rollback()
            raise

    def read(self, stream):
        return [
            dict(row)
            for row in self.db.execute(
                "SELECT * FROM events WHERE stream=? ORDER BY version", (stream,)
            )
        ]

    def verify(self, stream):
        previous = ZERO
        for version, event in enumerate(self.read(stream), 1):
            if (
                event["version"] != version
                or event["previous"] != previous
                or event["hash"] != digest(stream, version, event["payload"], previous)
            ):
                return False
            previous = event["hash"]
        return True

    def project(self, stream):
        if not self.verify(stream):
            raise ValueError("Chaîne altérée")
        balance = 0
        for event in self.read(stream):
            payload = json.loads(event["payload"])
            if (
                payload.get("type") not in ("deposit", "withdraw")
                or type(payload.get("amount")) is not int
                or payload["amount"] <= 0
            ):
                raise ValueError("Événement métier invalide")
            balance += payload["amount"] if payload["type"] == "deposit" else -payload["amount"]
        return balance

    def close(self):
        self.db.close()


def run(request, db=":memory:"):
    store = EventStore(db)
    try:
        for batch in request["batches"]:
            store.append(batch["stream"], batch["expected_version"], batch["events"])
        streams = sorted({batch["stream"] for batch in request["batches"]})
        return {
            "streams": {
                s: {
                    "version": len(store.read(s)),
                    "chain_valid": store.verify(s),
                    "balance": store.project(s),
                }
                for s in streams
            }
        }
    finally:
        store.close()
