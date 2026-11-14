#!/usr/bin/env python3
"""Audit declared capture relationships and optional bytes/audio, not physical truth.

The corpus companion leaves capture v1 unchanged. All observed identities bind
actual reads; deterministic stars retain every reason without pairwise expansion.
Inputs must remain quiescent during portable filesystem verification.
"""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

from capture_common import DataError, parse_json_bytes, validate_json_value
from validate_capture import CaptureError, validate_capture


MAX_INDEX_BYTES = 1048576
MAX_INDEX_NODES = 65536
MAX_DEPTH = 16
MAX_TEXT = 2048
MAX_CAPTURES = 512
MAX_MANIFEST_BYTES = 65536
MAX_MANIFEST_NODES = 4096
MAX_TOTAL_MANIFEST_BYTES = 16777216
MAX_TOTAL_ARTIFACT_BYTES = 2147483648
MAX_TOTAL_AUDIO_BYTES = 268435456
MAX_PARENT_EDGES = 8192
MAX_EDGES = 65536
MAX_FINDINGS = 18432
CHUNK_BYTES = 65536
DECODED_DIGEST_VERSION = "hammond-capture-decoded-v1"
FORMATS = {"wav_pcm16", "wav_pcm24", "wav_pcm32", "wav_float32",
           "wav_float64", "flac_pcm16", "flac_pcm24", "raw_float32_le"}
AUDIO_FORMATS = FORMATS - {"flac_pcm16", "flac_pcm24"}
PURPOSE_ROLES = {"fit": "fit", "validation": "held_out", "final": "held_out",
                 "unassigned": "unassigned"}
ID_RE = re.compile(r"[a-z][a-z0-9_-]{0,63}")
SHA_RE = re.compile(r"[0-9a-f]{64}")
COMPONENT_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")
DEVICE_RE = re.compile(r"(?:con|prn|aux|nul|com[1-9]|lpt[1-9])", re.IGNORECASE)
INDEX_KEYS = {"schema_version", "contract_origin", "corpus_id", "captures"}
ENTRY_KEYS = {"capture_id", "manifest_path", "manifest_sha256", "purpose",
              "relation_labels", "parent_capture_ids", "derived_audio"}
AUDIO_KEYS = {"format", "sample_rate_hz", "channel_count"}
CLAIM_FIELDS = ("independence", "final_holdout_history", "authenticity",
                "specimen_identity", "calibration", "permissions", "physical_fidelity")


class CorpusError(ValueError):
    """Rejected corpus input, identity, file, audio or resource bound."""


def _require(condition: bool, label: str, message: str) -> None:
    if not condition:
        raise CorpusError(f"{label}: {message}")


def _keys(value: object, fields: set[str], label: str) -> None:
    _require(type(value) is dict and set(value) == fields, label,
             f"expected exactly these keys: {', '.join(sorted(fields))}")


def _text(value: object, label: str) -> None:
    _require(type(value) is str and 0 < len(value) <= MAX_TEXT and bool(value.strip()),
             label, "expected nonblank text of at most 2048 characters")
    _require(not any(ord(char) < 32 or 127 <= ord(char) <= 159 for char in value),
             label, "control characters are forbidden")
    try:
        value.encode("utf-8")
    except UnicodeError as error:
        raise CorpusError(f"{label}: unpaired Unicode surrogate") from error


def _guard(value: object) -> None:
    try:
        validate_json_value(value, max_nodes=MAX_INDEX_NODES, max_depth=MAX_DEPTH,
                            max_number=1e12)
    except DataError as error:
        raise CorpusError(f"corpus JSON: {error}") from error
    # The common guard owns exact JSON types and bounded traversal; corpus v1
    # additionally bounds every string and container, including unknown keys.
    pending = [value]
    while pending:
        item = pending.pop()
        if type(item) is dict:
            _require(len(item) <= MAX_INDEX_NODES, "corpus JSON", "container member limit exceeded")
            for key in item:
                _text(key, "JSON key")
            pending.extend(item.values())
        elif type(item) is list:
            _require(len(item) <= MAX_INDEX_NODES, "corpus JSON", "container member limit exceeded")
            pending.extend(item)
        elif type(item) is str:
            _text(item, "JSON string")


def _id(value: object, label: str) -> str:
    _require(type(value) is str and ID_RE.fullmatch(value) is not None,
             label, "expected ID matching [a-z][a-z0-9_-]{0,63}")
    return value


