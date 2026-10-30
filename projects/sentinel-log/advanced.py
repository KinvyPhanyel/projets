"""Corrélation temporelle multi-règles avec événements désordonnés et liste de confiance."""

from collections import defaultdict, deque
from datetime import datetime
import ipaddress
import json


def correlate(events, threshold=3, window=300, trusted=()):
    if type(threshold) is not int or threshold < 2 or window <= 0:
        raise ValueError("Seuil >= 2 et fenêtre positive requis")
    trusted_networks = [ipaddress.ip_network(n) for n in trusted]
    normalized = []
    for index, event in enumerate(events):
        stamp = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            raise ValueError("Fuseau obligatoire")
        address = ipaddress.ip_address(event["ip"])
        if event["status"] not in ("failed", "success") or not event.get("user"):
            raise ValueError("Événement invalide")
        if any(address in network for network in trusted_networks):
            continue
        normalized.append((stamp.timestamp(), index, event))
    failures = defaultdict(deque)
    by_ip = defaultdict(deque)
    active = set()
    alerts = []
    for stamp, _, event in sorted(normalized):
        key = (event["ip"], event["user"])
        queue = failures[key]
        while queue and queue[0] < stamp - window:
            queue.popleft()
        ips = by_ip[event["ip"]]
        while ips and ips[0][0] < stamp - window:
            ips.popleft()
        if len(queue) < threshold:
            active.discard(("brute", key))
        if len({u for _, u in ips}) < threshold:
            active.discard(("spray", event["ip"]))
        if event["status"] == "success":
            if len(queue) >= threshold:
                alerts.append(
                    {
                        "rule": "success_after_failures",
                        "severity": "high",
                        "ip": key[0],
                        "user": key[1],
                        "failures": len(queue),
                    }
                )
            queue.clear()
            active.discard(("brute", key))
            continue
        queue.append(stamp)
        ips.append((stamp, event["user"]))
        if len(queue) >= threshold and ("brute", key) not in active:
            alerts.append(
                {
                    "rule": "brute_force",
                    "severity": "medium",
                    "ip": key[0],
                    "user": key[1],
                    "count": len(queue),
                }
            )
            active.add(("brute", key))
        distinct = len({u for _, u in ips})
        if distinct >= threshold and ("spray", event["ip"]) not in active:
            alerts.append(
                {"rule": "password_spray", "severity": "high", "ip": event["ip"], "users": distinct}
            )
            active.add(("spray", event["ip"]))
    return {
        "alerts": alerts,
        "events_processed": len(normalized),
        "events_ignored": len(events) - len(normalized),
    }


def run(request, db=":memory:"):
    return correlate(
        request["events"],
        request.get("threshold", 3),
        request.get("window", 300),
        request.get("trusted", []),
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
