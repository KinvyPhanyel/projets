"""Validate all projects with isolated test discovery and executable CLI scenarios."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading
from check_basics import run as check_basics

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def verify(output=None, export_examples=False):
    catalogue = json.loads((ROOT / "site/projects.json").read_text())
    tests = {}
    results = {}
    total = 0
    for project in catalogue:
        slug = project["slug"]
        folder = ROOT / "projects" / slug
        completed = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-v"],
            cwd=folder,
            capture_output=True,
            text=True,
            timeout=30,
        )
        match = re.search(r"Ran (\d+) tests?", completed.stderr)
        if completed.returncode or not match or int(match[1]) == 0:
            raise RuntimeError(
                f"{slug}: tests failed or no tests executed\n{completed.stdout}\n{completed.stderr}"
            )
        count = int(match[1])
        total += count
        tests[slug] = {"passed": count}
        print(f"{slug}: {count} tests passed", file=sys.stderr)
    lab = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "automation", "-p", "test_*.py", "-v"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    lab_match = re.search(r"Ran (\d+) tests?", lab.stderr)
    if lab.returncode or not lab_match or int(lab_match[1]) == 0:
        raise RuntimeError("Lab integration tests failed\n" + lab.stderr)
    lab_count = int(lab_match[1])
    print(f"HTTP lab: {lab_count} integration tests passed", file=sys.stderr)
    baseline = check_basics()
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT / "site"))
    )
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        for project in catalogue:
            slug = project["slug"]
            folder = ROOT / "projects" / slug
            advanced = (folder / "advanced.py").exists()
            entry = "advanced.py" if advanced else "app.py"
            sample = "advanced-sample.json" if advanced else "sample.json"
            with tempfile.TemporaryDirectory() as tmp:
                input_file = folder / sample
                if slug == "pulsewatch":
                    scenario = json.loads(input_file.read_text())
                    url = f"http://127.0.0.1:{server.server_port}"
                    scenario["targets"] = [url + "/", url + "/absent"]
                    input_file = Path(tmp) / "input.json"
                    input_file.write_text(json.dumps(scenario))
                completed = subprocess.run(
                    [sys.executable, entry, "--input", str(input_file)],
                    cwd=folder,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if completed.returncode:
                    raise RuntimeError(f"{slug}: CLI failed\n{completed.stderr}")
                result = json.loads(completed.stdout)
                if slug == "pulsewatch":
                    if result["summary"]["healthy"] != 1:
                        raise RuntimeError("Expected one healthy and one failing HTTP target")
                    # Keep behavior, remove ephemeral port and timings from saved examples.
                    for target in result["targets"]:
                        target["url"] = target["url"].replace(url, "http://local-demo")
                        for attempt in target["history"]:
                            attempt["url"] = attempt["url"].replace(url, "http://local-demo")
                            attempt.pop("latency_ms", None)
                    result["summary"].pop("p95_final_latency_ms", None)
                    result["note"] = (
                        "Local HTTP checks; measured latencies omitted from reproducible examples."
                    )
                results[slug] = result
                if export_examples:
                    (folder / "examples").mkdir(exist_ok=True)
                    (folder / "examples/result.json").write_text(
                        json.dumps(result, indent=2, ensure_ascii=False) + "\n"
                    )
        # Actual HTTP requests are also covered in check_basics. Here verify catalogue files exist and parse.
        if len(catalogue) != 22 or len(results) != 22:
            raise RuntimeError("Expected exactly 22 documented projects")
    finally:
        server.shutdown()
        server.server_close()
        worker.join()
    report = {
        "status": "passed",
        "projects_checked": len(results),
        "unit_tests_passed": total,
        "lab_tests_passed": lab_count,
        "checks": tests,
        "baseline_checks": baseline["projects_checked"],
        "results": results,
    }
    if output:
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--export-examples", action="store_true")
    args = parser.parse_args()
    report = verify(args.output, args.export_examples)
    print(
        json.dumps(
            {
                "status": report["status"],
                "projects_checked": report["projects_checked"],
                "unit_tests_passed": report["unit_tests_passed"],
                "lab_tests_passed": report["lab_tests_passed"],
            },
            indent=2,
        )
    )
