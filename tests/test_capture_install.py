#!/usr/bin/env python3
"""Independent real CaptureTools installation and relocation acceptance.

The literal inventory comes from the frozen capture-tools-install-v1 contract.
All mutations affect private copies. No native target is built by this suite.
CTest supplies HAMMOND_TEST_CMAKE; a direct run may supply it or use PATH.
"""

import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULES = (
    "validate_capture", "capture_common", "capture_audio", "capture_corpus",
    "compare_capture", "capture_job", "capture_readiness", "capture_study",
    "make_capture_demo", "verify_capture_report",
)
DATA = (
    "capture.schema.json", "capture-corpus.schema.json",
    "capture-policy.schema.json", "capture-job.schema.json",
    "capture-study.schema.json", "capture-planned-example.json",
    "corpus-planned-example.json", "capture-policy-synthetic-example.json",
)
DOCUMENTS = (
    "CAPTURE_FORMAT", "CAPTURE_PROTOCOL", "CAPTURE_VALIDATION", "CAPTURE_COMMON",
    "CAPTURE_AUDIO_CONTRACT", "CAPTURE_AUDIO", "CAPTURE_CORPUS_CONTRACT",
    "CAPTURE_CORPUS", "CAPTURE_COMPARISON_CONTRACT", "CAPTURE_COMPARISON",
    "CAPTURE_POLICY", "CAPTURE_JOB_CONTRACT", "CAPTURE_JOB", "CAPTURE_READINESS",
    "CAPTURE_STUDY", "CAPTURE_DEMO", "CAPTURE_REPLAY", "CAPTURE_TOOLS_INSTALL",
    "PLAN", "CALIBRATION_SCOPE", "CAPTURE_JOB_REVIEW",
)
DEMO_FILES = (
    "README.md", "EXPECTED.json", "study.json", "job-pass.json",
    "job-inconclusive.json", "job-fail.json", "policy-pass.json",
    "policy-inconclusive.json", "policy-fail.json", "corpus/corpus.json",
    "corpus/reference.json", "corpus/quarter.json", "corpus/half.json",
    "corpus/audio/reference.f32", "corpus/audio/quarter.f32", "corpus/audio/half.f32",
)
PAYLOAD = frozenset(
    ["README.md", "THIRD_PARTY_NOTICES.md"]
    + [f"tools/{name}.py" for name in MODULES]
    + [f"data/{name}" for name in DATA]
    + [f"docs/{name}.md" for name in DOCUMENTS]
    + [f"examples/capture-demo/{name}" for name in DEMO_FILES]
)
PACKAGE_SUFFIX = Path("hammond-b3-organ/capture-tools")
CLAIMS = (
    "boundary_equivalence", "synchronization", "authenticity", "specimen_identity",
    "calibration", "permissions", "independence", "preregistration",
    "final_holdout_history", "physical_fidelity",
)
VECTORS = {
    "reference": ([1.0, -1.0, 1.0, -1.0],
                  "fd801740524b1e1c23a61b5400725b76428652827ba1261b83243eb5ce551402",
                  "786665f3cf05b2f9b33e7cadee75e7176e122d62ad82133c72737c76261dd440"),
    "quarter": ([1.25, -0.75, 1.25, -0.75],
                "bac1c395abe23908b8c106a28b6c151bc25b9473d470f4d942775b5dfdf523e2",
                "79d8014af588d583abcc570598d3e073413543ef518b339cbca37dbb5eb6bd0c"),
    "half": ([1.5, -0.5, 1.5, -0.5],
             "36d231b4ecc15924aea04f08725924f18ae4346fd287747791d7396eca3d5758",
             "52c3450c9c276f60b8ed6dc728977cfe33b4b0702ce8332927169d25f18e4db8"),
}


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


def files(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file() and not p.is_symlink()}


