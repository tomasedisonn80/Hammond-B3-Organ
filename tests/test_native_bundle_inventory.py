#!/usr/bin/env python3
"""SDK-free payload/transport checks; header fixtures are not executable plugins."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/native_bundle_inventory.py"
SPEC = importlib.util.spec_from_file_location("native_bundle_inventory", SCRIPT)
assert SPEC and SPEC.loader
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)
COMMIT = "1234567890abcdef1234567890abcdef12345678"
LICENSE = b"MIT fixture notice\n"
NOTICES = b"Fixture-specific notices; no project license assertion.\n"


def elf(cpu: int = 62) -> bytes:
    data = bytearray(64)
    data[:7] = b"\x7fELF\x02\x01\x01"
    struct.pack_into("<HH", data, 16, 3, cpu)
    return bytes(data)


def pe(cpu: int = 0x8664) -> bytes:
    data = bytearray(128)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 60, 64)
    data[64:68] = b"PE\0\0"
    struct.pack_into("<H", data, 68, cpu)
    struct.pack_into("<H", data, 84, 2)
    struct.pack_into("<H", data, 86, 0x2000)
    struct.pack_into("<H", data, 88, 0x20B)
    return bytes(data)


def mach(cpu: int = 0x0100000C, endian: str = "<") -> bytes:
    return struct.pack(endian + "IIIIIIII", 0xFEEDFACF, cpu, 0, 8, 0, 0, 0, 0)


def universal(wide: bool = False) -> bytes:
    width = 32 if wide else 20
    data = bytearray(256)
    data[:8] = struct.pack(">II", 0xCAFEBABF if wide else 0xCAFEBABE, 2)
    for index, (cpu, offset) in enumerate(((0x01000007, 128), (0x0100000C, 192))):
        entry = (struct.pack(">IIQQII", cpu, 0, offset, 32, 6, 0) if wide else
                 struct.pack(">IIIII", cpu, 0, offset, 32, 6))
        data[8 + index * width:8 + (index + 1) * width] = entry
        data[offset:offset + 32] = mach(cpu)
    return bytes(data)


class Fixture:
    def __init__(self, root: Path, module: str = "Contents/x86_64-linux/HammondB3.so",
                 data: bytes | None = None):
        self.root = root
        self.bundle = root / "HammondB3.vst3"
        self.resources = self.bundle / "Contents/Resources"
        self.resources.mkdir(parents=True)
        self.module = self.bundle / module
        self.module.parent.mkdir(parents=True, exist_ok=True)
        self.module.write_bytes(elf() if data is None else data)
        # The actual pinned SDK writer also emits trailing commas. Preserve
        # module metadata as identified opaque bytes, not a rewritten JSON file.
        (self.resources / "moduleinfo.json").write_bytes(b'{"Name":"HammondB3",}\n')
        (self.resources / "VST3_SDK_LICENSE.txt").write_bytes(LICENSE)
        (self.resources / "THIRD_PARTY_NOTICES.md").write_bytes(NOTICES)
        self.notices = root / "source-notices.md"
        self.notices.write_bytes(NOTICES)
        self.lock = root / "sdk-lock.json"
        self.lock_value = {"schema_version": 1, "commit": "a" * 40,
                           "license": {"bytes": len(LICENSE),
                                       "sha256": hashlib.sha256(LICENSE).hexdigest()}}
        self.lock.write_text(json.dumps(self.lock_value), encoding="utf-8")

    def report(self, **changes):
        args = dict(bundle=self.bundle, configuration="Release", sdk_lock=self.lock,
                    notices=self.notices, source_commit=COMMIT)
        args.update(changes)
        return inventory.make_inventory(**args)

    def cli(self, output: Path, *extra: str):
        return subprocess.run([sys.executable, str(SCRIPT), "--bundle", str(self.bundle),
                               "--output", str(output), "--sdk-lock", str(self.lock),
                               "--project-notices", str(self.notices),
                               "--source-commit", COMMIT, *extra],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                              encoding="utf-8", timeout=30)


class NativeBundleInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.fixture = Fixture(self.root)

    def tearDown(self):
        self.temporary.cleanup()

    def test_descriptor_metadata_does_not_have_to_match_path_representation(self):
        original_fstat = os.fstat

        def descriptor(fd):
            actual = original_fstat(fd)
            fields = {name: getattr(actual, name) for name in
                      ("st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns", "st_ctime_ns")}
            fields["st_ctime_ns"] += 1234
            fields["st_mode"] ^= 0o111
            return SimpleNamespace(**fields)

        with mock.patch.object(inventory.os, "fstat", side_effect=descriptor):
            record = inventory._file_record(self.fixture.module, inventory.MAX_FILE_BYTES)
        raw = self.fixture.module.read_bytes()
        self.assertEqual(record, {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})

    def test_descriptor_identity_and_in_stream_metadata_changes_still_reject(self):
        original_fstat = os.fstat
        for field, change_on in (("st_ino", 1), ("st_size", 1), ("st_ctime_ns", 2),
                                 ("st_mtime_ns", 2), ("st_mode", 2)):
            with self.subTest(field=field, change_on=change_on):
                calls = 0

                def changed(fd):
                    nonlocal calls
                    calls += 1
                    actual = original_fstat(fd)
                    fields = {name: getattr(actual, name) for name in
                              ("st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns", "st_ctime_ns")}
                    if calls >= change_on:
                        fields[field] += 1
                    return SimpleNamespace(**fields)

                with mock.patch.object(inventory.os, "fstat", side_effect=changed):
                    with self.assertRaisesRegex(inventory.InventoryError, "file changed"):
                        inventory._file_record(self.fixture.module, inventory.MAX_FILE_BYTES)

    def test_exact_inventory_preserves_sdk_metadata_bytes(self):
        report = self.fixture.report()
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["file_count"], 4)
        self.assertEqual(report["module"], {"path": "Contents/x86_64-linux/HammondB3.so",
                                          "platform": "linux", "format": "ELF64",
                                          "architectures": ["x86_64"]})
        self.assertEqual(report["source"], {"kind": "caller-declared-git-commit", "revision": COMMIT})
        self.assertEqual(report["files"], sorted(report["files"], key=lambda item: item["path"]))
        total = 0
        for record in report["files"]:
            path = self.fixture.bundle / record["path"]
            raw = path.read_bytes()
            total += len(raw)
            self.assertEqual(record["bytes"], len(raw))
            self.assertEqual(record["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(int(record["mode_octal"], 8), path.stat().st_mode & 0o7777)
        self.assertEqual(report["total_bytes"], total)
        self.assertNotIn(str(self.root), json.dumps(report))
        self.assertEqual((self.fixture.resources / "moduleinfo.json").read_bytes(),
                         b'{"Name":"HammondB3",}\n')

    def test_supported_thin_native_headers_are_observed(self):
        cases = [("Contents/aarch64-linux/HammondB3.so", elf(183), "ELF64", "arm64"),
                 ("Contents/x86_64-win/HammondB3.vst3", pe(), "PE32+", "x86_64"),
                 ("Contents/arm64-win/HammondB3.vst3", pe(0xAA64), "PE32+", "arm64"),
                 ("Contents/MacOS/HammondB3", mach(), "Mach-O64", "arm64"),
                 ("Contents/MacOS/HammondB3", mach(0x01000007), "Mach-O64", "x86_64"),
                 ("Contents/MacOS/HammondB3", mach(0x01000007, ">"), "Mach-O64", "x86_64")]
        for index, (path, raw, format_name, architecture) in enumerate(cases):
            with self.subTest(path=path, architecture=architecture):
                fixture = Fixture(self.root / f"case{index}", path, raw)
                record = fixture.report()["module"]
                self.assertEqual(record["format"], format_name)
                self.assertEqual(record["architectures"], [architecture])

    def test_universal_macho_extent_and_architecture_checks(self):
        for wide in (False, True):
            with self.subTest(wide=wide):
                fixture = Fixture(self.root / str(wide), "Contents/MacOS/HammondB3", universal(wide))
                self.assertEqual(fixture.report()["module"]["architectures"], ["arm64", "x86_64"])
        for index, mutation in enumerate(("count", "overlap", "cpu", "alignment", "size")):
            with self.subTest(mutation=mutation):
                raw = bytearray(universal())
                if mutation == "count": struct.pack_into(">I", raw, 4, 5)
                if mutation == "overlap": struct.pack_into(">I", raw, 36, 128)
                if mutation == "cpu": struct.pack_into(">I", raw, 28, 0x01000007)
                if mutation == "alignment": struct.pack_into(">I", raw, 24, 31)
                if mutation == "size": struct.pack_into(">I", raw, 20, 10000)
                fixture = Fixture(self.root / f"badfat{index}", "Contents/MacOS/HammondB3", bytes(raw))
                with self.assertRaises(inventory.InventoryError): fixture.report()

    def test_bad_module_headers_and_platform_mismatches_reject(self):
        cases = [b"", b"not a plugin", elf()[:31], pe(), elf(1), mach(),
                 b"\x7fELF\x01\x01" + bytes(58), b"MZ" + bytes(62)]
        for index, raw in enumerate(cases):
            with self.subTest(index=index):
                self.fixture.module.write_bytes(raw)
                with self.assertRaises(inventory.InventoryError): self.fixture.report()

    def test_required_resources_and_exact_notices_are_enforced(self):
        for name in ("moduleinfo.json", "VST3_SDK_LICENSE.txt", "THIRD_PARTY_NOTICES.md"):
            path = self.fixture.resources / name
            original = path.read_bytes()
            for bad in (None, b""):
                with self.subTest(name=name, bad=bad):
                    if bad is None: path.unlink()
                    else: path.write_bytes(bad)
                    with self.assertRaises(inventory.InventoryError): self.fixture.report()
                    path.write_bytes(original)
        for name in ("VST3_SDK_LICENSE.txt", "THIRD_PARTY_NOTICES.md"):
            path = self.fixture.resources / name
            original = path.read_bytes()
            path.write_bytes(original + b"tampered")
            with self.assertRaises(inventory.InventoryError): self.fixture.report()
            path.write_bytes(original)

    def test_one_module_and_all_extra_resource_bytes_are_inventoried(self):
        extra = self.fixture.resources / "additional.txt"
        extra.write_bytes(b"retained extra payload")
        report = self.fixture.report()
        self.assertEqual(report["file_count"], 5)
        self.assertIn(extra.relative_to(self.fixture.bundle).as_posix(),
                      [record["path"] for record in report["files"]])
        other = self.fixture.bundle / "Contents/x86_64-win/HammondB3.vst3"
        other.parent.mkdir()
        other.write_bytes(pe())
        with self.assertRaises(inventory.InventoryError): self.fixture.report()
        other.unlink()
        self.fixture.module.unlink()
        with self.assertRaises(inventory.InventoryError): self.fixture.report()

    def test_lock_shape_hash_and_nonfinite_rejections(self):
        original = self.fixture.lock.read_bytes()
        cases = [b"[]", b"{", b"\xff", b'{"schema_version":1,"schema_version":1}',
                 b'{"schema_version":1,"commit":NaN}',
                 json.dumps({**self.fixture.lock_value, "schema_version": True}).encode(),
                 json.dumps({**self.fixture.lock_value, "commit": "A" * 40}).encode(),
                 json.dumps({**self.fixture.lock_value, "license": {"bytes": True, "sha256": "a" * 64}}).encode()]
        for raw in cases:
            with self.subTest(raw=raw):
                self.fixture.lock.write_bytes(raw)
                with self.assertRaises((inventory.InventoryError, ValueError, UnicodeError)):
                    self.fixture.report()
        self.fixture.lock.write_bytes(original)

    def test_source_overlay_is_identified_without_inventing_a_commit(self):
        manifest = self.root / "source-overlay.json"
        manifest.write_bytes(b'{"base_tree":"frozen","overlays":["actual files"]}\n')
        report = self.fixture.report(source_commit=None, source_manifest=manifest)
        self.assertEqual(report["source"], {"kind": "overlay-manifest-bytes", "name": manifest.name,
                                          "bytes": manifest.stat().st_size,
                                          "sha256": hashlib.sha256(manifest.read_bytes()).hexdigest()})
        for change in ({"source_commit": None}, {"source_manifest": manifest},
                       {"source_commit": "unknown"}, {"configuration": "Invented"}):
            with self.subTest(change=change):
                with self.assertRaises(inventory.InventoryError): self.fixture.report(**change)

    def test_entry_depth_path_file_total_and_metadata_bounds(self):
        cases = [("MAX_ENTRIES", 1), ("MAX_DEPTH", 1), ("MAX_PATH_BYTES", 8),
                 ("MAX_FILE_BYTES", 32), ("MAX_TOTAL_BYTES", 32), ("MAX_METADATA_BYTES", 16)]
        for constant, limit in cases:
            with self.subTest(constant=constant), mock.patch.object(inventory, constant, limit):
                with self.assertRaises(inventory.InventoryError): self.fixture.report()
        output = self.root / "too-big.json"
        with mock.patch.object(inventory, "MAX_REPORT_BYTES", 1):
            with self.assertRaises(inventory.InventoryError):
                inventory.publish_report(self.fixture.report(), output, self.fixture.bundle)
        self.assertFalse(output.exists())

    def test_symlink_files_directories_root_and_broken_outputs_reject(self):
        target = self.root / "outside.txt"
        target.write_bytes(b"outside sentinel")
        link = self.fixture.resources / "external-link"
        try:
            link.symlink_to(target)
        except OSError:
            # Windows may deny symlink creation. The portable classification
            # branch still receives a real stat result with a link mode.
            regular = link.parent.stat()
            fake = os.stat_result((0o120777, *regular[1:]))
            with mock.patch.object(Path, "lstat", return_value=fake):
                with self.assertRaises(inventory.InventoryError): inventory._regular(target, 100)
            return
        with self.assertRaises(inventory.InventoryError): self.fixture.report()
        link.unlink()
        link.symlink_to(self.fixture.bundle, target_is_directory=True)
        with self.assertRaises(inventory.InventoryError): self.fixture.report()
        link.unlink()
        alias_parent = self.root / "alias"
        alias_parent.mkdir()
        alias = alias_parent / "HammondB3.vst3"
        alias.symlink_to(self.fixture.bundle, target_is_directory=True)
        with self.assertRaises(inventory.InventoryError): self.fixture.report(bundle=alias)
        output = self.root / "broken.json"
        output.symlink_to(self.root / "missing")
        with self.assertRaises(inventory.InventoryError):
            inventory.publish_report(self.fixture.report(), output, self.fixture.bundle)
        self.assertTrue(output.is_symlink())
        self.assertEqual(target.read_bytes(), b"outside sentinel")

    def test_special_file_is_rejected_without_reading_it(self):
        if hasattr(os, "mkfifo"):
            special = self.fixture.resources / "named-pipe"
            os.mkfifo(special)
            with self.assertRaises(inventory.InventoryError): self.fixture.report()
        else:
            original = self.fixture.module.stat()
            fake = os.stat_result((0o010600, *original[1:]))
            with mock.patch.object(Path, "lstat", return_value=fake):
                with self.assertRaises(inventory.InventoryError): inventory._regular(self.fixture.module, 100)

    def test_case_collisions_are_not_silently_normalized(self):
        first = self.fixture.resources / "Extra.txt"
        second = self.fixture.resources / "extra.txt"
        first.write_bytes(b"first")
        second.write_bytes(b"second")
        if first.samefile(second):
            self.assertEqual(first.read_bytes(), b"second")
        else:
            with self.assertRaises(inventory.InventoryError): self.fixture.report()

    def test_publication_is_complete_and_never_overwrites(self):
        output = self.root / "inventory.json"
        report = self.fixture.report()
        inventory.publish_report(report, output, self.fixture.bundle)
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), report)
        before = output.read_bytes()
        with self.assertRaises(inventory.InventoryError):
            inventory.publish_report(report, output, self.fixture.bundle)
        self.assertEqual(output.read_bytes(), before)
        with self.assertRaises(inventory.InventoryError):
            inventory.publish_report(report, self.fixture.bundle / "inventory.json", self.fixture.bundle)
        with self.assertRaises(inventory.InventoryError):
            inventory.publish_report(report, self.root / "absent" / "out.json", self.fixture.bundle)
        self.assertEqual(list(self.root.glob(".native-inventory-*")), [])

    def test_publication_failure_and_race_leave_no_partial_file(self):
        report = self.fixture.report()
        output = self.root / "race.json"
        with mock.patch.object(inventory.os, "link", side_effect=OSError("synthetic link failure")):
            with self.assertRaises(OSError): inventory.publish_report(report, output, self.fixture.bundle)
        self.assertFalse(output.exists())
        self.assertEqual(list(self.root.glob(".native-inventory-*")), [])

        def publish():
            try:
                inventory.publish_report(report, output, self.fixture.bundle)
                return True
            except (OSError, inventory.InventoryError):
                return False

        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(executor.map(lambda _: publish(), range(2)))
        self.assertEqual(sum(outcomes), 1)
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), report)
        self.assertEqual(list(self.root.glob(".native-inventory-*")), [])

    def test_actual_cli_unicode_paths_and_preserved_failure_destination(self):
        fixture = Fixture(self.root / "unicode-\u00e9-\u4e2d-\U0001f3b9")
        output = fixture.root / "inventory-\u65e5.json"
        result = fixture.cli(output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("linux x86_64", result.stdout)
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), fixture.report())
        before = output.read_bytes()
        result = fixture.cli(output)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(output.read_bytes(), before)
        fixture.module.write_bytes(b"broken")
        rejected = fixture.root / "rejected.json"
        result = fixture.cli(rejected)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(rejected.exists())

    def test_copy_preserves_inventory_and_native_permission_facts(self):
        self.fixture.module.chmod(0o755)
        before = self.fixture.report()
        copied = self.root / "copied" / "HammondB3.vst3"
        shutil.copytree(self.fixture.bundle, copied, copy_function=shutil.copy2)
        self.assertEqual(self.fixture.report(bundle=copied), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
