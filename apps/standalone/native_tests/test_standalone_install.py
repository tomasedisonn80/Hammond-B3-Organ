#!/usr/bin/env python3
"""Require a real built app, stage its component, move it, and exercise SDL.

Registered explicitly only for HAMMOND_BUILD_STANDALONE=ON. Destructive input
probes use private copies and the real install module; shared products survive.
"""

import hashlib
import json
import ntpath
import os
import re
from pathlib import Path
import shutil
import stat
import struct
import subprocess
import tempfile
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[3]
SOURCE_FILES = {
    "STANDALONE_INSTALL.md": Path("docs/STANDALONE_INSTALL.md"),
    "STANDALONE_APP.md": Path("docs/STANDALONE_APP.md"),
    "STANDALONE_MODEL.md": Path("docs/STANDALONE_MODEL.md"),
    "MIDI_UI_RUNBOOK.md": Path("docs/MIDI_UI_RUNBOOK.md"),
    "THIRD_PARTY_NOTICES.md": Path("THIRD_PARTY_NOTICES.md"),
    "LICENSE-DejaVu.txt": Path("assets/standalone/fonts/LICENSE-DejaVu.txt"),
    "sdl2-lock.json": Path("data/dependencies/sdl2-lock.json"),
    "font-source-manifest.json": Path("assets/standalone/fonts/source-manifest.json"),
    "reference-source-manifest.json": Path("assets/standalone/reference/manifest.json"),
    "atlas-reference.json": Path("docs/design/atlas-reference.json"),
}

MIDI_FILES = {"LICENSE-RtMidi.txt", "rtmidi-lock.json", "rtmidi-prepared-source.json",
              "rtmidi-coremidi-zero-init.patch"}
GUIDES = ("STANDALONE_INSTALL.md", "STANDALONE_APP.md", "STANDALONE_MODEL.md",
          "MIDI_UI_RUNBOOK.md", "THIRD_PARTY_NOTICES.md")


