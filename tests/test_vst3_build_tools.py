#!/usr/bin/env python3
"""SDK-free tests of dependency admission and byte-exact profile embedding."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(os.environ.get("HAMMOND_SOURCE_DIR", Path(__file__).resolve().parents[1]))


def load_tool(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sdk = load_tool("acquire_vst3_sdk")
embed = load_tool("embed_profile")
compiler = load_tool("compile_profile")


def git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=SDK fixture",
         "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
         *arguments], capture_output=True, text=True, check=True,
        encoding="utf-8", errors="strict", timeout=20,
    )
    return completed.stdout.strip()


class SdkFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shared = tempfile.TemporaryDirectory(prefix="hammond-sdk-fixture-")
        cls.template = Path(cls.shared.name) / "SDK template"
        cls.template.mkdir()
        cls.lock = sdk.load_lock(ROOT / "data/dependencies/vst3-sdk-lock.json")
        license_bytes = b"MIT License\nSynthetic local fixture, not SDK code.\n"
        license_info = {"spdx": "MIT", "path": "LICENSE.txt", "bytes": len(license_bytes),
                        "sha256": hashlib.sha256(license_bytes).hexdigest()}
        git(cls.template, "init", "--quiet")
        git(cls.template, "config", "core.autocrlf", "false")
        (cls.template / "LICENSE.txt").write_bytes(license_bytes)
        (cls.template / "README.md").write_bytes(b"root fixture\n")
        embedded = b"/* Synthetic Unlicense fixture */\n"
        for module in cls.lock["required_submodules"]:
            target = cls.template / module["path"]
            target.mkdir()
            git(target, "init", "--quiet")
            git(target, "config", "core.autocrlf", "false")
            (target / "LICENSE.txt").write_bytes(license_bytes)
            (target / "README.md").write_bytes(b"module fixture\n")
            if module["path"] == "public.sdk":
                leaf = target / "source/vst/moduleinfo/json.h"
                leaf.parent.mkdir(parents=True)
                leaf.write_bytes(embedded)
            git(target, "add", ".")
            git(target, "commit", "--quiet", "-m", "Synthetic SDK fixture")
            module["commit"] = git(target, "rev-parse", "HEAD")
            module["license"] = copy.deepcopy(license_info)
            git(cls.template, "update-index", "--add", "--cacheinfo",
                f"160000,{module['commit']},{module['path']}")
        git(cls.template, "add", "LICENSE.txt", "README.md")
        git(cls.template, "commit", "--quiet", "-m", "Synthetic parent gitlinks")
        cls.lock["commit"] = git(cls.template, "rev-parse", "HEAD")
        cls.lock["license"] = license_info
        cls.lock["embedded_third_party"][0]["bytes"] = len(embedded)
        cls.lock["embedded_third_party"][0]["sha256"] = hashlib.sha256(embedded).hexdigest()

    @classmethod
    def tearDownClass(cls):
        cls.shared.cleanup()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hammond-sdk-test-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.checkout = self.directory / "SDK checkout"
        shutil.copytree(self.template, self.checkout)
        self.record = copy.deepcopy(self.lock)

    def test_local_verification_has_no_network_command(self):
        with mock.patch.object(sdk.subprocess, "run", wraps=subprocess.run) as run:
            result = sdk.verify_sdk(self.checkout, self.record)
        self.assertFalse(result["network_used"])
        self.assertEqual(result["primary_licenses_verified"], 5)
        self.assertTrue(result["embedded_json_verified"])
        self.assertEqual(len(result["verified_checkouts"]), 5)
        for call in run.call_args_list:
            command = call.args[0]
            self.assertNotIn("clone", command)
            self.assertNotIn("fetch", command)
            self.assertNotIn("pull", command)
            self.assertNotIn("reset", command)
            self.assertNotIn("checkout", command)

    def test_root_and_required_commit_mismatches_fail(self):
        for index in (None, 0, 1, 2, 3):
            with self.subTest(index=index):
                record = copy.deepcopy(self.record)
                item = record if index is None else record["required_submodules"][index]
                item["commit"] = "0" * 40
                with self.assertRaisesRegex(sdk.SdkError, "commit mismatch"):
                    sdk.verify_sdk(self.checkout, record)

    def test_same_head_tracked_tampering_rejects_staged_and_unstaged(self):
        for relative in (".", "base", "cmake", "pluginterfaces", "public.sdk"):
            root = self.checkout / relative
            original = (root / "README.md").read_bytes()
            head = git(root, "rev-parse", "HEAD")
            (root / "README.md").write_bytes(original + b"changed input\n")
            with self.assertRaisesRegex(sdk.SdkError, "tracked files are modified"):
                sdk.verify_sdk(self.checkout, self.record)
            git(root, "add", "README.md")
            self.assertEqual(git(root, "rev-parse", "HEAD"), head)
            with self.assertRaisesRegex(sdk.SdkError, "tracked files are modified"):
                sdk.verify_sdk(self.checkout, self.record)
            (root / "README.md").write_bytes(original)
            git(root, "add", "README.md")
        self.assertFalse(sdk.verify_sdk(self.checkout, self.record)["network_used"])

    def test_missing_module_cannot_inherit_parent_checkout(self):
        shutil.rmtree(self.checkout / "base" / ".git")
        with self.assertRaisesRegex(sdk.SdkError, "not its own checkout"):
            sdk.verify_sdk(self.checkout, self.record)

    def test_parent_gitlink_is_checked_separately(self):
        root = self.checkout / "base"
        (root / "README.md").write_bytes(b"new committed fixture\n")
        git(root, "add", "README.md")
        git(root, "commit", "--quiet", "-m", "Another fixture commit")
        self.record["required_submodules"][0]["commit"] = git(root, "rev-parse", "HEAD")
        with self.assertRaisesRegex(sdk.SdkError, "parent gitlink mismatch"):
            sdk.verify_sdk(self.checkout, self.record)

    def test_primary_and_embedded_raw_hashes_are_checked(self):
        for index in (None, 0, 1, 2, 3, "json"):
            with self.subTest(index=index):
                record = copy.deepcopy(self.record)
                if index == "json":
                    item = record["embedded_third_party"][0]
                elif index is None:
                    item = record["license"]
                else:
                    item = record["required_submodules"][index]["license"]
                item["sha256"] = "0" * 64
                with self.assertRaisesRegex(sdk.SdkError, "size/SHA-256 mismatch"):
                    sdk.verify_sdk(self.checkout, record)

    def test_existing_acquisition_destination_is_untouched(self):
        before = (self.checkout / "README.md").read_bytes()
        with mock.patch.object(sdk.subprocess, "run", side_effect=AssertionError("Git must not run")):
            with self.assertRaisesRegex(sdk.SdkError, "already exists"):
                sdk.acquire_sdk(self.checkout, self.record)
            with self.assertRaisesRegex(sdk.SdkError, "outside the project"):
                sdk.acquire_sdk(ROOT / "this-sdk-must-never-be-created", self.record)
        self.assertEqual((self.checkout / "README.md").read_bytes(), before)
        self.assertFalse((ROOT / "this-sdk-must-never-be-created").exists())

    def test_untracked_and_ignored_cmake_inputs_reject_even_at_same_head(self):
        root = self.checkout / "public.sdk"
        original_head = git(root, "rev-parse", "HEAD")
        leaf = root / "samples/vst-utilities/new/CMakeLists.txt"
        leaf.parent.mkdir(parents=True)
        leaf.write_bytes(b'message(FATAL_ERROR "Unreviewed discovered target")\n')
        with self.assertRaisesRegex(sdk.SdkError, "untracked or ignored files"):
            sdk.verify_sdk(self.checkout, self.record)
        # Exclude is local Git metadata, so HEAD and tracked status stay clean.
        (root / ".git/info/exclude").write_text("samples/vst-utilities/new/\n", encoding="utf-8")
        self.assertEqual(git(root, "status", "--porcelain=v1"), "")
        self.assertEqual(git(root, "rev-parse", "HEAD"), original_head)
        with self.assertRaisesRegex(sdk.SdkError, "untracked or ignored files"):
            sdk.verify_sdk(self.checkout, self.record)
        leaf.unlink()
        (self.directory / "out-of-tree-build.log").write_bytes(b"safe external output\n")
        self.assertFalse(sdk.verify_sdk(self.checkout, self.record)["network_used"])

    def test_cmake_boundary_rejects_missing_and_modified_checkout(self):
        cmake = os.environ.get("HAMMOND_TEST_CMAKE") or shutil.which("cmake")
        self.assertIsNotNone(cmake, "CMake is required for the build-boundary test")
        project = self.directory / "Fixture project"
        (project / "tools").mkdir(parents=True)
        (project / "data/dependencies").mkdir(parents=True)
        shutil.copyfile(ROOT / "tools/acquire_vst3_sdk.py", project / "tools/acquire_vst3_sdk.py")
        (project / "data/dependencies/vst3-sdk-lock.json").write_text(json.dumps(self.record), encoding="utf-8")
        script = self.directory / "verify.cmake"

        def invoke(checkout: Path):
            script.write_text(
                f'set(PROJECT_SOURCE_DIR [==[{project.as_posix()}]==])\n'
                f'set(Python3_EXECUTABLE [==[{Path(sys.executable).as_posix()}]==])\n'
                f'include([==[{(ROOT / "cmake/VerifyVst3Sdk.cmake").as_posix()}]==])\n'
                f'hammond_verify_vst3_sdk([==[{checkout.as_posix()}]==])\n', encoding="utf-8")
            return subprocess.run([str(cmake), "-P", str(script)], capture_output=True,
                                  text=True, timeout=40, check=False)

        valid = invoke(self.checkout)
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
        missing = invoke(self.directory / "missing")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("existing external", missing.stderr)
        (self.checkout / "base" / "README.md").write_bytes(b"invalid tracked input\n")
        changed = invoke(self.checkout)
        self.assertNotEqual(changed.returncode, 0)
        self.assertIn("tracked files are modified", " ".join(changed.stderr.split()))


class LockAndEmbeddingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hammond-native-tools-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def test_default_configure_never_executes_an_unverified_sdk(self):
        cmake = os.environ.get("HAMMOND_TEST_CMAKE") or shutil.which("cmake")
        self.assertIsNotNone(cmake, "CMake is required for the build-boundary test")
        fake = self.directory / "unverified sdk"
        fake.mkdir()
        sentinel = self.directory / "sdk-was-executed"
        (fake / "CMakeLists.txt").write_text(
            f'file(WRITE [==[{sentinel.as_posix()}]==] "unexpected SDK execution")\n'
            'message(FATAL_ERROR "Unverified SDK must not be executed")\n', encoding="utf-8")
        for enabled in ("OFF", "ON"):
            completed = subprocess.run(
                [str(cmake), "-S", str(ROOT), "-B", str(self.directory / f"build-{enabled}"),
                 "-DCMAKE_BUILD_TYPE=Release", "-DBUILD_TESTING=OFF",
                 f"-DHAMMOND_BUILD_VST3={enabled}", f"-DHAMMOND_VST3_SDK_ROOT={fake}"],
                capture_output=True, text=True, timeout=60, check=False)
            if enabled == "OFF":
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            else:
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("Pinned VST3 SDK verification failed", completed.stderr)
            self.assertFalse(sentinel.exists())

    def test_reviewed_lock_and_malformed_fields(self):
        original = sdk.load_lock(ROOT / "data/dependencies/vst3-sdk-lock.json")
        self.assertEqual(original["commit"], "3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96")
        bad = []
        for key, value in (("schema_version", True), ("commit", "abc"),
                           ("repository", "file:///unreviewed"), ("tag", "--upload-pack=bad")):
            variant = copy.deepcopy(original)
            variant[key] = value
            bad.append(json.dumps(variant).encode())
        variant = copy.deepcopy(original)
        variant["required_submodules"][0]["path"] = "../outside"
        bad.append(json.dumps(variant).encode())
        variant = copy.deepcopy(original)
        variant["required_submodules"][1] = variant["required_submodules"][0]
        bad.append(json.dumps(variant).encode())
        bad += [b'{"schema_version":1,"schema_version":1}', b" " * (sdk.MAX_LOCK_BYTES + 1),
                b"\xff", b'{"value":NaN}', b"[" * 2000 + b"]" * 2000]
        path = self.directory / "bad-lock.json"
        for payload in bad:
            with self.subTest(payload=payload[:70]):
                path.write_bytes(payload)
                with self.assertRaises(sdk.SdkError):
                    sdk.load_lock(path)

    def test_actual_compiled_profile_roundtrips_exact_bytes(self):
        profile = compiler.load_profile(ROOT / "data/profiles/nominal-unmeasured-v1.json")
        raw = compiler.compile_profile(profile).encode("utf-8")
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f")
        header = embed.make_header(raw).decode("ascii")
        array = header.split("kEmbeddedProfileBytes[] = {", 1)[1].split("};", 1)[0]
        recovered = bytes(int(pair, 16) for pair in re.findall(r"0x([0-9a-f]{2})", array))
        self.assertEqual(recovered, raw)
        self.assertIn("kEmbeddedProfileText", header)
        self.assertIn(hashlib.sha256(raw).hexdigest(), header)

    def test_invalid_embedding_preserves_destination_and_rejects_alias(self):
        source = self.directory / "profile.b3p"
        output = self.directory / "EmbeddedProfile.h"
        output.write_bytes(b"preserve sentinel\n")
        for raw in (b"", b"B3PROFILE 2\nend\n", b"B3PROFILE 1\n\x00end\n",
                    b"B3PROFILE 1\r\nend\r\n", b"B3PROFILE 1\n\xffend\n",
                    b"B3PROFILE 1\n" + b" " * embed.MAX_PROFILE_BYTES + b"end\n"):
            with self.subTest(raw=raw[:30]):
                source.write_bytes(raw)
                with self.assertRaises(embed.EmbeddingError):
                    embed.embed_profile(source, output)
                self.assertEqual(output.read_bytes(), b"preserve sentinel\n")
        source.write_bytes(b"B3PROFILE 1\nend\n")
        with self.assertRaisesRegex(embed.EmbeddingError, "different files"):
            embed.embed_profile(source, source)
        self.assertEqual(source.read_bytes(), b"B3PROFILE 1\nend\n")

    def test_generated_header_is_deterministic_and_unchanged_output_is_not_rewritten(self):
        source = self.directory / "profile.b3p"
        output = self.directory / "generated" / "EmbeddedProfile.h"
        source.write_bytes(b"B3PROFILE 1\nend\n")
        first = embed.embed_profile(source, output)
        original = output.read_bytes()
        os.utime(output, ns=(1234567890000000000, 1234567890000000000))
        before = output.stat().st_mtime_ns
        second = embed.embed_profile(source, output)
        self.assertEqual(first, second)
        self.assertEqual(output.read_bytes(), original)
        self.assertEqual(output.stat().st_mtime_ns, before)
        self.assertEqual(list(output.parent.glob(".embedded-profile-*")), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
