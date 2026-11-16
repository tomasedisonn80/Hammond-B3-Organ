#!/usr/bin/env python3
"""Independent exact numerical acceptance for contact-grid conversion v1.

Run from the repository root: python3 -B tests/test_contact_grid_conversion.py -v
Optionally retain a source-bound result with --report PATH.  All 35 pre-frozen
cases and all 36 original inputs are mandatory; rejected originals are retained.
Candidate code is imported only at the public convert/encode boundary. Expected
facts come from the separate epoch/contact-major oracle, never candidate helpers.
"""

from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
import importlib
import json
from pathlib import Path
import re
import sys
import time
import unittest


sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO / "tools"), str(REPO / "tests" / "reference")]
from contact_switching_io import parse_input
import contact_grid_conversion_cases as frozen
import contact_grid_conversion_oracle as oracle


MANIFEST_PATH = REPO / "data/contact-grid-conversion/v1/manifest.json"
MANIFEST = json.loads(MANIFEST_PATH.read_bytes())
CONTRACT_PATH = REPO / "docs/CONTACT_GRID_CONVERSION_CONTRACT.md"
IMPLEMENTATION_PATHS = (
    "tools/contact_grid_conversion.py", "tools/convert_contact_grid.py",
    "tools/contact_switching_io.py", "tools/fractional_contact_reference.py",
)
ROOT_FIELDS = set((
    "schema_version conversion_id status evidence_class source_model_id target_model_id "
    "audio_accuracy fixture_id input_sha256 input_bytes grid_case sidecar scalar_errors "
    "edges arrivals commands final_keys preorder position_samples root_bounds summary transport"
).split())
OUTCOMES = []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def implementation_hashes():
    return {path: sha(REPO / path) for path in IMPLEMENTATION_PATHS}


def admitted(row):
    return parse_input(frozen.canonical_input_bytes(row["input"]))


def named(name):
    return next(row for row in frozen.cases() if row["name"] == name)


def scalar_path(root, path):
    for name, index in re.findall(r"([A-Za-z_]+)|\[(\d+)\]", path):
        root = root[name] if name else root[int(index)]
    return root


def typed_equal(test, expected, actual, path="result"):
    """Python considers bool==int; certificates must retain the actual types."""
    test.assertIs(type(actual), type(expected), path)
    if type(expected) is dict:
        test.assertEqual(set(actual), set(expected), path)
        for key in expected:
            typed_equal(test, expected[key], actual[key], path + "." + key)
    elif type(expected) is list:
        test.assertEqual(len(actual), len(expected), path)
        for index, (left, right) in enumerate(zip(expected, actual)):
            typed_equal(test, left, right, f"{path}[{index}]")
    else:
        test.assertEqual(actual, expected, path)


def check_rationals(test, value):
    if type(value) is dict:
        if set(value) == {"numerator", "denominator"}:
            actual = oracle.decode_rational(value)
            test.assertLessEqual(abs(actual.numerator).bit_length(), 4096)
            test.assertLessEqual(actual.denominator.bit_length(), 4096)
        else:
            for child in value.values():
                check_rationals(test, child)
    elif type(value) is list:
        for child in value:
            check_rationals(test, child)


