#!/usr/bin/env python3
"""Exercise explicit local bundle staging and load the relocated real VST3.

Registered only for HAMMOND_BUILD_VST3=ON. Inputs are mandatory; missing build
products fail instead of silently skipping native qualification.
"""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
REQUIRED_RESOURCES = (
    Path("Contents/Resources/moduleinfo.json"),
    Path("Contents/Resources/VST3_SDK_LICENSE.txt"),
    Path("Contents/Resources/THIRD_PARTY_NOTICES.md"),
)


def required_path(variable, *, directory=False):
    value = os.environ.get(variable)
    path = Path(value) if value else None
    if path is None or not (path.is_dir() if directory else path.is_file()):
        raise RuntimeError(f"Missing native install prerequisite {variable}={value!r}; "
                           "build HammondB3 and test_native_abi for the selected configuration.")
    return path.resolve()


def payload_hashes(root):
    """Hash opaque bytes, including SDK metadata whose JSON permits trailing commas."""
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise AssertionError(f"Staged payload must not depend on a symbolic link: {path}")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif not path.is_dir():
            raise AssertionError(f"Unexpected non-file payload entry: {path}")
    return result


def entry_paths(root):
    return {path.relative_to(root).as_posix() for path in root.rglob("*")}


class NativeInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cmake = required_path("HAMMOND_TEST_CMAKE")
        cls.build = required_path("HAMMOND_TEST_BUILD_DIR", directory=True)
        cls.bundle = required_path("HAMMOND_TEST_VST3_BUNDLE", directory=True)
        cls.module = required_path("HAMMOND_TEST_NATIVE_MODULE")
        cls.abi = required_path("HAMMOND_TEST_NATIVE_ABI")
        cls.profile = required_path("HAMMOND_TEST_PROFILE")
        cls.configuration = os.environ.get("HAMMOND_TEST_CONFIG", "")
        libdir = os.environ.get("HAMMOND_INSTALL_LIBDIR")
        cls.libdir = Path(libdir) if libdir else None
        if cls.libdir is None or cls.libdir.is_absolute() or ".." in cls.libdir.parts:
            raise RuntimeError("HAMMOND_INSTALL_LIBDIR must be a nonempty relative directory")
        cls.module_relative = cls.module.relative_to(cls.bundle)
        cls.bundle_relative = cls.libdir / "vst3" / cls.bundle.name
        if cls.bundle.name != "HammondB3.vst3":
            raise RuntimeError(f"Unexpected actual SDK bundle: {cls.bundle}")
        cls.hashes = payload_hashes(cls.bundle)
        cls.entries = entry_paths(cls.bundle)
        for relative in (*REQUIRED_RESOURCES, cls.module_relative):
            if relative.as_posix() not in cls.hashes or (cls.bundle / relative).stat().st_size == 0:
                raise RuntimeError(f"Incomplete actual native bundle: {relative}")
        if not (cls.build / "cmake_install.cmake").is_file():
            raise RuntimeError("Missing native build install script; configure again")

    def invoke(self, command, cwd, environment):
        return subprocess.run(list(map(str, command)), cwd=cwd, env=environment,
                              capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=180, check=False)

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def install_command(self, build, prefix):
        command = [self.cmake, "--install", build, "--component", "NativeVST3", "--prefix", prefix]
        if self.configuration:
            command.extend(("--config", self.configuration))
        return command

    @staticmethod
    def clean_environment():
        environment = {name: value for name, value in os.environ.items()
                       if not name.upper().startswith("HAMMOND_")}
        environment.pop("DESTDIR", None)
        environment.pop("CMAKE_INSTALL_MODE", None)
        return environment

    def test_install_move_and_load(self):
        with tempfile.TemporaryDirectory(prefix="hammond native install ") as temporary:
            work = Path(temporary)
            prefix, relocated, unrelated = work / "original prefix", work / "moved prefix", work / "unrelated cwd"
            prefix.mkdir()
            unrelated.mkdir()
            (prefix / "unrelated.txt").write_bytes(b"existing prefix contents\n")
            other = prefix / self.libdir / "vst3" / "OtherPlugin.vst3" / "keep.txt"
            other.parent.mkdir(parents=True)
            other.write_bytes(b"unrelated plugin must survive\n")
            existing = payload_hashes(prefix)
            environment = self.clean_environment()
            self.assert_success(self.invoke(self.install_command(self.build, prefix), unrelated, environment))
            installed = prefix / self.bundle_relative
            self.assertEqual(payload_hashes(installed), self.hashes)
            self.assertEqual(entry_paths(installed), self.entries)
            expected = {**existing, **{(self.bundle_relative / name).as_posix(): value
                                      for name, value in self.hashes.items()}}
            self.assertEqual(payload_hashes(prefix), expected, "NativeVST3 installed extra/missing files")
            repeated = self.invoke(self.install_command(self.build, prefix), unrelated, environment)
            self.assertNotEqual(repeated.returncode, 0)
            self.assertIn("destination bundle already exists", repeated.stderr)
            self.assertEqual(payload_hashes(prefix), expected, "Refused reinstall changed existing data")

            prefix.rename(relocated)
            self.assertFalse(prefix.exists())
            relocated_bundle = relocated / self.bundle_relative
            self.assertEqual(payload_hashes(relocated), expected)
            self.assertEqual(entry_paths(relocated_bundle), self.entries)
            # The harness is a build/test tool, not installed payload. Its explicit
            # reference profile is copied away from the build tree for this run.
            profile = unrelated / "reference nominal.b3p"
            shutil.copyfile(self.profile, profile)
            result = self.invoke([self.abi, relocated_bundle, profile], unrelated, environment)
            self.assert_success(result)
            report = json.loads(result.stdout)
            self.assertEqual(report["suite"], "native-abi-v1")
            self.assertGreater(report["compared_frames"], 200000)
            self.assertGreater(report["audible_frames"], 0)
            self.assertEqual(report["maximum_audio_error"], 0)
            self.assertEqual(payload_hashes(relocated), expected, "Native load changed staged bundle")
            self.assertEqual(entry_paths(relocated_bundle), self.entries)
            self.assertEqual(payload_hashes(self.bundle), self.hashes, "Install changed built bundle")
            print(json.dumps({"suite": "native-install-v1", "payload_files": len(self.hashes),
                              "bundle_sha256": self.hashes, "relocated_abi": report}, sort_keys=True))

    def test_preflight_rejects_incomplete_bundle_without_mutating_prefix(self):
        # Exercise the actual module's install rules against a private copy of
        # built bundle bytes; never damage inputs shared with parallel native tests.
        with tempfile.TemporaryDirectory(prefix="hammond native preflight ") as temporary:
            work = Path(temporary)
            source, build, prefix = work / "source", work / "build", work / "prefix"
            source.mkdir()
            prefix.mkdir()
            (prefix / "unrelated.txt").write_bytes(b"retain existing data\n")
            fixture = source / self.bundle.name
            module = fixture / self.module_relative
            cmake_script = (
                "cmake_minimum_required(VERSION 3.25)\n"
                "project(NativeInstallContract LANGUAGES NONE)\n"
                "set(HAMMOND_BUILD_VST3 ON)\n"
                f"set(CMAKE_INSTALL_LIBDIR [=[{self.libdir.as_posix()}]=] CACHE PATH \"\")\n"
                "add_library(HammondB3 MODULE IMPORTED)\n"
                f"set_property(TARGET HammondB3 PROPERTY IMPORTED_LOCATION [=[{module.as_posix()}]=])\n"
                f"set_property(TARGET HammondB3 PROPERTY SMTG_PLUGIN_PACKAGE_PATH [=[{fixture.as_posix()}]=])\n"
                f"include([=[{(ROOT / 'cmake/InstallHammondTools.cmake').as_posix()}]=])\n")
            (source / "CMakeLists.txt").write_text(cmake_script, encoding="utf-8")
            environment = self.clean_environment()
            self.assert_success(self.invoke([self.cmake, "-S", source, "-B", build], work, environment))
            def snapshot():
                return payload_hashes(prefix), entry_paths(prefix)

            before = snapshot()
            install = self.install_command(build, prefix)
            # Explicit component opt-in: an unqualified install does not stage native files.
            self.assert_success(self.invoke([self.cmake, "--install", build, "--prefix", prefix],
                                            work, environment))
            self.assertEqual(snapshot(), before)
            unbuilt = self.invoke(install, work, environment)
            self.assertNotEqual(unbuilt.returncode, 0)
            self.assertIn("complete built HammondB3.vst3 bundle", unbuilt.stderr)
            self.assertEqual(snapshot(), before)
            shutil.copytree(self.bundle, fixture)
            required = [self.module_relative, *REQUIRED_RESOURCES]
            if (fixture / "Contents/Info.plist").is_file():
                required.append(Path("Contents/Info.plist"))
            for relative in required:
                with self.subTest(missing=str(relative)):
                    missing = fixture / relative
                    held = missing.with_name(missing.name + ".held")
                    missing.rename(held)
                    try:
                        result = self.invoke(install, work, environment)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn("NativeVST3 missing required bundle file", result.stderr)
                        self.assertIn(missing.name, result.stderr)
                        self.assertEqual(snapshot(), before)
                    finally:
                        held.rename(missing)
            license_file = fixture / REQUIRED_RESOURCES[1]
            license_bytes = license_file.read_bytes()
            try:
                license_file.write_bytes(b"")
                empty = self.invoke(install, work, environment)
                self.assertNotEqual(empty.returncode, 0)
                self.assertIn("bundle file is empty", empty.stderr)
                self.assertEqual(snapshot(), before)
            finally:
                license_file.write_bytes(license_bytes)
            for invalid in ("../escape", str(work / "absolute destination"), "..\\escape", ""):
                with self.subTest(libdir=invalid):
                    result = self.invoke([self.cmake, "-S", source, "-B", build,
                                          f"-DCMAKE_INSTALL_LIBDIR:PATH={invalid}"], work, environment)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("nonempty relative", result.stderr)
                    self.assertEqual(snapshot(), before)


if __name__ == "__main__":
    unittest.main()
