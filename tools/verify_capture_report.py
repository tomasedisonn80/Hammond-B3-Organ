#!/usr/bin/env python3
"""Replay a complete canonical capture job or study report against its archive.

Matching a failed or inconclusive engineering result preserves that outcome.
Reproduction does not establish historical authenticity or physical fidelity.
Keep the archive, saved report and coherent sources quiescent during execution.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
from pathlib import Path
import sys

import capture_common
import capture_corpus
import capture_job
import capture_study


MAX_REPORT_BYTES = 16777216
MAX_REPORT_NODES = 1048576
MAX_REPORT_NUMBER = 4e18
REPORT_DEPTHS = {"job": 32, "study": 40}
MAX_INPUT_BYTES = 65536
MAX_SOURCE_BYTES = 1048576
MAX_REPLAY_SNAPSHOTS = 12
MAX_SUMMARY_BYTES = 65536
MAX_SUMMARY_NODES = 8192
MAX_SUMMARY_DEPTH = 12
ENGINEERING_STATUSES = {"pass", "failed", "inconclusive"}
ROLES = ("fit", "validation", "final_test", "unassigned")
CLAIM_FIELDS = ("boundary_equivalence", "synchronization", "authenticity",
                "specimen_identity", "calibration", "permissions", "independence",
                "preregistration", "final_holdout_history", "physical_fidelity")
JOB_SOURCES = ("capture_audio.py", "capture_common.py", "capture_corpus.py",
               "capture_job.py", "compare_capture.py", "validate_capture.py")
STUDY_SOURCES = tuple(sorted((*JOB_SOURCES, "capture_study.py")))
RUNTIME_KEYS = {"python_implementation", "python_version", "sys_platform", "machine"}
JOB_REPORT_KEYS = {"schema_version", "job_contract", "job_id", "status", "inputs",
                   "job", "policy", "reference", "candidate", "self_comparison",
                   "corpus_report", "evaluation", "runtime", "tool_sources", *CLAIM_FIELDS}
STUDY_REPORT_KEYS = {"schema_version", "study_contract", "study_id", "status", "input",
                     "study", "corpus", "work", "summary", "jobs", "runtime",
                     "tool_sources", *CLAIM_FIELDS}


class ReplayError(ValueError):
    """Rejected replay input, execution, identity, resource or publication."""


def _require(condition: bool, label: str, message: str) -> None:
    if not condition:
        raise ReplayError(f"{label}: {message}")


def _keys(value: object, fields: set[str], label: str) -> None:
    _require(type(value) is dict and set(value) == fields, label,
             "expected exactly these keys: " + ", ".join(sorted(fields)))


def _integer(value: object, low: int, high: int, label: str) -> None:
    _require(type(value) is int and low <= value <= high, label,
             f"expected an exact integer in {low}..{high}")


def _enum(value: object, choices, label: str) -> None:
    _require(type(value) is str and value in choices, label,
             "unexpected value")


def _path_argument(value: object, label: str) -> None:
    _require((type(value) is str and bool(value)) or isinstance(value, Path),
             label, "expected an exact nonempty string or pathlib.Path")


def _same_value(left: object, right: object) -> bool:
    # Python equality alone conflates Boolean/integer and integer/float values.
    return (capture_common.canonical_json_bytes(left)
            == capture_common.canonical_json_bytes(right))


def _guard_report(kind: str, value: object) -> None:
    capture_common.validate_json_value(value, max_nodes=MAX_REPORT_NODES,
                                       max_depth=REPORT_DEPTHS[kind],
                                       max_number=MAX_REPORT_NUMBER)
    pending = [value]
    while pending:
        item = pending.pop()
        if type(item) is dict:
            for key in item:
                _require(not any(ord(char) < 32 or 127 <= ord(char) <= 159 for char in key),
                         "report JSON key", "control characters are forbidden")
            pending.extend(item.values())
        elif type(item) is list:
            pending.extend(item)
        elif type(item) is str:
            _require(not any(ord(char) < 32 or 127 <= ord(char) <= 159 for char in item),
                     "report JSON string", "control characters are forbidden")


def _observation(value: object, maximum: int, label: str) -> None:
    _keys(value, {"sha256", "size_bytes"}, label)
    capture_corpus._sha(value["sha256"], label + ".sha256")
    _integer(value["size_bytes"], 1, maximum, label + ".size_bytes")


def _runtime(value: object, label: str) -> None:
    _keys(value, RUNTIME_KEYS, label)
    for key, item in value.items():
        capture_job._text(item, label + "." + key, limit=128, allow_empty=key == "machine")


def _sources(value: object, kind: str, label: str) -> None:
    names = JOB_SOURCES if kind == "job" else STUDY_SOURCES
    _require(type(value) is list and len(value) == len(names), label,
             "expected the complete ordered source inventory")
    for row, name in zip(value, names):
        _keys(row, {"module", "size_bytes", "sha256"}, label)
        _require(type(row["module"]) is str and row["module"] == name,
                 label + ".module", "unexpected or unordered source module")
        _integer(row["size_bytes"], 1, MAX_SOURCE_BYTES, label + ".size_bytes")
        capture_corpus._sha(row["sha256"], label + ".sha256")


def _claims_and_runtime(report: dict, kind: str, label: str) -> None:
    _integer(report["schema_version"], 1, 1, label + ".schema_version")
    _enum(report["status"], ENGINEERING_STATUSES, label + ".status")
    for name in CLAIM_FIELDS:
        _require(report[name] == "not_established", label + "." + name,
                 "expected not_established")
    _runtime(report["runtime"], label + ".runtime")
    _sources(report["tool_sources"], kind, label + ".tool_sources")


def _binding(value: object, declared: dict, maximum: int, label: str) -> None:
    _keys(value, {"path", "size_bytes", "expected_sha256", "observed_sha256"}, label)
    _require(value["path"] == declared["path"], label + ".path",
             "differs from the embedded input")
    _integer(value["size_bytes"], 1, maximum, label + ".size_bytes")
    for field in ("expected_sha256", "observed_sha256"):
        capture_corpus._sha(value[field], label + "." + field)
        _require(value[field] == declared["sha256"], label + "." + field,
                 "differs from the embedded input binding")


def _job_envelope(report: object, label: str) -> None:
    _guard_report("job", report)
    _keys(report, JOB_REPORT_KEYS, label)
    _claims_and_runtime(report, "job", label)
    _require(report["job_contract"] == "capture-job-v1", label + ".job_contract",
             "expected capture-job-v1")
    capture_corpus._id(report["job_id"], label + ".job_id")
    capture_job.validate_job(report["job"])
    job = report["job"]
    _require(report["job_id"] == job["job_id"], label + ".job_id",
             "differs from the embedded job")
    for field in ("policy", "reference", "candidate", "corpus_report", "evaluation"):
        _require(type(report[field]) is dict, label + "." + field, "expected an object")
    _require(type(report["self_comparison"]) is bool
             and report["self_comparison"] == (job["reference"] == job["candidate"]),
             label + ".self_comparison", "must agree with the embedded selectors")
    inputs = report["inputs"]
    _keys(inputs, {"job", "corpus", "policy"}, label + ".inputs")
    _observation(inputs["job"], MAX_INPUT_BYTES, label + ".inputs.job")
    _binding(inputs["corpus"], job["corpus"], 1048576, label + ".inputs.corpus")
    _binding(inputs["policy"], job["policy"], 65536, label + ".inputs.policy")
    corpus = report["corpus_report"]
    _require(corpus.get("mode") == "files_and_audio_checked", label + ".corpus_report.mode",
             "expected files_and_audio_checked")
    _require(corpus.get("index_sha256") == inputs["corpus"]["observed_sha256"],
             label + ".corpus_report.index_sha256", "differs from the observed binding")
    _enum(corpus.get("status"), ENGINEERING_STATUSES, label + ".corpus_report.status")
    evaluation = report["evaluation"]
    _require(evaluation.get("policy_sha256") == inputs["policy"]["observed_sha256"],
             label + ".evaluation.policy_sha256", "differs from the observed binding")
    _enum(evaluation.get("evaluation_role"), ROLES, label + ".evaluation.evaluation_role")
    _enum(evaluation.get("numerical_verdict"), {"pass", "fail", "inconclusive"},
          label + ".evaluation.numerical_verdict")
    corpus_status, numerical = corpus["status"], evaluation["numerical_verdict"]
    status = ("failed" if corpus_status == "failed" or numerical == "fail" else
              "inconclusive" if "inconclusive" in (corpus_status, numerical) else "pass")
    _require(report["status"] == status, label + ".status",
             "differs from the declared subordinate outcome precedence")


def _study_envelope(report: object, label: str) -> None:
    _guard_report("study", report)
    _keys(report, STUDY_REPORT_KEYS, label)
    _claims_and_runtime(report, "study", label)
    _require(report["study_contract"] == "capture-study-v1", label + ".study_contract",
             "expected capture-study-v1")
    capture_corpus._id(report["study_id"], label + ".study_id")
    capture_study.validate_study(report["study"])
    study = report["study"]
    _require(report["study_id"] == study["study_id"], label + ".study_id",
             "differs from the embedded study")
    _observation(report["input"], MAX_INPUT_BYTES, label + ".input")
    _keys(report["corpus"], {"expected_sha256", "observed_sha256"}, label + ".corpus")
    _require(all(value == study["corpus_sha256"] for value in report["corpus"].values()),
             label + ".corpus", "differs from the embedded study corpus binding")
    _keys(report["work"], {"window_samples", "spectral_terms"}, label + ".work")
    _integer(report["work"]["window_samples"], 1, capture_study.MAX_WINDOW_SAMPLES,
             label + ".work.window_samples")
    _integer(report["work"]["spectral_terms"], 0, capture_study.MAX_SPECTRAL_TERMS,
             label + ".work.spectral_terms")
    jobs = report["jobs"]
    _require(type(jobs) is list and len(jobs) == len(study["jobs"]), label + ".jobs",
             "expected every ordered declared job")
    work = {"window_samples": 0, "spectral_terms": 0}
    summary = {"jobs": len(jobs), "pass": 0, "failed": 0, "inconclusive": 0,
               "roles": dict.fromkeys(ROLES, 0)}
    ordinary_sources = [row for row in report["tool_sources"]
                        if row["module"] != "capture_study.py"]
    for position, (entry, declared) in enumerate(zip(jobs, study["jobs"])):
        where = label + f".jobs[{position}]"
        _keys(entry, {"job_id", "path", "expected_sha256", "observed_sha256",
                      "size_bytes", "report"}, where)
        for key in ("job_id", "path"):
            _require(entry[key] == declared[key], where + "." + key,
                     "differs from the ordered study entry")
        _require(entry["expected_sha256"] == declared["sha256"], where + ".expected_sha256",
                 "differs from the ordered study entry")
        _job_envelope(entry["report"], where + ".report")
        nested = entry["report"]
        _require(nested["job_id"] == declared["job_id"], where + ".report.job_id",
                 "differs from the ordered study entry")
        _integer(entry["size_bytes"], 1, MAX_INPUT_BYTES, where + ".size_bytes")
        _require(entry["observed_sha256"] == declared["sha256"]
                 and entry["observed_sha256"] == nested["inputs"]["job"]["sha256"]
                 and entry["size_bytes"] == nested["inputs"]["job"]["size_bytes"], where,
                 "observed job identity differs from declared or nested identity")
        _require(nested["inputs"]["corpus"]["observed_sha256"] == study["corpus_sha256"],
                 where + ".report.inputs.corpus", "differs from the common corpus binding")
        _require(nested["runtime"] == report["runtime"]
                 and nested["tool_sources"] == ordinary_sources, where,
                 "nested runtime or source observations disagree with the study")
        analysis = nested["job"]["analysis"]
        samples = analysis["channel_count"] * analysis["frame_count"]
        work["window_samples"] += samples
        work["spectral_terms"] += samples * len(analysis["frequencies_hz"])
        summary[nested["status"]] += 1
        summary["roles"][nested["evaluation"]["evaluation_role"]] += 1
    _require(report["work"] == work, label + ".work", "differs from the actual nested work sums")
    _keys(report["summary"], set(summary), label + ".summary")
    _keys(report["summary"]["roles"], set(ROLES), label + ".summary.roles")
    for key in ("jobs", "pass", "failed", "inconclusive"):
        _integer(report["summary"][key], 0, capture_study.MAX_JOBS, label + ".summary." + key)
    for key in ROLES:
        _integer(report["summary"]["roles"][key], 0, capture_study.MAX_JOBS,
                 label + ".summary.roles." + key)
    _require(report["summary"] == summary, label + ".summary",
             "differs from the complete ordered nested outcomes")
    status = ("failed" if summary["failed"] else
              "inconclusive" if summary["inconclusive"] else "pass")
    _require(report["status"] == status, label + ".status",
             "differs from the declared nested outcome precedence")


def _admit_report(kind: str, report: object) -> bytes:
    if kind == "job":
        _job_envelope(report, "job report")
    else:
        _study_envelope(report, "study report")
    payload = capture_common.canonical_json_bytes(report)
    _require(len(payload) <= MAX_REPORT_BYTES, "report",
             f"canonical UTF-8 byte limit exceeded: {MAX_REPORT_BYTES}")
    return payload


class _ReplaySnapshots(capture_job._Snapshots):
    """Bound wrapper observations separately from the ordinary runner's set."""

    def select(self, path: str | Path) -> tuple[Path, str]:
        _require(len(self.roots) < MAX_REPLAY_SNAPSHOTS, "replay snapshots",
                 "selected-root limit exceeded")
        return super().select(path)

    def admit(self, root: Path, parts: list[str]) -> tuple:
        _require(len(self.leaves) < MAX_REPLAY_SNAPSHOTS, "replay snapshots",
                 "leaf limit exceeded")
        return super().admit(root, parts)


