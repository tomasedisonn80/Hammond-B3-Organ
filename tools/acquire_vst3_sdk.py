#!/usr/bin/env python3
"""Explicitly acquire or locally verify the locked, external VST3 SDK.

Configure calls only --verify-existing. Acquisition requires a new destination
outside this project, never resets an existing checkout, and leaves a failed
new checkout available for inspection. Neither operation changes the lock.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = PROJECT_ROOT / "data/dependencies/vst3-sdk-lock.json"
MAX_LOCK_BYTES = 64 * 1024
MODULE_NAMES = ("base", "cmake", "pluginterfaces", "public.sdk")
ROOT_URL = "https://github.com/steinbergmedia/vst3sdk.git"
MODULE_URLS = {
    "base": "https://github.com/steinbergmedia/vst3_base.git",
    "cmake": "https://github.com/steinbergmedia/vst3_cmake.git",
    "pluginterfaces": "https://github.com/steinbergmedia/vst3_pluginterfaces.git",
    "public.sdk": "https://github.com/steinbergmedia/vst3_public_sdk.git",
}


class SdkError(ValueError):
    """A dependency identity or acquisition precondition was not satisfied."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SdkError(f"duplicate lock field: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise SdkError(f"nonfinite JSON value in SDK lock: {value}")


def _hex(value: Any, count: int, label: str) -> None:
    if not isinstance(value, str) or re.fullmatch(rf"[0-9a-f]{{{count}}}", value) is None:
        raise SdkError(f"{label} must be {count} lowercase hexadecimal characters")


def _license(value: Any, label: str) -> None:
    if not isinstance(value, dict) or set(value) != {"spdx", "path", "bytes", "sha256"}:
        raise SdkError(f"{label} license fields are invalid")
    if value["spdx"] != "MIT" or value["path"] != "LICENSE.txt":
        raise SdkError(f"{label} must retain the reviewed primary MIT LICENSE.txt")
    if type(value["bytes"]) is not int or not 0 < value["bytes"] <= MAX_LOCK_BYTES:
        raise SdkError(f"{label} license size is invalid")
    _hex(value["sha256"], 64, f"{label} license hash")


def load_lock(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_LOCK_BYTES + 1)
        if len(raw) > MAX_LOCK_BYTES:
            raise SdkError("SDK lock exceeds 64 KiB")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                           parse_constant=_reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise SdkError(f"cannot read SDK lock: {exc}") from exc
    if not isinstance(value, dict) or type(value.get("schema_version")) is not int:
        raise SdkError("SDK lock must be an object with integer schema_version")
    if value["schema_version"] != 1 or value.get("repository") != ROOT_URL:
        raise SdkError("unsupported SDK lock schema or root repository")
    _hex(value.get("commit"), 40, "root commit")
    if not isinstance(value.get("tag"), str) or re.fullmatch(r"v[0-9.]+_build_[0-9]+", value["tag"]) is None:
        raise SdkError("SDK lock tag has an unsupported form")
    _license(value.get("license"), "root")
    modules = value.get("required_submodules")
    if not isinstance(modules, list) or len(modules) != len(MODULE_NAMES):
        raise SdkError("SDK lock must name exactly four required submodules")
    seen: set[str] = set()
    for module in modules:
        if not isinstance(module, dict) or set(module) != {"path", "repository", "commit", "license"}:
            raise SdkError("invalid required submodule fields")
        name = module["path"]
        if not isinstance(name, str) or name not in MODULE_NAMES or name in seen:
            raise SdkError("invalid or duplicate required submodule path")
        seen.add(name)
        if module["repository"] != MODULE_URLS[name]:
            raise SdkError(f"unexpected repository for submodule {name}")
        _hex(module["commit"], 40, f"{name} commit")
        _license(module["license"], name)
    embedded = value.get("embedded_third_party")
    if not isinstance(embedded, list) or len(embedded) != 1 or not isinstance(embedded[0], dict):
        raise SdkError("SDK lock must retain the reviewed embedded json.h record")
    item = embedded[0]
    if item.get("path") != "public.sdk/source/vst/moduleinfo/json.h" or item.get("license") != "Unlicense":
        raise SdkError("unexpected embedded json.h path or license")
    if type(item.get("bytes")) is not int or not 0 < item["bytes"] <= 1024 * 1024:
        raise SdkError("invalid embedded json.h size")
    _hex(item.get("sha256"), 64, "embedded json.h hash")
    return value


