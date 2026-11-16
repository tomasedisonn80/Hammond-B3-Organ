"""Independent adversarial boundary checks for the offline contact command.

Expected schemas, exact times and limits come from the frozen v1 contracts,
not the candidate's constants or trajectory/filter helpers. Small synthetic
cases keep this suite separate from continuous-oracle numerical admission.
Run from the repository root: python3 -B tests/test_contact_switching_io.py -v
"""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import copy
import errno
from fractions import Fraction
import hashlib
import io
import json
import math
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / "tools"
sys.path.insert(0, str(TOOLS))
import contact_switching_io as candidate
import contact_switching_reference as command


ROOT_FIELDS = set("schema_version model_id evidence_class fixture_id input_sha256 "
                  "implementation_sha256 python_version platform sample_rate_hz frames "
                  "factor first_frame time_offset_seconds samples raw_bound output_bound "
                  "work caps observations targets edges final_keys filter gate_jumps".split())
EDGE_FIELDS = set("exact_u frame fraction key_index contact_index closed_after "
                  "inside_observation value_jump slope_jump_per_second".split())
TARGET_FIELDS = set("frame fraction key_id target input_ordinal".split())
FINAL_FIELDS = set("key_id position target closed".split())
FILTER_FIELDS = set("H beta normalizer coefficient_count coefficient_sha256 sum "
                    "absolute_sum dc_residual responses".split())
IMPLEMENTATIONS = ("fractional_contact_reference.py", "contact_switching_io.py",
                   "contact_switching_reference.py")
PRIOR_OUTPUT = b"previous artifact\x00\xff\nkeep byte-for-byte\n"


def fixture(frames=24):
    # F*P = F*R = 375/32 host frames exactly; make at 375/64.
    return {
        "schema_version": 1, "model_id": "fractional-contact-reference-v1",
        "evidence_class": "synthetic", "fixture_id": "A23-small-v1",
        "sample_rate_hz": 48000, "frames": frames,
        "sources": [{"source_id": 7, "frequency_hz": 0.0,
                     "amplitude": 1.0, "phase_turns": 0.25}],
        "keys": [{"key_id": "A", "press_seconds": 1 / 4096,
                  "release_seconds": 1 / 4096, "on": [0.5] * 9,
                  "off": [0.25] * 9, "source_ids": [7] * 9,
                  "gains": [1.0] + [0.0] * 8}],
        "targets": [{"frame": 0, "fraction": 0.0, "key_id": "A", "target": 1.0}],
    }


def encoded(document):
    return json.dumps(document, ensure_ascii=True, separators=(",", ":")).encode("ascii")


def changed(document, path, value):
    result = copy.deepcopy(document)
    node = result
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = value
    return result


def exact_coordinate(value):
    value = Fraction(value)
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def own_hashes():
    return {"tools/" + name: hashlib.sha256((TOOLS / name).read_bytes()).hexdigest()
            for name in IMPLEMENTATIONS}


def stat_with(information, **changes):
    """Retain real file facts except the explicitly injected platform metadata."""
    fields = {name: getattr(information, name) for name in dir(information)
              if name.startswith("st_")}
    fields.update(changes)
    return SimpleNamespace(**fields)


def invalid_documents():
    """Mutations of independently specified input records, with useful labels."""
    base = fixture()
    for path in ((), ("sources", 0), ("keys", 0), ("targets", 0)):
        node = base
        for part in path:
            node = node[part]
        for member in node:
            document = copy.deepcopy(base)
            record = document
            for part in path:
                record = record[part]
            del record[member]
            yield f"missing {path}/{member}", document
        document = copy.deepcopy(base)
        record = document
        for part in path:
            record = record[part]
        record["undeclared"] = 0
        yield f"unknown {path}", document

    numeric_paths = [
        ("schema_version",), ("sample_rate_hz",), ("frames",),
        *(("sources", 0, name) for name in
          ("source_id", "frequency_hz", "amplitude", "phase_turns")),
        ("keys", 0, "press_seconds"), ("keys", 0, "release_seconds"),
        *(("keys", 0, name, 0) for name in ("on", "off", "source_ids", "gains")),
        *(("targets", 0, name) for name in ("frame", "fraction", "target")),
    ]
    for path in numeric_paths:
        for value in (True, False, None, "0"):
            yield f"wrong numeric type {path} {value!r}", changed(base, path, value)
    for path in (("schema_version",), ("sample_rate_hz",), ("frames",),
                 ("sources", 0, "source_id"), ("keys", 0, "source_ids", 0),
                 ("targets", 0, "frame")):
        value = base
        for part in path:
            value = value[part]
        yield f"floating integer {path}", changed(base, path, float(value))
    for path in numeric_paths:
        for value in (math.nan, math.inf, -math.inf):
            yield f"nonfinite {path} {value}", changed(base, path, value)

    bounds = (
        (("schema_version",), (0, 2)), (("sample_rate_hz",), (0, 47999, 192000)),
        (("frames",), (-1, 4097)), (("sources", 0, "source_id"), (0, 92)),
        (("sources", 0, "frequency_hz"), (-1, math.nextafter(21600.0, math.inf))),
        (("sources", 0, "amplitude"), (-0.01, 1.01)),
        (("sources", 0, "phase_turns"), (-0.01, 1.0)),
        (("keys", 0, "press_seconds"), (0, math.nextafter(0.0001, 0), 1.01)),
        (("keys", 0, "release_seconds"), (0, 1.01)),
        (("keys", 0, "on", 0), (0.25, 0, 1.01)),
        (("keys", 0, "off", 0), (-0.01, 0.5)),
        (("keys", 0, "source_ids", 0), (0, 8, 92)),
        (("keys", 0, "gains", 0), (-1.01, 1.01)),
        (("targets", 0, "frame"), (-1, 25)),
        (("targets", 0, "fraction"), (-0.01, 1.0)),
        (("targets", 0, "target"), (-0.01, 1.01)),
    )
    for path, values in bounds:
        for value in values:
            yield f"bounds {path} {value}", changed(base, path, value)
    for path in (("fixture_id",), ("keys", 0, "key_id"), ("targets", 0, "key_id")):
        for value in ("", "_start", "with space", "with/slash", "a" * 65, "\u00e9", None, 1):
            yield f"identifier {path} {value!r}", changed(base, path, value)
    for path, value in ((("model_id",), "other-model"), (("evidence_class",), "measured"),
                        (("targets", 0, "key_id"), "absent")):
        yield f"identity {path}", changed(base, path, value)
    for name, low, high in (("sources", 1, 36), ("keys", 1, 4), ("targets", 0, 512)):
        for value in (None, {}, "[]", base[name] * (high + 1)):
            yield f"array {name} {type(value).__name__}", changed(base, (name,), value)
        if low:
            yield f"empty {name}", changed(base, (name,), [])
        yield f"nonrecord {name}", changed(base, (name, 0), [])
    for name in ("on", "off", "source_ids", "gains"):
        for value in (None, {}, "[]", [], base["keys"][0][name][:-1], base["keys"][0][name] + [0]):
            yield f"contact array {name} {value!r}", changed(base, ("keys", 0, name), value)
    for name in ("sources", "keys"):
        yield f"duplicate {name}", changed(base, (name,), base[name] * 2)
    terminal = changed(base, ("targets", 0, "frame"), 24)
    yield "fraction at N", changed(terminal, ("targets", 0, "fraction"), 0.125)
    lost = changed(base, ("targets", 0, "frame"), 1)
    yield "lost nonzero fraction", changed(lost, ("targets", 0, "fraction"), 2.0**-54)
    for first, second in (((1, 0.5), (1, math.nextafter(0.5, 1.0))),
                          ((1, math.nextafter(1.0, 0.0)), (2, 0.0))):
        targets = [{"frame": f, "fraction": q, "key_id": "A", "target": 1.0}
                   for f, q in (first, second)]
        yield f"rounded time collision {first} {second}", changed(base, ("targets",), targets)


