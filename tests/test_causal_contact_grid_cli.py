#!/usr/bin/env python3
"""Bounded CGGRID1 native transport, rejection and JSON-schema checks.

Set HAMMOND_CAUSAL_CONTACT_GRID_PROBE_EXECUTABLE to the coherently built native
probe, or run through CTest. Unset, empty, missing or nonexecutable probe
configuration fails setup. Each process has a ten-second timeout and
checked output ceilings. No fixture files, shell commands or oracle evaluation
are needed. The differential suite owns broad trajectory comparison; this file
imports only its validation-free wire encoder.
"""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "tests"))
from test_causal_contact_grid_differential import encode_case


PROBE_ENV = "HAMMOND_CAUSAL_CONTACT_GRID_PROBE_EXECUTABLE"
TICKS = 65536
FULL = 1 << 48
UINT32_MAX = (1 << 32) - 1
MAX_INPUT_BYTES = 128 * 1024
MAX_REPORT_BYTES = 2 * 1024 * 1024
MAX_DIAGNOSTIC_BYTES = 256
FIELD_LIMIT = "integer exceeds its field limit"
DIGITS_ONLY = "expected unsigned decimal digits only"


def case(*, frames=1, targets=(), keys=1, rate=48000):
    return {
        "sample_rate_hz": rate,
        "frames": frames,
        "keys": [{"press_units_per_tick": 1, "release_units_per_tick": 1,
                  "contacts": [{"off": 0, "on": 1} for _ in range(9)]}
                 for _ in range(keys)],
        "targets": list(targets),
    }


def command(tick, position, key=0):
    return {"tick": tick, "key_index": key, "position": position}


def replace_token(payload, index, replacement):
    tokens = payload.split()
    tokens[index] = replacement if isinstance(replacement, bytes) else str(replacement).encode("ascii")
    return b" ".join(tokens) + b"\n"


def empty_report(fixture, partitions):
    """Schema scaffolding only: callers explicitly set nonzero motion/edges."""
    inactive_config = {"press_units_per_tick": 0, "release_units_per_tick": 0,
                       "contacts": [{"off": 0, "on": 0} for _ in range(9)]}
    zero_key = {"position": 0, "target": 0, "anchor_position": 0,
                "anchor_tick": 0, "closed": [False] * 9}
    configs = copy.deepcopy(fixture["keys"])
    configs.extend(copy.deepcopy(inactive_config) for _ in range(4 - len(configs)))
    cursor = 0
    blocks = []
    for frames in partitions:
        cursor += frames
        blocks.append({"frames": frames, "cursor_frames": cursor, "edges_written": 0})
    return {
        "schema_version": 1,
        "model_id": "causal-contact-grid-v1",
        "edges": [],
        "snapshot": {
            "phase": "closed",
            "config": {"sample_rate_hz": fixture["sample_rate_hz"],
                       "key_count": len(fixture["keys"]), "keys": configs},
            "cursor_frames": fixture["frames"],
            "command_count": len(fixture["targets"]),
            "edge_count": 0,
            "keys": [copy.deepcopy(zero_key) for _ in range(4)],
        },
        "blocks": blocks,
    }


