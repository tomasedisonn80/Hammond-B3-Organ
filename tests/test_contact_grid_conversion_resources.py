#!/usr/bin/env python3
"""Independent public-API resource boundaries for contact-grid conversion.

The constructed inputs, expected counts and root times below are derived from
their specified motion, not production replay helpers. Lowered-limit checks
are explicitly guard fault injections, not claims that the normal corpus reaches
every conservative cap. Run with --report PATH for a source-bound receipt.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time
import unittest
from unittest import mock

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import contact_grid_conversion as candidate
from contact_switching_io import parse_input

OBSERVATIONS = {}
SOURCES = (
    "tools/contact_grid_conversion.py", "tools/convert_contact_grid.py",
    "tools/contact_switching_io.py", "tools/fractional_contact_reference.py",
    "docs/CONTACT_GRID_CONVERSION_CONTRACT.md",
    "tests/test_contact_grid_conversion_resources.py",
)


def hashes():
    return {path: hashlib.sha256((REPO / path).read_bytes()).hexdigest() for path in SOURCES}


def fixture(count=2, key_count=1, *, noops=False, offset_first=False):
    """Binary-exact durations, complete motion, and deliberately silent routes."""
    result = {
        "schema_version": 1, "model_id": "fractional-contact-reference-v1",
        "evidence_class": "synthetic", "fixture_id": "A19-resource-boundary",
        "sample_rate_hz": 48000,
        "frames": 512 if noops else (8 * ((count + key_count - 1) // key_count) +
                                      (8 if offset_first else 0)),
        "sources": [{"source_id": 1, "frequency_hz": 440.0,
                     "amplitude": 1.0, "phase_turns": 0.0}],
        "keys": [], "targets": [],
    }
    for key in range(key_count):
        result["keys"].append({
            "key_id": f"K{key}", "press_seconds": 1 / 8192,
            "release_seconds": 1 / 8192, "on": [0.5] * 9,
            "off": [0.25] * 9, "source_ids": [1] * 9, "gains": [0.0] * 9,
        })
    for ordinal in range(count):
        key, step = ordinal % key_count, ordinal // key_count
        result["targets"].append({
            "frame": ordinal if noops else 8 * step + (key + 1 if offset_first else 0),
            "fraction": 0.1 if noops else 0.0,
            "key_id": f"K{key}", "target": 0.0 if noops else float(1 - step % 2),
        })
    return result


def document(value):
    return parse_input(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                  allow_nan=False).encode("ascii"))


def converted(value=None, **kwargs):
    return candidate.convert_document(document(fixture() if value is None else value), **kwargs)


def encoded(value, **kwargs):
    identities = hashes()
    return candidate.encode_certificate(
        value, implementation_sha256={p: identities[p] for p in SOURCES[:4]},
        contract_sha256=identities[SOURCES[4]], **kwargs)


def rational(value):
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def maximum_bits(value):
    if type(value) is dict:
        if set(value) == {"numerator", "denominator"}:
            q = rational(value)
            return max(abs(q.numerator).bit_length(), q.denominator.bit_length())
        return max((maximum_bits(child) for child in value.values()), default=0)
    if type(value) is list:
        return max((maximum_bits(child) for child in value), default=0)
    return 0


class RefusalAssertions(unittest.TestCase):
    def refusal(self, operation, code="resource", reason=None):
        with self.assertRaises(candidate.ConversionRefusal) as caught:
            operation()
        error = caught.exception
        self.assertEqual(error.code, code)
        if reason is not None:
            self.assertEqual(error.witness.get("reason"), reason)
        return error


class CapacityTests(RefusalAssertions):
    def test_actual_edge_arrival_and_labeled_event_maxima(self):
        data = fixture(512)
        result = converted(data)
        self.assertEqual((len(result["edges"]), len(result["arrivals"]),
                          sum(map(len, result["preorder"]))), (4608, 512, 5634))
        self.assertEqual(len(result["position_samples"]), 1537)
        # One full move per command; source travel takes exactly 375/64 frames.
        # 2**32 * (64/375) rounds to the nearest/even integer below.
        exact_units = Fraction((1 << 32) * 64, 375)
        rounded_units = round(exact_units)
        grid_duration = Fraction(1 << 32, rounded_units)
        expected_edges, expected_arrivals = {}, {}
        for ordinal in range(512):
            base = 8 * ordinal
            direction, occurrence = (1 if ordinal % 2 == 0 else 0), ordinal // 2
            distance = Fraction(1, 2) if direction else Fraction(3, 4)
            times = (base + distance * Fraction(375, 64), base + distance * grid_duration)
            for contact in range(9):
                expected_edges[f"E:0:{contact}:{direction}:{occurrence}"] = times
            expected_arrivals[f"A:0:{1 if direction else -1}:{occurrence}"] = (
                base + Fraction(375, 64), base + grid_duration)
        for family, expected in (("edges", expected_edges), ("arrivals", expected_arrivals)):
            observed = {row["label"]: (rational(row["source_time"]), rational(row["grid_time"]))
                        for row in result[family]}
            self.assertEqual(observed, expected)
        self.assertEqual(result["final_keys"][0]["closed9"], [False] * 9)
        payload = encoded(result)
        self.assertEqual(json.loads(payload)["audio_accuracy"], "unqualified")
        self.assertLessEqual(result["summary"]["work_units"], 1_000_000)
        self.assertLessEqual(maximum_bits(result), 4096)
        OBSERVATIONS["full_event_capacity"] = {
            "edges": 4608, "arrivals": 512, "labels": 5634,
            "union_knots": len(result["position_samples"]),
            "work_units": result["summary"]["work_units"],
            "maximum_retained_rational_bits": maximum_bits(result),
            "certificate_bytes": len(payload), "transport_bytes": len(result["transport"]["text"]),
            "certificate_sha256": hashlib.sha256(payload).hexdigest(),
            "input_sha256": document(data).input_sha256,
        }

    def test_actual_union_knot_limit_and_first_excess(self):
        accepted = converted(fixture(511, 4, noops=True))
        self.assertEqual(len(accepted["position_samples"]), 4096)
        for key in range(4):
            samples = [row for row in accepted["position_samples"] if row["key_index"] == key]
            self.assertEqual(len(samples), 1024)
            self.assertTrue(all(rational(row["source"]) == rational(row["grid"]) == 0 for row in samples))
        self.assertEqual(sum(map(len, accepted["preorder"])), 513)
        self.assertEqual(json.loads(encoded(accepted))["summary"]["max_position_error"],
                         {"numerator": "0", "denominator": "1"})
        failure = self.refusal(lambda: converted(fixture(512, 4, noops=True)), reason="union-knots")
        self.assertEqual(failure.path, "position_samples")
        self.assertEqual(failure.witness, {"reason": "union-knots", "limit": 4096,
                                          "retained": 3078, "next_key_count": 1026})
        OBSERVATIONS["union_knot_boundary"] = {
            "accepted_commands": 511, "accepted_knots": 4096,
            "accepted_work_units": accepted["summary"]["work_units"],
            "refused_commands": 512, "refusal": failure.witness,
        }

    def test_smallest_frame_one_increment_is_admitted_exactly(self):
        data = fixture(1)
        data["targets"][0]["frame"] = 1
        fraction = math.nextafter(2.0 ** -53, math.inf)
        data["targets"][0]["fraction"] = fraction
        result = converted(data)
        self.assertEqual(rational(result["commands"][0]["source_time"]),
                         Fraction(1) + Fraction(1, 1 << 53) + Fraction(1, 1 << 105))
        self.assertEqual(rational(result["commands"][0]["grid_time"]), 1)
        self.assertEqual((len(result["edges"]), len(result["arrivals"])), (9, 1))
        bits = maximum_bits(result)
        self.assertGreaterEqual(bits, 106)
        self.assertLessEqual(bits, 4096)
        encoded(result)
        OBSERVATIONS["accepted_small_frame_one_increment"] = {
            "source_fraction": "1/2^53 + 1/2^105", "maximum_retained_rational_bits": bits,
            "root_count": 10, "work_units": result["summary"]["work_units"],
            "input_sha256": document(data).input_sha256,
        }

    def test_subnormal_time_obeys_original_admission_and_grid_collision(self):
        data = fixture(1)
        data["targets"][0]["fraction"] = float.fromhex("0x0.0000000000001p-1022")
        data["targets"][0]["frame"] = 1
        with self.assertRaisesRegex(ValueError, "nonzero target fraction is lost at its frame"):
            document(data)
        data["targets"][0]["frame"] = 0
        failure = self.refusal(lambda: converted(data), code="time_collision",
                               reason="interior-to-boundary")
        self.assertEqual(rational(failure.witness["source"]), Fraction(1, 1 << 1074))
        self.assertEqual(rational(failure.witness["grid"]), 0)

    def test_four_key_segment_guard_has_constructive_boundary(self):
        # 512 command intervals, 4 initial holds, 512 after-arrival holds:
        # 1028 segments in each replay. The ordinary 1032 cap stays unchanged.
        data = fixture(512, 4, offset_first=True)
        with mock.patch.object(candidate, "MAX_SEGMENTS", 1028):
            result = converted(data)
            self.assertEqual((len(result["edges"]), len(result["arrivals"])), (4608, 512))
        with mock.patch.object(candidate, "MAX_SEGMENTS", 1027):
            error = self.refusal(lambda: converted(data), reason="segments")
            self.assertEqual(error.path, "source.segments")
        OBSERVATIONS["segment_guard_injection"] = {"accepted_limit": 1028, "refused_limit": 1027,
                                                    "ordinary_limit": 1032}

    def test_event_and_root_guard_injections_preserve_exact_capacity(self):
        data = fixture(2)
        for attribute, exact, reason in (("MAX_EDGES", 18, "edges"),
                                         ("MAX_ARRIVALS", 2, "arrivals"),
                                         ("MAX_EVENTS", 24, "labeled-events")):
            with self.subTest(cap=attribute):
                with mock.patch.object(candidate, attribute, exact):
                    self.assertEqual(len(converted(data)["edges"]), 18)
                with mock.patch.object(candidate, attribute, exact - 1):
                    self.refusal(lambda: converted(data), reason=reason)

    def test_work_guard_accepts_its_reported_boundary_then_refuses_one_less(self):
        data = fixture(4)
        result = converted(data)
        count = result["summary"]["work_units"]
        # This verifies enforcement at the reported count, not independent
        # completeness of the operation accounting; that needs source review.
        with mock.patch.object(candidate, "MAX_WORK_UNITS", count):
            self.assertEqual(converted(data), result)
        with mock.patch.object(candidate, "MAX_WORK_UNITS", count - 1):
            self.refusal(lambda: converted(data), reason="work-units")

    def test_transport_byte_guard_exact_boundary_and_first_excess(self):
        data = fixture(2)
        size = len(converted(data)["transport"]["text"].encode("ascii"))
        with mock.patch.object(candidate, "MAX_TRANSPORT_BYTES", size):
            self.assertEqual(len(converted(data)["transport"]["text"]), size)
        with mock.patch.object(candidate, "MAX_TRANSPORT_BYTES", size - 1):
            self.refusal(lambda: converted(data), reason="transport-bytes")

    def test_encoded_byte_guard_includes_final_lf(self):
        result = converted()
        payload = encoded(result)
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))
        with mock.patch.object(candidate, "MAX_CERTIFICATE_BYTES", len(payload)):
            self.assertEqual(encoded(result), payload)
        with mock.patch.object(candidate, "MAX_CERTIFICATE_BYTES", len(payload) - 1):
            error = self.refusal(lambda: encoded(result), reason="certificate-bytes")
            self.assertEqual(error.path, "encoding")


class CertificateResourceTests(RefusalAssertions):
    def test_retained_rational_4096_and_4097_bit_boundaries(self):
        for field in ("numerator", "denominator"):
            for bits in (4096, 4097):
                with self.subTest(field=field, bits=bits):
                    result = converted()
                    value = {"numerator": "1", "denominator": "1"}
                    value[field] = str(1 << (bits - 1))
                    result["summary"]["max_position_error"] = value
                    if bits == 4097:
                        failure = self.refusal(lambda: encoded(result), reason="rational-bits")
                        self.assertEqual(failure.witness[field + "_bits"], 4097)
                    else:
                        # Shape/bit admission succeeds; the forged numerical
                        # fact must still fail independent reconstruction.
                        failure = self.refusal(lambda: encoded(result), code="certificate",
                                               reason="reconstruction-value")
                        self.assertIn("summary.max_position_error", failure.path)

    def test_product_bound_does_not_claim_all_sums_fit_8192_bits(self):
        n = (1 << 4096) - 1
        left, right = Fraction(n, n - 1), Fraction(n - 2, n - 3)
        products = (left.numerator * right.denominator, right.numerator * left.denominator)
        self.assertTrue(all(value.bit_length() <= 8192 for value in products))
        self.assertEqual(sum(products).bit_length(), 8193)
        # The frozen contract bounds transient products, then every reduced
        # retained result. It does not assert an 8192-bit addition accumulator.
        self.assertGreater((left + right).numerator.bit_length(), 4096)
        OBSERVATIONS["arithmetic_distinction"] = {
            "operand_bits": 4096, "product_bits": [x.bit_length() for x in products],
            "unreduced_sum_bits": sum(products).bit_length(),
            "reduced_result_numerator_bits": (left + right).numerator.bit_length(),
            "scope": "Independent arithmetic illustration; no private production helper call.",
        }

    def test_all_declared_array_caps_reject_before_traversal(self):
        edits = (
            ("grid_case", "keys", 5), ("grid_case", "targets", 513),
            ("sidecar", "sources", 37), ("sidecar", "keys", 5),
            ("sidecar", "targets", 513), (None, "scalar_errors", 1121),
            (None, "edges", 4609), (None, "arrivals", 513), (None, "commands", 513),
            (None, "final_keys", 5), (None, "preorder", 5635),
            (None, "position_samples", 4097), (None, "root_bounds", 5121),
            ("transport", "partitions", 2),
        )
        for parent, field, length in edits:
            with self.subTest(parent=parent, field=field):
                result = converted()
                destination = result if parent is None else result[parent]
                destination[field] = [None] * length
                self.refusal(lambda: encoded(result), code="certificate", reason="invalid-array-size")

    def test_total_preorder_label_cap_is_aggregate(self):
        result = converted()
        result["preorder"] = [["B:0"] * 2818, ["B:1"] * 2818]
        self.refusal(lambda: encoded(result), code="certificate", reason="labeled-event-cap")

    def test_aggregate_certificate_string_limit_precedes_replay(self):
        result = converted()
        q = {"numerator": str((1 << 4095) - 1), "denominator": str((1 << 4095) + 1)}
        self.assertEqual(math.gcd(int(q["numerator"]), int(q["denominator"])), 1)
        row = {field: q for field in result["root_bounds"][0] if field != "label"}
        row["label"] = "E:0:0:1:0"
        # Aliasing avoids allocating the >120 MiB expanded JSON. Every field
        # still counts in the finite schema traversal before reconstruction.
        result["root_bounds"] = [row] * 5120
        failure = self.refusal(lambda: encoded(result), reason="certificate-bytes")
        self.assertTrue(failure.path.startswith("root_bounds["))

    def test_long_rational_and_transport_strings_are_bounded_before_decoding(self):
        for field in ("numerator", "denominator"):
            result = converted()
            result["summary"]["max_position_error"][field] = "9" * 5000
            self.refusal(lambda: encoded(result), code="certificate", reason="invalid-ascii-string")
        result = converted()
        result["transport"]["text"] = "A" * 131073
        self.refusal(lambda: encoded(result), code="certificate", reason="invalid-ascii-string")

    def test_boolean_integer_aliases_fail_at_each_resource_index_family(self):
        paths = (("grid_case", "frames"), ("input_bytes",),
                 ("summary", "work_units"), ("summary", "root_witness"),
                 ("commands", 0, "ordinal"), ("commands", 0, "before_direction"),
                 ("position_samples", 0, "key_index"))
        for path in paths:
            with self.subTest(path=path):
                result = converted()
                node = result
                for key in path[:-1]:
                    node = node[key]
                node[path[-1]] = True
                self.refusal(lambda: encoded(result), code="certificate", reason="invalid-integer")

    def test_cyclic_and_deep_malformed_certificate_is_rejected_structurally(self):
        cycle = []; cycle.append(cycle)
        deep = []
        for _ in range(10000):
            deep = [deep]
        for malformed in (cycle, deep):
            for field in ("preorder", "scalar_errors", "position_samples"):
                with self.subTest(field=field, cycle=malformed is cycle):
                    result = converted()
                    result[field] = malformed
                    self.refusal(lambda: encoded(result), code="certificate")


class DeadlineAndDiagnosticTests(RefusalAssertions):
    def test_deadline_equality_and_expiry_during_work(self):
        with mock.patch.object(candidate.time, "monotonic", return_value=5.0):
            self.refusal(lambda: converted(deadline=5.0), reason="deadline")
        calls = 0
        def clock():
            nonlocal calls
            calls += 1
            return 0.0 if calls < 100 else 2.0
        with mock.patch.object(candidate.time, "monotonic", side_effect=clock):
            self.refusal(lambda: converted(fixture(512), deadline=1.0), reason="deadline")
        self.assertEqual(calls, 100)

    def test_encoder_deadline_is_checked_on_output_iteration(self):
        result = converted()
        current = 0.0
        original = json.JSONEncoder.iterencode
        def expiring(encoder, value, *args, **kwargs):
            nonlocal current
            for chunk in original(encoder, value, *args, **kwargs):
                current = 2.0
                yield chunk
        with mock.patch.object(candidate.time, "monotonic", side_effect=lambda: current), \
                mock.patch.object(json.JSONEncoder, "iterencode", expiring):
            failure = self.refusal(lambda: encoded(result, deadline=1.0), reason="deadline")
        self.assertEqual(failure.path, "encoding")

    def test_deadline_invalid_types_and_nonfinite_values_are_input_refusals(self):
        for deadline in (True, "1", float("inf"), float("nan"), 10 ** 1000):
            with self.subTest(kind=type(deadline).__name__):
                self.refusal(lambda: converted(deadline=deadline), code="input")

    def test_diagnostic_size_exact_limit_and_first_excess(self):
        def envelope(witness):
            return {"schema_version": 1, "conversion_id": "fractional-to-contact-grid-rne-v1",
                    "status": "refused", "code": "input", "path": "x", "witness": witness}
        overhead = len(json.dumps(envelope({"value": ""}), sort_keys=True,
                                  separators=(",", ":"), ensure_ascii=True).encode("ascii")) + 1
        exact = candidate.ConversionRefusal("input", "x", {"value": "a" * (8192 - overhead)})
        self.assertEqual((exact.code, exact.path), ("input", "x"))
        excess = candidate.ConversionRefusal("input", "x", {"value": "a" * (8193 - overhead)})
        self.assertEqual((excess.code, excess.path, excess.witness),
                         ("resource", "diagnostic", {"reason": "diagnostic-size"}))

    def test_deep_diagnostic_is_bounded_instead_of_recursion_error(self):
        nested = []
        for _ in range(10000):
            nested = [nested]
        failure = candidate.ConversionRefusal("input", "deep", {"nested": nested})
        self.assertEqual((failure.code, failure.path, failure.witness),
                         ("resource", "diagnostic", {"reason": "diagnostic-size"}))

    def test_cyclic_and_nonfinite_diagnostic_fallbacks(self):
        cycle = {}; cycle["cycle"] = cycle
        for witness in (cycle, {"number": float("nan")}, {"not_json": object()}):
            failure = candidate.ConversionRefusal("input", "invalid", witness)
            self.assertEqual((failure.code, failure.path), ("resource", "diagnostic"))


def main():
    report = None
    if "--report" in sys.argv:
        index = sys.argv.index("--report")
        report = Path(sys.argv[index + 1]).resolve()
        del sys.argv[index:index + 2]
        if report.exists():
            raise SystemExit("Refusing to overwrite an existing resource receipt")
    before = hashes()
    started = time.monotonic()
    program = unittest.main(exit=False)
    elapsed = time.monotonic() - started
    after = hashes()
    if report is not None:
        peak = None
        if sys.platform.startswith("linux"):
            import resource
            peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        report.write_text(json.dumps({
            "schema": 1, "status": "passed" if program.result.wasSuccessful() else "failed",
            "tests": program.result.testsRun, "failures": len(program.result.failures),
            "errors": len(program.result.errors), "elapsed_seconds": elapsed,
            "python": platform.python_version(), "platform": platform.platform(),
            "cwd": str(Path.cwd()), "source_before": before, "source_after": after,
            "sources_unchanged": before == after, "observations": OBSERVATIONS,
            "process_peak_rss_bytes_linux": peak,
            "limits": "Finite synthetic public-API cases; lowered-limit injections are guard tests. "
                      "Process high-water RSS includes the entire test runner, not an API allocation bound. "
                      "No native, audio, physical, callback or portable performance claim.",
        }, indent=2, allow_nan=False) + "\n")
    raise SystemExit(0 if program.result.wasSuccessful() and before == after else 1)


if __name__ == "__main__":
    main()
