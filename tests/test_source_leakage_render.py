#!/usr/bin/env python3
"""Independent process/filesystem acceptance of the optional leakage audition.

Use HAMMOND_RENDER_EXECUTABLE and HAMMOND_TEST_PROFILE to select a coherent
built renderer/profile. Missing inputs fail. All fixtures live in private
temporary directories; repository inputs and preexisting outputs are preserved.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import stat
import struct
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(os.environ.get("HAMMOND_SOURCE_DIR", Path(__file__).resolve().parents[1]))
BASE_KEYS = {
    "status", "model", "render_schema_version", "contact_model", "percussion_model",
    "pedal_routing_model", "pedal_voice_model", "pedal_gain_law", "pedal_contact_model",
    "pedal_map_id", "pedal_map_raw_sha256", "pedal_map_canonical_sha256",
    "pedal_reference_a_sha256", "pedal_reference_b_sha256", "pedal_mixture_matrix",
    "pedal_mixture_denominator", "pedal_gain_denominator", "pedal_weight_policy",
    "evidence_status", "profile_id", "authoring_sha256", "sample_rate", "block_size",
    "frames", "seed", "channels", "sample_format", "peak", "rms", "clipped_frames",
    "clipped_channel_samples",
}
LEAKAGE_KEYS = {
    "source_leakage_model", "source_leakage_integration", "source_leakage_profile_id",
    "source_leakage_authoring_sha256", "source_leakage_evidence_status",
    "source_leakage_boundary", "source_leakage_source_content", "source_leakage_input_gain",
    "source_leakage_edge_count", "source_leakage_maximum_row_absolute_gain_sum",
    "source_leakage_guarded_output_bound", "source_leakage_identity_bypass",
}


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate receipt key: {key}")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError(f"nonfinite JSON constant: {value}")


def receipt(text):
    return json.loads(text, object_pairs_hook=strict_object, parse_constant=invalid_constant)


def required_file(value, fallback, label):
    path = Path(value) if value is not None else fallback
    if not path.is_file():
        raise RuntimeError(f"Missing {label}: {path}; build matching inputs before testing")
    return path.resolve()


class DirectoryCreates:
    """Optional Linux observation of actual creation, not directory timestamps."""

    def __init__(self, directory):
        self.fd = None
        if not sys.platform.startswith("linux"):
            return
        libc = ctypes.CDLL(None, use_errno=True)
        libc.inotify_init1.argtypes = [ctypes.c_int]
        libc.inotify_init1.restype = ctypes.c_int
        libc.inotify_add_watch.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
        libc.inotify_add_watch.restype = ctypes.c_int
        descriptor = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
        if descriptor < 0:
            raise OSError(ctypes.get_errno(), "inotify_init1")
        if libc.inotify_add_watch(descriptor, os.fsencode(directory), 0x100 | 0x80) < 0:
            os.close(descriptor)
            raise OSError(ctypes.get_errno(), "inotify_add_watch")
        self.fd = descriptor

    def finish(self):
        if self.fd is None:
            return None
        names = []
        try:
            while True:
                try:
                    block = os.read(self.fd, 65536)
                except BlockingIOError:
                    break
                if not block:
                    break
                offset = 0
                while offset < len(block):
                    _watch, mask, _cookie, length = struct.unpack_from("iIII", block, offset)
                    if mask & 0x4000:
                        raise RuntimeError("directory observation overflowed")
                    offset += 16
                    names.append(os.fsdecode(block[offset:offset + length].split(b"\0", 1)[0]))
                    offset += length
        finally:
            os.close(self.fd)
            self.fd = None
        return names


class SourceLeakageRendererTests(unittest.TestCase):
    calls = 0
    setup_watches = 0

    @classmethod
    def setUpClass(cls):
        name = "hammond_render.exe" if os.name == "nt" else "hammond_render"
        cls.renderer = required_file(os.environ.get("HAMMOND_RENDER_EXECUTABLE"),
                                     ROOT / "build" / name, "renderer")
        cls.compiled_profile = required_file(os.environ.get("HAMMOND_TEST_PROFILE"),
                                             cls.renderer.parent / "nominal.b3p", "profile")
        cls.profile_bytes = cls.compiled_profile.read_bytes()
        cls.fixture_bytes = {}
        cls.author_bytes = {}
        with tempfile.TemporaryDirectory(prefix="hammond-leakage-cli-setup-") as folder:
            for short, identity in (("pair", "synthetic-pair-demo-v1"),
                                    ("empty", "synthetic-identity-v1")):
                author = ROOT / "data" / "source-leakage" / f"{identity}.json"
                cls.author_bytes[short] = author.read_bytes()
                compiled = Path(folder) / f"{short}.b3leakage"
                result = subprocess.run(
                    [sys.executable, "-B", str(ROOT / "tools" / "compile_source_leakage.py"),
                     "--input", str(author), "--output", str(compiled)],
                    capture_output=True, text=True, encoding="utf-8", timeout=20, check=False)
                if result.returncode != 0:
                    raise RuntimeError(result.stdout + result.stderr)
                cls.fixture_bytes[short] = compiled.read_bytes()

    @classmethod
    def tearDownClass(cls):
        print(f"leakage renderer: {cls.calls} actual invocations; "
              f"{cls.setup_watches} Linux setup-creation observations")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-leakage-cli-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.profile = self.work / "organ profile ü.b3p"
        self.profile.write_bytes(self.profile_bytes)
        self.graphs = {}
        for name in ("pair", "empty"):
            graph = self.work / f"{name} graph Ω.b3leakage"
            graph.write_bytes(self.fixture_bytes[name])
            self.graphs[name] = graph
            (self.work / f"{name} original.json").write_bytes(self.author_bytes[name])
        self.serial = 0

    def unique(self, suffix="wav"):
        self.serial += 1
        return self.work / f"result {self.serial}.{suffix}"

    def snapshot(self):
        result = {}
        for path in self.work.rglob("*"):
            info = path.lstat()
            key = str(path.relative_to(self.work))
            if stat.S_ISLNK(info.st_mode):
                result[key] = ("symlink", os.readlink(path))
            elif stat.S_ISREG(info.st_mode):
                result[key] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
            else:
                result[key] = ("other", stat.S_IFMT(info.st_mode))
        return result

    def arguments(self, output, *, graph="pair", gain="0.5", frames=2048,
                  rate=48000, block=64, score=None, drawbars="008000000", extra=()):
        args = ["--profile", self.profile, "--output", output, "--frames", frames,
                "--sample-rate", rate, "--block-size", block, "--seed", 13,
                "--drawbars", drawbars]
        args += ["--events", score] if score is not None else ["--note", 48]
        if graph is not None:
            args += ["--source-leakage", self.graphs.get(graph, graph),
                     "--leakage-input-gain", gain]
        return args + list(extra)

    def invoke(self, args, **kwargs):
        type(self).calls += 1
        return subprocess.run([str(self.renderer), *map(str, args)], cwd=self.work,
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=30, check=False, **kwargs)

    def rejected(self, args, message=None, *, observe_setup=True, **kwargs):
        before = self.snapshot()
        watcher = DirectoryCreates(self.work) if observe_setup else None
        try:
            result = self.invoke(args, **kwargs)
        finally:
            names = watcher.finish() if watcher is not None else None
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr.strip())
        if message is not None:
            self.assertIn(message, result.stderr)
        self.assertEqual(self.snapshot(), before, "Rejected call changed inputs/output/temp files")
        if names is not None:
            type(self).setup_watches += 1
            self.assertEqual(names, [], "Rejected setup created a file or temporary directory")
        return result

    def rendered(self, **kwargs):
        output = self.unique()
        before = self.snapshot()
        result = self.invoke(self.arguments(output, **kwargs))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        after = self.snapshot()
        self.assertEqual(set(after) - set(before), {output.name})
        self.assertEqual({key: after[key] for key in before}, before)
        data = output.read_bytes()
        report = receipt(result.stdout)
        self.assertEqual(len(data), 44 + report["frames"] * 4)
        self.assertEqual(data[:4], b"RIFF")
        self.assertEqual(data[8:12], b"WAVE")
        samples = struct.unpack_from(f"<{report['frames'] * 2}h", data, 44)
        self.assertEqual(samples[::2], samples[1::2])
        return data, report

    def score(self, contents):
        path = self.unique("events")
        path.write_text(contents, encoding="utf-8", newline="\n")
        return path

    def test_default_schema_and_exact_empty_identity(self):
        score = self.score("0 drawbar lower 3 5\n0 note_on upper 48 100\n"
                           "0 note_on lower 60 100\n0 percussion upper 0 1\n"
                           "0 pedal_drawbar lower 0 8\n0 pedal_on lower 1 127\n"
                           "73 expression upper 0 0.5\n99 cancel upper 0 0\n"
                           "131 select_bank upper 0 1\n180 note_off lower 60 0\n")
        for rate in (44100, 48000, 96000):
            for contacts in ("ideal", "nominal"):
                with self.subTest(rate=rate, contacts=contacts):
                    settings = dict(frames=257, rate=rate, score=score,
                                    extra=("--contacts", contacts))
                    default, base = self.rendered(graph=None, **settings)
                    empty, selected = self.rendered(graph="empty", gain="1", **settings)
                    self.assertEqual(default, empty)
                    self.assertEqual(set(base), BASE_KEYS)
                    self.assertEqual(set(selected), BASE_KEYS | LEAKAGE_KEYS)
                    self.assertEqual(base["render_schema_version"], 3)
                    self.assertEqual(selected["render_schema_version"], 5)
                    for key in BASE_KEYS - {"render_schema_version"}:
                        self.assertEqual(selected[key], base[key], key)
                    self.assertIs(selected["source_leakage_identity_bypass"], True)
                    self.assertEqual(selected["source_leakage_guarded_output_bound"], 1)

    def test_exact_schema5_facts_and_gain_matched_difference(self):
        actual, report = self.rendered()
        identity, reference = self.rendered(graph="empty", gain="0.5")
        expected = {
            "source_leakage_model": "static-source-leakage-v1",
            "source_leakage_integration": "source-leakage-audition-v1",
            "source_leakage_profile_id": "synthetic-pair-demo-v1",
            "source_leakage_authoring_sha256": hashlib.sha256(self.author_bytes["pair"]).hexdigest(),
            "source_leakage_evidence_status": "synthetic",
            "source_leakage_boundary": "normalized-generator-precontact-v1",
            "source_leakage_source_content": "excludes-leakage",
            "source_leakage_input_gain": 0.5, "source_leakage_edge_count": 2,
            "source_leakage_maximum_row_absolute_gain_sum": 0.0625,
            "source_leakage_guarded_output_bound": float.fromhex("0x1.1000000000041p-1"),
            "source_leakage_identity_bypass": False,
        }
        self.assertEqual(set(report), BASE_KEYS | LEAKAGE_KEYS)
        self.assertEqual({key: report[key] for key in LEAKAGE_KEYS}, expected)
        self.assertIs(report["source_leakage_identity_bypass"], False)
        self.assertIs(type(report["source_leakage_edge_count"]), int)
        self.assertEqual(report["model"], "ideal-shared-sine-v1")
        self.assertEqual(report["evidence_status"], "unmeasured")
        self.assertEqual(report["source_leakage_input_gain"], reference["source_leakage_input_gain"])
        self.assertNotEqual(actual, identity)
        self.assertGreater(report["peak"], 0)
        self.assertGreater(reference["peak"], 0)
        self.assertEqual(report["clipped_frames"], 0)

    def test_nonempty_partition_equivalence(self):
        first, _ = self.rendered(block=1)
        for block in (17, 257, 4096):
            with self.subTest(block=block):
                data, _ = self.rendered(block=block)
                self.assertEqual(data, first)

    def test_valid_decimal_forms_and_zero_silence(self):
        for gain in (".5", "+0.5", "5e-1", "0.5000"):
            with self.subTest(gain=gain):
                _, report = self.rendered(gain=gain, frames=64)
                self.assertEqual(report["source_leakage_input_gain"], 0.5)
        for gain in ("0", "-0", "0e9999", "4.9406564584124654e-324"):
            with self.subTest(gain=gain):
                data, report = self.rendered(gain=gain, frames=64)
                self.assertEqual(data[44:], bytes(64 * 4))
                self.assertEqual(report["peak"], 0)
                self.assertEqual(report["rms"], 0)
                self.assertFalse(report["source_leakage_identity_bypass"])
                self.assertTrue(math.isfinite(report["source_leakage_guarded_output_bound"]))

    def test_paired_duplicate_missing_unknown_and_argument_limits(self):
        base = self.arguments(self.unique(), graph=None)
        cases = [
            ["--source-leakage", self.graphs["pair"]], ["--leakage-input-gain", "0.5"],
            ["--source-leakage"], ["--leakage-input-gain"],
            ["--source-leakage", ""], ["--source-leakage", "x" * 4097],
            ["--source-leakage", "--fail-on-clip"], ["--source-leak", self.graphs["pair"]],
            ["--leakage-input-gain", "0.5", "--leakage-input-gain", "0.5"],
            ["--source-leakage", self.graphs["pair"], "--source-leakage", self.graphs["pair"]],
        ]
        for suffix in cases:
            with self.subTest(suffix=str(suffix)[:120]):
                self.rejected(base + suffix)

    def test_gain_syntax_range_and_underflow_reject(self):
        for gain in ("nan", "NaN", "inf", "-inf", "1e9999", "1e-9999", "1e-324",
                     "-0.1", "1.0000000000000002", "0x1p-1", "0,5", " .5", ".5 ",
                     "0.5junk", "+", ".", "1e", "1_0", "1\n", "0" * 129):
            with self.subTest(gain=gain):
                self.rejected(self.arguments(self.unique(), gain=gain))

    def test_unsafe_headroom_and_adjacent_full_row_boundary(self):
        for gain in ("1", format(16 / 17, ".17g")):
            self.rejected(self.arguments(self.unique(), gain=gain), "headroom")
        full = self.unique("b3leakage")
        header = self.fixture_bytes["pair"].split(b"edge_count ", 1)[0]
        full.write_bytes(header + b"edge_count 8\n" + b"".join(
            f"edge destination 91 source {source} gain 0.0625\n".encode()
            for source in range(1, 9)) + b"end\n")
        accepted = float.fromhex("0x1.555555555551cp-1")
        rejected = float.fromhex("0x1.555555555551dp-1")
        _, report = self.rendered(graph=full, gain=format(accepted, ".17g"), frames=64)
        self.assertEqual(report["source_leakage_guarded_output_bound"], 1.0)
        self.rejected(self.arguments(self.unique(), graph=full,
                                     gain=format(rejected, ".17g")), "headroom")

    def test_malformed_wrong_metadata_and_oversized_graphs(self):
        graph = self.unique("b3leakage")
        original = self.fixture_bytes["pair"]
        cases = (b"", b"B3LEAKAGE9\n", original[:-5], original + b"unexpected\n",
                 original.replace(b"evidence_status synthetic", b"evidence_status measured"),
                 original.replace(b"excludes-leakage", b"includes-leakage"),
                 original.replace(b"gain 0.0625", b"gain 0.3"),
                 original + b"\0", original + b"\xc3\xa9", b" " * (128 * 1024 + 1))
        for raw in cases:
            with self.subTest(length=len(raw), prefix=raw[:30]):
                graph.write_bytes(raw)
                self.rejected(self.arguments(self.unique(), graph=graph))

    def test_missing_directory_and_fifo_graphs(self):
        directory = self.work / "graph directory"
        directory.mkdir()
        self.rejected(self.arguments(self.unique(), graph=self.work / "missing.graph"), "regular")
        self.rejected(self.arguments(self.unique(), graph=directory), "regular")
        if not hasattr(os, "mkfifo"):
            self.skipTest("FIFO creation is unavailable; missing/directory cases executed")
        fifo = self.work / "graph fifo"
        os.mkfifo(fifo)
        self.rejected(self.arguments(self.unique(), graph=fifo), "regular")

    def test_existing_output_directories_and_bad_parents(self):
        output = self.unique()
        output.write_bytes(b"keep existing output\x00\xff")
        self.rejected(self.arguments(output), "already exists")
        directory = self.work / "output directory"
        directory.mkdir()
        (directory / "keep").write_bytes(b"retained")
        self.rejected(self.arguments(directory), "already exists")
        self.rejected(self.arguments(self.work / "missing parent" / "out.wav"))
        self.rejected(self.arguments(output / "out.wav"))

    def test_graph_score_profile_collisions_and_lexical_aliases(self):
        score = self.score("0 note_on upper 48 100\n")
        subdirectory = self.work / "subdirectory"
        subdirectory.mkdir()
        for input_path in (self.graphs["pair"], self.profile, score):
            for output in (input_path, input_path.name,
                           subdirectory / ".." / input_path.name):
                with self.subTest(output=output):
                    self.rejected(self.arguments(output, score=score), "collides")

    def test_hardlink_output_alias_preserves_graph(self):
        alias = self.work / "graph hardlink.wav"
        os.link(self.graphs["pair"], alias)
        self.rejected(self.arguments(alias), "already exists")
        self.assertTrue(os.path.samefile(alias, self.graphs["pair"]))

    def symlink(self, target, path):
        try:
            path.symlink_to(target)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Symlink creation unavailable: {error}")

    def test_symlink_input_and_output_aliases_and_dangling_output(self):
        alias = self.work / "graph symlink"
        self.symlink(self.graphs["pair"], alias)
        direct, _ = self.rendered()
        linked, _ = self.rendered(graph=alias)
        self.assertEqual(direct, linked)
        self.rejected(self.arguments(alias), "collides")
        dangling = self.work / "dangling output.wav"
        self.symlink(self.work / "missing-target", dangling)
        self.rejected(self.arguments(dangling), "already exists")

    def test_fail_on_clip_preserves_inputs_and_cleans_temporary_wave(self):
        score = self.score("".join(f"0 drawbar lower {index} 8\n" for index in range(9)) +
                           "".join(f"0 note_on {manual} {note} 127\n"
                                   for manual in ("upper", "lower") for note in range(36, 97)))
        settings = dict(score=score, drawbars="888888888", frames=4096, block=127)
        _, loud = self.rendered(**settings)
        self.assertGreater(loud["clipped_frames"], 0, "Fixture must actually exercise clipping")
        output = self.unique()
        before = self.snapshot()
        result = self.invoke(self.arguments(output, extra=("--fail-on-clip",), **settings))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        report = receipt(result.stdout)
        self.assertEqual({**report, "status": "ok"}, loud)
        self.assertIn("clipping", result.stderr.lower())
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(output.exists())

    @unittest.skipUnless(os.name == "posix", "POSIX file-size fault injection unavailable")
    def test_actual_write_failure_cleans_temporary_output(self):
        import resource
        import signal

        def limit_output():
            signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
            resource.setrlimit(resource.RLIMIT_FSIZE, (4096, 4096))

        result = self.rejected(self.arguments(self.unique(), frames=65536),
                               observe_setup=False, preexec_fn=limit_output)
        self.assertTrue("writing temporary WAV" in result.stderr or
                        "flushing temporary WAV" in result.stderr, result.stderr)

    def test_racing_publication_never_replaces_new_output(self):
        output = self.unique()
        before = self.snapshot()
        type(self).calls += 1
        process = subprocess.Popen([str(self.renderer), *map(str, self.arguments(
            output, frames=480000, block=257))], cwd=self.work, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
        observed = False
        try:
            deadline = time.monotonic() + 20
            while process.poll() is None and time.monotonic() < deadline:
                if any(self.work.glob(".hammond-render-*")):
                    with output.open("xb") as stream:
                        stream.write(b"racing output must survive\x00\xff")
                    observed = True
                    break
                time.sleep(0.001)
            stdout, stderr = process.communicate(timeout=30)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()
        self.assertTrue(observed, "Could not observe reserved temporary directory before publication")
        self.assertEqual(process.returncode, 1, stdout + stderr)
        self.assertEqual(stdout, "")
        self.assertIn("Cannot publish WAV without overwriting", stderr)
        self.assertEqual(output.read_bytes(), b"racing output must survive\x00\xff")
        after = self.snapshot()
        self.assertEqual(set(after) - set(before), {output.name})
        self.assertEqual({key: after[key] for key in before}, before)


if __name__ == "__main__":
    unittest.main()
