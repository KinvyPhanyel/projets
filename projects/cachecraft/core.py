"""Cache en mémoire avec single-flight et budget pondéré."""

from collections import OrderedDict
from concurrent.futures import Future
import math
import threading
import time


class Cache:
    def __init__(self, max_weight=100, ttl=60, clock=time.monotonic):
        if (
            type(max_weight) is not int
            or max_weight < 1
            or not isinstance(ttl, (int, float))
            or not math.isfinite(ttl)
            or ttl <= 0
        ):
            raise ValueError("Budget entier et TTL positif requis")
        self.max_weight = max_weight
        self.ttl = ttl
        self.clock = clock
        self.data = OrderedDict()
        self.flights = {}
        self.weight = 0
        self.lock = threading.RLock()
        self.stats = {"hits": 0, "misses": 0, "loads": 0, "evictions": 0}

    def _expire(self):
        now = self.clock()
        for key, (_, weight, expires) in list(self.data.items()):
            if expires <= now:
                self.weight -= weight
                del self.data[key]

    def put(self, key, value, weight=1):
        if type(weight) is not int or weight < 1 or weight > self.max_weight:
            raise ValueError("Poids invalide")
        with self.lock:
            self._expire()
            if key in self.data:
                self.weight -= self.data.pop(key)[1]
            while self.weight + weight > self.max_weight:
                _, (_, removed, _) = self.data.popitem(last=False)
                self.weight -= removed
                self.stats["evictions"] += 1
            self.data[key] = (value, weight, self.clock() + self.ttl)
            self.weight += weight

    def get_or_load(self, key, loader, weight=1):
        with self.lock:
            self._expire()
            if key in self.data:
                self.stats["hits"] += 1
                value = self.data[key][0]
                self.data.move_to_end(key)
                return value
            self.stats["misses"] += 1
            leader = key not in self.flights
            future = self.flights.setdefault(key, Future())
        if not leader:
            return future.result()
        try:
            with self.lock:
                self.stats["loads"] += 1
            value = loader()
            self.put(key, value, weight)
            future.set_result(value)
            return value
        except BaseException as error:
            future.set_exception(error)
            raise
        finally:
            with self.lock:
                self.flights.pop(key, None)

    def snapshot(self):
        with self.lock:
            self._expire()
            return {
                "keys_lru_to_mru": list(self.data),
                "weight": self.weight,
                "stats": dict(self.stats),
            }


def run(request, db=":memory:"):
    now = [0.0]
    cache = Cache(request["max_weight"], request["ttl"], clock=lambda: now[0])
    values = []
    for c in request["commands"]:
        if c["action"] == "advance":
            if c["seconds"] < 0:
                raise ValueError("Temps négatif")
            now[0] += c["seconds"]
        elif c["action"] == "put":
            cache.put(c["key"], c["value"], c.get("weight", 1))
        elif c["action"] == "get":
            values.append(
                cache.get_or_load(c["key"], lambda: c.get("fallback"), c.get("weight", 1))
            )
        else:
            raise ValueError("Action inconnue")
    return {"values": values, **cache.snapshot()}
