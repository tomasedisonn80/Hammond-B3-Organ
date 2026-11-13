#!/usr/bin/env python3
"""Retained pedal-demo integrity plus current-renderer musical replay.

Pinned bytes identify the historical artifact only. Current renders must agree
with each other across partitions; arbitrary platforms need not reproduce the
historical Linux floating-point stream byte for byte.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples/demos/pedal-phrase-v1"
BUNDLE = DEMO / "bundle"
VERIFIER = ROOT / "tools/verify_render.py"
SPEC = importlib.util.spec_from_file_location("pedal_demo_verifier", VERIFIER)
assert SPEC is not None and SPEC.loader is not None
consumer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(consumer)

SOURCE_COMMIT = "d7b886103f8c9d4649ffa1c35930b79808217a3d"
SOURCE_TREE = "018c3897889aaae0070f632981e0c889a35cad30"
SOURCE_INVENTORY_SHA = "4b207c6ad747761442ab326b3fd683ecd48fbbf6b1eedea4a8de600b832b64e8"
PROVENANCE_SHA = "da04261fe618b457d3e4162550d905efac5faa02049c2d00485ee0a186ea184b"
AUTHORING_SHA = "49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83"
PCM_SHA = "3107d186bb811b2cf1a2a3497422f5d77169f92ca2c9c7f22a1553482141c77c"
ARTIFACTS = {
    "manifest.json": (6844, "8cca3be0d5f451e9574590a211db748885062446674e46efb2a5e385027efb87"),
    "profile.json": (19627, "d17a266ed97cbbd3a2925ebebafafbd6c0e3f84763635732e0a9351d0eab2bff"),
    "profile.b3p": (4545, "b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f"),
    "events.txt": (1246, "47daa264ca9524c98d7a189d28728778c9057852b8fd3d68e7fea9d2e63b9be5"),
    "render.wav": (576044, "a3d1958189e811b8e353a75380d380016db5286eb08a2005626d95df64dde6f1"),
    "renderer.stdout.txt": (1284, "a41b8e19525ae76c891170b3677964c27093ce88fcfb394754375683acf82d05"),
    "renderer.stderr.txt": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
}
PARAMETERS = {
    "block_size": 127, "contacts": "ideal", "drawbars": "006400000", "event_count": 38,
    "event_mode": "file", "fail_on_clip": True, "frames": 144000, "note": None,
    "pedal_drawbars": "32", "percussion": "off", "percussion_decay": "slow",
    "percussion_volume": "normal", "sample_rate": 48000, "seed": 2704,
}
WINDOWS = {
    "whole": (0, 144000), "leading-silence": (0, 4800),
    "c-opening": (7200, 30000), "f": (36000, 58800),
    "g": (64800, 87600), "c-return": (93600, 116400),
    "trailing-silence": (120000, 144000),
}


def bounded(path: Path, maximum: int = 1024 * 1024) -> bytes:
    with path.open("rb") as stream:
        raw = stream.read(maximum + 1)
    if len(raw) > maximum:
        raise AssertionError(f"Oversized test input: {path}")
    return raw


def document(path: Path):
    return json.loads(bounded(path))


def identity(raw: bytes):
    return len(raw), hashlib.sha256(raw).hexdigest()


def decode_pcm(raw: bytes) -> tuple[list[int], bytes]:
    """Independent parser for this retained canonical 44-byte PCM WAV header."""
    if len(raw) != 576044:
        raise AssertionError("Expected exactly 144000 stereo PCM16 frames")
    header = struct.unpack("<4sI4s4sIHHIIHH4sI", raw[:44])
    expected = (b"RIFF", 576036, b"WAVE", b"fmt ", 16, 1, 2, 48000,
                192000, 4, 16, b"data", 576000)
    if header != expected:
        raise AssertionError(f"Unexpected RIFF/PCM format: {header}")
    mono = []
    for left, right in struct.iter_unpack("<hh", raw[44:]):
        if left != right:
            raise AssertionError("Dry stereo channels differ")
        mono.append(left)
    return mono, raw[44:]


def integer_statistics(samples):
    return {
        "frames": len(samples), "sum": sum(samples),
        "sum_squares": sum(value * value for value in samples),
        "peak": max(map(abs, samples)), "nonzero": sum(value != 0 for value in samples),
        "negative_rail": samples.count(-32768), "positive_rail": samples.count(32767),
    }


def phrase_events(manuals=True, pedals=True):
    """Literal musical timeline, independent of score parsing/producer code."""
    result = [(0, "expression", "upper", 0, "0.75")]
    if manuals:
        result.append((0, "bank_drawbar", "lower", 11, 6))
    chords = (
        (4800, (60, 64, 67), (48, 55), 1),
        (33600, (60, 65, 69), (53, 60), 6),
        (62400, (59, 62, 67), (55, 62), 8),
        (91200, (60, 64, 67), (48, 55), 1),
    )
    for frame, upper, lower, pedal in chords:
        if frame != 4800:
            if manuals:
                result.extend((frame, "all_notes_off", manual, 0, 0)
                              for manual in ("upper", "lower"))
            if pedals:
                result.append((frame, "pedal_all_notes_off", "lower", 0, 0))
        if manuals:
            result.extend((frame, "note_on", "upper", note, 100) for note in upper)
            result.extend((frame, "note_on", "lower", note, 100) for note in lower)
        if pedals:
            result.append((frame, "pedal_on", "lower", pedal, 100))
    if manuals:
        result.extend((120000, "all_notes_off", manual, 0, 0)
                      for manual in ("upper", "lower"))
    if pedals:
        result.append((120000, "pedal_all_notes_off", "lower", 0, 0))
    return [tuple(map(str, event)) for event in result]


def tree_from_inventory(records):
    """Reconstruct Git tree objects without requiring historical checkout data."""
    root = {}
    for record in records:
        path = PurePosixPath(record["path"])
        if path.is_absolute() or any(part in (".", "..") for part in path.parts):
            raise AssertionError("Noncanonical source path")
        mode, blob = record["mode"], record["git_blob"]
        if mode not in ("100644", "100755") or not re.fullmatch(r"[0-9a-f]{40}", blob):
            raise AssertionError("Unexpected source object")
        parent = root
        for part in path.parts[:-1]:
            parent = parent.setdefault(part, {})
        if path.name in parent:
            raise AssertionError("Duplicate source inventory path")
        parent[path.name] = (mode, bytes.fromhex(blob))

    def tree(node):
        entries = []
        for name, value in node.items():
            encoded = name.encode("utf-8")
            if isinstance(value, dict):
                entries.append((encoded + b"/", b"40000 " + encoded + b"\0" + tree(value)))
            else:
                mode, digest = value
                entries.append((encoded, mode.encode("ascii") + b" " + encoded + b"\0" + digest))
        raw = b"".join(entry for _, entry in sorted(entries))
        return hashlib.sha1(b"tree " + str(len(raw)).encode("ascii") + b"\0" + raw).digest()

    return tree(root).hex()


class RetainedPedalDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = document(BUNDLE / "manifest.json")
        cls.provenance = document(DEMO / "provenance.json")
        cls.mono, cls.pcm = decode_pcm(bounded(BUNDLE / "render.wav"))

    def test_exact_historical_bundle_and_scope(self):
        self.assertEqual({path.name for path in BUNDLE.iterdir()}, set(ARTIFACTS))
        for name, expected in ARTIFACTS.items():
            with self.subTest(name=name):
                self.assertEqual(identity(bounded(BUNDLE / name)), expected)
        report = consumer.verify_bundle(BUNDLE)
        self.assertEqual(report["schema_version"], 3)
        self.assertEqual(report["status"], "verified_retained_bundle")
        self.assertEqual(report["artifacts_verified"], 6)
        self.assertEqual(report["canonical_authoring_sha256"], AUTHORING_SHA)
        self.assertEqual(report["evidence_scope"], "synthetic_engineering")
        self.assertEqual(report["replay"]["status"], "not_performed")
        self.assertIn(report["renderer"]["status"], ("matched", "unavailable"))
        self.assertTrue(all(value in ("not_established", "recorded_not_reverified")
                            for value in report["provenance"].values()))
        self.assertIsNone(self.manifest["git"]["head"])
        self.assertIsNone(self.manifest["git"]["dirty"])
        self.assertEqual(self.manifest["git"]["binary_association"], "not_established")

    def test_source_tree_and_complete_provenance_inventory(self):
        self.assertEqual(hashlib.sha256(bounded(DEMO / "provenance.json")).hexdigest(), PROVENANCE_SHA)
        raw = bounded(DEMO / "source-blobs.json")
        self.assertEqual(hashlib.sha256(raw).hexdigest(), SOURCE_INVENTORY_SHA)
        inventory = json.loads(raw)
        self.assertEqual((inventory["file_count"], len(inventory["files"])), (474, 474))
        self.assertEqual(inventory["source_commit"], SOURCE_COMMIT)
        self.assertEqual(inventory["source_tree"], SOURCE_TREE)
        self.assertEqual(tree_from_inventory(inventory["files"]), SOURCE_TREE)
        self.assertEqual(self.provenance["source"]["commit"], SOURCE_COMMIT)
        self.assertEqual(self.provenance["source"]["tree"], SOURCE_TREE)
        self.assertEqual(self.provenance["source"]["archived_file_count"], 474)
        self.assertEqual(self.provenance["physical_status"], "unmeasured")
        self.assertEqual(self.provenance["evidence_scope"], "synthetic_engineering")
        self.assertIs(self.provenance["audio"]["subjective_listening_performed"], False)
        records = self.provenance["artifact_inventory"]
        self.assertEqual(len(records), 17)
        indexed = {item["path"] for item in records}
        self.assertEqual(len(indexed), len(records))
        actual = {path.relative_to(DEMO).as_posix() for path in DEMO.rglob("*") if path.is_file()}
        self.assertEqual(indexed, actual - {"provenance.json"})
        for record in records:
            with self.subTest(path=record["path"]):
                relative = PurePosixPath(record["path"])
                self.assertFalse(relative.is_absolute())
                self.assertNotIn("..", relative.parts)
                self.assertEqual(identity(bounded(DEMO / relative)), (record["bytes"], record["sha256"]))
        build = self.provenance["build"]
        self.assertEqual(len(build["translation_units"]), 17)
        self.assertEqual(build["renderer"]["sha256"], self.manifest["renderer"]["sha256_before"])
        by_path = {record["path"]: record for record in inventory["files"]}
        archive = PurePosixPath(self.provenance["source"]["archive_path"])
        for unit in build["translation_units"]:
            relative = PurePosixPath(unit["file"]).relative_to(archive).as_posix()
            self.assertEqual(unit["source_identity"],
                             {key: by_path[relative][key] for key in ("bytes", "sha256")})

    def test_literal_score_catalog_and_nominal_inputs(self):
        self.assertEqual(self.manifest["parameters"], PARAMETERS)
        score = bounded(BUNDLE / "events.txt")
        self.assertEqual(score, bounded(ROOT / "examples/fixtures/pedals/pedal-phrase-v1.events"))
        parsed = [tuple(line.split()) for line in score.decode("utf-8").splitlines()
                  if line.strip() and not line.lstrip().startswith("#")]
        self.assertEqual(parsed, phrase_events())
        self.assertEqual(len(parsed), 38)
        self.assertEqual(bounded(BUNDLE / "profile.json"),
                         bounded(ROOT / "data/profiles/nominal-unmeasured-v1.json"))
        catalog = document(ROOT / "examples/fixtures/pedals/pedal-catalog-v1.json")
        fixture, = [item for item in catalog["fixtures"] if item["id"] == "pedal-phrase-v1"]
        for field in ("frames", "sample_rate", "block_size", "seed"):
            self.assertEqual(fixture[field], PARAMETERS[field])
        self.assertEqual(fixture["registration"], "006400000")
        self.assertEqual(fixture["pedal_registration"], "32")
        self.assertEqual(fixture["expression"], 0.75)
        self.assertEqual(fixture["events"]["sha256"], ARTIFACTS["events.txt"][1])
        self.assertEqual([fit["span"] for fit in fixture["expectations"]["fits"]],
                         [list(WINDOWS[name]) for name in ("c-opening", "f", "g", "c-return")])

    def test_independent_pcm_statistics_and_audible_timeline(self):
        self.assertEqual(hashlib.sha256(self.pcm).hexdigest(), PCM_SHA)
        stats = integer_statistics(self.mono)
        self.assertEqual((stats["frames"], stats["peak"], stats["sum_squares"], stats["nonzero"]),
                         (144000, 2762, 81653430143, 115143))
        self.assertEqual((stats["negative_rail"], stats["positive_rail"]), (0, 0))
        self.assertEqual(set(self.mono[:4800]), {0})
        self.assertEqual(set(self.mono[120000:]), {0})
        for start in (4800, 33600, 62400, 91200):
            self.assertGreater(sum(value != 0 for value in self.mono[start:start + 28800]), 28000)
        metrics = self.manifest["renderer_metrics"]
        self.assertEqual((metrics["clipped_frames"], metrics["clipped_channel_samples"]), (0, 0))
        self.assertEqual(metrics["pedal_voice_model"], "nominal-static-pedal-mixture-v1")
        self.assertEqual((metrics["model"], metrics["evidence_status"]),
                         ("ideal-shared-sine-v1", "unmeasured"))
        self.assertLessEqual(abs(metrics["peak"] - stats["peak"] / 32768), 1 / 32768 + 1e-12)
        self.assertLessEqual(abs(metrics["rms"] - math.sqrt(stats["sum_squares"] / 144000) / 32768),
                             1 / 32768 + 1e-12)

    def test_all_seven_analysis_windows_against_integer_pcm(self):
        for name, (start, end) in WINDOWS.items():
            with self.subTest(window=name):
                report = document(DEMO / "analysis" / (name + ".json"))
                stats = integer_statistics(self.mono[start:end])
                self.assertEqual(report["window"], {"start_frame": start, "end_frame": end,
                                                     "frames": end - start,
                                                     "duration_seconds": (end - start) / 48000})
                self.assertEqual(report["stereo"], {"applicable": True, "identical": True,
                                                    "differing_frames": 0})
                self.assertIsNone(report["frequency"]["fixture_assumption"])
                self.assertIsNone(report["frequency"]["expected_frequency_hz"])
                self.assertIsNone(report["clipping"]["confirmed_pre_quantization_clipping"])
                self.assertEqual(report["clipping"]["full_scale_channel_samples"], 0)
                self.assertEqual(len(report["channels"]), 2)
                for index, channel in enumerate(report["channels"]):
                    self.assertEqual(channel["channel_index"], index)
                    self.assertEqual(channel["sample_count"], end - start)
                    self.assertEqual(channel["nonzero_sample_count"], stats["nonzero"])
                    self.assertEqual(channel["peak"], stats["peak"] / 32768)
                    self.assertAlmostEqual(channel["rms"],
                                           math.sqrt(stats["sum_squares"] / stats["frames"]) / 32768,
                                           delta=2e-15)
                    self.assertAlmostEqual(channel["dc"], stats["sum"] / stats["frames"] / 32768,
                                           delta=2e-15)
                    self.assertIsNone(channel["frequency_estimate"])
                    self.assertEqual(channel["full_scale_sample_count"], 0)

    def test_relocation_does_not_rewrite_or_execute_historical_paths(self):
        with tempfile.TemporaryDirectory(prefix="hammond-pedal-demo-") as directory:
            work = Path(directory).resolve()
            copied = work / "relocated bundle"
            shutil.copytree(BUNDLE, copied)
            before = {path.name: identity(bounded(path)) for path in copied.iterdir()}
            result = subprocess.run([sys.executable, str(VERIFIER), str(copied)],
                                    cwd=work, capture_output=True, timeout=30, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stderr, b"")
            report = json.loads(result.stdout)
            self.assertEqual(report["wav_sha256"], ARTIFACTS["render.wav"][1])
            self.assertEqual(report["replay"]["status"], "not_performed")
            self.assertEqual({path.name: identity(bounded(path)) for path in copied.iterdir()}, before)

    def test_targeted_copied_bundle_mutations_reject(self):
        cases = {
            "wav-byte": "WAV: channels differ",
            "wav-truncated": "WAV: truncated or misaligned samples",
            "wav-rate": "WAV: expected PCM16 stereo with declared rate/byte rate/alignment",
            "events-pedal-zero": "events line 10: unknown event type or invalid payload",
            "pedal-map": "renderer_metrics.pedal_map_raw_sha256: expected",
            "mixture": "renderer_metrics.pedal_mixture_matrix: expected",
            "initial-pedals": "parameters.pedal_drawbars: expected two digits 0..8",
            "physical-scope": "evidence_scope: expected 'synthetic_engineering'",
            "schema-downgrade": "parameters: missing or unexpected fields",
            "clipping": "renderer_metrics.clipped_frames: expected 0",
        }
        with tempfile.TemporaryDirectory(prefix="hammond-pedal-mutations-") as directory:
            for case in cases:
                with self.subTest(case=case):
                    copied = Path(directory).resolve() / case
                    shutil.copytree(BUNDLE, copied)
                    manifest = document(copied / "manifest.json")
                    if case.startswith("wav-"):
                        raw = bytearray(bounded(copied / "render.wav"))
                        if case == "wav-byte":
                            raw[44 + 4800 * 4] ^= 1
                        elif case == "wav-truncated":
                            del raw[-4:]
                        else:
                            struct.pack_into("<I", raw, 24, 44100)
                        (copied / "render.wav").write_bytes(raw)
                        manifest["wav"].update(size_bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
                    elif case == "events-pedal-zero":
                        raw = bounded(copied / "events.txt").replace(b"4800 pedal_on lower 1 100",
                                                                     b"4800 pedal_on lower 0 100", 1)
                        (copied / "events.txt").write_bytes(raw)
                        manifest["inputs"]["events"].update(size_bytes=len(raw),
                                                               sha256=hashlib.sha256(raw).hexdigest())
                    elif case in ("pedal-map", "mixture", "clipping"):
                        key, value = {"pedal-map": ("pedal_map_raw_sha256", "0" * 64),
                                      "mixture": ("pedal_mixture_matrix", "1,1,1,1;1,1,1,1"),
                                      "clipping": ("clipped_frames", 1)}[case]
                        metrics = manifest["renderer_metrics"]
                        metrics[key] = value
                        raw = (json.dumps(metrics, sort_keys=True) + "\n").encode("utf-8")
                        (copied / "renderer.stdout.txt").write_bytes(raw)
                        manifest["invocation"]["stdout"].update(size_bytes=len(raw),
                                                                   sha256=hashlib.sha256(raw).hexdigest())
                    elif case == "initial-pedals":
                        manifest["parameters"]["pedal_drawbars"] = "99"
                        arguments = manifest["invocation"]["argv"]
                        arguments[arguments.index("--pedal-drawbars") + 1] = "99"
                    elif case == "physical-scope":
                        manifest["evidence_scope"] = "measured_instrument"
                    else:
                        manifest["schema_version"] = 2
                    (copied / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
                    with self.assertRaisesRegex(consumer.VerificationError, re.escape(cases[case])):
                        consumer.verify_bundle(copied)
        # Every mutation was made in a private copy.
        for name, expected in ARTIFACTS.items():
            self.assertEqual(identity(bounded(BUNDLE / name)), expected)


class CurrentPedalDemoReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="hammond-pedal-replay-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.work = Path(cls.temporary.name).resolve()
        configured = os.environ.get("HAMMOND_RENDER_EXECUTABLE")
        if not configured:
            raise AssertionError("HAMMOND_RENDER_EXECUTABLE must identify the current built renderer")
        cls.renderer = Path(configured).resolve(strict=True)
        cls.outputs = {}
        for block in (64, 127, 1024):
            cls.outputs[f"whole-{block}"] = cls.render(f"whole-{block}", block, BUNDLE / "events.txt")
        for name, manuals, pedals in (("manual-only", True, False), ("pedal-only", False, True)):
            score = cls.work / (name + ".events")
            score.write_text("".join(" ".join(event) + "\n" for event in phrase_events(manuals, pedals)),
                             encoding="ascii")
            cls.outputs[name] = cls.render(name, 127, score, "006400000" if manuals else "000000000",
                                           "32" if pedals else "00")

    @classmethod
    def render(cls, name, block, score, drawbars="006400000", pedal_drawbars="32"):
        output = cls.work / (name + ".wav")
        command = [str(cls.renderer), "--profile", str(BUNDLE / "profile.b3p"), "--output", str(output),
                   "--frames", "144000", "--sample-rate", "48000", "--block-size", str(block),
                   "--seed", "2704", "--drawbars", drawbars, "--pedal-drawbars", pedal_drawbars,
                   "--contacts", "ideal", "--percussion", "off", "--percussion-volume", "normal",
                   "--percussion-decay", "slow", "--fail-on-clip", "--events", str(score)]
        result = subprocess.run(command, cwd=cls.work, capture_output=True, timeout=30, check=False)
        if result.returncode != 0 or result.stderr:
            raise AssertionError(f"Current demo render failed: {result.returncode} {result.stderr!r}")
        raw = bounded(output)
        mono, pcm = decode_pcm(raw)
        return raw, mono, pcm, json.loads(result.stdout)

    def test_current_complete_wav_is_partition_identical(self):
        reference = self.outputs["whole-127"][0]
        self.assertEqual(self.outputs["whole-64"][0], reference)
        self.assertEqual(self.outputs["whole-1024"][0], reference)
        # Deliberately no assertion that another toolchain matches historical WAV bytes.

    def test_each_current_division_is_audible_and_stops_at_its_panic(self):
        for name, (_, mono, _, metrics) in self.outputs.items():
            with self.subTest(name=name):
                self.assertEqual(set(mono[:4800]), {0})
                self.assertEqual(set(mono[120000:]), {0})
                for start, end in (WINDOWS[key] for key in ("c-opening", "f", "g", "c-return")):
                    self.assertGreater(sum(sample != 0 for sample in mono[start:end]), 22000)
                self.assertEqual((metrics["clipped_frames"], metrics["clipped_channel_samples"]), (0, 0))
                self.assertEqual(metrics["evidence_status"], "unmeasured")
                self.assertTrue(0 < metrics["rms"] <= metrics["peak"] < 0.103)
                stats = integer_statistics(mono)
                self.assertLessEqual(abs(metrics["peak"] - stats["peak"] / 32768), 1 / 32768 + 1e-12)

    def test_independent_division_scores_reconstruct_combined_pcm(self):
        combined = self.outputs["whole-127"][1]
        manual = self.outputs["manual-only"][1]
        pedal = self.outputs["pedal-only"][1]
        # Sum separately encoded independent division renders. Two PCM code
        # steps conservatively cover their separate rounding plus float mixing.
        maximum = max(abs(full - upper_lower - bass)
                      for full, upper_lower, bass in zip(combined, manual, pedal))
        self.assertLessEqual(maximum, 2)
        self.assertNotEqual(combined, manual)
        self.assertNotEqual(combined, pedal)
        self.assertGreater(sum(full != manuals for full, manuals in zip(combined, manual)), 110000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
