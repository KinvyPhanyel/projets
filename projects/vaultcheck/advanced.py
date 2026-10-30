"""Sauvegarde de fichiers dans SQLite, déduplication par contenu et restauration vérifiée."""

import hashlib
import json
from pathlib import Path, PurePosixPath
import sqlite3


class Snapshots:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript(
            """CREATE TABLE IF NOT EXISTS blobs(hash TEXT PRIMARY KEY,data BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS snapshots(id TEXT PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS files(snapshot TEXT REFERENCES snapshots(id),path TEXT,hash TEXT REFERENCES blobs(hash),PRIMARY KEY(snapshot,path));"""
        )

    def create(self, identifier, files):
        if not identifier:
            raise ValueError("Identifiant requis")
        for name in files:
            path = self.safe_path(name)
            if any(
                parent.as_posix() in files for parent in path.parents if parent.as_posix() != "."
            ):
                raise ValueError("Un fichier ne peut pas être parent d’un autre fichier")
        try:
            with self.db:
                self.db.execute("INSERT INTO snapshots VALUES(?)", (identifier,))
                for name, data in sorted(files.items()):
                    if not isinstance(data, bytes):
                        raise ValueError("Contenu binaire requis")
                    digest = hashlib.sha256(data).hexdigest()
                    self.db.execute("INSERT OR IGNORE INTO blobs VALUES(?,?)", (digest, data))
                    self.db.execute("INSERT INTO files VALUES(?,?,?)", (identifier, name, digest))
        except sqlite3.IntegrityError as error:
            raise ValueError("Snapshot déjà présent") from error

    @staticmethod
    def safe_path(name):
        p = PurePosixPath(name)
        if (
            not name
            or p.is_absolute()
            or ".." in p.parts
            or chr(92) in name
            or chr(0) in name
            or ":" in name
            or p.as_posix() != name
            or name == "."
        ):
            raise ValueError("Chemin relatif canonique requis")
        return p

    def read(self, identifier):
        if not self.db.execute("SELECT 1 FROM snapshots WHERE id=?", (identifier,)).fetchone():
            raise ValueError("Snapshot inconnu")
        result = {}
        for name, digest, data in self.db.execute(
            "SELECT path,hash,data FROM files JOIN blobs USING(hash) WHERE snapshot=? ORDER BY path",
            (identifier,),
        ):
            self.safe_path(name)
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError("Blob corrompu")
            result[name] = data
        return result

    def restore(self, identifier, destination):
        # Destination must be new and exclusively controlled by this process.
        content = self.read(identifier)
        target = Path(destination)
        if target.is_symlink() or target.exists():
            raise ValueError("Destination nouvelle requise")
        target.mkdir(parents=True, exist_ok=False)
        for name, data in content.items():
            path = target.joinpath(*self.safe_path(name).parts)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(data)
        return len(content)

    def stats(self):
        return {
            "snapshots": self.db.execute("SELECT count(*) FROM snapshots").fetchone()[0],
            "unique_blobs": self.db.execute("SELECT count(*) FROM blobs").fetchone()[0],
            "file_references": self.db.execute("SELECT count(*) FROM files").fetchone()[0],
        }

    def close(self):
        self.db.close()


def run(request, db=":memory:"):
    repository = Snapshots(db)
    try:
        for snapshot in request["snapshots"]:
            repository.create(
                snapshot["id"],
                {name: text.encode("utf-8") for name, text in snapshot["files"].items()},
            )
        restored = {
            name: data.decode("utf-8") for name, data in repository.read(request["read"]).items()
        }
        return {**repository.stats(), "restored_content": restored}
    finally:
        repository.close()


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
