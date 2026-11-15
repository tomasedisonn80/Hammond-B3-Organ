#!/usr/bin/env python3
"""Qualify the real contact-reference install rules without a native build.

Only a small private source copy and a LANGUAGES NONE CMake wrapper are changed.
The expected inventory comes from the distribution contract, independently of
the installer. Relocated commands run with no private source/build remaining.
This suite admits the complete study inputs but does not run its 36x4 numerics.
"""

from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path("hammond-b3-organ/contact-reference")
FIXTURES = Path("data/contact-switching/reference-v1")
TOOLS = (
    "fractional_contact_reference.py", "contact_switching_io.py",
    "contact_switching_reference.py", "contact_switching_oracle.py",
    "contact_switching_study.py", "make_contact_switching_fixtures.py",
)
DOCUMENTS = (
    "FRACTIONAL_CONTACT_REFERENCE.md", "CONTACT_SWITCHING_VALIDATION.md",
    "CONTACT_SWITCHING_GUIDE.md", "CONTACT_REFERENCE_INSTALL.md",
)
PAYLOAD = (
    *("tools/" + name for name in TOOLS),
    *("docs/" + name for name in DOCUMENTS),
    *((FIXTURES / f"F{recipe:02d}-{rate}-v1.json").as_posix()
      for recipe in range(12) for rate in (44100, 48000, 96000)),
    (FIXTURES / "manifest.json").as_posix(),
    (FIXTURES / "probes.json").as_posix(),
)
INSTALLERS = ("cmake/InstallHammondTools.cmake", "cmake/InstallContactReferenceTools.cmake")
OTHER_COMPONENTS = ("OfflineTools", "Standalone", "CaptureTools", "CrossoverTools",
                    "SourceLeakageTools", "NativeVST3")
SENTINEL = b"unrelated component remains available\n"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def environment():
    result = {name: value for name, value in os.environ.items()
              if not name.upper().startswith("HAMMOND_")}
    for name in ("DESTDIR", "CMAKE_INSTALL_MODE", "PYTHONPATH", "PYTHONHOME",
                 "CMAKE_GENERATOR", "CMAKE_GENERATOR_PLATFORM",
                 "CMAKE_GENERATOR_TOOLSET", "CMAKE_GENERATOR_INSTANCE"):
        result.pop(name, None)
    result["PYTHONDONTWRITEBYTECODE"] = "1"
    return result


def invoke(command, cwd, env=None):
    return subprocess.run(list(map(str, command)), cwd=cwd,
                          env=environment() if env is None else env,
                          capture_output=True, check=False, timeout=45)


def diagnostic(result):
    return (result.stdout + result.stderr).decode("utf-8", errors="replace")


def state(root):
    """Capture bytes, permissions, empty directories and links without following links."""
    def entry(path):
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            return ("link", os.readlink(path))
        if stat.S_ISDIR(mode):
            return ("directory", stat.S_IMODE(mode))
        if stat.S_ISREG(mode):
            return ("file", stat.S_IMODE(mode), path.read_bytes())
        return ("special", mode)

    if root.is_symlink():
        return entry(root)
    if not root.exists():
        return None
    if not root.is_dir():
        return entry(root)
    result = {".": entry(root)}
    for directory, subdirs, names in os.walk(root, followlinks=False):
        for name in subdirs + names:
            path = Path(directory) / name
            result[path.relative_to(root).as_posix()] = entry(path)
    return result


@contextmanager
def withheld(path):
    """Temporarily replace an owned private input, including its original mode."""
    backup = path.with_name(path.name + ".held-by-contact-install-test")
    path.rename(backup)
    try:
        yield backup
    finally:
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.is_dir():
            path.rmdir()
        backup.rename(path)


