#!/usr/bin/env python3
"""Compare one confined-reader allocation change in private, coherent tool copies.

This fixed stdlib experiment does not edit source directories or real archives.
It publishes one new JSON artifact, with complete canonical before/after reports.
Traced Python allocation is not RSS, native memory, latency or a public limit.
"""

import argparse
import copy
import gc
import hashlib
import importlib
import json
import os
from pathlib import Path
import platform
import stat
import subprocess
import sys
import tempfile
import tracemalloc


MODULES = (
    "capture_audio", "capture_common", "capture_corpus", "capture_job",
    "capture_readiness", "capture_study", "compare_capture",
    "make_capture_demo", "validate_capture", "verify_capture_report",
)
SOURCE_LIMIT = 1048576
REPORT_LIMIT = 16 * 1048576
REPEATS = 3
PROTOCOL_SHA256 = "f045d9ef6a5abaa7217d440ea32ca84d734b0af46efb83061da1fec563a5a277"
BEGIN = b"<!-- BEGIN FROZEN PROTOCOL -->"
END = b"<!-- END FROZEN PROTOCOL -->\n"


class ExperimentError(ValueError):
    """A complete comparison was not obtained."""


def require(condition, message):
    if not condition:
        raise ExperimentError(message)


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False,
                       sort_keys=True, indent=2) + "\n").encode("utf-8")


