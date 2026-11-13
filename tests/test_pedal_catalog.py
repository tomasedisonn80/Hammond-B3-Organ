#!/usr/bin/env python3
"""Independent actual-PCM acceptance for four nominal pedal fixtures.

No production routing, mixture, source PRNG or evidence producer is imported.
CTest supplies HAMMOND_RENDER_EXECUTABLE and HAMMOND_TEST_PROFILE; direct use:
  python3 tests/test_pedal_catalog.py --renderer build/hammond_render \
      --profile build/nominal.b3p
Missing render prerequisites fail explicitly; no audio checks are skipped.
"""

import argparse
from collections import Counter
import copy
import csv
from fractions import Fraction
import hashlib
import io
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
FIXTURES = ROOT / "examples/fixtures/pedals"
CATALOG = FIXTURES / "pedal-catalog-v1.json"
PCM = 1.0 / 32768.0
RENDERER_OVERRIDE = None
PROFILE_OVERRIDE = None
IDS = {"pedal-mixtures-v1", "pedal-shared-source-v1", "pedal-held-routing-v1",
       "pedal-phrase-v1"}
BOUNDS = {"fixture_count": 4, "sample_rate": 48000, "max_frames": 144000,
          "max_score_bytes": 8192, "max_events": 64, "max_events_at_frame": 12,
          "max_fits_per_fixture": 8, "max_fit_frames": 24000,
          "max_fit_tones": 24, "fit_stride": 4}
TOLERANCES = {"component_peak_abs": .00004, "phase_vector_abs": .006,
              "residual_pcm_max": 2.0, "meaningful_pcm_peak_min": 64}
MODELS = {"source": "ideal-shared-sine-v1", "manual_contacts": "ideal-contacts-v1",
          "percussion": "shared-readiness-v1", "pedal_routing": "linear-pedal-bus-reference-v1",
          "pedal_voice": "nominal-static-pedal-mixture-v1", "pedal_gain": "linear-pedal-position-v1",
          "pedal_contacts": "ideal-eight-contact-pedal-v1"}
PROFILE_IDENTITY = {
    "id": "nominal-unmeasured-v1",
    "authoring_path": "data/profiles/nominal-unmeasured-v1.json",
    "authoring_sha256": "49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83",
    "compiled_sha256": "b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f",
}
MAP_RAW = "58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd"
MAP_CANONICAL = "7b2631a0c7d55a18f8225d4ee420e472c23b9f2809eec69865474eafce6f5fb2"
PEDAL_CSV_HASH = "b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1"
MANUAL_CSV_HASH = "23ade40234db10d0bf99cd5acf9ee0ff29e4656e847e61409ebe8717f7cb9dc6"
PARAMETER_HASH = "13ba488bec90154c960c3fd700dc4a774aff5664caf5d68472821493f22d1cad"
# Original fixed engineering fixture from PEDAL_INTEGRATION_CONTRACT, not
# recovered electrical values. Contact-to-bus membership follows atlas p.140.
NUMERATORS = ((4, 2, 1, 1), (1, 4, 2, 1))
CONTACT_BUSES = (0, 0, 1, 1, 2, 2, 3, 3)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, low, high):
    return type(value) is int and low <= value <= high


def exact(value, expected, label):
    # JSON encodings distinguish 1 from true and 8 from 8.0 in identity fields.
    require(canonical(value) == canonical(expected), label)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_bounded(path, maximum):
    require(path.is_file() and not path.is_symlink(), "expected regular nonsymlink file: " + str(path))
    require(path.stat().st_size <= maximum, "file exceeds bound: " + str(path))
    with path.open("rb") as source:
        raw = source.read(maximum + 1)
    require(len(raw) <= maximum, "read exceeds bound: " + str(path))
    return raw


def decode_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    def constant(token):
        raise ValueError("non-JSON number: " + token)

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def prerequisites(override, variable, fallback):
    value = override if override is not None else os.environ.get(variable)
    path = Path(value) if value is not None else fallback
    if not path.is_file():
        raise RuntimeError(f"Missing {variable}: {path}. Build hammond_render and nominal.b3p; "
                           "no pedal catalog audio check was run.")
    return path.resolve()


