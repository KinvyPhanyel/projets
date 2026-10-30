"""Détection chronologique par capteur, apprentissage sur le passé et hystérésis."""

from collections import defaultdict, deque
from datetime import datetime
import json
import math
import statistics


def detect_stream(
    events, window=5, warmup=3, threshold=3.5, confirmation=2, recovery=2, min_scale=0.1
):
    if (
        any(type(x) is not int or x < 1 for x in (window, warmup, confirmation, recovery))
        or warmup > window
        or threshold <= 0
        or min_scale <= 0
        or not math.isfinite(threshold)
        or not math.isfinite(min_scale)
    ):
        raise ValueError("Paramètres invalides")
    histories = defaultdict(lambda: deque(maxlen=window))
    last = {}
    state = {}
    points = []
    alerts = []
    for event in events:
        sensor = event["sensor"]
        value = float(event["value"])
        stamp = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
        if not sensor or not math.isfinite(value) or stamp.tzinfo is None:
            raise ValueError("Mesure invalide")
        moment = stamp.timestamp()
        if sensor in last and moment <= last[sensor]:
            raise ValueError("Dates strictement croissantes par capteur requises")
        last[sensor] = moment
        history = histories[sensor]
        mode, bad, good = state.get(sensor, ("normal", 0, 0))
        score = None
        anomaly = False
        if len(history) >= warmup:
            median = statistics.median(history)
            mad = statistics.median(abs(x - median) for x in history)
            score = abs(value - median) / max(mad / 0.67448975, min_scale)
            anomaly = score > threshold
            bad = bad + 1 if anomaly else 0
            good = 0 if anomaly else good + 1
            if mode == "normal" and bad >= confirmation:
                mode = "alert"
                alerts.append(
                    {"sensor": sensor, "event": "opened", "timestamp": event["timestamp"]}
                )
            elif mode == "alert" and good >= recovery:
                mode = "normal"
                alerts.append(
                    {"sensor": sensor, "event": "recovered", "timestamp": event["timestamp"]}
                )
        # Excluding anomalies prevents a spike from poisoning the baseline.
        if not anomaly:
            history.append(value)
        state[sensor] = (mode, bad, good)
        points.append(
            {
                "sensor": sensor,
                "value": value,
                "score": round(score, 4) if score is not None else None,
                "anomaly": anomaly,
                "state": mode,
            }
        )
    return {
        "points": points,
        "alerts": alerts,
        "baselines": {sensor: list(history) for sensor, history in histories.items()},
    }


def run(request, db=":memory:"):
    return detect_stream(request["events"], **request.get("parameters", {}))


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
