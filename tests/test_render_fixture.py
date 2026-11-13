#!/usr/bin/env python3
"""Real-renderer evidence tests; missing build prerequisites are explicit failures.

CTest supplies HAMMOND_RENDER_EXECUTABLE and HAMMOND_TEST_PROFILE. Direct use:
  HAMMOND_RENDER_EXECUTABLE=/path/hammond_render \
  HAMMOND_TEST_PROFILE=/path/nominal.b3p python3 tests/test_render_fixture.py
"""

import hashlib
import importlib.util
import itertools
import json
import math
import os
from pathlib import Path
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("render_fixture", ROOT / "tools/render_fixture.py")
fixture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fixture)

# Frozen from the documented v2 contract, independently of producer constants.
PARAMETER_FIELDS_V2 = {
    "frames", "sample_rate", "block_size", "seed", "drawbars", "note", "event_mode",
    "event_count", "contacts", "percussion", "percussion_volume", "percussion_decay",
    "fail_on_clip",
}
METRIC_FIELDS_V2 = {
    "status", "model", "evidence_status", "profile_id", "authoring_sha256",
    "sample_rate", "block_size", "frames", "seed", "channels", "sample_format",
    "clipped_frames", "clipped_channel_samples", "peak", "rms",
    "render_schema_version", "contact_model", "percussion_model",
}
# Additive schema 3 fields are frozen here, without importing producer metadata.
PARAMETER_FIELDS_V3 = PARAMETER_FIELDS_V2 | {"pedal_drawbars"}
METRIC_FIELDS_V3 = METRIC_FIELDS_V2 | {
    "pedal_routing_model", "pedal_voice_model", "pedal_gain_law", "pedal_contact_model",
    "pedal_map_id", "pedal_map_raw_sha256", "pedal_map_canonical_sha256",
    "pedal_reference_a_sha256", "pedal_reference_b_sha256", "pedal_mixture_matrix",
    "pedal_mixture_denominator", "pedal_gain_denominator", "pedal_weight_policy",
}


def required_file(environment_name):
    raw = os.environ.get(environment_name)
    if not raw or not Path(raw).is_file():
        raise RuntimeError(
            f"Missing prerequisite {environment_name}: {raw!r}. Build hammond_render and "
            "nominal.b3p with CMake, then run CTest or explicitly set "
            "HAMMOND_RENDER_EXECUTABLE and HAMMOND_TEST_PROFILE. Evidence tests were not run.")
    return Path(raw).resolve()


def metadata(info, **changes):
    fields = {name: getattr(info, name) for name in (
        "st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns", "st_ctime_ns")}
    fields.update(changes)
    return SimpleNamespace(**fields)


class FileIntegrityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-file-integrity-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.path = self.work / "one-frame.wav"
        self.raw = struct.pack("<4sI4s4sIHHIIHH4sIhh", b"RIFF", 40, b"WAVE", b"fmt ",
                               16, 1, 2, 48000, 192000, 4, 16, b"data", 4, 123, 123)
        self.path.write_bytes(self.raw)

    def readers(self):
        return (lambda: fixture.sha256_file(self.path, len(self.raw)),
                lambda: fixture.inspect_wav(self.path, frames=1, sample_rate=48000))

    def test_within_api_changes_are_rejected_by_hash_and_wav_readers(self):
        original = self.path.lstat()
        changes = dict(st_dev=original.st_dev + 1, st_ino=original.st_ino + 1,
                       st_mode=stat.S_IFDIR | 0o700, st_size=original.st_size + 1,
                       st_mtime_ns=original.st_mtime_ns + 1,
                       st_ctime_ns=original.st_ctime_ns + 1)
        for reader in self.readers():
            for api in ("path", "descriptor"):
                for field, value in changes.items():
                    with self.subTest(reader=reader, api=api, field=field):
                        changed = metadata(original, **{field: value})
                        path_after = changed if api == "path" else original
                        fd_after = changed if api == "descriptor" else original
                        with mock.patch.object(fixture, "os", wraps=os) as windows_os, \
                                mock.patch.object(type(self.path), "lstat",
                                                  side_effect=[original, path_after]):
                            windows_os.name = "nt"
                            windows_os.fstat.side_effect = [original, fd_after]
                            with self.assertRaisesRegex(fixture.FixtureError, "changed"):
                                reader()

    def test_posix_requires_matching_open_file_identity(self):
        original = self.path.lstat()
        for reader in self.readers():
            for field in ("st_dev", "st_ino"):
                with self.subTest(reader=reader, field=field):
                    with mock.patch.object(fixture, "os", wraps=os) as posix_os:
                        posix_os.name = "posix"
                        posix_os.fstat.return_value = metadata(
                            original, **{field: getattr(original, field) + 1})
                        with self.assertRaisesRegex(fixture.FixtureError, "identity changed"):
                            reader()

    def test_regular_nonsymlink_type_and_size_checks_remain_enforced(self):
        original = self.path.lstat()
        for reader in self.readers():
            for mode in (stat.S_IFLNK, stat.S_IFDIR, stat.S_IFIFO):
                with self.subTest(reader=reader, mode=mode):
                    with mock.patch.object(type(self.path), "lstat",
                                           return_value=metadata(original, st_mode=mode)), \
                            mock.patch.object(type(self.path), "open") as opened:
                        with self.assertRaisesRegex(fixture.FixtureError, "regular file"):
                            reader()
                        opened.assert_not_called()
            for change in ({"st_mode": stat.S_IFIFO}, {"st_size": len(self.raw) + 1}):
                with self.subTest(reader=reader, opened=change):
                    with mock.patch.object(fixture, "os", wraps=os) as windows_os:
                        windows_os.name = "nt"
                        windows_os.fstat.return_value = metadata(original, **change)
                        with self.assertRaisesRegex(fixture.FixtureError, "type/size changed"):
                            reader()
        with self.assertRaisesRegex(fixture.FixtureError, "no larger than"):
            fixture.sha256_file(self.path, len(self.raw) - 1)
        # An inaccurate metadata size must not defeat the streaming byte limit.
        smaller = metadata(original, st_size=len(self.raw) - 1)
        with mock.patch.object(type(self.path), "lstat", return_value=smaller), \
                mock.patch.object(fixture, "os", wraps=os) as windows_os:
            windows_os.name = "nt"
            windows_os.fstat.return_value = smaller
            with self.assertRaisesRegex(fixture.FixtureError, "exceeds .* byte limit"):
                fixture.sha256_file(self.path, len(self.raw) - 1)

    def test_git_autocrlf_checkout_preserves_catalog_hashes_and_binary_bytes(self):
        catalog_path = Path("examples/fixtures/catalog-v1.json")
        catalog = json.loads((ROOT / catalog_path).read_bytes())
        paths = [Path(".gitattributes"), catalog_path,
                 Path(catalog["profile"]["authoring_path"]), Path("tools/render_fixture.py")]
        paths += [catalog_path.parent / item["events"]["path"] for item in catalog["fixtures"]]
        expected = {path: (ROOT / path).read_bytes() for path in paths}
        for suffix in ("pdf", "wav", "b3p"):
            # Text-looking payloads prove the extension rule prevents conversion.
            expected[Path(f"binary.{suffix}")] = b"preserve these bytes\r\nincluding CRLF\r\n"
        for relative, raw in expected.items():
            destination = self.work / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)

        def git(*arguments):
            result = subprocess.run(
                ["git", "-c", "core.autocrlf=true", "-c", "core.safecrlf=false",
                 "-C", str(self.work), *arguments], capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
            return result.stdout

        git("init", "--quiet")
        git("add", "--", *map(str, expected))
        for relative in expected:
            (self.work / relative).unlink()
        git("checkout-index", "--all", "--force")
        for relative, raw in expected.items():
            with self.subTest(path=relative):
                checked_out = (self.work / relative).read_bytes()
                self.assertEqual(checked_out, raw)
                self.assertEqual(hashlib.sha256(checked_out).hexdigest(), hashlib.sha256(raw).hexdigest())
        for item in catalog["fixtures"]:
            raw = (self.work / catalog_path.parent / item["events"]["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), item["events"]["sha256"])
        self.assertEqual(git("check-attr", "text", "--", "binary.pdf", "binary.wav", "binary.b3p").splitlines(),
                         [b"binary.pdf: text: unset", b"binary.wav: text: unset", b"binary.b3p: text: unset"])


class RenderFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.renderer = required_file("HAMMOND_RENDER_EXECUTABLE")
        cls.expected_compiled = required_file("HAMMOND_TEST_PROFILE").read_bytes()
        if not os.access(cls.renderer, os.X_OK):
            raise RuntimeError(f"HAMMOND_RENDER_EXECUTABLE is not executable: {cls.renderer}")
        cls.authoring_bytes = fixture.DEFAULT_PROFILE.read_bytes()

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-evidence-test-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.profile = self.work / "authoring profile.json"
        self.profile.write_bytes(self.authoring_bytes)
        self.sequence = 0

    def new_output(self):
        self.sequence += 1
        return self.work / f"result {self.sequence}"

    def render(self, **changes):
        output = changes.pop("output_dir", self.new_output())
        arguments = dict(renderer=self.renderer, output_dir=output, profile_json=self.profile,
                         frames=259, block_size=64, seed=7, drawbars="008000000")
        arguments.update(changes)
        return output, fixture.run_fixture(**arguments)

    def score(self, raw):
        path = self.work / "score ; literal.txt"
        path.write_bytes(raw.encode("utf-8") if isinstance(raw, str) else raw)
        return path

    def assert_success(self, directory, manifest):
        directory = directory.resolve()
        self.assertEqual(manifest["status"], "succeeded", manifest.get("error"))
        self.assertIs(type(manifest["schema_version"]), int)
        self.assertEqual(manifest["schema_version"], 3)
        parameters = manifest["parameters"]
        self.assertEqual(set(parameters), PARAMETER_FIELDS_V3)
        metrics = manifest["renderer_metrics"]
        self.assertEqual(set(metrics), METRIC_FIELDS_V3)
        self.assertIs(type(metrics["render_schema_version"]), int)
        self.assertEqual(metrics["render_schema_version"], 3)
        self.assertEqual(metrics["contact_model"], {
            "ideal": "ideal-contacts-v1", "nominal": "nominal-linear-travel-v1",
        }[parameters["contacts"]])
        self.assertEqual(metrics["percussion_model"], "shared-readiness-v1")
        expected_argv = [
            manifest["renderer"]["path"], "--profile", str(directory / "profile.b3p"),
            "--output", str(directory / "render.wav"), "--frames", str(parameters["frames"]),
            "--sample-rate", str(parameters["sample_rate"]),
            "--block-size", str(parameters["block_size"]), "--seed", str(parameters["seed"]),
            "--drawbars", parameters["drawbars"], "--pedal-drawbars", parameters["pedal_drawbars"],
            "--contacts", parameters["contacts"],
            "--percussion", parameters["percussion"],
            "--percussion-volume", parameters["percussion_volume"],
            "--percussion-decay", parameters["percussion_decay"], "--fail-on-clip",
        ]
        expected_argv += (["--events", str(directory / "events.txt")]
                          if parameters["event_mode"] == "file"
                          else ["--note", str(parameters["note"])])
        self.assertEqual(manifest["invocation"]["argv"], expected_argv)
        self.assertEqual(manifest["evidence_scope"], "synthetic_engineering")
        self.assertTrue(manifest["integrity_verified"])
        self.assertEqual(manifest, json.loads((directory / "manifest.json").read_text()))
        self.assertEqual(manifest["renderer_metrics"],
                         json.loads((directory / "renderer.stdout.txt").read_bytes()))
        self.assertEqual(manifest["invocation"]["returncode"], 0)
        self.assertFalse(manifest["invocation"]["timed_out"])
        self.assertIn("--fail-on-clip", manifest["invocation"]["argv"])
        self.assertEqual(manifest["renderer"]["sha256_before"], manifest["renderer"]["sha256_after"])
        self.assertEqual(manifest["git"]["binary_association"], "not_established")
        self.assertIsNone(manifest["error"])
        self.assertTrue(manifest["started_at_utc"].endswith("Z"))
        self.assertTrue(manifest["finished_at_utc"].endswith("Z"))
        records = [manifest["inputs"]["profile_json"], manifest["compiled_profile"], manifest["wav"],
                   manifest["invocation"]["stdout"], manifest["invocation"]["stderr"]]
        if manifest["inputs"]["events"]:
            records.append(manifest["inputs"]["events"])
        for record in records:
            raw = (directory / record["path"]).read_bytes()
            self.assertEqual(len(raw), record["size_bytes"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), record["sha256"])

    def test_success_invocation_resolves_output_path_aliases(self):
        # Exercise canonicalization on every runner without symlink privileges.
        # macOS /var and Windows short temporary paths exposed this same oracle
        # error: the producer records resolved paths, not the caller's spelling.
        parent = self.work / "existing parent"
        parent.mkdir()
        requested = parent / ".." / "canonical evidence"
        self.assertNotEqual(str(requested), str(requested.resolve()))
        events = self.score("0 note_on upper 69 100\n32 note_off upper 69 0\n")
        directory, manifest = self.render(output_dir=requested, events=events, frames=64)
        self.assert_success(directory, manifest)
        argv = manifest["invocation"]["argv"]
        for flag, filename in (("--profile", "profile.b3p"),
                               ("--output", "render.wav"), ("--events", "events.txt")):
            self.assertEqual(argv[argv.index(flag) + 1], str(requested.resolve() / filename))

    def test_real_render_preserves_inputs_metrics_and_independent_pcm_statistics(self):
        directory, manifest = self.render()
        self.assert_success(directory, manifest)
        self.assertEqual((directory / "profile.json").read_bytes(), self.authoring_bytes)
        self.assertEqual((directory / "profile.b3p").read_bytes(), self.expected_compiled)
        self.assertIsNone(manifest["inputs"]["events"])
        self.assertEqual(set(p.name for p in directory.iterdir()), {
            "manifest.json", "profile.json", "profile.b3p", "render.wav",
            "renderer.stdout.txt", "renderer.stderr.txt"})
        wav = (directory / "render.wav").read_bytes()
        self.assertEqual(len(wav), 44 + 259 * 4)
        self.assertEqual(struct.unpack_from("<I", wav, 4)[0], len(wav) - 8)
        self.assertEqual(struct.unpack_from("<HHIIHH", wav, 20), (1, 2, 48000, 192000, 4, 16))
        samples = struct.unpack("<" + "h" * (259 * 2), wav[44:])
        left, right = samples[::2], samples[1::2]
        self.assertEqual(left, right)
        peak = max(abs(v) for v in left) / 32768
        rms = math.sqrt(math.fsum(v * v for v in left) / len(left)) / 32768
        self.assertEqual(peak, manifest["wav"]["pcm_peak"])
        self.assertEqual(rms, manifest["wav"]["pcm_rms"])
        self.assertEqual(sum(v * v for v in left), manifest["wav"]["pcm_sum_squares_integer"])
        self.assertNotEqual(peak, manifest["renderer_metrics"]["peak"])
        self.assertTrue(manifest["metric_comparison"]["within_quantization_bound"])
        for metric in ("peak", "rms"):
            self.assertLessEqual(abs(manifest["renderer_metrics"][metric] - manifest["wav"]["pcm_" + metric]),
                                 1 / 32768 + 1e-12)

    def test_same_build_replay_is_identical_excluding_time_and_run_paths(self):
        first_dir, first = self.render(frames=1027)
        second_dir, second = self.render(frames=1027)
        self.assert_success(first_dir, first)
        self.assert_success(second_dir, second)
        for field in ("parameters", "inputs", "compiled_profile", "renderer", "renderer_metrics",
                      "wav", "metric_comparison", "environment", "limits"):
            self.assertEqual(first[field], second[field], field)
        self.assertEqual((first_dir / "render.wav").read_bytes(), (second_dir / "render.wav").read_bytes())
        self.assertNotEqual(first["started_at_utc"], second["started_at_utc"])
        changed_dir, changed = self.render(frames=1027, seed=8)
        self.assert_success(changed_dir, changed)
        self.assertNotEqual(first["wav"]["sha256"], changed["wav"]["sha256"])

    def test_real_render_with_stable_windows_metadata_preserves_crlf_inputs(self):
        profile_raw = self.authoring_bytes.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        self.profile.write_bytes(profile_raw)
        events_raw = b"0 note_on upper 60 100\r\n128 note_off upper 60 0\r\n"
        events = self.score(events_raw)

        def descriptor_info(descriptor):
            info = os.fstat(descriptor)
            return metadata(info, st_dev=0, st_ino=0, st_mode=stat.S_IFREG | 0o600,
                            st_ctime_ns=info.st_ctime_ns + 1000000)

        # Simulate stable Windows path/fd differences on every CI platform.
        with mock.patch.object(fixture, "os", wraps=os) as windows_os:
            windows_os.name = "nt"
            windows_os.fstat.side_effect = descriptor_info
            directory, manifest = self.render(events=events)
        self.assert_success(directory, manifest)
        self.assertEqual((directory / "profile.json").read_bytes(), profile_raw)
        self.assertEqual((directory / "events.txt").read_bytes(), events_raw)
        self.assertEqual((directory / "profile.b3p").read_bytes(), self.expected_compiled)

    def test_rates_partial_blocks_max_seed_and_literal_path_cli(self):
        for rate in (44100, 48000, 96000):
            with self.subTest(rate=rate):
                directory, manifest = self.render(sample_rate=rate, frames=131,
                                                  block_size=17, seed=2**64 - 1, note=96)
                self.assert_success(directory, manifest)
                self.assertEqual(manifest["wav"]["frames"], 131)
        output = self.work / "new ; $(no command) result"
        result = subprocess.run([sys.executable, str(ROOT / "tools/render_fixture.py"),
                                 "--renderer", str(self.renderer), "--output-dir", str(output),
                                 "--frames", "37", "--note", "36"],
                                cwd=self.work, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assert_success(output, json.loads((output / "manifest.json").read_bytes()))
        self.assertEqual(json.loads(result.stdout)["status"], "succeeded")

    def test_event_bytes_and_console_extensions_are_retained(self):
        raw = (b"\xef\xbb\xbf# exact UTF-8 comment: caf\xc3\xa9\r\n"
               b"0 note_on upper 60 100\r\n"
               b"64 bank_drawbar upper 11 8\r\n64 select_bank upper 0 1\r\n"
               b"127 cancel upper 0 0\r\n128 select_bank upper 0 1\r\n"
               b"258 note_off upper 60 0\r\n")
        events = self.score(raw)
        directory, manifest = self.render(events=events)
        self.assert_success(directory, manifest)
        self.assertEqual((directory / "events.txt").read_bytes(), raw)
        self.assertEqual(manifest["parameters"]["event_count"], 6)
        self.assertIsNone(manifest["parameters"]["note"])
        self.assertNotIn("--note", manifest["invocation"]["argv"])
        self.assertEqual(manifest["inputs"]["events"]["sha256"], hashlib.sha256(raw).hexdigest())

    def test_default_console_options_preserve_legacy_flag_audio_and_metrics(self):
        implicit_dir, implicit = self.render(frames=1027)
        explicit_dir, explicit = self.render(
            frames=1027, contacts="ideal", percussion="off",
            percussion_volume="normal", percussion_decay="slow")
        self.assert_success(implicit_dir, implicit)
        self.assert_success(explicit_dir, explicit)
        self.assertEqual(implicit["parameters"], {
            "frames": 1027, "sample_rate": 48000, "block_size": 64, "seed": 7,
            "drawbars": "008000000", "pedal_drawbars": "00", "note": 60, "event_mode": "default_note",
            "event_count": None, "contacts": "ideal", "percussion": "off",
            "percussion_volume": "normal", "percussion_decay": "slow", "fail_on_clip": True,
        })
        direct_wav = self.work / "legacy flags.wav"
        result = subprocess.run([
            str(self.renderer), "--profile", str(implicit_dir / "profile.b3p"),
            "--output", str(direct_wav), "--frames", "1027", "--sample-rate", "48000",
            "--block-size", "64", "--seed", "7", "--drawbars", "008000000",
            "--fail-on-clip", "--note", "60",
        ], capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.assertEqual(implicit["renderer_metrics"], json.loads(result.stdout))
        self.assertEqual(implicit["renderer_metrics"], explicit["renderer_metrics"])
        self.assertEqual((implicit_dir / "render.wav").read_bytes(), direct_wav.read_bytes())
        self.assertEqual((explicit_dir / "render.wav").read_bytes(), direct_wav.read_bytes())

    def test_all_console_combinations_bind_flags_models_and_audible_controls(self):
        rendered = {}
        frames = 2049
        for contacts, percussion, volume, decay in itertools.product(
                ("ideal", "nominal"), ("off", "second", "third"),
                ("normal", "soft"), ("slow", "fast")):
            with self.subTest(contacts=contacts, percussion=percussion, volume=volume, decay=decay):
                options = dict(contacts=contacts, percussion=percussion,
                               percussion_volume=volume, percussion_decay=decay)
                directory, manifest = self.render(frames=frames, drawbars="000000000", **options)
                self.assert_success(directory, manifest)
                for key, value in options.items():
                    self.assertEqual(manifest["parameters"][key], value)
                raw = (directory / "render.wav").read_bytes()
                samples = struct.unpack("<" + "h" * (frames * 2), raw[44:])[::2]
                rendered[contacts, percussion, volume, decay] = samples
                if percussion == "off":
                    self.assertFalse(any(samples))
                    self.assertEqual(manifest["wav"]["pcm_peak_integer"], 0)
                else:
                    self.assertTrue(any(samples[256:1024]))
                    if contacts == "nominal":
                        # Independent factory timing: 8 ms full travel; harmonic
                        # contact 3 closes at .42 and contact 4 at .52.
                        threshold = .42 if percussion == "second" else .52
                        first_frame = math.ceil(threshold * .008 * 48000)
                        self.assertFalse(any(samples[:first_frame]))
                        self.assertTrue(any(samples[first_frame:first_frame + 64]))
        for contacts, harmonic, decay in itertools.product(
                ("ideal", "nominal"), ("second", "third"), ("slow", "fast")):
            normal = rendered[contacts, harmonic, "normal", decay]
            soft = rendered[contacts, harmonic, "soft", decay]
            # With sustained drawbars zero, Soft changes only the documented
            # 0.5 percussion amplitude; PCM rounding permits one integer step.
            self.assertLessEqual(max(abs(2 * s - n) for s, n in zip(soft, normal)), 1)
            self.assertNotEqual(normal, rendered[contacts, harmonic, "normal",
                                                 "fast" if decay == "slow" else "slow"])
        self.assertNotEqual(rendered["ideal", "second", "normal", "slow"],
                            rendered["ideal", "third", "normal", "slow"])

    def test_percussion_score_controls_retain_bytes_and_override_initial_controls(self):
        prefix = (b"\xef\xbb\xbf# exact controls\r\n0 percussion upper 0 1.0\r\n"
                  b"0 percussion upper 1 1e0\r\n0 percussion upper 2 +1\r\n"
                  b"0 percussion upper 3 01\r\n")
        notes = b"0 note_on upper 60 100\r\n768 note_off upper 60 0\r\n"
        events = self.score(prefix + notes)
        first_dir, first = self.render(events=events, frames=1027,
                                       contacts="nominal", drawbars="000000000")
        self.assert_success(first_dir, first)
        self.assertEqual((first_dir / "events.txt").read_bytes(), prefix + notes)
        self.assertEqual(first["parameters"]["event_count"], 6)
        self.assertEqual(first["parameters"]["percussion"], "off")
        self.assertGreater(first["wav"]["pcm_peak_integer"], 0)
        second_dir, second = self.render(
            events=self.score(notes), frames=1027, contacts="nominal", drawbars="000000000",
            percussion="third", percussion_volume="soft", percussion_decay="fast")
        self.assert_success(second_dir, second)
        self.assertEqual((first_dir / "render.wav").read_bytes(),
                         (second_dir / "render.wav").read_bytes())
        self.assertEqual(first["renderer_metrics"], second["renderer_metrics"])
        muted_dir, muted = self.render(
            events=self.score(b"0 percussion upper 0 0e0\n" + notes), frames=1027,
            contacts="nominal", drawbars="000000000", percussion="third")
        self.assert_success(muted_dir, muted)
        self.assertEqual(muted["parameters"]["percussion"], "third")
        self.assertEqual(muted["wav"]["pcm_peak_integer"], 0)

    def test_nominal_console_score_replays_across_partitions_and_sample_rates(self):
        events = self.score(
            "0 note_on upper 60 100\n257 note_on upper 64 5\n"
            "400 percussion upper 1 1\n511 note_off upper 60 0\n"
            "511 note_on upper 60 127\n512 cancel upper 0 0\n"
            "600 percussion upper 2 1\n600 select_bank upper 0 1\n"
            "701 note_off upper 64 0\n901 note_off upper 60 0\n"
            "1100 note_on upper 60 1\n1300 percussion upper 3 1\n")
        for rate in (44100, 48000, 96000):
            reference = None
            for block in (1, 17, 64, 257):
                with self.subTest(rate=rate, block=block):
                    directory, manifest = self.render(
                        events=events, frames=1537, sample_rate=rate, block_size=block,
                        contacts="nominal", percussion="second", drawbars="008000008")
                    self.assert_success(directory, manifest)
                    self.assertEqual(manifest["parameters"]["event_count"], 12)
                    raw = (directory / "render.wav").read_bytes()
                    metrics = dict(manifest["renderer_metrics"])
                    metrics.pop("block_size")
                    observed = (raw, metrics)
                    if reference is None:
                        reference = observed
                    self.assertEqual(observed, reference)

    def test_invalid_console_api_choices_fail_before_launch_or_directory_creation(self):
        choices = {
            "contacts": ("ideal", "nominal"), "percussion": ("off", "second", "third"),
            "percussion_volume": ("normal", "soft"), "percussion_decay": ("slow", "fast"),
        }
        for key, accepted in choices.items():
            invalid = (None, True, False, 0, 1.0, float("nan"), b"nominal", [], {},
                       "", "unknown", accepted[0].upper(), " " + accepted[0], accepted[0] + " ")
            for value in invalid:
                with self.subTest(key=key, value=value):
                    output = self.new_output()
                    with mock.patch.object(fixture, "_invoke") as invoked:
                        with self.assertRaisesRegex(fixture.FixtureError, key):
                            self.render(output_dir=output, **{key: value})
                        invoked.assert_not_called()
                    self.assertFalse(output.exists())

    def test_invalid_percussion_score_is_rejected_before_launch_or_creation(self):
        malformed = [
            "0 percussion lower 0 1", "0 percussion upper 4 0", "0 percussion upper 0 2",
            "0 percussion upper 0 -1", "0 percussion upper 0 .5", "0 percussion upper 0 nan",
            "0 percussion upper 0 inf", "0 percussion upper 0 1e999",
            "0 percussion upper 0 1e-999", "0 percussion upper +0 1",
            "0 percussion upper 1.0 1", "0 percussion upper -1 1",
            "0 Percussion upper 0 1", "0 percussion Upper 0 1", "0 percussion upper 0 1 extra",
            "259 percussion upper 0 1", "1 percussion upper 0 1\n0 percussion upper 0 0",
        ]
        malformed += [f"0 percussion upper {index} {value}"
                      for index in range(4) for value in ("1.000001", "-0.000001")]
        for raw in malformed:
            with self.subTest(raw=raw):
                output = self.new_output()
                events = self.score(raw + "\n")
                with mock.patch.object(fixture, "_invoke") as invoked:
                    with self.assertRaises(fixture.FixtureError):
                        self.render(output_dir=output, events=events)
                    invoked.assert_not_called()
                self.assertFalse(output.exists())

    def test_console_cli_choices_are_forwarded_and_strictly_parsed(self):
        output = self.new_output()
        arguments = [sys.executable, str(ROOT / "tools/render_fixture.py"),
                     "--renderer", str(self.renderer), "--profile-json", str(self.profile),
                     "--output-dir", str(output), "--frames", "1027", "--seed", "7",
                     "--drawbars", "000000000", "--contacts", "nominal", "--percussion", "third",
                     "--percussion-volume", "soft", "--percussion-decay", "fast"]
        result = subprocess.run(arguments, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        manifest = json.loads((output / "manifest.json").read_bytes())
        self.assert_success(output, manifest)
        self.assertGreater(manifest["wav"]["pcm_peak_integer"], 0)
        for field, value in (("contacts", "nominal"), ("percussion", "third"),
                             ("percussion_volume", "soft"), ("percussion_decay", "fast")):
            self.assertEqual(manifest["parameters"][field], value)
        invalid = []
        for flag, value in (("--contacts", "nominal"), ("--percussion", "third"),
                            ("--percussion-volume", "soft"), ("--percussion-decay", "fast")):
            invalid += [[flag], [flag, "unknown"], [flag, value.upper()],
                        [flag, value, flag, value]]
        invalid += [["--contact", "nominal"], ["--percussion-v", "soft"],
                    ["--percussion-d", "fast"], ["--contacts=nominal", "--contacts", "nominal"]]
        for suffix in invalid:
            with self.subTest(suffix=suffix):
                output = self.new_output()
                result = subprocess.run([
                    sys.executable, str(ROOT / "tools/render_fixture.py"),
                    "--renderer", str(self.renderer), "--output-dir", str(output), *suffix,
                ], capture_output=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr)
                self.assertFalse(result.stdout)
                self.assertFalse(output.exists())

    def test_wrong_console_metrics_are_retained_as_failed_evidence(self):
        invoke = fixture._invoke
        mutations = [("render_schema_version", value) for value in (1, 2, 4, 3.0, True, "3", None)]
        mutations += [("contact_model", value) for value in
                      ("ideal-contacts-v1", "unknown", True, None)]
        mutations += [("percussion_model", value) for value in
                      ("per-note-envelope-v1", "unknown", 1, None)]
        mutations += [("remove", key) for key in
                      ("render_schema_version", "contact_model", "percussion_model")]
        mutations += [("extra", "console_model"), ("legacy", None)]
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                captured = {}

                def alter(argv, cwd, timeout):
                    status, stdout, stderr = invoke(argv, cwd, timeout)
                    if "--fail-on-clip" in argv:
                        metrics = json.loads(stdout)
                        if key == "remove":
                            metrics.pop(value)
                        elif key == "extra":
                            metrics[value] = "unknown"
                        elif key == "legacy":
                            for field in ("render_schema_version", "contact_model", "percussion_model"):
                                metrics.pop(field)
                        else:
                            metrics[key] = value
                        stdout = (json.dumps(metrics) + "\n").encode()
                        captured.update(metrics=metrics, stdout=stdout)
                    return status, stdout, stderr

                with mock.patch.object(fixture, "_invoke", side_effect=alter):
                    directory, manifest = self.render(contacts="nominal", percussion="second")
                self.assertEqual(manifest["status"], "failed")
                self.assertEqual(manifest["error"]["stage"], "metrics")
                self.assertTrue(manifest["error"]["message"])
                self.assertEqual(manifest["invocation"]["returncode"], 0)
                self.assertIsNone(manifest["wav"])
                self.assertEqual(manifest["renderer_metrics"], captured["metrics"])
                self.assertEqual((directory / "renderer.stdout.txt").read_bytes(), captured["stdout"])
                record = manifest["invocation"]["stdout"]
                self.assertEqual(record["sha256"], hashlib.sha256(captured["stdout"]).hexdigest())
                self.assertEqual(record["size_bytes"], len(captured["stdout"]))
                self.assertEqual(manifest, json.loads((directory / "manifest.json").read_bytes()))

    def test_invalid_preflight_never_creates_result(self):
        invalid = [dict(frames=0), dict(frames=48000 * 600 + 1), dict(sample_rate=22050),
                   dict(block_size=65537), dict(block_size=True), dict(seed=-1),
                   dict(seed=2**64), dict(note=35), dict(drawbars="888888889"),
                   dict(drawbars="\u0668" * 9), dict(timeout_seconds=0),
                   dict(renderer=self.work / "missing"), dict(profile_json=self.work)]
        for changes in invalid:
            with self.subTest(changes=changes):
                output = self.new_output()
                with self.assertRaises((fixture.FixtureError, OSError)):
                    self.render(output_dir=output, **changes)
                self.assertFalse(output.exists())
        events = self.score("0 note_on upper 60 100\n")
        output = self.new_output()
        with self.assertRaisesRegex(fixture.FixtureError, "incompatible"):
            self.render(output_dir=output, events=events, note=60)
        self.assertFalse(output.exists())
        missing_parent = self.work / "absent" / "child"
        with self.assertRaisesRegex(fixture.FixtureError, "parent"):
            self.render(output_dir=missing_parent)
        self.assertFalse(missing_parent.parent.exists())

    def test_malformed_authoring_and_event_inputs_fail_before_creation(self):
        for raw in (b"{}", b"{\"a\":1,\"a\":2}", b"\xff", b"[" * 3000,
                    b" " * (fixture.profile_compiler.MAX_INPUT_BYTES + 1)):
            self.profile.write_bytes(raw)
            output = self.new_output()
            with self.assertRaises(fixture.FixtureError):
                self.render(output_dir=output)
            self.assertFalse(output.exists())
        self.profile.write_bytes(self.authoring_bytes)
        malformed = ["259 note_on upper 60 100\n", "1 note_on upper 60 100\n0 cancel upper 0 0\n",
                     "0 note_on upper 60 1 extra", "0 expression upper 0 nan", "0 expression upper 0 1e-999",
                     "0 select_bank upper 0 2", "0 bank_drawbar upper 18 8", "0 cancel upper 0 1",
                     "0 note_on\u00a0upper 60 100", "0 expression upper 0 1\n" * 1025,
                     b"#bad\xff", b"#nul\x00", b"#" + b"x" * 4096]
        for raw in malformed:
            with self.subTest(prefix=repr(raw[:50])):
                events = self.score(raw)
                output = self.new_output()
                with self.assertRaises(fixture.FixtureError):
                    self.render(output_dir=output, events=events)
                self.assertFalse(output.exists())

    def test_existing_output_directory_and_file_are_untouched(self):
        directory = self.new_output()
        directory.mkdir()
        sentinel = directory / "manifest.json"
        sentinel.write_bytes(b"previous retained evidence")
        original_time = sentinel.stat().st_mtime_ns
        with self.assertRaisesRegex(fixture.FixtureError, "already exists"):
            self.render(output_dir=directory)
        self.assertEqual(list(directory.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_bytes(), b"previous retained evidence")
        self.assertEqual(sentinel.stat().st_mtime_ns, original_time)
        with self.assertRaisesRegex(fixture.FixtureError, "already exists"):
            self.render(output_dir=sentinel)
        self.assertEqual(sentinel.read_bytes(), b"previous retained evidence")

    def test_real_clipping_retains_failed_status_metrics_and_logs_without_wav(self):
        lines = [f"0 drawbar lower {drawbar} 8\n" for drawbar in range(9)]
        lines += [f"0 note_on {manual} {note} 127\n"
                  for manual in ("upper", "lower") for note in range(36, 97)]
        directory, manifest = self.render(events=self.score("".join(lines)), drawbars="888888888")
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["invocation"]["returncode"], 2)
        self.assertEqual(manifest["renderer_metrics"]["status"], "clipped")
        self.assertGreater(manifest["renderer_metrics"]["clipped_frames"], 0)
        self.assertGreater(manifest["renderer_metrics"]["peak"], 1)
        self.assertIn("clipping", (directory / "renderer.stderr.txt").read_text())
        self.assertIsNone(manifest["wav"])
        self.assertFalse((directory / "render.wav").exists())
        self.assertEqual(manifest, json.loads((directory / "manifest.json").read_bytes()))
        output = self.new_output()
        result = subprocess.run([sys.executable, str(ROOT / "tools/render_fixture.py"),
                                 "--renderer", str(self.renderer), "--output-dir", str(output),
                                 "--events", str(self.score("".join(lines))), "--frames", "259",
                                 "--drawbars", "888888888", "--seed", "7"],
                                capture_output=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(result.stdout)
        self.assertIn(b"failed", result.stderr)
        self.assertEqual(json.loads((output / "manifest.json").read_bytes())["status"], "failed")

    def test_modified_sources_copies_and_executable_cannot_be_success(self):
        invoke = fixture._invoke
        events = self.score("0 note_on upper 60 100\n")
        original_hash = hashlib.sha256(self.renderer.read_bytes()).hexdigest()
        targets = ("profile.json", "profile.b3p", "events.txt", "source_profile", "source_events", "renderer")
        for target in targets:
            with self.subTest(target=target):
                self.profile.write_bytes(self.authoring_bytes)
                events.write_text("0 note_on upper 60 100\n")
                executable = self.work / f"renderer copy {target}"
                shutil.copy2(self.renderer, executable)
                if target == "renderer":
                    # Alter a separate file, then replace the checked path. Writing
                    # directly to an execution image can fail before the hash check.
                    replacement = self.work / "changed renderer"
                    shutil.copy2(executable, replacement)
                    with replacement.open("ab") as changed:
                        changed.write(b"\n")
                    changed_hash = hashlib.sha256(replacement.read_bytes()).hexdigest()
                    self.assertNotEqual(original_hash, changed_hash)
                output = self.new_output()
                observed = {}

                def alter(argv, cwd, timeout):
                    result = invoke(argv, cwd, timeout)
                    if "--fail-on-clip" in argv:
                        observed.update(result=result[0], stdout=result[1], stderr=result[2])
                        if target == "renderer":
                            replacement.replace(executable)
                        else:
                            path = {"source_profile": self.profile, "source_events": events}.get(
                                target, output / target)
                            with path.open("ab") as changed:
                                changed.write(b"\n")
                    return result

                with mock.patch.object(fixture, "_invoke", side_effect=alter):
                    _, manifest = self.render(output_dir=output, events=events, renderer=executable)
                diagnostic = {"error": manifest["error"], "invocation": manifest["invocation"],
                              "renderer": manifest["renderer"], "observed": observed}
                self.assertEqual(manifest["status"], "failed", diagnostic)
                self.assertEqual(manifest["error"]["stage"], "integrity", diagnostic)
                self.assertEqual(manifest["invocation"]["returncode"], 0, diagnostic)
                for flag in ("timed_out", "stdout_truncated", "stderr_truncated",
                             "capture_incomplete", "capture_errors"):
                    self.assertFalse(manifest["invocation"][flag], diagnostic)
                self.assertFalse(manifest["integrity_verified"], diagnostic)
                self.assertIsNone(manifest["wav"], diagnostic)
                self.assertEqual(manifest, json.loads((output / "manifest.json").read_bytes()))
                if target == "renderer":
                    self.assertEqual(manifest["renderer"]["sha256_before"], original_hash, diagnostic)
                    self.assertEqual(manifest["renderer"]["sha256_after"], changed_hash, diagnostic)
                    self.assertEqual(hashlib.sha256(executable.read_bytes()).hexdigest(), changed_hash)

    def test_corrupt_wav_or_metrics_are_failed_and_not_verified(self):
        invoke = fixture._invoke
        for kind in ("header", "channel", "truncated", "metrics", "nonfinite_metrics",
                     "quantization", "nested_metrics", "oversized_metrics"):
            with self.subTest(kind=kind):
                output = self.new_output()

                def alter(argv, cwd, timeout):
                    status, stdout, stderr = invoke(argv, cwd, timeout)
                    if "--fail-on-clip" in argv:
                        path = output / "render.wav"
                        wav = bytearray(path.read_bytes())
                        if kind == "header":
                            struct.pack_into("<I", wav, 24, 44100)
                        elif kind == "channel":
                            wav[46] ^= 1
                        elif kind == "truncated":
                            wav = wav[:-4]
                        elif kind == "metrics":
                            metrics = json.loads(stdout)
                            metrics["frames"] += 1
                            stdout = json.dumps(metrics).encode()
                        elif kind == "quantization":
                            metrics = json.loads(stdout)
                            metrics["peak"] = metrics["rms"] = 0
                            stdout = json.dumps(metrics).encode()
                        elif kind == "nested_metrics":
                            stdout = b'{"peak":[[[[0]]]]}'
                        elif kind == "oversized_metrics":
                            stdout = b'{"extra":"' + b'x' * fixture.MAX_METRICS_BYTES + b'"}'
                        else:
                            stdout = b'{"peak":1e999}'
                        path.write_bytes(wav)
                    return status, stdout, stderr

                with mock.patch.object(fixture, "_invoke", side_effect=alter):
                    _, manifest = self.render(output_dir=output)
                self.assertEqual(manifest["status"], "failed")
                self.assertIsNone(manifest["wav"])
                self.assertIn(manifest["error"]["stage"], ("wav", "metrics"))

    def test_process_launch_failure_is_retained_without_fake_metrics(self):
        invalid = self.work / "invalid executable"
        invalid.write_bytes(b"this is not an executable\n")
        invalid.chmod(0o700)
        directory, manifest = self.render(renderer=invalid)
        self.assertEqual(manifest["status"], "failed")
        self.assertIsNone(manifest["invocation"]["returncode"])
        self.assertIsNone(manifest["renderer_metrics"])
        self.assertIsNone(manifest["wav"])
        self.assertTrue((directory / "manifest.json").is_file())

    def test_bounded_subprocess_time_and_log_capture(self):
        result, stdout, _ = fixture._invoke(
            [sys.executable, "-c", "import sys,time; sys.stdout.buffer.write(b'started\\n'); "
             "sys.stdout.buffer.flush(); time.sleep(20)"],
            self.work, 1)
        self.assertTrue(result["timed_out"])
        self.assertNotEqual(result["returncode"], 0)
        self.assertEqual(stdout, b"started\n")
        result, stdout, stderr = fixture._invoke(
            [sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'raw\\r\\n\\x1a'); "
             "sys.stderr.buffer.write(b'error\\r\\n')"], self.work, 5)
        self.assertEqual(result["returncode"], 0)
        self.assertEqual(stdout, b"raw\r\n\x1a")
        self.assertEqual(stderr, b"error\r\n")
        with mock.patch.object(fixture, "MAX_LOG_BYTES", 4096):
            result, stdout, _ = fixture._invoke(
                [sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'x'*100000); sys.stdout.flush()"],
                self.work, 5)
        self.assertTrue(result["stdout_truncated"])
        self.assertEqual(stdout, b"x" * 4096)

    def test_cli_rejects_bad_duplicate_and_conflicting_options_without_directory(self):
        for suffix in (["--frames", "+1"], ["--frames", "1e2"], ["--frames", "1", "--frames", "1"],
                       ["--seed", str(2**64)], ["--unknown"], ["--note", "60", "--events", str(self.score(""))]):
            output = self.new_output()
            result = subprocess.run([sys.executable, str(ROOT / "tools/render_fixture.py"),
                                     "--renderer", str(self.renderer), "--output-dir", str(output), *suffix],
                                    capture_output=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())
            self.assertTrue(result.stderr)

    def test_missing_prerequisite_helper_has_clear_failure(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "Missing prerequisite HAMMOND_TEST_PROFILE"):
                required_file("HAMMOND_TEST_PROFILE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