def read_map(path, kind):
    pedal = kind == "pedal"
    count, width = (25, 8) if pedal else (61, 9)
    rows = list(csv.reader(io.StringIO(read_bounded(path, 16384).decode("ascii"))))
    exact(rows[0], [kind if pedal else "key"] +
          [("c" if pedal else "d") + str(i) for i in range(1, width + 1)], "CSV header")
    require(len(rows) == count + 1, "CSV row count")
    result = {}
    for expected, row in enumerate(rows[1:], 1):
        require(len(row) == width + 1 and row[0] == str(expected), "CSV row identity")
        values = []
        for cell in row[1:]:
            if cell == "":
                require(pedal, "manual disconnection is unsupported")
                values.append(None)
            else:
                require(re.fullmatch(r"[1-9][0-9]?", cell) is not None and 1 <= int(cell) <= 91,
                        "CSV source domain")
                values.append(int(cell))
        result[expected] = values
    return result


def validate_score(raw, fixture):
    events = []
    for line in raw.decode("ascii").splitlines():
        require(len(line) <= 256, "score line bound")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = line.split()
        require(len(fields) == 5, "score field count")
        frame, kind, manual, index, value = fields
        require(re.fullmatch(r"[0-9]{1,12}", frame) is not None and
                re.fullmatch(r"[0-9]{1,3}", index) is not None, "unsigned score fields")
        frame, index, value = int(frame), int(index), float(value)
        require(0 <= frame < fixture["frames"] and math.isfinite(value), "event range")
        require(manual in ("upper", "lower") and (not events or frame >= events[-1][0]),
                "manual or chronology")
        if kind in ("note_on", "note_off"):
            valid = 36 <= index <= 96 and (0 <= value <= 127 and value.is_integer()
                                          if kind == "note_on" else value == 0)
        elif kind in ("pedal_on", "pedal_off"):
            valid = manual == "lower" and 1 <= index <= 25 and (
                0 <= value <= 127 and value.is_integer() if kind == "pedal_on" else value == 0)
        elif kind in ("drawbar", "bank_drawbar", "pedal_drawbar"):
            maximum = {"drawbar": 8, "bank_drawbar": 17, "pedal_drawbar": 1}[kind]
            valid = index <= maximum and 0 <= value <= 8 and value.is_integer()
            valid = valid and (kind != "pedal_drawbar" or manual == "lower")
        elif kind == "expression":
            valid = index == 0 and 0 <= value <= 1
        elif kind == "select_bank":
            valid = index == 0 and value in (0, 1)
        elif kind in ("cancel", "all_notes_off", "pedal_all_notes_off"):
            valid = index == 0 and value == 0 and (kind != "pedal_all_notes_off" or manual == "lower")
        else:
            valid = False
        require(valid, "invalid catalog event payload")
        events.append((frame, kind, manual, index, value))
    require(0 < len(events) <= BOUNDS["max_events"], "event count bound")
    require(max(Counter(event[0] for event in events).values()) <= BOUNDS["max_events_at_frame"],
            "same-frame event bound")
    require(events[0] == (0, "expression", "upper", 0, fixture["expression"]),
            "explicit initial expression")
    return events


def expected_components(fixture, specification, pedal_map, manual_map, profile,
                        numerators=NUMERATORS, deduplicate=False):
    """Independent integer contact sum; no production map formula or matrix import."""
    coefficients = {}
    for pedal in specification["pedals"]:
        seen = set()
        for contact, tone in enumerate(pedal_map[pedal]):
            if tone is None or (deduplicate and tone in seen):
                continue
            seen.add(tone)
            bus = CONTACT_BUSES[contact]
            numerator = sum(position * numerators[mixture][bus]
                            for mixture, position in enumerate(specification["positions"]))
            coefficients[tone] = coefficients.get(tone, Fraction()) + Fraction(numerator, 64)
    gains = profile["drawbar_gains"]["values"]
    for branch in specification["manual_branches"]:
        # Manual MIDI36 is physical playing key1. CSV selects the route literally.
        tone = manual_map[branch["midi_note"] - 35][branch["drawbar_index"]]
        coefficients[tone] = float(coefficients.get(tone, 0.0)) + gains[branch["position"]]
    multiplier = fixture["expression"] * profile["output_gain"]["value"]
    sources = {source["tone_id"]: source for source in profile["sources"]}
    return {tone: float(value) * multiplier * sources[tone]["peak_amplitude"]
            for tone, value in sorted(coefficients.items()) if value != 0}


