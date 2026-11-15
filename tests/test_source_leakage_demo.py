#!/usr/bin/env python3
"""Real audition regeneration plus bounded publication/failure qualification."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("source_leakage_demo", ROOT / "tools/build_source_leakage_demo.py")
assert spec is not None and spec.loader is not None
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class SourceLeakageDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        supplied = os.environ.get("HAMMOND_RENDER_EXECUTABLE")
        if not supplied or not Path(supplied).is_file():
            raise RuntimeError("HAMMOND_RENDER_EXECUTABLE is required; build hammond_render then run CTest")
        cls.renderer = Path(supplied).resolve()
        cls.temporary = tempfile.TemporaryDirectory(prefix="hammond-leakage-demo-test-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.work = Path(cls.temporary.name)
        cls.bundle = cls.work / "first"
        cls.result = demo.build_demo(cls.renderer, cls.bundle)
        cls.receipt = json.loads((cls.bundle / "provenance.json").read_bytes())

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_actual_bundle_identity_and_source_oracle(self):
        self.assertEqual(self.result["renders"], 6)
        self.assertEqual(self.result["files"], 22)
        self.assertLess(self.result["bytes"], 4 * 1024 * 1024)
        self.assertEqual(self.receipt["status"], "verified_synthetic_demonstration")
        self.assertTrue(self.receipt["unchanged_inputs_and_executable"])
        self.assertEqual(len(self.receipt["invocations"]), 9)
        self.assertTrue(all(row["returncode"] == 0 for row in self.receipt["invocations"]))
        self.assertEqual(self.receipt["renderer"]["sha256"], hashlib.sha256(self.renderer.read_bytes()).hexdigest())
        for name, facts in self.receipt["artifacts"].items():
            raw = (self.bundle / name).read_bytes()
            self.assertEqual(facts, {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
        for row in self.receipt["renders"]:
            self.assertEqual(row["summary"]["clipped_frames"], 0)
            self.assertTrue(row["wav"]["identical_channels"])
            self.assertEqual(row["wav"]["frames"], 96000)
            if row["score"] == "solo.events":
                oracle = row["independent_pcm_oracle"]
                self.assertEqual(oracle["channel_samples_checked"], 192000)
                self.assertEqual(oracle["exact_silent_frames"], 24000)
                self.assertLessEqual(oracle["maximum_integer_error"], 1)
        self.assertEqual((self.bundle / "solo-legacy-g100.wav").read_bytes(),
                         (self.bundle / "solo-identity-g100.wav").read_bytes())
        for comparison in self.receipt["comparisons"]["pairs"]:
            self.assertEqual(comparison["same_input_gain"], 0.75)
            self.assertGreater(comparison["changed_frames"], 0)

    def test_second_actual_generation_preserves_audio_and_data_bytes(self):
        other = self.work / "repeat"
        result = demo.build_demo(self.renderer, other)
        self.assertEqual(result["comparisons"], self.result["comparisons"])
        retained = [path for path in self.bundle.iterdir()
                    if path.suffix in (".wav", ".b3p", ".b3leakage", ".events") or path.name.endswith("-authoring.json")]
        self.assertEqual(len(retained), 14)
        for path in retained:
            self.assertEqual(path.read_bytes(), (other / path.name).read_bytes(), path.name)

    def test_existing_output_and_input_aliases_are_preserved(self):
        before = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in self.bundle.iterdir()}
        renderer_hash = hashlib.sha256(self.renderer.read_bytes()).hexdigest()
        for target in (self.bundle, self.renderer, ROOT / "data/source-leakage/synthetic-pair-demo-v1.json"):
            with self.assertRaises(demo.DemoError):
                demo.build_demo(self.renderer, target)
        after = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in self.bundle.iterdir()}
        self.assertEqual(before, after)
        self.assertEqual(renderer_hash, hashlib.sha256(self.renderer.read_bytes()).hexdigest())
        dangling = self.work / "dangling"
        try:
            dangling.symlink_to(self.work / "missing")
        except (NotImplementedError, OSError):
            return  # Existing-file/directory/alias checks above remain mandatory.
        with self.assertRaises(demo.DemoError):
            demo.build_demo(self.renderer, dangling)
        self.assertTrue(dangling.is_symlink())

    def test_failed_renderer_and_invalid_setup_leave_no_staging_or_output(self):
        before = set(self.work.iterdir())
        with self.assertRaises(demo.DemoError):
            # Python is an actual executable which rejects renderer's --profile.
            demo.build_demo(Path(sys.executable), self.work / "failed-render")
        for timeout in (0, -1, 121, float("inf"), float("nan"), True):
            with self.assertRaises(demo.DemoError):
                demo.build_demo(self.renderer, self.work / "invalid-timeout", timeout)
        with self.assertRaises(FileNotFoundError):
            demo.build_demo(self.renderer, self.work / "absent-parent" / "new")
        self.assertEqual(before, set(self.work.iterdir()))

    def test_command_stream_and_time_limits_are_enforced(self):
        with self.assertRaisesRegex(demo.DemoError, "stream limit"):
            demo._run([sys.executable, "-c", "import sys;sys.stdout.write('x'*262144)"], 5)
        with self.assertRaisesRegex(demo.DemoError, "time"):
            demo._run([sys.executable, "-c", "import time;time.sleep(5)"], 0.05)

    def test_pcm_oracle_detects_changed_samples_and_silence(self):
        pcm, _ = demo.inspect_pcm(self.bundle / "solo-pair-g075.wav")
        profile = json.loads((self.bundle / "nominal-authoring.json").read_bytes())
        changed = pcm.copy()
        changed[100] += 8
        with self.assertRaisesRegex(demo.DemoError, "1-LSB"):
            demo.pcm_oracle(changed, profile, 0.75, True)
        changed = pcm.copy()
        changed[25000] = 1
        with self.assertRaisesRegex(demo.DemoError, "silent"):
            demo.pcm_oracle(changed, profile, 0.75, True)

    def test_publication_failure_rolls_back_own_files(self):
        with tempfile.TemporaryDirectory(dir=self.work) as name:
            stage = Path(name) / "stage"
            stage.mkdir()
            for filename in ("a", "b", "provenance.json"):
                (stage / filename).write_text(filename)
            output = Path(name) / "output"
            original_link = os.link
            calls = []

            def injected(source, destination):
                calls.append(Path(source).name)
                if len(calls) == 2:
                    raise OSError("injected publication failure")
                return original_link(source, destination)

            with mock.patch.object(demo.os, "link", side_effect=injected):
                with self.assertRaisesRegex(OSError, "injected"):
                    demo._publish(stage, output)
            self.assertFalse(output.exists())
            self.assertEqual(calls, ["a", "b"])
            self.assertEqual(len(list(stage.iterdir())), 3)
            demo._publish(stage, output)
            self.assertEqual({p.name for p in output.iterdir()}, {"a", "b", "provenance.json"})
            with self.assertRaises(FileExistsError):
                demo._publish(stage, output)

    def test_raced_destination_is_preserved_and_provenance_is_last(self):
        with tempfile.TemporaryDirectory(dir=self.work) as name:
            stage = Path(name) / "stage"
            stage.mkdir()
            for filename in ("a", "b", "provenance.json"):
                (stage / filename).write_text(filename)
            output = Path(name) / "output"
            original_link = os.link
            calls = []

            def collision(source, destination):
                calls.append(Path(source).name)
                if len(calls) == 2:
                    Path(destination).write_bytes(b"concurrent owner")
                return original_link(source, destination)

            with mock.patch.object(demo.os, "link", side_effect=collision):
                with self.assertRaises(FileExistsError):
                    demo._publish(stage, output)
            self.assertEqual([p.name for p in output.iterdir()], ["b"])
            self.assertEqual((output / "b").read_bytes(), b"concurrent owner")
            other = Path(name) / "clean"
            order = []

            def observe(source, destination):
                order.append(Path(source).name)
                return original_link(source, destination)

            with mock.patch.object(demo.os, "link", side_effect=observe):
                demo._publish(stage, other)
            self.assertEqual(order, ["a", "b", "provenance.json"])


if __name__ == "__main__":
    unittest.main()