def _git(root: Path, *arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", os.fspath(root), *arguments],
            check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace", timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SdkError(f"cannot inspect SDK git checkout: {exc}") from exc
    if result.returncode != 0:
        raise SdkError(f"git inspection failed for {root.name}: {result.stderr.strip()[:500]}")
    return result.stdout.strip()


def _file_identity(root: Path, path: str, size: int, digest: str) -> None:
    target = root / path
    if target.is_symlink() or not target.is_file():
        raise SdkError(f"SDK identity file is missing or a symlink: {path}")
    try:
        with target.open("rb") as stream:
            raw = stream.read(size + 1)
    except OSError as exc:
        raise SdkError(f"cannot read SDK identity file {path}: {exc}") from exc
    if len(raw) != size or hashlib.sha256(raw).hexdigest() != digest:
        raise SdkError(f"SDK identity file size/SHA-256 mismatch: {path}")


def _checkout(root: Path, commit: str, license_info: dict[str, Any]) -> None:
    if not root.is_dir():
        raise SdkError(f"SDK checkout is missing: {root}")
    # This also rejects a missing submodule that merely inherits its parent's Git.
    actual_top = Path(_git(root, "rev-parse", "--show-toplevel")).resolve()
    if actual_top != root.resolve():
        raise SdkError(f"SDK path is not its own checkout: {root}")
    if _git(root, "rev-parse", "HEAD") != commit:
        raise SdkError(f"SDK commit mismatch: {root.name}")
    # Ignore nested gitlink worktrees here: every required module is checked below.
    if _git(root, "status", "--porcelain=v1", "--untracked-files=no", "--ignore-submodules=all"):
        raise SdkError(f"SDK tracked files are modified: {root.name}")
    # SDK utilities discover subdirectories, so even an untracked/ignored
    # CMakeLists.txt can alter compilation. Require out-of-checkout build output;
    # --others without --exclude-standard deliberately includes ignored files.
    if _git(root, "ls-files", "--others", "--directory", "--no-empty-directory"):
        raise SdkError(f"SDK contains untracked or ignored files: {root.name}; build outside the checkout")
    _file_identity(root, license_info["path"], license_info["bytes"], license_info["sha256"])


def verify_sdk(root: Path, lock: dict[str, Any]) -> dict[str, Any]:
    root = root.resolve()
    _checkout(root, lock["commit"], lock["license"])
    identities = [{"path": ".", "commit": lock["commit"]}]
    for module in lock["required_submodules"]:
        _checkout(root / module["path"], module["commit"], module["license"])
        # Inspect the immutable parent gitlink independently of the worktree HEAD.
        gitlink = _git(root, "ls-tree", "HEAD", "--", module["path"]).split()
        if gitlink != ["160000", "commit", module["commit"], module["path"]]:
            raise SdkError(f"SDK parent gitlink mismatch: {module['path']}")
        identities.append({"path": module["path"], "commit": module["commit"]})
    for item in lock["embedded_third_party"]:
        _file_identity(root, item["path"], item["bytes"], item["sha256"])
    return {"schema_version": 1, "sdk_root": os.fspath(root), "verified_checkouts": identities,
            "primary_licenses_verified": 5, "embedded_json_verified": True,
            "network_used": False}


def acquire_sdk(destination: Path, lock: dict[str, Any]) -> dict[str, Any]:
    # lexists also rejects a broken symlink; no existing path is ever reused.
    if os.path.lexists(destination):
        raise SdkError("acquisition destination already exists; use --verify-existing to inspect it")
    destination = destination.absolute()
    if not destination.parent.is_dir():
        raise SdkError("acquisition destination parent must already exist")
    resolved = destination.parent.resolve() / destination.name
    if resolved == PROJECT_ROOT or PROJECT_ROOT in resolved.parents:
        raise SdkError("acquire the SDK outside the project source tree")
    commands = [
        ["git", "-c", "core.autocrlf=false", "clone", "--depth", "1", "--single-branch",
         "--branch", lock["tag"], "--config", "core.autocrlf=false", "--config", "core.eol=lf",
         lock["repository"], os.fspath(resolved)],
        ["git", "-C", os.fspath(resolved), "-c", "core.autocrlf=false",
         "-c", "protocol.file.allow=never", "submodule", "update", "--init", "--depth", "1",
         "--", *MODULE_NAMES],
    ]
    try:
        subprocess.run(commands[0], check=True, timeout=600)
        if _git(resolved, "rev-parse", "HEAD") != lock["commit"]:
            raise SdkError("acquired tag does not match the locked root commit; submodules not fetched")
        subprocess.run(commands[1], check=True, timeout=600)
        for name in MODULE_NAMES:
            # The command-scoped setting protected initial submodule checkout;
            # retain it for later explicitly requested operations in these new
            # repositories. No pre-existing checkout/configuration is changed.
            _git(resolved / name, "config", "core.autocrlf", "false")
            _git(resolved / name, "config", "core.eol", "lf")
    except (OSError, subprocess.SubprocessError) as exc:
        raise SdkError(f"SDK acquisition failed; any new partial checkout is retained: {exc}") from exc
    result = verify_sdk(resolved, lock)
    result["network_used"] = True
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--destination", type=Path, help="explicit network acquisition into a new external path")
    choice.add_argument("--verify-existing", type=Path, help="read-only local identity check; never fetches")
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK,
                        help="reviewed lock (CMake always supplies the project's own lock)")
    args = parser.parse_args(argv)
    try:
        lock = load_lock(args.lock)
        result = (acquire_sdk(args.destination, lock) if args.destination is not None
                  else verify_sdk(args.verify_existing, lock))
    except SdkError as exc:
        print(f"VST3 SDK error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
