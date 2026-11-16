#!/usr/bin/env python3
"""Independent admission of the proposed starter recipes through native tools.

The literal JSON was authored before the separate native generator. This suite
does not import or read that generator's recipe implementation. Its small table
is independently transcribed from the frozen product contract, including every
default and override. Musical comparisons consume the real native inspector's
canonical output, never a Python substitute for ControlSnapshot or its parser.

Required: HAMMOND_REGISTRATION_EXECUTABLE and
HAMMOND_STARTER_GENERATOR_EXECUTABLE from one coherent native build.
HAMMOND_SOURCE_DIR optionally selects the checkout containing the authored pack.
"""

from collections import namedtuple
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


ROOT = Path(os.environ.get("HAMMOND_SOURCE_DIR", Path(__file__).resolve().parents[1])).resolve()
PACK = ROOT / "data/registrations/starter-v1"
ENTRIES = PACK / "entries"
CATALOG_ID = "atlas-chapel-nominal-v1"
CATALOG_SHA256 = "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf"
RECIPE_FIELDS = {"name", "purpose", "registration_file", "performance_file",
                 "drawbars", "selected_banks", "route_enabled", "fixed_registrations",
                 "pedal_drawbars", "expression", "percussion"}
PERCUSSION_FIELDS = {"enabled", "harmonic", "volume", "decay"}
FIXED_NAMES = {"none", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A"}

ContractRow = namedtuple("ContractRow", "name purpose drawbars pedals expression "
                        "banks routes fixed percussion overrides")
# Every row is complete: no inherited/default musical values are applied here.
CONTRACT = tuple(ContractRow(*row) for row in (
    ("01 Quiet Foundation", "sparse chords",
     ("008000000", "008400000", "008000000", "004000000"), (2, 0), 0.5,
     ("B", "B"), (True, True), ("none", "none"),
     (False, "second", "normal", "slow"), "none"),
    ("02 Warm Comp", "chord support",
     ("808000000", "808400000", "008400000", "008300000"), (3, 0), 0.625,
     ("B", "B"), (True, True), ("none", "none"),
     (False, "second", "normal", "slow"), "none"),
    ("03 Clear Lead", "melody over soft chords",
     ("008400000", "808600000", "006000000", "006400000"), (2, 0), 0.625,
     ("B", "B"), (True, True), ("none", "none"),
     (False, "second", "normal", "slow"), "none"),
    ("04 Reed Edge", "focused upper melody",
     ("008620400", "008640400", "008200000", "008300000"), (2, 0), 0.5,
     ("B", "B"), (True, True), ("none", "none"),
     (False, "second", "normal", "slow"), "none"),
    ("05 Bright Ensemble", "full chord accents",
     ("808600004", "808600008", "008400000", "008440000"), (4, 0), 0.5,
     ("B", "B"), (True, True), ("none", "none"),
     (False, "second", "normal", "slow"), "none"),
    ("06 High Shimmer", "upper partial color",
     ("008000248", "008000468", "008000000", "008200000"), (1, 0), 0.5,
     ("B", "B"), (True, True), ("none", "none"),
     (False, "second", "normal", "slow"), "none"),
    ("07 Percussive Pair", "short upper accents",
     ("888000000", "888000000", "008400000", "008400000"), (4, 0), 0.5,
     ("B", "B"), (True, True), ("none", "none"),
     (True, "third", "normal", "fast"), "percussion On/Third/Normal/Fast"),
    ("08 Slow Accent", "sustained upper attacks",
     ("808000000", "808000000", "008000000", "008200000"), (3, 0), 0.625,
     ("B", "B"), (True, True), ("none", "none"),
     (True, "second", "soft", "slow"), "percussion On/Second/Soft/Slow"),
    ("09 Split Dialogue", "contrasting manuals",
     ("008400000", "008600004", "808000000", "808400000"), (4, 0), 0.5,
     ("A", "B"), (True, True), ("none", "none"),
     (False, "second", "normal", "slow"), "selected A/B"),
    ("10 Pedal Study", "pedals with muted manuals",
     ("008000000", "008400000", "008000000", "008200000"), (6, 2), 0.5,
     ("A", "B"), (False, False), ("none", "none"),
     (False, "second", "normal", "slow"), "selected A/B; routes Off/Off"),
    ("11 Fixed Contrast", "compare existing fixed modes",
     ("008000000", "808400000", "008400000", "008440000"), (3, 0), 0.5,
     ("B", "A"), (True, True), ("D#", "F"),
     (False, "second", "normal", "slow"), "selected B/A; fixed D#/F"),
    ("12 Manual Return", "lower support before upper return",
     ("808000000", "808600000", "008400000", "008440000"), (4, 0), 0.5,
     ("A", "B"), (False, True), ("G#", "none"),
     (True, "third", "soft", "fast"),
     "selected A/B; routes Off/On; fixed G#/none; percussion On/Third/Soft/Fast"),
))

CURRENT_TEMPLATE = """B3CONTROLS4
registration_catalog atlas-chapel-nominal-v1 sha256 c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf
expression {expression}
percussion enabled 1 harmonic second volume soft decay fast
pedal drawbars 8 7
manual upper selected A fixed_registration C# route_enabled 0
bank A 0 1 2 3 4 5 6 7 8
bank B 8 7 6 5 4 3 2 1 0
manual lower selected A fixed_registration A route_enabled 0
bank A 1 3 5 7 0 2 4 6 8
bank B 8 6 4 2 0 7 5 3 1
end
"""


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Nonfinite JSON constant: {value}")


def decode_json(raw):
    return json.loads(raw.decode("utf-8"), object_pairs_hook=strict_object,
                      parse_constant=reject_constant)


def required_executable(variable):
    value = os.environ.get(variable)
    if not value or not Path(value).is_file():
        raise RuntimeError(f"Set {variable} to a coherently built native executable")
    return Path(value).resolve()


def flat_bytes(directory):
    result = {}
    for path in sorted(directory.iterdir()):
        if path.is_symlink() or not path.is_file():
            raise AssertionError(f"Unexpected nonregular entry: {path}")
        result[path.name] = path.read_bytes()
    return result


class StarterRegistrationOracleTests(unittest.TestCase):
    calls = 0

    @classmethod
    def setUpClass(cls):
        cls.registration = required_executable("HAMMOND_REGISTRATION_EXECUTABLE")
        cls.generator = required_executable("HAMMOND_STARTER_GENERATOR_EXECUTABLE")
        cls.manifest_bytes = (PACK / "recipes.json").read_bytes()
        cls.manifest = decode_json(cls.manifest_bytes)
        cls.recipes = cls.manifest["recipes"]
        cls.original_entries = flat_bytes(ENTRIES)
        cls.ordered_keys = [row.name + suffix for row in CONTRACT
                            for suffix in (".b3registration", ".b3performance")]

    @classmethod
    def tearDownClass(cls):
        if flat_bytes(ENTRIES) != cls.original_entries:
            raise AssertionError("Admission changed the source payloads")
        if (PACK / "recipes.json").read_bytes() != cls.manifest_bytes:
            raise AssertionError("Admission changed the independent manifest")
        print(f"starter recipe oracle: {cls.calls} actual native subprocess invocations")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-starter-oracle-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name).resolve()

    def run_native(self, executable, *arguments):
        type(self).calls += 1
        result = subprocess.run([str(executable), *map(str, arguments)], cwd=self.work,
                                capture_output=True, timeout=20, check=False)
        self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))
        self.assertEqual(result.stderr, b"")
        self.assertTrue(result.stdout.endswith(b"\n"))
        self.assertLessEqual(len(result.stdout), 1024 * 1024)
        return result.stdout

    def invoke(self, *arguments):
        raw = self.run_native(self.registration, *arguments)
        self.assertEqual(raw.count(b"\n"), 1)
        report = decode_json(raw)
        self.assertEqual(report["schema"], "hammond-registration-cli-v1")
        self.assertEqual(report["outcome"], "ok")
        return report

    def assert_catalog(self, catalog, expected_count=24):
        self.assertEqual(catalog["status"], "Ready")
        self.assertIs(catalog["complete"], True)
        self.assertEqual(catalog["candidate_count"], expected_count)
        self.assertEqual(catalog["directory_items"], expected_count)
        for field in ("invalid_name_count", "invalid_entry_count",
                      "ambiguous_entry_count", "warning_count"):
            self.assertEqual(catalog[field], 0, field)

    def assert_musical_fields(self, canonical, recipe, expression=None):
        """Compare every field in the native serialization with literal JSON."""
        self.assertIsInstance(canonical, str)
        canonical.encode("ascii")
        lines = canonical.splitlines()
        self.assertEqual(len(lines), 12)
        self.assertEqual(canonical, "\n".join(lines) + "\n")
        self.assertEqual(lines, [" ".join(line.split()) for line in lines])
        self.assertEqual(len(canonical.split()), 81)
        self.assertEqual(lines[0], "B3CONTROLS4")
        self.assertEqual(lines[1], f"registration_catalog {CATALOG_ID} sha256 {CATALOG_SHA256}")
        self.assertEqual(lines[2].split(), ["expression", str(
            recipe["expression"] if expression is None else expression)])
        percussion = recipe["percussion"]
        self.assertEqual(lines[3].split(), [
            "percussion", "enabled", str(int(percussion["enabled"])),
            "harmonic", percussion["harmonic"], "volume", percussion["volume"],
            "decay", percussion["decay"]])
        self.assertEqual(lines[4].split(), ["pedal", "drawbars",
                                          *map(str, recipe["pedal_drawbars"])])
        for index, manual in enumerate(("upper", "lower")):
            line = 5 + 3 * index
            self.assertEqual(lines[line].split(), [
                "manual", manual, "selected", recipe["selected_banks"][index],
                "fixed_registration", recipe["fixed_registrations"][index],
                "route_enabled", str(int(recipe["route_enabled"][index]))])
            for bank, letter in enumerate(("A", "B")):
                self.assertEqual(lines[line + 1 + bank].split(),
                                 ["bank", letter, *recipe["drawbars"][index][bank]])
        self.assertEqual(lines[11], "end")

    def inspect(self, directory, key, recipe, scope, expression=None, name=None):
        report = self.invoke("inspect", "--library", directory, "--key", key)
        self.assertEqual(report["command"], "inspect")
        self.assertEqual(report["code"], "Valid")
        self.assertIs(report["committed"], False)
        self.assertIsNone(report["input"])
        self.assertIsNone(report["save"])
        entry = report["entry"]
        self.assertEqual(entry["key"], key)
        self.assertEqual(entry["name"], recipe["name"] if name is None else name)
        self.assertEqual(entry["scope"], scope)
        self.assertEqual(entry["status"], "Valid")
        self.assertEqual(entry["reason"], "")
        canonical = entry["canonical_controls"]
        self.assert_musical_fields(canonical, recipe, expression)
        self.assertEqual(canonical.encode("ascii"), (directory / key).read_bytes())
        return report

    def test_manifest_is_fully_literal_and_matches_frozen_contract(self):
        self.assertEqual(set(self.manifest), {"schema_version", "pack_id", "evidence_status",
                                             "authorship", "provenance", "recipes"})
        self.assertIs(type(self.manifest["schema_version"]), int)
        self.assertEqual(self.manifest["schema_version"], 1)
        self.assertEqual(self.manifest["pack_id"], "starter-registration-pack-v1")
        self.assertEqual(self.manifest["evidence_status"], "proposed-unmeasured")
        for field in ("authorship", "provenance"):
            self.assertIsInstance(self.manifest[field], str)
            self.assertTrue(self.manifest[field].strip())
        self.assertIsInstance(self.recipes, list)
        self.assertEqual(len(self.recipes), 12)
        for recipe, row in zip(self.recipes, CONTRACT):
            with self.subTest(recipe=row.name):
                self.assertIsInstance(recipe, dict)
                self.assertEqual(set(recipe), RECIPE_FIELDS)
                self.assertEqual(recipe["name"], row.name)
                self.assertEqual(recipe["purpose"].casefold(), row.purpose)
                self.assertEqual(recipe["registration_file"], row.name + ".b3registration")
                self.assertEqual(recipe["performance_file"], row.name + ".b3performance")
                for field in ("drawbars", "selected_banks", "route_enabled",
                              "fixed_registrations", "pedal_drawbars"):
                    self.assertIsInstance(recipe[field], list)
                    self.assertEqual(len(recipe[field]), 2)
                self.assertEqual(len(recipe["drawbars"]), 2)
                for manual in recipe["drawbars"]:
                    self.assertIsInstance(manual, list)
                    self.assertEqual(len(manual), 2)
                    for bank in manual:
                        self.assertIsInstance(bank, str)
                        self.assertRegex(bank, r"^[0-8]{9}$")
                self.assertEqual(tuple(bank for manual in recipe["drawbars"] for bank in manual),
                                 row.drawbars)
                self.assertEqual(tuple(recipe["selected_banks"]), row.banks)
                self.assertEqual(tuple(recipe["fixed_registrations"]), row.fixed)
                for fixed in recipe["fixed_registrations"]:
                    self.assertIn(fixed, FIXED_NAMES)
                for route in recipe["route_enabled"]:
                    self.assertIs(type(route), bool)
                self.assertEqual(tuple(recipe["route_enabled"]), row.routes)
                for pedal in recipe["pedal_drawbars"]:
                    self.assertIs(type(pedal), int)
                    self.assertIn(pedal, range(9))
                self.assertEqual(tuple(recipe["pedal_drawbars"]), row.pedals)
                self.assertIn(type(recipe["expression"]), (int, float))
                self.assertTrue(math.isfinite(recipe["expression"]))
                self.assertEqual(recipe["expression"], row.expression)
                percussion = recipe["percussion"]
                self.assertIsInstance(percussion, dict)
                self.assertEqual(set(percussion), PERCUSSION_FIELDS)
                self.assertIs(type(percussion["enabled"]), bool)
                self.assertEqual(tuple(percussion[key] for key in
                                       ("enabled", "harmonic", "volume", "decay")), row.percussion)
        contract = (ROOT / "docs/STARTER_REGISTRATION_PACK_CONTRACT.md").read_text(encoding="utf-8")
        table = [tuple(cell.strip() for cell in line.split("|")[1:-1])
                 for line in contract.splitlines() if re.match(r"^\| \d{2} ", line)]
        self.assertEqual(table, [
            (row.name + " / " + row.purpose, *row.drawbars,
             "".join(map(str, row.pedals)), str(row.expression), row.overrides)
            for row in CONTRACT])

    def test_flat_store_has_only_exact_paired_payloads(self):
        self.assertEqual(sorted(self.original_entries), sorted(self.ordered_keys))
        self.assertEqual(len(self.original_entries), 24)
        for recipe in self.recipes:
            with self.subTest(recipe=recipe["name"]):
                registration = self.original_entries[recipe["registration_file"]]
                performance = self.original_entries[recipe["performance_file"]]
                self.assertEqual(registration, performance)
                self.assertTrue(registration.startswith(b"B3CONTROLS4\n"))
                self.assertTrue(registration.endswith(b"\nend\n"))
                self.assertNotIn(b"\r", registration)
                self.assertLessEqual(len(registration), 16384)
                registration.decode("ascii")

    def test_native_catalog_has_exact_names_scopes_and_contract_order(self):
        report = self.invoke("list", "--library", ENTRIES)
        self.assertIs(report["committed"], False)
        self.assert_catalog(report["catalog"])
        self.assertEqual(report["catalog"]["entries"], [
            {"key": row.name + ".b3" + scope, "name": row.name,
             "scope": scope, "status": "Valid", "reason": ""}
            for row in CONTRACT for scope in ("registration", "performance")])

    def test_every_native_inspection_matches_literal_fields_and_canonical_bytes(self):
        for recipe in self.recipes:
            for scope in ("registration", "performance"):
                key = recipe[scope + "_file"]
                with self.subTest(file=key):
                    report = self.inspect(ENTRIES, key, recipe, scope)
                    self.assert_catalog(report["catalog"])

    def test_registration_materialization_preserves_each_supplied_expression(self):
        for expression in (0.125, 0.875):
            current_bytes = CURRENT_TEMPLATE.format(expression=expression).encode("ascii")
            current = self.work / (str(expression) + ".controls")
            current.write_bytes(current_bytes)
            destination = self.work / ("registration recall " + str(expression))
            for index, recipe in enumerate(self.recipes, 1):
                with self.subTest(recipe=recipe["name"], expression=expression):
                    self.assertNotEqual(recipe["expression"], expression)
                    report = self.invoke("materialize", "--library", ENTRIES, "--key",
                                         recipe["registration_file"], "--current", current,
                                         "--destination", destination, "--name", recipe["name"])
                    self.assertIs(report["committed"], True)
                    self.assertEqual(report["save"]["status"], "Saved")
                    self.assertEqual(report["save"]["scope"], "performance")
                    self.assertEqual(report["save"]["key"], recipe["performance_file"])
                    self.assert_catalog(report["save"]["refreshed_catalog"], index)
                    self.assertEqual(report["input"]["source_version"], 4)
                    self.assertEqual(report["input"]["source_bytes"], len(current_bytes))
                    self.assertEqual(report["input"]["canonical_controls"].encode("ascii"), current_bytes)
                    self.assert_musical_fields(report["entry"]["canonical_controls"], recipe)
                    self.inspect(destination, recipe["performance_file"], recipe,
                                 "performance", expression)
            self.assertEqual(current.read_bytes(), current_bytes)

    def test_performance_materialization_restores_each_saved_expression(self):
        destination = self.work / "performance recall"
        for index, recipe in enumerate(self.recipes, 1):
            with self.subTest(recipe=recipe["name"]):
                report = self.invoke("materialize", "--library", ENTRIES, "--key",
                                     recipe["performance_file"], "--destination", destination,
                                     "--name", recipe["name"])
                self.assertIs(report["committed"], True)
                self.assertIsNone(report["input"])
                self.assertEqual(report["save"]["status"], "Saved")
                self.assertEqual(report["save"]["scope"], "performance")
                self.assertEqual(report["save"]["key"], recipe["performance_file"])
                self.assert_catalog(report["save"]["refreshed_catalog"], index)
                self.assert_musical_fields(report["entry"]["canonical_controls"], recipe)
                self.inspect(destination, recipe["performance_file"], recipe, "performance")
                self.assertEqual((destination / recipe["performance_file"]).read_bytes(),
                                 self.original_entries[recipe["performance_file"]])

    def test_regeneration_matches_checked_in_bytes_and_independent_native_oracle(self):
        destination = self.work / "regenerated entries"
        raw = self.run_native(self.generator, "--output", destination)
        records = [decode_json(line) for line in raw.splitlines()]
        self.assertEqual(len(records), 25)
        self.assertEqual([record["file"] for record in records[:-1]], self.ordered_keys)
        self.assertEqual(records[-1]["status"], "Complete")
        self.assertEqual(records[-1]["committed_count"], 24)
        self.assertEqual(flat_bytes(destination), self.original_entries)
        for recipe in self.recipes:
            for scope in ("registration", "performance"):
                with self.subTest(file=recipe[scope + "_file"]):
                    self.inspect(destination, recipe[scope + "_file"], recipe, scope)

    def test_frozen_catalog_authoring_identity_is_unchanged(self):
        catalog = (ROOT / "data/registrations/atlas-chapel-nominal-v1.json").read_bytes()
        self.assertEqual(hashlib.sha256(catalog).hexdigest(), CATALOG_SHA256)


if __name__ == "__main__":
    unittest.main()
