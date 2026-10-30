"""Token bucket en mémoire, protégé contre les accès concurrents."""

import math
import threading
import time


class TokenBuckets:
    def __init__(self, capacity, rate, clock=time.monotonic, max_clients=10000):
        if any(
            isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x <= 0
            for x in (capacity, rate)
        ):
            raise ValueError("Capacité et débit doivent être positifs et finis")
        if type(max_clients) is not int or max_clients < 1:
            raise ValueError("Nombre maximal de clients invalide")
        self.capacity = capacity
        self.rate = rate
        self.clock = clock
        self.max_clients = max_clients
        self.clients = {}
        self.lock = threading.Lock()

    def acquire(self, key, cost=1):
        if not isinstance(key, str) or not key:
            raise ValueError("Clé client requise")
        if (
            isinstance(cost, bool)
            or not isinstance(cost, (int, float))
            or not math.isfinite(cost)
            or cost <= 0
            or cost > self.capacity
        ):
            raise ValueError("Coût positif inférieur ou égal à la capacité requis")
        with self.lock:
            now = self.clock()
            if not math.isfinite(now):
                raise ValueError("Horloge non finie")
            if key not in self.clients and len(self.clients) >= self.max_clients:
                # Evict only fully replenished buckets: no client gains credit.
                for old, (tokens, stamp) in list(self.clients.items()):
                    if tokens + max(0, now - stamp) * self.rate >= self.capacity:
                        del self.clients[old]
                if len(self.clients) >= self.max_clients:
                    return {"allowed": False, "reason": "client_capacity", "retry_after": None}
            tokens, last = self.clients.get(key, (self.capacity, now))
            if now < last:
                raise ValueError("Horloge revenue en arrière")
            tokens = min(self.capacity, tokens + (now - last) * self.rate)
            allowed = tokens >= cost
            if allowed:
                tokens -= cost
            self.clients[key] = (tokens, now)
            return {
                "allowed": allowed,
                "remaining": round(tokens, 6),
                "retry_after": 0 if allowed else round((cost - tokens) / self.rate, 6),
                "reason": "accepted" if allowed else "rate_limited",
            }


def run(request, db=":memory:"):
    now = [0.0]
    limiter = TokenBuckets(request["capacity"], request["rate"], clock=lambda: now[0])
    decisions = []
    for event in request["events"]:
        timestamp = float(event["at"])
        if timestamp < now[0]:
            raise ValueError("Les événements doivent être ordonnés")
        now[0] = timestamp
        decisions.append(
            {
                "client": event["client"],
                "at": timestamp,
                **limiter.acquire(event["client"], event.get("cost", 1)),
            }
        )
    return {"decisions": decisions}