def _sha(value: object, label: str) -> str:
    _require(type(value) is str and SHA_RE.fullmatch(value) is not None,
             label, "expected 64 lowercase hexadecimal SHA-256 characters")
    return value


def _integer(value: object, low: int, high: int, label: str) -> None:
    _require(type(value) is int and low <= value <= high, label,
             f"expected integer in {low}..{high}")


def _array(value: object, low: int, high: int, label: str) -> list:
    _require(type(value) is list and low <= len(value) <= high, label,
             f"expected array of {low}..{high} entries")
    return value


def _path(value: object, label: str) -> str:
    _text(value, label)
    _require(len(value) <= 240, label, "path exceeds 240 characters")
    parts = value.split("/")
    _require(1 <= len(parts) <= 8, label, "path exceeds eight components")
    for part in parts:
        _require(COMPONENT_RE.fullmatch(part) is not None
                 and not part.endswith(".")
                 and DEVICE_RE.fullmatch(part.split(".", 1)[0]) is None,
                 label, "expected confined portable relative path without device names")
    return value


def validate_corpus(value: object) -> None:
    """Validate exact bounded index types, identities and ancestry without I/O."""
    _guard(value)
    _keys(value, INDEX_KEYS, "corpus")
    _require(type(value["schema_version"]) is int and value["schema_version"] == 1,
             "schema_version", "expected integer 1")
    _require(value["contract_origin"] == "project-proposed-corpus-v1",
             "contract_origin", "expected project-proposed-corpus-v1")
    _id(value["corpus_id"], "corpus_id")
    entries = _array(value["captures"], 1, MAX_CAPTURES, "captures")
    by_id, paths, hashes = {}, set(), set()
    parent_count = 0
    for position, entry in enumerate(entries):
        label = f"captures[{position}]"
        _keys(entry, ENTRY_KEYS, label)
        ident = _id(entry["capture_id"], f"{label}.capture_id")
        _require(ident not in by_id, label, f"duplicate capture ID {ident!r}")
        by_id[ident] = entry
        path = _path(entry["manifest_path"], f"{label}.manifest_path").casefold()
        _require(path not in paths, label, "duplicate manifest path (case-insensitive)")
        paths.add(path)
        digest = _sha(entry["manifest_sha256"], f"{label}.manifest_sha256")
        _require(digest not in hashes, label, "duplicate manifest SHA-256 identity")
        hashes.add(digest)
        _require(type(entry["purpose"]) is str and entry["purpose"] in PURPOSE_ROLES,
                 f"{label}.purpose", "expected fit, validation, final or unassigned")
        labels = _array(entry["relation_labels"], 0, 32, f"{label}.relation_labels")
        seen_labels = set()
        for relation in labels:
            _keys(relation, {"kind", "label"}, f"{label}.relation_labels")
            _require(relation["kind"] in ("gesture", "family"), label,
                     "relation kind must be gesture or family")
            _id(relation["label"], f"{label}.relation_labels.label")
            pair = relation["kind"], relation["label"]
            _require(pair not in seen_labels, label, "duplicate relation (kind, label)")
            seen_labels.add(pair)
        parents = _array(entry["parent_capture_ids"], 0, 16, f"{label}.parent_capture_ids")
        for parent in parents:
            _id(parent, f"{label}.parent_capture_ids")
            _require(parent != ident, label, "capture cannot be its own parent")
        _require(len(set(parents)) == len(parents), label, "duplicate parent capture ID")
        parent_count += len(parents)
        _require(parent_count <= MAX_PARENT_EDGES, "captures", "parent edge limit exceeded")
        derived = _array(entry["derived_audio"], 0, 32, f"{label}.derived_audio")
        seen_files = set()
        for descriptor in derived:
            _keys(descriptor, AUDIO_KEYS | {"file_id"}, f"{label}.derived_audio")
            file_id = _id(descriptor["file_id"], f"{label}.derived_audio.file_id")
            _require(file_id not in seen_files, label, "duplicate derived audio file ID")
            seen_files.add(file_id)
            _require(type(descriptor["format"]) is str and descriptor["format"] in FORMATS,
                     f"{label}.derived_audio.format", "expected a capture-v1 format token")
            _integer(descriptor["sample_rate_hz"], 1, 768000,
                     f"{label}.derived_audio.sample_rate_hz")
            _integer(descriptor["channel_count"], 1, 16,
                     f"{label}.derived_audio.channel_count")
    # Kahn's algorithm visits every declared branch once. A shared ancestor is
    # neither recursion nor exponential traversal, and unresolved parents fail.
    children = {ident: [] for ident in by_id}
    outstanding = {}
    for ident, entry in by_id.items():
        outstanding[ident] = len(entry["parent_capture_ids"])
        for parent in entry["parent_capture_ids"]:
            _require(parent in by_id, f"capture {ident}", f"unresolved parent capture {parent!r}")
            children[parent].append(ident)
    ready = deque(ident for ident, count in outstanding.items() if count == 0)
    visited = 0
    while ready:
        parent = ready.popleft()
        visited += 1
        for child in children[parent]:
            outstanding[child] -= 1
            if outstanding[child] == 0:
                ready.append(child)
    _require(visited == len(by_id), "parent_capture_ids", "capture ancestry contains a directed cycle")


