#!/usr/bin/env python3
"""Independent graph, authoring-admission and atomic compiler regressions.

The literal tables below were transcribed from atlas pp. 157-158. They do not
call the compiler's expected_components/expected_outputs helpers. This suite
requires only the Python standard library; circuit/runtime fidelity is separate.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
import compile_scanner_line as compiler


PROFILE = ROOT / "data/scanner/atlas-late-b3-nominal-v1.json"
SCHEMA = ROOT / "data/scanner-line.schema.json"
RAW = PROFILE.read_bytes()
AUTHORING = json.loads(RAW)
MODEL = "atlas-late-b3-nominal-line-v1"
ATLAS_SHA = "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769"
NODES = "g p0 p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15 p16 p17 p18 r d1 d2 d3 d4 d5 d6".split()

# id, kind, positive, negative, SI value, SI unit, printed magnitude, printed unit.
# Keep all edges literal: a loop using the producer's formula would reproduce
# its possible off-by-one error instead of independently detecting it.
ELEMENT_ROWS = """
L1 L p0 p1 0.5 H 500 mH
L2 L p1 p2 0.5 H 500 mH
L3 L p2 p3 0.5 H 500 mH
L4 L p3 p4 0.5 H 500 mH
L5 L p4 p5 0.5 H 500 mH
L6 L p5 p6 0.5 H 500 mH
L7 L p6 p7 0.5 H 500 mH
L8 L p7 p8 0.5 H 500 mH
L9 L p8 p9 0.5 H 500 mH
L10 L p9 p10 0.5 H 500 mH
L11 L p10 p11 0.5 H 500 mH
L12 L p11 p12 0.5 H 500 mH
L13 L p12 p13 0.5 H 500 mH
L14 L p13 p14 0.5 H 500 mH
L15 L p14 p15 0.5 H 500 mH
L16 L p15 p16 0.5 H 500 mH
L17 L p16 p17 0.5 H 500 mH
L18 L p17 p18 0.5 H 500 mH
C1 C p1 r 4e-9 F 0.004 uF
C2 C p2 r 4e-9 F 0.004 uF
C3 C p3 r 4e-9 F 0.004 uF
C4 C p4 r 4e-9 F 0.004 uF
C5 C p5 r 4e-9 F 0.004 uF
C6 C p6 r 4e-9 F 0.004 uF
C7 C p7 r 4e-9 F 0.004 uF
C8 C p8 r 4e-9 F 0.004 uF
C9 C p9 r 4e-9 F 0.004 uF
C10 C p10 r 4e-9 F 0.004 uF
C11 C p11 r 4e-9 F 0.004 uF
C12 C p12 r 4e-9 F 0.004 uF
C13 C p13 r 4e-9 F 0.004 uF
C14 C p14 r 4e-9 F 0.004 uF
C15 C p15 r 4e-9 F 0.004 uF
C16 C p16 r 4e-9 F 0.004 uF
C17 C p17 r 4e-9 F 0.004 uF
C18 C p18 r 1e-9 F 0.001 uF
R1+ R p0 d1 27000 ohm 27 kOhm
R1- R d1 r 68000 ohm 68 kOhm
R2+ R p1 d2 56000 ohm 56 kOhm
R2- R d2 r 150000 ohm 0.15 MOhm
R3+ R p2 d3 39000 ohm 39 kOhm
R3- R d3 r 150000 ohm 0.15 MOhm
R4+ R p3 d4 33000 ohm 33 kOhm
R4- R d4 r 180000 ohm 0.18 MOhm
R5+ R p4 d5 18000 ohm 18 kOhm
R5- R d5 r 180000 ohm 0.18 MOhm
R6+ R p5 d6 12000 ohm 12 kOhm
R6- R d6 r 180000 ohm 0.18 MOhm
Rc R r g 22000 ohm 22 kOhm
Rt R p18 r 15000 ohm 15 kOhm
"""
ELEMENTS = [tuple(line.split()) for line in ELEMENT_ROWS.strip().splitlines()]
OUTPUTS = [tuple(line.split()) for line in """
v1 d1 g
v2 d2 g
v3 d3 g
v4 d4 g
v5 d5 g
v6 d6 g
v7 p6 g
v8 p7 g
v9 p8 g
v10 p9 g
v11 p10 g
v12 p11 g
v13 p12 g
v14 p13 g
v15 p14 g
v16 p15 g
v17 p16 g
v18 p17 g
v19 p18 g
""".strip().splitlines()]
UNKNOWN_UNITS = {
    "winding-resistance": "ohm", "mutual-inductance": "H", "stray-capacitance": "F",
    "drive-impedance": "ohm", "receiver-loading": "ohm",
    "scanner-coupling-capacitance": "F", "normalized-signal-scale": "V",
    "specimen-revision": "identifier",
}


def literal_authoring_elements():
    return [{"id": name, "kind": kind, "positive": positive, "negative": negative,
             "value": {"magnitude": magnitude, "unit": unit,
                       "printed": f"{magnitude} {unit}"},
             "source": {"pages": [157, 158], "evidence_class": "documentary-nominal",
                        "uncertainty": "not-supplied"}}
            for name, kind, positive, negative, _, _, magnitude, unit in ELEMENTS]


def record(profile, section, name):
    return next(item for item in profile[section] if item["id"] == name)


class ScannerProfileTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="scanner-profile-")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.input = self.directory / "source.json"
        self.input.write_bytes(RAW)
        self.output = self.directory / "result.json"

    def cli(self, output=None, output_format="json", input_path=None):
        return subprocess.run(
            [sys.executable, "-B", str(TOOLS / "compile_scanner_line.py"),
             "--input", str(self.input if input_path is None else input_path),
             "--output", str(self.output if output is None else output),
             "--format", output_format], capture_output=True, text=True,
            timeout=10, check=False)

    def assert_cli_rejects(self, payload):
        self.input.write_bytes(payload)
        sentinel = b"previous accepted output\n"
        self.output.write_bytes(sentinel)
        result = self.cli()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("scanner profile rejected:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(self.output.read_bytes(), sentinel)
        self.assertEqual(self.input.read_bytes(), payload)
        self.assertEqual(set(self.directory.iterdir()), {self.input, self.output})

    def assert_rejects(self, value, *, cli=False):
        with self.assertRaises(compiler.ScannerProfileError):
            compiler.validate_profile(value)
        if cli:
            self.assert_cli_rejects(json.dumps(value).encode())

    def test_literal_all_edges_and_ground_outputs(self):
        admitted = compiler.load_profile(self.input)
        self.assertEqual(len(ELEMENTS), 50)
        self.assertEqual(len(OUTPUTS), 19)
        self.assertEqual(set(admitted["nodes"]), set(NODES))
        self.assertEqual(len(admitted["nodes"]), 27)
        self.assertEqual(admitted["ground"], "g")
        self.assertEqual({item["id"]: item for item in admitted["components"]},
                         {item["id"]: item for item in literal_authoring_elements()})
        self.assertEqual({item["id"]: item for item in admitted["outputs"]}, {
            name: {"id": name, "positive": positive, "negative": negative, "source_pages": [158]}
            for name, positive, negative in OUTPUTS})
        normalized = compiler.normalized_profile(admitted)
        for item, expected in zip(normalized["components"], ELEMENTS):
            name, kind, positive, negative, si, si_unit, magnitude, unit = expected
            with self.subTest(component=name):
                self.assertEqual((item["id"], item["kind"], item["positive"], item["negative"]),
                                 (name, kind, positive, negative))
                self.assertEqual(item["value"], {
                    "si_value": float(si), "si_unit": si_unit,
                    "printed": f"{magnitude} {unit}", "printed_unit": unit,
                    "printed_magnitude": magnitude})

    def test_boundaries_evidence_and_unknowns_are_explicit(self):
        profile = compiler.load_profile(self.input)
        self.assertEqual(profile["model_id"], MODEL)
        self.assertEqual(profile["evidence_class"], "documentary-reconstruction")
        self.assertEqual(profile["source"], {
            "document": "Hammond_B3_Leslie_Research_Atlas_500pp.pdf", "sha256": ATLAS_SHA,
            "values_pages": [157], "topology_pages": [158, 175, 182]})
        self.assertEqual(profile["drive"], {"id": "Vin", "kind": "ideal-voltage-source",
            "positive": "p0", "negative": "g", "quantity": "volts"})
        self.assertEqual(profile["return_switch"], {"id": "Sreturn", "positive": "r",
            "negative": "g", "states": {"vibrato": "closed", "chorus": "open"},
            "closed_model": "node-contraction"})
        self.assertEqual({item["id"]: item["unit"] for item in profile["unknowns"]}, UNKNOWN_UNITS)
        for unknown in profile["unknowns"]:
            self.assertIsNone(unknown["value"])
            self.assertEqual(unknown["status"], "unknown")
            self.assertTrue(unknown["reason"].strip() and unknown["acquisition"].strip())

    def test_schema_graph_enumerations_match_independent_literals(self):
        schema = json.loads(SCHEMA.read_text())
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIs(schema["additionalProperties"], False)
        properties = schema["properties"]
        self.assertEqual(set(schema["required"]), set(AUTHORING))
        self.assertEqual(set(properties["nodes"]["items"]["enum"]), set(NODES))
        self.assertEqual({item["id"]: item for item in properties["components"]["items"]["enum"]},
                         {item["id"]: item for item in literal_authoring_elements()})
        self.assertEqual({item["id"]: item for item in properties["outputs"]["items"]["enum"]}, {
            name: {"id": name, "positive": positive, "negative": negative, "source_pages": [158]}
            for name, positive, negative in OUTPUTS})
        for section, count in (("nodes", 27), ("components", 50), ("outputs", 19)):
            self.assertEqual(properties[section]["minItems"], count)
            self.assertEqual(properties[section]["maxItems"], count)
            self.assertIs(properties[section]["uniqueItems"], True)

    def test_schema_requires_each_editable_prose_identity_exactly_once(self):
        # Whole-object uniqueItems is insufficient when description/reason can
        # differ. These required-ID cardinalities prevent the discovered schema
        # admission hole without introducing a JSON Schema runtime dependency.
        properties = json.loads(SCHEMA.read_text())["properties"]
        for section, expected_ids in (
                ("assumptions", {"ideal-coils", "ideal-drive", "unloaded-tap-observation"}),
                ("unknowns", set(UNKNOWN_UNITS))):
            with self.subTest(section=section):
                clauses = properties[section]["allOf"]
                self.assertEqual(len(clauses), len(expected_ids))
                found_ids = set()
                for clause in clauses:
                    self.assertEqual(clause["minContains"], 1)
                    self.assertEqual(clause["maxContains"], 1)
                    self.assertEqual(clause["contains"]["type"], "object")
                    self.assertIn("id", clause["contains"]["required"])
                    found_ids.add(clause["contains"]["properties"]["id"]["const"])
                self.assertEqual(found_ids, expected_ids)

    def test_normalization_is_independent_canonical_and_nonmutating(self):
        profile = copy.deepcopy(AUTHORING)
        original = copy.deepcopy(profile)
        self.assertIs(compiler.validate_profile(profile), profile)
        result = compiler.normalized_profile(profile)
        self.assertEqual(profile, original)
        for key in ("nodes", "components", "outputs", "assumptions", "unknowns"):
            profile[key].reverse()
        reordered = copy.deepcopy(profile)
        self.assertEqual(compiler.normalized_profile(profile), result)
        self.assertEqual(profile, reordered)
        result["components"][0]["source"]["pages"].append(999)
        self.assertEqual(profile, reordered)

    def test_header_values_and_raw_digest_are_reproducible(self):
        text = compiler.compile_profile(self.input, "header")
        self.assertEqual(text, compiler.compile_profile(self.input, "header"))
        self.assertIn(f'kModelId = "{MODEL}";', text)
        self.assertIn(f'kAuthoringSha256 = "{hashlib.sha256(RAW).hexdigest()}";', text)
        groups = {
            "kInductancesH": [float(row[4]) for row in ELEMENTS if row[1] == "L"],
            "kCapacitancesF": [float(row[4]) for row in ELEMENTS if row[1] == "C"],
            "kDividerUpperOhms": [float(row[4]) for row in ELEMENTS if row[0].endswith("+")],
            "kDividerLowerOhms": [float(row[4]) for row in ELEMENTS if row[0].endswith("-")],
        }
        for name, values in groups.items():
            match = re.search(rf"std::array<double, {len(values)}> {name}\{{([^}}]+)\}};", text)
            self.assertIsNotNone(match, name)
            self.assertEqual([float(v) for v in match[1].split(",")], values)
        self.assertIn("kReturnOhms = 22000.0;", text)
        self.assertIn("kTerminationOhms = 15000.0;", text)
        self.assertNotIn("\r", text)
        self.assertNotIn(str(self.directory), text)
        self.assertTrue(text.endswith("\n"))
        loaded, digest = compiler.load_profile_with_digest(self.input)
        self.assertEqual(loaded, AUTHORING)
        self.assertEqual(digest, hashlib.sha256(RAW).hexdigest())
        compiled = json.loads(compiler.compile_profile(self.input))
        self.assertEqual(compiled.pop("authoring_sha256"), digest)
        self.assertEqual(compiled, compiler.normalized_profile(AUTHORING))

    def test_cli_publishes_both_formats_and_replaces_existing_output(self):
        for output_format in ("json", "header"):
            with self.subTest(format=output_format):
                self.output.write_text("obsolete output")
                result = self.cli(output_format=output_format)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout + result.stderr, "")
                self.assertEqual(self.output.read_text(), compiler.compile_profile(self.input, output_format))
                self.assertEqual(self.input.read_bytes(), RAW)
                self.assertEqual(set(self.directory.iterdir()), {self.input, self.output})

    def test_every_divider_after_inductor_and_every_wrong_tap_reference_rejected(self):
        for name, node in (("R1+", "p1"), ("R2+", "p2"), ("R3+", "p3"),
                           ("R4+", "p4"), ("R5+", "p5"), ("R6+", "p6")):
            with self.subTest(divider=name):
                value = copy.deepcopy(AUTHORING)
                record(value, "components", name)["positive"] = node
                self.assert_rejects(value, cli=True)
        for name, _, _ in OUTPUTS:
            with self.subTest(output=name):
                value = copy.deepcopy(AUTHORING)
                record(value, "outputs", name)["negative"] = "r"
                self.assert_rejects(value)
        value = copy.deepcopy(AUTHORING)
        tap = record(value, "outputs", "v7")
        tap["positive"], tap["negative"] = tap["negative"], tap["positive"]
        self.assert_rejects(value, cli=True)

    def test_dangling_edges_wrong_counts_and_duplicate_identities(self):
        for section in ("nodes", "components", "outputs", "assumptions", "unknowns"):
            for mutation in ("remove", "duplicate", "extra"):
                with self.subTest(section=section, mutation=mutation):
                    value = copy.deepcopy(AUTHORING)
                    if mutation == "remove":
                        value[section].pop()
                    elif mutation == "duplicate":
                        value[section][1] = copy.deepcopy(value[section][0])
                    else:
                        value[section].append(copy.deepcopy(value[section][0]))
                    self.assert_rejects(value, cli=mutation == "duplicate")
        for section, name in (("components", "L18"), ("components", "R3-"), ("outputs", "v19")):
            value = copy.deepcopy(AUTHORING)
            record(value, section, name)["positive"] = "not-a-node"
            self.assert_rejects(value)

    def test_duplicate_prose_records_still_require_distinct_ids(self):
        for section, prose in (("assumptions", "description"), ("unknowns", "reason")):
            value = copy.deepcopy(AUTHORING)
            value[section][1] = copy.deepcopy(value[section][0])
            value[section][1][prose] = "Different nonempty text cannot make a repeated identity unique."
            self.assertNotEqual(value[section][0], value[section][1])
            self.assert_rejects(value, cli=True)

    def test_unknown_fields_at_all_structural_boundaries(self):
        paths = [(), ("source",), ("drive",), ("return_switch",), ("return_switch", "states"),
                 ("components", 0), ("components", 0, "value"), ("components", 0, "source"),
                 ("outputs", 0), ("assumptions", 0), ("unknowns", 0)]
        for path in paths:
            with self.subTest(path=path):
                value = copy.deepcopy(AUTHORING)
                destination = value
                for key in path:
                    destination = destination[key]
                destination["undeclared"] = 1
                self.assert_rejects(value, cli=True)

    def test_numeric_lexical_forms_prefixes_and_printed_values(self):
        for magnitude in ("0", "-1", "NaN", "Infinity", "1e999", "0.5", 500, 500.0, True, None):
            value = copy.deepcopy(AUTHORING)
            value["components"][0]["value"]["magnitude"] = magnitude
            self.assert_rejects(value)
        for unit in ("H", "uH", "F", "mF", "nF", "ohm", "kohm", "MOhm"):
            value = copy.deepcopy(AUTHORING)
            record(value, "components", "C1")["value"]["unit"] = unit
            self.assert_rejects(value)
        for name, field, replacement in (("C18", "magnitude", "0.004"),
                                          ("R2-", "unit", "kOhm"),
                                          ("L1", "printed", "500 H")):
            value = copy.deepcopy(AUTHORING)
            record(value, "components", name)["value"][field] = replacement
            self.assert_rejects(value, cli=True)
        for metadata in (True, 1.0, "1", None, 2):
            value = copy.deepcopy(AUTHORING)
            value["schema_version"] = metadata
            self.assert_rejects(value, cli=True)
        value = copy.deepcopy(AUTHORING)
        value["components"][0]["source"]["pages"][0] = 157.0
        self.assert_rejects(value, cli=True)

    def test_model_provenance_switch_and_unknown_claim_mutations(self):
        mutations = [
            (("model_id",), "other-model"), (("evidence_class",), "measured"),
            (("source", "sha256"), "0" * 64), (("source", "values_pages"), [158]),
            (("components", 0, "source", "uncertainty"), "measured-exact"),
            (("drive", "negative"), "r"), (("return_switch", "positive"), "p0"),
            (("return_switch", "states", "vibrato"), "open"),
            (("return_switch", "states", "chorus"), "closed"),
            (("return_switch", "closed_model"), "infinite-conductance"),
            (("unknowns", 0, "value"), 0), (("unknowns", 0, "status"), "measured"),
            (("unknowns", 0, "unit"), "H"), (("unknowns", 0, "reason"), "   "),
            (("assumptions", 0, "replacement"), ""),
        ]
        for path, replacement in mutations:
            with self.subTest(path=path):
                value = copy.deepcopy(AUTHORING)
                destination = value
                for key in path[:-1]:
                    destination = destination[key]
                destination[path[-1]] = replacement
                self.assert_rejects(value, cli=True)
        value = copy.deepcopy(AUTHORING)
        del value["return_switch"]
        self.assert_rejects(value, cli=True)

    def test_duplicate_json_keys_invalid_encoding_and_nonfinite_tokens(self):
        for payload in (
                RAW.replace(b'"schema_version": 1', b'"schema_version": 1, "schema_version": 1', 1),
                RAW.replace(b'"positive": "p0"', b'"positive": "p0", "positive": "p1"', 1),
                RAW.replace(b'"schema_version": 1', b'"schema_version": NaN', 1),
                RAW.replace(b'"schema_version": 1', b'"schema_version": Infinity', 1),
                RAW.replace(b'"schema_version": 1', b'"schema_version": -Infinity', 1),
                RAW.replace(b'"schema_version": 1', b'"schema_version": 1e999', 1),
                b"\xff" + RAW, RAW[:-7], b"[]"):
            self.assert_cli_rejects(payload)

    def test_bounded_bytes_strings_depth_values_and_cycles(self):
        self.assert_cli_rejects(RAW + b" " * (256 * 1024 + 1 - len(RAW)))
        value = copy.deepcopy(AUTHORING)
        value["assumptions"][0]["description"] = "x" * 512
        compiler.validate_profile(value)
        value["assumptions"][0]["description"] += "x"
        self.assert_rejects(value, cli=True)
        value["assumptions"][0]["description"] = "control\x00character"
        self.assert_rejects(value, cli=True)
        deep = 0
        for _ in range(16):
            deep = [deep]
        value = copy.deepcopy(AUTHORING)
        value["extra"] = deep
        self.assert_rejects(value, cli=True)
        value["extra"] = [list(range(100)) for _ in range(100)]
        with self.assertRaisesRegex(compiler.ScannerProfileError, "value-count"):
            compiler.validate_profile(value)
        value["extra"] = value
        with self.assertRaisesRegex(compiler.ScannerProfileError, "cycle"):
            compiler.validate_profile(value)
        # A parser-recursion failure also must become a clean rejected CLI input.
        self.assert_cli_rejects(b"[" * 1500 + b"0" + b"]" * 1500)

    def test_input_aliases_and_nonregular_destinations_preserve_sources(self):
        same = self.cli(output=self.input)
        self.assertEqual(same.returncode, 2, same.stderr)
        self.assertEqual(self.input.read_bytes(), RAW)
        alias = self.directory / "hard-link.json"
        os.link(self.input, alias)
        linked = self.cli(output=alias)
        self.assertEqual(linked.returncode, 2, linked.stderr)
        self.assertEqual(alias.read_bytes(), RAW)
        directory = self.directory / "directory"
        directory.mkdir()
        self.assertEqual(self.cli(output=directory).returncode, 2)
        self.assertEqual(list(directory.iterdir()), [])
        # Windows symlink creation may require privileges; core alias/directory
        # cases above always execute. This actual symlink case is POSIX-scoped.
        if os.name != "nt":
            external = self.directory / "external.json"
            external.write_bytes(b"external sentinel")
            symlink = self.directory / "output-link.json"
            symlink.symlink_to(external)
            self.assertEqual(self.cli(output=symlink).returncode, 2)
            self.assertTrue(symlink.is_symlink())
            self.assertEqual(external.read_bytes(), b"external sentinel")

    def test_publication_failures_preserve_previous_output_and_clean_temporaries(self):
        sentinel = b"previous good output"
        self.output.write_bytes(sentinel)
        text = compiler.compile_profile(self.input)
        for operation in ("replace", "fsync"):
            with self.subTest(operation=operation), mock.patch.object(
                    compiler.os, operation, side_effect=OSError("injected publication failure")):
                with self.assertRaises(compiler.ScannerProfileError):
                    compiler.write_output(self.output, text, self.input)
            self.assertEqual(self.output.read_bytes(), sentinel)
            self.assertEqual(set(self.directory.iterdir()), {self.input, self.output})
        for invalid_text in ("x" * (256 * 1024 + 1), "invalid surrogate \ud800"):
            with self.assertRaises(compiler.ScannerProfileError):
                compiler.write_output(self.output, invalid_text, self.input)
            self.assertEqual(self.output.read_bytes(), sentinel)
        self.assertEqual(self.input.read_bytes(), RAW)

    def test_input_change_during_read_is_rejected(self):
        before = self.input.stat()
        after = SimpleNamespace(**{name: getattr(before, name) for name in
            ("st_mode", "st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns")})
        after.st_mtime_ns += 1
        with mock.patch.object(compiler.os, "fstat", side_effect=[before, after]):
            with self.assertRaisesRegex(compiler.ScannerProfileError, "changed during"):
                compiler.load_profile_with_digest(self.input)
        self.assertEqual(self.input.read_bytes(), RAW)

    def test_nonregular_input_is_rejected_without_reading(self):
        with self.assertRaises(compiler.ScannerProfileError):
            compiler.load_profile(self.directory)
        if hasattr(os, "mkfifo") and hasattr(os, "O_NONBLOCK"):
            fifo = self.directory / "input-fifo"
            os.mkfifo(fifo)
            result = self.cli(input_path=fifo)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
