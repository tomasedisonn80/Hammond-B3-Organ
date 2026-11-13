#!/usr/bin/env python3
"""Documentary pedal-map checks; no audio or factory/specimen verification claim.

The five printed rows are copied from atlas PDF p.140, independently of the
validator's formula. Remaining exhaustive checks establish rule consistency.
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools" / "validate_pedal_map.py"
DATA_PATH = ROOT / "data" / "pedal-map.json"
SPEC = importlib.util.spec_from_file_location("pedal_map_validator", VALIDATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {VALIDATOR_PATH}")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)
RAW_DATA = DATA_PATH.read_bytes()
DATA = json.loads(RAW_DATA)
PRINTED_ROWS = {
    1: [1, 13, 13, 25, 32, 37, 41, 44],
    7: [7, 19, 19, 31, 38, 43, 47, 50],
    8: [8, None, 20, 32, 39, 44, 48, 51],
    13: [13, 32, 25, 37, 44, 49, 53, 56],
    25: [25, 44, 37, 49, 56, 61, 65, 68],
}


def at_path(value, path):
    for key in path:
        value = value[key]
    return value


def object_paths(value, path=()):
    if type(value) is dict:
        yield path
        for key, child in value.items():
            yield from object_paths(child, path + (key,))
    elif type(value) is list:
        for index, child in enumerate(value):
            yield from object_paths(child, path + (index,))


def leaf_paths(value, path=()):
    if type(value) is dict:
        for key, child in value.items():
            yield from leaf_paths(child, path + (key,))
    elif type(value) is list:
        for index, child in enumerate(value):
            yield from leaf_paths(child, path + (index,))
    else:
        yield path, value


class PedalMapTests(unittest.TestCase):
    def setUp(self):
        self.data = copy.deepcopy(DATA)
        directory = tempfile.TemporaryDirectory(prefix="pedal-map-tests-")
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "map.json"

    def rejected(self, data):
        before = copy.deepcopy(data)
        with self.assertRaises(validator.PedalMapError):
            validator.validate_pedal_map(data)
        self.assertEqual(data, before)

    def load_bytes(self, payload):
        self.path.write_bytes(payload)
        return validator.load_pedal_map(self.path)

    def test_valid_map_and_validation_do_not_mutate(self):
        before = copy.deepcopy(self.data)
        self.assertIsNone(validator.validate_pedal_map(self.data))
        self.assertEqual(self.data, before)
        self.assertEqual(validator.load_pedal_map(DATA_PATH), DATA)
        self.assertEqual(DATA_PATH.read_bytes(), RAW_DATA)
        # Object order has no meaning; the row and column array order does.
        validator.validate_pedal_map(dict(reversed(list(self.data.items()))))

    def test_five_printed_page_140_rows(self):
        for pedal, expected in PRINTED_ROWS.items():
            with self.subTest(pedal=pedal):
                self.assertEqual(self.data["rows"][pedal - 1],
                                 {"pedal_id": pedal, "sources": expected})

    def test_all_positions_disconnections_duplicates_and_bus_membership(self):
        disconnected, duplicates, connected = [], [], []
        regular_offsets = {0: 0, 2: 12, 3: 24, 4: 31, 5: 36, 6: 40, 7: 43}
        self.assertEqual([row["pedal_id"] for row in self.data["rows"]], list(range(1, 26)))
        for row in self.data["rows"]:
            pedal, sources = row["pedal_id"], row["sources"]
            self.assertEqual(len(sources), 8)
            for column, offset in regular_offsets.items():
                self.assertEqual(sources[column], pedal + offset)
            self.assertEqual(sources[1], pedal + 12 if pedal < 8 else
                             None if pedal < 13 else pedal + 19)
            for column, source in enumerate(sources):
                if source is None:
                    disconnected.append((pedal, column))
                else:
                    self.assertIs(type(source), int)
                    self.assertTrue(1 <= source <= 91)
                    connected.append(source)
                    for earlier in range(column):
                        if source == sources[earlier]:
                            duplicates.append((pedal, earlier, column))
        self.assertEqual(len(connected), 195)
        self.assertEqual(disconnected, [(8, 1), (9, 1), (10, 1), (11, 1), (12, 1)])
        self.assertEqual(duplicates, [(pedal, 1, 2) for pedal in range(1, 8)])
        self.assertEqual(len(connected) + len(disconnected), 200)
        self.assertEqual(self.data["bus_columns"],
                         {"brown": [0, 1], "red": [2, 3], "orange": [4, 5], "yellow": [6, 7]})

    def test_every_position_rejects_an_in_range_wrong_source(self):
        for row in range(25):
            for column in range(8):
                with self.subTest(row=row, column=column):
                    data = copy.deepcopy(DATA)
                    data["rows"][row]["sources"][column] = 91
                    self.rejected(data)

    def test_every_connected_position_rejects_disconnection(self):
        for row in range(25):
            for column, source in enumerate(DATA["rows"][row]["sources"]):
                if source is not None:
                    with self.subTest(row=row, column=column):
                        data = copy.deepcopy(DATA)
                        data["rows"][row]["sources"][column] = None
                        self.rejected(data)

    def test_exception_contacts_cannot_be_repaired_or_deduplicated(self):
        for pedal in range(1, 13):
            wrong = [pedal + 19] if pedal <= 7 else [0, pedal + 12, pedal + 19]
            for source in wrong:
                with self.subTest(pedal=pedal, source=source):
                    data = copy.deepcopy(DATA)
                    data["rows"][pedal - 1]["sources"][1] = source
                    self.rejected(data)
        self.data["rows"][0]["sources"].pop(1)
        self.rejected(self.data)

    def test_all_object_fields_are_required_and_unknown_fields_rejected(self):
        for path in object_paths(DATA):
            for key in at_path(DATA, path):
                with self.subTest(path=path, missing=key):
                    data = copy.deepcopy(DATA)
                    del at_path(data, path)[key]
                    self.rejected(data)
            with self.subTest(path=path, unknown=True):
                data = copy.deepcopy(DATA)
                at_path(data, path)["gain"] = 1
                self.rejected(data)

    def test_every_metadata_value_and_integer_type_is_exact(self):
        for path, value in leaf_paths({key: value for key, value in DATA.items() if key != "rows"}):
            invalid = [value + 1, float(value)] if type(value) is int else ["changed"]
            if value == 1:
                invalid.append(True)
            for replacement in invalid:
                with self.subTest(path=path, replacement=replacement):
                    data = copy.deepcopy(DATA)
                    at_path(data, path[:-1])[path[-1]] = replacement
                    self.rejected(data)

    def test_ids_shapes_and_order_are_strict(self):
        for value in (None, [], "map", True, 1):
            self.rejected(value)
        for value in (None, {}, [], DATA["rows"][:-1], DATA["rows"] + [DATA["rows"][0]],
                      list(reversed(DATA["rows"]))):
            self.data["rows"] = value
            self.rejected(self.data)
        for pedal_id in (0, 26, 2, True, 1.0, "1", None):
            data = copy.deepcopy(DATA)
            data["rows"][0]["pedal_id"] = pedal_id
            self.rejected(data)
        for sources in (None, {}, [], DATA["rows"][0]["sources"] + [44]):
            data = copy.deepcopy(DATA)
            data["rows"][0]["sources"] = sources
            self.rejected(data)
        data = copy.deepcopy(DATA)
        data["rows"][1]["pedal_id"] = 1
        self.rejected(data)

    def test_source_bounds_and_types(self):
        for source in (0, -1, 92, True, False, 1.0, "1", {}, []):
            with self.subTest(source=source):
                data = copy.deepcopy(DATA)
                data["rows"][0]["sources"][0] = source
                self.rejected(data)
        for source in (float("nan"), float("inf"), -float("inf")):
            self.data["rows"][0]["sources"][0] = source
            with self.assertRaises(validator.PedalMapError):
                validator.validate_pedal_map(self.data)
            self.assertIs(self.data["rows"][0]["sources"][0], source)

    def test_json_duplicate_names_rejected_at_all_depths(self):
        for payload in (b'{"rows":[],"rows":[]}',
                        b'{"provenance":{"source_document":{"sha256":"a","sha256":"b"}}}',
                        b'{"rows":[{"pedal_id":1,"pedal_id":2}]}'):
            with self.subTest(payload=payload), self.assertRaisesRegex(validator.PedalMapError, "duplicate"):
                self.load_bytes(payload)

    def test_json_nonfinite_fractional_and_overflow_tokens_rejected(self):
        for token in ("NaN", "Infinity", "-Infinity", "1.0", "1e0", "1e999", "9" * 5000):
            with self.subTest(token=token[:20]), self.assertRaises(validator.PedalMapError):
                self.load_bytes(('{"schema_version":' + token + '}').encode())

    def test_malformed_encoding_depth_and_io_failures(self):
        for payload in (b"", b"{", RAW_DATA + b" junk", b"\xff", b"\xef\xbb\xbf" + RAW_DATA,
                        b"[" * 2000 + b"0" + b"]" * 2000):
            with self.subTest(prefix=payload[:20]), self.assertRaises(validator.PedalMapError):
                self.load_bytes(payload)
        for path in (self.path.parent / "missing.json", self.path.parent):
            with self.assertRaises(validator.PedalMapError):
                validator.load_pedal_map(path)

    def test_byte_limit_inclusive_and_read_only(self):
        exact = RAW_DATA + b" " * (validator.MAX_INPUT_BYTES - len(RAW_DATA))
        self.assertEqual(self.load_bytes(exact), DATA)
        self.assertEqual(self.path.read_bytes(), exact)
        with self.assertRaisesRegex(validator.PedalMapError, "byte limit"):
            self.load_bytes(exact + b" ")
        self.assertEqual(self.path.read_bytes(), exact + b" ")

    def test_cli_success_and_rejection_are_read_only(self):
        for payload, code in ((RAW_DATA, 0), (b'{"schema_version":NaN}', 1)):
            self.path.write_bytes(payload)
            result = subprocess.run([sys.executable, str(VALIDATOR_PATH), "--input", str(self.path)],
                                    text=True, capture_output=True, check=False)
            self.assertEqual(result.returncode, code, result.stderr)
            self.assertEqual(self.path.read_bytes(), payload)
            self.assertNotIn("Traceback", result.stderr)
            if code == 0:
                self.assertIn("200 positions, 195 connected, 5 disconnected", result.stdout)
                self.assertEqual(result.stderr, "")
            else:
                self.assertIn("pedal map error:", result.stderr)
                self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
