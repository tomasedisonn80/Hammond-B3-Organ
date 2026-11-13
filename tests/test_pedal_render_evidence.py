#!/usr/bin/env python3
"""Independent schema-3 pedal evidence and preserved historical-bundle checks.

The producer creates real fixtures; expectations come from the retained source
bytes and written contracts. Missing native prerequisites are errors, not skips.
"""

import hashlib
import importlib.util
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

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


producer = module("pedal_evidence_producer", "render_fixture.py")
consumer = module("pedal_evidence_independent_consumer", "verify_render.py")

PARAMETER_FIELDS = {
    "frames", "sample_rate", "block_size", "seed", "drawbars", "pedal_drawbars",
    "note", "event_mode", "event_count", "contacts", "percussion",
    "percussion_volume", "percussion_decay", "fail_on_clip",
}
OLD_METRIC_FIELDS = {
    "status", "model", "evidence_status", "profile_id", "authoring_sha256",
    "sample_rate", "block_size", "frames", "seed", "channels", "sample_format",
    "clipped_frames", "clipped_channel_samples", "peak", "rms",
    "render_schema_version", "contact_model", "percussion_model",
}
# Contract expectations are not imported from either executable or Python tool.
PEDAL_LITERALS = {
    "pedal_routing_model": "linear-pedal-bus-reference-v1",
    "pedal_voice_model": "nominal-static-pedal-mixture-v1",
    "pedal_gain_law": "linear-pedal-position-v1",
    "pedal_contact_model": "ideal-eight-contact-pedal-v1",
    "pedal_map_id": "atlas-derived-b3-c3-pedal-v1",
    "pedal_mixture_matrix": "4,2,1,1;1,4,2,1",
    "pedal_mixture_denominator": 8,
    "pedal_gain_denominator": 8,
    "pedal_weight_policy": "all-200-unit-positive-v1",
}
PEDAL_HASH_FIELDS = {
    "pedal_map_raw_sha256", "pedal_map_canonical_sha256",
    "pedal_reference_a_sha256", "pedal_reference_b_sha256",
}
PEDAL_FIELDS = set(PEDAL_LITERALS) | PEDAL_HASH_FIELDS


def required_file(name):
    value = os.environ.get(name)
    if not value or not Path(value).is_file():
        raise RuntimeError(f"Missing prerequisite {name}: {value!r}; build hammond_render "
                           "and nominal.b3p, then run CTest. Pedal evidence was not tested.")
    return Path(value).resolve()


