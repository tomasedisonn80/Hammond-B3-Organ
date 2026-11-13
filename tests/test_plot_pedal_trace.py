#!/usr/bin/env python3
"""Independent CSV/plot/publication oracles, plus nine actual native scenarios."""

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
TOOL = ROOT / "tools" / "plot_pedal_trace.py"
SPEC = importlib.util.spec_from_file_location("pedal_plot_under_test", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Cannot load pedal plotter")
plot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plot)
SVG = "{http://www.w3.org/2000/svg}"
HEADER = (
    "frame,sample_rate,time_seconds,pedal_position_0,pedal_position_1,brown,red,orange,"
    "yellow,mixture_0,mixture_1,pedal_output,audio,expression,active_pedals,pedal_targets,"
    "contact_bits,upper_down,lower_down,upper_route,lower_route,upper_bank,lower_bank,"
    "upper_drawbar,lower_drawbar,source_phase_before,clock_after"
)


def fixture(rate=48000, scenario="unmute", seed=0):
    # Hand-authored schema fixture, deliberately not an Engine replay. No producer
    # helper or plotter constants provide the contract or expected values.
    metadata = [
        ("hammond_pedal_trace_schema", "1"), ("evidence_scope", "synthetic_engineering"),
        ("source_model", "ideal-shared-sine-v1"), ("manual_contact_model", "ideal-contacts-v1"),
        ("pedal_contact_model", "ideal-eight-contact-pedal-v1"),
        ("pedal_routing_model", "linear-pedal-bus-reference-v1"),
        ("pedal_voice_model", "nominal-static-pedal-mixture-v1"),
        ("pedal_gain_law", "linear-pedal-position-v1"),
        ("pedal_map_id", "atlas-derived-b3-c3-pedal-v1"),
        ("pedal_map_raw_sha256", "58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd"),
        ("pedal_map_canonical_sha256", "7b2631a0c7d55a18f8225d4ee420e472c23b9f2809eec69865474eafce6f5fb2"),
        ("pedal_reference_a_sha256", "b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1"),
        ("pedal_reference_b_sha256", "b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1"),
        ("mixture_matrix", "0.5,0.25,0.125,0.125;0.125,0.5,0.25,0.125"),
        ("pedal_position_gains", "0,0.125,0.25,0.375,0.5,0.625,0.75,0.875,1"),
        ("pedal_weight_policy", "all-200-unit-positive-v1"),
        ("signal_units", "dimensionless_source_normalized"), ("scenario", scenario),
        ("scenario_version", "1"), ("profile_id", "nominal-unmeasured-v1"),
        ("authoring_sha256", "0123456789abcdef" * 4),
        ("profile_digest_scope", "declared_authoring_not_compiled_hash"),
        ("sample_rate", str(rate)), ("seed", str(seed)), ("frames", str(rate * 120 // 1000)),
        ("timing", "events_then_pre_render_state_then_one_render_then_historical_record"),
        ("contact_bits_order", "pedal_1_to_25_each_contact_0_to_7"),
        ("pedal_targets_order", "pedal_1_to_25"), ("manual_midi", "48"),
        ("manual_drawbar_index", "2"), ("tracked_tone_id", "25"),
        ("tracked_frequency_hz", "130.81278265029931"), ("tracked_source_peak", "1"),
        ("profile_output_gain", "0.03"), ("percussion", "off"),
        ("row_count_limit", "11520"), ("byte_limit", "8388608"),
    ]
    lines = [f"# {key}={value}" for key, value in metadata] + [HEADER]
    for frame in range(rate * 120 // 1000):
        fields = [str(frame), str(rate), format(frame / rate, ".17g"), "0", "0"]
        fields += ["0"] * 8  # four buses, two mixtures, P, audio
        fields += ["1", "0", "0" * 25, "0" * 200, "0", "0", "1", "1", "1", "1",
                   "8", "4", "0.25", str(frame + 1)]
        assert len(fields) == 27
        lines.append(",".join(fields))
    return ("\n".join(lines) + "\n").encode("ascii")


def change_metadata(raw, name, value):
    lines = raw.decode("ascii").splitlines()
    index = next(i for i, line in enumerate(lines[:37]) if line.startswith(f"# {name}="))
    lines[index] = f"# {name}={value}"
    return ("\n".join(lines) + "\n").encode("ascii")


def change_row(raw, frame, changes):
    lines = raw.decode("ascii").splitlines()
    fields = lines[38 + frame].split(",")
    names = HEADER.split(",")
    for name, value in changes.items():
        fields[names.index(name)] = str(value)
    lines[38 + frame] = ",".join(fields)
    return ("\n".join(lines) + "\n").encode("ascii")


def path_numbers(path):
    return [float(token) for token in re.findall(r"-?\d+(?:\.\d+)?", path.attrib["d"])]


class PedalPlotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = fixture()
        cls.trace = plot.parse_trace(cls.raw)
        cls.svg = plot.render_svg(cls.trace)
        cls.cli_calls = 0

    @classmethod
    def tearDownClass(cls):
        print(json.dumps({"pedal_plot_cli_calls": cls.cli_calls,
                          "fixture_svg_bytes": len(cls.svg)}, sort_keys=True))

    def cli(self, arguments, cwd):
        type(self).cli_calls += 1
        return subprocess.run([sys.executable, str(TOOL), *map(str, arguments)], cwd=cwd,
                              capture_output=True, text=True, timeout=20, check=False)

    def test_supported_rates_scenarios_seed_and_exact_source_digest(self):
        for rate, scenario in zip((44100, 48000, 96000), ("unmute", "overlap", "routing")):
            with self.subTest(rate=rate, scenario=scenario):
                raw = fixture(rate, scenario, 2**64 - 1)
                trace = plot.parse_trace(raw)
                self.assertEqual(len(trace.rows), rate * 120 // 1000)
                self.assertEqual(trace.rows[-1].frame, len(trace.rows) - 1)
                self.assertEqual(trace.rows[-1].clock_after, len(trace.rows))
                self.assertEqual(trace.rows[-1].time_seconds, (len(trace.rows) - 1) / rate)
                self.assertEqual(trace.sha256, hashlib.sha256(raw).hexdigest())
                self.assertEqual(trace.metadata["scenario"], scenario)
        with self.assertRaises(TypeError):
            self.trace.metadata["scenario"] = "changed"

    def test_unsupported_models_provenance_and_metadata_are_rejected(self):
        changes = {
            "hammond_pedal_trace_schema": "2", "source_model": "measured", "evidence_scope": "physical",
            "manual_contact_model": "nominal-linear-travel-v1", "pedal_contact_model": "bouncing",
            "pedal_routing_model": "reactor", "pedal_voice_model": "calibrated",
            "pedal_gain_law": "logarithmic", "pedal_map_id": "other",
            "pedal_map_raw_sha256": "0" * 64, "pedal_map_canonical_sha256": "0" * 64,
            "pedal_reference_a_sha256": "0" * 64, "pedal_reference_b_sha256": "0" * 64,
            "mixture_matrix": "1,0,0,0;0,1,0,0", "pedal_position_gains": "linear",
            "pedal_weight_policy": "measured", "signal_units": "volts", "scenario": "custom",
            "scenario_version": "2", "profile_id": "measured", "authoring_sha256": "A" * 64,
            "profile_digest_scope": "authenticated", "sample_rate": "88200", "seed": str(2**64),
            "frames": "5761", "timing": "after_render", "contact_bits_order": "contact_first",
            "pedal_targets_order": "reverse", "manual_midi": "49", "manual_drawbar_index": "3",
            "tracked_tone_id": "26", "tracked_frequency_hz": "24000", "tracked_source_peak": "1.01",
            "profile_output_gain": "-0.01", "percussion": "on", "row_count_limit": "20000",
            "byte_limit": "999999999",
        }
        for name, value in changes.items():
            with self.subTest(field=name), self.assertRaises(plot.PlotError):
                plot.parse_trace(change_metadata(self.raw, name, value))
        for frequency in ("0", "1e-99", "1e999", "nan"):
            with self.subTest(frequency=frequency), self.assertRaises(plot.PlotError):
                plot.parse_trace(change_metadata(self.raw, "tracked_frequency_hz", frequency))

    def test_exact_header_metadata_order_rows_and_byte_limits(self):
        lines = self.raw.splitlines(keepends=True)
        reordered = lines[:]
        reordered[0], reordered[1] = reordered[1], reordered[0]
        malformed = [
            b"", self.raw[:-1], self.raw + b"\n", self.raw + lines[-1], b"".join(lines[:-1]),
            self.raw.replace(b"\n", b"\r\n", 1), b"\xef\xbb\xbf" + self.raw,
            self.raw.replace(b"# scenario=unmute", b"# scenario=un\x00mute"),
            self.raw.replace(b"# scenario=unmute", b"# scenario=un\xc3\xa9mute"),
            b"".join(reordered), b"".join(lines[:1] + lines),
            self.raw.replace(b"frame,sample_rate,", b"frame,sample_rate,extra,", 1),
            self.raw.replace(b"frame,sample_rate,", b"sample_rate,frame,", 1),
            self.raw.replace(lines[38], lines[38].rstrip(b"\n") + b",0\n", 1),
            b"x" * (8 * 1024 * 1024 + 1),
            change_row(self.raw, 0, {"audio": "0" * 4097}),
        ]
        for index, raw in enumerate(malformed):
            with self.subTest(case=index), self.assertRaises(plot.PlotError):
                plot.parse_trace(raw)

    def test_finite_numeric_domains_and_monotonic_clock(self):
        changes = [
            {"frame": "01"}, {"frame": "1"}, {"sample_rate": "44100"}, {"clock_after": "2"},
            {"time_seconds": "0.0001"}, {"pedal_position_0": "9"}, {"pedal_position_1": "-1"},
            {"audio": "nan"}, {"audio": "inf"}, {"audio": "1e999"}, {"audio": "1e-999"},
            {"audio": "102.000001"}, {"audio": " 0"}, {"audio": "+0"}, {"audio": "0x0"},
            {"audio": "0" * 65}, {"brown": "50.00001"}, {"pedal_output": "100.00001"},
            {"expression": "1.00001"}, {"expression": "-0.001"},
            {"source_phase_before": "1"}, {"source_phase_before": "-0.01"},
            {"upper_down": "2"}, {"lower_route": "0.0"}, {"upper_bank": "2"},
            {"upper_drawbar": "9"}, {"lower_drawbar": "-1"},
        ]
        for mutation in changes:
            with self.subTest(mutation=mutation), self.assertRaises(plot.PlotError):
                plot.parse_trace(change_row(self.raw, 0, mutation))
        # A subnormal output is representable; decimal conversion underflow is not.
        trace = plot.parse_trace(change_row(self.raw, 0, {"audio": "5e-324",
                                       "source_phase_before": repr(math.nextafter(1.0, 0.0))}))
        self.assertGreater(trace.rows[0].audio, 0)
        ET.fromstring(plot.render_svg(trace))

    def test_all_contact_bits_including_five_null_positions_are_checked(self):
        targets = "00000001" + "0" * 17  # physical pedal 8
        contacts = "0" * 56 + "1" * 8 + "0" * 136
        valid = change_row(self.raw, 0, {"active_pedals": 1, "pedal_targets": targets,
                                       "contact_bits": contacts})
        self.assertEqual(plot.parse_trace(valid).rows[0].contact_bits[57], "1")
        for changes in ({"active_pedals": 0}, {"pedal_targets": targets[:-1]},
                        {"contact_bits": contacts[:57] + "0" + contacts[58:]},
                        {"contact_bits": contacts + "0"}, {"pedal_targets": "2" + "0" * 24}):
            with self.subTest(changes=changes), self.assertRaises(plot.PlotError):
                plot.parse_trace(change_row(valid, 0, changes))
        for pedal in range(8, 13):
            bit = 8 * (pedal - 1) + 1
            mutation = "0" * bit + "1" + "0" * (199 - bit)
            with self.subTest(null_position=bit), self.assertRaises(plot.PlotError):
                plot.parse_trace(change_row(self.raw, 0, {"contact_bits": mutation}))

    def test_independent_mixture_known_answer_and_float_audio_bound(self):
        # Eight/four/two/zero gives 5.25 and 3.5; positions four/two give P=3.5.
        values = {"brown": 8, "red": 4, "orange": 2, "yellow": 0,
                  "mixture_0": 5.25, "mixture_1": 3.5, "pedal_position_0": 4,
                  "pedal_position_1": 2, "pedal_output": 3.5, "audio": -2.5,
                  "active_pedals": 1, "pedal_targets": "1" + "0" * 24,
                  "contact_bits": "1" * 8 + "0" * 192}
        raw = change_row(self.raw, 0, values)
        self.assertEqual(plot.parse_trace(raw).rows[0].pedal_output, 3.5)
        for changes in ({"mixture_0": 5.2501}, {"mixture_1": 3.5001}, {"pedal_output": 3.5001}):
            with self.subTest(changes=changes), self.assertRaises(plot.PlotError):
                plot.parse_trace(change_row(raw, 0, changes))
        extreme = {name: 50 for name in ("brown", "red", "orange", "yellow", "mixture_0", "mixture_1")}
        extreme.update(pedal_position_0=8, pedal_position_1=8, pedal_output=100, audio=102)
        self.assertEqual(plot.parse_trace(change_row(self.raw, 0, extreme)).rows[0].audio, 102)

    def test_standalone_accessible_deterministic_svg_preserves_provenance(self):
        self.assertEqual(self.svg, plot.render_svg(self.trace))
        self.assertLessEqual(len(self.svg), 1024 * 1024)
        root = ET.fromstring(self.svg)
        self.assertEqual(root.attrib["viewBox"], "0 0 1200 1535")
        self.assertEqual(root.attrib["role"], "img")
        self.assertIn("Nominal pedals", root.find(SVG + "title").text)
        self.assertIn("unmeasured", root.find(SVG + "desc").text)
        payload = json.loads(root.find(SVG + "metadata").text)
        self.assertEqual(payload["trace_sha256"], hashlib.sha256(self.raw).hexdigest())
        self.assertEqual(payload["source_metadata"], dict(self.trace.metadata))
        self.assertEqual(payload["signal_reduction"], "min_max_per_time_bin")
        self.assertEqual(payload["state_transition_reduction"], "none")
        self.assertEqual(payload["contact_bits_checked"], 200)
        self.assertEqual(payload["source_phase_plot"], "omitted_original_values_remain_in_csv")
        labels = " ".join(element.text or "" for element in root.iter(SVG + "text"))
        for label in ("Pedal registration", "Four bus excitations", "Mixtures and pedal output",
                      "Targets, contacts", "Final audio", "Trace SHA-256", "physical calibration"):
            self.assertIn(label, labels)
        self.assertEqual(len([node for node in root.iter(SVG + "path")
                              if node.attrib.get("id", "").endswith("-envelope")]), 8)
        for element in root.iter():
            self.assertNotIn(element.tag, (SVG + "script", SVG + "image", SVG + "foreignObject"))
            self.assertFalse(any("href" in key or key.startswith("on") for key in element.attrib))

    def test_xml_dynamic_fields_are_escaped_even_for_programmatic_trace(self):
        metadata = dict(self.trace.metadata)
        metadata["scenario"] = '<script>&"name"'
        unsafe = plot.Trace(metadata, self.trace.rows, '<&"' * 22)
        raw = plot.render_svg(unsafe)
        root = ET.fromstring(raw)
        self.assertIn('<script>&"name"', root.find(SVG + "title").text.lower())
        self.assertEqual(root.findall(".//" + SVG + "script"), [])
        self.assertIn(b"&lt;script&gt;", raw.lower())

    def test_per_bin_extrema_retain_isolated_spikes_and_final_sample(self):
        samples = (0, -2, 3, 0, 0, 0, 7, -8, 0, 11, -12)
        rows = tuple(self.trace.rows[i]._replace(audio=value) for i, value in enumerate(samples))
        with mock.patch.object(plot, "TIME_BINS", 4):
            ranges = plot.envelope_ranges(self.trace._replace(rows=rows), "audio")
        self.assertEqual(ranges, ((0, 2, -2, 0), (2, 5, 0, 3),
                                  (5, 8, -8, 7), (8, 11, -12, 11)))
        raw = change_row(self.raw, 0, {"audio": -2})
        raw = change_row(raw, 1, {"audio": 2.5})
        root = ET.fromstring(plot.render_svg(plot.parse_trace(raw)))
        path = root.find(f"{SVG}path[@id='audio-envelope']")
        self.assertEqual(path.attrib["data-bins"], "1000")
        numbers = path_numbers(path)
        # Observed first-bin -2,2.5 on an independently expected +/-5 axis.
        self.assertAlmostEqual(numbers[1], 1282 + 110 * 2.5 / 10, delta=0.00051)
        self.assertAlmostEqual(numbers[2], 1282 + 110 * 7 / 10, delta=0.00051)
        self.assertEqual(len(numbers), 3000)  # 1000 exact min/max strokes

    def test_exact_state_intervals_one_sample_final_sample_and_drawbar_changes(self):
        self.assertEqual(plot.closed_intervals((1, 1, 0, 1)), ((0, 2), (3, 4)))
        self.assertEqual(plot.closed_intervals((0, 0)), ())
        raw = self.raw
        for frame in (0, 1, 5759):
            raw = change_row(raw, frame, {"pedal_targets": "1" + "0" * 24,
                  "contact_bits": "1" * 8 + "0" * 192, "active_pedals": 1,
                  "lower_down": 1, "pedal_position_0": 8})
        root = ET.fromstring(plot.render_svg(plot.parse_trace(raw)))
        numbers = path_numbers(root.find(f"{SVG}path[@id='pedal-01-contacts']"))
        self.assertEqual(len(numbers), 6)
        for actual, expected in zip(numbers, (140, 772, 140 + 2000 / 5760,
                                               140 + 5759000 / 5760, 772, 1140)):
            self.assertAlmostEqual(actual, expected, delta=0.00051)
        steps = root.find(f"{SVG}path[@id='pedal-position-0']").attrib["d"]
        self.assertEqual(steps, "M140,187H140.347V278H1139.826V187H1140")
        lower = path_numbers(root.find(f"{SVG}path[@id='lower-down']"))
        self.assertEqual((lower[0], lower[2], lower[3], lower[5]),
                         (numbers[0], numbers[2], numbers[3], numbers[5]))

    def test_excessive_exact_transitions_fail_instead_of_being_decimated(self):
        rows = tuple(row._replace(pedal_targets=str(i % 2) * 25,
                                  contact_bits=str(i % 2) * 200, active_pedals=25 * (i % 2))
                     for i, row in enumerate(self.trace.rows))
        with self.assertRaisesRegex(plot.PlotError, "exceeds 1 MiB"):
            plot.render_svg(self.trace._replace(rows=rows))

    def test_no_clobber_failed_publication_cleanup_and_atomic_race(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            source = parent / "input.csv"
            source.write_bytes(self.raw)
            target = parent / "plot.svg"
            plot.write_plot(source, target)
            self.assertEqual(target.read_bytes(), self.svg)
            for destination in (target, source, parent):
                with self.subTest(destination=destination), self.assertRaises(plot.PlotError):
                    plot.write_plot(source, destination)
            self.assertEqual(source.read_bytes(), self.raw)
            before = {path.name for path in parent.iterdir()}
            with mock.patch.object(plot.os, "link", side_effect=OSError("injected link failure")):
                with self.assertRaisesRegex(OSError, "injected"):
                    plot.write_plot(source, parent / "failed.svg")
            self.assertEqual({path.name for path in parent.iterdir()}, before)
            raced = parent / "race.svg"
            def race(_source, destination):
                Path(destination).write_bytes(b"other writer")
                raise FileExistsError("injected race")
            with mock.patch.object(plot.os, "link", side_effect=race):
                with self.assertRaises(FileExistsError):
                    plot.write_plot(source, raced)
            self.assertEqual(raced.read_bytes(), b"other writer")
            self.assertFalse(any(path.name.startswith(".hammond-pedal-plot-") for path in parent.iterdir()))

    def test_invalid_input_and_missing_parent_publish_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            source = parent / "bad.csv"
            source.write_bytes(self.raw[:-1])
            for input_path, destination in ((source, parent / "bad.svg"),
                                            (parent, parent / "directory.svg"),
                                            (source, parent / "missing" / "bad.svg")):
                with self.subTest(destination=destination), self.assertRaises((plot.PlotError, OSError)):
                    plot.write_plot(input_path, destination)
            self.assertEqual([path.name for path in parent.iterdir()], ["bad.csv"])

    def test_cli_contract_unicode_paths_and_actual_concurrent_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            source = parent / "pédal source.csv"
            source.write_bytes(self.raw)
            target = parent / "pédal plot.svg"
            result = self.cli(["--output", target, "--input", source], parent)
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))
            self.assertEqual(target.read_bytes(), self.svg)
            result = self.cli(["--help"], parent)
            self.assertEqual(result.returncode, 0)
            self.assertIn("--input TRACE.csv --output PLOT.svg", result.stdout)
            for arguments in ([], ["--help", "extra"], ["--input", source],
                              ["--in", source, "--output", target],
                              ["--input", source, "--input", source],
                              ["--input", source, "--output", target],
                              ["--input", "", "--output", target],
                              ["--input", "é" * 2049, "--output", target],
                              ["--input", source, "--output", target, "extra"]):
                with self.subTest(arguments=str(arguments)[:100]):
                    result = self.cli(arguments, parent)
                    self.assertEqual(result.returncode, 1)
                    self.assertEqual(result.stdout, "")
                    self.assertIn("plot_pedal_trace:", result.stderr)
            self.assertEqual(target.read_bytes(), self.svg)
            destination = parent / "simultaneous.svg"
            arguments = [sys.executable, str(TOOL), "--input", str(source), "--output", str(destination)]
            processes = [subprocess.Popen(arguments, cwd=parent, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE, text=True) for _ in range(2)]
            type(self).cli_calls += 2
            outputs = [process.communicate(timeout=30) for process in processes]
            self.assertEqual(sorted(process.returncode for process in processes), [0, 1])
            self.assertTrue(all(stdout == "" for stdout, _ in outputs))
            self.assertEqual(destination.read_bytes(), self.svg)
            self.assertFalse(any(path.name.startswith(".hammond-pedal-plot-") for path in parent.iterdir()))

    def test_symlink_destinations_are_preserved_when_platform_permits_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            source = parent / "input.csv"
            source.write_bytes(self.raw)
            dangling = parent / "dangling.svg"
            try:
                dangling.symlink_to(parent / "absent.svg")
            except OSError as error:
                print(json.dumps({"pedal_plot_symlink_cases_executed": 0,
                                  "reason": str(error)}, sort_keys=True))
                return  # Explicitly reported unavailable; no claim of execution.
            real = parent / "real.svg"
            real.symlink_to(source)
            for target in (dangling, real):
                with self.subTest(target=target), self.assertRaises(plot.PlotError):
                    plot.write_plot(source, target)
                self.assertTrue(target.is_symlink())
            self.assertEqual(source.read_bytes(), self.raw)
            print(json.dumps({"pedal_plot_symlink_cases_executed": 2}))


class ActualPedalTracePlotTests(unittest.TestCase):
    def test_nine_actual_scenario_rate_pairs_and_separate_manual_routes(self):
        executable = os.environ.get("HAMMOND_PEDAL_TRACE_EXECUTABLE")
        profile = os.environ.get("HAMMOND_TEST_PROFILE")
        self.assertTrue(executable and profile,
                        "Run through CTest or set HAMMOND_PEDAL_TRACE_EXECUTABLE and HAMMOND_TEST_PROFILE")
        observed = []
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            for scenario in ("unmute", "overlap", "routing"):
                for rate in (44100, 48000, 96000):
                    with self.subTest(scenario=scenario, rate=rate):
                        source = parent / f"{scenario}-{rate}.csv"
                        result = subprocess.run([str(executable), "--profile", str(profile),
                            "--scenario", scenario, "--sample-rate", str(rate), "--seed", "0",
                            "--output", str(source)], cwd=parent, capture_output=True, timeout=30, check=False)
                        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b"", b""))
                        trace = plot.load_trace(source)
                        destination = source.with_suffix(".svg")
                        plot.write_plot(source, destination)
                        root = ET.fromstring(destination.read_bytes())
                        metadata = json.loads(root.find(SVG + "metadata").text)
                        self.assertEqual(metadata["trace_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
                        self.assertEqual(len(trace.rows), rate * 120 // 1000)
                        self.assertEqual(len(source.read_bytes()), source.stat().st_size)
                        self.assertLessEqual(destination.stat().st_size, 1024 * 1024)
                        if scenario == "unmute":
                            self.assertEqual(trace.rows[0].contact_bits[57], "1")
                            self.assertEqual(trace.rows[0].contact_bits[89], "1")
                            self.assertTrue(all(row.pedal_output == 0 for row in trace.rows[:rate * 20 // 1000]))
                            self.assertTrue(any(abs(row.mixture_0) > 0.01 for row in trace.rows[:100]))
                        elif scenario == "routing":
                            self.assertEqual(trace.rows[0].contact_bits, "1" * 200)
                            cancel = trace.rows[rate * 20 // 1000]
                            self.assertEqual((cancel.lower_down, cancel.lower_route, cancel.active_pedals), (1, 0, 25))
                            pedal_panic = trace.rows[rate * 80 // 1000]
                            self.assertEqual((pedal_panic.upper_down, pedal_panic.active_pedals), (1, 0))
                            self.assertTrue(all(row.audio == 0 for row in trace.rows[rate * 100 // 1000:]))
                        else:
                            self.assertEqual(trace.rows[rate * 48 // 1000].active_pedals, 2)
                            self.assertEqual(trace.rows[rate * 48 // 1000].upper_down, 1)
                            self.assertEqual(trace.rows[rate * 48 // 1000].lower_down, 1)
                        observed.append({"scenario": scenario, "rate": rate, "rows": len(trace.rows),
                                         "svg_bytes": destination.stat().st_size,
                                         "csv_sha256": metadata["trace_sha256"]})
        self.assertEqual(len(observed), 9)
        print(json.dumps({"actual_pedal_trace_calls": 9, "actual_plots": observed}, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