def _identity(info) -> tuple:
    return info.st_dev, info.st_ino


def _usable_identity(info) -> bool:
    return bool(info.st_ino)


def _stamp(info) -> tuple:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _safe_info(info, *, directory: bool, label: str) -> None:
    kind_ok = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
    _require(kind_ok, label, "expected a nonsymlink directory" if directory
             else "expected a regular nonsymlink file")
    _require(not (getattr(info, "st_file_attributes", 0)
                  & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)),
             label, "Windows reparse points are not permitted")


def _snapshot(path: Path, *, directory: bool):
    info = path.lstat()
    _safe_info(info, directory=directory, label=str(path))
    return info


def _select_index(path: str | Path) -> tuple:
    _require(isinstance(path, (str, Path)) and (not isinstance(path, str) or bool(path)),
             "input", "expected a nonempty path string or pathlib.Path")
    try:
        raw = str(path)
        _require("\x00" not in raw, "input", "NUL is forbidden in a path")
        raw.encode("utf-8")
        selected = Path(os.path.abspath(path))
        chosen_root = selected.parent
        before = _snapshot(chosen_root, directory=True)
        root = chosen_root.resolve(strict=True)
        _require(_identity(before) == _identity(_snapshot(root, directory=True)),
                 "input", "corpus root changed while resolving ancestors")
        return root, selected.name, chosen_root, before
    except CorpusError:
        raise
    except (OSError, ValueError, TypeError, OverflowError) as error:
        raise CorpusError(f"cannot select corpus input: {error}") from error


def _root_unchanged(root: Path, chosen_root: Path, before) -> None:
    for path in (chosen_root, root):
        _require(_identity(before) == _identity(_snapshot(path, directory=True)),
                 "corpus root", "selected directory changed during audit")


def _confined_snapshot(root: Path, parts: list[str]) -> tuple:
    directories = [(root, _snapshot(root, directory=True))]
    parent = root
    for part in parts[:-1]:
        parent /= part
        directories.append((parent, _snapshot(parent, directory=True)))
    target = parent / parts[-1]
    return target, directories, _snapshot(target, directory=False)


def _close_after_failure(descriptor: int, primary: BaseException) -> None:
    """Release a still-owned descriptor without hiding the original failure."""
    try:
        os.close(descriptor)
    except OSError as cleanup:
        if isinstance(primary, Exception):
            raise CorpusError(
                f"{primary}; descriptor cleanup also failed: {cleanup}"
            ) from primary
        # Cancellation keeps its original type even if cleanup also fails.
        raise primary from cleanup


def _open_confined(root: Path, parts: list[str], directories: list[tuple]) -> int:
    flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0)
             | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0))
    if os.name != "posix" or os.open not in os.supports_dir_fd:
        return os.open(root.joinpath(*parts), flags)
    directory_flags = flags | os.O_DIRECTORY
    descriptor = os.open(root, directory_flags)
    try:
        for position, (path, expected) in enumerate(directories):
            actual = os.fstat(descriptor)
            _safe_info(actual, directory=True, label=str(path))
            _require(_identity(actual) == _identity(expected), str(path),
                     "directory replaced while opening")
            if position < len(parts) - 1:
                child = os.open(parts[position], directory_flags, dir_fd=descriptor)
                predecessor = descriptor
                # Own the new child before the predecessor's fallible close.
                # Do not retry an ambiguous close of a possibly released FD.
                descriptor = child
                os.close(predecessor)
        leaf = os.open(parts[-1], flags, dir_fd=descriptor)
    except BaseException as primary:
        _close_after_failure(descriptor, primary)
        raise
    try:
        os.close(descriptor)
    except BaseException as primary:
        # The leaf was opened successfully but cannot be returned after a
        # parent-close failure. Keep its ownership until cleanup completes.
        _close_after_failure(leaf, primary)
        raise
    return leaf


