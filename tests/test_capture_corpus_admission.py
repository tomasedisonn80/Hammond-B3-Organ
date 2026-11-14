#!/usr/bin/env python3
"""Independent adversarial admission for capture-corpus-v1.

The separately authored assignment-17 archive writer supplies small synthetic
fixtures. Expected resource boundaries, path outcomes and descriptor ownership
are specified here, without using producer validators as acceptance oracles.
"""

from __future__ import annotations

from contextlib import contextmanager
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import capture_corpus as subject
import capture_audio
from test_capture_corpus import _Archive, _json_bytes


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def index_value(count=1):
    return {
        "schema_version": 1,
        "contract_origin": "project-proposed-corpus-v1",
        "corpus_id": "admission-fixture",
        "captures": [
            {"capture_id": f"c{i}", "manifest_path": f"c{i}.json",
             "manifest_sha256": sha(f"manifest-{i}".encode()), "purpose": "fit",
             "relation_labels": [], "parent_capture_ids": [], "derived_audio": []}
            for i in range(count)
        ],
    }


def value_nodes(value):
    """Independent literal count; object keys are not value nodes."""
    pending, result = [value], 0
    while pending:
        value = pending.pop()
        result += 1
        if type(value) is dict:
            pending.extend(value.values())
        elif type(value) is list:
            pending.extend(value)
    return result


class StatView:
    def __init__(self, original, **changes):
        self.original = original
        self.changes = changes

    def __getattr__(self, name):
        return self.changes[name] if name in self.changes else getattr(self.original, name)


class FileView:
    """Fault-injection wrapper that always owns and closes its real stream."""
    def __init__(self, stream, *, read_action=None, close_error=None):
        self.stream = stream
        self.read_action = read_action
        self.close_error = close_error

    def __enter__(self):
        self.stream.__enter__()
        return self

    def __exit__(self, *args):
        result = self.stream.__exit__(*args)
        if self.close_error is not None:
            raise self.close_error
        return result

    def fileno(self):
        return self.stream.fileno()

    def read(self, size=-1):
        if self.read_action is None:
            return self.stream.read(size)
        return self.read_action(self.stream, size)


@contextmanager
def instrument_open(*, before_open=None, after_close=None):
    """Keep POSIX dir_fd capability under an observed os.open replacement."""
    real_open, real_close = os.open, os.close
    opened = []
    events = []

    def observed_open(path, flags, *args, **kwargs):
        if before_open is not None:
            before_open(path, flags, kwargs, events)
        descriptor = real_open(path, flags, *args, **kwargs)
        opened.append(descriptor)
        events.append(("open", descriptor, str(path), flags, dict(kwargs)))
        return descriptor

    def observed_close(descriptor):
        real_close(descriptor)
        events.append(("close", descriptor))
        if after_close is not None:
            after_close(descriptor, events)

    capabilities = set(os.supports_dir_fd)
    if real_open in capabilities:
        capabilities.add(observed_open)
    try:
        with mock.patch.object(os, "open", observed_open), \
                mock.patch.object(os, "close", observed_close), \
                mock.patch.object(os, "supports_dir_fd", capabilities):
            yield opened, events
    finally:
        # A failing regression must not leak its deliberately observed resources
        # into later tests. Assertions run before this independent final cleanup.
        for descriptor in set(opened):
            try:
                os.fstat(descriptor)
            except OSError:
                continue
            real_close(descriptor)


