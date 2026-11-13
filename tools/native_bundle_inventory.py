#!/usr/bin/env python3
"""Record a bounded, byte-identified native bundle without claiming host qualification.

Inputs must be quiescent. All bundle symlinks and special files reject. The report
is published as a complete new file with a no-clobber hard link; it never edits
the bundle, dependency lock, notices, or an existing destination.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import stat
import struct
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MAX_ENTRIES = 512
MAX_DEPTH = 12
MAX_PATH_BYTES = 1024
MAX_FILE_BYTES = 128 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
MAX_METADATA_BYTES = 128 * 1024
MAX_REPORT_BYTES = 1024 * 1024
CONFIGURATIONS = ("Debug", "Release", "RelWithDebInfo", "MinSizeRel")
MODULE_PATHS = {
    "Contents/x86_64-linux/HammondB3.so": ("linux", "x86_64"),
    "Contents/aarch64-linux/HammondB3.so": ("linux", "arm64"),
    "Contents/x86_64-win/HammondB3.vst3": ("windows", "x86_64"),
    "Contents/arm64-win/HammondB3.vst3": ("windows", "arm64"),
    "Contents/MacOS/HammondB3": ("macos", None),
}
RESOURCES = "Contents/Resources/"


class InventoryError(ValueError):
    """The selected payload or publication precondition is unsupported."""


def _signature(info: os.stat_result) -> tuple[int, ...]:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _regular(path: Path, maximum: int) -> os.stat_result:
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise InventoryError(f"expected a regular file, without symlinks: {path.name}")
    if info.st_size > maximum:
        raise InventoryError(f"file exceeds byte bound: {path.name}")
    return info


def _file_record(path: Path, maximum: int) -> dict[str, Any]:
    before = _regular(path, maximum)
    digest = hashlib.sha256()
    count = 0
    with path.open("rb") as stream:
        if _signature(os.fstat(stream.fileno())) != _signature(before):
            raise InventoryError("file changed before hashing")
        while chunk := stream.read(1024 * 1024):
            count += len(chunk)
            if count > maximum:
                raise InventoryError("file grew beyond byte bound")
            digest.update(chunk)
        after = os.fstat(stream.fileno())
    if count != before.st_size or _signature(after) != _signature(before) or \
            _signature(path.lstat()) != _signature(before):
        raise InventoryError("file changed during hashing")
    return {"bytes": count, "sha256": digest.hexdigest()}


def _bounded_bytes(path: Path) -> bytes:
    record = _file_record(path, MAX_METADATA_BYTES)
    with path.open("rb") as stream:
        raw = stream.read(MAX_METADATA_BYTES + 1)
    if len(raw) != record["bytes"] or hashlib.sha256(raw).hexdigest() != record["sha256"]:
        raise InventoryError("metadata changed during reading")
    return raw


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InventoryError(f"duplicate SDK lock field: {key}")
        result[key] = value
    return result


def _no_constant(value: str) -> None:
    raise InventoryError(f"nonfinite SDK lock value: {value}")


def _hex(value: Any, length: int, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(rf"[0-9a-f]{{{length}}}", value) is None:
        raise InventoryError(f"invalid {label}")
    return value


def _path_name(path: Path, root: Path) -> str:
    relative = path.relative_to(root)
    text = relative.as_posix()
    if len(relative.parts) > MAX_DEPTH or len(text.encode("utf-8")) > MAX_PATH_BYTES:
        raise InventoryError("bundle path exceeds depth or byte bound")
    for part in relative.parts:
        if part.endswith((" ", ".")) or any(ord(c) < 32 or c in '<>:"\\|?*' for c in part):
            raise InventoryError("bundle path is not a portable relative name")
    return text


def _walk(root: Path) -> list[tuple[str, Path, os.stat_result]]:
    result: list[tuple[str, Path, os.stat_result]] = []
    pending = [root]
    names: set[str] = set()
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as iterator:
            for entry in iterator:
                if len(result) >= MAX_ENTRIES:
                    raise InventoryError("bundle exceeds entry bound")
                path = Path(entry.path)
                name = _path_name(path, root)
                key = name.casefold()
                if key in names:
                    raise InventoryError("bundle contains a case-colliding path")
                names.add(key)
                info = entry.stat(follow_symlinks=False)
                if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                    raise InventoryError("bundle contains a symlink or special file")
                result.append((name, path, info))
                if stat.S_ISDIR(info.st_mode):
                    pending.append(path)
    return sorted(result, key=lambda row: row[0])


def _native_header(path: Path, size: int) -> dict[str, Any]:
    """Read format/CPU facts only; this does not load a plugin or verify exports."""
    with path.open("rb") as stream:
        def read(offset: int, length: int) -> bytes:
            if offset < 0 or length < 0 or offset + length > size:
                raise InventoryError("truncated native module header")
            stream.seek(offset)
            data = stream.read(length)
            if len(data) != length:
                raise InventoryError("truncated native module header")
            return data

        magic = read(0, 4)
        if magic == b"\x7fELF":
            header = read(0, 64)
            if header[4] != 2 or header[5] not in (1, 2):
                raise InventoryError("only 64-bit ELF modules are supported")
            endian = "<" if header[5] == 1 else ">"
            kind, cpu = struct.unpack_from(endian + "HH", header, 16)
            architecture = {62: "x86_64", 183: "arm64"}.get(cpu)
            if kind != 3 or architecture is None:
                raise InventoryError("unsupported ELF module kind or architecture")
            return {"format": "ELF64", "platform": "linux", "architectures": [architecture]}
        if magic[:2] == b"MZ":
            offset = struct.unpack_from("<I", read(0, 64), 60)[0]
            if offset > 1024 * 1024:
                raise InventoryError("PE header offset exceeds bound")
            header = read(offset, 26)
            cpu = struct.unpack_from("<H", header, 4)[0]
            flags = struct.unpack_from("<H", header, 22)[0]
            optional_magic = struct.unpack_from("<H", header, 24)[0]
            architecture = {0x8664: "x86_64", 0xAA64: "arm64"}.get(cpu)
            if header[:4] != b"PE\0\0" or optional_magic != 0x20B or \
                    not flags & 0x2000 or architecture is None:
                raise InventoryError("unsupported PE DLL header or architecture")
            return {"format": "PE32+", "platform": "windows", "architectures": [architecture]}

        def mach(offset: int, length: int) -> tuple[int, str]:
            if length < 32:
                raise InventoryError("truncated Mach-O slice")
            header = read(offset, 32)
            endian = {b"\xcf\xfa\xed\xfe": "<", b"\xfe\xed\xfa\xcf": ">"}.get(header[:4])
            if endian is None:
                raise InventoryError("only 64-bit Mach-O slices are supported")
            cpu, _, kind = struct.unpack_from(endian + "III", header, 4)
            architecture = {0x01000007: "x86_64", 0x0100000C: "arm64"}.get(cpu)
            if architecture is None or kind not in (6, 8):
                raise InventoryError("unsupported Mach-O module kind or architecture")
            return cpu, architecture

        if magic in (b"\xcf\xfa\xed\xfe", b"\xfe\xed\xfa\xcf"):
            _, architecture = mach(0, size)
            return {"format": "Mach-O64", "platform": "macos", "architectures": [architecture]}
        if magic in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"):
            count = struct.unpack(">I", read(4, 4))[0]
            width = 20 if magic[-1] == 0xBE else 32
            if not 1 <= count <= 4:
                raise InventoryError("Mach-O slice count exceeds bound")
            regions: list[tuple[int, int]] = []
            architectures: list[str] = []
            for index in range(count):
                entry = read(8 + index * width, width)
                if width == 20:
                    cpu, _, offset, length, alignment = struct.unpack(">IIIII", entry)
                else:
                    cpu, _, offset, length, alignment, _ = struct.unpack(">IIQQII", entry)
                if offset < 8 + count * width or alignment > 30 or offset % (1 << alignment) or \
                        offset + length > size or any(offset < end and start < offset + length
                                                    for start, end in regions):
                    raise InventoryError("invalid or overlapping Mach-O slice extent")
                inner_cpu, architecture = mach(offset, length)
                if inner_cpu != cpu or architecture in architectures:
                    raise InventoryError("inconsistent or duplicate Mach-O slice architecture")
                regions.append((offset, offset + length))
                architectures.append(architecture)
            return {"format": "Mach-O-universal64", "platform": "macos",
                    "architectures": sorted(architectures)}
    raise InventoryError("unrecognized native module header")


def make_inventory(bundle: Path, configuration: str, sdk_lock: Path, notices: Path,
                   source_commit: str | None = None,
                   source_manifest: Path | None = None) -> dict[str, Any]:
    if configuration not in CONFIGURATIONS or (source_commit is None) == (source_manifest is None):
        raise InventoryError("select a supported configuration and exactly one source identity")
    if bundle.is_symlink() or not bundle.is_dir() or bundle.name != "HammondB3.vst3":
        raise InventoryError("bundle must be the nonsymlink HammondB3.vst3 directory")
    root = bundle.resolve(strict=True)
    if source_commit is not None:
        source = {"kind": "caller-declared-git-commit",
                  "revision": _hex(source_commit, 40, "source commit")}
    else:
        assert source_manifest is not None
        source = {"kind": "overlay-manifest-bytes", "name": source_manifest.name,
                  **_file_record(source_manifest, MAX_METADATA_BYTES)}

    lock_bytes = _bounded_bytes(sdk_lock)
    lock = json.loads(lock_bytes.decode("utf-8"), object_pairs_hook=_unique, parse_constant=_no_constant)
    if not isinstance(lock, dict) or type(lock.get("schema_version")) is not int or lock["schema_version"] != 1:
        raise InventoryError("unsupported SDK lock shape")
    commit = _hex(lock.get("commit"), 40, "SDK root commit")
    license_info = lock.get("license")
    if not isinstance(license_info, dict) or type(license_info.get("bytes")) is not int:
        raise InventoryError("invalid primary SDK license record")
    license_sha = _hex(license_info.get("sha256"), 64, "SDK primary license hash")
    notice_record = _file_record(notices, MAX_METADATA_BYTES)
    initial = _walk(root)
    records = []
    total = 0
    for name, path, info in initial:
        if stat.S_ISREG(info.st_mode):
            if info.st_size > MAX_FILE_BYTES or total + info.st_size > MAX_TOTAL_BYTES:
                raise InventoryError("bundle exceeds file or total byte bound")
            record = _file_record(path, MAX_FILE_BYTES)
            records.append({"path": name, "mode_octal": f"{stat.S_IMODE(info.st_mode):04o}", **record})
            total += record["bytes"]
    by_name = {record["path"]: record for record in records}
    for name in ("moduleinfo.json", "VST3_SDK_LICENSE.txt", "THIRD_PARTY_NOTICES.md"):
        record = by_name.get(RESOURCES + name)
        if record is None or not 0 < record["bytes"] <= MAX_METADATA_BYTES:
            raise InventoryError(f"required bounded resource missing or empty: {name}")
    bundled_license = by_name[RESOURCES + "VST3_SDK_LICENSE.txt"]
    if bundled_license["bytes"] != license_info["bytes"] or bundled_license["sha256"] != license_sha:
        raise InventoryError("bundled SDK license does not match the selected lock")
    bundled_notices = by_name[RESOURCES + "THIRD_PARTY_NOTICES.md"]
    if any(bundled_notices[key] != notice_record[key] for key in ("bytes", "sha256")):
        raise InventoryError("bundled project notices differ from the selected source notices")
    modules = [name for name in by_name if name in MODULE_PATHS]
    if len(modules) != 1:
        raise InventoryError("bundle must contain exactly one supported native module path")
    module_path = modules[0]
    module = {"path": module_path, **_native_header(root / module_path, by_name[module_path]["bytes"])}
    expected_platform, expected_arch = MODULE_PATHS[module_path]
    if module["platform"] != expected_platform or \
            (expected_arch is not None and module["architectures"] != [expected_arch]):
        raise InventoryError("native header does not match its bundle platform path")
    final = _walk(root)
    if [(name, _signature(info)) for name, _, info in initial] != \
            [(name, _signature(info)) for name, _, info in final]:
        raise InventoryError("bundle changed during inventory")
    return {"schema_version": 1, "kind": "hammond-native-bundle-inventory-v1",
            "bundle_name": root.name, "configuration": configuration, "source": source,
            "sdk_lock": {"bytes": len(lock_bytes), "sha256": hashlib.sha256(lock_bytes).hexdigest(),
                         "root_commit": commit, "primary_license_sha256": license_sha},
            "module": module, "file_count": len(records), "total_bytes": total, "files": records,
            "execution_environment": {"system": platform.system(), "machine": platform.machine(),
                                      "python": platform.python_version()},
            "scope": "File identities and native-header inspection; no SDK/DAW/device/signature/fidelity result."}


def publish_report(report: dict[str, Any], output: Path, bundle: Path) -> None:
    if os.path.lexists(output):
        raise InventoryError("inventory output already exists")
    if output.resolve().is_relative_to(bundle.resolve()):
        raise InventoryError("inventory output must be outside the bundle")
    if not output.parent.is_dir():
        raise InventoryError("inventory output parent must already exist")
    raw = (json.dumps(report, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if len(raw) > MAX_REPORT_BYTES:
        raise InventoryError("inventory report exceeds byte bound")
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".native-inventory-", dir=output.parent,
                                         delete=False) as stream:
            temporary = stream.name
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, output)
    finally:
        if temporary is not None:
            os.unlink(temporary)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--configuration", choices=CONFIGURATIONS, default="Release")
    parser.add_argument("--sdk-lock", type=Path, default=ROOT / "data/dependencies/vst3-sdk-lock.json")
    parser.add_argument("--project-notices", type=Path, default=ROOT / "THIRD_PARTY_NOTICES.md")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--source-commit", help="actual caller-recorded Git commit; not binary attestation")
    source.add_argument("--source-manifest", type=Path, help="bounded source-overlay manifest to identify by bytes")
    args = parser.parse_args(argv)
    try:
        report = make_inventory(args.bundle, args.configuration, args.sdk_lock, args.project_notices,
                                args.source_commit, args.source_manifest)
        publish_report(report, args.output, args.bundle)
    except (InventoryError, OSError, UnicodeError, json.JSONDecodeError, RecursionError,
            struct.error) as error:
        print(f"Native bundle inventory error: {error}", file=sys.stderr)
        return 1
    print(f"inventoried {report['file_count']} files, {report['total_bytes']} bytes; "
          f"{report['module']['platform']} {','.join(report['module']['architectures'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
