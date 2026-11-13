#!/usr/bin/env python3
"""Real OfflineTools install/relocation smoke; uses only the standard library.

Build hammond_render first, then run ctest -R '^python_test_install$'. CTest
supplies the exact CMake, build, configuration, executable and profile paths,
including multi-configuration generators. Missing inputs are errors, not skips.
"""

import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import unittest
import wave


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_NAMES = {
    "catalog-v1.json",
    "a4-fundamental-v1.events",
    "two-manual-changes-v1.events",
    "low-fold-coherent-v1.events",
    "held-bank-cancel-v1.events",
    "high-fold-coherent-v1.events",
}


def required_path(variable, *, directory=False):
    value = os.environ.get(variable)
    path = Path(value) if value else None
    if path is None or not (path.is_dir() if directory else path.is_file()):
        raise RuntimeError(
            f"Missing install-test input {variable}={value!r}. Build the "
            "hammond_render target (including nominal.b3p) for the selected "
            "configuration, then run this test through CTest."
        )
    return path.resolve()


def relative_install_dir(variable):
    value = os.environ.get(variable)
    path = Path(value) if value else None
    if path is None or path.is_absolute() or ".." in path.parts:
        raise RuntimeError(f"{variable} must name a relative install directory")
    return path


class OfflineInstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cmake = required_path("HAMMOND_TEST_CMAKE")
        cls.build = required_path("HAMMOND_TEST_BUILD_DIR", directory=True)
        cls.renderer = required_path("HAMMOND_RENDER_EXECUTABLE")
        cls.profile = required_path("HAMMOND_TEST_PROFILE")
        cls.bindir = relative_install_dir("HAMMOND_INSTALL_BINDIR")
        cls.datadir = relative_install_dir("HAMMOND_INSTALL_DATADIR") / "hammond-b3-organ"
        cls.configuration = os.environ.get("HAMMOND_TEST_CONFIG", "")
        if not (cls.build / "cmake_install.cmake").is_file():
            raise RuntimeError(f"Missing CMake install script in {cls.build}; configure again")

    def invoke(self, command, cwd, environment):
        return subprocess.run(
            list(map(str, command)), cwd=cwd, env=environment, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=60, check=False,
        )

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def read_pcm(self, path, fixture):
        with wave.open(str(path), "rb") as reader:
            self.assertEqual(reader.getparams()[:4],
                             (2, 2, fixture["sample_rate"], fixture["frames"]))
            self.assertEqual(reader.getcomptype(), "NONE")
            pcm = reader.readframes(fixture["frames"] + 1)
        self.assertEqual(len(pcm), fixture["frames"] * 4)
        samples = struct.unpack(f"<{fixture['frames'] * 2}h", pcm)
        self.assertEqual(samples[::2], samples[1::2], "Dry stereo channels differ")
        return pcm

    def test_install_move_and_render(self):
        with tempfile.TemporaryDirectory(prefix="hammond install smoke ") as temporary:
            work = Path(temporary)
            prefix = work / "original prefix with spaces"
            relocated = work / "relocated prefix with spaces"
            unrelated = work / "unrelated working directory"
            unrelated.mkdir()
            environment = dict(os.environ)
            # Prevent a caller's staging root from redirecting this local install.
            environment.pop("DESTDIR", None)
            install = [self.cmake, "--install", self.build, "--component", "OfflineTools",
                       "--prefix", prefix]
            if self.configuration:
                install.extend(("--config", self.configuration))
            self.assert_success(self.invoke(install, unrelated, environment))
            expected = {self.bindir / self.renderer.name, self.datadir / "nominal.b3p"}
            expected.update(self.datadir / "fixtures" / name for name in FIXTURE_NAMES)
            actual = {path.relative_to(prefix) for path in prefix.rglob("*") if path.is_file()}
            self.assertEqual(actual, expected, "OfflineTools installed an unexpected file set")
            self.assertFalse(any(path.is_symlink() for path in prefix.rglob("*")))
            prefix.rename(relocated)
            self.assertFalse(prefix.exists(), "Original install prefix must be absent")
            installed_renderer = relocated / self.bindir / self.renderer.name
            installed_profile = relocated / self.datadir / "nominal.b3p"
            installed_fixtures = relocated / self.datadir / "fixtures"
            profile_bytes = self.profile.read_bytes()
            self.assertEqual(installed_profile.read_bytes(), profile_bytes)
            for name in FIXTURE_NAMES:
                self.assertEqual((installed_fixtures / name).read_bytes(),
                                 (ROOT / "examples" / "fixtures" / name).read_bytes(), name)
            catalog = json.loads((installed_fixtures / "catalog-v1.json").read_text(encoding="utf-8"))
            self.assertEqual(hashlib.sha256(profile_bytes).hexdigest(),
                             catalog["profile"]["compiled_sha256"])
            fixture = next(item for item in catalog["fixtures"]
                           if item["id"] == "a4-fundamental-v1")
            self.assertLessEqual(fixture["frames"], 96000, "Keep the install smoke bounded")
            score_name = fixture["events"]["path"]
            self.assertEqual(score_name, "a4-fundamental-v1.events")
            common = ["--sample-rate", fixture["sample_rate"], "--frames", fixture["frames"],
                      "--block-size", fixture["block_size"], "--seed", fixture["seed"],
                      "--drawbars", fixture["registration"], "--fail-on-clip"]
            # Installed execution receives no test/build/source path variables.
            render_environment = {key: value for key, value in environment.items()
                                  if not key.startswith("HAMMOND_")}

            def render(executable, profile, score, name):
                output = unrelated / name
                command = [executable, "--profile", profile, "--events", score,
                           "--output", output, *common]
                return self.invoke(command, unrelated, render_environment), output

            reference_result, reference_wav = render(
                self.renderer, self.profile, ROOT / "examples" / "fixtures" / score_name,
                "build reference.wav")
            installed_result, installed_wav = render(
                installed_renderer, installed_profile, installed_fixtures / score_name,
                "relocated render.wav")
            self.assert_success(reference_result)
            self.assert_success(installed_result)
            self.assertEqual(installed_result.stderr, "")
            report = json.loads(installed_result.stdout)
            self.assertEqual(report, json.loads(reference_result.stdout))
            self.assertEqual(report["profile_id"], catalog["profile"]["id"])
            self.assertEqual(report["authoring_sha256"], catalog["profile"]["authoring_sha256"])
            self.assertEqual(report["status"], "ok")
            self.assertEqual(report["evidence_status"], "unmeasured")
            self.assertEqual(report["clipped_frames"], 0)
            reference_pcm = self.read_pcm(reference_wav, fixture)
            self.assertTrue(any(reference_pcm), "The fixture must contain audible PCM")
            self.assertEqual(self.read_pcm(installed_wav, fixture), reference_pcm)
            self.assertEqual(installed_wav.read_bytes(), reference_wav.read_bytes())

            # Prove that the installed file supplies both identity and signal data.
            # This temporary synthetic probe is restored, never installed as a fixture.
            probe = profile_bytes.decode("ascii")
            probe, digest_count = re.subn(r"(?m)^authoring_sha256 [0-9a-f]{64}$",
                                         "authoring_sha256 " + "0" * 64, probe)
            probe, gain_count = re.subn(r"(?m)^output_gain [^\r\n]+$", "output_gain 0", probe)
            self.assertEqual((digest_count, gain_count), (1, 1))
            try:
                installed_profile.write_bytes(probe.encode("ascii"))
                probe_result, probe_wav = render(
                    installed_renderer, installed_profile, installed_fixtures / score_name,
                    "explicit installed profile probe.wav")
                self.assert_success(probe_result)
                probe_report = json.loads(probe_result.stdout)
                self.assertEqual(probe_report["authoring_sha256"], "0" * 64)
                self.assertEqual(probe_report["peak"], 0)
                self.assertFalse(any(self.read_pcm(probe_wav, fixture)))
                installed_profile.unlink()
                missing_result, missing_wav = render(
                    installed_renderer, installed_profile, installed_fixtures / score_name,
                    "must not exist.wav")
                self.assertEqual(missing_result.returncode, 1, missing_result.stderr)
                self.assertIn("Profile", missing_result.stderr)
                self.assertFalse(missing_wav.exists(), "Missing installed profile used a fallback")
            finally:
                installed_profile.write_bytes(profile_bytes)


if __name__ == "__main__":
    unittest.main()
