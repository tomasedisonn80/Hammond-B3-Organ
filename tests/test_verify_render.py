#!/usr/bin/env python3
"""Independent-consumer tests using real renderer bundles plus targeted mutations.

CTest supplies HAMMOND_RENDER_EXECUTABLE and HAMMOND_TEST_PROFILE. Missing build
inputs fail explicitly; the producer is used only to create genuine fixtures.
"""

import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


consumer = module("independent_render_consumer", "verify_render.py")
producer = module("test_fixture_producer", "render_fixture.py")

# Exact additive schema-3 fields, independent of the producer and consumer.
PEDAL_METRIC_FIELDS = (
    "pedal_routing_model", "pedal_voice_model", "pedal_gain_law", "pedal_contact_model",
    "pedal_map_id", "pedal_map_raw_sha256", "pedal_map_canonical_sha256",
    "pedal_reference_a_sha256", "pedal_reference_b_sha256", "pedal_mixture_matrix",
    "pedal_mixture_denominator", "pedal_gain_denominator", "pedal_weight_policy",
)


def required_file(name):
    value = os.environ.get(name)
    if not value or not Path(value).is_file():
        raise RuntimeError(f"Missing prerequisite {name}: {value!r}; build hammond_render and nominal.b3p, "
                           "then run CTest or set both HAMMOND_RENDER_EXECUTABLE and HAMMOND_TEST_PROFILE. "
                           "Independent evidence tests were not run.")
    return Path(value).resolve()


