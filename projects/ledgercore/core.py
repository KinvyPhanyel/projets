"""Grand livre pédagogique : un journal équilibré est enregistré atomiquement."""

import json
import sqlite3


class Ledger:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript(
            """CREATE TABLE IF NOT EXISTS journals(id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS entries(seq INTEGER PRIMARY KEY, journal TEXT REFERENCES journals(id), account TEXT NOT NULL, amount INTEGER NOT NULL);
        CREATE INDEX IF NOT EXISTS entries_account ON entries(account);"""
        )

    def post(self, identifier, entries):
        if (
            not isinstance(identifier, str)
            or not identifier.strip()
            or not isinstance(entries, list)
            or len(entries) < 2
        ):
            raise ValueError("Identifiant et au moins deux lignes requis")
        normalized = []
        for e in entries:
            if (
                not isinstance(e["account"], str)
                or not e["account"].strip()
                or type(e["amount"]) is not int
                or not e["amount"]
                or abs(e["amount"]) > 10**12
            ):
                raise ValueError("Compte et montant entier non nul borné requis")
            normalized.append({"account": e["account"], "amount": e["amount"]})
        if sum(e["amount"] for e in normalized) != 0:
            raise ValueError("Écriture déséquilibrée")
        fingerprint = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
        self.db.execute("BEGIN IMMEDIATE")
        try:
            old = self.db.execute(
                "SELECT fingerprint FROM journals WHERE id=?", (identifier,)
            ).fetchone()
            if old:
                if old["fingerprint"] != fingerprint:
                    raise ValueError("Clé réutilisée avec un contenu différent")
                self.db.commit()
                return False
            self.db.execute("INSERT INTO journals VALUES(?,?)", (identifier, fingerprint))
            self.db.executemany(
                "INSERT INTO entries(journal,account,amount) VALUES(?,?,?)",
                [(identifier, e["account"], e["amount"]) for e in normalized],
            )
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise

    def reverse(self, original, identifier):
        if original == identifier:
            raise ValueError("Identifiant de contre-passation distinct requis")
        rows = self.db.execute(
            "SELECT account,amount FROM entries WHERE journal=? ORDER BY seq", (original,)
        ).fetchall()
        if not rows:
            raise ValueError("Écriture inconnue")
        return self.post(
            identifier, [{"account": r["account"], "amount": -r["amount"]} for r in rows]
        )

    def balances(self):
        return {
            r["account"]: r["balance"]
            for r in self.db.execute(
                "SELECT account,SUM(amount) AS balance FROM entries GROUP BY account ORDER BY account"
            )
        }

    def close(self):
        self.db.close()


def run(request, db=":memory:"):
    ledger = Ledger(db)
    try:
        for c in request["commands"]:
            if c["action"] == "post":
                ledger.post(c["id"], c["entries"])
            elif c["action"] == "reverse":
                ledger.reverse(c["original"], c["id"])
            else:
                raise ValueError("Action inconnue")
        return {
            "balances_minor_units": ledger.balances(),
            "journals": ledger.db.execute("SELECT count(*) FROM journals").fetchone()[0],
        }
    finally:
        ledger.close()
