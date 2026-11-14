#!/usr/bin/env python3
"""Independent corpus graph acceptance at mixed and maximum record counts.

The oracle deliberately builds all pairwise relationships and uses breadth-first
reachability. It does not call the producer's buckets, stars, union-find, inventory
or classification helpers. Tiny synthetic streams provide exact byte and decoded
identities; these tests do not establish physical independence or maximum-byte
performance. Existing suites own ordinary malformed-input/filesystem coverage.
"""

from __future__ import annotations

from collections import Counter, deque
import copy
from dataclasses import dataclass, field
import hashlib
from itertools import combinations
import json
from pathlib import Path
import random
import struct
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import capture_corpus as subject


CLAIMS = (
    "independence", "final_holdout_history", "authenticity", "specimen_identity",
    "calibration", "permissions", "physical_fidelity",
)
MODES = ((False, False), (True, False), (True, True))
KNOWN_PAIRS = (("fit", "validation"), ("fit", "final"), ("validation", "final"))
REASONS = (
    "session_id", "v1_group_id", "gesture_label", "family_label",
    "parent_capture", "artifact_sha256", "decoded_audio_sha256",
)


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


def known(value):
    return {"value": value, "unknown_reason": None}


def unknown():
    return {"value": None, "unknown_reason": "Synthetic graph fixture; no physical observation."}


def calibration():
    return {"status": "not_applicable", "value": None, "unit": None,
            "standard_uncertainty": None, "evidence": None,
            "unknown_reason": "Synthetic digital fixture; no physical calibration."}


def wav_float(samples, marker):
    """Ordinary IEEE-float RIFF constructed without any production audio writer."""
    def chunk(name, payload):
        return name + struct.pack("<I", len(payload)) + payload + (b"\0" if len(payload) % 2 else b"")

    data = struct.pack("<" + "f" * len(samples), *samples)
    fmt = struct.pack("<HHIIHH", 3, 1, 48000, 192000, 4, 32)
    body = b"WAVE" + chunk(b"fmt ", fmt) + chunk(b"JUNK", marker.encode("ascii")) + chunk(b"data", data)
    return b"RIFF" + struct.pack("<I", len(body)) + body


def decoded_digest(samples):
    # All authored values are exactly representable binary fractions. This is
    # the literal contract preimage, not an inspected/produced sample array.
    payload = b"HAMMOND-CAPTURE-DECODED-V1\0" + struct.pack("<IIQ", 48000, 1, len(samples))
    payload += b"".join(struct.pack("<d", 0.0 if value == 0.0 else value) for value in samples)
    return digest(payload)


@dataclass
class Artifact:
    file_id: str
    kind: str
    payload: bytes
    samples: tuple[float, ...] | None = None
    format_name: str | None = None
    selected: bool = True


def audio(file_id, kind, samples, *, marker=None, selected=True):
    samples = tuple(samples)
    payload = (struct.pack("<" + "f" * len(samples), *samples)
               if marker is None else wav_float(samples, marker))
    return Artifact(file_id, kind, payload, samples,
                    "raw_float32_le" if marker is None else "wav_float32", selected)


@dataclass
class Capture:
    ident: str
    purpose: str
    planned: bool = False
    session: str | None = None
    group: str | None = None
    labels: list[tuple[str, str]] = field(default_factory=list)
    parents: list[str] = field(default_factory=list)
    files: list[Artifact] = field(default_factory=list)


def recorded(ident, code, purpose="fit"):
    return Capture(ident, purpose, session=f"session-{ident}", group=f"group-{ident}",
                   files=[audio("raw", "raw", (code / 1024, -code / 1024))])


