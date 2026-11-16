#!/usr/bin/env python3
"""A47 bounded independent admission checks for the Windows identity repair.

This review script is not a replacement for the registered I/O/install/study
tests or repaired Windows execution. It uses real temporary files on this host,
with explicit metadata and syscall faults, and retains a source-bound receipt.
"""

from __future__ import annotations

import ast
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import errno
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import stat
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[4]
BASE = "af2b74760ee195c9497b314a1a29172f5238dd44"
SOURCE = "tools/contact_switching_io.py"
TESTS = "tests/test_contact_switching_io.py"
sys.path.insert(0, str(ROOT / "tools"))
import contact_switching_io as candidate
import contact_switching_reference as command

REAL_OPEN, REAL_FSTAT, REAL_STAT = os.open, os.fstat, os.stat
FIELDS = ("st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns", "st_ctime_ns")
PRIOR = b"A47 earlier report\x00\xff\n"
CASES = []


def digest(data):
    return hashlib.sha256(data).hexdigest()


def metadata(information, **changes):
    values = {name: getattr(information, name) for name in dir(information)
              if name.startswith("st_")}
    values.update(changes)
    return SimpleNamespace(**values)


def historical(path):
    return subprocess.check_output(["git", "show", BASE + ":" + path], cwd=ROOT)


