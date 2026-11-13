#!/usr/bin/env python3
"""Real-renderer evidence tests; missing build prerequisites are explicit failures.

CTest supplies HAMMOND_RENDER_EXECUTABLE and HAMMOND_TEST_PROFILE. Direct use:
  HAMMOND_RENDER_EXECUTABLE=/path/hammond_render \
  HAMMOND_TEST_PROFILE=/path/nominal.b3p python3 tests/test_render_fixture.py
"""

import hashlib
import importlib.util
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
        self.assertEqual(manifest["status"], "succeeded", manifest.get("error"))
        self.assertEqual(manifest["schema_version"], 1)
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
        executable = self.work / "renderer copy"
        shutil.copy2(self.renderer, executable)
        targets = ("profile.json", "profile.b3p", "events.txt", "source_profile", "source_events", "renderer")
        for target in targets:
            with self.subTest(target=target):
                self.profile.write_bytes(self.authoring_bytes)
                events.write_text("0 note_on upper 60 100\n")
                shutil.copy2(self.renderer, executable)
                output = self.new_output()

                def alter(argv, cwd, timeout):
                    result = invoke(argv, cwd, timeout)
                    if "--fail-on-clip" in argv:
                        path = {"source_profile": self.profile, "source_events": events,
                                "renderer": executable}.get(target, output / target)
                        with path.open("ab") as changed:
                            changed.write(b"\n")
                    return result

                with mock.patch.object(fixture, "_invoke", side_effect=alter):
                    _, manifest = self.render(output_dir=output, events=events, renderer=executable)
                self.assertEqual(manifest["status"], "failed")
                self.assertEqual(manifest["error"]["stage"], "integrity")
                self.assertFalse(manifest["integrity_verified"])
                self.assertIsNone(manifest["wav"])
                self.assertEqual(manifest, json.loads((output / "manifest.json").read_bytes()))
                if target == "renderer":
                    self.assertNotEqual(manifest["renderer"]["sha256_before"], manifest["renderer"]["sha256_after"])

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