class Archive:
    """Own literal v1 author. No producer/test-helper imports form fixtures."""

    def __init__(self, root, captures):
        self.root = Path(root)
        self.root.mkdir(parents=True)
        self.path = self.root / "corpus.json"
        self.captures = captures
        self.index = {"schema_version": 1, "contract_origin": "project-proposed-corpus-v1",
                      "corpus_id": "graph-scale-fixture", "captures": []}
        self.manifests = {}
        for capture in captures:
            raw = next((item for item in capture.files if item.kind == "raw"), None)
            manifest = {
                "schema_version": 1, "contract_origin": "project-proposed-v1",
                "capture_id": capture.ident,
                "status": "planned" if capture.planned else "recorded",
                "status_reason": "Unacquired synthetic plan." if capture.planned else None,
                "capture_kind": "synthetic",
                "specimen": {"specimen_id": unknown(),
                             "variant": known("Synthetic graph acceptance only"),
                             "revision": known("graph-test-v1"), "identity_evidence": unknown()},
                "acquisition": {
                    "started_at_utc": unknown() if capture.planned else known("2000-01-01T00:00:00Z"),
                    "operator_id": known("shared-test-author"),
                    "session_id": unknown() if capture.session is None else known(capture.session),
                },
                "digital": {
                    "format": unknown() if raw is None else known(raw.format_name),
                    "sample_rate_hz": unknown() if raw is None else known(48000),
                    "channel_count": unknown() if raw is None else known(1),
                    "channels": [] if raw is None else [
                        {"channel_id": "mono", "index": 0, "boundary": known("synthetic"),
                         "port_reference": unknown(), "calibration": calibration()}],
                },
                "physical_clock": calibration(),
                "stimulus": {key: unknown() for key in ("description", "controls", "conditions", "synchronization")},
                "signal_path": {key: unknown() for key in ("description", "bypass", "loading")},
                "files": [],
                "partition": {
                    "role": {"fit": "fit", "validation": "held_out", "final": "held_out",
                             "unassigned": "unassigned"}[capture.purpose],
                    "group_id": unknown() if capture.group is None else known(capture.group),
                    "rationale": "Literal synthetic acceptance assignment, not a physical holdout.",
                },
                "rights": unknown(),
            }
            entry = {"capture_id": capture.ident, "manifest_path": f"captures/{capture.ident}.json",
                     "manifest_sha256": "0" * 64, "purpose": capture.purpose,
                     "relation_labels": [{"kind": kind, "label": label} for kind, label in capture.labels],
                     "parent_capture_ids": list(capture.parents), "derived_audio": []}
            for item in capture.files:
                relative = f"{capture.ident}/{item.file_id}.bin"
                manifest["files"].append({
                    "file_id": item.file_id, "kind": item.kind, "path": relative,
                    "size_bytes": len(item.payload), "sha256": digest(item.payload),
                    "parents": [raw.file_id] if item.kind == "derived" else [],
                    "derivation": ({"operation": "literal-synthetic-fixture", "tool": "unittest",
                                    "tool_version": "1", "parameters": "Authored bytes; no fitting or acquisition."}
                                   if item.kind == "derived" else None),
                })
                target = self.root / "captures" / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(item.payload)
                if item.kind == "derived" and item.selected:
                    entry["derived_audio"].append({"file_id": item.file_id, "format": item.format_name,
                                                   "sample_rate_hz": 48000, "channel_count": 1})
            self.manifests[capture.ident] = manifest
            self.index["captures"].append(entry)
        self.write()

    def write(self):
        for entry in self.index["captures"]:
            payload = json_bytes(self.manifests[entry["capture_id"]])
            target = self.root / entry["manifest_path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            entry["manifest_sha256"] = digest(payload)
        self.write_index()

    def write_index(self):
        # Dense declared relationships remain under the existing 1 MiB input
        # bound in compact JSON. Input formatting is free; its exact bytes bind.
        self.path.write_bytes((json.dumps(self.index, sort_keys=True, separators=(",", ":"),
                                          ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8"))

    def inventory(self):
        return {path.relative_to(self.root).as_posix(): digest(path.read_bytes())
                for path in self.root.rglob("*") if path.is_file()}


def edge(reason, value, left, right, files, checked):
    basis = ("verified_audio" if reason == "decoded_audio_sha256" else
             "verified_bytes" if reason == "artifact_sha256" and checked else
             "manifest_declaration" if reason in ("session_id", "v1_group_id", "artifact_sha256") else
             "index_declaration")
    return {"reason": reason, "value": value, "left_capture_id": left,
            "right_capture_id": right, "left_file_id": files[0], "right_file_id": files[1],
            "basis": basis}


def edge_key(item):
    return (item["reason"], item["value"], item["left_capture_id"], item["right_capture_id"],
            item["left_file_id"] or "", item["right_file_id"] or "", item["basis"])


def pairwise_oracle(captures, *, check_files, check_audio):
    """Expand equality cliques, add directed-parent undirected connectivity, BFS.

    Expected returned stars are a separate projection of all pairwise witnesses:
    retain an equality pair exactly when its left endpoint is the global minimum
    carrying that token. This does not compute components from the expected stars.
    """
    by_id = {item.ident: item for item in captures}
    ids = sorted(by_id)
    facts = {}
    for capture in captures:
        tokens = {}
        for reason, value in (("session_id", capture.session), ("v1_group_id", capture.group)):
            if value is not None:
                tokens[(reason, value)] = None
        for kind, label in capture.labels:
            tokens[(kind + "_label", label)] = None
        for item in sorted(capture.files, key=lambda item: item.file_id):
            if item.kind == "support":
                continue
            tokens.setdefault(("artifact_sha256", digest(item.payload)), item.file_id)
            if check_audio and (item.kind == "raw" or item.selected):
                tokens.setdefault(("decoded_audio_sha256", decoded_digest(item.samples)), item.file_id)
        facts[capture.ident] = tokens
    all_tokens = set().union(*(set(value) for value in facts.values()))
    anchors = {token: min(ident for ident in ids if token in facts[ident]) for token in all_tokens}
    adjacent = {ident: set() for ident in ids}
    edges = []
    for left, right in combinations(ids, 2):
        common = facts[left].keys() & facts[right].keys()
        if common:
            adjacent[left].add(right)
            adjacent[right].add(left)
        for token in common:
            if anchors[token] == left:
                edges.append(edge(*token, left, right, (facts[left][token], facts[right][token]), check_files))
    for capture in captures:
        for parent in capture.parents:
            adjacent[capture.ident].add(parent)
            adjacent[parent].add(capture.ident)
            edges.append(edge("parent_capture", parent, capture.ident, parent, (None, None), check_files))
    unseen = set(ids)
    groups, findings = [], []

    def finding(code, component, members, refs=()):
        return {"code": code, "severity": "error" if code == "cross_purpose_component" else "inconclusive",
                "component_id": component, "capture_ids": sorted(members),
                "file_refs": [{"capture_id": ident, "file_id": file_id} for ident, file_id in sorted(refs)]}

    while unseen:
        component = min(unseen)
        visited = {component}
        queue = deque([component])
        while queue:
            current = queue.popleft()
            for neighbour in adjacent[current] - visited:
                visited.add(neighbour)
                queue.append(neighbour)
        unseen -= visited
        purposes = {by_id[ident].purpose for ident in visited}
        known_purposes = purposes & {"fit", "validation", "final"}
        local = []
        if len(known_purposes) > 1:
            local.append(finding("cross_purpose_component", component, visited))
        for ident in sorted(visited):
            capture = by_id[ident]
            if capture.planned:
                local.append(finding("planned_capture", component, [ident]))
            if capture.purpose == "unassigned":
                local.append(finding("unassigned_capture", component, [ident]))
            if check_audio:
                for item in capture.files:
                    if item.kind == "derived" and not item.selected:
                        local.append(finding("derived_audio_not_declared", component, [ident], [(ident, item.file_id)]))
        status = "failed" if len(known_purposes) > 1 else "inconclusive" if local else "pass"
        groups.append({"component_id": component, "capture_ids": sorted(visited),
                       "purposes": sorted(purposes), "status": status})
        findings.extend(local)
    statuses = {item["status"] for item in groups}
    return {
        "edges": sorted(edges, key=edge_key),
        "groups": sorted(groups, key=lambda item: item["component_id"]),
        "findings": sorted(findings, key=lambda item: (
            item["code"], item["component_id"], tuple(item["capture_ids"]),
            tuple((ref["capture_id"], ref["file_id"]) for ref in item["file_refs"]))),
        "status": "failed" if "failed" in statuses else "inconclusive" if "inconclusive" in statuses else "pass",
    }


def mixed_captures(seed):
    rng = random.Random(seed)
    captures = []
    for block in range(6):
        for offset in range(8):
            number = 8 * block + offset
            ident = f"c{number:03d}"
            purpose = ("validation" if block == 0 and offset == 7 else
                       "final" if block == 1 and offset == 7 else
                       "unassigned" if block == 2 and offset == 7 else "fit")
            code = 16 * block + offset % 3 + 1
            capture = recorded(ident, code, purpose)
            capture.session = f"session-b{block}-s{rng.randrange(3)}"
            capture.group = f"group-b{block}-g{rng.randrange(3)}"
            capture.labels = [("gesture", f"b{block}-g{rng.randrange(3)}"),
                              ("family", f"b{block}-f{rng.randrange(3)}")]
            capture.files = [audio("zraw", "raw", (code / 1024, -code / 1024),
                                   marker=ident if offset % 2 else None)]
            if offset % 2 == 0:
                second_code = 16 * block + (offset + 1) % 3 + 1
                capture.files.append(audio("alpha", "derived", (second_code / 1024, -second_code / 1024),
                                           marker=f"derived-{ident}", selected=offset != 6))
            capture.files.append(Artifact("support", "support", b"shared support without grouping\n"))
            if offset:
                capture.parents = [f"c{8 * block + rng.randrange(offset):03d}"]
                if offset > 2:
                    capture.parents = sorted(set(capture.parents + [f"c{8 * block:03d}"]))
            captures.append(capture)
    # A cross-block parent creates a deliberate transitive three-purpose leak.
    captures[15].parents.append("c000")
    captures.extend([Capture("pending-a", "unassigned", planned=True),
                     Capture("pending-b", "unassigned", planned=True)])
    return captures


class CorpusGraphScale(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hammond-graph-scale-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name).resolve()

    def assert_audit(self, archive, *, check_files=False, check_audio=False):
        original = archive.inventory()
        expected = pairwise_oracle(archive.captures, check_files=check_files, check_audio=check_audio)
        report = subject.audit_corpus(archive.path, check_files=check_files, check_audio=check_audio)
        self.assertEqual({key: report[key] for key in expected}, expected)
        self.assertEqual(report["index_sha256"], digest(archive.path.read_bytes()))
        self.assertEqual({key: report[key] for key in CLAIMS}, dict.fromkeys(CLAIMS, "not_established"))
        self.assertEqual(archive.inventory(), original)
        self.assertEqual(len(report["captures"]), len(archive.captures))
        originals = {item.ident: item for item in archive.captures}
        for capture in report["captures"]:
            specification = originals[capture["capture_id"]]
            self.assertEqual(capture["capture_kind"], "synthetic")
            self.assertEqual(capture["purpose"], specification.purpose)
            self.assertEqual(capture["record_status"], "planned" if specification.planned else "recorded")
            self.assertEqual(capture["expected_manifest_sha256"], capture["observed_manifest_sha256"])
            files = {item.file_id: item for item in specification.files}
            self.assertEqual(len(capture["files"]), len(files))
            for item in capture["files"]:
                original_file = files[item["file_id"]]
                self.assertEqual(item["expected_sha256"], digest(original_file.payload))
                self.assertEqual(item["observed_sha256"], digest(original_file.payload) if check_files else None)
                self.assertEqual(item["observed_size_bytes"], len(original_file.payload) if check_files else None)
                selected = check_audio and (original_file.kind == "raw" or
                                            original_file.kind == "derived" and original_file.selected)
                if selected:
                    self.assertEqual(item["observed_audio"]["decoded_sha256"], decoded_digest(original_file.samples))
                else:
                    self.assertIsNone(item["observed_audio"])
                if original_file.kind == "support":
                    self.assertEqual(item["audio_status"], "excluded_support")
        return report

    def test_512_recorded_dense_graph_and_513_preflight(self):
        captures = []
        samples = (0.0, 0.25, -0.5, 0.0)
        labels = [(kind, f"shared-{kind}-{n}") for kind in ("gesture", "family") for n in range(8)]
        purposes = ("fit", "validation", "final", "unassigned")
        for number in range(512):
            ident = f"c{number:03d}"
            capture = Capture(ident, purposes[number % 4], session="shared-session", group="shared-group",
                              labels=list(labels), parents=[f"c{n:03d}" for n in range(max(0, number - 16), number)])
            capture.files = [audio("zraw", "raw", samples), audio("alpha", "derived", samples),
                             Artifact("support", "support", struct.pack("<4f", *samples))]
            captures.append(capture)
        archive = Archive(self.work / "dense", captures)
        report = self.assert_audit(archive, check_files=True, check_audio=True)
        self.assertEqual(report["groups"], [{"component_id": "c000", "capture_ids": [f"c{n:03d}" for n in range(512)],
                                            "purposes": sorted(purposes), "status": "failed"}])
        self.assertEqual(Counter(item["reason"] for item in report["edges"]),
                         {"session_id": 511, "v1_group_id": 511, "gesture_label": 4088, "family_label": 4088,
                          "artifact_sha256": 511, "decoded_audio_sha256": 511, "parent_capture": 8056})
        self.assertEqual(len(report["edges"]), 18276)
        self.assertEqual(Counter(item["code"] for item in report["findings"]),
                         {"cross_purpose_component": 1, "unassigned_capture": 128})
        self.assertEqual(sum(len(item.files) for item in captures), 1536)
        self.assertEqual(sum(len(item.payload) for capture in captures for item in capture.files), 24576)
        content_edges = [item for item in report["edges"] if item["reason"] in ("artifact_sha256", "decoded_audio_sha256")]
        self.assertTrue(all(item["left_file_id"] == item["right_file_id"] == "alpha" for item in content_edges))
        extra = copy.deepcopy(archive.index["captures"][-1])
        extra.update(capture_id="c512", manifest_path="captures/c512.json", manifest_sha256=digest(b"unwritten-513th-manifest"))
        archive.index["captures"].append(extra)
        archive.write_index()
        for files, audio_mode in MODES:
            with self.subTest(excess_mode=(files, audio_mode)):
                with mock.patch.object(subject, "_load_manifests", side_effect=AssertionError("manifest work reached")) as reached:
                    with self.assertRaisesRegex(subject.CorpusError, "512"):
                        subject.audit_corpus(archive.path, check_files=files, check_audio=audio_mode)
                    reached.assert_not_called()

    def test_seeded_mixed_graphs_match_clique_bfs_in_all_modes(self):
        for seed in (0, 1, 17, 65537):
            archive = Archive(self.work / f"seed-{seed}", mixed_captures(seed))
            for files, audio_mode in MODES:
                with self.subTest(seed=seed, mode=(files, audio_mode)):
                    report = self.assert_audit(archive, check_files=files, check_audio=audio_mode)
                    self.assertEqual(len(report["groups"]), 7)
                    self.assertEqual(report["status"], "failed")
                    self.assertEqual({item["status"] for item in report["groups"]},
                                     {"failed", "inconclusive"} if audio_mode else {"failed", "inconclusive", "pass"})
                    if audio_mode:
                        self.assertEqual(report["audio_check"], "partial")
                        self.assertEqual(sum(item["code"] == "derived_audio_not_declared" for item in report["findings"]), 6)

    def test_index_permutations_bind_bytes_and_preserve_all_other_fields(self):
        archive = Archive(self.work / "permutations", mixed_captures(17))
        first = self.assert_audit(archive, check_files=True, check_audio=True)
        hashes = {first["index_sha256"]}
        expected = {key: value for key, value in first.items() if key != "index_sha256"}
        for seed in (5, 19, 71, 2026):
            rng = random.Random(seed)
            rng.shuffle(archive.index["captures"])
            for entry in archive.index["captures"]:
                for name in ("relation_labels", "parent_capture_ids", "derived_audio"):
                    rng.shuffle(entry[name])
            archive.write_index()
            report = self.assert_audit(archive, check_files=True, check_audio=True)
            self.assertNotIn(report["index_sha256"], hashes)
            hashes.add(report["index_sha256"])
            self.assertEqual({key: value for key, value in report.items() if key != "index_sha256"}, expected)
        self.assertEqual(len(hashes), 5)

    def test_manifest_file_permutation_keeps_graph_and_changes_bound_identity(self):
        captures = []
        for number in range(12):
            capture = recorded(f"c{number:03d}", number + 1, "fit" if number % 2 else "final")
            capture.files = [audio("zraw", "raw", (0.25, -0.25), marker=f"raw-{number}"),
                             audio("zeta", "derived", (0.25, -0.25)),
                             audio("alpha", "derived", (0.25, -0.25)),
                             Artifact("support", "support", b"uninterpreted support")]
            captures.append(capture)
        archive = Archive(self.work / "manifest-order", captures)
        first = self.assert_audit(archive, check_files=True, check_audio=True)
        for manifest in archive.manifests.values():
            manifest["files"].reverse()
        archive.write()
        second = self.assert_audit(archive, check_files=True, check_audio=True)
        self.assertNotEqual(first["index_sha256"], second["index_sha256"])
        for before, after in zip(first["captures"], second["captures"]):
            self.assertNotEqual(before["observed_manifest_sha256"], after["observed_manifest_sha256"])
            for name in ("expected_manifest_sha256", "observed_manifest_sha256"):
                del before[name]
                del after[name]
        del first["index_sha256"]
        del second["index_sha256"]
        self.assertEqual(first, second)

    def test_512_deep_ancestry_closure_and_full_length_cycle_preflight(self):
        captures = [recorded(f"c{number:03d}", number + 1, "final" if number == 511 else "fit")
                    for number in range(512)]
        for number in range(1, 512):
            captures[number].parents = [captures[number - 1].ident]
        archive = Archive(self.work / "deep", captures)
        report = self.assert_audit(archive)
        self.assertEqual(Counter(item["reason"] for item in report["edges"]), {"parent_capture": 511})
        self.assertEqual(len(report["groups"]), 1)
        self.assertEqual(report["status"], "failed")
        archive.index["captures"][0]["parent_capture_ids"] = ["c511"]
        archive.write_index()
        for order in (False, True):
            if order:
                archive.index["captures"].reverse()
                archive.write_index()
            with self.subTest(reversed_index=order):
                with mock.patch.object(subject, "_load_manifests", side_effect=AssertionError("manifest work reached")) as reached:
                    with self.assertRaisesRegex(subject.CorpusError, "directed cycle"):
                        subject.audit_corpus(archive.path, check_files=True, check_audio=True)
                    reached.assert_not_called()

    def test_all_seven_reasons_propagate_each_known_purpose_pair(self):
        for reason in REASONS:
            for left_purpose, right_purpose in KNOWN_PAIRS:
                captures = [recorded("left", 1, left_purpose), recorded("middle", 2, "unassigned"),
                            recorded("right", 3, right_purpose)]
                if reason in ("session_id", "v1_group_id"):
                    for capture in captures:
                        setattr(capture, "session" if reason == "session_id" else "group", "shared")
                elif reason in ("gesture_label", "family_label"):
                    kind = reason.removesuffix("_label")
                    captures[0].labels = [(kind, "first-link")]
                    captures[1].labels = [(kind, "first-link"), (kind, "second-link")]
                    captures[2].labels = [(kind, "second-link")]
                elif reason == "parent_capture":
                    captures[1].parents = ["left"]
                    captures[2].parents = ["middle"]
                else:
                    for number, capture in enumerate(captures):
                        samples = (0.25, -0.25) if number < 2 else (0.5, -0.5)
                        capture.files = [audio("raw", "raw", samples,
                                               marker=capture.ident if reason == "decoded_audio_sha256" else None)]
                    captures[1].files.append(audio("derivative", "derived", (0.5, -0.5),
                                                   marker="middle-derived" if reason == "decoded_audio_sha256" else None))
                archive = Archive(self.work / f"{reason}-{left_purpose}-{right_purpose}", captures)
                audio_mode = reason == "decoded_audio_sha256"
                files = reason in ("artifact_sha256", "decoded_audio_sha256")
                with self.subTest(reason=reason, purposes=(left_purpose, right_purpose)):
                    report = self.assert_audit(archive, check_files=files, check_audio=audio_mode)
                    self.assertEqual(Counter(item["reason"] for item in report["edges"]), {reason: 2})
                    self.assertEqual(report["status"], "failed")
                    self.assertEqual(len(report["groups"]), 1)
                    self.assertEqual(report["groups"][0]["capture_ids"], ["left", "middle", "right"])
                    self.assertEqual(Counter(item["code"] for item in report["findings"]),
                                     {"cross_purpose_component": 1, "unassigned_capture": 1})

    def test_shared_support_and_pending_singletons_do_not_merge(self):
        purposes = ("fit", "validation", "final", "unassigned")
        captures = [recorded(f"c{number:03d}", number + 1, purposes[number % 4]) for number in range(64)]
        shared = captures[0].files[0].payload
        for capture in captures:
            capture.files.append(Artifact("support", "support", shared))
        captures.extend([Capture("pending-a", "unassigned", planned=True),
                         Capture("pending-b", "unassigned", planned=True)])
        archive = Archive(self.work / "support", captures)
        report = self.assert_audit(archive, check_files=True, check_audio=True)
        self.assertEqual(report["edges"], [])
        self.assertEqual(len(report["groups"]), 66)
        self.assertTrue(all(len(item["capture_ids"]) == 1 for item in report["groups"]))
        self.assertEqual(report["status"], "inconclusive")
        self.assertEqual(Counter(item["code"] for item in report["findings"]),
                         {"planned_capture": 2, "unassigned_capture": 18})


if __name__ == "__main__":
    unittest.main()
