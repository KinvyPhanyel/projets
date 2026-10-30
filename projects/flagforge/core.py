"""Évaluation pure et explicable de flags, sans dépendance à un service distant."""

import hashlib
import math


class FlagEngine:
    def __init__(self, flags):
        self.flags = flags
        for name, f in flags.items():
            rollout = f.get("rollout", 100)
            if (
                isinstance(rollout, bool)
                or not isinstance(rollout, (float, int))
                or not math.isfinite(rollout)
                or not 0 <= rollout <= 100
            ):
                raise ValueError("Pourcentage invalide")
            if (
                type(f.get("enabled", True)) is not bool
                or type(f.get("default", False)) is not bool
            ):
                raise ValueError("enabled et default doivent être booléens")
            for rule in f.get("rules", []):
                if rule["op"] not in ("eq", "in", "gte") or type(rule["result"]) is not bool:
                    raise ValueError("Règle invalide")

    def evaluate(self, name, subject, attributes):
        if not isinstance(subject, str) or not subject:
            raise ValueError("Identifiant stable du sujet requis")
        if name not in self.flags:
            return {"value": False, "reason": "unknown_flag"}
        flag = self.flags[name]
        if not flag.get("enabled", True):
            return {"value": False, "reason": "disabled"}
        for index, rule in enumerate(flag.get("rules", [])):
            if rule["attribute"] not in attributes:
                continue
            actual = attributes[rule["attribute"]]
            expected = rule["value"]
            try:
                matched = {
                    "eq": lambda: actual == expected,
                    "in": lambda: actual in expected,
                    "gte": lambda: actual >= expected,
                }[rule["op"]]()
            except TypeError:
                matched = False
            if matched:
                return {"value": rule["result"], "reason": "rule", "rule": index}
        digest = hashlib.sha256(
            (name + chr(0) + flag.get("salt", "v1") + chr(0) + subject).encode()
        ).digest()
        bucket = int.from_bytes(digest[:8], "big") % 10000
        if bucket < flag.get("rollout", 100) * 100:
            return {"value": True, "reason": "rollout", "bucket": bucket}
        return {"value": flag.get("default", False), "reason": "default", "bucket": bucket}


def run(request, db=":memory:"):
    engine = FlagEngine(request["flags"])
    return {
        "evaluations": [
            {
                "flag": c["flag"],
                "subject": c["subject"],
                **engine.evaluate(c["flag"], c["subject"], c.get("attributes", {})),
            }
            for c in request["contexts"]
        ]
    }
