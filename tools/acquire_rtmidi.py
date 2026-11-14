#!/usr/bin/env python3
"""Explicitly acquire or verify locked RtMidi and prepare its reviewed build copy.

Only --destination contacts the network. --verify-existing is read-only;
--prepare-build-copy additionally creates a separate, identified source copy.
An existing prepared copy must match exactly and is never silently repaired.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = PROJECT_ROOT / "data/dependencies/rtmidi-lock.json"
MAX_LOCK_BYTES = 16 * 1024
PATCH_FILENAME = "rtmidi-coremidi-zero-init.patch"
MANIFEST_FILENAME = "prepared-source.json"
REVIEWED_LOCK = {
    "schema_version": 1,
    "name": "RtMidi",
    "version": "6.0.0",
    "repository": "https://github.com/thestk/rtmidi.git",
    "tag": "6.0.0",
    "commit": "1e5b49925aa60065db52de44c366d446a902547b",
    "sources": {
        "RtMidi.cpp": {
            "bytes": 168212,
            "sha256": "184d775e88e5d73b079897363fb42af155122e879f0bc9254a1c7edae4eadb3c",
        },
        "RtMidi.h": {
            "bytes": 27901,
            "sha256": "74f98ca172243b0b9c0c59f53c4e20285d879ffa86b3d61692109b013f4606f9",
        },
    },
    "license": {
        "spdx": "MIT",
        "path": "LICENSE",
        "bytes": 1349,
        "sha256": "7fa091d9c1aa492ebfcafa9f919d27bbce61e4f048ece2dfc3b7f93181e9e364",
    },
    "patch": {
        "id": "coremidi-zero-initialize-v1",
        "source": "RtMidi.cpp",
        "before": "CoreMidiData *data = (CoreMidiData *) new CoreMidiData;",
        "after": "CoreMidiData *data = (CoreMidiData *) new CoreMidiData{};",
        "occurrences": 2,
        "format": "unified-diff-lf-context-3",
        "bytes": 728,
        "sha256": "80aedddee9affe1c9ab305b605c6ca1f5c2209fd5d23da843c8c3f325426c4ad",
        "prepared_bytes": 168216,
        "prepared_sha256": "240705532b17e593dc17434259233a586c9136808724124f1d3af649eadea17a",
    },
}


class RtMidiError(ValueError):
    """A dependency identity or preparation precondition failed."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise RtMidiError(f"duplicate RtMidi lock field: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise RtMidiError(f"nonfinite JSON value in RtMidi lock: {value}")


def load_lock(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_LOCK_BYTES + 1)
        if len(raw) > MAX_LOCK_BYTES:
            raise RtMidiError("RtMidi lock exceeds 16 KiB")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                           parse_constant=_reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise RtMidiError(f"cannot read RtMidi lock: {exc}") from exc
    # Canonical JSON equality also distinguishes booleans/floats from integers.
    # --lock cannot authorize a different source, license or safety correction.
    if json.dumps(value, sort_keys=True) != json.dumps(REVIEWED_LOCK, sort_keys=True):
        raise RtMidiError("RtMidi lock does not match the reviewed release, files and patch")
    return value


def _resolve(path: Path) -> Path:
    try:
        return path.resolve()
    except (OSError, RuntimeError) as exc:
        raise RtMidiError(f"cannot resolve RtMidi path {path}: {exc}") from exc


def _external(root: Path) -> None:
    if root == PROJECT_ROOT or PROJECT_ROOT in root.parents:
        raise RtMidiError("keep the locked RtMidi checkout outside the project source tree")


def _git_environment() -> dict[str, str]:
    env = os.environ.copy()
    for name in ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
                 "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                 "GIT_NAMESPACE", "GIT_PREFIX"):
        env.pop(name, None)
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["GIT_NO_LAZY_FETCH"] = "1"
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


def _git(root: Path, *arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", os.fspath(root), "-c", "core.fsmonitor=false",
             "-c", "protocol.allow=never", *arguments],
            check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace", timeout=30,
            env=_git_environment(),
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RtMidiError(f"cannot inspect RtMidi Git checkout: {exc}") from exc
    if result.returncode != 0:
        raise RtMidiError(f"RtMidi Git inspection failed: {result.stderr.strip()[:500]}")
    return result.stdout.rstrip("\r\n")


