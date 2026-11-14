#!/usr/bin/env python3
"""Run up to eight fixed, hash-bound capture jobs against one corpus identity.

All completed outcomes remain visible. Engineering results do not establish
physical acquisition, calibration, permissions, independence or fidelity.
Keep the complete archive and project sources quiescent during execution.
"""

from __future__ import annotations

import argparse
import copy
from pathlib import Path
import sys

import capture_common
import capture_corpus
import capture_job


MAX_STUDY_BYTES = 65536
MAX_STUDY_NODES = 4096
MAX_STUDY_DEPTH = 8
MAX_JOBS = 8
MAX_WINDOW_SAMPLES = 8388608
MAX_SPECTRAL_TERMS = 33554432
MAX_LEAF_SNAPSHOTS = 3000
MAX_ROOT_SNAPSHOTS = 64
MAX_SOURCE_BYTES = 1048576
MAX_REPORT_BYTES = 16777216
MAX_REPORT_NODES = 1048576
MAX_REPORT_DEPTH = 40
MAX_REPORT_NUMBER = 4e18
STUDY_KEYS = {"schema_version", "contract_origin", "study_id", "corpus_sha256", "jobs"}
ENTRY_KEYS = {"job_id", "path", "sha256"}
ROLES = ("fit", "validation", "final_test", "unassigned")
JOB_SOURCES = {"capture_audio.py", "capture_common.py", "capture_corpus.py",
               "capture_job.py", "compare_capture.py", "validate_capture.py"}
CLAIM_FIELDS = ("boundary_equivalence", "synchronization", "authenticity",
                "specimen_identity", "calibration", "permissions", "independence",
                "preregistration", "final_holdout_history", "physical_fidelity")


class StudyError(ValueError):
    """Rejected study input, dependency, identity, resource or publication."""


def _require(condition: bool, label: str, message: str) -> None:
    if not condition:
        raise StudyError(f"{label}: {message}")


def _keys(value: object, fields: set[str], label: str) -> None:
    _require(type(value) is dict and set(value) == fields, label,
             "expected exactly these keys: " + ", ".join(sorted(fields)))


def _guard_study(value: object) -> None:
    capture_common.validate_json_value(value, max_nodes=MAX_STUDY_NODES,
                                       max_depth=MAX_STUDY_DEPTH, max_number=1e12)
    pending = [value]
    while pending:
        item = pending.pop()
        if type(item) in (dict, list):
            _require(len(item) <= MAX_STUDY_NODES, "study JSON", "container member limit exceeded")
            if type(item) is dict:
                for key in item:
                    capture_job._text(key, "JSON key")
                pending.extend(item.values())
            else:
                pending.extend(item)
        elif type(item) is str:
            capture_job._text(item, "JSON string")


def validate_study(value: object) -> None:
    """Validate the exact study value and unique bindings without any I/O."""
    try:
        _guard_study(value)
        _keys(value, STUDY_KEYS, "study")
        _require(type(value["schema_version"]) is int and value["schema_version"] == 1,
                 "schema_version", "expected integer 1")
        _require(value["contract_origin"] == "project-proposed-capture-study-v1",
                 "contract_origin", "expected project-proposed-capture-study-v1")
        capture_corpus._id(value["study_id"], "study_id")
        capture_corpus._sha(value["corpus_sha256"], "corpus_sha256")
        jobs = value["jobs"]
        _require(type(jobs) is list and 1 <= len(jobs) <= MAX_JOBS,
                 "jobs", f"expected 1..{MAX_JOBS} job entries")
        ids, paths, hashes = set(), set(), set()
        for position, entry in enumerate(jobs):
            label = f"jobs[{position}]"
            _keys(entry, ENTRY_KEYS, label)
            capture_corpus._id(entry["job_id"], label + ".job_id")
            capture_corpus._path(entry["path"], label + ".path")
            capture_corpus._sha(entry["sha256"], label + ".sha256")
            _require(entry["job_id"] not in ids, label, "duplicate job ID")
            _require(entry["path"].casefold() not in paths, label, "duplicate case-folded job path")
            _require(entry["sha256"] not in hashes, label, "duplicate job SHA-256")
            ids.add(entry["job_id"])
            paths.add(entry["path"].casefold())
            hashes.add(entry["sha256"])
    except StudyError:
        raise
    except (ValueError, TypeError, OverflowError) as error:
        raise StudyError(f"study admission: {error}") from error