def _stream(descriptor: int):
    try:
        return os.fdopen(descriptor, "rb")
    except BaseException as primary:
        _close_after_failure(descriptor, primary)
        raise


def _bind_descriptor(before_path, before_fd, label: str) -> None:
    _safe_info(before_fd, directory=False, label=label)
    if _usable_identity(before_fd) and _usable_identity(before_path):
        _require(_identity(before_fd) == _identity(before_path), label,
                 "file replaced while opening (path/descriptor identity mismatch)")


def _finish_read(target: Path, directories: list[tuple], before_path) -> None:
    _require(_stamp(before_path) == _stamp(_snapshot(target, directory=False)),
             str(target), "file changed while reading")
    for path, before in directories:
        _require(_identity(before) == _identity(_snapshot(path, directory=True)),
                 str(path), "directory replaced while reading")


def _read_confined_bytes(root: Path, parts: list[str], *, max_bytes: int) -> bytes:
    target, directories, before_path = _confined_snapshot(root, parts)
    _require(0 <= before_path.st_size <= max_bytes, str(target),
             f"input byte limit exceeded: limit {max_bytes}, observed {before_path.st_size}")
    with _stream(_open_confined(root, parts, directories)) as source:
        before_fd = os.fstat(source.fileno())
        _bind_descriptor(before_path, before_fd, str(target))
        _require(0 <= before_fd.st_size <= max_bytes, str(target),
                 f"opened input byte limit exceeded: limit {max_bytes}, observed {before_fd.st_size}")
        payload = source.read(max_bytes + 1)
        _require(len(payload) <= max_bytes and len(payload) == before_fd.st_size,
                 str(target), "input size changed or byte limit exceeded")
        _require(_stamp(before_fd) == _stamp(os.fstat(source.fileno())),
                 str(target), "file changed while reading")
    _finish_read(target, directories, before_path)
    return payload


def _load_index(path: str | Path) -> tuple:
    root, name, chosen_root, before_root = _select_index(path)
    try:
        payload = _read_confined_bytes(root, [name], max_bytes=MAX_INDEX_BYTES)
        value = parse_json_bytes(payload, max_bytes=MAX_INDEX_BYTES,
                                 max_nodes=MAX_INDEX_NODES, max_depth=MAX_DEPTH,
                                 max_number=1e12)
        validate_corpus(value)
        _root_unchanged(root, chosen_root, before_root)
        return value, hashlib.sha256(payload).hexdigest(), root, chosen_root, before_root
    except CorpusError:
        raise
    except (DataError, OSError, ValueError, TypeError, OverflowError) as error:
        raise CorpusError(f"cannot load corpus index: {error}") from error


def load_corpus(path: str | Path) -> dict:
    """Read one strict bounded index and return it unchanged after validation."""
    return _load_index(path)[0]


def _where(entry: dict, file_id: str | None = None) -> str:
    text = f"manifest {entry['manifest_path']!r}, capture {entry['capture_id']!r}"
    return text if file_id is None else f"{text}, file {file_id!r}"


def _load_manifests(index: dict, root: Path) -> list[tuple]:
    loaded = []
    total = 0
    for entry in sorted(index["captures"], key=lambda item: item["capture_id"]):
        try:
            remaining = MAX_TOTAL_MANIFEST_BYTES - total
            _require(remaining > 0, "manifests", "aggregate manifest byte limit exceeded")
            payload = _read_confined_bytes(root, entry["manifest_path"].split("/"),
                                           max_bytes=min(MAX_MANIFEST_BYTES, remaining))
            total += len(payload)
            observed = hashlib.sha256(payload).hexdigest()
            _require(observed == entry["manifest_sha256"], "manifest SHA-256",
                     f"mismatch: expected {entry['manifest_sha256']}, observed {observed}")
            capture = parse_json_bytes(payload, max_bytes=MAX_MANIFEST_BYTES,
                                       max_nodes=MAX_MANIFEST_NODES, max_depth=MAX_DEPTH,
                                       max_number=1e12)
            validate_capture(capture)
            _require(capture["capture_id"] == entry["capture_id"], "capture_id",
                     f"mismatch: expected {entry['capture_id']!r}, observed {capture['capture_id']!r}")
            role = PURPOSE_ROLES[entry["purpose"]]
            _require(capture["partition"]["role"] == role, "partition.role",
                     f"purpose {entry['purpose']!r} requires {role!r}, observed {capture['partition']['role']!r}")
            files = {item["file_id"]: item for item in capture["files"]}
            for descriptor in entry["derived_audio"]:
                file_id = descriptor["file_id"]
                _require(file_id in files, f"derived_audio file {file_id!r}", "unresolved file ID")
                _require(files[file_id]["kind"] == "derived", f"derived_audio file {file_id!r}",
                         f"expected derived kind, observed {files[file_id]['kind']!r}")
            loaded.append((entry, capture, observed))
        except (CorpusError, CaptureError, DataError, OSError, ValueError, TypeError, OverflowError) as error:
            raise CorpusError(f"{_where(entry)}: {error}") from error
    return loaded