def _read_report(kind: str, path: str | Path, snapshots: _ReplaySnapshots) -> tuple:
    root, name = snapshots.select(path)
    payload, observation = capture_job._read_observed(
        root, [name], max_bytes=MAX_REPORT_BYTES, snapshots=snapshots)
    value = capture_common.parse_json_bytes(
        payload, max_bytes=MAX_REPORT_BYTES, max_nodes=MAX_REPORT_NODES,
        max_depth=REPORT_DEPTHS[kind], max_number=MAX_REPORT_NUMBER)
    canonical = _admit_report(kind, value)
    _require(payload == canonical, "saved report", "original bytes must be exact canonical JSON")
    return value, observation, payload


def _source_inventory(kind: str, snapshots: _ReplaySnapshots) -> tuple:
    sources = capture_job._source_observations(snapshots)
    if kind == "study":
        sources.append(capture_study._study_source(snapshots))
        sources.sort(key=lambda row: row["module"])
    _sources(sources, kind, "observed tool sources")
    path = __file__
    _require(type(path) is str and Path(path).name == "verify_capture_report.py",
             "verifier source", "an associated verify_capture_report.py source file is required")
    root, name = snapshots.select(path)
    _, observation = capture_job._read_observed(
        root, [name], max_bytes=MAX_SOURCE_BYTES, snapshots=snapshots)
    _observation(observation, MAX_SOURCE_BYTES, "verifier source")
    return sources, {"module": "verify_capture_report.py", **observation}


