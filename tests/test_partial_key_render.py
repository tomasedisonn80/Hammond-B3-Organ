#!/usr/bin/env python3
"""Independent partial-position CLI/evidence acceptance using actual renders.

The producer creates fixtures only. Expected samples and schema decisions use
independent formulas, explicit public contracts and the separately implemented
consumer. Missing build inputs fail instead of silently skipping acceptance.
"""

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
from unittest import mock
import wave


ROOT = Path(__file__).resolve().parents[1]


def load_tool(name):
    spec = importlib.util.spec_from_file_location(
        f"partial_key_{name}", ROOT / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


producer = load_tool("render_fixture")
consumer = load_tool("verify_render")


def prerequisite(name):
    value = os.environ.get(name)
    if not value or not Path(value).is_file():
        raise RuntimeError(f"Missing {name}: build hammond_render and nominal.b3p, then run CTest")
    return Path(value).resolve()


def save_manifest(directory, manifest):
    (directory / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def rewrite(directory, record, contents):
    (directory / record["path"]).write_bytes(contents)
    record["size_bytes"] = len(contents)
    record["sha256"] = hashlib.sha256(contents).hexdigest()


class PartialKeyRenderTests(unittest.TestCase):
    cli_invocations = 0
    verified_bundles = 0
    fit_errors = []

    @classmethod
    def setUpClass(cls):
        cls.renderer = prerequisite("HAMMOND_RENDER_EXECUTABLE")
        cls.compiled = prerequisite("HAMMOND_TEST_PROFILE")
        cls.profile = ROOT / "data/profiles/nominal-unmeasured-v1.json"

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-partial-key-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name).resolve()
        self.sequence = 0

    def next_path(self, suffix):
        self.sequence += 1
        return self.work / f"case-{self.sequence}{suffix}"

    def render(self, score, *, contacts="nominal", rate=48000, block=127,
               frames=4096, drawbars="000000000", percussion="second", output=None):
        events = self.next_path(".events")
        events.write_bytes(score)
        output = output or self.next_path(".wav")
        before = set(self.work.iterdir())
        result = subprocess.run([
            str(self.renderer), "--profile", str(self.compiled), "--output", str(output),
            "--frames", str(frames), "--sample-rate", str(rate), "--block-size", str(block),
            "--seed", "1939", "--drawbars", drawbars, "--events", str(events),
            "--contacts", contacts, "--percussion", percussion, "--fail-on-clip"],
            capture_output=True, timeout=20, check=False)
        type(self).cli_invocations += 1
        return result, output, before

    def read_wav(self, output, rate, frames):
        with wave.open(str(output), "rb") as wav:
            self.assertEqual((wav.getnchannels(), wav.getsampwidth(), wav.getframerate(),
                              wav.getnframes(), wav.getcomptype()), (2, 2, rate, frames, "NONE"))
            pairs = list(struct.iter_unpack("<hh", wav.readframes(frames)))
        self.assertTrue(all(left == right for left, right in pairs))
        return [left / 32768.0 for left, _ in pairs]

    def bundle(self, score, *, contacts="nominal"):
        events = self.next_path(".events")
        events.write_bytes(score)
        directory = self.next_path("-bundle")
        manifest = producer.run_fixture(
            renderer=self.renderer, output_dir=directory, profile_json=self.profile,
            events=events, frames=4096, sample_rate=48000, block_size=127, seed=1939,
            drawbars="000000000", contacts=contacts, percussion="second")
        self.assertEqual(manifest["status"], "succeeded", manifest.get("error"))
        report = consumer.verify_bundle(directory)
        self.assertEqual(report["status"], "verified_retained_bundle")
        self.assertEqual(report["schema_version"], 3)
        type(self).verified_bundles += 1
        self.assertEqual(len(manifest["parameters"]), 14)
        self.assertEqual(len(manifest["renderer_metrics"]), 31)
        self.assertEqual(len(manifest["invocation"]["argv"]), 28)
        self.assertEqual((directory / "events.txt").read_bytes(), score)
        self.assertEqual((directory / "profile.b3p").read_bytes(), self.compiled.read_bytes())
        return directory, manifest

    def test_partial_harmonic_stays_recovered_at_three_rates_and_partitions(self):
        for rate in (44100, 48000, 96000):
            with self.subTest(rate=rate):
                frames = rate // 10
                score = b"0 key_position upper 69 0.5\n"
                first, path, _ = self.render(score, rate=rate, frames=frames, block=1)
                self.assertEqual(first.returncode, 0, first.stderr)
                metrics = json.loads(first.stdout)
                self.assertEqual(metrics["contact_model"], "nominal-linear-travel-v1")
                self.assertEqual(metrics["render_schema_version"], 3)
                samples = self.read_wav(path, rate, frames)
                onset = math.ceil(0.42 * 0.008 * rate)
                self.assertTrue(all(value == 0.0 for value in samples[:onset]))
                self.assertTrue(any(value != 0.0 for value in samples[onset:onset + 16]))
                # At target .5, contact3 is closed but detector8 never closes.
                # Fit the independent 880 Hz sine with unknown phase; q remains1.
                rows = [(math.sin(math.tau * 880.0 * n / rate),
                         math.cos(math.tau * 880.0 * n / rate), samples[n])
                        for n in range(rate // 50, 9 * rate // 100)]
                xx = sum(x * x for x, _, _ in rows)
                yy = sum(y * y for _, y, _ in rows)
                xy = sum(x * y for x, y, _ in rows)
                xs = sum(x * sample for x, _, sample in rows)
                ys = sum(y * sample for _, y, sample in rows)
                determinant = xx * yy - xy * xy
                self.assertGreater(determinant, 0)
                a = (xs * yy - ys * xy) / determinant
                b = (ys * xx - xs * xy) / determinant
                sample_bound = 0.5 / 32768.0 + 1e-8
                a_bound = sample_bound * sum(abs(yy * x - xy * y) for x, y, _ in rows) / determinant
                b_bound = sample_bound * sum(abs(xx * y - xy * x) for x, y, _ in rows) / determinant
                error = abs(math.hypot(a, b) - 0.03)
                self.assertLessEqual(error, math.hypot(a_bound, b_bound))
                self.assertLess(max(abs(sample - a * x - b * y) for x, y, sample in rows),
                                1.0 / 32768.0)
                type(self).fit_errors.append(error)
                second, other, _ = self.render(score, rate=rate, frames=frames, block=127)
                self.assertEqual(second.returncode, 0, second.stderr)
                self.assertEqual(path.read_bytes(), other.read_bytes())

    def test_ideal_endpoints_match_existing_note_commands(self):
        partial = (b"0 key_position upper 60 1\n512 key_position upper 60 0\n"
                   b"700 drawbar lower 2 8\n700 key_position lower 96 1\n"
                   b"1000 key_position lower 96 0\n")
        notes = partial.replace(b"key_position upper 60 1", b"note_on upper 60 100").replace(
            b"key_position upper 60 0", b"note_off upper 60 0").replace(
            b"key_position lower 96 1", b"note_on lower 96 127").replace(
            b"key_position lower 96 0", b"note_off lower 96 0")
        outputs = []
        for score in (partial, notes):
            result, output, _ = self.render(score, contacts="ideal", drawbars="008000000")
            self.assertEqual(result.returncode, 0, result.stderr)
            outputs.append(output.read_bytes())
        self.assertEqual(*outputs)

    def test_cli_rejects_mode_and_payload_before_creating_output(self):
        invalid = [
            ("ideal", b"0 key_position upper 60 .5\n"),
            ("ideal", b"0 key_position lower 60 0.00001\n"),
            ("nominal", b"0 key_position upper 60 -.01\n"),
            ("nominal", b"0 key_position upper 60 1.00001\n"),
            ("nominal", b"0 key_position upper 35 1\n"),
            ("nominal", b"0 key_position lower 97 1\n"),
            ("nominal", b"0 key_position pedal 60 .5\n"),
            ("nominal", b"0 key_position upper 60 nan\n"),
            ("nominal", b"0 key_position upper 60 inf\n"),
            ("nominal", b"0 key_position upper 60 1e-400\n")]
        for mode, score in invalid:
            with self.subTest(mode=mode, score=score):
                result, output, before = self.render(score, contacts=mode)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(output.exists())
                self.assertEqual(set(self.work.iterdir()), before)

    def test_existing_output_is_preserved(self):
        output = self.next_path(".wav")
        output.write_bytes(b"existing user bytes")
        result, _, before = self.render(b"0 key_position upper 60 .5\n", output=output)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_bytes(), b"existing user bytes")
        self.assertEqual(set(self.work.iterdir()), before)

    def test_producer_preflights_without_launch_or_directory_creation(self):
        for mode, score in (("ideal", b"0 key_position upper 60 .5\n"),
                            ("nominal", b"0 key_position upper 35 .5\n"),
                            ("nominal", b"0 key_position lower 60 1.1\n")):
            with self.subTest(mode=mode, score=score):
                events = self.next_path(".events")
                events.write_bytes(score)
                destination = self.next_path("-bundle")
                before = set(self.work.iterdir())
                with mock.patch.object(producer.subprocess, "Popen") as launch:
                    with self.assertRaises(producer.FixtureError):
                        producer.run_fixture(renderer=self.renderer, output_dir=destination,
                                             profile_json=self.profile, events=events, frames=4096,
                                             contacts=mode)
                    launch.assert_not_called()
                self.assertFalse(destination.exists())
                self.assertEqual(set(self.work.iterdir()), before)

    def test_current_schema_retains_partial_score_and_verifier_checks_declared_mode(self):
        directory, manifest = self.bundle(b"0 key_position upper 60 .5\n2000 note_on upper 60 100\n")
        self.assertEqual(manifest["parameters"]["event_count"], 2)
        manifest["parameters"]["contacts"] = "ideal"
        argv = manifest["invocation"]["argv"]
        argv[argv.index("--contacts") + 1] = "ideal"
        manifest["renderer_metrics"]["contact_model"] = "ideal-contacts-v1"
        rewrite(directory, manifest["invocation"]["stdout"],
                (json.dumps(manifest["renderer_metrics"]) + "\n").encode("utf-8"))
        save_manifest(directory, manifest)
        with self.assertRaisesRegex(consumer.VerificationError, "events line"):
            consumer.verify_bundle(directory)
        self.bundle(b"0 key_position upper 60 1\n1000 key_position upper 60 0\n", contacts="ideal")

    def test_historical_schema1_stays_valid_and_rejects_new_grammar(self):
        historical = ROOT / "examples/rendered/nominal-two-manual-v1/bundle"
        report = consumer.verify_bundle(historical)
        self.assertEqual(report["schema_version"], 1)
        for target in ("1", ".5"):
            destination = self.next_path("-schema1-mutation")
            shutil.copytree(historical, destination)
            manifest = json.loads((destination / "manifest.json").read_bytes())
            score = f"0 key_position upper 60 {target}\n".encode("ascii")
            rewrite(destination, manifest["inputs"]["events"], score)
            manifest["parameters"]["event_count"] = 1
            save_manifest(destination, manifest)
            with self.assertRaisesRegex(consumer.VerificationError, "events line"):
                consumer.verify_bundle(destination)

    @classmethod
    def tearDownClass(cls):
        print(f"partial-key CLI: {cls.cli_invocations} actual renderer calls; "
              f"{cls.verified_bundles} verified schema3 bundles; "
              f"max independent amplitude error={max(cls.fit_errors, default=0.0):.12g}")


if __name__ == "__main__":
    unittest.main()