def validate_catalog(catalog, compiled):
    require(set(catalog) == {"schema_version", "catalog_id", "evidence_status", "models", "profile",
                             "routing", "control_model", "provenance", "bounds", "tolerances",
                             "conventions", "fixtures"}, "catalog fields")
    exact(catalog["schema_version"], 1, "catalog version")
    require(catalog["catalog_id"] == "nominal-pedal-fixtures-v1" and
            catalog["evidence_status"] == "synthetic-unmeasured", "catalog identity")
    for key, value in (("models", MODELS), ("profile", PROFILE_IDENTITY), ("bounds", BOUNDS),
                       ("tolerances", TOLERANCES)):
        exact(catalog[key], value, "catalog " + key)
    profile = decode_json(read_bounded(ROOT / PROFILE_IDENTITY["authoring_path"], 256 * 1024))
    require(digest(canonical(profile)) == PROFILE_IDENTITY["authoring_sha256"] and
            digest(read_bounded(compiled, 128 * 1024)) == PROFILE_IDENTITY["compiled_sha256"],
            "source profile identities")
    references = [{"path": "data/references/review-" + review + "-" + kind + ".csv",
                   "sha256": PEDAL_CSV_HASH if kind == "pedal" else MANUAL_CSV_HASH}
                  for kind in ("pedal", "manual") for review in ("a", "b")]
    exact(catalog["routing"], {"map_id": "atlas-derived-b3-c3-pedal-v1", "map_path": "data/pedal-map.json",
                              "map_raw_sha256": MAP_RAW, "map_canonical_sha256": MAP_CANONICAL,
                              "references": references}, "routing identity")
    raw_map = read_bounded(ROOT / "data/pedal-map.json", 256 * 1024)
    require(digest(raw_map) == MAP_RAW and digest(canonical(decode_json(raw_map))) == MAP_CANONICAL,
            "raw/canonical map identity")
    for reference in references:
        require(digest(read_bounded(ROOT / reference["path"], 16384)) == reference["sha256"],
                "reference CSV identity")
    maps = {kind: [read_map(ROOT / ("data/references/review-" + review + "-" + kind + ".csv"), kind)
                   for review in ("a", "b")] for kind in ("pedal", "manual")}
    require(all(pair[0] == pair[1] for pair in maps.values()), "independent CSV readings disagree")
    pedal_map, manual_map = maps["pedal"][0], maps["manual"][0]
    require(sum(tone is not None for row in pedal_map.values() for tone in row) == 195,
            "195 connected positions required")
    require(sum(tone is None for row in pedal_map.values() for tone in row) == 5,
            "five explicit disconnections required")
    expected_control = {"registry_schema_version": 3,
                        "registry_model": "exclusive-ab-percussion-pedal-console-v3",
                        "parameter_count": 45, "parameter_records_canonical_sha256": PARAMETER_HASH,
                        "pedal_parameters": [{"id": 16384, "path": "pedal.drawbar.mixture1"},
                                             {"id": 16385, "path": "pedal.drawbar.mixture2"}],
                        "bus_order": ["Brown", "Red", "Orange", "Yellow"],
                        "mixture_numerators": [list(row) for row in NUMERATORS],
                        "mixture_denominator": 8, "position_gain_denominator": 8,
                        "weight_policy": "all-200-unit-positive-v1"}
    exact(catalog["control_model"], expected_control, "control identities")
    registry = decode_json(read_bounded(ROOT / "data/parameter-registry.json", 128 * 1024))
    require(registry["schema_version"] == 3 and registry["model"] == expected_control["registry_model"]
            and len(registry["parameters"]) == 45 and digest(canonical(registry["parameters"])) == PARAMETER_HASH,
            "registry record identities")
    provenance = catalog["provenance"]
    require(set(provenance) == {"evidence_class", "source_document", "source_sha256", "source_pages",
                                "uncertainty", "reason"} and provenance["evidence_class"] == "proposed"
            and provenance["source_document"] == "Hammond_B3_Leslie_Research_Atlas_500pp.pdf"
            and provenance["source_sha256"] == "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769"
            and provenance["source_pages"] == [139, 140, 142, 144, 447]
            and provenance["uncertainty"] is None and type(provenance["reason"]) is str
            and len(provenance["reason"]) > 80, "nominal evidence provenance")
    require(type(catalog["conventions"]) is dict and len(catalog["conventions"]) == 8
            and all(type(value) is str and 1 <= len(value) <= 1024
                    for value in catalog["conventions"].values()), "catalog conventions")
    fixtures = catalog["fixtures"]
    require(type(fixtures) is list and len(fixtures) == 4 and {f["id"] for f in fixtures} == IDS,
            "fixture identities")
    require({f["events"]["path"] for f in fixtures} == {p.name for p in FIXTURES.glob("*.events")},
            "catalog event inventory")
    for fixture in fixtures:
        require(set(fixture) == {"id", "purpose", "events", "sample_rate", "frames", "seed", "block_size",
                                 "registration", "pedal_registration", "controls", "expression", "expectations"},
                "fixture fields")
        require(integer(fixture["sample_rate"], 48000, 48000) and integer(fixture["frames"], 1, 144000)
                and integer(fixture["seed"], 0, 2**64 - 1) and fixture["block_size"] == 127,
                "fixture timing")
        require(re.fullmatch(r"[0-8]{9}", fixture["registration"]) is not None and
                re.fullmatch(r"[0-8]{2}", fixture["pedal_registration"]) is not None,
                "fixture registrations")
        exact(fixture["controls"], {"contacts": "ideal", "percussion": "off",
                                    "percussion_volume": "normal", "percussion_decay": "slow"},
              "fixture console model")
        require(type(fixture["expression"]) is float and fixture["expression"] in (.5, .75), "expression")
        require(set(fixture["events"]) == {"path", "sha256"}, "score identity fields")
        require(fixture["events"]["path"] == fixture["id"] + ".events", "confined score path")
        raw = read_bounded(FIXTURES / fixture["events"]["path"], BOUNDS["max_score_bytes"])
        require(digest(raw) == fixture["events"]["sha256"], "score identity")
        events = validate_score(raw, fixture)
        expectations = fixture["expectations"]
        required = {"clipped_frames", "float_peak_max", "silence_spans", "audible_spans", "fits"}
        optional = {"initially_audible_reference"} if fixture["id"] == "pedal-held-routing-v1" else set()
        require(set(expectations) == required | optional, "expectation fields")
        require(type(expectations["clipped_frames"]) is int and expectations["clipped_frames"] == 0
                and type(expectations["float_peak_max"]) is float
                and 0 < expectations["float_peak_max"] <= .103, "peak/clipping bounds")
        for name in ("silence_spans", "audible_spans"):
            require(type(expectations[name]) is list and 1 <= len(expectations[name]) <= 4, "span count")
            for span in expectations[name]:
                require(type(span) is list and len(span) == 2 and
                        all(integer(value, 0, fixture["frames"]) for value in span) and span[0] < span[1],
                        "span domain")
        fits = expectations["fits"]
        require(type(fits) is list and 1 <= len(fits) <= BOUNDS["max_fits_per_fixture"], "fit count")
        for specification in fits:
            require(set(specification) == {"span", "pedals", "positions", "manual_branches"}, "fit fields")
            start, end = specification["span"]
            require(integer(start, 0, fixture["frames"]) and integer(end, 0, fixture["frames"])
                    and 2400 <= end - start <= BOUNDS["max_fit_frames"], "fit frame bound")
            require(not any(start < event[0] < end for event in events), "fit must not cross a score event")
            require(type(specification["pedals"]) is list and 1 <= len(specification["pedals"]) <= 2
                    and len(set(specification["pedals"])) == len(specification["pedals"])
                    and all(integer(pedal, 1, 25) for pedal in specification["pedals"]), "fit pedal domain")
            require(type(specification["positions"]) is list and len(specification["positions"]) == 2
                    and all(integer(position, 0, 8) for position in specification["positions"]), "fit positions")
            require(type(specification["manual_branches"]) is list and len(specification["manual_branches"]) <= 8,
                    "manual branch count")
            for branch in specification["manual_branches"]:
                require(set(branch) == {"manual", "midi_note", "drawbar_index", "position"}
                        and branch["manual"] in ("upper", "lower") and integer(branch["midi_note"], 36, 96)
                        and integer(branch["drawbar_index"], 0, 8) and integer(branch["position"], 1, 8),
                        "manual branch domain")
            require(1 <= len(expected_components(fixture, specification, pedal_map, manual_map, profile))
                    <= BOUNDS["max_fit_tones"], "fit component bound")
        if optional:
            exact(expectations["initially_audible_reference"],
                  {"pedal_registration": "40", "identical_suffix_start": 4800}, "unmute counterfactual")
    return profile, pedal_map, manual_map


