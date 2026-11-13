#!/usr/bin/env python3
"""Inspect actual factory metadata, not a measured organ or render checkpoint."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


MAX_BYTES = 128 * 1024


def unique_object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"duplicate JSON member: {name}")
        result[name] = value
    return result


def reject_constant(value):
    raise ValueError(f"nonfinite JSON constant: {value}")


class ModelInfoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        executable = os.environ.get("HAMMOND_MODEL_INFO_EXECUTABLE")
        if not executable or not Path(executable).is_file():
            raise RuntimeError("Build hammond_model_info and set HAMMOND_MODEL_INFO_EXECUTABLE; metadata tests were not run.")
        cls.executable = str(Path(executable).resolve())
        result = subprocess.run([cls.executable], capture_output=True, timeout=15, check=False)
        if result.returncode != 0 or result.stderr:
            raise RuntimeError(f"metadata exporter failed: {result.returncode}, {result.stderr!r}")
        cls.raw = result.stdout
        cls.document = json.loads(cls.raw.decode("utf-8"), object_pairs_hook=unique_object,
                                  parse_constant=reject_constant)
        cls.models = {model["choice"]: model for model in cls.document["console_models"]}
        cls.root = Path(os.environ.get("HAMMOND_SOURCE_DIR", Path(__file__).resolve().parents[1]))

    def test_bounded_strict_schema_and_separate_generator(self):
        self.assertGreater(len(self.raw), 0)
        self.assertLess(len(self.raw), MAX_BYTES)
        self.assertTrue(self.raw.endswith(b"\n"))
        self.assertNotIn(b"\r", self.raw)
        self.assertEqual(set(self.document), {"schema_version", "evidence_scope", "physical_fidelity",
                                              "source_generator", "console_models", "pedal_model"})
        self.assertIs(type(self.document["schema_version"]), int)
        self.assertEqual(self.document["schema_version"], 2)
        self.assertEqual(self.document["evidence_scope"], "synthetic_engineering")
        self.assertEqual(self.document["physical_fidelity"], "unestablished")
        generator = self.document["source_generator"]
        self.assertIs(generator["included"], False)
        self.assertEqual(generator["profile_type"], "RuntimeProfile")
        self.assertEqual(generator["source_count"], 91)
        self.assertTrue(generator["reason"])
        self.assertEqual(len(self.document["console_models"]), 2)
        self.assertEqual(set(self.models), {"legacy", "nominal"})

    def test_all_manual_key_contact_records_and_units(self):
        for choice, model in self.models.items():
            with self.subTest(choice=choice):
                self.assertEqual(set(model), {"choice", "factory", "contacts", "percussion"})
                self.assertEqual(model["factory"], f"make_{choice}_console_model")
                contacts = model["contacts"]
                self.assertEqual(contacts["units"], {
                    "on_thresholds": "normalized_key_travel", "off_thresholds": "normalized_key_travel",
                    "press_seconds": "s", "release_seconds": "s"})
                self.assertEqual(contacts["evidence_class"], "proposed")
                self.assertIsNone(contacts["uncertainty"])
                self.assertTrue(contacts["missing_evidence"])
                self.assertIn(39, contacts["atlas_pages"])
                self.assertEqual([manual["manual"] for manual in contacts["manuals"]], ["upper", "lower"])
                contact_count = 0
                for manual in contacts["manuals"]:
                    self.assertEqual(len(manual["keys"]), 61)
                    self.assertEqual([key["midi_note"] for key in manual["keys"]], list(range(36, 97)))
                    for key in manual["keys"]:
                        self.assertEqual(set(key), {"midi_note", "press_seconds", "release_seconds",
                                                   "on_thresholds", "off_thresholds"})
                        self.assertEqual(len(key["on_thresholds"]), 9)
                        self.assertEqual(len(key["off_thresholds"]), 9)
                        self.assertEqual(key["press_seconds"], 8 / 1000)
                        self.assertEqual(key["release_seconds"], 12 / 1000)
                        for index, (on, off) in enumerate(zip(key["on_thresholds"], key["off_thresholds"])):
                            # Independent decimal specification, not a copied C++ initializer.
                            self.assertEqual(on, (12 + 10 * index) / 100)
                            self.assertEqual(off, (4 + 10 * index) / 100)
                            self.assertTrue(0 <= off < on <= 1)
                            contact_count += 1
                self.assertEqual(contact_count, 1098)

    def test_algorithm_ids_and_mode_choice_are_distinct(self):
        legacy, nominal = self.models["legacy"], self.models["nominal"]
        self.assertEqual(legacy["contacts"]["algorithm_id"], "ideal-contacts-v1")
        self.assertEqual(legacy["contacts"]["mode"], "ideal")
        self.assertEqual(nominal["contacts"]["algorithm_id"], "nominal-linear-travel-v1")
        self.assertEqual(nominal["contacts"]["mode"], "linear_travel")
        # Both factories currently retain equal, independently represented key data.
        self.assertEqual(legacy["contacts"]["manuals"], nominal["contacts"]["manuals"])
        self.assertEqual(legacy["percussion"], nominal["percussion"])

    def test_rc_hypotheses_gain_units_and_default_controls(self):
        # Derive RC products from the atlas's nominal components in SI units.
        capacitance = 33 / 100_000_000
        r57, r58 = 1_500_000, 4_700_000
        expected = {
            "slow_decay_seconds": (r58 * capacitance, "s", "derived"),
            "fast_decay_seconds": (capacitance / (1 / r57 + 1 / r58), "s", "derived"),
            "recovery_seconds": ((82_000 + 22_000) * capacitance, "s", "derived"),
            "normal_gain": (1.0, "normalized_amplitude", "proposed"),
            "soft_gain": (0.5, "normalized_amplitude", "proposed"),
            "fast_gain_multiplier": (1.5, "dimensionless", "proposed"),
            "normal_sustain_gain": (math.sqrt(0.5), "dimensionless", "proposed"),
        }
        for model in self.models.values():
            percussion = model["percussion"]
            self.assertEqual(percussion["algorithm_id"], "shared-readiness-v1")
            self.assertEqual(percussion["readiness_unit"], "dimensionless")
            self.assertEqual(percussion["gain_map"], "F(q)=q")
            self.assertIsNone(percussion["uncertainty"])
            self.assertTrue(percussion["missing_evidence"])
            self.assertEqual(set(percussion["parameters"]), set(expected))
            for name, (value, unit, evidence) in expected.items():
                parameter = percussion["parameters"][name]
                self.assertEqual(set(parameter), {"value", "unit", "evidence_class", "atlas_pages"})
                self.assertTrue(math.isfinite(parameter["value"]))
                self.assertTrue(math.isclose(parameter["value"], value, rel_tol=0, abs_tol=2e-15))
                self.assertEqual(parameter["unit"], unit)
                self.assertEqual(parameter["evidence_class"], evidence)
                self.assertIn(135 if evidence == "derived" else 134, parameter["atlas_pages"])
            self.assertEqual(percussion["default_settings"], {
                "enabled": False, "harmonic": "second", "volume": "normal", "decay": "slow"})
            self.assertIs(type(percussion["default_settings"]["enabled"]), bool)

    def test_pedal_map_identities_counts_and_all_disconnections(self):
        routing = self.document["pedal_model"]["routing"]
        self.assertEqual(set(routing), {
            "model_id", "map_id", "map_raw_sha256", "map_canonical_sha256",
            "factory_comparison_id", "factory_comparison_raw_sha256", "review_a_sha256",
            "review_b_sha256", "evidence_class", "pedal_count", "contacts_per_pedal",
            "position_count", "bus_count", "connected_count", "disconnected_count",
            "repeated_source_pairs", "bus_order", "connected_per_bus", "disconnections"})
        self.assertEqual(routing["model_id"], "linear-pedal-bus-reference-v1")
        self.assertEqual(routing["evidence_class"], "documented")
        raw_map = (self.root / "data/pedal-map.json").read_bytes()
        self.assertLess(len(raw_map), 256 * 1024)
        pedal_map = json.loads(raw_map)
        self.assertEqual(routing["map_id"], pedal_map["map_id"])
        self.assertEqual(routing["map_raw_sha256"], hashlib.sha256(raw_map).hexdigest())
        canonical_map = json.dumps(pedal_map, sort_keys=True, separators=(",", ":"),
                                   ensure_ascii=False, allow_nan=False).encode("utf-8")
        self.assertEqual(routing["map_canonical_sha256"], hashlib.sha256(canonical_map).hexdigest())
        raw_comparison = (self.root / "data/references/factory-table-iii.json").read_bytes()
        self.assertLess(len(raw_comparison), 256 * 1024)
        comparison = json.loads(raw_comparison)
        self.assertEqual(routing["factory_comparison_id"], comparison["reference_id"])
        self.assertEqual(routing["factory_comparison_raw_sha256"],
                         hashlib.sha256(raw_comparison).hexdigest())

        bus_names = ["Brown", "Red", "Orange", "Yellow"]
        reference_rows = []
        for review in ("a", "b"):
            raw = (self.root / f"data/references/review-{review}-pedal.csv").read_bytes()
            self.assertLess(len(raw), 8192)
            self.assertEqual(routing[f"review_{review}_sha256"], hashlib.sha256(raw).hexdigest())
            rows = list(csv.reader(io.StringIO(raw.decode("ascii"), newline="")))
            self.assertEqual(rows[0], ["pedal", *[f"c{i}" for i in range(1, 9)]])
            self.assertEqual(len(rows), 26)
            parsed = []
            for pedal, row in enumerate(rows[1:], 1):
                self.assertEqual(len(row), 9)
                self.assertEqual(int(row[0]), pedal)
                tones = [int(cell) if cell else None for cell in row[1:]]
                self.assertTrue(all(tone is None or 1 <= tone <= 91 for tone in tones))
                parsed.append(tones)
            reference_rows.append(parsed)
        self.assertEqual(*reference_rows)
        rows = reference_rows[0]
        connected = [0] * 4
        nulls = []
        repeated = 0
        for pedal, tones in enumerate(rows, 1):
            for contact, tone in enumerate(tones):
                if tone is None:
                    nulls.append({"pedal_id": pedal, "contact_index": contact,
                                  "bus": bus_names[contact // 2], "source_tone_id": None})
                else:
                    connected[contact // 2] += 1
                    repeated += sum(other == tone for other in tones[contact + 1:])
        expected_counts = {"pedal_count": len(rows), "contacts_per_pedal": len(rows[0]),
                           "position_count": sum(map(len, rows)), "bus_count": len(bus_names),
                           "connected_count": sum(connected), "disconnected_count": len(nulls),
                           "repeated_source_pairs": repeated}
        for key, value in expected_counts.items():
            self.assertIs(type(routing[key]), int)
            self.assertEqual(routing[key], value)
        self.assertEqual((sum(connected), len(nulls), repeated), (195, 5, 7))
        self.assertEqual(routing["bus_order"], bus_names)
        self.assertEqual(routing["connected_per_bus"], connected)
        self.assertTrue(all(type(value) is int for value in routing["connected_per_bus"]))
        self.assertEqual(routing["disconnections"], nulls)
        for null in routing["disconnections"]:
            self.assertIs(type(null["pedal_id"]), int)
            self.assertIs(type(null["contact_index"]), int)
            self.assertIsNone(null["source_tone_id"])

    def test_pedal_nominal_voice_weights_units_and_limits(self):
        pedal = self.document["pedal_model"]
        self.assertEqual(set(pedal), {"runtime_state_included", "evidence_class", "atlas_pages",
                                     "uncertainty", "missing_evidence", "routing", "contacts",
                                     "weights", "voice"})
        self.assertIs(pedal["runtime_state_included"], False)
        self.assertEqual(pedal["evidence_class"], "proposed")
        self.assertEqual(pedal["atlas_pages"], [139, 140, 142, 144, 447])
        self.assertIsNone(pedal["uncertainty"])
        self.assertIn("reactor/loading", pedal["missing_evidence"])
        self.assertIn("original engineering fixture", pedal["missing_evidence"])
        self.assertEqual(pedal["contacts"], {
            "policy": "ideal_simultaneous", "canonical_event_manual": "lower",
            "null_contact_state_retained": True, "velocity_scales_output": False,
            "source_clock_owned": False, "prepared_closed_contact_count": 0})
        for key in ("null_contact_state_retained", "velocity_scales_output", "source_clock_owned"):
            self.assertIs(type(pedal["contacts"][key]), bool)
        self.assertIs(type(pedal["contacts"]["prepared_closed_contact_count"]), int)
        weights = pedal["weights"]
        self.assertEqual(set(weights), {"factory", "unit", "position_order", "values"})
        self.assertEqual(weights["factory"], "nominal_pedal_reference_weights")
        self.assertEqual(weights["unit"], "dimensionless")
        self.assertEqual(weights["position_order"], "pedal_id_then_contact_index")
        self.assertEqual(weights["values"], [1] * (25 * 8))
        self.assertTrue(all(type(value) in (int, float) for value in weights["values"]))

        voice = pedal["voice"]
        self.assertEqual(set(voice), {"model_id", "gain_law_id", "mixture_labels", "matrix",
                                     "position_gains", "default_positions", "units", "absolute_limits"})
        self.assertEqual(voice["model_id"], "nominal-static-pedal-mixture-v1")
        self.assertEqual(voice["gain_law_id"], "linear-pedal-position-v1")
        self.assertEqual(voice["mixture_labels"], ["Pedal Mixture 1", "Pedal Mixture 2"])
        # Independently adopted rational contract, not values parsed from C++.
        expected_matrix = [[numerator / 8 for numerator in row]
                           for row in ((4, 2, 1, 1), (1, 4, 2, 1))]
        self.assertEqual(voice["matrix"], expected_matrix)
        self.assertEqual(voice["position_gains"], [position / 8 for position in range(9)])
        self.assertEqual(voice["default_positions"], [0, 0])
        self.assertTrue(all(type(position) is int for position in voice["default_positions"]))
        self.assertTrue(all(type(value) in (int, float) and math.isfinite(value)
                            for row in voice["matrix"] for value in row))
        self.assertTrue(all(type(value) in (int, float) and math.isfinite(value)
                            for value in voice["position_gains"]))
        self.assertEqual(voice["units"], {
            "matrix": "dimensionless", "position_gains": "dimensionless",
            "default_positions": "drawbar_position", "bus_input": "source_normalized_dimensionless",
            "mixture_output": "source_normalized_dimensionless",
            "combined_output": "source_normalized_dimensionless"})
        bus_bound = 25 * 2  # At most two independent positions per pedal/bus.
        mixture_bound = max(sum(row) * bus_bound for row in expected_matrix)
        self.assertEqual(voice["absolute_limits"], {
            "bus_input": bus_bound, "mixture_output": mixture_bound,
            "combined_output": 2 * mixture_bound})
        self.assertTrue(all(type(value) in (int, float) and math.isfinite(value)
                            for value in voice["absolute_limits"].values()))

    def test_pedal_identity_agrees_with_actual_render_summary(self):
        renderer = os.environ.get("HAMMOND_RENDER_EXECUTABLE")
        profile = os.environ.get("HAMMOND_TEST_PROFILE")
        if not renderer or not Path(renderer).is_file() or not profile or not Path(profile).is_file():
            raise RuntimeError("Build hammond_render/profile and set their test environment; coupling was not run.")
        with tempfile.TemporaryDirectory(prefix="hammond-pedal-metadata-") as directory:
            score = Path(directory) / "pedal.events"
            score.write_bytes(b"0 pedal_on lower 8 100\n63 pedal_all_notes_off lower 0 0\n")
            result = subprocess.run([
                renderer, "--profile", profile, "--output", str(Path(directory) / "pedal.wav"),
                "--frames", "64", "--sample-rate", "48000", "--block-size", "32", "--seed", "0",
                "--drawbars", "000000000", "--pedal-drawbars", "80", "--events", str(score),
                "--fail-on-clip"], capture_output=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, b"")
            self.assertLess(len(result.stdout), 16 * 1024)
            metrics = json.loads(result.stdout, object_pairs_hook=unique_object, parse_constant=reject_constant)
            self.assertEqual(metrics["render_schema_version"], 3)
            self.assertGreater(metrics["peak"], 0)
            self.assertEqual(metrics["clipped_frames"], 0)
        pedal = self.document["pedal_model"]
        routing, voice = pedal["routing"], pedal["voice"]
        for renderer_key, model_key in (
                ("pedal_routing_model", "model_id"), ("pedal_map_id", "map_id"),
                ("pedal_map_raw_sha256", "map_raw_sha256"),
                ("pedal_map_canonical_sha256", "map_canonical_sha256"),
                ("pedal_reference_a_sha256", "review_a_sha256"),
                ("pedal_reference_b_sha256", "review_b_sha256")):
            self.assertEqual(metrics[renderer_key], routing[model_key])
        self.assertEqual(metrics["pedal_voice_model"], voice["model_id"])
        self.assertEqual(metrics["pedal_gain_law"], voice["gain_law_id"])
        self.assertEqual(metrics["pedal_contact_model"], "ideal-eight-contact-pedal-v1")
        self.assertEqual(metrics["pedal_weight_policy"], "all-200-unit-positive-v1")
        self.assertEqual(metrics["pedal_mixture_denominator"], 8)
        self.assertEqual(metrics["pedal_gain_denominator"], 8)
        matrix = [[int(value) / metrics["pedal_mixture_denominator"] for value in row.split(",")]
                  for row in metrics["pedal_mixture_matrix"].split(";")]
        self.assertEqual(matrix, voice["matrix"])

    def test_repeated_exports_and_locale_environment_are_byte_identical(self):
        for locale in ("C", "de_DE.UTF-8", "fr_FR.UTF-8"):
            with self.subTest(locale=locale):
                environment = dict(os.environ, LC_ALL=locale, LANG=locale)
                result = subprocess.run([self.executable], capture_output=True, timeout=15, env=environment)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, b"")
                self.assertEqual(result.stdout, self.raw)

    def test_help_and_unknown_arguments(self):
        result = subprocess.run([self.executable, "--help"], capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, b"")
        self.assertIn(b"Usage: hammond_model_info", result.stdout)
        self.assertIn(b"synthetic", result.stdout)
        for arguments in (["--json"], ["-h"], ["value"], [""], ["--help", "extra"], ["--help", "--help"]):
            with self.subTest(arguments=arguments):
                result = subprocess.run([self.executable, *arguments], capture_output=True, timeout=15)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, b"")
                self.assertIn(b"Expected no arguments or --help", result.stderr)

    def test_stdout_failure_has_nonzero_status(self):
        with tempfile.TemporaryDirectory(prefix="hammond-model-output-") as directory:
            path = Path(directory) / "read-only-stdout.bin"
            original = b"retained destination bytes\n"
            path.write_bytes(original)
            # A read-only handle rejects writes independently of filesystem
            # permission bypasses, and does not need a platform-specific device.
            with path.open("rb", buffering=0) as failed_output:
                result = subprocess.run([self.executable], stdout=failed_output,
                                        stderr=subprocess.PIPE, timeout=15)
            self.assertEqual(path.read_bytes(), original)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"Cannot write metadata to stdout", result.stderr)


if __name__ == "__main__":
    unittest.main()
