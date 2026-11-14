#!/usr/bin/env python3
"""Collect twelve bounded offline observations; no performance threshold is set.

Only the explicitly requested new results file is published. The selected ten
tool sources are copied into a private temporary workspace before importing.
Run in a fresh Python process; keep the selected sources quiescent throughout.
"""

from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import gc
import hashlib
import importlib
import json
import os
from pathlib import Path
import platform
import stat
import statistics
import struct
import sys
import tempfile
import time
import tracemalloc


MODULES = (
    "capture_audio", "capture_common", "capture_corpus", "capture_job",
    "capture_readiness", "capture_study", "compare_capture",
    "make_capture_demo", "validate_capture", "verify_capture_report",
)
SOURCE_LIMIT = 1048576
RATE = 48000
CHANNELS = 2
AUDIO_FRAMES = (16384, 65536)
WINDOW_FRAMES = 1024
COMPARISON_FRAMES = (1024, 8192)
FREQUENCIES = (0, 187.5, 375, 750, 1500, 3000, 6000, 12000)
OFFSET = 1 / 128
REPEATS = 3
ARRAY_DOMAIN = b"HAMMOND-CAPTURE-BENCH-ARRAYS-V1\x00"


class ProfileError(ValueError):
    """Collection failed; no completed observation may be inferred."""


def require(condition, message):
    if not condition:
        raise ProfileError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


def identity(payload):
    return {"size_bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}


def source_bytes(path):
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and not path.is_symlink(),
            f"source must be a regular nonsymlink file: {path.name}")
    require(0 < before.st_size <= SOURCE_LIMIT, f"source size is outside bounds: {path.name}")
    with path.open("rb") as stream:
        payload = stream.read(SOURCE_LIMIT + 1)
    after = path.lstat()
    stamp = lambda value: (value.st_dev, value.st_ino, value.st_size,
                           value.st_mtime_ns, value.st_ctime_ns)
    require(stamp(before) == stamp(after) and len(payload) == before.st_size,
            f"source changed while being copied: {path.name}")
    return payload


def source_inventory(root):
    return [{"module": name + ".py", **identity(source_bytes(root / (name + ".py")))}
            for name in MODULES]


def file_inventory(root):
    rows = []
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink(), "temporary fixture unexpectedly became a symlink")
        if path.is_file():
            rows.append({"path": path.relative_to(root).as_posix(), **identity(path.read_bytes())})
    return rows


def saw(frame, channel):
    return (((frame * (channel + 1)) % 257) - 128) / 256


def array_identity(channels):
    digest = hashlib.sha256(ARRAY_DOMAIN)
    digest.update(struct.pack("<II", len(channels), len(channels[0])))
    for channel in channels:
        for sample in channel:
            digest.update(struct.pack("<d", sample))
    return {"sha256": digest.hexdigest(), "channel_count": len(channels),
            "frame_count": len(channels[0]),
            "encoding": "domain-NUL, little-endian uint32 C,N, channel-major float64"}


def portable_output(report, case):
    result = copy.deepcopy(report)
    if case["category"] == "audio":
        inspection = result if case["operation"] == "inspect" else result["inspection"]
        inspection["input_path"] = case["fixture"]
    return result


