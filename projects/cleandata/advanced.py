"""Validation de schéma configurable, transformations et rapport de qualité."""

from collections import Counter
from datetime import datetime
import json
import math


def pipeline(rows, schema, unique):
    if not schema or unique not in schema:
        raise ValueError("Schéma et clé unique requis")
    for name, rule in schema.items():
        if rule["type"] not in ("text", "number", "integer", "datetime"):
            raise ValueError("Type inconnu")
    accepted = []
    rejected = []
    seen = set()
    reasons = Counter()
    for index, row in enumerate(rows, 1):
        output = {}
        errors = []
        for name, rule in schema.items():
            raw = row.get(name)
            try:
                if raw is None or raw == "":
                    if rule.get("required", True):
                        raise ValueError("required")
                    output[name] = None
                    continue
                kind = rule["type"]
                if kind == "text":
                    value = str(raw).strip()
                    if rule.get("lowercase"):
                        value = value.casefold()
                    if not value:
                        raise ValueError("empty")
                elif kind == "number":
                    value = float(raw)
                    if not math.isfinite(value):
                        raise ValueError("finite")
                elif kind == "integer":
                    if isinstance(raw, bool) or str(raw).strip() != str(int(raw)):
                        raise ValueError("integer")
                    value = int(raw)
                else:
                    value = datetime.fromisoformat(str(raw).replace("Z", "+00:00")).isoformat()
                if "min" in rule and value < rule["min"]:
                    raise ValueError("min")
                if "max" in rule and value > rule["max"]:
                    raise ValueError("max")
                if "choices" in rule and value not in rule["choices"]:
                    raise ValueError("choice")
                output[name] = value
            except (ValueError, TypeError, OverflowError):
                errors.append(name + ":invalid")
        if not errors:
            key = output[unique]
            if key is None:
                errors.append(unique + ":required")
            elif key in seen:
                errors.append(unique + ":duplicate")
        if errors:
            reasons.update(errors)
            rejected.append({"row": index, "errors": errors, "original": row})
        else:
            seen.add(output[unique])
            accepted.append(output)
    count = len(accepted) + len(rejected)
    return {
        "accepted": accepted,
        "rejected": rejected,
        "quality": {
            "total": count,
            "valid": len(accepted),
            "invalid": len(rejected),
            "valid_ratio": len(accepted) / count if count else None,
            "errors_by_field": dict(sorted(reasons.items())),
        },
    }


def run(request, db=":memory:"):
    return pipeline(request["rows"], request["schema"], request["unique"])


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