def metadata_inputs(source, sdl, capabilities, prepared=None):
    result = {name: source / relative for name, relative in SOURCE_FILES.items()}
    result["LICENSE-SDL2.txt"] = sdl / "LICENSE.txt"
    result["standalone-capabilities.json"] = capabilities
    if prepared is not None:
        result.update({
            "LICENSE-RtMidi.txt": prepared / "LICENSE",
            "rtmidi-lock.json": source / "data/dependencies/rtmidi-lock.json",
            "rtmidi-prepared-source.json": prepared / "prepared-source.json",
            "rtmidi-coremidi-zero-init.patch": prepared / "rtmidi-coremidi-zero-init.patch",
        })
    return result


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
        mode = os.environ.get("HAMMOND_TEST_ENABLE_MIDI", "").upper()
        if mode not in ("ON", "OFF", "TRUE", "FALSE", "1", "0"):
            raise RuntimeError("HAMMOND_TEST_ENABLE_MIDI must identify the selected build as ON or OFF")
        cls.midi_enabled = mode in ("ON", "TRUE", "1")
        cls.prepared = required_path("HAMMOND_RTMIDI_PREPARED_ROOT", directory=True) if cls.midi_enabled else None
        cls.backend = os.environ.get("HAMMOND_RTMIDI_BACKEND", "") if cls.midi_enabled else "unavailable"
        if cls.midi_enabled and cls.backend not in ("ALSA", "WinMM", "CoreMIDI"):
            raise RuntimeError("Missing exact configured RtMidi backend identity")
        capabilities = required_path("HAMMOND_STANDALONE_CAPABILITIES")
        cls.metadata = metadata_inputs(ROOT, cls.sdl, capabilities, cls.prepared)
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
        cache = {}
        for line in (cls.build / "CMakeCache.txt").read_text(encoding="utf-8").splitlines():
            if line and not line.startswith(("#", "//")) and ":" in line and "=" in line:
                key, rest = line.split(":", 1)
                cache[key] = rest.split("=", 1)[1]
        cls.configurations = cache.get("CMAKE_CONFIGURATION_TYPES", "").split(";")
        cls.configurations = [value for value in cls.configurations if value]

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

    def payload(self, bindir, datadir, source_hashes=None):
        metadata = datadir / "hammond-b3-organ" / "standalone"
        return {(bindir / self.executable.name).as_posix(): self.binary_hash,
                **{(metadata / name).as_posix(): digest
                   for name, digest in (self.source_hashes if source_hashes is None else source_hashes).items()}}

    def assert_capabilities(self, metadata, midi_enabled, backend):
        document = json.loads(metadata["standalone-capabilities.json"].read_text(encoding="utf-8"))
        self.assertEqual(document["schema_version"], 1)
        self.assertEqual(document["component"], "Standalone")
        self.assertEqual(document["profile"], "embedded nominal-unmeasured-v1")
        sdl = json.loads(metadata["sdl2-lock.json"].read_text(encoding="utf-8"))
        fonts = json.loads(metadata["font-source-manifest.json"].read_text(encoding="utf-8"))
        reference = json.loads(metadata["reference-source-manifest.json"].read_text(encoding="utf-8"))
        atlas = json.loads(metadata["atlas-reference.json"].read_text(encoding="utf-8"))
        self.assertEqual(document["sdl2"], {
            "version": sdl["version"], "commit": sdl["commit"], "linkage": "static",
            "lock_sha256": sha256(metadata["sdl2-lock.json"]),
            "license_sha256": sha256(metadata["LICENSE-SDL2.txt"]),
        })
        self.assertEqual(document["sdl2"]["license_sha256"], sdl["license"]["sha256"])
        self.assertEqual(document["fonts"], {
            "embedded": True, "manifest_sha256": sha256(metadata["font-source-manifest.json"]),
            "license_sha256": sha256(metadata["LICENSE-DejaVu.txt"]),
        })
        self.assertEqual(document["fonts"]["license_sha256"], fonts["license"]["sha256"])
        self.assertEqual(document["reference_art"], {
            "embedded": True, "identity": reference["identity"],
            "manifest_sha256": sha256(metadata["reference-source-manifest.json"]),
            "provenance_sha256": sha256(metadata["atlas-reference.json"]),
            "source_image_sha256": reference["source"]["sha256"],
            "rights_notice": "THIRD_PARTY_NOTICES.md#embedded-reference-decoration",
        })
        self.assertEqual(reference["source"]["sha256"], atlas["sha256"])
        self.assertEqual(reference["source"]["pdf_sha256"], atlas["source_sha256"])
        self.assertEqual(reference["source"]["pdf_pages"], [1, 409])
        self.assertTrue(reference["rights"])
        notices = metadata["THIRD_PARTY_NOTICES.md"].read_text(encoding="utf-8")
        self.assertIn("## Embedded reference decoration", notices)
        self.assertIn(reference["source"]["sha256"], notices)
        midi = document["midi"]
        self.assertIs(midi["enabled"], midi_enabled)
        self.assertEqual(midi["backend"], backend)
        if midi_enabled:
            self.assertTrue(MIDI_FILES.issubset(metadata))
            lock = json.loads(metadata["rtmidi-lock.json"].read_text(encoding="utf-8"))
            prepared = json.loads(metadata["rtmidi-prepared-source.json"].read_text(encoding="utf-8"))
            self.assertEqual(prepared["dependency_lock"], lock)
            self.assertEqual(midi["rtmidi"], {
                "version": lock["version"], "commit": lock["commit"], "linkage": "static",
                "lock_sha256": sha256(metadata["rtmidi-lock.json"]),
                "license_sha256": sha256(metadata["LICENSE-RtMidi.txt"]),
                "prepared_manifest_sha256": sha256(metadata["rtmidi-prepared-source.json"]),
                "prepared_source_sha256": lock["patch"]["prepared_sha256"],
                "patch_id": lock["patch"]["id"],
                "patch_sha256": sha256(metadata["rtmidi-coremidi-zero-init.patch"]),
            })
            self.assertEqual(midi["rtmidi"]["license_sha256"], lock["license"]["sha256"])
            self.assertEqual(midi["rtmidi"]["patch_sha256"], lock["patch"]["sha256"])
            self.assertEqual(prepared["prepared_files"]["RtMidi.cpp"], {
                "bytes": lock["patch"]["prepared_bytes"], "sha256": lock["patch"]["prepared_sha256"]})
            for installed, prepared_name in (("LICENSE-RtMidi.txt", "LICENSE"),
                                              ("rtmidi-coremidi-zero-init.patch", "rtmidi-coremidi-zero-init.patch")):
                self.assertEqual(prepared["prepared_files"][prepared_name], {
                    "bytes": metadata[installed].stat().st_size, "sha256": sha256(metadata[installed])})
            self.assertRegex(prepared["preparation_tool"]["sha256"], r"^[0-9a-f]{64}$")
            self.assertIn("runtime service", midi["availability"])
        else:
            self.assertFalse(MIDI_FILES.intersection(metadata))
            self.assertIsNone(midi["rtmidi"])
            self.assertIn("No physical MIDI backend was compiled", midi["availability"])
        self.assertNotIn(str(ROOT), json.dumps(document))
        self.assertNotIn(str(self.build), json.dumps(document))
        return document

    def assert_installed_guide_links(self, metadata):
        for name in GUIDES:
            document = metadata[name].read_text(encoding="utf-8")
            for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", document):
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                    continue
                path = target.split("#", 1)[0]
                self.assertIn(path, metadata, f"{name}: installed relative link is absent: {target}")
                self.assertTrue(metadata[path].is_file())

    def test_configured_capabilities_identify_exact_payload(self):
        self.assert_capabilities(self.metadata, self.midi_enabled, self.backend)
        self.assertEqual(len(self.metadata) + 1, 17 if self.midi_enabled else 13)

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
            installed_directory = moved / self.datadir / "hammond-b3-organ/standalone"
            installed_metadata = {name: installed_directory / name for name in self.metadata}
            self.assert_capabilities(installed_metadata, self.midi_enabled, self.backend)
            self.assert_installed_guide_links(installed_metadata)
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
            self.assertEqual(report["schema_version"], 2)
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
            self.assertIs(report["midi"]["backend_available"], self.midi_enabled)
            self.assertEqual(report["midi"]["backend"], self.backend)
            self.assertEqual(report["midi"]["requested_port"], "")
            self.assertEqual(report["midi"]["port_name"], "")
            self.assertEqual(report["midi"]["state_after_shutdown"], "closed" if self.midi_enabled else "unavailable")
            self.assertFalse(report["midi"]["active_after_shutdown"])
            self.assertEqual(report["midi"]["open_failures"], 0)
            self.assertEqual(report["midi"]["device"]["callback_messages"], 0)
            self.assertEqual(Path(report["state_path"]), state)
            self.assertFalse(state.exists(), "Running must not implicitly save a controls file")
            bitmap = screenshot.read_bytes()
            self.assertEqual(bitmap[:2], b"BM")
            self.assertEqual(struct.unpack_from("<ii", bitmap, 18), (960, 700))
            self.assertGreater(len(set(bitmap[54:])), 32, "Rendered frame must contain actual image data")
            self.assertEqual(tree_state(moved), expected_tree(expected), "Relocated execution changed the payload")
            self.assertEqual(sha256(self.executable), self.binary_hash, "Install changed the source binary")
            print(json.dumps({"suite": "standalone-install-v2", "payload_files": len(self.source_hashes) + 1,
                              "midi_enabled": self.midi_enabled, "midi_backend": self.backend,
                              "binary_sha256": self.binary_hash,
                              "sdl_license_sha256": self.source_hashes["LICENSE-SDL2.txt"],
                              "font_license_sha256": self.source_hashes["LICENSE-DejaVu.txt"],
                              "relocated_smoke": report}, sort_keys=True))

    def fixture(self, work, *, bindir="bin", datadir="share", enabled=True, midi_enabled=None):
        """Actual install module and private input bytes; no compiler, SDK or device."""
        if midi_enabled is None:
            midi_enabled = self.midi_enabled
        source, build, sdl = work / "source", work / "build", work / "SDL2 source"
        source.mkdir(parents=True)
        sdl.mkdir()
        for relative in (*SOURCE_FILES.values(), Path("cmake/InstallStandalone.cmake"),
                         Path("cmake/InstallHammondTools.cmake")):
            destination = source / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)
        shutil.copyfile(self.sdl / "LICENSE.txt", sdl / "LICENSE.txt")
        prepared = None
        if midi_enabled:
            self.assertIsNotNone(self.prepared, "Enabled fixture requires the actual verified prepared metadata")
            prepared = work / "prepared RtMidi"
            prepared.mkdir()
            for name in ("LICENSE", "prepared-source.json", "rtmidi-coremidi-zero-init.patch"):
                shutil.copyfile(self.prepared / name, prepared / name)
            shutil.copyfile(ROOT / "data/dependencies/rtmidi-lock.json", source / "data/dependencies/rtmidi-lock.json")
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
            f"set(HAMMOND_ENABLE_MIDI {'ON' if midi_enabled else 'OFF'})\n"
            f"set(HAMMOND_RTMIDI_ROOT {cmake_literal(work / 'absent external RtMidi checkout')})\n"
            "set(CMAKE_DISABLE_FIND_PACKAGE_ALSA TRUE)\nset(CMAKE_DISABLE_FIND_PACKAGE_Threads TRUE)\n"
            "if(HAMMOND_BUILD_STANDALONE)\nadd_executable(hammond_standalone IMPORTED)\n"
            f"set_property(TARGET hammond_standalone PROPERTY IMPORTED_CONFIGURATIONS {selected} {unselected})\n"
            f"set_property(TARGET hammond_standalone PROPERTY IMPORTED_LOCATION {cmake_literal(binary)})\n"
            f"set_property(TARGET hammond_standalone PROPERTY IMPORTED_LOCATION_{selected.upper()} {cmake_literal(binary)})\n"
            f"set_property(TARGET hammond_standalone PROPERTY IMPORTED_LOCATION_{unselected.upper()} {cmake_literal(decoy)})\n"
            "endif()\n")
        if midi_enabled:
            script += ("add_library(hammond_rtmidi STATIC IMPORTED)\n"
                       f"set_property(TARGET hammond_rtmidi PROPERTY HAMMOND_RTMIDI_PREPARED_ROOT {cmake_literal(prepared)})\n"
                       f"set_property(TARGET hammond_rtmidi PROPERTY HAMMOND_RTMIDI_BACKEND {self.backend})\n")
        script += "include(cmake/InstallHammondTools.cmake)\ninclude(cmake/InstallStandalone.cmake)\n"
        (source / "CMakeLists.txt").write_text(script, encoding="utf-8")
        self.assert_success(self.invoke([self.cmake, "-S", source, "-B", build,
                                         f"-DCMAKE_BUILD_TYPE={selected}"], work))
        metadata = metadata_inputs(source, sdl, build / "generated/standalone-capabilities.json", prepared) if enabled else {}
        hashes = {name: sha256(path) for name, path in metadata.items()}
        return SimpleNamespace(source=source, build=build, binary=binary,
                               inputs=[binary, *metadata.values()], metadata=metadata, hashes=hashes,
                               midi_enabled=midi_enabled, backend=self.backend if midi_enabled else "unavailable")

    def test_actual_configuration_selection_preserves_complete_payload_or_destination(self):
        # This uses the actual generated build, not an imported-target fixture.
        # A single-config generator selects its configured executable regardless
        # of --config; no additional generator is needed to run this test.
        unknown = "HammondUnknownConfiguration"
        while unknown.casefold() in {value.casefold() for value in self.configurations}:
            unknown += "X"
        with tempfile.TemporaryDirectory(prefix="hammond configuration install ") as temporary:
            work = Path(temporary).resolve()
            for existing in (False, True):
                with self.subTest(existing=existing, configurations=self.configurations):
                    prefix = work / ("existing prefix Ω" if existing else "fresh prefix Ω")
                    if existing:
                        (prefix / "keep directory").mkdir(parents=True)
                        (prefix / "keep directory/sentinel.bin").write_bytes(b"retain this installation prefix\x00\xff")
                        (prefix / "empty directory").mkdir()
                    before = tree_state(prefix)
                    present = prefix.exists()
                    result = self.invoke(self.install_command(self.build, prefix, configuration=unknown), work)
                    if self.configurations:
                        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                        self.assertIn("Standalone unknown configuration", result.stderr)
                        self.assertEqual(prefix.exists(), present, "Unknown configuration created a destination")
                        self.assertEqual(tree_state(prefix), before, "Unknown configuration changed the destination")
                    else:
                        self.assert_success(result)
                        expected = expected_tree(self.payload(self.bindir, self.datadir))
                        expected.update(before)
                        self.assertEqual(tree_state(prefix), expected, "Single-config selection installed a partial payload")

    def test_preflight_rejects_private_bad_inputs_before_any_destination_write(self):
        with tempfile.TemporaryDirectory(prefix="hammond standalone preflight ") as temporary:
            work = Path(temporary).resolve()
            fixture = self.fixture(work)
            source, build, binary, inputs = fixture.source, fixture.build, fixture.binary, fixture.inputs
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
            for path in inputs:
                with self.subTest(empty=str(path.relative_to(work))):
                    original = path.read_bytes()
                    try:
                        path.write_bytes(b"")
                        rejected("required input is empty")
                    finally:
                        path.write_bytes(original)
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
            for path in fixture.metadata.values():
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

    def test_disabled_midi_inventory_requires_no_rtmidi_input_or_sdk_lookup(self):
        # This imported-target fixture checks install-rule selection. Actual
        # executable/configuration agreement is checked by the relocated smoke.
        with tempfile.TemporaryDirectory(prefix="hammond disabled MIDI package ") as temporary:
            work = Path(temporary).resolve()
            fixture = self.fixture(work / "fixture", midi_enabled=False)
            self.assertFalse((fixture.source / "data/dependencies/rtmidi-lock.json").exists())
            self.assertFalse((work / "fixture/prepared RtMidi").exists())
            self.assertFalse((work / "fixture/absent external RtMidi checkout").exists())
            fixture.binary.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.executable, fixture.binary)
            self.assert_capabilities(fixture.metadata, False, "unavailable")
            prefix = work / "installed without MIDI"
            self.assert_success(self.invoke(self.install_command(fixture.build, prefix), work))
            self.assertEqual(tree_state(prefix), expected_tree(self.payload(Path("bin"), Path("share"), fixture.hashes)))
            self.assertEqual(len(fixture.hashes) + 1, 13)
            install_text = (fixture.build / "cmake_install.cmake").read_text(encoding="utf-8")
            self.assertNotIn("prepared RtMidi", install_text)
            self.assertNotIn("rtmidi-lock.json", install_text)
            self.assertFalse((work / "fixture/absent external RtMidi checkout").exists())

    def test_reference_capability_and_midi_records_reject_nonregular_inputs(self):
        with tempfile.TemporaryDirectory(prefix="hammond identity preflight ") as temporary:
            work = Path(temporary).resolve()
            fixture = self.fixture(work / "fixture")
            fixture.binary.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.executable, fixture.binary)
            prefix = work / "destination"
            # Preserve existing ordinary entries as well as refusing creation
            # of the application and metadata directories.
            (prefix / "empty sentinel").mkdir(parents=True)
            (prefix / "sentinel.bin").write_bytes(b"preserve identity preflight\x00\xff")
            before = tree_state(prefix)
            names = {"reference-source-manifest.json", "atlas-reference.json", "standalone-capabilities.json"}
            names.update(MIDI_FILES.intersection(fixture.metadata))
            for name in sorted(names):
                path = fixture.metadata[name]
                held = path.with_name(path.name + ".held")
                path.rename(held)
                try:
                    kinds = ["directory", "symlink", "dangling symlink"]
                    if hasattr(os, "mkfifo"):
                        kinds.append("fifo")
                    for kind in kinds:
                        with self.subTest(input=name, kind=kind):
                            if kind == "directory":
                                path.mkdir()
                            elif kind == "symlink":
                                path.symlink_to(held)
                            elif kind == "dangling symlink":
                                path.symlink_to(work / "absent target")
                            else:
                                os.mkfifo(path)
                            try:
                                result = self.invoke(self.install_command(fixture.build, prefix), work)
                                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                                self.assertIn("regular input without symlinks", result.stderr)
                                self.assertEqual(tree_state(prefix), before)
                            finally:
                                path.rmdir() if kind == "directory" else path.unlink()
                finally:
                    held.rename(path)

    def test_destination_ancestors_remain_ordinary_directories(self):
        with tempfile.TemporaryDirectory(prefix="hammond destination ancestry ") as temporary:
            work = Path(temporary).resolve()
            fixture = self.fixture(work / "fixture")
            fixture.binary.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.executable, fixture.binary)
            external = work / "external directory"
            external.mkdir()
            (external / "sentinel.bin").write_bytes(b"preserve external target\x00\xff")
            external_before = tree_state(external)
            for directory in ("bin", "share"):
                for kind in ("file", "symlink"):
                    with self.subTest(directory=directory, kind=kind):
                        prefix = work / f"{directory}-{kind}"
                        prefix.mkdir()
                        path = prefix / directory
                        if kind == "file":
                            path.write_bytes(b"preserve parent entry\n")
                        else:
                            path.symlink_to(external, target_is_directory=True)
                        before = tree_state(prefix)
                        result = self.invoke(self.install_command(fixture.build, prefix), work)
                        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                        self.assertIn("destination parent must be an ordinary directory without symlinks", " ".join(result.stderr.split()))
                        self.assertEqual(tree_state(prefix), before)
                        self.assertEqual(tree_state(external), external_before)

    def test_custom_directories_copy_mode_and_disabled_component(self):
        with tempfile.TemporaryDirectory(prefix="hammond standalone directories ") as temporary:
            work = Path(temporary).resolve()
            bindir, datadir = Path("program files Ω/bin"), Path("readable data Ω/share")
            fixture = self.fixture(work / "custom", bindir=bindir, datadir=datadir)
            source, build, binary = fixture.source, fixture.build, fixture.binary
            binary.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.executable, binary)
            prefix, moved = work / "prefix Ω", work / "relocated Ω"
            environment = self.environment()
            environment["CMAKE_INSTALL_MODE"] = "COPY"
            self.assert_success(self.invoke(self.install_command(build, prefix), work, environment))
            self.assertEqual(tree_state(prefix), expected_tree(self.payload(bindir, datadir, fixture.hashes)))
            prefix.rename(moved)
            shutil.rmtree(source)
            shutil.rmtree(build)
            self.assert_success(self.invoke([moved / bindir / self.executable.name, "--help"], work))
            # The flag-off fixture cannot create or preflight a Standalone payload.
            disabled = self.fixture(work / "disabled", enabled=False, midi_enabled=False)
            self.assert_success(self.invoke(self.install_command(disabled.build, prefix), work))
            self.assertFalse(prefix.exists())
            install_text = (disabled.build / "cmake_install.cmake").read_text(encoding="utf-8")
            self.assertNotIn("Standalone requires", install_text)


if __name__ == "__main__":
    unittest.main()
