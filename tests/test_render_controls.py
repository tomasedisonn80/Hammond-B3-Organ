#!/usr/bin/env python3
"""Author regressions for additive saved-controls rendering.

CTest supplies HAMMOND_RENDER_EXECUTABLE and HAMMOND_TEST_PROFILE. Direct use
accepts --renderer/--profile. Missing configured inputs fail, never skip.
These are nominal software/audio checks, not physical or live-recall evidence.
"""

import argparse
import errno
import hashlib
import json
import os
from pathlib import Path
import stat
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(os.environ.get("HAMMOND_SOURCE_DIR", Path(__file__).resolve().parents[1]))
RENDERER_OVERRIDE = None
PROFILE_OVERRIDE = None
CATALOG = (
    "registration_catalog atlas-chapel-nominal-v1 sha256 "
    "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf\n"
)
STATE4 = (
    "B3CONTROLS4\n" + CATALOG +
    "expression 0.375\n"
    "percussion enabled 1 harmonic third volume soft decay fast\n"
    "pedal drawbars 2 7\n"
    "manual upper selected B fixed_registration C# route_enabled 0\n"
    "bank A 0 1 2 3 4 5 6 7 8\n"
    "bank B 8 7 6 5 4 3 2 1 0\n"
    "manual lower selected A fixed_registration A route_enabled 1\n"
    "bank A 1 3 5 7 0 2 4 6 8\n"
    "bank B 8 6 4 2 0 7 5 3 1\n"
    "end\n"
)

# Independently spelled event initialization, never produced by the state
# parser/writer. All banks precede remembered-bank/fixed selection and Cancel.
INITIAL_SCORE = """0 bank_drawbar upper 0 0
0 bank_drawbar upper 1 1
0 bank_drawbar upper 2 2
0 bank_drawbar upper 3 3
0 bank_drawbar upper 4 4
0 bank_drawbar upper 5 5
0 bank_drawbar upper 6 6
0 bank_drawbar upper 7 7
0 bank_drawbar upper 8 8
0 bank_drawbar upper 9 8
0 bank_drawbar upper 10 7
0 bank_drawbar upper 11 6
0 bank_drawbar upper 12 5
0 bank_drawbar upper 13 4
0 bank_drawbar upper 14 3
0 bank_drawbar upper 15 2
0 bank_drawbar upper 16 1
0 bank_drawbar upper 17 0
0 bank_drawbar lower 0 1
0 bank_drawbar lower 1 3
0 bank_drawbar lower 2 5
0 bank_drawbar lower 3 7
0 bank_drawbar lower 4 0
0 bank_drawbar lower 5 2
0 bank_drawbar lower 6 4
0 bank_drawbar lower 7 6
0 bank_drawbar lower 8 8
0 bank_drawbar lower 9 8
0 bank_drawbar lower 10 6
0 bank_drawbar lower 11 4
0 bank_drawbar lower 12 2
0 bank_drawbar lower 13 0
0 bank_drawbar lower 14 7
0 bank_drawbar lower 15 5
0 bank_drawbar lower 16 3
0 bank_drawbar lower 17 1
0 select_bank upper 0 1
0 select_bank lower 0 0
0 select_preset upper 0 1
0 select_preset lower 0 9
0 cancel upper 0 0
0 pedal_drawbar lower 0 2
0 pedal_drawbar lower 1 7
0 percussion upper 0 1
0 percussion upper 1 1
0 percussion upper 2 1
0 percussion upper 3 1
0 expression upper 0 0.375
"""

# Exercise cancelled fixed memory, every hidden bank, upper-B percussion,
# route-independent pedals, tied notes, and common partition boundaries.
PHRASE = """0 note_on upper 60 100
0 note_on lower 48 100
0 pedal_on lower 1 100
17 select_preset upper 0 1
64 select_bank upper 0 1
127 note_off upper 60 0
127 note_on upper 64 100
128 select_bank lower 0 1
511 select_bank upper 0 0
512 note_off upper 64 0
512 note_on upper 67 100
1023 cancel lower 0 0
1024 select_preset lower 0 9
1536 select_bank lower 0 0
1792 pedal_off lower 1 0
2048 pedal_on lower 25 100
2560 note_off upper 67 0
3072 note_off lower 48 0
3584 pedal_all_notes_off lower 0 0
"""


