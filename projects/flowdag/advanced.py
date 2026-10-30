"""Exécuteur DAG avec concurrence bornée, reprises et propagation des échecs."""

from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import json
from app import schedule


def execute(graph, handlers, max_workers=4, retries=0):
    schedule(graph)
    if (
        set(graph) - set(handlers)
        or type(max_workers) is not int
        or max_workers < 1
        or type(retries) is not int
        or retries < 0
    ):
        raise ValueError("Handlers ou paramètres invalides")
    state = {n: "pending" for n in graph}
    attempts = {n: 0 for n in graph}
    outputs = {}
    errors = {}
    running = {}

    def perform(name):
        inputs = {dependency: outputs[dependency] for dependency in graph[name]}
        return handlers[name](inputs)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        while any(s in ("pending", "running") for s in state.values()):
            changed = True
            while changed:
                changed = False
                for name in sorted(graph):
                    if state[name] == "pending" and any(
                        state[d] in ("failed", "skipped") for d in graph[name]
                    ):
                        state[name] = "skipped"
                        changed = True
            for name in sorted(graph):
                if len(running) >= max_workers:
                    break
                if state[name] == "pending" and all(state[d] == "done" for d in graph[name]):
                    state[name] = "running"
                    attempts[name] += 1
                    running[pool.submit(perform, name)] = name
            if not running:
                if any(s == "pending" for s in state.values()):
                    raise RuntimeError("Ordonnancement bloqué")
                break
            done, _ = wait(running, return_when=FIRST_COMPLETED)
            for future in done:
                name = running.pop(future)
                try:
                    outputs[name] = future.result()
                    state[name] = "done"
                    errors.pop(name, None)
                except Exception as error:
                    errors[name] = type(error).__name__ + ": " + str(error)
                    state[name] = "pending" if attempts[name] <= retries else "failed"
    return {"states": state, "attempts": attempts, "outputs": outputs, "errors": errors}


def run(request, db=":memory:"):
    tasks = request["tasks"]
    graph = {name: t.get("depends_on", []) for name, t in tasks.items()}
    handlers = {}
    for name, task in tasks.items():

        def handler(inputs, task=task):
            operation = task["operation"]
            if operation == "value":
                return task["value"]
            if operation == "sum":
                return sum(inputs.values())
            if operation == "multiply":
                value = 1
                for item in inputs.values():
                    value *= item
                return value
            if operation == "fail":
                raise ValueError("Échec demandé par le scénario")
            raise ValueError("Opération inconnue")

        handlers[name] = handler
    return execute(graph, handlers, request.get("workers", 4), request.get("retries", 0))


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