def _inventory(loaded: list[tuple], *, check_audio: bool) -> tuple:
    inventories, work = [], []
    locators, digest_sizes = {}, {}
    artifact_total = audio_total = 0
    for entry, capture, observed in loaded:
        descriptors = {item["file_id"]: item for item in entry["derived_audio"]}
        manifest_parts = entry["manifest_path"].split("/")[:-1]
        files = []
        for artifact in sorted(capture["files"], key=lambda item: item["file_id"]):
            context = _where(entry, artifact["file_id"])
            identity = artifact["size_bytes"], artifact["sha256"]
            parts = manifest_parts + artifact["path"].split("/")
            locator = "/".join(parts).casefold()
            _require(locator not in locators or locators[locator] == identity, context,
                     "conflicting declared size/SHA-256 for the same case-folded artifact locator")
            locators[locator] = identity
            digest = artifact["sha256"]
            _require(digest not in digest_sizes or digest_sizes[digest] == artifact["size_bytes"],
                     context, "equal expected artifact SHA-256 has conflicting declared sizes")
            digest_sizes[digest] = artifact["size_bytes"]
            artifact_total += artifact["size_bytes"]
            _require(artifact_total <= MAX_TOTAL_ARTIFACT_BYTES, context,
                     f"aggregate declared artifact byte limit exceeded: limit {MAX_TOTAL_ARTIFACT_BYTES}, observed {artifact_total}")
            expected_audio = None
            if artifact["kind"] == "raw":
                expected_audio = {name: capture["digital"][name]["value"] for name in AUDIO_KEYS}
            elif artifact["file_id"] in descriptors:
                expected_audio = {name: descriptors[artifact["file_id"]][name] for name in AUDIO_KEYS}
            if check_audio and expected_audio is not None:
                audio_total += artifact["size_bytes"]
                _require(audio_total <= MAX_TOTAL_AUDIO_BYTES, context,
                         f"aggregate selected audio byte limit exceeded: limit {MAX_TOTAL_AUDIO_BYTES}, observed {audio_total}")
            if artifact["kind"] == "support":
                audio_status, audio_reason = "excluded_support", "support_not_audio_scope"
            elif not check_audio:
                audio_status, audio_reason = "not_run", "audio_check_not_requested"
            elif expected_audio is None:
                audio_status, audio_reason = "not_inspected", "derived_audio_not_declared"
            else:
                # This is internal pending state, never returned before a read.
                audio_status, audio_reason = "not_run", "audio_check_not_requested"
            item = {"file_id": artifact["file_id"], "kind": artifact["kind"],
                    "path": artifact["path"], "expected_size_bytes": artifact["size_bytes"],
                    "expected_sha256": artifact["sha256"], "observed_size_bytes": None,
                    "observed_sha256": None, "expected_audio": expected_audio,
                    "audio_status": audio_status, "audio_reason": audio_reason,
                    "observed_audio": None}
            files.append(item)
            work.append((entry, artifact, parts, item))
        inventories.append({
            "capture_id": entry["capture_id"], "manifest_path": entry["manifest_path"],
            "expected_manifest_sha256": entry["manifest_sha256"],
            "observed_manifest_sha256": observed, "record_status": capture["status"],
            "capture_kind": capture["capture_kind"], "purpose": entry["purpose"],
            "v1_role": capture["partition"]["role"],
            "session_id": capture["acquisition"]["session_id"]["value"],
            "v1_group_id": capture["partition"]["group_id"]["value"],
            "relation_labels": sorted((dict(item) for item in entry["relation_labels"]),
                                      key=lambda item: (item["kind"], item["label"])),
            "parent_capture_ids": sorted(entry["parent_capture_ids"]), "files": files})
    return inventories, work