def identity(payload):
    return {"size_bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest()}


def stamp(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def bounded_bytes(path, limit):
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and not path.is_symlink(),
            f"expected a regular nonsymlink file: {path.name}")
    require(0 <= before.st_size <= limit, f"input exceeds bound: {path.name}")
    with path.open("rb") as stream:
        opened = os.fstat(stream.fileno())
        require(stamp(opened) == stamp(before), f"input changed before read: {path.name}")
        payload = stream.read(before.st_size + 1)
        require(stamp(os.fstat(stream.fileno())) == stamp(before),
                f"input changed during read: {path.name}")
    require(len(payload) == before.st_size and stamp(path.lstat()) == stamp(before),
            f"input changed after read: {path.name}")
    return payload


def source_set(root):
    require(root.is_dir() and not root.is_symlink(),
            "tools root must be an existing nonsymlink directory")
    return {name + ".py": bounded_bytes(root / (name + ".py"), SOURCE_LIMIT)
            for name in MODULES}


def source_inventory(sources):
    return [{"module": name, **identity(payload)} for name, payload in sources.items()]


def fixture_inventory(root):
    rows = []
    total = 0
    for path in sorted(root.rglob("*")):
        require(not path.is_symlink(), "fixture unexpectedly contains a symlink")
        if path.is_dir():
            continue
        payload = bounded_bytes(path, SOURCE_LIMIT)
        total += len(payload)
        require(len(rows) < 16 and total <= 32831, "fixed fixture bound exceeded")
        rows.append({"path": path.relative_to(root).as_posix(), **identity(payload)})
    require(len(rows) == 16 and total == 32831, "fixed demo fixture changed")
    return rows


def measure(call, *, bytes_result=False):
    require(not tracemalloc.is_tracing(), "allocation tracer was already active")
    warm = call()
    expected = warm if bytes_result else canonical(warm)
    del warm
    samples = []
    for number in range(1, REPEATS + 1):
        gc.collect()
        tracemalloc.start(1)
        try:
            result = call()
            current, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        observed = result if bytes_result else canonical(result)
        require(observed == expected, "complete operation result changed between calls")
        samples.append({"sample": number, "current_bytes": current, "peak_bytes": peak})
        del result, observed
    return {"warmup_calls": 1, "traced_calls": REPEATS, "traceback_frames": 1,
            "result": identity(expected), "samples": samples}


def witness_request(corpus, root, filename, expected):
    requests = []
    original = corpus._stream

    class Witness:
        def __init__(self, stream):
            self.stream = stream

        def __enter__(self):
            self.stream.__enter__()
            return self

        def __exit__(self, *args):
            return self.stream.__exit__(*args)

        def fileno(self):
            return self.stream.fileno()

        def read(self, amount):
            requests.append(amount)
            return self.stream.read(amount)

    require(not tracemalloc.is_tracing(), "request witness must run outside tracing")
    corpus._stream = lambda descriptor: Witness(original(descriptor))
    try:
        observed = corpus._read_confined_bytes(root, [filename], max_bytes=REPORT_LIMIT)
    finally:
        corpus._stream = original
    require(len(requests) == 1 and observed == expected, "read witness was not reached exactly once")
    return {"calls": 1, "requested_bytes": requests[0], "consumed_bytes": len(observed),
            "original_bytes_equal": True, "traced": False}


def worker(work, variant):
    """Each invocation runs in a separate interpreter against one private copy."""
    work = work.resolve(strict=True)
    tools_root = work / variant / "tools"
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(tools_root))
    modules = {name: importlib.import_module(name) for name in MODULES}
    for name, module in modules.items():
        require(Path(module.__file__).resolve() == tools_root / (name + ".py"),
                "a module was imported outside its coherent private copy")
    sources_before = source_set(tools_root)
    corpus = modules["capture_corpus"]
    study = modules["capture_study"]
    replay = modules["verify_capture_report"]
    demo = work / "demo"
    if variant == "before":
        inventory = modules["make_capture_demo"].build_demo(demo)
        require(inventory["file_count"] == 16 and inventory["execution"] == "not_run",
                "demo generator behavior changed")
    fixture_before = fixture_inventory(demo)
    study_path = demo / "study.json"
    report = study.run_study(study_path)
    report_bytes = canonical(report)
    require(report["status"] == "failed", "fixed study engineering outcome changed")
    require([job["report"]["status"] for job in report["jobs"]]
            == ["pass", "inconclusive", "failed"], "fixed job outcomes changed")
    require(len(report_bytes) <= REPORT_LIMIT, "saved report exceeds replay bound")
    report_path = work / (variant + "-study.json")
    with report_path.open("xb") as output:
        output.write(report_bytes)
    original_path = work / "before-study.json"
    original_bytes = bounded_bytes(original_path, REPORT_LIMIT)
    request = witness_request(corpus, work, original_path.name, original_bytes)
    isolated = measure(lambda: corpus._read_confined_bytes(
        work, [original_path.name], max_bytes=REPORT_LIMIT), bytes_result=True)
    require(isolated["result"] == identity(original_bytes), "isolated bytes changed")
    replay_call = lambda: replay.verify_report("study", study_path, report_path)
    replay_measurement = measure(replay_call)
    fresh_summary = replay_call()
    require(fresh_summary["status"] == "match" and fresh_summary["exact_report_match"],
            "same-source fresh report does not replay exactly")
    require(fresh_summary["saved_engineering_status"]
            == fresh_summary["replayed_engineering_status"] == "failed",
            "replay changed the failed engineering result")
    old_summary = None
    if variant == "after":
        old_summary = replay.verify_report("study", study_path, original_path)
        require(old_summary["status"] == "mismatch" and not old_summary["exact_report_match"],
                "old source report should remain a complete-report mismatch")
        require(old_summary["context"]["same_runtime"]
                and not old_summary["context"]["same_tool_sources"],
                "old report mismatch lacks the expected changed-source context")
    require(source_set(tools_root) == sources_before, "copied sources changed during execution")
    require(fixture_inventory(demo) == fixture_before, "fixture changed during execution")
    require(bounded_bytes(original_path, REPORT_LIMIT) == original_bytes,
            "original saved report changed")
    require(bounded_bytes(report_path, REPORT_LIMIT) == report_bytes,
            "fresh saved report changed")
    value = {
        "variant": variant, "sources": source_inventory(sources_before),
        "runtime": {"python_implementation": platform.python_implementation(),
                    "python_version": platform.python_version(), "python_build": sys.version,
                    "system": platform.system(), "release": platform.release(),
                    "machine": platform.machine(), "gc_enabled": gc.isenabled()},
        "fixture": fixture_before, "original_report": identity(original_bytes),
        "fresh_report": identity(report_bytes), "witness": request,
        "isolated_reader": isolated, "complete_fresh_replay": replay_measurement,
        "fresh_replay_summary": fresh_summary, "old_report_replay_summary": old_summary,
        "copied_sources_unchanged": True, "fixture_unchanged": True,
        "saved_reports_unchanged": True,
    }
    with (work / (variant + "-observations.json")).open("xb") as output:
        output.write(canonical(value))


