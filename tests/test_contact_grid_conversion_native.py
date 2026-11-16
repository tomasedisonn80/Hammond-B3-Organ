#!/usr/bin/env python3
"""Independently replay every admitted conversion through the native grid.

The native probe is required through HAMMOND_CAUSAL_CONTACT_GRID_PROBE_EXECUTABLE;
missing configuration is a setup error, never a skip. Expected grid scalars are
rounded independently from the original admitted binary64 case. Exact edges and
all padded snapshot fields come from the existing independent completed-path
Fraction oracle, not the converter or C++ crossing helpers.

The probe exposes final snapshots and per-block counts. Causal prefix runs check
full state before endpoint commands and after explicit endpoint closure. They do
not pretend to expose an intermediate snapshot inside another native process or
short-buffer retry. The separate native lifecycle gate owns that API boundary.
"""

from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
import importlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import unittest


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "tests" / "reference")]
from contact_switching_io import parse_input
import contact_grid_conversion_cases as frozen
from causal_contact_grid_reference import evaluate_case


TICKS = 65536
TRAVEL = 1 << 48
MAX_NATIVE_BYTES = 2 * 1024 * 1024
MAX_RECEIPT_BYTES = 16 * 1024 * 1024
MANIFEST_PATH = ROOT / "data/contact-grid-conversion/v1/manifest.json"
CONTRACT_PATH = ROOT / "docs/CONTACT_GRID_CONVERSION_CONTRACT.md"
IMPLEMENTATION_PATHS = (
    "tools/contact_grid_conversion.py", "tools/convert_contact_grid.py",
    "tools/contact_switching_io.py", "tools/fractional_contact_reference.py",
)
WATCHED_PATHS = IMPLEMENTATION_PATHS + (
    "tests/test_contact_grid_conversion_native.py",
    "tests/reference/contact_grid_conversion_cases.py",
    "tests/reference/causal_contact_grid_reference.py",
    "data/contact-grid-conversion/v1/manifest.json",
    "docs/CONTACT_GRID_CONVERSION_CONTRACT.md",
    "docs/CAUSAL_CONTACT_GRID_CONTRACT.md",
    "tools/causal_contact_grid_probe.cpp",
    "src/research/CausalContactGrid.cpp",
    "include/hammond/research/CausalContactGrid.h",
)
OUTCOMES = {}
RUNS = []
SOURCE_BEFORE = {}
SOURCE_AFTER = {}
PROBE_IDENTITY = None


def digest_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def file_hash(path):
    return digest_bytes(Path(path).read_bytes())


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def exact_number(value):
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def native_tick(edge):
    value = edge["time"]
    return Fraction(value["tick"]) + Fraction(value["numerator"], value["denominator"])


def independent_grid(case):
    """Direct contract equations, with Fraction.__round__ nearest/even."""
    key_indices = {key.key_id: index for index, key in enumerate(case.keys)}
    keys = []
    for key in case.keys:
        keys.append({
            "press_units_per_tick": round(Fraction(TRAVEL, TICKS * case.sample_rate_hz)
                                          / Fraction.from_float(key.press_seconds)),
            "release_units_per_tick": round(Fraction(TRAVEL, TICKS * case.sample_rate_hz)
                                            / Fraction.from_float(key.release_seconds)),
            "contacts": [{"off": round(TRAVEL * Fraction.from_float(off)),
                          "on": round(TRAVEL * Fraction.from_float(on))}
                         for off, on in zip(key.off9, key.on9)],
        })
    ordered = sorted(enumerate(case.targets), key=lambda item: (
        Fraction(item[1].frame) + Fraction.from_float(item[1].fraction), item[0]))
    targets = [{"tick": round(TICKS * (Fraction(command.frame)
                                       + Fraction.from_float(command.fraction))),
                "key_index": key_indices[command.key_id],
                "position": round(TRAVEL * Fraction.from_float(command.target))}
               for _, command in ordered]
    return {"sample_rate_hz": case.sample_rate_hz, "frames": case.frames,
            "keys": keys, "targets": targets}


