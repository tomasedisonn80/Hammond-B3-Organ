#!/usr/bin/env python3
"""Independent acceptance for the shared offline capture JSON contract.

Run directly with Python 3.10+ or CTest's python_test_capture_common. Fixtures
are literal bytes or separately constructed Python values, never saved producer
output. Controlled filesystem faults test observations, not adversarial race
protection or hardware evidence. Only the standard library is required.
"""

from __future__ import annotations

import copy
from decimal import Decimal
import errno
import hashlib
import importlib.util
import math
import os
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


REPOSITORY = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "capture_common_acceptance_subject", REPOSITORY / "tools" / "capture_common.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Cannot load the shared capture JSON implementation")
common = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(common)


# Written from the documented sorting, indentation, escaping and UTF-8 rules.
# No serializer, producer-generated snapshot or production digest builds this.
CANONICAL_VALUE = {
    "z": {},
    "q": 'line\nquote"slash\\',
    "b": "\u00e9\U0001f600",
    "a": [1, True, None, -0.0],
}
CANONICAL_BYTES = (
    b'{\n'
    b'  "a": [\n'
    b'    1,\n'
    b'    true,\n'
    b'    null,\n'
    b'    -0.0\n'
    b'  ],\n'
    b'  "b": "\xc3\xa9\xf0\x9f\x98\x80",\n'
    b'  "q": "line\\nquote\\"slash\\\\",\n'
    b'  "z": {}\n'
    b'}\n'
)
RAW_JSON_BYTES = b' \r\n{ "z": 2, "a": "\\u00e9" }\t\n'
SENTINEL_BYTES = b'\x00existing input\xff\r\n'


def nested_lists(container_depth):
    """A root list is depth zero; the innermost list contains one scalar."""
    result = 0
    for _ in range(container_depth + 1):
        result = [result]
    return result


def changed_stat(info, **changes):
    fields = {
        name: getattr(info, name)
        for name in (
            "st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns", "st_ctime_ns"
        )
    }
    fields["st_file_attributes"] = getattr(info, "st_file_attributes", 0)
    fields.update(changes)
    return SimpleNamespace(**fields)


class StreamHook:
    """Wrap an actual owned stream while injecting one controlled operation."""

    def __init__(self, stream, operations):
        self.stream = stream
        self.operations = operations

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.stream.__exit__(*args)

    def __getattr__(self, name):
        if name in self.operations:
            operation = self.operations[name]
            return lambda *args, **kwargs: operation(self.stream, *args, **kwargs)
        return getattr(self.stream, name)


def stream_factory(operations, streams=None):
    real_fdopen = os.fdopen

    def open_stream(*args, **kwargs):
        stream = real_fdopen(*args, **kwargs)
        if streams is not None:
            streams.append(stream)
        return StreamHook(stream, operations)

    return open_stream


