#!/usr/bin/env python3
"""Run one identity-bound, untransformed digital capture comparison offline.

Every declared corpus artifact participates in the audit. Numerical outcomes
never establish physical provenance, calibration, independence or fidelity.
Inputs and the six observed project sources must remain quiescent throughout.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
from pathlib import Path
import platform
import sys

import capture_audio
import capture_common
import capture_corpus
import compare_capture
import validate_capture


MAX_JOB_BYTES = 65536
MAX_JOB_NODES = 4096
MAX_JOB_DEPTH = 8
MAX_CAPTURES = 64
MAX_ARTIFACT_REFERENCES = 256
MAX_EDGES = 4096
MAX_SOURCE_BYTES = 1048576
MAX_REPORT_BYTES = 16777216
MAX_REPORT_NODES = 1048576
MAX_REPORT_DEPTH = 32
MAX_REPORT_NUMBER = 4e18
MAX_WINDOW_SAMPLES = 1048576
MAX_WINDOW_SECONDS = 600
MAX_STREAM_FRAMES = 134217728
ANALYSIS_KEYS = {"sample_rate_hz", "channel_count", "frame_count", "window",
                 "floor_fs", "frequencies_hz"}
JOB_KEYS = {"schema_version", "contract_origin", "job_id", "corpus", "reference",
            "candidate", "analysis", "policy", "pairing", "transform"}
PURPOSE_ROLES = {"fit": "fit", "validation": "validation", "final": "final_test",
                 "unassigned": "unassigned"}
CLAIM_FIELDS = ("boundary_equivalence", "synchronization", "authenticity",
                "specimen_identity", "calibration", "permissions", "independence",
                "preregistration", "final_holdout_history", "physical_fidelity")


class JobError(ValueError):
    """Rejected job input, dependency, identity, resource or publication."""


def _require(condition: bool, label: str, message: str) -> None:
    if not condition:
        raise JobError(f"{label}: {message}")


def _keys(value: object, fields: set[str], label: str) -> None:
    _require(type(value) is dict and set(value) == fields, label,
             "expected exactly these keys: " + ", ".join(sorted(fields)))


def _text(value: object, label: str, *, limit: int = 2048,
          allow_empty: bool = False) -> None:
    _require(type(value) is str and len(value) <= limit
             and (bool(value.strip()) or allow_empty and value == ""), label,
             f"expected {'possibly empty' if allow_empty else 'nonblank'} text of at most {limit} characters")
    _require(not any(ord(char) < 32 or 127 <= ord(char) <= 159 for char in value),
             label, "control characters are forbidden")
    try:
        value.encode("utf-8")
    except UnicodeError as error:
        raise JobError(f"{label}: unpaired Unicode surrogate") from error


def _guard_job(value: object) -> None:
    capture_common.validate_json_value(value, max_nodes=MAX_JOB_NODES,
                                       max_depth=MAX_JOB_DEPTH, max_number=1e12)
    pending = [value]
    while pending:
        item = pending.pop()
        if type(item) in (dict, list):
            _require(len(item) <= MAX_JOB_NODES, "job JSON", "container member limit exceeded")
            if type(item) is dict:
                for key in item:
                    _text(key, "JSON key")
                pending.extend(item.values())
            else:
                pending.extend(item)
        elif type(item) is str:
            _text(item, "JSON string")


def validate_job(value: object) -> None:
    """Validate the exact job value and intrinsic work bounds without any I/O."""
    try:
        _guard_job(value)
        _keys(value, JOB_KEYS, "job")
        _require(type(value["schema_version"]) is int and value["schema_version"] == 1,
                 "schema_version", "expected integer 1")
        _require(value["contract_origin"] == "project-proposed-capture-job-v1",
                 "contract_origin", "expected project-proposed-capture-job-v1")
        capture_corpus._id(value["job_id"], "job_id")
        _require(value["pairing"] == "index", "pairing", "expected index")
        _require(value["transform"] == "none", "transform", "expected none")
        for name in ("corpus", "policy"):
            binding = value[name]
            _keys(binding, {"path", "sha256"}, name)
            capture_corpus._path(binding["path"], name + ".path")
            capture_corpus._sha(binding["sha256"], name + ".sha256")
        for name in ("reference", "candidate"):
            selection = value[name]
            _keys(selection, {"capture_id", "file_id", "start_frame"}, name)
            capture_corpus._id(selection["capture_id"], name + ".capture_id")
            capture_corpus._id(selection["file_id"], name + ".file_id")
            capture_corpus._integer(selection["start_frame"], 0, MAX_STREAM_FRAMES - 1,
                                    name + ".start_frame")
        analysis = value["analysis"]
        _keys(analysis, ANALYSIS_KEYS, "analysis")
        compare_capture._analysis_parameters(
            analysis["sample_rate_hz"], analysis["channel_count"],
            analysis["frame_count"], analysis["frequencies_hz"],
            analysis["window"], analysis["floor_fs"], sequence_types=(list,))
        count = analysis["frame_count"]
        _require(analysis["channel_count"] * count <= MAX_WINDOW_SAMPLES,
                 "analysis", f"channel/frame window work exceeds {MAX_WINDOW_SAMPLES}")
        _require(count <= analysis["sample_rate_hz"] * MAX_WINDOW_SECONDS,
                 "analysis", f"window exceeds {MAX_WINDOW_SECONDS} seconds")
        for name in ("reference", "candidate"):
            _require(value[name]["start_frame"] + count <= MAX_STREAM_FRAMES,
                     name, "start plus frame count exceeds the stream frame bound")
    except JobError:
        raise
    except (ValueError, TypeError, OverflowError) as error:
        raise JobError(f"job admission: {error}") from error


class _Snapshots:
    """Retain first pathname observations; constituent reads also bind their FDs."""

    def __init__(self) -> None:
        self.leaves = []
        self.roots = []

    def select(self, path: str | Path) -> tuple[Path, str]:
        root, name, chosen_root, before_root = capture_corpus._select_index(path)
        self.roots.append((root, chosen_root, before_root))
        return root, name

    def admit(self, root: Path, parts: list[str]) -> tuple:
        snapshot = capture_corpus._confined_snapshot(root, parts)
        self.leaves.append(snapshot)
        return snapshot

    def verify(self) -> None:
        for snapshot in self.leaves:
            capture_corpus._finish_read(*snapshot)
        for root in self.roots:
            capture_corpus._root_unchanged(*root)


def _read_observed(root: Path, parts: list[str], *, max_bytes: int,
                   snapshots: _Snapshots) -> tuple[bytes, dict]:
    snapshot = snapshots.admit(root, parts)
    payload = capture_corpus._read_confined_bytes(root, parts, max_bytes=max_bytes)
    capture_corpus._finish_read(*snapshot)
    return payload, {"size_bytes": len(payload),
                     "sha256": hashlib.sha256(payload).hexdigest()}


def _read_job(path: str | Path, snapshots: _Snapshots) -> tuple:
    root, name = snapshots.select(path)
    payload, observation = _read_observed(root, [name], max_bytes=MAX_JOB_BYTES,
                                          snapshots=snapshots)
    value = capture_common.parse_json_bytes(payload, max_bytes=MAX_JOB_BYTES,
                                            max_nodes=MAX_JOB_NODES,
                                            max_depth=MAX_JOB_DEPTH, max_number=1e12)
    validate_job(value)
    return value, observation, root


def load_job(path: str | Path) -> dict:
    """Read one bounded strict job and return its unmodified parsed value."""
    try:
        snapshots = _Snapshots()
        value, _, _ = _read_job(path, snapshots)
        snapshots.verify()
        return value
    except JobError:
        raise
    except (OSError, ValueError, TypeError, OverflowError, ImportError) as error:
        raise JobError(f"cannot load job: {error}") from error


def _bound_input(binding: dict, root: Path, *, max_bytes: int,
                  snapshots: _Snapshots, label: str) -> tuple[bytes, dict]:
    payload, observation = _read_observed(root, binding["path"].split("/"),
                                          max_bytes=max_bytes, snapshots=snapshots)
    _require(observation["sha256"] == binding["sha256"], label + " SHA-256",
             f"mismatch: expected {binding['sha256']}, observed {observation['sha256']}")
    return payload, {"path": binding["path"], "size_bytes": observation["size_bytes"],
                     "expected_sha256": binding["sha256"],
                     "observed_sha256": observation["sha256"]}


def _source_observations(snapshots: _Snapshots) -> list[dict]:
    modules = {"capture_audio.py": capture_audio,
               "capture_common.py": capture_common,
               "capture_corpus.py": capture_corpus,
               "compare_capture.py": compare_capture,
               "validate_capture.py": validate_capture}
    paths = {name: getattr(module, "__file__", None) for name, module in modules.items()}
    paths["capture_job.py"] = __file__
    observations = []
    for name in sorted(paths):
        source_path = paths[name]
        _require(isinstance(source_path, str) and Path(source_path).name == name,
                 f"source {name}", "an associated Python source file is required")
        root, leaf = snapshots.select(source_path)
        _, observation = _read_observed(root, [leaf], max_bytes=MAX_SOURCE_BYTES,
                                        snapshots=snapshots)
        observations.append({"module": name, **observation})
    return observations


def _runtime() -> dict:
    result = {"python_implementation": sys.implementation.name,
              "python_version": platform.python_version(),
              "sys_platform": sys.platform, "machine": platform.machine()}
    for name, value in result.items():
        _text(value, "runtime." + name, limit=128, allow_empty=name == "machine")
    return result


def _preflight_selections(job: dict, policy: dict, loaded: list[tuple],
                          captures: list[dict]) -> dict:
    _require(job["analysis"] == policy["analysis"], "policy.analysis",
             "all six fields must match the job analysis")
    metadata = {entry["capture_id"]: (entry, capture, digest)
                for entry, capture, digest in loaded}
    inventories = {capture["capture_id"]: capture for capture in captures}
    selections = {}
    for side in ("reference", "candidate"):
        selector = job[side]
        ident, file_id = selector["capture_id"], selector["file_id"]
        _require(ident in metadata, side, f"unresolved capture ID {ident!r}")
        entry, capture, digest = metadata[ident]
        _require(capture["status"] == "recorded", side, "selected capture must be recorded")
        files = {item["file_id"]: item for item in capture["files"]}
        _require(file_id in files, side, f"unresolved file ID {file_id!r}")
        artifact = files[file_id]
        _require(artifact["kind"] in ("raw", "derived"), side,
                 "selected file must be raw or derived, never support")
        item = next(item for item in inventories[ident]["files"] if item["file_id"] == file_id)
        expected = item["expected_audio"]
        _require(expected is not None, side, "selected derivative requires its own derived_audio descriptor")
        _require(expected["format"] in capture_corpus.AUDIO_FORMATS, side,
                 f"unsupported requested audio format {expected['format']!r}")
        for name in ("sample_rate_hz", "channel_count"):
            _require(expected[name] == job["analysis"][name], side + "." + name,
                     "selected file descriptor must match the job analysis")
        selections[side] = (entry, capture, digest, artifact, expected)
    purpose = selections["reference"][0]["purpose"]
    _require(selections["candidate"][0]["purpose"] == purpose, "selected purposes",
             "reference and candidate purposes must agree")
    _require(policy["evaluation_role"] == PURPOSE_ROLES[purpose], "policy.evaluation_role",
             f"purpose {purpose!r} requires {PURPOSE_ROLES[purpose]!r}")
    if policy["evidence_class"] == "synthetic_numerical_fixture":
        _require(all(selection[1]["capture_kind"] == "synthetic"
                     for selection in selections.values()), "policy.evidence_class",
                 "a synthetic numerical policy requires both selected captures to be synthetic")
    return selections


def _selection_window(side: str, job: dict, selected: tuple, corpus_report: dict,
                       root: Path) -> tuple[dict, list]:
    entry, capture, manifest_hash, artifact, expected = selected
    selector, count = job[side], job["analysis"]["frame_count"]
    start = selector["start_frame"]
    observed_capture = next(item for item in corpus_report["captures"]
                            if item["capture_id"] == entry["capture_id"])
    item = next(item for item in observed_capture["files"]
                if item["file_id"] == artifact["file_id"])
    _require(item["audio_status"] == "verified" and type(item["observed_audio"]) is dict,
             side, "complete corpus audit did not verify the selected audio")
    audio = item["observed_audio"]
    for name in ("format", "sample_rate_hz", "channel_count"):
        _require(audio[name] == expected[name], side + "." + name,
                 "actual audio differs from the selected descriptor")
    _require(start + count <= audio["frame_count"], side + ".window",
             "declared interval exceeds the inspected stream")
    parts = entry["manifest_path"].split("/")[:-1] + artifact["path"].split("/")
    snapshot = capture_corpus._confined_snapshot(root, parts)
    target = snapshot[0]
    window = capture_audio.read_audio_window(
        target, start, count,
        raw_format="raw_float32_le" if expected["format"] == "raw_float32_le" else None,
        sample_rate_hz=expected["sample_rate_hz"], channel_count=expected["channel_count"])
    capture_corpus._finish_read(*snapshot)
    inspection = window["inspection"]
    identities = {"size_bytes": item["observed_size_bytes"],
                  "sha256": item["observed_sha256"], **audio}
    for name, observed in identities.items():
        _require(inspection[name] == observed, side + ".inspection." + name,
                 "window inspection differs from the complete corpus observation")
    for name, value in (("start_frame", start), ("frame_count", count), ("end_frame", start + count)):
        _require(window[name] == value, side + ".window." + name,
                 "audio reader returned a different interval")
    samples = window["samples"]
    _require(type(samples) is list and len(samples) == job["analysis"]["channel_count"]
             and all(type(channel) is list and len(channel) == count for channel in samples),
             side + ".samples", "audio reader returned a different channel/window geometry")
    record = {
        "capture_id": entry["capture_id"], "file_id": artifact["file_id"],
        "purpose": entry["purpose"], "capture_kind": capture["capture_kind"],
        "file_kind": artifact["kind"], "manifest_path": entry["manifest_path"],
        "manifest_sha256": manifest_hash, "artifact_path": artifact["path"],
        "capture_manifest": copy.deepcopy(capture),
        "context_scope": "selected_raw_stream" if artifact["kind"] == "raw" else "ancestor_raw_stream_only",
        "window": {"start_frame": start, "frame_count": count, "end_frame": start + count},
        "inspection": copy.deepcopy({name: value for name, value in inspection.items() if name != "input_path"}),
    }
    return record, samples


def _report_bytes(report: dict) -> bytes:
    capture_common.validate_json_value(report, max_nodes=MAX_REPORT_NODES,
                                       max_depth=MAX_REPORT_DEPTH,
                                       max_number=MAX_REPORT_NUMBER)
    payload = capture_common.canonical_json_bytes(report)
    _require(len(payload) <= MAX_REPORT_BYTES, "report",
             f"canonical UTF-8 byte limit exceeded: limit {MAX_REPORT_BYTES}, observed {len(payload)}")
    return payload


def run_job(path: str | Path) -> dict:
    """Audit every corpus artifact and evaluate two declared original windows.

    No file is written. Valid failed and inconclusive results are complete
    reports; malformed inputs or observed changes raise JobError instead.
    """
    return _run_bound_job(path)


def _run_bound_job(path: str | Path, *, expected_job_sha256: str | None = None,
                   snapshots: _Snapshots | None = None) -> dict:
    """Share the unchanged job execution with a hash-bound study operation.

    A study supplies its original expected job digest and one snapshot set that
    outlives every constituent job. The consumed job must match before any
    corpus or policy read. Ordinary public calls still own their snapshot set.
    """
    try:
        if snapshots is None:
            snapshots = _Snapshots()
        sources = _source_observations(snapshots)
        job, job_observation, root = _read_job(path, snapshots)
        if expected_job_sha256 is not None:
            capture_corpus._sha(expected_job_sha256, "expected job SHA-256")
            _require(job_observation["sha256"] == expected_job_sha256,
                     "job SHA-256",
                     f"mismatch: expected {expected_job_sha256}, observed {job_observation['sha256']}")
        index_bytes, index_observation = _bound_input(
            job["corpus"], root, max_bytes=capture_corpus.MAX_INDEX_BYTES,
            snapshots=snapshots, label="corpus")
        policy_bytes, policy_observation = _bound_input(
            job["policy"], root, max_bytes=compare_capture.MAX_POLICY_BYTES,
            snapshots=snapshots, label="policy")
        index = capture_common.parse_json_bytes(
            index_bytes, max_bytes=capture_corpus.MAX_INDEX_BYTES,
            max_nodes=capture_corpus.MAX_INDEX_NODES, max_depth=capture_corpus.MAX_DEPTH,
            max_number=1e12)
        capture_corpus.validate_corpus(index)
        policy = compare_capture.parse_policy(policy_bytes)
        _require(len(index["captures"]) <= MAX_CAPTURES, "corpus",
                 f"job capture limit exceeded: limit {MAX_CAPTURES}, observed {len(index['captures'])}")
        corpus_root = root.joinpath(*job["corpus"]["path"].split("/")).parent
        before_corpus_root = capture_corpus._snapshot(corpus_root, directory=True)
        # First-admission observations outlive each constituent read. Reuse the
        # exact parsed and SHA-bound manifests; do not call a public reread path.
        for entry in index["captures"]:
            snapshots.admit(corpus_root, entry["manifest_path"].split("/"))
        loaded = capture_corpus._load_manifests(index, corpus_root)
        reference_count = sum(len(capture["files"]) for _, capture, _ in loaded)
        _require(reference_count <= MAX_ARTIFACT_REFERENCES, "corpus artifacts",
                 f"job reference limit exceeded: limit {MAX_ARTIFACT_REFERENCES}, observed {reference_count}")
        inventories, work = capture_corpus._inventory(loaded, check_audio=True)
        selections = _preflight_selections(job, policy, loaded, inventories)
        # No artifact stat, open, hash or decode precedes the complete preflight.
        for _, _, parts, _ in work:
            snapshots.admit(corpus_root, parts)
        corpus_report = capture_corpus._audit_loaded(
            index, index_observation["observed_sha256"], corpus_root,
            corpus_root, before_corpus_root, loaded, check_files=True, check_audio=True)
        _require(corpus_report["index_sha256"] == index_observation["observed_sha256"],
                 "corpus report", "observed index identity differs from admitted bytes")
        _require(corpus_report["mode"] == "files_and_audio_checked", "corpus report",
                 "a complete files-and-audio audit is required")
        _require(len(corpus_report["edges"]) <= MAX_EDGES, "corpus report",
                 f"job graph edge limit exceeded: limit {MAX_EDGES}")
        reference, reference_samples = _selection_window(
            "reference", job, selections["reference"], corpus_report, corpus_root)
        candidate, candidate_samples = _selection_window(
            "candidate", job, selections["candidate"], corpus_report, corpus_root)
        analysis = job["analysis"]
        comparison = compare_capture.compare_signals(
            reference_samples, candidate_samples, analysis["sample_rate_hz"],
            frequencies_hz=analysis["frequencies_hz"], window=analysis["window"],
            floor_fs=analysis["floor_fs"])
        # Reserializing policy would change identity and can exceed its original
        # admitted byte bound. Preserve the consumed buffer through evaluation.
        evaluation = compare_capture.evaluate_policy(comparison, policy_bytes)
        _require(evaluation["policy_sha256"] == policy_observation["observed_sha256"],
                 "policy evaluation", "policy identity differs from the admitted original bytes")
        corpus_status, numerical = corpus_report["status"], evaluation["numerical_verdict"]
        status = ("failed" if corpus_status == "failed" or numerical == "fail" else
                  "inconclusive" if "inconclusive" in (corpus_status, numerical) else "pass")
        report = {
            "schema_version": 1, "job_contract": "capture-job-v1", "job_id": job["job_id"],
            "status": status, "inputs": {"job": job_observation,
                                         "corpus": index_observation, "policy": policy_observation},
            "job": copy.deepcopy(job), "policy": copy.deepcopy(policy),
            "reference": reference, "candidate": candidate,
            "self_comparison": job["reference"] == job["candidate"],
            "corpus_report": corpus_report, "evaluation": evaluation,
            "runtime": _runtime(), "tool_sources": sources,
            **dict.fromkeys(CLAIM_FIELDS, "not_established"),
        }
        _report_bytes(report)
        snapshots.verify()
        return report
    except JobError:
        raise
    except (OSError, ValueError, TypeError, OverflowError, ImportError) as error:
        raise JobError(f"cannot run job: {error}") from error


def _write_stdout(payload: bytes) -> None:
    # A real CLI stream always has a binary buffer. The text fallback admits
    # StringIO-style API callers without letting a terminal encoding alter bytes.
    stream = getattr(sys.stdout, "buffer", None)
    if stream is not None:
        written = stream.write(payload)
        _require(written == len(payload), "stdout", "incomplete output write")
        stream.flush()
    else:
        text = payload.decode("utf-8")
        written = sys.stdout.write(text)
        _require(written == len(text), "stdout", "incomplete output write")
        sys.stdout.flush()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                     allow_abbrev=False)
    parser.add_argument("--input", required=True, type=Path, help="identity-bound capture job JSON")
    parser.add_argument("--output", type=Path, help="new report file in an existing directory")
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return int(error.code)
    try:
        report = run_job(args.input)
        payload = _report_bytes(report)
        if args.output is not None:
            capture_common.write_json_new(args.output, report)
        _write_stdout(payload)
        return {"pass": 0, "failed": 1, "inconclusive": 3}[report["status"]]
    except (JobError, OSError, ValueError, TypeError, OverflowError, ImportError) as error:
        # Keep publication/cleanup context from the common helper verbatim.
        # Cancellation is deliberately outside this exception set.
        message = str(error).replace("\r", "\\r").replace("\n", "\\n")
        print(f"job error: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(capture_common._cli_exit(main, lambda message: print(
        f"job error: standard-stream delivery failed: {message}", file=sys.stderr)))