def independent_transport(grid, partitions):
    """Literal CGGRID1 grammar, independent of production transport helpers."""
    tokens = ["CGGRID1", str(grid["sample_rate_hz"]), str(len(grid["keys"])),
              str(grid["frames"]), str(len(grid["targets"])), str(len(partitions))]
    lines = [" ".join(tokens)]
    for key in grid["keys"]:
        fields = [key["press_units_per_tick"], key["release_units_per_tick"]]
        for contact in key["contacts"]:
            fields += [contact["off"], contact["on"]]
        lines.append(" ".join(str(value) for value in fields))
    lines += [" ".join(str(command[field]) for field in ("tick", "key_index", "position"))
              for command in grid["targets"]]
    if partitions:
        lines.append(" ".join(str(frames) for frames in partitions))
    return ("\n".join(lines) + "\n").encode("ascii")


def partition_variants(frames):
    if not frames:
        return [("empty", ())]
    irregular = []
    remaining = frames
    pattern = (3, 1, 11, 2, 7, 5)
    while remaining:
        count = min(remaining, pattern[len(irregular) % len(pattern)])
        irregular.append(count)
        remaining -= count
    choices = [("single", (frames,)), ("one-frame", (1,) * frames),
               ("irregular", tuple(irregular))]
    seen = set()
    return [(name, value) for name, value in choices
            if not (value in seen or seen.add(value))]