def _checked_bytes(path: Path, identity: dict[str, Any]) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise RtMidiError(f"RtMidi file is missing, not regular, or a symlink: {path.name}")
    try:
        with path.open("rb") as stream:
            raw = stream.read(identity["bytes"] + 1)
    except OSError as exc:
        raise RtMidiError(f"cannot read RtMidi file {path.name}: {exc}") from exc
    if (len(raw) != identity["bytes"]
            or hashlib.sha256(raw).hexdigest() != identity["sha256"]):
        raise RtMidiError(f"RtMidi {path.name} size/SHA-256 mismatch")
    return raw


def verify_rtmidi(root: Path, lock: dict[str, Any]) -> dict[str, Any]:
    root = _resolve(root)
    _external(root)
    if not root.is_dir():
        raise RtMidiError(f"RtMidi checkout is missing: {root}")
    if _resolve(Path(_git(root, "rev-parse", "--show-toplevel"))) != root:
        raise RtMidiError("RtMidi path is not the root of its own checkout")
    for entry in _git(root, "config", "--local", "--list").splitlines():
        key = entry.partition("=")[0].lower()
        if key == "extensions.partialclone" or (key.startswith("remote.") and key.endswith(".promisor")):
            raise RtMidiError("RtMidi partial/promisor clones are unsupported; use a complete checkout")
    if _git(root, "rev-parse", "--verify", "HEAD^{commit}") != lock["commit"]:
        raise RtMidiError("RtMidi root commit mismatch")
    if _git(root, "rev-parse", "--verify", f"refs/tags/{lock['tag']}^{{commit}}") != lock["commit"]:
        raise RtMidiError("RtMidi release tag does not resolve to the locked commit")
    entries = _git(root, "ls-files", "-v", "-z").split("\0")
    if any(entry and not entry.startswith("H ") for entry in entries):
        raise RtMidiError("RtMidi index has hidden/sparse or unmerged files")
    if _git(root, "status", "--porcelain=v1", "--untracked-files=no", "--ignore-submodules=none"):
        raise RtMidiError("RtMidi tracked files are modified")
    if _git(root, "ls-files", "--others", "--directory", "--no-empty-directory"):
        raise RtMidiError("RtMidi contains untracked or ignored files; prepare outside its checkout")
    for name, identity in lock["sources"].items():
        _checked_bytes(root / name, identity)
    _checked_bytes(root / lock["license"]["path"], lock["license"])
    return {
        "schema_version": 1,
        "rtmidi_root": os.fspath(root),
        "version": lock["version"],
        "repository": lock["repository"],
        "tag": lock["tag"],
        "commit": lock["commit"],
        "source_files_verified": len(lock["sources"]),
        "primary_licenses_verified": 1,
        "network_used": False,
    }


def _prepared_payload(root: Path, lock: dict[str, Any]) -> dict[str, bytes]:
    payload = {name: _checked_bytes(root / name, identity)
               for name, identity in lock["sources"].items()}
    payload[lock["license"]["path"]] = _checked_bytes(root / lock["license"]["path"], lock["license"])
    patch_info = lock["patch"]
    before = patch_info["before"].encode("utf-8")
    original = payload[patch_info["source"]]
    if original.count(before) != patch_info["occurrences"]:
        raise RtMidiError("RtMidi safety correction requires exactly two original allocations")
    prepared = original.replace(before, patch_info["after"].encode("utf-8"))
    if (len(prepared) != patch_info["prepared_bytes"]
            or hashlib.sha256(prepared).hexdigest() != patch_info["prepared_sha256"]):
        raise RtMidiError("RtMidi prepared source does not match the reviewed correction")
    patch = "".join(difflib.unified_diff(
        original.decode("utf-8").splitlines(keepends=True),
        prepared.decode("utf-8").splitlines(keepends=True),
        fromfile="original/RtMidi.cpp", tofile="prepared/RtMidi.cpp", n=3,
    )).encode("utf-8")
    if len(patch) != patch_info["bytes"] or hashlib.sha256(patch).hexdigest() != patch_info["sha256"]:
        raise RtMidiError("RtMidi generated patch does not match its reviewed identity")
    payload[patch_info["source"]] = prepared
    payload[PATCH_FILENAME] = patch
    manifest = {
        "schema_version": 1,
        "dependency_lock": lock,
        "preparation_tool": {
            "path": "tools/acquire_rtmidi.py",
            "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "prepared_files": {name: {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
                           for name, raw in sorted(payload.items())},
    }
    payload[MANIFEST_FILENAME] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return payload


