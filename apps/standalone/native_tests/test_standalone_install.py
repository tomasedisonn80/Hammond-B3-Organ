#!/usr/bin/env python3
"""Require a real built app, stage its component, move it, and exercise SDL.

Registered explicitly only for HAMMOND_BUILD_STANDALONE=ON. Destructive input
probes use private copies and the real install module; shared products survive.
"""

import hashlib
import json
import ntpath
import os
from pathlib import Path
import shutil
import stat
import struct
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
SOURCE_FILES = {
    "STANDALONE_INSTALL.md": Path("docs/STANDALONE_INSTALL.md"),
    "STANDALONE_APP.md": Path("docs/STANDALONE_APP.md"),
    "STANDALONE_MODEL.md": Path("docs/STANDALONE_MODEL.md"),
    "THIRD_PARTY_NOTICES.md": Path("THIRD_PARTY_NOTICES.md"),
    "LICENSE-DejaVu.txt": Path("assets/standalone/fonts/LICENSE-DejaVu.txt"),
    "sdl2-lock.json": Path("data/dependencies/sdl2-lock.json"),
    "font-source-manifest.json": Path("assets/standalone/fonts/source-manifest.json"),
}


def required_path(variable, *, directory=False):
    value = os.environ.get(variable)
    path = Path(value) if value else None
    if path is None or not (path.is_dir() if directory else path.is_file()):
        raise RuntimeError(f"Missing standalone install prerequisite {variable}={value!r}; "
                           "configure and build hammond_standalone for the selected configuration.")
    return path.resolve()


def relative_directory(variable):
    value = os.environ.get(variable, "").replace("\\", "/")
    path = Path(value)
    if not value or path.is_absolute() or ntpath.splitdrive(value)[0] or ".." in path.parts or ";" in value:
        raise RuntimeError(f"{variable} must be a nonempty relative directory without parent traversal")
    return path


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_state(root):
    """Capture files, empty directories and dangling symlinks without following them."""
    if not root.exists():
        return {}
    result = {}
    for path in sorted(root.rglob("*")):
        mode = path.lstat().st_mode
        relative = path.relative_to(root).as_posix()
        if stat.S_ISLNK(mode):
            result[relative] = ("symlink", os.readlink(path))
        elif stat.S_ISREG(mode):
            result[relative] = ("file", sha256(path))
        elif stat.S_ISDIR(mode):
            result[relative] = ("directory",)
        else:
            result[relative] = ("special", stat.S_IFMT(mode))
    return result


def expected_tree(files):
    result = {name: ("file", digest) for name, digest in files.items()}
    for name in files:
        for parent in Path(name).parents:
            if parent != Path("."):
                result[parent.as_posix()] = ("directory",)
    return result


def cmake_literal(value):
    value = str(value).replace("\\", "/")
    if "]=]" in value:
        raise ValueError("Unsupported CMake fixture path delimiter")
    return f"[=[{value}]=]"


class StandaloneInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cmake = required_path("HAMMOND_TEST_CMAKE")
        cls.build = required_path("HAMMOND_TEST_BUILD_DIR", directory=True)
        cls.executable = required_path("HAMMOND_STANDALONE_EXECUTABLE")
        cls.sdl = required_path("HAMMOND_SDL2_ROOT", directory=True)
        cls.configuration = os.environ.get("HAMMOND_TEST_CONFIG", "")
        cls.bindir = relative_directory("HAMMOND_INSTALL_BINDIR")
        cls.datadir = relative_directory("HAMMOND_INSTALL_DATADIR")
        cls.metadata = {name: ROOT / relative for name, relative in SOURCE_FILES.items()}
        cls.metadata["LICENSE-SDL2.txt"] = cls.sdl / "LICENSE.txt"
        for path in (cls.executable, *cls.metadata.values()):
            if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
                raise RuntimeError(f"Missing/nonregular standalone input: {path}")
        cls.source_hashes = {name: sha256(path) for name, path in cls.metadata.items()}
        cls.binary_hash = sha256(cls.executable)
        cls.lock = json.loads(cls.metadata["sdl2-lock.json"].read_text(encoding="utf-8"))
        cls.fonts = json.loads(cls.metadata["font-source-manifest.json"].read_text(encoding="utf-8"))
        if cls.source_hashes["LICENSE-SDL2.txt"] != cls.lock["license"]["sha256"]:
            raise RuntimeError("SDL2 license does not match its lock")
        if cls.source_hashes["LICENSE-DejaVu.txt"] != cls.fonts["license"]["sha256"]:
            raise RuntimeError("Font license does not match its manifest")
        authoring = json.loads((ROOT / "data/profiles/nominal-unmeasured-v1.json").read_text(encoding="utf-8"))
        canonical = json.dumps(authoring, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=False, allow_nan=False).encode("utf-8")
        cls.authoring_hash = hashlib.sha256(canonical).hexdigest()
        if not (cls.build / "cmake_install.cmake").is_file():
            raise RuntimeError("Missing selected build install script; configure again")

    @staticmethod
    def environment():
        environment = {name: value for name, value in os.environ.items()
                       if not name.upper().startswith("HAMMOND_")}
        environment.pop("DESTDIR", None)
        environment.pop("CMAKE_INSTALL_MODE", None)
        return environment

    def invoke(self, command, cwd, environment=None):
        return subprocess.run(list(map(str, command)), cwd=cwd,
                              env=self.environment() if environment is None else environment,
                              capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=20, check=False)

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def install_command(self, build, prefix, *, component=True, configuration=None):
        command = [self.cmake, "--install", build, "--prefix", prefix]
        if component:
            command.extend(("--component", "Standalone"))
        selected = self.configuration if configuration is None else configuration
        if selected:
            command.extend(("--config", selected))
        return command

    def payload(self, bindir, datadir):
        metadata = datadir / "hammond-b3-organ" / "standalone"
        return {(bindir / self.executable.name).as_posix(): self.binary_hash,
                **{(metadata / name).as_posix(): digest for name, digest in self.source_hashes.items()}}

    def test_actual_component_relocates_and_runs(self):
        with tempfile.TemporaryDirectory(prefix="hammond standalone install ") as temporary:
            work = Path(temporary).resolve()
            prefix, moved, unrelated = work / "original organ Ω", work / "moved organ Ω", work / "unrelated cwd"
            unrelated.mkdir()
            # Coexisting OfflineTools names must survive. This deliberately bad
            # external profile also exposes accidental installed-profile lookup.
            existing = {
                self.bindir / ("hammond_render" + self.executable.suffix): b"unrelated offline executable\n",
                self.datadir / "hammond-b3-organ" / "nominal.b3p": b"invalid external profile sentinel\n",
            }
            for relative, content in existing.items():
                path = prefix / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            expected = self.payload(self.bindir, self.datadir)
            expected.update({name.as_posix(): hashlib.sha256(value).hexdigest() for name, value in existing.items()})
            self.assert_success(self.invoke(self.install_command(self.build, prefix), unrelated))
            self.assertEqual(tree_state(prefix), expected_tree(expected), "Extra/missing installed payload")
            repeated = self.invoke(self.install_command(self.build, prefix), unrelated)
            self.assertNotEqual(repeated.returncode, 0)
            self.assertIn("destination already exists", repeated.stderr)
            self.assertEqual(tree_state(prefix), expected_tree(expected))
            prefix.rename(moved)
            self.assertFalse(prefix.exists())
            executable = moved / self.bindir / self.executable.name
            help_result = self.invoke([executable, "--help"], unrelated)
            self.assert_success(help_result)
            self.assertIn("nominal dry organ", help_result.stdout)
            self.assertIn("--smoke-ms", help_result.stdout)
            diagnostics, screenshot, state = (unrelated / name for name in
                                              ("diagnostics.json", "frame.bmp", "absent controls.b3controls"))
            environment = self.environment()
            environment.update(SDL_AUDIODRIVER="dummy", SDL_VIDEODRIVER="dummy")
            result = self.invoke([executable, "--state", state, "--smoke-ms", "600",
                                  "--width", "960", "--height", "700",
                                  "--screenshot", screenshot, "--diagnostics", diagnostics],
                                 unrelated, environment)
            self.assert_success(result)
            report = json.loads(diagnostics.read_text(encoding="utf-8"))
            self.assertEqual(report["schema_version"], 1)
            self.assertEqual(report["profile"], {"id": "nominal-unmeasured-v1",
                                                 "authoring_sha256": self.authoring_hash})
            self.assertEqual(report["runtime"]["sdl_version"], self.lock["version"])
            self.assertEqual(report["runtime"]["video_driver"], "dummy")
            self.assertGreater(report["runtime"]["rendered_images"], 0)
            self.assertTrue(report["runtime"]["screenshot_written"])
            self.assertEqual(report["audio"]["driver"], "dummy")
            for field in ("callback_count", "rendered_frames"):
                self.assertGreater(report["audio"][field], 0)
            for field in ("render_failures", "format_failures", "nonfinite_failures", "overrange_failures"):
                self.assertEqual(report["audio"][field], 0)
            self.assertTrue(report["smoke"]["passed"])
            self.assertEqual(report["smoke"]["duration_ms"], 600)
            self.assertTrue(report["smoke"]["held_observed"])
            self.assertTrue(report["smoke"]["release_observed"])
            self.assertEqual(report["session"]["fault_flags"], 0)
            self.assertFalse(report["session"]["held_after_shutdown"])
            self.assertGreater(report["session"]["maximum_observed_peak"], 0)
            self.assertEqual(report["errors"]["count"], 0)
            self.assertEqual(Path(report["state_path"]), state)
            self.assertFalse(state.exists(), "Running must not implicitly save a controls file")
            bitmap = screenshot.read_bytes()
            self.assertEqual(bitmap[:2], b"BM")
            self.assertEqual(struct.unpack_from("<ii", bitmap, 18), (960, 700))
            self.assertGreater(len(set(bitmap[54:])), 32, "Rendered frame must contain actual image data")
            self.assertEqual(tree_state(moved), expected_tree(expected), "Relocated execution changed the payload")
            self.assertEqual(sha256(self.executable), self.binary_hash, "Install changed the source binary")
            print(json.dumps({"suite": "standalone-install-v1", "payload_files": 9,
                              "binary_sha256": self.binary_hash,
                              "sdl_license_sha256": self.source_hashes["LICENSE-SDL2.txt"],
                              "font_license_sha256": self.source_hashes["LICENSE-DejaVu.txt"],
                              "relocated_smoke": report}, sort_keys=True))

    def fixture(self, work, *, bindir="bin", datadir="share", enabled=True):
        """Generate actual module rules around private copies of the real input bytes."""
        source, build, sdl = work / "source", work / "build", work / "SDL2 source"
        source.mkdir(parents=True)
        sdl.mkdir()
        for relative in (*SOURCE_FILES.values(), Path("cmake/InstallStandalone.cmake"),
                         Path("cmake/InstallHammondTools.cmake")):
            destination = source / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        shutil.copyfile(self.sdl / "LICENSE.txt", sdl / "LICENSE.txt")
        selected = self.configuration or "Release"
        unselected = "Debug" if selected.upper() != "DEBUG" else "Release"
        binary = build / selected / self.executable.name
        decoy = build / unselected / self.executable.name
        decoy.parent.mkdir(parents=True)
        shutil.copy2(self.executable, decoy)
        script = (
            "cmake_minimum_required(VERSION 3.21)\nproject(StandaloneInstallContract LANGUAGES NONE)\n"
            "set(CMAKE_INSTALL_LIBDIR lib CACHE PATH \"\")\n"
            f"set(CMAKE_INSTALL_BINDIR {cmake_literal(bindir)} CACHE PATH \"\")\n"
            f"set(CMAKE_INSTALL_DATADIR {cmake_literal(datadir)} CACHE PATH \"\")\n"
            f"set(HAMMOND_SDL2_ROOT {cmake_literal(sdl)})\n"
            f"set(HAMMOND_BUILD_STANDALONE {'ON' if enabled else 'OFF'})\n"
            "if(HAMMOND_BUILD_STANDALONE)\nadd_executable(hammond_standalone IMPORTED)\n"
            f"set_property(TARGET hammond_standalone PROPERTY IMPORTED_CONFIGURATIONS {selected} {unselected})\n"
            f"set_property(TARGET hammond_standalone PROPERTY IMPORTED_LOCATION {cmake_literal(binary)})\n"
            f"set_property(TARGET hammond_standalone PROPERTY IMPORTED_LOCATION_{selected.upper()} {cmake_literal(binary)})\n"
            f"set_property(TARGET hammond_standalone PROPERTY IMPORTED_LOCATION_{unselected.upper()} {cmake_literal(decoy)})\n"
            "endif()\ninclude(cmake/InstallHammondTools.cmake)\ninclude(cmake/InstallStandalone.cmake)\n")
        (source / "CMakeLists.txt").write_text(script, encoding="utf-8")
        self.assert_success(self.invoke([self.cmake, "-S", source, "-B", build,
                                         f"-DCMAKE_BUILD_TYPE={selected}"], work))
        inputs = [binary, *(source / relative for relative in SOURCE_FILES.values()), sdl / "LICENSE.txt"]
        return source, build, binary, inputs

    def test_preflight_rejects_private_bad_inputs_before_any_destination_write(self):
        with tempfile.TemporaryDirectory(prefix="hammond standalone preflight ") as temporary:
            work = Path(temporary).resolve()
            source, build, binary, inputs = self.fixture(work)
            prefix = work / "fresh destination Ω"
            command = self.install_command(build, prefix, configuration=self.configuration or "Release")

            def rejected(fragment, environment=None):
                before = tree_state(prefix)
                existed = prefix.exists()
                result = self.invoke(command, work, environment)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(fragment, result.stderr)
                self.assertEqual(prefix.exists(), existed, "Preflight created a fresh destination")
                self.assertEqual(tree_state(prefix), before, "Preflight changed the destination")

            # An unselected configuration exists. Only the selected one admits install.
            rejected("selected configuration")
            self.assert_success(self.invoke(self.install_command(build, prefix, component=False), work))
            self.assertFalse(prefix.exists(), "Ordinary installation must exclude Standalone")
            binary.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.executable, binary)
            for path in inputs:
                with self.subTest(missing=str(path.relative_to(work))):
                    held = path.with_name(path.name + ".held")
                    path.rename(held)
                    try:
                        rejected("missing or unreadable required input")
                    finally:
                        held.rename(path)
            original = binary.read_bytes()
            binary.write_bytes(b"")
            rejected("required input is empty")
            binary.write_bytes(original)
            guide = source / "docs/STANDALONE_APP.md"
            held = guide.with_name(guide.name + ".held")
            guide.rename(held)
            try:
                guide.mkdir()
                rejected("regular input without symlinks")
                guide.rmdir()
                guide.symlink_to(held)
                rejected("regular input without symlinks")
                guide.unlink()
                guide.symlink_to(source / "missing link target")
                rejected("regular input without symlinks")
                guide.unlink()
                if hasattr(os, "mkfifo"):
                    os.mkfifo(guide)
                    rejected("regular input without symlinks")
                    guide.unlink()
            finally:
                if os.path.lexists(guide):
                    guide.rmdir() if guide.is_dir() else guide.unlink()
                held.rename(guide)
            for path in (source / "assets/standalone/fonts/LICENSE-DejaVu.txt",
                         work / "SDL2 source/LICENSE.txt", source / "data/dependencies/sdl2-lock.json",
                         source / "assets/standalone/fonts/source-manifest.json"):
                with self.subTest(identity=str(path.relative_to(work))):
                    content = path.read_bytes()
                    try:
                        path.write_bytes(content + b"\n")
                        rejected("configured notice/identity mismatch")
                    finally:
                        path.write_bytes(content)
            for mode in ("SYMLINK", "SYMLINK_OR_COPY"):
                environment = self.environment()
                environment["CMAKE_INSTALL_MODE"] = mode
                rejected("CMAKE_INSTALL_MODE=COPY", environment)
            destinations = (prefix / "bin" / self.executable.name,
                            prefix / "share/hammond-b3-organ/standalone")
            for destination in destinations:
                for kind in ("file", "directory", "dangling symlink"):
                    with self.subTest(destination=destination.name, kind=kind):
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        if kind == "file":
                            destination.write_bytes(b"preserve this existing entry\n")
                        elif kind == "directory":
                            destination.mkdir()
                        else:
                            destination.symlink_to(work / "no existing target")
                        rejected("destination already exists")
                        shutil.rmtree(prefix)
            self.assertEqual(sha256(self.executable), self.binary_hash)

    def test_custom_directories_copy_mode_and_disabled_component(self):
        with tempfile.TemporaryDirectory(prefix="hammond standalone directories ") as temporary:
            work = Path(temporary).resolve()
            bindir, datadir = Path("program files Ω/bin"), Path("readable data Ω/share")
            source, build, binary, _ = self.fixture(work / "custom", bindir=bindir, datadir=datadir)
            binary.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.executable, binary)
            prefix, moved = work / "prefix Ω", work / "relocated Ω"
            environment = self.environment()
            environment["CMAKE_INSTALL_MODE"] = "COPY"
            self.assert_success(self.invoke(self.install_command(build, prefix), work, environment))
            self.assertEqual(tree_state(prefix), expected_tree(self.payload(bindir, datadir)))
            prefix.rename(moved)
            shutil.rmtree(source)
            shutil.rmtree(build)
            self.assert_success(self.invoke([moved / bindir / self.executable.name, "--help"], work))
            # The flag-off fixture cannot create or preflight a Standalone payload.
            _, disabled, _, _ = self.fixture(work / "disabled", enabled=False)
            self.assert_success(self.invoke(self.install_command(disabled, prefix), work))
            self.assertFalse(prefix.exists())
            install_text = (disabled / "cmake_install.cmake").read_text(encoding="utf-8")
            self.assertNotIn("Standalone requires", install_text)


if __name__ == "__main__":
    unittest.main()