def checkpoints(grid):
    """All command-adjacent frame boundaries and fixed early/middle/end cuts."""
    frames = grid["frames"]
    cuts = {0, frames}
    if frames:
        cuts.update((1, frames // 2, frames - 1))
    for command in grid["targets"]:
        whole, remainder = divmod(command["tick"], TICKS)
        cuts.add(whole)
        if remainder:
            cuts.add(whole + 1)
    return sorted(cuts)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field: " + key)
        result[key] = value
    return result


def reject_number(value):
    raise ValueError("noninteger JSON number: " + value)


def typed_equal(test, actual, expected, path="report"):
    test.assertIs(type(actual), type(expected), path + ": type")
    if type(expected) is dict:
        test.assertEqual(set(actual), set(expected), path + ": fields")
        for key in expected:
            typed_equal(test, actual[key], expected[key], path + "." + key)
    elif type(expected) is list:
        test.assertEqual(len(actual), len(expected), path + ": length")
        for index, value in enumerate(expected):
            typed_equal(test, actual[index], value, f"{path}[{index}]")
    else:
        test.assertEqual(actual, expected, path)


def expected_report(grid, partitions):
    expected = evaluate_case(grid, close_observation=True)
    times = [native_tick(edge) for edge in expected["edges"]]
    offset = cursor = 0
    blocks = []
    for frames in partitions:
        cursor += frames
        previous = offset
        while offset < len(times) and times[offset] <= cursor * TICKS:
            offset += 1
        blocks.append({"frames": frames, "cursor_frames": cursor,
                       "edges_written": offset - previous})
    if cursor != grid["frames"] or offset != len(times):
        raise ValueError("test partition schedule does not cover the complete observation")
    return {"schema_version": 1, **expected, "blocks": blocks}


class ContactGridConversionNative(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global SOURCE_BEFORE, PROBE_IDENTITY
        configured = os.environ.get("HAMMOND_CAUSAL_CONTACT_GRID_PROBE_EXECUTABLE")
        if not configured:
            raise RuntimeError("native grid probe required: build hammond_causal_contact_grid_probe "
                               "and set HAMMOND_CAUSAL_CONTACT_GRID_PROBE_EXECUTABLE, or run CTest")
        cls.probe = Path(configured).resolve()
        if not cls.probe.is_file() or not os.access(cls.probe, os.X_OK):
            raise RuntimeError(f"configured native grid probe unavailable: {cls.probe}")
        SOURCE_BEFORE = {name: file_hash(ROOT / name) for name in WATCHED_PATHS}
        PROBE_IDENTITY = {"path": str(cls.probe), "sha256": file_hash(cls.probe),
                          "bytes": cls.probe.stat().st_size}
        cls.candidate = importlib.import_module("contact_grid_conversion")
        cls.implementation_hashes = {name: SOURCE_BEFORE[name] for name in IMPLEMENTATION_PATHS}
        cls.manifest = json.loads(MANIFEST_PATH.read_bytes())
        if file_hash(ROOT / cls.manifest["generator"]["path"]) != cls.manifest["generator"]["sha256"]:
            raise AssertionError("frozen generator hash changed")
        if file_hash(CONTRACT_PATH) != cls.manifest["contract"]["sha256"]:
            raise AssertionError("admitted contract hash changed")
        named = {row["name"]: row for row in cls.manifest["cases"]}
        cls.rows = []
        for row in frozen.cases():
            raw = frozen.canonical_input_bytes(row["input"])
            identity = named[row["name"]]
            if digest_bytes(raw) != identity["input_sha256"] or len(raw) != identity["input_bytes"]:
                raise AssertionError("frozen case bytes changed: " + row["name"])
            cls.rows.append((row["name"], "frozen", raw, row["expected_code_or_stage"]))
        for row in cls.manifest["original_fixtures"]:
            raw = (ROOT / row["path"]).read_bytes()
            if digest_bytes(raw) != row["sha256"] or len(raw) != row["bytes"]:
                raise AssertionError("original case bytes changed: " + row["path"])
            expected = "event_order" if Path(row["path"]).name.startswith("F09-") else "accepted"
            cls.rows.append((row["path"], "original", raw, expected))
        if len(cls.rows) != 71:
            raise AssertionError("all 35 frozen and 36 original inputs are mandatory")
        cls.accepted = []
        for name, family, raw, expected in cls.rows:
            document = parse_input(raw)
            record = {"name": name, "family": family, "input_sha256": digest_bytes(raw),
                      "input_bytes": len(raw), "expected": expected, "native_runs": [],
                      "checkpoints": []}
            try:
                result = cls.candidate.convert_document(document)
            except cls.candidate.ConversionRefusal as error:
                record.update(status="refused", code=error.code, path=error.path,
                              witness=error.witness)
            else:
                record.update(status="accepted", code="accepted")
                # A known refusal must never be forwarded to the native model,
                # even if a regressed candidate unexpectedly accepts it.
                if expected == "accepted":
                    cls.accepted.append((name, document, result))
            OUTCOMES[name] = record

    @classmethod
    def tearDownClass(cls):
        global SOURCE_AFTER
        SOURCE_AFTER = {name: file_hash(ROOT / name) for name in WATCHED_PATHS}
        if SOURCE_AFTER != SOURCE_BEFORE or file_hash(cls.probe) != PROBE_IDENTITY["sha256"]:
            raise AssertionError("qualification input changed during the native run")

    def run_native(self, name, grid, partitions, label, *, raw=None):
        if raw is None:
            raw = independent_transport(grid, partitions)
        self.assertLessEqual(len(raw), 131072)
        started = time.monotonic()
        record = {"case": name, "kind": label, "input_sha256": digest_bytes(raw),
                  "input_bytes": len(raw), "partitions": list(partitions)}
        RUNS.append(record)
        OUTCOMES[name]["native_runs"].append(len(RUNS) - 1)
        try:
            process = subprocess.run([str(self.probe)], input=raw, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, cwd=ROOT, timeout=10, check=False)
        except subprocess.TimeoutExpired:
            record.update(status="timeout", seconds=time.monotonic() - started)
            raise
        record.update(exit_code=process.returncode, seconds=time.monotonic() - started,
                      output_sha256=digest_bytes(process.stdout), output_bytes=len(process.stdout),
                      stderr=process.stderr.decode("utf-8", errors="replace")[:2048])
        self.assertEqual(process.returncode, 0, record)
        self.assertEqual(process.stderr, b"")
        self.assertLessEqual(len(process.stdout), MAX_NATIVE_BYTES)
        self.assertTrue(process.stdout.endswith(b"\n"))
        actual = json.loads(process.stdout, object_pairs_hook=unique_object,
                            parse_float=reject_number, parse_constant=reject_number)
        expected = expected_report(grid, partitions)
        typed_equal(self, actual, expected)
        record.update(status="passed", edges=len(actual["edges"]),
                      block_checkpoints=len(actual["blocks"]),
                      full_snapshot_sha256=digest_bytes(canonical_bytes(actual["snapshot"])))
        return actual

    def check_certificate_native_facts(self, certificate, native):
        occurrences = {}
        actual_edges = {}
        for edge in native["edges"]:
            identity = (edge["key_index"], edge["contact_index"], int(edge["closed_after"]))
            ordinal = occurrences.get(identity, 0)
            occurrences[identity] = ordinal + 1
            label = "E:" + ":".join(str(value) for value in (*identity, ordinal))
            actual_edges[label] = native_tick(edge) / TICKS
        expected_edges = {edge["label"]: exact_number(edge["grid_time"])
                          for edge in certificate["edges"]}
        self.assertEqual(actual_edges, expected_edges)
        active_count = native["snapshot"]["config"]["key_count"]
        self.assertEqual(len(certificate["final_keys"]), active_count)
        for index, final in enumerate(certificate["final_keys"]):
            state = native["snapshot"]["keys"][index]
            self.assertEqual(final["key_index"], index)
            self.assertEqual(exact_number(final["grid_position"]), Fraction(state["position"], TRAVEL))
            self.assertEqual(exact_number(final["grid_target"]), Fraction(state["target"], TRAVEL))
            typed_equal(self, state["closed"], final["closed9"])

    def exercise_complete(self, family):
        seen = 0
        for name, document, result in self.accepted:
            if OUTCOMES[name]["family"] != family:
                continue
            seen += 1
            with self.subTest(case=name):
                grid = independent_grid(document.case)
                typed_equal(self, result["grid_case"], grid, "independent-rounded-grid")
                payload = self.candidate.encode_certificate(
                    result, implementation_sha256=self.implementation_hashes,
                    contract_sha256=SOURCE_BEFORE["docs/CONTACT_GRID_CONVERSION_CONTRACT.md"])
                certificate = json.loads(payload, object_pairs_hook=unique_object,
                                         parse_float=reject_number, parse_constant=reject_number)
                self.assertEqual(payload, canonical_bytes(certificate))
                provenance = certificate.pop("provenance")
                typed_equal(self, certificate, result, "encoded-certificate")
                typed_equal(self, provenance, {
                    "implementation_sha256": self.implementation_hashes,
                    "contract_sha256": SOURCE_BEFORE["docs/CONTACT_GRID_CONVERSION_CONTRACT.md"],
                    "python_version": platform.python_version()}, "provenance")
                variants = partition_variants(grid["frames"])
                wire = independent_transport(grid, variants[0][1])
                self.assertEqual(certificate["transport"]["text"].encode("ascii"), wire)
                typed_equal(self, certificate["transport"], {
                    "format": "CGGRID1", "text": wire.decode("ascii"),
                    "sha256": digest_bytes(wire), "partitions": list(variants[0][1])})
                observed = []
                for index, (kind, partitions) in enumerate(variants):
                    native = self.run_native(name, grid, partitions, "complete-" + kind,
                                             raw=wire if index == 0 else None)
                    self.check_certificate_native_facts(certificate, native)
                    if observed:
                        typed_equal(self, native["edges"], observed[0]["edges"], "partition.edges")
                        typed_equal(self, native["snapshot"], observed[0]["snapshot"], "partition.snapshot")
                    observed.append(native)
                OUTCOMES[name].update(certificate_sha256=digest_bytes(payload),
                                      certificate_bytes=len(payload),
                                      certificate_transport_sha256=digest_bytes(wire),
                                      complete_native_result=observed[0])
        self.assertEqual(seen, 18 if family == "frozen" else 33)

    def test_all_35_frozen_dispositions_and_native_certificates(self):
        selected = [row for row in OUTCOMES.values() if row["family"] == "frozen"]
        self.assertEqual(len(selected), 35)
        for row in selected:
            with self.subTest(case=row["name"]):
                self.assertEqual(row["code"], row["expected"])
                if row["status"] == "refused":
                    self.assertEqual(row["native_runs"], [])
        self.exercise_complete("frozen")

    def test_all_36_original_dispositions_and_native_certificates(self):
        selected = [row for row in OUTCOMES.values() if row["family"] == "original"]
        self.assertEqual(len(selected), 36)
        self.assertEqual(sum(row["status"] == "refused" for row in selected), 3)
        for row in selected:
            with self.subTest(case=row["name"]):
                self.assertEqual(row["code"], row["expected"])
                if row["status"] == "refused":
                    self.assertEqual(row["native_runs"], [])
        self.exercise_complete("original")

    def test_causal_prefix_full_state_before_and_after_endpoint_commands(self):
        self.assertEqual(len(self.accepted), 51)
        for name, document, result in self.accepted:
            grid = independent_grid(document.case)
            full = evaluate_case(grid, close_observation=True)
            for cursor in checkpoints(grid):
                with self.subTest(case=name, cursor=cursor):
                    tick = cursor * TICKS
                    before = {**grid, "frames": cursor,
                              "targets": [command for command in grid["targets"] if command["tick"] < tick]}
                    parts = partition_variants(cursor)[-1][1]
                    native_before = self.run_native(name, before, parts, f"prefix-{cursor}-before")
                    active = evaluate_case(before, close_observation=False)
                    self.assertEqual(active["snapshot"]["phase"], "active" if cursor else "ready")
                    # The wire probe always closes; empty closure changes only
                    # phase. Every other exact state/configuration field is kept.
                    active["snapshot"]["phase"] = "closed"
                    typed_equal(self, native_before["snapshot"], active["snapshot"], "prefix-open-state")
                    through = [edge for edge in full["edges"] if native_tick(edge) <= tick]
                    typed_equal(self, native_before["edges"], through, "causal-prefix-edges")
                    record = {"cursor_frames": cursor, "before_snapshot": native_before["snapshot"],
                              "incoming_edges": len(native_before["edges"])}
                    at_endpoint = [command for command in grid["targets"] if command["tick"] == tick]
                    if at_endpoint:
                        closed = {**grid, "frames": cursor,
                                  "targets": [command for command in grid["targets"] if command["tick"] <= tick]}
                        native_after = self.run_native(name, closed, parts, f"prefix-{cursor}-with-closure")
                        typed_equal(self, native_after["edges"], native_before["edges"], "closure-no-new-edges")
                        for previous, after in zip(native_before["snapshot"]["keys"], native_after["snapshot"]["keys"]):
                            self.assertEqual(previous["position"], after["position"])
                            typed_equal(self, after["closed"], previous["closed"], "closure-contact-bits")
                        self.assertEqual(native_after["snapshot"]["command_count"],
                                         native_before["snapshot"]["command_count"] + len(at_endpoint))
                        record.update(endpoint_commands=len(at_endpoint), after_snapshot=native_after["snapshot"])
                    OUTCOMES[name]["checkpoints"].append(record)

    def test_independent_wire_and_complete_field_comparison_are_sensitive(self):
        grid = {"sample_rate_hz": 48000, "frames": 1,
                "keys": [{"press_units_per_tick": 3, "release_units_per_tick": 2,
                          "contacts": [{"off": 1, "on": 4} for _ in range(9)]}],
                "targets": [{"tick": 0, "key_index": 0, "position": 10},
                            {"tick": TICKS, "key_index": 0, "position": 0}]}
        self.assertEqual(independent_transport(grid, (1,)),
                         b"CGGRID1 48000 1 1 2 1\n3 2 1 4 1 4 1 4 1 4 1 4 1 4 1 4 1 4 1 4\n0 0 10\n65536 0 0\n1\n")
        expected = expected_report(grid, (1,))
        mutations = [(("snapshot", "keys", 0, "anchor_tick"), 0),
                     (("snapshot", "keys", 3, "closed", 8), True),
                     (("snapshot", "config", "keys", 3, "contacts", 8, "on"), 1),
                     (("snapshot", "command_count"), 2.0),
                     (("blocks", 0, "edges_written"), 8),
                     (("edges", 0, "time", "numerator"), 0)]
        for path, replacement in mutations:
            altered = copy.deepcopy(expected)
            target = altered
            for part in path[:-1]:
                target = target[part]
            target[path[-1]] = replacement
            with self.subTest(field=path), self.assertRaises(AssertionError):
                typed_equal(self, altered, expected)


def main():
    report_path = None
    original_arguments = list(sys.argv)
    if "--report" in sys.argv:
        index = sys.argv.index("--report")
        if index + 1 >= len(sys.argv):
            raise SystemExit("--report requires a path")
        report_path = Path(sys.argv[index + 1])
        del sys.argv[index:index + 2]
        if report_path.exists():
            raise SystemExit("refusing to overwrite retained native evidence: " + str(report_path))
    started = time.monotonic()
    result = unittest.main(exit=False).result
    if report_path is not None:
        complete = [row for row in RUNS if row["kind"].startswith("complete-")]
        report = {
            "schema_version": 1, "suite": "converted-contact-grid-native-v1",
            "evidence_class": "synthetic", "passed": result.wasSuccessful(),
            "cwd": str(ROOT), "command": [sys.executable, "-B", *original_arguments],
            "tests_run": result.testsRun, "failures": len(result.failures),
            "errors": len(result.errors), "skipped": len(result.skipped),
            "elapsed_seconds": time.monotonic() - started,
            "python": platform.python_version(), "platform": platform.platform(),
            "source_before": SOURCE_BEFORE, "source_after": SOURCE_AFTER,
            "sources_unchanged": SOURCE_BEFORE == SOURCE_AFTER,
            "probe": PROBE_IDENTITY, "input_count": len(OUTCOMES),
            "accepted_inputs": sum(row["status"] == "accepted" for row in OUTCOMES.values()),
            "refused_inputs": sum(row["status"] == "refused" for row in OUTCOMES.values()),
            "native_processes": len(RUNS), "complete_partition_processes": len(complete),
            "prefix_processes": len(RUNS) - len(complete),
            "native_block_count_checks": sum(row.get("block_checkpoints", 0) for row in RUNS),
            "full_native_snapshots_compared": sum(row.get("status") == "passed" for row in RUNS),
            "outcomes": list(OUTCOMES.values()), "runs": RUNS,
            "limits": "Finite converted synthetic trajectories only. Prefix probes always close; "
                      "only phase is normalized for their pre-closure oracle comparison. No native "
                      "short-buffer retry control is exposed by CGGRID1. Existing lifecycle gates "
                      "retain that separate scope. No audio, physical, callback or live integration claim.",
        }
        encoded = json.dumps(report, indent=2, sort_keys=True, allow_nan=False).encode("utf-8") + b"\n"
        if len(encoded) > MAX_RECEIPT_BYTES:
            raise SystemExit("native evidence exceeds the 16 MiB receipt limit")
        report_path.write_bytes(encoded)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
