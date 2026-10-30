"""Mesurer le statut et la latence d’une URL HTTP avec des délais bornés."""

import argparse, json, time, urllib.request, urllib.error
from urllib.parse import urlsplit


def probe(url, timeout=5):
    parsed = urlsplit(url)
    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise ValueError("URL HTTP(S) sans identifiants requise")
    start = time.perf_counter()
    try:
        request = urllib.request.Request(
            url, method="HEAD", headers={"User-Agent": "PulseWatch-demo/1.0"}
        )
        with urllib.request.urlopen(request, timeout=timeout) as r:
            status = r.status
        error = None
    except urllib.error.HTTPError as e:
        status = e.code
        error = str(e)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        status = None
        error = str(e)
    return {
        "url": url,
        "status": status,
        "healthy": status is not None and 200 <= status < 400,
        "latency_ms": round((time.perf_counter() - start) * 1000, 2),
        "error": error,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("url")
    p.add_argument("--timeout", type=float, default=5)
    a = p.parse_args()
    if a.timeout <= 0:
        p.error("timeout doit être positif")
    result = probe(a.url, a.timeout)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["healthy"] else 1)


if __name__ == "__main__":
    main()
