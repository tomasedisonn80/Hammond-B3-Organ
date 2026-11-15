#!/usr/bin/env python3
"""Actual author compiler -> native loader/preparation/process qualification.

Build hammond_source_leakage_probe, then run through CTest or set
HAMMOND_SOURCE_LEAKAGE_PROBE_EXECUTABLE to that exact executable. Missing native
inputs fail setup; the suite never substitutes a Python parser or skips native
execution. Expected coefficients and rational frame algebra do not import the
compiler or a production numerical implementation.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "tools/compile_source_leakage.py"
ATLAS_SHA = "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769"
MODEL = "static-source-leakage-v1"
BOUNDARY = "normalized-generator-precontact-v1"
PAIR_EDGES = [(25, 37, 1 / 16), (37, 25, -1 / 32)]
MAX_BYTES = 128 * 1024


def author_bytes(edges, profile_id="synthetic-roundtrip-v1"):
    return (json.dumps({
        "schema_version": 1, "profile_id": profile_id, "model": MODEL,
        "evidence_status": "synthetic", "coefficient_origin": "synthetic-fixture",
        "boundary": BOUNDARY, "units": "normalized-amplitude-ratio",
        "source_content": "excludes-leakage", "source_count": 91,
        "algorithm_reference": {
            "document": "Hammond_B3_Leslie_Research_Atlas_500pp.pdf",
            "sha256": ATLAS_SHA, "pdf_pages": [79, 80, 81, 82, 83, 84],
        },
        "description": "Independent synthetic data-path fixture; no measured coupling.",
        "edges": [{"destination": d, "source": s, "gain": g} for d, s, g in edges],
    }, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def native_bytes(edges, digest="0" * 64):
    # Independent grammar fixture, used when intentionally invalid coefficients
    # must reach the native loader without being admitted by the compiler first.
    text = (
        "B3LEAKAGE1\nmodel static-source-leakage-v1\n"
        "profile_id synthetic-native-fixture-v1\nevidence_status synthetic\n"
        "boundary normalized-generator-precontact-v1\nsource_content excludes-leakage\n"
        f"authoring_sha256 {digest}\nsource_count 91\nedge_count {len(edges)}\n"
    )
    for destination, source, gain in edges:
        text += f"edge destination {destination} source {source} gain {gain:.17g}\n"
    return (text + "end\n").encode("ascii")


def binary64(value):
    return struct.pack(">d", value)


class SourceLeakageRoundTrip(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.environ.get("HAMMOND_SOURCE_LEAKAGE_PROBE_EXECUTABLE")
        if not value:
            raise RuntimeError("Build hammond_source_leakage_probe and set "
                               "HAMMOND_SOURCE_LEAKAGE_PROBE_EXECUTABLE or run CTest")
        cls.probe = Path(value).resolve()
        if not cls.probe.is_file() or not os.access(cls.probe, os.X_OK):
            raise RuntimeError(f"Exact configured native probe is unavailable: {cls.probe}")
        if not COMPILER.is_file():
            raise RuntimeError(f"Source leakage compiler is unavailable: {COMPILER}")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-leakage-roundtrip-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.serial = 0

    def invoke(self, *arguments, env=None):
        return subprocess.run([str(self.probe), *map(str, arguments)], input=b"",
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              cwd=self.work, env=env, timeout=10, check=False)

    def rejected(self, *arguments):
        result = self.invoke(*arguments)
        self.assertEqual(result.returncode, 1, result.stderr.decode(errors="replace"))
        self.assertEqual(result.stdout, b"", "a rejected request emitted partial JSON")
        self.assertTrue(result.stderr.startswith(b"hammond_source_leakage_probe:"))
        return result

    def compile(self, raw, expect_success=True):
        self.serial += 1
        source = self.work / f"author {self.serial} Ω é 漢字.json"
        output = self.work / f"compiled {self.serial} Ω é 漢字.b3l"
        source.write_bytes(raw)
        result = subprocess.run(
            [sys.executable, "-B", str(COMPILER), "--input", str(source),
             "--output", str(output)], input=b"", stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, cwd=self.work, timeout=10, check=False,
        )
        self.assertEqual(source.read_bytes(), raw)
        if not expect_success:
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b"")
            self.assertFalse(output.exists())
            self.assertNotIn(b"Traceback", result.stderr)
            return None
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.assertEqual(result.stderr, b"")
        receipt = json.loads(result.stdout, parse_constant=self.fail)
        compiled = output.read_bytes()
        self.assertEqual(receipt["input_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(receipt["compiled_sha256"], hashlib.sha256(compiled).hexdigest())
        self.assertEqual(receipt["compiled_bytes"], len(compiled))
        return output, receipt

    def inspect(self, path):
        original = path.read_bytes()
        result = self.invoke("--input", path)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.assertEqual(result.stderr, b"")
        self.assertEqual(path.read_bytes(), original)
        self.assertLessEqual(len(result.stdout), MAX_BYTES)
        self.assertEqual(len(result.stdout.splitlines()), 1)
        self.assertTrue(result.stdout.endswith(b"\n"))
        record = json.loads(result.stdout, parse_constant=self.fail)
        self.assertEqual(record["schema_version"], 1)
        self.assertEqual(record["probe_id"], "source-leakage-profile-probe-v1")
        self.assertEqual(record["status"], "ok")
        self.assertEqual(record["model"], MODEL)
        self.assertEqual(record["evidence_status"], "synthetic")
        self.assertEqual(record["boundary"], BOUNDARY)
        self.assertEqual(record["source_content"], "excludes-leakage")
        self.assertEqual(record["authoring_digest_verification"], "file-supplied-unverified")
        self.assertEqual(record["source_count"], 91)
        return record, result.stdout

    def algebra(self, record, edges):
        canonical = sorted(edges)
        self.assertEqual(record["edge_count"], len(canonical))
        self.assertEqual(len(record["edges"]), len(canonical))
        for actual, (destination, source, gain) in zip(record["edges"], canonical):
            self.assertEqual(set(actual), {"destination", "source", "gain"})
            self.assertEqual((actual["destination"], actual["source"]), (destination, source))
            self.assertEqual(binary64(actual["gain"]), binary64(gain))
        row_sums = [0.0] * 91
        for destination, _source, gain in canonical:
            row_sums[destination - 1] = row_sums[destination - 1] + abs(gain)
        self.assertEqual(record["rows"], [
            {"destination": index + 1, "absolute_gain_sum": value}
            for index, value in enumerate(row_sums)
        ])
        self.assertEqual(binary64(record["maximum_row_absolute_gain_sum"]),
                         binary64(max(row_sums)))
        self.assertEqual(record["frame_id"], "dyadic-permuted-ramp-v1")
        inputs = [Fraction((37 * tone) % 129 - 64, 64) for tone in range(1, 92)]
        self.assertEqual(record["input_frame"], list(map(float, inputs)))
        # Exact rational dot products use original-frame inputs. This reference
        # does not repeat sparse binary64 product/addition rounding.
        expected = inputs.copy()
        for destination, source, gain in edges:
            expected[destination - 1] += Fraction(gain) * inputs[source - 1]
        self.assertEqual(len(record["output_frame"]), 91)
        for actual, exact in zip(record["output_frame"], expected):
            reference = float(exact)
            self.assertTrue(math.isfinite(actual))
            self.assertLessEqual(abs(actual - reference),
                                 32 * sys.float_info.epsilon * max(1, abs(reference)))

    def test_shipped_pair_and_identity_through_real_tools(self):
        fixtures = (("synthetic-pair-demo-v1", PAIR_EDGES),
                    ("synthetic-identity-v1", []))
        for profile_id, edges in fixtures:
            with self.subTest(profile_id=profile_id):
                raw = (ROOT / "data/source-leakage" / f"{profile_id}.json").read_bytes()
                path, receipt = self.compile(raw)
                record, _ = self.inspect(path)
                self.assertEqual(record["profile_id"], profile_id)
                self.assertEqual(record["authoring_sha256"], receipt["input_sha256"])
                self.assertEqual(record["edge_count"], receipt["edge_count"])
                self.assertEqual(record["maximum_row_absolute_gain_sum"],
                                 receipt["maximum_row_absolute_gain_sum"])
                self.algebra(record, edges)
                if edges:
                    self.assertEqual(record["output_frame"][24], -657 / 1024)
                    self.assertEqual(record["output_frame"][36], 261 / 1024)
                else:
                    self.assertEqual(record["output_frame"], record["input_frame"])

    def test_maximum_capacity_shuffled_signed_cyclic_graph(self):
        edges = [(destination, (destination + offset - 1) % 91 + 1,
                  (-1 if offset % 2 else 1) / 16)
                 for destination in range(1, 92) for offset in range(1, 9)]
        random.Random(42731).shuffle(edges)
        path, receipt = self.compile(author_bytes(edges))
        record, _ = self.inspect(path)
        self.algebra(record, edges)
        self.assertEqual(record["edge_count"], 728)
        self.assertEqual(record["maximum_row_absolute_gain_sum"], 0.5)
        self.assertEqual(receipt["maximum_row_absolute_gain_sum"], 0.5)

    def test_representable_subnormal_and_normal_boundary_coefficients(self):
        minimum_normal = sys.float_info.min
        gains = [math.ulp(0.0), -math.ulp(0.0),
                 math.nextafter(minimum_normal, 0.0),
                 -math.nextafter(minimum_normal, 0.0),
                 minimum_normal, math.nextafter(minimum_normal, math.inf)]
        edges = [(index + 1, 91, gain) for index, gain in enumerate(gains)]
        path, _ = self.compile(author_bytes(edges))
        record, _ = self.inspect(path)
        self.algebra(record, edges)
        self.assertEqual(binary64(record["edges"][0]["gain"]), binary64(math.ulp(0.0)))

    def test_frozen_sequential_rounding_agreement_and_rejection(self):
        tiny = 2.0 ** -56
        good = [(91, source, gain) for source, gain in enumerate(
            [0.25] + [tiny] * 6 + [0.25], start=1)]
        bad = [(91, source, gain) for source, gain in enumerate(
            [tiny] * 6 + [0.25, 0.25], start=1)]
        random.Random(947).shuffle(good)
        path, receipt = self.compile(author_bytes(good))
        record, _ = self.inspect(path)
        self.algebra(record, good)
        self.assertEqual(record["maximum_row_absolute_gain_sum"], 0.5)
        self.assertEqual(receipt["maximum_row_absolute_gain_sum"], 0.5)
        self.compile(author_bytes(list(reversed(bad))), expect_success=False)
        native = self.work / "rejected rounded row.b3l"
        native.write_bytes(native_bytes(bad))
        self.rejected("--input", native)
        self.assertEqual(native.read_bytes(), native_bytes(bad))

    def test_author_byte_provenance_does_not_change_canonical_arithmetic(self):
        first, _ = self.compile(author_bytes(PAIR_EDGES))
        second_raw = b" \n" + author_bytes(list(reversed(PAIR_EDGES))) + b"\t"
        second, _ = self.compile(second_raw)
        a, _ = self.inspect(first)
        b, _ = self.inspect(second)
        self.assertNotEqual(a["authoring_sha256"], b["authoring_sha256"])
        self.assertEqual(b["authoring_sha256"], hashlib.sha256(second_raw).hexdigest())
        self.assertNotEqual(first.read_bytes(), second.read_bytes())
        del a["authoring_sha256"]
        del b["authoring_sha256"]
        self.assertEqual(a, b)

    def test_forged_digest_remains_explicitly_unverified(self):
        path, _ = self.compile(author_bytes(PAIR_EDGES))
        old = hashlib.sha256(author_bytes(PAIR_EDGES)).hexdigest().encode()
        changed = path.read_bytes().replace(old, b"a" * 64)
        path.write_bytes(changed)
        record, _ = self.inspect(path)
        self.assertEqual(record["authoring_sha256"], "a" * 64)
        self.assertEqual(record["authoring_digest_verification"], "file-supplied-unverified")
        self.algebra(record, PAIR_EDGES)

    def test_native_rejects_malformed_or_noncanonical_compiled_data(self):
        original = native_bytes(PAIR_EDGES)
        mutations = [
            original.replace(b"B3LEAKAGE1", b"B3LEAKAGE2"),
            original.replace(MODEL.encode(), b"unknown-model"),
            original.replace(b"profile_id synthetic-", b"profile_id Synthetic-"),
            original.replace(b"evidence_status synthetic", b"evidence_status measured"),
            original.replace(BOUNDARY.encode(), b"unknown-boundary"),
            original.replace(b"excludes-leakage", b"includes-leakage"),
            original.replace(b"0" * 64, b"A" * 64),
            original.replace(b"source_count 91", b"source_count 90"),
            original.replace(b"edge_count 2", b"edge_count 1"),
            original.replace(b"edge_count 2", b"edge_count 3"),
            original.replace(b"gain 0.0625", b"gain 0"),
            original.replace(b"gain 0.0625", b"gain 1e-4000"),
            original.replace(b"gain 0.0625", b"gain 1e4000"),
            original.replace(b"gain 0.0625", b"gain 0x1p-4"),
            original.replace(b"gain 0.0625", b"gain NaN"),
            original.replace(b"destination 25", b"destination 4294967297"),
            original.replace(b"source 37", b"source 25"),
            original.replace(b"source 37", b"source -37"),
            original.replace(b"source_count", b"unknown_count"),
            original[:-4], original + b"unexpected", original + b"\0",
            original + "é".encode(), native_bytes(list(reversed(PAIR_EDGES))),
            native_bytes([PAIR_EDGES[0], PAIR_EDGES[0]]),
            native_bytes([(91, source, 1 / 32) for source in range(1, 10)]),
        ]
        path = self.work / "invalid native.b3l"
        for index, raw in enumerate(mutations):
            with self.subTest(index=index):
                path.write_bytes(raw)
                self.rejected("--input", path)
                self.assertEqual(path.read_bytes(), raw)

    def test_inclusive_byte_limit_and_crlf_whitespace(self):
        original = native_bytes(PAIR_EDGES)
        path = self.work / "bounded profile.b3l"
        path.write_bytes(original.replace(b"\n", b"\r\n") + b"\t\v\f\r\n ")
        record, _ = self.inspect(path)
        self.algebra(record, PAIR_EDGES)
        exact = original + b" " * (MAX_BYTES - len(original))
        path.write_bytes(exact)
        self.inspect(path)
        path.write_bytes(exact + b" ")
        self.rejected("--input", path)
        self.assertEqual(path.read_bytes(), exact + b" ")

    def test_cli_paths_repetition_and_deterministic_output(self):
        path, _ = self.compile(author_bytes(PAIR_EDGES))
        original = path.read_bytes()
        record, first = self.inspect(path)
        _, second = self.inspect(path)
        self.assertEqual(first, second)
        self.algebra(record, PAIR_EDGES)
        help_result = self.invoke("--help")
        self.assertEqual(help_result.returncode, 0)
        self.assertEqual(help_result.stderr, b"")
        self.assertIn(b"file-supplied and unverified", help_result.stdout)
        arguments = [(), ("--input",), ("--input", ""), ("--unknown", path),
                     ("--input", path, "--input", path), ("--help", "--input", path),
                     ("--input", self.work), ("--input", self.work / "absent"),
                     ("--input", "á" * 16385)]
        for args in arguments:
            with self.subTest(arguments=str(args)[:120]):
                self.rejected(*args)
        if hasattr(os, "mkfifo"):
            fifo = self.work / "fifo"
            os.mkfifo(fifo)
            self.rejected("--input", fifo)
        if os.name != "nt":
            alias = self.work / "input alias.b3l"
            alias.symlink_to(path)
            _, aliased = self.inspect(alias)
            self.assertEqual(first, aliased)
        self.assertEqual(path.read_bytes(), original)

    @unittest.skipUnless(os.name == "posix" and Path("/dev/full").exists(),
                         "actual /dev/full write-failure check requires POSIX")
    def test_stdout_failure_is_reported(self):
        # /dev/full is an actual failed write, independent of pipe timing.
        path, _ = self.compile(author_bytes(PAIR_EDGES))
        with open("/dev/full", "wb", buffering=0) as sink:
            result = subprocess.run([str(self.probe), "--input", str(path)],
                                    stdout=sink, stderr=subprocess.PIPE,
                                    cwd=self.work, timeout=10, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"Cannot write", result.stderr)


if __name__ == "__main__":
    unittest.main()
