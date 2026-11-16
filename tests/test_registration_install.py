#!/usr/bin/env python3
"""Real registration component rules, private admission faults and native use.

CTest supplies the selected executable, CMake, build/config and relative install
directories. Tiny LANGUAGES NONE projects import copies of that executable; they
compile nothing. A second fixture copies the root's generated install script to
check actual integration without writing its install manifest or changing its
inputs. Relocation deletes every private source/build input before native use.
"""

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
GUIDE = Path("docs/REGISTRATION_GUIDE.md")
SOURCE_PACK = Path("data/registrations/starter-v1")
PACKAGE = Path("hammond/registrations/starter-v1")
INSTALLED_GUIDE = Path("hammond/REGISTRATION_GUIDE.md")
STEMS = (
    "01 Quiet Foundation", "02 Warm Comp", "03 Clear Lead", "04 Reed Edge",
    "05 Bright Ensemble", "06 High Shimmer", "07 Percussive Pair", "08 Slow Accent",
    "09 Split Dialogue", "10 Pedal Study", "11 Fixed Contrast", "12 Manual Return",
)
ENTRIES = tuple(stem + suffix for stem in STEMS
                for suffix in (".b3registration", ".b3performance"))
PAYLOAD = tuple(SOURCE_PACK / "entries" / name for name in ENTRIES) + (
    SOURCE_PACK / "README.md", SOURCE_PACK / "recipes.json")
MODULES = (Path("cmake/InstallHammondTools.cmake"),
           Path("cmake/InstallRegistrationTools.cmake"))
COMPONENTS = ("RegistrationTools", "StarterRegistrations")
CALLS = 0


def environment():
    result = {key: value for key, value in os.environ.items()
              if not key.upper().startswith(("HAMMOND_", "CMAKE_GENERATOR"))}
    for key in ("DESTDIR", "CMAKE_INSTALL_MODE", "PYTHONPATH", "PYTHONHOME"):
        result.pop(key, None)
    result["PYTHONDONTWRITEBYTECODE"] = "1"
    return result


def invoke(args, cwd, env=None):
    global CALLS
    CALLS += 1
    return subprocess.run(list(map(str, args)), cwd=cwd,
                          env=environment() if env is None else env,
                          capture_output=True, check=False, timeout=45)


def diagnostic(result):
    return (result.stdout + result.stderr).decode("utf-8", "replace")


def snapshot(root):
    """Include empty directories, modes, bytes and links without following them."""
    def entry(path):
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            return ("link", os.readlink(path))
        if stat.S_ISDIR(mode):
            return ("directory", stat.S_IMODE(mode))
        if stat.S_ISREG(mode):
            return ("file", stat.S_IMODE(mode), path.read_bytes())
        return ("special", mode)

    if not root.exists() and not root.is_symlink():
        return None
    result = {".": entry(root)}
    if result["."][0] == "directory":
        for directory, directories, files in os.walk(root, followlinks=False):
            for name in directories + files:
                path = Path(directory) / name
                result[path.relative_to(root).as_posix()] = entry(path)
    return result


@contextmanager
def withheld(path):
    backup = path.with_name(path.name + ".held-by-registration-install-test")
    path.rename(backup)
    try:
        yield backup
    finally:
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.is_dir():
            path.rmdir()
        backup.rename(path)


def copy_source(destination):
    for relative in (*PAYLOAD, GUIDE, *MODULES):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)