def _input_observation(kind: str, report: dict) -> dict:
    return report["inputs"]["job"] if kind == "job" else report["input"]


def _summary_bytes(summary: dict) -> bytes:
    capture_common.validate_json_value(summary, max_nodes=MAX_SUMMARY_NODES,
                                       max_depth=MAX_SUMMARY_DEPTH,
                                       max_number=MAX_REPORT_NUMBER)
    payload = capture_common.canonical_json_bytes(summary)
    _require(len(payload) <= MAX_SUMMARY_BYTES, "verification summary",
             f"canonical UTF-8 byte limit exceeded: {MAX_SUMMARY_BYTES}")
    return payload


def verify_report(kind: str, input_path: str | Path, report_path: str | Path) -> dict:
    """Re-execute one original input and compare every canonical report byte."""
    try:
        _enum(kind, ("job", "study"), "kind")
        _path_argument(input_path, "input")
        _path_argument(report_path, "report")
        snapshots = _ReplaySnapshots()
        saved, saved_observation, saved_payload = _read_report(kind, report_path, snapshots)
        sources, own_source = _source_inventory(kind, snapshots)
        runtime = capture_job._runtime()
        if kind == "job":
            original, input_observation, _ = capture_job._read_job(input_path, snapshots)
        else:
            original, input_observation, _ = capture_study._read_study(input_path, snapshots)
        _require(input_observation == _input_observation(kind, saved), "original input identity",
                 "actual consumed bytes differ from the saved report binding")
        _require(_same_value(original, saved[kind]), "original input value",
                 "actual parsed input differs from the saved embedded input")
        # The public runner independently rereads and bounds the original archive.
        # This is not an atomic preflight: a race may do bounded work then reject.
        fresh = (capture_job.run_job(input_path) if kind == "job"
                 else capture_study.run_study(input_path))
        fresh_payload = _admit_report(kind, fresh)
        _require(_input_observation(kind, fresh) == input_observation
                 and _same_value(fresh[kind], original), "replayed input identity",
                 "runner consumed an input differing from replay preflight")
        _require(fresh["tool_sources"] == sources, "replayed tool sources",
                 "runner observations differ from replay preflight")
        _require(fresh["runtime"] == runtime, "replayed runtime",
                 "runner observations differ from replay preflight")
        matches = saved_payload == fresh_payload
        summary = {
            "schema_version": 1, "replay_contract": "capture-report-replay-v1", "kind": kind,
            "status": "match" if matches else "mismatch",
            "verification_scope": "complete_canonical_report_bytes", "exact_report_match": matches,
            "input": copy.deepcopy(input_observation),
            "saved_report": copy.deepcopy(saved_observation),
            "replayed_report": {"sha256": hashlib.sha256(fresh_payload).hexdigest(),
                                  "size_bytes": len(fresh_payload)},
            "saved_engineering_status": saved["status"],
            "replayed_engineering_status": fresh["status"],
            "context": {
                "same_runtime": saved["runtime"] == fresh["runtime"],
                "same_tool_sources": saved["tool_sources"] == fresh["tool_sources"],
                "saved_runtime": copy.deepcopy(saved["runtime"]),
                "replayed_runtime": copy.deepcopy(fresh["runtime"]),
                "saved_tool_sources": copy.deepcopy(saved["tool_sources"]),
                "replayed_tool_sources": copy.deepcopy(fresh["tool_sources"]),
            },
            "verifier_source": own_source, "verifier_runtime": copy.deepcopy(runtime),
            **dict.fromkeys(CLAIM_FIELDS, "not_established"),
        }
        _summary_bytes(summary)
        snapshots.verify()
        _require(capture_job._runtime() == runtime, "verifier runtime",
                 "runtime identity changed during replay")
        return summary
    except ReplayError:
        raise
    except (OSError, ValueError, TypeError, OverflowError, ImportError, KeyError, IndexError) as error:
        raise ReplayError(f"cannot verify report: {error}") from error


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