def required_file(value, fallback, label):
    path = Path(value) if value is not None else fallback
    if not path.is_file():
        raise RuntimeError(f"Missing {label}: {path}; build coherent inputs before testing")
    return path.resolve()


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError(f"Nonfinite JSON constant: {value}")


class RenderControlsTests(unittest.TestCase):
    calls = 0

    @classmethod
    def setUpClass(cls):
        name = "hammond_render.exe" if os.name == "nt" else "hammond_render"
        cls.renderer = required_file(
            RENDERER_OVERRIDE if RENDERER_OVERRIDE is not None
            else os.environ.get("HAMMOND_RENDER_EXECUTABLE"),
            ROOT / "build" / name, "renderer")
        cls.profile_source = required_file(
            PROFILE_OVERRIDE if PROFILE_OVERRIDE is not None
            else os.environ.get("HAMMOND_TEST_PROFILE"),
            cls.renderer.parent / "nominal.b3p", "compiled profile")
        cls.profile_bytes = cls.profile_source.read_bytes()

    @classmethod
    def tearDownClass(cls):
        print(f"saved-controls renderer: {cls.calls} actual CLI invocations")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-render-controls-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.profile = self.work / "organ profile ü.b3p"
        self.profile.write_bytes(self.profile_bytes)
        self.serial = 0

    def unique(self, suffix):
        self.serial += 1
        return self.work / f"result {self.serial}.{suffix}"

    def write(self, text, suffix="b3controls", name=None):
        path = self.work / name if name is not None else self.unique(suffix)
        path.write_bytes(text.encode("utf-8") if isinstance(text, str) else text)
        return path

    def snapshot(self):
        result = {}
        for path in self.work.rglob("*"):
            mode = path.lstat().st_mode
            key = str(path.relative_to(self.work))
            if stat.S_ISLNK(mode):
                result[key] = ("link", os.readlink(path))
            elif stat.S_ISREG(mode):
                result[key] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
            else:
                result[key] = ("other", stat.S_IFMT(mode))
        return result

    def arguments(self, output, *, controls=None, score=None, frames=4097,
                  rate=48000, block=64, contacts="ideal"):
        result = ["--profile", self.profile, "--output", output, "--frames", frames,
                  "--sample-rate", rate, "--block-size", block, "--seed", 73,
                  "--contacts", contacts]
        if controls is not None:
            result.extend(("--controls", controls))
        if score is not None:
            result.extend(("--events", score))
        return result

    def invoke(self, arguments):
        type(self).calls += 1
        return subprocess.run(
            [str(self.renderer), *map(str, arguments)], cwd=self.work,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=15, check=False)

    def rejected(self, arguments, message=None):
        before = self.snapshot()
        result = self.invoke(arguments)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr.strip())
        if message is not None:
            self.assertIn(message, result.stderr)
        self.assertEqual(self.snapshot(), before, "Refusal changed input/output or left staging")
        return result

    def render(self, *, controls=None, text=None, extra=(), **settings):
        output = self.unique("wav")
        score = self.write(text, "events") if text is not None else None
        arguments = self.arguments(output, controls=controls, score=score, **settings)
        before = self.snapshot()
        result = self.invoke([*arguments, *extra])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout.count("\n"), 1, "Summary must be one JSON line")
        report = json.loads(result.stdout, object_pairs_hook=strict_object,
                            parse_constant=invalid_constant)
        data = output.read_bytes()
        after = self.snapshot()
        del after[str(output.relative_to(self.work))]
        self.assertEqual(after, before, "Successful render changed inputs or left staging")
        frames = settings.get("frames", 4097)
        rate = settings.get("rate", 48000)
        self.assertEqual(len(data), 44 + frames * 4)
        self.assertEqual(struct.unpack_from("<4sI4s4sIHHIIHH4sI", data), (
            b"RIFF", len(data) - 8, b"WAVE", b"fmt ", 16, 1, 2,
            rate, rate * 4, 4, 16, b"data", frames * 4))
        samples = struct.unpack_from(f"<{frames * 2}h", data, 44)
        self.assertEqual(samples[::2], samples[1::2])
        self.assertEqual(report["evidence_status"], "unmeasured")
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["render_schema_version"], 6 if controls is not None else
                         5 if "--source-leakage" in extra else 3)
        if controls is None:
            self.assertNotIn("controls", report)
        return data, samples[::2], report

    def assert_provenance(self, report, path, raw, canonical=STATE4, version=4):
        self.assertEqual(report["controls"], {
            "schema_version": 1,
            "restore_policy": "full-state-including-expression",
            "path": str(path.resolve()),
            "source_version": version,
            "source_bytes": len(raw),
            "canonical_b3controls4": canonical,
        })
        for key in ("schema_version", "source_version", "source_bytes"):
            self.assertIs(type(report["controls"][key]), int)

    def test_help_explains_full_state_expression_and_score_precedence(self):
        before = self.snapshot()
        result = self.invoke(["--help"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        for text in ("--controls", "including expression", "suffix", "schema 6",
                     "score events take precedence"):
            self.assertIn(text, result.stdout)
        self.assertEqual(self.snapshot(), before)

    def test_suffixes_preserve_complete_initial_identity_and_base_fields(self):
        raw = (" \t\n" + STATE4 + "\r\n").encode("ascii")
        baseline = None
        for suffix in ("b3registration", "b3performance", "b3controls", "other"):
            with self.subTest(suffix=suffix):
                path = self.write(raw, name=f"saved controls Ω.{suffix}")
                data, samples, report = self.render(controls=path, text=PHRASE)
                self.assert_provenance(report, path, raw)
                self.assertTrue(any(samples))
                if baseline is not None:
                    self.assertEqual(data, baseline)
                baseline = data
        _, _, old_report = self.render(text=INITIAL_SCORE + PHRASE)
        self.assertEqual(set(report), set(old_report) | {"controls"})
        self.assertEqual(old_report["render_schema_version"], 3)

    def test_full_state_matches_independent_score_across_rates_contacts_and_blocks(self):
        controls = self.write(STATE4)
        for rate in (44100, 48000, 96000):
            for contacts in ("ideal", "nominal"):
                expected, expected_samples, expected_report = self.render(
                    text=INITIAL_SCORE + PHRASE, rate=rate, contacts=contacts, block=127)
                self.assertTrue(any(expected_samples))
                for block in (1, 17, 64, 127, 512):
                    with self.subTest(rate=rate, contacts=contacts, block=block):
                        actual, _, report = self.render(
                            controls=controls, text=PHRASE, rate=rate,
                            contacts=contacts, block=block)
                        self.assertEqual(actual, expected)
                        for key in ("peak", "rms", "clipped_frames", "clipped_channel_samples"):
                            self.assertEqual(report[key], expected_report[key], key)

    def test_legacy_versions_migrate_to_exact_state4_and_equivalent_audio(self):
        for version in (1, 2, 3):
            with self.subTest(version=version):
                canonical = STATE4.replace("fixed_registration C#", "fixed_registration none")
                canonical = canonical.replace("fixed_registration A", "fixed_registration none")
                initial = INITIAL_SCORE.replace("0 select_preset upper 0 1\n", "")
                initial = initial.replace("0 select_preset lower 0 9\n", "")
                if version < 3:
                    canonical = canonical.replace("pedal drawbars 2 7", "pedal drawbars 0 0")
                    initial = initial.replace("0 pedal_drawbar lower 0 2", "0 pedal_drawbar lower 0 0")
                    initial = initial.replace("0 pedal_drawbar lower 1 7", "0 pedal_drawbar lower 1 0")
                if version == 1:
                    canonical = canonical.replace(
                        "percussion enabled 1 harmonic third volume soft decay fast",
                        "percussion enabled 0 harmonic second volume normal decay slow")
                    for index in range(4):
                        initial = initial.replace(f"0 percussion upper {index} 1",
                                                  f"0 percussion upper {index} 0")
                legacy = canonical.replace("B3CONTROLS4", f"B3CONTROLS{version}")
                legacy = legacy.replace(CATALOG, "").replace(" fixed_registration none", "")
                if version < 3:
                    legacy = legacy.replace("pedal drawbars 0 0\n", "")
                if version == 1:
                    legacy = legacy.replace(
                        "percussion enabled 0 harmonic second volume normal decay slow\n", "")
                path = self.write(legacy)
                data, samples, report = self.render(controls=path, text=PHRASE)
                expected, _, _ = self.render(text=initial + PHRASE)
                self.assertEqual(data, expected)
                self.assertTrue(any(samples))
                self.assert_provenance(report, path, legacy.encode("ascii"), canonical, version)

    def test_signed_zero_and_frame_zero_then_later_tied_score_precedence(self):
        zero = STATE4.replace("expression 0.375", "expression -0")
        controls = self.write(zero)
        _, silent, silent_report = self.render(controls=controls, text=PHRASE)
        self.assertFalse(any(silent))
        self.assert_provenance(silent_report, controls, zero.encode("ascii"), zero)
        score = """0 expression upper 0 0.125
0 expression lower 0 0.5
0 select_bank upper 0 1
0 note_on upper 60 100
64 expression upper 0 0.75
64 expression upper 0 0.25
127 note_off upper 60 0
127 note_on upper 62 100
2048 note_off upper 62 0
"""
        data, samples, report = self.render(controls=controls, text=score, block=17)
        expected, _, _ = self.render(text=INITIAL_SCORE + score, block=17)
        self.assertEqual(data, expected)
        self.assertTrue(any(samples))
        # Canonical provenance stays at admitted -0 even though scored expression
        # changes before the first sample. PCM silence alone cannot prove its sign.
        self.assert_provenance(report, controls, zero.encode("ascii"), zero)
        last_only = score.replace("0 expression upper 0 0.125\n", "")
        last_only = last_only.replace("64 expression upper 0 0.75\n", "")
        last_data, _, _ = self.render(controls=controls, text=last_only, block=512)
        self.assertEqual(data, last_data)

    def test_default_note_and_explicit_note_follow_restoration(self):
        state = STATE4.replace("selected B fixed_registration C# route_enabled 0",
                               "selected B fixed_registration none route_enabled 1")
        controls = self.write(state)
        for note, extra in ((60, ()), (72, ("--note", 72))):
            with self.subTest(note=note):
                actual, samples, _ = self.render(controls=controls, extra=extra)
                expected, _, _ = self.render(
                    controls=controls,
                    text=f"0 note_on upper {note} 100\n3072 note_off upper {note} 0\n")
                self.assertEqual(actual, expected)
                self.assertTrue(any(samples))

    def test_explicit_default_control_flags_conflict_in_either_order(self):
        controls = self.write(STATE4)
        for flag, value in (("--drawbars", "888000000"), ("--pedal-drawbars", "00"),
                            ("--percussion", "off"), ("--percussion-volume", "normal"),
                            ("--percussion-decay", "slow")):
            for controls_first in (False, True):
                with self.subTest(flag=flag, controls_first=controls_first):
                    args = self.arguments(self.unique("wav"))
                    pairs = ["--controls", controls, flag, value] if controls_first else [
                        flag, value, "--controls", controls]
                    self.rejected(args + pairs, "incompatible with explicit " + flag)

    def test_controls_option_bounds_and_note_score_conflict(self):
        controls = self.write(STATE4)
        base = self.arguments(self.unique("wav"))
        self.rejected(base + ["--controls"], "Missing value")
        self.rejected(base + ["--controls", ""], "Missing or oversized")
        self.rejected(base + ["--controls", "x" * 4097], "oversized")
        self.rejected(base + ["--controls", "--events"], "Missing or oversized")
        self.rejected(base + ["--controls", controls, "--controls", controls], "Duplicate")
        self.rejected(base + ["--controls=" + str(controls)], "Unknown argument")
        score = self.write(PHRASE, "events")
        self.rejected(base + ["--controls", controls, "--events", score, "--note", 60],
                      "--note is incompatible with --events")

    def test_malformed_payloads_refuse_without_any_file_changes(self):
        raw = STATE4.encode("ascii")
        invalid = (
            b"", raw.replace(b"B3CONTROLS4", b"B3CONTROLS5"),
            raw.replace(b"c9f1dd2d", b"d9f1dd2d"), raw + b"trailing\n",
            raw[:-4], raw.replace(b"expression 0.375", b"expression nan"),
            raw.replace(b"expression 0.375", b"expression 1e9999"),
            raw.replace(b"expression 0.375", b"expression -0.1"),
            raw.replace(b"bank A 0 1", b"bank A 9 1"),
            raw.replace(b"fixed_registration C#", b"fixed_registration None"),
            raw.replace(b"pedal drawbars 2 7\n", b""), b"\xef\xbb\xbf" + raw,
            raw + b"\x00", raw + b" " * (16385 - len(raw)),
        )
        for number, payload in enumerate(invalid):
            with self.subTest(case=number):
                controls = self.write(payload)
                self.rejected(self.arguments(self.unique("wav"), controls=controls))

    def test_whole_input_limit_includes_whitespace_and_reports_raw_bytes(self):
        raw = STATE4.encode("ascii")
        exact = raw + b" " * (16384 - len(raw))
        controls = self.write(exact)
        _, _, report = self.render(controls=controls, text=PHRASE)
        self.assert_provenance(report, controls, exact)
        excess = self.write(exact + b" ")
        self.rejected(self.arguments(self.unique("wav"), controls=excess))

    def test_existing_output_and_control_collision_preserve_all_bytes(self):
        controls = self.write(STATE4)
        output = self.write(b"existing destination must survive\n", "wav")
        self.rejected(self.arguments(output, controls=controls), "already exists")
        self.rejected(self.arguments(controls, controls=controls), "collides")
        hard_link = self.unique("wav")
        os.link(controls, hard_link)
        self.rejected(self.arguments(hard_link, controls=controls), "already exists")

    def test_missing_directory_and_invalid_other_input_are_preflight_refusals(self):
        controls = self.write(STATE4)
        self.rejected(self.arguments(self.unique("wav"), controls=self.work / "missing"))
        self.rejected(self.arguments(self.unique("wav"), controls=self.work))
        score = self.write("0 unknown upper 0 0\n", "events")
        self.rejected(self.arguments(self.unique("wav"), controls=controls, score=score),
                      "Unknown event type")
        invalid_profile = self.write(b"not a profile\n", "b3p")
        args = self.arguments(self.unique("wav"), controls=controls)
        args[args.index("--profile") + 1] = invalid_profile
        self.rejected(args, "Cannot load profile")

    def test_leaf_links_refuse_but_ancestor_links_resolve(self):
        folder = self.work / "real directory"
        folder.mkdir()
        controls = folder / "saved Ω.b3registration"
        controls.write_bytes(STATE4.encode("ascii"))
        leaf = self.work / "leaf.b3controls"
        ancestor = self.work / "ancestor"
        try:
            leaf.symlink_to(controls)
            ancestor.symlink_to(folder, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"This runner cannot create test symlinks: {error}")
        self.rejected(self.arguments(self.unique("wav"), controls=leaf))
        _, _, report = self.render(controls=ancestor / controls.name, text=PHRASE)
        self.assert_provenance(report, controls, STATE4.encode("ascii"))
        self.rejected(self.arguments(leaf, controls=controls), "collides")

    @unittest.skipUnless(os.name == "posix" and hasattr(os, "mkfifo"), "POSIX FIFO admission")
    def test_fifo_refuses_without_waiting_for_a_writer(self):
        controls = self.unique("fifo")
        os.mkfifo(controls)
        self.rejected(self.arguments(self.unique("wav"), controls=controls))

    @unittest.skipUnless(os.name == "posix", "POSIX raw filename bytes")
    def test_invalid_utf8_leaf_and_resolved_ancestor_refuse(self):
        folder = self.work / os.fsdecode(b"directory-\xfe")
        try:
            controls = self.write(STATE4, name=os.fsdecode(b"invalid-\xff.b3controls"))
            folder.mkdir()
        except OSError as error:
            if error.errno in (errno.EILSEQ, errno.EINVAL):
                self.skipTest(f"This volume rejects invalid UTF-8 filenames: {error}")
            raise
        self.rejected(self.arguments(self.unique("wav"), controls=controls), "UTF-8")
        (folder / "valid.b3controls").write_bytes(STATE4.encode("ascii"))
        alias = self.work / "valid-ancestor-link"
        alias.symlink_to(folder, target_is_directory=True)
        self.rejected(self.arguments(self.unique("wav"), controls=alias / "valid.b3controls"),
                      "UTF-8")

    @unittest.skipUnless(os.name == "posix", "POSIX filename control/quote characters")
    def test_controls_path_and_canonical_lines_are_json_escaped(self):
        controls = self.write(STATE4, name='quote" slash\\ tab\t newline\n Ω.b3controls')
        _, _, report = self.render(controls=controls, text=PHRASE)
        self.assert_provenance(report, controls, STATE4.encode("ascii"))

    def test_controls_with_leakage_keep_provenance_and_headroom_admission(self):
        author = ROOT / "data" / "source-leakage" / "synthetic-pair-demo-v1.json"
        graph = self.unique("b3leakage")
        compiled = subprocess.run(
            [sys.executable, "-B", str(ROOT / "tools" / "compile_source_leakage.py"),
             "--input", str(author), "--output", str(graph)],
            capture_output=True, text=True, encoding="utf-8", timeout=15, check=False)
        self.assertEqual(compiled.returncode, 0, compiled.stdout + compiled.stderr)
        controls = self.write(STATE4)
        extra = ("--source-leakage", graph, "--leakage-input-gain", "0.5")
        actual, _, report = self.render(controls=controls, text=PHRASE, extra=extra)
        expected, _, plain_report = self.render(text=INITIAL_SCORE + PHRASE, extra=extra)
        self.assertEqual(actual, expected)
        self.assertEqual(plain_report["render_schema_version"], 5)
        self.assertEqual(set(report), set(plain_report) | {"controls"})
        for key, value in plain_report.items():
            if key != "render_schema_version":
                self.assertEqual(report[key], value, key)
        self.assert_provenance(report, controls, STATE4.encode("ascii"))
        self.rejected(self.arguments(self.unique("wav"), controls=controls) + [
            "--source-leakage", graph, "--leakage-input-gain", "1"], "headroom admission")
        self.rejected(self.arguments(self.unique("wav"), controls=controls) + [
            "--source-leakage", graph], "must be supplied together")

    def test_clipping_refusal_keeps_schema6_and_does_not_publish(self):
        state = STATE4.replace("expression 0.375", "expression 1")
        state = state.replace("pedal drawbars 2 7", "pedal drawbars 8 8")
        state = state.replace("fixed_registration C# route_enabled 0",
                              "fixed_registration none route_enabled 1")
        state = state.replace("fixed_registration A", "fixed_registration none")
        state = "\n".join(
            (line[:7] + " ".join("8" * 9)) if line.startswith("bank ") else line
            for line in state.splitlines()) + "\n"
        controls = self.write(state)
        notes = [f"0 note_on {manual} {note} 127"
                 for manual in ("upper", "lower") for note in range(36, 97)]
        notes.extend(f"0 pedal_on lower {pedal} 127" for pedal in range(1, 26))
        score = "\n".join(notes) + "\n"
        _, _, ordinary = self.render(controls=controls, text=score, frames=1025, block=127)
        self.assertGreater(ordinary["clipped_frames"], 0)
        score_path = self.write(score, "events")
        arguments = self.arguments(self.unique("wav"), controls=controls,
                                   score=score_path, frames=1025, block=127)
        before = self.snapshot()
        result = self.invoke(arguments + ["--fail-on-clip"])
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("clipping detected", result.stderr)
        self.assertEqual(self.snapshot(), before)
        report = json.loads(result.stdout, object_pairs_hook=strict_object,
                            parse_constant=invalid_constant)
        self.assertEqual(report, {**ordinary, "status": "clipped"})
        self.assert_provenance(report, controls, state.encode("ascii"), state)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--renderer")
    parser.add_argument("--profile")
    arguments, remaining = parser.parse_known_args()
    RENDERER_OVERRIDE = arguments.renderer
    PROFILE_OVERRIDE = arguments.profile
    unittest.main(argv=[__file__, *remaining])