class PrivateProject:
    def __init__(self, root, cmake, executable, *, generator=None, make_program=None,
                 bindir="bin", datadir="share"):
        self.root, self.cmake = root, cmake
        self.source, self.build = root / "source", root / "build"
        self.generator, self.make_program = generator, make_program
        self.bindir_text, self.datadir_text = bindir, datadir
        self.bindir, self.datadir = Path(bindir.replace("\\", "/")), Path(datadir.replace("\\", "/"))
        self.name = executable.name
        root.mkdir()
        copy_source(self.source)
        self.binaries = {}
        for config in ("Release", "Debug"):
            path = self.build / "private-native" / config / self.name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(executable, path)
            self.binaries[config] = path
        # Unlisted siblings must never be discovered or copied by the installer.
        (self.source / SOURCE_PACK / "entries" / "unlisted.txt").write_bytes(b"not a registration\n")
        (self.source / SOURCE_PACK / "unlisted.json").write_bytes(b"{}\n")
        (self.source / "sentinel.txt").write_bytes(b"unrelated component\n")
        (self.source / "CMakeLists.txt").write_text(
            'cmake_minimum_required(VERSION 3.21)\n'
            'project(RegistrationInstallFixture LANGUAGES NONE)\n'
            'include(cmake/InstallHammondTools.cmake)\n'
            # Apply raw fixture values after GNUInstallDirs so intentional empty
            # values reach the real shared validator instead of its defaults.
            'set(CMAKE_INSTALL_BINDIR "${FIXTURE_BINDIR}")\n'
            'set(CMAKE_INSTALL_DATADIR "${FIXTURE_DATADIR}")\n'
            'add_executable(hammond_registration IMPORTED GLOBAL)\n'
            'set_target_properties(hammond_registration PROPERTIES\n'
            '  IMPORTED_CONFIGURATIONS "Release;Debug"\n'
            '  IMPORTED_LOCATION "${FIXTURE_RELEASE_BINARY}"\n'
            '  IMPORTED_LOCATION_RELEASE "${FIXTURE_RELEASE_BINARY}"\n'
            '  IMPORTED_LOCATION_DEBUG "${FIXTURE_DEBUG_BINARY}")\n'
            'include(cmake/InstallRegistrationTools.cmake)\n'
            'install(FILES sentinel.txt DESTINATION unrelated COMPONENT Sentinel)\n',
            encoding="utf-8")
        self.configured = self.configure()

    def configure(self, *, bindir=None, datadir=None, build=None):
        args = [self.cmake, "-S", self.source, "-B", build or self.build, "-Wno-dev",
                "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_CONFIGURATION_TYPES=Release;Debug",
                f"-DFIXTURE_BINDIR:STRING={self.bindir_text if bindir is None else bindir}",
                f"-DFIXTURE_DATADIR:STRING={self.datadir_text if datadir is None else datadir}",
                f"-DFIXTURE_RELEASE_BINARY:FILEPATH={self.binaries['Release'].as_posix()}",
                f"-DFIXTURE_DEBUG_BINARY:FILEPATH={self.binaries['Debug'].as_posix()}"]
        if self.generator:
            args += ["-G", self.generator]
        if self.make_program:
            args += [f"-DCMAKE_MAKE_PROGRAM:FILEPATH={self.make_program}"]
        return invoke(args, self.root)

    def install(self, prefix, component, *, config="Release", env=None, strip=False):
        args = [self.cmake, "--install", self.build, "--prefix", prefix, "--config", config]
        if component is not None:
            args += ["--component", component]
        if strip:
            args += ["--strip"]
        return invoke(args, self.root, env)

    def inputs(self, component):
        if component == "RegistrationTools":
            return [self.binaries["Release"], self.source / GUIDE]
        return [self.source / relative for relative in PAYLOAD]


class RegistrationInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def required(variable, directory=False):
            value = os.environ.get(variable)
            path = Path(value).resolve() if value else None
            if path is None or not (path.is_dir() if directory else path.is_file()):
                raise RuntimeError(f"Missing {variable}={value!r}; configure the registration install "
                                   "test and build hammond_registration before running CTest")
            return path

        def relative(variable):
            value = os.environ.get(variable)
            text = value.replace("\\", "/") if value is not None else ""
            path = Path(text)
            if not text or path.is_absolute() or ".." in path.parts or ";" in text or re.match(r"^[A-Za-z]:", text):
                raise RuntimeError(f"{variable} must name a nonempty relative install directory")
            return path

        cls.cmake = required("HAMMOND_TEST_CMAKE")
        cls.build = required("HAMMOND_TEST_BUILD_DIR", directory=True)
        cls.executable = required("HAMMOND_REGISTRATION_EXECUTABLE")
        cls.config = os.environ.get("HAMMOND_TEST_CONFIG") or "Release"
        cls.bindir, cls.datadir = relative("HAMMOND_INSTALL_BINDIR"), relative("HAMMOND_INSTALL_DATADIR")
        cls.generator = os.environ.get("HAMMOND_TEST_CMAKE_GENERATOR")
        cls.make_program = os.environ.get("HAMMOND_TEST_CMAKE_MAKE_PROGRAM")
        if cls.make_program and cls.make_program.endswith("-NOTFOUND"):
            cls.make_program = None
        cls.script = cls.build / "cmake_install.cmake"
        cls.script_text = cls.script.read_text(encoding="utf-8")
        for component in COMPONENTS:
            if f'CMAKE_INSTALL_COMPONENT STREQUAL "{component}"' not in cls.script_text:
                raise RuntimeError(f"Root install script lacks {component}; reconfigure through the build owner")
        cls.binary_bytes = cls.executable.read_bytes()
        cls.originals = {relative: (ROOT / relative).read_bytes() for relative in (*PAYLOAD, GUIDE)}
        watched = [ROOT / relative for relative in (*PAYLOAD, GUIDE, *MODULES)]
        watched += [cls.executable, cls.script]
        cls.hashes = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
        cls.temporary = tempfile.TemporaryDirectory(prefix="registration-install-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name).resolve()
        cls.base = PrivateProject(cls.root / "base", cls.cmake, cls.executable,
                                  generator=cls.generator, make_program=cls.make_program)
        if cls.base.configured.returncode:
            raise RuntimeError("Private install fixture failed:\n" + diagnostic(cls.base.configured))

    @classmethod
    def tearDownClass(cls):
        changed = [str(path) for path, expected in cls.hashes.items()
                   if hashlib.sha256(path.read_bytes()).hexdigest() != expected]
        if changed:
            raise AssertionError("Real source/build inputs changed: " + repr(changed))
        print(f"registration installed-component acceptance: {CALLS} subprocess invocations")

    def setUp(self):
        self.work = self.root / self._testMethodName
        self.work.mkdir()
        self.number = 0

    def new_path(self, label):
        self.number += 1
        return self.work / f"{self.number:03d} {label}"

    def project(self, label, **options):
        options.setdefault("generator", self.generator)
        options.setdefault("make_program", self.make_program)
        project = PrivateProject(self.new_path(label), self.cmake, self.executable, **options)
        self.ok(project.configured)
        return project

    def ok(self, result):
        self.assertEqual(result.returncode, 0, diagnostic(result))

    def expected(self, bindir, datadir, components):
        result = {}
        if "RegistrationTools" in components:
            result[bindir / self.executable.name] = self.binary_bytes
            result[datadir / INSTALLED_GUIDE] = self.originals[GUIDE]
        if "StarterRegistrations" in components:
            for relative in PAYLOAD:
                result[datadir / PACKAGE / relative.relative_to(SOURCE_PACK)] = self.originals[relative]
        return result

    def exact(self, prefix, bindir, datadir, components):
        expected = self.expected(bindir, datadir, components)
        actual = snapshot(prefix)
        self.assertIsInstance(actual, dict)
        self.assertFalse(any(value[0] == "link" for value in actual.values()))
        files = {Path(name): value[2] for name, value in actual.items() if value[0] == "file"}
        self.assertEqual(files, expected)
        directories = {Path(".")}
        for relative in expected:
            directories.update(relative.parents)
        self.assertEqual({Path(name) for name, value in actual.items() if value[0] == "directory"},
                         directories)
        return prefix / bindir / self.executable.name, prefix / datadir / PACKAGE

    def refused(self, project, prefix, component, *, env=None, observed=None):
        observed = prefix if observed is None else observed
        before = snapshot(observed)
        result = project.install(prefix, component, env=env)
        self.assertNotEqual(result.returncode, 0, diagnostic(result))
        self.assertIn(component, diagnostic(result))
        self.assertEqual(snapshot(observed), before)
        return result

    def test_exact_explicit_inventory_and_component_independence(self):
        for component in COMPONENTS:
            with self.subTest(component=component):
                prefix = self.new_path(component)
                self.ok(self.base.install(prefix, component))
                self.exact(prefix, self.base.bindir, self.base.datadir, [component])
                self.refused(self.base, prefix, component)
        # Ordinary installs and unrelated component dispatch must not copy either
        # new component or execute their preflight, even with every input absent.
        project = self.project("default exclusion")
        shutil.rmtree(project.source / SOURCE_PACK)
        (project.source / GUIDE).unlink()
        for binary in project.binaries.values():
            binary.unlink()
        for component in (None, "Sentinel"):
            prefix = self.new_path("unrelated prefix")
            self.ok(project.install(prefix, component))
            self.assertEqual({p.relative_to(prefix).as_posix(): p.read_bytes()
                              for p in prefix.rglob("*") if p.is_file()},
                             {"unrelated/sentinel.txt": b"unrelated component\n"})
        for order in (COMPONENTS, tuple(reversed(COMPONENTS))):
            prefix = self.new_path("shared prefix")
            for component in order:
                self.ok(self.base.install(prefix, component, strip=True))
            self.exact(prefix, self.base.bindir, self.base.datadir, COMPONENTS)

    def test_every_missing_or_empty_input_refuses_before_mutation(self):
        prefix = self.new_path("preserved prefix")
        prefix.mkdir()
        (prefix / "unrelated.txt").write_bytes(b"preserve exactly\x00\n")
        for component in COMPONENTS:
            for path in self.base.inputs(component):
                with self.subTest(component=component, input=path.name):
                    with withheld(path):
                        self.refused(self.base, prefix, component)
                        path.write_bytes(b"")
                        self.refused(self.base, prefix, component)
        for component in COMPONENTS:
            with withheld(self.base.inputs(component)[-1]):
                absent = self.new_path("must remain absent")
                self.refused(self.base, absent, component)
                self.assertFalse(absent.exists())

    def test_input_directories_and_symlinks_are_rejected(self):
        for component in COMPONENTS:
            for path in (self.base.inputs(component)[0], self.base.inputs(component)[-1]):
                with self.subTest(component=component, input=path.name):
                    with withheld(path) as backup:
                        path.mkdir()
                        self.refused(self.base, self.new_path("directory input"), component)
                        path.rmdir()
                        try:
                            path.symlink_to(backup)
                        except (OSError, NotImplementedError):
                            continue
                        self.refused(self.base, self.new_path("linked input"), component)
        entries = self.base.source / SOURCE_PACK / "entries"
        with withheld(entries) as backup:
            try:
                entries.symlink_to(backup, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Directory symlink creation unavailable")
            self.refused(self.base, self.new_path("linked source ancestor"), "StarterRegistrations")

    def test_destination_collisions_and_ancestors_preserve_both_outputs(self):
        destinations = (("RegistrationTools", Path("bin") / self.executable.name),
                        ("RegistrationTools", Path("share") / INSTALLED_GUIDE),
                        ("StarterRegistrations", Path("share") / PACKAGE))
        for component, relative in destinations:
            for kind in ("file", "directory", "dangling link"):
                with self.subTest(component=component, destination=str(relative), kind=kind):
                    prefix = self.new_path("collision")
                    path = prefix / relative
                    path.parent.mkdir(parents=True)
                    if kind == "file":
                        path.write_bytes(b"existing destination\n")
                    elif kind == "directory":
                        path.mkdir()
                    else:
                        try:
                            path.symlink_to(self.new_path("absent target"))
                        except (OSError, NotImplementedError):
                            continue
                    self.refused(self.base, prefix, component)
        for component, ancestor in (("RegistrationTools", "bin"),
                                    ("RegistrationTools", "share"),
                                    ("StarterRegistrations", "share")):
            prefix = self.new_path("blocked parent")
            prefix.mkdir()
            (prefix / ancestor).write_bytes(b"ordinary file cannot contain payload\n")
            self.refused(self.base, prefix, component)
            (prefix / ancestor).unlink()
            outside = self.new_path("linked outside")
            outside.mkdir()
            try:
                (prefix / ancestor).symlink_to(outside, target_is_directory=True)
            except (OSError, NotImplementedError):
                continue
            before = snapshot(outside)
            self.refused(self.base, prefix, component)
            self.assertEqual(snapshot(outside), before)

    def test_copy_mode_and_strip_preserve_selected_bytes(self):
        for mode in ("SYMLINK", "REL_SYMLINK", "ABS_SYMLINK_OR_COPY", "invalid"):
            env = environment()
            env["CMAKE_INSTALL_MODE"] = mode
            for component in COMPONENTS:
                with self.subTest(mode=mode, component=component):
                    result = self.refused(self.base, self.new_path("noncopy"), component, env=env)
                    self.assertIn("CMAKE_INSTALL_MODE=COPY", diagnostic(result))
        env = environment()
        env["CMAKE_INSTALL_MODE"] = "COPY"
        prefix = self.new_path("explicit copy")
        for component in COMPONENTS:
            self.ok(self.base.install(prefix, component, env=env, strip=True))
        self.exact(prefix, self.base.bindir, self.base.datadir, COMPONENTS)

    def test_custom_directories_reconfigure_and_invalid_values(self):
        for bindir, datadir in (("native tools/é音", "resources/音 data"),
                               ("native\\tools", "resources\\data"), (".", ".")):
            project = self.project("custom directories", bindir=bindir, datadir=datadir)
            self.ok(project.configure())
            prefix = self.new_path("custom prefix")
            for component in COMPONENTS:
                self.ok(project.install(prefix, component))
            self.exact(prefix, project.bindir, project.datadir, COMPONENTS)
            self.ok(project.configure(bindir="other tools", datadir="other data"))
            changed = self.new_path("reconfigured prefix")
            for component in COMPONENTS:
                self.ok(project.install(changed, component))
            self.exact(changed, Path("other tools"), Path("other data"), COMPONENTS)
        for variable in ("bindir", "datadir"):
            for value in ("", "/absolute", "C:/absolute", "C:relative", "\\absolute",
                          "..", "a/../b", "a\\..\\b", "a;b"):
                with self.subTest(variable=variable, value=value):
                    result = self.base.configure(build=self.new_path("invalid build"), **{variable: value})
                    self.assertNotEqual(result.returncode, 0, diagnostic(result))
                    self.assertIn("nonempty relative CMAKE_INSTALL_", " ".join(diagnostic(result).split()))
        conflict = self.project("file ancestor conflict", bindir=".", datadir=self.executable.name)
        self.refused(conflict, self.new_path("conflicting destination"), "RegistrationTools")

    @unittest.skipIf(os.name == "nt", "CMake DESTDIR is a POSIX staging facility")
    def test_destdir_success_and_late_admission_failure(self):
        stage, nominal = self.new_path("stage é音"), self.new_path("nominal prefix")
        effective = stage / str(nominal).lstrip("/")
        env = environment()
        env["DESTDIR"] = str(stage)
        for component in COMPONENTS:
            self.ok(self.base.install(nominal, component, env=env))
            self.refused(self.base, nominal, component, env=env, observed=stage)
        self.exact(effective, self.base.bindir, self.base.datadir, COMPONENTS)
        self.assertFalse(nominal.exists())
        for component in COMPONENTS:
            stage, nominal = self.new_path("absent stage"), self.new_path("unused nominal")
            env["DESTDIR"] = str(stage)
            with withheld(self.base.inputs(component)[-1]):
                self.refused(self.base, nominal, component, env=env, observed=stage)
            self.assertFalse(stage.exists() or nominal.exists())

    def test_late_copy_failure_retains_partial_package_and_refuses_reinstall(self):
        source, build = self.new_path("partial source"), self.new_path("partial build")
        copy_source(source)
        build.mkdir()
        # Exercise the actual configured rules, retaining only private paths.
        script = self.script_text.replace(self.build.as_posix(), build.as_posix())
        script = script.replace(ROOT.as_posix(), source.as_posix())
        first, second, third = ENTRIES[:3]
        third_source = source / SOURCE_PACK / "entries" / third
        held = third_source.with_name(third + ".held-by-registration-install-test")
        original_source = snapshot(source)
        # A file-size limit need not stop a platform's native copy mechanism.
        # Instead, withdraw this private input immediately before its actual
        # generated file(INSTALL), after preflight and the first two copies.
        anchors = []
        for name in (first, second, third):
            path = (source / SOURCE_PACK / "entries" / name).as_posix()
            pattern = (r'(?m)^[ \t]*file\(INSTALL [^\n]* TYPE FILE FILES "'
                       + re.escape(path) + r'"\)$')
            matches = list(re.finditer(pattern, script))
            self.assertEqual(len(matches), 1,
                             f"Expected one actual generated copy command for {path}")
            anchors.append(matches[0])
        preflight = 'message(STATUS "StarterRegistrations preflight passed; copying begins.'
        self.assertEqual(script.count(preflight), 1)
        self.assertLess(script.index(preflight), anchors[0].start())
        self.assertLess(anchors[0].start(), anchors[1].start())
        self.assertLess(anchors[1].start(), anchors[2].start())
        fault = f'  file(RENAME "{third_source.as_posix()}" "{held.as_posix()}")\n'
        anchor = anchors[2].start()
        script = script[:anchor] + fault + script[anchor:]
        install_script = build / "cmake_install.cmake"
        install_script.write_text(script, encoding="utf-8")
        prefix = self.new_path("partial prefix")
        args = [self.cmake, f"-DCMAKE_INSTALL_PREFIX={prefix.as_posix()}",
                "-DCMAKE_INSTALL_COMPONENT=StarterRegistrations",
                f"-DCMAKE_INSTALL_CONFIG_NAME={self.config}",
                "-DCMAKE_INSTALL_LOCAL_ONLY=1", "-P", install_script]
        expected = {name: self.originals[SOURCE_PACK / "entries" / name]
                    for name in (first, second, third)}
        failed = invoke(args, self.work)
        failure_output = diagnostic(failed)
        # Retain the genuine child error even if a later filesystem assertion
        # fails; the old size-limit test hid its eventual nonzero diagnostic.
        print(f"registration late-copy fault (exit {failed.returncode}):\n{failure_output}")
        self.assertGreater(failed.returncode, 0, failure_output)
        self.assertIn("preflight passed; copying begins", failure_output)
        self.assertIn("file INSTALL cannot find", " ".join(failure_output.split()), failure_output)
        self.assertIn(third, " ".join(failure_output.split()), failure_output)
        self.assertFalse(third_source.exists(), failure_output)
        self.assertTrue(held.is_file(), failure_output)
        self.assertEqual(held.read_bytes(), expected[third], failure_output)
        retained = snapshot(prefix)
        self.assertIsInstance(retained, dict, failure_output)
        files = {name: item[2] for name, item in retained.items() if item[0] == "file"}
        expected_files = {(self.datadir / PACKAGE / "entries" / name).as_posix(): expected[name]
                          for name in (first, second)}
        self.assertEqual(files, expected_files, failure_output)
        directories = {"."}
        for name in expected_files:
            directories.update(parent.as_posix() for parent in Path(name).parents)
        self.assertEqual({name for name, item in retained.items() if item[0] == "directory"},
                         directories, failure_output)
        self.assertFalse(any(item[0] in ("link", "special") for item in retained.values()),
                         failure_output)
        # Restore every private input so the unchanged second preflight must
        # refuse the existing package, rather than the deliberately absent file.
        held.rename(third_source)
        self.assertEqual(snapshot(source), original_source, failure_output)
        refused = invoke(args, self.work)
        refusal_output = diagnostic(refused)
        print(f"registration partial-package reinstall (exit {refused.returncode}):\n{refusal_output}")
        self.assertNotEqual(refused.returncode, 0, refusal_output)
        self.assertIn("destination already exists", refusal_output)
        self.assertNotIn("preflight passed; copying begins", refusal_output)
        self.assertEqual(snapshot(prefix), retained, refusal_output)
        self.assertEqual(snapshot(source), original_source, refusal_output)

    def test_multiconfig_copies_selected_artifact_without_building(self):
        ninja = (self.make_program if self.make_program and "ninja" in Path(self.make_program).name.lower()
                 else shutil.which("ninja"))
        if ninja:
            generator, make_program = "Ninja Multi-Config", ninja
        elif self.generator and (self.generator.startswith("Visual Studio") or self.generator == "Xcode"):
            generator, make_program = self.generator, self.make_program
        else:
            self.skipTest("No available multi-configuration generator")
        project = self.project("multiple configurations", generator=generator, make_program=make_program)
        for config in ("Release", "Debug"):
            with withheld(project.binaries["Debug" if config == "Release" else "Release"]):
                prefix = self.new_path(config)
                self.ok(project.install(prefix, "RegistrationTools", config=config))
                self.exact(prefix, project.bindir, project.datadir, ["RegistrationTools"])
        prefix = self.new_path("unknown configuration")
        result = project.install(prefix, "RegistrationTools", config="NotConfigured")
        self.assertNotEqual(result.returncode, 0, diagnostic(result))
        self.assertIn("unknown configuration", diagnostic(result))
        self.assertFalse(prefix.exists())

    def test_root_rules_relocate_and_native_list_inspect_materialize(self):
        source, build = self.new_path("root source copy"), self.new_path("root build copy")
        copy_source(source)
        relative_binary = self.executable.relative_to(self.build)
        binary_copy = build / relative_binary
        binary_copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.executable, binary_copy)
        # Disable subdirectory dispatch; these two components are top-level.
        # Only filesystem roots are substituted in otherwise unchanged rules.
        script = self.script_text.replace(self.build.as_posix(), build.as_posix())
        script = script.replace(ROOT.as_posix(), source.as_posix())
        install_script = build / "cmake_install.cmake"
        install_script.write_text(script, encoding="utf-8")
        prefix, moved = self.new_path("original prefix"), self.new_path("relocated prefix é音")
        for component in COMPONENTS:
            self.ok(invoke([self.cmake, f"-DCMAKE_INSTALL_PREFIX={prefix.as_posix()}",
                            f"-DCMAKE_INSTALL_COMPONENT={component}",
                            f"-DCMAKE_INSTALL_CONFIG_NAME={self.config}",
                            "-DCMAKE_INSTALL_LOCAL_ONLY=1", "-P", install_script], self.work))
        self.exact(prefix, self.bindir, self.datadir, COMPONENTS)
        prefix.rename(moved)
        executable, package = self.exact(moved, self.bindir, self.datadir, COMPONENTS)
        shutil.rmtree(source)
        shutil.rmtree(build)
        self.assertFalse(source.exists() or build.exists() or prefix.exists())
        foreign = self.new_path("unrelated working directory")
        foreign.mkdir()
        before = snapshot(moved)

        def cli(*args):
            result = invoke([executable, *args], foreign)
            self.ok(result)
            self.assertEqual(result.stderr, b"")
            self.assertEqual(result.stdout.count(b"\n"), 1)
            report = json.loads(result.stdout)
            self.assertEqual(report["schema"], "hammond-registration-cli-v1")
            self.assertEqual(report["outcome"], "ok")
            return report

        entries = package / "entries"
        report = cli("list", "--library", entries)
        self.assertTrue(report["catalog"]["complete"])
        self.assertEqual({row["key"] for row in report["catalog"]["entries"]}, set(ENTRIES))
        self.assertEqual(len(report["catalog"]["entries"]), 24)
        self.assertEqual(list(foreign.iterdir()), [])
        current = foreign / "current.controls"
        current.write_bytes(re.sub(rb"(?m)^expression [^\n]+$", b"expression 0.8125",
                                   (entries / ENTRIES[0]).read_bytes()))
        destination = foreign / "explicit prepared destination"
        for name in ENTRIES:
            with self.subTest(entry=name):
                payload = (entries / name).read_bytes()
                scope = "registration" if name.endswith(".b3registration") else "performance"
                inspected = cli("inspect", "--library", entries, "--key", name)
                self.assertEqual(inspected["entry"]["scope"], scope)
                self.assertEqual(inspected["entry"]["canonical_controls"].encode("ascii"), payload)
                output_name = Path(name).stem + (" Reg" if scope == "registration" else " Perf")
                args = ["materialize", "--library", entries, "--key", name,
                        "--destination", destination, "--name", output_name]
                if scope == "registration":
                    args += ["--current", current]
                prepared = cli(*args)
                self.assertTrue(prepared["committed"])
                self.assertEqual(prepared["save"]["scope"], "performance")
                expected = (re.sub(rb"(?m)^expression [^\n]+$", b"expression 0.8125", payload)
                            if scope == "registration" else payload)
                self.assertEqual((destination / (output_name + ".b3performance")).read_bytes(), expected)
        self.assertEqual(len(list(destination.iterdir())), 24)
        self.assertEqual(snapshot(moved), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