class CausalContactGridCli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        configured = os.environ.get(PROBE_ENV)
        if configured is None:
            raise RuntimeError(
                "native causal-grid probe unavailable: build "
                "hammond_causal_contact_grid_probe and set " + PROBE_ENV + ", or run CTest")
        if not configured:
            raise RuntimeError("configured native causal-grid probe path is empty")
        cls.probe = Path(configured).resolve()
        if not cls.probe.is_file() or not os.access(cls.probe, os.X_OK):
            raise RuntimeError(f"configured native causal-grid probe unavailable: {cls.probe}")

    def invoke(self, payload=b"", arguments=()):
        try:
            result = subprocess.run(
                [str(self.probe), *arguments], input=payload,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=ROOT, timeout=10, check=False)
        except subprocess.TimeoutExpired:
            self.fail("native causal-grid probe exceeded its ten-second timeout")
        except OSError as error:
            self.fail(f"configured native causal-grid probe could not execute: {error}")
        self.assertLessEqual(len(result.stdout), MAX_REPORT_BYTES, "stdout exceeds 2 MiB")
        self.assertLessEqual(len(result.stderr), MAX_DIAGNOSTIC_BYTES, "stderr is unbounded")
        return result

    def reject(self, payload, diagnostic, arguments=()):
        result = self.invoke(payload, arguments)
        self.assertNotEqual(result.returncode, 0, "invalid input was accepted")
        self.assertEqual(result.stdout, b"", "rejection leaked a partial report")
        # Literal diagnostics also prove that arbitrary input is not echoed.
        message = b"causal_contact_grid_probe: " + diagnostic.encode("ascii")
        self.assertIn(result.stderr, (message + b"\n", message + b"\r\n"))

    def accept(self, payload):
        result = self.invoke(payload)
        self.assertEqual(result.returncode, 0, result.stderr.decode("ascii", errors="replace"))
        self.assertEqual(result.stderr, b"")
        self.assertTrue(result.stdout.endswith(b"\n"), "report needs a final newline")

        def unique_fields(pairs):
            fields = {}
            for name, value in pairs:
                if name in fields:
                    raise ValueError(f"duplicate JSON field: {name}")
                fields[name] = value
            return fields

        def reject_noninteger(value):
            raise ValueError(f"noninteger JSON number: {value}")

        try:
            return json.loads(result.stdout.decode("ascii"), object_pairs_hook=unique_fields,
                              parse_float=reject_noninteger, parse_constant=reject_noninteger)
        except (UnicodeError, ValueError) as error:
            self.fail(f"report is not one strict ASCII/integer JSON object: {error}")

    def assert_exact(self, actual, expected, path="report"):
        self.assertIs(type(actual), type(expected), f"{path}: scalar/container type")
        if isinstance(expected, dict):
            self.assertEqual(set(actual), set(expected), f"{path}: schema fields")
            for name, value in expected.items():
                self.assert_exact(actual[name], value, f"{path}.{name}")
        elif isinstance(expected, list):
            self.assertEqual(len(actual), len(expected), f"{path}: array length")
            for index, (observed, value) in enumerate(zip(actual, expected)):
                self.assert_exact(observed, value, f"{path}[{index}]")
        else:
            self.assertEqual(actual, expected, path)

    def test_help_documents_wire_domains_schema_and_ignores_stdin(self):
        result = self.invoke(b"not a case", ("--help",))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, b"")
        help_text = result.stdout.decode("ascii")
        for text in ("Usage:", "[--help]", "CGGRID1 F K N C P", "131072",
                     "[0-9]+", "44100", "48000", "96000", "0..4096", "0..512",
                     "4294967295", "281474976710656", "65536", "N=0 requires P=0",
                     "close_observation", "schema_version=1", "model_id", "snapshot",
                     "frames,cursor_frames,edges_written", "bounded stderr"):
            with self.subTest(documented=text):
                self.assertIn(text, help_text)

    def test_arguments_reject_paths_version_flags_and_extra_help_arguments(self):
        for arguments in (("--version",), ("-h",), ("--",), ("case.txt",), ("",),
                          ("--help", "extra"), ("--help", "--help"), ("x" * 4096,)):
            with self.subTest(arguments=tuple(value[:30] for value in arguments)):
                self.reject(encode_case(case()), "only --help or no arguments are accepted",
                            arguments)

    def test_transport_version_is_exact_and_has_no_bom(self):
        payload = encode_case(case())
        for version in (b"CGGRID0", b"CGGRID2", b"cggrid1", b"CGGRID1x",
                        b"\xef\xbb\xbfCGGRID1", b"CGGRID1\x00"):
            with self.subTest(version=version):
                self.reject(replace_token(payload, 0, version),
                            "expected CGGRID1 transport version")

    def test_all_ascii_whitespace_leading_zeros_and_eof_without_newline(self):
        fixture = case()
        tokens = encode_case(fixture).split()
        expected = empty_report(fixture, [1])
        for separator in (b" ", b"\t", b"\n", b"\r", b"\f", b"\v", b" \t\n\r\f\v"):
            with self.subTest(separator=separator):
                self.assert_exact(self.accept(separator + separator.join(tokens) + separator),
                                  expected)
        self.assert_exact(self.accept(b" ".join(tokens)), expected)
        self.assert_exact(self.accept(b" ".join([tokens[0]] + [b"000" + t for t in tokens[1:]])),
                          expected)

    def test_unsigned_decimal_only_rejects_signs_floats_unicode_and_comments(self):
        payload = encode_case(case())
        invalid = (b"+1", b"-1", b"-0", b"1.0", b".5", b"1.", b"1e0", b"1E+0",
                   b"0x1", b"0b1", b"1_0", b"1,0", b"nan", b"inf", b"true", b"1#comment",
                   b"\x001", b"\xff", "١".encode(), "１".encode(), "−1".encode())
        for token in invalid:
            with self.subTest(token=token):
                self.reject(replace_token(payload, 6, token), DIGITS_ONLY)

    def test_non_ascii_and_other_control_separators_are_not_whitespace(self):
        tokens = encode_case(case()).split()
        separators = [text.encode() for text in ("\u0085", "\u00a0", "\u2003", "\u2028",
                                                "\u2029", "\u3000", "\ufeff")]
        separators.extend((b"\x00", b"\x1c", b"\x1f"))
        for separator in separators:
            with self.subTest(separator=separator):
                payload = (b" ".join(tokens[:6]) + b" " + tokens[6] + separator
                           + b" ".join(tokens[7:]) + b"\n")
                self.reject(payload, DIGITS_ONLY)

    def test_unsigned_field_limits_reject_before_narrowing(self):
        payload = encode_case(case(targets=[command(0, 1)]))
        # Header, both speeds, both threshold fields and each target field.
        invalid = ((1, 1 << 32), (2, 5), (3, 4097), (4, 513), (5, 2),
                   (6, 1 << 32), (7, 1 << 32), (8, FULL + 1), (9, FULL + 1),
                   (26, TICKS + 1), (27, 1), (28, FULL + 1),
                   (6, (1 << 64) - 1), (6, 1 << 64), (28, 1 << 64))
        for index, value in invalid:
            with self.subTest(token_index=index, value=value):
                self.reject(replace_token(payload, index, value), FIELD_LIMIT)

    def test_configuration_domains_and_last_contact_are_validated(self):
        payload = encode_case(case())
        for rate in (0, 44101, 48001, 96001, UINT32_MAX):
            with self.subTest(rate=rate):
                self.reject(replace_token(payload, 1, rate), "unsupported sample rate")
        self.reject(replace_token(payload, 2, 0), "key count must be 1 through 4")
        for index in (6, 7):
            with self.subTest(zero_speed_field=index):
                self.reject(replace_token(payload, index, 0),
                            "press and release speeds must be positive")
        for off, on in ((0, 0), (1, 1), (2, 1), (FULL, FULL)):
            with self.subTest(last_threshold=(off, on)):
                changed = replace_token(replace_token(payload, 24, off), 25, on)
                self.reject(changed, "each contact requires off < on")

    def test_target_order_domains_and_zero_epoch_endpoint_are_checked(self):
        self.reject(encode_case(case(targets=[command(2, 0), command(1, 0)])),
                    "target ticks must be globally nondecreasing")
        self.reject(encode_case(case(targets=[command(TICKS, 0), command(TICKS - 1, 0)])),
                    "target ticks must be globally nondecreasing")
        self.reject(encode_case(case(frames=0, targets=[command(1, 0)])), FIELD_LIMIT)
        # Invalid final commands still prevent all output from otherwise valid input.
        for invalid in (command(TICKS + 1, 0), command(TICKS, 0, 1), command(TICKS, FULL + 1)):
            with self.subTest(last_command=invalid):
                self.reject(encode_case(case(targets=[command(0, 1), invalid])), FIELD_LIMIT)

    def test_every_required_token_and_declared_record_count(self):
        payload = encode_case(case(targets=[command(1, 1)]))
        tokens = payload.split()
        for length in range(len(tokens)):
            with self.subTest(truncated_token_count=length):
                self.reject(b" ".join(tokens[:length]) + b"\n", "missing input token")
        self.reject(replace_token(payload, 4, 0), "unexpected trailing input token")
        self.reject(replace_token(payload, 4, 2), "missing input token")
        extra_key = encode_case(case(frames=0, keys=2))
        self.reject(replace_token(extra_key, 2, 1), "unexpected trailing input token")
        self.reject(encode_case(case(frames=0)) + b"0 1\n", "unexpected trailing input token")

    def test_partition_count_positive_lengths_and_exact_sum(self):
        invalid = ((0, [1], FIELD_LIMIT),
                   (3, [], "a positive epoch needs at least one block"),
                   (3, [0, 3], "block lengths must be positive"),
                   (3, [1, 0, 2], "block lengths must be positive"),
                   (3, [1, 1], "block lengths must sum to N"),
                   (3, [3, 1], FIELD_LIMIT), (3, [4], FIELD_LIMIT),
                   (3, [1, 3], FIELD_LIMIT), (3, [1, 1, 1, 1], FIELD_LIMIT))
        for frames, blocks, diagnostic in invalid:
            with self.subTest(frames=frames, blocks=blocks):
                self.reject(encode_case(case(frames=frames), blocks), diagnostic)

    def test_trailing_tokens_second_case_and_binary_junk_are_rejected(self):
        payload = encode_case(case())
        for trailing in (b"0", b"# comment", encode_case(case()), b"\x00", b"\x1a",
                         b"\xff", "\u00a0".encode()):
            with self.subTest(trailing=trailing[:30]):
                self.reject(payload + trailing, "unexpected trailing input token")

    def test_exact_128_kib_input_is_allowed_and_one_byte_more_is_rejected(self):
        fixture = case(frames=0)
        payload = encode_case(fixture)
        for whitespace in (b" ", b"\r\n"):
            with self.subTest(padding=whitespace):
                padding_size = MAX_INPUT_BYTES - len(payload)
                padding = (whitespace * (padding_size // len(whitespace) + 1))[:padding_size]
                padded = payload + padding
                self.assertEqual(len(padded), MAX_INPUT_BYTES)
                self.assert_exact(self.accept(padded), empty_report(fixture, []))
                self.reject(padded + b" ", "stdin exceeds 131072 bytes")
        # A maximal-length malformed integer is not reflected in stderr either.
        oversized_integer = replace_token(payload, 6, b"9" * (MAX_INPUT_BYTES - len(payload) + 1))
        self.assertEqual(len(oversized_integer), MAX_INPUT_BYTES)
        self.reject(oversized_integer, FIELD_LIMIT)

    def test_zero_epoch_schema_types_and_padding_at_each_supported_rate(self):
        for rate in (44100, 48000, 96000):
            with self.subTest(rate=rate):
                fixture = case(frames=0, rate=rate)
                self.assert_exact(self.accept(encode_case(fixture)), empty_report(fixture, []))

    def test_zero_epoch_tied_endpoint_targets_close_without_travel(self):
        fixture = case(frames=0, targets=[command(0, FULL), command(0, 7), command(0, 7)])
        expected = empty_report(fixture, [])
        expected["snapshot"]["keys"][0]["target"] = 7
        self.assert_exact(self.accept(encode_case(fixture)), expected)

    def test_block_and_final_endpoint_dispatch_preserve_incoming_edges(self):
        fixture = case(frames=2, targets=[command(0, TICKS), command(TICKS, 0),
                                          command(2 * TICKS, FULL), command(2 * TICKS, 7),
                                          command(2 * TICKS, 7)])
        fixture["keys"][0]["contacts"] = [{"off": 0, "on": TICKS} for _ in range(9)]
        for partitions in ([2], [1, 1]):
            with self.subTest(partitions=partitions):
                expected = empty_report(fixture, partitions)
                expected["edges"] = [
                    {"time": {"tick": tick, "numerator": 0, "denominator": 1},
                     "key_index": 0, "contact_index": index, "closed_after": closed}
                    for tick, closed in ((TICKS, True), (2 * TICKS, False))
                    for index in range(9)]
                expected["snapshot"]["edge_count"] = 18
                expected["snapshot"]["keys"][0].update(target=7, anchor_tick=2 * TICKS)
                for block in expected["blocks"]:
                    block["edges_written"] = 9 * block["frames"]
                self.assert_exact(self.accept(encode_case(fixture, partitions)), expected)

    def test_admitted_maximum_counts_and_values_have_bounded_report(self):
        # Pure endpoint commands keep this transport stress cheap: no oracle or
        # 4608-edge trajectory replay, already covered by the differential suite.
        fixture = case(frames=4096, keys=4, rate=96000,
                       targets=[command(4096 * TICKS, FULL, index % 4) for index in range(512)])
        for key in fixture["keys"]:
            key.update(press_units_per_tick=UINT32_MAX, release_units_per_tick=UINT32_MAX)
            key["contacts"] = [{"off": FULL - 1, "on": FULL} for _ in range(9)]
        partitions = [1] * 4096
        expected = empty_report(fixture, partitions)
        for state in expected["snapshot"]["keys"]:
            state.update(target=FULL, anchor_tick=4096 * TICKS)
        self.assert_exact(self.accept(encode_case(fixture, partitions)), expected)


if __name__ == "__main__":
    unittest.main()