def _verify_artifact(root: Path, parts: list[str], artifact: dict, seen: set) -> tuple:
    target, directories, before_path = _confined_snapshot(root, parts)
    expected_size = artifact["size_bytes"]
    _require(before_path.st_size == expected_size, "artifact size",
             f"mismatch: expected {expected_size}, observed {before_path.st_size}")
    with _stream(_open_confined(root, parts, directories)) as source:
        before_fd = os.fstat(source.fileno())
        _bind_descriptor(before_path, before_fd, str(target))
        _require(before_fd.st_size == expected_size, "opened artifact size",
                 f"mismatch: expected {expected_size}, observed {before_fd.st_size}")
        identity_info = before_fd if _usable_identity(before_fd) else before_path
        _require(_usable_identity(identity_info), "artifact identity",
                 "file identity unavailable; cannot exclude hardlink aliases")
        identity = _identity(identity_info)
        _require(identity not in seen, "artifact identity", "hardlink alias duplicates a file within this manifest")
        seen.add(identity)
        digest, count = hashlib.sha256(), 0
        while count <= expected_size:
            block = source.read(min(CHUNK_BYTES, expected_size + 1 - count))
            if not block:
                break
            count += len(block)
            digest.update(block)
        _require(count == expected_size, "stream size",
                 f"mismatch: expected {expected_size}, observed {count}")
        _require(_stamp(before_fd) == _stamp(os.fstat(source.fileno())),
                 str(target), "file changed during hashing")
    _finish_read(target, directories, before_path)
    observed = digest.hexdigest()
    _require(observed == artifact["sha256"], "artifact SHA-256",
             f"mismatch: expected {artifact['sha256']}, observed {observed}")
    return count, observed


def _inspect_selected_audio(root: Path, parts: list[str], item: dict) -> None:
    # Import only when actual audio was selected: structural/files-only use does
    # not depend on availability or initialization of a decoder.
    try:
        from capture_audio import inspect_audio
    except ImportError as error:
        raise CorpusError(f"capture audio inspector unavailable: {error}") from error
    expected = item["expected_audio"]
    _require(expected["format"] in AUDIO_FORMATS, "audio format",
             f"unsupported requested format {expected['format']!r}")
    # The direct inspector permits ancestor aliases. This caller independently
    # admits every corpus-relative ancestor before and after its complete read.
    target, directories, before_path = _confined_snapshot(root, parts)
    result = inspect_audio(target,
                           raw_format="raw_float32_le" if expected["format"] == "raw_float32_le" else None,
                           sample_rate_hz=expected["sample_rate_hz"],
                           channel_count=expected["channel_count"])
    _finish_read(target, directories, before_path)
    for name, observed_name in (("size_bytes", "observed_size_bytes"),
                                ("sha256", "observed_sha256")):
        _require(result[name] == item[observed_name], f"audio {name}",
                 f"changed from verified identity: expected {item[observed_name]!r}, observed {result[name]!r}")
    for name in sorted(AUDIO_KEYS):
        _require(result[name] == expected[name], f"audio {name}",
                 f"mismatch: expected {expected[name]!r}, observed {result[name]!r}")
    _require(result["decoded_digest_version"] == DECODED_DIGEST_VERSION, "decoded digest version",
             f"expected {DECODED_DIGEST_VERSION!r}, observed {result['decoded_digest_version']!r}")
    item["observed_audio"] = {name: result[name] for name in (
        "format", "sample_rate_hz", "channel_count", "frame_count",
        "decoded_digest_version", "decoded_sha256")}
    item["audio_status"], item["audio_reason"] = "verified", None


class _Graph:
    def __init__(self, captures: list[dict]):
        self.parents = {item["capture_id"]: item["capture_id"] for item in captures}
        self.ranks = dict.fromkeys(self.parents, 0)
        self.edges = {}

    def find(self, ident: str) -> str:
        root = ident
        while self.parents[root] != root:
            root = self.parents[root]
        while self.parents[ident] != ident:
            next_id = self.parents[ident]
            self.parents[ident] = root
            ident = next_id
        return root

    def add(self, left: str, right: str, reason: str, basis: str, value: str,
            left_file: str | None = None, right_file: str | None = None) -> None:
        if left == right:
            return
        key = (reason, value, left, right, left_file or "", right_file or "", basis)
        if key in self.edges:
            return
        _require(len(self.edges) < MAX_EDGES, "graph", "returned graph edge limit exceeded")
        self.edges[key] = {"left_capture_id": left, "right_capture_id": right,
                           "reason": reason, "basis": basis, "value": value,
                           "left_file_id": left_file, "right_file_id": right_file}
        left_root, right_root = self.find(left), self.find(right)
        if left_root != right_root:
            if self.ranks[left_root] < self.ranks[right_root]:
                left_root, right_root = right_root, left_root
            self.parents[right_root] = left_root
            if self.ranks[left_root] == self.ranks[right_root]:
                self.ranks[left_root] += 1

    def result(self) -> list[dict]:
        return [self.edges[key] for key in sorted(self.edges)]


