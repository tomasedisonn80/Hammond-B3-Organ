#!/usr/bin/env python3
"""Actual PCM checks of the separate, synthetic nominal-console catalog.

CTest supplies HAMMOND_RENDER_EXECUTABLE and HAMMOND_TEST_PROFILE. Direct use:
  python3 tests/test_console_catalog.py --renderer build/hammond_render \
      --profile build/nominal.b3p
All render prerequisites are required; no audio check is skipped.
"""

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
import unittest
import wave


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "examples/fixtures/console"
CATALOG = FIXTURES / "console-catalog-v1.json"
PCM = 1.0 / 32768.0
RENDERER_OVERRIDE = None
PROFILE_OVERRIDE = None
IDS = {"console-travel-v1", "console-percussion-legato-v1", "console-routing-mask-v1"}
BOUNDS = {"fixture_count": 3, "sample_rate": 48000, "max_frames": 42000,
          "max_score_bytes": 4096, "max_events": 32, "max_events_at_frame": 8}
MODELS = {"source": "ideal-shared-sine-v1", "contacts": "nominal-linear-travel-v1",
          "percussion": "shared-readiness-v1"}
METRICS = {"status", "model", "render_schema_version", "contact_model",
           "percussion_model", "evidence_status", "profile_id", "authoring_sha256",
           "sample_rate", "block_size", "frames", "seed", "channels", "sample_format",
           "peak", "rms", "clipped_frames", "clipped_channel_samples",
    "pedal_routing_model", "pedal_voice_model", "pedal_gain_law", "pedal_contact_model",
    "pedal_map_id", "pedal_map_raw_sha256", "pedal_map_canonical_sha256",
    "pedal_reference_a_sha256", "pedal_reference_b_sha256", "pedal_mixture_matrix",
    "pedal_mixture_denominator", "pedal_gain_denominator", "pedal_weight_policy",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("non-JSON numeric value: " + value)


def read_bounded(path, maximum):
    require(path.is_file() and not path.is_symlink(), "not a regular nonsymlink file: " + str(path))
    require(path.stat().st_size <= maximum, "file exceeds bound: " + str(path))
    with path.open("rb") as stream:
        raw = stream.read(maximum + 1)
    require(len(raw) <= maximum, "read exceeds bound: " + str(path))
    return raw


def decode_json(raw):
    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)


def integer(value, low, high):
    return type(value) is int and low <= value <= high


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def prerequisite(override, environment, fallback):
    configured = override if override is not None else os.environ.get(environment)
    path = Path(configured) if configured is not None else fallback
    if not path.is_file():
        raise RuntimeError(f"Missing prerequisite {environment}: {path}. Build hammond_render "
                           "and nominal.b3p, then set the environment or --renderer/--profile. "
                           "No console audio check was run.")
    return path.resolve()


def validate_score(raw, fixture):
    lines = raw.decode("ascii").splitlines()
    events = []
    for line in lines:
        require(len(line) <= 256, "score line exceeds catalog bound")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = line.split()
        require(len(fields) == 5, "score requires five fields")
        frame, kind, manual, index, value = fields
        require(re.fullmatch(r"[0-9]+", frame) is not None and
                re.fullmatch(r"[0-9]+", index) is not None, "unsigned event field required")
        frame, index, value = int(frame), int(index), float(value)
        require(0 <= frame < fixture["frames"] and math.isfinite(value), "event range invalid")
        require(manual in ("upper", "lower"), "invalid manual")
        require(not events or frame >= events[-1][0], "unsorted events")
        if kind == "note_on":
            valid = 36 <= index <= 96 and value.is_integer() and 0 <= value <= 127
        elif kind == "note_off":
            valid = 36 <= index <= 96 and value == 0
        elif kind in ("drawbar", "bank_drawbar"):
            valid = index < (9 if kind == "drawbar" else 18) and value.is_integer() and 0 <= value <= 8
        elif kind == "expression":
            valid = index == 0 and 0 <= value <= 1
        elif kind == "select_bank":
            valid = index == 0 and value in (0, 1)
        elif kind in ("cancel", "all_notes_off"):
            valid = index == 0 and value == 0
        elif kind == "percussion":
            valid = manual == "upper" and index < 4 and value in (0, 1)
        else:
            valid = False
        require(valid, "invalid catalog event payload")
        events.append((frame, kind, manual, index, value))
    require(0 < len(events) <= BOUNDS["max_events"], "event count bound")
    require(max(Counter(event[0] for event in events).values()) <= BOUNDS["max_events_at_frame"],
            "same-frame event bound")
    require(events[0] == (0, "expression", "upper", 0, 0.5), "explicit half expression required")
    return events