def decoded_mono(path):
    raw = path.read_bytes()
    stereo = struct.unpack("<" + "h" * ((len(raw) - 44) // 2), raw[44:])
    if stereo[::2] != stereo[1::2]:
        raise AssertionError("renderer dry stereo channels differ")
    return stereo[::2]


class PedalRenderEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.renderer = required_file("HAMMOND_RENDER_EXECUTABLE")
        cls.compiled = required_file("HAMMOND_TEST_PROFILE")
        temporary = tempfile.TemporaryDirectory(prefix="hammond-pedal-evidence-base-")
        cls.addClassCleanup(temporary.cleanup)
        cls.fixtures = Path(temporary.name).resolve()
        cls.profile = ROOT / "data/profiles/nominal-unmeasured-v1.json"
        cls.score = cls.fixtures / "pedal score.txt"
        cls.score.write_bytes(
            b"\xef\xbb\xbf# explicit pedal IDs, mixed old commands, CRLF\r\n"
            b"0 pedal_on lower 1 100\r\n"
            b"9 pedal_drawbar lower 1 1.0\r\n"
            b"31 pedal_off lower 1 0\r\n"
            b"32 pedal_on lower 25 127\r\n"
            b"63 cancel lower 0 0\r\n"
            b"64 select_bank lower 0 0\r\n"
            b"96 pedal_all_notes_off lower 0 0\r\n")
        cls.base = cls.fixtures / "actual schema3 bundle"
        cls.manifest = producer.run_fixture(
            renderer=cls.renderer, output_dir=cls.base, profile_json=cls.profile,
            events=cls.score, frames=259, block_size=127, sample_rate=48000,
            seed=7, drawbars="000000000", pedal_drawbars="10")
        if cls.manifest["status"] != "succeeded":
            raise RuntimeError(f"Actual pedal renderer prerequisite failed: {cls.manifest['error']}")
        if (cls.base / "profile.b3p").read_bytes() != cls.compiled.read_bytes():
            raise RuntimeError("Compiled profile differs from native test prerequisite")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-pedal-evidence-test-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name).resolve()
        self.sequence = 0

    def destination(self, label="bundle"):
        self.sequence += 1
        return self.work / f"{label}-{self.sequence}"

    def clone(self, source=None):
        directory = self.destination()
        shutil.copytree(source or self.base, directory)
        return directory, json.loads((directory / "manifest.json").read_bytes())

    @staticmethod
    def save(directory, manifest):
        (directory / "manifest.json").write_bytes(
            (json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n").encode())

    @staticmethod
    def rewrite(directory, record, raw):
        (directory / record["path"]).write_bytes(raw)
        record.update(size_bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())

    def replace_metrics(self, directory, manifest, metrics):
        manifest["renderer_metrics"] = metrics
        self.rewrite(directory, manifest["invocation"]["stdout"],
                     (json.dumps(metrics, sort_keys=True) + "\n").encode())
        self.save(directory, manifest)

    def render(self, *, events=None, **options):
        directory = self.destination("real")
        arguments = dict(renderer=self.renderer, output_dir=directory,
                         profile_json=self.profile, frames=259, block_size=127,
                         sample_rate=48000, seed=7, drawbars="000000000", events=events)
        arguments.update(options)
        manifest = producer.run_fixture(**arguments)
        self.assertEqual(manifest["status"], "succeeded", manifest["error"])
        report = consumer.verify_bundle(directory)
        self.assertEqual(report["schema_version"], 3)
        return directory, manifest

    def test_actual_schema3_shape_parameters_and_invocation(self):
        manifest = self.manifest
        self.assertEqual(manifest["schema_version"], 3)
        self.assertEqual(set(manifest["parameters"]), PARAMETER_FIELDS)
        self.assertEqual(set(manifest["renderer_metrics"]), OLD_METRIC_FIELDS | PEDAL_FIELDS)
        self.assertEqual(manifest["parameters"]["pedal_drawbars"], "10")
        self.assertEqual(manifest["parameters"]["event_count"], 7)
        argv = manifest["invocation"]["argv"]
        self.assertEqual(len(argv), 28)
        self.assertEqual(argv[13:19], ["--drawbars", "000000000", "--pedal-drawbars", "10",
                                      "--contacts", "ideal"])
        self.assertEqual(argv[-3:], ["--fail-on-clip", "--events", str(self.base / "events.txt")])
        self.assertEqual((self.base / "events.txt").read_bytes(), self.score.read_bytes())
        report = consumer.verify_bundle(self.base)
        self.assertEqual(report["status"], "verified_retained_bundle")
        self.assertEqual(report["schema_version"], 3)
        self.assertEqual(report["artifacts_verified"], 6)
        self.assertEqual(report["renderer"]["status"], "matched")
        self.assertEqual(report["replay"]["status"], "not_performed")
        self.assertEqual(report["provenance"]["physical_fidelity"], "not_established")

    def test_actual_metadata_matches_independently_read_source_bytes(self):
        metrics = self.manifest["renderer_metrics"]
        for key, expected in PEDAL_LITERALS.items():
            with self.subTest(field=key):
                self.assertIs(type(metrics[key]), type(expected))
                self.assertEqual(metrics[key], expected)
        raw_map = (ROOT / "data/pedal-map.json").read_bytes()
        parsed_map = json.loads(raw_map)
        canonical = json.dumps(parsed_map, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False, allow_nan=False).encode()
        self.assertEqual(metrics["pedal_map_id"], parsed_map["map_id"])
        for key, raw in (
                ("pedal_map_raw_sha256", raw_map),
                ("pedal_map_canonical_sha256", canonical),
                ("pedal_reference_a_sha256", (ROOT / "data/references/review-a-pedal.csv").read_bytes()),
                ("pedal_reference_b_sha256", (ROOT / "data/references/review-b-pedal.csv").read_bytes())):
            with self.subTest(field=key):
                self.assertEqual(metrics[key], hashlib.sha256(raw).hexdigest())

    def test_real_pcm_statistics_and_mute_after_separate_pedal_panic(self):
        mono = decoded_mono(self.base / "render.wav")
        self.assertTrue(any(value != 0 for value in mono[:96]))
        self.assertTrue(all(value == 0 for value in mono[96:]))
        wav = self.manifest["wav"]
        self.assertEqual(wav["pcm_sum_squares_integer"], sum(value * value for value in mono))
        self.assertEqual(wav["pcm_peak"], max(abs(value) for value in mono) / 32768)
        self.assertEqual(wav["sha256"], hashlib.sha256((self.base / "render.wav").read_bytes()).hexdigest())
        self.assertTrue(self.manifest["metric_comparison"]["within_quantization_bound"])

    def test_all_pedal_ids_at_three_rates_and_registrations(self):
        score = self.work / "all pedals.txt"
        score.write_text("".join(f"{(pedal - 1) * 4} pedal_on lower {pedal} 1\n"
                                 f"{(pedal - 1) * 4 + 3} pedal_off lower {pedal} 0\n"
                                 for pedal in range(1, 26)), encoding="ascii")
        for rate in (44100, 48000, 96000):
            for positions in ("10", "01", "12"):
                with self.subTest(rate=rate, positions=positions):
                    directory, manifest = self.render(events=score, sample_rate=rate,
                                                      pedal_drawbars=positions)
                    self.assertEqual(manifest["parameters"]["event_count"], 50)
                    self.assertEqual(manifest["parameters"]["pedal_drawbars"], positions)
                    self.assertGreater(manifest["wav"]["pcm_peak"], 0)
                    self.assertTrue(all(value == 0 for value in decoded_mono(directory / "render.wav")[99:]))

    def test_default_muted_held_pedals_preserve_manual_pcm(self):
        manual = self.work / "manual.txt"
        held = self.work / "held muted pedals.txt"
        manual.write_bytes(b"0 note_on upper 60 100\n200 note_off upper 60 0\n")
        held.write_bytes(b"0 note_on upper 60 100\n0 pedal_on lower 1 100\n"
                         b"0 pedal_on lower 25 100\n200 note_off upper 60 0\n")
        plain, plain_manifest = self.render(events=manual, drawbars="008000000")
        muted, muted_manifest = self.render(events=held, drawbars="008000000")
        self.assertEqual(plain_manifest["parameters"]["pedal_drawbars"], "00")
        self.assertEqual(muted_manifest["parameters"]["pedal_drawbars"], "00")
        self.assertEqual((plain / "render.wav").read_bytes(), (muted / "render.wav").read_bytes())

    def test_schema3_score_grammar_boundaries_in_both_independent_parsers(self):
        lines = [f"0 pedal_on lower {pedal} 127\n0 pedal_off lower {pedal} 0e0\n"
                 for pedal in range(1, 26)]
        lines += [f"0 pedal_drawbar lower {index} {position}.0\n"
                  for index in (0, 1) for position in range(9)]
        lines += ["0 pedal_on lower 1 0\n", "0 pedal_all_notes_off lower 0 -0\n"]
        raw = "".join(lines).encode()
        for contacts in ("ideal", "nominal"):
            self.assertEqual(producer.validate_events(raw, 2, contacts), 70)
            self.assertEqual(consumer._events(raw, 2, 3, contacts), 70)
        boundary = b"0 pedal_on lower 1 1\n" * 1024
        self.assertEqual(producer.validate_events(boundary, 1), 1024)
        self.assertEqual(consumer._events(boundary, 1, 3), 1024)
        for parse in (lambda value: producer.validate_events(value, 1),
                      lambda value: consumer._events(value, 1, 3)):
            with self.assertRaises(ValueError):
                parse(boundary + b"0 pedal_off lower 1 0\n")

    def test_malformed_pedal_scores_reject_before_output_directory_creation(self):
        payloads = [
            "pedal_on upper 1 100", "pedal_on lower 0 1", "pedal_on lower 26 1",
            "pedal_on lower 1 -1", "pedal_on lower 1 128", "pedal_on lower 1 .5",
            "pedal_on lower 1 nan", "pedal_on lower 1 1e999", "pedal_on lower 1 1e-999",
            "pedal_off upper 1 0", "pedal_off lower 0 0", "pedal_off lower 26 0",
            "pedal_off lower 1 1", "pedal_drawbar upper 0 1", "pedal_drawbar lower 2 1",
            "pedal_drawbar lower 0 -1", "pedal_drawbar lower 0 9", "pedal_drawbar lower 0 .5",
            "pedal_all_notes_off upper 0 0", "pedal_all_notes_off lower 1 0",
            "pedal_all_notes_off lower 0 1", "pedal_on lower 1.0 1", "pedal_on pedals 1 1",
        ]
        score = self.work / "bad score.txt"
        for payload in payloads:
            with self.subTest(payload=payload):
                raw = f"0 expression upper 0 .5\n1 {payload}\n".encode()
                score.write_bytes(raw)
                directory = self.destination()
                with mock.patch.object(producer, "_invoke") as invoked:
                    with self.assertRaises(producer.FixtureError):
                        producer.run_fixture(renderer=self.renderer, output_dir=directory,
                                             events=score, frames=2)
                    invoked.assert_not_called()
                self.assertFalse(os.path.lexists(directory))
                with self.assertRaises(consumer.VerificationError):
                    consumer._events(raw, 2, 3)

    def test_bad_initial_pedal_positions_reject_before_directory_creation(self):
        for value in (None, True, 0, 12, 0.0, [], {}, "", "0", "000", "09", "90",
                      "-1", "1.0", " 10", "10 ", "1\n", "８0", "٠1", "1\x000"):
            with self.subTest(value=value):
                directory = self.destination()
                with self.assertRaises(producer.FixtureError):
                    producer.run_fixture(renderer=self.renderer, output_dir=directory,
                                         frames=1, pedal_drawbars=value)
                self.assertFalse(os.path.lexists(directory))

    def test_identity_mutations_reject_even_when_both_copies_and_hashes_agree(self):
        for field in sorted(PEDAL_FIELDS):
            original = self.manifest["renderer_metrics"][field]
            replacements = [None, True, 8.0 if type(original) is int else "unrecognized-v9"]
            for replacement in replacements:
                with self.subTest(field=field, replacement=replacement):
                    directory, manifest = self.clone()
                    metrics = dict(manifest["renderer_metrics"])
                    metrics[field] = replacement
                    self.replace_metrics(directory, manifest, metrics)
                    with self.assertRaises(consumer.VerificationError):
                        consumer.verify_bundle(directory)
            with self.subTest(field=field, mutation="missing"):
                directory, manifest = self.clone()
                metrics = dict(manifest["renderer_metrics"])
                del metrics[field]
                self.replace_metrics(directory, manifest, metrics)
                with self.assertRaises(consumer.VerificationError):
                    consumer.verify_bundle(directory)

    def test_matrix_equivalence_does_not_hide_changed_versioned_representation(self):
        for matrix in ("8,4,2,2;2,8,4,2", "4,2,1,1;1,4,2,1 ",
                       "[[0.5,0.25,0.125,0.125],[0.125,0.5,0.25,0.125]]",
                       "1,4,2,1;4,2,1,1"):
            directory, manifest = self.clone()
            metrics = dict(manifest["renderer_metrics"], pedal_mixture_matrix=matrix)
            self.replace_metrics(directory, manifest, metrics)
            with self.assertRaises(consumer.VerificationError):
                consumer.verify_bundle(directory)

    def test_pedal_invocation_and_parameter_mismatches_reject(self):
        for mutation in ("missing", "extra", "different", "reordered", "mistyped"):
            with self.subTest(mutation=mutation):
                directory, manifest = self.clone()
                if mutation == "missing":
                    del manifest["parameters"]["pedal_drawbars"]
                elif mutation == "extra":
                    manifest["parameters"]["pedal_note"] = 1
                elif mutation == "different":
                    manifest["invocation"]["argv"][16] = "01"
                elif mutation == "reordered":
                    argv = manifest["invocation"]["argv"]
                    argv[13:17] = argv[15:17] + argv[13:15]
                else:
                    manifest["parameters"]["pedal_drawbars"] = 10
                self.save(directory, manifest)
                with self.assertRaises(consumer.VerificationError):
                    consumer.verify_bundle(directory)

    def test_historical_retained_bundles_verify_without_changes(self):
        for name, version in (("nominal-two-manual-v1", 1), ("nominal-console-v2", 2)):
            directory = ROOT / "examples/rendered" / name / "bundle"
            before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in directory.iterdir()}
            report = consumer.verify_bundle(directory)
            self.assertEqual(report["schema_version"], version)
            after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in directory.iterdir()}
            self.assertEqual(before, after)

    def test_historical_versions_reject_new_pedal_grammar_and_fields(self):
        for name, version in (("nominal-two-manual-v1", 1), ("nominal-console-v2", 2)):
            source = ROOT / "examples/rendered" / name / "bundle"
            for command in ("pedal_on lower 1 1", "pedal_off lower 1 0",
                            "pedal_drawbar lower 0 1", "pedal_all_notes_off lower 0 0"):
                with self.subTest(version=version, command=command):
                    directory, manifest = self.clone(source)
                    score = (directory / "events.txt").read_bytes()
                    score += f"\n{manifest['parameters']['frames'] - 1} {command}\n".encode()
                    self.rewrite(directory, manifest["inputs"]["events"], score)
                    manifest["parameters"]["event_count"] += 1
                    self.save(directory, manifest)
                    with self.assertRaises(consumer.VerificationError):
                        consumer.verify_bundle(directory)
            directory, manifest = self.clone(source)
            manifest["parameters"]["pedal_drawbars"] = "00"
            self.save(directory, manifest)
            with self.assertRaises(consumer.VerificationError):
                consumer.verify_bundle(directory)
            directory, manifest = self.clone(source)
            metrics = dict(manifest["renderer_metrics"], pedal_voice_model="nominal-static-pedal-mixture-v1")
            self.replace_metrics(directory, manifest, metrics)
            with self.assertRaises(consumer.VerificationError):
                consumer.verify_bundle(directory)

    def test_version_labels_cannot_reinterpret_current_output(self):
        for version in (1, 2, 4, True, 3.0):
            with self.subTest(version=version):
                directory, manifest = self.clone()
                manifest["schema_version"] = version
                self.save(directory, manifest)
                with self.assertRaises(consumer.VerificationError):
                    consumer.verify_bundle(directory)

    def test_producer_rejects_old_or_mixed_metrics_after_real_render(self):
        real_invoke = producer._invoke

        def old_metrics(*arguments):
            info, stdout, stderr = real_invoke(*arguments)
            if arguments[0][0] != str(self.renderer):
                return info, stdout, stderr
            metrics = json.loads(stdout)
            for key in PEDAL_FIELDS:
                del metrics[key]
            metrics["render_schema_version"] = 2
            return info, (json.dumps(metrics) + "\n").encode(), stderr

        directory = self.destination("modified-stdout")
        with mock.patch.object(producer, "_invoke", side_effect=old_metrics):
            manifest = producer.run_fixture(renderer=self.renderer, output_dir=directory,
                                            frames=13, drawbars="000000000")
        self.assertEqual(manifest["schema_version"], 3)
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["error"]["stage"], "metrics")
        self.assertEqual(manifest["renderer_metrics"]["render_schema_version"], 2)
        self.assertIsNone(manifest["wav"])
        self.assertTrue((directory / "render.wav").is_file())
        with self.assertRaises(consumer.VerificationError):
            consumer.verify_bundle(directory)

    def test_no_clobber_and_fixed_bundle_inventory_remain_enforced(self):
        directory = self.destination()
        directory.mkdir()
        sentinel = directory / "sentinel.txt"
        sentinel.write_bytes(b"preserve\x00bytes\n")
        with self.assertRaises(producer.FixtureError):
            producer.run_fixture(renderer=self.renderer, output_dir=directory, frames=1)
        self.assertEqual(sentinel.read_bytes(), b"preserve\x00bytes\n")
        self.assertEqual(list(directory.iterdir()), [sentinel])
        directory, _ = self.clone()
        (directory / "unreported-pedal-map.json").write_text("{}", encoding="ascii")
        with self.assertRaises(consumer.VerificationError):
            consumer.verify_bundle(directory)

    def test_cli_exposes_and_checks_new_option_without_abbreviations(self):
        for extra in (("--pedal-drawbars", "09"),
                      ("--pedal-drawbars", "10", "--pedal-drawbars", "01"),
                      ("--pedal-draw", "10")):
            directory = self.destination("cli")
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/render_fixture.py"),
                 "--renderer", str(self.renderer), "--output-dir", str(directory),
                 "--frames", "1", *extra], capture_output=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(os.path.lexists(directory))
        help_result = subprocess.run([sys.executable, str(ROOT / "tools/render_fixture.py"), "--help"],
                                     capture_output=True, timeout=15)
        self.assertEqual(help_result.returncode, 0)
        self.assertIn(b"--pedal-drawbars", help_result.stdout)


if __name__ == "__main__":
    unittest.main()
