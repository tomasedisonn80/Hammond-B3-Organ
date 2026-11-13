#!/usr/bin/env python3
"""CLI/WAV engineering regressions for the explicitly unmeasured dry renderer.

CTest supplies HAMMOND_RENDER_EXECUTABLE and HAMMOND_TEST_PROFILE. Direct use:
    python tests/test_render.py --renderer build/hammond_render --profile build/nominal.b3p
Without overrides, those build/ paths are inferred. Missing inputs are errors,
never successful skips. All fixtures use the Python standard library.
"""

import argparse
import io
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import wave


ROOT = Path(__file__).resolve().parents[1]
RENDERER_OVERRIDE = None
PROFILE_OVERRIDE = None
BLOCK_SIZES = (1, 17, 64, 127, 512, 1024)
HALF_PCM_STEP = 0.5 / 32768.0


def required_file(explicit, candidates, description, environment_name):
    """An explicit configuration error must not silently use a different build."""
    paths = [Path(explicit)] if explicit is not None else candidates
    for path in paths:
        if path.is_file():
            return path.resolve()
    searched = ", ".join(str(path) for path in paths)
    raise RuntimeError(
        f"Missing {description}; checked {searched}. Build hammond_render and "
        f"nominal.b3p, then set {environment_name} or pass "
        "--renderer/--profile. Renderer CLI tests were not run."
    )


def reject_nonfinite_json(token):
    raise ValueError(f"Renderer emitted a non-JSON number: {token}")


class RendererTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        executable_name = "hammond_render.exe" if os.name == "nt" else "hammond_render"
        cls.renderer = required_file(
            RENDERER_OVERRIDE if RENDERER_OVERRIDE is not None
            else os.environ.get("HAMMOND_RENDER_EXECUTABLE"),
            [ROOT / "build" / executable_name],
            "renderer executable", "HAMMOND_RENDER_EXECUTABLE",
        )
        if not os.access(cls.renderer, os.X_OK):
            raise RuntimeError(f"Renderer is not executable: {cls.renderer}")
        cls.compiled_profile = required_file(
            PROFILE_OVERRIDE if PROFILE_OVERRIDE is not None
            else os.environ.get("HAMMOND_TEST_PROFILE"),
            [cls.renderer.parent / "nominal.b3p", ROOT / "build" / "nominal.b3p"],
            "compiled test profile", "HAMMOND_TEST_PROFILE",
        )
        cls.profile_bytes = cls.compiled_profile.read_bytes()
        lines = cls.profile_bytes.decode("ascii").splitlines()
        cls.profile_id = next(line.split()[1] for line in lines
                              if line.startswith("profile_id "))
        cls.authoring_sha256 = next(line.split()[1] for line in lines
                                    if line.startswith("authoring_sha256 "))

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-render-test-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        # Paths with spaces and an unrelated cwd exercise real argument passing.
        self.profile = self.work / "compiled profile.b3p"
        self.profile.write_bytes(self.profile_bytes)
        self.serial = 0

    def new_output(self):
        self.serial += 1
        return self.work / f"render {self.serial}.wav"

    def paths(self):
        return set(self.work.rglob("*"))

    def score(self, contents, name="score.events"):
        path = self.work / name
        path.write_bytes(contents.encode("utf-8") if isinstance(contents, str) else contents)
        return path

    def arguments(self, output, *, profile=None, frames=257):
        arguments = ["--profile", self.profile if profile is None else profile,
                     "--output", output]
        if frames is not None:
            arguments.extend(("--frames", frames))
        return arguments

    def invoke(self, arguments):
        return subprocess.run(
            [str(self.renderer), *map(str, arguments)], cwd=self.work,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30, check=False,
        )

    def assert_rejected(self, arguments, message=None):
        before = self.paths()
        result = self.invoke(arguments)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "", result.stdout)
        self.assertTrue(result.stderr.strip(), "Rejected input needs a diagnostic")
        if message is not None:
            self.assertIn(message, result.stderr)
        self.assertEqual(self.paths(), before, "Failure left output or temporary files")
        self.assertEqual(self.profile.read_bytes(), self.profile_bytes)
        return result

    def assert_metrics(self, result, *, frames, rate, block, seed, status="ok"):
        report = json.loads(result.stdout, parse_constant=reject_nonfinite_json)
        self.assertIsInstance(report, dict)
        expected = {
            "status": status, "model": "ideal-shared-sine-v1",
            "evidence_status": "unmeasured", "profile_id": self.profile_id,
            "authoring_sha256": self.authoring_sha256, "sample_rate": rate,
            "block_size": block, "frames": frames, "seed": seed,
            "channels": 2, "sample_format": "pcm_s16le",
        }
        for key, value in expected.items():
            self.assertEqual(report[key], value, key)
        for key in ("peak", "rms"):
            self.assertIsInstance(report[key], (int, float))
            self.assertTrue(math.isfinite(report[key]), key)
            self.assertGreaterEqual(report[key], 0.0, key)
        self.assertLessEqual(report["rms"], report["peak"] + 1e-15)
        self.assertIs(type(report["clipped_frames"]), int)
        self.assertGreaterEqual(report["clipped_frames"], 0)
        self.assertLessEqual(report["clipped_frames"], frames)
        self.assertEqual(report["clipped_channel_samples"], 2 * report["clipped_frames"])
        return report

    def assert_wave(self, path, *, frames, rate):
        data = path.read_bytes()
        self.assertEqual(len(data), 44 + frames * 4)
        header = struct.unpack_from("<4sI4s4sIHHIIHH4sI", data)
        self.assertEqual(header, (
            b"RIFF", len(data) - 8, b"WAVE", b"fmt ", 16, 1, 2,
            rate, rate * 4, 4, 16, b"data", frames * 4,
        ))
        samples = struct.unpack_from(f"<{frames * 2}h", data, 44)
        mono = samples[::2]
        self.assertEqual(mono, samples[1::2], "Dry stereo channels differ")
        # A second parser verifies the serialized format independently.
        with wave.open(io.BytesIO(data), "rb") as reader:
            self.assertEqual(reader.getparams()[:4], (2, 2, rate, frames))
            self.assertEqual(reader.getcomptype(), "NONE")
            self.assertEqual(reader.readframes(frames + 1), data[44:])
        return data, mono

    def render(self, *, frames=257, rate=48000, block=64, seed=0,
               drawbars=None, note=None, events=None, extra=()):
        output = self.new_output()
        arguments = self.arguments(output, frames=frames)
        arguments.extend(("--sample-rate", rate, "--block-size", block, "--seed", seed))
        for flag, value in (("--drawbars", drawbars), ("--note", note), ("--events", events)):
            if value is not None:
                arguments.extend((flag, value))
        arguments.extend(extra)
        before = self.paths()
        result = self.invoke(arguments)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(self.paths(), before | {output}, "Success left temporary files")
        report = self.assert_metrics(result, frames=frames, rate=rate, block=block, seed=seed)
        data, mono = self.assert_wave(output, frames=frames, rate=rate)
        if report["clipped_frames"] == 0 and report["peak"] < 0.99:
            pcm_peak = max(map(abs, mono)) / 32768.0
            pcm_rms = math.sqrt(math.fsum(value * value for value in mono) / frames) / 32768.0
            self.assertAlmostEqual(report["peak"], pcm_peak, delta=HALF_PCM_STEP + 1e-12)
            self.assertAlmostEqual(report["rms"], pcm_rms, delta=HALF_PCM_STEP + 1e-12)
        return data, mono, report

    def assert_same_render(self, left, right):
        self.assertEqual(left[0], right[0], "Block partition changed WAV bytes")
        for key in left[2]:
            if key != "block_size":
                self.assertEqual(left[2][key], right[2][key], key)

    def test_help_is_successful_without_required_inputs_or_output(self):
        before = self.paths()
        result = self.invoke(["--help"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertIn("--profile", result.stdout)
        self.assertIn("--events", result.stdout)
        self.assertIn("unmeasured", result.stdout)
        self.assertEqual(self.paths(), before)

    def test_riff_stereo_supported_rates_and_partial_final_blocks(self):
        frames = 1031
        release = frames * 3 // 4
        for rate in (44100, 48000, 96000):
            with self.subTest(sample_rate=rate):
                _, mono, report = self.render(frames=frames, rate=rate, block=127, note=69)
                self.assertTrue(any(mono[:release]), "Renderer emitted only silence")
                self.assertEqual(mono[release:], (0,) * (frames - release))
                self.assertGreater(report["peak"], 0.01)
                self.assertGreater(report["rms"], 0.001)
                self.assertEqual(report["clipped_frames"], 0)

    def test_cli_defaults_match_explicit_default_gesture(self):
        frames = 259
        output = self.new_output()
        before = self.paths()
        result = self.invoke(self.arguments(output, frames=frames))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(self.paths(), before | {output})
        report = self.assert_metrics(result, frames=frames, rate=48000, block=64, seed=0)
        data, mono = self.assert_wave(output, frames=frames, rate=48000)
        events = self.score(f"0 note_on upper 60 100\n{frames * 3 // 4} note_off upper 60 0\n")
        explicit = self.render(frames=frames, drawbars="888000000", events=events)
        self.assert_same_render((data, mono, report), explicit)

    def test_one_frame_and_largest_block_have_exact_sizes(self):
        # The default on and off both occur at frame zero for a one-frame render.
        one = self.render(frames=1, block=65536)
        self.assertEqual(one[1], (0,))
        self.assertEqual(one[2]["peak"], 0)
        self.assertEqual(one[2]["rms"], 0)
        long_block = self.render(frames=131, block=65536, seed=(1 << 64) - 1)
        one_block = self.render(frames=131, block=1, seed=(1 << 64) - 1)
        self.assert_same_render(long_block, one_block)
        self.assertTrue(any(long_block[1]))

    def test_replay_seed_and_all_requested_block_partitions(self):
        events = self.score(
            "0 drawbar lower 2 6\n0 note_on upper 60 100\n"
            "17 note_on upper 64 1\n63 expression upper 0 0.5\n"
            "64 drawbar upper 4 3\n126 note_off upper 64 0\n"
            "127 note_on lower 48 127\n511 note_off upper 60 0\n"
            "512 note_off lower 48 0\n1023 note_on upper 72 100\n"
            "1024 expression lower 0 0.75\n2047 all_notes_off upper 0 0\n"
            "2050 note_on lower 48 64\n3091 all_notes_off lower 0 0\n"
        )
        reference = self.render(frames=4099, block=1, seed=123456789, events=events)
        for block in BLOCK_SIZES:
            with self.subTest(block_size=block):
                self.assert_same_render(
                    reference,
                    self.render(frames=4099, block=block, seed=123456789, events=events),
                )
        changed = self.render(frames=4099, block=64, seed=123456790, events=events)
        self.assertNotEqual(reference[0][44:], changed[0][44:])
        self.assertEqual(reference[1][3091:], (0,) * (4099 - 3091))

    def test_absolute_block_end_and_final_sample_events(self):
        held = self.render(frames=259, events=self.score("0 note_on upper 60 100\n"))
        gated_score = self.score("64 note_on upper 60 100\n128 note_off upper 60 0\n")
        gated = self.render(frames=259, block=64, events=gated_score)
        self.assertEqual(gated[1][:64], (0,) * 64)
        self.assertNotEqual(held[1][64], 0)
        self.assertNotEqual(held[1][127], 0)
        self.assertEqual(gated[1][64:128], held[1][64:128])
        self.assertEqual(gated[1][128:], (0,) * 131)
        self.assert_same_render(gated, self.render(frames=259, block=17, events=gated_score))
        last_score = self.score("0 note_on upper 60 100\n258 note_off upper 60 0\n")
        last = self.render(frames=259, block=127, events=last_score)
        self.assertEqual(last[1][:-1], held[1][:-1])
        self.assertEqual(last[1][-1], 0)

    def test_same_frame_file_order_is_stable(self):
        held = self.render(frames=193, events=self.score("0 note_on upper 60 100\n"))
        forward = self.score(
            "0 note_off upper 60 0\n0 note_on upper 60 127\n"
            "64 note_off upper 60 0\n64 note_on upper 60 1\n"
            "128 note_on upper 60 100\n128 note_off upper 60 0\n"
        )
        first = self.render(frames=193, block=64, events=forward)
        self.assertEqual(first[1][:128], held[1][:128])
        self.assertEqual(first[1][128:], (0,) * 65)
        reversed_ties = self.score(
            "0 note_on upper 60 127\n0 note_off upper 60 0\n"
            "64 note_on upper 60 1\n64 note_off upper 60 0\n"
            "128 note_off upper 60 0\n128 note_on upper 60 100\n"
        )
        second = self.render(frames=193, block=64, events=reversed_ties)
        self.assertEqual(second[1][:128], (0,) * 128)
        self.assertEqual(second[1][128:], held[1][128:])
        self.assertNotEqual(first[0], second[0])

    def test_initial_registration_precedes_score_and_lower_starts_muted(self):
        muted_events = "".join(f"0 drawbar upper {index} 0\n" for index in range(9))
        muted = self.render(events=self.score(muted_events + "0 note_on upper 60 100\n"))
        self.assertEqual(muted[1], (0,) * 257)
        self.assertEqual(muted[2]["peak"], 0)
        self.assertEqual(muted[2]["rms"], 0)
        baseline = self.render(drawbars="008000000",
                               events=self.score("0 note_on upper 60 100\n"))
        override = self.render(drawbars="000000000", events=self.score(
            "0 drawbar upper 2 8\n0 note_on upper 60 100\n"))
        self.assert_same_render(baseline, override)
        lower = self.render(events=self.score(
            "0 note_on lower 60 100\n64 drawbar lower 2 8\n"))
        self.assertEqual(lower[1][:64], (0,) * 64)
        self.assertEqual(lower[1][64:], baseline[1][64:])

    def test_dense_blocks_subdivide_without_moving_or_dropping_events(self):
        # Two exact-capacity timestamps coexist with >1024 events per host block.
        dense = [f"0 expression upper 0 {(index + 1) % 2}\n" for index in range(1023)]
        dense.append("0 note_on upper 60 100\n")
        dense.extend(f"1 drawbar upper 2 {8 * (index % 2)}\n" for index in range(700))
        dense.extend(f"17 expression upper 0 {0.5 * (index % 2)}\n"
                     for index in range(1024))
        dense.extend("18 expression upper 0 1\n" for _ in range(512))
        dense.append("31 all_notes_off upper 0 0\n")
        dense_score = self.score("".join(dense), "dense.events")
        sparse_score = self.score(
            "0 note_on upper 60 100\n17 expression upper 0 0.5\n"
            "18 expression upper 0 1\n31 all_notes_off upper 0 0\n", "sparse.events")
        reference = self.render(frames=67, block=1, drawbars="008000000", events=sparse_score)
        self.assertTrue(any(reference[1][:31]))
        for block in BLOCK_SIZES:
            with self.subTest(block_size=block):
                self.assert_same_render(reference, self.render(
                    frames=67, block=block, drawbars="008000000", events=dense_score))

    def test_empty_comment_whitespace_bom_and_decimal_scores_are_accepted(self):
        for contents in (b"", b"\xef\xbb\xbf", b"\r\n \t\f\v\n",
                         "  # UTF-8 comment: caf\u00e9\n", "#" + "x" * 4095 + "\n"):
            with self.subTest(prefix=repr(contents[:30])):
                rendered = self.render(frames=19, events=self.score(contents))
                self.assertEqual(rendered[1], (0,) * 19)
                self.assertEqual(rendered[2]["peak"], 0)
                self.assertEqual(rendered[2]["rms"], 0)
        normal = self.render(frames=37, events=self.score(
            "0 expression upper 0 0.5\n0 note_on upper 60 100\n"))
        decimal = self.render(frames=37, events=self.score(
            b"\xef\xbb\xbf\t# comment\r\n000 expression upper 00 +5.e-1\r\n"
            b"000 note_on upper 060 1e2\r\n"))
        self.assert_same_render(normal, decimal)

    def test_metrics_are_floats_before_pcm_quantization(self):
        _, mono, report = self.render(frames=1031, block=127, seed=7, drawbars="008000000")
        pcm_peak = max(map(abs, mono)) / 32768.0
        pcm_rms = math.sqrt(math.fsum(value * value for value in mono) / len(mono)) / 32768.0
        self.assertGreater(abs(report["peak"] - pcm_peak), 1e-10)
        self.assertGreater(abs(report["rms"] - pcm_rms), 1e-12)
        self.assertAlmostEqual(report["peak"], pcm_peak, delta=HALF_PCM_STEP)
        self.assertAlmostEqual(report["rms"], pcm_rms, delta=HALF_PCM_STEP)
        self.assertEqual(report["clipped_frames"], 0)

    def clipping_score(self, expression=1):
        lines = [f"0 expression upper 0 {expression}\n"]
        lines.extend(f"0 drawbar lower {index} 8\n" for index in range(9))
        lines.extend(f"0 note_on {manual} {note} 127\n"
                     for manual in ("upper", "lower") for note in range(36, 97))
        return self.score("".join(lines), f"clipping-{expression}.events")

    def test_clipping_metrics_and_fail_on_clip_remove_all_output(self):
        frames = 1025
        events = self.clipping_score()
        loud = self.render(frames=frames, block=127, seed=7,
                           drawbars="888888888", events=events)
        self.assertGreater(loud[2]["peak"], 1)
        self.assertGreater(loud[2]["rms"], 1)
        self.assertGreater(loud[2]["clipped_frames"], 0)
        self.assertIn(-32768, loud[1])
        self.assertIn(32767, loud[1])
        self.assertLessEqual(loud[2]["clipped_frames"],
                             sum(sample in (-32768, 32767) for sample in loud[1]))
        # A power-of-two expression change preserves the float signal's scaling.
        quiet = self.render(frames=frames, block=127, seed=7,
                            drawbars="888888888", events=self.clipping_score(0.0625))
        self.assertEqual(quiet[2]["clipped_frames"], 0)
        self.assertEqual(loud[2]["peak"], quiet[2]["peak"] * 16)
        self.assertAlmostEqual(loud[2]["rms"], quiet[2]["rms"] * 16, delta=1e-12)
        certainly_clipped = sum(abs(sample) / 32768.0 - HALF_PCM_STEP > 0.0625
                                for sample in quiet[1])
        possibly_clipped = sum(abs(sample) / 32768.0 + HALF_PCM_STEP > 0.0625
                               for sample in quiet[1])
        self.assertLessEqual(certainly_clipped, loud[2]["clipped_frames"])
        self.assertLessEqual(loud[2]["clipped_frames"], possibly_clipped)
        output = self.new_output()
        arguments = self.arguments(output, frames=frames) + [
            "--block-size", 127, "--seed", 7, "--drawbars", "888888888",
            "--events", events, "--fail-on-clip",
        ]
        before = self.paths()
        result = self.invoke(arguments)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("clipping", result.stderr.lower())
        self.assertFalse(output.exists())
        self.assertEqual(self.paths(), before, "Clipping failure left temporary files")
        failed_report = self.assert_metrics(result, frames=frames, rate=48000,
                                            block=127, seed=7, status="clipped")
        self.assertEqual({**failed_report, "status": "ok"}, loud[2])

    def test_fail_on_clip_allows_unclipped_audio(self):
        rendered = self.render(frames=131, extra=("--fail-on-clip",))
        self.assertTrue(any(rendered[1]))
        self.assertEqual(rendered[2]["clipped_frames"], 0)

    def test_required_unknown_duplicate_and_missing_value_flags_reject(self):
        output = self.new_output()
        for arguments in ([], ["--profile", self.profile], ["--output", output],
                          ["--profile"], ["--output"], ["--help", "extra"]):
            with self.subTest(arguments=arguments):
                self.assert_rejected(arguments)
        base = self.arguments(output)
        bad_suffixes = [
            ["--unknown"], ["positional"], ["--frames=10"], ["--note"],
            ["--drawbars", "--seed", "7"], ["--profile", self.profile],
            ["--output", output], ["--frames", "257"],
            ["--seed", "0", "--seed", "0"],
            ["--fail-on-clip", "--fail-on-clip"],
            ["--sample-rate", "48000", "--sample-rate", "48000"],
            ["--block-size", "64", "--block-size", "64"],
            ["--drawbars", "888000000", "--drawbars", "888000000"],
            ["--note", "60", "--note", "60"],
            ["--seed", "0"] * 20,
        ]
        events = self.score("")
        bad_suffixes.extend((["--note", "60", "--events", events],
                             ["--events", events, "--events", events]))
        for suffix in bad_suffixes:
            with self.subTest(suffix=str(suffix)[:140]):
                self.assert_rejected(base + suffix)
        self.assert_rejected(self.arguments("x" * 4097), "oversized")

    def test_unsigned_flag_grammar_bounds_and_bad_registrations_reject(self):
        flags = ("--sample-rate", "--block-size", "--frames", "--seed", "--note")
        malformed = ("", "-1", "+1", "1.5", "1e2", "1x", " 1", "0x10", "nan",
                     "18446744073709551616", "0" * 129)
        for flag in flags:
            for value in malformed:
                with self.subTest(flag=flag, value=value[:32]):
                    base = self.arguments(self.new_output(), frames=None if flag == "--frames" else 37)
                    self.assert_rejected(base + [flag, value])
        bounds = {
            "--sample-rate": ("0", "22050", "48001", "192000"),
            "--block-size": ("0", "65537"),
            "--frames": ("0", "28800001", "18446744073709551615"),
            "--note": ("0", "35", "97", "128"),
            "--drawbars": ("", "88800000", "8880000000", "988000000", "88800000x", "\u0668" * 9),
        }
        for flag, values in bounds.items():
            for value in values:
                with self.subTest(flag=flag, value=value):
                    base = self.arguments(self.new_output(), frames=None if flag == "--frames" else 37)
                    self.assert_rejected(base + [flag, value])
        for rate in (44100, 48000, 96000):
            with self.subTest(duration_bound_rate=rate):
                self.assert_rejected(self.arguments(self.new_output(), frames=rate * 600 + 1)
                                     + ["--sample-rate", rate])

    def test_malformed_score_types_numbers_payloads_and_order_reject(self):
        scores = [
            "0 unknown upper 60 1", "0 NOTE_ON upper 60 1", "0 note_on pedal 60 1",
            "0 note_on upper 60", "0 note_on upper 60 1 extra", "0 note_on upper 60 1 # inline",
            "-1 note_on upper 60 1", "+0 note_on upper 60 1", "0.0 note_on upper 60 1",
            "18446744073709551616 note_on upper 60 1", "73 note_on upper 60 1",
            "74 note_on upper 60 1", "1 note_on upper 60 1\n0 note_off upper 60 0",
            "0 note_on upper -1 1", "0 note_on upper +60 1", "0 note_on upper 60.0 1",
            "0 note_on upper 35 1", "0 note_on upper 97 1", "0 note_on upper 256 1",
            "0 note_on upper 18446744073709551616 1", "0 note_on upper 60 -1",
            "0 note_on upper 60 128", "0 note_on upper 60 1.5", "0 note_off upper 60 1",
            "0 drawbar upper 9 8", "0 drawbar upper 0 9", "0 drawbar upper 0 1.5",
            "0 expression upper 1 0.5", "0 expression upper 0 -0.001",
            "0 expression upper 0 1.0001", "0 all_notes_off upper 1 0",
            "0 all_notes_off upper 0 1", "0 expression upper 0 nan",
            "0 expression upper 0 inf", "0 expression upper 0 -Infinity",
            "0 expression upper 0 1e9999", "0 expression upper 0 0x1",
            "0 expression upper 0 1,0", "0 expression upper 0 1x",
            "0 expression upper 0 .", "0 expression upper 0 +",
            "0 expression upper 0 1e", "0 expression upper 0 1e+",
            "0 expression upper 0 " + "0" * 129,
            "0" * 129 + " note_on upper 60 1",
            b"# invalid UTF-8 \xff\n", b"0 note_on upper 60 1\x00\n",
            b"# surrogate \xed\xa0\x80\n", b"# overlong \xc0\xaf\n",
        ]
        for index, contents in enumerate(scores):
            with self.subTest(case=index, prefix=repr(contents[:70])):
                events = self.score(contents)
                original = events.read_bytes()
                self.assert_rejected(self.arguments(self.new_output(), frames=73)
                                     + ["--events", events])
                self.assertEqual(events.read_bytes(), original)

    def test_1025_same_frame_and_oversized_score_inputs_reject(self):
        same_frame = self.score("0 expression upper 0 1\n" * 1025)
        self.assert_rejected(self.arguments(self.new_output()) + ["--events", same_frame], "1024")
        too_long = self.score("#" + "x" * 4096)
        self.assert_rejected(self.arguments(self.new_output()) + ["--events", too_long], "4096")
        too_large = self.score(b"\n" * (16 * 1024 * 1024 + 1))
        self.assert_rejected(self.arguments(self.new_output()) + ["--events", too_large], "byte limit")
        # Keep timestamps sorted and <=1024/frame so the total-event gate is reached.
        too_many = self.score("".join(f"{index // 1024} expression upper 0 1\n"
                                      for index in range(262145)))
        self.assert_rejected(self.arguments(self.new_output(), frames=258)
                             + ["--events", too_many], "262144")

    def test_missing_nonregular_and_malformed_inputs_reject(self):
        directory = self.work / "directory"
        directory.mkdir()
        for profile in (self.work / "missing.b3p", directory):
            with self.subTest(profile=profile):
                self.assert_rejected(self.arguments(self.new_output(), profile=profile))
        for events in (self.work / "missing.events", directory):
            with self.subTest(events=events):
                self.assert_rejected(self.arguments(self.new_output()) + ["--events", events])
        invalid = self.work / "invalid.b3p"
        for contents in (b"", b"not a profile\n", self.profile_bytes + b"extra\n",
                         b" " * (128 * 1024 + 1)):
            with self.subTest(profile_bytes=len(contents)):
                invalid.write_bytes(contents)
                self.assert_rejected(self.arguments(self.new_output(), profile=invalid))
                self.assertEqual(invalid.read_bytes(), contents)

    def test_input_output_collisions_and_lexical_aliases_preserve_inputs(self):
        subdirectory = self.work / "subdirectory"
        subdirectory.mkdir()
        for output in (self.profile, self.profile.name, "./" + self.profile.name,
                       subdirectory / ".." / self.profile.name):
            with self.subTest(output=output):
                self.assert_rejected(self.arguments(output), "collides")
        events = self.score("0 note_on upper 60 100\n")
        original = events.read_bytes()
        self.assert_rejected(self.arguments(events) + ["--events", events], "collides")
        self.assertEqual(events.read_bytes(), original)
        # Rendering itself requires hard-link support for no-clobber publication.
        alias = self.work / "profile hardlink.b3p"
        os.link(self.profile, alias)
        self.assert_rejected(self.arguments(alias))
        self.assertEqual(alias.read_bytes(), self.profile_bytes)
        self.assertTrue(os.path.samefile(alias, self.profile))

    def test_existing_outputs_and_invalid_parents_are_preserved(self):
        output = self.new_output()
        sentinel = b"previous useful output\n"
        output.write_bytes(sentinel)
        before_time = output.stat().st_mtime_ns
        self.assert_rejected(self.arguments(output), "already exists")
        self.assertEqual(output.read_bytes(), sentinel)
        self.assertEqual(output.stat().st_mtime_ns, before_time)
        self.assert_rejected(self.arguments(output, profile=self.work / "missing.b3p"))
        self.assertEqual(output.read_bytes(), sentinel)
        directory_output = self.work / "directory.wav"
        directory_output.mkdir()
        marker = directory_output / "keep.txt"
        marker.write_bytes(sentinel)
        self.assert_rejected(self.arguments(directory_output))
        self.assertEqual(marker.read_bytes(), sentinel)
        self.assert_rejected(self.arguments(self.work / "missing" / "output.wav"))
        self.assertFalse((self.work / "missing").exists())
        self.assert_rejected(self.arguments(output / "output.wav"))
        self.assertEqual(output.read_bytes(), sentinel)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--renderer", help="Path to an already-built hammond_render")
    parser.add_argument("--profile", help="Path to an already-compiled nominal.b3p")
    options, unittest_arguments = parser.parse_known_args()
    RENDERER_OVERRIDE = options.renderer
    PROFILE_OVERRIDE = options.profile
    unittest.main(argv=[sys.argv[0], *unittest_arguments], verbosity=2)
