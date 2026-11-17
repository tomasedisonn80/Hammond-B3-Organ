#!/usr/bin/env python3
"""Record bounded serial timing of genuine accepted-T3 and current-H1 binaries.

This is a manual software-paint experiment, not a timing-sensitive CTest or an
audio deadline test. Run from the repository root after all other native work
and builds have stopped. Both real executables retain the benchmark's original
30 warmup frames and 300 measured samples; no painter switches are introduced.
"""
import datetime
import hashlib
import json
import pathlib
import platform
import subprocess
import time


ROOT = pathlib.Path(__file__).resolve().parents[3]
SESSION = pathlib.Path(__file__).resolve().parent
OUTPUT = SESSION / "reports" / "h1-paint-timing"
BINARIES = {
    "before": ROOT.parent / "t3-native" / "hammond_standalone_paint_benchmark",
    "after": ROOT.parent / "build-native/apps/standalone/hammond_standalone_paint_benchmark",
}
PAINTERS = {
    "before": ROOT.parent / "t3-native/InstrumentView.cpp",
    "after": ROOT / "apps/standalone/InstrumentView.cpp",
}
CASES = (
    ("minimum-active", 1400, 820, "dimensional"),
    ("canonical", 1672, 941, "dimensional"),
    ("wide", 1920, 1080, "dimensional"),
    ("compact-inactive", 960, 700, "dimensional"),
    ("flat-inactive", 1672, 941, "flat"),
)


def identity(path):
    data = path.read_bytes()
    return {"path": str(path), "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}


def main():
    OUTPUT.mkdir(exist_ok=False)
    identities = {name: {"binary": identity(BINARIES[name]),
                         "painter": identity(PAINTERS[name])}
                  for name in BINARIES}
    report = {
        "schema": 1, "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "system": platform.platform(), "cwd": str(ROOT), "inputs": identities,
        "method": "One native child at a time; adjacent genuine before/after executables, reversing executable order on alternate cases. 30 warmup and 300 samples per executable. No concurrent build, capture or native test.",
        "cases": [], "limitations": [
            "Software SDL surface at scale 1 with no window or audio device.",
            "Separate executable runs do not eliminate scheduler or frequency drift.",
            "No audio callback deadline, hardware renderer, physical display or arbitrary C/SDL allocation claim.",
            "Existing benchmark investigation flag (>2 ms and >15% median growth) is diagnostic; it does not replace visual/resource admission.",
        ],
    }
    started = time.monotonic()
    for index, (name, width, height, presentation) in enumerate(CASES):
        entry = {"name": name, "width": width, "height": height,
                 "presentation": presentation, "scenario": "mixed-held", "runs": {}}
        order = ("before", "after") if index % 2 == 0 else ("after", "before")
        entry["execution_order"] = list(order)
        for side in order:
            command = [str(BINARIES[side]), str(width), str(height), presentation, "mixed-held"]
            run_started = time.monotonic()
            completed = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=120, check=False)
            elapsed = time.monotonic() - run_started
            if len(completed.stdout) > 2 * 1024 * 1024 or len(completed.stderr) > 1024 * 1024:
                raise RuntimeError("Benchmark output exceeds bounded receipt size")
            out = OUTPUT / (name + "-" + side + ".json")
            err = OUTPUT / (name + "-" + side + ".stderr.log")
            out.write_bytes(completed.stdout)
            err.write_bytes(completed.stderr)
            record = json.loads(completed.stdout)
            entry["runs"][side] = {"command": command, "exit_code": completed.returncode,
                "elapsed_seconds": elapsed, "stdout": identity(out), "stderr": identity(err),
                "result": record}
            if completed.returncode != 0 or completed.stderr:
                raise RuntimeError(f"Benchmark failed: {name} {side}")
            assert record["warmup_each"] == 30 and record["samples_each"] == 300
            assert record["heap_instrumentation"] is False
        old = entry["runs"]["before"]["result"]
        new = entry["runs"]["after"]["result"]
        assert old["layout_fnv1a64"] == new["layout_fnv1a64"]
        if name.endswith("inactive"):
            assert old["current_pixels_fnv1a64"] == new["current_pixels_fnv1a64"]
        old_time = old["current"]["total"]["median_ms"]
        new_time = new["current"]["total"]["median_ms"]
        growth = new_time - old_time
        percent = 100.0 * growth / old_time
        entry["comparison"] = {"before_total_median_ms": old_time,
            "after_total_median_ms": new_time, "growth_ms": growth, "growth_percent": percent,
            "before_total_p95_ms": old["current"]["total"]["p95_ms"],
            "after_total_p95_ms": new["current"]["total"]["p95_ms"],
            "benchmark_investigation_required": growth > 2.0 and percent > 15.0}
        report["cases"].append(entry)
        (OUTPUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"case": name, **entry["comparison"]}), flush=True)
    assert identities == {name: {"binary": identity(BINARIES[name]),
                                 "painter": identity(PAINTERS[name])}
                          for name in BINARIES}
    report.update({"inputs_unchanged": True, "completed": True,
                   "elapsed_seconds": time.monotonic() - started})
    (OUTPUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
