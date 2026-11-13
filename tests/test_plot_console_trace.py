#!/usr/bin/env python3
"""Independent schema fixtures and publication/plot checks; no C++ prerequisite."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "plot_console_trace.py"
SPEC = importlib.util.spec_from_file_location("trace_plot_under_test", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Cannot load the trace plotter")
plot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plot)

# Authored from the published CSV contract, not imported from the plotter or the
# trace generator. This is a structural fixture, not a claimed Engine simulation.
HEADER = (
    "frame,time_seconds,position,target,c0,c1,c2,c3,c4,c5,c6,c7,c8,"
    "companion_position,companion_target,companion_c0,companion_c1,companion_c2,"
    "companion_c3,companion_c4,companion_c5,companion_c6,companion_c7,companion_c8,"
    "readiness,physical_detector,eligible,routed_detector,percussion_gain,"
    "upper_sustain_gain,route_enabled,selected_bank,percussion_enabled,"
    "primary_phase_turns,companion_phase_turns,audio"
)
SVG = "{http://www.w3.org/2000/svg}"


def fixture(rate=48000, scenario="partial", seed=0):
    frames = rate * 120 // 1000
    metadata = [
        ("hammond_console_trace_schema", "1"), ("evidence_scope", "synthetic_engineering"),
        ("source_model", "ideal-shared-sine-v1"), ("contact_model", "nominal-linear-travel-v1"),
        ("percussion_model", "shared-readiness-v1"), ("scenario", scenario),
        ("scenario_version", "1"), ("profile_id", "nominal-unmeasured-v1"),
        ("authoring_sha256", "0123456789abcdef" * 4),
        ("profile_digest_scope", "declared_authoring_not_compiled_hash"),
        ("sample_rate", str(rate)), ("seed", str(seed)), ("frames", str(frames)),
        ("timing", "after_events_before_render_and_advance"), ("manual", "upper"),
        ("primary_midi", "60"), ("companion_midi", "67"),
        ("primary_tone_id", "49"), ("companion_tone_id", "56"),
        ("primary_frequency_hz", "523.25"), ("companion_frequency_hz", "784"),
        ("primary_source_peak", "1"), ("companion_source_peak", "1"),
        ("profile_output_gain", "1"), ("initial_percussion", "on_second_normal_fast"),
        ("sustained_drawbars", "all_zero"), ("row_count_limit", "11520"),
        ("byte_limit", "8388608"),
    ]
    lines = [f"# {key}={value}" for key, value in metadata] + [HEADER]
    for frame in range(frames):
        fields = [str(frame), format(frame / rate, ".17g"), "0", "0.5"]
        fields += ["0"] * 9 + ["0", "0"] + ["0"] * 9
        fields += ["1", "0", "1", "0", "1.5", "0.70710678118654757",
                   "1", "1", "1", "0.25", "0.5", "0"]
        assert len(fields) == 36
        lines.append(",".join(fields))
    return ("\n".join(lines) + "\n").encode("ascii")


def change_metadata(raw, key, value):
    lines = raw.decode("ascii").splitlines()
    index = next(i for i, line in enumerate(lines[:28]) if line.startswith(f"# {key}="))
    lines[index] = f"# {key}={value}"
    return ("\n".join(lines) + "\n").encode("ascii")


def change_row(raw, frame, changes):
    lines = raw.decode("ascii").splitlines()
    fields = lines[29 + frame].split(",")
    names = HEADER.split(",")
    for name, value in changes.items():
        fields[names.index(name)] = str(value)
    lines[29 + frame] = ",".join(fields)
    return ("\n".join(lines) + "\n").encode("ascii")


class TracePlotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = fixture()
        cls.trace = plot.parse_trace(cls.raw)
        cls.svg = plot.render_svg(cls.trace)
        cls.calls = 0

    @classmethod
    def tearDownClass(cls):
        print(f"console plot: {cls.calls} actual CLI calls; baseline SVG {len(cls.svg)} bytes")

    def test_all_rates_scenarios_and_unsigned_seed_boundary(self):
        for rate, scenario in zip((44100, 48000, 96000), ("partial", "legato", "routing")):
            with self.subTest(rate=rate):
                raw = fixture(rate, scenario, 2**64 - 1)
                trace = plot.parse_trace(raw)
                self.assertEqual(len(trace.rows), rate * 120 // 1000)
                self.assertEqual(trace.metadata["scenario"], scenario)
                self.assertEqual(trace.sha256, hashlib.sha256(raw).hexdigest())
                self.assertEqual(trace.rows[-1][1], (len(trace.rows) - 1) / rate)
        boundary = change_row(self.raw, 0, {"position": 1, "readiness": 0,
                              "percussion_gain": 0, "audio": 3,
                              "primary_phase_turns": repr(math.nextafter(1.0, 0.0))})
        self.assertEqual(plot.parse_trace(boundary).rows[0][35], 3)
        self.assertEqual(plot.parse_trace(change_row(boundary, 0, {"audio": -3})).rows[0][35], -3)

    def test_unsupported_metadata_and_representation_are_rejected(self):
        mutations = {
            "hammond_console_trace_schema": "2", "contact_model": "ideal-contacts-v1",
            "source_model": "measured", "percussion_model": "different",
            "scenario": "unknown", "scenario_version": "2", "manual": "lower",
            "seed": str(2**64), "sample_rate": "88200", "frames": "5761",
            "primary_tone_id": "0", "primary_frequency_hz": "24000",
            "companion_frequency_hz": "1e-99", "primary_source_peak": "1.1",
            "profile_output_gain": "-0.1", "authoring_sha256": "A" * 64,
            "profile_digest_scope": "authenticated", "byte_limit": "99999999",
        }
        for key, value in mutations.items():
            with self.subTest(key=key), self.assertRaises(plot.PlotError):
                plot.parse_trace(change_metadata(self.raw, key, value))
        invalid = [self.raw[:-1], b"\xef\xbb\xbf" + self.raw,
                   self.raw.replace(b"\n", b"\r\n", 1), self.raw + b"\n",
                   self.raw.replace(b"# scenario=partial", b"# scenario=par\x00tial"),
                   self.raw.replace(b"# scenario=partial", b"# scenario=parti\xc3\xa9l"),
                   self.raw.replace(b"frame,time_seconds,", b"frame,time_seconds,extra,", 1),
                   self.raw.replace(b"# evidence_scope=synthetic_engineering\n", b"", 1),
                   self.raw + b"0\n", b"x" * (8 * 1024 * 1024 + 1)]
        for index, raw in enumerate(invalid):
            with self.subTest(representation=index), self.assertRaises(plot.PlotError):
                plot.parse_trace(raw)

    def test_numeric_domains_contiguous_time_and_routing_relations(self):
        cases = [
            {"frame": "01"}, {"time_seconds": "0.000001"}, {"position": "1.00001"},
            {"target": "-0.1"}, {"readiness": "nan"}, {"audio": "inf"},
            {"audio": "1e999"}, {"audio": "1e-999"}, {"audio": "3.00001"},
            {"percussion_gain": "1.5001"}, {"upper_sustain_gain": "-1"},
            {"primary_phase_turns": "1"}, {"companion_phase_turns": "-0.01"},
            {"c0": "1.0"}, {"c1": "2"}, {"c8": "1"},
            {"route_enabled": "0"}, {"routed_detector": "1"},
            {"position": "0" * 4097},
        ]
        for changes in cases:
            with self.subTest(changes=changes), self.assertRaises(plot.PlotError):
                plot.parse_trace(change_row(self.raw, 0, changes))
        # A structurally consistent routing change is admitted without pretending
        # to verify the scenario's event schedule or readiness differential equation.
        valid = change_row(self.raw, 0, {"c8": 1, "physical_detector": 1,
                           "route_enabled": 0, "eligible": 0, "routed_detector": 0})
        self.assertEqual(plot.parse_trace(valid).rows[0][25:28], (1, 0, 0))

    def test_deterministic_accessible_standalone_svg_and_provenance(self):
        self.assertEqual(self.svg, plot.render_svg(self.trace))
        self.assertLessEqual(len(self.svg), 1024 * 1024)
        root = ET.fromstring(self.svg)
        self.assertEqual(root.attrib["viewBox"], "0 0 1200 1150")
        self.assertEqual(root.attrib["role"], "img")
        self.assertIn("Nominal console", root.find(SVG + "title").text)
        self.assertIn("unmeasured", root.find(SVG + "desc").text)
        payload = json.loads(root.find(SVG + "metadata").text)
        self.assertEqual(payload["trace_sha256"], hashlib.sha256(self.raw).hexdigest())
        self.assertEqual(payload["trajectory_reduction"], "first_min_max_last_per_time_bin")
        self.assertEqual(payload["contact_target_reduction"], "none")
        self.assertEqual(payload["verification"], "structure_domains_and_routing_only")
        text = " ".join(element.text or "" for element in root.iter(SVG + "text"))
        for phrase in ("Key travel", "Shared percussion", "Contact closures", "Time (ms)",
                       "min/max", "Trace SHA-256", "No DSP replay"):
            self.assertIn(phrase, text)
        for element in root.iter():
            self.assertNotIn(element.tag, (SVG + "script", SVG + "image", SVG + "foreignObject"))
            self.assertFalse(any(key.startswith("on") or "href" in key for key in element.attrib))

    def test_exact_contact_boundary_and_audio_min_max_above_full_scale(self):
        raw = change_row(self.raw, 0, {"c0": 1, "audio": -2})
        raw = change_row(raw, 1, {"c0": 1, "audio": 2.5})
        root = ET.fromstring(plot.render_svg(plot.parse_trace(raw)))
        contact = root.find(f"{SVG}path[@id='primary-c0']")
        self.assertIsNotNone(contact)
        numbers = [float(number) for number in re.findall(r"-?\d+(?:\.\d+)?", contact.attrib["d"])]
        self.assertEqual(len(numbers), 3)  # one on-interval, exactly frames [0,2)
        self.assertEqual(numbers[0], 130)
        self.assertAlmostEqual(numbers[2] - numbers[0], 1010 * 2 / 5760, delta=0.00051)
        audio = root.find(f"{SVG}path[@id='audio-envelope']")
        self.assertEqual(audio.attrib["data-bins"], "1010")
        first = audio.attrib["d"].split("M")[1]
        values = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", first)]
        # Automatic +/-5 scale, top895, height116; values2.5 and-2 are extrema.
        self.assertAlmostEqual(values[1], 895 + 116 * (5 - 2.5) / 10, delta=0.00051)
        self.assertAlmostEqual(values[2], 895 + 116 * (5 + 2) / 10, delta=0.00051)

    def test_formatter_escapes_dynamic_xml_even_for_programmatic_trace(self):
        metadata = dict(self.trace.metadata)
        metadata["scenario"] = '<script>&"x"'
        unsafe = plot.Trace(metadata, self.trace.rows, '"<&' * 22)
        raw = plot.render_svg(unsafe)
        root = ET.fromstring(raw)
        self.assertIn('<script>&"x"', root.find(SVG + "title").text.lower())
        self.assertEqual(root.findall(".//" + SVG + "script"), [])
        self.assertIn(b"&lt;script&gt;", raw.lower())

    def test_transition_complexity_is_bounded_before_publication(self):
        # Deliberately artificial high-frequency toggles are structurally valid
        # but exceed the exact-transition drawing budget. They must not be silently
        # decimated or published as an apparently complete plot.
        rows = []
        for frame, original in enumerate(self.trace.rows):
            row = list(original)
            bit = frame % 2
            for index in list(range(4, 13)) + list(range(15, 24)):
                row[index] = bit
            row[25] = row[27] = bit
            rows.append(tuple(row))
        dense = plot.Trace(self.trace.metadata, tuple(rows), self.trace.sha256)
        with self.assertRaisesRegex(plot.PlotError, "exceeds 1 MiB"):
            plot.render_svg(dense)

    def test_publish_no_clobber_paths_and_cleanup_on_link_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.csv"
            source.write_bytes(self.raw)
            target = root / "plot.svg"
            plot.write_plot(source, target)
            self.assertEqual(target.read_bytes(), self.svg)
            with self.assertRaises(plot.PlotError):
                plot.write_plot(source, target)
            self.assertEqual(target.read_bytes(), self.svg)
            with self.assertRaises(plot.PlotError):
                plot.write_plot(source, source)
            self.assertEqual(source.read_bytes(), self.raw)
            dangling = root / "dangling.svg"
            dangling.symlink_to(root / "absent.svg")
            with self.assertRaises(plot.PlotError):
                plot.write_plot(source, dangling)
            self.assertTrue(dangling.is_symlink())
            before = {path.name for path in root.iterdir()}
            with mock.patch.object(plot.os, "link", side_effect=OSError("simulated link failure")):
                with self.assertRaisesRegex(OSError, "simulated"):
                    plot.write_plot(source, root / "failed.svg")
            self.assertEqual({path.name for path in root.iterdir()}, before)
            # Simulate a competitor creating the destination after preflight.
            raced = root / "raced.svg"
            def race(_source, destination):
                Path(destination).write_bytes(b"other writer")
                raise FileExistsError("simulated race")
            with mock.patch.object(plot.os, "link", side_effect=race):
                with self.assertRaises(FileExistsError):
                    plot.write_plot(source, raced)
            self.assertEqual(raced.read_bytes(), b"other writer")
            self.assertFalse(any(path.name.startswith(".hammond-plot-") for path in root.iterdir()))

    def test_invalid_input_or_missing_parent_creates_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "bad.csv"
            source.write_bytes(b"malformed\n")
            before = list(root.iterdir())
            with self.assertRaises(plot.PlotError):
                plot.write_plot(source, root / "bad.svg")
            self.assertEqual(list(root.iterdir()), before)
            with self.assertRaises((plot.PlotError, OSError)):
                plot.write_plot(root, root / "directory.svg")
            with self.assertRaises((plot.PlotError, OSError)):
                plot.write_plot(source, root / "missing" / "bad.svg")
            self.assertFalse((root / "missing").exists())

    def test_partial_write_flush_and_close_failures_leave_no_output(self):
        original_open = Path.open
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.csv"
            source.write_bytes(self.raw)
            for stage in ("write", "flush", "close"):
                class FailingStream:
                    def __init__(self, stream):
                        self.stream = stream
                    def __enter__(self):
                        return self
                    def __exit__(self, *_args):
                        self.stream.close()
                        if stage == "close":
                            raise OSError("simulated close failure")
                    def write(self, data):
                        if stage == "write":
                            self.stream.write(data[:20])
                            raise OSError("simulated write failure")
                        return self.stream.write(data)
                    def flush(self):
                        if stage == "flush":
                            raise OSError("simulated flush failure")
                        return self.stream.flush()
                def failing_open(path, *args, **kwargs):
                    stream = original_open(path, *args, **kwargs)
                    return FailingStream(stream) if path.name == "plot.svg" else stream
                with self.subTest(stage=stage), mock.patch.object(Path, "open", failing_open):
                    with self.assertRaisesRegex(OSError, f"simulated {stage}"):
                        plot.write_plot(source, root / f"{stage}.svg")
                self.assertEqual([path.name for path in root.iterdir()], ["input.csv"])

    def test_actual_cli_strict_arguments_and_success(self):
        def run(args):
            type(self).calls += 1
            return subprocess.run([sys.executable, str(TOOL), *args],
                                  capture_output=True, timeout=15, check=False)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, destination = root / "trace.csv", root / "plot.svg"
            source.write_bytes(self.raw)
            help_result = run(["--help"])
            self.assertEqual(help_result.returncode, 0, help_result.stderr)
            self.assertIn(b"--input", help_result.stdout)
            bad = [[], ["--help", "extra"], ["--in", str(source), "--output", str(destination)],
                   ["--input", str(source), "--input", str(source)],
                   ["--input", str(source), "--unknown", str(destination)],
                   ["--input", "", "--output", str(destination)],
                   ["--input", "x" * 4097, "--output", str(destination)]]
            for args in bad:
                with self.subTest(args=args[:1]):
                    result = run(args)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, b"")
                    self.assertIn(b"plot_console_trace", result.stderr)
                    self.assertFalse(destination.exists())
            result = run(["--output", str(destination), "--input", str(source)])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, b"")
            self.assertEqual(result.stderr, b"")
            self.assertEqual(destination.read_bytes(), self.svg)
            repeated = run(["--input", str(source), "--output", str(destination)])
            self.assertNotEqual(repeated.returncode, 0)
            self.assertEqual(destination.read_bytes(), self.svg)


if __name__ == "__main__":
    unittest.main()
