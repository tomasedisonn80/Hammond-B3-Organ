#!/usr/bin/env python3
"""Native audition workflow checks; no Python synthesizer or physical claim.

HAMMOND_RENDER_EXECUTABLE, HAMMOND_TEST_PROFILE and optional HAMMOND_SOURCE_DIR
select coherent inputs. Missing native inputs fail rather than skipping.
Failure/timeout/race injections are author checks, not observed native failures.
"""

from array import array
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import wave


ROOT = Path(os.environ.get("HAMMOND_SOURCE_DIR", Path(__file__).resolve().parents[1])).resolve()
TOOL = ROOT / "tools/audition_starter_registrations.py"
spec = importlib.util.spec_from_file_location("starter_auditions", TOOL)
auditions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditions)
REAL_RUN = subprocess.run


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pcm(path):
    with wave.open(str(path), "rb") as source:
        if (source.getnframes(), source.getframerate(), source.getnchannels(),
                source.getsampwidth()) != (48000, 48000, 2, 2):
            raise AssertionError("expected one second of 48 kHz stereo PCM16")
        values = array("h", source.readframes(48000))
    if sys.byteorder != "little":
        values.byteswap()
    if values[::2] != values[1::2]:
        raise AssertionError("dry renderer channels unexpectedly differ")
    return values[::2]


class StarterAuditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        name = "hammond_render.exe" if os.name == "nt" else "hammond_render"
        cls.renderer = Path(os.environ.get("HAMMOND_RENDER_EXECUTABLE", ROOT / "build" / name)).resolve()
        profile = Path(os.environ.get("HAMMOND_TEST_PROFILE", cls.renderer.parent / "nominal.b3p"))
        for label, path in (("renderer", cls.renderer), ("profile", profile)):
            if not path.is_file():
                raise RuntimeError(f"missing coherent {label}: {path}; build before testing")
        cls.temporary = tempfile.TemporaryDirectory(prefix="starter-audition-author-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.base = Path(cls.temporary.name).resolve()
        cls.profile = cls.base / "organ profile Ω.b3p"
        shutil.copyfile(profile, cls.profile)
        cls.pack = cls.base / "proposed pack ü"
        shutil.copytree(ROOT / "data/registrations/starter-v1", cls.pack)
        cls.output = cls.base / "audition output ü"
        invocation = [sys.executable, "-B", str(TOOL), "--renderer", str(cls.renderer),
                      "--profile", str(cls.profile), "--pack", str(cls.pack),
                      "--output", str(cls.output)]
        result = REAL_RUN(invocation, capture_output=True, text=True,
                          encoding="utf-8", timeout=60, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"real audition CLI failed: {result.stdout}\n{result.stderr}")
        cls.cli_summary = json.loads(result.stdout)
        cls.manifest = json.loads((cls.output / "manifest.json").read_text(encoding="utf-8"))
        cls.jobs = {job["id"]: job for job in cls.manifest["jobs"]}

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="case-", dir=self.base)
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)

    def run_auditions(self, output=None, **overrides):
        arguments = dict(renderer=self.renderer, profile=self.profile, pack=self.pack,
                         output=output or self.work / "new", timeout_seconds=15)
        arguments.update(overrides)
        return auditions.run_auditions(**arguments)

    def assert_record(self, record):
        path = Path(record["path"])
        self.assertEqual(record["size_bytes"], path.stat().st_size)
        self.assertEqual(record["sha256"], digest(path))

    def test_actual_cli_covers_all_pairs_and_exact_provenance(self):
        report = self.manifest
        self.assertEqual(self.cli_summary["status"], "succeeded")
        self.assertEqual(report["status"], "succeeded")
        self.assertEqual(report["evidence_status"], "proposed-unmeasured")
        self.assertEqual(report["engine"], "nominal-dry")
        self.assertEqual(report["restore_policy"], "full-state-including-expression")
        self.assertEqual((report["attempted_jobs"], report["completed_jobs"]), (32, 32))
        self.assertTrue(report["inputs_unchanged"])
        self.assertEqual(len(report["paired_wavs_equal"]), 16)
        inputs = report["inputs"]
        for key in ("renderer", "profile", "pack_manifest", "tool"):
            self.assert_record(inputs[key])
        for key, record in inputs["scores"].items():
            self.assert_record(record)
            used = report["copied_scores"][key]
            self.assert_record(used)
            self.assertEqual(used["path"], str(self.output / "scores" / auditions.SCORES[key]))
            self.assertEqual(used["sha256"], record["sha256"])
        self.assertEqual(len(inputs["recipes"]), 12)
        for recipe in inputs["recipes"]:
            for scope in ("registration", "performance"):
                self.assert_record(recipe[scope])
            self.assertEqual(recipe["registration"]["sha256"], recipe["performance"]["sha256"])
        for job in report["jobs"]:
            with self.subTest(render=job["id"]):
                self.assertEqual(job["status"], "succeeded")
                self.assertEqual(job["returncode"], 0)
                self.assertTrue(job["stdout_is_json"])
                self.assertTrue(job["canonical_controls_match_payload"])
                self.assertEqual(job["argv"][0], str(self.renderer))
                self.assertEqual(job["argv"][job["argv"].index("--frames") + 1], "48000")
                self.assertIn("--fail-on-clip", job["argv"])
                for record in job["outputs"].values():
                    self.assert_record(record)
                summary = json.loads(Path(job["outputs"]["stdout_json"]["path"]).read_bytes())
                payload = Path(job["argv"][job["argv"].index("--controls") + 1])
                self.assertEqual(summary["render_schema_version"], 6)
                self.assertEqual(summary["controls"]["canonical_b3controls4"], payload.read_text())
                self.assertEqual(summary["controls"]["path"], str(payload))
                self.assertEqual(summary["controls"]["source_bytes"], payload.stat().st_size)
                self.assertEqual(summary["clipped_channel_samples"], 0)
                self.assertTrue(any(pcm(job["outputs"]["wav"]["path"])))
        for first, second in report["paired_wavs_equal"]:
            self.assertEqual(Path(self.jobs[first]["outputs"]["wav"]["path"]).read_bytes(),
                             Path(self.jobs[second]["outputs"]["wav"]["path"]).read_bytes())

    def test_note_only_score_sounds_suitable_manual_and_pedal_segments(self):
        for number in range(1, 13):
            samples = pcm(self.output / f"{number:02d}-audition-registration.wav")
            with self.subTest(recipe=number):
                self.assertEqual(any(samples[1200:6500]), number not in (10, 12))
                self.assertEqual(any(samples[17200:23000]), number != 10)
                self.assertTrue(any(samples[27200:33000]), "all twelve recipes require pedal audition")
        pedal_only = pcm(self.output / "10-audition-registration.wav")
        self.assertFalse(any(pedal_only[:26000]), "cancelled manuals must stay silent")
        manual_return = pcm(self.output / "12-audition-registration.wav")
        self.assertFalse(any(manual_return[:16000]), "note-only audition must not reselect Upper")

    def test_named_companions_reveal_cancelled_fixed_and_hidden_banks(self):
        for number in (9, 10, 11):
            samples = pcm(self.output / f"{number:02d}-banks-reveal-registration.wav")
            self.assertEqual(any(samples[1000:9000]), number != 10)
            self.assertTrue(any(samples[13200:21000]))
            self.assertTrue(any(samples[25200:33000]))
        samples = pcm(self.output / "12-manual-return-registration.wav")
        self.assertFalse(any(samples[:8000]))
        for start, end in ((9000, 15000), (19200, 27000), (31200, 41000)):
            self.assertTrue(any(samples[start:end]))
        summary = json.loads((self.output / "12-manual-return-registration.stdout.json").read_bytes())
        self.assertIn("selected A fixed_registration G# route_enabled 0",
                      summary["controls"]["canonical_b3controls4"])

    def test_exact_recorded_argv_reproduces_percussion_and_pedal_wavs(self):
        for number in (7, 10):
            job = self.jobs[f"{number:02d}-audition-registration"]
            argv = job["argv"].copy()
            output = self.work / f"repeat-{number}.wav"
            argv[argv.index("--output") + 1] = str(output)
            result = REAL_RUN(argv, capture_output=True, timeout=15, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output.read_bytes(), Path(job["outputs"]["wav"]["path"]).read_bytes())

    def test_main_score_changes_no_saved_controls(self):
        source = ROOT / "examples/registrations/starter-audition.events"
        for line in source.read_text().splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            frame, kind, manual, index, value = line.split()
            self.assertLess(int(frame), 48000)
            self.assertIn(kind, ("note_on", "note_off", "pedal_on", "pedal_off"))
            if kind.startswith("pedal_"):
                self.assertEqual(manual, "lower")
                self.assertTrue(1 <= int(index) <= 25)

    def test_all_required_inputs_and_timeout_are_explicit_and_bounded(self):
        result = REAL_RUN([sys.executable, "-B", str(TOOL)], capture_output=True,
                          text=True, timeout=5, check=False)
        self.assertEqual(result.returncode, 2)
        for flag in ("--renderer", "--profile", "--pack", "--output"):
            self.assertIn(flag, result.stderr)
        for value in (0, -1, 0.099, 30.1, float("inf"), float("nan"), True):
            with self.subTest(timeout=value), mock.patch.object(auditions.subprocess, "run") as runner:
                with self.assertRaises(auditions.AuditionError):
                    self.run_auditions(timeout_seconds=value)
                runner.assert_not_called()
                self.assertFalse((self.work / "new").exists())

    def test_existing_outputs_and_input_aliases_are_refused_without_mutation(self):
        empty = self.work / "empty"
        empty.mkdir()
        occupied = self.work / "occupied"
        occupied.mkdir()
        sentinel = occupied / "keep.txt"
        sentinel.write_bytes(b"existing user bytes\n")
        regular = self.work / "existing.file"
        regular.write_bytes(b"existing file\n")
        original_profile = self.profile.read_bytes()
        for path in (empty, occupied, regular, self.profile, self.pack, self.output):
            with self.subTest(path=path), mock.patch.object(auditions.subprocess, "run") as runner:
                with self.assertRaises(auditions.AuditionError):
                    self.run_auditions(path)
                runner.assert_not_called()
        self.assertEqual(list(empty.iterdir()), [])
        self.assertEqual(sentinel.read_bytes(), b"existing user bytes\n")
        self.assertEqual(regular.read_bytes(), b"existing file\n")
        self.assertEqual(self.profile.read_bytes(), original_profile)

    def test_symlink_and_parent_aliases_are_refused_before_creation(self):
        target = self.work / "target"
        target.mkdir()
        link = self.work / "alias"
        broken = self.work / "broken"
        try:
            link.symlink_to(target, target_is_directory=True)
            broken.symlink_to(self.work / "absent", target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"symlink creation unavailable on this platform: {error}")
        for path in (link, broken, link / "fresh", target / ".." / "fresh"):
            with self.subTest(path=path), mock.patch.object(auditions.subprocess, "run") as runner:
                with self.assertRaises(auditions.AuditionError):
                    self.run_auditions(path)
                runner.assert_not_called()
        self.assertEqual(list(target.iterdir()), [])
        self.assertFalse((self.work / "absent").exists())
        self.assertTrue(link.is_symlink())
        self.assertTrue(broken.is_symlink())

    def test_hard_link_output_and_nonregular_input_are_refused(self):
        alias = self.work / "profile-alias"
        os.link(self.profile, alias)
        original = digest(self.profile)
        with self.assertRaises(auditions.AuditionError):
            self.run_auditions(alias)
        self.assertEqual(digest(alias), original)
        with self.assertRaises(auditions.AuditionError):
            self.run_auditions(profile=self.work)
        if hasattr(os, "mkfifo"):
            fifo = self.work / "profile-fifo"
            os.mkfifo(fifo)
            with self.assertRaises(auditions.AuditionError):
                self.run_auditions(profile=fifo)
        self.assertFalse((self.work / "new").exists())

    def test_unsafe_pack_filename_extra_entry_and_pair_difference_fail_preflight(self):
        pack = self.work / "pack"
        shutil.copytree(self.pack, pack)
        manifest_path = pack / "recipes.json"
        original = manifest_path.read_bytes()
        manifest = json.loads(original)
        manifest["recipes"][0]["registration_file"] = "../escape.b3registration"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(auditions.AuditionError):
            self.run_auditions(pack=pack)
        manifest_path.write_bytes(original)
        extra = pack / "entries" / "extra.txt"
        extra.write_bytes(b"not an admitted payload\n")
        with self.assertRaises(auditions.AuditionError):
            self.run_auditions(pack=pack)
        extra.unlink()
        payload = pack / "entries/12 Manual Return.b3performance"
        payload.write_bytes(payload.read_bytes().replace(b"expression 0.5", b"expression 0.4"))
        with mock.patch.object(auditions.subprocess, "run") as runner:
            with self.assertRaises(auditions.AuditionError):
                self.run_auditions(pack=pack)
            runner.assert_not_called()
        self.assertFalse((self.work / "new").exists())

    def test_partial_failure_retains_real_completed_job_and_exact_child_logs(self):
        calls = []

        def injected(argv, **kwargs):
            self.assertIsInstance(argv, list)
            self.assertFalse(kwargs["shell"])
            self.assertEqual(kwargs["timeout"], 15)
            calls.append(argv)
            if len(calls) == 1:
                return REAL_RUN(argv, **kwargs)
            kwargs["stdout"].write(b'{"injected_failure":true}\n')
            kwargs["stderr"].write(b"injected renderer failure\n")
            return subprocess.CompletedProcess(argv, 3)

        with mock.patch.object(auditions.subprocess, "run", side_effect=injected):
            manifest = self.run_auditions()
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual((manifest["attempted_jobs"], manifest["completed_jobs"]), (2, 1))
        first, failed = manifest["jobs"][:2]
        self.assertEqual(first["status"], "succeeded")
        self.assertEqual(failed["returncode"], 3)
        self.assertIsNone(failed["outputs"]["wav"])
        self.assertTrue(failed["stdout_is_json"])
        for job in (first, failed):
            for record in job["outputs"].values():
                if record is not None:
                    self.assert_record(record)
        self.assertEqual(Path(failed["outputs"]["stderr"]["path"]).read_bytes(),
                         b"injected renderer failure\n")
        for job in manifest["jobs"][2:]:
            self.assertEqual(job["status"], "not-run")
            self.assertTrue(all(item is None for item in job["outputs"].values()))
        self.assertEqual(json.loads((self.work / "new/manifest.json").read_bytes()), manifest)
        self.assertIn("1 of 32 renders succeeded", (self.work / "new/report.md").read_text())
        with self.assertRaises(auditions.AuditionError):
            self.run_auditions()

    def test_timeout_retains_actual_partial_wav_and_non_json_stdout(self):
        def timeout(argv, **kwargs):
            Path(argv[argv.index("--output") + 1]).write_bytes(b"RIFFpartial")
            kwargs["stdout"].write(b'{"unfinished":')
            kwargs["stderr"].write(b"injected timeout\n")
            raise subprocess.TimeoutExpired(argv, kwargs["timeout"])

        with mock.patch.object(auditions.subprocess, "run", side_effect=timeout):
            manifest = self.run_auditions(timeout_seconds=0.1)
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual((manifest["attempted_jobs"], manifest["completed_jobs"]), (1, 0))
        failed = manifest["jobs"][0]
        self.assertTrue(failed["timed_out"])
        self.assertIsNone(failed["returncode"])
        self.assertFalse(failed["stdout_is_json"])
        self.assertNotIn("wav", failed)
        for record in failed["outputs"].values():
            self.assert_record(record)
        self.assertEqual(failed["outputs"]["wav"]["sha256"],
                         hashlib.sha256(b"RIFFpartial").hexdigest())

    def test_destination_race_cannot_replace_new_user_directory(self):
        output = self.work / "raced"
        original_mkdir = Path.mkdir

        def race(path, *args, **kwargs):
            if path == output:
                original_mkdir(path)
                (path / "keep.txt").write_bytes(b"new user data\n")
            return original_mkdir(path, *args, **kwargs)

        with mock.patch.object(Path, "mkdir", race), mock.patch.object(auditions.subprocess, "run") as runner:
            with self.assertRaises(FileExistsError):
                self.run_auditions(output)
            runner.assert_not_called()
        self.assertEqual([path.name for path in output.iterdir()], ["keep.txt"])
        self.assertEqual((output / "keep.txt").read_bytes(), b"new user data\n")

    def test_wrong_runtime_provenance_fails_without_hiding_published_wav(self):
        def wrong_provenance(argv, **kwargs):
            result = REAL_RUN(argv, **kwargs)
            kwargs["stdout"].flush()
            summary_path = Path(kwargs["stdout"].name)
            summary = json.loads(summary_path.read_bytes())
            summary["controls"]["canonical_b3controls4"] = "injected wrong initial state\n"
            kwargs["stdout"].seek(0)
            kwargs["stdout"].truncate()
            kwargs["stdout"].write((json.dumps(summary) + "\n").encode())
            return result

        with mock.patch.object(auditions.subprocess, "run", side_effect=wrong_provenance):
            manifest = self.run_auditions()
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["completed_jobs"], 0)
        failed = manifest["jobs"][0]
        self.assertEqual(failed["returncode"], 0)
        self.assertIn("provenance differs", failed["error"])
        self.assert_record(failed["outputs"]["wav"])
        self.assert_record(failed["outputs"]["stdout_json"])
        self.assertTrue(any(pcm(failed["outputs"]["wav"]["path"])))


if __name__ == "__main__":
    unittest.main()
