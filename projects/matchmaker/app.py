"""Interface CLI JSON : aucune exécution de code fourni par l'entrée."""

import argparse
import json
import sys
from core import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="sample.json", help="Scénario JSON")
    parser.add_argument("--db", default=":memory:", help="Base SQLite pour les projets persistants")
    args = parser.parse_args()
    try:
        with open(args.input, encoding="utf-8") as stream:
            request = json.load(stream)
        print(json.dumps(run(request, db=args.db), indent=2, ensure_ascii=False, allow_nan=False))
    except (ValueError, KeyError, TypeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