class VerifyRenderTests(unittest.TestCase):
    @staticmethod
    def legacy_grammar_fixture(source, destination, version=1):
        """Construct old-schema parser evidence from muted-pedal current audio.

        Metadata is deliberately rewritten; this does not claim the current
        renderer emitted schema 1/2. Actual old-executable audio is compared in
        the separate legacy replay gate. No old executable is a CTest dependency.
        """
        if version not in (1, 2):
            raise ValueError("historical parser fixture version must be 1 or 2")
        shutil.copytree(source, destination)
        manifest = json.loads((destination / "manifest.json").read_bytes())
        if manifest["schema_version"] != 3 or manifest["parameters"]["pedal_drawbars"] != "00":
            raise ValueError("historical parser fixture requires current muted-pedal input")
        manifest["schema_version"] = version
        del manifest["parameters"]["pedal_drawbars"]
        argv = manifest["invocation"]["argv"]
        pedal_index = argv.index("--pedal-drawbars")
        del argv[pedal_index:pedal_index + 2]
        for name in PEDAL_METRIC_FIELDS:
            del manifest["renderer_metrics"][name]
        manifest["renderer_metrics"]["render_schema_version"] = 2
        if version == 1:
            for name in ("contacts", "percussion", "percussion_volume", "percussion_decay"):
                del manifest["parameters"][name]
                flag_index = argv.index("--" + name.replace("_", "-"))
                del argv[flag_index:flag_index + 2]
            for name in ("render_schema_version", "contact_model", "percussion_model"):
                del manifest["renderer_metrics"][name]
        VerifyRenderTests.rewrite(destination, manifest["invocation"]["stdout"],
                                 (json.dumps(manifest["renderer_metrics"]) + "\n").encode("utf-8"))
        VerifyRenderTests.save(destination, manifest)

    @classmethod
    def setUpClass(cls):
        source_renderer = required_file("HAMMOND_RENDER_EXECUTABLE")
        cls.expected_compiled = required_file("HAMMOND_TEST_PROFILE").read_bytes()
        if not os.access(source_renderer, os.X_OK):
            raise RuntimeError(f"HAMMOND_RENDER_EXECUTABLE is not executable: {source_renderer}")
        temporary = tempfile.TemporaryDirectory(prefix="hammond-consumer-fixtures-")
        cls.addClassCleanup(temporary.cleanup)
        cls.fixtures = Path(temporary.name).resolve()
        cls.renderer = cls.fixtures / ("renderer under test" + source_renderer.suffix)
        shutil.copy2(source_renderer, cls.renderer)
        cls.profile = cls.fixtures / "source profile.json"
        cls.profile.write_bytes((ROOT / "data/profiles/nominal-unmeasured-v1.json").read_bytes())
        cls.base = cls.fixtures / "retained note bundle"
        cls.event_base = cls.fixtures / "retained events bundle"
        cls.console_base = cls.fixtures / "retained nominal console bundle"
        cls.legacy_base = cls.fixtures / "constructed schema1 note bundle"
        cls.legacy_event_base = cls.fixtures / "constructed schema1 event bundle"
        score = cls.fixtures / "source events.txt"
        score.write_bytes(b"\xef\xbb\xbf# all supported controls; explicit CRLF\r\n"
                          b"0 drawbar upper 2 8\r\n0 bank_drawbar upper 11 6\r\n"
                          b"0 select_bank upper 0 1\r\n0 note_on upper 60 100\r\n"
                          b"1 expression lower 0 .25\r\n3 cancel upper 0 0\r\n"
                          b"3 select_bank upper 0 0\r\n4 note_off upper 60 0\r\n"
                          b"5 note_on lower 48 127\r\n6 all_notes_off lower 0 0\r\n")
        for directory, events in ((cls.base, None), (cls.event_base, score)):
            result = producer.run_fixture(renderer=cls.renderer, output_dir=directory,
                                          profile_json=cls.profile, frames=259, sample_rate=48000,
                                          block_size=127, seed=7, drawbars="008000000", events=events)
            if result["status"] != "succeeded":
                raise RuntimeError(f"Real-render prerequisite failed: {result['error']}")
        if (cls.base / "profile.b3p").read_bytes() != cls.expected_compiled:
            raise RuntimeError("Real fixture's compiled profile differs from HAMMOND_TEST_PROFILE")
        cls.legacy_grammar_fixture(cls.base, cls.legacy_base)
        cls.legacy_grammar_fixture(cls.event_base, cls.legacy_event_base)
        console_score = cls.fixtures / "console events.txt"
        console_score.write_bytes(
            b"0 select_bank upper 0 1\n0 percussion upper 0 1.0\n"
            b"0 percussion upper 1 1e0\n0 percussion upper 2 0.0\n"
            b"0 percussion upper 3 +1\n0 note_on upper 60 100\n"
            b"1000 note_off upper 60 0\n1700 note_on upper 64 100\n"
            b"2400 percussion upper 0 0\n2700 all_notes_off upper 0 0\n")
        result = producer.run_fixture(renderer=cls.renderer, output_dir=cls.console_base,
                                      profile_json=cls.profile, frames=4096, sample_rate=48000,
                                      block_size=127, seed=7, drawbars="008000000",
                                      contacts="nominal", percussion="third", percussion_volume="soft",
                                      percussion_decay="fast", events=console_score)
        if result["status"] != "succeeded":
            raise RuntimeError(f"Nominal-console real-render prerequisite failed: {result['error']}")
        cls.schema2_base = cls.fixtures / "constructed schema2 note bundle"
        cls.schema2_event_base = cls.fixtures / "constructed schema2 event bundle"
        cls.schema2_console_base = cls.fixtures / "constructed schema2 console bundle"
        for source, destination in ((cls.base, cls.schema2_base),
                                    (cls.event_base, cls.schema2_event_base),
                                    (cls.console_base, cls.schema2_console_base)):
            cls.legacy_grammar_fixture(source, destination, version=2)

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="hammond-consumer-mutations-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name).resolve()
        self.sequence = 0

    def clone(self, source=None):
        self.sequence += 1
        directory = self.work / f"copied bundle {self.sequence}"
        shutil.copytree(source or self.base, directory)
        return directory, json.loads((directory / "manifest.json").read_bytes())

    @staticmethod
    def save(directory, manifest):
        (directory / "manifest.json").write_bytes(
            (json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8"))

    @staticmethod
    def rewrite(directory, record, raw):
        (directory / record["path"]).write_bytes(raw)
        record["size_bytes"] = len(raw)
        record["sha256"] = hashlib.sha256(raw).hexdigest()

    def reject(self, directory, manifest=None, message=None):
        if manifest is not None:
            self.save(directory, manifest)
        context = self.assertRaisesRegex(consumer.VerificationError, message) if message else (
            self.assertRaises((consumer.VerificationError, OSError)))
        with context:
            consumer.verify_bundle(directory)

    def change_field(self, keys, value, source=None):
        directory, manifest = self.clone(source)
        target = manifest
        for key in keys[:-1]:
            target = target[key]
        target[keys[-1]] = value
        self.reject(directory, manifest)

    def test_real_bundle_recomputes_identity_pcm_and_reports_scope(self):
        report = consumer.verify_bundle(self.base)
        self.assertEqual(report["status"], "verified_retained_bundle")
        self.assertEqual(report["schema_version"], 3)
        self.assertEqual(report["artifacts_verified"], 5)
        self.assertEqual(report["evidence_scope"], "synthetic_engineering")
        self.assertEqual(report["renderer"]["status"], "matched")
        self.assertEqual(report["replay"]["status"], "not_performed")
        for key in ("authentication", "source_build_association", "physical_fidelity"):
            self.assertEqual(report["provenance"][key], "not_established")
        manifest = json.loads((self.base / "manifest.json").read_bytes())
        raw = (self.base / "render.wav").read_bytes()
        samples = struct.unpack("<" + "h" * (manifest["parameters"]["frames"] * 2), raw[44:])
        left, right = samples[::2], samples[1::2]
        self.assertEqual(left, right)
        self.assertEqual(manifest["wav"]["pcm_peak_integer"], max(map(abs, left)))
        squares = sum(sample * sample for sample in left)
        self.assertEqual(manifest["wav"]["pcm_sum_squares_integer"], squares)
        self.assertEqual(manifest["wav"]["pcm_rms"], math.sqrt(squares / len(left)) / 32768)
        self.assertEqual(report["wav_sha256"], hashlib.sha256(raw).hexdigest())

    def test_relocated_bundle_and_manifest_path_are_accepted(self):
        directory, manifest = self.clone()
        self.assertNotEqual(Path(manifest["invocation"]["argv"][2]).parent, directory)
        report = consumer.verify_bundle(directory / "manifest.json")
        self.assertEqual(report["status"], "verified_retained_bundle")
        self.assertEqual(report["manifest"], str(directory / "manifest.json"))

    def test_constructed_schema1_note_and_event_grammars_remain_supported(self):
        for source, artifact_count in ((self.legacy_base, 5), (self.legacy_event_base, 6)):
            with self.subTest(source=source.name):
                directory, manifest = self.clone(source)
                self.assertEqual(len(manifest["parameters"]), 9)
                self.assertEqual(len(manifest["invocation"]["argv"]), 18)
                self.assertEqual(len(manifest["renderer_metrics"]), 15)
                report = consumer.verify_bundle(directory)
                self.assertEqual(report["schema_version"], 1)
                self.assertEqual(report["artifacts_verified"], artifact_count)
                self.assertEqual(report["replay"]["status"], "not_performed")
                self.assertEqual(report["provenance"]["authentication"], "not_established")

    def test_constructed_schema2_note_event_and_console_grammars_remain_supported(self):
        for source, artifact_count in ((self.schema2_base, 5), (self.schema2_event_base, 6),
                                       (self.schema2_console_base, 6)):
            with self.subTest(source=source.name):
                directory, manifest = self.clone(source)
                self.assertEqual(len(manifest["parameters"]), 13)
                self.assertEqual(len(manifest["invocation"]["argv"]), 26)
                self.assertEqual(len(manifest["renderer_metrics"]), 18)
                report = consumer.verify_bundle(directory)
                self.assertEqual(report["schema_version"], 2)
                self.assertEqual(report["artifacts_verified"], artifact_count)
                self.assertEqual(report["replay"]["status"], "not_performed")
                self.assertEqual(report["provenance"]["authentication"], "not_established")

    def test_real_nominal_console_bundle_checks_model_and_retained_events(self):
        report = consumer.verify_bundle(self.console_base)
        manifest = json.loads((self.console_base / "manifest.json").read_bytes())
        self.assertEqual(report["schema_version"], 3)
        self.assertEqual(report["artifacts_verified"], 6)
        self.assertEqual(len(manifest["parameters"]), 14)
        self.assertEqual(len(manifest["invocation"]["argv"]), 28)
        self.assertEqual(len(manifest["renderer_metrics"]), 31)
        self.assertEqual(manifest["renderer_metrics"]["contact_model"], "nominal-linear-travel-v1")
        self.assertEqual(manifest["renderer_metrics"]["percussion_model"], "shared-readiness-v1")
        self.assertGreater(manifest["wav"]["pcm_sum_squares_integer"], 0)
        self.assertEqual(manifest["parameters"]["event_count"], 10)

    def test_all_console_parameter_combinations_verify_actual_renders(self):
        for contacts in ("ideal", "nominal"):
            for percussion in ("off", "second", "third"):
                for volume in ("normal", "soft"):
                    for decay in ("slow", "fast"):
                        with self.subTest(contacts=contacts, percussion=percussion, volume=volume, decay=decay):
                            directory = self.work / f"{contacts}-{percussion}-{volume}-{decay}"
                            result = producer.run_fixture(
                                renderer=self.renderer, output_dir=directory, profile_json=self.profile,
                                frames=401, sample_rate=48000, block_size=127, seed=7,
                                drawbars="008000000", contacts=contacts, percussion=percussion,
                                percussion_volume=volume, percussion_decay=decay)
                            self.assertEqual(result["status"], "succeeded", result["error"])
                            self.assertEqual(consumer.verify_bundle(directory)["schema_version"], 3)

    def test_schema2_and_current_console_parameters_require_exact_strings_and_fields(self):
        invalid = {
            "contacts": ("Ideal", "linear", "", 0, False, None, [], {}),
            "percussion": ("on", "Second", "", 1, True, None, [], {}),
            "percussion_volume": ("loud", "Soft", "", 0, False, None, [], {}),
            "percussion_decay": ("quick", "Slow", "", 0, False, None, [], {}),
        }
        for source in (self.schema2_base, self.base):
            for name, values in invalid.items():
                for value in values:
                    with self.subTest(source=source.name, name=name, value=value):
                        self.change_field(["parameters", name], value, source)
                directory, manifest = self.clone(source)
                del manifest["parameters"][name]
                self.reject(directory, manifest, "parameters")
            directory, manifest = self.clone(source)
            manifest["parameters"]["console_model"] = "nominal"
            self.reject(directory, manifest, "parameters")

    def test_schema1_rejects_new_parameters_metrics_invocation_and_events(self):
        for name, value in (("contacts", "ideal"), ("percussion", "off"),
                            ("percussion_volume", "normal"), ("percussion_decay", "slow")):
            with self.subTest(parameter=name):
                self.change_field(["parameters", name], value, self.legacy_base)
        for name, value in (("render_schema_version", 2), ("contact_model", "ideal-contacts-v1"),
                            ("percussion_model", "shared-readiness-v1")):
            with self.subTest(metric=name):
                directory, manifest = self.clone(self.legacy_base)
                manifest["renderer_metrics"][name] = value
                self.rewrite(directory, manifest["invocation"]["stdout"],
                             json.dumps(manifest["renderer_metrics"]).encode("utf-8"))
                self.reject(directory, manifest, "renderer_metrics")
        directory, manifest = self.clone(self.legacy_base)
        manifest["invocation"]["argv"][15:15] = ["--contacts", "ideal", "--percussion", "off",
                                                "--percussion-volume", "normal", "--percussion-decay", "slow"]
        self.reject(directory, manifest, "invocation.argv")
        directory, manifest = self.clone(self.legacy_event_base)
        self.rewrite(directory, manifest["inputs"]["events"], b"0 percussion upper 0 1\n")
        manifest["parameters"]["event_count"] = 1
        self.reject(directory, manifest, "events")

    def test_schema2_and_current_require_matching_model_fields_and_render_version(self):
        for source, console, version in ((self.schema2_base, self.schema2_console_base, 2),
                                         (self.base, self.console_base, 3)):
            changes = (("render_schema_version", 1), ("render_schema_version", 5 - version),
                       ("render_schema_version", float(version)), ("render_schema_version", True),
                       ("contact_model", "nominal-linear-travel-v1"), ("contact_model", "ideal"),
                       ("contact_model", None), ("percussion_model", "none"),
                       ("percussion_model", None))
            for key, value in changes:
                with self.subTest(version=version, key=key, value=value):
                    directory, manifest = self.clone(source)
                    manifest["renderer_metrics"][key] = value
                    self.rewrite(directory, manifest["invocation"]["stdout"],
                                 json.dumps(manifest["renderer_metrics"]).encode("utf-8"))
                    self.reject(directory, manifest, "renderer_metrics")
            for key in ("render_schema_version", "contact_model", "percussion_model"):
                with self.subTest(version=version, missing=key):
                    directory, manifest = self.clone(source)
                    del manifest["renderer_metrics"][key]
                    self.rewrite(directory, manifest["invocation"]["stdout"],
                                 json.dumps(manifest["renderer_metrics"]).encode("utf-8"))
                    self.reject(directory, manifest, "renderer_metrics")
            directory, manifest = self.clone(console)
            manifest["renderer_metrics"]["contact_model"] = "ideal-contacts-v1"
            self.rewrite(directory, manifest["invocation"]["stdout"],
                         json.dumps(manifest["renderer_metrics"]).encode("utf-8"))
            self.reject(directory, manifest, "contact_model")

    def test_schema2_and_current_reject_rehashed_invalid_percussion_scores(self):
        invalid = (b"0 percussion lower 0 1\n", b"0 percussion upper 4 1\n",
                   b"0 percussion upper 0 -1\n", b"0 percussion upper 1 2\n",
                   b"0 percussion upper 2 .5\n", b"0 percussion upper 3 0.999\n",
                   b"0 percussion upper -1 1\n", b"0 percussion upper 1.0 1\n",
                   b"0 percussion upper 0 1e-999\n", b"0 percussion upper 0 nan\n",
                   b"0 percussion upper 0 1 extra\n")
        for source in (self.schema2_console_base, self.console_base):
            for raw in invalid:
                with self.subTest(source=source.name, score=raw):
                    directory, manifest = self.clone(source)
                    self.rewrite(directory, manifest["inputs"]["events"], raw)
                    manifest["parameters"]["event_count"] = 1
                    self.reject(directory, manifest, "events")

    def test_consumer_does_not_call_producer_verification_helpers(self):
        with mock.patch.object(producer, "inspect_wav", side_effect=AssertionError("producer WAV helper")), \
             mock.patch.object(producer, "validate_events", side_effect=AssertionError("producer event helper")), \
             mock.patch.object(producer, "sha256_file", side_effect=AssertionError("producer hash helper")), \
             mock.patch.object(producer, "_validate_metrics", side_effect=AssertionError("producer metric helper")):
            self.assertEqual(consumer.verify_bundle(self.event_base)["artifacts_verified"], 6)

    def test_empty_events_supported_rates_and_uint64_seed(self):
        events = self.work / "empty events.txt"
        events.write_bytes(b"")
        for rate in (44100, 96000):
            with self.subTest(rate=rate):
                directory = self.work / str(rate)
                result = producer.run_fixture(renderer=self.renderer, output_dir=directory,
                                              profile_json=self.profile, events=events, frames=17,
                                              sample_rate=rate, block_size=65536, seed=2**64 - 1)
                self.assertEqual(result["status"], "succeeded", result["error"])
                report = consumer.verify_bundle(directory)
                self.assertEqual(report["sample_rate"], rate)
                self.assertEqual(result["wav"]["pcm_sum_squares_integer"], 0)

    def test_missing_external_renderer_keeps_retained_verification_explicit(self):
        directory, manifest = self.clone()
        absent = str(self.work / "absent renderer")
        manifest["renderer"]["path"] = absent
        manifest["invocation"]["argv"][0] = absent
        self.save(directory, manifest)
        report = consumer.verify_bundle(directory)
        self.assertEqual(report["status"], "verified_retained_bundle")
        self.assertEqual(report["renderer"]["status"], "unavailable")
        self.assertFalse(report["replay"]["renderer_available"])
        self.assertEqual(report["provenance"]["source_build_association"], "not_established")

    def test_changed_external_renderer_is_rejected(self):
        directory, manifest = self.clone()
        changed = self.work / "changed renderer"
        shutil.copy2(self.renderer, changed)
        with changed.open("ab") as stream:
            stream.write(b"changed bytes")
        manifest["renderer"]["path"] = str(changed)
        manifest["invocation"]["argv"][0] = str(changed)
        self.reject(directory, manifest, "current renderer")

    def test_recorded_renderer_hashes_must_agree(self):
        for keys, value in ((["renderer", "sha256_after"], "0" * 64),
                            (["renderer", "sha256_before"], "A" * 64),
                            (["renderer", "sha256_after"], None),
                            (["renderer", "size_bytes"], True)):
            with self.subTest(keys=keys):
                self.change_field(keys, value)

    def test_success_scope_integrity_and_error_must_be_true_claims(self):
        for key, values in {"schema_version": [True, 3.0, 0, 1, 2, 4], "status": ["failed", "incomplete"],
                            "evidence_scope": ["measured"], "integrity_verified": [False, 1],
                            "error": [{"stage": "metrics", "message": "failure"}]}.items():
            for value in values:
                with self.subTest(key=key, value=value):
                    self.change_field([key], value)

    def test_manifest_structure_and_context_are_typed(self):
        changes = [(["parameters", "frames"], True), (["parameters", "seed"], 2**64),
                   (["parameters", "block_size"], 0), (["parameters", "sample_rate"], 32000),
                   (["parameters", "drawbars"], "888000009"), (["parameters", "note"], 35),
                   (["parameters", "event_count"], 0), (["parameters", "fail_on_clip"], False),
                   (["limits", "expected_wav_bytes"], 0), (["limits", "log_bytes_per_stream"], 2**30),
                   (["git", "dirty"], 1), (["git", "head"], "unknown"),
                   (["git", "binary_association"], "authenticated"),
                   (["tools", "wrapper", "size_bytes"], -1),
                   (["environment", "byteorder"], "middle"),
                   (["started_at_utc"], "2026-02-30T00:00:00Z"),
                   (["finished_at_utc"], "1999-01-01T00:00:00Z")]
        for keys, value in changes:
            with self.subTest(keys=keys):
                self.change_field(keys, value)
        directory, manifest = self.clone()
        manifest["unexpected"] = True
        self.reject(directory, manifest)
        del manifest["unexpected"]
        del manifest["invocation"]["capture_errors"]
        self.reject(directory, manifest)

    def test_duplicate_nonfinite_deep_oversized_and_non_utf8_json(self):
        bad_values = [b'{"status":"failed","status":"succeeded"}',
                      b'{"outer":{"same":1,"same":2}}', b'{"number":NaN}',
                      b'{"number":Infinity}', b'{"number":1e999}',
                      b'{"number":' + b"1" * 129 + b"}",
                      b"[" * 30 + b"0" + b"]" * 30,
                      b'{"text":"\\ud800"}', b"\xff", b" " * (consumer.MAX_MANIFEST + 1)]
        for raw in bad_values:
            with self.subTest(prefix=raw[:50]):
                directory, _ = self.clone()
                (directory / "manifest.json").write_bytes(raw)
                self.reject(directory)

    def test_missing_extra_and_nonregular_artifacts_fail(self):
        for name in ("manifest.json", "profile.json", "profile.b3p", "render.wav",
                     "renderer.stdout.txt", "renderer.stderr.txt"):
            with self.subTest(missing=name):
                directory, _ = self.clone()
                (directory / name).unlink()
                self.reject(directory)
        directory, _ = self.clone()
        (directory / "extra.txt").write_bytes(b"unexpected")
        self.reject(directory)
        directory, _ = self.clone()
        (directory / "profile.b3p").unlink()
        (directory / "profile.b3p").mkdir()
        self.reject(directory)

    def test_fixed_artifact_paths_reject_escape_absolute_and_alias_names(self):
        for value in ("../render.wav", str(self.base / "render.wav"), "./render.wav", "other.wav"):
            with self.subTest(value=value):
                self.change_field(["wav", "path"], value)

    def test_symlink_artifacts_bundle_and_parent_are_rejected(self):
        for name in ("manifest.json", "profile.json", "render.wav"):
            with self.subTest(artifact=name):
                directory, _ = self.clone()
                (directory / name).unlink()
                (directory / name).symlink_to(self.base / name)
                self.reject(directory)
        alias = self.work / "bundle alias"
        alias.symlink_to(self.base, target_is_directory=True)
        self.reject(alias)
        parent_alias = self.work / "parent alias"
        parent_alias.symlink_to(self.fixtures, target_is_directory=True)
        self.reject(parent_alias / self.base.name)

    def test_every_retained_artifact_hash_and_size_is_checked(self):
        for name in ("profile.json", "profile.b3p", "render.wav", "renderer.stdout.txt", "renderer.stderr.txt"):
            with self.subTest(artifact=name):
                directory, _ = self.clone()
                path = directory / name
                raw = path.read_bytes()
                path.write_bytes((bytes([raw[0] ^ 1]) + raw[1:]) if raw else b"modified")
                self.reject(directory)
        self.change_field(["compiled_profile", "size_bytes"], 0)
        directory, _ = self.clone(self.event_base)
        with (directory / "events.txt").open("ab") as stream:
            stream.write(b"# changed\n")
        self.reject(directory)

    def test_compiled_profile_reconstruction_rejects_rehashed_change(self):
        directory, manifest = self.clone()
        compiled = (directory / "profile.b3p").read_bytes() + b"\n"
        self.rewrite(directory, manifest["compiled_profile"], compiled)
        self.reject(directory, manifest, "independently recompiled")

    def test_profile_raw_hash_canonical_identity_and_semantics_are_distinct(self):
        directory, manifest = self.clone()
        raw = b"\n" + (directory / "profile.json").read_bytes() + b"\n"
        self.rewrite(directory, manifest["inputs"]["profile_json"], raw)
        self.save(directory, manifest)
        self.assertEqual(consumer.verify_bundle(directory)["status"], "verified_retained_bundle")
        self.change_field(["inputs", "profile_json", "canonical_authoring_sha256"], "0" * 64)
        for raw in (b'{"schema_version":1,"schema_version":1}', b'{"number":NaN}'):
            directory, manifest = self.clone()
            self.rewrite(directory, manifest["inputs"]["profile_json"], raw)
            self.reject(directory, manifest)
        directory, manifest = self.clone()
        profile = json.loads((directory / "profile.json").read_bytes())
        profile["output_gain"]["value"] = 0.5
        self.rewrite(directory, manifest["inputs"]["profile_json"], json.dumps(profile).encode("utf-8"))
        self.reject(directory, manifest, "profile compilation failed")

    def test_argv_exact_parameters_flags_and_copied_paths_are_checked(self):
        for index, value in ((0, "other-renderer"), (1, "--unknown"), (2, str(self.work / "other.b3p")),
                             (4, str(self.work / "render.wav")), (6, "260"), (10, "0127"),
                             (12, "8"), (14, "888000000"), (15, "--unknown"),
                             (16, "80"), (17, "--unknown"), (18, "nominal"),
                             (19, "--unknown"), (20, "second"), (21, "--unknown"),
                             (22, "soft"), (23, "--unknown"), (24, "fast"),
                             (25, "--no-fail-on-clip"), (26, "--events"), (27, "61")):
            with self.subTest(index=index):
                directory, manifest = self.clone()
                manifest["invocation"]["argv"][index] = value
                self.reject(directory, manifest)
        directory, manifest = self.clone()
        manifest["invocation"]["argv"] += ["--frames", "259"]
        self.reject(directory, manifest)

    def test_capture_failure_flags_and_return_code_cannot_claim_success(self):
        for key, value in (("returncode", 2), ("returncode", False), ("timed_out", True),
                           ("stdout_truncated", True), ("stderr_truncated", True),
                           ("capture_incomplete", True), ("capture_errors", ["lost log"]),
                           ("capture_errors", None)):
            with self.subTest(key=key):
                self.change_field(["invocation", key], value)

    def test_actual_stdout_must_equal_manifest_and_be_strict_bounded_json(self):
        directory, manifest = self.clone()
        manifest["renderer_metrics"]["peak"] += 1e-7
        self.reject(directory, manifest, "actual retained stdout")
        for raw in (b'{"status":"ok","status":"ok"}', b'{"peak":NaN}',
                    b" " * (consumer.MAX_METRICS + 1), b"[]", b"\xff"):
            with self.subTest(raw=raw[:30]):
                directory, manifest = self.clone()
                self.rewrite(directory, manifest["invocation"]["stdout"], raw)
                self.reject(directory, manifest)

    def test_rehashed_false_metrics_fail_identity_types_range_and_zero_clip(self):
        for key, value in (("frames", 260), ("sample_rate", 44100), ("block_size", 64),
                           ("seed", 8), ("status", "clipped"), ("model", "measured"),
                           ("evidence_status", "measured"), ("profile_id", "other"),
                           ("authoring_sha256", "0" * 64), ("channels", True),
                           ("sample_format", "float32"), ("clipped_frames", 1),
                           ("clipped_channel_samples", 1), ("peak", True),
                           ("peak", -0.01), ("peak", 1.1), ("rms", 0.9)):
            with self.subTest(key=key, value=value):
                directory, manifest = self.clone()
                manifest["renderer_metrics"][key] = value
                self.rewrite(directory, manifest["invocation"]["stdout"],
                             json.dumps(manifest["renderer_metrics"]).encode("utf-8"))
                self.reject(directory, manifest)

    def test_rehashed_wav_header_truncation_channels_and_sample_stats_fail(self):
        mutations = [lambda raw: raw[:4] + struct.pack("<I", 1) + raw[8:],
                     lambda raw: raw[:20] + struct.pack("<H", 3) + raw[22:],
                     lambda raw: raw[:24] + struct.pack("<I", 44100) + raw[28:],
                     lambda raw: raw[:32] + struct.pack("<H", 2) + raw[34:],
                     lambda raw: raw[:34] + struct.pack("<H", 24) + raw[36:],
                     lambda raw: raw[:-4], lambda raw: raw + b"extra",
                     lambda raw: raw[:46] + struct.pack("<h", 12345) + raw[48:],
                     lambda raw: raw[:44] + struct.pack("<hh", 12345, 12345) + raw[48:]]
        for index, mutate in enumerate(mutations):
            with self.subTest(mutation=index):
                directory, manifest = self.clone()
                self.rewrite(directory, manifest["wav"], mutate((directory / "render.wav").read_bytes()))
                self.reject(directory, manifest)

    def test_false_pcm_statistics_domains_and_comparison_assertions_fail(self):
        changes = [(["wav", "channels_identical"], False), (["wav", "normalization_divisor"], 32767),
                   (["wav", "pcm_peak_integer"], 0), (["wav", "pcm_sum_squares_integer"], 0),
                   (["wav", "pcm_peak"], 0), (["wav", "pcm_rms"], 0),
                   (["wav", "metric_domain"], "engine_pre_quantization"),
                   (["metric_comparison", "within_quantization_bound"], False),
                   (["metric_comparison", "absolute_error_bound"], 1),
                   (["metric_comparison", "numeric_tolerance"], 1),
                   (["metric_comparison", "peak_absolute_difference"], 0.0),
                   (["metric_comparison", "rms_absolute_difference"], 0.0)]
        for keys, value in changes:
            with self.subTest(keys=keys):
                self.change_field(keys, value)

    def test_rehashed_plausible_float_metrics_must_meet_actual_pcm_bound(self):
        directory, manifest = self.clone()
        manifest["renderer_metrics"]["peak"] = 0.5
        manifest["renderer_metrics"]["rms"] = 0.25
        self.rewrite(directory, manifest["invocation"]["stdout"],
                     json.dumps(manifest["renderer_metrics"]).encode("utf-8"))
        self.reject(directory, manifest, "quantization bound")

    def test_event_count_and_independent_grammar_reject_rehashed_bad_scores(self):
        bad_scores = [b"0 unknown upper 0 0\n", b"0 note_on pedals 60 127\n",
                      b"0 note_on upper 35 127\n", b"0 note_on upper 60 127.1\n",
                      b"0 note_off upper 60 1\n", b"0 drawbar upper 9 8\n",
                      b"0 bank_drawbar upper 18 8\n", b"0 select_bank upper 0 2\n",
                      b"0 cancel upper 1 0\n", b"0 all_notes_off upper 0 1\n",
                      b"0 expression upper 0 1e999\n", b"0 expression upper 0 1e-999\n",
                      b"0 expression upper 0 nan\n", b"0 expression upper 0 0x1\n",
                      b"+0 note_on upper 60 127\n", b"259 note_on upper 60 127\n",
                      b"2 note_on upper 60 127\n1 note_off upper 60 0\n",
                      b"0 note_on upper 60 127 extra\n", b"0 note_on upper 60 127\x00\n",
                      b"#" + b"x" * 4096 + b"\n", b"\xff\n",
                      b"0 cancel upper 0 0\n" * 1025]
        for raw in bad_scores:
            with self.subTest(score=raw[:60]):
                directory, manifest = self.clone(self.event_base)
                self.rewrite(directory, manifest["inputs"]["events"], raw)
                manifest["parameters"]["event_count"] = raw.count(b"\n")
                self.reject(directory, manifest, "events")
        self.change_field(["parameters", "event_count"], 9, self.event_base)
        self.change_field(["parameters", "note"], 60, self.event_base)

    def test_changed_file_after_its_read_is_rejected(self):
        directory, _ = self.clone()
        original_compile = consumer._compiler.compile_profile

        def change_after_read(profile):
            with (directory / "profile.json").open("ab") as stream:
                stream.write(b" ")
            return original_compile(profile)

        with mock.patch.object(consumer._compiler, "compile_profile", side_effect=change_after_read):
            self.reject(directory, message="file changed during verification")

    def test_descriptor_metadata_is_compared_with_its_own_observation(self):
        directory, _ = self.clone()
        file = directory / "renderer.stdout.txt"
        reader = consumer._Reader()
        real_fstat = os.fstat

        def different_api_times(descriptor):
            info = real_fstat(descriptor)
            return types.SimpleNamespace(st_dev=info.st_dev, st_ino=info.st_ino, st_mode=info.st_mode,
                                         st_size=info.st_size, st_mtime_ns=info.st_mtime_ns + 7,
                                         st_ctime_ns=info.st_ctime_ns + 11)

        with mock.patch.object(consumer.os, "fstat", side_effect=different_api_times):
            actual, raw = reader.read(file, consumer.MAX_METRICS)
        reader.finish()
        self.assertEqual(actual["sha256"], hashlib.sha256(raw).hexdigest())

    def test_cli_returns_machine_json_and_nonzero_on_failure(self):
        command = [sys.executable, str(ROOT / "tools/verify_render.py")]
        good = subprocess.run(command + [str(self.base / "manifest.json")], capture_output=True, check=False)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(json.loads(good.stdout)["status"], "verified_retained_bundle")
        directory, manifest = self.clone()
        manifest["status"] = "failed"
        self.save(directory, manifest)
        for args in ([str(directory)], [], ["--unknown"]):
            with self.subTest(args=args):
                bad = subprocess.run(command + args, capture_output=True, check=False)
                self.assertNotEqual(bad.returncode, 0)
                self.assertEqual(json.loads(bad.stdout)["status"], "failed")
                self.assertIn("error", json.loads(bad.stdout))


if __name__ == "__main__":
    unittest.main(verbosity=2)
