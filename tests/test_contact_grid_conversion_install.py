#!/usr/bin/env python3
"""Independent acceptance of the explicit five-file conversion distribution.

Exercise real CMake install scripts in private LANGUAGES NONE projects. The
inventories below come from the two distribution contracts, not installer
variables or the A23 smoke. No native build, repository mutation or oracle
import is involved. Numerical correctness has separate acceptance suites.
"""

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = "ContactGridConversionTools"
PACKAGE = Path("hammond-b3-organ/contact-grid-conversion")
PAYLOAD = (
    "tools/contact_grid_conversion.py",
    "tools/convert_contact_grid.py",
    "tools/contact_switching_io.py",
    "tools/fractional_contact_reference.py",
    "docs/CONTACT_GRID_CONVERSION_CONTRACT.md",
)
REFERENCE = (
    *("tools/" + name for name in (
        "fractional_contact_reference.py", "contact_switching_io.py",
        "contact_switching_reference.py", "contact_switching_oracle.py",
        "contact_switching_study.py", "make_contact_switching_fixtures.py")),
    *("docs/" + name for name in (
        "FRACTIONAL_CONTACT_REFERENCE.md", "CONTACT_SWITCHING_VALIDATION.md",
        "CONTACT_SWITCHING_GUIDE.md", "CONTACT_REFERENCE_INSTALL.md")),
    *(f"data/contact-switching/reference-v1/F{recipe:02d}-{rate}-v1.json"
      for recipe in range(12) for rate in (44100, 48000, 96000)),
    "data/contact-switching/reference-v1/manifest.json",
    "data/contact-switching/reference-v1/probes.json",
)
MODULES = (
    "cmake/InstallHammondTools.cmake",
    "cmake/InstallContactGridConversionTools.cmake",
    "cmake/InstallContactReferenceTools.cmake",
)
SENTINEL = b"unrelated default component\x00\r\n"
EVENTS = []
FACTS = {}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def child_environment():
    env = dict(os.environ)
    for key in tuple(env):
        if key.upper().startswith(("HAMMOND_", "CMAKE_GENERATOR")) or key.upper() in (
                "DESTDIR", "CMAKE_INSTALL_MODE", "PYTHONPATH", "PYTHONHOME"):
            env.pop(key)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def process(label, args, cwd, env=None):
    started = time.monotonic()
    result = subprocess.run(list(map(str, args)), cwd=cwd,
                            env=child_environment() if env is None else env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=45, check=False)
    EVENTS.append({"label": label, "argv": list(map(str, args)), "cwd": str(cwd),
                   "returncode": result.returncode, "seconds": time.monotonic() - started,
                   "stdout_bytes": len(result.stdout), "stdout_sha256": digest(result.stdout),
                   "stderr_bytes": len(result.stderr), "stderr_sha256": digest(result.stderr),
                   "diagnostic": diagnostic(result)[:4096] if result.returncode else ""})
    return result


def diagnostic(result):
    return (result.stdout + result.stderr).decode("utf-8", "replace")


def snapshot(root):
    """Observe links themselves, every directory, modes and exact file bytes."""
    def one(path):
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
    entries = {".": one(root)}
    if entries["."][0] == "directory":
        for directory, directories, files in os.walk(root, followlinks=False):
            for name in directories + files:
                path = Path(directory) / name
                entries[path.relative_to(root).as_posix()] = one(path)
    return entries


@contextmanager
def removed(path):
    backup = path.with_name(path.name + ".a30-held")
    path.rename(backup)
    try:
        yield backup
    finally:
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.is_dir():
            path.rmdir()
        backup.rename(path)