class _StudySnapshots(capture_job._Snapshots):
    """Retain every first observation across the complete bounded study."""

    def select(self, path: str | Path) -> tuple[Path, str]:
        _require(len(self.roots) < MAX_ROOT_SNAPSHOTS, "snapshots",
                 f"selected-root limit exceeded: {MAX_ROOT_SNAPSHOTS}")
        return super().select(path)

    def admit(self, root: Path, parts: list[str]) -> tuple:
        _require(len(self.leaves) < MAX_LEAF_SNAPSHOTS, "snapshots",
                 f"leaf limit exceeded: {MAX_LEAF_SNAPSHOTS}")
        return super().admit(root, parts)


def _read_study(path: str | Path, snapshots: _StudySnapshots) -> tuple:
    _require((type(path) is str and bool(path)) or isinstance(path, Path),
             "input", "expected an exact nonempty string or pathlib.Path")
    root, name = snapshots.select(path)
    payload, observation = capture_job._read_observed(
        root, [name], max_bytes=MAX_STUDY_BYTES, snapshots=snapshots)
    value = capture_common.parse_json_bytes(payload, max_bytes=MAX_STUDY_BYTES,
                                            max_nodes=MAX_STUDY_NODES,
                                            max_depth=MAX_STUDY_DEPTH, max_number=1e12)
    validate_study(value)
    return value, observation, root


def load_study(path: str | Path) -> dict:
    """Read and validate one study; do not read any declared job or artifact."""
    try:
        snapshots = _StudySnapshots()
        value, _, _ = _read_study(path, snapshots)
        snapshots.verify()
        return value
    except StudyError:
        raise
    except (OSError, ValueError, TypeError, OverflowError, ImportError) as error:
        raise StudyError(f"cannot load study: {error}") from error


def _study_source(snapshots: _StudySnapshots) -> dict:
    source_path = __file__
    _require(type(source_path) is str and Path(source_path).name == "capture_study.py",
             "study source", "an associated capture_study.py source file is required")
    root, name = snapshots.select(source_path)
    _, observation = capture_job._read_observed(
        root, [name], max_bytes=MAX_SOURCE_BYTES, snapshots=snapshots)
    return {"module": "capture_study.py", **observation}


def _preflight_jobs(study: dict, root: Path, snapshots: _StudySnapshots) -> tuple:
    prepared = []
    work = {"window_samples": 0, "spectral_terms": 0}
    for position, entry in enumerate(study["jobs"]):
        label = f"jobs[{position}] {entry['job_id']}"
        parts = entry["path"].split("/")
        # This full study-relative read retains all confined parent observations
        # without selecting another root. Execution later selects its job root.
        payload, observation = capture_job._read_observed(
            root, parts, max_bytes=capture_job.MAX_JOB_BYTES, snapshots=snapshots)
        _require(observation["sha256"] == entry["sha256"], label + " SHA-256",
                 f"mismatch: expected {entry['sha256']}, observed {observation['sha256']}")
        job = capture_common.parse_json_bytes(
            payload, max_bytes=capture_job.MAX_JOB_BYTES,
            max_nodes=capture_job.MAX_JOB_NODES, max_depth=capture_job.MAX_JOB_DEPTH,
            max_number=1e12)
        capture_job.validate_job(job)
        _require(job["job_id"] == entry["job_id"], label, "bound job ID differs from the study entry")
        _require(job["corpus"]["sha256"] == study["corpus_sha256"], label,
                 "bound job declares a different corpus SHA-256")
        analysis = job["analysis"]
        samples = analysis["channel_count"] * analysis["frame_count"]
        work["window_samples"] += samples
        work["spectral_terms"] += samples * len(analysis["frequencies_hz"])
        _require(work["window_samples"] <= MAX_WINDOW_SAMPLES, "study work",
                 f"window sample limit exceeded: {MAX_WINDOW_SAMPLES}")
        _require(work["spectral_terms"] <= MAX_SPECTRAL_TERMS, "study work",
                 f"spectral term limit exceeded: {MAX_SPECTRAL_TERMS}")
        prepared.append((entry, observation, job, root.joinpath(*parts)))
    return prepared, work