class OracleSelfTests(unittest.TestCase):
    """Hand-computable checks that do not load the candidate module."""

    def test_nearest_even_both_parities_and_neighbors(self):
        for lower in (0, 1, 2, 3, (1 << 32) - 2, (1 << 48) - 1):
            for delta, expected in ((Fraction(1, 3), lower),
                                    (Fraction(1, 2), lower + (lower % 2)),
                                    (Fraction(2, 3), lower + 1),
                                    (Fraction(0), lower)):
                with self.subTest(lower=lower, delta=delta):
                    self.assertEqual(oracle.nearest_even(Fraction(lower) + delta), expected)

    def test_finished_epochs_resolve_incoming_contact_and_positive_arrivals(self):
        key = oracle.KeyModel(Fraction(1, 2), Fraction(1, 4),
                              (Fraction(1, 4),) * 9, (Fraction(1, 2),) * 9)
        # At t=1 the incoming makes happen first. A transient target equal to
        # current position has no duration and therefore creates no arrival.
        commands = [oracle.Command(Fraction(t), n, 0, Fraction(value)) for n, (t, value) in enumerate((
            (0, 1), (Fraction(1, 2), 1), (1, Fraction(1, 2)), (1, 1), (2, 0)))]
        result = oracle.reconstruct(6, [key], commands)
        self.assertEqual(len(result.edges), 18)
        self.assertEqual({label: root.time for label, root in result.arrivals.items()},
                         {"A:0:1:0": Fraction(2), "A:0:-1:0": Fraction(6)})
        for contact in range(9):
            make = result.edges[f"E:0:{contact}:1:0"]
            release = result.edges[f"E:0:{contact}:0:0"]
            self.assertEqual((make.time, make.anchor_time, make.anchor_position), (1, 0, 0))
            self.assertEqual((release.time, release.anchor_time, release.anchor_position), (5, 2, 1))
        self.assertEqual(result.arrivals["A:0:1:0"].anchor_time, 1)
        self.assertEqual(result.arrivals["A:0:1:0"].anchor_position, Fraction(1, 2))
        self.assertEqual(result.observations[1]["repeated"], True)
        self.assertEqual(result.observations[2]["after"], 0)
        self.assertEqual(result.observations[3]["after"], 1)
        self.assertEqual(result.paths[0].closed, (False,) * 9)
        self.assertEqual(result.paths[0].final_position, 0)

    def test_partial_hold_and_incomplete_reversal_preserve_hysteresis(self):
        key = oracle.KeyModel(Fraction(1, 4), Fraction(1, 8),
                              (Fraction(1, 4),) * 9, (Fraction(3, 4),) * 9)
        commands = [oracle.Command(Fraction(t), n, 0, Fraction(value)) for n, (t, value) in enumerate((
            (0, 1), (5, Fraction(1, 2)), (10, Fraction(5, 8)), (12, 0)))]
        result = oracle.reconstruct(17, [key], commands)
        self.assertEqual(result.edges["E:0:0:1:0"].time, 3)
        self.assertEqual(result.edges["E:0:0:0:0"].time, 15)
        self.assertEqual(result.paths[0].at(Fraction(10)), Fraction(1, 2))
        self.assertEqual(result.paths[0].at(Fraction(11)), Fraction(5, 8))
        self.assertEqual(len(result.arrivals), 4)

    def test_empty_epoch_keeps_boundaries_and_all_closure_commands(self):
        result = oracle.evaluate_case(admitted(named("maximum-command-noops")).case)
        self.assertEqual(len(result["commands"]), 512)
        self.assertEqual(len(result["preorder"]), 1)
        self.assertEqual(len(result["preorder"][0]), 514)
        self.assertEqual(result["edges"], [])
        self.assertEqual(result["arrivals"], [])
        self.assertEqual(result["transport"]["partitions"], [])
        self.assertEqual(result["summary"]["max_root_error"], oracle.rational(0))
        self.assertIsNone(result["summary"]["root_witness"])

    def test_rational_decoder_does_not_accept_lossy_or_noncanonical_forms(self):
        for value in ({"numerator": "2", "denominator": "4"},
                      {"numerator": "-0", "denominator": "1"},
                      {"numerator": "+1", "denominator": "2"},
                      {"numerator": "01", "denominator": "2"},
                      {"numerator": "1", "denominator": "-2"},
                      {"numerator": True, "denominator": "1"},
                      {"numerator": "1", "denominator": "0"}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                oracle.decode_rational(value)


class FrozenEvidenceTests(unittest.TestCase):
    def test_manifest_generator_contract_and_all_input_identities_are_unchanged(self):
        self.assertEqual(MANIFEST["case_count"], 35)
        self.assertEqual(MANIFEST["original_fixture_count"], 36)
        self.assertEqual(sha(REPO / MANIFEST["generator"]["path"]), MANIFEST["generator"]["sha256"])
        self.assertEqual(sha(REPO / MANIFEST["contract"]["path"]), MANIFEST["contract"]["sha256"])
        original_manifest = MANIFEST["original_fixture_manifest"]
        self.assertEqual(sha(REPO / original_manifest["path"]), original_manifest["sha256"])
        manifest_cases = {row["name"]: row for row in MANIFEST["cases"]}
        self.assertEqual(set(manifest_cases), {row["name"] for row in frozen.cases()})
        for row in frozen.cases():
            with self.subTest(case=row["name"]):
                expected = manifest_cases[row["name"]]
                raw = frozen.canonical_input_bytes(row["input"])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), expected["input_sha256"])
                self.assertEqual(len(raw), expected["input_bytes"])
                self.assertEqual(row["expected_status"], expected["expected_status"])
                self.assertEqual(row["expected_code_or_stage"], expected["expected_code_or_stage"])
                parse_input(raw)
        for row in MANIFEST["original_fixtures"]:
            with self.subTest(original=row["path"]):
                raw = (REPO / row["path"]).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])
                self.assertEqual(len(raw), row["bytes"])
                parse_input(raw)

    def test_all_35_pre_frozen_dispositions_match_independent_oracle(self):
        dispositions = []
        for row in frozen.cases():
            with self.subTest(case=row["name"]):
                try:
                    facts = oracle.evaluate_case(admitted(row).case)
                    code = "accepted"
                except oracle.OracleRefusal as failure:
                    code = failure.code
                dispositions.append(code)
                self.assertEqual(code, row["expected_code_or_stage"])
                if code == "accepted":
                    for path, value in row.get("expected_grid_fields", {}).items():
                        self.assertEqual(scalar_path(facts["grid_case"], path), value, path)
        self.assertEqual(dispositions.count("accepted"), 18)
        self.assertEqual(len(dispositions) - dispositions.count("accepted"), 17)

    def test_pre_frozen_exact_position_and_root_witnesses(self):
        below = oracle.evaluate_case(admitted(named("position-budget-below")).case)
        witnesses = MANIFEST["independent_exact_witnesses"]
        self.assertEqual(oracle.decode_rational(below["summary"]["max_position_error"]),
                         Fraction(witnesses["position_budget_below"]["sup_error"]))
        # The above-budget refusal occurs at its first excess. Independently
        # reconstruct the full paths to check the pre-frozen maximum at t=4.
        case = admitted(named("position-budget-above")).case
        source_keys, grid_keys, source_commands, grid_commands, _, _ = oracle.convert_scalars(case)
        source = oracle.reconstruct(case.frames, source_keys, source_commands)
        grid = oracle.reconstruct(case.frames, grid_keys, grid_commands)
        self.assertEqual(abs(grid.paths[0].at(Fraction(4)) - source.paths[0].at(Fraction(4))),
                         Fraction(witnesses["position_budget_above"]["sup_error"]))
        with self.assertRaises(oracle.OracleRefusal) as caught:
            oracle.evaluate_case(admitted(named("root-budget-slow-travel")).case)
        self.assertEqual(caught.exception.code, "root_budget")
        self.assertEqual(oracle.decode_rational(caught.exception.witness["error"]),
                         Fraction(witnesses["slow_root"]["error_frames"]))
        with self.assertRaises(oracle.OracleRefusal) as caught:
            oracle.evaluate_case(admitted(named("reviewed-f09-equality")).case)
        witness = caught.exception.witness
        self.assertEqual(witness["labels"], ["C:2", "E:0:4:1:0"])
        self.assertEqual(oracle.decode_rational(witness["source_times"][1]) -
                         oracle.decode_rational(witness["grid_times"][1]),
                         Fraction(witnesses["f09_equality_loss_frames"]))


class CandidateBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # This is the only candidate import. No candidate helper supplies an
        # expected number, path, crossing, command observation or event order.
        cls.candidate = importlib.import_module("contact_grid_conversion")
        cls.hashes = implementation_hashes()
        cls.contract_hash = sha(CONTRACT_PATH)

    def assertAccepted(self, document, expected, actual):
        self.assertEqual(set(actual), ROOT_FIELDS)
        metadata = {
            "schema_version": 1, "conversion_id": "fractional-to-contact-grid-rne-v1",
            "status": "accepted", "evidence_class": "synthetic",
            "source_model_id": "fractional-contact-reference-v1", "target_model_id": "causal-contact-grid-v1",
            "audio_accuracy": "unqualified", "fixture_id": document.fixture_id,
            "input_sha256": document.input_sha256, "input_bytes": document.input_size_bytes,
        }
        for key, value in metadata.items():
            typed_equal(self, value, actual[key], key)
        for key, value in expected.items():
            other = actual[key]
            if key == "summary":
                self.assertEqual(set(other), set(value) | {"work_units"})
                self.assertIs(type(other["work_units"]), int)
                self.assertGreater(other["work_units"], 0)
                self.assertLessEqual(other["work_units"], 1_000_000)
                other = {name: data for name, data in other.items() if name != "work_units"}
            typed_equal(self, value, other, key)
        check_rationals(self, actual)
        before = copy.deepcopy(actual)
        encoded = self.candidate.encode_certificate(actual, implementation_sha256=self.hashes,
                                                     contract_sha256=self.contract_hash)
        self.assertIs(type(encoded), bytes)
        self.assertLessEqual(len(encoded), 32 * 1024 * 1024)
        self.assertEqual(encoded[-1:], b"\n")
        self.assertEqual(encoded.count(b"\n"), 1)
        payload = json.loads(encoded)
        provenance = payload.pop("provenance")
        typed_equal(self, actual, payload)
        typed_equal(self, before, actual, "pure encoder input")
        self.assertEqual(provenance["implementation_sha256"], self.hashes)
        self.assertEqual(provenance["contract_sha256"], self.contract_hash)
        self.assertIs(type(provenance["python_version"]), str)
        self.assertEqual(len(provenance), 3)
        whole = {**payload, "provenance": provenance}
        self.assertEqual(encoded, (json.dumps(whole, sort_keys=True, separators=(",", ":"),
                                             ensure_ascii=True, allow_nan=False) + "\n").encode("ascii"))
        return len(encoded)

    def exercise(self, name, raw, *, family, expected_stage=None):
        document = parse_input(raw)
        started = time.monotonic()
        try:
            expected = oracle.evaluate_case(document.case)
            oracle_code = "accepted"
        except oracle.OracleRefusal as failure:
            expected = None
            oracle_code = failure.code
        record = {"name": name, "family": family, "input_sha256": document.input_sha256,
                  "input_bytes": len(raw), "oracle": oracle_code}
        try:
            actual = self.candidate.convert_document(document)
            record["candidate"] = "accepted"
            self.assertEqual(oracle_code, "accepted", name)
            record["certificate_bytes"] = self.assertAccepted(document, expected, actual)
            record["counts"] = {field: len(actual[field]) for field in
                                ("edges", "arrivals", "commands", "position_samples", "root_bounds")}
            record["summary"] = actual["summary"]
        except self.candidate.ConversionRefusal as failure:
            record["candidate"] = failure.code
            record["refusal_path"] = failure.path
            record["witness"] = failure.witness
            self.assertEqual(failure.code, oracle_code, name)
            self.assertNotEqual(oracle_code, "accepted", name)
            self.assertIs(type(failure.path), str)
            self.assertTrue(failure.path)
            self.assertIs(type(failure.witness), dict)
            check_rationals(self, failure.witness)
            self.assertLessEqual(len(json.dumps({"code": failure.code, "path": failure.path,
                                                 "witness": failure.witness}, allow_nan=False).encode()), 8192)
        finally:
            record["elapsed_seconds"] = time.monotonic() - started
            OUTCOMES.append(record)
        if expected_stage is not None:
            self.assertEqual(oracle_code, expected_stage, name)
            self.assertEqual(record["candidate"], expected_stage, name)

    def test_all_35_frozen_cases_exact_facts_and_dispositions(self):
        for row in frozen.cases():
            with self.subTest(case=row["name"]):
                self.exercise(row["name"], frozen.canonical_input_bytes(row["input"]), family="frozen",
                              expected_stage=row["expected_code_or_stage"])

    def test_all_36_unchanged_original_inputs_are_retained(self):
        for row in MANIFEST["original_fixtures"]:
            with self.subTest(original=row["path"]):
                raw = (REPO / row["path"]).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])
                self.assertEqual(len(raw), row["bytes"])
                self.exercise(row["path"], raw, family="original")

    def test_source_sidecar_keeps_subnormals_and_parser_canonical_zero(self):
        result = self.candidate.convert_document(admitted(named("subnormal-canonical-sidecar")))
        sidecar = result["sidecar"]
        for field in ("frequency_hz", "amplitude", "phase_turns"):
            self.assertEqual(sidecar["sources"][0][field], "0000000000000001")
        self.assertEqual(sidecar["keys"][0]["gains"][:2], ["8000000000000001", "0000000000000001"])
        result = self.candidate.convert_document(admitted(named("zero-frame-closure-ties")))
        self.assertEqual(result["sidecar"]["targets"][1]["target"], "0000000000000000")

    def test_encoder_refuses_forged_facts_and_boolean_integer_aliases(self):
        original = self.candidate.convert_document(admitted(named("ordinary-44100")))
        changes = [
            (("schema_version",), True),
            (("grid_case", "targets", 0, "tick"), False),
            (("commands", 0, "ordinal"), False),
            (("commands", 0, "repeated_target"), 0),
            (("final_keys", 0, "closed9", 0), 0),
            (("position_samples", 0, "source"), {"numerator": "0", "denominator": "2"}),
            (("root_bounds", 0, "source_anchor_time"), oracle.rational(123)),
            (("summary", "work_units"), 1),
            (("sidecar", "keys", 0, "gains", 0), "xyz"),
            (("sidecar", "targets", 0, "fraction"), "8000000000000000"),
            (("transport", "sha256"), "0" * 64),
        ]
        for path, replacement in changes:
            with self.subTest(path=path):
                altered = copy.deepcopy(original)
                target = altered
                for part in path[:-1]:
                    target = target[part]
                target[path[-1]] = replacement
                with self.assertRaises(self.candidate.ConversionRefusal) as caught:
                    self.candidate.encode_certificate(altered, implementation_sha256=self.hashes,
                                                       contract_sha256=self.contract_hash)
                self.assertEqual(caught.exception.code, "certificate")


def main():
    report_path = None
    if "--report" in sys.argv:
        index = sys.argv.index("--report")
        if index + 1 >= len(sys.argv):
            raise SystemExit("--report requires a path")
        report_path = Path(sys.argv[index + 1])
        del sys.argv[index:index + 2]
    started = time.monotonic()
    result = unittest.main(exit=False).result
    if report_path is not None:
        report = {
            "schema_version": 1, "evidence_class": "synthetic",
            "suite": "independent-contact-grid-conversion-v1", "passed": result.wasSuccessful(),
            "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
            "skipped": len(result.skipped), "elapsed_seconds": time.monotonic() - started,
            "implementation_sha256": implementation_hashes(), "contract_sha256": sha(CONTRACT_PATH),
            "test_sha256": sha(__file__), "oracle_sha256": sha(oracle.__file__),
            "generator_sha256": sha(frozen.__file__), "manifest_sha256": sha(MANIFEST_PATH),
            "case_count": len(OUTCOMES), "outcomes": OUTCOMES,
            "limits": "Exact finite synthetic trajectories only. No native snapshots, CLI atomicity, "
                      "audio accuracy, live callback deadline, or physical-fidelity qualification.",
        }
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
