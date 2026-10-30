"""Valider et dédupliquer un fichier de mesures, en isolant chaque ligne rejetée."""

import argparse, csv, json, math
from datetime import datetime


def clean(rows):
    accepted = []
    rejected = []
    seen = set()
    for line, row in enumerate(rows, 2):
        try:
            identifier = row["id"].strip()
            value = float(row["value"])
            stamp = datetime.fromisoformat(row["timestamp"])
            if not identifier:
                raise ValueError("identifiant vide")
            if not math.isfinite(value):
                raise ValueError("valeur non finie")
            if identifier in seen:
                raise ValueError("identifiant dupliqué")
            seen.add(identifier)
            accepted.append({"id": identifier, "timestamp": stamp.isoformat(), "value": value})
        except (ValueError, TypeError, KeyError) as e:
            rejected.append({"line": line, "reason": str(e), "row": row})
    return {
        "accepted": accepted,
        "rejected": rejected,
        "counts": {"accepted": len(accepted), "rejected": len(rejected)},
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file")
    a = p.parse_args()
    with open(a.file, newline="") as f:
        result = clean(csv.DictReader(f))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