def _report_bytes(report: dict) -> bytes:
    capture_common.validate_json_value(report, max_nodes=MAX_REPORT_NODES,
                                       max_depth=MAX_REPORT_DEPTH,
                                       max_number=MAX_REPORT_NUMBER)
    payload = capture_common.canonical_json_bytes(report)
    _require(len(payload) <= MAX_REPORT_BYTES, "study report",
             f"canonical UTF-8 byte limit exceeded: limit {MAX_REPORT_BYTES}, observed {len(payload)}")
    return payload


def _checked_result(entry: dict, observation: dict, original_job: dict,
                    report: dict, corpus_hash: str) -> None:
    _require(type(report) is dict and report.get("job_contract") == "capture-job-v1",
             entry["job_id"], "a complete capture-job-v1 result is required")
    _require(report.get("job_id") == entry["job_id"], entry["job_id"], "returned job ID changed")
    _require(report.get("status") in ("pass", "failed", "inconclusive"),
             entry["job_id"], "invalid returned job status")
    _require(report.get("job") == original_job, entry["job_id"], "returned job differs from preflight")
    _require(report["inputs"]["job"] == observation,
             entry["job_id"], "executed job identity differs from the original preflight read")
    _require(report["inputs"]["corpus"]["observed_sha256"] == corpus_hash
             and report["corpus_report"]["index_sha256"] == corpus_hash,
             entry["job_id"], "observed corpus identity differs from the study")
    sources = report["tool_sources"]
    _require(type(sources) is list and len(sources) == 6
             and all(type(item) is dict and set(item) == {"module", "size_bytes", "sha256"}
                     for item in sources)
             and [item["module"] for item in sources] == sorted(JOB_SOURCES),
             entry["job_id"], "exactly the six ordered job source observations are required")
    _require(report["evaluation"]["evaluation_role"] in ROLES,
             entry["job_id"], "invalid returned evaluation role")


def _make_report(study: dict, observation: dict, work: dict, results: list,
                  runtime: dict, sources: list[dict], corpus_hash: str) -> dict:
    summary = {"jobs": len(results), "pass": 0, "failed": 0, "inconclusive": 0,
               "roles": dict.fromkeys(ROLES, 0)}
    for result in results:
        report = result["report"]
        summary[report["status"]] += 1
        summary["roles"][report["evaluation"]["evaluation_role"]] += 1
    status = ("failed" if summary["failed"] else
              "inconclusive" if summary["inconclusive"] else "pass")
    return {"schema_version": 1, "study_contract": "capture-study-v1",
            "study_id": study["study_id"], "status": status,
            "input": copy.deepcopy(observation), "study": copy.deepcopy(study),
            "corpus": {"expected_sha256": study["corpus_sha256"], "observed_sha256": corpus_hash},
            "work": copy.deepcopy(work), "summary": summary, "jobs": list(results),
            "runtime": copy.deepcopy(runtime), "tool_sources": copy.deepcopy(sources),
            **dict.fromkeys(CLAIM_FIELDS, "not_established")}