class CorpusAdmission(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="corpus-admission-")
        self.addCleanup(self.temporary.cleanup)
        # The confined reader resolves ancestors before observing descendants.
        # Match those paths on macOS /var aliases and Windows short TEMP names.
        self.work = Path(self.temporary.name).resolve(strict=True)
        self.archive = _Archive(self.work / "archive")
        self.archive.add("a")
        self.path = self.archive.write()
        self.manifest = self.archive.root / "captures" / "a.json"
        self.raw = self.archive.file_path("a", "raw")

    def reject(self, operation, *args, contains=None, **kwargs):
        with self.assertRaises(subject.CorpusError) as caught:
            operation(*args, **kwargs)
        self.assertTrue(str(caught.exception).strip())
        if contains is not None:
            self.assertIn(contains, str(caught.exception))
        return caught.exception

    def write_index(self, value):
        self.path.write_bytes(_json_bytes(value))
        return self.path

    def write_manifest_bytes(self, payload, ident="a"):
        entry = self.archive.entries[ident]
        target = self.archive.root / entry["manifest_path"]
        target.write_bytes(payload)
        entry["manifest_sha256"] = sha(payload)
        self.path.write_bytes(_json_bytes(self.archive.index))

    def assert_closed(self, descriptors):
        live = []
        for descriptor in set(descriptors):
            try:
                os.fstat(descriptor)
            except OSError:
                continue
            live.append(descriptor)
        self.assertEqual(live, [], f"operation leaked descriptors {live}")

    def require_dir_fd(self):
        if os.name != "posix" or os.open not in os.supports_dir_fd:
            self.skipTest("native POSIX directory-descriptor traversal unavailable")

    def symlink(self, target, link, *, directory=False):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"symlink capability unavailable: {error}")

    @contextmanager
    def stream_hook(self, target, *, read_action=None, close_error=None):
        expected = target.stat()
        identity = expected.st_dev, expected.st_ino
        original = os.fdopen
        descriptors = []

        def wrapped(descriptor, *args, **kwargs):
            info = os.fstat(descriptor)
            stream = original(descriptor, *args, **kwargs)
            descriptors.append(descriptor)
            if (info.st_dev, info.st_ino) == identity:
                return FileView(stream, read_action=read_action, close_error=close_error)
            return stream

        with mock.patch.object(os, "fdopen", wrapped):
            yield descriptors

    def no_artifact_open(self, path, flags, kwargs, events):
        if str(path).endswith(".bin"):
            raise AssertionError("artifact opened before complete declaration preflight")

    def test_strict_index_bytes_reject_encoding_constants_and_trailing_data(self):
        valid = _json_bytes(index_value())
        cases = [b"", b"\xff", b"\xef\xbb\xbf" + valid, valid + b"{}",
                 b"NaN", b"Infinity", b"-Infinity", b"1e9999",
                 valid.replace(b'"admission-fixture"', b'"\\ud800"'),
                 valid.replace(b'"admission-fixture"', b'"bad\\u0000text"'),
                 valid.replace(b'"admission-fixture"', b'"bad\\u007ftext"'),
                 valid.replace(b'"admission-fixture"', b'"bad\\u009ftext"')]
        for payload in cases:
            with self.subTest(payload=payload[:60]):
                self.path.write_bytes(payload)
                self.reject(subject.load_corpus, self.path)
                self.assertEqual(self.path.read_bytes(), payload)

    def test_duplicate_json_keys_reject_at_every_index_object_level(self):
        value = index_value()
        entry = value["captures"][0]
        entry["relation_labels"] = [{"kind": "gesture", "label": "g"}]
        entry["derived_audio"] = [{"file_id": "d", "format": "wav_pcm16",
                                    "sample_rate_hz": 48000, "channel_count": 1}]
        payload = json.dumps(value, separators=(",", ":")).encode()
        for token in (b'"schema_version":1', b'"purpose":"fit"',
                      b'"kind":"gesture"', b'"channel_count":1'):
            with self.subTest(token=token):
                self.path.write_bytes(payload.replace(token, token + b"," + token, 1))
                self.reject(subject.load_corpus, self.path, contains="duplicate JSON key")

    def test_numeric_token_length_and_generic_magnitude_are_bounded(self):
        for token in (b"1" * 65, b"0." + b"0" * 63):
            self.path.write_bytes(token)
            self.reject(subject.load_corpus, self.path, contains="numeric token")
        self.path.write_bytes(b"0." + b"0" * 62)  # Exactly 64 token characters.
        error = self.reject(subject.load_corpus, self.path)
        self.assertNotIn("numeric token", str(error))
        for value in (1000000000001, -1000000000001, 1e100, -(10 ** 200)):
            invalid = index_value()
            invalid["extra"] = value
            self.reject(subject.validate_corpus, invalid, contains="bound")

    def test_exact_index_byte_limit_and_excess_before_open(self):
        payload = _json_bytes(index_value())
        padded = payload + b" " * (1048576 - len(payload))
        self.path.write_bytes(padded)
        self.assertEqual(subject.load_corpus(self.path), index_value())
        self.path.write_bytes(padded + b" ")
        with instrument_open(before_open=lambda *args: self.fail("oversized index opened")):
            self.reject(subject.load_corpus, self.path, contains="byte limit")

    def test_direct_json_types_subclasses_and_unsafe_keys_reject(self):
        class DictSubclass(dict):
            pass
        class ListSubclass(list):
            pass
        class IntSubclass(int):
            pass
        class StringSubclass(str):
            pass
        bad = [None, [], (), object(), DictSubclass(index_value()),
               {1: "not a JSON key"}, {StringSubclass("schema_version"): 1}]
        for value in bad:
            self.reject(subject.validate_corpus, value)
        for value in (True, 1.0, IntSubclass(1)):
            changed = index_value(); changed["schema_version"] = value
            self.reject(subject.validate_corpus, changed)
        for value in (tuple(index_value()["captures"]), ListSubclass(index_value()["captures"])):
            changed = index_value(); changed["captures"] = value
            self.reject(subject.validate_corpus, changed)

    def test_direct_cycles_and_depth_guard_have_bounded_failure(self):
        cyclic = []; cyclic.append(cyclic)
        self.reject(subject.validate_corpus, cyclic, contains="nesting")
        cyclic_dict = {}; cyclic_dict["self"] = cyclic_dict
        self.reject(subject.validate_corpus, cyclic_dict, contains="nesting")
        for depth in (16, 17):
            value = index_value(); nested = []
            for _ in range(depth - 1):
                nested = [nested]
            value["extra"] = nested
            error = self.reject(subject.validate_corpus, value)
            if depth == 16:
                self.assertNotIn("nesting", str(error))
            else:
                self.assertIn("nesting", str(error))
        self.path.write_bytes(b"[" * 1200 + b"0" + b"]" * 1200)
        self.reject(subject.load_corpus, self.path)

    def test_exact_value_node_limit_and_one_more_node(self):
        value = index_value(512)
        for entry in value["captures"]:
            entry["relation_labels"] = [{"kind": "gesture", "label": f"g{i}"}
                                         for i in range(32)]
        remaining = 2456
        for entry in value["captures"]:
            amount = min(32, remaining); remaining -= amount
            entry["derived_audio"] = [
                {"file_id": f"d{i}", "format": "wav_pcm16",
                 "sample_rate_hz": 48000, "channel_count": 1}
                for i in range(amount)]
        value["captures"][1]["parent_capture_ids"] = ["c0"]
        value["captures"][2]["parent_capture_ids"] = ["c0", "c1"]
        self.assertEqual(value_nodes(value), 65536)
        subject.validate_corpus(value)
        value["captures"][3]["parent_capture_ids"] = ["c0"]
        self.assertEqual(value_nodes(value), 65537)
        self.reject(subject.validate_corpus, value, contains="value-node")

    def test_512_capture_index_boundary_and_513_rejection(self):
        value = index_value(512)
        subject.validate_corpus(value)
        self.write_index(value)
        self.assertEqual(len(subject.load_corpus(self.path)["captures"]), 512)
        self.reject(subject.validate_corpus, index_value(513), contains="512")

    def test_actual_512_planned_manifest_audit(self):
        archive = _Archive(self.work / "many")
        for index in range(512):
            archive.add(f"p{index}", planned=True)
        report = subject.audit_corpus(archive.write())
        self.assertEqual(report["status"], "inconclusive")
        self.assertEqual(len(report["captures"]), 512)
        self.assertEqual(len(report["groups"]), 512)
        self.assertEqual(len(report["findings"]), 512)
        self.assertTrue(all(item["code"] == "planned_capture" for item in report["findings"]))

    def test_relation_parent_and_descriptor_count_boundaries(self):
        value = index_value(17); entry = value["captures"][-1]
        entry["relation_labels"] = [{"kind": "gesture", "label": f"g{i}"} for i in range(32)]
        entry["parent_capture_ids"] = [f"c{i}" for i in range(16)]
        entry["derived_audio"] = [{"file_id": f"d{i}", "format": "wav_pcm16",
                                   "sample_rate_hz": 48000, "channel_count": 1} for i in range(32)]
        subject.validate_corpus(value)
        for field, extra in (("relation_labels", {"kind": "gesture", "label": "extra"}),
                             ("parent_capture_ids", "missing"),
                             ("derived_audio", {"file_id": "extra", "format": "wav_pcm16",
                                                "sample_rate_hz": 48000, "channel_count": 1})):
            changed = copy.deepcopy(value)
            changed["captures"][-1][field].append(extra)
            self.reject(subject.validate_corpus, changed)

    def test_portable_path_rejection_before_manifest_access(self):
        bad = ["", ".", "..", "a/../b.json", "a//b.json", "/a.json", "a/",
               "a\\b.json", "C:/a.json", "//host/share", "a:b.json", "CON",
               "nul.json", "a/COM1.wav", "a/lPt9.txt", "PRN.extra.txt", "a.",
               "a./b", "é.json", "a\n.json", "a\x7f.json", "a" * 65,
               "/".join(["a"] * 9), "/".join(["a" * 60] * 4)]
        for path in bad:
            with self.subTest(path=path):
                value = index_value(); value["captures"][0]["manifest_path"] = path
                before = copy.deepcopy(value)
                self.reject(subject.validate_corpus, value)
                self.assertEqual(value, before)

    def test_portable_path_inclusive_component_depth_and_total_boundaries(self):
        paths = ["a" * 64, "/".join(["a"] * 8),
                 "/".join(["a" * 60, "b" * 60, "c" * 60, "d" * 57]),
                 "console.json", "COM0.json", "LPT10.json", "a-b_c.2.json"]
        self.assertEqual(len(paths[2]), 240)
        for path in paths:
            value = index_value(); value["captures"][0]["manifest_path"] = path
            subject.validate_corpus(value)

    def test_generic_string_controls_length_and_narrow_ids_reject(self):
        for value in (" ", "a" * 2049, "a\ud800", "a\u0080", "a\n", "A", "0a", "a" * 65):
            changed = index_value(); changed["corpus_id"] = value
            self.reject(subject.validate_corpus, changed)
        value = index_value(); value["corpus_id"] = "a" * 64
        subject.validate_corpus(value)

    def test_strict_manifest_json_rejects_after_exact_expected_hash(self):
        original = self.manifest.read_bytes()
        cases = [b"\xef\xbb\xbf" + original, b"\xff", original + b"{}",
                 original.replace(b'"schema_version": 1', b'"schema_version": 1, "schema_version": 1'),
                 original.replace(b'"status_reason": null', b'"status_reason": NaN'),
                 original.replace(b'"capture_id": "a"', b'"capture_id": "\\ud800"')]
        for payload in cases:
            with self.subTest(payload=payload[:60]):
                self.write_manifest_bytes(payload)
                with instrument_open(before_open=self.no_artifact_open):
                    self.reject(subject.audit_corpus, self.path, check_files=True,
                                contains="manifest 'captures/a.json', capture 'a'")

    def test_exact_manifest_byte_limit_and_excess_before_open(self):
        original = self.manifest.read_bytes()
        padded = original + b" " * (65536 - len(original))
        self.write_manifest_bytes(padded)
        self.assertEqual(subject.audit_corpus(self.path)["status"], "pass")
        self.write_manifest_bytes(padded + b" ")
        def trap(path, *unused):
            if Path(path).name == "a.json":
                self.fail("oversized manifest opened")
        with instrument_open(before_open=trap):
            self.reject(subject.audit_corpus, self.path, contains="byte limit")

    def test_actual_16mib_manifest_aggregate_and_next_manifest_preflight(self):
        archive = _Archive(self.work / "manifest-budget")
        for index in range(256):
            archive.add(f"m{index:03d}", planned=True)
        archive.write()
        for ident, entry in archive.entries.items():
            path = archive.root / entry["manifest_path"]
            payload = path.read_bytes()
            payload += b" " * (65536 - len(payload))
            path.write_bytes(payload)
            entry["manifest_sha256"] = sha(payload)
        archive.path.write_bytes(_json_bytes(archive.index))
        self.assertEqual(sum((archive.root / e["manifest_path"]).stat().st_size
                             for e in archive.entries.values()), 16777216)
        self.assertEqual(len(subject.audit_corpus(archive.path)["captures"]), 256)
        archive.add("zextra", planned=True)
        entry = archive.entries["zextra"]
        payload = _json_bytes(archive.manifests["zextra"])
        (archive.root / entry["manifest_path"]).write_bytes(payload)
        entry["manifest_sha256"] = sha(payload)
        archive.path.write_bytes(_json_bytes(archive.index))
        def trap(path, *unused):
            if Path(path).name == "zextra.json":
                self.fail("next manifest opened after exhausted aggregate")
        with instrument_open(before_open=trap):
            self.reject(subject.audit_corpus, archive.path, contains="aggregate manifest")

    def declared_large_archive(self, count, size):
        archive = _Archive(self.work / f"large-{count}-{size}")
        for index in range(count):
            archive.add(f"b{index}")
            archive.manifests[f"b{index}"]["files"][0]["size_bytes"] = size
        archive.write()
        return archive

    def test_exact_2gib_declared_artifact_aggregate_and_excess(self):
        archive = self.declared_large_archive(8, 268435456)
        report = subject.audit_corpus(archive.path)
        self.assertEqual(report["status"], "pass")
        self.assertTrue(all(c["files"][0]["observed_size_bytes"] is None for c in report["captures"]))
        archive.add("extra")
        archive.manifests["extra"]["files"][0]["size_bytes"] = 1
        archive.write()
        with instrument_open(before_open=self.no_artifact_open):
            self.reject(subject.audit_corpus, archive.path, check_files=True,
                        contains="aggregate declared artifact")

    def test_repeated_artifact_references_count_before_any_scan(self):
        archive = self.declared_large_archive(9, 268435456)
        raw = archive.manifests["b0"]["files"][0]
        for record in archive.manifests.values():
            record["files"][0].update(path=raw["path"], sha256=raw["sha256"])
        archive.write()
        with instrument_open(before_open=self.no_artifact_open):
            self.reject(subject.audit_corpus, archive.path, check_files=True,
                        contains="aggregate declared artifact")

    def test_actual_repeated_audio_budget_counts_refs_and_precedes_file_scan(self):
        self.archive.add("b")
        a = self.archive.manifests["a"]["files"][0]
        self.archive.manifests["b"]["files"][0].update(path=a["path"], size_bytes=a["size_bytes"], sha256=a["sha256"])
        self.archive.write()
        bound = 2 * a["size_bytes"]
        with mock.patch.object(subject, "MAX_TOTAL_AUDIO_BYTES", bound):
            report = subject.audit_corpus(self.path, check_files=True, check_audio=True)
            self.assertEqual(report["audio_check"], "verified")
        with mock.patch.object(subject, "MAX_TOTAL_AUDIO_BYTES", bound - 1), \
                instrument_open(before_open=self.no_artifact_open), \
                mock.patch.object(capture_audio, "inspect_audio", side_effect=AssertionError("decoder entered")):
            self.reject(subject.audit_corpus, self.path, check_files=True, check_audio=True,
                        contains="aggregate selected audio")

    def test_audio_budget_includes_declared_derivatives_not_support_or_omitted(self):
        payload = self.raw.read_bytes()
        descriptor = {"format": "wav_pcm16", "sample_rate_hz": 48000, "channel_count": 1}
        self.archive.file("a", "decoded", payload, descriptor=descriptor)
        self.archive.file("a", "omitted", b"not selected as audio")
        self.archive.file("a", "support", b"not audio", kind="support")
        self.archive.write()
        with mock.patch.object(subject, "MAX_TOTAL_AUDIO_BYTES", 2 * len(payload)):
            report = subject.audit_corpus(self.path, check_files=True, check_audio=True)
            self.assertEqual(report["audio_check"], "partial")
        with mock.patch.object(subject, "MAX_TOTAL_AUDIO_BYTES", 2 * len(payload) - 1), \
                instrument_open(before_open=self.no_artifact_open):
            self.reject(subject.audit_corpus, self.path, check_files=True, check_audio=True,
                        contains="aggregate selected audio")

    def test_artifact_budget_counts_support_and_omitted_derivatives(self):
        self.archive.file("a", "support", b"support", kind="support")
        self.archive.file("a", "omitted", b"derived")
        self.archive.write()
        total = sum(item["size_bytes"] for item in self.archive.manifests["a"]["files"])
        with mock.patch.object(subject, "MAX_TOTAL_ARTIFACT_BYTES", total):
            self.assertEqual(subject.audit_corpus(self.path, check_files=True)["file_check"], "verified")
        with mock.patch.object(subject, "MAX_TOTAL_ARTIFACT_BYTES", total - 1), \
                instrument_open(before_open=self.no_artifact_open):
            self.reject(subject.audit_corpus, self.path, check_files=True,
                        contains="aggregate declared artifact")

    def test_oversized_single_artifact_and_manifest_file_count_preflight(self):
        record = self.archive.manifests["a"]
        record["files"][0]["size_bytes"] = 268435457
        self.archive.write()
        with instrument_open(before_open=self.no_artifact_open):
            self.reject(subject.audit_corpus, self.path, check_files=True)
        record["files"][0]["size_bytes"] = len(self.archive.payloads[("a", "raw")])
        for index in range(32):
            self.archive.file("a", f"s{index}", bytes([index]), kind="support")
        self.archive.write()
        with instrument_open(before_open=self.no_artifact_open):
            self.reject(subject.audit_corpus, self.path, check_files=True, contains="32")

    def test_graph_and_finding_limits_reject_without_truncation(self):
        archive = _Archive(self.work / "graph-budget")
        for ident in ("a", "b", "c", "d"):
            archive.add(ident, purpose="unassigned", planned=True,
                        labels=[{"kind": "gesture", "label": "shared"}])
        path = archive.write()
        with mock.patch.object(subject, "MAX_EDGES", 3), mock.patch.object(subject, "MAX_FINDINGS", 8):
            report = subject.audit_corpus(path)
            self.assertEqual((len(report["edges"]), len(report["findings"])), (3, 8))
        with mock.patch.object(subject, "MAX_EDGES", 2):
            self.reject(subject.audit_corpus, path, contains="edge limit")
        with mock.patch.object(subject, "MAX_FINDINGS", 7):
            self.reject(subject.audit_corpus, path, contains="finding limit")

    def test_missing_index_manifest_artifact_and_invalid_path_types(self):
        for value in (None, True, 7, b"index.json", [], "", "a\0b", "a\ud800"):
            self.reject(subject.load_corpus, value)
        self.reject(subject.load_corpus, self.work / "missing" / "index.json")
        payload = self.manifest.read_bytes(); self.manifest.unlink()
        self.reject(subject.audit_corpus, self.path, contains="capture 'a'")
        self.manifest.write_bytes(payload); self.raw.unlink()
        self.assertEqual(subject.audit_corpus(self.path)["status"], "pass")
        self.reject(subject.audit_corpus, self.path, check_files=True, contains="file 'raw'")

    def test_unavailable_current_directory_error_is_wrapped(self):
        with mock.patch.object(os, "getcwd", side_effect=OSError("cwd unavailable")):
            self.reject(subject.load_corpus, "relative.json", contains="cwd unavailable")

    def test_index_leaf_and_root_symlinks_reject(self):
        link = self.archive.root / "alias.json"
        self.symlink(self.path, link)
        self.reject(subject.load_corpus, link)
        root_alias = self.work / "alias-root"
        self.symlink(self.archive.root, root_alias, directory=True)
        self.reject(subject.load_corpus, root_alias / "corpus.json")

    def test_manifest_leaf_and_directory_symlinks_reject(self):
        saved = self.archive.root / "saved.json"
        self.manifest.rename(saved); self.symlink(saved, self.manifest)
        self.reject(subject.audit_corpus, self.path)
        self.manifest.unlink(); saved.rename(self.manifest)
        directory = self.archive.root / "captures"
        moved = self.archive.root / "original-captures"
        directory.rename(moved); self.symlink(moved, directory, directory=True)
        self.reject(subject.audit_corpus, self.path)

    def test_artifact_leaf_and_directory_symlinks_reject(self):
        saved = self.raw.with_name("saved.bin")
        self.raw.rename(saved); self.symlink(saved, self.raw)
        self.reject(subject.audit_corpus, self.path, check_files=True)
        self.raw.unlink(); saved.rename(self.raw)
        directory = self.raw.parent; moved = directory.with_name("saved-a")
        directory.rename(moved); self.symlink(moved, directory, directory=True)
        self.reject(subject.audit_corpus, self.path, check_files=True)

    def test_dangling_symlinks_are_rejected_without_following(self):
        for target in (self.path, self.manifest, self.raw):
            with self.subTest(target=target.name):
                original = target.read_bytes(); target.unlink()
                self.symlink(self.work / "does-not-exist", target)
                self.reject(subject.audit_corpus, self.path, check_files=True)
                target.unlink(); target.write_bytes(original)

    def test_alias_above_selected_root_is_allowed_but_not_a_root_alias(self):
        outer = self.work / "outer"; outer.mkdir()
        moved = outer / "archive"; self.archive.root.rename(moved)
        alias = self.work / "outer-alias"; self.symlink(outer, alias, directory=True)
        report = subject.audit_corpus(alias / "archive" / "corpus.json", check_files=True)
        self.assertEqual(report["status"], "pass")
        self.assertNotIn(str(self.work), json.dumps(report))

    def test_directory_leaves_reject_at_all_input_levels(self):
        for target in (self.path, self.manifest, self.raw):
            original = target.read_bytes(); target.unlink(); target.mkdir()
            self.reject(subject.audit_corpus, self.path, check_files=True)
            target.rmdir(); target.write_bytes(original)

    def test_fifo_leaves_reject_before_open(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("native FIFO creation unavailable")
        for target in (self.path, self.manifest, self.raw):
            original = target.read_bytes(); target.unlink()
            try:
                os.mkfifo(target)
            except OSError as error:
                self.skipTest(f"native FIFO creation unavailable: {error}")
            def trap(path, *unused):
                if Path(path).name == target.name:
                    self.fail("unsafe FIFO leaf opened")
            with instrument_open(before_open=trap):
                self.reject(subject.audit_corpus, self.path, check_files=True)
            target.unlink(); target.write_bytes(original)

    def test_controlled_reparse_metadata_rejects_every_confined_level(self):
        original = Path.lstat
        for target in (self.archive.root, self.path, self.manifest.parent,
                       self.manifest, self.raw.parent, self.raw):
            intercepted = []
            def changed(path, *args, **kwargs):
                info = original(path, *args, **kwargs)
                if path == target:
                    intercepted.append(path)
                    return StatView(info, st_file_attributes=0x400)
                return info
            with self.subTest(target=str(target)), mock.patch.object(Path, "lstat", changed):
                self.reject(subject.audit_corpus, self.path, check_files=True, contains="reparse")
                self.assertTrue(intercepted, "confined reparse hook must be reached")

    def test_within_manifest_hardlink_aliases_reject_for_all_kinds(self):
        for kind in ("derived", "support"):
            item = self.archive.file("a", kind, self.raw.read_bytes(), kind=kind)
            path = self.archive.file_path("a", kind); path.unlink()
            try:
                os.link(self.raw, path)
            except OSError as error:
                self.skipTest(f"hardlink capability unavailable: {error}")
            self.archive.write()
            self.reject(subject.audit_corpus, self.path, check_files=True, contains="hardlink alias")
            self.archive.manifests["a"]["files"].remove(item); path.unlink()

    def test_cross_capture_hardlinks_are_allowed_and_grouped(self):
        self.archive.add("b")
        other = self.archive.file_path("b", "raw"); other.unlink()
        try:
            os.link(self.raw, other)
        except OSError as error:
            self.skipTest(f"hardlink capability unavailable: {error}")
        item = self.archive.manifests["b"]["files"][0]
        item.update(size_bytes=self.raw.stat().st_size, sha256=sha(self.raw.read_bytes()))
        self.archive.write()
        report = subject.audit_corpus(self.path, check_files=True)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["groups"][0]["capture_ids"], ["a", "b"])
        self.assertEqual([e["reason"] for e in report["edges"]], ["artifact_sha256"])

    @contextmanager
    def identity_hook(self, *, path_zero=False, fd_zero=False, device_zero=False, mismatch=False, reparse=False):
        path_stat, fd_stat = Path.lstat, os.fstat
        original = self.raw.stat(); identity = original.st_dev, original.st_ino
        intercepted = {"path": 0, "descriptor": 0}
        def path_info(path, *args, **kwargs):
            info = path_stat(path, *args, **kwargs)
            if path == self.raw:
                intercepted["path"] += 1
                return StatView(info, st_ino=0 if path_zero else info.st_ino,
                                st_dev=0 if device_zero else info.st_dev)
            return info
        def fd_info(fd):
            info = fd_stat(fd)
            if (info.st_dev, info.st_ino) == identity:
                intercepted["descriptor"] += 1
                return StatView(info, st_ino=0 if fd_zero else info.st_ino + int(mismatch),
                                st_dev=0 if device_zero else info.st_dev,
                                st_file_attributes=0x400 if reparse else 0)
            return info
        with mock.patch.object(Path, "lstat", path_info), mock.patch.object(os, "fstat", fd_info):
            yield
        self.assertGreater(intercepted["path"], 0, "path identity hook must be reached")
        self.assertGreater(intercepted["descriptor"], 0, "descriptor identity hook must be reached")

    def test_usable_path_or_descriptor_identity_fallback_and_zero_device(self):
        for options in ({"path_zero": True}, {"fd_zero": True}, {"device_zero": True}):
            with self.subTest(options=options), self.identity_hook(**options):
                self.assertEqual(subject.audit_corpus(self.path, check_files=True)["file_check"], "verified")

    def test_missing_both_artifact_identities_rejects_alias_claim(self):
        with self.identity_hook(path_zero=True, fd_zero=True):
            self.reject(subject.audit_corpus, self.path, check_files=True, contains="identity unavailable")

    def test_opened_artifact_identity_mismatch_and_reparse_reject(self):
        with self.identity_hook(mismatch=True):
            self.reject(subject.audit_corpus, self.path, check_files=True, contains="identity mismatch")
        with self.identity_hook(reparse=True):
            self.reject(subject.audit_corpus, self.path, check_files=True, contains="reparse")

    def test_open_failures_close_all_acquired_descriptors(self):
        for target in (self.path, self.manifest, self.raw):
            def fail(path, *unused):
                if Path(path).name == target.name:
                    raise PermissionError("injected open denial")
            with instrument_open(before_open=fail) as (opened, events):
                self.reject(subject.audit_corpus, self.path, check_files=True, contains="injected open denial")
                self.assert_closed(opened)

    def test_stat_failures_are_contextual_and_release_descriptors(self):
        original_fstat, original_lstat = os.fstat, Path.lstat
        for target in (self.path, self.manifest, self.raw):
            identity = target.stat().st_dev, target.stat().st_ino
            for when in (1, 2):
                calls = 0
                def fail_fd(descriptor):
                    nonlocal calls
                    info = original_fstat(descriptor)
                    if (info.st_dev, info.st_ino) == identity:
                        calls += 1
                        if calls == when:
                            raise OSError("injected fstat failure")
                    return info
                with self.subTest(target=target.name, kind="fstat", when=when), \
                        instrument_open() as (opened, events):
                    with mock.patch.object(os, "fstat", fail_fd):
                        self.reject(subject.audit_corpus, self.path, check_files=True,
                                    contains="injected fstat failure")
                    self.assertEqual(calls, when)
                    self.assert_closed(opened)
            calls = 0
            def fail_path(path, *args, **kwargs):
                nonlocal calls
                if path == target:
                    calls += 1
                    raise PermissionError("injected lstat denial")
                return original_lstat(path, *args, **kwargs)
            with self.subTest(target=target.name, kind="lstat"), \
                    instrument_open() as (opened, events):
                with mock.patch.object(Path, "lstat", fail_path):
                    self.reject(subject.audit_corpus, self.path, check_files=True,
                                contains="injected lstat denial")
                self.assertEqual(calls, 1)
                self.assert_closed(opened)

    def test_fdopen_failure_and_cancellation_close_leaf(self):
        for error in (OSError("injected fdopen failure"), KeyboardInterrupt("cancel fdopen")):
            with instrument_open() as (opened, events), mock.patch.object(os, "fdopen", side_effect=error):
                if isinstance(error, KeyboardInterrupt):
                    with self.assertRaises(KeyboardInterrupt):
                        subject.load_corpus(self.path)
                else:
                    self.reject(subject.load_corpus, self.path, contains="injected fdopen failure")
                self.assert_closed(opened)

    def test_read_failures_and_cancellation_close_stream(self):
        for target in (self.path, self.manifest, self.raw):
            for error in (OSError("injected read failure"), KeyboardInterrupt("cancel read")):
                def fail(stream, size):
                    raise error
                with self.stream_hook(target, read_action=fail) as descriptors:
                    if isinstance(error, KeyboardInterrupt):
                        with self.assertRaises(KeyboardInterrupt):
                            subject.audit_corpus(self.path, check_files=True)
                    else:
                        self.reject(subject.audit_corpus, self.path, check_files=True, contains="injected read failure")
                    self.assert_closed(descriptors)

    def test_stream_close_failures_remain_contextual_and_closed(self):
        for target in (self.path, self.manifest, self.raw):
            with self.stream_hook(target, close_error=OSError("injected stream close")) as descriptors:
                self.reject(subject.audit_corpus, self.path, check_files=True, contains="injected stream close")
                self.assert_closed(descriptors)

    def test_parent_close_failure_after_leaf_open_releases_leaf_regression(self):
        self.require_dir_fd(); failed = False
        def fail_once(descriptor, events):
            nonlocal failed
            if not failed:
                failed = True
                raise OSError("injected parent close after actual close")
        with instrument_open(after_close=fail_once) as (opened, events):
            self.reject(subject.load_corpus, self.path, contains="injected parent close")
            self.assertTrue(failed)
            self.assert_closed(opened)

    def test_predecessor_close_failure_releases_new_child_regression(self):
        self.require_dir_fd(); failed = False
        def fail_child_transition(descriptor, events):
            nonlocal failed
            latest = next(event for event in reversed(events) if event[0] == "open")
            if not failed and Path(latest[2]).name == "captures":
                failed = True
                raise OSError("injected predecessor close after actual close")
        with instrument_open(after_close=fail_child_transition) as (opened, events):
            self.reject(subject.audit_corpus, self.path, contains="injected predecessor close")
            self.assertTrue(failed)
            self.assert_closed(opened)

    def test_fdopen_primary_and_cleanup_failure_keep_both_reasons(self):
        def cleanup_failure(descriptor, events):
            latest = next(event for event in reversed(events) if event[0] == "open")
            if descriptor == latest[1]:
                raise OSError("injected cleanup failure after actual close")
        with instrument_open(after_close=cleanup_failure) as (opened, events), \
                mock.patch.object(os, "fdopen", side_effect=OSError("primary fdopen failure")):
            error = self.reject(subject.load_corpus, self.path)
            self.assertIn("primary fdopen failure", str(error))
            self.assertIn("cleanup failure", str(error))
            self.assert_closed(opened)

    def test_fdopen_cancellation_survives_cleanup_error(self):
        def cleanup_failure(descriptor, events):
            latest = next(event for event in reversed(events) if event[0] == "open")
            if descriptor == latest[1]:
                raise OSError("cleanup failed after actual close")
        with instrument_open(after_close=cleanup_failure) as (opened, events), \
                mock.patch.object(os, "fdopen", side_effect=KeyboardInterrupt("cancel")):
            with self.assertRaises(KeyboardInterrupt):
                subject.load_corpus(self.path)
            self.assert_closed(opened)

    def test_short_metadata_read_and_appended_artifact_data_reject(self):
        def short(stream, size):
            return stream.read(size)[:-1]
        for target in (self.path, self.manifest):
            with self.stream_hook(target, read_action=short):
                self.reject(subject.audit_corpus, self.path, contains="size changed")
        changed = False
        def append_after_read(stream, size):
            nonlocal changed
            payload = stream.read(size)
            if not changed:
                try:
                    with self.raw.open("ab") as output:
                        output.write(b"!")
                except OSError as error:
                    self.skipTest(f"native append while reading unavailable: {error}")
                changed = True
            return payload
        with self.stream_hook(self.raw, read_action=append_after_read):
            self.reject(subject.audit_corpus, self.path, check_files=True)

    def test_artifact_read_requests_are_bounded_and_hash_all_bytes(self):
        payload = bytes(range(256)) * 600
        item = self.archive.manifests["a"]["files"][0]
        item.update(size_bytes=len(payload), sha256=sha(payload))
        self.raw.write_bytes(payload); self.archive.write()
        requested = []
        def observe(stream, size):
            requested.append(size)
            return stream.read(size)
        with self.stream_hook(self.raw, read_action=observe):
            report = subject.audit_corpus(self.path, check_files=True)
        self.assertGreater(len(requested), 2)
        self.assertTrue(all(0 < size <= 65536 for size in requested))
        observed = report["captures"][0]["files"][0]
        self.assertEqual(observed["observed_size_bytes"], len(payload))
        self.assertEqual(observed["observed_sha256"], sha(payload))

    def test_file_mutation_during_metadata_or_artifact_read_rejects(self):
        for target in (self.path, self.manifest, self.raw):
            original = target.read_bytes(); changed = False
            before = target.stat()
            def mutate(stream, size):
                nonlocal changed
                payload = stream.read(size)
                if not changed:
                    try:
                        with target.open("r+b") as writer:
                            writer.seek(0); writer.write(bytes([original[0] ^ 1]))
                        # Require an observable stamp change even when native
                        # write timestamps are coarser than this tiny fixture.
                        os.utime(target, ns=(before.st_atime_ns, before.st_mtime_ns + 2000000000))
                    except OSError as error:
                        self.skipTest(f"native mutation while reading unavailable: {error}")
                    changed = True
                    self.assertNotEqual(target.stat().st_mtime_ns, before.st_mtime_ns)
                return payload
            with self.stream_hook(target, read_action=mutate):
                self.reject(subject.audit_corpus, self.path, check_files=True)
            self.assertTrue(changed, "the actual in-place mutation must execute")
            target.write_bytes(original)

    def test_path_replacement_after_read_is_detected(self):
        original = self.raw.read_bytes(); changed = False
        def replace(stream, size):
            nonlocal changed
            payload = stream.read(size)
            if not changed:
                alternative = self.raw.with_name("replacement.bin")
                alternative.write_bytes(original)
                try:
                    alternative.replace(self.raw)
                except OSError as error:
                    self.skipTest(f"native replacement while reading unavailable: {error}")
                changed = True
            return payload
        with self.stream_hook(self.raw, read_action=replace):
            self.reject(subject.audit_corpus, self.path, check_files=True, contains="changed")

    def test_parent_alias_introduced_after_manifest_read_rejects(self):
        moved = self.archive.root / "moved-captures"; changed = False
        def replace_parent(stream, size):
            nonlocal changed
            payload = stream.read(size)
            if not changed:
                try:
                    self.manifest.parent.rename(moved)
                except OSError as error:
                    self.skipTest(f"native parent rename while reading unavailable: {error}")
                self.symlink(moved, self.manifest.parent, directory=True)
                changed = True
            return payload
        with self.stream_hook(self.manifest, read_action=replace_parent):
            self.reject(subject.audit_corpus, self.path, check_files=True)

    def test_selected_root_replaced_after_index_read_rejects(self):
        moved = self.work / "moved-root"; changed = False
        def replace_root(stream, size):
            nonlocal changed
            payload = stream.read(size)
            if not changed:
                try:
                    self.archive.root.rename(moved)
                except OSError as error:
                    self.skipTest(f"native root rename while reading unavailable: {error}")
                shutil.copytree(moved, self.archive.root)
                changed = True
            return payload
        with self.stream_hook(self.path, read_action=replace_root):
            self.reject(subject.audit_corpus, self.path, check_files=True)

    def test_above_root_ancestor_alias_retarget_is_detected(self):
        outer, other = self.work / "outer", self.work / "other"
        outer.mkdir()
        actual_root = outer / "archive"
        self.archive.root.rename(actual_root)
        shutil.copytree(outer, other)
        alias = self.work / "alias"
        self.symlink(outer, alias, directory=True)
        selected = alias / "archive" / self.path.name
        changed = False
        def retarget(stream, size):
            nonlocal changed
            payload = stream.read(size)
            if not changed:
                try:
                    alias.unlink()
                except OSError as error:
                    self.skipTest(f"native ancestor alias replacement unavailable: {error}")
                self.symlink(other, alias, directory=True)
                changed = True
            return payload
        with self.stream_hook(actual_root / self.path.name, read_action=retarget):
            self.reject(subject.audit_corpus, selected, check_files=True,
                        contains="changed")
        self.assertTrue(changed)

    def test_unrelated_sibling_creation_does_not_change_file_identity(self):
        changed = False
        def sibling(stream, size):
            nonlocal changed
            payload = stream.read(size)
            if not changed:
                changed = True
                (self.raw.parent / "sibling.txt").write_text("unrelated sibling")
            return payload
        with self.stream_hook(self.raw, read_action=sibling):
            self.assertEqual(subject.audit_corpus(self.path, check_files=True)["status"], "pass")

    def test_audio_observation_must_match_verified_bytes(self):
        inspector = capture_audio.inspect_audio
        def changed(*args, **kwargs):
            report = inspector(*args, **kwargs)
            report["sha256"] = "0" * 64
            return report
        with mock.patch.object(capture_audio, "inspect_audio", changed):
            self.reject(subject.audit_corpus, self.path, check_files=True, check_audio=True,
                        contains="changed from verified identity")

    def test_rejected_cli_has_no_report_and_preserves_all_inputs(self):
        self.raw.write_bytes(b"bad")
        (self.work / "prior-report.json").write_bytes(b'{"preserve":"existing output"}\n')
        before = {str(path.relative_to(self.work)): path.read_bytes() if path.is_file() else None
                  for path in self.work.rglob("*")}
        result = subprocess.run([sys.executable, "-B", str(ROOT / "tools" / "capture_corpus.py"),
                                 "--input", str(self.path), "--check-files", "--check-audio"],
                                cwd=self.work, capture_output=True, timeout=20, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"corpus error:", result.stderr)
        self.assertIn(b"file 'raw'", result.stderr)
        after = {str(path.relative_to(self.work)): path.read_bytes() if path.is_file() else None
                 for path in self.work.rglob("*")}
        self.assertEqual(after, before)

    def test_cli_bytes_bypass_text_newline_and_encoding_translation(self):
        for target, expected_status in ((self.path, 0), (self.work / "missing-é.json", 1)):
            with self.subTest(target=target.name):
                out_bytes, error_bytes = io.BytesIO(), io.BytesIO()
                out = io.TextIOWrapper(out_bytes, encoding="ascii", newline="\r\n")
                error = io.TextIOWrapper(error_bytes, encoding="ascii", newline="\r\n")
                try:
                    with mock.patch.object(sys, "stdout", out), mock.patch.object(sys, "stderr", error):
                        self.assertEqual(subject.main(["--input", str(target), "--check-files"]),
                                         expected_status)
                    out.flush()
                    error.flush()
                    if expected_status == 0:
                        actual = out_bytes.getvalue()
                        expected = (json.dumps(json.loads(actual), sort_keys=True, indent=2,
                                               ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
                        self.assertEqual(actual, expected)
                        self.assertEqual(error_bytes.getvalue(), b"")
                    else:
                        self.assertEqual(out_bytes.getvalue(), b"")
                        message = error_bytes.getvalue().decode("utf-8")
                        self.assertIn("corpus error:", message)
                        self.assertIn("missing-é.json", message)
                        self.assertTrue(message.endswith("\n"))
                        self.assertNotIn("\r\n", message)
                finally:
                    out.close()
                    error.close()

    def test_unicode_inputs_and_rejection_match_stringio_and_legacy_bytes(self):
        archive = _Archive(self.work / "archive-café-東京")
        capture = archive.add("unicode-path")
        capture["specimen"]["variant"]["value"] = "Synthetic café-東京"
        path = archive.write()
        report = subject.audit_corpus(path, check_files=True)
        self.assertEqual(report["captures"][0]["capture_id"], "unicode-path")
        missing = self.work / "missing-café-東京.json"
        rejected = self.reject(subject.audit_corpus, missing, check_files=True)
        cases = ((path, 0, _json_bytes(report)),
                 (missing, 1, f"corpus error: {rejected}\n".encode("utf-8")))
        for target, expected_status, expected in cases:
            if expected_status == 1:
                self.assertIn("café-東京".encode("utf-8"), expected)
            for text_only in (False, True):
                with self.subTest(target=target.name, text_only=text_only):
                    out, error = ((io.StringIO(), io.StringIO()) if text_only else
                                  (io.TextIOWrapper(io.BytesIO(), encoding="cp1252", newline="\r\n"),
                                   io.TextIOWrapper(io.BytesIO(), encoding="cp1252", newline="\r\n")))
                    try:
                        with mock.patch.object(sys, "stdout", out), mock.patch.object(sys, "stderr", error):
                            self.assertEqual(subject.main(["--input", str(target), "--check-files"]),
                                             expected_status)
                        out.flush(); error.flush()
                        actual, unused = (out, error) if expected_status == 0 else (error, out)
                        if text_only:
                            self.assertEqual(actual.getvalue(), expected.decode("utf-8"))
                            self.assertEqual(unused.getvalue(), "")
                        else:
                            self.assertEqual(actual.buffer.getvalue(), expected)
                            self.assertEqual(unused.buffer.getvalue(), b"")
                    finally:
                        out.close(); error.close()
            # Counterexample: the real text layer translates report LFs and
            # cannot encode the Unicode diagnostic. The corpus report retains
            # ASCII IDs/paths, not the free-text specimen metadata above.
            with io.TextIOWrapper(io.BytesIO(), encoding="cp1252", newline="\r\n") as control:
                if expected_status == 0:
                    control.write(expected.decode("utf-8")); control.flush()
                    self.assertEqual(control.buffer.getvalue(), expected.replace(b"\n", b"\r\n"))
                    self.assertNotEqual(control.buffer.getvalue(), expected)
                else:
                    with self.assertRaises(UnicodeEncodeError):
                        control.write(expected.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
