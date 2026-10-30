"""Surveillance multi-cibles bornée en concurrence, avec reprises et agrégats."""

from concurrent.futures import ThreadPoolExecutor
import json
import math
import time
from app import probe


def monitor(
    targets, attempts=2, workers=4, timeout=2, delay=0.05, probe_fn=probe, sleep=time.sleep
):
    if (
        not targets
        or len(targets) > 100
        or type(attempts) is not int
        or not 1 <= attempts <= 5
        or type(workers) is not int
        or not 1 <= workers <= 16
    ):
        raise ValueError("Cibles, tentatives ou concurrence invalides")
    if not math.isfinite(timeout) or timeout <= 0 or not math.isfinite(delay) or delay < 0:
        raise ValueError("Délais invalides")

    def one(url):
        history = []
        for number in range(attempts):
            result = probe_fn(url, timeout)
            history.append(result)
            if result["healthy"]:
                break
            if number + 1 < attempts:
                sleep(delay * (2**number))
        return {
            "url": url,
            "healthy": history[-1]["healthy"],
            "attempts": len(history),
            "history": history,
        }

    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(one, targets))
    latencies = sorted(r["history"][-1]["latency_ms"] for r in results)
    return {
        "targets": results,
        "summary": {
            "total": len(results),
            "healthy": sum(r["healthy"] for r in results),
            "availability_snapshot": sum(r["healthy"] for r in results) / len(results),
            "p95_final_latency_ms": latencies[max(0, math.ceil(0.95 * len(latencies)) - 1)],
        },
    }


def run(request, db=":memory:"):
    return monitor(
        request["targets"],
        request.get("attempts", 2),
        request.get("workers", 4),
        request.get("timeout", 2),
    )


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
