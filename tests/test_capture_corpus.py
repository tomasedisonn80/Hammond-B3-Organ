#!/usr/bin/env python3
"""Independent capture-corpus contract acceptance with tiny synthetic archives.

Fixtures are assembled here from literal dictionaries and struct-packed audio.
Expected hashes, edges, groups and findings do not call producer internals.
Filesystem race/resource torture and JSON Schema parity have separate suites.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from capture_corpus import CorpusError, audit_corpus, load_corpus, validate_corpus


TOOL = ROOT / "tools" / "capture_corpus.py"
CLAIMS = {
    "independence", "final_holdout_history", "authenticity", "specimen_identity",
    "calibration", "permissions", "physical_fidelity",
}
REPORT_KEYS = {
    "schema_version", "contract_origin", "corpus_id", "index_sha256", "mode",
    "status", "structural_validation", "file_check", "audio_check", "captures",
    "edges", "groups", "findings",
} | CLAIMS
CAPTURE_KEYS = {
    "capture_id", "manifest_path", "expected_manifest_sha256",
    "observed_manifest_sha256", "record_status", "capture_kind", "purpose",
    "v1_role", "session_id", "v1_group_id", "relation_labels",
    "parent_capture_ids", "files",
}
FILE_KEYS = {
    "file_id", "kind", "path", "expected_size_bytes", "expected_sha256",
    "observed_size_bytes", "observed_sha256", "expected_audio", "audio_status",
    "audio_reason", "observed_audio",
}


def _sha(payload):
    return hashlib.sha256(payload).hexdigest()


def _json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


def _known(value):
    return {"value": value, "unknown_reason": None}


def _unknown(reason="No physical observation exists in this synthetic test."):
    return {"value": None, "unknown_reason": reason}


def _calibration(unit=None):
    return {
        "status": "not_applicable" if unit is None else "uncalibrated",
        "value": None, "unit": unit, "standard_uncertainty": None,
        "evidence": None,
        "unknown_reason": "Synthetic acceptance fixture; no physical calibration.",
    }


def _channel(index, hardware=False):
    return {
        "channel_id": f"channel-{index}", "index": index,
        "boundary": _known("electrical_voltage" if hardware else "synthetic"),
        "port_reference": _unknown(),
        "calibration": _calibration("V/FS" if hardware else None),
    }


def _chunk(name, payload):
    return name + struct.pack("<I", len(payload)) + payload + (b"\0" if len(payload) & 1 else b"")


def _wave(values, *, rate=48000, channels=1, floating=False, bits=16, junk=None):
    """Literal ordinary-tag WAV writer, independent of all production tools."""
    tag = 3 if floating else 1
    code = {16: "h", 32: "f" if floating else "i", 64: "d"}[bits]
    data = struct.pack("<" + code * len(values), *values)
    alignment = channels * (bits // 8)
    fmt = struct.pack("<HHIIHH", tag, channels, rate, rate * alignment,
                      alignment, bits)
    body = b"WAVE" + _chunk(b"fmt ", fmt)
    if junk is not None:
        body += _chunk(b"JUNK", junk)
    body += _chunk(b"data", data)
    return b"RIFF" + struct.pack("<I", len(body)) + body


def _decoded(values, *, rate=48000, channels=1):
    """Hash the contract's literal preimage, never decoded producer output."""
    payload = (b"HAMMOND-CAPTURE-DECODED-V1\x00"
               + struct.pack("<IIQ", rate, channels, len(values) // channels))
    payload += b"".join(struct.pack("<d", 0.0 if x == 0.0 else x) for x in values)
    return _sha(payload)


def _edge(reason, value, left, right, basis, left_file=None, right_file=None):
    return {
        "left_capture_id": left, "right_capture_id": right,
        "reason": reason, "basis": basis, "value": value,
        "left_file_id": left_file, "right_file_id": right_file,
    }


def _edge_key(edge):
    return (edge["reason"], edge["value"], edge["left_capture_id"],
            edge["right_capture_id"], edge["left_file_id"] or "",
            edge["right_file_id"] or "", edge["basis"])


def _group(ids, purposes, status):
    return {"component_id": min(ids), "capture_ids": sorted(ids),
            "purposes": sorted(set(purposes)), "status": status}


def _finding(code, component, ids, files=()):
    return {
        "code": code,
        "severity": "error" if code == "cross_purpose_component" else "inconclusive",
        "component_id": component, "capture_ids": sorted(ids),
        "file_refs": [{"capture_id": c, "file_id": f} for c, f in sorted(files)],
    }


def _finding_key(item):
    return (item["code"], item["component_id"], tuple(item["capture_ids"]),
            tuple((ref["capture_id"], ref["file_id"]) for ref in item["file_refs"]))


class _Archive:
    """Small independent v1/index author; not a production validator or oracle."""

    def __init__(self, root):
        self.root = Path(root)
        (self.root / "captures").mkdir(parents=True)
        self.index = {"schema_version": 1,
                      "contract_origin": "project-proposed-corpus-v1",
                      "corpus_id": "synthetic-acceptance", "captures": []}
        self.manifests = {}
        self.entries = {}
        self.payloads = {}
        self.path = self.root / "corpus.json"

    def add(self, ident, purpose="fit", *, raw=None, rate=48000, channels=1,
            format_name="wav_pcm16", planned=False, hardware=False,
            session=None, group=None, labels=(), parents=()):
        record = {
            "schema_version": 1, "contract_origin": "project-proposed-v1",
            "capture_id": ident, "status": "planned" if planned else "recorded",
            "status_reason": "Synthetic unacquired plan." if planned else None,
            "capture_kind": "hardware" if hardware else "synthetic",
            "specimen": {
                "specimen_id": _unknown(),
                "variant": _known("Synthetic test metadata; no physical specimen."),
                "revision": _known("unittest-fixture-v1"),
                "identity_evidence": _unknown(),
            },
            "acquisition": {
                "started_at_utc": _unknown() if planned else _known("2026-01-01T00:00:00Z"),
                "operator_id": _known("synthetic-test-author"),
                "session_id": (_unknown() if planned and session is None
                               else _known(session or f"session-{ident}")),
            },
            "digital": {
                "format": _unknown() if planned else _known(format_name),
                "sample_rate_hz": _unknown() if planned else _known(rate),
                "channel_count": _unknown() if planned else _known(channels),
                "channels": [] if planned else [_channel(i, hardware) for i in range(channels)],
            },
            "physical_clock": _calibration("Hz" if hardware else None),
            "stimulus": {key: _unknown() for key in
                         ("description", "controls", "conditions", "synchronization")},
            "signal_path": {key: _unknown() for key in ("description", "bypass", "loading")},
            "files": [],
            "partition": {
                "role": {"fit": "fit", "validation": "held_out", "final": "held_out",
                         "unassigned": "unassigned"}[purpose],
                "group_id": (_unknown() if planned and purpose == "unassigned" and group is None
                             else _known(group or f"group-{ident}")),
                "rationale": "Explicit synthetic acceptance assignment only.",
            },
            "rights": _known("Generated unittest fixtures; no acquired recording."),
        }
        entry = {"capture_id": ident, "manifest_path": f"captures/{ident}.json",
                 "manifest_sha256": "0" * 64, "purpose": purpose,
                 "relation_labels": copy.deepcopy(list(labels)),
                 "parent_capture_ids": list(parents), "derived_audio": []}
        self.manifests[ident] = record
        self.entries[ident] = entry
        self.index["captures"].append(entry)
        if not planned:
            if raw is None:
                code = 1 + sum((n + 1) * ord(c) for n, c in enumerate(ident)) % 16000
                raw = _wave([code, -code], rate=rate, channels=channels)
            self.file(ident, "raw", raw, kind="raw")
        return record

    def file(self, ident, file_id, payload, *, kind="derived", parents=("raw",), descriptor=None):
        path = f"{ident}/{file_id}.bin"
        item = {"file_id": file_id, "kind": kind, "path": path,
                "size_bytes": len(payload), "sha256": _sha(payload),
                "parents": list(parents) if kind == "derived" else [],
                "derivation": ({"operation": "synthetic-fixture", "tool": "unittest",
                                "tool_version": "1", "parameters": "Literal bytes, not executed fitting."}
                               if kind == "derived" else None)}
        self.manifests[ident]["files"].append(item)
        target = self.root / "captures" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        self.payloads[(ident, file_id)] = payload
        if descriptor is not None:
            self.entries[ident]["derived_audio"].append({"file_id": file_id, **descriptor})
        return item

    def write(self):
        for ident, record in self.manifests.items():
            payload = _json_bytes(record)
            entry = self.entries[ident]
            (self.root / entry["manifest_path"]).write_bytes(payload)
            entry["manifest_sha256"] = _sha(payload)
        self.path.write_bytes(_json_bytes(self.index))
        return self.path

    def file_path(self, ident, file_id):
        item = next(f for f in self.manifests[ident]["files"] if f["file_id"] == file_id)
        return (self.root / self.entries[ident]["manifest_path"]).parent / item["path"]


class CorpusAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hammond-corpus-test-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.archive = _Archive(self.work / "archive")

    def assert_report(self, report):
        self.assertEqual(set(report), REPORT_KEYS)
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["contract_origin"], "project-proposed-corpus-report-v1")
        self.assertEqual(report["structural_validation"], "pass")
        for field in CLAIMS:
            self.assertEqual(report[field], "not_established")
        for capture in report["captures"]:
            self.assertEqual(set(capture), CAPTURE_KEYS)
            self.assertEqual(capture["expected_manifest_sha256"], capture["observed_manifest_sha256"])
            for item in capture["files"]:
                self.assertEqual(set(item), FILE_KEYS)
        self.assertEqual(report["edges"], sorted(report["edges"], key=_edge_key))
        self.assertEqual(report["findings"], sorted(report["findings"], key=_finding_key))
        self.assertNotIn(str(self.archive.root), json.dumps(report))

    def cli(self, path, *flags):
        return subprocess.run([sys.executable, "-B", str(TOOL), "--input", str(path), *flags],
                              cwd=self.work, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=20, check=False)

    def test_validate_and_load_preserve_exact_supplied_index(self):
        self.archive.add("a", planned=True)
        path = self.archive.write()
        value = copy.deepcopy(self.archive.index)
        before = copy.deepcopy(value)
        self.assertIsNone(validate_corpus(value))
        self.assertEqual(value, before)
        loaded = load_corpus(path)
        self.assertEqual(loaded, value)
        self.assertIsNot(loaded, value)
        # Public structural validation cannot depend on manifest existence.
        (self.archive.root / "captures/a.json").unlink()
        self.assertIsNone(validate_corpus(value))

    def test_planned_hardware_in_all_modes_is_inconclusive(self):
        self.archive.add("plan", "unassigned", planned=True, hardware=True)
        path = self.archive.write()
        for files, audio, mode in ((False, False, "structural_only"),
                                   (True, False, "files_checked"),
                                   (True, True, "files_and_audio_checked")):
            with self.subTest(mode=mode):
                report = audit_corpus(path, check_files=files, check_audio=audio)
                self.assert_report(report)
                self.assertEqual(report["mode"], mode)
                self.assertEqual(report["status"], "inconclusive")
                self.assertEqual(report["file_check"], "not_applicable" if files else "not_run")
                self.assertEqual(report["audio_check"], "not_applicable" if audio else "not_run")
                self.assertEqual(report["captures"][0]["files"], [])
                self.assertEqual(report["captures"][0]["capture_kind"], "hardware")
                self.assertEqual(report["groups"], [_group(["plan"], ["unassigned"], "inconclusive")])
                self.assertEqual(report["findings"], [
                    _finding("planned_capture", "plan", ["plan"]),
                    _finding("unassigned_capture", "plan", ["plan"]),
                ])

    def test_all_four_purposes_retain_v1_role_mapping(self):
        for purpose in ("fit", "validation", "final", "unassigned"):
            self.archive.add(purpose, purpose)
        report = audit_corpus(self.archive.write(), check_files=True, check_audio=True)
        self.assert_report(report)
        self.assertEqual([(c["purpose"], c["v1_role"]) for c in report["captures"]],
                         [("final", "held_out"), ("fit", "fit"),
                          ("unassigned", "unassigned"), ("validation", "held_out")])
        self.assertEqual(report["edges"], [])
        self.assertEqual(report["status"], "inconclusive")
        self.assertEqual(report["findings"], [_finding("unassigned_capture", "unassigned", ["unassigned"])])

    def test_role_mismatch_rejected_for_planned_and_recorded(self):
        for planned in (False, True):
            for purpose, wrong in (("fit", "held_out"), ("validation", "fit"),
                                   ("final", "unassigned"), ("unassigned", "held_out")):
                with self.subTest(planned=planned, purpose=purpose):
                    fixture = _Archive(self.work / f"role-{planned}-{purpose}")
                    record = fixture.add("a", purpose, planned=planned)
                    record["partition"]["role"] = wrong
                    record["partition"]["group_id"] = _known("some-group")
                    with self.assertRaisesRegex(CorpusError, "purpose .*requires"):
                        audit_corpus(fixture.write())

    def test_manifest_capture_id_must_match_index(self):
        self.archive.add("indexed")["capture_id"] = "different"
        with self.assertRaisesRegex(CorpusError, "capture_id.*expected 'indexed'.*different"):
            audit_corpus(self.archive.write())

    def test_index_identity_uniqueness_is_not_whole_object_uniqueness(self):
        self.archive.add("a")
        self.archive.add("b")
        self.archive.write()
        cases = (("capture_id", "a"), ("manifest_path", "CAPTURES/A.JSON"),
                 ("manifest_sha256", self.archive.entries["a"]["manifest_sha256"]))
        for field, value in cases:
            with self.subTest(field=field):
                index = copy.deepcopy(self.archive.index)
                index["captures"][1][field] = value
                before = copy.deepcopy(index)
                with self.assertRaises(CorpusError):
                    validate_corpus(index)
                self.assertEqual(index, before)

    def test_parent_resolution_self_duplicates_and_cycles_are_rejected(self):
        for ident in ("a", "b", "c", "d"):
            self.archive.add(ident)
        self.archive.write()
        bad = (
            {"a": ["missing"]}, {"a": ["a"]}, {"a": ["b", "b"]},
            {"a": ["b"], "b": ["a"]},
            {"a": ["b"], "b": ["c"], "c": ["d"], "d": ["a"]},
        )
        for parents in bad:
            with self.subTest(parents=parents):
                index = copy.deepcopy(self.archive.index)
                for entry in index["captures"]:
                    entry["parent_capture_ids"] = parents.get(entry["capture_id"], [])
                with self.assertRaises(CorpusError):
                    validate_corpus(index)

    def test_parent_chain_keeps_unassigned_plan_inside_failed_component(self):
        self.archive.add("a", "fit")
        self.archive.add("b", "unassigned", planned=True, parents=["a"])
        self.archive.add("c", "final", parents=["b"])
        report = audit_corpus(self.archive.write())
        self.assert_report(report)
        self.assertEqual(report["edges"], [
            _edge("parent_capture", "a", "b", "a", "index_declaration"),
            _edge("parent_capture", "b", "c", "b", "index_declaration"),
        ])
        self.assertEqual(report["groups"], [_group(["a", "b", "c"], ["fit", "final", "unassigned"], "failed")])
        self.assertEqual(report["findings"], [
            _finding("cross_purpose_component", "a", ["a", "b", "c"]),
            _finding("planned_capture", "a", ["b"]),
            _finding("unassigned_capture", "a", ["b"]),
        ])

    def test_each_declared_equality_reason_has_exact_basis_and_edges(self):
        cases = (("session_id", {"session": "shared"}, "manifest_declaration"),
                 ("v1_group_id", {"group": "shared"}, "manifest_declaration"),
                 ("gesture_label", {"labels": [{"kind": "gesture", "label": "shared"}]}, "index_declaration"),
                 ("family_label", {"labels": [{"kind": "family", "label": "shared"}]}, "index_declaration"))
        for reason, kwargs, basis in cases:
            with self.subTest(reason=reason):
                fixture = _Archive(self.work / reason)
                fixture.add("b", "validation", **kwargs)
                fixture.add("a", "fit", **kwargs)
                report = audit_corpus(fixture.write())
                self.assert_report(report)
                self.assertEqual(report["edges"], [_edge(reason, "shared", "a", "b", basis)])
                self.assertEqual(report["groups"], [_group(["a", "b"], ["fit", "validation"], "failed")])

    def test_gesture_and_family_labels_are_distinct_namespaces(self):
        self.archive.add("a", "fit", labels=[{"kind": "gesture", "label": "same"}])
        self.archive.add("b", "final", labels=[{"kind": "family", "label": "same"}])
        report = audit_corpus(self.archive.write())
        self.assertEqual(report["edges"], [])
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["groups"], [_group(["a"], ["fit"], "pass"), _group(["b"], ["final"], "pass")])

    def test_null_planned_identities_do_not_create_edges(self):
        for ident in ("a", "b", "c"):
            self.archive.add(ident, "unassigned", planned=True)
        report = audit_corpus(self.archive.write())
        self.assertEqual(report["edges"], [])
        self.assertEqual(report["groups"], [_group([ident], ["unassigned"], "inconclusive") for ident in ("a", "b", "c")])
        self.assertEqual(len(report["findings"]), 6)

    def test_shared_operator_specimen_and_support_do_not_merge_groups(self):
        for ident, purpose in (("a", "fit"), ("b", "final")):
            record = self.archive.add(ident, purpose, hardware=True)
            record["specimen"]["specimen_id"] = _known("declared-common-specimen")
            self.archive.file(ident, "support", b"Shared non-audio support document.\n", kind="support")
        report = audit_corpus(self.archive.write(), check_files=True, check_audio=True)
        self.assert_report(report)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["edges"], [])
        for capture in report["captures"]:
            support = next(x for x in capture["files"] if x["file_id"] == "support")
            self.assertEqual(support["audio_status"], "excluded_support")
            self.assertEqual(support["audio_reason"], "support_not_audio_scope")
            self.assertIsNone(support["expected_audio"])
            self.assertIsNone(support["observed_audio"])
            self.assertEqual(support["observed_sha256"], _sha(b"Shared non-audio support document.\n"))

    def test_each_distinct_known_purpose_pair_fails(self):
        for left, right in (("fit", "validation"), ("fit", "final"), ("validation", "final")):
            with self.subTest(left=left, right=right):
                fixture = _Archive(self.work / f"pair-{left}-{right}")
                fixture.add("a", left, group="same-group")
                fixture.add("b", right, group="same-group")
                report = audit_corpus(fixture.write())
                self.assertEqual(report["status"], "failed")
                self.assertEqual(report["findings"], [_finding("cross_purpose_component", "a", ["a", "b"])])

    def test_transitive_different_reasons_join_complete_group(self):
        self.archive.add("a", "fit", session="ab")
        self.archive.add("b", "fit", session="ab", group="bc")
        self.archive.add("c", "fit", group="bc", labels=[{"kind": "family", "label": "cd"}])
        self.archive.add("d", "final", labels=[{"kind": "family", "label": "cd"}])
        report = audit_corpus(self.archive.write())
        expected = [_edge("session_id", "ab", "a", "b", "manifest_declaration"),
                    _edge("v1_group_id", "bc", "b", "c", "manifest_declaration"),
                    _edge("family_label", "cd", "c", "d", "index_declaration")]
        self.assertEqual(report["edges"], sorted(expected, key=_edge_key))
        self.assertEqual(report["groups"], [_group(["a", "b", "c", "d"], ["fit", "final"], "failed")])
        self.assertEqual(report["findings"], [_finding("cross_purpose_component", "a", ["a", "b", "c", "d"])])

    def test_all_seven_reasons_retained_on_already_connected_nodes(self):
        raw = _wave([0, 8192, -16384, 0])
        labels = [{"kind": "gesture", "label": "gesture-x"}, {"kind": "family", "label": "family-x"}]
        self.archive.add("a", "fit", raw=raw, session="session-x", group="group-x", labels=labels)
        self.archive.add("b", "final", raw=raw, session="session-x", group="group-x", labels=labels, parents=["a"])
        report = audit_corpus(self.archive.write(), check_files=True, check_audio=True)
        decoded = "4cc959a21407b8f45476ffa9794f7b8e78b7626a3cb7f03408cf2255b7c66ce6"
        self.assertEqual(_decoded([0.0, 0.25, -0.5, 0.0]), decoded)
        expected = [
            _edge("artifact_sha256", _sha(raw), "a", "b", "verified_bytes", "raw", "raw"),
            _edge("decoded_audio_sha256", decoded, "a", "b", "verified_audio", "raw", "raw"),
            _edge("family_label", "family-x", "a", "b", "index_declaration"),
            _edge("gesture_label", "gesture-x", "a", "b", "index_declaration"),
            _edge("parent_capture", "a", "b", "a", "index_declaration"),
            _edge("session_id", "session-x", "a", "b", "manifest_declaration"),
            _edge("v1_group_id", "group-x", "a", "b", "manifest_declaration"),
        ]
        self.assert_report(report)
        self.assertEqual(report["edges"], sorted(expected, key=_edge_key))
        self.assertEqual(report["groups"], [_group(["a", "b"], ["fit", "final"], "failed")])

    def test_raw_byte_equality_basis_tracks_requested_evidence_mode(self):
        raw = _wave([100, -200])
        self.archive.add("a", "fit", raw=raw)
        self.archive.add("b", "validation", raw=raw)
        path = self.archive.write()
        for check_files, basis in ((False, "manifest_declaration"), (True, "verified_bytes")):
            with self.subTest(check_files=check_files):
                report = audit_corpus(path, check_files=check_files)
                self.assertEqual(report["edges"], [_edge("artifact_sha256", _sha(raw), "a", "b", basis, "raw", "raw")])
                self.assertEqual(report["status"], "failed")
                for capture in report["captures"]:
                    item = capture["files"][0]
                    self.assertEqual(item["expected_sha256"], _sha(raw))
                    self.assertEqual(item["observed_sha256"], _sha(raw) if check_files else None)
                    self.assertIsNone(item["observed_audio"])

    def test_raw_to_derived_and_derived_to_derived_bytes_merge(self):
        payload = _wave([700, -800])
        for left_kind, right_kind in (("raw", "derived"), ("derived", "derived")):
            with self.subTest(left=left_kind, right=right_kind):
                fixture = _Archive(self.work / f"content-{left_kind}-{right_kind}")
                for ident, purpose, kind in (("a", "fit", left_kind), ("b", "final", right_kind)):
                    fixture.add(ident, purpose, raw=payload if kind == "raw" else None)
                    if kind == "derived":
                        fixture.file(ident, "derived", payload)
                report = audit_corpus(fixture.write(), check_files=True)
                self.assertEqual(report["edges"], [
                    _edge("artifact_sha256", _sha(payload), "a", "b", "verified_bytes", left_kind, right_kind)
                ])
                self.assertEqual(report["status"], "failed")

    def test_support_equal_to_another_raw_file_is_excluded_from_content_graph(self):
        raw = _wave([123, -456])
        self.archive.add("a", "fit", raw=raw)
        self.archive.add("b", "final")
        self.archive.file("b", "matching-support", raw, kind="support")
        report = audit_corpus(self.archive.write(), check_files=True, check_audio=True)
        self.assertEqual(report["edges"], [])
        self.assertEqual(report["status"], "pass")

    def test_harmless_wrapper_difference_only_merges_after_actual_audio_check(self):
        plain = _wave([0, 8192, -16384, 0])
        wrapped = _wave([0, 8192, -16384, 0], junk=b"odd")
        self.assertNotEqual(_sha(plain), _sha(wrapped))
        self.archive.add("a", "fit", raw=plain)
        self.archive.add("b", "final", raw=wrapped)
        path = self.archive.write()
        files = audit_corpus(path, check_files=True)
        self.assertEqual(files["edges"], [])
        self.assertEqual(files["status"], "pass")
        audio = audit_corpus(path, check_files=True, check_audio=True)
        expected = _decoded([0.0, 0.25, -0.5, 0.0])
        self.assertEqual(audio["edges"], [_edge("decoded_audio_sha256", expected, "a", "b", "verified_audio", "raw", "raw")])
        self.assertEqual(audio["status"], "failed")
        for capture in audio["captures"]:
            self.assertEqual(capture["files"][0]["observed_audio"]["decoded_sha256"], expected)

    def test_compatible_encodings_share_independent_decoded_identity(self):
        streams = (("pcm", "wav_pcm16", _wave([0, 8192, -16384, 0])),
                   ("float", "wav_float32", _wave([0.0, 0.25, -0.5, 0.0], floating=True, bits=32)),
                   ("raw", "raw_float32_le", struct.pack("<4f", 0, 0.25, -0.5, 0)))
        for ident, format_name, payload in streams:
            self.archive.add(ident, raw=payload, format_name=format_name)
        report = audit_corpus(self.archive.write(), check_files=True, check_audio=True)
        digest = _decoded([0.0, 0.25, -0.5, 0.0])
        self.assertEqual(report["edges"], [
            _edge("decoded_audio_sha256", digest, "float", "pcm", "verified_audio", "raw", "raw"),
            _edge("decoded_audio_sha256", digest, "float", "raw", "verified_audio", "raw", "raw"),
        ])
        self.assertEqual(report["groups"], [_group(["float", "pcm", "raw"], ["fit"], "pass")])

    def test_signed_zero_does_not_change_decoded_identity(self):
        left = _wave([-0.0, 0.0], floating=True, bits=32)
        right = _wave([0.0, -0.0], floating=True, bits=64)
        self.archive.add("a", "fit", raw=left, format_name="wav_float32")
        self.archive.add("b", "final", raw=right, format_name="wav_float64")
        report = audit_corpus(self.archive.write(), check_files=True, check_audio=True)
        self.assertEqual(report["edges"], [_edge("decoded_audio_sha256", _decoded([0.0, 0.0]), "a", "b", "verified_audio", "raw", "raw")])

    def test_decoded_geometry_order_duration_and_samples_are_not_silently_equated(self):
        base = [0.25, -0.5, 0.75, 0.0]
        cases = (("rate", base, 24000, 2),
                 ("channels", base, 48000, 1),
                 ("order", [-0.5, 0.25, 0.0, 0.75], 48000, 2),
                 ("duration", base + [0.0, 0.0], 48000, 2),
                 ("sample", [0.25, -0.5, 0.5, 0.0], 48000, 2))
        for name, samples, rate, channels in cases:
            with self.subTest(case=name):
                fixture = _Archive(self.work / f"decoded-{name}")
                fixture.add("a", "fit", raw=struct.pack("<4f", *base), channels=2, format_name="raw_float32_le")
                fixture.add("b", "final", raw=struct.pack("<" + "f" * len(samples), *samples),
                            rate=rate, channels=channels, format_name="raw_float32_le")
                report = audit_corpus(fixture.write(), check_files=True, check_audio=True)
                expected = [_decoded(base, channels=2), _decoded(samples, rate=rate, channels=channels)]
                self.assertNotEqual(expected[0], expected[1])
                self.assertEqual([c["files"][0]["observed_audio"]["decoded_sha256"] for c in report["captures"]], expected)
                # Rate/count live outside headerless raw bytes. Different
                # decoded geometry cannot erase their independent byte edge.
                if name in ("rate", "channels"):
                    self.assertEqual(report["edges"], [
                        _edge("artifact_sha256", _sha(struct.pack("<4f", *base)),
                              "a", "b", "verified_bytes", "raw", "raw")
                    ])
                    self.assertEqual(report["status"], "failed")
                else:
                    self.assertEqual(report["edges"], [])
                    self.assertEqual(report["status"], "pass")

    def test_derivative_uses_its_own_raw_float_geometry(self):
        self.archive.add("a", raw=_wave([0, 8192, -16384, 0]))
        descriptor = {"format": "raw_float32_le", "sample_rate_hz": 24000, "channel_count": 2}
        self.archive.file("a", "derived", struct.pack("<2f", 0.25, -0.5), descriptor=descriptor)
        report = audit_corpus(self.archive.write(), check_files=True, check_audio=True)
        self.assertEqual(report["status"], "pass")
        derivative, raw = report["captures"][0]["files"]
        self.assertEqual(derivative["expected_audio"], descriptor)
        self.assertEqual(derivative["observed_audio"], {
            **descriptor, "frame_count": 1,
            "decoded_digest_version": "hammond-capture-decoded-v1",
            "decoded_sha256": "9326afae23b16ec1f263f6c21e47616630d6e505798b8037476cc55a7cc4b598",
        })
        self.assertEqual(raw["expected_audio"], {"format": "wav_pcm16", "sample_rate_hz": 48000, "channel_count": 1})
        self.assertEqual(raw["observed_audio"]["frame_count"], 4)

    def test_raw_format_rate_and_channel_declarations_are_asserted(self):
        for field, value in (("format", "wav_pcm24"), ("sample_rate_hz", 24000), ("channel_count", 2)):
            with self.subTest(field=field):
                fixture = _Archive(self.work / f"raw-assertion-{field}")
                record = fixture.add("a", raw=_wave([0, 8192]))
                record["digital"][field] = _known(value)
                if field == "channel_count":
                    record["digital"]["channels"] = [_channel(i) for i in range(value)]
                with self.assertRaises(CorpusError) as caught:
                    audit_corpus(fixture.write(), check_files=True, check_audio=True)
                message = str(caught.exception)
                self.assertIn("captures/a.json", message)
                self.assertIn("capture 'a'", message)
                self.assertIn("file 'raw'", message)
                self.assertIn("mismatch", message)

    def test_derived_descriptor_must_resolve_only_to_derived_file(self):
        self.archive.add("a")
        self.archive.file("a", "support", b"not audio", kind="support")
        for file_id in ("missing", "raw", "support"):
            with self.subTest(file_id=file_id):
                self.archive.entries["a"]["derived_audio"] = [
                    {"file_id": file_id, "format": "wav_pcm16", "sample_rate_hz": 48000, "channel_count": 1}
                ]
                with self.assertRaisesRegex(CorpusError, "derived_audio"):
                    audit_corpus(self.archive.write())

    def test_omitted_derivatives_remain_individually_inconclusive(self):
        self.archive.add("a")
        for file_id in ("zeta", "alpha"):
            self.archive.file("a", file_id, ("unclassified " + file_id).encode())
        path = self.archive.write()
        files = audit_corpus(path, check_files=True)
        self.assertEqual(files["status"], "pass")
        report = audit_corpus(path, check_files=True, check_audio=True)
        self.assertEqual(report["status"], "inconclusive")
        self.assertEqual(report["audio_check"], "partial")
        self.assertEqual(report["findings"], [
            _finding("derived_audio_not_declared", "a", ["a"], [("a", "alpha")]),
            _finding("derived_audio_not_declared", "a", ["a"], [("a", "zeta")]),
        ])
        for item in report["captures"][0]["files"]:
            if item["kind"] == "derived":
                self.assertEqual(item["audio_status"], "not_inspected")
                self.assertEqual(item["audio_reason"], "derived_audio_not_declared")
                self.assertIsNone(item["expected_audio"])
                self.assertIsNone(item["observed_audio"])
                self.assertEqual(item["observed_sha256"], item["expected_sha256"])

    def test_failed_report_keeps_all_other_eligibility_findings(self):
        self.archive.add("a", "fit", group="shared")
        self.archive.add("b", "final", group="shared")
        self.archive.add("c", "unassigned", planned=True, parents=["b"])
        self.archive.file("b", "opaque", b"unknown derivative content")
        report = audit_corpus(self.archive.write(), check_files=True, check_audio=True)
        self.assert_report(report)
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["audio_check"], "partial")
        self.assertEqual(report["findings"], [
            _finding("cross_purpose_component", "a", ["a", "b", "c"]),
            _finding("derived_audio_not_declared", "a", ["b"], [("b", "opaque")]),
            _finding("planned_capture", "a", ["c"]),
            _finding("unassigned_capture", "a", ["c"]),
        ])

    def test_structural_mode_tolerates_absent_artifacts_without_observing_them(self):
        self.archive.add("a")
        self.archive.file("a", "support", b"support", kind="support")
        path = self.archive.write()
        for item in self.archive.manifests["a"]["files"]:
            self.archive.file_path("a", item["file_id"]).unlink()
        report = audit_corpus(path)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["file_check"], "not_run")
        self.assertEqual(report["audio_check"], "not_run")
        self.assertEqual(report["index_sha256"], _sha(path.read_bytes()))
        self.assertEqual(report["captures"][0]["observed_manifest_sha256"],
                         _sha((self.archive.root / "captures/a.json").read_bytes()))
        for item in report["captures"][0]["files"]:
            self.assertIsNone(item["observed_size_bytes"])
            self.assertIsNone(item["observed_sha256"])
            self.assertIsNone(item["observed_audio"])
        with self.assertRaises(CorpusError):
            audit_corpus(path, check_files=True)

    def test_file_mode_does_not_decode_or_invent_audio_evidence(self):
        payload = b"This is intentionally not audio."
        self.archive.add("a", raw=payload)
        path = self.archive.write()
        report = audit_corpus(path, check_files=True)
        self.assertEqual(report["status"], "pass")
        item = report["captures"][0]["files"][0]
        self.assertEqual(item["observed_sha256"], _sha(payload))
        self.assertEqual(item["audio_status"], "not_run")
        self.assertEqual(item["audio_reason"], "audio_check_not_requested")
        self.assertIsNone(item["observed_audio"])
        with self.assertRaisesRegex(CorpusError, "unsupported_format"):
            audit_corpus(path, check_files=True, check_audio=True)

    def test_malformed_and_nonfinite_audio_errors_remain_contextual(self):
        cases = (("truncated", _wave([0, 1])[:-1], "wav_pcm16", "malformed_audio"),
                 ("nan", _wave([float("nan")], floating=True, bits=32), "wav_float32", "nonfinite_sample"))
        for name, payload, format_name, reason in cases:
            with self.subTest(case=name):
                fixture = _Archive(self.work / f"bad-audio-{name}")
                fixture.add("a", raw=payload, format_name=format_name)
                with self.assertRaises(CorpusError) as caught:
                    audit_corpus(fixture.write(), check_files=True, check_audio=True)
                for token in ("captures/a.json", "capture 'a'", "file 'raw'", reason):
                    self.assertIn(token, str(caught.exception))

    def test_legal_flac_declaration_remains_valid_metadata_but_unsupported_audio(self):
        self.archive.add("a", raw=b"fLaC synthetic bytes", format_name="flac_pcm24")
        path = self.archive.write()
        self.assertEqual(audit_corpus(path)["status"], "pass")
        self.assertEqual(audit_corpus(path, check_files=True)["status"], "pass")
        with self.assertRaisesRegex(CorpusError, "unsupported requested format 'flac_pcm24'"):
            audit_corpus(path, check_files=True, check_audio=True)

    def test_exact_manifest_bytes_are_bound_even_when_json_value_is_unchanged(self):
        self.archive.add("a")
        path = self.archive.write()
        manifest = self.archive.root / "captures/a.json"
        old = manifest.read_bytes()
        manifest.write_bytes(old + b" \n")
        self.assertEqual(json.loads(old), json.loads(manifest.read_bytes()))
        with self.assertRaises(CorpusError) as caught:
            audit_corpus(path)
        message = str(caught.exception)
        self.assertIn(self.archive.entries["a"]["manifest_sha256"], message)
        self.assertIn(_sha(old + b" \n"), message)
        self.assertIn("manifest SHA-256", message)

    def test_actual_artifact_byte_and_size_corruption_rejected_without_report(self):
        for name, change in (("byte", lambda p: p[:-1] + bytes([p[-1] ^ 1])),
                             ("size", lambda p: p + b"x")):
            with self.subTest(case=name):
                fixture = _Archive(self.work / f"corrupt-{name}")
                fixture.add("a")
                path = fixture.write()
                artifact = fixture.file_path("a", "raw")
                artifact.write_bytes(change(artifact.read_bytes()))
                with self.assertRaises(CorpusError) as caught:
                    audit_corpus(path, check_files=True)
                self.assertIn("expected", str(caught.exception))
                self.assertIn("observed", str(caught.exception))
                self.assertIn("file 'raw'", str(caught.exception))

    def test_conflicting_sizes_for_equal_declared_hashes_fail_in_structural_mode(self):
        self.archive.add("a")
        self.archive.add("b")
        a = self.archive.manifests["a"]["files"][0]
        b = self.archive.manifests["b"]["files"][0]
        b["sha256"] = a["sha256"]
        b["size_bytes"] = a["size_bytes"] + 1
        with self.assertRaisesRegex(CorpusError, "equal expected artifact SHA-256 has conflicting declared sizes"):
            audit_corpus(self.archive.write())

    def test_same_casefolded_locator_cannot_declare_conflicting_identity(self):
        self.archive.add("a")
        self.archive.add("b")
        a = self.archive.manifests["a"]["files"][0]
        b = self.archive.manifests["b"]["files"][0]
        b["path"] = a["path"].upper()
        with self.assertRaisesRegex(CorpusError, "same case-folded artifact locator"):
            audit_corpus(self.archive.write())

    def test_shared_regular_artifact_across_manifests_is_grouped(self):
        self.archive.add("a", "fit")
        self.archive.add("b", "final")
        a = self.archive.manifests["a"]["files"][0]
        b = self.archive.manifests["b"]["files"][0]
        for field in ("path", "size_bytes", "sha256"):
            b[field] = a[field]
        report = audit_corpus(self.archive.write(), check_files=True)
        self.assertEqual(report["edges"], [_edge("artifact_sha256", a["sha256"], "a", "b", "verified_bytes", "raw", "raw")])
        self.assertEqual(report["status"], "failed")

    def test_artifacts_resolve_against_each_manifest_parent(self):
        for ident, directory, purpose in (("a", "left", "fit"), ("b", "right", "final")):
            record = self.archive.add(ident, purpose)
            self.archive.entries[ident]["manifest_path"] = f"{directory}/{ident}.json"
            record["files"][0]["path"] = "same.bin"
            parent = self.archive.root / directory
            parent.mkdir()
            (parent / "same.bin").write_bytes(self.archive.payloads[(ident, "raw")])
        (self.work / "same.bin").write_bytes(b"Wrong working-directory file.")
        report = audit_corpus(self.archive.write(), check_files=True, check_audio=True)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["edges"], [])
        for capture in report["captures"]:
            ident = capture["capture_id"]
            item = capture["files"][0]
            self.assertEqual(item["path"], "same.bin")
            self.assertEqual(item["observed_sha256"], _sha(self.archive.payloads[(ident, "raw")]))

    def test_shared_ancestor_diamond_keeps_every_declared_parent_edge(self):
        self.archive.add("a")
        self.archive.add("b", parents=["a"])
        self.archive.add("c", parents=["a"])
        self.archive.add("d", parents=["c", "b"])
        report = audit_corpus(self.archive.write())
        self.assertEqual(report["edges"], [
            _edge("parent_capture", "a", "b", "a", "index_declaration"),
            _edge("parent_capture", "a", "c", "a", "index_declaration"),
            _edge("parent_capture", "b", "d", "b", "index_declaration"),
            _edge("parent_capture", "c", "d", "c", "index_declaration"),
        ])
        self.assertEqual(report["groups"], [_group(["a", "b", "c", "d"], ["fit"], "pass")])

    def test_content_star_uses_smallest_capture_and_file_witnesses(self):
        payload = _wave([0, 8192, -16384, 0])
        descriptor = {"format": "wav_pcm16", "sample_rate_hz": 48000, "channel_count": 1}
        for ident in ("d", "c", "b", "a"):
            self.archive.add(ident, raw=payload)
            self.archive.file(ident, "zeta", payload, descriptor=descriptor)
            self.archive.file(ident, "alpha", payload, descriptor=descriptor)
        report = audit_corpus(self.archive.write(), check_files=True, check_audio=True)
        expected = []
        for other in ("b", "c", "d"):
            expected.append(_edge("artifact_sha256", _sha(payload), "a", other, "verified_bytes", "alpha", "alpha"))
            expected.append(_edge("decoded_audio_sha256", _decoded([0.0, 0.25, -0.5, 0.0]), "a", other, "verified_audio", "alpha", "alpha"))
        self.assertEqual(report["edges"], sorted(expected, key=_edge_key))
        self.assertEqual(sum(len(c["files"]) for c in report["captures"]), 12)
        self.assertEqual(report["groups"], [_group(["a", "b", "c", "d"], ["fit"], "pass")])

    def test_shared_label_bucket_emits_linear_star_not_all_pairs(self):
        ids = [f"capture-{n:02d}" for n in range(32)]
        for ident in reversed(ids):
            self.archive.add(ident, planned=True, labels=[{"kind": "family", "label": "shared-family"}])
        report = audit_corpus(self.archive.write())
        self.assertEqual(report["edges"], [_edge("family_label", "shared-family", ids[0], ident, "index_declaration") for ident in ids[1:]])
        self.assertEqual(report["groups"], [_group(ids, ["fit"], "inconclusive")])
        self.assertEqual(len(report["findings"]), 32)

    def test_index_order_changes_exact_hash_but_not_canonical_semantics(self):
        labels = [{"kind": "gesture", "label": "z"}, {"kind": "family", "label": "a"}]
        self.archive.add("a", labels=labels)
        self.archive.add("b", labels=labels)
        self.archive.add("c", parents=["b", "a"])
        path = self.archive.write()
        first = audit_corpus(path, check_files=True, check_audio=True)
        self.archive.index["captures"].reverse()
        for entry in self.archive.index["captures"]:
            entry["relation_labels"].reverse()
            entry["parent_capture_ids"].reverse()
        path.write_bytes(_json_bytes(self.archive.index))
        second = audit_corpus(path, check_files=True, check_audio=True)
        self.assertNotEqual(first["index_sha256"], second["index_sha256"])
        self.assertEqual(second["index_sha256"], _sha(path.read_bytes()))
        self.assertEqual({k: v for k, v in first.items() if k != "index_sha256"},
                         {k: v for k, v in second.items() if k != "index_sha256"})

    def test_repeat_relocation_cli_bytes_and_input_preservation(self):
        self.archive.add("a", labels=[{"kind": "family", "label": "x"}])
        self.archive.add("b", "final", labels=[{"kind": "family", "label": "x"}])
        path = self.archive.write()
        before = {p.relative_to(self.archive.root).as_posix(): _sha(p.read_bytes())
                  for p in self.archive.root.rglob("*") if p.is_file()}
        report = audit_corpus(path, check_files=True, check_audio=True)
        self.assertEqual(audit_corpus(path, check_files=True, check_audio=True), report)
        relocated = self.work / "relocated archive"
        shutil.copytree(self.archive.root, relocated)
        self.assertEqual(audit_corpus(relocated / "corpus.json", check_files=True, check_audio=True), report)
        left = self.cli(path, "--check-files", "--check-audio")
        right = self.cli(relocated / "corpus.json", "--check-files", "--check-audio")
        self.assertEqual((left.returncode, right.returncode), (1, 1))
        self.assertEqual(left.stderr, b"")
        self.assertEqual(right.stderr, b"")
        self.assertEqual(left.stdout, _json_bytes(report))
        self.assertEqual(right.stdout, left.stdout)
        after = {p.relative_to(self.archive.root).as_posix(): _sha(p.read_bytes())
                 for p in self.archive.root.rglob("*") if p.is_file()}
        self.assertEqual(after, before)

    def test_cli_all_exit_codes_and_error_report_separation(self):
        self.archive.add("a")
        path = self.archive.write()
        result = self.cli(path)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")
        self.assertEqual(result.stderr, b"")
        self.archive.add("b", "final", parents=["a"])
        result = self.cli(self.archive.write())
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "failed")
        self.assertEqual(result.stderr, b"")
        usage = self.cli(path, "--check-audio")
        self.assertEqual(usage.returncode, 2)
        self.assertEqual(usage.stdout, b"")
        self.assertIn(b"requires --check-files", usage.stderr)
        plan = _Archive(self.work / "planned-cli")
        plan.add("plan", "unassigned", planned=True)
        result = self.cli(plan.write())
        self.assertEqual(result.returncode, 3)
        self.assertEqual(json.loads(result.stdout)["status"], "inconclusive")
        self.assertEqual(result.stderr, b"")
        manifest = self.archive.root / "captures/a.json"
        manifest.write_bytes(manifest.read_bytes() + b" ")
        rejected = self.cli(path)
        self.assertEqual(rejected.returncode, 1)
        self.assertEqual(rejected.stdout, b"")
        self.assertTrue(rejected.stderr.startswith(b"corpus error: "))

    def test_mode_flags_are_exact_booleans_and_audio_requires_files(self):
        self.archive.add("a")
        path = self.archive.write()
        for name in ("check_files", "check_audio"):
            for value in (0, 1, None, "false", []):
                with self.subTest(flag=name, value=value):
                    with self.assertRaises(CorpusError):
                        audit_corpus(path, **{name: value})
        with self.assertRaises(CorpusError):
            audit_corpus(path, check_audio=True)

    def test_cli_does_not_offer_output_or_alternate_artifact_root(self):
        self.archive.add("a")
        path = self.archive.write()
        destination = self.work / "not-created.json"
        for option in ("--output", "--artifact-root"):
            with self.subTest(option=option):
                result = self.cli(path, option, str(destination))
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b"")
                self.assertIn(b"unrecognized arguments", result.stderr)
                self.assertFalse(destination.exists())

    def test_missing_and_extra_index_object_keys_are_rejected(self):
        self.archive.add("a", labels=[{"kind": "gesture", "label": "x"}])
        self.archive.file("a", "derived", _wave([1, 2]), descriptor={
            "format": "wav_pcm16", "sample_rate_hz": 48000, "channel_count": 1})
        self.archive.write()
        paths = ((), ("captures", 0), ("captures", 0, "relation_labels", 0),
                 ("captures", 0, "derived_audio", 0))
        for path in paths:
            original = self.archive.index
            for key in path:
                original = original[key]
            for missing in original:
                with self.subTest(path=path, missing=missing):
                    value = copy.deepcopy(self.archive.index)
                    node = value
                    for key in path:
                        node = node[key]
                    del node[missing]
                    with self.assertRaises(CorpusError):
                        validate_corpus(value)
            value = copy.deepcopy(self.archive.index)
            node = value
            for key in path:
                node = node[key]
            node["unexpected"] = "extra"
            with self.subTest(path=path, extra=True):
                with self.assertRaises(CorpusError):
                    validate_corpus(value)

    def test_duplicate_relations_and_derived_file_ids_rejected(self):
        self.archive.add("a", labels=[{"kind": "gesture", "label": "x"}])
        self.archive.file("a", "derived", _wave([1, 2]), descriptor={
            "format": "wav_pcm16", "sample_rate_hz": 48000, "channel_count": 1})
        self.archive.write()
        for field in ("relation_labels", "derived_audio"):
            with self.subTest(field=field):
                value = copy.deepcopy(self.archive.index)
                items = value["captures"][0][field]
                items.append(copy.deepcopy(items[0]))
                if field == "derived_audio":
                    items[1]["sample_rate_hz"] = 24000
                with self.assertRaises(CorpusError):
                    validate_corpus(value)


if __name__ == "__main__":
    unittest.main()
