#!/usr/bin/env python3
"""Independent acceptance of the frozen capture-demo-v1 archive contract.

Literal vectors, digests, geometry, intervals, statuses and expected layout are
from CAPTURE_DEMO.md and job contract section 8. The generator is not their
oracle. JSON formatting is checked with the standard library's documented
serialization rule; no production serializer or test fixture builder is reused.
"""

from __future__ import annotations

import ast
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import capture_corpus
import capture_job
import capture_study
import make_capture_demo as subject
import validate_capture


TOOL = ROOT / "tools" / "make_capture_demo.py"
RETAINED = ROOT / "examples" / "capture-demo"
VECTORS = {
    "reference": (
        [1.0, -1.0, 1.0, -1.0], "0000803f000080bf0000803f000080bf",
        "fd801740524b1e1c23a61b5400725b76428652827ba1261b83243eb5ce551402",
        "786665f3cf05b2f9b33e7cadee75e7176e122d62ad82133c72737c76261dd440"),
    "quarter": (
        [1.25, -0.75, 1.25, -0.75], "0000a03f000040bf0000a03f000040bf",
        "bac1c395abe23908b8c106a28b6c151bc25b9473d470f4d942775b5dfdf523e2",
        "79d8014af588d583abcc570598d3e073413543ef518b339cbca37dbb5eb6bd0c"),
    "half": (
        [1.5, -0.5, 1.5, -0.5], "0000c03f000000bf0000c03f000000bf",
        "36d231b4ecc15924aea04f08725924f18ae4346fd287747791d7396eca3d5758",
        "52c3450c9c276f60b8ed6dc728977cfe33b4b0702ce8332927169d25f18e4db8"),
}
OUTCOMES = (
    ("pass", "quarter", 0.25, 0.375, 0.125, 0.375, "pass", 0),
    ("inconclusive", "quarter", 0.25, 0.25, 0.125, 0.375, "inconclusive", 3),
    ("fail", "half", 0.5, 0.25, 0.375, 0.625, "failed", 1),
)
ANALYSIS = {"sample_rate_hz": 4, "channel_count": 1, "frame_count": 4,
            "frequencies_hz": [1], "window": "rectangular", "floor_fs": 1e-12}
PATHS = tuple(sorted([
    "README.md", "EXPECTED.json", "study.json", "corpus/corpus.json",
    *[f"corpus/{name}.json" for name in VECTORS],
    *[f"corpus/audio/{name}.f32" for name in VECTORS],
    *[f"job-{name}.json" for name, *_ in OUTCOMES],
    *[f"policy-{name}.json" for name, *_ in OUTCOMES],
]))
CLAIMS = ("boundary_equivalence", "synchronization", "authenticity",
          "specimen_identity", "calibration", "permissions", "independence",
          "preregistration", "final_holdout_history", "physical_fidelity")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


def read_value(path):
    return json.loads(Path(path).read_bytes())


def archive_bytes(path):
    return {item.relative_to(path).as_posix(): item.read_bytes()
            for item in Path(path).rglob("*") if item.is_file()}


def inventory_from_bytes(files):
    return {
        "schema_version": 1,
        "contract_origin": "project-proposed-capture-demo-v1",
        "evidence_class": "synthetic_numerical_fixture",
        "execution": "not_run",
        "file_count": 16,
        "total_size_bytes": sum(len(data) for data in files.values()),
        "files": [{"path": path, "size_bytes": len(files[path]),
                   "sha256": sha(files[path])} for path in sorted(files)],
        "physical_fidelity": "not_established",
        "permissions": "not_established",
    }


class DemoAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained_before = archive_bytes(RETAINED)

    @classmethod
    def tearDownClass(cls):
        if archive_bytes(RETAINED) != cls.retained_before:
            raise AssertionError("independent demo acceptance changed retained inputs")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="capture-demo-acceptance-")
        self.addCleanup(self.temp.cleanup)
        # Resolve ordinary native temp aliases before fault-hook path matching.
        self.root = Path(self.temp.name).resolve(strict=True)

    def create(self, name="demo"):
        path = self.root / name
        return path, subject.build_demo(path)

    def invoke(self, args, *, cwd=None, ascii_terminal=False):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        if ascii_terminal:
            env["PYTHONIOENCODING"] = "ascii:strict"
        return subprocess.run([sys.executable, "-B", str(TOOL), *args],
                              cwd=cwd or self.root, env=env,
                              capture_output=True, check=False)

    def assert_claims(self, report):
        for key in CLAIMS:
            self.assertEqual(report[key], "not_established", key)

    def make_symlink(self, destination, target, *, directory=False):
        try:
            destination.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"native symlink creation unavailable: {exc}")

    def test_literal_oracles_recomputed_independently(self):
        for name, (samples, hexadecimal, raw_digest, decoded_digest) in VECTORS.items():
            with self.subTest(name=name):
                raw = struct.pack("<4f", *samples)
                self.assertEqual(raw.hex(), hexadecimal)
                self.assertEqual(sha(raw), raw_digest)
                preimage = (b"HAMMOND-CAPTURE-DECODED-V1\0"
                            + struct.pack("<IIQ", 4, 1, 4)
                            + struct.pack("<4d", *samples))
                self.assertEqual(sha(preimage), decoded_digest)
        reference = VECTORS["reference"][0]
        for _, candidate, error, bound, lower, upper, status, _ in OUTCOMES:
            differences = [b - a for a, b in zip(reference, VECTORS[candidate][0])]
            self.assertEqual(differences, [error] * 4)
            self.assertEqual(sum(differences) / 4, error)
            self.assertEqual((sum(x * x for x in differences) / 4) ** 0.5, error)
            self.assertEqual((max(0, error - 0.125), error + 0.125), (lower, upper))
            decision = "pass" if upper <= bound else "failed" if lower > bound else "inconclusive"
            self.assertEqual(decision, status)

    def test_exact_archive_layout_and_independent_inventory(self):
        path, report = self.create()
        files = archive_bytes(path)
        self.assertEqual(tuple(sorted(files)), PATHS)
        self.assertEqual(len(files), 16)
        directories = sorted(p.relative_to(path).as_posix()
                             for p in path.rglob("*") if p.is_dir())
        self.assertEqual(directories, ["corpus", "corpus/audio"])
        self.assertFalse(any(p.is_symlink() for p in path.rglob("*")))
        self.assertEqual(report, inventory_from_bytes(files))
        self.assertTrue(all(type(row["size_bytes"]) is int for row in report["files"]))
        self.assertIs(type(report["schema_version"]), int)

    def test_regeneration_relocation_and_retained_archive_equal(self):
        first, report = self.create("first")
        second, repeated = self.create("relocated_é_音")
        self.assertEqual(archive_bytes(first), archive_bytes(second))
        self.assertEqual(report, repeated)
        self.assertEqual(archive_bytes(first), self.retained_before)
        self.assertEqual(archive_bytes(RETAINED), self.retained_before)

    def test_inventory_has_no_execution_or_machine_observations(self):
        _, report = self.create()
        self.assertEqual(set(report), {"schema_version", "contract_origin", "evidence_class",
                                      "execution", "file_count", "total_size_bytes", "files",
                                      "physical_fidelity", "permissions"})
        self.assertEqual(report["execution"], "not_run")
        self.assertEqual(report["evidence_class"], "synthetic_numerical_fixture")
        self.assertEqual(report["physical_fidelity"], "not_established")
        self.assertEqual(report["permissions"], "not_established")
        self.assertNotIn(str(self.root), json.dumps(report))

    def test_inventory_is_fresh_not_mutable_generator_state(self):
        _, first = self.create("first")
        expected = json.loads(encode(first))
        first["files"][0]["sha256"] = "not-a-digest"
        first["file_count"] = -1
        _, second = self.create("second")
        self.assertEqual(second, expected)

    def test_text_files_are_canonical_utf8_lf(self):
        path, _ = self.create()
        for name, payload in archive_bytes(path).items():
            if name.endswith(".f32"):
                continue
            with self.subTest(path=name):
                text = payload.decode("utf-8")
                self.assertTrue(text.endswith("\n"))
                self.assertFalse(text.endswith("\n\n"))
                self.assertNotIn(b"\r", payload)
                if name.endswith(".json"):
                    self.assertEqual(payload, encode(json.loads(payload)))

    def test_raw_files_match_literal_bytes_and_geometry(self):
        path, _ = self.create()
        for name, (samples, hexadecimal, raw_digest, _) in VECTORS.items():
            with self.subTest(name=name):
                payload = (path / "corpus" / "audio" / f"{name}.f32").read_bytes()
                self.assertEqual(payload, bytes.fromhex(hexadecimal))
                self.assertEqual(len(payload), 16)
                self.assertEqual(list(struct.unpack("<4f", payload)), samples)
                self.assertEqual(sha(payload), raw_digest)

    def test_expectation_vectors_are_exact_literal_oracles(self):
        path, _ = self.create()
        expected = read_value(path / "EXPECTED.json")
        vectors = expected["vectors"]
        self.assertEqual([x["capture_id"] for x in vectors], list(VECTORS))
        for row in vectors:
            samples, hexadecimal, raw_digest, decoded_digest = VECTORS[row["capture_id"]]
            self.assertEqual(row, {"capture_id": row["capture_id"], "samples": samples,
                                  "raw_hex": hexadecimal, "raw_size_bytes": 16,
                                  "raw_sha256": raw_digest,
                                  "decoded_digest_version": "hammond-capture-decoded-v1",
                                  "decoded_sha256": decoded_digest})
        self.assertEqual(expected["execution"], "not_run")
        self.assertEqual(expected["analysis"], ANALYSIS)
        for key in ("physical_fidelity", "permissions", "independence", "preregistration"):
            self.assertEqual(expected[key], "not_established")

    def test_expectation_outcomes_preserve_failure_and_inconclusion(self):
        path, _ = self.create()
        expected = read_value(path / "EXPECTED.json")
        self.assertEqual(len(expected["jobs"]), 3)
        for row, (name, candidate, error, bound, lower, upper, status, exit_code) in zip(expected["jobs"], OUTCOMES):
            with self.subTest(name=name):
                self.assertEqual(row["job_id"], "demo-" + name)
                self.assertEqual(row["path"], f"job-{name}.json")
                self.assertEqual(row["candidate_capture_id"], candidate)
                self.assertEqual(row["expected_status"], status)
                self.assertEqual(row["expected_exit"], exit_code)
                self.assertEqual(row["pointwise_values_fs"], {
                    "absolute_dc_bias_fs": error, "dc_bias_fs": error,
                    "max_abs_error_fs": error, "rms_error_fs": error})
                self.assertEqual(row["criterion"], {
                    "metric": "rms_error_fs", "margin_fs": 0.125, "upper_bound_fs": bound,
                    "interval_fs": {"lower": lower, "upper": upper},
                    "numerical_verdict": "fail" if status == "failed" else status})
        self.assertEqual(expected["study"]["counts"],
                         {"jobs": 3, "pass": 1, "inconclusive": 1, "failed": 1})
        self.assertEqual(expected["study"]["expected_status"], "failed")
        self.assertEqual(expected["study"]["expected_exit"], 1)
        self.assertEqual(expected["study"]["work"], {"window_samples": 12, "spectral_terms": 12})

    def test_recorded_manifests_are_valid_explicitly_synthetic(self):
        path, _ = self.create()
        for name in VECTORS:
            with self.subTest(name=name):
                manifest = read_value(path / "corpus" / f"{name}.json")
                self.assertIsNone(validate_capture.validate_capture(manifest))
                self.assertEqual(manifest["capture_id"], name)
                self.assertEqual(manifest["status"], "recorded")
                self.assertEqual(manifest["capture_kind"], "synthetic")
                self.assertEqual(manifest["digital"]["format"]["value"], "raw_float32_le")
                self.assertEqual(manifest["digital"]["sample_rate_hz"]["value"], 4)
                self.assertEqual(manifest["digital"]["channel_count"]["value"], 1)
                self.assertEqual(manifest["files"], [{
                    "file_id": "raw", "kind": "raw", "path": f"audio/{name}.f32",
                    "size_bytes": 16, "sha256": VECTORS[name][2],
                    "parents": [], "derivation": None}])
                self.assertEqual(manifest["partition"]["role"], "held_out")
                self.assertEqual(manifest["partition"]["group_id"]["value"], "synthetic-demo-related")
                self.assertEqual(manifest["acquisition"]["session_id"]["value"], "synthetic-demo-session")
                self.assertEqual(manifest["acquisition"]["started_at_utc"]["value"], "2000-01-01T00:00:00Z")

    def test_constructed_metadata_discloses_missing_physical_rights_evidence(self):
        path, _ = self.create()
        for name in VECTORS:
            with self.subTest(name=name):
                manifest = read_value(path / "corpus" / f"{name}.json")
                self.assertIsNone(manifest["specimen"]["specimen_id"]["value"])
                self.assertTrue(manifest["specimen"]["specimen_id"]["unknown_reason"])
                self.assertIsNone(manifest["rights"]["value"])
                self.assertTrue(manifest["rights"]["unknown_reason"])
                self.assertEqual(manifest["physical_clock"]["status"], "not_applicable")
                self.assertTrue(manifest["physical_clock"]["unknown_reason"])
                channel = manifest["digital"]["channels"][0]
                self.assertEqual(channel["boundary"]["value"], "synthetic")
                self.assertEqual(channel["calibration"]["status"], "not_applicable")
                self.assertTrue(channel["calibration"]["unknown_reason"])
                disclosure = manifest["stimulus"]["conditions"]["value"].lower()
                for text in ("2000-01-01t00:00:00z", "constructed", "not observed", "rights"):
                    self.assertIn(text, disclosure)
                self.assertIn("constructed", manifest["specimen"]["identity_evidence"]["value"].lower())

    def test_corpus_references_bind_original_manifest_bytes(self):
        path, _ = self.create()
        corpus = read_value(path / "corpus" / "corpus.json")
        self.assertEqual(corpus["corpus_id"], "synthetic-offset-corpus")
        self.assertEqual([x["capture_id"] for x in corpus["captures"]], list(VECTORS))
        for item in corpus["captures"]:
            self.assertEqual(item["purpose"], "validation")
            self.assertEqual(item["manifest_path"], item["capture_id"] + ".json")
            self.assertEqual(item["manifest_sha256"], sha((path / "corpus" / item["manifest_path"]).read_bytes()))
            self.assertEqual(item["derived_audio"], [])
            self.assertEqual(item["parent_capture_ids"], [])
            self.assertEqual(item["relation_labels"], [{"kind": "family", "label": "literal-offsets"}])

    def test_jobs_and_policies_bind_exact_inputs_and_frozen_intervals(self):
        path, _ = self.create()
        corpus_sha = sha((path / "corpus" / "corpus.json").read_bytes())
        for name, candidate, _, bound, _, _, _, _ in OUTCOMES:
            job = read_value(path / f"job-{name}.json")
            policy_path = path / f"policy-{name}.json"
            policy = read_value(policy_path)
            self.assertEqual(job["job_id"], "demo-" + name)
            self.assertEqual(job["corpus"], {"path": "corpus/corpus.json", "sha256": corpus_sha})
            self.assertEqual(job["policy"], {"path": f"policy-{name}.json", "sha256": sha(policy_path.read_bytes())})
            self.assertEqual(job["reference"], {"capture_id": "reference", "file_id": "raw", "start_frame": 0})
            self.assertEqual(job["candidate"], {"capture_id": candidate, "file_id": "raw", "start_frame": 0})
            self.assertEqual(job["analysis"], ANALYSIS)
            self.assertEqual((job["pairing"], job["transform"]), ("index", "none"))
            self.assertEqual(policy["analysis"], ANALYSIS)
            self.assertEqual(policy["evaluation_role"], "validation")
            self.assertEqual(policy["evidence_class"], "synthetic_numerical_fixture")
            self.assertIsNone(policy["freeze_evidence"]["value"])
            self.assertTrue(policy["freeze_evidence"]["unknown_reason"])
            self.assertEqual(len(policy["criteria"]), 1)
            criterion = policy["criteria"][0]
            self.assertEqual(criterion["target"], {"channel_index": 0, "frequency_hz": None, "metric": "rms_error_fs"})
            self.assertEqual(criterion["upper_bound"], bound)
            self.assertEqual(criterion["uncertainty"]["margin"], 0.125)
            self.assertEqual(criterion["uncertainty"]["basis"], "synthetic_numerical")
            self.assertEqual(criterion["unit"], "FS")

    def test_study_binds_all_original_jobs_in_declared_order(self):
        path, _ = self.create()
        study = read_value(path / "study.json")
        self.assertEqual(study["study_id"], "synthetic-offset-demo")
        self.assertEqual(study["corpus_sha256"], sha((path / "corpus" / "corpus.json").read_bytes()))
        self.assertEqual(study["jobs"], [
            {"job_id": "demo-" + name, "path": f"job-{name}.json",
             "sha256": sha((path / f"job-{name}.json").read_bytes())}
            for name, *_ in OUTCOMES])

    def test_actual_corpus_reads_all_three_streams_one_related_group(self):
        path, _ = self.create()
        report = capture_corpus.audit_corpus(path / "corpus" / "corpus.json", check_files=True, check_audio=True)
        self.assertEqual((report["status"], report["mode"]), ("pass", "files_and_audio_checked"))
        self.assertEqual((report["file_check"], report["audio_check"]), ("verified", "verified"))
        self.assertEqual(len(report["groups"]), 1)
        self.assertEqual(report["groups"][0]["capture_ids"], sorted(VECTORS))
        self.assertEqual(report["groups"][0]["purposes"], ["validation"])
        self.assertEqual(len(report["captures"]), 3)
        for item in report["captures"]:
            artifact = item["files"][0]
            self.assertEqual(artifact["observed_sha256"], VECTORS[item["capture_id"]][2])
            self.assertEqual(artifact["audio_status"], "verified")
            self.assertEqual(artifact["observed_audio"], {
                "format": "raw_float32_le", "sample_rate_hz": 4, "channel_count": 1,
                "frame_count": 4, "decoded_digest_version": "hammond-capture-decoded-v1",
                "decoded_sha256": VECTORS[item["capture_id"]][3]})
        self.assertEqual(report["physical_fidelity"], "not_established")

    def test_actual_jobs_match_literal_values_intervals_and_statuses(self):
        path, _ = self.create()
        for name, _, error, bound, lower, upper, status, _ in OUTCOMES:
            with self.subTest(name=name):
                report = capture_job.run_job(path / f"job-{name}.json")
                self.assertEqual(report["status"], status)
                self.assert_claims(report)
                self.assertEqual(report["corpus_report"]["status"], "pass")
                evaluation = report["evaluation"]
                self.assertEqual(evaluation["numerical_verdict"], "fail" if status == "failed" else status)
                metrics = evaluation["comparison"]["channels"][0]["metrics"]
                for metric in ("dc_bias_fs", "absolute_dc_bias_fs", "max_abs_error_fs", "rms_error_fs"):
                    self.assertEqual(metrics[metric], {"value": error, "unit": "FS", "undefined_reason": None})
                criterion = evaluation["criteria"][0]
                self.assertEqual(criterion["upper_bound"], bound)
                self.assertEqual(criterion["interval"], {"lower": lower, "upper": upper, "unit": "FS", "undefined_reason": None})

    def test_actual_study_preserves_complete_job_reports(self):
        path, _ = self.create()
        expected_jobs = [capture_job.run_job(path / f"job-{name}.json") for name, *_ in OUTCOMES]
        report = capture_study.run_study(path / "study.json")
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["summary"], {
            "jobs": 3, "pass": 1, "failed": 1, "inconclusive": 1,
            "roles": {"fit": 0, "validation": 3, "final_test": 0, "unassigned": 0}})
        self.assertEqual(report["work"], {"window_samples": 12, "spectral_terms": 12})
        self.assertEqual([row["job_id"] for row in report["jobs"]], ["demo-" + row[0] for row in OUTCOMES])
        self.assertEqual([row["report"] for row in report["jobs"]], expected_jobs)
        self.assert_claims(report)
        for row in report["jobs"]:
            self.assert_claims(row["report"])

    def test_actual_study_is_relocation_invariant_and_does_not_modify_archive(self):
        first, _ = self.create("original")
        initial = archive_bytes(first)
        first_report = capture_study.run_study(first / "study.json")
        second = self.root / "moved_音"
        shutil.move(str(first), str(second))
        moved_report = capture_study.run_study(second / "study.json")
        self.assertEqual(first_report, moved_report)
        self.assertEqual(archive_bytes(second), initial)

    def test_readme_explains_outcomes_placeholders_and_later_gates(self):
        path, _ = self.create()
        text = (path / "README.md").read_text(encoding="utf-8")
        for item in ("2000-01-01T00:00:00Z", "constructed", "Rights remain unknown",
                     "not_run", "inconclusive", "failed", "0, 0, 3, 1, 1",
                     "Physical captures", "not_established", "partial"):
            self.assertIn(item, text)

    def test_rejects_wrong_output_types_without_creation(self):
        class StringSubclass(str):
            pass

        class ArbitraryPath:
            def __fspath__(self):
                return str(self.root / "wrong")

        for value in (None, b"bytes", 1, True, [], {}, "", StringSubclass(str(self.root / "subclass")), ArbitraryPath()):
            with self.subTest(type=type(value).__name__):
                with self.assertRaises(subject.DemoError):
                    subject.build_demo(value)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_missing_parent_is_not_created(self):
        missing = self.root / "missing"
        with self.assertRaises(subject.DemoError):
            subject.build_demo(missing / "nested" / "demo")
        self.assertFalse(missing.exists())

    def test_existing_directory_and_contents_are_preserved(self):
        path = self.root / "existing"
        path.mkdir()
        (path / "owner.txt").write_bytes(b"owner content\n")
        before = archive_bytes(path)
        with self.assertRaises(subject.DemoError):
            subject.build_demo(path)
        self.assertEqual(archive_bytes(path), before)

    def test_existing_file_is_preserved(self):
        path = self.root / "existing"
        path.write_bytes(b"owner file\0\xff")
        with self.assertRaises(subject.DemoError):
            subject.build_demo(path)
        self.assertEqual(path.read_bytes(), b"owner file\0\xff")

    def test_existing_dangling_symlink_is_preserved(self):
        path = self.root / "dangling"
        missing = self.root / "absent-target"
        self.make_symlink(path, missing)
        # Windows may return an extended-length target spelling from readlink.
        # Preservation compares the actual link with its own initial value.
        before_target = path.readlink()
        before_stat = path.lstat()
        with self.assertRaises(subject.DemoError):
            subject.build_demo(path)
        self.assertTrue(path.is_symlink())
        self.assertEqual(path.readlink(), before_target)
        after_stat = path.lstat()
        fields = ("st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns")
        self.assertEqual(tuple(getattr(after_stat, key) for key in fields),
                         tuple(getattr(before_stat, key) for key in fields))
        self.assertFalse(missing.exists())

    def test_existing_directory_symlink_does_not_modify_target(self):
        target = self.root / "target"
        target.mkdir()
        (target / "owner.txt").write_bytes(b"preserve")
        alias = self.root / "alias"
        self.make_symlink(alias, target, directory=True)
        with self.assertRaises(subject.DemoError):
            subject.build_demo(alias)
        self.assertTrue(alias.is_symlink())
        self.assertEqual(archive_bytes(target), {"owner.txt": b"preserve"})

    def test_alias_ancestor_is_allowed(self):
        target = self.root / "target"
        target.mkdir()
        alias = self.root / "alias"
        self.make_symlink(alias, target, directory=True)
        report = subject.build_demo(alias / "demo")
        self.assertEqual(report, inventory_from_bytes(archive_bytes(target / "demo")))
        self.assertEqual(archive_bytes(target / "demo"), self.retained_before)

    def test_late_creation_failure_retains_partial_and_other_writer_content(self):
        destination = self.root / "demo"
        real_open = Path.open
        reached = []

        def reject_readme(path, mode="r", *args, **kwargs):
            if path == destination / "README.md" and mode == "xb":
                reached.append(path)
                with real_open(destination / "other-writer.txt", "xb") as stream:
                    stream.write(b"preserve unrelated writer")
                raise OSError("controlled later file creation failure")
            return real_open(path, mode, *args, **kwargs)

        with mock.patch.object(Path, "open", reject_readme):
            with self.assertRaises(subject.DemoError) as caught:
                subject.build_demo(destination)
        self.assertEqual(reached, [destination / "README.md"])
        self.assertIn("partial new demo creation retained", str(caught.exception))
        self.assertIn(str(destination), str(caught.exception))
        self.assertEqual((destination / "EXPECTED.json").read_bytes(), self.retained_before["EXPECTED.json"])
        self.assertEqual((destination / "other-writer.txt").read_bytes(), b"preserve unrelated writer")
        self.assertTrue((destination / "corpus" / "audio").is_dir())

    def test_raced_file_is_exclusively_preserved(self):
        destination = self.root / "demo"
        real_open = Path.open
        reached = []

        def race_readme(path, mode="r", *args, **kwargs):
            if path == destination / "README.md" and mode == "xb":
                reached.append(path)
                with real_open(path, "xb") as stream:
                    stream.write(b"racing owner README")
            return real_open(path, mode, *args, **kwargs)

        with mock.patch.object(Path, "open", race_readme):
            with self.assertRaises(subject.DemoError) as caught:
                subject.build_demo(destination)
        self.assertEqual(reached, [destination / "README.md"])
        self.assertIn("partial new demo creation retained", str(caught.exception))
        self.assertEqual((destination / "README.md").read_bytes(), b"racing owner README")
        self.assertEqual((destination / "EXPECTED.json").read_bytes(), self.retained_before["EXPECTED.json"])

    def test_cancellation_propagates_and_retains_created_directory(self):
        destination = self.root / "demo"
        real_open = Path.open
        reached = []

        def cancel_readme(path, mode="r", *args, **kwargs):
            if path == destination / "README.md" and mode == "xb":
                reached.append(path)
                raise KeyboardInterrupt("controlled cancellation")
            return real_open(path, mode, *args, **kwargs)

        with mock.patch.object(Path, "open", cancel_readme):
            with self.assertRaises(KeyboardInterrupt):
                subject.build_demo(destination)
        self.assertEqual(reached, [destination / "README.md"])
        self.assertEqual((destination / "EXPECTED.json").read_bytes(), self.retained_before["EXPECTED.json"])
        self.assertTrue((destination / "corpus" / "audio").is_dir())

    def test_incomplete_file_write_rejects_and_retains_partial_bytes(self):
        destination = self.root / "demo"
        real_open = Path.open
        reached = []

        class ShortStream:
            def __init__(self, stream):
                self.stream = stream

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return self.stream.__exit__(*args)

            def write(self, payload):
                return self.stream.write(payload[:7])

        def short_open(path, mode="r", *args, **kwargs):
            stream = real_open(path, mode, *args, **kwargs)
            if path == destination / "EXPECTED.json" and mode == "xb":
                reached.append(path)
                return ShortStream(stream)
            return stream

        with mock.patch.object(Path, "open", short_open):
            with self.assertRaises(subject.DemoError) as caught:
                subject.build_demo(destination)
        self.assertEqual(reached, [destination / "EXPECTED.json"])
        self.assertIn("partial new demo creation retained", str(caught.exception))
        self.assertIn("incomplete write", str(caught.exception))
        self.assertEqual((destination / "EXPECTED.json").read_bytes(), self.retained_before["EXPECTED.json"][:7])

    def test_root_creation_race_preserves_other_owner(self):
        destination = self.root / "demo"
        real_mkdir = Path.mkdir
        reached = []

        def race_mkdir(path, *args, **kwargs):
            if path == destination:
                reached.append(path)
                real_mkdir(path)
                (path / "owner.txt").write_bytes(b"other owner")
            return real_mkdir(path, *args, **kwargs)

        with mock.patch.object(Path, "mkdir", race_mkdir):
            with self.assertRaises(subject.DemoError):
                subject.build_demo(destination)
        self.assertEqual(reached, [destination])
        self.assertEqual(archive_bytes(destination), {"owner.txt": b"other owner"})

    def test_generation_uses_only_standard_library_imports(self):
        tree = ast.parse(TOOL.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.partition(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add((node.module or "").partition(".")[0])
        self.assertTrue(imported <= set(sys.stdlib_module_names))
        self.assertFalse(any(name.startswith(("capture", "test_", "compare_capture")) for name in imported))

    def test_cli_unicode_foreign_cwd_and_ascii_terminal(self):
        destination = self.root / "démo_音"
        cwd = self.root / "elsewhere"
        cwd.mkdir()
        result = self.invoke(["--output", str(destination)], cwd=cwd, ascii_terminal=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")
        self.assertEqual(result.stdout, encode(inventory_from_bytes(archive_bytes(destination))))
        self.assertEqual(archive_bytes(destination), self.retained_before)

    def test_cli_relative_output_path_is_resolved_from_cwd(self):
        result = self.invoke(["--output", "relative-demo"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(archive_bytes(self.root / "relative-demo"), self.retained_before)

    def test_cli_usage_errors_do_not_create_archives(self):
        cases = ([], ["--out", "bad"], ["--output", ""],
                 ["--output", "first", "--output", "second"],
                 ["--output", "bad", "--unknown"], ["--output"])
        for args in cases:
            with self.subTest(args=args):
                result = self.invoke(args)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b"")
                self.assertTrue(result.stderr)
                self.assertEqual(list(self.root.iterdir()), [])

    def test_cli_help_and_direct_main_have_integer_exit(self):
        result = self.invoke(["--help"])
        self.assertEqual((result.returncode, result.stderr), (0, b""))
        self.assertIn(b"--output", result.stdout)
        self.assertEqual(list(self.root.iterdir()), [])
        for args, expected in ((["--help"], 0), ([], 2)):
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                actual = subject.main(args)
            self.assertIs(type(actual), int)
            self.assertEqual(actual, expected)

    def test_cli_existing_destination_reports_error_preserves_bytes(self):
        destination, _ = self.create()
        before = archive_bytes(destination)
        result = self.invoke(["--output", str(destination)])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertTrue(result.stderr.startswith(b"demo error: "))
        self.assertEqual(archive_bytes(destination), before)

    def test_cli_unicode_rejection_remains_contextual_under_ascii_terminal(self):
        destination, _ = self.create("démo_音")
        before = archive_bytes(destination)
        result = self.invoke(["--output", str(destination)], ascii_terminal=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertTrue(result.stderr.startswith(b"demo error: "), result.stderr)
        self.assertNotIn(b"Traceback", result.stderr)
        self.assertEqual(archive_bytes(destination), before)

    def test_cli_lf_binary_output_bypasses_text_translation(self):
        destination = self.root / "demo"
        stdout_bytes, stderr_bytes = io.BytesIO(), io.BytesIO()
        stdout = io.TextIOWrapper(stdout_bytes, encoding="ascii", newline="\r\n")
        stderr = io.TextIOWrapper(stderr_bytes, encoding="ascii", newline="\r\n")
        try:
            with mock.patch.object(sys, "stdout", stdout), mock.patch.object(sys, "stderr", stderr):
                code = subject.main(["--output", str(destination)])
            stdout.flush()
            stderr.flush()
            self.assertEqual(code, 0)
            self.assertEqual(stdout_bytes.getvalue(), encode(inventory_from_bytes(archive_bytes(destination))))
            self.assertEqual(stderr_bytes.getvalue(), b"")
            self.assertNotIn(b"\r", stdout_bytes.getvalue())
        finally:
            stdout.detach()
            stderr.detach()

    def test_cli_text_only_output_matches_unicode_inventory(self):
        destination = self.root / "demo"
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = subject.main(["--output", str(destination)])
        self.assertEqual(code, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(stdout.getvalue(), encode(inventory_from_bytes(archive_bytes(destination))).decode("utf-8"))

    def test_failed_inventory_stdout_retains_created_archive_and_discloses(self):
        destination = self.root / "demo"

        class BrokenText(io.StringIO):
            def write(self, value):
                raise OSError("controlled inventory stream failure")

        stderr = io.StringIO()
        with redirect_stdout(BrokenText()), redirect_stderr(stderr):
            code = subject.main(["--output", str(destination)])
        self.assertEqual(code, 1)
        self.assertIn("created demo retained", stderr.getvalue())
        self.assertIn("inventory stdout publication failed", stderr.getvalue())
        self.assertEqual(archive_bytes(destination), self.retained_before)

    def test_short_inventory_stdout_is_not_reported_as_success(self):
        destination = self.root / "demo"

        class ShortText(io.StringIO):
            def write(self, value):
                return super().write(value[:9])

        stdout, stderr = ShortText(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = subject.main(["--output", str(destination)])
        self.assertEqual(code, 1)
        self.assertEqual(len(stdout.getvalue()), 9)
        self.assertIn("created demo retained", stderr.getvalue())
        self.assertIn("incomplete inventory stdout write", stderr.getvalue())
        self.assertEqual(archive_bytes(destination), self.retained_before)

    def test_actual_cli_job_and_study_exit_matrix_retains_all_reports(self):
        destination, _ = self.create("démo_音")
        before = archive_bytes(destination)
        cases = [("capture_corpus.py", "corpus/corpus.json", 0, "pass", ["--check-files", "--check-audio"])]
        cases += [("capture_job.py", f"job-{name}.json", exit_code, status, [])
                  for name, _, _, _, _, _, status, exit_code in OUTCOMES]
        cases.append(("capture_study.py", "study.json", 1, "failed", []))
        for tool, relative, exit_code, status, flags in cases:
            with self.subTest(tool=tool, relative=relative):
                result = subprocess.run([sys.executable, "-B", str(ROOT / "tools" / tool),
                                         "--input", str(destination / relative), *flags],
                                        cwd=self.root, capture_output=True, check=False,
                                        env=dict(os.environ, PYTHONIOENCODING="ascii:strict",
                                                 PYTHONDONTWRITEBYTECODE="1"))
                self.assertEqual(result.returncode, exit_code, result.stderr)
                self.assertEqual(result.stderr, b"")
                report = json.loads(result.stdout)
                self.assertEqual(report["status"], status)
                self.assertEqual(result.stdout, encode(report))
                self.assertEqual(report["physical_fidelity"], "not_established")
        self.assertEqual(archive_bytes(destination), before)


if __name__ == "__main__":
    unittest.main()
