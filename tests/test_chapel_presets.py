#!/usr/bin/env python3
"""Independent atlas chapel catalog admission and publication acceptance.

Literal registration/position oracles come from reading B and its source guide,
not compiler constants. The producer is imported only to call its public API or
inject I/O failure; expected semantic data and serialized hashes are independent.
"""

from __future__ import annotations

from copy import deepcopy
import csv
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/compile_chapel_presets.py"
AUTHORING = ROOT / "data/registrations/atlas-chapel-nominal-v1.json"
REVIEW_A = ROOT / "data/registrations/review-a-chapel.csv"
REVIEW_B = ROOT / "data/registrations/review-b-chapel.csv"
SCHEMA = ROOT / "data/chapel-presets.schema.json"

# Entered from the independently frozen reading B, after reviewing its source
# guide. These literal rows are not loaded from the authoring/compiler at runtime.
KEYS = ("C#", "D", "D#", "E", "F", "F#", "G", "G#", "A")
UPPER = ("005320000", "004432000", "008740000", "004544222", "005403000",
         "004675300", "005644320", "006876540", "327645222")
LOWER = ("004545440", "004423220", "007373430", "004544220", "006644322",
         "005642200", "006845433", "008030000", "427866244")
POSITIONS = (("16", "brown"), ("5 1/3", "red"), ("8", "orange"), ("4", "yellow"),
             ("2 2/3", "green"), ("2", "blue"), ("1 3/5", "violet"),
             ("1 1/3", "gray"), ("1", "white"))
ATLAS_HASH = "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769"
READING_HASH = "dc2a8fd4e9750133c982bb42fd6cc7c12908f011154826035bb623f52d8de694"
AUTHORING_HASH = "c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf"
CANONICAL_HASH = "ebed39e9b73a0479b7493ce1d5fce1f3309f4c0663981144263877b8ca74dd1b"
CATALOG_HASH = "f500fa0aaca0ba8652eeede330094deb888f6a516b5c51958fd2381778fb5a91"
SENTINEL = b"previous output must survive\x00\xff\n"


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def expected_authoring() -> dict:
    return {
        "schema_version": 1,
        "model_id": "atlas-chapel-nominal-v1",
        "evidence_class": "documentary-reconstruction",
        "applicable_variant": "atlas-approved-chapel-arrangement",
        "source": {
            "document": "Hammond_B3_Leslie_Research_Atlas_500pp.pdf",
            "sha256": ATLAS_HASH,
            "page": 122,
            "primary_reference": {"citation": "S019-01", "table": "Table IV",
                                  "printed_page": "4-1", "status": "not-independently-verified"},
        },
        "tap_units": "discrete-transformer-tap-index",
        "drawbars": [{"position": n, "footage_ft": footage, "lead_color": color}
                     for n, (footage, color) in enumerate(POSITIONS, 1)],
        "registrations": [
            {"manual": manual, "preset_key": key, "preset_name": None,
             "drawbars": taps, "source_page": 122}
            for manual, row in (("upper", UPPER), ("lower", LOWER))
            for key, taps in zip(KEYS, row)
        ],
        "limitations": {"registration_names": "not-published-in-atlas-table",
                        "specimen_wiring": "unverified", "loaded_tap_gains": "unmeasured-not-modeled",
                        "physical_latch": "not-modeled", "percussion_interlock": "not-modeled"},
    }


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    output = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"duplicate output key: {key}")
        output[key] = value
    return output


def reject_nonfinite(token: str) -> None:
    raise ValueError(f"nonfinite JSON token: {token}")


def parse_json(payload: bytes | str) -> dict:
    return json.loads(payload, object_pairs_hook=unique_object, parse_constant=reject_nonfinite)


