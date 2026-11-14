#!/usr/bin/env python3
"""Independent file-job acceptance from the frozen capture-job-v1 contract.

Archives use assignment 17's independent literal v1 author. Expected metrics,
decisions, byte hashes, decoded hashes and fields are assembled here, never by
the production job/metric helpers. Fault hooks observe admission and retention;
they are not claims about an adversarial filesystem or native platform.
"""

from __future__ import annotations

from contextlib import ExitStack
import copy
import hashlib
import io
import json
import math
import os
from pathlib import Path
import platform
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import capture_audio
import capture_common
import capture_corpus
import compare_capture
import capture_job as subject
import test_capture_corpus as fixtures


TOOL = ROOT / "tools" / "capture_job.py"
SOURCES = ("capture_audio.py", "capture_common.py", "capture_corpus.py",
           "capture_job.py", "compare_capture.py", "validate_capture.py")
CLAIMS = {"boundary_equivalence", "synchronization", "authenticity",
          "specimen_identity", "calibration", "permissions", "independence",
          "preregistration", "final_holdout_history", "physical_fidelity"}
REPORT_KEYS = {"schema_version", "job_contract", "job_id", "status", "inputs",
               "job", "policy", "reference", "candidate", "self_comparison",
               "corpus_report", "evaluation", "runtime", "tool_sources"} | CLAIMS
SELECTION_KEYS = {"capture_id", "file_id", "purpose", "capture_kind", "file_kind",
                  "manifest_path", "manifest_sha256", "artifact_path",
                  "capture_manifest", "context_scope", "window", "inspection"}
INSPECTION_KEYS = {"schema_version", "inspector_version", "status", "size_bytes",
                   "sha256", "decoded_digest_version", "decoded_sha256", "format",
                   "container", "bits_per_sample", "sample_rate_hz", "channel_count",
                   "frame_count", "data_offset_bytes", "data_size_bytes", "chunk_count",
                   "duration_seconds", "amplitude_unit", "channels", "clipping",
                   "evidence_scope", "authenticity", "physical_clock", "calibration",
                   "physical_fidelity"}
VECTORS = (
    ([1.0, -1.0, 1.0, -1.0], "0000803f000080bf0000803f000080bf",
     "fd801740524b1e1c23a61b5400725b76428652827ba1261b83243eb5ce551402",
     "786665f3cf05b2f9b33e7cadee75e7176e122d62ad82133c72737c76261dd440"),
    ([1.25, -0.75, 1.25, -0.75], "0000a03f000040bf0000a03f000040bf",
     "bac1c395abe23908b8c106a28b6c151bc25b9473d470f4d942775b5dfdf523e2",
     "79d8014af588d583abcc570598d3e073413543ef518b339cbca37dbb5eb6bd0c"),
    ([1.5, -0.5, 1.5, -0.5], "0000c03f000000bf0000c03f000000bf",
     "36d231b4ecc15924aea04f08725924f18ae4346fd287747791d7396eca3d5758",
     "52c3450c9c276f60b8ed6dc728977cfe33b4b0702ce8332927169d25f18e4db8"),
)


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def encoded(value, *, compact=False):
    options = {"separators": (",", ":")} if compact else {"indent": 2}
    return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                       allow_nan=False, **options) + "\n").encode("utf-8")


def raw(values):
    return struct.pack("<" + "f" * len(values), *values)


