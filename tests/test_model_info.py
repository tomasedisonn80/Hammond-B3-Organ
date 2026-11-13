#!/usr/bin/env python3
"""Inspect actual factory metadata, not a measured organ or render checkpoint."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
import subprocess
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

    def test_bounded_strict_schema_and_separate_generator(self):
        self.assertGreater(len(self.raw), 0)
        self.assertLess(len(self.raw), MAX_BYTES)
        self.assertTrue(self.raw.endswith(b"\n"))
        self.assertNotIn(b"\r", self.raw)
        self.assertEqual(set(self.document), {"schema_version", "evidence_scope", "physical_fidelity",
                                              "source_generator", "console_models"})
        self.assertIs(type(self.document["schema_version"]), int)
        self.assertEqual(self.document["schema_version"], 1)
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

    @unittest.skipUnless(os.name == "posix" and Path("/dev/full").exists(), "requires POSIX /dev/full")
    def test_stdout_failure_has_nonzero_status(self):
        with open("/dev/full", "wb", buffering=0) as failed_output:
            result = subprocess.run([self.executable], stdout=failed_output, stderr=subprocess.PIPE, timeout=15)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"Cannot write metadata to stdout", result.stderr)


if __name__ == "__main__":
    unittest.main()