def state(root):
    if not root.exists() and not root.is_symlink():
        return None
    result = {}
    for path in root.rglob("*"):
        name = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[name] = ("link", os.readlink(path))
        elif path.is_dir():
            result[name] = ("directory",)
        else:
            result[name] = ("file", path.read_bytes())
    return result


def environment():
    result = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for name in ("CMAKE_INSTALL_MODE", "DESTDIR", "PYTHONPATH", "PYTHONHOME"):
        result.pop(name, None)
    return result


def invoke(command, cwd, env=None):
    return subprocess.run(list(map(str, command)), cwd=cwd,
                          env=environment() if env is None else env,
                          capture_output=True, check=False, timeout=90)


def diagnostic(result):
    return (result.stdout + result.stderr).decode("utf-8", errors="replace")


class PrivateProject:
    """One ordinary repository configuration, with private source and no build."""

    def __init__(self, root, cmake):
        self.root, self.cmake = root, cmake
        self.source, self.build = root / "source", root / "build"
        self.source.mkdir()
        # Deliberately omit the PDF, Git database, build products and unrelated
        # tests. All native/source inputs needed for actual configuration remain.
        for directory in ("apps", "assets", "cmake", "data", "docs", "examples",
                          "include", "plugins", "src", "tools"):
            shutil.copytree(ROOT / directory, self.source / directory,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for path in ROOT.iterdir():
            if path.is_file() and path.suffix.lower() != ".pdf":
                shutil.copyfile(path, self.source / path.name)
        (self.source / "tests").mkdir()
        shutil.copyfile(Path(__file__), self.source / "tests" / Path(__file__).name)
        self.originals = {path: (self.source / path).read_bytes()
                          for path in PAYLOAD if path != "README.md"}
        self.configured = self.configure()

    def configure(self, *definitions, build=None):
        return invoke([
            self.cmake, "-S", self.source, "-B", self.build if build is None else build,
            "-DCMAKE_BUILD_TYPE=Release", "-DBUILD_TESTING=ON",
            "-DHAMMOND_BUILD_VST3=OFF", "-DHAMMOND_BUILD_STANDALONE=OFF",
            f"-DPython3_EXECUTABLE={sys.executable}", *definitions,
        ], self.root)

    def install(self, prefix, *, build=None, configuration="Release",
                component="CaptureTools", env=None):
        command = [self.cmake, "--install", self.build if build is None else build,
                   "--config", configuration, "--prefix", prefix]
        if component is not None:
            command.extend(("--component", component))
        return invoke(command, self.root, env)

    def package(self, prefix, datadir="share"):
        return prefix / datadir / PACKAGE_SUFFIX


class CaptureInstallAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        named = os.environ.get("HAMMOND_TEST_CMAKE") or shutil.which("cmake")
        if not named or not Path(named).is_file():
            raise RuntimeError("CaptureTools acceptance requires HAMMOND_TEST_CMAKE "
                               "or a real cmake on PATH; run through configured CTest")
        cls.cmake = Path(named).resolve(strict=True)
        cls.temp = tempfile.TemporaryDirectory(prefix="capture-install-acceptance-")
        cls.root = Path(cls.temp.name).resolve(strict=True)
        cls.project = PrivateProject(cls.root, cls.cmake)
        if cls.project.configured.returncode:
            raise RuntimeError("Private source configure failed:\n" + diagnostic(cls.project.configured))
        cls.counter = 0
        cls.live_sources = {path: (ROOT / path).read_bytes() for path in PAYLOAD
                            if path != "README.md"}
        for path in ("cmake/InstallCaptureTools.cmake", "cmake/InstallHammondTools.cmake"):
            cls.live_sources[path] = (ROOT / path).read_bytes()

    @classmethod
    def tearDownClass(cls):
        try:
            for path, payload in cls.live_sources.items():
                if (ROOT / path).read_bytes() != payload:
                    raise AssertionError("Qualified live source changed during install checks: " + path)
        finally:
            cls.temp.cleanup()

    def fresh(self, label="prefix"):
        type(self).counter += 1
        return self.root / f"{type(self).counter:03d}-{label}"

    def success(self, result):
        self.assertEqual(result.returncode, 0, diagnostic(result))

    def package_ok(self, package, originals=None):
        actual = files(package)
        self.assertEqual(len(PAYLOAD), 57)
        self.assertEqual(set(actual), PAYLOAD)
        self.assertFalse(any(p.is_symlink() for p in package.rglob("*")))
        for name, expected in (originals or self.project.originals).items():
            self.assertEqual(actual[name], expected, name)
        text = actual["README.md"].decode("utf-8")
        for token in ("tools/capture_job.py", "tools/capture_study.py",
                      "tools/verify_capture_report.py", "docs/CAPTURE_TOOLS_INSTALL.md",
                      "inconclusive", "failed", "synthetic"):
            self.assertIn(token, text)
        self.assertNotIn(str(self.project.source), text)
        self.assertNotIn(str(self.project.build), text)
        self.assertEqual(sum(len(actual["examples/capture-demo/" + p]) for p in DEMO_FILES), 32831)
        return actual

    def rejection_preserves(self, result, prefix, before, *, named=None):
        self.assertNotEqual(result.returncode, 0, diagnostic(result))
        self.assertIn("CaptureTools", diagnostic(result))
        if named is not None:
            # CMake may wrap diagnostics at spaces or use platform slashes.
            compact = "".join(diagnostic(result).replace("\\", "/").split())
            self.assertIn("".join(named.as_posix().split()), compact)
        self.assertEqual(state(prefix), before)

    def make_link(self, link, target, *, directory=False):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Native symlink creation unavailable: {error}")
        self.assertTrue(link.is_symlink())

    def test_exact_component_inventory_without_build(self):
        for executable in ("hammond_render", "hammond_model_info", "hammond_parameter_info",
                           "hammond_console_trace", "hammond_pedal_trace"):
            self.assertFalse(list(self.project.build.glob(executable + ".exe")))
            self.assertFalse((self.project.build / executable).exists())
            self.assertFalse((self.project.build / "Release" / (executable + ".exe")).exists())
        self.assertFalse((self.project.build / "nominal.b3p").exists())
        prefix = self.fresh("prefix with spaces-\u00e9\u97f3")
        prefix.mkdir()
        marker = prefix / "unrelated.txt"
        marker.write_bytes(b"preserve existing prefix content\n")
        self.success(self.project.install(prefix))
        package = self.project.package(prefix)
        self.package_ok(package)
        self.assertEqual(marker.read_bytes(), b"preserve existing prefix content\n")
        self.assertEqual(set(files(prefix)),
                         {"unrelated.txt"} | {"share/hammond-b3-organ/capture-tools/" + p for p in PAYLOAD})
        manifest = self.project.build / "install_manifest_CaptureTools.txt"
        observed = {Path(value).resolve() for value in manifest.read_text(encoding="utf-8").splitlines()}
        self.assertEqual(observed, {(package / name).resolve() for name in PAYLOAD})

    def test_ctest_receives_configured_cmake(self):
        ctest = self.cmake.with_name("ctest" + self.cmake.suffix)
        self.assertTrue(ctest.is_file())
        result = invoke([ctest, "--test-dir", self.project.build, "-C", "Release",
                         "--show-only=json-v1", "-R", "^python_test_capture_install$"], self.root)
        self.success(result)
        tests = json.loads(result.stdout)["tests"]
        self.assertEqual(len(tests), 1)
        properties = {row["name"]: row["value"] for row in tests[0]["properties"]}
        variables = dict(item.split("=", 1) for item in properties["ENVIRONMENT"])
        self.assertEqual(Path(variables["HAMMOND_TEST_CMAKE"]).resolve(), self.cmake)
        self.assertEqual(properties["TIMEOUT"], 180.0)

    def test_import_closure_contains_only_packaged_or_standard_modules(self):
        local = set(MODULES)
        for name in MODULES:
            tree = ast.parse(self.project.originals[f"tools/{name}.py"])
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported = [item.name.split(".", 1)[0] for item in node.names]
                elif isinstance(node, ast.ImportFrom):
                    if node.level:
                        self.assertEqual(node.level, 1, "Only a packaged sibling can supply a relative import")
                        siblings = ([node.module.split(".", 1)[0]] if node.module else
                                    [item.name.split(".", 1)[0] for item in node.names])
                        for sibling in siblings:
                            self.assertIn(sibling, local, (name, sibling))
                        continue
                    imported = [(node.module or "").split(".", 1)[0]]
                else:
                    continue
                for module in imported:
                    self.assertIn(module, local | sys.stdlib_module_names, (name, module))

    def test_repeat_configuration_and_configuration_independent_copy(self):
        self.success(self.project.configure())
        inventories = []
        for configuration, mode in (("Release", None), ("Debug", "COPY"),
                                    ("NoNativeConfiguration", "")):
            prefix = self.fresh("configuration")
            env = environment()
            if mode is not None:
                env["CMAKE_INSTALL_MODE"] = mode
            self.success(self.project.install(prefix, configuration=configuration, env=env))
            inventories.append(self.package_ok(self.project.package(prefix)))
        self.assertEqual(inventories[0], inventories[1])
        self.assertEqual(inventories[1], inventories[2])

    def test_custom_relative_datadir(self):
        build = self.fresh("custom-build")
        self.success(self.project.configure("-DCMAKE_INSTALL_DATADIR=assets/reference", build=build))
        self.success(self.project.configure("-DCMAKE_INSTALL_DATADIR=assets/reference", build=build))
        prefix = self.fresh("custom-prefix")
        self.success(self.project.install(prefix, build=build, configuration="Debug"))
        self.package_ok(self.project.package(prefix, "assets/reference"))
        self.assertFalse((prefix / "share").exists())

    def test_invalid_datadirs_reject_during_configuration(self):
        build = self.fresh("invalid-directory-build")
        self.success(self.project.configure(build=build))
        for invalid in ("", "../escape", "..\\escape", "/absolute", "C:/absolute", "one;two"):
            with self.subTest(value=invalid):
                result = self.project.configure(f"-DCMAKE_INSTALL_DATADIR:PATH={invalid}", build=build)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("nonempty relative", diagnostic(result))

    def test_every_payload_input_is_preflighted_before_prefix_writes(self):
        generated = [p for p in self.project.build.rglob("README.md")
                     if "capture" in p.relative_to(self.project.build).as_posix().lower()]
        self.assertEqual(len(generated), 1, "Locate the generated entry point, not the installer's list")
        inputs = [self.project.source / p for p in sorted(PAYLOAD - {"README.md"})] + generated
        self.assertEqual(len(inputs), 57)
        prefix = self.fresh("missing-input-prefix")
        prefix.mkdir()
        (prefix / "unrelated.txt").write_bytes(b"old prefix remains\n")
        before = state(prefix)
        for path in inputs:
            with self.subTest(input=path.name):
                payload = path.read_bytes()
                path.unlink()
                try:
                    self.assertFalse(path.exists(), "The intended missing-input fault must execute")
                    result = self.project.install(prefix)
                    self.rejection_preserves(result, prefix, before, named=path)
                finally:
                    path.write_bytes(payload)

    def test_empty_and_directory_inputs_reject_before_writes(self):
        prefix = self.fresh("malformed-input-prefix")
        prefix.mkdir()
        (prefix / "unrelated.txt").write_bytes(b"retain\n")
        before = state(prefix)
        for relative in ("tools/capture_audio.py", "THIRD_PARTY_NOTICES.md"):
            path = self.project.source / relative
            payload = path.read_bytes()
            with self.subTest(input=relative, kind="empty"):
                try:
                    path.write_bytes(b"")
                    self.assertEqual(path.stat().st_size, 0)
                    self.rejection_preserves(self.project.install(prefix), prefix, before, named=path)
                finally:
                    path.write_bytes(payload)
            with self.subTest(input=relative, kind="directory"):
                path.unlink()
                path.mkdir()
                try:
                    self.assertTrue(path.is_dir())
                    self.rejection_preserves(self.project.install(prefix), prefix, before, named=path)
                finally:
                    path.rmdir()
                    path.write_bytes(payload)

    def test_source_symlink_rejects_before_writes(self):
        prefix = self.fresh("source-link-prefix")
        prefix.mkdir()
        (prefix / "unrelated.txt").write_bytes(b"retain\n")
        before = state(prefix)
        target = self.fresh("source-link-target")
        target.write_bytes(b"nonempty link target\n")
        path = self.project.source / "THIRD_PARTY_NOTICES.md"
        payload = path.read_bytes()
        path.unlink()
        try:
            self.make_link(path, target)
            self.rejection_preserves(self.project.install(prefix), prefix, before, named=path)
        finally:
            if path.is_symlink():
                path.unlink()
            path.write_bytes(payload)

    def test_noncopy_modes_reject_before_writes(self):
        prefix = self.fresh("mode-prefix")
        prefix.mkdir()
        (prefix / "unrelated.txt").write_bytes(b"retain modes\n")
        before = state(prefix)
        for mode in ("SYMLINK", "REL_SYMLINK", "ABS_SYMLINK_OR_COPY", "copy", "INVALID"):
            with self.subTest(mode=mode):
                env = environment()
                env["CMAKE_INSTALL_MODE"] = mode
                result = self.project.install(prefix, env=env)
                self.rejection_preserves(result, prefix, before)
                self.assertIn("CMAKE_INSTALL_MODE", diagnostic(result))

    def test_existing_destination_file_directory_and_completed_package_survive(self):
        for kind in ("file", "directory", "complete"):
            with self.subTest(kind=kind):
                prefix = self.fresh("existing-prefix")
                package = self.project.package(prefix)
                if kind == "complete":
                    self.success(self.project.install(prefix))
                else:
                    package.parent.mkdir(parents=True)
                    if kind == "file":
                        package.write_bytes(b"existing destination file\n")
                    else:
                        package.mkdir()
                        (package / "owned.txt").write_bytes(b"existing destination tree\n")
                before = state(prefix)
                self.rejection_preserves(self.project.install(prefix), prefix, before, named=package)

    def test_existing_destination_links_survive(self):
        for dangling in (False, True):
            with self.subTest(dangling=dangling):
                prefix = self.fresh("destination-link-prefix")
                package = self.project.package(prefix)
                package.parent.mkdir(parents=True)
                target = self.fresh("destination-link-target")
                if not dangling:
                    target.mkdir()
                    (target / "other.txt").write_bytes(b"other owner\n")
                self.make_link(package, target, directory=True)
                before = state(prefix)
                target_before = state(target)
                self.rejection_preserves(self.project.install(prefix), prefix, before, named=package)
                self.assertEqual(state(target), target_before)

    @unittest.skipIf(os.name == "nt", "CMake DESTDIR staging is a POSIX facility")
    def test_destdir_staging_uses_actual_staged_destination(self):
        stage = self.fresh("stage-\u00e9")
        prefix = self.fresh("logical-prefix")
        env = environment()
        env["DESTDIR"] = str(stage)
        self.success(self.project.install(prefix, env=env))
        actual_prefix = stage / str(prefix).lstrip("/")
        self.package_ok(self.project.package(actual_prefix))
        self.assertFalse(prefix.exists())
        before = state(stage)
        self.rejection_preserves(self.project.install(prefix, env=env), stage, before)

    def test_component_is_excluded_from_default_and_other_selections(self):
        # A private no-language project isolates CMake's component dispatch. Its
        # one unrelated rule is a sentinel, not a fake native-runtime result.
        source = self.fresh("component-source")
        source.mkdir()
        for name, payload in self.project.originals.items():
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        (source / "cmake").mkdir()
        for name in ("InstallHammondTools.cmake", "InstallCaptureTools.cmake"):
            shutil.copyfile(self.project.source / "cmake" / name, source / "cmake" / name)
        (source / "sentinel.txt").write_bytes(b"independent component sentinel\n")
        (source / "CMakeLists.txt").write_text(
            'cmake_minimum_required(VERSION 3.21)\n'
            'project(CaptureComponentIsolation LANGUAGES NONE)\n'
            'include(cmake/InstallHammondTools.cmake)\n'
            'include(cmake/InstallCaptureTools.cmake)\n'
            'install(FILES "${PROJECT_SOURCE_DIR}/sentinel.txt" DESTINATION other COMPONENT Other)\n',
            encoding="utf-8")
        build = self.fresh("component-build")
        self.success(invoke([self.cmake, "-S", source, "-B", build], self.root))
        for selected in (None, "Other", "OfflineTools", "NativeStandalone", "NativeVST3"):
            with self.subTest(component=selected):
                prefix = self.fresh("component-prefix")
                self.success(self.project.install(prefix, build=build, component=selected))
                expected = {"other/sentinel.txt": b"independent component sentinel\n"}
                self.assertEqual(files(prefix) if prefix.exists() else {},
                                 expected if selected in (None, "Other") else {})
        prefix = self.fresh("selected-capture-prefix")
        self.success(self.project.install(prefix, build=build))
        self.package_ok(self.project.package(prefix))
        self.assertFalse((prefix / "other").exists())

    def test_late_install_abort_preserves_partial_package(self):
        # Instrument only the private generated install script, after the first
        # real copy. This is a deterministic late abort, not a disk-failure claim.
        script = self.project.build / "cmake_install.cmake"
        original = script.read_text(encoding="utf-8")
        # The ordinary project lists OfflineTools first. Find the first actual
        # copy that belongs to CaptureTools, rather than aborting an unrelated rule.
        capture_start = original.index('CMAKE_INSTALL_COMPONENT STREQUAL "CaptureTools"')
        start = original.index("file(INSTALL", capture_start)
        depth, quote, escaped, end = 0, False, False, None
        for position in range(start + 4, len(original)):
            char = original[position]
            if escaped:
                escaped = False
            elif char == "\\" and quote:
                escaped = True
            elif char == '"':
                quote = not quote
            elif not quote:
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                    if depth == 0:
                        end = position + 1
                        break
        self.assertIsNotNone(end)
        prefix = self.fresh("late-failure-prefix")
        package = self.project.package(prefix)
        marker = package / "other-writer-marker.txt"
        # Copy literal bytes: CMake's text writer uses native line endings.
        marker_source = self.fresh("other-writer-source.bin")
        marker_bytes = b"preserve other writer\r\n\x00unchanged\n"
        marker_source.write_bytes(marker_bytes)
        injected = ('\nfile(COPY_FILE [=[' + marker_source.as_posix() + ']=] [=['
                    + marker.as_posix() + ']=])\n'
                    'message(FATAL_ERROR "capture acceptance reached late abort")\n')
        try:
            script.write_text(original[:end] + injected + original[end:], encoding="utf-8")
            result = self.project.install(prefix)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("capture acceptance reached late abort", diagnostic(result))
            self.assertIn("partial", diagnostic(result).lower())
            self.assertEqual(marker.read_bytes(), marker_bytes)
            retained = files(package)
            self.assertGreater(len(retained), 1)
            self.assertLess(len(retained), 58)
            for name, payload in retained.items():
                if name != "other-writer-marker.txt":
                    self.assertIn(name, PAYLOAD)
                    if name != "README.md":
                        self.assertEqual(payload, self.project.originals[name])
        finally:
            script.write_text(original, encoding="utf-8")

    def test_relocated_tools_work_after_private_sources_and_build_are_removed(self):
        work = self.fresh("relocation-work")
        work.mkdir()
        project = PrivateProject(work, self.cmake)
        self.success(project.configured)
        prefix = work / "original prefix"
        self.success(project.install(prefix))
        moved = work / "moved prefix-\u00e9\u97f3"
        prefix.rename(moved)
        package = project.package(moved)
        original_package = self.package_ok(package, project.originals)
        demo = package / "examples/capture-demo"
        for name, (samples, raw_digest, decoded_digest) in VECTORS.items():
            payload = (demo / f"corpus/audio/{name}.f32").read_bytes()
            self.assertEqual(payload, struct.pack("<4f", *samples))
            self.assertEqual(sha(payload), raw_digest)
            decoded = b"HAMMOND-CAPTURE-DECODED-V1\0" + struct.pack("<IIQ", 4, 1, 4)
            self.assertEqual(sha(decoded + struct.pack("<4d", *samples)), decoded_digest)
        shutil.rmtree(project.source)
        shutil.rmtree(project.build)
        self.assertFalse(project.source.exists())
        self.assertFalse(project.build.exists())
        self.assertFalse(prefix.exists())
        foreign = work / "foreign directory-\u00e9\u97f3"
        foreign.mkdir()
        outputs = foreign / "reports"
        outputs.mkdir()
        env = {key: value for key, value in environment().items()
               if not key.upper().startswith("HAMMOND_")}
        env["PYTHONIOENCODING"] = "ascii:strict"
        env["PYTHONUTF8"] = "0"

        def run(module, args, code, *, report=True):
            result = invoke([sys.executable, "-B", "-S", package / "tools" / (module + ".py"),
                             *args], foreign, env)
            self.assertEqual(result.returncode, code, diagnostic(result))
            self.assertEqual(result.stderr, b"")
            if report:
                value = json.loads(result.stdout)
                self.assertEqual(result.stdout, canonical(value))
                return value, result.stdout
            return result

        probe = ('import importlib,json,pathlib,sys; '
                 'sys.path.insert(0,sys.argv[1]); '
                 'print(json.dumps({n:str(pathlib.Path(importlib.import_module(n).__file__).resolve()) '
                 'for n in sys.argv[2:]},sort_keys=True))')
        imports = invoke([sys.executable, "-B", "-S", "-c", probe, package / "tools", *MODULES], foreign, env)
        self.success(imports)
        self.assertEqual(json.loads(imports.stdout),
                         {name: str((package / "tools" / (name + ".py")).resolve()) for name in MODULES})
        run("validate_capture", ["--input", package / "data/capture-planned-example.json"], 0, report=False)
        readiness, _ = run("capture_readiness", ["--input", package / "data/capture-planned-example.json"], 3)
        self.assertEqual(readiness["status"], "planned")
        self.assertEqual(len(readiness["checks"]), 21)
        planned, _ = run("capture_corpus", ["--input", package / "data/corpus-planned-example.json"], 3)
        self.assertEqual(planned["status"], "inconclusive")
        corpus, _ = run("capture_corpus", ["--input", demo / "corpus/corpus.json", "--check-files", "--check-audio"], 0)
        self.assertEqual(corpus["status"], "pass")
        self.assertEqual(corpus["index_sha256"], sha((demo / "corpus/corpus.json").read_bytes()))
        audio = invoke([sys.executable, "-B", "-S", package / "tools/capture_audio.py",
                        "--input", demo / "corpus/audio/reference.f32", "--raw-format", "raw_float32_le",
                        "--sample-rate-hz", "4", "--channel-count", "1"], foreign, env)
        self.success(audio)
        self.assertEqual(audio.stderr, b"")
        inspected = json.loads(audio.stdout)
        self.assertEqual(inspected["decoded_sha256"], VECTORS["reference"][2])
        self.assertEqual(inspected["sha256"], VECTORS["reference"][1])
        self.assertEqual((inspected["frame_count"], inspected["sample_rate_hz"], inspected["channel_count"]), (4, 4, 1))
        self.assertEqual((inspected["channels"][0]["dc"], inspected["channels"][0]["rms"]), (0, 1))
        jobs = []
        saved_reports = []
        for name, status, exit_code, error, limit in (
                ("pass", "pass", 0, 0.25, 0.375),
                ("inconclusive", "inconclusive", 3, 0.25, 0.25),
                ("fail", "failed", 1, 0.5, 0.25)):
            path = outputs / f"{name}.json"
            report, payload = run("capture_job", ["--input", demo / f"job-{name}.json", "--output", path], exit_code)
            self.assertEqual(report["status"], status)
            self.assertEqual(path.read_bytes(), payload)
            self.assertEqual(report["inputs"]["job"],
                             {"size_bytes": (demo / f"job-{name}.json").stat().st_size,
                              "sha256": sha((demo / f"job-{name}.json").read_bytes())})
            for claim in CLAIMS:
                self.assertEqual(report[claim], "not_established")
            metrics = report["evaluation"]["comparison"]["channels"][0]["metrics"]
            for metric in ("rms_error_fs", "max_abs_error_fs", "dc_bias_fs", "absolute_dc_bias_fs"):
                self.assertEqual(metrics[metric], {"value": error, "unit": "FS", "undefined_reason": None})
            criterion = report["evaluation"]["criteria"][0]
            self.assertEqual(criterion["upper_bound"], limit)
            self.assertEqual(criterion["interval"],
                             {"lower": error - 0.125, "upper": error + 0.125,
                              "unit": "FS", "undefined_reason": None})
            for observation in report["tool_sources"]:
                source = (package / "tools" / observation["module"]).read_bytes()
                self.assertEqual(observation["sha256"], sha(source))
                self.assertEqual(observation["size_bytes"], len(source))
            jobs.append(report)
            saved_reports.append(("job", demo / f"job-{name}.json", path, status, payload))
        path = outputs / "study.json"
        study, payload = run("capture_study", ["--input", demo / "study.json", "--output", path], 1)
        self.assertEqual(path.read_bytes(), payload)
        self.assertEqual(study["status"], "failed")
        self.assertEqual([row["report"] for row in study["jobs"]], jobs)
        self.assertEqual(study["work"], {"window_samples": 12, "spectral_terms": 12})
        self.assertEqual(study["summary"], {"jobs": 3, "pass": 1, "inconclusive": 1, "failed": 1,
                                          "roles": {"fit": 0, "validation": 3, "final_test": 0, "unassigned": 0}})
        saved_reports.append(("study", demo / "study.json", path, "failed", payload))
        for kind, source, report_path, status, original_bytes in saved_reports:
            verification, _ = run("verify_capture_report",
                                  ["--kind", kind, "--input", source, "--report", report_path], 0)
            self.assertEqual(verification["status"], "match")
            self.assertIs(verification["exact_report_match"], True)
            self.assertEqual(verification["saved_engineering_status"], status)
            self.assertEqual(verification["replayed_engineering_status"], status)
            self.assertEqual(verification["saved_report"],
                             {"size_bytes": len(original_bytes), "sha256": sha(original_bytes)})
            self.assertEqual(verification["replayed_report"], verification["saved_report"])
            self.assertEqual(report_path.read_bytes(), original_bytes)
            for claim in CLAIMS:
                self.assertEqual(verification[claim], "not_established")
        generated = outputs / "new demo"
        inventory, _ = run("make_capture_demo", ["--output", generated], 0)
        self.assertEqual(inventory["execution"], "not_run")
        self.assertEqual(inventory["file_count"], 16)
        self.assertEqual(inventory["total_size_bytes"], 32831)
        self.assertEqual(files(generated), files(demo))
        self.assertEqual(files(package), original_package)


if __name__ == "__main__":
    unittest.main()