def snapshot_tree(root: Path) -> dict:
    """Do not follow symlinks or open special files in rejection fixtures."""
    result = {}
    for path in sorted(root.rglob("*")):
        metadata = path.lstat()
        mode = stat.S_IFMT(metadata.st_mode)
        if stat.S_ISLNK(metadata.st_mode):
            content = os.readlink(path)
        elif stat.S_ISREG(metadata.st_mode):
            content = path.read_bytes()
        else:
            content = None
        result[path.relative_to(root).as_posix()] = (mode, stat.S_IMODE(metadata.st_mode),
                                                   metadata.st_ino, content)
    return result


class ChapelCatalogAcceptance(unittest.TestCase):
    cli_invocations = 0
    api_rejections = 0
    io_faults = 0

    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("chapel_compiler_acceptance_subject", TOOL)
        if spec is None or spec.loader is None:
            raise RuntimeError("chapel compiler module is required")
        cls.subject = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.subject)
        cls.original_inputs = {path: path.read_bytes() for path in (AUTHORING, REVIEW_A, REVIEW_B, SCHEMA, TOOL)}
        print(f"Chapel compiler SHA-256: {sha256(cls.original_inputs[TOOL])}", flush=True)

    @classmethod
    def tearDownClass(cls) -> None:
        for path, original in cls.original_inputs.items():
            if path.read_bytes() != original:
                raise AssertionError(f"source input changed during acceptance: {path}")
        print(f"Chapel acceptance: {cls.cli_invocations} CLI invocations, "
              f"{cls.api_rejections} public-API admission rejects, "
              f"{cls.io_faults} injected publication failures", flush=True)

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="hammond-chapel-acceptance-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.authoring = self.root / "authoring.json"
        self.review_a = self.root / "review-a.csv"
        self.review_b = self.root / "review-b.csv"
        self.output = self.root / "catalog.json"
        for destination, source in ((self.authoring, AUTHORING), (self.review_a, REVIEW_A),
                                    (self.review_b, REVIEW_B)):
            destination.write_bytes(self.original_inputs[source])
        self.inputs = (self.authoring, self.review_a, self.review_b)
        self.output.write_bytes(SENTINEL)

    def arguments(self, *, output: Path | None = None, inputs: tuple | None = None) -> list[str]:
        selected = inputs or self.inputs
        return ["--input", str(selected[0]), "--review-a", str(selected[1]),
                "--review-b", str(selected[2]), "--output", str(output or self.output)]

    def cli(self, arguments: list[str] | None = None, *, expected: int = 0) -> subprocess.CompletedProcess:
        self.__class__.cli_invocations += 1
        result = subprocess.run([sys.executable, str(TOOL), *(arguments if arguments is not None else self.arguments())],
                                cwd=self.root, stdin=subprocess.DEVNULL, capture_output=True,
                                timeout=5, check=False, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        self.assertEqual(result.returncode, expected, result.stdout.decode(errors="replace") +
                         result.stderr.decode(errors="replace"))
        if expected == 0:
            self.assertEqual(result.stderr, b"")
        else:
            self.assertNotEqual(result.stderr, b"")
            self.assertNotIn(b"Traceback", result.stderr)
        return result

    def reject_cli(self, arguments: list[str] | None = None, *, expected: int = 1) -> subprocess.CompletedProcess:
        before = snapshot_tree(self.root)
        result = self.cli(arguments, expected=expected)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(snapshot_tree(self.root), before, "failed CLI changed a file, inode or fixture entry")
        return result

    def reject_authoring(self, data: object) -> None:
        self.authoring.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        before = snapshot_tree(self.root)
        with self.assertRaises(self.subject.ChapelCompileError):
            self.subject.compile_chapel_presets(*self.inputs)
        self.__class__.api_rejections += 1
        self.assertEqual(snapshot_tree(self.root), before)

    def symlink(self, target: Path, link: Path, *, directory: bool = False) -> None:
        try:
            link.symlink_to(target, target_is_directory=directory)
        except OSError as error:
            if os.name == "nt" and getattr(error, "winerror", None) == 1314:
                self.skipTest("Windows account lacks the privilege needed for this real symlink fixture")
            raise

    def test_frozen_readings_and_authoring_match_source_literals(self) -> None:
        expected_rows = [[manual, key, "", taps, "122"]
                         for manual, taps_list in (("upper", UPPER), ("lower", LOWER))
                         for key, taps in zip(KEYS, taps_list)]
        for source in (REVIEW_A, REVIEW_B):
            payload = self.original_inputs[source]
            self.assertEqual(len(payload), 466)
            self.assertEqual(sha256(payload), READING_HASH)
            rows = list(csv.reader(io.StringIO(payload.decode("utf-8"), newline="")))
            self.assertEqual(rows[0], ["manual", "preset_key", "preset_name", "drawbars", "page"])
            self.assertEqual(rows[1:], expected_rows)
        self.assertEqual(sum(len(row[3]) for row in expected_rows), 162)
        self.assertEqual(sum(row[3].startswith("0") for row in expected_rows), 16)
        self.assertEqual(parse_json(self.original_inputs[AUTHORING]), expected_authoring())
        self.assertEqual(sha256(self.original_inputs[AUTHORING]), AUTHORING_HASH)

    def test_schema_declares_every_literal_and_closed_shape(self) -> None:
        schema = parse_json(self.original_inputs[SCHEMA])
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["$id"], "urn:hammond:chapel-presets:atlas-chapel-nominal-v1")

        def inspect(node: dict, expected: object) -> None:
            if type(expected) is dict:
                self.assertEqual(node["type"], "object")
                self.assertIs(node["additionalProperties"], False)
                self.assertEqual(set(node["required"]), set(expected))
                self.assertEqual(len(node["required"]), len(expected))
                self.assertEqual(set(node["properties"]), set(expected))
                for key, value in expected.items():
                    inspect(node["properties"][key], value)
            elif type(expected) is list:
                self.assertEqual(node["type"], "array")
                self.assertEqual(node["minItems"], len(expected))
                self.assertEqual(node["maxItems"], len(expected))
                self.assertIs(node["items"], False)
                self.assertEqual(len(node["prefixItems"]), len(expected))
                for entry, value in zip(node["prefixItems"], expected):
                    inspect(entry, value)
            else:
                self.assertEqual(node["type"], {str: "string", int: "integer", type(None): "null"}[type(expected)])
                self.assertIs(type(node["const"]), type(expected))
                self.assertEqual(node["const"], expected)
        inspect(schema, expected_authoring())

    def test_cli_output_exact_semantics_identity_and_repeatability(self) -> None:
        before_inputs = [path.read_bytes() for path in self.inputs]
        self.assertEqual(self.cli().stdout, b"")
        first = self.output.read_bytes()
        self.assertEqual(len(first), 4837)
        self.assertEqual(sha256(first), CATALOG_HASH)
        expected = expected_authoring()
        expected["format"] = "hammond-chapel-catalog-v1"
        expected["inputs"] = {
            "authoring": {"sha256": AUTHORING_HASH, "canonical_sha256": CANONICAL_HASH, "bytes": 4298},
            "review_a": {"sha256": READING_HASH, "bytes": 466},
            "review_b": {"sha256": READING_HASH, "bytes": 466},
        }
        actual = parse_json(first)
        self.assertEqual(actual, expected)
        self.assertIs(type(actual["schema_version"]), int)
        self.assertIs(type(actual["source"]["page"]), int)
        for row in actual["drawbars"]:
            self.assertIs(type(row["position"]), int)
        for row in actual["registrations"]:
            self.assertIs(type(row["source_page"]), int)
            self.assertIs(type(row["drawbars"]), str)
            self.assertIsNone(row["preset_name"])
        self.assertEqual(self.cli().stdout, b"")
        self.assertEqual(self.output.read_bytes(), first)
        self.assertEqual([path.read_bytes() for path in self.inputs], before_inputs)
        self.assertEqual(set(path.name for path in self.root.iterdir()),
                         {"authoring.json", "review-a.csv", "review-b.csv", "catalog.json"})

    def test_authoring_format_variation_changes_only_raw_identity(self) -> None:
        self.cli()
        original = parse_json(self.output.read_bytes())
        # Standard JSON formatting is an admitted input variation. Semantic and
        # canonical identity remain exact; source byte identity must change.
        changed = json.dumps(expected_authoring(), sort_keys=True, separators=(",", ":")).encode() + b"\n \t\r\n"
        self.authoring.write_bytes(changed)
        self.cli()
        actual = parse_json(self.output.read_bytes())
        expected = deepcopy(original)
        expected["inputs"]["authoring"] = {"sha256": sha256(changed), "bytes": len(changed),
                                             "canonical_sha256": CANONICAL_HASH}
        self.assertEqual(actual, expected)
        self.assertNotEqual(actual["inputs"]["authoring"]["sha256"], AUTHORING_HASH)

    def test_unicode_space_paths_and_destination_only_replacement(self) -> None:
        directory = self.root / "chapel \u96ea controls"
        directory.mkdir()
        paths = tuple(directory / name for name in ("source \u03a9.json", "review A.csv", "review B.csv"))
        for source, destination in zip(self.inputs, paths):
            destination.write_bytes(source.read_bytes())
        output = directory / "compiled \u03bc catalog.json"
        old_alias = directory / "old output retained.json"
        output.write_bytes(SENTINEL)
        os.link(output, old_alias)
        self.cli(self.arguments(output=output, inputs=paths))
        self.assertEqual(sha256(output.read_bytes()), CATALOG_HASH)
        self.assertEqual(old_alias.read_bytes(), SENTINEL)
        self.assertFalse(output.samefile(old_alias))

    def test_strict_cli_and_help_do_not_touch_files(self) -> None:
        before = snapshot_tree(self.root)
        help_result = self.cli(["--help"])
        self.assertIn(b"--review-a", help_result.stdout)
        self.assertEqual(snapshot_tree(self.root), before)
        complete = self.arguments()
        bad_arguments = [[], ["--unknown"], complete + ["--unknown"],
                         ["--in", complete[1], *complete[2:]], complete + ["extra"]]
        for index in (0, 2, 4, 6):
            bad_arguments.append(complete[:index] + complete[index + 2:])
            bad_arguments.append(complete + complete[index:index + 2])
            bad_arguments.append([*complete, complete[index]])
        for arguments in bad_arguments:
            with self.subTest(arguments=arguments):
                self.reject_cli(arguments, expected=2)

    def test_json_lexical_failures_are_bounded_and_atomic(self) -> None:
        normal = self.original_inputs[AUTHORING]
        compact = json.dumps(expected_authoring(), separators=(",", ":")).encode()
        payloads = {
            "duplicate-root": compact.replace(b'"schema_version":1', b'"schema_version":1,"schema_version":1', 1),
            "duplicate-source": compact.replace(b'"page":122', b'"page":122,"page":122', 1),
            "duplicate-row": compact.replace(b'"preset_key":"C#"', b'"preset_key":"C#","preset_key":"C#"', 1),
            "float-equal-integer": compact.replace(b'"schema_version":1', b'"schema_version":1.0', 1),
            "exponent-equal-integer": compact.replace(b'"page":122', b'"page":1.22e2', 1),
            "nan": compact.replace(b'"schema_version":1', b'"schema_version":NaN', 1),
            "infinity": compact.replace(b'"schema_version":1', b'"schema_version":Infinity', 1),
            "invalid-utf8": b"\xff" + normal,
            "utf8-bom": b"\xef\xbb\xbf" + normal,
            "empty": b"",
            "truncated": normal[:-5],
            "trailing-object": normal + b"{}",
            "nul": normal + b"\0",
            "deep-nesting": b"[" * 1800 + b"0" + b"]" * 1800,
            "huge-integer": b'{"schema_version":' + b"1" * 5000 + b"}",
        }
        for name, payload in payloads.items():
            with self.subTest(case=name):
                self.authoring.write_bytes(payload)
                self.reject_cli()

    def test_every_tap_position_rejects_an_in_range_wrong_digit(self) -> None:
        checked = 0
        for row, taps in enumerate((*UPPER, *LOWER)):
            for position, digit in enumerate(taps):
                with self.subTest(row=row, position=position):
                    candidate = expected_authoring()
                    candidate["registrations"][row]["drawbars"] = (
                        taps[:position] + str((int(digit) + 1) % 9) + taps[position + 1:])
                    self.reject_authoring(candidate)
                    checked += 1
        self.assertEqual(checked, 162)

    def test_closed_fields_types_and_evidence_cannot_be_relabelled(self) -> None:
        base = expected_authoring()
        paths = [(), ("source",), ("source", "primary_reference"), ("limitations",),
                 ("drawbars", 0), ("registrations", 0)]
        for path in paths:
            for action in ("missing", "unknown", "wrong-container"):
                candidate = deepcopy(base)
                selected = candidate
                for part in path:
                    selected = selected[part]
                if action == "missing":
                    del selected[next(iter(selected))]
                elif action == "unknown":
                    selected["unreviewed_extra"] = 0
                elif path:
                    parent = candidate
                    for part in path[:-1]:
                        parent = parent[part]
                    parent[path[-1]] = []
                else:
                    candidate = []
                with self.subTest(path=path, action=action):
                    self.reject_authoring(candidate)
        replacements = [
            (("schema_version",), True), (("schema_version",), "1"), (("schema_version",), 1.0),
            (("schema_version",), 0), (("model_id",), "factory-chapel"),
            (("evidence_class",), "measured"), (("applicable_variant",), "all-B3"),
            (("tap_units",), "linear-amplitude"), (("source", "sha256"), "0" * 64),
            (("source", "page"), True), (("source", "page"), 123),
            (("source", "primary_reference", "status"), "verified"),
            (("source", "primary_reference", "printed_page"), "122"),
            (("limitations", "physical_latch"), "measured"),
            (("limitations", "specimen_wiring"), "verified"),
            (("drawbars", 0, "position"), True), (("drawbars", 1, "footage_ft"), 16 / 3),
            (("drawbars", 7, "lead_color"), "grey"),
            (("registrations", 0, "source_page"), 122.0),
            (("registrations", 0, "preset_name"), ""),
            (("registrations", 0, "preset_name"), "Invented factory name"),
            (("registrations", 0, "drawbars"), 5320000),
        ]
        for path, value in replacements:
            candidate = deepcopy(base)
            selected = candidate
            for part in path[:-1]:
                selected = selected[part]
            selected[path[-1]] = value
            with self.subTest(path=path, value=value):
                self.reject_authoring(candidate)

    def test_matrix_shape_manual_order_keys_and_digit_syntax(self) -> None:
        base = expected_authoring()
        for field in ("drawbars", "registrations"):
            for action in ("remove", "append", "swap", "duplicate"):
                candidate = deepcopy(base)
                values = candidate[field]
                if action == "remove":
                    values.pop()
                elif action == "append":
                    values.append(deepcopy(values[0]))
                elif action == "swap":
                    values[0], values[1] = values[1], values[0]
                else:
                    values[1] = deepcopy(values[0])
                with self.subTest(field=field, action=action):
                    self.reject_authoring(candidate)
        for field, values in (
            ("manual", ("lower", "Upper", "pedals", "")),
            ("preset_key", ("C", "A#", "B", "Db", "C\u266f", "D")),
            ("drawbars", ("00532000", "0053200000", "905320000", "-05320000", " 05320000", "\u066005320000", "00532000\n")),
        ):
            for value in values:
                candidate = deepcopy(base)
                candidate["registrations"][0][field] = value
                with self.subTest(field=field, value=value):
                    self.reject_authoring(candidate)

    def test_both_reviews_require_exact_cells_and_frozen_bytes(self) -> None:
        original = self.original_inputs[REVIEW_B]
        lines = original.splitlines(keepends=True)
        mutations = {
            "header": original.replace(b"manual,preset_key", b"preset_key,manual", 1),
            "missing-row": b"".join(lines[:-1]),
            "extra-row": original + lines[-1],
            "duplicate-row": b"".join([*lines[:2], lines[1], *lines[3:]]),
            "swapped-rows": b"".join([lines[0], lines[2], lines[1], *lines[3:]]),
            "wrong-manual": original.replace(b"upper,C#", b"lower,C#", 1),
            "wrong-key": original.replace(b"upper,C#", b"upper,Db", 1),
            "invented-name": original.replace(b"C#,,", b"C#,Flute,", 1),
            "wrong-tap": original.replace(b"005320000", b"105320000", 1),
            "out-of-range-tap": original.replace(b"005320000", b"905320000", 1),
            "lost-zero": original.replace(b"005320000", b"5320000", 1),
            "extra-column": original.replace(b"005320000,122", b"005320000,122,extra", 1),
            "missing-column": original.replace(b"005320000,122", b"005320000", 1),
            "space-page": original.replace(b",122\n", b", 122\n", 1),
            "crlf-same-cells": original.replace(b"\n", b"\r\n"),
            "quoted-same-cells": original.replace(b"upper,C#", b'"upper",C#', 1),
            "blank-line": original + b"\n",
            "broken-quote": original.replace(b"upper,C#", b'"upper,C#', 1),
            "invalid-utf8": b"\xff" + original,
            "bom": b"\xef\xbb\xbf" + original,
        }
        for path in (self.review_a, self.review_b):
            for name, payload in mutations.items():
                with self.subTest(review=path.name, case=name):
                    path.write_bytes(payload)
                    self.reject_cli()
            path.write_bytes(original)

    def test_authoring_byte_limit_inclusive_and_oversize_rejection(self) -> None:
        base = self.original_inputs[AUTHORING]
        exact = base + b" " * (65536 - len(base))
        self.authoring.write_bytes(exact)
        self.cli()
        identity = parse_json(self.output.read_bytes())["inputs"]["authoring"]
        self.assertEqual(identity, {"bytes": 65536, "sha256": sha256(exact), "canonical_sha256": CANONICAL_HASH})
        self.authoring.write_bytes(exact + b" ")
        result = self.reject_cli()
        self.assertIn(b"at most 65536 bytes", result.stderr)
        self.authoring.write_bytes(base)
        for path in (self.review_a, self.review_b):
            path.write_bytes(b" " * 16385)
            result = self.reject_cli()
            self.assertIn(b"at most 16384 bytes", result.stderr)
            path.write_bytes(self.original_inputs[REVIEW_B])

    def test_missing_directory_and_special_inputs_reject_without_blocking(self) -> None:
        for index, original in enumerate(self.inputs):
            for kind in ("missing", "directory", "fifo"):
                if kind == "fifo" and not hasattr(os, "mkfifo"):
                    continue
                candidate = self.root / f"input-{index}-{kind}"
                if kind == "directory":
                    candidate.mkdir()
                elif kind == "fifo":
                    os.mkfifo(candidate)
                inputs = list(self.inputs)
                inputs[index] = candidate
                with self.subTest(index=index, kind=kind):
                    self.reject_cli(self.arguments(inputs=tuple(inputs)))
                if kind != "missing":
                    candidate.rmdir() if kind == "directory" else candidate.unlink()

    def test_input_symlink_leaves_and_distinct_readings(self) -> None:
        for index, original in enumerate(self.inputs):
            for dangling in (False, True):
                link = self.root / f"source-link-{index}-{dangling}"
                self.symlink(self.root / "absent" if dangling else original, link)
                inputs = list(self.inputs)
                inputs[index] = link
                self.reject_cli(self.arguments(inputs=tuple(inputs)))
                link.unlink()
        self.reject_cli(self.arguments(inputs=(self.authoring, self.review_a, self.review_a)))
        alias = self.root / "review-hardlink.csv"
        os.link(self.review_a, alias)
        result = self.reject_cli(self.arguments(inputs=(self.authoring, self.review_a, alias)))
        self.assertIn(b"must be distinct", result.stderr)

    def test_output_direct_hardlink_and_resolved_parent_aliases(self) -> None:
        for source in self.inputs:
            with self.subTest(source=source.name):
                self.reject_cli(self.arguments(output=source))
                hardlink = self.root / "output-hardlink"
                os.link(source, hardlink)
                self.reject_cli(self.arguments(output=hardlink))
                hardlink.unlink()
        parent_alias = self.root / "parent-alias"
        self.symlink(self.root, parent_alias, directory=True)
        # snapshot_tree does not recurse into directory symlinks.
        self.reject_cli(self.arguments(output=parent_alias / self.review_a.name))

    def test_output_nonregular_missing_parent_and_symlink_rejection(self) -> None:
        directory = self.root / "output-directory"
        directory.mkdir()
        self.reject_cli(self.arguments(output=directory))
        self.reject_cli(self.arguments(output=self.root / "absent-parent" / "catalog.json"))
        if hasattr(os, "mkfifo"):
            fifo = self.root / "output-fifo"
            os.mkfifo(fifo)
            self.reject_cli(self.arguments(output=fifo))
        for dangling in (False, True):
            link = self.root / f"output-link-{dangling}"
            self.symlink(self.root / "absent-target" if dangling else self.output, link)
            self.reject_cli(self.arguments(output=link))

    def test_publication_failures_preserve_existing_files_and_remove_temporary(self) -> None:
        text = self.subject.compile_chapel_presets(*self.inputs)
        real_temporary = self.subject.tempfile.NamedTemporaryFile

        class FaultySink:
            def __init__(self, sink, stage):
                self.sink, self.stage = sink, stage
                self.name = sink.name

            def __enter__(self):
                self.sink.__enter__()
                return self

            def __exit__(self, *arguments):
                return self.sink.__exit__(*arguments)

            def write(self, payload):
                if self.stage == "short-write":
                    return self.sink.write(payload[:-1])
                return self.sink.write(payload)

            def flush(self):
                if self.stage == "flush":
                    raise OSError("injected flush failure")
                return self.sink.flush()

            def fileno(self):
                return self.sink.fileno()

        for stage in ("create", "short-write", "flush", "fsync", "replace"):
            if stage == "create":
                patch = mock.patch.object(self.subject.tempfile, "NamedTemporaryFile", side_effect=OSError("injected create failure"))
            elif stage in ("short-write", "flush"):
                patch = mock.patch.object(self.subject.tempfile, "NamedTemporaryFile",
                                          side_effect=lambda *a, **kw: FaultySink(real_temporary(*a, **kw), stage))
            else:
                patch = mock.patch.object(self.subject.os, stage, side_effect=OSError(f"injected {stage} failure"))
            with self.subTest(stage=stage):
                before = snapshot_tree(self.root)
                with patch, self.assertRaises(self.subject.ChapelCompileError):
                    self.subject.write_compiled_catalog(self.output, text, self.inputs)
                self.__class__.io_faults += 1
                self.assertEqual(snapshot_tree(self.root), before)

    def test_writer_payload_and_input_list_bounds_preserve_destination(self) -> None:
        text = self.subject.compile_chapel_presets(*self.inputs)
        for payload, inputs in ((None, self.inputs), (b"{}", self.inputs), ("", self.inputs),
                                (" " * 65537, self.inputs), ("\ud800", self.inputs),
                                (text, self.inputs[:2]), (text, (*self.inputs, self.authoring))):
            with self.subTest(payload_type=type(payload).__name__, size=len(payload) if payload else 0,
                              input_count=len(inputs)):
                before = snapshot_tree(self.root)
                with self.assertRaises(self.subject.ChapelCompileError):
                    self.subject.write_compiled_catalog(self.output, payload, inputs)
                self.__class__.api_rejections += 1
                self.assertEqual(snapshot_tree(self.root), before)


if __name__ == "__main__":
    unittest.main()
