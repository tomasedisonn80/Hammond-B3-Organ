#!/usr/bin/env python3
"""Explicitly acquire or locally verify the locked, external SDL2 source.

Configure calls only --verify-existing, which never fetches or repairs sources.
Acquisition needs --destination naming a new path outside this project. Failed
new checkouts are left for inspection. Neither operation changes the lock.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = PROJECT_ROOT / "data/dependencies/sdl2-lock.json"
MAX_LOCK_BYTES = 16 * 1024
ROOT_URL = "https://github.com/libsdl-org/SDL.git"
REVIEWED_VERSION = "2.32.10"
REVIEWED_TAG = "release-2.32.10"
REVIEWED_COMMIT = "5d249570393f7a37e037abf22cd6012a4cc56a71"
REVIEWED_LICENSE = {
    "spdx": "Zlib",
    "path": "LICENSE.txt",
    "bytes": 884,
    "sha256": "97f35b302b361680ec1e891e95d2d52097bb95abff361434916d99dc1305f127",
}


class SdlError(ValueError):
    """An SDL2 identity or acquisition precondition was not satisfied."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SdlError(f"duplicate SDL2 lock field: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise SdlError(f"nonfinite JSON value in SDL2 lock: {value}")


def load_lock(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as stream:
            raw = stream.read(MAX_LOCK_BYTES + 1)
        if len(raw) > MAX_LOCK_BYTES:
            raise SdlError("SDL2 lock exceeds 16 KiB")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                           parse_constant=_reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise SdlError(f"cannot read SDL2 lock: {exc}") from exc
    fields = {"schema_version", "name", "version", "repository", "tag", "commit", "license"}
    if not isinstance(value, dict) or set(value) != fields:
        raise SdlError("SDL2 lock must contain exactly the reviewed schema fields")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise SdlError("unsupported SDL2 lock schema")
    # An alternate --lock cannot authorize an unreviewed repository, release,
    # or notice. Upgrades require a deliberate review of both code and data.
    if (value["name"] != "SDL2" or value["version"] != REVIEWED_VERSION
            or value["repository"] != ROOT_URL or value["tag"] != REVIEWED_TAG
            or value["commit"] != REVIEWED_COMMIT):
        raise SdlError("SDL2 lock does not match the reviewed official release identity")
    license_info = value["license"]
    if (not isinstance(license_info, dict) or license_info != REVIEWED_LICENSE
            or type(license_info.get("bytes")) is not int):
        raise SdlError("SDL2 lock does not match the reviewed primary Zlib LICENSE.txt")
    return value


def _resolve(path: Path) -> Path:
    try:
        return path.resolve()
    except (OSError, RuntimeError) as exc:
        raise SdlError(f"cannot resolve SDL2 path {path}: {exc}") from exc


def _external(root: Path) -> None:
    if root == PROJECT_ROOT or PROJECT_ROOT in root.parents:
        raise SdlError("keep the SDL2 checkout outside the project source tree")


def _git_environment() -> dict[str, str]:
    env = os.environ.copy()
    # A caller's enclosing Git operation must not redirect inspection to its
    # index, worktree or object database. Preserve proxy and CA configuration.
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
        raise SdlError(f"cannot inspect SDL2 Git checkout: {exc}") from exc
    if result.returncode != 0:
        raise SdlError(f"SDL2 Git inspection failed: {result.stderr.strip()[:500]}")
    return result.stdout.rstrip("\r\n")


def _license_identity(root: Path, license_info: dict[str, Any]) -> None:
    target = root / license_info["path"]
    if target.is_symlink() or not target.is_file():
        raise SdlError("SDL2 LICENSE.txt is missing or a symlink")
    try:
        with target.open("rb") as stream:
            raw = stream.read(license_info["bytes"] + 1)
    except OSError as exc:
        raise SdlError(f"cannot read SDL2 LICENSE.txt: {exc}") from exc
    if (len(raw) != license_info["bytes"]
            or hashlib.sha256(raw).hexdigest() != license_info["sha256"]):
        raise SdlError("SDL2 LICENSE.txt size/SHA-256 mismatch")


def verify_sdl2(root: Path, lock: dict[str, Any]) -> dict[str, Any]:
    root = _resolve(root)
    _external(root)
    if not root.is_dir():
        raise SdlError(f"SDL2 checkout is missing: {root}")
    # Reject a child directory that merely inherits its parent's Git checkout.
    if _resolve(Path(_git(root, "rev-parse", "--show-toplevel"))) != root:
        raise SdlError("SDL2 path is not the root of its own checkout")
    # Reject partial clones before any command might need a missing object.
    # Shallow clones are supported; no inspection command contacts a remote.
    for entry in _git(root, "config", "--local", "--list").splitlines():
        key = entry.partition("=")[0].lower()
        if key == "extensions.partialclone" or (key.startswith("remote.") and key.endswith(".promisor")):
            raise SdlError("SDL2 partial/promisor clones are unsupported; use a complete checkout")
    if _git(root, "rev-parse", "--verify", "HEAD^{commit}") != lock["commit"]:
        raise SdlError("SDL2 root commit mismatch")
    tag_commit = _git(root, "rev-parse", "--verify", f"refs/tags/{lock['tag']}^{{commit}}")
    if tag_commit != lock["commit"]:
        raise SdlError("SDL2 release tag does not resolve to the locked commit")
    # Do not let index flags hide a modified or absent tracked source file.
    entries = _git(root, "ls-files", "-v", "-z").split("\0")
    if any(entry and not entry.startswith("H ") for entry in entries):
        raise SdlError("SDL2 index has hidden/sparse or unmerged files; use an ordinary complete checkout")
    if _git(root, "status", "--porcelain=v1", "--untracked-files=no", "--ignore-submodules=none"):
        raise SdlError("SDL2 tracked files are modified")
    # SDL's build discovers source directories. Include ignored files: an
    # ignored extra source or CMakeLists.txt must not affect the locked build.
    if _git(root, "ls-files", "--others", "--directory", "--no-empty-directory"):
        raise SdlError("SDL2 contains untracked or ignored files; build outside the checkout")
    for name in ("CMakeLists.txt", "include/SDL.h", "include/SDL_version.h"):
        source = root / name
        if source.is_symlink() or not source.is_file():
            raise SdlError(f"SDL2 source file is missing or a symlink: {name}")
    _license_identity(root, lock["license"])
    return {
        "schema_version": 1,
        "sdl2_root": os.fspath(root),
        "version": lock["version"],
        "repository": lock["repository"],
        "tag": lock["tag"],
        "commit": lock["commit"],
        "primary_licenses_verified": 1,
        "network_used": False,
    }


def acquire_sdl2(destination: Path, lock: dict[str, Any]) -> dict[str, Any]:
    # lexists also rejects broken links; never reuse or repair an existing path.
    if os.path.lexists(destination):
        raise SdlError("acquisition destination already exists; use --verify-existing to inspect it")
    if not destination.parent.is_dir():
        raise SdlError("acquisition destination parent must already exist")
    resolved = _resolve(destination.parent) / destination.name
    _external(resolved)
    try:
        # Reserve the new directory atomically before Git; another writer's
        # pre-existing empty directory is not ours to reuse either.
        resolved.mkdir()
    except OSError as exc:
        raise SdlError(f"cannot create new SDL2 destination: {exc}") from exc
    command = [
        "git", "-c", "core.autocrlf=false", "clone", "--depth", "1", "--single-branch",
        "--branch", lock["tag"], "--no-recurse-submodules",
        "--config", "core.autocrlf=false", "--config", "core.eol=lf",
        "--", lock["repository"], os.fspath(resolved),
    ]
    try:
        subprocess.run(command, check=True, timeout=600, env=_git_environment())
    except (OSError, subprocess.SubprocessError) as exc:
        raise SdlError(f"SDL2 acquisition failed; any new partial checkout is retained: {exc}") from exc
    result = verify_sdl2(resolved, lock)
    result["network_used"] = True
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--destination", type=Path,
                        help="explicit network acquisition into a new external path")
    choice.add_argument("--verify-existing", type=Path,
                        help="read-only local identity check; never fetches or repairs")
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK,
                        help="strict reviewed lock (CMake always uses the project's own lock)")
    args = parser.parse_args(argv)
    try:
        lock = load_lock(args.lock)
        result = (acquire_sdl2(args.destination, lock) if args.destination is not None
                  else verify_sdl2(args.verify_existing, lock))
    except SdlError as exc:
        print(f"SDL2 error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