def prepare_build_copy(root: Path, destination: Path, lock: dict[str, Any]) -> dict[str, Any]:
    """Verify all inputs, then create a new copy or verify an exact existing one."""
    result = verify_rtmidi(root, lock)
    root = _resolve(root)
    if destination.is_symlink():
        raise RtMidiError("prepared RtMidi destination must not be a symlink")
    output = _resolve(destination)
    if output == root or root in output.parents or output in root.parents:
        raise RtMidiError("prepared RtMidi copy must be separate from the locked checkout")
    payload = _prepared_payload(root, lock)
    reused = output.exists()
    if reused:
        if not output.is_dir() or {entry.name for entry in output.iterdir()} != set(payload):
            raise RtMidiError("existing prepared RtMidi directory has unexpected or missing files")
        for name, raw in payload.items():
            _checked_bytes(output / name, {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    else:
        if not output.parent.is_dir():
            raise RtMidiError("prepared RtMidi destination parent must already exist")
        # Reserve a new directory and use exclusive writes. On interruption keep
        # the incomplete copy for inspection; never repair or overwrite it.
        output.mkdir()
        for name, raw in payload.items():
            with (output / name).open("xb") as stream:
                stream.write(raw)
    result.update({
        "prepared_root": os.fspath(output),
        "prepared_copy_reused": reused,
        "prepared_cpp_sha256": lock["patch"]["prepared_sha256"],
        "patch_sha256": lock["patch"]["sha256"],
        "manifest_sha256": hashlib.sha256(payload[MANIFEST_FILENAME]).hexdigest(),
    })
    return result


def acquire_rtmidi(destination: Path, lock: dict[str, Any]) -> dict[str, Any]:
    if os.path.lexists(destination):
        raise RtMidiError("acquisition destination exists; use --verify-existing to inspect it")
    if not destination.parent.is_dir():
        raise RtMidiError("acquisition destination parent must already exist")
    resolved = _resolve(destination.parent) / destination.name
    _external(resolved)
    resolved.mkdir()
    command = [
        "git", "-c", "core.autocrlf=false", "clone", "--depth", "1", "--single-branch",
        "--branch", lock["tag"], "--no-recurse-submodules",
        "--config", "core.autocrlf=false", "--config", "core.eol=lf",
        "--", lock["repository"], os.fspath(resolved),
    ]
    try:
        subprocess.run(command, check=True, timeout=600, env=_git_environment())
    except (OSError, subprocess.SubprocessError) as exc:
        raise RtMidiError(f"RtMidi acquisition failed; any new partial checkout is retained: {exc}") from exc
    result = verify_rtmidi(resolved, lock)
    result["network_used"] = True
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--destination", type=Path,
                        help="explicit network acquisition into a new external path")
    choice.add_argument("--verify-existing", type=Path,
                        help="local checkout verification; never fetches or repairs")
    parser.add_argument("--prepare-build-copy", type=Path,
                        help="with --verify-existing, create or verify a separate prepared directory")
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK,
                        help="strict reviewed lock (CMake uses this project's own lock)")
    args = parser.parse_args(argv)
    if args.prepare_build_copy is not None and args.verify_existing is None:
        parser.error("--prepare-build-copy requires --verify-existing")
    try:
        lock = load_lock(args.lock)
        if args.destination is not None:
            result = acquire_rtmidi(args.destination, lock)
        elif args.prepare_build_copy is not None:
            result = prepare_build_copy(args.verify_existing, args.prepare_build_copy, lock)
        else:
            result = verify_rtmidi(args.verify_existing, lock)
    except (RtMidiError, OSError) as exc:
        print(f"RtMidi error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
