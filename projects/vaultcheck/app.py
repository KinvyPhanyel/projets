"""Créer et vérifier un manifeste SHA-256 de fichiers locaux."""

import argparse, hashlib, json
from pathlib import Path


def manifest(directory):
    base = Path(directory).resolve()
    result = {}
    if not base.is_dir():
        raise ValueError("Dossier introuvable")
    for path in sorted(base.rglob("*")):
        if (
            path.is_file()
            and not path.is_symlink()
            and all(not p.is_symlink() for p in path.parents)
        ):
            digest = hashlib.sha256()
            with path.open("rb") as f:
                for block in iter(lambda: f.read(65536), b""):
                    digest.update(block)
            result[path.relative_to(base).as_posix()] = digest.hexdigest()
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    for name in ["create", "verify"]:
        s = sub.add_parser(name)
        s.add_argument("directory")
        s.add_argument("manifest")
    a = p.parse_args()
    base = Path(a.directory).resolve()
    destination = Path(a.manifest).resolve()
    if destination.is_relative_to(base):
        p.error("Le manifeste doit être enregistré hors du dossier analysé")
    current = manifest(base)
    if a.command == "create":
        with destination.open("x") as f:
            json.dump(current, f, indent=2)
        print(json.dumps({"files": len(current), "manifest": str(destination)}))
    else:
        with destination.open() as f:
            expected = json.load(f)
        result = {
            "added": sorted(current.keys() - expected.keys()),
            "missing": sorted(expected.keys() - current.keys()),
            "changed": sorted(
                k for k in current.keys() & expected.keys() if current[k] != expected[k]
            ),
        }
        print(json.dumps(result, indent=2))
        raise SystemExit(1 if any(result.values()) else 0)


if __name__ == "__main__":
    main()