def check_result(case, result):
    category = case["category"]
    if category == "audio":
        inspection = result if case["operation"] == "inspect" else result["inspection"]
        require(inspection["status"] == "inspected", "audio did not complete inspection")
        require(inspection["frame_count"] == case["work"]["stream_frames"]
                and inspection["channel_count"] == CHANNELS
                and inspection["sample_rate_hz"] == RATE, "audio geometry differs")
        require(inspection["sha256"] == case["input_identity"]["sha256"], "audio byte identity differs")
        require(inspection["physical_fidelity"] == "not_established", "audio claim changed")
        if case["operation"] == "window":
            start = case["work"]["window_start"]
            expected = [[saw(start + n, c) for n in range(WINDOW_FRAMES)]
                        for c in range(CHANNELS)]
            require(result["samples"] == expected, "selected literal samples differ")
        return {"status": "inspected", "physical_fidelity": "not_established"}
    if category == "comparison":
        require(result["metric_contract"] == "capture-comparison-v1", "comparison contract changed")
        require(result["frame_count"] == case["work"]["frames"]
                and result["channel_count"] == CHANNELS, "comparison geometry differs")
        for channel in result["channels"]:
            for metric in ("dc_bias_fs", "rms_error_fs", "max_abs_error_fs"):
                require(channel["metrics"][metric]["value"] == OFFSET,
                        "literal binary-exact offset metric differs")
            require(len(channel["frequencies"]) == len(FREQUENCIES), "frequency coverage differs")
        require(result["physical_fidelity"] == "not_established", "comparison claim changed")
        return {"status": "calculated", "rms_error_fs": OFFSET,
                "physical_fidelity": "not_established"}
    require(result["status"] == case["expected_status"], "pipeline outcome changed")
    require(result["physical_fidelity"] == "not_established", "pipeline claim changed")
    if case["operation"] == "study":
        require([entry["report"]["status"] for entry in result["jobs"]]
                == ["pass", "inconclusive", "failed"], "study dropped or reordered outcomes")
        require(result["summary"]["jobs"] == 3, "study job count differs")
    outcome = {"status": result["status"], "physical_fidelity": "not_established"}
    if case["operation"] == "replay":
        require(result["exact_report_match"] is True, "complete study replay differs")
        require(result["saved_engineering_status"] == "failed"
                and result["replayed_engineering_status"] == "failed",
                "replay changed the underlying failed outcome")
        outcome["saved_engineering_status"] = "failed"
        outcome["replayed_engineering_status"] = "failed"
    return outcome


def measure(case):
    # Garbage collection and fixture validation are outside every timed interval.
    gc.collect()
    start = time.perf_counter_ns()
    result = case["call"]()
    warmup_ns = time.perf_counter_ns() - start
    outcome = check_result(case, result)
    baseline = canonical(result)
    portable = canonical(portable_output(result, case))
    result = None
    samples = []
    for _ in range(REPEATS):
        gc.collect()
        start = time.perf_counter_ns()
        result = case["call"]()
        elapsed = time.perf_counter_ns() - start
        require(check_result(case, result) == outcome, "ordinary outcome changed")
        require(canonical(result) == baseline, "ordinary complete API output changed")
        samples.append(elapsed)
        result = None
    gc.collect()
    require(not tracemalloc.is_tracing(), "collection requires tracing to be initially disabled")
    tracemalloc.start(1)
    try:
        start = time.perf_counter_ns()
        result = case["call"]()
        traced_ns = time.perf_counter_ns() - start
        current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    require(check_result(case, result) == outcome, "traced outcome changed")
    require(canonical(result) == baseline, "traced complete API output changed")
    result = None
    return {key: value for key, value in case.items() if key != "call"} | {
        "observed_outcome": outcome,
        "warmup": {"calls": 1, "elapsed_ns": warmup_ns, "included_in_statistics": False},
        "ordinary": {"samples_ns": samples, "min_ns": min(samples),
                     "median_ns": statistics.median(samples), "max_ns": max(samples)},
        "separate_tracemalloc": {"calls": 1, "traceback_frames": 1,
                                 "elapsed_ns": traced_ns, "current_bytes_at_return": current,
                                 "peak_bytes_during_call": peak,
                                 "included_in_ordinary_statistics": False},
        "complete_api_output": identity(baseline),
        "portable_output": identity(portable),
        "portable_output_change": ("only audio input_path replaced by fixture-relative path"
                                   if case["category"] == "audio" else "none"),
    }