def solve(matrix, vector):
    """Small generic normal-equation solve; partial pivoting, no DSP code reuse."""
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


def fit_components(samples, span, tones, profile, sample_rate):
    frequencies = {source["tone_id"]: source["frequency_hz"] for source in profile["sources"]}
    angular = [math.tau * frequencies[tone] / sample_rate for tone in tones]
    count = 2 * len(tones)
    matrix, vector = [[0.0] * count for _ in range(count)], [0.0] * count

    def basis(frame):
        row = []
        for increment in angular:
            angle = increment * frame
            row.extend((math.sin(angle), math.cos(angle)))
        return row

    # Subsample only the least-squares construction, never the residual gate.
    # These fixtures remain below the reduced 6kHz Nyquist boundary.
    require(max(frequencies[tone] for tone in tones) < sample_rate / (2 * BOUNDS["fit_stride"]),
            "fitting stride would alias a source")
    for frame in range(*span, BOUNDS["fit_stride"]):
        row, value = basis(frame), samples[frame] * PCM
        for i in range(count):
            vector[i] += row[i] * value
            for j in range(i + 1):
                matrix[i][j] += row[i] * row[j]
    for i in range(count):
        for j in range(i):
            matrix[j][i] = matrix[i][j]
    coefficients = solve(matrix, vector)
    residual = max(abs(sum(a * b for a, b in zip(basis(frame), coefficients))
                       - samples[frame] * PCM) for frame in range(*span)) / PCM
    return {tone: tuple(coefficients[2 * i:2 * i + 2]) for i, tone in enumerate(tones)}, residual