def decoded(values, rate=4, channels=1):
    preimage = (b"HAMMOND-CAPTURE-DECODED-V1\0"
                + struct.pack("<IIQ", rate, channels, len(values) // channels)
                + b"".join(struct.pack("<d", 0.0 if x == 0 else x) for x in values))
    return sha(preimage)


def criterion(ident="rms-limit", *, metric="rms_error_fs", channel=0,
              frequency=None, bound=0.375, margin=0.125,
              basis="synthetic_numerical"):
    unit = "rad" if metric.endswith("_rad") else (
        "ratio" if metric.startswith("normalized_") else "FS")
    uncertainty = {"margin": margin, "unit": unit, "basis": basis,
                   "evidence": "Declared synthetic fixture margin.", "unknown_reason": None}
    if basis == "unknown":
        uncertainty.update(margin=None, evidence=None,
                           unknown_reason="No physical uncertainty was acquired.")
    return {"criterion_id": ident,
            "target": {"channel_index": channel, "frequency_hz": frequency, "metric": metric},
            "upper_bound": bound, "unit": unit,
            "rationale": "Predeclared literal acceptance fixture.", "uncertainty": uncertainty}


class JobArchive:
    """Independent author of original job, policy, corpus and raw byte files."""

    def __init__(self, root, *, reference=None, candidate=None, purpose="validation",
                 rate=4, channels=1, frames=4, frequencies=(1,), hardware=(False, False)):
        self.root = Path(root)
        self.root.mkdir(parents=True)
        self.archive = fixtures._Archive(self.root / "corpus")
        values = (VECTORS[0][0] if reference is None else reference,
                  VECTORS[1][0] if candidate is None else candidate)
        for ident, samples, declared_hardware in zip(("reference", "candidate"), values, hardware):
            self.archive.add(ident, purpose, raw=raw(samples), rate=rate, channels=channels,
                             format_name="raw_float32_le", hardware=declared_hardware)
        analysis = {"sample_rate_hz": rate, "channel_count": channels, "frame_count": frames,
                    "window": "rectangular", "floor_fs": 1e-12,
                    "frequencies_hz": list(frequencies)}
        role = {"fit": "fit", "validation": "validation", "final": "final_test",
                "unassigned": "unassigned"}[purpose]
        self.policy = {"schema_version": 1, "metric_contract": "capture-comparison-v1",
                       "policy_id": "literal-policy-v1",
                       "evidence_class": "synthetic_numerical_fixture", "evaluation_role": role,
                       "freeze_evidence": {"value": None,
                                           "unknown_reason": "No chronology is established by a fixture."},
                       "analysis": copy.deepcopy(analysis), "criteria": [criterion()]}
        self.job = {"schema_version": 1, "contract_origin": "project-proposed-capture-job-v1",
                    "job_id": "literal-offset-v1", "corpus": {"path": "corpus/corpus.json", "sha256": "0" * 64},
                    "reference": {"capture_id": "reference", "file_id": "raw", "start_frame": 0},
                    "candidate": {"capture_id": "candidate", "file_id": "raw", "start_frame": 0},
                    "analysis": analysis, "policy": {"path": "policy.json", "sha256": "0" * 64},
                    "pairing": "index", "transform": "none"}
        self.path = self.root / "job.json"
        self.policy_path = self.root / "policy.json"

    def write(self, *, policy_bytes=None, job_bytes=None):
        self.archive.write()
        self.policy_path.write_bytes(encoded(self.policy) if policy_bytes is None else policy_bytes)
        self.job["corpus"]["sha256"] = sha(self.archive.path.read_bytes())
        self.job["policy"]["sha256"] = sha(self.policy_path.read_bytes())
        self.path.write_bytes(encoded(self.job) if job_bytes is None else job_bytes)
        return self.path


class JobAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hammond-job-test-")
        self.addCleanup(self.temp.cleanup)
        # Match the producer's canonical observations on macOS and Windows.
        self.work = Path(self.temp.name).resolve(strict=True)
        self.fixture = JobArchive(self.work / "archive")
        self.fixture.write()

    def fixture_at(self, name, **options):
        result = JobArchive(self.work / name, **options)
        result.write()
        return result

    def run_job(self, fixture=None):
        return subject.run_job((fixture or self.fixture).path)

    def cli(self, fixture=None, *flags, cwd=None, env=None):
        return subprocess.run([sys.executable, "-B", str(TOOL), "--input",
                               str((fixture or self.fixture).path), *flags],
                              cwd=cwd or self.work, env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=30, check=False)

    def main(self, flags):
        buffer = io.BytesIO()
        stdout = io.TextIOWrapper(buffer, encoding="ascii", errors="strict")
        stderr = io.StringIO()
        try:
            with mock.patch.object(sys, "stdout", stdout), mock.patch.object(sys, "stderr", stderr):
                result = subject.main(flags)
            stdout.flush()
            return result, buffer.getvalue(), stderr.getvalue()
        finally:
            stdout.detach()

    def patched_call(self, stack, module, name, replacement):
        """Observe an actual imported call whether producer uses module or import-name syntax."""
        original = getattr(module, name)
        patched = stack.enter_context(mock.patch.object(module, name, side_effect=replacement))
        if getattr(subject, name, None) is original:
            stack.enter_context(mock.patch.object(subject, name, patched))
        return patched

    def reject_before_artifacts(self, fixture=None):
        with ExitStack() as stack:
            scans = [self.patched_call(stack, capture_corpus, "_verify_artifact",
                                      AssertionError("artifact hashing entered before preflight")),
                     self.patched_call(stack, capture_audio, "inspect_audio",
                                      AssertionError("audio inspection entered before preflight")),
                     self.patched_call(stack, capture_audio, "read_audio_window",
                                      AssertionError("audio window entered before preflight"))]
            with self.assertRaises(subject.JobError):
                self.run_job(fixture)
            for scan in scans:
                self.assertEqual(scan.call_count, 0)

    def assert_report(self, report, fixture=None):
        fixture = fixture or self.fixture
        self.assertEqual(set(report), REPORT_KEYS)
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["job_contract"], "capture-job-v1")
        self.assertEqual(report["job_id"], fixture.job["job_id"])
        self.assertEqual(report["job"], fixture.job)
        self.assertEqual(report["policy"], fixture.policy)
        for field in CLAIMS:
            self.assertEqual(report[field], "not_established")
        self.assertEqual(set(report["inputs"]), {"job", "corpus", "policy"})
        self.assertEqual(report["inputs"]["job"], {"size_bytes": len(fixture.path.read_bytes()),
                                                   "sha256": sha(fixture.path.read_bytes())})
        for name, path in (("corpus", fixture.archive.path), ("policy", fixture.policy_path)):
            self.assertEqual(report["inputs"][name], {
                "path": fixture.job[name]["path"], "size_bytes": len(path.read_bytes()),
                "expected_sha256": fixture.job[name]["sha256"], "observed_sha256": sha(path.read_bytes())})
        self.assertEqual(report["inputs"]["corpus"]["observed_sha256"], report["corpus_report"]["index_sha256"])
        self.assertEqual(report["inputs"]["policy"]["observed_sha256"], report["evaluation"]["policy_sha256"])
        self.assertEqual(report["corpus_report"]["mode"], "files_and_audio_checked")
        for side in ("reference", "candidate"):
            selected = report[side]
            selector = fixture.job[side]
            manifest = fixture.archive.manifests[selector["capture_id"]]
            entry = fixture.archive.entries[selector["capture_id"]]
            self.assertEqual(set(selected), SELECTION_KEYS)
            self.assertEqual(selected["capture_manifest"], manifest)
            self.assertEqual(selected["manifest_path"], entry["manifest_path"])
            self.assertEqual(selected["manifest_sha256"], sha((fixture.archive.root / entry["manifest_path"]).read_bytes()))
            self.assertEqual(selected["window"], {"start_frame": selector["start_frame"],
                                                  "frame_count": fixture.job["analysis"]["frame_count"],
                                                  "end_frame": selector["start_frame"] + fixture.job["analysis"]["frame_count"]})
            self.assertEqual(set(selected["inspection"]), INSPECTION_KEYS)
        self.assertNotIn(str(fixture.root), encoded(report).decode("utf-8"))
        self.assertNotIn('"samples":', encoded(report).decode("utf-8"))

    def assert_error(self, result):
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertTrue(result.stderr.startswith(b"job error:"), result.stderr)
        self.assertEqual(len(result.stderr.splitlines()), 1)

    def test_validate_is_io_free_and_load_returns_fresh_exact_value(self):
        before = copy.deepcopy(self.fixture.job)
        loaded = subject.load_job(self.fixture.path)
        self.assertEqual(loaded, before)
        self.assertIsNot(loaded, self.fixture.job)
        shutil.rmtree(self.fixture.root)
        self.assertIsNone(subject.validate_job(before))
        self.assertEqual(before, self.fixture.job)

    def test_all_missing_and_unknown_input_keys_reject(self):
        paths = ((), ("corpus",), ("policy",), ("reference",), ("candidate",), ("analysis",))
        for path in paths:
            original = self.fixture.job
            for key in path:
                original = original[key]
            for missing in (*original, None):
                with self.subTest(path=path, missing=missing):
                    value = copy.deepcopy(self.fixture.job)
                    target = value
                    for key in path:
                        target = target[key]
                    if missing is None:
                        target["unknown"] = "reject"
                    else:
                        del target[missing]
                    with self.assertRaises(subject.JobError):
                        subject.validate_job(value)

    def test_exact_types_reject_bool_subclasses_tuple_cycles_and_nonfinite(self):
        class DictSubclass(dict):
            pass
        class IntSubclass(int):
            pass
        cases = [DictSubclass(self.fixture.job)]
        for field, bad in (("schema_version", True), ("schema_version", 1.0),
                           ("schema_version", IntSubclass(1)), ("reference", [])):
            value = copy.deepcopy(self.fixture.job)
            value[field] = bad
            cases.append(value)
        for field, bad in (("channel_count", True), ("sample_rate_hz", 4.0),
                           ("frame_count", IntSubclass(4)), ("floor_fs", float("nan")),
                           ("floor_fs", float("inf")), ("frequencies_hz", (1,))):
            value = copy.deepcopy(self.fixture.job)
            value["analysis"][field] = bad
            cases.append(value)
        cyclic = copy.deepcopy(self.fixture.job)
        cyclic["analysis"]["frequencies_hz"] = [cyclic]
        cases.append(cyclic)
        for index, value in enumerate(cases):
            with self.subTest(index=index), self.assertRaises(subject.JobError):
                subject.validate_job(value)

    def test_portable_paths_ids_digests_and_fixed_literals_reject(self):
        bad_paths = ("", ".", "..", "../policy.json", "/policy.json", "a//b", "a/./b", "a\\b",
                     "C:policy.json", "//server/p", "con", "NUL.json", "a/com1.wav", "policy.",
                     "réel.json", "a/" * 8 + "z", "a" * 65, ".hidden", "p\n")
        for path in bad_paths:
            for field in ("corpus", "policy"):
                with self.subTest(path=path, field=field):
                    value = copy.deepcopy(self.fixture.job)
                    value[field]["path"] = path
                    with self.assertRaises(subject.JobError):
                        subject.validate_job(value)
        for field, bad in (("job_id", "Upper"), ("job_id", "a" * 65),
                           ("contract_origin", "capture-job-v1"), ("pairing", "channel_name"),
                           ("transform", "fitted_delay")):
            value = copy.deepcopy(self.fixture.job)
            value[field] = bad
            with self.subTest(field=field), self.assertRaises(subject.JobError):
                subject.validate_job(value)
        for bad in ("F" * 64, "0" * 63, "0" * 65, 0, "g" * 64):
            value = copy.deepcopy(self.fixture.job)
            value["corpus"]["sha256"] = bad
            with self.subTest(digest=bad), self.assertRaises(subject.JobError):
                subject.validate_job(value)

    def test_intrinsic_geometry_window_and_work_limits(self):
        changes = ({"sample_rate_hz": 0}, {"sample_rate_hz": 768001}, {"channel_count": 0},
                   {"channel_count": 17}, {"frame_count": 0}, {"frame_count": 262145},
                   {"window": "hann_symmetric", "frame_count": 2}, {"window": "blackman"},
                   {"floor_fs": 0}, {"floor_fs": 1000001}, {"frequencies_hz": [1, 1.0]},
                   {"frequencies_hz": [2, 1]}, {"frequencies_hz": [-1]}, {"frequencies_hz": [2.1]},
                   {"frequencies_hz": list(range(65)), "sample_rate_hz": 128},
                   {"sample_rate_hz": 1, "frame_count": 601, "frequencies_hz": []},
                   {"sample_rate_hz": 48000, "frame_count": 65537, "channel_count": 16},
                   {"sample_rate_hz": 48000, "frame_count": 16385, "channel_count": 16,
                    "frequencies_hz": list(range(64))})
        for change in changes:
            value = copy.deepcopy(self.fixture.job)
            value["analysis"].update(change)
            with self.subTest(change=change), self.assertRaises(subject.JobError):
                subject.validate_job(value)
        for bad in (-1, True, 0.0, 134217728, 134217725):
            value = copy.deepcopy(self.fixture.job)
            value["reference"]["start_frame"] = bad
            with self.subTest(start=bad), self.assertRaises(subject.JobError):
                subject.validate_job(value)
        value = copy.deepcopy(self.fixture.job)
        value["analysis"].update(sample_rate_hz=48000, channel_count=16, frame_count=16384,
                                  frequencies_hz=list(range(64)))
        self.assertIsNone(subject.validate_job(value))
        value = copy.deepcopy(self.fixture.job)
        value["analysis"].update(window="hann_symmetric", frame_count=3, frequencies_hz=[])
        self.assertIsNone(subject.validate_job(value))

    def test_strict_job_bytes_and_exact_byte_ceiling(self):
        normal = self.fixture.path.read_bytes()
        invalid = (b"\xef\xbb\xbf" + normal, normal + b"{}", b"\xff",
                   normal.replace(b'"schema_version": 1', b'"schema_version": 1, "schema_version": 1'),
                   normal.replace(b'"schema_version": 1', b'"schema_version": 1.0'),
                   normal.replace(b'"floor_fs": 1e-12', b'"floor_fs": NaN'),
                   normal.replace(b'"literal-offset-v1"', b'"a\\ud800"'),
                   normal.replace(b'"literal-offset-v1"', b'"a\\u0001"'),
                   normal.replace(b'"frame_count": 4', b'"frame_count": ' + b"1" * 65))
        for index, payload in enumerate(invalid):
            self.fixture.path.write_bytes(payload)
            with self.subTest(index=index), self.assertRaises(subject.JobError):
                subject.load_job(self.fixture.path)
        self.fixture.path.write_bytes(normal + b" " * (65536 - len(normal)))
        self.assertEqual(subject.load_job(self.fixture.path), self.fixture.job)
        self.fixture.path.write_bytes(normal + b" " * (65537 - len(normal)))
        with self.assertRaises(subject.JobError):
            subject.load_job(self.fixture.path)

    def test_six_printed_hashes_match_independent_literal_preimages(self):
        contract = (ROOT / "docs/CAPTURE_JOB_CONTRACT.md").read_text(encoding="utf-8")
        for values, hex_bytes, byte_hash, decoded_hash in VECTORS:
            with self.subTest(byte_hash=byte_hash):
                self.assertEqual(raw(values), bytes.fromhex(hex_bytes))
                self.assertEqual(sha(raw(values)), byte_hash)
                self.assertEqual(decoded(values), decoded_hash)
                self.assertIn(byte_hash, contract)
                self.assertIn(decoded_hash, contract)
        report = self.run_job()
        for side, vector in (("reference", VECTORS[0]), ("candidate", VECTORS[1])):
            self.assertEqual(report[side]["inspection"]["sha256"], vector[2])
            self.assertEqual(report[side]["inspection"]["decoded_sha256"], vector[3])
        half = self.fixture_at("half", candidate=VECTORS[2][0])
        self.assertEqual(self.run_job(half)["candidate"]["inspection"]["sha256"], VECTORS[2][2])
        self.assertEqual(self.run_job(half)["candidate"]["inspection"]["decoded_sha256"], VECTORS[2][3])

    def test_literal_quarter_interval_pass_and_complete_metrics(self):
        report = self.run_job()
        self.assert_report(report)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["corpus_report"]["status"], "pass")
        self.assertEqual(report["evaluation"]["numerical_verdict"], "pass")
        observed = report["evaluation"]["comparison"]["channels"][0]["metrics"]
        for name in ("dc_bias_fs", "absolute_dc_bias_fs", "rms_error_fs", "max_abs_error_fs"):
            self.assertEqual(observed[name], {"value": 0.25, "unit": "FS", "undefined_reason": None})
        decision = report["evaluation"]["criteria"][0]
        self.assertEqual(decision["interval"], {"lower": 0.125, "upper": 0.375, "unit": "FS", "undefined_reason": None})
        self.assertEqual(decision["numerical_verdict"], "pass")
        self.assertEqual(report["evaluation"]["comparison"]["analysis"]["transform"], "none")

    def test_literal_quarter_interval_inconclusive(self):
        self.fixture.policy["criteria"][0]["upper_bound"] = 0.25
        self.fixture.write()
        report = self.run_job()
        self.assertEqual(report["status"], "inconclusive")
        self.assertEqual(report["evaluation"]["criteria"][0]["numerical_verdict"], "inconclusive")
        self.assertEqual(report["evaluation"]["criteria"][0]["reason"], "interval_overlaps_upper_bound")

    def test_literal_half_interval_fail(self):
        fixture = self.fixture_at("half-fail", candidate=VECTORS[2][0])
        fixture.policy["criteria"][0]["upper_bound"] = 0.25
        fixture.write()
        report = self.run_job(fixture)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["evaluation"]["numerical_verdict"], "fail")
        self.assertEqual(report["evaluation"]["criteria"][0]["interval"],
                         {"lower": 0.375, "upper": 0.625, "unit": "FS", "undefined_reason": None})

    def test_lower_endpoint_equality_remains_inconclusive(self):
        fixture = self.fixture_at("equality", candidate=[1.375, -0.625, 1.375, -0.625])
        fixture.policy["criteria"][0]["upper_bound"] = 0.25
        fixture.write()
        report = self.run_job(fixture)
        self.assertEqual(report["status"], "inconclusive")
        self.assertEqual(report["evaluation"]["criteria"][0]["interval"]["lower"], 0.25)

    def test_distinct_original_windows_keep_complete_stream_identities(self):
        reference = [9.0, 8.0, *VECTORS[0][0], 7.0]
        candidate = [6.0, *VECTORS[1][0], 5.0, 4.0, 3.0]
        fixture = self.fixture_at("windows", reference=reference, candidate=candidate)
        fixture.job["reference"]["start_frame"] = 2
        fixture.job["candidate"]["start_frame"] = 1
        fixture.write()
        report = self.run_job(fixture)
        self.assert_report(report, fixture)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["evaluation"]["criteria"][0]["observed"]["value"], 0.25)
        for side, values in (("reference", reference), ("candidate", candidate)):
            inspection = report[side]["inspection"]
            self.assertEqual(inspection["frame_count"], len(values))
            self.assertEqual(inspection["sha256"], sha(raw(values)))
            self.assertEqual(inspection["decoded_sha256"], decoded(values))
            self.assertEqual(inspection["channels"][0]["sample_count"], len(values))
            self.assertEqual(inspection["channels"][0]["peak"], max(map(abs, values)))

    def test_nonfinite_samples_outside_either_window_reject(self):
        for side in ("reference", "candidate"):
            for invalid in (float("nan"), float("inf"), -float("inf")):
                with self.subTest(side=side, invalid=str(invalid)):
                    options = {side: [*VECTORS[0 if side == "reference" else 1][0], invalid]}
                    fixture = self.fixture_at(f"bad-{side}-{len(list(self.work.iterdir()))}", **options)
                    with self.assertRaises(subject.JobError):
                        self.run_job(fixture)

    def test_requested_window_cannot_exceed_actual_frames(self):
        self.fixture.job["candidate"]["start_frame"] = 1
        self.fixture.write()
        with self.assertRaises(subject.JobError):
            self.run_job()

    def test_all_channels_are_compared_in_original_index_order(self):
        reference = [x for value in VECTORS[0][0] for x in (value, value * 2)]
        candidate = [x for value in VECTORS[0][0] for x in (value + 0.25, value * 2 + 0.5)]
        fixture = self.fixture_at("stereo", reference=reference, candidate=candidate, channels=2)
        fixture.policy["criteria"].append(criterion("right", channel=1, bound=0.625))
        fixture.write()
        report = self.run_job(fixture)
        self.assertEqual(report["status"], "pass")
        self.assertEqual([(c["reference_channel_index"], c["candidate_channel_index"], c["metrics"]["rms_error_fs"]["value"])
                          for c in report["evaluation"]["comparison"]["channels"]], [(0, 0, 0.25), (1, 1, 0.5)])

    def test_unrelated_duplicate_fit_capture_fails_whole_job(self):
        self.fixture.archive.add("leak", "fit", raw=raw(VECTORS[0][0]), rate=4, format_name="raw_float32_le")
        self.fixture.write()
        report = self.run_job()
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["evaluation"]["numerical_verdict"], "pass")
        self.assertEqual(report["corpus_report"]["status"], "failed")
        self.assertEqual({c["capture_id"] for c in report["corpus_report"]["captures"]}, {"reference", "candidate", "leak"})
        reasons = {edge["reason"] for edge in report["corpus_report"]["edges"]}
        self.assertTrue({"artifact_sha256", "decoded_audio_sha256"} <= reasons)
        self.assertIn("cross_purpose_component", {f["code"] for f in report["corpus_report"]["findings"]})

    def test_unrelated_declared_parent_retains_transitive_split_failure(self):
        self.fixture.archive.add("ancestor", "fit", raw=raw([0.1, 0.2, 0.3, 0.4]), rate=4,
                                 format_name="raw_float32_le")
        self.fixture.archive.entries["candidate"]["parent_capture_ids"] = ["ancestor"]
        self.fixture.write()
        report = self.run_job()
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["evaluation"]["numerical_verdict"], "pass")
        self.assertTrue(any(set(f["capture_ids"]) == {"ancestor", "candidate"}
                            and f["code"] == "cross_purpose_component" for f in report["corpus_report"]["findings"]))

    def test_unrelated_planned_unassigned_capture_keeps_inconclusive_findings(self):
        self.fixture.archive.add("plan", "unassigned", planned=True)
        self.fixture.write()
        report = self.run_job()
        self.assertEqual(report["status"], "inconclusive")
        self.assertEqual(report["evaluation"]["numerical_verdict"], "pass")
        self.assertEqual({f["code"] for f in report["corpus_report"]["findings"]}, {"planned_capture", "unassigned_capture"})

    def test_numerical_failure_retains_inconclusive_whole_corpus(self):
        fixture = self.fixture_at("failure-and-plan", candidate=VECTORS[2][0])
        fixture.policy["criteria"][0]["upper_bound"] = 0.25
        fixture.archive.add("plan", "unassigned", planned=True)
        fixture.write()
        report = self.run_job(fixture)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["corpus_report"]["status"], "inconclusive")
        self.assertEqual(report["evaluation"]["numerical_verdict"], "fail")
        self.assertEqual(len(report["corpus_report"]["findings"]), 2)

    def test_all_purpose_to_policy_role_mappings(self):
        for purpose, role in (("fit", "fit"), ("validation", "validation"), ("final", "final_test"),
                              ("unassigned", "unassigned")):
            fixture = self.fixture_at("purpose-" + purpose, purpose=purpose)
            report = self.run_job(fixture)
            with self.subTest(purpose=purpose):
                self.assertEqual(report["evaluation"]["evaluation_role"], role)
                self.assertEqual(report["reference"]["purpose"], purpose)
                self.assertEqual(report["candidate"]["purpose"], purpose)
                self.assertEqual(report["status"], "inconclusive" if purpose == "unassigned" else "pass")
                for field in CLAIMS:
                    self.assertEqual(report[field], "not_established")

    def test_purpose_mismatch_and_wrong_policy_role_reject_before_artifacts(self):
        self.fixture.archive.entries["candidate"]["purpose"] = "fit"
        self.fixture.archive.manifests["candidate"]["partition"]["role"] = "fit"
        self.fixture.write()
        self.reject_before_artifacts()
        for role in ("fit", "final_test", "unassigned"):
            fixture = self.fixture_at("wrong-role-" + role)
            fixture.policy["evaluation_role"] = role
            fixture.write()
            with self.subTest(role=role):
                self.reject_before_artifacts(fixture)

    def test_synthetic_policy_rejects_either_selected_hardware_kind(self):
        for hardware in ((True, False), (False, True), (True, True)):
            fixture = self.fixture_at("hardware-" + str(hardware), hardware=hardware)
            with self.subTest(hardware=hardware):
                self.reject_before_artifacts(fixture)

    def test_digital_policy_accepts_all_selected_kind_combinations_without_physical_claims(self):
        for hardware in ((False, False), (True, False), (False, True), (True, True)):
            fixture = self.fixture_at("digital-" + str(hardware), hardware=hardware)
            fixture.policy["evidence_class"] = "digital_comparison"
            fixture.policy["criteria"][0]["uncertainty"]["basis"] = "declared_margin"
            fixture.write()
            report = self.run_job(fixture)
            with self.subTest(hardware=hardware):
                self.assertEqual(report["status"], "pass")
                self.assertEqual(report["reference"]["capture_kind"], "hardware" if hardware[0] else "synthetic")
                self.assertEqual(report["candidate"]["capture_kind"], "hardware" if hardware[1] else "synthetic")
                for field in CLAIMS:
                    self.assertEqual(report[field], "not_established")

    def test_unselected_hardware_does_not_reclassify_synthetic_pair(self):
        self.fixture.archive.add("other-hardware", "fit", hardware=True,
                                 raw=raw([0.1, 0.2, 0.3, 0.4]), rate=4, format_name="raw_float32_le")
        self.fixture.write()
        report = self.run_job()
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["evaluation"]["evidence_class"], "synthetic_numerical_fixture")
        self.assertEqual(len(report["corpus_report"]["captures"]), 3)

    def test_exact_self_comparison_exposed_and_different_window_is_not_self(self):
        self.fixture.job["candidate"] = copy.deepcopy(self.fixture.job["reference"])
        self.fixture.write()
        report = self.run_job()
        self.assertIs(report["self_comparison"], True)
        self.assertEqual(report["evaluation"]["criteria"][0]["observed"]["value"], 0)
        values = [*VECTORS[0][0], *VECTORS[1][0]]
        fixture = self.fixture_at("same-file-windows", reference=values)
        fixture.job["candidate"] = {"capture_id": "reference", "file_id": "raw", "start_frame": 4}
        fixture.write()
        report = self.run_job(fixture)
        self.assertIs(report["self_comparison"], False)
        self.assertEqual(report["evaluation"]["criteria"][0]["observed"]["value"], 0.25)

    def test_raw_selection_retains_complete_bound_context(self):
        manifest = self.fixture.archive.manifests["reference"]
        manifest["stimulus"]["description"] = fixtures._known("Literal fixture — no acquired organ.")
        manifest["signal_path"]["loading"] = fixtures._known("No physical load is asserted.")
        self.fixture.write()
        report = self.run_job()
        self.assert_report(report)
        self.assertEqual(report["reference"]["context_scope"], "selected_raw_stream")
        self.assertEqual(report["reference"]["artifact_path"], "reference/raw.bin")
        self.assertEqual(report["reference"]["capture_manifest"]["stimulus"], manifest["stimulus"])
        self.assertEqual(report["reference"]["capture_manifest"]["physical_clock"], manifest["physical_clock"])

    def test_derivative_owns_changed_geometry_and_does_not_inherit_raw_context(self):
        self.fixture.job["analysis"].update(sample_rate_hz=8, channel_count=2, frequencies_hz=[0])
        self.fixture.policy["analysis"] = copy.deepcopy(self.fixture.job["analysis"])
        for side, vector in (("reference", VECTORS[0][0]), ("candidate", VECTORS[1][0])):
            values = [x for value in vector for x in (value, value)]
            self.fixture.archive.file(side, "processed", fixtures._wave(values, rate=8, channels=2, floating=True, bits=32),
                                      descriptor={"format": "wav_float32", "sample_rate_hz": 8, "channel_count": 2})
            self.fixture.job[side]["file_id"] = "processed"
        self.fixture.write()
        report = self.run_job()
        self.assert_report(report)
        self.assertEqual(report["status"], "pass")
        for side in ("reference", "candidate"):
            selected = report[side]
            self.assertEqual(selected["context_scope"], "ancestor_raw_stream_only")
            self.assertEqual(selected["file_kind"], "derived")
            self.assertEqual(selected["capture_manifest"]["digital"]["channel_count"]["value"], 1)
            self.assertEqual(selected["capture_manifest"]["digital"]["sample_rate_hz"]["value"], 4)
            self.assertEqual(selected["inspection"]["channel_count"], 2)
            self.assertEqual(selected["inspection"]["sample_rate_hz"], 8)
            self.assertEqual(selected["inspection"]["format"], "wav_float32")
            self.assertEqual(selected["inspection"]["calibration"], "not_established")
            self.assertEqual(selected["inspection"]["physical_clock"], "not_established")

    def test_support_missing_planned_and_undescribed_derivative_selections_reject(self):
        for case in ("support", "derived", "missing-file", "missing-capture", "planned"):
            fixture = self.fixture_at("selection-" + case)
            if case in ("support", "derived"):
                fixture.archive.file("candidate", "chosen", raw(VECTORS[1][0]), kind=case)
                fixture.job["candidate"]["file_id"] = "chosen"
            elif case == "missing-file":
                fixture.job["candidate"]["file_id"] = "missing"
            elif case == "missing-capture":
                fixture.job["candidate"]["capture_id"] = "missing"
            else:
                fixture.archive.add("plan", "validation", planned=True)
                fixture.job["candidate"]["capture_id"] = "plan"
            fixture.write()
            with self.subTest(case=case):
                self.reject_before_artifacts(fixture)

    def test_job_policy_geometry_mismatch_rejects_before_artifacts(self):
        for field, value in (("sample_rate_hz", 8), ("channel_count", 2), ("frame_count", 3),
                              ("window", "hann_symmetric"), ("floor_fs", 1e-6), ("frequencies_hz", [0])):
            fixture = self.fixture_at("analysis-" + field)
            fixture.policy["analysis"][field] = value
            fixture.write()
            with self.subTest(field=field):
                self.reject_before_artifacts(fixture)

    def test_selected_declared_geometry_mismatch_rejects_before_artifacts(self):
        for field, value in (("sample_rate_hz", 8), ("channel_count", 2)):
            fixture = self.fixture_at("descriptor-" + field)
            fixture.job["analysis"][field] = value
            fixture.policy["analysis"][field] = value
            fixture.write()
            with self.subTest(field=field):
                self.reject_before_artifacts(fixture)

    def test_invalid_policy_rejects_before_any_artifact_scan(self):
        duplicate = encoded(self.fixture.policy).replace(
            b'"schema_version": 1', b'"schema_version": 1, "schema_version": 1')
        for payload in (b"{}", duplicate, b"\xef\xbb\xbf{}", b" " * 65537):
            self.fixture.write(policy_bytes=payload)
            with self.subTest(size=len(payload)):
                self.reject_before_artifacts()

    def test_expected_policy_and_index_bytes_bind_whitespace(self):
        for name in ("policy", "index"):
            fixture = self.fixture_at("changed-" + name)
            path = fixture.policy_path if name == "policy" else fixture.archive.path
            path.write_bytes(path.read_bytes() + b" ")
            with self.subTest(name=name):
                self.reject_before_artifacts(fixture)

    def test_manifest_exact_consumed_bytes_bind_whitespace_before_artifacts(self):
        manifest = self.fixture.archive.root / self.fixture.archive.entries["reference"]["manifest_path"]
        manifest.write_bytes(manifest.read_bytes() + b" ")
        self.reject_before_artifacts()

    def test_artifact_byte_mismatch_and_missing_unrelated_support_reject(self):
        path = self.fixture.archive.file_path("candidate", "raw")
        path.write_bytes(raw(VECTORS[2][0]))
        with self.assertRaises(subject.JobError):
            self.run_job()
        fixture = self.fixture_at("unrelated-support")
        fixture.archive.add("other", "fit", raw=raw([0.1, 0.2, 0.3, 0.4]), rate=4, format_name="raw_float32_le")
        fixture.archive.file("other", "notes", b"The complete audit must consume this.", kind="support")
        fixture.write()
        fixture.archive.file_path("other", "notes").unlink()
        with self.assertRaises(subject.JobError):
            self.run_job(fixture)

    def test_sixty_four_captures_are_admitted_and_sixty_five_reject_before_manifests(self):
        for index in range(62):
            self.fixture.archive.add(f"plan-{index:02}", "unassigned", planned=True)
        self.fixture.write()
        report = self.run_job()
        self.assertEqual(len(report["corpus_report"]["captures"]), 64)
        self.assertEqual(report["status"], "inconclusive")
        self.fixture.archive.add("plan-62", "unassigned", planned=True)
        self.fixture.write()
        with mock.patch.object(capture_corpus, "_load_manifests", side_effect=AssertionError("manifest read before 64-capture check")) as manifests:
            self.reject_before_artifacts()
            self.assertEqual(manifests.call_count, 0)

    def test_reference_limit_counts_support_files_and_accepts_exact_256(self):
        for number in range(6):
            self.fixture.archive.add(f"extra-{number}", "validation", raw=raw([number + 2.0]),
                                     rate=4, format_name="raw_float32_le")
        for ident in self.fixture.archive.manifests:
            for index in range(31):
                self.fixture.archive.file(ident, f"support-{index}", (ident + str(index)).encode("ascii"), kind="support")
        self.fixture.write()
        report = self.run_job()
        self.assertEqual(sum(len(c["files"]) for c in report["corpus_report"]["captures"]), 256)
        self.fixture.archive.add("overflow", "validation", raw=raw([10.0]), rate=4, format_name="raw_float32_le")
        self.fixture.write()
        self.reject_before_artifacts()

    def test_artifact_and_audio_aggregate_limits_reject_before_reads(self):
        for case in ("audio", "all-artifacts"):
            fixture = self.fixture_at("aggregate-" + case)
            if case == "audio":
                for record in fixture.archive.manifests.values():
                    record["files"][0]["size_bytes"] = 134217729
            else:
                for index in range(7):
                    ident = f"extra-{index}"
                    fixture.archive.add(ident, "validation", raw=raw([index + 2.0]), rate=4,
                                         format_name="raw_float32_le")
                    item = fixture.archive.file(ident, "large", b"x", kind="support")
                    item["size_bytes"] = 268435456
                for ident in ("reference", "candidate"):
                    item = fixture.archive.file(ident, "large", b"x", kind="support")
                    item["size_bytes"] = 268435456
            fixture.write()
            with self.subTest(case=case):
                self.reject_before_artifacts(fixture)

    def test_original_policy_bytes_are_passed_unchanged_to_evaluation(self):
        original = b"  " + encoded(self.fixture.policy, compact=True) + b" \n"
        self.fixture.write(policy_bytes=original)
        real = compare_capture.evaluate_policy
        received = []
        def observe(comparison, payload):
            received.append(payload)
            return real(comparison, payload)
        with ExitStack() as stack:
            self.patched_call(stack, compare_capture, "evaluate_policy", observe)
            report = self.run_job()
        self.assertEqual(received, [original])
        self.assertEqual(report["evaluation"]["policy_sha256"], sha(original))
        self.assertNotEqual(sha(original), sha(encoded(report["policy"])))

    def test_valid_compact_policy_can_exceed_sixty_four_kib_when_formatted(self):
        reference = [x for value in VECTORS[0][0] for x in (value, value, value)]
        candidate = [x for value in VECTORS[1][0] for x in (value, value, value)]
        fixture = self.fixture_at("compact-policy", reference=reference, candidate=candidate,
                                  rate=128, channels=3, frequencies=range(64))
        fixture.policy["criteria"] = []
        for channel in range(3):
            for frequency in range(64):
                item = criterion(f"c{channel}-f{frequency}", metric="complex_abs_error_fs",
                                 channel=channel, frequency=frequency, bound=2)
                item["rationale"] = "Fixture."
                item["uncertainty"]["evidence"] = "Fixture."
                fixture.policy["criteria"].append(item)
        payload = encoded(fixture.policy, compact=True)
        self.assertLessEqual(len(payload), 65536)
        self.assertGreater(len(encoded(fixture.policy)), 65536)
        fixture.write(policy_bytes=payload)
        report = self.run_job(fixture)
        self.assertEqual(report["evaluation"]["policy_sha256"], sha(payload))
        self.assertEqual(len(report["evaluation"]["criteria"]), 192)
        self.assertEqual(report["status"], "pass")

    def test_job_whitespace_changes_only_the_original_job_identity(self):
        first = self.run_job()
        self.fixture.path.write_bytes(b"  " + encoded(self.fixture.job, compact=True) + b" ")
        second = self.run_job()
        self.assertNotEqual(first["inputs"]["job"], second["inputs"]["job"])
        first["inputs"]["job"] = second["inputs"]["job"]
        self.assertEqual(first, second)

    def test_runtime_and_six_tool_sources_are_exact_observations(self):
        report = self.run_job()
        self.assertEqual(report["runtime"], {"python_implementation": sys.implementation.name,
                                             "python_version": platform.python_version(),
                                             "sys_platform": sys.platform, "machine": platform.machine()})
        expected = [{"module": name, "size_bytes": len((ROOT / "tools" / name).read_bytes()),
                     "sha256": sha((ROOT / "tools" / name).read_bytes())} for name in SOURCES]
        self.assertEqual(report["tool_sources"], expected)

    def test_report_copies_do_not_alias_each_other_or_future_runs(self):
        self.fixture.job["candidate"] = copy.deepcopy(self.fixture.job["reference"])
        self.fixture.write()
        first = self.run_job()
        first["reference"]["capture_manifest"]["rights"]["value"] = "modified by caller"
        self.assertNotEqual(first["reference"]["capture_manifest"], first["candidate"]["capture_manifest"])
        first["job"]["analysis"]["frequencies_hz"].append(0)
        self.assertEqual(first["policy"]["analysis"]["frequencies_hz"], [1])
        second = self.run_job()
        self.assertEqual(second["reference"]["capture_manifest"], self.fixture.archive.manifests["reference"])
        self.assertEqual(second["job"], self.fixture.job)

    def test_deterministic_relocation_foreign_cwd_and_unicode_root(self):
        first = self.cli()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stderr, b"")
        relocated = self.work / "élève-東京-Ω"
        shutil.copytree(self.fixture.root, relocated)
        result = subprocess.run([sys.executable, "-B", str(TOOL), "--input", str(relocated / "job.json")],
                                cwd=self.work.parent, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")
        self.assertEqual(result.stdout, first.stdout)
        self.assertEqual(result.stdout, encoded(json.loads(result.stdout)))
        self.assertEqual(self.cli().stdout, first.stdout)

    def test_cli_all_report_exits_and_usage_exit(self):
        cases = (("pass", 0, 0.375, VECTORS[1][0]), ("inconclusive", 3, 0.25, VECTORS[1][0]),
                 ("failed", 1, 0.25, VECTORS[2][0]))
        for status, code, bound, candidate in cases:
            fixture = self.fixture_at("cli-" + status, candidate=candidate)
            fixture.policy["criteria"][0]["upper_bound"] = bound
            fixture.write()
            result = self.cli(fixture)
            with self.subTest(status=status):
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(json.loads(result.stdout)["status"], status)
                self.assertEqual(result.stderr, b"")
        result = subprocess.run([sys.executable, "-B", str(TOOL)], cwd=self.work,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"usage", result.stderr.lower())

    def test_cli_help_and_no_implicit_overrides_or_abbreviations(self):
        help_result = self.cli(None, "--help")
        self.assertEqual(help_result.returncode, 0)
        self.assertIn(b"--input", help_result.stdout)
        for flag in ("--sample-rate-hz", "--gain", "--delay", "--role", "--corpus", "--hash", "--out", "--inp"):
            result = self.cli(None, flag, "1")
            with self.subTest(flag=flag):
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b"")

    def test_cli_rejected_input_has_one_contextual_error_no_stdout(self):
        self.fixture.path.write_bytes(b"{}")
        self.assert_error(self.cli())

    def test_output_bytes_match_stdout_for_all_completed_outcomes(self):
        for name, bound, candidate in (("pass", 0.375, VECTORS[1][0]),
                                        ("inconclusive", 0.25, VECTORS[1][0]),
                                        ("failed", 0.25, VECTORS[2][0])):
            fixture = self.fixture_at("publish-" + name, candidate=candidate)
            fixture.policy["criteria"][0]["upper_bound"] = bound
            fixture.write()
            target = self.work / (name + ".json")
            result = self.cli(fixture, "--output", str(target))
            with self.subTest(status=name):
                self.assertEqual(result.stderr, b"")
                self.assertEqual(target.read_bytes(), result.stdout)
                self.assertEqual(json.loads(result.stdout)["status"], name)
                self.assertNotIn(str(target).encode(), result.stdout)

    def test_existing_file_directory_and_symlink_output_preserved(self):
        target = self.work / "existing.json"
        target.write_bytes(b"preserve existing bytes")
        self.assert_error(self.cli(None, "--output", str(target)))
        self.assertEqual(target.read_bytes(), b"preserve existing bytes")
        directory = self.work / "existing-directory"
        directory.mkdir()
        self.assert_error(self.cli(None, "--output", str(directory)))
        self.assertTrue(directory.is_dir())
        if hasattr(os, "symlink"):
            link = self.work / "existing-link"
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError) as error:
                self.skipTest("Symlink creation unavailable: " + str(error))
            self.assert_error(self.cli(None, "--output", str(link)))
            self.assertTrue(link.is_symlink())
            self.assertEqual(target.read_bytes(), b"preserve existing bytes")

    def test_no_output_parent_creation_and_no_report_before_validation(self):
        missing = self.work / "missing" / "report.json"
        self.assert_error(self.cli(None, "--output", str(missing)))
        self.assertFalse(missing.parent.exists())
        target = self.work / "invalid.json"
        self.fixture.path.write_bytes(b"{}")
        self.assert_error(self.cli(None, "--output", str(target)))
        self.assertFalse(target.exists())

    def test_unicode_report_uses_utf8_bytes_independent_of_terminal_encoding(self):
        self.fixture.policy["criteria"][0]["rationale"] = "Prédeclared Ω — 東京 synthetic fixture."
        self.fixture.write()
        result, output, error = self.main(["--input", str(self.fixture.path)])
        self.assertEqual(result, 0, error)
        self.assertEqual(error, "")
        self.assertIn("Prédeclared Ω — 東京".encode("utf-8"), output)
        self.assertEqual(output, encoded(json.loads(output)))

    def test_primary_composition_uses_one_bound_metadata_read_and_one_full_audit(self):
        real_read = capture_corpus._read_confined_bytes
        real_loaded = capture_corpus._load_manifests
        real_audit = capture_corpus._audit_loaded
        real_window = capture_audio.read_audio_window
        reads, loaded_values, audits, windows = {}, [], [], []
        def read(root, parts, **kwargs):
            path = root.joinpath(*parts)
            reads[path] = reads.get(path, 0) + 1
            return real_read(root, parts, **kwargs)
        def load(index, root):
            value = real_loaded(index, root)
            loaded_values.append((index, value))
            return value
        def audit(index, index_hash, root, chosen_root, before_root, loaded, **kwargs):
            self.assertIs(index, loaded_values[0][0])
            self.assertIs(loaded, loaded_values[0][1])
            self.assertEqual(index_hash, sha(self.fixture.archive.path.read_bytes()))
            self.assertEqual(index, self.fixture.archive.index)
            self.assertEqual(kwargs, {"check_files": True, "check_audio": True})
            audits.append(1)
            return real_audit(index, index_hash, root, chosen_root, before_root, loaded, **kwargs)
        def window(path, start, count, **kwargs):
            windows.append((Path(path), start, count))
            return real_window(path, start, count, **kwargs)
        with mock.patch.object(capture_corpus, "_read_confined_bytes", side_effect=read), \
             mock.patch.object(capture_corpus, "_load_manifests", side_effect=load), \
             mock.patch.object(capture_corpus, "_audit_loaded", side_effect=audit), \
             mock.patch.object(capture_audio, "read_audio_window", side_effect=window):
            report = self.run_job()
        self.assertEqual(report["status"], "pass")
        self.assertEqual(len(audits), 1)
        self.assertEqual(len(windows), 2)
        expected = [self.fixture.path, self.fixture.policy_path, self.fixture.archive.path]
        expected.extend(self.fixture.archive.root / e["manifest_path"] for e in self.fixture.archive.entries.values())
        for path in expected:
            self.assertEqual(reads[path], 1, str(path))
        for name in SOURCES:
            self.assertEqual(reads[ROOT / "tools" / name], 1, name)

    def test_changed_index_after_preflight_never_drives_unbound_manifest_or_artifact_work(self):
        real_loaded = capture_corpus._load_manifests
        real_verify = capture_corpus._verify_artifact
        verified = []
        def load(index, root):
            admitted = real_loaded(index, root)
            changed = copy.deepcopy(index)
            for number in range(63):
                entry = copy.deepcopy(changed["captures"][0])
                entry.update(capture_id=f"injected-{number}", manifest_path=f"captures/injected-{number}.json")
                changed["captures"].append(entry)
            self.fixture.archive.path.write_bytes(encoded(changed))
            return admitted
        def verify(root, parts, artifact, seen):
            verified.append(tuple(parts))
            return real_verify(root, parts, artifact, seen)
        with mock.patch.object(capture_corpus, "_load_manifests", side_effect=load) as loads, \
             mock.patch.object(capture_corpus, "_verify_artifact", side_effect=verify):
            with self.assertRaises(subject.JobError):
                self.run_job()
        self.assertEqual(loads.call_count, 1)
        self.assertLessEqual(len(verified), 2)
        self.assertTrue(all("injected" not in "/".join(parts) for parts in verified))

    def test_entire_actual_corpus_and_evaluation_results_are_retained_unchanged(self):
        self.fixture.archive.add("plan", "unassigned", planned=True)
        self.fixture.write()
        real_audit, real_evaluate = capture_corpus._audit_loaded, compare_capture.evaluate_policy
        observed = {}
        def audit(*args, **kwargs):
            result = real_audit(*args, **kwargs)
            observed["corpus"] = copy.deepcopy(result)
            return result
        def evaluate(*args, **kwargs):
            result = real_evaluate(*args, **kwargs)
            observed["evaluation"] = copy.deepcopy(result)
            return result
        with mock.patch.object(capture_corpus, "_audit_loaded", side_effect=audit), \
             mock.patch.object(compare_capture, "evaluate_policy", side_effect=evaluate):
            report = self.run_job()
        # These are retention assertions, not an expected numerical oracle.
        self.assertEqual(report["corpus_report"], observed["corpus"])
        self.assertEqual(report["evaluation"], observed["evaluation"])
        self.assertEqual(report["status"], "inconclusive")

    def test_selected_arrays_reach_comparison_without_transform_or_reordering(self):
        real = compare_capture.compare_signals
        calls = []
        def compare(reference, candidate, rate, **kwargs):
            calls.append((copy.deepcopy(reference), copy.deepcopy(candidate), rate, copy.deepcopy(kwargs)))
            return real(reference, candidate, rate, **kwargs)
        with mock.patch.object(compare_capture, "compare_signals", side_effect=compare):
            self.run_job()
        self.assertEqual(calls, [([VECTORS[0][0]], [VECTORS[1][0]], 4,
                                 {"frequencies_hz": [1], "window": "rectangular", "floor_fs": 1e-12})])

    def test_invalid_job_work_rejects_before_artifact_io(self):
        self.fixture.job["analysis"].update(sample_rate_hz=48000, frame_count=65537, channel_count=16)
        self.fixture.policy["analysis"] = copy.deepcopy(self.fixture.job["analysis"])
        self.fixture.write()
        self.reject_before_artifacts()

    def test_window_full_stream_inspection_must_match_every_corpus_identity_field(self):
        real = capture_audio.read_audio_window
        changes = {"size_bytes": 17, "sha256": "0" * 64, "format": "wav_float32",
                   "sample_rate_hz": 8, "channel_count": 2, "frame_count": 5,
                   "decoded_digest_version": "changed-v1", "decoded_sha256": "f" * 64}
        for field, wrong in changes.items():
            def tamper(*args, **kwargs):
                result = real(*args, **kwargs)
                result["inspection"][field] = wrong
                return result
            with self.subTest(field=field), mock.patch.object(capture_audio, "read_audio_window", side_effect=tamper):
                with self.assertRaises(subject.JobError):
                    self.run_job()

    def test_window_returned_interval_and_sample_geometry_cannot_change(self):
        real = capture_audio.read_audio_window
        changes = {"start_frame": 1, "frame_count": 3, "end_frame": 3,
                   "samples": [[1.0, -1.0, 1.0]]}
        for field, wrong in changes.items():
            def tamper(*args, **kwargs):
                result = real(*args, **kwargs)
                result[field] = wrong
                return result
            with self.subTest(field=field), mock.patch.object(capture_audio, "read_audio_window", side_effect=tamper):
                with self.assertRaises(subject.JobError):
                    self.run_job()

    def test_every_consumed_input_leaf_is_rechecked_after_evaluation(self):
        labels = ("job", "index", "policy", "reference-manifest", "candidate-manifest",
                  "unselected-manifest", "reference-audio", "candidate-audio",
                  "unselected-audio", "unselected-support")
        for label in labels:
            fixture = self.fixture_at("late-" + label)
            fixture.archive.add("unselected", "fit", raw=raw([0.1, 0.2, 0.3, 0.4]),
                                rate=4, format_name="raw_float32_le")
            fixture.archive.file("unselected", "notes", b"Required audit support bytes.", kind="support")
            fixture.write()
            paths = {"job": fixture.path, "index": fixture.archive.path, "policy": fixture.policy_path}
            for ident in ("reference", "candidate", "unselected"):
                paths[ident + "-manifest"] = fixture.archive.root / fixture.archive.entries[ident]["manifest_path"]
                paths[ident + "-audio"] = fixture.archive.file_path(ident, "raw")
            paths["unselected-support"] = fixture.archive.file_path("unselected", "notes")
            real = compare_capture.evaluate_policy
            def mutate(*args, **kwargs):
                result = real(*args, **kwargs)
                path = paths[label]
                path.write_bytes(path.read_bytes() + b" ")
                return result
            with self.subTest(label=label), mock.patch.object(compare_capture, "evaluate_policy", side_effect=mutate) as evaluation:
                with self.assertRaises(subject.JobError):
                    self.run_job(fixture)
                self.assertEqual(evaluation.call_count, 1)

    def test_same_bytes_replacement_of_unselected_artifact_is_rejected(self):
        self.fixture.archive.file("reference", "notes", b"Original bytes.", kind="support")
        self.fixture.write()
        target = self.fixture.archive.file_path("reference", "notes")
        payload = target.read_bytes()
        before = target.stat()
        real = compare_capture.evaluate_policy
        def mutate(*args, **kwargs):
            result = real(*args, **kwargs)
            replacement = target.with_name("replacement")
            replacement.write_bytes(payload)
            os.utime(replacement, ns=(before.st_atime_ns, before.st_mtime_ns))
            os.replace(replacement, target)
            return result
        with mock.patch.object(compare_capture, "evaluate_policy", side_effect=mutate):
            with self.assertRaises(subject.JobError):
                self.run_job()
        self.assertEqual(target.read_bytes(), payload)

    def test_unrelated_sibling_creation_does_not_invalidate_directory_identity(self):
        real = compare_capture.evaluate_policy
        def create_sibling(*args, **kwargs):
            result = real(*args, **kwargs)
            (self.fixture.root / "new-sibling.txt").write_bytes(b"Sibling activity.")
            (self.fixture.archive.root / "captures" / "reference" / "new-sibling.txt").write_bytes(b"Sibling activity.")
            return result
        with mock.patch.object(compare_capture, "evaluate_policy", side_effect=create_sibling):
            report = self.run_job()
        self.assertEqual(report["status"], "pass")

    def test_replaced_confined_parent_rejects_even_when_original_bytes_are_linked_back(self):
        target = self.fixture.archive.file_path("candidate", "raw")
        real = compare_capture.evaluate_policy
        def replace_parent(*args, **kwargs):
            result = real(*args, **kwargs)
            parent = target.parent
            moved = parent.with_name("saved-candidate")
            parent.rename(moved)
            parent.mkdir()
            os.link(moved / target.name, target)
            return result
        with mock.patch.object(compare_capture, "evaluate_policy", side_effect=replace_parent):
            with self.assertRaises(subject.JobError):
                self.run_job()

    def test_all_six_source_files_are_rechecked_after_evaluation(self):
        # Only private temporary copies are changed. The repository sources are
        # never modified by an acceptance test, even temporarily.
        script = r'''
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
import capture_job, compare_capture
real = compare_capture.evaluate_policy
def mutate(*args, **kwargs):
    report = real(*args, **kwargs)
    target = Path(sys.argv[1]) / sys.argv[3]
    target.write_bytes(target.read_bytes() + b"\n# controlled late source mutation\n")
    return report
compare_capture.evaluate_policy = mutate
try:
    capture_job.run_job(sys.argv[2])
except capture_job.JobError as error:
    print(type(error).__name__ + ": " + str(error))
else:
    raise SystemExit("source mutation accepted")
'''
        for name in SOURCES:
            copied = self.work / ("source-" + name)
            copied.mkdir()
            for source in SOURCES:
                shutil.copyfile(ROOT / "tools" / source, copied / source)
            result = subprocess.run([sys.executable, "-B", "-c", script, str(copied), str(self.fixture.path), name],
                                    cwd=self.work, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    timeout=30, check=False)
            with self.subTest(source=name):
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue(result.stdout.startswith(b"JobError:"), result.stdout)
                self.assertEqual(result.stderr, b"")

    def test_source_byte_limit_and_nonregular_source_reject_without_artifacts(self):
        original = capture_audio.__file__
        copied = self.work / "oversized-source"
        copied.mkdir()
        source = copied / "capture_audio.py"
        source.write_bytes(b"#" * 1048577)
        with mock.patch.object(capture_audio, "__file__", str(source)):
            self.reject_before_artifacts()
        source.unlink()
        source.mkdir()
        with mock.patch.object(capture_audio, "__file__", str(source)):
            self.reject_before_artifacts()
        self.assertEqual(capture_audio.__file__, original)

    def test_runtime_identity_allows_empty_machine_and_rejects_bad_values(self):
        with mock.patch.object(platform, "machine", return_value=""):
            self.assertEqual(self.run_job()["runtime"]["machine"], "")
        for value in ("x" * 129, "control\n", "\ud800"):
            with self.subTest(value=repr(value)), mock.patch.object(platform, "machine", return_value=value):
                with self.assertRaises(subject.JobError):
                    self.run_job()
        with mock.patch.object(platform, "python_version", return_value=""):
            with self.assertRaises(subject.JobError):
                self.run_job()

    def test_symlink_job_root_leaf_and_every_confined_descendant_reject(self):
        if not hasattr(os, "symlink"):
            self.skipTest("Symlinks unavailable on this platform.")
        probe = self.work / "probe-link"
        try:
            probe.symlink_to(self.fixture.root, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest("Symlink creation unavailable: " + str(error))
        with self.assertRaises(subject.JobError):
            subject.run_job(probe / "job.json")
        for case in ("job", "policy", "index", "manifest", "artifact", "directory"):
            fixture = self.fixture_at("alias-" + case)
            target = {"job": fixture.path, "policy": fixture.policy_path, "index": fixture.archive.path,
                      "manifest": fixture.archive.root / "captures/reference.json",
                      "artifact": fixture.archive.file_path("reference", "raw"),
                      "directory": fixture.archive.root / "captures"}[case]
            saved = target.with_name(target.name + ".saved")
            target.rename(saved)
            target.symlink_to(saved, target_is_directory=saved.is_dir())
            with self.subTest(case=case), self.assertRaises(subject.JobError):
                self.run_job(fixture)

    def test_ordinary_alias_above_job_parent_remains_admissible(self):
        if not hasattr(os, "symlink"):
            self.skipTest("Symlinks unavailable on this platform.")
        alias = self.work / "ancestor-alias"
        try:
            alias.symlink_to(self.work, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest("Symlink creation unavailable: " + str(error))
        report = subject.run_job(alias / self.fixture.root.name / "job.json")
        self.assertEqual(report, self.run_job())

    def test_nonregular_job_policy_index_manifest_and_artifact_reject(self):
        for case in ("job", "policy", "index", "manifest", "artifact"):
            fixture = self.fixture_at("nonregular-" + case)
            target = {"job": fixture.path, "policy": fixture.policy_path, "index": fixture.archive.path,
                      "manifest": fixture.archive.root / "captures/reference.json",
                      "artifact": fixture.archive.file_path("reference", "raw")}[case]
            target.unlink()
            target.mkdir()
            with self.subTest(case=case), self.assertRaises(subject.JobError):
                self.run_job(fixture)

    def test_fifo_job_rejects_without_waiting_for_a_writer(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("FIFO creation unavailable on this platform.")
        self.fixture.path.unlink()
        try:
            os.mkfifo(self.fixture.path)
        except OSError as error:
            self.skipTest("FIFO creation unavailable: " + str(error))
        self.assert_error(self.cli())

    def test_corpus_hardlink_alias_guard_survives_composition(self):
        payload = self.fixture.archive.file_path("reference", "raw").read_bytes()
        self.fixture.archive.file("reference", "alias", payload, kind="support")
        self.fixture.write()
        alias = self.fixture.archive.file_path("reference", "alias")
        alias.unlink()
        try:
            os.link(self.fixture.archive.file_path("reference", "raw"), alias)
        except OSError as error:
            self.skipTest("Hard links unavailable: " + str(error))
        with self.assertRaises(subject.JobError):
            self.run_job()

    def test_final_report_resource_limits_reject_without_truncating_or_publishing(self):
        real = compare_capture.evaluate_policy
        def deeply_nested():
            value = []
            for _ in range(34):
                value = [value]
            return value
        cases = {"bytes": lambda: "x" * 16777216,
                 "nodes": lambda: [None] * 1048576,
                 "depth": deeply_nested,
                 "number": lambda: 4000000000000000001}
        for label, make in cases.items():
            def exceed(*args, **kwargs):
                report = real(*args, **kwargs)
                report["controlled_dependency_excess"] = make()
                return report
            target = self.work / ("excess-" + label + ".json")
            with self.subTest(bound=label), mock.patch.object(compare_capture, "evaluate_policy", side_effect=exceed):
                code, output, error = self.main(["--input", str(self.fixture.path), "--output", str(target)])
                self.assertEqual(code, 1)
                self.assertEqual(output, b"")
                self.assertTrue(error.startswith("job error:"), error)
                self.assertFalse(target.exists())

    def test_returned_graph_edge_ceiling_is_checked_without_truncation(self):
        real = capture_corpus._audit_loaded
        def exceed(*args, **kwargs):
            report = real(*args, **kwargs)
            report["edges"] = [{} for _ in range(4097)]
            return report
        with mock.patch.object(capture_corpus, "_audit_loaded", side_effect=exceed):
            with self.assertRaises(subject.JobError):
                self.run_job()

    def test_mismatching_evaluator_policy_hash_is_rejected(self):
        real = compare_capture.evaluate_policy
        def change_hash(*args, **kwargs):
            report = real(*args, **kwargs)
            report["policy_sha256"] = "0" * 64
            return report
        with mock.patch.object(compare_capture, "evaluate_policy", side_effect=change_hash):
            with self.assertRaises(subject.JobError):
                self.run_job()

    def test_raced_output_destination_is_preserved_and_stdout_remains_empty(self):
        target = self.work / "raced.json"
        real = os.link
        def race(source, destination, *args, **kwargs):
            if Path(destination) == target:
                target.write_bytes(b"concurrent winner")
            return real(source, destination, *args, **kwargs)
        with mock.patch.object(os, "link", side_effect=race):
            code, output, error = self.main(["--input", str(self.fixture.path), "--output", str(target)])
        self.assertEqual(code, 1)
        self.assertEqual(output, b"")
        self.assertTrue(error.startswith("job error:"), error)
        self.assertEqual(target.read_bytes(), b"concurrent winner")
        self.assertEqual(list(self.work.glob(".capture-json-*")), [])

    def test_completed_publication_cleanup_failure_is_disclosed_and_preserved(self):
        target = self.work / "published-before-cleanup.json"
        real = Path.unlink
        def fail_temporary(path, *args, **kwargs):
            if path.name.startswith(".capture-json-"):
                raise OSError("controlled temporary cleanup failure")
            return real(path, *args, **kwargs)
        with mock.patch.object(Path, "unlink", fail_temporary):
            code, output, error = self.main(["--input", str(self.fixture.path), "--output", str(target)])
        self.assertEqual(code, 1)
        self.assertEqual(output, b"")
        self.assertIn("published", error)
        self.assertIn("remains complete", error)
        self.assertIn("cleanup", error)
        self.assertEqual(json.loads(target.read_bytes())["status"], "pass")
        self.assertEqual(target.read_bytes(), encoded(json.loads(target.read_bytes())))

    def test_primary_publication_and_cleanup_failures_keep_both_contexts(self):
        target = self.work / "failed-publication.json"
        real = Path.unlink
        def cleanup_failure(path, *args, **kwargs):
            if path.name.startswith(".capture-json-"):
                raise OSError("secondary-cleanup-marker")
            return real(path, *args, **kwargs)
        with mock.patch.object(os, "link", side_effect=OSError("primary-publication-marker")), \
             mock.patch.object(Path, "unlink", cleanup_failure):
            code, output, error = self.main(["--input", str(self.fixture.path), "--output", str(target)])
        self.assertEqual(code, 1)
        self.assertEqual(output, b"")
        self.assertIn("primary-publication-marker", error)
        self.assertIn("secondary-cleanup-marker", error)
        self.assertFalse(target.exists())

    def test_stdout_failure_after_publication_keeps_complete_file_and_returns_failure(self):
        class BrokenBuffer:
            def write(self, payload):
                raise OSError("controlled stdout I/O failure")
            def flush(self):
                return None
        class BrokenStdout:
            buffer = BrokenBuffer()
        target = self.work / "published-before-stdout.json"
        error = io.StringIO()
        with mock.patch.object(sys, "stdout", BrokenStdout()), mock.patch.object(sys, "stderr", error):
            code = subject.main(["--input", str(self.fixture.path), "--output", str(target)])
        self.assertEqual(code, 1)
        self.assertIn("controlled stdout I/O failure", error.getvalue())
        self.assertEqual(json.loads(target.read_bytes())["status"], "pass")

    def test_short_stdout_write_is_not_success(self):
        class ShortBuffer:
            def write(self, payload):
                return len(payload) - 1
            def flush(self):
                return None
        class ShortStdout:
            buffer = ShortBuffer()
        error = io.StringIO()
        with mock.patch.object(sys, "stdout", ShortStdout()), mock.patch.object(sys, "stderr", error):
            code = subject.main(["--input", str(self.fixture.path)])
        self.assertEqual(code, 1)
        self.assertIn("stdout", error.getvalue())

    def test_cancellation_propagates_without_output_or_publication(self):
        target = self.work / "cancelled.json"
        with mock.patch.object(compare_capture, "evaluate_policy", side_effect=KeyboardInterrupt("controlled cancellation")):
            with self.assertRaises(KeyboardInterrupt):
                self.main(["--input", str(self.fixture.path), "--output", str(target)])
        self.assertFalse(target.exists())

    def test_all_nine_whole_corpus_and_numerical_outcome_combinations(self):
        for corpus_status in ("pass", "failed", "inconclusive"):
            for numerical in ("pass", "fail", "inconclusive"):
                fixture = self.fixture_at("outcome-" + corpus_status + "-" + numerical,
                                          candidate=VECTORS[2 if numerical == "fail" else 1][0])
                fixture.policy["criteria"][0]["upper_bound"] = 0.375 if numerical == "pass" else 0.25
                if corpus_status == "failed":
                    fixture.archive.add("leak", "fit", raw=raw(VECTORS[0][0]), rate=4,
                                        format_name="raw_float32_le")
                elif corpus_status == "inconclusive":
                    fixture.archive.add("plan", "unassigned", planned=True)
                fixture.write()
                report = self.run_job(fixture)
                expected = ("failed" if corpus_status == "failed" or numerical == "fail" else
                            "inconclusive" if "inconclusive" in (corpus_status, numerical) else "pass")
                with self.subTest(corpus=corpus_status, numerical=numerical):
                    self.assertEqual(report["status"], expected)
                    self.assertEqual(report["corpus_report"]["status"], corpus_status)
                    self.assertEqual(report["evaluation"]["numerical_verdict"], numerical)

    def test_selection_inspections_remove_only_machine_input_path(self):
        real = capture_audio.read_audio_window
        observations = []
        def observe(*args, **kwargs):
            result = real(*args, **kwargs)
            observations.append(copy.deepcopy(result["inspection"]))
            return result
        with mock.patch.object(capture_audio, "read_audio_window", side_effect=observe):
            report = self.run_job()
        self.assertEqual(len(observations), 2)
        for side, inspection in zip(("reference", "candidate"), observations):
            del inspection["input_path"]
            self.assertEqual(report[side]["inspection"], inspection)

    def test_descriptor_failure_and_cancellation_release_actual_open_files(self):
        directory = Path("/proc/self/fd")
        if not directory.is_dir():
            self.skipTest("Actual descriptor inventory requires Linux /proc/self/fd.")
        real = os.fstat
        for exception in (OSError("controlled descriptor failure"), KeyboardInterrupt("controlled descriptor cancellation")):
            before = set(directory.iterdir())
            raised = []
            def fail_regular(fd):
                info = real(fd)
                if not raised and stat.S_ISREG(info.st_mode):
                    raised.append(fd)
                    raise exception
                return info
            expected = subject.JobError if isinstance(exception, OSError) else KeyboardInterrupt
            with self.subTest(exception=type(exception).__name__), mock.patch.object(os, "fstat", side_effect=fail_regular):
                with self.assertRaises(expected):
                    self.run_job()
            self.assertEqual(len(raised), 1)
            self.assertEqual(set(directory.iterdir()), before)


if __name__ == "__main__":
    unittest.main()