class RepairChecks(unittest.TestCase):
    def setUp(self):
        self.owner = tempfile.TemporaryDirectory(prefix="contact-a47-")
        self.addCleanup(self.owner.cleanup)
        self.directory = Path(self.owner.name)
        self.source = self.directory / "input.json"
        # Frozen synthetic input; metadata faults do not alter these bytes.
        self.data = (ROOT / "data/contact-switching/reference-v1/F00-48000-v1.json").read_bytes()
        self.source.write_bytes(self.data)
        self.destination = self.directory / "report.json"
        self.destination.write_bytes(PRIOR)
        self.unrelated = self.directory / ".contact-switching-not-owned.tmp"
        self.unrelated.write_bytes(b"unrelated")
        info = REAL_STAT(self.source)
        self.identity = (info.st_dev, info.st_ino)
        self.report = candidate.build_report(candidate.parse_input(self.data), 32)

    def assert_outputs(self, existed=True):
        self.assertEqual(self.destination.exists(), existed)
        if existed:
            self.assertEqual(self.destination.read_bytes(), PRIOR)
        self.assertEqual(self.source.read_bytes(), self.data)
        self.assertEqual(self.unrelated.read_bytes(), b"unrelated")
        self.assertEqual(set(self.directory.glob(".contact-switching-*.tmp")), {self.unrelated})

    def assert_closed(self, descriptors):
        self.assertTrue(descriptors)
        for descriptor in set(descriptors):
            try:
                REAL_FSTAT(descriptor)
            except OSError as error:
                self.assertEqual(error.errno, errno.EBADF)
            else:
                os.close(descriptor)
                self.fail("candidate left an owned descriptor open")

    def test_late_metadata_mutations_preserve_absent_and_existing_output(self):
        # Change only one field after the temporary is fsynced. Both full
        # metadata domains must still reject at the last publication recheck.
        for domain in ("path", "descriptor"):
            for field in FIELDS:
                for existed in (False, True):
                    with self.subTest(domain=domain, field=field, existed=existed):
                        if existed:
                            self.destination.write_bytes(PRIOR)
                        else:
                            self.destination.unlink(missing_ok=True)
                        changed = False
                        opened = []

                        def mutate(information):
                            if changed:
                                value = getattr(information, field)
                                value = value ^ stat.S_IXUSR if field == "st_mode" else value + 1
                                return metadata(information, **{field: value})
                            return information

                        def by_descriptor(descriptor):
                            information = REAL_FSTAT(descriptor)
                            if (information.st_dev, information.st_ino) == self.identity:
                                # Stable API disagreement throughout this check.
                                information = metadata(information, st_ctime_ns=information.st_ctime_ns + 10**9)
                                if domain == "descriptor":
                                    information = mutate(information)
                            return information

                        def by_path(path, *args, **kwargs):
                            information = REAL_STAT(path, *args, **kwargs)
                            if domain == "path" and not isinstance(path, int) and Path(path) == self.source:
                                information = mutate(information)
                            return information

                        def record_open(*args, **kwargs):
                            descriptor = REAL_OPEN(*args, **kwargs)
                            opened.append(descriptor)
                            return descriptor

                        def after_fsync(descriptor):
                            nonlocal changed
                            os_fsync(descriptor)
                            changed = True

                        os_fsync = os.fsync
                        with patch.object(os, "fstat", side_effect=by_descriptor), \
                                patch.object(os, "stat", side_effect=by_path), \
                                patch.object(os, "open", side_effect=record_open), \
                                patch.object(os, "fsync", side_effect=after_fsync):
                            plan = candidate.preflight_paths(self.source, self.destination)
                            with self.assertRaises(ValueError):
                                candidate.atomic_write_report(plan, self.report)
                        self.assertTrue(changed, "fault did not reach the late publication boundary")
                        self.assert_closed(opened)
                        self.assert_outputs(existed)
                        CASES.append({"boundary": "after temporary fsync", "domain": domain,
                                      "only_mutated_field": field, "prior_output": existed,
                                      "rejected": True, "output_preserved": True,
                                      "owned_temporaries_removed": True, "descriptors_closed": True})

    def test_same_identity_descriptor_type_and_size_reject_before_read(self):
        for operation in ("preflight", "load"):
            for fault in ("special file", "oversize"):
                with self.subTest(operation=operation, fault=fault):
                    opened = []

                    def record_open(*args, **kwargs):
                        descriptor = REAL_OPEN(*args, **kwargs)
                        opened.append(descriptor)
                        return descriptor

                    def by_descriptor(descriptor):
                        information = REAL_FSTAT(descriptor)
                        if fault == "special file":
                            return metadata(information, st_mode=stat.S_IFIFO | 0o600)
                        return metadata(information, st_size=262145)

                    with patch.object(os, "open", side_effect=record_open), \
                            patch.object(os, "fstat", side_effect=by_descriptor), \
                            patch.object(candidate, "parse_input") as parse, \
                            patch.object(candidate.tempfile, "mkstemp") as create, \
                            self.assertRaisesRegex(ValueError, "regular file|256 KiB"):
                        if operation == "preflight":
                            candidate.preflight_paths(self.source, self.destination)
                        else:
                            candidate.load_input(self.source)
                    parse.assert_not_called()
                    create.assert_not_called()
                    self.assert_closed(opened)
                    self.assert_outputs()
                    CASES.append({"boundary": operation, "fault": fault, "same_device_inode": True,
                                  "rejected_before_parse_and_output": True, "descriptors_closed": True})

    def test_path_snapshot_error_closes_preflight_descriptor(self):
        opened = []

        def record_open(*args, **kwargs):
            descriptor = REAL_OPEN(*args, **kwargs)
            opened.append(descriptor)
            return descriptor

        def by_path(path, *args, **kwargs):
            if opened and not isinstance(path, int) and Path(path) == self.source:
                raise OSError("A47 path snapshot disappeared")
            return REAL_STAT(path, *args, **kwargs)

        with patch.object(os, "open", side_effect=record_open), \
                patch.object(os, "stat", side_effect=by_path), \
                self.assertRaisesRegex(OSError, "A47 path snapshot"):
            candidate.preflight_paths(self.source, self.destination)
        self.assert_closed(opened)
        self.assert_outputs()
        CASES.append({"boundary": "path snapshot while preflight descriptor open",
                      "fault": "OSError", "descriptors_closed": True, "output_preserved": True})

    def test_interrupted_stream_construction_closes_load_descriptor(self):
        opened = []

        def record_open(*args, **kwargs):
            descriptor = REAL_OPEN(*args, **kwargs)
            opened.append(descriptor)
            return descriptor

        with patch.object(os, "open", side_effect=record_open), \
                patch.object(os, "fdopen", side_effect=KeyboardInterrupt("A47 interrupted wrapper")), \
                self.assertRaises(KeyboardInterrupt):
            candidate.load_input(self.source)
        self.assert_closed(opened)
        self.assert_outputs()
        CASES.append({"boundary": "load fdopen construction", "fault": "KeyboardInterrupt",
                      "descriptors_closed": True, "output_preserved": True})

    def test_cli_stable_api_divergence_keeps_current_source_hash(self):
        source_info = REAL_STAT(self.source)

        def by_path(path, *args, **kwargs):
            information = REAL_STAT(path, *args, **kwargs)
            if not isinstance(path, int) and Path(path) == self.source:
                return metadata(information, st_mode=information.st_mode | 0o111)
            return information

        def by_descriptor(descriptor):
            information = REAL_FSTAT(descriptor)
            if (information.st_dev, information.st_ino) == self.identity:
                return metadata(information, st_ctime_ns=information.st_ctime_ns + 10**9)
            return information

        out, err = io.StringIO(), io.StringIO()
        with patch.object(os, "stat", side_effect=by_path), \
                patch.object(os, "fstat", side_effect=by_descriptor), \
                redirect_stdout(out), redirect_stderr(err):
            result = command.main(["--input", str(self.source), "--factor", "32",
                                   "--output", str(self.destination)])
        self.assertEqual((result, out.getvalue(), err.getvalue()), (0, "", ""))
        report = json.loads(self.destination.read_bytes())
        self.assertEqual(report["input_sha256"], digest(self.data))
        self.assertEqual(report["implementation_sha256"][SOURCE], digest((ROOT / SOURCE).read_bytes()))
        self.assertEqual(report["samples"], self.report["samples"])
        self.assertEqual(REAL_STAT(self.source).st_mtime_ns, source_info.st_mtime_ns)
        self.assertEqual(set(self.directory.glob(".contact-switching-*.tmp")), {self.unrelated})
        CASES.append({"boundary": "complete CLI", "path_execute_bits": "added 0111",
                      "descriptor_ctime_offset_ns": 10**9, "result": "success",
                      "source_hash_current": True, "input_hash_exact": True,
                      "samples_equal_unmocked_same_fixture": True})


