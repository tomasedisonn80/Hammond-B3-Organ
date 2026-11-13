#!/usr/bin/env python3
"""Offline SDL2 admission tests; synthetic fixtures are not official SDL sources."""

from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(os.environ.get("HAMMOND_SOURCE_DIR", Path(__file__).resolve().parents[1]))
spec = importlib.util.spec_from_file_location("acquire_sdl2", ROOT / "tools/acquire_sdl2.py")
assert spec is not None and spec.loader is not None
sdl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sdl)

# Independent literals: a coordinated unreviewed change to code and lock must
# not turn the synthetic-fixture tests into acceptance of another real release.
REVIEWED_LOCK = {
    "schema_version": 1,
    "name": "SDL2",
    "version": "2.32.10",
    "repository": "https://github.com/libsdl-org/SDL.git",
    "tag": "release-2.32.10",
    "commit": "5d249570393f7a37e037abf22cd6012a4cc56a71",
    "license": {
        "spdx": "Zlib", "path": "LICENSE.txt", "bytes": 884,
        "sha256": "97f35b302b361680ec1e891e95d2d52097bb95abff361434916d99dc1305f127",
    },
}


def git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=SDL fixture",
         "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
         *arguments], check=True, capture_output=True, text=True,
        encoding="utf-8", errors="strict", timeout=20,
    ).stdout.strip()


def snapshot(root: Path) -> dict:
    """Observe file bytes, modes and mtimes, including private Git metadata."""
    result = {}
    for path in sorted(root.rglob("*")):
        stat = path.lstat()
        payload = (os.readlink(path) if path.is_symlink() else
                   hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None)
        result[path.relative_to(root).as_posix()] = (stat.st_mode, stat.st_mtime_ns, payload)
    return result


class SdlLockTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-sdl-lock-")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.path = self.directory / "lock.json"

    def test_exact_reviewed_release_identity(self):
        self.assertEqual(sdl.load_lock(ROOT / "data/dependencies/sdl2-lock.json"), REVIEWED_LOCK)

    def test_malformed_bounded_json_and_read_errors(self):
        for raw in (b"{", b"\xff", b"[]", b"null", b'{"x":NaN}',
                    b" " * (16 * 1024 + 1), b"[" * 2000 + b"]" * 2000):
            with self.subTest(raw=raw[:40]):
                self.path.write_bytes(raw)
                with self.assertRaises(sdl.SdlError):
                    sdl.load_lock(self.path)
        for path in (self.directory, self.directory / "missing.json"):
            with self.subTest(path=path), self.assertRaisesRegex(sdl.SdlError, "cannot read"):
                sdl.load_lock(path)

    def test_duplicate_fields_reject_at_root_and_in_license(self):
        raw = json.dumps(REVIEWED_LOCK)
        for field, value in (("schema_version", "1"), ("spdx", '"Zlib"')):
            self.path.write_text(raw.replace(f'"{field}": {value}',
                                            f'"{field}": {value}, "{field}": {value}'),
                                 encoding="utf-8")
            with self.subTest(field=field), self.assertRaisesRegex(sdl.SdlError, "duplicate"):
                sdl.load_lock(self.path)

    def test_unknown_missing_and_substituted_fields_reject_before_git(self):
        variants = []
        for key, value in (("schema_version", True), ("schema_version", 1.0),
                           ("name", "SDL3"), ("version", "2.32.9"),
                           ("repository", "file:///unreviewed"), ("tag", "--unreviewed"),
                           ("commit", "0" * 40), ("extra", None), ("license", [])):
            record = copy.deepcopy(REVIEWED_LOCK)
            record[key] = value
            variants.append(record)
        missing = copy.deepcopy(REVIEWED_LOCK)
        del missing["tag"]
        variants.append(missing)
        for key, value in (("bytes", 884.0), ("path", "../LICENSE.txt"),
                           ("sha256", "0" * 64), ("extra", None)):
            record = copy.deepcopy(REVIEWED_LOCK)
            record["license"][key] = value
            variants.append(record)
        sentinel = self.directory / "preserved"
        sentinel.write_bytes(b"existing destination\n")
        with mock.patch.object(sdl.subprocess, "run", side_effect=AssertionError("Git must not run")):
            for record in variants:
                self.path.write_text(json.dumps(record), encoding="utf-8")
                with self.subTest(record=record):
                    with self.assertRaises(sdl.SdlError):
                        sdl.load_lock(self.path)
                    for action in ("--destination", "--verify-existing"):
                        with contextlib.redirect_stdout(io.StringIO()) as out, \
                                contextlib.redirect_stderr(io.StringIO()) as err:
                            code = sdl.main([action, str(sentinel), "--lock", str(self.path)])
                        self.assertEqual(code, 1)
                        self.assertEqual(out.getvalue(), "")
                        self.assertIn("SDL2 error:", err.getvalue())
        self.assertEqual(sentinel.read_bytes(), b"existing destination\n")

    def test_cli_requires_exactly_one_action(self):
        for arguments in ([], ["--destination", "a", "--verify-existing", "b"]):
            with self.subTest(arguments=arguments), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    sdl.main(arguments)
                self.assertEqual(error.exception.code, 2)


class SdlFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shared = tempfile.TemporaryDirectory(prefix="hammond-sdl-template-")
        cls.template = Path(cls.shared.name) / "synthetic SDL source"
        (cls.template / "include").mkdir(parents=True)
        git(cls.template, "init", "--quiet")
        git(cls.template, "config", "core.autocrlf", "false")
        notice = b"Synthetic local test fixture; no upstream SDL source or license text.\n"
        for name, raw in {
            "LICENSE.txt": notice,
            "CMakeLists.txt": b"# Synthetic fixture; never evaluated by SDL verification.\n",
            "include/SDL.h": b"/* Synthetic header fixture. */\n",
            "include/SDL_version.h": b"/* Synthetic version fixture. */\n",
            "README.md": b"Synthetic ancestor\n",
        }.items():
            (cls.template / name).write_bytes(raw)
        git(cls.template, "add", ".")
        git(cls.template, "commit", "--quiet", "-m", "Synthetic ancestor")
        (cls.template / "README.md").write_bytes(b"Synthetic selected release\n")
        git(cls.template, "commit", "--quiet", "-a", "-m", "Synthetic selected release")
        record = {
            "schema_version": 1, "name": "SDL2", "version": "synthetic-test",
            "repository": cls.template.as_uri(), "tag": "synthetic-release",
            "commit": git(cls.template, "rev-parse", "HEAD"),
            "license": {"spdx": "Zlib", "path": "LICENSE.txt", "bytes": len(notice),
                        "sha256": hashlib.sha256(notice).hexdigest()},
        }
        git(cls.template, "tag", record["tag"])
        cls.fixture_lock = Path(cls.shared.name) / "synthetic-lock.json"
        cls.fixture_lock.write_text(json.dumps(record), encoding="utf-8")
        # Patch only this imported module, only while admitting this local
        # fixture. Production constants and the real repository lock stay intact.
        with mock.patch.multiple(sdl, ROOT_URL=record["repository"],
                                 REVIEWED_VERSION=record["version"], REVIEWED_TAG=record["tag"],
                                 REVIEWED_COMMIT=record["commit"], REVIEWED_LICENSE=record["license"]):
            cls.lock = sdl.load_lock(cls.fixture_lock)

    @classmethod
    def tearDownClass(cls):
        cls.shared.cleanup()

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-sdl-test-")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.checkout = self.directory / "source with spaces"
        shutil.copytree(self.template, self.checkout)
        self.record = copy.deepcopy(self.lock)

    def commit_fixture(self, root: Path) -> dict:
        git(root, "add", "-A")
        git(root, "commit", "--quiet", "-m", "Synthetic mutation")
        record = copy.deepcopy(self.record)
        record["commit"] = git(root, "rev-parse", "HEAD")
        git(root, "tag", "-f", record["tag"])
        return record

    def symlink(self, link: Path, target: Path):
        try:
            link.symlink_to(target, target_is_directory=target.is_dir())
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"host cannot create test symlinks: {exc}")

    def test_synthetic_lock_is_rejected_without_fixture_patches(self):
        with self.assertRaisesRegex(sdl.SdlError, "reviewed official release identity"):
            sdl.load_lock(self.fixture_lock)

    def test_valid_verification_is_read_only_and_cannot_use_network(self):
        git(self.checkout, "remote", "add", "unused", "https://not-contacted.invalid/SDL.git")
        before = snapshot(self.checkout)
        redirected = {name: str(self.directory / "wrong-git-path") for name in (
            "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
            "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE", "GIT_PREFIX")}
        with mock.patch.dict(os.environ, redirected), \
                mock.patch.object(sdl.subprocess, "run", wraps=subprocess.run) as run:
            result = sdl.verify_sdl2(self.checkout, self.record)
        self.assertFalse(result["network_used"])
        self.assertEqual(result["sdl2_root"], str(self.checkout.resolve()))
        self.assertEqual(result["commit"], self.record["commit"])
        self.assertEqual(result["primary_licenses_verified"], 1)
        self.assertEqual(snapshot(self.checkout), before)
        self.assertGreater(len(run.call_args_list), 0)
        for call in run.call_args_list:
            command, env = call.args[0], call.kwargs["env"]
            self.assertEqual(command[0], "git")
            self.assertIn(command[7], {"rev-parse", "config", "ls-files", "status"})
            self.assertIn("protocol.allow=never", command)
            self.assertIn("core.fsmonitor=false", command)
            self.assertTrue(set(redirected).isdisjoint(env))
            for key, value in (("GIT_OPTIONAL_LOCKS", "0"), ("GIT_NO_REPLACE_OBJECTS", "1"),
                               ("GIT_NO_LAZY_FETCH", "1"), ("GIT_TERMINAL_PROMPT", "0")):
                self.assertEqual(env[key], value)

    def test_missing_non_git_and_inherited_checkout_roots_reject(self):
        for root, message in ((self.directory / "missing", "checkout is missing"),
                              (self.directory, "Git inspection failed"),
                              (self.checkout / "include", "not the root of its own checkout")):
            with self.subTest(root=root), self.assertRaisesRegex(sdl.SdlError, message):
                sdl.verify_sdl2(root, self.record)

    def test_head_and_release_tag_are_separate_requirements(self):
        (self.checkout / "README.md").write_bytes(b"Unreviewed local commit\n")
        changed = self.commit_fixture(self.checkout)
        with self.assertRaisesRegex(sdl.SdlError, "root commit mismatch"):
            sdl.verify_sdl2(self.checkout, self.record)
        git(self.checkout, "tag", "-f", changed["tag"], "HEAD^")
        with self.assertRaisesRegex(sdl.SdlError, "release tag does not resolve"):
            sdl.verify_sdl2(self.checkout, changed)
        git(self.checkout, "tag", "-d", changed["tag"])
        with self.assertRaisesRegex(sdl.SdlError, "Git inspection failed"):
            sdl.verify_sdl2(self.checkout, changed)
        git(self.checkout, "tag", "-a", "-m", "Synthetic annotated tag", changed["tag"])
        self.assertEqual(sdl.verify_sdl2(self.checkout, changed)["commit"], changed["commit"])

    def test_staged_and_unstaged_source_changes_reject_at_same_head(self):
        source = self.checkout / "include/SDL.h"
        source.write_bytes(source.read_bytes() + b"unreviewed bytes\n")
        with self.assertRaisesRegex(sdl.SdlError, "tracked files are modified"):
            sdl.verify_sdl2(self.checkout, self.record)
        git(self.checkout, "add", "include/SDL.h")
        self.assertEqual(git(self.checkout, "rev-parse", "HEAD"), self.record["commit"])
        with self.assertRaisesRegex(sdl.SdlError, "tracked files are modified"):
            sdl.verify_sdl2(self.checkout, self.record)

    def test_untracked_and_ignored_inputs_reject_but_empty_directories_do_not(self):
        extra = self.checkout / "generated/CMakeLists.txt"
        extra.parent.mkdir()
        extra.write_bytes(b"# Unreviewed discovered input\n")
        with self.assertRaisesRegex(sdl.SdlError, "untracked or ignored files"):
            sdl.verify_sdl2(self.checkout, self.record)
        (self.checkout / ".git/info/exclude").write_text("generated/\n", encoding="utf-8")
        self.assertEqual(git(self.checkout, "status", "--porcelain=v1"), "")
        self.assertEqual(git(self.checkout, "rev-parse", "HEAD"), self.record["commit"])
        with self.assertRaisesRegex(sdl.SdlError, "untracked or ignored files"):
            sdl.verify_sdl2(self.checkout, self.record)
        extra.unlink()
        (self.directory / "external-build-output").write_bytes(b"safe external output\n")
        self.assertFalse(sdl.verify_sdl2(self.checkout, self.record)["network_used"])

    def test_assume_unchanged_and_skip_worktree_cannot_hide_tampering(self):
        for flag in ("--assume-unchanged", "--skip-worktree"):
            root = self.directory / flag.removeprefix("--")
            shutil.copytree(self.template, root)
            git(root, "update-index", flag, "include/SDL.h")
            source = root / "include/SDL.h"
            if flag == "--skip-worktree":
                source.unlink()
            else:
                source.write_bytes(b"hidden modification\n")
            self.assertEqual(git(root, "status", "--porcelain=v1"), "")
            before = snapshot(root)
            with self.subTest(flag=flag), self.assertRaisesRegex(sdl.SdlError, "index has hidden/sparse"):
                sdl.verify_sdl2(root, self.record)
            self.assertEqual(snapshot(root), before)

    def test_partial_or_promisor_configuration_rejects_before_object_inspection(self):
        for key, value in (("extensions.partialClone", "origin"), ("remote.origin.promisor", "true")):
            root = self.directory / key
            shutil.copytree(self.template, root)
            git(root, "config", key, value)
            with self.subTest(key=key), \
                    mock.patch.object(sdl.subprocess, "run", wraps=subprocess.run) as run:
                with self.assertRaisesRegex(sdl.SdlError, "partial/promisor"):
                    sdl.verify_sdl2(root, self.record)
            self.assertFalse(any("HEAD^{commit}" in call.args[0] for call in run.call_args_list))

    def test_committed_missing_required_sources_are_rejected(self):
        for index, name in enumerate(("CMakeLists.txt", "include/SDL.h", "include/SDL_version.h")):
            root = self.directory / f"missing-source-{index}"
            shutil.copytree(self.template, root)
            (root / name).unlink()
            record = self.commit_fixture(root)
            with self.subTest(name=name), self.assertRaisesRegex(sdl.SdlError, "source file is missing"):
                sdl.verify_sdl2(root, record)

    def test_committed_source_and_license_symlinks_are_rejected(self):
        target = self.directory / "external-bytes"
        target.write_bytes(b"external bytes\n")
        for index, name in enumerate(("include/SDL.h", "LICENSE.txt")):
            root = self.directory / f"symlink-source-{index}"
            shutil.copytree(self.template, root)
            (root / name).unlink()
            self.symlink(root / name, target)
            record = self.commit_fixture(root)
            with self.subTest(name=name), self.assertRaisesRegex(sdl.SdlError, "symlink"):
                sdl.verify_sdl2(root, record)
        self.assertEqual(target.read_bytes(), b"external bytes\n")

    def test_committed_license_size_and_same_size_digest_tamper_reject(self):
        original = (self.checkout / "LICENSE.txt").read_bytes()
        for index, raw in enumerate((original + b"\n", b"X" * len(original))):
            root = self.directory / f"license-tamper-{index}"
            shutil.copytree(self.template, root)
            (root / "LICENSE.txt").write_bytes(raw)
            record = self.commit_fixture(root)
            with self.subTest(index=index), self.assertRaisesRegex(sdl.SdlError, "size/SHA-256 mismatch"):
                sdl.verify_sdl2(root, record)

    def test_existing_destinations_including_broken_symlinks_are_preserved(self):
        empty = self.directory / "empty"
        empty.mkdir()
        regular = self.directory / "existing-file"
        regular.write_bytes(b"preserve file\n")
        linked, broken = self.directory / "linked", self.directory / "broken"
        self.symlink(linked, self.checkout)
        self.symlink(broken, self.directory / "missing-target")
        before = snapshot(self.directory)
        with mock.patch.object(sdl.subprocess, "run", side_effect=AssertionError("Git must not run")):
            for destination in (self.checkout, empty, regular, linked, broken):
                with self.subTest(destination=destination), self.assertRaisesRegex(sdl.SdlError, "already exists"):
                    sdl.acquire_sdl2(destination, self.record)
        self.assertEqual(snapshot(self.directory), before)

    def test_missing_parent_and_project_paths_reject_without_creation(self):
        project = self.directory / "synthetic-project"
        project.mkdir()
        alias = self.directory / "project-alias"
        self.symlink(alias, project)
        before = snapshot(self.directory)
        with mock.patch.object(sdl, "PROJECT_ROOT", project.resolve()), \
                mock.patch.object(sdl.subprocess, "run", side_effect=AssertionError("Git must not run")):
            with self.assertRaisesRegex(sdl.SdlError, "parent must already exist"):
                sdl.acquire_sdl2(self.directory / "missing-parent/SDL", self.record)
            for root in (project, alias):
                with self.subTest(root=root), self.assertRaisesRegex(sdl.SdlError, "outside the project"):
                    sdl.verify_sdl2(root, self.record)
                with self.assertRaisesRegex(sdl.SdlError, "outside the project"):
                    sdl.acquire_sdl2(root / "new-SDL", self.record)
        self.assertEqual(snapshot(self.directory), before)

    def test_failed_clone_retains_partial_destination(self):
        destination = self.directory / "failed clone"

        def fail_clone(command, **kwargs):
            self.assertTrue(destination.is_dir())
            self.assertIn("--no-recurse-submodules", command)
            self.assertIn("core.eol=lf", command)
            (destination / "partial-evidence").write_bytes(b"retained partial clone\n")
            raise subprocess.CalledProcessError(128, command)

        with mock.patch.object(sdl.subprocess, "run", side_effect=fail_clone) as run:
            with self.assertRaisesRegex(sdl.SdlError, "partial checkout is retained"):
                sdl.acquire_sdl2(destination, self.record)
        run.assert_called_once()
        self.assertEqual((destination / "partial-evidence").read_bytes(), b"retained partial clone\n")

    def test_destination_created_after_preflight_is_not_reused(self):
        destination = self.directory / "competing destination"

        def race_preflight(path):
            self.assertEqual(path, destination)
            destination.mkdir()
            (destination / "other-owner").write_bytes(b"preserve concurrent owner\n")
            return False

        with mock.patch.object(sdl.os.path, "lexists", side_effect=race_preflight), \
                mock.patch.object(sdl.subprocess, "run", side_effect=AssertionError("Git must not run")):
            with self.assertRaisesRegex(sdl.SdlError, "cannot create new SDL2 destination"):
                sdl.acquire_sdl2(destination, self.record)
        self.assertEqual((destination / "other-owner").read_bytes(), b"preserve concurrent owner\n")

    def test_local_clone_and_failed_post_clone_verification(self):
        # file:// uses only our synthetic local Git repository. It does not
        # establish an official download or exercise network acquisition.
        destination = self.directory / "acquired fixture"
        result = sdl.acquire_sdl2(destination, self.record)
        self.assertEqual(result["repository"], self.template.as_uri())
        self.assertTrue(result["network_used"])  # explicit acquisition code path
        self.assertEqual(git(destination, "rev-parse", "--is-shallow-repository"), "true")
        broken = copy.deepcopy(self.record)
        broken["license"]["sha256"] = "0" * 64
        failed = self.directory / "retained rejected fixture"
        with self.assertRaisesRegex(sdl.SdlError, "size/SHA-256 mismatch"):
            sdl.acquire_sdl2(failed, broken)
        self.assertEqual(git(failed, "rev-parse", "HEAD"), self.record["commit"])
        self.assertEqual((failed / "LICENSE.txt").read_bytes(), (self.template / "LICENSE.txt").read_bytes())

    def test_cmake_helper_uses_repository_verifier_and_rejects_unreviewed_sources(self):
        cmake = os.environ.get("HAMMOND_TEST_CMAKE") or shutil.which("cmake")
        self.assertIsNotNone(cmake, "CMake is required for the isolated helper test")
        project = self.directory / "enclosing project"
        (project / "tools").mkdir(parents=True)
        sentinel = self.directory / "wrong-verifier-executed"
        (project / "tools/acquire_sdl2.py").write_text(
            f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('wrong verifier')\n",
            encoding="utf-8")
        script = self.directory / "verify.cmake"
        for root, message in ((self.directory / "missing", "existing external"),
                              (self.checkout, "Pinned SDL2 verification failed")):
            script.write_text(
                f'set(PROJECT_SOURCE_DIR [==[{project.as_posix()}]==])\n'
                f'set(Python3_EXECUTABLE [==[{Path(sys.executable).as_posix()}]==])\n'
                f'include([==[{(ROOT / "cmake/VerifySdl2.cmake").as_posix()}]==])\n'
                f'hammond_verify_sdl2([==[{root.as_posix()}]==])\n', encoding="utf-8")
            result = subprocess.run([str(cmake), "-P", str(script)], capture_output=True,
                                    text=True, timeout=40, check=False)
            with self.subTest(root=root):
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, " ".join(result.stderr.split()))
                self.assertFalse(sentinel.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