class InputAdmissionTests(unittest.TestCase):
    def test_exact_schema_numeric_types_domains_routes_and_time_collisions(self):
        for label, document in invalid_documents():
            with self.subTest(case=label), self.assertRaises(ValueError):
                candidate.parse_input(encoded(document))

    def test_duplicate_members_are_rejected_at_every_record_depth(self):
        data = encoded(fixture())
        for member in (b'"schema_version":1', b'"source_id":7', b'"key_id":"A"', b'"frame":0'):
            with self.subTest(member=member), self.assertRaisesRegex(ValueError, "duplicate"):
                candidate.parse_input(data.replace(member, member + b"," + member, 1))
        escaped_duplicate = data.replace(b'"schema_version":1',
                                         b'"schema_version":1,"\\u0073chema_version":1', 1)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            candidate.parse_input(escaped_duplicate)

    def test_strict_bytes_utf8_json_and_finite_tokens(self):
        data = encoded(fixture())
        malformed = (b"", b"\xff", b"\xc0\xaf", b"\xed\xa0\x80", b"\xef\xbb\xbf" + data,
                     data[:-1], data + b"false", b"[]", b"null", b"true", b"0",
                     data + b"\x00", b"/*comment*/" + data, data[:-1] + b",}")
        for value in malformed + (data.decode("ascii"), bytearray(data), None):
            with self.subTest(value=repr(value)[:90]), self.assertRaises(ValueError):
                candidate.parse_input(value)
        for token in (b"NaN", b"Infinity", b"-Infinity", b"1e999", b"-1e999", b"9" * 1000):
            with self.subTest(token=token[:30]), self.assertRaises(ValueError):
                candidate.parse_input(data.replace(b'"amplitude":1.0', b'"amplitude":' + token))

    def test_input_byte_cap_includes_whitespace_and_has_exact_boundary(self):
        data = encoded(fixture())
        boundary = data + b" " * (262144 - len(data))
        admitted = candidate.parse_input(boundary)
        self.assertEqual(admitted.input_size_bytes, 262144)
        self.assertEqual(admitted.input_sha256, hashlib.sha256(boundary).hexdigest())
        with self.assertRaises(ValueError):
            candidate.parse_input(boundary + b" ")

    def test_depth_limit_counts_containers_not_quoted_escaped_brackets(self):
        with self.assertRaisesRegex(ValueError, "unknown or missing"):
            candidate.parse_input(b"[" * 12 + b"0" + b"]" * 12)
        with self.assertRaisesRegex(ValueError, "nesting"):
            candidate.parse_input(b"[" * 13 + b"0" + b"]" * 13)
        text = encoded({"quoted": "[" * 40 + '\\"' + "]" * 40})
        with self.assertRaisesRegex(ValueError, "unknown or missing"):
            candidate.parse_input(text)

    def test_admitted_order_immutable_tuples_identical_times_and_signed_zero(self):
        document = fixture()
        document["sources"].insert(0, dict(document["sources"][0], source_id=91))
        document["keys"].insert(0, dict(document["keys"][0], key_id="Z"))
        document["targets"] = [
            {"frame": 2, "fraction": 0.5, "key_id": "A", "target": 0.5},
            {"frame": 0, "fraction": -0.0, "key_id": "Z", "target": -0.0},
            {"frame": 2, "fraction": 0.5, "key_id": "A", "target": 1.0},
        ]
        document["sources"][0]["frequency_hz"] = -0.0
        admitted = candidate.parse_input(encoded(document))
        self.assertEqual([row.source_id for row in admitted.case.sources], [91, 7])
        self.assertEqual([row.key_id for row in admitted.case.keys], ["Z", "A"])
        self.assertEqual([row.frame for row in admitted.case.targets], [2, 0, 2])
        for rows in (admitted.case, admitted.case.sources, admitted.case.keys,
                     admitted.case.targets, admitted.case.keys[0].gains9):
            self.assertIsInstance(rows, tuple)
        for value in (admitted.case.sources[0].frequency_hz,
                      admitted.case.targets[1].fraction, admitted.case.targets[1].target):
            self.assertEqual(math.copysign(1.0, value), 1.0)

    def test_valid_capacity_and_numeric_boundaries_remain_admissible(self):
        document = fixture(0)
        document["fixture_id"] = "A" * 64
        document["sources"] = [dict(document["sources"][0], source_id=source_id,
                                    frequency_hz=21600.0, phase_turns=math.nextafter(1.0, 0.0))
                               for source_id in range(1, 37)]
        document["keys"] = [dict(document["keys"][0], key_id="key-" + str(index),
                                 press_seconds=0.0001, release_seconds=1.0,
                                 on=[1.0] * 9, off=[0.0] * 9,
                                 gains=[-1.0, 1.0] + [0.0] * 7)
                            for index in range(4)]
        document["targets"] = [{"frame": 0, "fraction": 0.0, "key_id": "key-" + str(index % 4),
                                 "target": float(index % 2)} for index in range(512)]
        admitted = candidate.parse_input(encoded(document))
        self.assertEqual((len(admitted.case.sources), len(admitted.case.keys), len(admitted.case.targets)),
                         (36, 4, 512))
        report = candidate.build_report(admitted, 256)
        self.assertEqual(report["work"], 588)
        self.assertEqual(report["samples"], [])


class FilesystemBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="contact-io-test-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.input = self.directory / "input.json"
        self.output = self.directory / "prior.json"
        self.input.write_bytes(encoded(fixture(0)))
        self.output.write_bytes(PRIOR_OUTPUT)
        self.unrelated = self.directory / ".contact-switching-other-user.tmp"
        self.unrelated.write_bytes(b"not owned by this invocation")

    def arguments(self, *, input_path=None, output_path=None, factor="32"):
        return ["--input", os.fspath(self.input if input_path is None else input_path),
                "--factor", str(factor), "--output",
                os.fspath(self.output if output_path is None else output_path)]

    def invoke(self, arguments=None, *, real=False):
        arguments = self.arguments() if arguments is None else arguments
        if real:
            completed = subprocess.run([sys.executable, "-B", str(TOOLS / "contact_switching_reference.py"),
                                        *arguments], cwd=self.directory, capture_output=True,
                                       text=True, encoding="utf-8", errors="strict", timeout=4)
            return completed.returncode, completed.stdout, completed.stderr
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = command.main(arguments)
        return status, stdout.getvalue(), stderr.getvalue()

    def assert_rejected(self, arguments=None, *, real=False):
        status, stdout, stderr = self.invoke(arguments, real=real)
        self.assertNotEqual(status, 0)
        self.assertEqual(stdout, "")
        self.assertTrue(stderr.startswith("contact-switching: "), stderr)
        self.assertEqual(len(stderr.splitlines()), 1)
        self.assertLessEqual(len(stderr), 501)
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(self.unrelated.read_bytes(), b"not owned by this invocation")

    def assert_no_owned_temporary(self):
        self.assertEqual(sorted(path.name for path in self.directory.glob(".contact-switching-*.tmp")),
                         [self.unrelated.name])

    def facility(self, name, operation):
        try:
            return operation()
        except NotImplementedError as error:
            self.skipTest(f"{name} unavailable: {error}")
        except OSError as error:
            unavailable = {errno.EACCES, errno.EPERM, errno.ENOSYS, errno.ENOTSUP,
                           errno.EAFNOSUPPORT, errno.EPROTONOSUPPORT,
                           getattr(errno, "EOPNOTSUPP", errno.ENOTSUP)}
            if error.errno in unavailable or getattr(error, "winerror", None) == 1314:
                self.skipTest(f"{name} unavailable: {error}")
            raise

    def test_every_invalid_document_preserves_existing_output_before_rendering(self):
        with patch.object(candidate, "build_report") as render, \
                patch.object(candidate.tempfile, "mkstemp") as create:
            for label, document in invalid_documents():
                with self.subTest(case=label):
                    data = encoded(document)
                    self.input.write_bytes(data)
                    self.assert_rejected()
                    self.assertEqual(self.input.read_bytes(), data)
                    self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
            render.assert_not_called()
            create.assert_not_called()
        self.assert_no_owned_temporary()

    def test_real_malformed_utf8_and_json_diagnostics_preserve_output(self):
        for data in (b"\xff", b'{"schema_version":1,"schema_version":1}'):
            with self.subTest(data=data):
                self.input.write_bytes(data)
                self.assert_rejected(real=True)
                self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
                self.assertEqual(self.input.read_bytes(), data)
                self.assert_no_owned_temporary()

    def test_required_unique_options_and_only_declared_factors(self):
        valid = self.arguments()
        variants = [[], valid[2:], valid[:2] + valid[4:], valid[:4], valid + ["extra"],
                    valid + ["--" + "x" * 10000],
                    ["--inp", *valid[1:]], ["--unknown", *valid]]
        for option, value in (("--input", self.input), ("--factor", "32"), ("--output", self.output)):
            variants.extend((valid + [option, str(value)], valid + [option + "=" + str(value)]))
        variants.extend(self.arguments(factor=value) for value in
                        ("0", "16", "33", "512", "032", "+32", "32.0", "True", "nan", ""))
        with patch.object(candidate, "preflight_paths") as preflight:
            for arguments in variants:
                with self.subTest(arguments=arguments):
                    self.assert_rejected(arguments)
                    self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
            preflight.assert_not_called()
        self.assert_rejected(valid + ["--factor=32"], real=True)
        self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
        self.assert_no_owned_temporary()

    def test_cli_accepts_each_declared_factor_for_an_empty_flush(self):
        for factor in (32, 64, 128, 256):
            with self.subTest(factor=factor):
                self.assertEqual(self.invoke(self.arguments(factor=factor)), (0, "", ""))
                payload = self.output.read_bytes()
                report = json.loads(payload)
                self.assertEqual((report["factor"], report["frames"], report["samples"]), (factor, 0, []))
                self.assertIsNone(report["filter"])
                self.assertEqual(report["observations"]["report_bytes"], len(payload))
                self.assert_no_owned_temporary()

    def test_distinct_path_and_descriptor_metadata_views_allow_unchanged_input(self):
        # CPython 3.12 Windows path stat reports creation time in ctime while
        # fstat reports change time; path-derived execute bits can differ too.
        original_stat, original_fstat = candidate.os.stat, candidate.os.fstat
        resolved_input = self.input.resolve()
        for path_execute_bits in (0, 0o111):
            with self.subTest(path_execute_bits=path_execute_bits):
                def path_stat(path, *args, **kwargs):
                    information = original_stat(path, *args, **kwargs)
                    if path in (self.input, resolved_input):
                        return stat_with(information,
                                         st_mode=information.st_mode | path_execute_bits)
                    return information

                def descriptor_stat(fd):
                    information = original_fstat(fd)
                    return stat_with(information, st_ctime_ns=information.st_ctime_ns + 10**9)

                with patch.object(candidate.os, "stat", side_effect=path_stat), \
                        patch.object(candidate.os, "fstat", side_effect=descriptor_stat):
                    self.assertEqual(self.invoke(), (0, "", ""))
                report = json.loads(self.output.read_bytes())
                self.assertEqual(report["input_sha256"], hashlib.sha256(self.input.read_bytes()).hexdigest())
                self.assert_no_owned_temporary()

    def test_real_rewritten_input_with_preserved_mtime_is_admitted(self):
        previous = self.input.stat()
        document = fixture(0)
        document["fixture_id"] = "A45-rewritten-v1"
        data = encoded(document)
        self.input.write_bytes(data)
        os.utime(self.input, ns=(previous.st_atime_ns, previous.st_mtime_ns))
        self.assertEqual(self.invoke(real=True), (0, "", ""))
        report = json.loads(self.output.read_bytes())
        self.assertEqual(report["input_sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(report["fixture_id"], document["fixture_id"])
        self.assert_no_owned_temporary()

    def test_descriptor_ctime_only_change_rejects_load_and_output_recheck(self):
        original_fstat = candidate.os.fstat
        generation = 10**9

        def descriptor_stat(fd):
            information = original_fstat(fd)
            return stat_with(information, st_ctime_ns=information.st_ctime_ns + generation)

        report = candidate.build_report(candidate.parse_input(self.input.read_bytes()), 32)
        with patch.object(candidate.os, "fstat", side_effect=descriptor_stat):
            plan = candidate.preflight_paths(self.input, self.output)
            generation += 1  # Same device, inode, mode, size and mtime; only change time moves.
            with self.assertRaisesRegex(ValueError, "changed after path preflight"):
                candidate.load_input(plan.input_path, expected_signature=plan.input_signature)
            with patch.object(candidate.tempfile, "mkstemp") as create, \
                    self.assertRaisesRegex(ValueError, "changed after path preflight"):
                candidate.atomic_write_report(plan, report)
            create.assert_not_called()
        self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
        self.assert_no_owned_temporary()

    def test_descriptor_ctime_and_real_content_changes_during_read_reject(self):
        original_fdopen, original_fstat = candidate.os.fdopen, candidate.os.fstat
        original_bytes = self.input.read_bytes()
        for mutation in ("ctime", "content"):
            with self.subTest(mutation=mutation):
                self.input.write_bytes(original_bytes)
                generation = 10**9
                streams = []

                def descriptor_stat(fd):
                    information = original_fstat(fd)
                    return stat_with(information, st_ctime_ns=information.st_ctime_ns + generation)

                def changing_stream(fd, mode):
                    stream = original_fdopen(fd, mode)
                    streams.append(stream)
                    original_read = stream.read

                    def read_then_change(*args):
                        nonlocal generation
                        data = original_read(*args)
                        if mutation == "ctime":
                            generation += 1
                        else:
                            self.input.write_bytes(original_bytes + b" ")
                        return data

                    stream.read = read_then_change
                    return stream

                with patch.object(candidate.os, "fstat", side_effect=descriptor_stat), \
                        patch.object(candidate.os, "fdopen", side_effect=changing_stream), \
                        self.assertRaisesRegex(ValueError, "changed while being read"):
                    candidate.load_input(self.input)
                self.assertTrue(streams)
                self.assertTrue(all(stream.closed for stream in streams))
                self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
                self.assert_no_owned_temporary()

    def test_same_bytes_replacement_after_preflight_rejects_load_and_output(self):
        plan = candidate.preflight_paths(self.input, self.output)
        data, previous = self.input.read_bytes(), self.input.stat()
        replacement = self.directory / "replacement.json"
        replacement.write_bytes(data)
        os.utime(replacement, ns=(previous.st_atime_ns, previous.st_mtime_ns))
        os.replace(replacement, self.input)
        with self.assertRaisesRegex(ValueError, "changed after path preflight"):
            candidate.load_input(plan.input_path, expected_signature=plan.input_signature)
        report = candidate.build_report(candidate.parse_input(data), 32)
        with patch.object(candidate.tempfile, "mkstemp") as create, self.assertRaises(ValueError):
            candidate.atomic_write_report(plan, report)
        create.assert_not_called()
        self.assertEqual(self.input.read_bytes(), data)
        self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
        self.assert_no_owned_temporary()

    def test_preflight_rejects_path_replacement_and_wrong_opened_file(self):
        original_open = candidate.os.open
        resolved_input = self.input.resolve()
        data = self.input.read_bytes()
        for mutation in ("replace-path", "different-descriptor"):
            with self.subTest(mutation=mutation):
                replacement = self.directory / "replacement.json"
                replacement.write_bytes(data)
                opened = []

                def substituted_open(path, flags, *args, **kwargs):
                    if path == resolved_input:
                        if mutation == "replace-path":
                            os.replace(replacement, self.input)
                        else:
                            path = replacement
                    descriptor = original_open(path, flags, *args, **kwargs)
                    opened.append(descriptor)
                    return descriptor

                with patch.object(candidate.os, "open", side_effect=substituted_open), \
                        self.assertRaisesRegex(ValueError, "changed during path preflight"):
                    candidate.preflight_paths(self.input, self.output)
                self.assertTrue(opened, "the input identity must be obtained through an actual descriptor")
                for descriptor in opened:
                    with self.assertRaises(OSError):
                        os.fstat(descriptor)
                self.assertEqual(self.input.read_bytes(), data)
                self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
                self.assert_no_owned_temporary()

    def test_path_ctime_only_change_still_rejects_preflight_and_output_recheck(self):
        original_stat, original_fstat = candidate.os.stat, candidate.os.fstat
        resolved_input = self.input.resolve()
        report = candidate.build_report(candidate.parse_input(self.input.read_bytes()), 32)
        for when in ("during-preflight", "after-preflight"):
            with self.subTest(when=when):
                generation = 0

                def path_stat(path, *args, **kwargs):
                    information = original_stat(path, *args, **kwargs)
                    if path in (self.input, resolved_input):
                        return stat_with(information, st_ctime_ns=information.st_ctime_ns + generation)
                    return information

                def descriptor_stat(fd):
                    nonlocal generation
                    information = original_fstat(fd)
                    if when == "during-preflight":
                        generation += 1
                    return information

                with patch.object(candidate.os, "stat", side_effect=path_stat), \
                        patch.object(candidate.os, "fstat", side_effect=descriptor_stat):
                    if when == "during-preflight":
                        with self.assertRaisesRegex(ValueError, "changed during path preflight"):
                            candidate.preflight_paths(self.input, self.output)
                    else:
                        plan = candidate.preflight_paths(self.input, self.output)
                        generation += 1
                        with patch.object(candidate.tempfile, "mkstemp") as create, \
                                self.assertRaisesRegex(ValueError, "changed after path preflight"):
                            candidate.atomic_write_report(plan, report)
                        create.assert_not_called()
                self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
                self.assert_no_owned_temporary()

    def test_input_descriptors_close_on_preflight_and_stream_wrapper_failures(self):
        original_open = candidate.os.open
        for operation in ("preflight-fstat", "load-fdopen"):
            with self.subTest(operation=operation):
                opened = []

                def recording_open(*args, **kwargs):
                    descriptor = original_open(*args, **kwargs)
                    opened.append(descriptor)
                    return descriptor

                failure = OSError("injected input metadata or wrapper failure")
                target = "fstat" if operation == "preflight-fstat" else "fdopen"
                with patch.object(candidate.os, "open", side_effect=recording_open), \
                        patch.object(candidate.os, target, side_effect=failure), \
                        self.assertRaisesRegex(OSError, "injected"):
                    if operation == "preflight-fstat":
                        candidate.preflight_paths(self.input, self.output)
                    else:
                        candidate.load_input(self.input)
                self.assertTrue(opened)
                for descriptor in opened:
                    try:
                        os.fstat(descriptor)
                    except OSError:
                        pass
                    else:
                        # Keep the regression itself leak-free on the old source.
                        os.close(descriptor)
                        self.fail("input descriptor leaked on rejection")
                self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
                self.assert_no_owned_temporary()

    def test_direct_alias_and_normalized_parent_alias_preserve_input(self):
        data = self.input.read_bytes()
        subdirectory = self.directory / "subdirectory"
        subdirectory.mkdir()
        for output in (self.input, subdirectory / ".." / self.input.name):
            with self.subTest(output=output):
                self.assert_rejected(self.arguments(output_path=output))
                self.assertEqual(self.input.read_bytes(), data)
        self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
        self.assert_no_owned_temporary()

    def test_hardlink_alias_is_rejected_without_replacing_either_name(self):
        alias = self.directory / "hardlink.json"
        self.facility("hard links", lambda: os.link(self.input, alias))
        data = self.input.read_bytes()
        inode = self.input.stat().st_ino
        self.assert_rejected(self.arguments(output_path=alias))
        self.assertEqual(alias.read_bytes(), data)
        self.assertEqual(self.input.read_bytes(), data)
        self.assertEqual((alias.stat().st_ino, self.input.stat().st_ino), (inode, inode))
        self.assert_no_owned_temporary()

    def test_output_symlinks_and_dangling_links_are_preserved_and_rejected(self):
        for index, target in enumerate((self.input, self.output, self.directory / "absent.json")):
            link = self.directory / f"link-{index}.json"
            self.facility("symbolic links", lambda: os.symlink(target, link))
            original_destination = os.readlink(link)
            self.assert_rejected(self.arguments(output_path=link))
            self.assertTrue(link.is_symlink())
            self.assertEqual(os.readlink(link), original_destination)
            self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
        self.assertFalse((self.directory / "absent.json").exists())
        self.assert_no_owned_temporary()

    def test_input_symlink_is_supported_but_parent_symlink_alias_is_rejected(self):
        link = self.directory / "input-link.json"
        self.facility("symbolic links", lambda: os.symlink(self.input, link))
        status, stdout, stderr = self.invoke(self.arguments(input_path=link))
        self.assertEqual((status, stdout, stderr), (0, "", ""))
        self.assertTrue(link.is_symlink())
        report = json.loads(self.output.read_bytes())
        self.assertEqual(report["input_sha256"], hashlib.sha256(self.input.read_bytes()).hexdigest())
        parent_link = self.directory / "parent-link"
        self.facility("directory symbolic links",
                      lambda: os.symlink(self.directory, parent_link, target_is_directory=True))
        previous = self.input.read_bytes()
        self.assert_rejected(self.arguments(output_path=parent_link / self.input.name))
        self.assertEqual(self.input.read_bytes(), previous)
        self.assert_no_owned_temporary()

    def test_directories_missing_inputs_parents_and_trailing_separators_do_not_create_output(self):
        missing_parent = self.directory / "missing" / "nested"
        cases = (self.arguments(input_path=self.directory),
                 self.arguments(input_path=self.directory / "absent-input.json"),
                 self.arguments(output_path=self.directory),
                 self.arguments(output_path=missing_parent / "report.json"),
                 self.arguments(output_path=str(self.directory / "new-file") + os.sep),
                 self.arguments(output_path=str(self.output) + os.sep))
        for arguments in cases:
            with self.subTest(arguments=arguments):
                self.assert_rejected(arguments)
                self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
        self.assertFalse(missing_parent.parent.exists())
        self.assertFalse((self.directory / "new-file").exists())
        self.assert_no_owned_temporary()

    @unittest.skipUnless(hasattr(os, "mkfifo"), "named FIFOs unavailable on this OS")
    def test_fifo_input_and_output_reject_without_blocking_or_replacement(self):
        fifo = self.directory / "pipe"
        self.facility("named FIFOs", lambda: os.mkfifo(fifo))
        for arguments in (self.arguments(input_path=fifo), self.arguments(output_path=fifo)):
            with self.subTest(arguments=arguments):
                self.assert_rejected(arguments, real=True)
                self.assertTrue(stat.S_ISFIFO(fifo.lstat().st_mode))
                self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
        self.assert_no_owned_temporary()

    @unittest.skipUnless(hasattr(socket, "AF_UNIX"), "Unix sockets unavailable on this OS")
    def test_socket_input_and_output_are_unsupported_special_files(self):
        endpoint = self.directory / "socket"
        server = self.facility("Unix sockets", lambda: socket.socket(socket.AF_UNIX, socket.SOCK_STREAM))
        self.addCleanup(server.close)
        self.facility("Unix socket paths", lambda: server.bind(str(endpoint)))
        for arguments in (self.arguments(input_path=endpoint), self.arguments(output_path=endpoint)):
            with self.subTest(arguments=arguments):
                self.assert_rejected(arguments)
                self.assertTrue(stat.S_ISSOCK(endpoint.lstat().st_mode))
                self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
        server.close()
        self.assert_no_owned_temporary()

    def test_file_byte_cap_and_work_budget_reject_before_output_allocation(self):
        self.input.write_bytes(encoded(fixture(0)) + b" " * 262144)
        with patch.object(candidate, "build_report") as render:
            self.assert_rejected()
            render.assert_not_called()
        self.input.write_bytes(encoded(fixture(4096)))
        with patch.object(candidate.kernel, "render") as render, \
                patch.object(candidate.tempfile, "mkstemp") as create:
            self.assert_rejected(self.arguments(factor="256"))
            render.assert_not_called()
            create.assert_not_called()
        self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
        self.assert_no_owned_temporary()

    def test_changed_input_destination_and_parent_plans_reject_before_creation(self):
        report = candidate.build_report(candidate.parse_input(encoded(fixture(0))), 32)
        for mutation in ("input", "output", "new-output"):
            with self.subTest(mutation=mutation):
                destination = self.directory / "absent-report.json" if mutation == "new-output" else self.output
                plan = candidate.preflight_paths(self.input, destination)
                if mutation == "input":
                    self.input.write_bytes(self.input.read_bytes() + b" ")
                else:
                    destination.write_bytes(PRIOR_OUTPUT + b"changed since preflight")
                prior = destination.read_bytes()
                with patch.object(candidate.tempfile, "mkstemp") as create, self.assertRaises(ValueError):
                    candidate.atomic_write_report(plan, report)
                create.assert_not_called()
                self.assertEqual(destination.read_bytes(), prior)
        parent = self.directory / "parent"
        parent.mkdir()
        destination = parent / "report.json"
        plan = candidate.preflight_paths(self.input, destination)
        parent.rename(self.directory / "old-parent")
        parent.mkdir()
        with self.assertRaises(ValueError):
            candidate.atomic_write_report(plan, report)
        self.assertFalse(destination.exists())
        self.assert_no_owned_temporary()

    def test_partial_write_flush_fsync_and_replace_failures_clean_only_owned_temporary(self):
        report = candidate.build_report(candidate.parse_input(self.input.read_bytes()), 32)
        original_fdopen = candidate.os.fdopen

        class FaultyStream:
            def __init__(self, descriptor, mode, operation):
                self.stream = original_fdopen(descriptor, mode)
                self.operation = operation

            def __enter__(self):
                return self

            def __exit__(self, *exception):
                self.stream.close()

            def write(self, payload):
                if self.operation == "write":
                    self.stream.write(payload[:37])
                    raise OSError("injected partial write failure")
                return self.stream.write(payload)

            def flush(self):
                if self.operation == "flush":
                    raise OSError("injected flush failure")
                return self.stream.flush()

            def fileno(self):
                return self.stream.fileno()

        for existing in (False, True):
            destination = self.output if existing else self.directory / "new-report.json"
            for operation in ("write", "flush", "fsync", "replace"):
                with self.subTest(existing=existing, operation=operation):
                    plan = candidate.preflight_paths(self.input, destination)
                    if operation in ("write", "flush"):
                        injected = patch.object(candidate.os, "fdopen",
                                                side_effect=lambda fd, mode: FaultyStream(fd, mode, operation))
                    else:
                        injected = patch.object(candidate.os, operation,
                                                side_effect=OSError("injected " + operation + " failure"))
                    with injected, self.assertRaises(OSError):
                        candidate.atomic_write_report(plan, report)
                    self.assertEqual(destination.exists(), existing)
                    if existing:
                        self.assertEqual(destination.read_bytes(), PRIOR_OUTPUT)
                    self.assert_no_owned_temporary()
                    self.assertEqual(self.unrelated.read_bytes(), b"not owned by this invocation")

    def test_destination_changed_during_write_is_preserved_and_temporary_removed(self):
        report = candidate.build_report(candidate.parse_input(self.input.read_bytes()), 32)
        plan = candidate.preflight_paths(self.input, self.output)
        replacement = b"independent writer's new artifact"
        with patch.object(candidate.os, "fsync", side_effect=lambda fd: self.output.write_bytes(replacement)), \
                self.assertRaises(ValueError):
            candidate.atomic_write_report(plan, report)
        self.assertEqual(self.output.read_bytes(), replacement)
        self.assert_no_owned_temporary()

    def test_nonfinite_unknown_missing_and_oversize_reports_never_open_output(self):
        report = candidate.build_report(candidate.parse_input(self.input.read_bytes()), 32)
        invalid = []
        for member in ROOT_FIELDS:
            item = copy.deepcopy(report)
            del item[member]
            invalid.append(("missing " + member, item))
        invalid.append(("unknown root", dict(report, extra=0)))
        for value in (math.nan, math.inf, -math.inf):
            item = copy.deepcopy(report)
            item["samples"] = [value]
            invalid.append(("nonfinite " + str(value), item))
        invalid.append(("unsupported numeric type", dict(report, raw_bound=Fraction(1, 2))))
        plan = candidate.preflight_paths(self.input, self.output)
        with patch.object(candidate.tempfile, "mkstemp") as create:
            for label, item in invalid:
                with self.subTest(case=label), self.assertRaises(ValueError):
                    candidate.atomic_write_report(plan, item)
            # Reduce only the storage cap to inject this expensive boundary;
            # the real 32-MiB value is independently asserted in report tests.
            with patch.object(candidate, "MAX_REPORT_BYTES", 128), self.assertRaises(ValueError):
                candidate.atomic_write_report(plan, report)
            create.assert_not_called()
        self.assertEqual(self.output.read_bytes(), PRIOR_OUTPUT)
        self.assert_no_owned_temporary()

    def test_real_cli_small_render_hash_schema_tails_and_atomic_success(self):
        data = encoded(fixture()) + b" \n"
        self.input.write_bytes(data)
        status, stdout, stderr = self.invoke(real=True)
        self.assertEqual((status, stdout, stderr), (0, "", ""))
        payload = self.output.read_bytes()
        report = json.loads(payload)
        self.assertEqual(set(report), ROOT_FIELDS)
        self.assertEqual(report["input_sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(report["implementation_sha256"], own_hashes())
        self.assertEqual((report["frames"], report["factor"], report["first_frame"]), (24, 32, -16))
        self.assertEqual(len(report["samples"]), 57)
        self.assertEqual((report["samples"][0], report["samples"][-1]), (0.0, 0.0))
        self.assertGreater(max(abs(value) for value in report["samples"]), 0.5)
        self.assertEqual(report["time_offset_seconds"], -16 / 48000)
        self.assertEqual(report["observations"]["report_bytes"], len(payload))
        self.assertEqual(report["observations"]["input_bytes"], len(data))
        self.assertEqual(report["work"], 66389)
        self.assertEqual(report["observations"]["cell_count"], 769)
        self.assertEqual(report["observations"]["fir_product_bound"], 58425)
        self.assertEqual(len(report["edges"]), 9)
        self.assertEqual(report["gate_jumps"][-1]["value_jump"], -1.0)
        self.assertEqual(self.input.read_bytes(), data)
        self.assertTrue(payload.endswith(b"\n"))
        self.assert_no_owned_temporary()


class ReportSemanticsTests(unittest.TestCase):
    def build(self, document=None, factor=32):
        document = fixture() if document is None else document
        return candidate.build_report(candidate.parse_input(encoded(document)), factor)

    def assert_finite_and_canonical(self, value):
        if isinstance(value, dict):
            for item in value.values():
                self.assert_finite_and_canonical(item)
        elif isinstance(value, list):
            for item in value:
                self.assert_finite_and_canonical(item)
        elif type(value) is float:
            self.assertTrue(math.isfinite(value))
            if value == 0:
                self.assertEqual(math.copysign(1.0, value), 1.0)

    def test_report_exact_keys_finite_values_hashes_caps_and_measurement_eligibility(self):
        report = self.build()
        self.assertEqual(set(report), ROOT_FIELDS)
        self.assertEqual((report["schema_version"], report["model_id"], report["evidence_class"]),
                         (1, "fractional-contact-reference-v1", "synthetic"))
        self.assertEqual(report["implementation_sha256"], own_hashes())
        for edge in report["edges"]:
            self.assertEqual(set(edge), EDGE_FIELDS)
            self.assertEqual(set(edge["exact_u"]), {"numerator", "denominator"})
            self.assertIs(type(edge["closed_after"]), bool)
            self.assertIs(type(edge["inside_observation"]), bool)
            self.assertGreaterEqual(edge["fraction"], 0)
            self.assertLess(edge["fraction"], 1)
        for target in report["targets"]:
            self.assertEqual(set(target), TARGET_FIELDS)
        for final in report["final_keys"]:
            self.assertEqual(set(final), FINAL_FIELDS)
        self.assertEqual(set(report["filter"]), FILTER_FIELDS)
        self.assertEqual((report["filter"]["H"], report["filter"]["beta"],
                          report["filter"]["coefficient_count"]), (16, 0.45, 1025))
        self.assertRegex(report["filter"]["coefficient_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(report["caps"], {
            "input_bytes": 262144, "json_depth": 12, "invocation_work": 20_000_000,
            "suite_elapsed_seconds": 300, "suite_peak_resident_bytes": 268435456,
            "suite_fir_products": 180_000_000, "suite_oracle_integrand_evaluations": 10_000_000,
            "suite_report_bytes": 33554432,
        })
        observations = report["observations"]
        self.assertGreaterEqual(observations["elapsed_seconds"], 0)
        self.assertTrue(observations["elapsed_measurement"])
        if observations["peak_resident_bytes"] is None:
            self.assertTrue(observations["peak_resident_unavailable_reason"])
            self.assertIn("ineligible", observations["resource_gate_status"])
        else:
            self.assertGreater(observations["peak_resident_bytes"], 0)
            self.assertTrue(observations["peak_resident_measurement"])
        self.assert_finite_and_canonical(report)
        before = copy.deepcopy(report)
        payload = candidate.encode_report(report)
        self.assertEqual(report, before, "serialization must not mutate the computed report")
        self.assertEqual(json.loads(payload)["observations"]["report_bytes"], len(payload))

    def test_target_ordinals_and_key_contact_order_are_independent_of_identifier_sort(self):
        document = fixture()
        document["keys"].insert(0, dict(document["keys"][0], key_id="Z"))
        document["targets"] = [
            {"frame": 24, "fraction": 0.0, "key_id": "A", "target": 0.0},
            {"frame": 0, "fraction": 0.0, "key_id": "A", "target": 1.0},
            {"frame": 12, "fraction": 0.0, "key_id": "Z", "target": 0.0},
            {"frame": 0, "fraction": 0.0, "key_id": "Z", "target": 1.0},
            {"frame": 0, "fraction": 0.0, "key_id": "Z", "target": 0.5},
            {"frame": 0, "fraction": 0.0, "key_id": "Z", "target": 1.0},
        ]
        report = self.build(document)
        self.assertEqual([row["input_ordinal"] for row in report["targets"]], [1, 3, 4, 5, 2, 0])
        self.assertEqual([row["key_id"] for row in report["final_keys"]], ["Z", "A"])
        expected = [(Fraction(375, 64), key, contact, True)
                    for key in (0, 1) for contact in range(9)]
        expected += [(Fraction(2661, 128), 0, contact, False) for contact in range(9)]
        self.assertEqual(len(report["edges"]), len(expected))
        for edge, (u, key, contact, closed) in zip(report["edges"], expected):
            self.assertEqual(edge["exact_u"], exact_coordinate(u))
            self.assertEqual((edge["key_index"], edge["contact_index"], edge["closed_after"]),
                             (key, contact, closed))
        self.assertEqual(report["final_keys"][0]["closed"], [False] * 9)
        self.assertEqual(report["final_keys"][1]["closed"], [True] * 9)
        self.assertEqual(report["final_keys"][1]["target"], 0.0)

    def test_distinct_exact_roots_with_identical_display_keep_exact_identity_and_order(self):
        document = fixture(1)
        smallest = math.ulp(0.0)
        document["keys"][0]["on"] = [2 * smallest, smallest] + [0.5] * 7
        document["keys"][0]["off"] = [0.0] * 9
        document["keys"][0]["gains"] = [0.0] * 9
        document["targets"][0]["fraction"] = 0.5
        report = self.build(document)
        self.assertEqual(len(report["edges"]), 2)
        self.assertEqual([edge["contact_index"] for edge in report["edges"]], [1, 0])
        coordinates = [Fraction(1, 2) + Fraction(375, 32) * Fraction.from_float(threshold)
                       for threshold in (smallest, 2 * smallest)]
        self.assertLess(coordinates[0], coordinates[1])
        self.assertEqual([edge["exact_u"] for edge in report["edges"]],
                         [exact_coordinate(value) for value in coordinates])
        self.assertEqual([(edge["frame"], edge["fraction"]) for edge in report["edges"]],
                         [(0, 0.5), (0, 0.5)])
        self.assertEqual(report["samples"], [0.0] * 34)

    def test_empty_flush_validates_all_factors_retains_last_targets_and_has_no_filter(self):
        document = fixture(0)
        document["targets"].append(dict(document["targets"][0], target=0.25))
        with patch.object(candidate.kernel, "filter_metadata") as filter_metadata:
            for factor in (32, 64, 128, 256):
                with self.subTest(factor=factor):
                    report = self.build(document, factor)
                    self.assertEqual(set(report), ROOT_FIELDS)
                    self.assertEqual((report["factor"], report["first_frame"], report["time_offset_seconds"]),
                                     (factor, 0, 0.0))
                    self.assertEqual((report["samples"], report["edges"], report["gate_jumps"]), ([], [], []))
                    self.assertIsNone(report["filter"])
                    self.assertEqual((report["raw_bound"], report["output_bound"], report["work"]), (1.0, 0.0, 13))
                    self.assertEqual(report["final_keys"], [{"key_id": "A", "position": 0.0,
                                                            "target": 0.25, "closed": [False] * 9}])
                    self.assertEqual([row["input_ordinal"] for row in report["targets"]], [0, 1])
                    for field in ("cell_count", "filter_coefficient_count", "fir_product_bound",
                                  "sample_count", "edge_count", "observed_sample_peak"):
                        self.assertEqual(report["observations"][field], 0)
                    self.assert_finite_and_canonical(report)
            filter_metadata.assert_not_called()
        for factor in (0, 33, True, 32.0, "32", None):
            with self.subTest(factor=factor), self.assertRaises(ValueError):
                self.build(document, factor)

    def test_terminal_break_uses_ungated_left_limit_for_value_and_per_second_slope(self):
        # Release starts 1125/128 frames before N, placing the .25 break at N.
        for frequency in (0.0, 1000.0):
            with self.subTest(frequency=frequency):
                document = fixture()
                document["sources"][0].update(frequency_hz=frequency, phase_turns=0.125)
                document["targets"].append({"frame": 15, "fraction": 27 / 128,
                                             "key_id": "A", "target": 0.0})
                report = self.build(document)
                terminal = report["edges"][-9:]
                self.assertEqual(len(report["edges"]), 18)
                for edge in terminal:
                    self.assertEqual(edge["exact_u"], exact_coordinate(24))
                    self.assertEqual((edge["frame"], edge["fraction"], edge["closed_after"],
                                      edge["inside_observation"]), (24, 0.0, False, False))
                sign = 1.0 if frequency == 0 else -1.0
                value = sign * math.sqrt(0.5)
                slope = sign * 2 * math.pi * frequency * math.sqrt(0.5)
                gate = report["gate_jumps"][-1]
                self.assertEqual(gate["boundary"], "end")
                self.assertEqual(gate["exact_u"], exact_coordinate(24))
                self.assertEqual(gate["limit"], "negative_ungated_left_limit")
                self.assertAlmostEqual(gate["value_jump"], -value, delta=2e-12)
                self.assertAlmostEqual(gate["slope_jump_per_second"], -slope,
                                       delta=2e-10 * max(1, 2 * math.pi * frequency))
                self.assertAlmostEqual(terminal[0]["value_jump"], -value, delta=2e-12)
                self.assertAlmostEqual(terminal[0]["slope_jump_per_second"], -slope,
                                       delta=2e-10 * max(1, 2 * math.pi * frequency))
                self.assertEqual(report["final_keys"][0]["closed"], [False] * 9)
                self.assert_finite_and_canonical(report)

    def test_terminal_make_is_ledger_only_and_does_not_create_an_audible_gate_jump(self):
        document = fixture()
        document["targets"] = [{"frame": 18, "fraction": 9 / 64, "key_id": "A", "target": 1.0},
                               {"frame": 24, "fraction": 0.0, "key_id": "A", "target": 0.0}]
        report = self.build(document)
        self.assertEqual(len(report["edges"]), 9)
        for edge in report["edges"]:
            self.assertEqual(edge["exact_u"], exact_coordinate(24))
            self.assertTrue(edge["closed_after"])
            self.assertFalse(edge["inside_observation"])
        self.assertEqual(report["gate_jumps"][-1]["value_jump"], 0.0)
        self.assertEqual(report["gate_jumps"][-1]["slope_jump_per_second"], 0.0)
        self.assertEqual(report["samples"], [0.0] * 57)
        self.assertEqual(report["final_keys"][0], {"key_id": "A", "position": 0.5,
                                                  "target": 0.0, "closed": [True] * 9})

    def test_implementation_change_and_unavailable_resource_measurement_are_not_qualified(self):
        document = candidate.parse_input(encoded(fixture(0)))
        expected = own_hashes()
        altered = dict(expected, **{"tools/contact_switching_io.py": "0" * 64})
        with self.assertRaisesRegex(ValueError, "implementation changed"):
            candidate.build_report(document, 32, source_hashes=altered)
        with patch.object(candidate, "implementation_hashes", side_effect=(expected, altered)), \
                self.assertRaisesRegex(ValueError, "implementation changed"):
            candidate.build_report(document, 32)
        with patch.object(candidate, "_peak_resident", return_value=(None, "unavailable", "injected unavailable OS counter")):
            report = candidate.build_report(document, 32)
        observations = report["observations"]
        self.assertIsNone(observations["peak_resident_bytes"])
        self.assertEqual(observations["peak_resident_unavailable_reason"], "injected unavailable OS counter")
        self.assertIn("ineligible", observations["resource_gate_status"])


if __name__ == "__main__":
    unittest.main()
