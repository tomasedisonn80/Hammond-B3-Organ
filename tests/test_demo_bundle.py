#!/usr/bin/env python3
"""Portable integrity gate for the retained four-second synthetic demo.

Run directly with Python 3.10+ or through CTest's python_test_demo_bundle.
No renderer is launched or required. Pinned WAV bytes identify this retained
artifact, never the output expected from another compiler or operating system.
"""

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import struct
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock
import wave


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "examples/rendered/nominal-two-manual-v1/bundle"
VERIFIER = ROOT / "tools/verify_render.py"
SPEC = importlib.util.spec_from_file_location("demo_bundle_consumer", VERIFIER)
consumer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(consumer)

PARAMETERS = {
    "block_size": 127, "drawbars": "006400000", "event_count": 34,
    "event_mode": "file", "fail_on_clip": True, "frames": 192000,
    "note": None, "sample_rate": 48000, "seed": 2601,
}
AUTHORING_SHA256 = "49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83"
ARTIFACT_SHA256 = {
    "manifest.json": "74ad49caa3cc5170870bed1002ea64ffaaf8a202c0614095b31fdcd8308da2ce",
    "profile.json": "d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff",
    "profile.b3p": "b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f",
    "events.txt": "d86b7fb3e3a62865b218400828aaef7ee176c39da7f08ef29aed5ae5b0627ae8",
    "render.wav": "9c46d82dc8da8ba5be078e895765e98672b51a30da52e0684d75a293aa4d84fd",
    "renderer.stdout.txt": "a7778003ce642c29b39609602082d1824f4b4df279a3513b0815fd9eacc949b1",
    "renderer.stderr.txt": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
}
PROVENANCE = {
    "authentication": "not_established", "source_build_association": "not_established",
    "original_inputs_and_tools": "recorded_not_reverified", "physical_fidelity": "not_established",
}


def bounded_bytes(path, limit):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise AssertionError(f"Test input exceeds {limit} bytes: {path}")
    return raw


class DemoBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Missing artifacts are failures. This gate never skips missing inputs.
        cls.report = consumer.verify_bundle(BUNDLE)
        cls.manifest = json.loads(bounded_bytes(BUNDLE / "manifest.json", 256 * 1024))

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-demo-gate-")
        self.addCleanup(temporary.cleanup)
        # Resolve the current workspace independently of historical metadata.
        self.work = Path(temporary.name).resolve()

    def assert_report(self, report):
        self.assertEqual(report["status"], "verified_retained_bundle")
        self.assertEqual(report["evidence_scope"], "synthetic_engineering")
        self.assertEqual(report["artifacts_verified"], 6)
        self.assertEqual((report["frames"], report["sample_rate"]), (192000, 48000))
        self.assertEqual(report["canonical_authoring_sha256"], AUTHORING_SHA256)
        self.assertEqual(report["wav_sha256"], ARTIFACT_SHA256["render.wav"])
        self.assertIn(report["renderer"]["status"], ("matched", "unavailable"))
        self.assertEqual(report["replay"], {
            "status": "not_performed",
            "renderer_available": report["renderer"]["status"] == "matched",
            "reason": "verification never executes recorded commands",
        })
        self.assertEqual(report["provenance"], PROVENANCE)

    def test_retained_identities_and_historical_scope(self):
        self.assert_report(self.report)
        self.assertEqual({path.name for path in BUNDLE.iterdir()}, set(ARTIFACT_SHA256))
        for filename, expected in ARTIFACT_SHA256.items():
            with self.subTest(filename=filename):
                path = BUNDLE / filename
                self.assertLessEqual(path.stat().st_size, 800 * 1024)
                digest = hashlib.sha256()
                with path.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(64 * 1024), b""):
                        digest.update(chunk)
                self.assertEqual(digest.hexdigest(), expected)
        self.assertEqual(self.manifest["git"]["head"], "6c3dd8bc923a3c11f6b234425b056e135fbe9f4b")
        self.assertIs(self.manifest["git"]["dirty"], True)
        self.assertEqual(self.manifest["git"]["binary_association"], "not_established")
        self.assertTrue(PurePosixPath(self.manifest["renderer"]["path"]).is_absolute())

    def test_complete_score_profile_and_settings(self):
        self.assertEqual(self.manifest["parameters"], PARAMETERS)
        self.assertEqual(PARAMETERS["frames"], 4 * PARAMETERS["sample_rate"])
        retained_score = bounded_bytes(BUNDLE / "events.txt", 16 * 1024)
        self.assertEqual(retained_score, bounded_bytes(
            ROOT / "examples/fixtures/two-manual-changes-v1.events", 16 * 1024))
        self.assertEqual(bounded_bytes(BUNDLE / "profile.json", 256 * 1024), bounded_bytes(
            ROOT / "data/profiles/nominal-unmeasured-v1.json", 256 * 1024))
        events = [line.split() for line in retained_score.decode("utf-8").splitlines()
                  if line.strip() and not line.lstrip().startswith("#")]
        self.assertEqual(len(events), 34)
        self.assertEqual({event[2] for event in events}, {"upper", "lower"})
        self.assertEqual({int(event[0]) for event in events}, {0, 2400, 43200, 84000, 124800, 168000})
        catalog = json.loads(bounded_bytes(ROOT / "examples/fixtures/catalog-v1.json", 128 * 1024))
        fixture, = [item for item in catalog["fixtures"] if item["id"] == "two-manual-changes-v1"]
        for key in ("frames", "sample_rate", "block_size", "seed"):
            self.assertEqual(fixture[key], PARAMETERS[key])
        self.assertEqual(fixture["registration"], PARAMETERS["drawbars"])
        self.assertEqual(fixture["events"]["sha256"], ARTIFACT_SHA256["events.txt"])
        self.assertEqual(catalog["profile"]["authoring_sha256"], AUTHORING_SHA256)

    def test_actual_pcm_timeline_and_unclipped_metrics(self):
        # Decode the retained PCM independently of both wrapper and consumer.
        boundaries = (0, 2400, 43200, 84000, 124800, 168000, 192000)
        nonzero = [0] * 6
        frame = span = peak = squares = 0
        with wave.open(str(BUNDLE / "render.wav"), "rb") as stream:
            self.assertEqual((stream.getnchannels(), stream.getsampwidth(), stream.getframerate(),
                              stream.getnframes(), stream.getcomptype()), (2, 2, 48000, 192000, "NONE"))
            while raw := stream.readframes(16384):
                for left, right in struct.iter_unpack("<hh", raw):
                    self.assertEqual(left, right)
                    while frame >= boundaries[span + 1]:
                        span += 1
                    nonzero[span] += left != 0
                    peak = max(peak, abs(left))
                    squares += left * left
                    frame += 1
        self.assertEqual(frame, 192000)
        self.assertEqual((peak, squares), (2664, 82976846092))
        self.assertLess(peak, 32767)
        self.assertEqual((nonzero[0], nonzero[-1]), (0, 0))
        self.assertTrue(all(count > 0 for count in nonzero[1:-1]))
        metrics = self.manifest["renderer_metrics"]
        self.assertEqual((metrics["clipped_frames"], metrics["clipped_channel_samples"]), (0, 0))
        self.assertEqual((metrics["model"], metrics["evidence_status"]),
                         ("ideal-shared-sine-v1", "unmeasured"))
        self.assertTrue(0 < metrics["rms"] <= metrics["peak"] < 1)
        self.assertLessEqual(abs(metrics["peak"] - peak / 32768), 1 / 32768 + 1e-12)
        self.assertLessEqual(abs(metrics["rms"] - math.sqrt(squares / frame) / 32768), 1 / 32768 + 1e-12)

    def test_relocated_bundle_cli_preserves_historical_manifest(self):
        copied = self.work / "relocated bundle"
        shutil.copytree(BUNDLE, copied)
        result = subprocess.run([sys.executable, str(VERIFIER), str(copied / "manifest.json")],
                                cwd=self.work, capture_output=True, timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(result.stderr, b"")
        report = json.loads(result.stdout)
        self.assert_report(report)
        self.assertEqual(report["manifest"], str(copied / "manifest.json"))
        self.assertEqual(report["manifest_sha256"], ARTIFACT_SHA256["manifest.json"])

    def test_absent_historical_renderer_does_not_inspect_ancestor_aliases(self):
        # Reproduced with a real symlink before repair. Model that boundary on
        # every runner without requiring Windows symlink privileges or editing
        # the historical manifest; this is not native macOS qualification.
        external = Path(self.manifest["renderer"]["path"])
        original_lstat = Path.lstat
        original_directory = consumer._Reader.directory
        availability_checks = []

        def absent_lstat(path, *args, **kwargs):
            if path == external:
                availability_checks.append(path)
                raise FileNotFoundError("historical rendering session has expired")
            return original_lstat(path, *args, **kwargs)

        def guarded_directory(reader, path):
            if path == external.parent:
                raise consumer.VerificationError("unavailable historical path has a symlink ancestor")
            return original_directory(reader, path)

        with mock.patch.object(Path, "lstat", absent_lstat), \
             mock.patch.object(consumer._Reader, "directory", guarded_directory):
            report = consumer.verify_bundle(BUNDLE)
        self.assert_report(report)
        self.assertEqual(report["renderer"]["status"], "unavailable")
        expected_reason = ("recorded path belongs to another operating system"
                           if os.name == "nt" else "FileNotFoundError")
        self.assertEqual(report["renderer"]["reason"], expected_reason)
        self.assertEqual(availability_checks, [] if os.name == "nt" else [external])

    def test_foreign_posix_metadata_is_retained_without_external_reads(self):
        # Replace only this module's OS view, preserving pathlib and real file
        # operations. This exercises path classification, not a native OS run.
        foreign_host = types.SimpleNamespace(**vars(os))
        foreign_host.name = "nt"
        original_read = consumer._Reader.read

        def retained_only(reader, path, *args, **kwargs):
            self.assertTrue(path.is_relative_to(BUNDLE), f"Historical path was read: {path}")
            return original_read(reader, path, *args, **kwargs)

        with mock.patch.object(consumer, "os", foreign_host), \
             mock.patch.object(consumer._Reader, "read", retained_only):
            report = consumer.verify_bundle(BUNDLE)
        self.assert_report(report)
        self.assertEqual(report["renderer"], {
            "status": "unavailable", "reason": "recorded path belongs to another operating system"})
        self.assertFalse(report["replay"]["renderer_available"])

    def test_absent_historical_renderer_below_regular_file_is_unavailable(self):
        copied = self.work / "expired build ancestry"
        shutil.copytree(BUNDLE, copied)
        former_directory = self.work / "former build directory"
        former_directory.write_bytes(b"This historical directory is now a regular file.\n")
        absent = former_directory / "hammond_render"
        manifest = json.loads(bounded_bytes(copied / "manifest.json", 256 * 1024))
        manifest["renderer"]["path"] = str(absent)
        manifest["invocation"]["argv"][0] = str(absent)
        (copied / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        report = consumer.verify_bundle(copied)
        self.assert_report(report)
        self.assertEqual(report["renderer"]["status"], "unavailable")
        # POSIX reports ENOTDIR; Windows may report the same absence as ENOENT.
        self.assertIn(report["renderer"]["reason"], ("NotADirectoryError", "FileNotFoundError"))
        self.assertFalse(report["replay"]["renderer_available"])

    def test_present_external_renderer_keeps_hash_type_and_ancestry_checks(self):
        copied = self.work / "changed historical metadata"
        shutil.copytree(BUNDLE, copied)
        external = self.work / "present renderer"
        external.write_bytes(b"modified")
        manifest = json.loads(bounded_bytes(copied / "manifest.json", 256 * 1024))
        manifest["renderer"] = {
            "path": str(external), "size_bytes": 8,
            "sha256_before": hashlib.sha256(b"expected").hexdigest(),
            "sha256_after": hashlib.sha256(b"expected").hexdigest(),
        }
        manifest["invocation"]["argv"][0] = str(external)
        (copied / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(consumer.VerificationError, "current renderer SHA-256"):
            consumer.verify_bundle(copied)
        original_directory = consumer._Reader.directory

        def guarded_directory(reader, path):
            if path == external.parent:
                raise consumer.VerificationError("present external ancestor must be nonsymlink")
            return original_directory(reader, path)

        with mock.patch.object(consumer._Reader, "directory", guarded_directory), \
             self.assertRaisesRegex(consumer.VerificationError, "present external ancestor"):
            consumer.verify_bundle(copied)
        external.unlink()
        external.mkdir()
        with self.assertRaisesRegex(consumer.VerificationError, "regular nonsymlink file"):
            consumer.verify_bundle(copied)


if __name__ == "__main__":
    unittest.main()