def projection(report):
    projected = copy.deepcopy(report)
    require(type(projected.get("tool_sources")) is list and len(projected["jobs"]) == 3,
            "unexpected study report projection shape")
    del projected["tool_sources"]
    paths = ["/tool_sources"]
    for index, job in enumerate(projected["jobs"]):
        require(type(job["report"].get("tool_sources")) is list,
                "embedded job source observation is missing")
        del job["report"]["tool_sources"]
        paths.append(f"/jobs/{index}/report/tool_sources")
    return canonical(projected), paths


def publish_new(output, payload):
    require(output.parent.is_dir() and not output.parent.is_symlink(),
            "output parent must be an existing nonsymlink directory")
    descriptor, temporary = tempfile.mkstemp(prefix=".capture-allocation-", dir=output.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, output)
    finally:
        os.unlink(temporary)


def collect(before_root, after_root, output, protocol_path):
    require(not tracemalloc.is_tracing(), "run without a pre-existing allocation tracer")
    require(not output.exists() and not output.is_symlink(), "output already exists")
    resolved_output = output.parent.resolve(strict=True) / output.name
    for source_root in (before_root, after_root):
        resolved_root = source_root.resolve(strict=True)
        require(resolved_output != resolved_root and resolved_root not in resolved_output.parents,
                "output must be outside both original tools directories")
    own_path = Path(__file__).resolve(strict=True)
    own_bytes = bounded_bytes(own_path, SOURCE_LIMIT)
    protocol_document = bounded_bytes(protocol_path, 65536)
    start = protocol_document.index(BEGIN)
    stop = protocol_document.index(END, start) + len(END)
    protocol = protocol_document[start:stop]
    require(identity(protocol)["sha256"] == PROTOCOL_SHA256, "frozen protocol identity changed")
    sources = {"before": source_set(before_root), "after": source_set(after_root)}
    changes = [name for name in sources["before"]
               if sources["before"][name] != sources["after"][name]]
    require(changes == ["capture_corpus.py"], "only the corpus source may differ")
    observations = {}
    reports = {}
    with tempfile.TemporaryDirectory(prefix="capture-allocation-") as temporary:
        work = Path(temporary).resolve(strict=True)
        runner = work / "check_allocation.py"
        runner.write_bytes(own_bytes)
        for variant in ("before", "after"):
            destination = work / variant / "tools"
            destination.mkdir(parents=True)
            for name, payload in sources[variant].items():
                (destination / name).write_bytes(payload)
            require(source_set(destination) == sources[variant], "source copy differs")
        for variant in ("before", "after"):
            run = subprocess.run([sys.executable, "-I", "-B", str(runner),
                                  "--worker", variant, "--work", str(work)],
                                 capture_output=True, timeout=120, check=False)
            require(run.returncode == 0,
                    f"{variant} subprocess failed: {run.stderr.decode('utf-8', errors='replace')}")
            require(not run.stdout and not run.stderr, "worker emitted unexpected console output")
            observations[variant] = json.loads(bounded_bytes(
                work / (variant + "-observations.json"), SOURCE_LIMIT))
            report_bytes = bounded_bytes(work / (variant + "-study.json"), REPORT_LIMIT)
            report_value = json.loads(report_bytes)
            require(canonical(report_value) == report_bytes, "original saved report is not canonical")
            reports[variant] = {"identity": identity(report_bytes), "value": report_value}
        for variant in ("before", "after"):
            require(source_set(work / variant / "tools") == sources[variant],
                    "private source set changed after the worker returned")
            retained = bounded_bytes(work / (variant + "-study.json"), REPORT_LIMIT)
            require(identity(retained) == reports[variant]["identity"],
                    "saved report changed after its worker returned")
        require(fixture_inventory(work / "demo") == observations["before"]["fixture"]
                == observations["after"]["fixture"], "shared archive changed between source sets")
        require(bounded_bytes(runner, SOURCE_LIMIT) == own_bytes, "private collector changed")
    require(source_set(before_root) == sources["before"]
            and source_set(after_root) == sources["after"], "original sources changed")
    require(bounded_bytes(own_path, SOURCE_LIMIT) == own_bytes, "collector changed")
    require(observations["before"]["runtime"] == observations["after"]["runtime"],
            "worker runtime changed")
    require(observations["before"]["witness"]["requested_bytes"] == REPORT_LIMIT + 1,
            "baseline request no longer equals the loose cap plus one")
    require(observations["after"]["witness"]["requested_bytes"]
            == reports["before"]["identity"]["size_bytes"] + 1,
            "candidate request does not equal admitted file size plus one")
    before_projection, removed = projection(reports["before"]["value"])
    after_projection, after_removed = projection(reports["after"]["value"])
    require(removed == after_removed and before_projection == after_projection,
            "source-independent complete study content changed")
    decisions = {}
    for operation in ("isolated_reader", "complete_fresh_replay"):
        before_peaks = [sample["peak_bytes"] for sample in observations["before"][operation]["samples"]]
        after_peaks = [sample["peak_bytes"] for sample in observations["after"][operation]["samples"]]
        decisions[operation] = {
            "all_after_peaks_below_all_before_peaks": max(after_peaks) < min(before_peaks),
            "paired_peak_reduction_bytes": [old - new for old, new in zip(before_peaks, after_peaks)],
        }
    value = {
        "experiment": "confined-metadata-allocation-v1", "collector": identity(own_bytes),
        "protocol": identity(protocol), "changed_modules": changes,
        "before": observations["before"], "after": observations["after"],
        "retained_reports": {"serialization": "canonical UTF-8 JSON, sorted keys, two-space indent, final LF",
                             **reports},
        "source_independent_content": {"removed_paths": removed,
                                       "before": identity(before_projection),
                                       "after": identity(after_projection), "exact_bytes_equal": True,
                                       "used_by_public_replay": False},
        "resource_decision": decisions,
        "resource_observation_supported": all(row["all_after_peaks_below_all_before_peaks"]
                                              for row in decisions.values()),
        "original_sources_unchanged": True, "collector_unchanged": True,
        "scope": "fixed offline synthetic workload; traced Python allocations only; not RSS, latency, native memory or physical fidelity",
    }
    publish_new(output, canonical(value))
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--before-tools", type=Path)
    parser.add_argument("--after-tools", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--protocol", type=Path)
    parser.add_argument("--worker", choices=("before", "after"), help=argparse.SUPPRESS)
    parser.add_argument("--work", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        if args.worker:
            require(args.work is not None, "internal worker requires its private work directory")
            worker(args.work, args.worker)
            return 0
        require(all(value is not None for value in (args.before_tools, args.after_tools, args.output)),
                "--before-tools, --after-tools and --output are required")
        protocol_path = args.protocol
        if protocol_path is None:
            protocol_path = Path(__file__).resolve().parents[3] / "docs/reviews/CALIBRATION_METADATA_ALLOCATION.md"
        output = Path(os.path.abspath(args.output))
        value = collect(args.before_tools, args.after_tools, output, protocol_path)
        print(json.dumps({"output": str(output),
                          "resource_observation_supported": value["resource_observation_supported"]},
                         sort_keys=True))
        return 0 if value["resource_observation_supported"] else 1
    except (ExperimentError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"allocation experiment error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
