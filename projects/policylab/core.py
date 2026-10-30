"""Décisions d'autorisation explicables sur des données, jamais sur du code eval."""

import fnmatch


class Policy:
    def __init__(self, roles, rules):
        self.roles = roles
        self.rules = rules
        for role in roles:
            self.expand([role])
        for rule in rules:
            if rule["effect"] not in ("allow", "deny"):
                raise ValueError("Effet invalide")
            if rule["role"] not in roles and rule["role"] != "*":
                raise ValueError("Rôle de règle inconnu")
            for condition in rule.get("conditions", []):
                if condition["op"] not in ("eq", "in"):
                    raise ValueError("Opérateur invalide")

    def expand(self, names):
        result = set()
        visiting = set()

        def visit(name):
            if name not in self.roles:
                raise ValueError("Rôle inconnu: " + name)
            if name in visiting:
                raise ValueError("Cycle dans les rôles")
            if name in result:
                return
            visiting.add(name)
            for parent in self.roles[name]:
                visit(parent)
            visiting.remove(name)
            result.add(name)

        for name in names:
            visit(name)
        return result

    def decide(self, roles, action, resource, attributes):
        expanded = self.expand(roles)
        matches = []
        for index, rule in enumerate(self.rules):
            if rule["role"] != "*" and rule["role"] not in expanded:
                continue
            if not fnmatch.fnmatchcase(action, rule["action"]) or not fnmatch.fnmatchcase(
                resource, rule["resource"]
            ):
                continue
            valid = True
            for condition in rule.get("conditions", []):
                key = condition["attribute"]
                if key not in attributes:
                    valid = False
                    break
                actual = attributes[key]
                expected = condition["value"]
                if condition["op"] == "eq":
                    valid = actual == expected
                else:
                    try:
                        valid = actual in expected
                    except TypeError:
                        valid = False
                if not valid:
                    break
            if valid:
                matches.append({"rule": index, "effect": rule["effect"]})
        denied = any(m["effect"] == "deny" for m in matches)
        allowed = any(m["effect"] == "allow" for m in matches) and not denied
        return {
            "allowed": allowed,
            "reason": "explicit_deny" if denied else ("allow" if allowed else "default_deny"),
            "expanded_roles": sorted(expanded),
            "matched_rules": matches,
        }


def run(request, db=":memory:"):
    policy = Policy(request["roles"], request["rules"])
    return {
        "decisions": [
            policy.decide(c["roles"], c["action"], c["resource"], c.get("attributes", {}))
            for c in request["requests"]
        ]
    }