def validate_catalog(catalog, profile):
    require(set(catalog) == {"schema_version", "catalog_id", "evidence_status", "models", "profile",
                             "provenance", "bounds", "conventions", "tolerances", "fixtures"},
            "unexpected catalog keys")
    require(type(catalog["schema_version"]) is int and catalog["schema_version"] == 1,
            "catalog schema version")
    require(catalog["catalog_id"] == "nominal-console-fixtures-v1" and
            catalog["evidence_status"] == "synthetic-unmeasured", "catalog identity")
    require(catalog["models"] == MODELS and catalog["bounds"] == BOUNDS, "models/bounds changed")
    identity = catalog["profile"]
    require(identity == {
        "id": "nominal-unmeasured-v1",
        "authoring_path": "data/profiles/nominal-unmeasured-v1.json",
        "authoring_sha256": "49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83",
        "compiled_sha256": "b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f"},
        "bound nominal source profile changed")
    authoring = decode_json(read_bounded(ROOT / identity["authoring_path"], 256 * 1024))
    canonical = json.dumps(authoring, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf-8")
    require(hashlib.sha256(canonical).hexdigest() == identity["authoring_sha256"],
            "canonical authoring hash mismatch")
    require(hashlib.sha256(read_bounded(profile, 128 * 1024)).hexdigest() == identity["compiled_sha256"],
            "compiled profile hash mismatch")
    fixtures = catalog["fixtures"]
    require(type(fixtures) is list and len(fixtures) == 3 and
            {item["id"] for item in fixtures} == IDS, "fixture identities/count")
    require(catalog["tolerances"] == {"component_peak_abs": 0.00004, "phase_vector_abs": 0.006,
                                      "residual_pcm_max": 2.0, "meaningful_pcm_peak_min": 64},
            "reviewed tolerances changed")
    require({item["events"]["path"] for item in fixtures} ==
            {path.name for path in FIXTURES.glob("*.events")}, "unlisted console event file")
    for item in fixtures:
        require(set(item) == {"id", "purpose", "events", "sample_rate", "frames", "seed",
                              "block_size", "registration", "controls", "expectations"},
                "unexpected fixture keys")
        require(integer(item["sample_rate"], 48000, 48000) and
                integer(item["frames"], 1, BOUNDS["max_frames"]) and
                integer(item["seed"], 0, 2**64 - 1) and item["block_size"] == 127,
                "fixture timing bounds")
        require(re.fullmatch(r"[0-8]{9}", item["registration"]) is not None, "registration")
        controls = item["controls"]
        require(set(controls) == {"contacts", "percussion", "percussion_volume", "percussion_decay"}
                and controls["contacts"] == "nominal" and controls["percussion"] in ("off", "second", "third")
                and controls["percussion_volume"] in ("normal", "soft")
                and controls["percussion_decay"] in ("slow", "fast"), "console controls")
        record = item["events"]
        require(set(record) == {"path", "sha256"} and record["path"] == item["id"] + ".events",
                "confined event filename")
        raw = read_bounded(FIXTURES / record["path"], BOUNDS["max_score_bytes"])
        require(hashlib.sha256(raw).hexdigest() == record["sha256"], "score hash mismatch")
        validate_score(raw, item)
        expected = item["expectations"]
        require(expected["clipped_frames"] == 0 and finite(expected["float_peak_max"])
                and 0 < expected["float_peak_max"] <= .046, "peak/clipping expectations")
        for span in expected["silence_spans"] + expected["audible_spans"] + [f["span"] for f in expected["fits"]]:
            require(type(span) is list and len(span) == 2 and integer(span[0], 0, item["frames"] - 1)
                    and integer(span[1], span[0] + 1, item["frames"]), "bounded half-open span")
        for fit in expected["fits"]:
            require(1 <= len(fit["tones"]) <= 2, "bounded fit components")
            for tone in fit["tones"]:
                require(integer(tone["tone_id"], 1, 91) and finite(tone["frequency_hz"])
                        and 0 < tone["frequency_hz"] < 24000 and finite(tone["peak_amplitude"])
                        and 0 <= tone["peak_amplitude"] <= .045 and
                        tone["envelope"] in ("unity", "legato_readiness", "routing_readiness"),
                        "tone regression parameters")


def envelope(frame, kind, fixture):
    """Closed-form elapsed-time oracle, independent of the engine's recurrence."""
    if kind == "unity":
        return 1.0
    data = fixture["expectations"]["readiness"]
    decay = fixture["sample_rate"] * data["decay_seconds"]
    recovery = fixture["sample_rate"] * data["recovery_seconds"]
    start = data["first_detector_make"]
    if kind == "legato_readiness":
        stop, restart = data["detector_break"], data["second_detector_make"]
    else:
        stop, restart = data["route_off_frame"], data["route_on_frame"]
    if frame < start:
        return 1.0
    if frame < stop:
        return math.exp(-(frame - start) / decay)
    at_stop = math.exp(-(stop - start) / decay)
    if frame < restart:
        return 1.0 - (1.0 - at_stop) * math.exp(-(frame - stop) / recovery)
    at_restart = 1.0 - (1.0 - at_stop) * math.exp(-(restart - stop) / recovery)
    return at_restart * math.exp(-(frame - restart) / decay)


def solve(matrix, vector):
    """Small independent least-squares normal solve with partial pivoting."""
    count = len(vector)
    rows = [list(row) + [value] for row, value in zip(matrix, vector)]
    for column in range(count):
        pivot = max(range(column, count), key=lambda i: abs(rows[i][column]))
        require(abs(rows[pivot][column]) > 1e-10, "singular sinusoidal fit")
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        rows[column] = [value / divisor for value in rows[column]]
        for row in range(count):
            if row != column:
                multiplier = rows[row][column]
                rows[row] = [a - multiplier * b for a, b in zip(rows[row], rows[column])]
    return [row[-1] for row in rows]


def fit_components(samples, fixture, specification):
    tones = specification["tones"]
    count = 2 * len(tones)
    matrix, vector, observations = [[0.0] * count for _ in range(count)], [0.0] * count, []
    for frame in range(*specification["span"]):
        row = []
        for tone in tones:
            gain = envelope(frame, tone["envelope"], fixture)
            angle = math.tau * tone["frequency_hz"] * frame / fixture["sample_rate"]
            row.extend((gain * math.sin(angle), gain * math.cos(angle)))
        value = samples[frame] * PCM
        for i in range(count):
            vector[i] += row[i] * value
            for j in range(count):
                matrix[i][j] += row[i] * row[j]
        observations.append((row, value))
    coefficients = solve(matrix, vector)
    residual = max(abs(sum(a * b for a, b in zip(row, coefficients)) - value)
                   for row, value in observations) / PCM
    return [tuple(coefficients[i:i + 2]) for i in range(0, count, 2)], residual


class ConsoleCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.renderer = prerequisite(RENDERER_OVERRIDE, "HAMMOND_RENDER_EXECUTABLE",
                                    ROOT / "build" / ("hammond_render.exe" if os.name == "nt" else "hammond_render"))
        cls.profile = prerequisite(PROFILE_OVERRIDE, "HAMMOND_TEST_PROFILE", ROOT / "build/nominal.b3p")
        cls.catalog = decode_json(read_bounded(CATALOG, 64 * 1024))
        validate_catalog(cls.catalog, cls.profile)
        cls.temporary = tempfile.TemporaryDirectory(prefix="hammond-console-catalog-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.rendered = {}
        for fixture in cls.catalog["fixtures"]:
            renders = []
            for block in (1, fixture["block_size"], 1024):
                output = Path(cls.temporary.name) / (fixture["id"] + f"-{block}.wav")
                command = [str(cls.renderer), "--profile", str(cls.profile), "--output", str(output),
                           "--events", str(FIXTURES / fixture["events"]["path"]),
                           "--frames", str(fixture["frames"]), "--sample-rate", str(fixture["sample_rate"]),
                           "--block-size", str(block), "--seed", str(fixture["seed"]),
                           "--drawbars", fixture["registration"]]
                for name, value in fixture["controls"].items():
                    command.extend(("--" + name.replace("_", "-"), value))
                command.append("--fail-on-clip")
                result = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
                require(result.returncode == 0, f"actual render failed: {command}\n{result.stdout}\n{result.stderr}")
                require(result.stderr == "", "unexpected renderer stderr: " + result.stderr)
                raw = read_bounded(output, 44 + 4 * BOUNDS["max_frames"])
                with wave.open(str(output), "rb") as wav:
                    require(wav.getparams()[:4] == (2, 2, fixture["sample_rate"], fixture["frames"])
                            and wav.getcomptype() == "NONE", "WAV format mismatch")
                    pcm = wav.readframes(fixture["frames"])
                channels = struct.unpack("<" + "h" * (len(pcm) // 2), pcm)
                require(channels[::2] == channels[1::2], "dry channels differ")
                renders.append((block, raw, decode_json(result.stdout), channels[::2]))
            cls.rendered[fixture["id"]] = renders

    def test_catalog_and_actual_pcm_contracts(self):
        for fixture in self.catalog["fixtures"]:
            with self.subTest(fixture=fixture["id"]):
                renders = self.rendered[fixture["id"]]
                first_raw = renders[0][1]
                for block, raw, metrics, samples in renders:
                    self.assertEqual(raw, first_raw, "exact same-build partition WAV identity")
                    self.assertEqual(len(raw), 44 + fixture["frames"] * 4)
                    self.assertEqual(set(metrics), METRICS)
                    self.assertEqual(metrics["status"], "ok")
                    self.assertEqual(metrics["render_schema_version"], 3)
                    self.assertIs(type(metrics["render_schema_version"]), int)
                    self.assertEqual(metrics["model"], MODELS["source"])
                    self.assertEqual(metrics["contact_model"], MODELS["contacts"])
                    self.assertEqual(metrics["percussion_model"], MODELS["percussion"])
                    self.assertEqual(metrics["evidence_status"], "unmeasured")
                    for field in ("profile_id", "authoring_sha256"):
                        identity_key = "id" if field == "profile_id" else field
                        self.assertEqual(metrics[field], self.catalog["profile"][identity_key])
                    for field in ("frames", "sample_rate", "seed"):
                        self.assertEqual(metrics[field], fixture[field])
                    self.assertEqual(metrics["block_size"], block)
                    self.assertEqual((metrics["channels"], metrics["sample_format"]), (2, "pcm_s16le"))
                    self.assertEqual((metrics["clipped_frames"], metrics["clipped_channel_samples"]), (0, 0))
                    self.assertTrue(all(finite(metrics[field]) for field in ("peak", "rms")))
                    self.assertLessEqual(metrics["peak"], fixture["expectations"]["float_peak_max"])
                    self.assertGreater(metrics["rms"], 0)
                    pcm_peak = max(abs(value) for value in samples) * PCM
                    pcm_rms = math.sqrt(math.fsum((value * PCM)**2 for value in samples) / len(samples))
                    self.assertLessEqual(abs(pcm_peak - metrics["peak"]), PCM)
                    self.assertLessEqual(abs(pcm_rms - metrics["rms"]), PCM)

    def test_exact_silence_and_meaningful_audible_windows(self):
        for fixture in self.catalog["fixtures"]:
            samples = self.rendered[fixture["id"]][0][3]
            for start, stop in fixture["expectations"]["silence_spans"]:
                with self.subTest(fixture=fixture["id"], silence=(start, stop)):
                    self.assertTrue(all(value == 0 for value in samples[start:stop]))
            for start, stop in fixture["expectations"]["audible_spans"]:
                with self.subTest(fixture=fixture["id"], audible=(start, stop)):
                    self.assertGreater(max(abs(value) for value in samples[start:stop]),
                                       self.catalog["tolerances"]["meaningful_pcm_peak_min"])

    def test_contact_edges_use_declared_travel_not_block_boundaries(self):
        fixture = next(item for item in self.catalog["fixtures"] if item["id"] == "console-travel-v1")
        samples = self.rendered[fixture["id"]][0][3]
        for edge in fixture["expectations"]["contact_edges"]:
            with self.subTest(manual=edge["manual"]):
                # These independent analytic values use the nominal 8-foot contact,
                # and neither an engine helper nor a recurrence copied from it.
                make = edge["press_frame"] + math.ceil(.32 * 48000 * .008)
                release = edge["release_frame"] + math.ceil((1.0 - .24) * 48000 * .012)
                self.assertEqual((make, release), (edge["make_frame"], edge["break_frame"]))
                self.assertEqual(samples[make - 1], 0)
                self.assertNotEqual(samples[make], 0)
                self.assertNotEqual(samples[release - 1], 0)
                self.assertEqual(samples[release], 0)

    def test_component_levels_closed_form_readiness_and_continuous_phase(self):
        tolerances = self.catalog["tolerances"]
        for fixture in self.catalog["fixtures"]:
            samples = self.rendered[fixture["id"]][0][3]
            phases = {}
            for specification in fixture["expectations"]["fits"]:
                with self.subTest(fixture=fixture["id"], span=specification["span"]):
                    components, residual = fit_components(samples, fixture, specification)
                    self.assertLessEqual(residual, tolerances["residual_pcm_max"])
                    for tone, pair in zip(specification["tones"], components):
                        amplitude = math.hypot(*pair)
                        self.assertLessEqual(abs(amplitude - tone["peak_amplitude"]),
                                             tolerances["component_peak_abs"])
                        if tone["peak_amplitude"] > 0:
                            direction = tuple(value / amplitude for value in pair)
                            if tone["tone_id"] in phases:
                                previous = phases[tone["tone_id"]]
                                self.assertLessEqual(math.hypot(direction[0] - previous[0],
                                                               direction[1] - previous[1]),
                                                     tolerances["phase_vector_abs"])
                            else:
                                phases[tone["tone_id"]] = direction


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--renderer")
    parser.add_argument("--profile")
    options, remaining = parser.parse_known_args()
    RENDERER_OVERRIDE, PROFILE_OVERRIDE = options.renderer, options.profile
    unittest.main(argv=[sys.argv[0], *remaining])