class InstallProject:
    def __init__(self, folder, cmake, generator, make_program, config, datadir="share"):
        self.folder, self.cmake = folder, cmake
        self.source, self.build = folder / "source", folder / "build"
        self.generator, self.make_program, self.config = generator, make_program, config
        self.datadir = Path(datadir.replace("\\", "/"))
        self.data = {name: (ROOT / name).read_bytes() for name in (*PAYLOAD, *REFERENCE)}
        for name in (*self.data, *MODULES):
            target = self.source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
        # Neither plausible sibling source nor cached code is part of the package.
        for name in ("tools/unlisted.py", "tools/__pycache__/unlisted.pyc", "docs/unlisted.md"):
            target = self.source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"excluded from distribution\n")
        (self.source / "sentinel.bin").write_bytes(SENTINEL)
        (self.source / "CMakeLists.txt").write_text(
            'cmake_minimum_required(VERSION 3.21)\n'
            'project(IndependentConversionInstall LANGUAGES NONE)\n'
            'include(cmake/InstallHammondTools.cmake)\n'
            'set(CMAKE_INSTALL_DATADIR "${TEST_DATADIR}")\n'
            'include(cmake/InstallContactGridConversionTools.cmake)\n'
            'include(cmake/InstallContactReferenceTools.cmake)\n'
            'install(FILES sentinel.bin DESTINATION unrelated COMPONENT Sentinel)\n',
            encoding="utf-8")
        self.configured = self.configure(datadir)

    def configure(self, datadir, build=None):
        args = [self.cmake, "-S", self.source, "-B", build or self.build, "-Wno-dev",
                "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_CONFIGURATION_TYPES=Release;Debug",
                f"-DTEST_DATADIR:STRING={datadir}"]
        if self.generator:
            args += ["-G", self.generator]
        if self.make_program:
            args += [f"-DCMAKE_MAKE_PROGRAM:FILEPATH={self.make_program}"]
        return process("configure", args, self.folder)

    def install(self, prefix, component=COMPONENT, env=None, config=None):
        args = [self.cmake, "--install", self.build, "--prefix", prefix,
                "--config", config or self.config]
        if component is not None:
            args += ["--component", component]
        return process("install:" + str(component), args, self.folder, env)

    def package(self, prefix):
        return prefix / self.datadir / PACKAGE


class ContactGridConversionInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        selected = os.environ.get("HAMMOND_TEST_CMAKE") or shutil.which("cmake")
        executable = shutil.which(selected) if selected else None
        if not executable or not Path(executable).is_file():
            raise RuntimeError("Installed conversion acceptance needs CMake 3.21+; "
                               "set HAMMOND_TEST_CMAKE or put cmake on PATH")
        cls.cmake = Path(executable).resolve()
        cls.generator = os.environ.get("HAMMOND_TEST_CMAKE_GENERATOR")
        cls.make_program = os.environ.get("HAMMOND_TEST_CMAKE_MAKE_PROGRAM")
        if cls.make_program and cls.make_program.endswith("-NOTFOUND"):
            cls.make_program = None
        cls.config = os.environ.get("HAMMOND_TEST_CONFIG") or "Release"
        if len(PAYLOAD) != 5 or len(set(PAYLOAD)) != 5 or len(set(REFERENCE)) != 48:
            raise AssertionError("Independent five/48-file contracts have changed")
        cls.watched = {name: digest((ROOT / name).read_bytes())
                       for name in (*PAYLOAD, *REFERENCE, *MODULES)}
        FACTS["source_sha256"] = cls.watched
        FACTS["cmake"] = str(cls.cmake)
        FACTS["generator"] = cls.generator
        cls.temporary = tempfile.TemporaryDirectory(prefix="a30-conversion-install-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name).resolve()
        cls.base = InstallProject(cls.root / "base", cls.cmake, cls.generator,
                                  cls.make_program, cls.config)
        if cls.base.configured.returncode:
            raise RuntimeError("Private fixture configure failed:\n" + diagnostic(cls.base.configured))

    @classmethod
    def tearDownClass(cls):
        changed = [name for name, expected in cls.watched.items()
                   if digest((ROOT / name).read_bytes()) != expected]
        FACTS["changed_checkout_inputs"] = changed
        if changed:
            raise AssertionError("Read-only checkout inputs changed: " + repr(changed))

    def setUp(self):
        self.work = self.root / self._testMethodName
        self.work.mkdir()
        self.addCleanup(shutil.rmtree, self.work)
        self.number = 0

    def new_path(self, label):
        self.number += 1
        return self.work / f"{self.number:03d}-{label}"

    def ok(self, result):
        self.assertEqual(result.returncode, 0, diagnostic(result))

    def project(self, label, **options):
        values = dict(generator=self.generator, make_program=self.make_program,
                      config=self.config)
        values.update(options)
        project = InstallProject(self.new_path(label), self.cmake, **values)
        self.ok(project.configured)
        return project

    def preserve_on_refusal(self, project, prefix, *, env=None, observed=None):
        observed = prefix if observed is None else observed
        prior = snapshot(observed)
        result = project.install(prefix, env=env)
        self.assertNotEqual(result.returncode, 0, diagnostic(result))
        self.assertIn(COMPONENT, diagnostic(result))
        self.assertEqual(snapshot(observed), prior, "Preflight refusal changed destination")
        return result

    def exact_package(self, project, prefix, *, payload=PAYLOAD, package=PACKAGE):
        root = prefix / project.datadir / package
        actual = snapshot(root)
        directories = {".", *(str(parent.as_posix()) for name in payload
                               for parent in Path(name).parents)}
        self.assertEqual(set(actual or ()), set(payload) | directories)
        for name in payload:
            with self.subTest(installed=name):
                entry = actual[name]
                self.assertEqual(entry[0], "file")
                self.assertEqual(entry[2], project.data[name])
                if os.name != "nt":
                    self.assertEqual(entry[1], 0o644)
                if (project.source / name).exists():
                    self.assertFalse(os.path.samefile(root / name, project.source / name))
        for name in directories:
            self.assertEqual(actual[name][0], "directory")
        return root

    def link(self, path, target, directory=False):
        try:
            path.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest("Host cannot create symlinks: " + str(error))

    def test_exact_five_files_copy_modes_and_existing_prefix(self):
        for mode in (None, "", "COPY"):
            with self.subTest(mode=mode):
                prefix = self.new_path("prefix with spaces-é音")
                (prefix / "keep empty").mkdir(parents=True)
                keep = prefix / "keep.bin"
                keep.write_bytes(SENTINEL)
                env = child_environment()
                if mode is not None:
                    env["CMAKE_INSTALL_MODE"] = mode
                self.ok(self.base.install(prefix, env=env))
                self.exact_package(self.base, prefix)
                self.assertEqual(keep.read_bytes(), SENTINEL)
                self.assertEqual(list((prefix / "keep empty").iterdir()), [])
                expected_files = {self.base.datadir / PACKAGE / name for name in PAYLOAD}
                expected_files.add(Path("keep.bin"))
                expected_paths = {Path("."), Path("keep empty"), *expected_files}
                for name in expected_files:
                    expected_paths.update(name.parents)
                self.assertEqual(set(snapshot(prefix)), {name.as_posix() for name in expected_paths})

    @unittest.skipIf(os.name == "nt", "POSIX permission bits are not a Windows file-mode contract")
    def test_executable_private_sources_become_nonexecutable_copies(self):
        sources = [self.base.source / name for name in PAYLOAD]
        before = {path: stat.S_IMODE(path.stat().st_mode) for path in sources}
        try:
            for path in sources:
                path.chmod(0o755)
            prefix = self.new_path("permission-normalized package")
            self.ok(self.base.install(prefix))
            self.exact_package(self.base, prefix)
        finally:
            for path, mode in before.items():
                path.chmod(mode)

    def test_default_unknown_and_original_components_remain_independent(self):
        # Selected-component preflight must neither leak into unrelated installs
        # nor accidentally depend on an original-reference-only file.
        with removed(self.base.source / PAYLOAD[0]):
            ordinary = self.new_path("default")
            self.ok(self.base.install(ordinary, component=None))
            self.assertEqual(set(snapshot(ordinary)), {".", "unrelated", "unrelated/sentinel.bin"})
            self.assertEqual((ordinary / "unrelated/sentinel.bin").read_bytes(), SENTINEL)
            unknown = self.new_path("unknown")
            self.ok(self.base.install(unknown, component="UnknownComponent"))
            self.assertIsNone(snapshot(unknown))
            reference = self.new_path("original 48-file package")
            self.ok(self.base.install(reference, component="ContactReferenceTools"))
            self.exact_package(self.base, reference, payload=REFERENCE,
                               package=Path("hammond-b3-organ/contact-reference"))
            self.assertFalse(self.base.package(reference).exists())
        missing_original = self.base.source / "data/contact-switching/reference-v1/F11-96000-v1.json"
        with removed(missing_original):
            conversion = self.new_path("independent conversion")
            self.ok(self.base.install(conversion))
            self.exact_package(self.base, conversion)
            self.assertFalse((conversion / "share/hammond-b3-organ/contact-reference").exists())

    def test_all_missing_payloads_preserve_absent_and_existing_destinations(self):
        absent, existing = self.new_path("absent"), self.new_path("existing")
        existing.mkdir()
        (existing / "keep.bin").write_bytes(SENTINEL)
        for name in PAYLOAD:
            with self.subTest(payload=name), removed(self.base.source / name):
                for prefix in (absent, existing):
                    result = self.preserve_on_refusal(self.base, prefix)
                    self.assertIn(Path(name).name, diagnostic(result))

    def test_all_empty_and_directory_payloads_refuse_before_copy(self):
        prefix = self.new_path("uncreated")
        for name in PAYLOAD:
            for kind in ("empty", "directory"):
                path = self.base.source / name
                with self.subTest(payload=name, kind=kind), removed(path):
                    path.write_bytes(b"") if kind == "empty" else path.mkdir()
                    self.preserve_on_refusal(self.base, prefix)
                    self.assertFalse(prefix.exists())

    def test_all_linked_payloads_and_source_ancestors_refuse(self):
        prefix = self.new_path("uncreated")
        for name in PAYLOAD:
            path = self.base.source / name
            with self.subTest(payload=name), removed(path) as backup:
                self.link(path, backup)
                self.preserve_on_refusal(self.base, prefix)
        path = self.base.source / PAYLOAD[-1]
        with removed(path):
            self.link(path, self.new_path("dangling input"))
            self.preserve_on_refusal(self.base, prefix)
        for relative in ("tools", "docs", "."):
            path = self.base.source / relative
            with self.subTest(ancestor=relative), removed(path) as backup:
                self.link(path, backup, directory=True)
                result = self.preserve_on_refusal(self.base, prefix)
                self.assertIn("source ancestor", diagnostic(result))

    def test_noncopy_modes_refuse_without_destination_changes(self):
        for mode in ("SYMLINK", "ABS_SYMLINK", "REL_SYMLINK", "SYMLINK_OR_COPY",
                     "ABS_SYMLINK_OR_COPY", "REL_SYMLINK_OR_COPY", "copy", "COPY ", "INVALID"):
            with self.subTest(mode=mode):
                env = child_environment()
                env["CMAKE_INSTALL_MODE"] = mode
                result = self.preserve_on_refusal(self.base, self.new_path("noncopy"), env=env)
                self.assertIn("CMAKE_INSTALL_MODE", diagnostic(result))

    def test_existing_package_and_file_ancestors_are_never_replaced(self):
        for kind in ("file", "empty directory", "populated directory", "installed"):
            with self.subTest(package=kind):
                prefix = self.new_path(kind)
                package = self.base.package(prefix)
                if kind == "installed":
                    self.ok(self.base.install(prefix))
                else:
                    package.parent.mkdir(parents=True)
                    if kind == "file":
                        package.write_bytes(SENTINEL)
                    else:
                        package.mkdir()
                        if kind == "populated directory":
                            (package / "keep.bin").write_bytes(SENTINEL)
                result = self.preserve_on_refusal(self.base, prefix)
                self.assertIn("destination already exists", diagnostic(result))
        for relative in (".", "share", "share/hammond-b3-organ"):
            with self.subTest(ancestor=relative):
                prefix = self.new_path("obstructed prefix")
                path = prefix / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(SENTINEL)
                result = self.preserve_on_refusal(self.base, prefix)
                self.assertIn("destination ancestor", diagnostic(result))

    def test_destination_links_cannot_redirect_a_write(self):
        for relative in (".", "share", "share/hammond-b3-organ", "share/" + PACKAGE.as_posix()):
            for kind in ("directory", "file", "dangling"):
                with self.subTest(ancestor=relative, target=kind):
                    prefix, outside = self.new_path("linked prefix"), self.new_path("outside")
                    outside.mkdir()
                    (outside / "keep.bin").write_bytes(SENTINEL)
                    before = snapshot(outside)
                    target = outside if kind == "directory" else outside / (
                        "keep.bin" if kind == "file" else "absent")
                    path = prefix / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    self.link(path, target, directory=kind != "file")
                    self.preserve_on_refusal(self.base, prefix)
                    self.assertEqual(snapshot(outside), before)

    def test_custom_and_invalid_data_directories(self):
        for datadir in ("resources/conversion data", "resources\\conversion data", "."):
            with self.subTest(datadir=datadir):
                project = self.project("custom directory", datadir=datadir)
                prefix = self.new_path("prefix")
                self.ok(project.install(prefix))
                self.exact_package(project, prefix)
                self.assertFalse((prefix / "share").exists())
        for datadir in ("", "/absolute", "C:/absolute", "C:relative", "C:\\absolute",
                        "\\absolute", "..", "a/../b", "a\\..\\b", "a;b"):
            with self.subTest(invalid=datadir):
                result = self.base.configure(datadir, build=self.new_path("invalid build"))
                self.assertNotEqual(result.returncode, 0, diagnostic(result))
                self.assertIn(COMPONENT, diagnostic(result))
                self.assertIn("nonempty relative CMAKE_INSTALL_DATADIR", " ".join(diagnostic(result).split()))

    @unittest.skipIf(os.name == "nt", "CMake DESTDIR is a POSIX staging facility")
    def test_destdir_uses_the_effective_prefix_for_copy_and_refusal(self):
        stage, nominal = self.new_path("stage"), self.new_path("nominal prefix")
        effective = stage / str(nominal).lstrip("/")
        env = child_environment()
        env["DESTDIR"] = str(stage)
        self.ok(self.base.install(nominal, env=env))
        self.exact_package(self.base, effective)
        self.assertFalse(nominal.exists())
        self.preserve_on_refusal(self.base, nominal, env=env, observed=stage)
        stage2, nominal2 = self.new_path("empty stage"), self.new_path("unused prefix")
        env["DESTDIR"] = str(stage2)
        with removed(self.base.source / PAYLOAD[-1]):
            self.preserve_on_refusal(self.base, nominal2, env=env, observed=stage2)
        self.assertFalse(stage2.exists())
        self.assertFalse(nominal2.exists())

    def test_multi_configuration_copy_requires_no_build(self):
        ninja = (self.make_program if self.make_program and
                 "ninja" in Path(self.make_program).name.lower() else shutil.which("ninja"))
        if ninja:
            generator, make_program = "Ninja Multi-Config", ninja
        elif self.generator and (self.generator.startswith("Visual Studio") or self.generator == "Xcode"):
            generator, make_program = self.generator, self.make_program
        else:
            self.skipTest("No available multi-configuration generator")
        project = self.project("multiple configurations", generator=generator, make_program=make_program)
        for config in ("Release", "Debug"):
            prefix = self.new_path(config)
            self.ok(project.install(prefix, config=config))
            self.exact_package(project, prefix)

    def test_relocated_execution_without_source_build_or_working_directory_imports(self):
        project = self.project("relocation", datadir="resources/conversion data")
        prefix, moved = self.new_path("original prefix"), self.new_path("relocated prefix-é音")
        foreign = self.new_path("foreign working directory")
        foreign.mkdir()
        fixture = foreign / "F02-48000-v1.json"
        fixture.write_bytes(project.data["data/contact-switching/reference-v1/F02-48000-v1.json"])
        python = [sys.executable, "-B", "-E", "-s", "-S"]
        initial = foreign / "source certificate.json"
        source_run = process("source CLI", [*python, project.source / "tools/convert_contact_grid.py",
                             "--input", fixture, "--output", initial], foreign)
        self.ok(source_run)
        self.assertEqual((source_run.stdout, source_run.stderr), (b"", b""))
        self.ok(project.install(prefix))
        prefix.rename(moved)
        installed = self.exact_package(project, moved)
        shutil.rmtree(project.source)
        shutil.rmtree(project.build)
        self.assertFalse(project.source.exists() or project.build.exists() or prefix.exists())
        for name in (*PAYLOAD[:4], "tools/json.py"):
            (foreign / Path(name).name).write_text('raise AssertionError("foreign module imported")\n',
                                                   encoding="utf-8")
        env = child_environment()
        env["PYTHONPATH"] = str(foreign)
        before = snapshot(moved)
        output = foreign / "relocated certificate.json"
        result = process("relocated CLI", [*python, installed / "tools/convert_contact_grid.py",
                         "--input", fixture, "--output", output], foreign, env)
        self.ok(result)
        self.assertEqual((result.stdout, result.stderr), (b"", b""))
        self.assertEqual(output.read_bytes(), initial.read_bytes())
        certificate = json.loads(output.read_bytes())
        self.assertEqual((certificate["status"], certificate["conversion_id"], certificate["audio_accuracy"]),
                         ("accepted", "fractional-to-contact-grid-rne-v1", "unqualified"))
        self.assertEqual((certificate["fixture_id"], certificate["grid_case"]["frames"],
                          len(certificate["edges"]), len(certificate["arrivals"])),
                         ("F02-48000-v1", 256, 18, 2))
        self.assertEqual(certificate["input_sha256"], digest(fixture.read_bytes()))
        self.assertEqual(certificate["input_bytes"], fixture.stat().st_size)
        self.assertEqual(certificate["provenance"]["implementation_sha256"],
                         {name: digest(project.data[name]) for name in PAYLOAD[:4]})
        self.assertEqual(certificate["provenance"]["contract_sha256"], digest(project.data[PAYLOAD[-1]]))
        self.assertEqual(certificate["provenance"]["python_version"], platform.python_version())
        self.assertEqual(certificate["transport"]["sha256"],
                         digest(certificate["transport"]["text"].encode("ascii")))
        self.assertEqual(snapshot(moved), before)
        FACTS["relocation"] = {"source_and_build_deleted": True, "unchanged_package_files": 5,
                               "certificate_bytes": output.stat().st_size,
                               "certificate_sha256": digest(output.read_bytes()),
                               "source_and_installed_bytes_equal": True, "edges": 18, "arrivals": 2}


if __name__ == "__main__":
    report_path = os.environ.get("HAMMOND_CONTACT_GRID_CONVERSION_INSTALL_REPORT")
    if report_path and Path(report_path).exists():
        raise SystemExit("Refusing to overwrite installed-conversion acceptance evidence")
    started = time.monotonic()
    outcome = unittest.main(verbosity=2, exit=False).result
    if report_path:
        report = {"schema_version": 1, "scope": "independent installed-component acceptance",
                  "status": "passed" if outcome.wasSuccessful() else "failed",
                  "python": platform.python_version(), "platform": platform.platform(),
                  "tests_run": outcome.testsRun, "failures": len(outcome.failures),
                  "errors": len(outcome.errors), "skips": [(str(t), why) for t, why in outcome.skipped],
                  "seconds": time.monotonic() - started, "processes": len(EVENTS),
                  "test_sha256": digest(Path(__file__).read_bytes()), "facts": FACTS, "commands": EVENTS}
        Path(report_path).write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    raise SystemExit(0 if outcome.wasSuccessful() else 1)
