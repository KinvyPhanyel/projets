"""Local-only portfolio lab. Executes fixed project entrypoints with JSON input."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]
MAX_INPUT = 512_000
SLOTS = threading.BoundedSemaphore(2)


class LabHandler(SimpleHTTPRequestHandler):
    def respond(self, status, payload):
        data = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_HEAD(self):
        if self.path == "/demo/unavailable":
            self.send_error(503, "Demo failure")
        else:
            super().do_HEAD()

    def do_POST(self):
        if self.path != "/api/run":
            self.respond(404, {"error": "Route inconnue"})
            return
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            self.respond(415, {"error": "application/json requis"})
            return
        # Browser cross-origin requests must not trigger local computations.
        origin = self.headers.get("Origin")
        expected = f"http://127.0.0.1:{self.server.server_port}"
        if origin and origin not in (expected, f"http://localhost:{self.server.server_port}"):
            self.respond(403, {"error": "Origine refusée"})
            return
        host = self.headers.get("Host", "")
        if host not in (
            f"127.0.0.1:{self.server.server_port}",
            f"localhost:{self.server.server_port}",
        ):
            self.respond(403, {"error": "Host refusé"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_INPUT:
                self.respond(413, {"error": "Scénario trop volumineux ou vide"})
                return
            request = json.loads(self.rfile.read(length))
            slug = request["project"]
            scenario = request["scenario"]
            catalogue = json.loads((ROOT / "site/projects.json").read_text())
            allowed = {item["slug"] for item in catalogue}
            if slug not in allowed or not isinstance(scenario, dict):
                self.respond(400, {"error": "Projet ou scénario invalide"})
                return
        except (ValueError, KeyError, TypeError):
            self.respond(400, {"error": "Requête JSON invalide"})
            return
        if not SLOTS.acquire(blocking=False):
            self.respond(429, {"error": "Deux exécutions sont déjà en cours"})
            return
        try:
            if slug == "pulsewatch":
                # Fixed local targets only. No arbitrary network probes from this API.
                scenario = {**scenario, "targets": [expected + "/", expected + "/demo/unavailable"]}
            folder = ROOT / "projects" / slug
            entry = "advanced.py" if (folder / "advanced.py").exists() else "app.py"
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "scenario.json"
                path.write_text(json.dumps(scenario))
                completed = subprocess.run(
                    [sys.executable, entry, "--input", str(path)],
                    cwd=folder,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
            if completed.returncode:
                # Only expected validation errors are returned, not Python tracebacks.
                try:
                    error = json.loads(completed.stderr)["error"]
                except (ValueError, KeyError, TypeError):
                    error = (
                        "Scénario incompatible : vérifier les champs et les types dans le contrat."
                    )
                self.respond(422, {"error": error})
                return
            if len(completed.stdout) > 2_000_000:
                self.respond(413, {"error": "Résultat trop volumineux"})
                return
            self.respond(200, {"result": json.loads(completed.stdout)})
        except subprocess.TimeoutExpired:
            self.respond(408, {"error": "Exécution interrompue après 10 secondes"})
        except (OSError, ValueError):
            self.respond(500, {"error": "Exécution impossible"})
        finally:
            SLOTS.release()


def create_server(port=8080):
    return ThreadingHTTPServer(
        ("127.0.0.1", port), partial(LabHandler, directory=str(ROOT / "site"))
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    server = create_server(args.port)
    print(f"Laboratoire local sur le port {server.server_port}. Ctrl+C pour arrêter.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
