#!/usr/bin/env python3
"""Exercise the actual CrossoverTools installer using bounded private fixtures.

The selected native probe is a read-only input, never rebuilt or fault-injected.
Only its private copies and the six-file installed package are mutated. No
install command runs against the shared build or writes its install manifest.
"""

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path("hammond-b3-organ/crossover")
SCRIPT = "tools/crossover_reference.py"
REGISTRY = "data/crossover/leslie-122-ideal-v1.json"
PAYLOAD = (
    SCRIPT, REGISTRY, "docs/CROSSOVER_INSTALL.md",
    "docs/LESLIE_CROSSOVER_CONTRACT.md", "THIRD_PARTY_NOTICES.md",
)
INSTALLERS = ("cmake/InstallHammondTools.cmake", "cmake/InstallCrossoverTools.cmake")
MODEL = "atlas-leslie-122-ideal-crossover-v1"


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


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
    """Include root/empty directories and links without following linked trees."""
    if root.is_symlink():
        return ("link", os.readlink(root))
    if not root.exists():
        return None
    if root.is_file():
        return ("file", root.read_bytes())
    result = {".": ("directory",)}
    for directory, subdirs, names in os.walk(root, followlinks=False):
        for name in subdirs + names:
            path = Path(directory) / name
            key = path.relative_to(root).as_posix()
            if path.is_symlink():
                result[key] = ("link", os.readlink(path))
            elif path.is_dir():
                result[key] = ("directory",)
            else:
                result[key] = ("file", path.read_bytes())
    return result


@contextmanager
def withheld(path):
    """Fault-inject only a private input, preserving its original permissions."""
    backup = path.with_name(path.name + ".held-by-install-test")
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
    """Real copied installers plus an imported, already-built native artifact.

    No compiler, whole checkout, PDF or shared build-tree copy is needed. The
    sentinel rules model unrelated component dispatch, not native products.
    """

    def __init__(self, root, cmake, probe, *, generator=None, make_program=None,
                 bindir="bin", datadir="share", multi=False):
        self.root, self.cmake = root, cmake
        self.source, self.build = root / "source", root / "build"
        self.bindir, self.datadir = Path(bindir), Path(datadir)
        self.generator, self.make_program = generator, make_program
        root.mkdir()
        self.source.mkdir()
        self.originals = {name: (ROOT / name).read_bytes() for name in PAYLOAD}
        for name in (*PAYLOAD, *INSTALLERS):
            destination = self.source / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        self.binaries = {}
        for config in ("Release", "Debug"):
            destination = root / "artifacts" / config / probe.name
            destination.parent.mkdir(parents=True)
            shutil.copy2(probe, destination)
            self.binaries[config] = destination
        self.probe_bytes = probe.read_bytes()
        (self.source / "sentinel.txt").write_bytes(b"unrelated component\n")
        # InstallHammondTools defines the shared validator. Apply the fixture's
        # directory values afterwards so GNUInstallDirs cannot substitute away
        # an intentionally empty value before the crossover validator sees it.
        (self.source / "CMakeLists.txt").write_text(
            'cmake_minimum_required(VERSION 3.21)\n'
            'project(CrossoverInstallFixture LANGUAGES NONE)\n'
            'include(cmake/InstallHammondTools.cmake)\n'
            'set(CMAKE_INSTALL_BINDIR "${FIXTURE_BINDIR}")\n'
            'set(CMAKE_INSTALL_DATADIR "${FIXTURE_DATADIR}")\n'
            'add_executable(hammond_crossover_probe IMPORTED GLOBAL)\n'
            'set_target_properties(hammond_crossover_probe PROPERTIES\n'
            '  IMPORTED_CONFIGURATIONS "Debug;Release"\n'
            '  IMPORTED_LOCATION "${FIXTURE_RELEASE_PROBE}"\n'
            '  IMPORTED_LOCATION_RELEASE "${FIXTURE_RELEASE_PROBE}"\n'
            '  IMPORTED_LOCATION_DEBUG "${FIXTURE_DEBUG_PROBE}")\n'
            'include(cmake/InstallCrossoverTools.cmake)\n'
            'install(FILES sentinel.txt DESTINATION offline COMPONENT OfflineTools)\n'
            'install(FILES sentinel.txt DESTINATION standalone COMPONENT Standalone EXCLUDE_FROM_ALL)\n',
            encoding="utf-8")
        self.multi = multi
        self.configured = self.configure()

    def configure(self, *, build=None, bindir=None, datadir=None):
        command = [self.cmake, "-S", self.source, "-B", build or self.build,
                   "-Wno-dev", "-DCMAKE_BUILD_TYPE=Release",
                   "-DCMAKE_CONFIGURATION_TYPES=Debug;Release",
                   f"-DFIXTURE_BINDIR:STRING={self.bindir.as_posix() if bindir is None else bindir}",
                   f"-DFIXTURE_DATADIR:STRING={self.datadir.as_posix() if datadir is None else datadir}",
                   f"-DFIXTURE_RELEASE_PROBE:FILEPATH={self.binaries['Release'].as_posix()}",
                   f"-DFIXTURE_DEBUG_PROBE:FILEPATH={self.binaries['Debug'].as_posix()}"]
        if self.generator:
            command += ["-G", self.generator]
        if self.make_program:
            command += [f"-DCMAKE_MAKE_PROGRAM:FILEPATH={self.make_program}"]
        return invoke(command, self.root)

    def install(self, prefix, *, configuration="Release", component="CrossoverTools", env=None):
        command = [self.cmake, "--install", self.build, "--prefix", prefix,
                   "--config", configuration]
        if component is not None:
            command += ["--component", component]
        return invoke(command, self.root, env)

    def package(self, prefix):
        return prefix / self.datadir / PACKAGE

    def binary(self, prefix):
        return prefix / self.bindir / self.binaries["Release"].name

    def inputs(self):
        return [self.binaries["Release"], *[self.source / name for name in PAYLOAD]]


class CrossoverInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cmake = os.environ.get("HAMMOND_TEST_CMAKE") or shutil.which("cmake")
        probe = os.environ.get("HAMMOND_CROSSOVER_PROBE_EXECUTABLE")
        if not cmake or not Path(cmake).is_file() or not probe or not Path(probe).is_file():
            raise RuntimeError("CrossoverTools acceptance requires HAMMOND_TEST_CMAKE and "
                               "HAMMOND_CROSSOVER_PROBE_EXECUTABLE. Build hammond_crossover_probe "
                               "for the selected configuration and run through CTest.")
        cls.cmake, cls.probe = Path(cmake).resolve(), Path(probe).resolve()
        cls.generator = os.environ.get("HAMMOND_TEST_CMAKE_GENERATOR")
        cls.make_program = os.environ.get("HAMMOND_TEST_CMAKE_MAKE_PROGRAM")
        cls.live_hashes = {ROOT / name: sha((ROOT / name).read_bytes())
                           for name in (*PAYLOAD, *INSTALLERS)}
        cls.live_hashes[cls.probe] = sha(cls.probe.read_bytes())
        cls.temp = tempfile.TemporaryDirectory(prefix="crossover-install-")
        cls.root = Path(cls.temp.name).resolve()
        cls.counter = 0
        cls.project = PrivateProject(cls.root / "base", cls.cmake, cls.probe,
                                     generator=cls.generator, make_program=cls.make_program)
        if cls.project.configured.returncode:
            cls.temp.cleanup()
            raise RuntimeError("Private install configure failed:\n" + diagnostic(cls.project.configured))

    @classmethod
    def tearDownClass(cls):
        try:
            for path, expected in cls.live_hashes.items():
                if sha(path.read_bytes()) != expected:
                    raise AssertionError("Read-only source/build input changed: " + str(path))
        finally:
            cls.temp.cleanup()

    def fresh(self, label):
        type(self).counter += 1
        return self.root / f"{self.counter:03d}-{label}"

    def success(self, result):
        self.assertEqual(result.returncode, 0, diagnostic(result))

    def unchanged_rejection(self, project, prefix, *, before=None, env=None, configuration="Release"):
        if before is None:
            before = state(prefix)
        result = project.install(prefix, env=env, configuration=configuration)
        self.assertNotEqual(result.returncode, 0, diagnostic(result))
        self.assertIn("CrossoverTools", diagnostic(result))
        self.assertEqual(state(prefix), before, "Rejected install mutated its destination")
        return result

    def installed(self, project, prefix):
        expected = {project.bindir / self.probe.name: project.probe_bytes}
        expected.update({project.datadir / PACKAGE / name: payload
                         for name, payload in project.originals.items()})
        actual = {path.relative_to(prefix): path.read_bytes()
                  for path in prefix.rglob("*") if path.is_file()}
        self.assertEqual(len(expected), 6)
        self.assertEqual(actual, expected, "Component inventory or installed bytes differ")
        self.assertFalse(any(path.is_symlink() for path in prefix.rglob("*")))
        return project.package(prefix)

    def new_project(self, label, **options):
        options.setdefault("generator", self.generator)
        options.setdefault("make_program", self.make_program)
        project = PrivateProject(self.fresh(label), self.cmake, self.probe, **options)
        self.success(project.configured)
        return project

    def reference(self, package, cwd, *arguments):
        return invoke([sys.executable, "-I", "-B", "-S", package / SCRIPT, *arguments], cwd)

    def test_exact_inventory_and_copy_identity(self):
        prefix = self.fresh("exact prefix with spaces")
        env = environment()
        env["CMAKE_INSTALL_MODE"] = "COPY"
        self.success(self.project.install(prefix, env=env))
        package = self.installed(self.project, prefix)
        self.assertFalse(os.path.samefile(self.project.binary(prefix), self.project.binaries["Release"]))
        for name in PAYLOAD:
            self.assertFalse(os.path.samefile(package / name, self.project.source / name))
        before = state(prefix)
        self.unchanged_rejection(self.project, prefix, before=before)

    def test_relocation_default_registry_and_native_execution_without_private_sources(self):
        project = self.new_project("relocation fixture")
        prefix, moved = self.fresh("original prefix"), self.fresh("moved prefix-é音")
        foreign = self.fresh("unrelated working directory")
        (foreign / "data/crossover").mkdir(parents=True)
        (foreign / REGISTRY).write_bytes(b"not the installed registry\n")
        responses = [
            ["--operation", "response", "--sample-rate", "48000", "--frequencies", "0,400,800,1600,20000"],
            ["--operation", "sine", "--sample-rate", "48000", "--frequency", "800",
             "--warmup-frames", "4096", "--measurement-frames", "4096"],
        ]
        expected = [invoke([project.binaries["Release"], *args], foreign) for args in responses]
        for result in expected:
            self.success(result)
        self.success(project.install(prefix))
        prefix.rename(moved)
        package = self.installed(project, moved)
        for path in (project.source, project.build, project.root / "artifacts"):
            shutil.rmtree(path)
            self.assertFalse(path.exists())
        self.assertFalse(prefix.exists())
        before = state(moved)
        resolution = invoke([
            sys.executable, "-I", "-B", "-S", "-c",
            'import json,runpy,sys; m=runpy.run_path(sys.argv[1]); '
            'print(json.dumps(str(m["DEFAULT_REGISTRY"].resolve())))', package / SCRIPT,
        ], foreign)
        self.success(resolution)
        self.assertEqual(json.loads(resolution.stdout), str((package / REGISTRY).resolve()))
        reference = self.reference(package, foreign)
        self.success(reference)
        report = json.loads(reference.stdout)
        self.assertTrue(report["acceptance"]["passed"])
        self.assertEqual(report["model_id"], MODEL)
        self.assertEqual(report["registry_bytes_sha256"], sha(project.originals[REGISTRY]))
        self.assertEqual(report["reference_code_sha256"], sha(project.originals[SCRIPT]))
        self.assertEqual(report["grid"]["requested_count"], 124)
        for claim in ("atlas_bytes_verified_by_this_tool", "physical_measurement_claim", "engine_integration"):
            self.assertIs(report[claim], False)
        self.assertIsNone(report["unknown_physical_fields"]["actual_driver_complex_impedances"])
        explicit = self.reference(package, foreign, "--registry", package / REGISTRY)
        self.success(explicit)
        self.assertEqual(explicit.stdout, reference.stdout)
        for args, original in zip(responses, expected):
            result = invoke([project.binary(moved), *args], foreign)
            self.success(result)
            self.assertEqual(result.stderr, b"")
            self.assertEqual(result.stdout, original.stdout)
            native = json.loads(result.stdout)
            self.assertEqual(native["model_id"], MODEL)
            self.assertIs(native["physical_measurement_claim"], False)
            self.assertIs(native["engine_integration"], False)
        self.assertEqual(state(moved), before)

    def test_custom_relative_directories_keep_default_registry(self):
        project = self.new_project("custom directories", bindir="executables/native tools",
                                   datadir="resources/reference data")
        prefix = self.fresh("custom prefix")
        self.success(project.install(prefix))
        package = self.installed(project, prefix)
        foreign = self.fresh("custom unrelated cwd")
        foreign.mkdir()
        result = self.reference(package, foreign)
        self.success(result)
        self.assertEqual(json.loads(result.stdout)["registry_bytes_sha256"], sha(project.originals[REGISTRY]))
        self.assertFalse((prefix / "bin").exists())
        self.assertFalse((prefix / "share").exists())

    def test_invalid_install_directories_fail_configuration(self):
        invalid = ("", "/absolute", "C:/absolute", "C:relative", "..", "child/../escape",
                   "child\\..\\escape", "one;two")
        for variable in ("bindir", "datadir"):
            for value in invalid:
                with self.subTest(variable=variable, value=value):
                    result = self.project.configure(build=self.fresh("invalid configure"),
                                                    **{variable: value})
                    self.assertNotEqual(result.returncode, 0, diagnostic(result))
                    self.assertIn("CrossoverTools", diagnostic(result))
                    self.assertIn("nonempty relative", diagnostic(result))

    def test_every_missing_input_rejects_before_destination_mutation(self):
        prefix = self.fresh("missing input prefix")
        prefix.mkdir()
        (prefix / "unrelated.bin").write_bytes(b"preserve this file\x00\r\n")
        before = state(prefix)
        for path in self.project.inputs():
            with self.subTest(input=path.name), withheld(path):
                self.assertFalse(path.exists())
                result = self.unchanged_rejection(self.project, prefix, before=before)
                self.assertIn(path.name, diagnostic(result))
        # The last required input must also fail before creating a fresh prefix.
        with withheld(self.project.inputs()[-1]):
            fresh = self.fresh("absent prefix")
            self.unchanged_rejection(self.project, fresh)
            self.assertFalse(fresh.exists())

    def test_empty_and_directory_inputs_reject_before_copy(self):
        prefix = self.fresh("malformed input prefix")
        for path in self.project.inputs():
            for kind in ("empty", "directory"):
                with self.subTest(input=path.name, kind=kind), withheld(path):
                    path.write_bytes(b"") if kind == "empty" else path.mkdir()
                    result = self.unchanged_rejection(self.project, prefix)
                    self.assertIn(path.name, diagnostic(result))
                    self.assertFalse(prefix.exists())

    def make_link(self, path, target, *, directory=False):
        try:
            path.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest("Symlink creation unavailable on this host: " + str(error))

    def test_symlink_inputs_are_rejected(self):
        prefix = self.fresh("linked input prefix")
        for path in self.project.inputs():
            with self.subTest(input=path.name), withheld(path) as original:
                self.make_link(path, original)
                self.unchanged_rejection(self.project, prefix)
                self.assertFalse(prefix.exists())

    def test_noncopy_modes_reject_before_copy(self):
        prefix = self.fresh("mode prefix")
        for mode in ("SYMLINK", "REL_SYMLINK", "ABS_SYMLINK_OR_COPY", "copy", "INVALID"):
            with self.subTest(mode=mode):
                env = environment()
                env["CMAKE_INSTALL_MODE"] = mode
                result = self.unchanged_rejection(self.project, prefix, env=env)
                self.assertIn("CMAKE_INSTALL_MODE", diagnostic(result))
                self.assertFalse(prefix.exists())

    def test_existing_outputs_and_file_ancestors_are_preserved(self):
        for location in ("binary", "package", "binary_parent", "package_parent"):
            for kind in ("file", "directory"):
                if location.endswith("parent") and kind == "directory":
                    continue  # Ordinary parent directories are valid, not obstructions.
                with self.subTest(location=location, kind=kind):
                    prefix = self.fresh("obstructed prefix")
                    path = (self.project.binary(prefix) if location.startswith("binary")
                            else self.project.package(prefix))
                    if location.endswith("parent"):
                        path = path.parent
                    path.parent.mkdir(parents=True)
                    if kind == "file":
                        path.write_bytes(b"existing owned bytes\n")
                    else:
                        path.mkdir()
                        (path / "sentinel").write_bytes(b"existing tree\n")
                    self.unchanged_rejection(self.project, prefix)

    def test_destination_and_parent_links_do_not_redirect_copy(self):
        for location in ("binary", "package", "binary_parent", "prefix"):
            for dangling in (False, True):
                with self.subTest(location=location, dangling=dangling):
                    prefix, target = self.fresh("linked prefix"), self.fresh("owned link target")
                    target.mkdir()
                    (target / "sentinel").write_bytes(b"outside prefix stays unchanged\n")
                    before_target = state(target)
                    link_target = target / "absent" if dangling else target
                    path = (prefix if location == "prefix" else
                            self.project.package(prefix) if location == "package" else
                            self.project.binary(prefix))
                    if location == "binary_parent":
                        path = path.parent
                    path.parent.mkdir(parents=True, exist_ok=True)
                    self.make_link(path, link_target, directory=True)
                    self.unchanged_rejection(self.project, prefix)
                    self.assertEqual(state(target), before_target)

    def test_component_selection_preserves_unrelated_payloads(self):
        for component in (None, "OfflineTools", "Standalone", "CaptureTools", "NativeVST3", "Unknown"):
            with self.subTest(component=component):
                prefix = self.fresh("component prefix")
                self.success(self.project.install(prefix, component=component))
                expected = {}
                if component in (None, "OfflineTools"):
                    expected[Path("offline/sentinel.txt")] = b"unrelated component\n"
                elif component == "Standalone":
                    expected[Path("standalone/sentinel.txt")] = b"unrelated component\n"
                actual = {p.relative_to(prefix): p.read_bytes()
                          for p in prefix.rglob("*") if p.is_file()}
                self.assertEqual(actual, expected)

    def test_multiconfig_selection_and_unknown_configuration(self):
        ninja = (self.make_program if self.make_program and
                 "ninja" in Path(self.make_program).name.lower() else shutil.which("ninja"))
        if ninja:
            generator, make_program = "Ninja Multi-Config", ninja
        elif self.generator and (self.generator.startswith("Visual Studio") or self.generator == "Xcode"):
            generator, make_program = self.generator, self.make_program
        else:
            self.skipTest("No available multi-configuration generator for private fixture")
        project = self.new_project("multi config", generator=generator, make_program=make_program, multi=True)
        with withheld(project.binaries["Debug"]):
            for name in ("Release", "release"):
                prefix = self.fresh("selected release")
                self.success(project.install(prefix, configuration=name))
                self.installed(project, prefix)
            self.unchanged_rejection(project, self.fresh("missing selected debug"), configuration="Debug")
        with withheld(project.binaries["Release"]):
            prefix = self.fresh("selected debug")
            self.success(project.install(prefix, configuration="Debug"))
            self.installed(project, prefix)
        prefix = self.fresh("unknown config")
        result = self.unchanged_rejection(project, prefix, configuration="NoSuchConfiguration")
        self.assertIn("unknown configuration", diagnostic(result))
        self.assertFalse(prefix.exists())

    @unittest.skipIf(os.name == "nt", "CMake DESTDIR is a POSIX staging facility")
    def test_destdir_checks_and_copies_the_staged_prefix(self):
        stage, prefix = self.fresh("stage"), self.fresh("logical prefix")
        env = environment()
        env["DESTDIR"] = str(stage)
        self.success(self.project.install(prefix, env=env))
        actual = stage / str(prefix).lstrip("/")
        self.installed(self.project, actual)
        self.assertFalse(prefix.exists())
        before = state(stage)
        result = self.project.install(prefix, env=env)
        self.assertNotEqual(result.returncode, 0, diagnostic(result))
        self.assertEqual(state(stage), before)

    def test_installed_reference_output_and_native_rejection_safety(self):
        prefix, foreign = self.fresh("output safety prefix"), self.fresh("reports")
        foreign.mkdir()
        self.success(self.project.install(prefix))
        package = self.installed(self.project, prefix)
        before = state(prefix)
        stdout = self.reference(package, foreign)
        self.success(stdout)
        report_path = foreign / "reference.json"
        report_path.write_bytes(b"old report selected for replacement\n")
        result = self.reference(package, foreign, "--output", report_path)
        self.success(result)
        self.assertEqual(result.stdout, b"")
        # The atomic file writer specifies LF; Windows text stdout emits CRLF.
        # Normalize only that platform representation, retaining exact content.
        stdout_report = stdout.stdout.replace(b"\r\n", b"\n") if os.name == "nt" else stdout.stdout
        self.assertEqual(report_path.read_bytes(), stdout_report)
        for destination in (package / SCRIPT, package / REGISTRY):
            result = self.reference(package, foreign, "--output", destination)
            self.assertEqual(result.returncode, 2, diagnostic(result))
            self.assertEqual(result.stdout, b"")
            self.assertIn("must not replace", diagnostic(result))
            self.assertEqual(state(prefix), before)
        retained = report_path.read_bytes()
        result = self.reference(package, foreign, "--bass-ohms", "nan", "--output", report_path)
        self.assertEqual(result.returncode, 2, diagnostic(result))
        self.assertEqual(result.stdout, b"")
        self.assertEqual(report_path.read_bytes(), retained)
        for destination in (foreign / "absent/report.json", foreign):
            result = self.reference(package, foreign, "--output", destination)
            self.assertEqual(result.returncode, 2, diagnostic(result))
            self.assertEqual(result.stdout, b"")
            self.assertEqual(report_path.read_bytes(), retained)
        result = invoke([self.project.binary(prefix), "--operation", "response",
                         "--sample-rate", "48000", "--frequencies", "24000"], foreign)
        self.assertEqual(result.returncode, 2, diagnostic(result))
        self.assertEqual(result.stdout, b"")
        self.assertEqual(state(prefix), before)
        self.assertEqual({p.name for p in foreign.iterdir()}, {"reference.json"},
                         "Rejected output left temporary files or created parents")


if __name__ == "__main__":
    unittest.main()
