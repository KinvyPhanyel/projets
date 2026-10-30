"""Stock multi-entrepôts, transferts atomiques et clés d'idempotence."""

import json
import sqlite3


class Warehouse:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(
            """CREATE TABLE IF NOT EXISTS balances(
        warehouse TEXT, sku TEXT, quantity INTEGER NOT NULL CHECK(quantity>=0),PRIMARY KEY(warehouse,sku));
        CREATE TABLE IF NOT EXISTS operations(id TEXT PRIMARY KEY,payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS warehouse_audit(seq INTEGER PRIMARY KEY,operation TEXT,warehouse TEXT,sku TEXT,delta INTEGER);"""
        )

    def apply(self, identifier, sku, quantity, destination, source=None):
        if (
            type(quantity) is not int
            or quantity <= 0
            or not all(isinstance(x, str) and x.strip() for x in (identifier, sku, destination))
            or source == destination
        ):
            raise ValueError("Mouvement invalide")
        if source is not None and (not isinstance(source, str) or not source.strip()):
            raise ValueError("Source invalide")
        payload = json.dumps([sku, quantity, source, destination], separators=(",", ":"))
        self.db.execute("BEGIN IMMEDIATE")
        try:
            previous = self.db.execute(
                "SELECT payload FROM operations WHERE id=?", (identifier,)
            ).fetchone()
            if previous:
                if previous["payload"] != payload:
                    raise ValueError("Clé réutilisée avec un contenu différent")
                self.db.commit()
                return False
            movements = [(destination, quantity)] + ([(source, -quantity)] if source else [])
            for location, delta in movements:
                self.db.execute("INSERT OR IGNORE INTO balances VALUES(?,?,0)", (location, sku))
                current = self.db.execute(
                    "SELECT quantity FROM balances WHERE warehouse=? AND sku=?", (location, sku)
                ).fetchone()[0]
                if current + delta < 0:
                    raise ValueError("Stock insuffisant dans la source")
                self.db.execute(
                    "UPDATE balances SET quantity=quantity+? WHERE warehouse=? AND sku=?",
                    (delta, location, sku),
                )
                self.db.execute(
                    "INSERT INTO warehouse_audit(operation,warehouse,sku,delta) VALUES(?,?,?,?)",
                    (identifier, location, sku, delta),
                )
            self.db.execute("INSERT INTO operations VALUES(?,?)", (identifier, payload))
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise

    def snapshot(self):
        return {
            "stock": [
                dict(r) for r in self.db.execute("SELECT * FROM balances ORDER BY warehouse,sku")
            ],
            "audit": [
                dict(r) for r in self.db.execute("SELECT * FROM warehouse_audit ORDER BY seq")
            ],
        }

    def close(self):
        self.db.close()


def run(request, db=":memory:"):
    warehouse = Warehouse(db)
    try:
        for c in request["operations"]:
            warehouse.apply(c["id"], c["sku"], c["quantity"], c["destination"], c.get("source"))
        return warehouse.snapshot()
    finally:
        warehouse.close()


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="advanced-sample.json")
    parser.add_argument("--db", default=":memory:")
    args = parser.parse_args()
    try:
        with open(args.input, encoding="utf-8") as file:
            scenario = json.load(file)
        print(json.dumps(run(scenario, db=args.db), indent=2, ensure_ascii=False, allow_nan=False))
    except (ValueError, KeyError, TypeError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        raise SystemExit(2)