def make_cases(modules, inputs):
    audio = modules["capture_audio"]
    compare = modules["compare_capture"]
    corpus = modules["capture_corpus"]
    job = modules["capture_job"]
    study = modules["capture_study"]
    replay = modules["verify_capture_report"]
    cases, arrays = [], []
    (inputs / "audio").mkdir()
    for frames in AUDIO_FRAMES:
        path = inputs / "audio" / f"stereo-{frames}.f32"
        payload = b"".join(struct.pack("<ff", saw(n, 0), saw(n, 1)) for n in range(frames))
        path.write_bytes(payload)
        observed = identity(payload)
        for operation in ("inspect", "window"):
            start_frame = (frames - WINDOW_FRAMES) // 2
            options = {"raw_format": "raw_float32_le", "sample_rate_hz": RATE,
                       "channel_count": CHANNELS}
            call = (lambda p=path, o=options: audio.inspect_audio(p, **o)) if operation == "inspect" else (
                lambda p=path, s=start_frame, o=options:
                audio.read_audio_window(p, s, WINDOW_FRAMES, **o))
            cases.append({"case_id": f"audio-{operation}-{frames}", "category": "audio",
                          "operation": operation, "fixture": path.relative_to(inputs).as_posix(),
                          "input_identity": observed,
                          "work": {"stream_frames": frames, "channels": CHANNELS,
                                   "decoded_scalars": frames * CHANNELS, "file_bytes": len(payload),
                                   "sample_rate_hz": RATE,
                                   "window_start": start_frame if operation == "window" else None,
                                   "returned_window_frames": WINDOW_FRAMES if operation == "window" else 0,
                                   "complete_stream_validated": True}, "call": call})
    for frames in COMPARISON_FRAMES:
        reference = [[saw(n, c) for n in range(frames)] for c in range(CHANNELS)]
        candidate = [[value + OFFSET for value in channel] for channel in reference]
        arrays.extend((reference, candidate))
        cases.append({"case_id": f"comparison-{frames}", "category": "comparison",
                      "operation": "compare_signals", "input_identities": {
                          "reference": array_identity(reference), "candidate": array_identity(candidate)},
                      "work": {"frames": frames, "channels": CHANNELS, "frequencies": len(FREQUENCIES),
                               "window_samples_per_side": CHANNELS * frames,
                               "spectral_terms_per_side": CHANNELS * frames * len(FREQUENCIES),
                               "sample_rate_hz": RATE, "frequencies_hz": list(FREQUENCIES),
                               "window": "hann_symmetric", "floor_fs": 1e-12,
                               "candidate_offset_fs": OFFSET},
                      "call": lambda r=reference, c=candidate:
                      compare.compare_signals(r, c, RATE, frequencies_hz=list(FREQUENCIES),
                                              window="hann_symmetric", floor_fs=1e-12)})
    demo = inputs / "demo"
    inventory = modules["make_capture_demo"].build_demo(demo)
    require(inventory["file_count"] == 16 and inventory["execution"] == "not_run",
            "demo generator contract changed")
    work = {"captures": 3, "artifact_references": 3, "declared_artifact_bytes": 48}
    job_work = {**work, "declared_job_window_samples": 4, "declared_job_spectral_terms": 4}
    cases.append({"case_id": "demo-corpus", "category": "pipeline", "operation": "corpus",
                  "expected_status": "pass", "work": work,
                  "call": lambda: corpus.audit_corpus(demo / "corpus/corpus.json",
                                                       check_files=True, check_audio=True)})
    for token, expected in (("pass", "pass"), ("inconclusive", "inconclusive"), ("fail", "failed")):
        cases.append({"case_id": "demo-job-" + token, "category": "pipeline", "operation": "job",
                      "expected_status": expected, "work": job_work,
                      "call": lambda t=token: job.run_job(demo / f"job-{t}.json")})
    study_path = demo / "study.json"
    saved = inputs / "saved-study.json"
    saved.write_bytes(canonical(study.run_study(study_path)))
    study_work = {**work, "jobs": 3, "study_window_samples": 12, "study_spectral_terms": 12}
    cases.append({"case_id": "demo-study", "category": "pipeline", "operation": "study",
                  "expected_status": "failed", "work": study_work,
                  "call": lambda: study.run_study(study_path)})
    cases.append({"case_id": "demo-study-replay", "category": "pipeline", "operation": "replay",
                  "expected_status": "match", "work": study_work,
                  "call": lambda: replay.verify_report("study", study_path, saved)})
    require(len(cases) == 12, "fixed case count changed")
    return cases, arrays, inventory


