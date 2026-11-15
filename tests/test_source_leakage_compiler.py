#!/usr/bin/env python3
"""Standard-library acceptance tests for authoring and safe compilation only.

Native-loader round trips belong to the later cross-language integration gate.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import compile_source_leakage as compiler  # noqa: E402


FIXTURES = ROOT / "data" / "source-leakage"
PAIR_BYTES = (FIXTURES / "synthetic-pair-demo-v1.json").read_bytes()
IDENTITY_BYTES = (FIXTURES / "synthetic-identity-v1.json").read_bytes()
PAIR = json.loads(PAIR_BYTES)


def authored(profile: dict) -> bytes:
    return json.dumps(profile, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def with_edges(edges: list[dict]) -> dict:
    result = copy.deepcopy(PAIR)
    result["edges"] = edges
    return result


class SourceLeakageCompilerTests(unittest.TestCase):
    def assert_rejected(self, profile: dict, pattern: str | None = None) -> None:
        with self.assertRaisesRegex(compiler.SourceLeakageProfileError, pattern or "."):
            compiler.compile_bytes(authored(profile))

    def test_pair_exact_grammar_and_actual_byte_hashes(self):
        compiled, receipt = compiler.compile_bytes(PAIR_BYTES)
        digest = hashlib.sha256(PAIR_BYTES).hexdigest()
        expected = (
            "B3LEAKAGE1\nmodel static-source-leakage-v1\n"
            "profile_id synthetic-pair-demo-v1\nevidence_status synthetic\n"
            "boundary normalized-generator-precontact-v1\n"
            "source_content excludes-leakage\n"
            f"authoring_sha256 {digest}\nsource_count 91\nedge_count 2\n"
            "edge destination 25 source 37 gain 0.0625\n"
            "edge destination 37 source 25 gain -0.03125\nend\n"
        ).encode("ascii")
        self.assertEqual(compiled, expected)
        self.assertEqual(receipt["input_sha256"], digest)
        self.assertEqual(receipt["compiled_sha256"], hashlib.sha256(expected).hexdigest())
        self.assertEqual(receipt["compiled_bytes"], len(expected))
        self.assertEqual(receipt["edge_count"], 2)
        self.assertEqual(receipt["maximum_row_absolute_gain_sum"], 0.0625)
        self.assertEqual(receipt["model"], "static-source-leakage-v1")
        self.assertEqual(receipt["profile_id"], "synthetic-pair-demo-v1")
        self.assertEqual(receipt["evidence_status"], "synthetic")
        self.assertEqual(receipt["boundary"], "normalized-generator-precontact-v1")

    def test_identity_fixture_is_valid_empty_graph(self):
        compiled, receipt = compiler.compile_bytes(IDENTITY_BYTES)
        self.assertTrue(compiled.endswith(b"edge_count 0\nend\n"))
        self.assertEqual(receipt["edge_count"], 0)
        self.assertEqual(receipt["maximum_row_absolute_gain_sum"], 0.0)
        self.assertEqual(math.copysign(1, receipt["maximum_row_absolute_gain_sum"]), 1)

    def test_authoring_whitespace_and_order_change_hash_but_not_arithmetic(self):
        reordered = copy.deepcopy(PAIR)
        reordered["edges"].reverse()
        first, first_receipt = compiler.compile_bytes(PAIR_BYTES)
        second, second_receipt = compiler.compile_bytes(authored(reordered))
        edge_lines = lambda data: [line for line in data.splitlines() if line.startswith(b"edge ")]
        self.assertEqual(edge_lines(first), edge_lines(second))
        self.assertNotEqual(first_receipt["input_sha256"], second_receipt["input_sha256"])
        self.assertNotEqual(first_receipt["compiled_sha256"], second_receipt["compiled_sha256"])
        spaced = PAIR_BYTES + b" \n\t"
        _, spaced_receipt = compiler.compile_bytes(spaced)
        self.assertEqual(spaced_receipt["input_sha256"], hashlib.sha256(spaced).hexdigest())

    def test_missing_and_unknown_members_at_every_object_level(self):
        for path in ((), ("algorithm_reference",), ("edges", 0)):
            original = copy.deepcopy(PAIR)
            nested = original
            for key in path:
                nested = nested[key]
            for missing in list(nested):
                profile = copy.deepcopy(original)
                target = profile
                for key in path:
                    target = target[key]
                del target[missing]
                with self.subTest(path=path, missing=missing):
                    self.assert_rejected(profile, "missing")
            nested["unexpected"] = None
            with self.subTest(path=path, unknown=True):
                self.assert_rejected(original, "unknown")

    def test_duplicate_json_members_and_nonfinite_literals(self):
        mutations = [
            PAIR_BYTES.replace(b'"schema_version": 1', b'"schema_version": 1, "schema_version": 1'),
            PAIR_BYTES.replace(b'"model":', b'"\\u006dodel": "static-source-leakage-v1", "model":', 1),
            PAIR_BYTES.replace(b'"document":', b'"document": "duplicate", "document":', 1),
            PAIR_BYTES.replace(b'"source": 37', b'"source": 37, "source": 37', 1),
        ]
        for raw in mutations:
            with self.subTest(raw=raw[:50]), self.assertRaisesRegex(compiler.SourceLeakageProfileError, "duplicate"):
                compiler.compile_bytes(raw)
        for token in (b"NaN", b"Infinity", b"-Infinity"):
            with self.subTest(token=token), self.assertRaisesRegex(compiler.SourceLeakageProfileError, "nonfinite"):
                compiler.compile_bytes(PAIR_BYTES.replace(b"0.0625", token, 1))

    def test_fixed_metadata_is_exact_and_typed(self):
        wrong = {
            "schema_version": [True, 1.0, "1", 2, None],
            "source_count": [True, 91.0, "91", 90, None],
            "model": ["static-source-leakage-v2", "STATIC-SOURCE-LEAKAGE-V1", 1],
            "evidence_status": ["measured", "Synthetic", True],
            "coefficient_origin": ["atlas", "Synthetic-fixture", None],
            "boundary": ["postcontact", "Normalized-generator-precontact-v1"],
            "units": ["dB", "Normalized-amplitude-ratio"],
            "source_content": ["includes-leakage", "Excludes-leakage"],
        }
        for key, values in wrong.items():
            for value in values:
                profile = copy.deepcopy(PAIR)
                profile[key] = value
                with self.subTest(key=key, value=value):
                    self.assert_rejected(profile)

    def test_algorithm_reference_is_exact(self):
        for key, values in {
            "document": ["other.pdf", None],
            "sha256": [compiler.ATLAS_SHA256.upper(), "0" * 64, None],
            "pdf_pages": [[79, 80, 81, 82, 83], [79.0, 80, 81, 82, 83, 84],
                          [True, 80, 81, 82, 83, 84], [84, 83, 82, 81, 80, 79], None],
        }.items():
            for value in values:
                profile = copy.deepcopy(PAIR)
                profile["algorithm_reference"][key] = value
                with self.subTest(key=key, value=value):
                    self.assert_rejected(profile)

    def test_profile_id_and_description_boundaries(self):
        for identifier in ("synthetic-a", "synthetic-" + "z" * 54):
            profile = copy.deepcopy(PAIR)
            profile["profile_id"] = identifier
            compiler.compile_bytes(authored(profile))
        for identifier in ("synthetic-", "synthetic--a", "synthetic-" + "z" * 55,
                           "synthetic-A", "synthetic-é", "Synthetic-a", "synthetic-a\n",
                           "synthetic-a b", "synthetic-a_", None, True):
            profile = copy.deepcopy(PAIR)
            profile["profile_id"] = identifier
            with self.subTest(identifier=identifier):
                self.assert_rejected(profile, "profile_id")
        for description in ("", "x" * 513, None, True):
            profile = copy.deepcopy(PAIR)
            profile["description"] = description
            with self.subTest(description=description):
                self.assert_rejected(profile, "description")
        profile = copy.deepcopy(PAIR)
        profile["description"] = "é" * 512
        compiler.compile_bytes(authored(profile))

    def test_structural_types(self):
        for raw in (b"[]", b"null", b"true", b"1", b'"profile"'):
            with self.subTest(raw=raw), self.assertRaises(compiler.SourceLeakageProfileError):
                compiler.compile_bytes(raw)
        for field, value in (("algorithm_reference", []), ("edges", {}),
                             ("edges", [None]), ("edges", [[37, 25, 0.0625]])):
            profile = copy.deepcopy(PAIR)
            profile[field] = value
            with self.subTest(field=field, value=value):
                self.assert_rejected(profile)

    def test_edge_ids_self_edges_and_duplicates(self):
        for field in ("source", "destination"):
            for value in (0, -1, 92, True, 25.0, "25", None):
                profile = copy.deepcopy(PAIR)
                profile["edges"][0][field] = value
                with self.subTest(field=field, value=value):
                    self.assert_rejected(profile)
        self.assert_rejected(with_edges([{"source": 1, "destination": 1, "gain": 0.125}]), "self-edge")
        for gain in (0.0625, -0.0625):
            profile = copy.deepcopy(PAIR)
            duplicate = copy.deepcopy(profile["edges"][0])
            duplicate["gain"] = gain
            profile["edges"].append(duplicate)
            with self.subTest(gain=gain):
                self.assert_rejected(profile, "duplicates")

    def test_gain_range_types_nonfinite_overflow_and_underflow(self):
        for gain in (0, -0.0, True, False, "0.125", None, [], {}, 0.2500001, -0.2500001):
            profile = copy.deepcopy(PAIR)
            profile["edges"][0]["gain"] = gain
            with self.subTest(gain=gain):
                self.assert_rejected(profile)
        for token in (b"1e309", b"-1e309", b"1e-400", b"-1e-400", b"1e-9999999"):
            with self.subTest(token=token), self.assertRaises(compiler.SourceLeakageProfileError):
                compiler.compile_bytes(PAIR_BYTES.replace(b"0.0625", token, 1))
        for token in (b"0x1p-3", b"+0.125", b".125", b"1.", b"01", b"1e"):
            with self.subTest(token=token), self.assertRaises(compiler.SourceLeakageProfileError):
                compiler.compile_bytes(PAIR_BYTES.replace(b"0.0625", token, 1))

    def test_round_trip_decimal_and_nonzero_subnormals(self):
        for value in (0.25, -0.25, 0.1, -0.1, math.nextafter(0.25, 0.0),
                      math.ulp(0.0), -math.ulp(0.0), sys.float_info.min):
            profile = with_edges([{"source": 1, "destination": 91, "gain": value}])
            compiled, receipt = compiler.compile_bytes(authored(profile))
            line = next(line for line in compiled.decode("ascii").splitlines() if line.startswith("edge "))
            token = line.split()[-1]
            with self.subTest(value=value):
                self.assertEqual(float(token).hex(), value.hex())
                self.assertLessEqual(len(token), 128)
                self.assertEqual(receipt["maximum_row_absolute_gain_sum"], abs(value))

    def test_row_and_total_capacities(self):
        eight = [{"source": source, "destination": 91, "gain": 0.0625} for source in range(1, 9)]
        compiler.compile_bytes(authored(with_edges(eight)))
        ninth = eight + [{"source": 9, "destination": 91, "gain": 0.001}]
        self.assert_rejected(with_edges(ninth), "8 incoming")
        too_loud = [{"source": source, "destination": 91, "gain": 0.25} for source in range(1, 4)]
        self.assert_rejected(with_edges(too_loud), "sum exceeds")
        full = [
            {"source": (destination - 1 + offset) % 91 + 1,
             "destination": destination, "gain": 0.0625}
            for destination in range(1, 92) for offset in range(1, 9)
        ]
        compiled, receipt = compiler.compile_bytes(authored(with_edges(full)))
        self.assertEqual(receipt["edge_count"], 728)
        self.assertEqual(receipt["maximum_row_absolute_gain_sum"], 0.5)
        self.assertLess(len(compiled), 128 * 1024)
        self.assert_rejected(with_edges(full + [copy.deepcopy(full[0])]), "728")

    def test_frozen_sequential_binary64_row_boundary(self):
        tiny = 2.0 ** -56
        admitted = [0.25, tiny, tiny, tiny, tiny, tiny, tiny, 0.25]
        rejected = [tiny, tiny, tiny, tiny, tiny, tiny, 0.25, 0.25]
        # These expected outcomes are fixed by A10 before implementation. They
        # distinguish sequential rounding from exact or compensated reduction.
        for gains, accept in ((admitted, True), (rejected, False)):
            original = [{"source": index + 1, "destination": 91, "gain": gain}
                        for index, gain in enumerate(gains)]
            for edges in (original, list(reversed(original)), original[3:] + original[:3]):
                with self.subTest(accept=accept, sources=[edge["source"] for edge in edges]):
                    if accept:
                        _, receipt = compiler.compile_bytes(authored(with_edges(edges)))
                        self.assertEqual(receipt["maximum_row_absolute_gain_sum"], 0.5)
                    else:
                        self.assert_rejected(with_edges(edges), "sum exceeds")

    def test_invalid_encoding_malformed_trailing_and_deep_json(self):
        for raw in (b"\xef\xbb\xbf" + PAIR_BYTES, b"\xff" + PAIR_BYTES,
                    PAIR_BYTES[:-2], PAIR_BYTES + b"{}", PAIR_BYTES + b"\x00",
                    b"[" * 2000 + b"0" + b"]" * 2000):
            with self.subTest(prefix=raw[:20]), self.assertRaises(compiler.SourceLeakageProfileError):
                compiler.compile_bytes(raw)

    def test_input_byte_limit_is_inclusive_and_file_read_is_bounded(self):
        exact = PAIR_BYTES + b" " * (256 * 1024 - len(PAIR_BYTES))
        _, receipt = compiler.compile_bytes(exact)
        self.assertEqual(receipt["input_sha256"], hashlib.sha256(exact).hexdigest())
        with self.assertRaisesRegex(compiler.SourceLeakageProfileError, "256 KiB"):
            compiler.compile_bytes(exact + b" ")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "large.json"
            output = Path(directory) / "output.b3leakage"
            source.write_bytes(exact + b" " * 100)
            with self.assertRaisesRegex(compiler.SourceLeakageProfileError, "256 KiB"):
                compiler.compile_profile(source, output)
            self.assertFalse(output.exists())
            self.assertEqual(source.stat().st_size, len(exact) + 100)

    def test_success_is_path_independent_and_receipt_hashes_published_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipts, outputs = [], []
            for index in range(2):
                source, output = root / f"input-{index}.json", root / f"output-{index}"
                source.write_bytes(PAIR_BYTES)
                receipts.append(compiler.compile_profile(source, output))
                outputs.append(output.read_bytes())
                self.assertEqual(source.read_bytes(), PAIR_BYTES)
            self.assertEqual(receipts[0], receipts[1])
            self.assertEqual(outputs[0], outputs[1])
            self.assertEqual(receipts[0]["compiled_sha256"], hashlib.sha256(outputs[0]).hexdigest())
            self.assertEqual(sorted(path.name for path in root.iterdir()),
                             ["input-0.json", "input-1.json", "output-0", "output-1"])

    def test_existing_files_input_aliases_directories_and_symlinks_survive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.json"
            source.write_bytes(PAIR_BYTES)
            existing = root / "existing"
            existing.write_bytes(b"sentinel")
            folder = root / "folder"
            folder.mkdir()
            link = root / "link"
            link.symlink_to(existing)
            dangling = root / "dangling"
            dangling.symlink_to(root / "absent-target")
            alias = root / "input-alias"
            alias.symlink_to(source)
            for output in (source, existing, folder, link, dangling, alias):
                with self.subTest(output=output.name), self.assertRaisesRegex(compiler.SourceLeakageProfileError, "already exists"):
                    compiler.compile_profile(source, output)
            self.assertEqual(source.read_bytes(), PAIR_BYTES)
            self.assertEqual(existing.read_bytes(), b"sentinel")
            self.assertTrue(folder.is_dir())
            self.assertTrue(link.is_symlink())
            self.assertTrue(dangling.is_symlink())
            self.assertFalse((root / "absent-target").exists())

    def test_invalid_input_does_not_create_output_or_change_existing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / "input.json", root / "output"
            source.write_bytes(b"{}")
            for existing in (False, True):
                if existing:
                    output.write_bytes(b"sentinel")
                with self.assertRaises(compiler.SourceLeakageProfileError):
                    compiler.compile_profile(source, output)
                self.assertEqual(source.read_bytes(), b"{}")
                self.assertEqual(output.read_bytes() if output.exists() else None,
                                 b"sentinel" if existing else None)
            self.assertEqual(sorted(path.name for path in root.iterdir()), ["input.json", "output"])

    def test_atomic_collision_preserves_racing_output_and_cleans_temporary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / "input.json", root / "output"
            source.write_bytes(PAIR_BYTES)
            original_link = os.link

            def race(candidate, target):
                self.assertEqual(Path(candidate).read_bytes(), compiler.compile_bytes(PAIR_BYTES)[0])
                output.write_bytes(b"racing sentinel")
                return original_link(candidate, target)

            with mock.patch.object(compiler.os, "link", side_effect=race):
                with self.assertRaisesRegex(compiler.SourceLeakageProfileError, "already exists"):
                    compiler.compile_profile(source, output)
            self.assertEqual(output.read_bytes(), b"racing sentinel")
            self.assertEqual(source.read_bytes(), PAIR_BYTES)
            self.assertEqual(sorted(path.name for path in root.iterdir()), ["input.json", "output"])

    def test_failed_flush_or_publication_leaves_no_partial_output(self):
        for operation in ("fsync", "link"):
            with self.subTest(operation=operation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source, output = root / "input.json", root / "output"
                source.write_bytes(PAIR_BYTES)
                with mock.patch.object(compiler.os, operation, side_effect=OSError("injected I/O failure")):
                    with self.assertRaisesRegex(OSError, "injected"):
                        compiler.compile_profile(source, output)
                self.assertFalse(output.exists())
                self.assertEqual(source.read_bytes(), PAIR_BYTES)
                self.assertEqual([path.name for path in root.iterdir()], ["input.json"])

    @unittest.skipUnless(hasattr(os, "mkfifo") and hasattr(os, "O_NONBLOCK"), "requires POSIX FIFO")
    def test_nonregular_input_is_rejected_without_waiting_for_writer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "fifo"
            os.mkfifo(source)
            process = subprocess.run(
                [sys.executable, "-B", str(ROOT / "tools" / "compile_source_leakage.py"),
                 "--input", str(source), "--output", str(root / "output")],
                capture_output=True, text=True, timeout=5,
            )
            self.assertEqual(process.returncode, 1)
            self.assertIn("regular file", process.stderr)
            self.assertFalse((root / "output").exists())

    def test_cli_success_receipt_and_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / "input.json", root / "output"
            source.write_bytes(PAIR_BYTES)
            command = [sys.executable, "-B", str(ROOT / "tools" / "compile_source_leakage.py")]
            arguments = ["--input", str(source), "--output", str(output)]
            success = subprocess.run(command + arguments, capture_output=True, text=True, timeout=5)
            self.assertEqual(success.returncode, 0, success.stderr)
            self.assertEqual(success.stderr, "")
            receipt = json.loads(success.stdout)
            self.assertEqual(receipt["input_sha256"], hashlib.sha256(PAIR_BYTES).hexdigest())
            self.assertEqual(receipt["compiled_sha256"], hashlib.sha256(output.read_bytes()).hexdigest())
            self.assertEqual(len(success.stdout.splitlines()), 1)
            for extra in ([], ["--input", str(source)], ["--unknown"], ["--output", str(root / "other")]):
                failure = subprocess.run(command + arguments + extra, capture_output=True, text=True, timeout=5)
                with self.subTest(extra=extra):
                    self.assertNotEqual(failure.returncode, 0)
                    self.assertEqual(failure.stdout, "")
                    self.assertNotIn("Traceback", failure.stderr)
            missing = subprocess.run(command + ["--input", str(root / "missing"), "--output", str(root / "absent")],
                                     capture_output=True, text=True, timeout=5)
            self.assertEqual(missing.returncode, 1)
            self.assertFalse((root / "absent").exists())
            self.assertFalse((root / "other").exists())
            self.assertEqual(output.read_bytes(), compiler.compile_bytes(PAIR_BYTES)[0])

    def test_schema_declares_exact_fixture_shapes_and_semantic_limits(self):
        schema = json.loads((ROOT / "data" / "source-leakage.schema.json").read_bytes())
        self.assertEqual(set(schema["required"]), set(PAIR))
        self.assertEqual(set(schema["properties"]), set(PAIR))
        self.assertFalse(schema["additionalProperties"])
        properties = schema["properties"]
        self.assertEqual(properties["edges"]["maxItems"], 728)
        self.assertFalse(properties["edges"]["items"]["additionalProperties"])
        self.assertFalse(properties["algorithm_reference"]["additionalProperties"])
        for raw in (PAIR_BYTES, IDENTITY_BYTES):
            fixture = json.loads(raw)
            for key, rules in properties.items():
                if "const" in rules:
                    self.assertEqual(fixture[key], rules["const"])
            for key, rules in properties["algorithm_reference"]["properties"].items():
                self.assertEqual(fixture["algorithm_reference"][key], rules["const"])
            self.assertIn("synthetic", fixture["description"].lower())
        self.assertIn("sequential binary64", schema["$comment"])


if __name__ == "__main__":
    unittest.main()
