#!/usr/bin/env python3
"""Run the two prospectively admitted, unmeasured same-scene Flat captures.

Reuses the frozen timing runner's bounded pipe transport only. It never invokes
that runner's execution path or either original timing executable. Original raw
streams remain in owned scratch; lossless compressed copies are retained here.
"""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import time

ROOT = Path(__file__).resolve().parents[3]
SESSION = Path(__file__).resolve().parent
REPORTS = SESSION / "reports"
STAGE = ROOT.parent / "p1-timing-qualification"
RUNNER_SHA = "0a5b7a42a17a93bc44f0abab0d26ce0d05c955c511d0bb34fbf399fd611ffedb"
SOURCE_SHA = "af2a675a5aeb7925d2a752f9897eca7bf5d70aa0b55aac1c1476d869c0e227ad"
ADMISSION_SHA = "3396a17b782fbc7a497cdfd9d54400985f2deccf1eafcbda150b3f1b19411392"
PIXEL_BYTES = 1672 * 941 * 4


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def fnv(raw):
    value = 14695981039346656037
    for byte in raw:
        value = ((value ^ byte) * 1099511628211) & ((1 << 64) - 1)
    return format(value, "x")


def main():
    runner_path = SESSION / "run_p1_timing.py"
    require(sha(runner_path.read_bytes()) == RUNNER_SHA, "frozen transport changed")
    source = ROOT / "tools/standalone_flat_pixel_capture.cpp"
    require(sha(source.read_bytes()) == SOURCE_SHA, "admitted companion changed")
    admission = REPORTS / "source-history/A25-environment-v2-prospective-admission.md.txt"
    require(sha(admission.read_bytes()) == ADMISSION_SHA, "precompile admission changed")
    spec = importlib.util.spec_from_file_location("p1_frozen_transport", runner_path)
    transport = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(transport)
    build_path = REPORTS / "p1-flat-witness-build/report.json"
    build = transport.strict_json(build_path.read_bytes())
    require(build["passed"] is True and [r["side"] for r in build["runs"]] == ["before", "after"],
            "both admitted capture executables must be built in fixed order")
    inputs = [build["source"], build["benchmark_source"], build["source_admission"],
              build["companion_object"], transport.identity(build_path), transport.identity(Path(__file__))]
    for run in build["runs"]:
        inputs.extend([*run["inputs"], run["executable"]])
    normalized = []
    for item in inputs:
        actual = transport.identity(Path(item["path"]))
        require(all(actual.get(key) == value for key, value in item.items()),
                "capture build input changed: " + item["path"])
        normalized.append(actual)
    inputs = normalized
    output = REPORTS / "p1-flat-witness-v2"
    raw_output = STAGE / "flat-raw-v2"
    require(not output.exists() and not raw_output.exists(), "refusing any previous capture output")
    output.mkdir()
    raw_output.mkdir()
    report = {"schema_version": 1, "purpose": "exact same-scene Flat pixels; zero timing samples",
              "started_utc": transport.utc(), "source_admission": transport.identity(admission),
              "source": transport.identity(source), "build_receipt": transport.identity(build_path),
              "driver": transport.identity(Path(__file__)), "inputs_before": inputs,
              "cpu": 0, "child_environment": transport.CHILD_ENV, "processes": [], "errors": [],
              "limits": {"processes": 2, "process_seconds": 180, "batch_seconds": 370,
                         "header_bytes": 65536, "pixel_bytes": PIXEL_BYTES,
                         "stdout_bytes": 65536 + 1 + PIXEL_BYTES, "stderr_bytes": 65536}}
    transport.LIMITS = dict(transport.LIMITS, stdout_bytes_each=65536 + 1 + PIXEL_BYTES,
                            stderr_bytes_each=65536, process_seconds=180)

    def validate_capture(raw, _row):
        newline = raw.find(b"\n", 0, 65537)
        require(0 < newline <= 65536, "bounded JSON header missing")
        header = transport.strict_json(raw[:newline])
        expected = {"schema": "standalone-benchmark-flat-pixels-v1", "width": 1672, "height": 941,
                    "presentation": "flat", "scenario": "mixed-held", "workspace": "Play", "overlay": "none",
                    "paints": 331, "timing_samples": 0, "paired": False, "heap_instrumentation": False,
                    "preservation_assertions_passed": True, "render_batching": "1", "renderer": "software",
                    "renderer_flags": 13, "sdl_version": "2.32.10", "surface_format": "SDL_PIXELFORMAT_ABGR8888",
                    "pixel_format": "RGBA32", "row_order": "top-to-bottom", "row_stride": 6688,
                    "bytes": PIXEL_BYTES, "scale": [1, 1], "viewport": [0, 0, 1672, 941], "clip": None}
        require(set(header) == set(expected) | {"layout_fnv1a64", "current_pixels_fnv1a64"}, "header schema differs")
        for key, value in expected.items():
            require(type(header[key]) is type(value) and header[key] == value, "header differs: " + key)
            if isinstance(value, list):
                require(all(type(actual) is type(wanted) for actual, wanted in zip(header[key], value)),
                        "header list member type differs: " + key)
        require(all(type(header[key]) is str and re.fullmatch(r"[0-9a-f]{1,16}", header[key])
                    for key in ("layout_fnv1a64", "current_pixels_fnv1a64")), "malformed fingerprint")
        pixels = raw[newline + 1:]
        require(len(pixels) == PIXEL_BYTES, "raw extent or trailer differs")
        fingerprint = fnv(pixels)
        require(fingerprint == header["current_pixels_fnv1a64"], "independent raw fingerprint differs")
        return {"header": header, "rgba_sha256": sha(pixels), "rgba_bytes": len(pixels),
                "independent_fnv1a64": fingerprint, "header_bytes": newline}

    transport.validate_stdout = validate_capture
    affinity = os.sched_getaffinity(0)
    try:
        require(0 in affinity, "prospective CPU0 is unavailable")
        os.sched_setaffinity(0, {0})
        deadline = time.monotonic() + 370
        for order, run in enumerate(build["runs"], 1):
            require(time.monotonic() < deadline, "capture batch deadline expired")
            row = {"order": order, "case": "flat-same-scene", "side": run["side"],
                   "command": [run["executable"]["path"], "1672", "941", "flat", "mixed-held"]}
            result = transport.run_process(row, raw_output, 0, deadline)
            for stream in ("stdout", "stderr"):
                raw = Path(result[stream]["path"]).read_bytes()
                name = f"{order:02d}-{run['side']}.{stream}.gz"
                result["retained_" + stream + "_gzip"] = transport.write_new(output / name, gzip.compress(raw, mtime=0))
                result["raw_" + stream + "_sha256"] = sha(raw)
            report["processes"].append(result)
            transport.write_new(output / f"{order:02d}-{run['side']}.json", result)
            if result["errors"]:
                report["errors"].extend(result["errors"])
                break
        require(len(report["processes"]) == 2 and not report["errors"], "two complete accepted captures required")
        left, right = report["processes"]
        left_raw = Path(left["stdout"]["path"]).read_bytes()
        right_raw = Path(right["stdout"]["path"]).read_bytes()
        left_pixels = left_raw.split(b"\n", 1)[1]
        right_pixels = right_raw.split(b"\n", 1)[1]
        report["headers_equal"] = left["validated"]["header"] == right["validated"]["header"]
        report["direct_rgba_byte_equality"] = left_pixels == right_pixels
        require(report["headers_equal"] and report["direct_rgba_byte_equality"], "same-scene raw Flat frames differ")
        report["rgba_sha256"] = sha(left_pixels)
        report["independent_fnv1a64"] = fnv(left_pixels)
    except BaseException as error:
        report["errors"].append(type(error).__name__ + ": " + str(error))
    finally:
        try:
            os.sched_setaffinity(0, affinity)
        except OSError as error:
            report["errors"].append("restore affinity: " + str(error))
        drift = []
        for item in inputs:
            try:
                if transport.identity(Path(item["path"])) != item:
                    drift.append(item["path"])
            except (OSError, ValueError) as error:
                drift.append(item["path"] + ": " + str(error))
        report["input_drift"] = drift
        report["passed"] = (len(report["processes"]) == 2 and not report["errors"] and not drift
                            and report.get("headers_equal") is True
                            and report.get("direct_rgba_byte_equality") is True)
        report["finished_utc"] = transport.utc()
        report["timing_samples"] = 0
        transport.write_new(output / "report.json", report)
    print(json.dumps({"passed": report["passed"], "processes": len(report["processes"]),
                      "errors": report["errors"], "rgba_sha256": report.get("rgba_sha256"),
                      "fnv1a64": report.get("independent_fnv1a64"), "timing_samples": 0}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