class _SingleValue(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is not None:
            parser.error(f"{option_string} may be provided only once")
        if not values:
            parser.error(f"{option_string} requires a nonempty value")
        setattr(namespace, self.dest, values if self.dest == "kind" else Path(values))


def _diagnostic(message: str) -> None:
    cleaned = message.replace("\r", "\\r").replace("\n", "\\n")
    try:
        _write_stream(sys.stderr, ("replay error: " + cleaned + "\n").encode("utf-8"), "stderr")
    except (OSError, ValueError, TypeError, OverflowError):
        pass


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(description=__doc__.split("\n\n")[0], allow_abbrev=False)
    parser.add_argument("--kind", required=True, choices=("job", "study"), action=_SingleValue,
                        help="complete report kind")
    parser.add_argument("--input", required=True, action=_SingleValue, help="original job or study JSON")
    parser.add_argument("--report", required=True, action=_SingleValue, help="saved complete canonical report")
    parser.add_argument("--output", action=_SingleValue, help="new verification summary in an existing directory")
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
        summary = verify_report(args.kind, args.input, args.report)
        payload = _summary_bytes(summary)
        if args.output is not None:
            capture_common.write_json_new(args.output, summary)
        try:
            _write_stream(sys.stdout, payload, "stdout")
        except (OSError, ValueError, TypeError, OverflowError) as error:
            raise ReplayError(f"stdout delivery failed: {error}") from error
        return 0 if summary["exact_report_match"] else 1
    except (ReplayError, OSError, ValueError, TypeError, OverflowError, ImportError) as error:
        _diagnostic(str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