class PrivateProject:
    def __init__(self, root, cmake, *, generator=None, make_program=None,
                 configuration="Release", datadir="share"):
        self.root, self.cmake = root, cmake
        self.source, self.build = root / "source", root / "build"
        self.generator, self.make_program = generator, make_program
        self.configuration, self.datadir_argument = configuration, datadir
        self.datadir = Path(datadir.replace("\\", "/"))
        root.mkdir()
        self.originals = {name: (ROOT / name).read_bytes() for name in PAYLOAD}
        for name in (*PAYLOAD, *INSTALLERS):
            destination = self.source / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        # These plausible siblings must never leak into the explicit inventory.
        for name in ("tools/unlisted.py", "docs/unlisted.md",
                     (FIXTURES / "unlisted.json").as_posix(), "reports/draft.json"):
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"not a distribution input\n")
        (self.source / "sentinel.txt").write_bytes(SENTINEL)
        cmakelists = (
            'cmake_minimum_required(VERSION 3.21)\n'
            'project(ContactReferenceInstallFixture LANGUAGES NONE)\n'
            'include(cmake/InstallHammondTools.cmake)\n'
            # Set after GNUInstallDirs so an explicitly empty fixture value is
            # passed to the actual shared validator rather than defaulted away.
            'set(CMAKE_INSTALL_DATADIR "${FIXTURE_DATADIR}")\n'
            'include(cmake/InstallContactReferenceTools.cmake)\n'
        )
        for component in OTHER_COMPONENTS:
            exclusion = "" if component == "OfflineTools" else " EXCLUDE_FROM_ALL"
            cmakelists += (
                f'install(FILES sentinel.txt DESTINATION legacy/{component} '
                f'COMPONENT {component}{exclusion})\n'
            )
        (self.source / "CMakeLists.txt").write_text(cmakelists, encoding="utf-8")
        self.configured = self.configure()

    def configure(self, *, build=None, datadir=None):
        command = [self.cmake, "-S", self.source, "-B", build or self.build,
                   "-Wno-dev", "-DCMAKE_BUILD_TYPE=Release",
                   "-DCMAKE_CONFIGURATION_TYPES=Debug;Release",
                   f"-DFIXTURE_DATADIR:STRING={self.datadir_argument if datadir is None else datadir}"]
        if self.generator:
            command += ["-G", self.generator]
        if self.make_program:
            command += [f"-DCMAKE_MAKE_PROGRAM:FILEPATH={self.make_program}"]
        return invoke(command, self.root)

    def install(self, prefix, *, component="ContactReferenceTools", env=None,
                configuration=None):
        command = [self.cmake, "--install", self.build, "--prefix", prefix,
                   "--config", configuration or self.configuration]
        if component is not None:
            command += ["--component", component]
        return invoke(command, self.root, env)

    def package(self, prefix):
        return prefix / self.datadir / PACKAGE


class ContactReferenceInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        selected = os.environ.get("HAMMOND_TEST_CMAKE") or shutil.which("cmake")
        cmake = shutil.which(selected) if selected else None
        if not cmake or not Path(cmake).is_file():
            raise RuntimeError("ContactReferenceTools acceptance requires CMake 3.21+; "
                               "set HAMMOND_TEST_CMAKE or put cmake on PATH")
        cls.cmake = Path(cmake).resolve()
        cls.generator = os.environ.get("HAMMOND_TEST_CMAKE_GENERATOR")
        cls.make_program = os.environ.get("HAMMOND_TEST_CMAKE_MAKE_PROGRAM")
        if cls.make_program and cls.make_program.endswith("-NOTFOUND"):
            cls.make_program = None
        cls.configuration = os.environ.get("HAMMOND_TEST_CONFIG") or "Release"
        if len(PAYLOAD) != 48 or len(set(PAYLOAD)) != 48:
            raise AssertionError("Independent distribution inventory must contain 48 distinct files")
        cls.live_hashes = {ROOT / name: sha((ROOT / name).read_bytes())
                           for name in (*PAYLOAD, *INSTALLERS)}
        cls.temporary = tempfile.TemporaryDirectory(prefix="contact-reference-install-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name).resolve()
        cls.project = PrivateProject(cls.root / "base", cls.cmake,
                                     generator=cls.generator, make_program=cls.make_program,
                                     configuration=cls.configuration)
        if cls.project.configured.returncode:
            raise RuntimeError("Private install configure failed:\n" + diagnostic(cls.project.configured))

    @classmethod
    def tearDownClass(cls):
        for path, expected in cls.live_hashes.items():
            if sha(path.read_bytes()) != expected:
                raise AssertionError("Read-only checkout input changed during acceptance: " + str(path))

    def setUp(self):
        # Per-method cleanup bounds peak scratch use even for all 48 fault cases.
        self.work = self.root / self._testMethodName
        self.work.mkdir()
        self.addCleanup(shutil.rmtree, self.work)
        self.counter = 0

    def fresh(self, label):
        self.counter += 1
        return self.work / f"{self.counter:03d}-{label}"

    def success(self, result):
        self.assertEqual(result.returncode, 0, diagnostic(result))

    def new_project(self, label, **options):
        options.setdefault("generator", self.generator)
        options.setdefault("make_program", self.make_program)
        options.setdefault("configuration", self.configuration)
        project = PrivateProject(self.fresh(label), self.cmake, **options)
        self.success(project.configured)
        return project

    def rejected(self, project, prefix, *, env=None, observed=None):
        observed = prefix if observed is None else observed
        before = state(observed)
        result = project.install(prefix, env=env)
        self.assertNotEqual(result.returncode, 0, diagnostic(result))
        self.assertIn("ContactReferenceTools", diagnostic(result))
        self.assertEqual(state(observed), before, "Rejected install changed destination contents")
        return result

    def installed(self, project, prefix, *, extra_files=None, extra_dirs=()):
        expected = {project.datadir / PACKAGE / name: data
                    for name, data in project.originals.items()}
        expected.update({Path(name): data for name, data in (extra_files or {}).items()})
        directories = {Path("."), *(Path(name) for name in extra_dirs)}
        for name in (*expected, *tuple(directories)):
            directories.update(name.parents)
        actual = state(prefix)
        self.assertIsInstance(actual, dict, "Successful install did not create an ordinary prefix")
        self.assertEqual(set(actual), {p.as_posix() for p in (*expected, *directories)},
                         "Component created missing/extra files, directories or links")
        for name, data in expected.items():
            with self.subTest(installed=name.as_posix()):
                observed = actual[name.as_posix()]
                self.assertEqual(observed[0], "file", "Payload must be an ordinary copied file")
                self.assertEqual(observed[2], data, "Installed bytes differ from the source snapshot")
        for name in directories:
            self.assertEqual(actual[name.as_posix()][0], "directory")
        package = project.package(prefix)
        for name in PAYLOAD:
            if (project.source / name).exists():
                self.assertFalse(os.path.samefile(package / name, project.source / name),
                                 "Payload aliases its source instead of being an independent copy")
        return package

    def make_link(self, path, target, *, directory=False):
        try:
            path.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest("Symlink creation unavailable on this host: " + str(error))

    def test_exact_48_file_inventory_and_copy_modes(self):
        for mode in (None, "", "COPY"):
            with self.subTest(mode=mode):
                prefix = self.fresh("prefix with spaces-é音")
                env = environment()
                if mode is not None:
                    env["CMAKE_INSTALL_MODE"] = mode
                self.success(self.project.install(prefix, env=env))
                self.installed(self.project, prefix)

    @unittest.skipIf(os.name == "nt", "POSIX permission bits are not a Windows file-mode contract")
    def test_all_payload_files_install_as_nonexecutable_0644(self):
        sources = [self.project.source / name for name in PAYLOAD]
        modes = {path: stat.S_IMODE(path.stat().st_mode) for path in sources}
        try:
            for path in sources:
                path.chmod(0o755)
            prefix = self.fresh("permission normalization")
            self.success(self.project.install(prefix))
            package = self.installed(self.project, prefix)
            for name in PAYLOAD:
                with self.subTest(payload=name):
                    self.assertEqual(stat.S_IMODE((package / name).stat().st_mode), 0o644)
        finally:
            for path, mode in modes.items():
                path.chmod(mode)

    def test_moved_package_runs_cli_and_full_study_admission_without_source_or_build(self):
        project = self.new_project("relocation fixture")
        prefix, moved = self.fresh("original prefix with spaces"), self.fresh("moved prefix-é音")
        foreign = self.fresh("neutral working directory")
        foreign.mkdir()
        for name in TOOLS:
            (foreign / name).write_text('raise AssertionError("loaded a working-directory module")\n',
                                        encoding="utf-8")
        self.success(project.install(prefix))
        prefix.rename(moved)
        package = self.installed(project, moved)
        shutil.rmtree(project.source)
        shutil.rmtree(project.build)
        self.assertFalse(prefix.exists())
        self.assertFalse(project.source.exists())
        self.assertFalse(project.build.exists())
        before = state(moved)
        python = [sys.executable, "-B", "-E", "-s", "-S"]
        fixture = "F02-48000-v1.json"
        output = foreign / "single fixture report.json"
        result = invoke([*python, package / "tools/contact_switching_reference.py",
                         "--input", package / FIXTURES / fixture, "--factor", "256",
                         "--output", output], foreign)
        self.success(result)
        self.assertEqual(result.stdout, b"")
        facts = json.loads(output.read_bytes())
        self.assertEqual((facts["schema_version"], facts["fixture_id"], facts["evidence_class"]),
                         (1, "F02-48000-v1", "synthetic"))
        self.assertEqual((facts["sample_rate_hz"], facts["frames"], facts["factor"], facts["first_frame"]),
                         (48000, 256, 256, -16))
        self.assertEqual(len(facts["samples"]), 289)
        self.assertTrue(all(math.isfinite(value) for value in facts["samples"]))
        self.assertTrue(any(value != 0 for value in facts["samples"]))
        self.assertEqual(facts["input_sha256"], sha(project.originals[(FIXTURES / fixture).as_posix()]))
        self.assertEqual(facts["implementation_sha256"],
                         {"tools/" + name: sha(project.originals["tools/" + name]) for name in TOOLS[:3]})

        # The genuine command admits all 36 fixtures, probes and source hashes
        # before its fresh-report check. This diagnostic therefore proves full
        # admission/imports without repeating the separately qualified numerics.
        prior = foreign / "prior study.json"
        prior.write_bytes(b"retained earlier experiment\n")
        before_outputs = state(foreign)
        result = invoke([*python, package / "tools/contact_switching_study.py",
                         "--fixtures", package / FIXTURES, "--output", prior], foreign)
        self.assertEqual(result.returncode, 2, diagnostic(result))
        self.assertEqual(result.stdout, b"")
        self.assertIn("study output already exists; use a distinct report path", diagnostic(result))
        self.assertEqual(state(foreign), before_outputs)
        self.assertEqual(state(moved), before, "Installed execution modified its package")

    def test_custom_relative_datadirs_preserve_layout(self):
        for datadir in ("resources/reference data", "resources\\reference data", "."):
            with self.subTest(datadir=datadir):
                project = self.new_project("custom data", datadir=datadir)
                prefix = self.fresh("custom prefix")
                self.success(project.install(prefix))
                self.installed(project, prefix)
                self.assertFalse((prefix / "share").exists())

    def test_invalid_datadirs_reject_at_configuration(self):
        invalid = ("", "/absolute", "C:/absolute", "C:relative", "C:\\absolute",
                   "\\absolute", "..", "child/../escape", "child\\..\\escape", "one;two")
        for datadir in invalid:
            with self.subTest(datadir=datadir):
                result = self.project.configure(build=self.fresh("invalid configure"), datadir=datadir)
                self.assertNotEqual(result.returncode, 0, diagnostic(result))
                self.assertIn("ContactReferenceTools", diagnostic(result))
                self.assertIn("nonempty relative CMAKE_INSTALL_DATADIR", diagnostic(result))

    def test_every_missing_input_preserves_absent_and_existing_prefixes(self):
        fresh = self.fresh("must stay absent")
        existing = self.fresh("unrelated existing prefix")
        existing.mkdir()
        (existing / "keep.bin").write_bytes(b"preserve existing bytes\x00\r\n")
        for name in PAYLOAD:
            with self.subTest(input=name), withheld(self.project.source / name):
                for prefix in (fresh, existing):
                    result = self.rejected(self.project, prefix)
                    self.assertIn(Path(name).name, diagnostic(result))
        self.assertFalse(fresh.exists())

    def test_every_empty_or_directory_input_rejects_before_prefix_creation(self):
        prefix = self.fresh("must stay absent")
        for name in PAYLOAD:
            path = self.project.source / name
            for kind in ("empty", "directory"):
                with self.subTest(input=name, kind=kind), withheld(path):
                    path.write_bytes(b"") if kind == "empty" else path.mkdir()
                    self.rejected(self.project, prefix)
                    self.assertFalse(prefix.exists())

    def test_every_linked_source_leaf_rejects_before_copy(self):
        prefix = self.fresh("must stay absent")
        for name in PAYLOAD:
            path = self.project.source / name
            with self.subTest(input=name), withheld(path) as original:
                self.make_link(path, original)
                self.rejected(self.project, prefix)
                self.assertFalse(prefix.exists())
        path = self.project.source / PAYLOAD[-1]
        with withheld(path):
            self.make_link(path, self.fresh("absent link target"))
            self.rejected(self.project, prefix)

    def test_all_source_ancestors_inside_source_root_reject_symlinks(self):
        prefix = self.fresh("must stay absent")
        for relative in ("tools", "docs", "data", "data/contact-switching",
                         FIXTURES.as_posix(), "."):
            path = self.project.source / relative
            with self.subTest(ancestor=relative), withheld(path) as original:
                self.make_link(path, original, directory=True)
                result = self.rejected(self.project, prefix)
                self.assertIn("source ancestor", diagnostic(result))
                self.assertFalse(prefix.exists())

    def test_noncopy_install_modes_reject_before_prefix_creation(self):
        for mode in ("SYMLINK", "ABS_SYMLINK", "REL_SYMLINK", "SYMLINK_OR_COPY",
                     "ABS_SYMLINK_OR_COPY", "REL_SYMLINK_OR_COPY", "copy", "COPY ", "INVALID"):
            with self.subTest(mode=mode):
                env = environment()
                env["CMAKE_INSTALL_MODE"] = mode
                prefix = self.fresh("must stay absent")
                result = self.rejected(self.project, prefix, env=env)
                self.assertIn("CMAKE_INSTALL_MODE", diagnostic(result))
                self.assertFalse(prefix.exists())

    def test_existing_package_files_directories_and_installed_package_are_preserved(self):
        for kind in ("file", "empty_directory", "populated_directory", "installed"):
            with self.subTest(kind=kind):
                prefix = self.fresh("existing package")
                package = self.project.package(prefix)
                if kind == "installed":
                    self.success(self.project.install(prefix))
                    self.installed(self.project, prefix)
                else:
                    package.parent.mkdir(parents=True)
                    if kind == "file":
                        package.write_bytes(b"existing package-path file\n")
                    else:
                        package.mkdir()
                        if kind == "populated_directory":
                            (package / "keep.bin").write_bytes(b"preserve prior installation\n")
                result = self.rejected(self.project, prefix)
                self.assertIn("destination already exists", diagnostic(result))

    def test_destination_file_ancestors_are_preserved(self):
        for relative in (".", "share", "share/hammond-b3-organ"):
            with self.subTest(ancestor=relative):
                prefix = self.fresh("obstructed prefix")
                path = prefix / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"unrelated existing file\n")
                result = self.rejected(self.project, prefix)
                self.assertIn("destination ancestor", diagnostic(result))

    def test_destination_links_cannot_redirect_copy(self):
        for relative in (".", "share", "share/hammond-b3-organ",
                         "share/hammond-b3-organ/contact-reference"):
            for kind in ("directory", "file", "dangling"):
                with self.subTest(location=relative, target=kind):
                    prefix, target = self.fresh("linked prefix"), self.fresh("outside link target")
                    target.mkdir()
                    (target / "keep.bin").write_bytes(b"outside target remains untouched\n")
                    before = state(target)
                    linked = target if kind == "directory" else target / ("keep.bin" if kind == "file" else "absent")
                    path = prefix / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    self.make_link(path, linked, directory=kind != "file")
                    self.rejected(self.project, prefix)
                    self.assertEqual(state(target), before, "Rejected link redirected a write")

    def test_ordinary_existing_prefix_directories_are_usable(self):
        prefix = self.fresh("shared prefix")
        (prefix / "share/hammond-b3-organ").mkdir(parents=True)
        (prefix / "keep empty").mkdir()
        (prefix / "keep.bin").write_bytes(b"other installed product\n")
        self.success(self.project.install(prefix))
        self.installed(self.project, prefix, extra_files={"keep.bin": b"other installed product\n"},
                       extra_dirs=("keep empty",))

    def test_default_and_other_components_do_not_install_or_preflight_contact_payload(self):
        # An invalid contact source must not prevent an unrelated selected rule.
        with withheld(self.project.source / PAYLOAD[-1]):
            for component in (None, *OTHER_COMPONENTS, "Unknown"):
                with self.subTest(component=component):
                    prefix = self.fresh("other component")
                    self.success(self.project.install(prefix, component=component))
                    expected_component = "OfflineTools" if component is None else component
                    if component == "Unknown":
                        self.assertIsNone(state(prefix))
                    else:
                        expected_file = f"legacy/{expected_component}/sentinel.txt"
                        observed = state(prefix)
                        self.assertEqual(set(observed), {".", "legacy", f"legacy/{expected_component}",
                                                         expected_file})
                        self.assertEqual(observed[expected_file][2], SENTINEL)
                    self.assertFalse(self.project.package(prefix).exists())

    def test_multi_configuration_install_needs_no_native_target(self):
        ninja = (self.make_program if self.make_program and
                 "ninja" in Path(self.make_program).name.lower() else shutil.which("ninja"))
        if ninja:
            generator, make_program = "Ninja Multi-Config", ninja
        elif self.generator and (self.generator.startswith("Visual Studio") or self.generator == "Xcode"):
            generator, make_program = self.generator, self.make_program
        else:
            self.skipTest("No available multi-configuration generator for a private fixture")
        project = self.new_project("multi configuration", generator=generator, make_program=make_program)
        for configuration in ("Release", "Debug"):
            with self.subTest(configuration=configuration):
                prefix = self.fresh(configuration + " prefix")
                self.success(project.install(prefix, configuration=configuration))
                self.installed(project, prefix)

    @unittest.skipIf(os.name == "nt", "CMake DESTDIR staging is a POSIX facility")
    def test_destdir_install_and_rejections_use_the_effective_staged_prefix(self):
        stage, prefix = self.fresh("stage with spaces"), self.fresh("logical prefix")
        staged_prefix = stage / str(prefix).lstrip("/")
        env = environment()
        env["DESTDIR"] = str(stage)
        self.success(self.project.install(prefix, env=env))
        self.installed(self.project, staged_prefix)
        self.assertFalse(prefix.exists())
        self.rejected(self.project, prefix, env=env, observed=stage)
        stage2, prefix2 = self.fresh("obstructed stage"), self.fresh("logical prefix")
        staged_prefix2 = stage2 / str(prefix2).lstrip("/")
        staged_prefix2.parent.mkdir(parents=True)
        staged_prefix2.write_bytes(b"staged prefix obstruction\n")
        env["DESTDIR"] = str(stage2)
        self.rejected(self.project, prefix2, env=env, observed=stage2)
        self.assertFalse(prefix2.exists())
        stage3, prefix3 = self.fresh("must stay absent stage"), self.fresh("logical prefix")
        env["DESTDIR"] = str(stage3)
        with withheld(self.project.source / PAYLOAD[-1]):
            self.rejected(self.project, prefix3, env=env, observed=stage3)
        self.assertFalse(stage3.exists())
        self.assertFalse(prefix3.exists())


if __name__ == "__main__":
    unittest.main()