def _bucket(buckets: dict, value: str, capture_id: str, file_id: str | None = None) -> None:
    members = buckets.setdefault(value, {})
    if capture_id not in members or (file_id is not None and file_id < members[capture_id]):
        members[capture_id] = file_id


def _stars(graph: _Graph, buckets: dict, reason: str, basis: str) -> None:
    for value in sorted(buckets):
        members = buckets[value]
        ids = sorted(members)
        anchor = ids[0]
        for other in ids[1:]:
            graph.add(anchor, other, reason, basis, value, members[anchor], members[other])


def _declared_graph(captures: list[dict], *, check_files: bool) -> _Graph:
    graph = _Graph(captures)
    buckets = {name: {} for name in ("session_id", "v1_group_id", "gesture_label",
                                    "family_label", "artifact_sha256")}
    for capture in captures:
        ident = capture["capture_id"]
        for name in ("session_id", "v1_group_id"):
            if capture[name] is not None:
                _bucket(buckets[name], capture[name], ident)
        for relation in capture["relation_labels"]:
            _bucket(buckets[relation["kind"] + "_label"], relation["label"], ident)
        for parent in capture["parent_capture_ids"]:
            graph.add(ident, parent, "parent_capture", "index_declaration", parent)
        for item in capture["files"]:
            if item["kind"] != "support":
                _bucket(buckets["artifact_sha256"], item["expected_sha256"], ident, item["file_id"])
    for name, values in buckets.items():
        basis = ("index_declaration" if name in ("gesture_label", "family_label") else
                 "verified_bytes" if name == "artifact_sha256" and check_files else
                 "manifest_declaration")
        _stars(graph, values, name, basis)
    return graph


def _groups_and_findings(captures: list[dict], graph: _Graph) -> tuple:
    by_id = {item["capture_id"]: item for item in captures}
    components = {}
    for ident in by_id:
        components.setdefault(graph.find(ident), []).append(ident)
    groups, findings = [], []

    def finding(code: str, severity: str, component: str, ids: list[str], refs: list[dict]) -> None:
        _require(len(findings) < MAX_FINDINGS, "findings", "returned finding limit exceeded")
        findings.append({"code": code, "severity": severity, "component_id": component,
                         "capture_ids": ids, "file_refs": refs})

    for members in components.values():
        members.sort()
        component = members[0]
        purposes = sorted({by_id[ident]["purpose"] for ident in members})
        failed = len(set(purposes) - {"unassigned"}) >= 2
        inconclusive = False
        if failed:
            finding("cross_purpose_component", "error", component, members.copy(), [])
        for ident in members:
            capture = by_id[ident]
            if capture["record_status"] == "planned":
                finding("planned_capture", "inconclusive", component, [ident], [])
                inconclusive = True
            if capture["purpose"] == "unassigned":
                finding("unassigned_capture", "inconclusive", component, [ident], [])
                inconclusive = True
            for item in capture["files"]:
                if item["audio_status"] == "not_inspected":
                    finding("derived_audio_not_declared", "inconclusive", component, [ident],
                            [{"capture_id": ident, "file_id": item["file_id"]}])
                    inconclusive = True
        groups.append({"component_id": component, "capture_ids": members,
                       "purposes": purposes,
                       "status": "failed" if failed else "inconclusive" if inconclusive else "pass"})
    groups.sort(key=lambda item: item["component_id"])
    findings.sort(key=lambda item: (
        item["code"], item["component_id"], tuple(item["capture_ids"]),
        tuple((ref["capture_id"], ref["file_id"]) for ref in item["file_refs"])))
    return groups, findings


def audit_corpus(path: str | Path, *, check_files: bool = False,
                 check_audio: bool = False) -> dict:
    """Audit the complete confined corpus in one of the three explicit modes."""
    _require(type(check_files) is bool and type(check_audio) is bool, "mode",
             "check_files and check_audio must be exact Boolean values")
    _require(not check_audio or check_files, "mode", "check_audio requires check_files")
    index, index_hash, root, chosen_root, before_root = _load_index(path)
    loaded = _load_manifests(index, root)
    return _audit_loaded(index, index_hash, root, chosen_root, before_root, loaded,
                         check_files=check_files, check_audio=check_audio)