class CaptureCommonAcceptance(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="capture-common-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def source(self, payload=b"{}", name="input.json"):
        path = self.root / name
        path.write_bytes(payload)
        return path

    def require_hard_links(self):
        source = self.source(b"probe", "hard-link-source")
        target = self.root / "hard-link-target"
        try:
            os.link(source, target)
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"Temporary filesystem cannot create hard links: {exc}")
        finally:
            source.unlink(missing_ok=True)
            target.unlink(missing_ok=True)

    def symlink(self, target, link, *, is_directory=False):
        try:
            link.symlink_to(target, target_is_directory=is_directory)
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"Symlink creation is unavailable in this environment: {exc}")

    def assert_closed(self, descriptor):
        with self.assertRaises(OSError) as raised:
            os.fstat(descriptor)
        self.assertEqual(raised.exception.errno, errno.EBADF)

    def test_error_is_a_value_error(self):
        self.assertTrue(issubclass(common.DataError, ValueError))

    def test_read_bytes_preserves_every_byte_and_exact_limit(self):
        payload = b"\x00abc\xff\r\n"
        source = self.source(payload)
        self.assertEqual(common.read_bytes(source, max_bytes=len(payload)), payload)
        self.assertEqual(common.read_bytes(str(source), max_bytes=len(payload)), payload)
        with self.assertRaises(common.DataError):
            common.read_bytes(source, max_bytes=len(payload) - 1)
        self.assertEqual(source.read_bytes(), payload)
        empty = self.source(b"", "empty")
        self.assertEqual(common.read_bytes(empty, max_bytes=1), b"")

    def test_read_json_identity_belongs_to_the_exact_parsed_bytes(self):
        source = self.source(RAW_JSON_BYTES)
        value, identity = common.read_json(source)
        self.assertEqual(value, {"a": "\u00e9", "z": 2})
        self.assertEqual(identity, {
            "sha256": hashlib.sha256(RAW_JSON_BYTES).hexdigest(),
            "size_bytes": len(RAW_JSON_BYTES),
        })
        compact = b'{"a":"\xc3\xa9","z":2}'
        other, other_identity = common.read_json(self.source(compact, "other.json"))
        self.assertEqual(other, value)
        self.assertNotEqual(other_identity["sha256"], identity["sha256"])
        self.assertEqual(source.read_bytes(), RAW_JSON_BYTES)

    def test_read_json_forwards_each_bound_and_preserves_rejected_input(self):
        payload = b"[[1]]"
        source = self.source(payload)
        for limits in (
            {"max_bytes": 4}, {"max_nodes": 2}, {"max_depth": 0}, {"max_number": 0.5}
        ):
            with self.subTest(limits=limits), self.assertRaises(common.DataError):
                common.read_json(source, **limits)
        self.assertEqual(common.read_json(
            source, max_bytes=5, max_nodes=3, max_depth=1, max_number=1
        )[0], [[1]])
        self.assertEqual(source.read_bytes(), payload)

    def test_invalid_byte_limits_reject_before_opening(self):
        invalid = (0, -1, 16777217, True, False, 1.0, "1", None)
        with mock.patch.object(common.os, "open") as opening:
            for bound in invalid:
                with self.subTest(bound=bound), self.assertRaises(common.DataError):
                    common.read_bytes(self.root / "absent", max_bytes=bound)
            opening.assert_not_called()
        for bound in invalid:
            with self.subTest(parser_bound=bound), self.assertRaises(common.DataError):
                common.parse_json_bytes(b"0", max_bytes=bound)
        self.assertEqual(common.parse_json_bytes(b"0", max_bytes=1), 0)
        self.assertEqual(common.parse_json_bytes(b"0", max_bytes=16777216), 0)
        with self.assertRaises(common.DataError):
            common.parse_json_bytes(b"0 ", max_bytes=1)

    def test_large_observed_size_rejects_without_open_or_large_allocation(self):
        source = self.source(b"0")
        observed = changed_stat(source.stat(), st_size=16777217)
        with mock.patch.object(Path, "lstat", return_value=observed), \
                mock.patch.object(common.os, "open") as opening:
            with self.assertRaises(common.DataError):
                common.read_bytes(source, max_bytes=16777216)
            opening.assert_not_called()

    def test_missing_directory_and_invalid_paths_are_controlled_rejections(self):
        directory = self.root / "directory"
        directory.mkdir()
        for path in (self.root / "missing", directory, None, 3, b"file", "\x00"):
            with self.subTest(path=repr(path)), self.assertRaises(common.DataError):
                common.read_bytes(path)

    def test_leaf_and_dangling_symlinks_reject_but_parent_aliases_are_allowed(self):
        source = self.source(b"42")
        leaf = self.root / "leaf-link"
        self.symlink(source, leaf)
        dangling = self.root / "dangling-link"
        self.symlink(self.root / "missing", dangling)
        for path in (leaf, dangling):
            with self.subTest(path=path.name), self.assertRaises(common.DataError):
                common.read_bytes(path)
        directory = self.root / "real-directory"
        directory.mkdir()
        (directory / "value").write_bytes(b"42")
        alias = self.root / "parent-alias"
        self.symlink(directory, alias, is_directory=True)
        self.assertEqual(common.read_bytes(alias / "value"), b"42")
        self.assertEqual(source.read_bytes(), b"42")

    def test_fifo_rejects_before_any_open(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("This platform has no os.mkfifo capability")
        fifo = self.root / "fifo"
        try:
            os.mkfifo(fifo)
        except (NotImplementedError, OSError) as exc:
            self.skipTest(f"Temporary filesystem cannot create a FIFO: {exc}")
        with mock.patch.object(common.os, "open") as opening:
            with self.assertRaises(common.DataError):
                common.read_bytes(fifo)
            opening.assert_not_called()

    def test_observed_reparse_attribute_rejects_before_open(self):
        source = self.source()
        reparse = 0x400
        observed = changed_stat(source.stat(), st_file_attributes=reparse)
        with mock.patch.object(Path, "lstat", return_value=observed), \
                mock.patch.object(stat, "FILE_ATTRIBUTE_REPARSE_POINT", reparse, create=True), \
                mock.patch.object(common.os, "open") as opening:
            with self.assertRaises(common.DataError):
                common.read_bytes(source)
            opening.assert_not_called()

    def test_opened_descriptor_must_itself_be_bounded_and_regular(self):
        source = self.source(b"{}")
        observed = source.stat()
        for changed in (
            changed_stat(observed, st_mode=stat.S_IFDIR),
            changed_stat(observed, st_size=3),
        ):
            with self.subTest(observation=changed), \
                    mock.patch.object(common.os, "fstat", return_value=changed), \
                    self.assertRaises(common.DataError):
                common.read_bytes(source, max_bytes=2)
        self.assertEqual(source.read_bytes(), b"{}")

    def test_posix_opened_identity_must_match_the_observed_path(self):
        if os.name != "posix":
            self.skipTest("Pre-open path/descriptor inode comparison is POSIX-specific")
        source = self.source()
        observed = source.stat()
        for field in ("st_dev", "st_ino"):
            changed = changed_stat(observed, **{field: getattr(observed, field) + 1})
            with self.subTest(field=field), \
                    mock.patch.object(common.os, "fstat", return_value=changed), \
                    self.assertRaises(common.DataError):
                common.read_bytes(source)

    def test_each_observed_descriptor_change_rejects(self):
        source = self.source(SENTINEL_BYTES)
        observed = source.stat()
        for field in ("st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns", "st_ctime_ns"):
            changed = changed_stat(observed, **{field: getattr(observed, field) + 1})
            with self.subTest(field=field), \
                    mock.patch.object(common.os, "fstat", side_effect=[observed, changed]), \
                    self.assertRaises(common.DataError):
                common.read_bytes(source)
        self.assertEqual(source.read_bytes(), SENTINEL_BYTES)

    def test_each_observed_path_change_or_disappearance_rejects(self):
        source = self.source(SENTINEL_BYTES)
        observed = source.lstat()
        changes = [
            changed_stat(observed, **{field: getattr(observed, field) + 1})
            for field in ("st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns", "st_ctime_ns")
        ]
        changes.append(FileNotFoundError("injected path disappearance"))
        for index, changed in enumerate(changes):
            with self.subTest(change=index), \
                    mock.patch.object(Path, "lstat", side_effect=[observed, changed]), \
                    self.assertRaises(common.DataError):
                common.read_bytes(source)
        self.assertEqual(source.read_bytes(), SENTINEL_BYTES)

    def test_short_or_excessive_read_is_rejected_and_read_request_is_bounded(self):
        source = self.source(b"{}")
        requests = []
        for returned in (b"{", b"{}xxx"):
            def read_operation(stream, requested):
                requests.append(requested)
                return returned
            with self.subTest(returned=returned), \
                    mock.patch.object(common.os, "fdopen", side_effect=stream_factory({"read": read_operation})), \
                    self.assertRaises(common.DataError):
                common.read_bytes(source, max_bytes=4)
        self.assertEqual(requests, [5, 5])
        self.assertEqual(source.read_bytes(), b"{}")

    def test_open_and_read_os_errors_become_data_errors(self):
        source = self.source()
        with mock.patch.object(common.os, "open", side_effect=OSError("injected open failure")), \
                self.assertRaises(common.DataError):
            common.read_bytes(source)

        def fail_read(stream, requested):
            raise OSError("injected read failure")

        streams = []
        with mock.patch.object(common.os, "fdopen", side_effect=stream_factory({"read": fail_read}, streams)), \
                self.assertRaises(common.DataError):
            common.read_bytes(source)
        self.assertTrue(streams[0].closed)

    def test_read_fdopen_failure_closes_the_owned_descriptor(self):
        source = self.source()
        real_open = os.open
        descriptors = []

        def capture_open(*args, **kwargs):
            descriptor = real_open(*args, **kwargs)
            descriptors.append(descriptor)
            return descriptor

        try:
            with mock.patch.object(common.os, "open", side_effect=capture_open), \
                    mock.patch.object(common.os, "fdopen", side_effect=OSError("injected fdopen failure")), \
                    self.assertRaises(common.DataError):
                common.read_bytes(source)
            self.assertEqual(len(descriptors), 1)
            self.assert_closed(descriptors[0])
        finally:
            for descriptor in descriptors:
                try:
                    os.close(descriptor)
                except OSError:
                    pass

    def test_parser_requires_exact_bytes_and_valid_json_grammar(self):
        class BytesSubclass(bytes):
            pass

        invalid = (
            "{}", bytearray(b"{}"), memoryview(b"{}"), BytesSubclass(b"{}"), None,
            b"", b" ", b"{}{}", b"{", b"[1,]", b"{'a': 1}", b"01", b"+1",
            b".5", b"1.", b'"literal\nnewline"', b"true false", b"// comment\n0",
        )
        for payload in invalid:
            with self.subTest(payload=repr(payload)), self.assertRaises(common.DataError):
                common.parse_json_bytes(payload)

    def test_duplicate_keys_reject_at_every_relevant_depth_and_after_unescaping(self):
        payloads = (
            b'{"a":1,"a":2}',
            b'{"outer":{"a":1,"a":2}}',
            b'[{"outer":[{"a":1,"a":2}]}]',
            b'{"a":1,"\\u0061":2}',
            b'{"\\ud83d\\ude00":1,"\xf0\x9f\x98\x80":2}',
        )
        for payload in payloads:
            with self.subTest(payload=payload), self.assertRaises(common.DataError):
                common.parse_json_bytes(payload)
        self.assertEqual(common.parse_json_bytes(b'[{"a":1},{"a":2}]'), [{"a": 1}, {"a": 2}])

    def test_bom_invalid_utf8_and_unpaired_surrogates_reject(self):
        payloads = (
            b"\xef\xbb\xbf{}", b"\xff", b'"\xc0\xaf"', b'"\xed\xa0\x80"',
            b'"\\ud800"', b'"\\udfff"', b'{"\\ud800":0}', b'"\\ud800x"',
        )
        for payload in payloads:
            with self.subTest(payload=payload), self.assertRaises(common.DataError):
                common.parse_json_bytes(payload)
        self.assertEqual(common.parse_json_bytes(b'"\\ud83d\\ude00"'), "\U0001f600")
        self.assertEqual(common.parse_json_bytes(b'"\xef\xbb\xbf"'), "\ufeff")

    def test_valid_unicode_is_not_normalized_or_ascii_escaped(self):
        value = common.parse_json_bytes(b'{"e\\u0301":"\xc3\xa9","\\u00e9":"e\\u0301"}')
        self.assertEqual(value, {"e\u0301": "\u00e9", "\u00e9": "e\u0301"})
        self.assertEqual(len(value), 2)
        self.assertEqual(common.canonical_json_bytes("\u00e9\U0001f600"), b'"\xc3\xa9\xf0\x9f\x98\x80"\n')

    def test_nonfinite_and_excessive_numeric_tokens_reject(self):
        payloads = (
            b"NaN", b"Infinity", b"-Infinity", b"1e309", b"-1e309",
            b"1e101", b"-1e101", b"1000000000001", b"-1000000000001",
            b'{"outer":[NaN]}', b"[1.000000000001e12]",
        )
        for payload in payloads:
            with self.subTest(payload=payload), self.assertRaises(common.DataError):
                common.parse_json_bytes(payload)
        self.assertEqual(common.parse_json_bytes(b"[-1000000000000,1000000000000]"), [-10**12, 10**12])
        self.assertEqual(common.parse_json_bytes(b"1e100", max_number=1e100), 1e100)

    def test_numeric_token_limit_counts_the_literal_spelling(self):
        accepted = (
            (b"1" + b"0" * 63, 10**63),
            (b"0." + b"0" * 61 + b"1", 1e-62),
            (b"1e" + b"0" * 61 + b"1", 10.0),
        )
        for token, expected in accepted:
            self.assertEqual(len(token), 64)
            with self.subTest(token=token):
                self.assertEqual(common.parse_json_bytes(token, max_number=1e100), expected)
        for token in (b"1" + b"0" * 64, b"0." + b"0" * 62 + b"1", b"1e" + b"0" * 62 + b"1"):
            self.assertEqual(len(token), 65)
            with self.subTest(token=token), self.assertRaises(common.DataError):
                common.parse_json_bytes(token, max_number=1e100)

    def test_scalar_types_boolean_and_negative_zero_are_preserved(self):
        cases = ((b"null", None, type(None)), (b"true", True, bool),
                 (b"false", False, bool), (b"1", 1, int), (b"1.0", 1.0, float))
        for payload, expected, expected_type in cases:
            value = common.parse_json_bytes(payload)
            self.assertEqual(value, expected)
            self.assertIs(type(value), expected_type)
        self.assertEqual(math.copysign(1.0, common.parse_json_bytes(b"-0.0")), -1.0)
        self.assertIs(common.parse_json_bytes(b"true", max_number=0.1), True)

    def test_direct_values_admit_only_exact_json_types_without_mutation(self):
        value = {"data": [None, False, True, 1, -2.5, "\u00e9", {"": []}]}
        before = copy.deepcopy(value)
        self.assertIsNone(common.validate_json_value(value))
        self.assertEqual(value, before)

        class IntSubclass(int):
            pass

        class StringSubclass(str):
            pass

        class FloatSubclass(float):
            pass

        class ListSubclass(list):
            pass

        class DictSubclass(dict):
            pass

        invalid = (
            (), (1,), {1}, b"text", bytearray(b"text"), memoryview(b"text"),
            Decimal("1"), 1 + 0j, object(), IntSubclass(1), FloatSubclass(1.0), StringSubclass("s"),
            ListSubclass([1]), DictSubclass(a=1),
        )
        for item in invalid:
            with self.subTest(kind=type(item).__name__):
                with self.assertRaises(common.DataError):
                    common.validate_json_value({"nested": [item]})
                with self.assertRaises(common.DataError):
                    common.canonical_json_bytes({"nested": [item]})

    def test_direct_keys_and_surrogate_strings_are_rejected_without_coercion(self):
        class StringSubclass(str):
            pass

        for key in (1, True, None, ("a",), StringSubclass("a"), "\ud800"):
            value = {key: "value"}
            before_items = list(value.items())
            with self.subTest(key=repr(key)), self.assertRaises(common.DataError):
                common.validate_json_value(value)
            self.assertEqual(list(value.items()), before_items)
            with self.assertRaises(common.DataError):
                common.canonical_json_bytes(value)
        for text in ("\ud800", "\udfff", "a\ud800b", "\ud83d\ude00"):
            with self.subTest(text=repr(text)), self.assertRaises(common.DataError):
                common.validate_json_value([text])

    def test_direct_numeric_bounds_are_inclusive_and_boolean_is_separate(self):
        self.assertIsNone(common.validate_json_value([-9, 9], max_number=9))
        self.assertIsNone(common.validate_json_value([-3.5, 3.5], max_number=3.5))
        self.assertIsNone(common.validate_json_value([True, False, 0], max_number=5e-324))
        for number in (10, -10, math.inf, -math.inf, math.nan, 10**400):
            with self.subTest(number=number), self.assertRaises(common.DataError):
                common.validate_json_value(number, max_number=9)
        for number in (math.nextafter(3.5, math.inf), math.nextafter(-3.5, -math.inf)):
            with self.subTest(number=number), self.assertRaises(common.DataError):
                common.validate_json_value(number, max_number=3.5)

    def test_resource_option_edges_use_small_values(self):
        limits = {
            "max_nodes": (0, -1, 1048577, True, 1.0, "1", None),
            "max_depth": (-1, 129, True, 1.0, "1", None),
            "max_number": (0, -1, True, False, math.inf, -math.inf, math.nan, 1e101, 10**400, "1", None),
        }
        for field, invalid in limits.items():
            for bound in invalid:
                with self.subTest(field=field, bound=bound):
                    with self.assertRaises(common.DataError):
                        common.validate_json_value(None, **{field: bound})
                    with self.assertRaises(common.DataError):
                        common.parse_json_bytes(b"null", **{field: bound})
        self.assertIsNone(common.validate_json_value(None, max_nodes=1, max_depth=0, max_number=5e-324))
        self.assertIsNone(common.validate_json_value(None, max_nodes=1048576, max_depth=128, max_number=1e100))

    def test_value_node_counts_include_containers_and_exclude_object_keys(self):
        value = {"a": [0], "b": None}
        self.assertIsNone(common.validate_json_value(value, max_nodes=4))
        with self.assertRaises(common.DataError):
            common.validate_json_value(value, max_nodes=3)
        self.assertEqual(common.parse_json_bytes(b'{"a":[0],"b":null}', max_nodes=4), value)
        with self.assertRaises(common.DataError):
            common.parse_json_bytes(b'{"a":[0],"b":null}', max_nodes=3)
        shared = [0]
        self.assertIsNone(common.validate_json_value([shared, shared], max_nodes=5))
        with self.assertRaises(common.DataError):
            common.validate_json_value([shared, shared], max_nodes=4)
        with self.assertRaises(common.DataError):
            common.validate_json_value([None] * 9, max_nodes=9)

    def test_container_depth_has_root_zero_and_scalar_leaves_do_not_add_depth(self):
        for value in (None, 1, "x", [], [1], {"a": 1}):
            with self.subTest(value=value):
                self.assertIsNone(common.validate_json_value(value, max_depth=0))
        for value in ([[]], {"a": []}, [{"a": 1}]):
            with self.subTest(value=value), self.assertRaises(common.DataError):
                common.validate_json_value(value, max_depth=0)
        for depth in (0, 1, 32, 128):
            value = nested_lists(depth)
            self.assertIsNone(common.validate_json_value(value, max_depth=depth))
            payload = b"[" * (depth + 1) + b"0" + b"]" * (depth + 1)
            self.assertEqual(common.parse_json_bytes(payload, max_depth=depth), value)
            if depth:
                with self.assertRaises(common.DataError):
                    common.parse_json_bytes(payload, max_depth=depth - 1)
        with self.assertRaises(common.DataError):
            common.validate_json_value(nested_lists(129), max_depth=128)

    def test_direct_cycles_and_parser_recursion_exhaustion_are_controlled(self):
        cycle = []
        cycle.append(cycle)
        mapping = {}
        mapping["self"] = mapping
        for value in (cycle, mapping):
            with self.subTest(kind=type(value).__name__), self.assertRaises(common.DataError):
                common.validate_json_value(value, max_nodes=8, max_depth=2)
        self.assertIs(cycle[0], cycle)
        self.assertIs(mapping["self"], mapping)
        with mock.patch.object(common.json, "loads", side_effect=RecursionError("injected parser recursion")), \
                self.assertRaises(common.DataError):
            common.parse_json_bytes(b"[]")

    def test_canonical_bytes_match_the_independent_literal_in_every_order(self):
        before = copy.deepcopy(CANONICAL_VALUE)
        for value in (CANONICAL_VALUE, dict(reversed(list(CANONICAL_VALUE.items())))):
            with self.subTest(keys=list(value)):
                self.assertEqual(common.canonical_json_bytes(value), CANONICAL_BYTES)
                self.assertEqual(common.canonical_json_bytes(value), CANONICAL_BYTES)
        self.assertEqual(CANONICAL_VALUE, before)
        self.assertEqual(common.parse_json_bytes(CANONICAL_BYTES), before)

    def test_canonical_scalar_empty_and_nested_object_encodings(self):
        cases = ((None, b"null\n"), (True, b"true\n"), (1.0, b"1.0\n"),
                 (-0.0, b"-0.0\n"), ([], b"[]\n"), ({}, b"{}\n"),
                 ({"z": {"b": 2, "a": 1}}, b'{\n  "z": {\n    "a": 1,\n    "b": 2\n  }\n}\n'))
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(common.canonical_json_bytes(value), expected)

    def test_canonical_uses_the_larger_declared_numeric_and_depth_bounds(self):
        self.assertEqual(common.canonical_json_bytes(1e100), b"1e+100\n")
        encoded = common.canonical_json_bytes(nested_lists(128))
        self.assertEqual(common.parse_json_bytes(encoded, max_depth=128), nested_lists(128))
        for value in (1e101, math.nan, math.inf, nested_lists(129)):
            with self.subTest(kind=type(value).__name__), self.assertRaises(common.DataError):
                common.canonical_json_bytes(value)

    def test_serialization_errors_are_normalized_before_any_file_is_created(self):
        for error in (TypeError("injected type error"), ValueError("injected value error"),
                      UnicodeError("injected Unicode error"), RecursionError("injected recursion")):
            with self.subTest(error=type(error).__name__), \
                    mock.patch.object(common.json, "dumps", side_effect=error), \
                    self.assertRaises(common.DataError):
                common.write_json_new(self.root / "target.json", {})
            self.assertEqual(list(self.root.iterdir()), [])

    def test_write_publishes_exact_bytes_and_returns_their_independent_identity(self):
        self.require_hard_links()
        target = self.root / "report.json"
        identity = common.write_json_new(target, CANONICAL_VALUE)
        self.assertEqual(target.read_bytes(), CANONICAL_BYTES)
        self.assertEqual(identity, {
            "sha256": hashlib.sha256(CANONICAL_BYTES).hexdigest(),
            "size_bytes": len(CANONICAL_BYTES),
        })
        self.assertEqual(set(self.root.iterdir()), {target})
        other = self.root / "second.json"
        self.assertEqual(common.write_json_new(str(other), CANONICAL_VALUE), identity)
        self.assertEqual(other.read_bytes(), CANONICAL_BYTES)

    def test_write_is_complete_flushed_synced_and_closed_before_same_parent_link(self):
        self.require_hard_links()
        target = self.root / "report.json"
        real_link = os.link
        real_fsync = os.fsync
        events = []
        streams = []

        def write(stream, payload):
            events.append("write")
            return stream.write(payload)

        def flush(stream):
            events.append("flush")
            return stream.flush()

        def sync(descriptor):
            events.append("fsync")
            return real_fsync(descriptor)

        def link(source, destination):
            self.assertEqual(events, ["write", "flush", "fsync"])
            self.assertTrue(streams[0].closed)
            self.assertEqual(Path(source).parent, target.parent)
            self.assertEqual(Path(source).read_bytes(), CANONICAL_BYTES)
            self.assertFalse(target.exists())
            events.append("link")
            return real_link(source, destination)

        with mock.patch.object(common.os, "fdopen", side_effect=stream_factory({"write": write, "flush": flush}, streams)), \
                mock.patch.object(common.os, "fsync", side_effect=sync), \
                mock.patch.object(common.os, "link", side_effect=link):
            common.write_json_new(target, CANONICAL_VALUE)
        self.assertEqual(events, ["write", "flush", "fsync", "link"])
        self.assertEqual(set(self.root.iterdir()), {target})

    def test_existing_regular_target_and_its_bytes_are_preserved(self):
        target = self.source(SENTINEL_BYTES, "report.json")
        with self.assertRaises(common.DataError):
            common.write_json_new(target, CANONICAL_VALUE)
        self.assertEqual(target.read_bytes(), SENTINEL_BYTES)
        self.assertEqual(set(self.root.iterdir()), {target})

    def test_existing_directory_target_and_its_contents_are_preserved(self):
        target = self.root / "report.json"
        target.mkdir()
        marker = target / "marker"
        marker.write_bytes(SENTINEL_BYTES)
        with self.assertRaises(common.DataError):
            common.write_json_new(target, CANONICAL_VALUE)
        self.assertTrue(target.is_dir())
        self.assertEqual(marker.read_bytes(), SENTINEL_BYTES)
        self.assertEqual(set(self.root.iterdir()), {target})

    def test_existing_dangling_symlink_target_is_preserved(self):
        target = self.root / "report.json"
        missing = self.root / "absent-target"
        self.symlink(missing, target)
        original_link = os.readlink(target)
        with self.assertRaises(common.DataError):
            common.write_json_new(target, CANONICAL_VALUE)
        self.assertTrue(target.is_symlink())
        self.assertEqual(os.readlink(target), original_link)
        self.assertFalse(missing.exists())
        self.assertEqual(set(self.root.iterdir()), {target})

    def test_target_created_at_link_time_is_preserved(self):
        self.require_hard_links()
        target = self.root / "report.json"
        real_link = os.link

        def install_competing_target(source, destination):
            target.write_bytes(SENTINEL_BYTES)
            return real_link(source, destination)

        with mock.patch.object(common.os, "link", side_effect=install_competing_target), \
                self.assertRaises(common.DataError):
            common.write_json_new(target, CANONICAL_VALUE)
        self.assertEqual(target.read_bytes(), SENTINEL_BYTES)
        self.assertEqual(set(self.root.iterdir()), {target})

    def test_invalid_value_or_path_does_not_create_or_modify_any_file(self):
        original = self.source(SENTINEL_BYTES, "existing")
        for value in ({"bad": {1, 2}}, {1: "key"}, {"bad": math.nan}, {"bad": "\ud800"}):
            with self.subTest(value=repr(value)), self.assertRaises(common.DataError):
                common.write_json_new(self.root / "report.json", value)
        for path in (None, 3, self.root / "\x00", self.root / "absent" / "report.json", original / "report.json"):
            with self.subTest(path=repr(path)), self.assertRaises(common.DataError):
                common.write_json_new(path, {})
        self.assertEqual(original.read_bytes(), SENTINEL_BYTES)
        self.assertEqual(set(self.root.iterdir()), {original})

    def test_temporary_creation_failure_preserves_existing_files(self):
        original = self.source(SENTINEL_BYTES)
        with mock.patch.object(common.tempfile, "mkstemp", side_effect=OSError("injected temporary failure")), \
                self.assertRaises(common.DataError):
            common.write_json_new(self.root / "report.json", {})
        self.assertEqual(original.read_bytes(), SENTINEL_BYTES)
        self.assertEqual(set(self.root.iterdir()), {original})

    def test_write_fdopen_failure_closes_descriptor_and_removes_temporary_name(self):
        real_mkstemp = tempfile.mkstemp
        descriptors = []

        def capture_temporary(*args, **kwargs):
            descriptor, name = real_mkstemp(*args, **kwargs)
            descriptors.append(descriptor)
            return descriptor, name

        try:
            with mock.patch.object(common.tempfile, "mkstemp", side_effect=capture_temporary), \
                    mock.patch.object(common.os, "fdopen", side_effect=OSError("injected fdopen failure")), \
                    self.assertRaises(common.DataError):
                common.write_json_new(self.root / "report.json", {})
            self.assertEqual(len(descriptors), 1)
            self.assert_closed(descriptors[0])
            self.assertEqual(list(self.root.iterdir()), [])
        finally:
            for descriptor in descriptors:
                try:
                    os.close(descriptor)
                except OSError:
                    pass

    def test_partial_write_then_error_closes_and_cleans_without_publication(self):
        original = self.source(SENTINEL_BYTES)
        streams = []

        def fail_after_prefix(stream, payload):
            stream.write(payload[:3])
            raise OSError("injected write failure after a prefix")

        with mock.patch.object(common.os, "fdopen", side_effect=stream_factory({"write": fail_after_prefix}, streams)), \
                mock.patch.object(common.os, "link") as linking:
            with self.assertRaises(common.DataError):
                common.write_json_new(self.root / "report.json", CANONICAL_VALUE)
            linking.assert_not_called()
        self.assertTrue(streams[0].closed)
        self.assertEqual(original.read_bytes(), SENTINEL_BYTES)
        self.assertEqual(set(self.root.iterdir()), {original})

    def test_flush_failure_closes_and_cleans_without_publication(self):
        streams = []

        def fail_flush(stream):
            raise OSError("injected flush failure")

        with mock.patch.object(common.os, "fdopen", side_effect=stream_factory({"flush": fail_flush}, streams)), \
                mock.patch.object(common.os, "link") as linking:
            with self.assertRaises(common.DataError):
                common.write_json_new(self.root / "report.json", CANONICAL_VALUE)
            linking.assert_not_called()
        self.assertTrue(streams[0].closed)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_fsync_and_link_failures_remove_owned_temporary_files(self):
        original = self.source(SENTINEL_BYTES)
        for operation in ("fsync", "link"):
            with self.subTest(operation=operation), \
                    mock.patch.object(common.os, operation, side_effect=OSError(f"injected {operation} failure")), \
                    self.assertRaises(common.DataError):
                common.write_json_new(self.root / "report.json", CANONICAL_VALUE)
            self.assertEqual(set(self.root.iterdir()), {original})
            self.assertEqual(original.read_bytes(), SENTINEL_BYTES)

    def test_post_publication_cleanup_error_is_explicit_and_keeps_complete_target(self):
        self.require_hard_links()
        target = self.root / "report.json"
        with mock.patch.object(Path, "unlink", side_effect=OSError("injected cleanup failure")):
            with self.assertRaises(common.DataError) as raised:
                common.write_json_new(target, CANONICAL_VALUE)
        message = str(raised.exception)
        self.assertIn("published", message)
        self.assertIn("complete", message)
        self.assertIn("injected cleanup failure", message)
        self.assertEqual(target.read_bytes(), CANONICAL_BYTES)
        remaining = set(self.root.iterdir()) - {target}
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining.pop().read_bytes(), CANONICAL_BYTES)

    def test_primary_and_cleanup_errors_are_both_retained(self):
        original = self.source(SENTINEL_BYTES)
        target = self.root / "report.json"
        with mock.patch.object(common.os, "link", side_effect=OSError("injected link failure")), \
                mock.patch.object(Path, "unlink", side_effect=OSError("injected cleanup failure")):
            with self.assertRaises(common.DataError) as raised:
                common.write_json_new(target, CANONICAL_VALUE)
        self.assertIn("injected link failure", str(raised.exception))
        self.assertIn("injected cleanup failure", str(raised.exception))
        self.assertFalse(target.exists())
        self.assertEqual(original.read_bytes(), SENTINEL_BYTES)
        remaining = set(self.root.iterdir()) - {original}
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining.pop().read_bytes(), CANONICAL_BYTES)


if __name__ == "__main__":
    unittest.main(verbosity=2)