def static_audit():
    before = ast.parse(historical(SOURCE))
    after = ast.parse((ROOT / SOURCE).read_bytes())

    def nodes(module):
        return {node.name: ast.dump(node, include_attributes=False) for node in module.body
                if isinstance(node, (ast.FunctionDef, ast.ClassDef))}

    old, new = nodes(before), nodes(after)
    changed = sorted(name for name in old if old[name] != new.get(name))
    added = sorted(set(new) - set(old))
    assert changed == ["OutputPlan", "load_input", "preflight_paths"], changed
    assert added == ["_preflight_input_signature"], added
    nondefinitions = lambda module: [ast.dump(node, include_attributes=False) for node in module.body
                                    if not isinstance(node, (ast.FunctionDef, ast.ClassDef))]
    assert nondefinitions(before) == nondefinitions(after)
    old_tests, new_tests = ast.parse(historical(TESTS)), ast.parse((ROOT / TESTS).read_bytes())

    def methods(module):
        return {node.name + "." + method.name: ast.dump(method, include_attributes=False)
                for node in module.body if isinstance(node, ast.ClassDef)
                for method in node.body if isinstance(method, ast.FunctionDef)}

    old_methods, new_methods = methods(old_tests), methods(new_tests)
    assert all(new_methods.get(name) == code for name, code in old_methods.items())
    new_methods_only = sorted(set(new_methods) - set(old_methods))
    assert len(new_methods_only) == 8
    prior = json.loads((ROOT / "docs/development/2026-11-15-streaming-continuation/reports/A30-compatibility.json").read_text())
    payload = prior["contact_reference_component"]["install_rules_and_payload_sha256"]
    observed = {path: digest((ROOT / path).read_bytes()) for path in payload}
    unequal = sorted(path for path, value in payload.items() if observed[path] != value)
    assert unequal == [SOURCE], unequal
    assert len(payload) == 49  # 48 unchanged names plus the installation module.
    assert (ROOT / "cmake/InstallContactReferenceTools.cmake").read_bytes() == historical("cmake/InstallContactReferenceTools.cmake")
    return {"changed_definitions": changed, "added_definitions": added,
            "all_other_function_and_class_asts_unchanged": True,
            "module_constants_and_imports_unchanged": True,
            "existing_class_methods_unchanged": len(old_methods),
            "existing_test_methods_unchanged": sum(name.split(".", 1)[1].startswith("test_")
                                                   for name in old_methods),
            "added_test_methods": new_methods_only,
            "payload_name_count": 48, "payload_name_inventory_unchanged": True,
            "payload_and_installer_sha256": observed,
            "different_from_A30_historical_hashes": unequal,
            "previous_io_sha256": payload[SOURCE]}


if __name__ == "__main__":
    started = time.perf_counter()
    hashes_before = {path: digest((ROOT / path).read_bytes()) for path in (SOURCE, TESTS)}
    audit = static_audit()
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RepairChecks))
    hashes_after = {path: digest((ROOT / path).read_bytes()) for path in (SOURCE, TESTS)}
    receipt = {"schema_version": 1, "reviewer": "/root/w08_a47", "observed_utc": datetime.now(timezone.utc).isoformat(),
               "cwd": str(ROOT), "base_commit": BASE, "python": sys.version, "python_executable": sys.executable,
               "platform": platform.platform(), "scope": "local real filesystem with explicit metadata/syscall faults; no Windows runtime claim",
               "source_sha256_before": hashes_before, "source_sha256_after": hashes_after,
               "sources_stable": hashes_before == hashes_after,
               "review_script_sha256": digest(Path(__file__).read_bytes()),
               "test_methods": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
               "skips": len(result.skipped), "case_count": len(CASES), "cases": CASES,
               "wall_seconds": time.perf_counter() - started, "static_audit": audit, "unittest_log": log.getvalue()}
    print(json.dumps(receipt, indent=2, sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() and hashes_before == hashes_after else 1)
