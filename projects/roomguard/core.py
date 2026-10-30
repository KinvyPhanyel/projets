"""Réservations UTC avec exclusion de chevauchement sous verrou d'écriture."""

import datetime
import sqlite3


def instant(text):
    value = datetime.datetime.fromisoformat(text.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("Fuseau horaire obligatoire")
    return value.timestamp()


class Reservations:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(
            """CREATE TABLE IF NOT EXISTS bookings(
        id TEXT PRIMARY KEY, resource TEXT NOT NULL, owner TEXT NOT NULL,
        start REAL NOT NULL, end REAL NOT NULL, active INTEGER NOT NULL CHECK(active IN(0,1)),
        CHECK(start<end)); CREATE INDEX IF NOT EXISTS bookings_resource ON bookings(resource,start,end);"""
        )

    def reserve(self, identifier, resource, owner, start, end):
        a, b = instant(start), instant(end)
        if (
            not all(isinstance(v, str) and v.strip() for v in [identifier, resource, owner])
            or a >= b
        ):
            raise ValueError("Réservation invalide")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            existing = self.db.execute(
                "SELECT * FROM bookings WHERE id=?", (identifier,)
            ).fetchone()
            if existing:
                if (
                    existing["resource"],
                    existing["owner"],
                    existing["start"],
                    existing["end"],
                ) != (resource, owner, a, b):
                    raise ValueError("Clé idempotente réutilisée avec un autre contenu")
                result = dict(existing)
            else:
                conflict = self.db.execute(
                    "SELECT id FROM bookings WHERE active=1 AND resource=? AND start<? AND end>?",
                    (resource, b, a),
                ).fetchone()
                if conflict:
                    raise ValueError("Créneau occupé")
                self.db.execute(
                    "INSERT INTO bookings VALUES(?,?,?,?,?,1)", (identifier, resource, owner, a, b)
                )
                result = dict(
                    self.db.execute("SELECT * FROM bookings WHERE id=?", (identifier,)).fetchone()
                )
            self.db.commit()
            return result
        except Exception:
            self.db.rollback()
            raise

    def cancel(self, identifier, owner):
        with self.db:
            row = self.db.execute("SELECT owner FROM bookings WHERE id=?", (identifier,)).fetchone()
            if not row or row["owner"] != owner:
                raise ValueError("Réservation inconnue ou propriétaire incorrect")
            self.db.execute("UPDATE bookings SET active=0 WHERE id=?", (identifier,))

    def list(self):
        return [dict(r) for r in self.db.execute("SELECT * FROM bookings ORDER BY start,id")]

    def close(self):
        self.db.close()


def run(request, db=":memory:"):
    service = Reservations(db)
    try:
        for c in request["commands"]:
            if c["action"] == "reserve":
                service.reserve(c["id"], c["resource"], c["owner"], c["start"], c["end"])
            elif c["action"] == "cancel":
                service.cancel(c["id"], c["owner"])
            else:
                raise ValueError("Action inconnue")
        return {"bookings": service.list()}
    finally:
        service.close()