def check_peaks(actual, expected):
    require(set(actual) == set(expected), "fitted component inventory")
    for tone, pair in actual.items():
        require(abs(math.hypot(*pair) - expected[tone]) <= TOLERANCES["component_peak_abs"],
                f"component amplitude mismatch for ToneId {tone}")


class PedalCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.renderer = prerequisites(RENDERER_OVERRIDE, "HAMMOND_RENDER_EXECUTABLE",
                                     ROOT / "build" / ("hammond_render.exe" if os.name == "nt" else "hammond_render"))
        cls.compiled = prerequisites(PROFILE_OVERRIDE, "HAMMOND_TEST_PROFILE", ROOT / "build/nominal.b3p")
        cls.catalog = decode_json(read_bounded(CATALOG, 128 * 1024))
        cls.profile, cls.pedal_map, cls.manual_map = validate_catalog(cls.catalog, cls.compiled)
        cls.temporary = tempfile.TemporaryDirectory(prefix="hammond-pedal-catalog-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.render_count, cls.rendered_frames = 0, 0
        cls.rendered = {}
        for fixture in cls.catalog["fixtures"]:
            cls.rendered[fixture["id"]] = [cls.render(fixture, block) for block in (1, 127, 1024)]
        held = next(f for f in cls.catalog["fixtures"] if f["id"] == "pedal-held-routing-v1")
        cls.counterfactual = cls.render(held, 127, pedal="40", suffix="audible-from-start")
        cls.fitted = {}
        cls.fit_frames = cls.component_checks = cls.phase_checks = 0
        cls.maximum_peak_error = cls.maximum_residual = cls.maximum_phase_error = 0.0
        for fixture in cls.catalog["fixtures"]:
            histories, fitted = {}, []
            samples = cls.rendered[fixture["id"]][0][1]
            for specification in fixture["expectations"]["fits"]:
                expected = expected_components(fixture, specification, cls.pedal_map, cls.manual_map, cls.profile)
                actual, residual = fit_components(samples, specification["span"], list(expected),
                                                  cls.profile, fixture["sample_rate"])
                check_peaks(actual, expected)
                require(residual <= TOLERANCES["residual_pcm_max"], "full-window PCM residual")
                cls.maximum_residual = max(cls.maximum_residual, residual)
                cls.fit_frames += specification["span"][1] - specification["span"][0]
                for tone, pair in actual.items():
                    amplitude = math.hypot(*pair)
                    cls.maximum_peak_error = max(cls.maximum_peak_error, abs(amplitude - expected[tone]))
                    cls.component_checks += 1
                    unit = tuple(value / amplitude for value in pair)
                    if tone in histories:
                        error = max(abs(a - b) for a, b in zip(unit, histories[tone]))
                        require(error <= TOLERANCES["phase_vector_abs"], "shared phase discontinuity")
                        cls.maximum_phase_error = max(cls.maximum_phase_error, error)
                        cls.phase_checks += 1
                    else:
                        histories[tone] = unit
                fitted.append((specification, expected, actual))
            cls.fitted[fixture["id"]] = fitted

    @classmethod
    def render(cls, fixture, block, pedal=None, suffix=""):
        output = Path(cls.temporary.name) / (fixture["id"] + f"-{block}-{suffix}.wav")
        command = [str(cls.renderer), "--profile", str(cls.compiled), "--output", str(output),
                   "--events", str(FIXTURES / fixture["events"]["path"]), "--frames", str(fixture["frames"]),
                   "--sample-rate", str(fixture["sample_rate"]), "--block-size", str(block),
                   "--seed", str(fixture["seed"]), "--drawbars", fixture["registration"],
                   "--pedal-drawbars", pedal if pedal is not None else fixture["pedal_registration"]]
        for key, value in fixture["controls"].items():
            command.extend(("--" + key.replace("_", "-"), value))
        command.append("--fail-on-clip")
        result = subprocess.run(command, capture_output=True, text=True, timeout=45, check=False)
        require(result.returncode == 0 and not result.stderr and len(result.stdout) <= 16384,
                "actual render failed: " + str(command) + "\n" + result.stdout + result.stderr)
        metrics = decode_json(result.stdout)
        for key, value in {"render_schema_version": 3, "model": MODELS["source"],
                           "contact_model": MODELS["manual_contacts"], "percussion_model": MODELS["percussion"],
                           "pedal_routing_model": MODELS["pedal_routing"], "pedal_voice_model": MODELS["pedal_voice"],
                           "pedal_gain_law": MODELS["pedal_gain"], "pedal_contact_model": MODELS["pedal_contacts"],
                           "pedal_map_raw_sha256": MAP_RAW, "pedal_map_canonical_sha256": MAP_CANONICAL,
                           "pedal_reference_a_sha256": PEDAL_CSV_HASH, "pedal_reference_b_sha256": PEDAL_CSV_HASH,
                           "pedal_mixture_matrix": "4,2,1,1;1,4,2,1", "pedal_mixture_denominator": 8,
                           "pedal_gain_denominator": 8, "pedal_weight_policy": "all-200-unit-positive-v1",
                           "frames": fixture["frames"], "sample_rate": 48000, "block_size": block,
                           "seed": fixture["seed"], "clipped_frames": 0, "clipped_channel_samples": 0}.items():
            exact(metrics[key], value, "actual renderer model/identity: " + key)
        require(0 < metrics["peak"] <= fixture["expectations"]["float_peak_max"], "actual peak bound")
        raw = read_bounded(output, 4 * BOUNDS["max_frames"] + 4096)
        with wave.open(io.BytesIO(raw), "rb") as wav:
            require((wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), wav.getnframes(), wav.getcomptype())
                    == (2, 2, 48000, fixture["frames"], "NONE"), "WAV format")
            pcm = wav.readframes(fixture["frames"] + 1)
            require(len(pcm) == fixture["frames"] * 4, "PCM byte count")
        pairs = list(struct.iter_unpack("<hh", pcm))
        require(all(left == right for left, right in pairs), "dry channels differ")
        cls.render_count += 1
        cls.rendered_frames += fixture["frames"]
        return raw, [left for left, _ in pairs], metrics

    def test_actual_pcm_partition_silence_and_audibility(self):
        for fixture in self.catalog["fixtures"]:
            with self.subTest(fixture=fixture["id"]):
                renders = self.rendered[fixture["id"]]
                self.assertEqual(renders[0][0], renders[1][0])
                self.assertEqual(renders[0][0], renders[2][0])
                samples = renders[0][1]
                for start, end in fixture["expectations"]["silence_spans"]:
                    self.assertTrue(all(value == 0 for value in samples[start:end]))
                for start, end in fixture["expectations"]["audible_spans"]:
                    self.assertGreaterEqual(max(abs(value) for value in samples[start:end]),
                                            TOLERANCES["meaningful_pcm_peak_min"])

    def test_independent_components_and_shared_phase(self):
        self.assertEqual(sum(len(values) for values in self.fitted.values()), 19)
        self.assertGreater(self.component_checks, 150)
        self.assertGreater(self.phase_checks, 100)
        shared = self.fitted["pedal-shared-source-v1"]
        # Literal source13 collisions: two pedal1 paths, lower36/8-foot,
        # pedal13 Brown contact, then each authority is independently released.
        self.assertEqual([spec[1][13] for spec in shared],
                         [.015 * 3 / 8, .015 * (1 + 3 / 8), .015 * (1 + 5 / 8),
                          .015 * 5 / 8, .015 / 4])

    def test_initially_muted_hold_matches_unmuted_source_suffix(self):
        held = self.rendered["pedal-held-routing-v1"][1][1]
        reference = self.counterfactual[1]
        self.assertTrue(any(value != 0 for value in reference[:4800]))
        self.assertEqual(held[4800:], reference[4800:])

    def test_oracle_rejects_deduplicated_and_altered_mixture_models(self):
        fixture = next(f for f in self.catalog["fixtures"] if f["id"] == "pedal-mixtures-v1")
        specification, _, actual = self.fitted[fixture["id"]][0]
        wrong_duplicate = expected_components(fixture, specification, self.pedal_map,
                                             self.manual_map, self.profile, deduplicate=True)
        wrong_matrix = expected_components(fixture, specification, self.pedal_map,
                                          self.manual_map, self.profile,
                                          numerators=((3, 3, 1, 1), (1, 4, 2, 1)))
        for wrong in (wrong_duplicate, wrong_matrix):
            with self.assertRaisesRegex(ValueError, "component amplitude mismatch"):
                check_peaks(actual, wrong)

    def test_catalog_rejects_changed_identities_bounds_and_grammar(self):
        mutations = [(["schema_version"], True), (["models", "pedal_voice"], "calibrated-16ft"),
                     (["routing", "map_raw_sha256"], "0" * 64),
                     (["control_model", "mixture_denominator"], 8.0),
                     (["control_model", "pedal_parameters", 0, "id"], 16386),
                     (["tolerances", "component_peak_abs"], .01),
                     (["bounds", "max_fit_frames"], 10**9),
                     (["fixtures", 0, "events", "path"], "../escape.events"),
                     (["fixtures", 0, "events", "sha256"], "0" * 64),
                     (["fixtures", 0, "expectations", "fits", 0, "positions"], [9, 0]),
                     (["fixtures", 0, "expectations", "fits", 0, "span"], [12000, 18000]),
                     (["fixtures", 0, "expectations", "fits", 0, "pedals"], [0])]
        for path, value in mutations:
            changed = copy.deepcopy(self.catalog)
            current = changed
            for item in path[:-1]:
                current = current[item]
            current[path[-1]] = value
            with self.subTest(path=path), self.assertRaises((ValueError, KeyError, TypeError)):
                validate_catalog(changed, self.compiled)
        fixture = self.catalog["fixtures"][0]
        for line in ("1 pedal_on upper 1 100", "1 pedal_on lower 0 100",
                     "1 pedal_drawbar lower 2 1", "1 pedal_off lower 1 1",
                     "1 pedal_all_notes_off lower 1 0", "1 note_on lower 1 100"):
            raw = ("0 expression upper 0 0.5\n" + line + "\n").encode("ascii")
            with self.subTest(line=line), self.assertRaises(ValueError):
                validate_score(raw, fixture)

    @classmethod
    def tearDownClass(cls):
        print(json.dumps({"pedal_catalog_renders": cls.render_count,
                          "rendered_mono_frames": cls.rendered_frames,
                          "independent_fit_windows": sum(len(values) for values in cls.fitted.values()),
                          "full_residual_frames": cls.fit_frames,
                          "component_amplitudes": cls.component_checks,
                          "shared_phase_comparisons": cls.phase_checks,
                          "maximum_component_peak_error": cls.maximum_peak_error,
                          "maximum_residual_pcm_lsb": cls.maximum_residual,
                          "maximum_phase_vector_error": cls.maximum_phase_error}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--renderer")
    parser.add_argument("--profile")
    options, remaining = parser.parse_known_args()
    RENDERER_OVERRIDE, PROFILE_OVERRIDE = options.renderer, options.profile
    unittest.main(argv=[sys.argv[0], *remaining], verbosity=2)