def _audit_loaded(index: dict, index_hash: str, root: Path, chosen_root: Path,
                   before_root, loaded: list[tuple], *, check_files: bool,
                   check_audio: bool) -> dict:
    """Audit freshly admitted metadata without reopening its index/manifests.

    The public auditor and the stricter file-job wrapper share this one core.
    A caller must retain the exact validated, hash-bound parsed metadata and
    root observations for this operation. No prior artifact observations enter
    this interface: every requested byte/audio check below performs its reads.
    """
    # All declarations and aggregate work limits are checked before any artifact
    # opens. The declared graph is bounded before file hashing or decoding.
    captures, work = _inventory(loaded, check_audio=check_audio)
    graph = _declared_graph(captures, check_files=check_files)
    if check_files:
        identities = {capture["capture_id"]: set() for capture in captures}
        for entry, artifact, parts, item in work:
            try:
                size, digest = _verify_artifact(root, parts, artifact, identities[entry["capture_id"]])
                item["observed_size_bytes"], item["observed_sha256"] = size, digest
            except (CorpusError, OSError, ValueError, TypeError, OverflowError) as error:
                raise CorpusError(f"{_where(entry, artifact['file_id'])}: {error}") from error
    if check_audio:
        decoded = {}
        for entry, artifact, parts, item in work:
            if item["expected_audio"] is None:
                continue
            try:
                _inspect_selected_audio(root, parts, item)
            except (CorpusError, OSError, ValueError, TypeError, OverflowError) as error:
                raise CorpusError(f"{_where(entry, artifact['file_id'])}: {error}") from error
            _bucket(decoded, item["observed_audio"]["decoded_sha256"],
                    entry["capture_id"], artifact["file_id"])
        _stars(graph, decoded, "decoded_audio_sha256", "verified_audio")
    groups, findings = _groups_and_findings(captures, graph)
    try:
        _root_unchanged(root, chosen_root, before_root)
    except (CorpusError, OSError, ValueError, TypeError, OverflowError) as error:
        raise CorpusError(f"corpus root verification: {error}") from error
    statuses = {item["status"] for item in groups}
    status = "failed" if "failed" in statuses else "inconclusive" if "inconclusive" in statuses else "pass"
    has_files = bool(work)
    partial = any(item["audio_status"] == "not_inspected" for capture in captures for item in capture["files"])
    report = {"schema_version": 1, "contract_origin": "project-proposed-corpus-report-v1",
              "corpus_id": index["corpus_id"], "index_sha256": index_hash,
              "mode": "files_and_audio_checked" if check_audio else "files_checked" if check_files else "structural_only",
              "status": status, "structural_validation": "pass",
              "file_check": "not_run" if not check_files else "verified" if has_files else "not_applicable",
              "audio_check": "not_run" if not check_audio else "partial" if partial else "verified" if has_files else "not_applicable",
              "captures": captures, "edges": graph.result(), "groups": groups, "findings": findings}
    report.update(dict.fromkeys(CLAIM_FIELDS, "not_established"))
    return report


def _write_utf8(stream, text: str) -> None:
    # Preserve canonical UTF-8 and LF bytes on Windows and under non-UTF-8
    # terminal encodings; StringIO-style API redirection remains supported.
    binary = getattr(stream, "buffer", None)
    if binary is not None:
        payload = text.encode("utf-8")
        if binary.write(payload) != len(payload):
            raise OSError("incomplete corpus stream write")
        binary.flush()
    else:
        if stream.write(text) != len(text):
            raise OSError("incomplete corpus stream write")
        stream.flush()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--input", required=True, type=Path, help="capture corpus index JSON")
    parser.add_argument("--check-files", action="store_true", help="verify every declared artifact's bytes")
    parser.add_argument("--check-audio", action="store_true", help="inspect all selected audio; requires --check-files")
    args = parser.parse_args(argv)
    if args.check_audio and not args.check_files:
        parser.error("--check-audio requires --check-files")
    try:
        report = audit_corpus(args.input, check_files=args.check_files, check_audio=args.check_audio)
        output = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    except CorpusError as error:
        _write_utf8(sys.stderr, f"corpus error: {error}\n")
        return 1
    _write_utf8(sys.stdout, output)
    return {"pass": 0, "failed": 1, "inconclusive": 3}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
