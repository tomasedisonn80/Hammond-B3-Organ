#!/usr/bin/env python3
"""Exercise real SourceLeakageTools rules with bounded private install fixtures.

Already-built executables/profile are read-only inputs. No compilation, install
or fault injection touches the coordinated build. Relocation removes all private
source/build/artifact inputs before running the installed tools with explicit
installed data from an unrelated directory.
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
import wave


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = Path("hammond-b3-organ/source-leakage")
COMPILER = "tools/compile_source_leakage.py"
PAIR = "data/source-leakage/synthetic-pair-demo-v1.json"
IDENTITY = "data/source-leakage/synthetic-identity-v1.json"
PROFILE = "profiles/nominal.b3p"
PAYLOAD = (COMPILER, "data/source-leakage.schema.json", PAIR, IDENTITY,
           "docs/SOURCE_LEAKAGE_INSTALL.md")
INSTALLERS = ("cmake/InstallHammondTools.cmake", "cmake/InstallSourceLeakageTools.cmake")
TARGETS = {
    "hammond_render": "HAMMOND_RENDER_EXECUTABLE",
    "hammond_source_leakage_probe": "HAMMOND_SOURCE_LEAKAGE_PROBE_EXECUTABLE",
    "hammond_source_leakage_benchmark": "HAMMOND_SOURCE_LEAKAGE_BENCHMARK_EXECUTABLE",
}


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
    """Retain bytes, empty directories and links without following linked trees."""
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
    """Fault-inject private inputs only and preserve their original permissions."""
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
    """Actual install modules and copied artifacts, with no compiler/language."""

    def __init__(self, root, cmake, executables, profile, *, generator=None,
                 make_program=None, bindir="bin", datadir="share"):
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
        self.profile = root / "artifacts" / "nominal.b3p"
        self.profile.parent.mkdir()
        shutil.copy2(profile, self.profile)
        self.profile_bytes = profile.read_bytes()
        self.binary_bytes = {name: path.read_bytes() for name, path in executables.items()}
        self.binaries = {}
        for config in ("Release", "Debug"):
            self.binaries[config] = {}
            for name, original in executables.items():
                destination = root / "artifacts" / config / original.name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(original, destination)
                self.binaries[config][name] = destination
        (self.source / "sentinel.txt").write_bytes(b"unrelated component\n")
        # Include the shared directory helper before targets exist: its legacy
        # component rules remain inactive in this intentionally tiny fixture.
        source = (
            'cmake_minimum_required(VERSION 3.21)\n'
            'project(SourceLeakageInstallFixture LANGUAGES NONE)\n'
            'include(cmake/InstallHammondTools.cmake)\n'
            'set(CMAKE_INSTALL_BINDIR "${FIXTURE_BINDIR}")\n'
            'set(CMAKE_INSTALL_DATADIR "${FIXTURE_DATADIR}")\n'
            'set(HAMMOND_COMPILED_PROFILE "${FIXTURE_PROFILE}")\n'
        )
        for name in executables:
            source += (
                f'add_executable({name} IMPORTED GLOBAL)\n'
                f'set_target_properties({name} PROPERTIES\n'
                '  IMPORTED_CONFIGURATIONS "Debug;Release"\n'
                f'  IMPORTED_LOCATION "${{FIXTURE_RELEASE_{name}}}"\n'
                f'  IMPORTED_LOCATION_RELEASE "${{FIXTURE_RELEASE_{name}}}"\n'
                f'  IMPORTED_LOCATION_DEBUG "${{FIXTURE_DEBUG_{name}}}")\n'
            )
        source += (
            'include(cmake/InstallSourceLeakageTools.cmake)\n'
            'install(FILES sentinel.txt DESTINATION offline COMPONENT OfflineTools)\n'
            'install(FILES sentinel.txt DESTINATION standalone COMPONENT Standalone EXCLUDE_FROM_ALL)\n'
        )
        (self.source / "CMakeLists.txt").write_text(source, encoding="utf-8")
        self.configured = self.configure()

    def configure(self, *, build=None, bindir=None, datadir=None):
        command = [self.cmake, "-S", self.source, "-B", build or self.build,
                   "-Wno-dev", "-DCMAKE_BUILD_TYPE=Release",
                   "-DCMAKE_CONFIGURATION_TYPES=Debug;Release",
                   f"-DFIXTURE_BINDIR:STRING={self.bindir.as_posix() if bindir is None else bindir}",
                   f"-DFIXTURE_DATADIR:STRING={self.datadir.as_posix() if datadir is None else datadir}",
                   f"-DFIXTURE_PROFILE:FILEPATH={self.profile.as_posix()}"]
        for config, artifacts in self.binaries.items():
            for name, path in artifacts.items():
                command += [f"-DFIXTURE_{config.upper()}_{name}:FILEPATH={path.as_posix()}"]
        if self.generator:
            command += ["-G", self.generator]
        if self.make_program:
            command += [f"-DCMAKE_MAKE_PROGRAM:FILEPATH={self.make_program}"]
        return invoke(command, self.root)

    def install(self, prefix, *, configuration="Release", component="SourceLeakageTools", env=None):
        command = [self.cmake, "--install", self.build, "--prefix", prefix,
                   "--config", configuration]
        if component is not None:
            command += ["--component", component]
        return invoke(command, self.root, env)

    def package(self, prefix):
        return prefix / self.datadir / PACKAGE

    def binary(self, prefix, name):
        return prefix / self.bindir / self.binaries["Release"][name].name

    def inputs(self):
        return [self.profile, *self.binaries["Release"].values(),
                *[self.source / name for name in PAYLOAD]]


class SourceLeakageInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cmake = os.environ.get("HAMMOND_TEST_CMAKE") or shutil.which("cmake")
        names = {"cmake": cmake, "profile": os.environ.get("HAMMOND_TEST_PROFILE")}
        names.update({name: os.environ.get(variable) for name, variable in TARGETS.items()})
        missing = [name for name, path in names.items() if not path or not Path(path).is_file()]
        if missing:
            raise RuntimeError("SourceLeakageTools acceptance requires CTest's selected CMake, "
                               "profile and all three built executable paths; missing " + ", ".join(missing))
        cls.cmake = Path(cmake).resolve()
        cls.profile = Path(names["profile"]).resolve()
        cls.executables = {name: Path(names[name]).resolve() for name in TARGETS}
        cls.generator = os.environ.get("HAMMOND_TEST_CMAKE_GENERATOR")
        cls.make_program = os.environ.get("HAMMOND_TEST_CMAKE_MAKE_PROGRAM")
        live = [ROOT / name for name in (*PAYLOAD, *INSTALLERS)]
        live += [cls.profile, *cls.executables.values()]
        cls.live_hashes = {path: sha(path.read_bytes()) for path in live}
        cls.temp = tempfile.TemporaryDirectory(prefix="source-leakage-install-")
        cls.root = Path(cls.temp.name).resolve()
        cls.counter = 0
        cls.project = PrivateProject(cls.root / "base", cls.cmake, cls.executables, cls.profile,
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

    def new_project(self, label, **options):
        options.setdefault("generator", self.generator)
        options.setdefault("make_program", self.make_program)
        project = PrivateProject(self.fresh(label), self.cmake, self.executables, self.profile, **options)
        self.success(project.configured)
        return project

    def unchanged_rejection(self, project, prefix, *, before=None, env=None, configuration="Release"):
        if before is None:
            before = state(prefix)
        result = project.install(prefix, env=env, configuration=configuration)
        self.assertNotEqual(result.returncode, 0, diagnostic(result))
        self.assertIn("SourceLeakageTools", diagnostic(result))
        self.assertEqual(state(prefix), before, "Rejected install mutated its destination")
        return result

    def installed(self, project, prefix):
        expected = {project.bindir / project.binaries["Release"][name].name: payload
                    for name, payload in project.binary_bytes.items()}
        expected.update({project.datadir / PACKAGE / name: payload
                         for name, payload in project.originals.items()})
        expected[project.datadir / PACKAGE / PROFILE] = project.profile_bytes
        actual = {path.relative_to(prefix): path.read_bytes()
                  for path in prefix.rglob("*") if path.is_file()}
        self.assertEqual(len(expected), 9)
        self.assertEqual(actual, expected, "Component inventory or installed bytes differ")
        self.assertFalse(any(path.is_symlink() for path in prefix.rglob("*")))
        return project.package(prefix)

    def compile(self, package, cwd, authored, output):
        return invoke([sys.executable, "-I", "-B", "-S", package / COMPILER,
                       "--input", package / authored, "--output", output], cwd)

    def test_exact_inventory_and_copy_identity(self):
        prefix = self.fresh("exact prefix with spaces-é音")
        env = environment()
        env["CMAKE_INSTALL_MODE"] = "COPY"
        self.success(self.project.install(prefix, env=env))
        package = self.installed(self.project, prefix)
        for name, original in self.project.binaries["Release"].items():
            self.assertFalse(os.path.samefile(self.project.binary(prefix, name), original))
        for name in PAYLOAD:
            self.assertFalse(os.path.samefile(package / name, self.project.source / name))
        self.assertFalse(os.path.samefile(package / PROFILE, self.project.profile))
        self.unchanged_rejection(self.project, prefix)

    def test_relocated_compiler_probe_gain_matched_render_and_benchmark_without_inputs(self):
        project = self.new_project("relocation fixture")
        prefix, moved = self.fresh("original prefix"), self.fresh("moved prefix-é音")
        foreign = self.fresh("unrelated working directory")
        foreign.mkdir()
        # Deliberately wrong CWD data must not satisfy any runtime lookup.
        (foreign / "nominal.b3p").write_bytes(b"wrong working-directory profile\n")
        self.success(project.install(prefix))
        prefix.rename(moved)
        package = self.installed(project, moved)
        for path in (project.source, project.build, project.root / "artifacts"):
            shutil.rmtree(path)
            self.assertFalse(path.exists())
        self.assertFalse(prefix.exists())
        before = state(moved)
        graphs = {}
        for name, authored, count in (("pair", PAIR, 2), ("identity", IDENTITY, 0)):
            graph = foreign / f"{name}-é音.b3leakage"
            result = self.compile(package, foreign, authored, graph)
            self.success(result)
            receipt = json.loads(result.stdout)
            self.assertEqual(receipt["input_sha256"], sha(project.originals[authored]))
            self.assertEqual(receipt["compiled_sha256"], sha(graph.read_bytes()))
            self.assertEqual(receipt["edge_count"], count)
            self.assertEqual(receipt["evidence_status"], "synthetic")
            probe = invoke([project.binary(moved, "hammond_source_leakage_probe"),
                            "--input", graph], foreign)
            self.success(probe)
            facts = json.loads(probe.stdout)
            self.assertEqual(facts["authoring_sha256"], receipt["input_sha256"])
            self.assertEqual(facts["authoring_digest_verification"], "file-supplied-unverified")
            self.assertEqual(facts["edge_count"], count)
            expected_edges = ([{"destination": 25, "source": 37, "gain": 0.0625},
                               {"destination": 37, "source": 25, "gain": -0.03125}]
                              if count else [])
            self.assertEqual(facts["edges"], expected_edges)
            expected = list(facts["input_frame"])
            for edge in expected_edges:
                expected[edge["destination"] - 1] += (
                    edge["gain"] * facts["input_frame"][edge["source"] - 1])
            self.assertEqual(facts["output_frame"], expected)
            self.assertEqual(len(expected), 91)
            graphs[name] = graph

        def render(name, graph=None, gain=None):
            output = foreign / f"{name}-é音.wav"
            arguments = [project.binary(moved, "hammond_render"), "--profile", package / PROFILE,
                         "--output", output, "--frames", "4096", "--sample-rate", "48000",
                         "--block-size", "64", "--seed", "1939", "--drawbars", "008000000",
                         "--note", "48", "--contacts", "ideal", "--percussion", "off",
                         "--fail-on-clip"]
            if graph:
                arguments += ["--source-leakage", graphs[graph], "--leakage-input-gain", str(gain)]
            result = invoke(arguments, foreign)
            self.success(result)
            facts = json.loads(result.stdout)
            self.assertEqual(facts["status"], "ok")
            self.assertEqual(facts["clipped_channel_samples"], 0)
            self.assertGreater(facts["peak"], 0)
            if graph:
                self.assertEqual(facts["render_schema_version"], 5)
                self.assertEqual(facts["source_leakage_input_gain"], gain)
                self.assertEqual(facts["source_leakage_edge_count"], 2 if graph == "pair" else 0)
                self.assertLessEqual(facts["source_leakage_guarded_output_bound"], 1)
            else:
                self.assertEqual(facts["render_schema_version"], 3)
            with wave.open(str(output), "rb") as wav:
                self.assertEqual((wav.getnchannels(), wav.getsampwidth(), wav.getframerate(),
                                  wav.getnframes()), (2, 2, 48000, 4096))
            return output.read_bytes()

        pair = render("pair", "pair", 0.75)
        identity = render("identity", "identity", 0.75)
        self.assertNotEqual(pair, identity, "Gain-matched leakage audition produced no changed audio")
        self.assertEqual(render("default"), render("identity-unity", "identity", 1.0))
        benchmark = invoke([project.binary(moved, "hammond_source_leakage_benchmark"),
                            "--profile", package / PROFILE, "--blocks", "2",
                            "--repetitions", "1", "--seed", "739"], foreign)
        self.success(benchmark)
        facts = json.loads(benchmark.stdout)
        self.assertTrue(facts["sanity_passed"])
        self.assertEqual(len(facts["rows"]), 19)
        self.assertFalse(facts["callback_deadlines_measured"])
        self.assertEqual(state(moved), before, "Runtime changed its installed package")

    def test_custom_relative_directories(self):
        project = self.new_project("custom directories", bindir="executables/native tools",
                                   datadir="resources/reference data")
        prefix = self.fresh("custom prefix-é音")
        self.success(project.install(prefix))
        package = self.installed(project, prefix)
        foreign = self.fresh("custom unrelated cwd")
        foreign.mkdir()
        result = self.compile(package, foreign, PAIR, foreign / "graph.b3leakage")
        self.success(result)
        self.assertEqual(json.loads(result.stdout)["input_sha256"], sha(project.originals[PAIR]))
        result = invoke([project.binary(prefix, "hammond_source_leakage_probe"),
                         "--input", foreign / "graph.b3leakage"], foreign)
        self.success(result)
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
                    self.assertIn("SourceLeakageTools", diagnostic(result))
                    self.assertIn("nonempty relative", diagnostic(result))

    def test_every_missing_input_rejects_before_any_destination_write(self):
        prefix = self.fresh("missing input prefix")
        prefix.mkdir()
        (prefix / "unrelated.bin").write_bytes(b"preserve this file\x00\r\n")
        before = state(prefix)
        self.assertEqual(len(self.project.inputs()), 9)
        for path in self.project.inputs():
            with self.subTest(input=path.name), withheld(path):
                result = self.unchanged_rejection(self.project, prefix, before=before)
                self.assertIn(path.name, diagnostic(result))
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
                    self.unchanged_rejection(self.project, prefix)
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

    def test_every_output_collision_and_file_ancestor_is_preserved(self):
        for location in (*TARGETS, "package", "binary_parent", "package_parent", "prefix"):
            for kind in ("file", "directory"):
                if (location.endswith("parent") or location == "prefix") and kind == "directory":
                    continue
                with self.subTest(location=location, kind=kind):
                    prefix = self.fresh("obstructed prefix")
                    if location == "prefix":
                        path = prefix
                    elif location.startswith("package"):
                        path = self.project.package(prefix)
                    else:
                        name = location if location in TARGETS else "hammond_render"
                        path = self.project.binary(prefix, name)
                    if location.endswith("parent"):
                        path = path.parent
                    path.parent.mkdir(parents=True, exist_ok=True)
                    if kind == "file":
                        path.write_bytes(b"existing owned bytes\n")
                    else:
                        path.mkdir()
                        (path / "sentinel").write_bytes(b"existing tree\n")
                    self.unchanged_rejection(self.project, prefix)

    def test_destination_and_parent_links_do_not_redirect_copy(self):
        for location in (*TARGETS, "package", "binary_parent", "package_parent", "prefix"):
            for dangling in (False, True):
                with self.subTest(location=location, dangling=dangling):
                    prefix, target = self.fresh("linked prefix"), self.fresh("owned link target")
                    target.mkdir()
                    (target / "sentinel").write_bytes(b"outside prefix stays unchanged\n")
                    before_target = state(target)
                    link_target = target / "absent" if dangling else target
                    if location == "prefix":
                        path = prefix
                    elif location.startswith("package"):
                        path = self.project.package(prefix)
                    else:
                        name = location if location in TARGETS else "hammond_render"
                        path = self.project.binary(prefix, name)
                    if location.endswith("parent"):
                        path = path.parent
                    path.parent.mkdir(parents=True, exist_ok=True)
                    self.make_link(path, link_target, directory=True)
                    self.unchanged_rejection(self.project, prefix)
                    self.assertEqual(state(target), before_target)

    def test_component_selection_preserves_legacy_payloads(self):
        for component in (None, "OfflineTools", "Standalone", "CaptureTools", "CrossoverTools",
                          "NativeVST3", "Unknown"):
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
        project = self.new_project("multi config", generator=generator, make_program=make_program)
        for name in TARGETS:
            with self.subTest(missing_debug=name), withheld(project.binaries["Debug"][name]):
                prefix = self.fresh("selected release")
                self.success(project.install(prefix, configuration="Release"))
                self.installed(project, prefix)
                self.unchanged_rejection(project, self.fresh("missing selected debug"), configuration="Debug")
        with withheld(project.binaries["Release"]["hammond_render"]):
            prefix = self.fresh("selected debug")
            self.success(project.install(prefix, configuration="Debug"))
            self.installed(project, prefix)
        prefix = self.fresh("lowercase config")
        self.success(project.install(prefix, configuration="release"))
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

    def test_installed_tool_rejections_preserve_inputs_outputs_and_package(self):
        prefix, foreign = self.fresh("output safety prefix"), self.fresh("outputs")
        foreign.mkdir()
        self.success(self.project.install(prefix))
        package = self.installed(self.project, prefix)
        graph = foreign / "pair.b3leakage"
        self.success(self.compile(package, foreign, PAIR, graph))
        existing = foreign / "existing.wav"
        existing.write_bytes(b"preserve prior user output\n")
        before_package, before_outputs = state(prefix), state(foreign)
        for output in (graph, package / PAIR, package / COMPILER):
            result = self.compile(package, foreign, PAIR, output)
            self.assertNotEqual(result.returncode, 0, diagnostic(result))
            self.assertEqual(result.stdout, b"")
            self.assertEqual(state(prefix), before_package)
            self.assertEqual(state(foreign), before_outputs)
        missing = foreign / "missing.b3leakage"
        result = invoke([self.project.binary(prefix, "hammond_source_leakage_probe"),
                         "--input", missing], foreign)
        self.assertNotEqual(result.returncode, 0, diagnostic(result))
        self.assertEqual(result.stdout, b"")
        base = [self.project.binary(prefix, "hammond_render"), "--profile", package / PROFILE,
                "--frames", "64", "--source-leakage", graph]
        for extra in (["--output", existing, "--leakage-input-gain", "0.75"],
                      ["--output", foreign / "unsafe.wav", "--leakage-input-gain", "1"],
                      ["--output", foreign / "missing-gain.wav"]):
            result = invoke([*base, *extra], foreign)
            self.assertNotEqual(result.returncode, 0, diagnostic(result))
            self.assertEqual(state(prefix), before_package)
            self.assertEqual(state(foreign), before_outputs)


if __name__ == "__main__":
    unittest.main()