def run_study(path: str | Path) -> dict:
    """Execute every declared bound job without fitting, mutation or publication."""
    try:
        snapshots = _StudySnapshots()
        study, observation, root = _read_study(path, snapshots)
        own_source = _study_source(snapshots)
        prepared, work = _preflight_jobs(study, root, snapshots)
        results = []
        runtime = None
        job_sources = None
        sources = None
        corpus_hash = None
        for entry, job_observation, original_job, path_to_job in prepared:
            report = capture_job._run_bound_job(
                path_to_job, expected_job_sha256=entry["sha256"], snapshots=snapshots)
            _checked_result(entry, job_observation, original_job, report, study["corpus_sha256"])
            if runtime is None:
                runtime = copy.deepcopy(report["runtime"])
                job_sources = copy.deepcopy(report["tool_sources"])
                sources = sorted([*job_sources, own_source], key=lambda item: item["module"])
                corpus_hash = report["inputs"]["corpus"]["observed_sha256"]
            else:
                _require(report["runtime"] == runtime, entry["job_id"],
                         "runtime identity changed between study jobs")
                _require(report["tool_sources"] == job_sources, entry["job_id"],
                         "job source observations changed between study jobs")
            result = {"job_id": entry["job_id"], "path": entry["path"],
                      "expected_sha256": entry["sha256"],
                      "observed_sha256": report["inputs"]["job"]["sha256"],
                      "size_bytes": report["inputs"]["job"]["size_bytes"], "report": report}
            results.append(result)
            assembled = _make_report(study, observation, work, results, runtime, sources, corpus_hash)
            _report_bytes(assembled)
        snapshots.verify()
        return assembled
    except StudyError:
        raise
    except (OSError, ValueError, TypeError, OverflowError, ImportError, KeyError, IndexError) as error:
        raise StudyError(f"cannot run study: {error}") from error


def _write_stream(stream, payload: bytes, label: str) -> None:
    binary = getattr(stream, "buffer", None)
    if binary is not None:
        written = binary.write(payload)
        _require(written == len(payload), label, "incomplete output write")
        binary.flush()
    else:
        text = payload.decode("utf-8")
        written = stream.write(text)
        _require(written == len(text), label, "incomplete output write")
        stream.flush()


class _Parser(argparse.ArgumentParser):
    def _print_message(self, message, file=None):
        if message:
            stream = sys.stderr if file is None else file
            _write_stream(stream, message.encode("utf-8"), "stderr" if stream is sys.stderr else "stdout")


class _SinglePath(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is not None:
            parser.error(f"{option_string} may be provided only once")
        if not values:
            parser.error(f"{option_string} requires a nonempty path")
        setattr(namespace, self.dest, Path(values))


def _diagnostic(message: str) -> None:
    cleaned = message.replace("\r", "\\r").replace("\n", "\\n")
    try:
        _write_stream(sys.stderr, ("study error: " + cleaned + "\n").encode("utf-8"), "stderr")
    except (OSError, ValueError, TypeError, OverflowError):
        # There is no reliable secondary diagnostic when the error stream fails.
        pass


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(description=__doc__.split("\n\n")[0], allow_abbrev=False)
    parser.add_argument("--input", required=True, action=_SinglePath, help="fixed capture study JSON")
    parser.add_argument("--output", action=_SinglePath, help="new report file in an existing directory")
    if argv is not None and (type(argv) is not list or any(type(item) is not str for item in argv)):
        _diagnostic("usage: argv must be None or an exact list of exact strings")
        return 2
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return int(error.code)
    except (OSError, ValueError, TypeError, OverflowError) as error:
        _diagnostic(f"standard-stream delivery failed while parsing arguments: {error}")
        return 1
    try:
        report = run_study(args.input)
        payload = _report_bytes(report)
        if args.output is not None:
            capture_common.write_json_new(args.output, report)
        try:
            _write_stream(sys.stdout, payload, "stdout")
        except (OSError, ValueError, TypeError, OverflowError) as error:
            raise StudyError(f"stdout delivery failed: {error}") from error
        return {"pass": 0, "failed": 1, "inconclusive": 3}[report["status"]]
    except (StudyError, OSError, ValueError, TypeError, OverflowError, ImportError) as error:
        _diagnostic(str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(capture_common._cli_exit(main, lambda message: _diagnostic(
        f"standard-stream delivery failed: {message}")))
