#!/usr/bin/env python3
"""Real OfflineTools install/relocation smoke; uses only the standard library.

Build all five offline executables first, then run ctest -R '^python_test_install$'. CTest
supplies the exact CMake, build, configuration, executable and profile paths,
including multi-configuration generators. Missing inputs are errors, not skips.
"""

import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import wave
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_PARAMETER_IDS = (set(range(4096, 4105)) | set(range(4112, 4121)) |
                            set(range(4128, 4137)) | set(range(4144, 4153)) |
                            {8192, 8208, 8209, 12288, 12289, 12290, 12291, 16384, 16385})
HISTORICAL_PARAMETER_HASH = "13ba488bec90154c960c3fd700dc4a774aff5664caf5d68472821493f22d1cad"
FIXTURE_NAMES = {
    "catalog-v1.json",
    "a4-fundamental-v1.events",
    "two-manual-changes-v1.events",
    "low-fold-coherent-v1.events",
    "held-bank-cancel-v1.events",
    "high-fold-coherent-v1.events",
}
CONSOLE_FIXTURE_NAMES = {
    "console-catalog-v1.json",
    "console-travel-v1.events",
    "console-percussion-legato-v1.events",
    "console-routing-mask-v1.events",
}
PEDAL_FIXTURE_NAMES = {
    "pedal-catalog-v1.json",
    "pedal-mixtures-v1.events",
    "pedal-shared-source-v1.events",
    "pedal-held-routing-v1.events",
    "pedal-phrase-v1.events",
}


