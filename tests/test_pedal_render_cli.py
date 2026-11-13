#!/usr/bin/env python3
"""Actual CLI/WAV checks for the named, unmeasured pedal extension.

CTest provides the matching renderer/profile. Direct use accepts --renderer and
--profile. Missing configured inputs are errors, never successful skips.
"""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest


ROOT = Path(os.environ.get("HAMMOND_SOURCE_DIR", Path(__file__).resolve().parents[1]))
RENDERER_OVERRIDE = None
PROFILE_OVERRIDE = None


def required_path(explicit, fallback, label):
    path = Path(explicit) if explicit is not None else fallback
    if not path.is_file():
        raise RuntimeError(f"Missing {label}: {path}; build matching inputs before testing")
    return path.resolve()


def invalid_json_constant(value):
    raise ValueError(f"Nonfinite JSON constant: {value}")


class PedalRendererTests(unittest.TestCase):
    calls = 0

    @classmethod
    def setUpClass(cls):
        name = "hammond_render.exe" if os.name == "nt" else "hammond_render"
        cls.renderer = required_path(
            RENDERER_OVERRIDE or os.environ.get("HAMMOND_RENDER_EXECUTABLE"),
            ROOT / "build" / name, "renderer")
        cls.compiled_profile = required_path(
            PROFILE_OVERRIDE or os.environ.get("HAMMOND_TEST_PROFILE"),
            ROOT / "build" / "nominal.b3p", "compiled profile")
        cls.profile_bytes = cls.compiled_profile.read_bytes()

    @classmethod
    def tearDownClass(cls):
        print(f"pedal renderer: {cls.calls} actual CLI invocations; no skipped cases")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-pedal-cli-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.profile = self.work / "compiled profile.b3p"
        self.profile.write_bytes(self.profile_bytes)
        self.serial = 0

    def unique(self, suffix):
        self.serial += 1
        return self.work / f"pedal {self.serial}.{suffix}"

    def score(self, text):
        path = self.unique("events")
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def paths(self):
        return set(self.work.rglob("*"))

    def arguments(self, output, *, frames=1024, rate=48000, block=64, score=None):
        result = ["--profile", self.profile, "--output", output,
                  "--frames", frames, "--sample-rate", rate, "--block-size", block,
                  "--seed", 13, "--drawbars", "000000000"]
        if score is not None:
            result.extend(("--events", score))
        return result

    def invoke(self, arguments):
        type(self).calls += 1
        return subprocess.run([str(self.renderer), *map(str, arguments)], cwd=self.work,
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", check=False, timeout=30)

    def test_unicode_values_are_not_best_fit_ascii(self):
        # Windows narrow argv previously changed full-width eight to ASCII eight
        # before the strict parser could inspect it. Keep exact Unicode inputs.
        for flag, value in (("--pedal-drawbars", "\u221e0"),
                            ("--pedal-drawbars", "\uff180"),
                            ("--drawbars", "\uff18" + "0" * 8),
                            ("--frames", "\uff11\uff10\uff12\uff14")):
            with self.subTest(flag=flag, value=value):
                arguments = self.arguments(self.unique("wav"))
                if flag in arguments:
                    arguments[arguments.index(flag) + 1] = value
                else:
                    arguments.extend((flag, value))
                self.rejected(arguments)

    def test_unicode_profile_score_and_output_paths_are_lossless(self):
        text = "0 pedal_on lower 1 100\n96 pedal_off lower 1 0\n"
        expected, _, _ = self.render(text, frames=128, registration="60")
        directory = self.work / "p\u00e9dale_\u97f3_\U0001f3b9"
        directory.mkdir()
        profile = directory / "profil_\u8db3.b3p"
        source = directory / "notes_\u8db3.events"
        output = directory / "r\u00e9sultat_\u4f4e.wav"
        profile.write_bytes(self.profile_bytes)
        source.write_text(text, encoding="utf-8", newline="\n")
        arguments = self.arguments(output, frames=128, score=source)
        arguments[arguments.index("--profile") + 1] = profile
        arguments.extend(("--pedal-drawbars", "60"))
        before = self.paths()
        result = self.invoke(arguments)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(self.paths(), before | {output})
        self.assertEqual(output.read_bytes(), expected)

    def rejected(self, arguments, needle=None):
        before = self.paths()
        result = self.invoke(arguments)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr.strip())
        if needle is not None:
            self.assertIn(needle, result.stderr)
        self.assertEqual(self.paths(), before, "Rejection left output or temporary work")
        self.assertEqual(self.profile.read_bytes(), self.profile_bytes)
        return result

    def render(self, text, *, frames=1024, rate=48000, block=64,
               registration=None, extra=()):
        source = self.score(text)
        output = self.unique("wav")
        arguments = self.arguments(output, frames=frames, rate=rate, block=block, score=source)
        if registration is not None:
            arguments.extend(("--pedal-drawbars", registration))
        arguments.extend(extra)
        before = self.paths()
        result = self.invoke(arguments)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(self.paths(), before | {output})
        report = json.loads(result.stdout, parse_constant=invalid_json_constant)
        self.assertIs(type(report["render_schema_version"]), int)
        self.assertEqual(report["render_schema_version"], 3)
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["evidence_status"], "unmeasured")
        for key, value in (("frames", frames), ("sample_rate", rate),
                           ("block_size", block), ("seed", 13), ("channels", 2)):
            self.assertEqual(report[key], value, key)
        for field in ("peak", "rms"):
            self.assertTrue(math.isfinite(report[field]))
            self.assertGreaterEqual(report[field], 0)
        data = output.read_bytes()
        self.assertEqual(len(data), 44 + frames * 4)
        header = struct.unpack_from("<4sI4s4sIHHIIHH4sI", data)
        self.assertEqual(header, (b"RIFF", len(data) - 8, b"WAVE", b"fmt ", 16, 1, 2,
                                  rate, rate * 4, 4, 16, b"data", frames * 4))
        samples = struct.unpack_from(f"<{frames * 2}h", data, 44)
        self.assertEqual(samples[::2], samples[1::2])
        return data, samples[::2], report

    def test_help_names_explicit_pedal_domains_and_nominal_models(self):
        before = self.paths()
        result = self.invoke(["--help"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        for value in ("--pedal-drawbars", "pedal_on", "pedal_off", "pedal_drawbar",
                      "pedal_all_notes_off", "one-based pedal ID1..25", "schema 3",
                      "unmeasured static transfer"):
            self.assertIn(value, result.stdout)
        self.assertEqual(self.paths(), before)

    def test_summary_identifies_actual_map_and_fixed_transfer_even_when_muted(self):
        _, samples, metrics = self.render("0 pedal_on lower 8 127\n", frames=257)
        self.assertFalse(any(samples))
        expected = {
            "model": "ideal-shared-sine-v1",
            "contact_model": "ideal-contacts-v1",
            "percussion_model": "shared-readiness-v1",
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
        raw = (ROOT / "data" / "pedal-map.json").read_bytes()
        canonical = json.dumps(json.loads(raw), sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False, allow_nan=False).encode("utf-8")
        expected["pedal_map_raw_sha256"] = hashlib.sha256(raw).hexdigest()
        expected["pedal_map_canonical_sha256"] = hashlib.sha256(canonical).hexdigest()
        for reading in ("a", "b"):
            path = ROOT / "data" / "references" / f"review-{reading}-pedal.csv"
            expected[f"pedal_reference_{reading}_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        for key, value in expected.items():
            self.assertEqual(metrics[key], value, key)
        self.assertIs(type(metrics["pedal_mixture_denominator"]), int)
        self.assertIs(type(metrics["pedal_gain_denominator"]), int)

    def test_all_twenty_five_pedals_are_audible_at_each_supported_rate(self):
        for rate in (44100, 48000, 96000):
            for pedal in range(1, 26):
                with self.subTest(rate=rate, pedal=pedal):
                    _, samples, metrics = self.render(
                        f"0 pedal_on lower {pedal} 1\n128 pedal_off lower {pedal} 0\n",
                        frames=257, rate=rate, registration="80")
                    self.assertTrue(any(samples[:128]))
                    self.assertFalse(any(samples[128:]))
                    self.assertGreater(metrics["peak"], 0)
                    self.assertEqual(metrics["clipped_frames"], 0)

    def test_all_initial_position_pairs_equal_frame_zero_scored_positions(self):
        gesture = "0 pedal_on lower 13 100\n200 pedal_off lower 13 0\n"
        for first in range(9):
            for second in range(9):
                with self.subTest(first=first, second=second):
                    initial = self.render(gesture, frames=257, registration=f"{first}{second}")
                    scored = self.render(
                        f"0 pedal_drawbar lower 0 {first}\n0 pedal_drawbar lower 1 {second}\n" + gesture,
                        frames=257)
                    self.assertEqual(initial, scored)

    def test_score_frame_zero_overrides_initial_pedal_positions(self):
        text = ("0 pedal_drawbar lower 0 2\n0 pedal_drawbar lower 1 5\n"
                "0 pedal_on lower 13 127\n")
        self.assertEqual(self.render(text, registration="88"), self.render(text))

    def test_muted_and_unplayed_pedals_preserve_manual_pcm(self):
        manual = ("0 drawbar upper 2 8\n0 note_on upper 60 100\n"
                  "500 note_off upper 60 0\n")
        pedal_events = "".join(f"0 pedal_on lower {pedal} 127\n" for pedal in range(1, 26))
        muted = pedal_events + manual.split("500", 1)[0] + (
            "100 pedal_all_notes_off lower 0 0\n500 note_off upper 60 0\n")
        expected = self.render(manual)
        self.assertEqual(expected, self.render(manual, registration="00"))
        self.assertEqual(expected, self.render(manual, registration="88"))
        self.assertEqual(expected, self.render(muted))

    def test_muted_held_pedal_unmutes_at_continuous_source_phase(self):
        full = self.render("0 pedal_on lower 7 127\n", registration="53")
        delayed = self.render("0 pedal_on lower 7 127\n"
                              "277 pedal_drawbar lower 0 5\n277 pedal_drawbar lower 1 3\n")
        self.assertFalse(any(delayed[1][:277]))
        self.assertEqual(delayed[1][277:], full[1][277:])

    def test_velocity_zero_duplicate_press_and_repeated_release_semantics(self):
        expected = self.render("0 pedal_on lower 25 1\n500 pedal_off lower 25 0\n", registration="28")
        for velocity in (1, 64, 127):
            for release in ("pedal_off lower 25 0", "pedal_on lower 25 0"):
                with self.subTest(velocity=velocity, release=release):
                    actual = self.render(
                        f"0 pedal_on lower 25 {velocity}\n100 pedal_on lower 25 127\n"
                        f"500 {release}\n501 pedal_off lower 25 0\n", registration="28")
                    self.assertEqual(actual, expected)

    def test_division_cancel_reselect_and_panic_are_independent(self):
        pedal = "0 pedal_on lower 7 100\n0 pedal_on lower 8 100\n0 pedal_on lower 13 100\n"
        edits = ("100 cancel lower 0 0\n200 select_bank lower 0 0\n"
                 "300 all_notes_off lower 0 0\n400 all_notes_off upper 0 0\n"
                 "500 cancel upper 0 0\n600 select_bank upper 0 1\n")
        self.assertEqual(self.render(pedal, registration="46"),
                         self.render(pedal + edits, registration="46"))
        manual = "0 drawbar lower 2 8\n0 note_on lower 60 100\n"
        self.assertEqual(self.render(manual), self.render(manual + "250 pedal_all_notes_off lower 0 0\n"))

    def test_pedal_panic_releases_every_pedal_at_the_exact_frame(self):
        notes = "".join(f"0 pedal_on lower {pedal} 100\n" for pedal in range(1, 26))
        panic = self.render(notes + "111 pedal_all_notes_off lower 0 0\n", frames=257, registration="22")
        releases = "".join(f"111 pedal_off lower {pedal} 0\n" for pedal in range(1, 26))
        self.assertEqual(panic, self.render(notes + releases, frames=257, registration="22"))
        self.assertTrue(any(panic[1][:111]))
        self.assertFalse(any(panic[1][111:]))

    def test_manual_contact_mode_never_invents_pedal_travel(self):
        score = "0 pedal_on lower 8 127\n127 pedal_off lower 8 0\n"
        ideal = self.render(score, frames=257, registration="72")
        nominal = self.render(score, frames=257, registration="72", extra=("--contacts", "nominal"))
        self.assertEqual(ideal[:2], nominal[:2])
        self.assertEqual(nominal[2]["contact_model"], "nominal-linear-travel-v1")
        self.assertEqual(nominal[2]["pedal_contact_model"], "ideal-eight-contact-pedal-v1")

    def test_same_frame_order_and_dense_partitioning_preserve_audio(self):
        quiet = self.render("0 pedal_on lower 1 100\n0 pedal_off lower 1 0\n",
                            frames=257, registration="80")
        audible = self.render("0 pedal_off lower 1 0\n0 pedal_on lower 1 100\n",
                              frames=257, registration="80")
        self.assertFalse(any(quiet[1]))
        self.assertTrue(any(audible[1]))
        lines = ["0 pedal_on lower 13 100"] + ["0 pedal_drawbar lower 0 8"] * 1023
        for frame in range(1, 1201):
            lines.extend((f"{frame} pedal_drawbar lower 0 {frame % 9}",
                          f"{frame} pedal_drawbar lower 1 {(frame * 2) % 9}"))
        lines.append("1400 pedal_all_notes_off lower 0 0")
        score = "\n".join(lines) + "\n"
        expected = None
        for block in (1, 17, 64, 127, 512, 65536):
            with self.subTest(block=block):
                actual = self.render(score, frames=1501, block=block)
                if expected is None:
                    expected = actual
                else:
                    self.assertEqual(actual[:2], expected[:2])
                    self.assertEqual({k: v for k, v in actual[2].items() if k != "block_size"},
                                     {k: v for k, v in expected[2].items() if k != "block_size"})

    def test_invalid_pedal_registration_flags_reject_before_output(self):
        for value in ("", "0", "000", "90", "09", "-1", "+1", "1.0", "ab", "８0"):
            with self.subTest(value=value):
                self.rejected(self.arguments(self.unique("wav")) + ["--pedal-drawbars", value])
        self.rejected(self.arguments(self.unique("wav")) + ["--pedal-drawbars"])
        self.rejected(self.arguments(self.unique("wav")) +
                      ["--pedal-drawbars", "80", "--pedal-drawbars", "08"], "Duplicate")

    def test_invalid_early_and_late_pedal_commands_leave_no_output(self):
        invalid = [
            "pedal_on lower 0 100", "pedal_on lower 26 100", "pedal_on lower 256 100",
            "pedal_on lower 18446744073709551615 100", "pedal_on lower -1 100",
            "pedal_on lower 1.0 100", "pedal_on lower 1 -1", "pedal_on lower 1 128",
            "pedal_on lower 1 1.5", "pedal_on lower 1 nan", "pedal_on lower 1 inf",
            "pedal_on lower 1 1e309", "pedal_off lower 0 0", "pedal_off lower 26 0",
            "pedal_off lower 1 1", "pedal_off lower 1 -1", "pedal_off lower 1 nan",
            "pedal_drawbar lower 2 8", "pedal_drawbar lower 255 8",
            "pedal_drawbar lower 0 -1", "pedal_drawbar lower 0 9", "pedal_drawbar lower 0 0.5",
            "pedal_drawbar lower 0 inf", "pedal_all_notes_off lower 1 0",
            "pedal_all_notes_off lower 0 1", "pedal_all_notes_off lower 0 -1",
            "pedal_on upper 1 100", "pedal_off upper 1 0", "pedal_drawbar upper 0 8",
            "pedal_all_notes_off upper 0 0", "pedal_on pedals 1 100",
            "Pedal_on lower 1 100", "pedal_on lower 1 100 extra", "pedal_on lower 1",
        ]
        for command in invalid:
            for frame in (0, 1000):
                with self.subTest(command=command, frame=frame):
                    prefix = "" if frame == 0 else "0 pedal_drawbar lower 0 8\n0 pedal_on lower 1 100\n"
                    score = self.score(prefix + f"{frame} {command}\n")
                    self.rejected(self.arguments(self.unique("wav"), score=score), "Event score line")

    def test_score_capacity_boundaries_and_zero_frame_render_reject_without_output(self):
        score = self.score("0 pedal_on lower 1 100\n" * 1025)
        self.rejected(self.arguments(self.unique("wav"), score=score), "1024")
        for text in ("1024 pedal_on lower 1 100\n",
                     "100 pedal_on lower 1 100\n99 pedal_off lower 1 0\n"):
            self.rejected(self.arguments(self.unique("wav"), score=self.score(text)))
        self.rejected(self.arguments(self.unique("wav"), frames=0), "Frames must be positive")

    def test_pedal_render_preserves_existing_destination_and_score_collision(self):
        score = self.score("0 pedal_on lower 1 100\n")
        output = self.unique("wav")
        sentinel = b"existing destination remains unchanged\n"
        output.write_bytes(sentinel)
        self.rejected(self.arguments(output, score=score) + ["--pedal-drawbars", "80"], "already exists")
        self.assertEqual(output.read_bytes(), sentinel)
        source_bytes = score.read_bytes()
        self.rejected(self.arguments(score, score=score) + ["--pedal-drawbars", "80"], "collides")
        self.assertEqual(score.read_bytes(), source_bytes)

    def test_dense_manual_and_pedal_clipping_keeps_existing_failure_policy(self):
        lines = [f"0 drawbar {manual} {index} 8" for manual in ("upper", "lower")
                 for index in range(9)]
        lines.extend(f"0 note_on {manual} {note} 127" for manual in ("upper", "lower")
                     for note in range(36, 97))
        lines.extend(f"0 pedal_on lower {pedal} 127" for pedal in range(1, 26))
        text = "\n".join(lines) + "\n"
        _, samples, loud = self.render(text, frames=1025, block=127, registration="88")
        self.assertGreater(loud["peak"], 1.0)
        self.assertGreater(loud["clipped_frames"], 0)
        self.assertTrue(any(value in (-32768, 32767) for value in samples))
        output = self.unique("wav")
        score = self.score(text)
        arguments = self.arguments(output, frames=1025, block=127, score=score)
        arguments.extend(("--pedal-drawbars", "88", "--fail-on-clip"))
        before = self.paths()
        result = self.invoke(arguments)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("clipping", result.stderr)
        self.assertEqual(self.paths(), before)
        failed = json.loads(result.stdout, parse_constant=invalid_json_constant)
        self.assertEqual(failed["status"], "clipped")
        self.assertEqual({**failed, "status": "ok"}, loud)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--renderer")
    parser.add_argument("--profile")
    args, remaining = parser.parse_known_args()
    RENDERER_OVERRIDE = args.renderer
    PROFILE_OVERRIDE = args.profile
    unittest.main(argv=[__file__, *remaining])
