"""Routage sous contraintes, plus court chemin à poids signés et cycles négatifs."""

import json
import math


def bellman_ford(graph, start, end, blocked=()):
    if start not in graph or end not in graph:
        raise ValueError("Sommet inconnu")
    blocked = set(blocked)
    if blocked - set(graph):
        raise ValueError("Sommet bloqué inconnu")
    if start in blocked or end in blocked:
        return {"cost": None, "path": []}
    nodes = set(graph) - blocked
    edges = []
    for source, neighbors in graph.items():
        for target, cost in neighbors.items():
            if target not in graph or not isinstance(cost, (int, float)) or not math.isfinite(cost):
                raise ValueError("Arête invalide")
            if source in nodes and target in nodes:
                edges.append((source, target, cost))
    distances = {n: float("inf") for n in nodes}
    distances[start] = 0
    previous = {}
    passes = 0
    for _ in range(len(nodes) - 1):
        changed = False
        passes += 1
        for source, target, cost in edges:
            if distances[source] + cost < distances[target]:
                distances[target] = distances[source] + cost
                previous[target] = source
                changed = True
        if not changed:
            break
    affected = {
        target for source, target, cost in edges if distances[source] + cost < distances[target]
    }
    for _ in nodes:
        affected.update(target for source, target, _ in edges if source in affected)
    if end in affected:
        raise ValueError("Cycle négatif atteignable influençant la destination")
    if distances[end] == float("inf"):
        return {"cost": None, "path": [], "passes": passes}
    path = [end]
    while path[-1] != start:
        path.append(previous[path[-1]])
        if len(path) > len(nodes):
            raise ValueError("Chemin incohérent")
    return {"cost": distances[end], "path": list(reversed(path)), "passes": passes}


def run(request, db=":memory:"):
    return {
        "routes": [
            bellman_ford(request["graph"], q["start"], q["end"], q.get("blocked", []))
            for q in request["queries"]
        ]
    }


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