def required_path(variable, *, directory=False):
    value = os.environ.get(variable)
    path = Path(value) if value else None
    if path is None or not (path.is_dir() if directory else path.is_file()):
        raise RuntimeError(
            f"Missing install-test input {variable}={value!r}. Build the "
            "hammond_render, hammond_model_info, hammond_parameter_info, "
            "hammond_console_trace and hammond_pedal_trace targets (including nominal.b3p) for the selected "
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
        cls.model_info = required_path("HAMMOND_MODEL_INFO_EXECUTABLE")
        cls.parameter_info = required_path("HAMMOND_PARAMETER_INFO_EXECUTABLE")
        cls.console_trace = required_path("HAMMOND_CONSOLE_TRACE_EXECUTABLE")
        cls.pedal_trace = required_path("HAMMOND_PEDAL_TRACE_EXECUTABLE")
        cls.plotter = ROOT / "tools" / "plot_console_trace.py"
        cls.pedal_plotter = ROOT / "tools" / "plot_pedal_trace.py"
        for plotter in (cls.plotter, cls.pedal_plotter):
            if not plotter.is_file():
                raise RuntimeError(f"Missing standalone plot script: {plotter}")
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
            environment.pop("CMAKE_INSTALL_MODE", None)
            install = [self.cmake, "--install", self.build, "--component", "OfflineTools",
                       "--prefix", prefix]
            if self.configuration:
                install.extend(("--config", self.configuration))
            self.assert_success(self.invoke(install, unrelated, environment))
            executables = (self.renderer, self.model_info, self.parameter_info,
                           self.console_trace, self.pedal_trace)
            expected = {self.bindir / path.name for path in executables}
            expected.update((self.bindir / self.plotter.name, self.bindir / self.pedal_plotter.name,
                             self.datadir / "nominal.b3p"))
            expected.update(self.datadir / "fixtures" / name for name in FIXTURE_NAMES)
            expected.update(self.datadir / "fixtures" / "console" / name
                            for name in CONSOLE_FIXTURE_NAMES)
            expected.update(self.datadir / "fixtures" / "pedals" / name
                            for name in PEDAL_FIXTURE_NAMES)
            self.assertEqual(len(expected), 23)
            actual = {path.relative_to(prefix) for path in prefix.rglob("*") if path.is_file()}
            self.assertEqual(actual, expected, "OfflineTools installed an unexpected file set")
            self.assertFalse(any(path.is_symlink() for path in prefix.rglob("*")))
            prefix.rename(relocated)
            self.assertFalse(prefix.exists(), "Original install prefix must be absent")
            installed_renderer = relocated / self.bindir / self.renderer.name
            installed_profile = relocated / self.datadir / "nominal.b3p"
            installed_fixtures = relocated / self.datadir / "fixtures"
            installed_plotter = relocated / self.bindir / self.plotter.name
            installed_pedal_plotter = relocated / self.bindir / self.pedal_plotter.name
            profile_bytes = self.profile.read_bytes()
            self.assertEqual(installed_profile.read_bytes(), profile_bytes)
            for name in FIXTURE_NAMES:
                self.assertEqual((installed_fixtures / name).read_bytes(),
                                 (ROOT / "examples" / "fixtures" / name).read_bytes(), name)
            for name in CONSOLE_FIXTURE_NAMES:
                self.assertEqual((installed_fixtures / "console" / name).read_bytes(),
                                 (ROOT / "examples" / "fixtures" / "console" / name).read_bytes(), name)
            for name in PEDAL_FIXTURE_NAMES:
                self.assertEqual((installed_fixtures / "pedals" / name).read_bytes(),
                                 (ROOT / "examples" / "fixtures" / "pedals" / name).read_bytes(), name)
            self.assertEqual(installed_plotter.read_bytes(), self.plotter.read_bytes())
            self.assertEqual(installed_pedal_plotter.read_bytes(), self.pedal_plotter.read_bytes())
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
                                  if not key.upper().startswith("HAMMOND_")}

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

            # Compile-time metadata must remain available after moving the prefix;
            # neither metadata executable reads the profile or a source JSON file.
            for executable, arguments in (
                    (self.model_info, []),
                    (self.parameter_info, ["--normalized", "0.49999999999999994"])):
                reference = self.invoke([executable, *arguments], unrelated, render_environment)
                installed = self.invoke([relocated / self.bindir / executable.name, *arguments],
                                        unrelated, render_environment)
                self.assert_success(reference)
                self.assert_success(installed)
                self.assertEqual(installed.stderr, "")
                self.assertEqual(installed.stdout, reference.stdout)
                metadata = json.loads(installed.stdout)
                if executable == self.model_info:
                    self.assertEqual(metadata["schema_version"], 2)
                    self.assertEqual(len(metadata["console_models"]), 2)
                    compiled_models = metadata
                else:
                    self.assertEqual(metadata["schema_version"], 2)
                    self.assertEqual(metadata["verification_scope"], "sdk-free-core-parameter-mapping")
                    self.assertIs(metadata["host_exports_verified"], False)
                    self.assertIs(metadata["native_host_curves_verified"], False)
                    self.assertNotIn("native_host_curves_implemented", metadata)
                    self.assertEqual(len(metadata["parameters"]), 47)
                    self.assertEqual(metadata["registry_schema_version"], 4)
                    self.assertEqual(metadata["model"], "exclusive-fixed-percussion-pedal-console-v4")
                    self.assertEqual(metadata["normalized"], 0.49999999999999994)
                    compiled_parameters = metadata

            console_catalog = json.loads((installed_fixtures / "console" /
                                          "console-catalog-v1.json").read_text(encoding="utf-8"))
            self.assertEqual(console_catalog["profile"]["compiled_sha256"],
                             hashlib.sha256(profile_bytes).hexdigest())
            console = next(item for item in console_catalog["fixtures"]
                           if item["id"] == "console-percussion-legato-v1")
            self.assertLessEqual(console["frames"], 42000)
            console_options = ["--sample-rate", console["sample_rate"], "--frames", console["frames"],
                               "--block-size", console["block_size"], "--seed", console["seed"],
                               "--drawbars", console["registration"], "--fail-on-clip"]
            for name in ("contacts", "percussion", "percussion_volume", "percussion_decay"):
                console_options.extend(("--" + name.replace("_", "-"), console["controls"][name]))
            console_outputs = []
            console_reports = []
            for executable, profile, fixtures, name in (
                    (self.renderer, self.profile, ROOT / "examples" / "fixtures" / "console",
                     "build console.wav"),
                    (installed_renderer, installed_profile, installed_fixtures / "console",
                     "relocated console.wav")):
                score = fixtures / console["events"]["path"]
                self.assertEqual(hashlib.sha256(score.read_bytes()).hexdigest(),
                                 console["events"]["sha256"])
                output = unrelated / name
                result = self.invoke([executable, "--profile", profile, "--events", score,
                                      "--output", output, *console_options], unrelated, render_environment)
                self.assert_success(result)
                self.assertEqual(result.stderr, "")
                console_outputs.append(output)
                console_reports.append(json.loads(result.stdout))
            self.assertEqual(console_reports[0], console_reports[1])
            self.assertEqual(console_reports[1]["contact_model"], "nominal-linear-travel-v1")
            self.assertEqual(console_reports[1]["percussion_model"], "shared-readiness-v1")
            self.assertEqual(console_reports[1]["clipped_frames"], 0)
            console_pcm = self.read_pcm(console_outputs[0], console)
            self.assertTrue(any(console_pcm), "The installed console fixture must produce audio")
            self.assertEqual(self.read_pcm(console_outputs[1], console), console_pcm)
            self.assertEqual(console_outputs[0].read_bytes(), console_outputs[1].read_bytes())

            # Couple the installed catalog/profile/compiled identities before
            # exercising a new pedal score and all three retained trace scenarios.
            pedal_catalog = json.loads((installed_fixtures / "pedals" /
                                        "pedal-catalog-v1.json").read_text(encoding="utf-8"))
            self.assertEqual(pedal_catalog["profile"]["compiled_sha256"],
                             hashlib.sha256(profile_bytes).hexdigest())
            model = compiled_models["pedal_model"]
            for field in ("map_id", "map_raw_sha256", "map_canonical_sha256"):
                self.assertEqual(model["routing"][field], pedal_catalog["routing"][field])
            self.assertEqual(model["routing"]["model_id"], pedal_catalog["models"]["pedal_routing"])
            self.assertEqual(model["voice"]["model_id"], pedal_catalog["models"]["pedal_voice"])
            self.assertEqual(model["voice"]["gain_law_id"], pedal_catalog["models"]["pedal_gain"])
            self.assert_historical_parameter_compatibility(compiled_parameters, pedal_catalog)
            pedal_ids = [{"id": item["id"], "path": item["path"]}
                         for item in compiled_parameters["parameters"]
                         if item["path"].startswith("pedal.")]
            self.assertEqual(pedal_ids, pedal_catalog["control_model"]["pedal_parameters"])
            for item in pedal_catalog["fixtures"]:
                score = installed_fixtures / "pedals" / item["events"]["path"]
                self.assertEqual(hashlib.sha256(score.read_bytes()).hexdigest(), item["events"]["sha256"])
            pedal = next(item for item in pedal_catalog["fixtures"] if item["id"] == "pedal-mixtures-v1")
            self.assertLessEqual(pedal["frames"], 48000)
            pedal_options = ["--sample-rate", pedal["sample_rate"], "--frames", pedal["frames"],
                             "--block-size", pedal["block_size"], "--seed", pedal["seed"],
                             "--drawbars", pedal["registration"],
                             "--pedal-drawbars", pedal["pedal_registration"], "--fail-on-clip"]
            for name, value in pedal["controls"].items():
                pedal_options.extend(("--" + name.replace("_", "-"), value))
            pedal_outputs, pedal_reports = [], []
            for executable, profile, fixtures, name in (
                    (self.renderer, self.profile, ROOT / "examples" / "fixtures" / "pedals",
                     "build pedal.wav"),
                    (installed_renderer, installed_profile, installed_fixtures / "pedals",
                     "relocated pedal.wav")):
                output = unrelated / name
                result = self.invoke([executable, "--profile", profile, "--events",
                                      fixtures / pedal["events"]["path"], "--output", output,
                                      *pedal_options], unrelated, render_environment)
                self.assert_success(result)
                self.assertEqual(result.stderr, "")
                pedal_outputs.append(output)
                pedal_reports.append(json.loads(result.stdout))
            self.assertEqual(pedal_reports[0], pedal_reports[1])
            self.assert_pedal_identity(pedal_reports[1], pedal_catalog)
            self.assertEqual(pedal_reports[1]["clipped_frames"], 0)
            self.assertLessEqual(pedal_reports[1]["peak"], pedal["expectations"]["float_peak_max"])
            pedal_pcm = self.read_pcm(pedal_outputs[0], pedal)
            self.assertTrue(any(pedal_pcm), "Installed pedal fixture must produce audio")
            self.assertEqual(self.read_pcm(pedal_outputs[1], pedal), pedal_pcm)
            self.assertEqual(pedal_outputs[0].read_bytes(), pedal_outputs[1].read_bytes())
            for start, end in pedal["expectations"]["silence_spans"]:
                self.assertFalse(any(pedal_pcm[start * 4:end * 4]))

            for scenario in ("unmute", "overlap", "routing"):
                with self.subTest(pedal_trace=scenario):
                    traces = []
                    for executable, profile, kind in (
                            (self.pedal_trace, self.profile, "build"),
                            (relocated / self.bindir / self.pedal_trace.name, installed_profile, "relocated")):
                        output = unrelated / f"{kind} pedal {scenario}.csv"
                        result = self.invoke([executable, "--profile", profile, "--scenario", scenario,
                                              "--sample-rate", 48000, "--seed", 2705,
                                              "--output", output], unrelated, render_environment)
                        self.assert_success(result)
                        self.assertEqual((result.stdout, result.stderr), ("", ""))
                        self.assertLessEqual(output.stat().st_size, 8 * 1024 * 1024)
                        traces.append(output.read_bytes())
                    self.assertEqual(*traces)
                    lines = traces[1].decode("ascii").splitlines()
                    identity = dict(line[2:].split("=", 1) for line in lines if line.startswith("# "))
                    self.assert_pedal_identity(identity, pedal_catalog)
                    self.assertEqual(identity["scenario"], scenario)
                    self.assertEqual(identity["evidence_scope"], "synthetic_engineering")
                    rows = list(csv.DictReader(io.StringIO("\n".join(
                        line for line in lines if not line.startswith("#")))))
                    self.assertEqual(len(rows), 5760)
                    self.assertEqual([int(row["frame"]) for row in rows], list(range(5760)))
                    self.assertTrue(any(float(row["pedal_output"]) != 0 for row in rows))
                    # Existing outputs must survive even after successful relocation.
                    repeated = self.invoke([relocated / self.bindir / self.pedal_trace.name,
                                            "--profile", installed_profile, "--scenario", scenario,
                                            "--sample-rate", 48000, "--seed", 2705,
                                            "--output", output], unrelated, render_environment)
                    self.assertNotEqual(repeated.returncode, 0)
                    self.assertEqual(output.read_bytes(), traces[1])
                    retained_trace = output
                    trace_digest = hashlib.sha256(traces[1]).hexdigest().encode("ascii")
                    plots = []
                    for script, kind in ((self.pedal_plotter, "source"),
                                         (installed_pedal_plotter, "relocated")):
                        plotted = unrelated / f"{kind} pedal {scenario}.svg"
                        result = self.invoke([sys.executable, script, "--input", retained_trace,
                                              "--output", plotted], unrelated, render_environment)
                        self.assert_success(result)
                        svg = plotted.read_bytes()
                        self.assertLessEqual(len(svg), 1024 * 1024)
                        self.assertEqual(ET.fromstring(svg).tag, "{http://www.w3.org/2000/svg}svg")
                        self.assertIn(trace_digest, svg)
                        plots.append(svg)
                    self.assertEqual(*plots)
                    repeated_plot = self.invoke(
                        [sys.executable, installed_pedal_plotter, "--input", retained_trace,
                         "--output", plotted], unrelated, render_environment)
                    self.assertNotEqual(repeated_plot.returncode, 0)
                    self.assertEqual(plotted.read_bytes(), plots[1])

            trace_options = ["--scenario", "partial", "--sample-rate", 48000, "--seed", 2644]
            trace_outputs = []
            for executable, profile, name in (
                    (self.console_trace, self.profile, "build trace.csv"),
                    (relocated / self.bindir / self.console_trace.name, installed_profile,
                     "relocated trace.csv")):
                output = unrelated / name
                result = self.invoke([executable, "--profile", profile, *trace_options,
                                      "--output", output], unrelated, render_environment)
                self.assert_success(result)
                self.assertEqual((result.stdout, result.stderr), ("", ""))
                trace_outputs.append(output)
            self.assertEqual(trace_outputs[0].read_bytes(), trace_outputs[1].read_bytes())
            self.assertLess(trace_outputs[1].stat().st_size, 8 * 1024 * 1024)
            trace_hash = hashlib.sha256(trace_outputs[1].read_bytes()).hexdigest()
            plot_outputs = []
            for script, name in ((self.plotter, "build plot.svg"),
                                 (installed_plotter, "relocated plot.svg")):
                output = unrelated / name
                result = self.invoke([sys.executable, script, "--input", trace_outputs[1],
                                      "--output", output], unrelated, render_environment)
                self.assert_success(result)
                self.assertEqual(result.stderr, "")
                self.assertLessEqual(output.stat().st_size, 1024 * 1024)
                svg = output.read_bytes()
                self.assertEqual(ET.fromstring(svg).tag, "{http://www.w3.org/2000/svg}svg")
                self.assertIn(trace_hash.encode("ascii"), svg)
                plot_outputs.append(svg)
            self.assertEqual(plot_outputs[0], plot_outputs[1])

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
                missing_trace = unrelated / "missing profile trace.csv"
                trace_result = self.invoke(
                    [relocated / self.bindir / self.console_trace.name, "--profile", installed_profile,
                     *trace_options, "--output", missing_trace], unrelated, render_environment)
                self.assertNotEqual(trace_result.returncode, 0, trace_result.stderr)
                self.assertFalse(missing_trace.exists(), "Trace tool used an implicit profile fallback")
                missing_pedal_trace = unrelated / "missing profile pedal.csv"
                pedal_result = self.invoke(
                    [relocated / self.bindir / self.pedal_trace.name, "--profile", installed_profile,
                     "--scenario", "unmute", "--sample-rate", 48000, "--seed", 0,
                     "--output", missing_pedal_trace], unrelated, render_environment)
                self.assertNotEqual(pedal_result.returncode, 0)
                self.assertFalse(missing_pedal_trace.exists(), "Pedal trace used an implicit profile fallback")
            finally:
                installed_profile.write_bytes(profile_bytes)

    def assert_historical_parameter_compatibility(self, compiled_parameters, pedal_catalog):
        # Preserve the catalog's original v3/count45 evidence and compare
        # its frozen full-record digest with the explicit historical subset.
        control_model = pedal_catalog["control_model"]
        self.assertEqual(control_model["registry_schema_version"], 3)
        self.assertEqual(control_model["registry_model"], "exclusive-ab-percussion-pedal-console-v3")
        self.assertEqual(control_model["parameter_count"], 45)
        self.assertEqual(control_model["parameter_records_canonical_sha256"], HISTORICAL_PARAMETER_HASH)
        registry = json.loads((ROOT / "data/parameter-registry.json").read_bytes())
        historical = sorted((p for p in registry["parameters"] if p["id"] in HISTORICAL_PARAMETER_IDS),
                            key=lambda p: p["id"])
        self.assertEqual(len(historical), 45)
        canonical = json.dumps(historical, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=True, allow_nan=False).encode("ascii")
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), HISTORICAL_PARAMETER_HASH)
        compiled_by_id = {p["id"]: p for p in compiled_parameters["parameters"]}
        self.assertEqual(set(compiled_by_id), HISTORICAL_PARAMETER_IDS | {20480, 20481})
        self.assertEqual(compiled_parameters["registry_schema_version"], registry["schema_version"])
        self.assertEqual(compiled_parameters["model"], registry["model"])
        for record in historical:
            compiled = compiled_by_id[record["id"]]
            for field in ("path", "kind", "unit", "minimum", "maximum", "step_count"):
                self.assertEqual(compiled[field], record[field])
            self.assertEqual(compiled["default_plain"], record["default"])
            self.assertEqual(compiled["default_normalized"], record["normalized"]["default"])
            for field in ("type", "manual", "index"):
                self.assertEqual(compiled["event"][field], record["engine_event"][field])

    def assert_pedal_identity(self, document, catalog):
        for field in ("profile_id", "authoring_sha256"):
            self.assertEqual(document[field], catalog["profile"]["id" if field == "profile_id" else field])
        for field, name in (("pedal_routing_model", "pedal_routing"),
                            ("pedal_voice_model", "pedal_voice"),
                            ("pedal_gain_law", "pedal_gain"),
                            ("pedal_contact_model", "pedal_contacts")):
            self.assertEqual(document[field], catalog["models"][name])
        for name in ("map_id", "map_raw_sha256", "map_canonical_sha256"):
            self.assertEqual(document["pedal_" + name], catalog["routing"][name])
        for index, review in enumerate(("a", "b")):
            self.assertEqual(document[f"pedal_reference_{review}_sha256"],
                             catalog["routing"]["references"][index]["sha256"])

    def test_preflight_preserves_existing_prefix(self):
        # Generate the real module's install rules in an isolated tiny project.
        # No live source/build input is renamed or removed while other tests run.
        with tempfile.TemporaryDirectory(prefix="hammond install preflight ") as temporary:
            work = Path(temporary)
            source, build, prefix = work / "source", work / "build", work / "prefix"
            source.mkdir()
            prefix.mkdir()
            (prefix / "unrelated.txt").write_bytes(b"preserve unrelated user data\n")
            (source / "stub.cpp").write_text("int main() { return 0; }\n", encoding="ascii")
            shutil.copytree(ROOT / "examples" / "fixtures", source / "examples" / "fixtures")
            (source / "tools").mkdir()
            shutil.copyfile(self.plotter, source / "tools" / self.plotter.name)
            shutil.copyfile(self.pedal_plotter, source / "tools" / self.pedal_plotter.name)
            shutil.copyfile(self.profile, source / "nominal.b3p")
            targets = ("hammond_render", "hammond_model_info", "hammond_parameter_info",
                       "hammond_console_trace", "hammond_pedal_trace")
            script = ["cmake_minimum_required(VERSION 3.21)",
                      "project(OfflineInstallContract LANGUAGES CXX)",
                      'set(HAMMOND_COMPILED_PROFILE "${PROJECT_SOURCE_DIR}/nominal.b3p")']
            script.extend(f"add_executable({target} stub.cpp)" for target in targets)
            paths = "\\n".join(f"$<TARGET_FILE:{target}>" for target in targets)
            script.extend((f'file(GENERATE OUTPUT "${{CMAKE_BINARY_DIR}}/inputs-$<CONFIG>.txt" CONTENT "{paths}\\n")',
                           f'include([=[{(ROOT / "cmake" / "InstallHammondTools.cmake").as_posix()}]=])'))
            (source / "CMakeLists.txt").write_text("\n".join(script) + "\n", encoding="utf-8")
            environment = dict(os.environ)
            for name in ("DESTDIR", "CMAKE_INSTALL_MODE"):
                environment.pop(name, None)
            configuration = self.configuration or "Release"
            self.assert_success(self.invoke([self.cmake, "-S", source, "-B", build,
                                             f"-DCMAKE_BUILD_TYPE={configuration}"], work, environment))
            # GNUInstallDirs can cache an empty derived DATADIR. The project
            # must support repeated default configuration while still rejecting
            # an explicitly empty command-line value below. Automatic defaults
            # follow DATAROOTDIR; custom DATADIR values remain independent.
            def cached_datadir():
                cache = (build / "CMakeCache.txt").read_text(encoding="utf-8")
                match = re.search(r"^CMAKE_INSTALL_DATADIR:PATH=(.*)$", cache, re.MULTILINE)
                self.assertIsNotNone(match)
                return match.group(1)

            self.assertEqual(cached_datadir(), "share")
            configure = [self.cmake, "-S", source, "-B", build]
            self.assert_success(self.invoke(configure, work, environment))
            self.assertEqual(cached_datadir(), "share")
            self.assert_success(self.invoke(configure + ["-DCMAKE_INSTALL_DATAROOTDIR=assets"],
                                             work, environment))
            self.assertEqual(cached_datadir(), "assets")
            self.assert_success(self.invoke(configure, work, environment))
            self.assertEqual(cached_datadir(), "assets")
            self.assert_success(self.invoke(configure + ["-DCMAKE_INSTALL_DATADIR=custom/data"],
                                             work, environment))
            self.assert_success(self.invoke(configure + ["-DCMAKE_INSTALL_DATAROOTDIR=share"],
                                             work, environment))
            self.assertEqual(cached_datadir(), "custom/data")
            self.assert_success(self.invoke(configure + ["-DCMAKE_INSTALL_DATADIR=share"],
                                             work, environment))
            outputs = [Path(value) for value in (build / f"inputs-{configuration}.txt").read_text(
                encoding="utf-8").splitlines()]
            install = [self.cmake, "--install", build, "--config", configuration,
                       "--component", "OfflineTools", "--prefix", prefix]

            def snapshot():
                return {str(path.relative_to(prefix)): path.read_bytes() if path.is_file() else None
                        for path in prefix.rglob("*")}

            before = snapshot()
            unbuilt = self.invoke(install, work, environment)
            self.assertNotEqual(unbuilt.returncode, 0)
            self.assertIn("OfflineTools missing required file", unbuilt.stderr)
            self.assertEqual(snapshot(), before)
            originals = (self.renderer, self.model_info, self.parameter_info,
                         self.console_trace, self.pedal_trace)
            for original, output in zip(originals, outputs):
                output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(original, output)
            # Missing binaries, profile, plot script and catalog/score inputs all
            # fail before an existing installed executable or unrelated data changes.
            (prefix / "bin").mkdir()
            (prefix / "bin" / self.renderer.name).write_bytes(b"older installation\n")
            before = snapshot()
            missing_inputs = [*outputs, source / "nominal.b3p", source / "tools" / self.plotter.name,
                              source / "tools" / self.pedal_plotter.name,
                              source / "examples/fixtures/catalog-v1.json",
                              source / "examples/fixtures/console/console-travel-v1.events",
                              source / "examples/fixtures/pedals/pedal-catalog-v1.json",
                              source / "examples/fixtures/pedals/pedal-phrase-v1.events"]
            for missing in missing_inputs:
                with self.subTest(missing=missing.name):
                    backup = missing.with_name(missing.name + ".held")
                    missing.rename(backup)
                    try:
                        result = self.invoke(install, work, environment)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn("OfflineTools missing required file", result.stderr)
                        self.assertIn(missing.name, result.stderr)
                        self.assertEqual(snapshot(), before)
                    finally:
                        backup.rename(missing)
            # Also exercise directory policy rather than relying on text inspection.
            for directory in ("CMAKE_INSTALL_BINDIR", "CMAKE_INSTALL_DATADIR"):
                for invalid in ("../escape", str(work / "absolute destination"), "..\\escape", ""):
                    with self.subTest(directory=directory, invalid=invalid):
                        result = self.invoke([self.cmake, "-S", source, "-B", build,
                                              "-DCMAKE_INSTALL_BINDIR=bin", "-DCMAKE_INSTALL_DATADIR=share",
                                              f"-D{directory}:PATH={invalid}"], work, environment)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertIn("nonempty relative", result.stderr)
                        self.assertEqual(snapshot(), before)


if __name__ == "__main__":
    unittest.main()
