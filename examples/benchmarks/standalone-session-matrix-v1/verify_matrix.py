#!/usr/bin/env python3
"""Reconcile retained Session matrix evidence without importing project code."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics

WORKLOADS = ("silence", "performance", "dense", "recovery")
RATES = (44100, 48000, 96000)
BUFFERS = (128, 256, 512, 1024, 2048)
SHARED_KEYS = ("schema", "status", "scope", "workload_version", "iterations",
               "warmup", "seed", "initial_frame", "session_model", "source_model",
               "build", "profile", "claims")
ZERO_CONTROLS = {
    "upper_a": [0] * 9, "upper_b": [0] * 9,
    "lower_a": [0] * 9, "lower_b": [0] * 9,
    "selected_banks": [1, 1], "route_enabled": [True, True],
    "pedal_drawbars": [0, 0], "expression": 1,
    "percussion": {"enabled": False, "harmonic": 0, "volume": 0, "decay": 0},
}
PLAY_CONTROLS = {
    **ZERO_CONTROLS,
    "upper_b": [8, 8, 8, 0, 0, 0, 0, 0, 0],
    "lower_b": [0, 0, 8, 8, 0, 0, 0, 0, 0],
    "pedal_drawbars": [8, 5], "expression": 0.75,
    "percussion": {"enabled": True, "harmonic": 1, "volume": 1, "decay": 1},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for name, value in pairs:
        require(name not in result, f"duplicate JSON member: {name}")
        result[name] = value
    return result


def loads(text):
    def constant(token):
        raise ValueError(f"non-JSON constant: {token}")
    return json.loads(text, object_pairs_hook=unique, parse_constant=constant)


def semantic_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def equal(actual, expected, label):
    if isinstance(expected, dict):
        require(type(actual) is dict and actual.keys() == expected.keys(), label + ": keys")
        for key in expected:
            equal(actual[key], expected[key], label + "." + key)
    elif isinstance(expected, list):
        require(type(actual) is list and len(actual) == len(expected), label + ": array")
        for index, value in enumerate(expected):
            equal(actual[index], value, f"{label}[{index}]")
    elif type(expected) in (int, float):
        require(type(actual) in (int, float) and math.isfinite(actual) and actual == expected, label)
    else:
        require(type(actual) is type(expected) and actual == expected, label)


def distribution(samples):
    ordered = sorted(samples)
    require(bool(ordered), "empty interval array")
    return {"minimum": ordered[0], "median": statistics.median(ordered),
            "p95": ordered[math.ceil(len(ordered) * 0.95) - 1],
            "p99": ordered[math.ceil(len(ordered) * 0.99) - 1],
            "maximum": ordered[-1], "total": math.fsum(ordered)}


def close(actual, expected, label):
    require(type(actual) in (int, float) and math.isfinite(actual) and
            math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-6), label)


def verify_report(report):
    """Use literal public workload/count/state contracts and independent sums."""
    work, rate, block = (report[name] for name in ("workload", "sample_rate_hz", "buffer_frames"))
    require(work in WORKLOADS and rate in RATES and block in BUFFERS, "case domain")
    iterations, warmup = report["iterations"], report["warmup"]
    require(type(iterations) is int and type(warmup) is int and
            (iterations, warmup) == (100, 16), "fixed matrix lengths")
    for key, expected in {
        "schema": "hammond-standalone-benchmark-v1", "status": "ok",
        "workload_version": 1, "seed": 0, "initial_frame": 0,
        "session_model": "standalone-callback-boundary-session-v1",
        "source_model": "ideal-shared-sine-v1",
    }.items():
        equal(report[key], expected, key)
    setup = {"silence": 0, "performance": 7, "dense": 7, "recovery": 1}[work]
    accepted = 256 if work == "dense" else 262 if work == "recovery" else 0
    applied = 256 if work == "dense" else 6 if work == "recovery" else 0
    discarded = 256 if work == "recovery" else 0
    recovering = int(work == "recovery")
    require(set(report["stages"]) == {"setup", "warmup", "measured"}, "stage names")
    for stage, cycles, earlier in (("setup", 0, 0), ("warmup", warmup, 0),
                                  ("measured", iterations, warmup)):
        values = report["stages"][stage]
        require(all(type(value) is int and value >= 0 for value in values.values()), "integer stage counts")
        expected = {
            "post_attempts": cycles * (accepted + 2 * recovering),
            "accepted_commands": cycles * accepted, "applied_commands": cycles * applied,
            "discarded_commands": cycles * discarded, "queue_full_posts": cycles * recovering,
            "recovery_pending_posts": cycles * recovering, "recoveries": cycles * recovering,
            "positive_render_calls": cycles, "zero_frame_render_calls": cycles * recovering,
            "rendered_frames": cycles * block, "start_frame": earlier * block,
            "end_frame": (earlier + cycles) * block,
            "start_resolved_sequence": setup + earlier * accepted,
            "end_resolved_sequence": setup + (earlier + cycles) * accepted,
        }
        if stage == "setup":
            expected.update(post_attempts=setup, accepted_commands=setup, applied_commands=setup,
                            zero_frame_render_calls=1, start_resolved_sequence=0)
        equal(values, expected, stage)
        require(values["accepted_commands"] == values["applied_commands"] +
                values["discarded_commands"], stage + ": accepted reconciliation")
    controls = ZERO_CONTROLS if work == "silence" else PLAY_CONTROLS
    previous_revision = 0
    for stage, cycles in (("after_setup", 0), ("after_warmup", warmup),
                          ("after_measurement", warmup + iterations),
                          ("after_stop", warmup + iterations)):
        snapshot = report["snapshots"][stage]
        stopped = stage == "after_stop"
        holds = work in ("performance", "dense") and not stopped
        recovered = recovering and cycles > 0
        expected = {
            "prepared": True, "running": not stopped, "sample_rate_hz": rate,
            "frame_clock": cycles * block, "resolved_sequence": setup + cycles * accepted,
            "last_applied_sequence": setup + cycles * accepted - (256 if recovered else 0),
            "recovery_count": cycles * recovering, "queue_overflows": cycles * recovering,
            "rejected_commands": 0, "discarded_commands": cycles * discarded,
            "fault_flags": int(bool(recovered)), "last_core_status": "ok",
            "held_upper_midi": [60, 64, 67] if holds else [],
            "held_lower_midi": [48, 55] if holds else [],
            "held_pedal_ids": [1] if holds else [], "controls": controls,
        }
        for field, value in expected.items():
            equal(snapshot[field], value, stage + "." + field)
        revision = snapshot["publication_revision"]
        require(type(revision) is int and revision > previous_revision and revision % 2 == 0,
                stage + ": advancing coherent revision")
        previous_revision = revision
        peak = snapshot["peak"]
        require(type(peak) in (int, float) and math.isfinite(peak) and peak >= 0, stage + ": peak")
        require(peak > 0 if holds and cycles else peak == 0, stage + ": expected activity")
    period = block * 1_000_000_000 / rate
    close(report["nominal_callback_period_ns"], period, "callback period formula")
    timing = report["timing"]
    equal(timing["clock"], "std::chrono::steady_clock", "steady clock name")
    for key, wanted in (("clock_is_steady", True), ("warmup_included", False),
                        ("timer_overhead_subtracted", False)):
        equal(timing[key], wanted, key)
    require(math.isfinite(timing["clock_tick_seconds"]) and timing["clock_tick_seconds"] > 0,
            "positive nominal clock tick")
    samples = timing["samples_ns"]
    require(type(samples) is list and len(samples) == iterations and
            all(type(value) in (int, float) and math.isfinite(value) and value >= 0 for value in samples),
            "all chronological measured intervals")
    calculated = distribution(samples)
    require(set(timing["render_ns"]) == set(calculated), "distribution fields")
    for key, value in calculated.items():
        close(timing["render_ns"][key], value, "independent render " + key)
        if key != "total":
            close(timing["callback_period_ratio"][key], value / period, "period ratio " + key)
    equal(timing["observed_calls_above_period"], sum(value > period for value in samples),
          "unfiltered above-period observations")
    require(timing["measured_loop_elapsed_ns"] >= calculated["total"], "enclosing measured loop")
    calibration = timing["clock_pair_calibration"]
    equal(calibration["iterations"], 1000, "calibration iterations")
    ordered = [calibration["ns"][key] for key in ("minimum", "median", "p95", "p99", "maximum")]
    require(all(math.isfinite(value) and value >= 0 for value in calibration["ns"].values()) and
            ordered == sorted(ordered), "calibration distribution consistency")
    require(1000 * ordered[0] <= calibration["ns"]["total"] <= 1000 * ordered[-1],
            "calibration total bounds")
    audio = report["audio"]
    for key, wanted in (("measured_stereo_samples", 2 * iterations * block),
                        ("all_samples_finite", True), ("channels_bit_identical", True)):
        equal(audio[key], wanted, "audio " + key)
    require(math.isfinite(audio["measured_peak_max"]), "finite output peak")
    if work in ("silence", "recovery"):
        equal(audio["measured_peak_max"], 0, "silent measured peak")
        zero_hash = 14695981039346656037 * pow(1099511628211, 8 * block * iterations, 1 << 64) % (1 << 64)
        equal(audio["measured_stereo_fnv1a64"], f"{zero_hash:016x}", "independent silent float byte hash")
    else:
        require(audio["measured_peak_max"] > 0, "sounding measured peak")
    equal(report["claims"], {"hard_realtime": False, "device_deadline_pass": None,
          "device_underruns": None, "device_latency_seconds": None,
          "timing_threshold_applied": False}, "claim boundary")
    return calculated


def verify_matrix(matrix):
    require(matrix["schema"] == "hammond-session-matrix-evidence-v1", "matrix schema")
    common = matrix["common_report"]
    require(set(common) == set(SHARED_KEYS), "common report fields")
    reports = {}
    totals = {"cases": 0, "measured_calls": 0, "warmup_calls": 0, "measured_frames": 0,
              "warmup_frames": 0, "stereo_samples": 0, "above_period_observations": 0}
    for case in matrix["cases"]:
        require(not (set(case["report"]) & set(common)), "deduplicated report collision")
        report = {**common, **case["report"]}
        require(semantic_sha256(report) == case["parsed_report_sha256"], "reconstructed complete report digest")
        require(case["returncode"] == 0 and case["stderr_bytes"] == 0, "actual process success")
        verify_report(report)
        key = (report["workload"], report["sample_rate_hz"], report["buffer_frames"])
        require(key not in reports, "duplicate case")
        reports[key] = report
        totals["cases"] += 1
        totals["measured_calls"] += report["iterations"]
        totals["warmup_calls"] += report["warmup"]
        totals["measured_frames"] += report["stages"]["measured"]["rendered_frames"]
        totals["warmup_frames"] += report["stages"]["warmup"]["rendered_frames"]
        totals["stereo_samples"] += report["audio"]["measured_stereo_samples"]
        totals["above_period_observations"] += report["timing"]["observed_calls_above_period"]
    require(set(reports) == set(itertools.product(WORKLOADS, RATES, BUFFERS)), "complete 4 by 3 by 5 matrix")
    for rate, block in itertools.product(RATES, BUFFERS):
        ordinary = reports[("performance", rate, block)]["audio"]
        dense = reports[("dense", rate, block)]["audio"]
        equal(dense, ordinary, f"unchanged sound with dense control boundary {rate}/{block}")
    manifest = matrix["source"]["benchmark_manifest"]
    entries = manifest["entries"]
    require(len(entries) == 57 and [e["path"] for e in entries] == sorted({e["path"] for e in entries}),
            "57 unique ordered source inputs")
    fingerprint = hashlib.sha256("".join(f'{e["path"]}:{e["sha256"]}\n' for e in entries).encode()).hexdigest()
    equal(fingerprint, manifest["source_manifest_sha256"], "recomputed source fingerprint")
    equal(fingerprint, common["build"]["source_manifest_sha256"], "reported build fingerprint")
    return totals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path, nargs="?", default=Path(__file__).with_name("matrix.json"))
    args = parser.parse_args()
    result = verify_matrix(loads(args.matrix.read_text(encoding="utf-8")))
    print(json.dumps({"status": "passed", **result,
                      "scope": "retained arithmetic, state and coverage; no device timing threshold"}, indent=2))


if __name__ == "__main__":
    main()
