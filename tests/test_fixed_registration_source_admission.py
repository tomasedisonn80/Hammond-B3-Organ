#!/usr/bin/env python3
"""Require the fixed-data CLI to execute its current adjacent admission source.

The two cache modes are constructed with Python's public py_compile API. A
separate ordinary import first proves each cache really contains an older
compiler; the actual generator must then follow current source bytes. All
mutations and output publication happen in isolated temporary directories.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import py_compile
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
INPUTS = (
    "data/registrations/atlas-chapel-nominal-v1.json",
    "data/registrations/review-a-chapel.csv",
    "data/registrations/review-b-chapel.csv",
)
VALID_SOURCE = (ROOT / "tools/compile_chapel_presets.py").read_bytes()
INVALID_SOURCE = VALID_SOURCE.replace(b'"427866244",', b'"427866243",', 1)
HEADER_SHA256 = "66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6"
SENTINEL = b"previous generated output must survive\x00\xff\n"


class FixedRegistrationSourceAdmission(unittest.TestCase):
    invocations = 0

    def run_python(self, arguments: list[str], directory: Path) -> subprocess.CompletedProcess:
        environment = dict(os.environ)
        for key in ("PYTHONPATH", "PYTHONPYCACHEPREFIX", "PYTHONOPTIMIZE"):
            environment.pop(key, None)
        self.__class__.invocations += 1
        return subprocess.run([sys.executable, "-B", *arguments], cwd=directory,
                              env=environment, capture_output=True, check=False, timeout=10)

    @classmethod
    def tearDownClass(cls) -> None:
        print(f"Fixed admission-source subprocesses: {cls.invocations}", flush=True)

    def test_current_source_wins_over_timestamp_and_unchecked_hash_bytecode(self) -> None:
        self.assertNotEqual(VALID_SOURCE, INVALID_SOURCE)
        self.assertEqual(len(VALID_SOURCE), len(INVALID_SOURCE))
        for mode in (py_compile.PycInvalidationMode.TIMESTAMP,
                     py_compile.PycInvalidationMode.UNCHECKED_HASH):
            for current_valid in (False, True):
                with self.subTest(mode=mode.name, current_valid=current_valid):
                    with tempfile.TemporaryDirectory(prefix="fixed-source-admission-") as name:
                        directory = Path(name)
                        generator = directory / "compile_fixed_registrations.py"
                        helper = directory / "compile_chapel_presets.py"
                        shutil.copyfile(ROOT / "tools/compile_fixed_registrations.py", generator)
                        paths = []
                        for index, relative in enumerate(INPUTS):
                            path = directory / f"input-{index}"
                            shutil.copyfile(ROOT / relative, path)
                            paths.append(path)
                        original_inputs = tuple(path.read_bytes() for path in paths)

                        # Quarter/three-quarter timestamps avoid floating-point
                        # rounding over the integer-second boundary. Python's
                        # timestamp cache deliberately ignores the newer fraction.
                        second = int(time.time()) - 120
                        old_ns = second * 1_000_000_000 + 250_000_000
                        new_ns = second * 1_000_000_000 + 750_000_000
                        cached = INVALID_SOURCE if current_valid else VALID_SOURCE
                        current = VALID_SOURCE if current_valid else INVALID_SOURCE
                        helper.write_bytes(cached)
                        os.utime(helper, ns=(old_ns, old_ns))
                        cache_directory = directory / "__pycache__"
                        cache_directory.mkdir()
                        cache = cache_directory / (
                            f"compile_chapel_presets.{sys.implementation.cache_tag}.pyc")
                        py_compile.compile(str(helper), cfile=str(cache), doraise=True,
                                           optimize=0, invalidation_mode=mode)
                        cache_bytes = cache.read_bytes()
                        flags = struct.unpack("<I", cache_bytes[4:8])[0]
                        self.assertEqual(flags, 0 if mode.name == "TIMESTAMP" else 1)
                        if mode.name == "TIMESTAMP":
                            self.assertEqual(struct.unpack("<I", cache_bytes[8:12])[0], second)
                        helper.write_bytes(current)
                        os.utime(helper, ns=(new_ns, new_ns))
                        self.assertEqual(int(helper.stat().st_mtime), second)

                        control = self.run_python([
                            "-c", "import compile_chapel_presets as c; print(c.LOWER_TAPS[-1])"
                        ], directory)
                        self.assertEqual(control.returncode, 0, control.stderr)
                        self.assertEqual(control.stdout.strip(),
                                         b"427866243" if current_valid else b"427866244")
                        self.assertEqual(control.stderr, b"")

                        output = directory / "FixedRegistrationData.h"
                        output.write_bytes(SENTINEL)
                        result = self.run_python([
                            str(generator), "--input", str(paths[0]),
                            "--review-a", str(paths[1]), "--review-b", str(paths[2]),
                            "--output", str(output),
                        ], directory)
                        self.assertEqual(result.stdout, b"")
                        if current_valid:
                            self.assertEqual(result.returncode, 0, result.stderr)
                            self.assertEqual(result.stderr, b"")
                            self.assertEqual(hashlib.sha256(output.read_bytes()).hexdigest(),
                                             HEADER_SHA256)
                        else:
                            self.assertEqual(result.returncode, 1, result.stderr)
                            self.assertIn(b"authoring.registrations[17].drawbars", result.stderr)
                            self.assertIn(b"427866243", result.stderr)
                            self.assertNotIn(b"Traceback", result.stderr)
                            self.assertEqual(output.read_bytes(), SENTINEL)
                        self.assertEqual(helper.read_bytes(), current)
                        self.assertEqual(cache.read_bytes(), cache_bytes)
                        self.assertEqual(tuple(path.read_bytes() for path in paths), original_inputs)
                        self.assertFalse(list(directory.glob(".chapel-catalog-*.tmp")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