def collect(tools_root, output):
    tools_root = tools_root.resolve(strict=True)
    require(tools_root.is_dir(), "tools root must be a directory")
    output = output.parent.resolve(strict=True) / output.name
    require(not output.is_relative_to(tools_root), "output must be outside the selected tools directory")
    require(not output.exists() and not output.is_symlink(), "output already exists; choose a new file")
    require(not any(name in sys.modules for name in MODULES), "run the collector in a fresh Python process")
    require(not tracemalloc.is_tracing(), "run without a pre-existing allocation tracer")
    own_bytes = source_bytes(Path(__file__))
    before = source_inventory(tools_root)
    started = datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix="hammond-capture-profile-") as temporary:
        workspace = Path(temporary).resolve()
        snapshot = workspace / "tools"
        snapshot.mkdir()
        for name in MODULES:
            (snapshot / (name + ".py")).write_bytes(source_bytes(tools_root / (name + ".py")))
        require(source_inventory(snapshot) == before == source_inventory(tools_root),
                "tool sources changed while preparing the coherent copy")
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(snapshot))
        modules = {name: importlib.import_module(name) for name in MODULES}
        require(all(Path(module.__file__).resolve().parent == snapshot for module in modules.values()),
                "an imported module escaped the coherent copied source set")
        inputs = workspace / "inputs"
        inputs.mkdir()
        cases, arrays, demo_inventory = make_cases(modules, inputs)
        files_before = file_inventory(inputs)
        arrays_before = [array_identity(value) for value in arrays]
        results = [measure(case) for case in cases]
        require(file_inventory(inputs) == files_before, "a fixture or saved report changed")
        require([array_identity(value) for value in arrays] == arrays_before, "an input array changed")
        require(source_inventory(snapshot) == before == source_inventory(tools_root),
                "tool sources changed during collection")
        require(source_bytes(Path(__file__)) == own_bytes, "collector source changed during collection")
        clock = time.get_clock_info("perf_counter")
        limits = {name + ".py": {key: value for key, value in sorted(vars(module).items())
                                 if (key.startswith("MAX_") or key == "CHUNK_BYTES")
                                 and type(value) in (int, float)}
                  for name, module in modules.items()}
        report = {
            "schema_version": 1, "observation_contract": "capture-resource-profile-v1",
            "status": "completed_observation", "collected_at_utc": started,
            "runtime": {"python_implementation": platform.python_implementation(),
                        "python_version": platform.python_version(), "sys_platform": sys.platform,
                        "machine": platform.machine(), "platform": platform.platform(),
                        "logical_cpu_count": os.cpu_count(), "gc_enabled": gc.isenabled()},
            "clock": {"implementation": clock.implementation, "monotonic": clock.monotonic,
                      "adjustable": clock.adjustable, "resolution_seconds": clock.resolution},
            "collector": identity(own_bytes), "tool_sources": before,
            "method": {"fixed_cases": 12, "warmups_per_case": 1, "ordinary_samples_per_case": REPEATS,
                       "traced_calls_per_case": 1, "top_level_profiled_api_calls": 60,
                       "setup_api_calls": {"make_capture_demo.build_demo": 1, "capture_study.run_study": 1},
                       "timed_scope": "public API call through return; setup, hashing, serialization and assertions excluded",
                       "output_encoding": "API dictionary encoded as sorted two-space UTF-8 JSON plus LF; not the compact audio CLI encoding",
                       "traced_scope": "Python allocations after setup/import/input allocation, during one separate call with returned result retained; not RSS or total process memory",
                       "cache_state": "uncontrolled; fixtures created and hashed before timing; one warmup per case",
                       "scheduler": "uncontrolled shared host; no CPU pinning or isolation",
                       "performance_threshold": None, "physical_fidelity": "not_established"},
            "declared_source_limits": limits, "demo_generation_inventory": demo_inventory,
            "fixture_files": files_before, "array_inputs": arrays_before, "cases": results,
            "identity_checks": {"original_tool_sources_unchanged": True, "copied_tool_sources_unchanged": True,
                                "fixture_files_unchanged": True, "array_inputs_unchanged": True,
                                "collector_unchanged": True},
            "limits": {"real_time_suitability": "not_established", "maximum_workload_execution": "not_run",
                       "process_memory_bound": "not_established", "cross_machine_comparison": "not_established",
                       "cold_cache_storage_cost": "not_measured", "physical_fidelity": "not_established"},
        }
        modules["capture_common"].write_json_new(output, report)
    return report


class SinglePath(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is not None or not values:
            parser.error(f"{option_string} requires one nonempty value, supplied once")
        setattr(namespace, self.dest, Path(values))


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--tools-root", required=True, action=SinglePath,
                        help="directory containing the ten coherent Python tool sources")
    parser.add_argument("--output", required=True, action=SinglePath,
                        help="new results JSON; parent must exist, outside the tools directory")
    args = parser.parse_args()
    try:
        result = collect(args.tools_root, args.output)
    except (OSError, ValueError, TypeError, ImportError, OverflowError, KeyError) as error:
        print(f"capture resource collection failed: {error}", file=sys.stderr)
        return 1
    print(f"Collected {len(result['cases'])} cases; 36 ordinary samples and 12 separate allocation traces.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
