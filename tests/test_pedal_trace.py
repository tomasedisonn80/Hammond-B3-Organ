#!/usr/bin/env python3
"""Independent source/CSV/voice acceptance for the actual pedal trace exporter."""

from __future__ import annotations

from collections import Counter
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest

RATES = (44100, 48000, 96000)
MAX_BYTES = 8 * 1024 * 1024
MAX_SEED = 2**64 - 1
HEADER = ("frame,sample_rate,time_seconds,pedal_position_0,pedal_position_1,"
          "brown,red,orange,yellow,mixture_0,mixture_1,pedal_output,audio,expression,"
          "active_pedals,pedal_targets,contact_bits,upper_down,lower_down,"
          "upper_route,lower_route,upper_bank,lower_bank,upper_drawbar,lower_drawbar,"
          "source_phase_before,clock_after").split(",")
METADATA = ("hammond_pedal_trace_schema", "evidence_scope", "source_model",
            "manual_contact_model", "pedal_contact_model", "pedal_routing_model",
            "pedal_voice_model", "pedal_gain_law", "pedal_map_id", "pedal_map_raw_sha256",
            "pedal_map_canonical_sha256", "pedal_reference_a_sha256", "pedal_reference_b_sha256",
            "mixture_matrix", "pedal_position_gains", "pedal_weight_policy", "signal_units",
            "scenario", "scenario_version", "profile_id", "authoring_sha256", "profile_digest_scope",
            "sample_rate", "seed", "frames", "timing", "contact_bits_order", "pedal_targets_order",
            "manual_midi", "manual_drawbar_index", "tracked_tone_id", "tracked_frequency_hz",
            "tracked_source_peak", "profile_output_gain", "percussion", "row_count_limit", "byte_limit")

# Independent transcription of version1 scenarios; no production score builder.
SCENARIOS = {
    "unmute": ((0, "on", 8, 0), (0, "on", 12, 0), (20, "bar", 0, 8),
               (40, "bar", 1, 4), (60, "bar", 0, 0), (72, "bar", 1, 0),
               (80, "bar", 1, 8), (96, "off", 8, 0), (104, "off", 12, 0),
               (112, "pedal_panic", 0, 0)),
    "overlap": ((0, "on", 1, 0), (16, "manual", 0, 1), (32, "on", 25, 0),
                (48, "manual", 1, 1), (64, "off", 1, 0), (80, "manual", 0, 0),
                (96, "off", 25, 0), (112, "manual", 1, 0)),
    "routing": tuple((0, "on", pedal, 0) for pedal in range(1, 26)) +
               ((0, "manual", 0, 1), (0, "manual", 1, 1), (20, "route", 1, 0),
                (40, "route", 1, 1), (60, "manual", 1, 0),
                (80, "pedal_panic", 0, 0), (100, "manual", 0, 0)),
}

# Exact top-53-bit initial offsets for tone IDs1..68, frozen by independent
# arbitrary-precision integer evaluation of the documented SplitMix64 mapping.
# IDs1/46/91 were cross-checked against the retained tonewheel known-answer table.
# This test never imports or reimplements the production source recurrence.
INITIAL_PHASES = {
    0: tuple(float.fromhex(value) for value in (
        '0x1.c4415072f63b9p-1', '0x1.b9e279aa86e58p-2', '0x1.b117462002500p-6', '0x1.f1177150e4990p-1',
        '0x1.b39896a51a870p-4', '0x1.4f2e7c31d1fa8p-2', '0x1.6414d5f0fa298p-3', '0x1.8b082675922d5p-1',
        '0x1.f72bc4820e4c4p-3', '0x1.e77091186d196p-1', '0x1.95fbb374f2c4ep-2', '0x1.85a64dc00ab7bp-1',
        '0x1.0c43407fc177bp-1', '0x1.1c3eeaab30755p-1', '0x1.6a9c1e2c01989p-1', '0x1.09767f2f2e3b0p-1',
        '0x1.f4a60971d5484p-2', '0x1.879e2e2056fefp-1', '0x1.a3374d041c8a4p-3', '0x1.b0351a56b4890p-1',
        '0x1.b602c05620173p-1', '0x1.52071524304bep-1', '0x1.dbebe3b21b945p-1', '0x1.5125ab59ef498p-2',
        '0x1.baf803a9ea80ep-1', '0x1.26bd05e3b6989p-1', '0x1.a6e0baf2488ccp-2', '0x1.034a7ad5f7874p-2',
        '0x1.45e13b5768b8cp-1', '0x1.dca43af41e9a7p-1', '0x1.e2d2a5dce5e68p-1', '0x1.bbe9aef547200p-3',
        '0x1.8fbd00c92c770p-5', '0x1.560b4dc446b00p-6', '0x1.a4a8e83eb33b8p-1', '0x1.a58c3dd64f442p-2',
        '0x1.05fbe586076a8p-2', '0x1.e1e20d1da19a0p-3', '0x1.b86641772f94cp-2', '0x1.3ea7e9cc92144p-2',
        '0x1.09d688a94f252p-1', '0x1.34f7096918170p-4', '0x1.f724c2cc089e0p-6', '0x1.2c015a97019e8p-4',
        '0x1.980d862ca5d7ep-1', '0x1.d9dccac614d23p-1', '0x1.f427658bb1f3cp-3', '0x1.a43b51d9d0eaap-2',
        '0x1.dd18575ec687cp-2', '0x1.159a9f827a7a8p-3', '0x1.c7bbb0d74e34bp-1', '0x1.be4d15bd6ca26p-1',
        '0x1.04c75b9ea1b3cp-3', '0x1.eb422991e71c0p-7', '0x1.92a58ac400878p-1', '0x1.3632d795089e2p-1',
        '0x1.81301a2eecf04p-3', '0x1.9e8914b105772p-1', '0x1.e94af1b99790ep-1', '0x1.7fbd5db342f67p-1',
        '0x1.daf2805a3ab8bp-1', '0x1.57c1c2ac72efcp-2', '0x1.f0051a494d444p-3', '0x1.c4ab646f71763p-1',
        '0x1.53db3d7b63568p-3', '0x1.19b579fcf91bcp-2', '0x1.08dd72ce6693ep-2', '0x1.19143e2915176p-1',
    )),
    MAX_SEED: tuple(float.fromhex(value) for value in (
        '0x1.c9b2e2ee36ca5p-1', '0x1.d33ff0cfb7ed0p-1', '0x1.c17fc26593940p-3', '0x1.b476cdb32ea60p-2',
        '0x1.69408e5caf00dp-1', '0x1.a63b5b7b48717p-1', '0x1.e29e59f004107p-1', '0x1.017690e28e7a0p-2',
        '0x1.89fd4e102adc1p-1', '0x1.8f287f3ddeb40p-7', '0x1.d91a4b0f38e40p-7', '0x1.9ceab2a5a604bp-1',
        '0x1.c9558bd006b80p-8', '0x1.bb21c21edef83p-1', '0x1.aa686fc592c3cp-3', '0x1.59dd427940fc6p-1',
        '0x1.a21e0a7a12978p-2', '0x1.895aa52ca2b74p-3', '0x1.1885ea55f4b74p-3', '0x1.b17b7d708ef88p-2',
        '0x1.752fb9eb3321ep-2', '0x1.58598ccf37470p-1', '0x1.e2828fac5b05cp-2', '0x1.8dd7e30e83b88p-3',
        '0x1.79b759ba8e888p-3', '0x1.30c5e9a71539bp-1', '0x1.b0e0b0f8c0fecp-1', '0x1.ca2ef99148f3ap-2',
        '0x1.835e566f90c7bp-1', '0x1.1df7a46e5ade0p-6', '0x1.25efb02f70c40p-3', '0x1.bc56bb6ca54a8p-1',
        '0x1.a748941b75158p-2', '0x1.e6551074dfd18p-1', '0x1.28c9fa75adff8p-1', '0x1.7524c199168fcp-2',
        '0x1.034c75d19b908p-4', '0x1.d0432344aea60p-3', '0x1.c84faaca00db4p-3', '0x1.b63821d748910p-2',
        '0x1.83d5332a818d6p-1', '0x1.6585dc6af6d2dp-1', '0x1.7c55efbc0a700p-5', '0x1.7c25a2bd44b56p-1',
        '0x1.9e8d589febb88p-2', '0x1.fef5432ddefd8p-4', '0x1.ffebea9e491a6p-2', '0x1.b0aa5bad513b3p-1',
        '0x1.9363ae7301a32p-1', '0x1.8920279f2cb34p-1', '0x1.050e325409104p-3', '0x1.8b2c66c2199e3p-1',
        '0x1.794e417e67b0ep-1', '0x1.58726feb534e8p-4', '0x1.d5349c9c267f2p-2', '0x1.2ce6e8a7e0914p-2',
        '0x1.a5471656e7f5ap-2', '0x1.cbe0f1dae8f88p-3', '0x1.9418b067b512ep-1', '0x1.a74f6fb0bb49ep-2',
        '0x1.51ec08a7e0352p-1', '0x1.5f3c52d423f50p-1', '0x1.9d8195b23e4c8p-4', '0x1.ec76f7208dfd5p-1',
        '0x1.4d9c0eb026bccp-2', '0x1.ce343b63727acp-3', '0x1.13d9a49889e90p-4', '0x1.5031cd20caa88p-4',
    )),
}


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def float32(value):
    return struct.unpack("<f", struct.pack("<f", value))[0]


class PedalTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.executable = Path(os.environ.get("HAMMOND_PEDAL_TRACE_EXECUTABLE", ""))
        cls.profile = Path(os.environ.get("HAMMOND_TEST_PROFILE", ""))
        if not cls.executable.is_file() or not cls.profile.is_file():
            raise RuntimeError("Build hammond_pedal_trace; set HAMMOND_PEDAL_TRACE_EXECUTABLE and HAMMOND_TEST_PROFILE.")
        cls.executable = cls.executable.resolve()
        cls.profile = cls.profile.resolve()
        cls.source = Path(os.environ.get("HAMMOND_SOURCE_DIR", Path(__file__).resolve().parents[1]))
        cls.authoring = json.loads((cls.source / "data/profiles/nominal-unmeasured-v1.json").read_text("utf-8"))
        cls.frequencies = [x["frequency_hz"] for x in cls.authoring["sources"]]
        cls.peaks = [x["peak_amplitude"] for x in cls.authoring["sources"]]
        cls.bases = [x["base_phase_turns"] for x in cls.authoring["sources"]]
        cls.gains = cls.authoring["drawbar_gains"]["values"]
        cls.output_gain = cls.authoring["output_gain"]["value"]
        cls.map_bytes = (cls.source / "data/pedal-map.json").read_bytes()
        cls.references = [(cls.source / f"data/references/review-{name}-pedal.csv").read_bytes()
                          for name in ("a", "b")]
        tables = []
        for raw in cls.references:
            reader = csv.reader(io.StringIO(raw.decode("ascii")))
            if next(reader) != ["pedal", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8"]:
                raise RuntimeError("Pedal reference column convention changed.")
            table = []
            for pedal, row in enumerate(reader, 1):
                if len(row) != 9 or int(row[0]) != pedal:
                    raise RuntimeError("Malformed independent pedal reference.")
                table.append([int(value) if value else None for value in row[1:]])
            if len(table) != 25:
                raise RuntimeError("Pedal reference must preserve all25 rows.")
            tables.append(table)
        if tables[0] != tables[1]:
            raise RuntimeError("The two retained pedal transcriptions disagree.")
        cls.routes = tables[0]
        manual_maps = []
        for name in ("a", "b"):
            with (cls.source / f"data/references/review-{name}-manual.csv").open(newline="") as stream:
                reader = list(csv.reader(stream))
                manual_maps.append(int(reader[13][3]))  # Key13 = MIDI48, third drawbar.
        if manual_maps != [25, 25] or cls.authoring["manual_map"]["tone_ids"][12][2] != 25:
            raise RuntimeError("Manual/pedal shared-source anchor requires source25.")
        cls.temp = tempfile.TemporaryDirectory(prefix="hammond-pedal-trace-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.directory = Path(cls.temp.name)
        cls.calls = cls.oracle_rows = cls.contact_bits_checked = 0
        cls.symlink_cases = 0
        cls.symlink_permission_unavailable = False
        cls.largest_bytes = 0
        cls.errors = {key: 0.0 for key in ("phase", "bus", "mixture", "pedal", "audio")}
        cls.traces = {}
        for scenario in SCENARIOS:
            for rate in RATES:
                path = cls.directory / f"{scenario}-{rate}.csv"
                result = cls.invoke(cls.arguments(path, scenario=scenario, rate=rate))
                if result.returncode or result.stdout or result.stderr or not path.is_file():
                    raise RuntimeError(f"Actual trace invocation failed: {result!r}")
                cls.traces[scenario, rate] = path

    @classmethod
    def tearDownClass(cls):
        print(json.dumps({"pedal_trace_calls": cls.calls, "oracle_rows": cls.oracle_rows,
                          "contact_bits_compared": cls.contact_bits_checked,
                          "largest_trace_bytes": cls.largest_bytes,
                          "symlink_cases": cls.symlink_cases,
                          "symlink_permission_unavailable": cls.symlink_permission_unavailable,
                          "maximum_absolute_errors": cls.errors}, sort_keys=True))

    @classmethod
    def arguments(cls, output, *, scenario="unmute", rate=48000, seed=0, profile=None):
        return ["--profile", str(profile or cls.profile), "--scenario", scenario,
                "--sample-rate", str(rate), "--seed", str(seed), "--output", str(output)]

    @classmethod
    def invoke(cls, arguments):
        cls.calls += 1
        return subprocess.run([str(cls.executable), *map(str, arguments)], cwd=cls.directory,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, check=False)

    def read_trace(self, path):
        raw = path.read_bytes()
        self.assertLessEqual(len(raw), MAX_BYTES)
        type(self).largest_bytes = max(self.largest_bytes, len(raw))
        self.assertNotIn(b"\r", raw)
        self.assertTrue(raw.endswith(b"\n"))
        lines = raw.decode("ascii").splitlines()
        metadata = {}
        for name, line in zip(METADATA, lines):
            self.assertTrue(line.startswith(f"# {name}="), (name, line))
            key, value = line[2:].split("=", 1)
            self.assertNotIn(key, metadata)
            metadata[key] = value
        self.assertEqual(tuple(metadata), METADATA)
        self.assertEqual(lines[len(METADATA)].split(","), HEADER)
        reader = csv.DictReader(lines[len(METADATA):])
        rows = list(reader)
        self.assertEqual(len(rows), int(metadata["frames"]))
        for row in rows:
            self.assertEqual(list(row), HEADER)
            self.assertNotIn(None, row.values())
        return metadata, rows

    def check_oracle(self, path, scenario, rate, *, seed=0, peaks=None, output_gain=None):
        metadata, rows = self.read_trace(path)
        peaks = self.peaks if peaks is None else peaks
        output_gain = self.output_gain if output_gain is None else output_gain
        positions = [0, 0] if scenario == "unmute" else [6 if scenario == "overlap" else 4, 2]
        down = [False, False]
        routes = [True, True]
        pedals = set()
        commands = [(rate * ms // 1000, kind, index, value)
                    for ms, kind, index, value in SCENARIOS[scenario]]
        cursor = 0
        cached_pedals = None
        bus_terms = []
        used = set()
        initial = INITIAL_PHASES[seed]
        for frame, row in enumerate(rows):
            while cursor < len(commands) and commands[cursor][0] == frame:
                _, kind, index, value = commands[cursor]
                if kind == "on": pedals.add(index)
                elif kind == "off": pedals.discard(index)
                elif kind == "bar": positions[index] = value
                elif kind == "manual": down[index] = bool(value)
                elif kind == "route": routes[index] = bool(value)
                elif kind == "pedal_panic": pedals.clear()
                else: self.fail(f"Unknown independent scenario operation {kind}")
                cursor += 1
            if cached_pedals != pedals:
                cached_pedals = pedals.copy()
                bus_terms = [Counter(self.routes[pedal - 1][contact]
                                     for pedal in pedals for contact in range(bus * 2, bus * 2 + 2)
                                     if self.routes[pedal - 1][contact] is not None)
                             for bus in range(4)]
                used = set().union(*bus_terms, {25})
            samples = {tone: peaks[tone - 1] * math.sin(math.tau * (
                (initial[tone - 1] + self.bases[tone - 1] + frame * self.frequencies[tone - 1] / rate) % 1))
                       for tone in used}
            buses = [math.fsum(count * samples[tone] for tone, count in terms.items())
                     for terms in bus_terms]
            brown, red, orange, yellow = buses
            mixture = [(4 * brown + 2 * red + orange + yellow) / 8,
                       (brown + 4 * red + 2 * orange + yellow) / 8]
            pedal_output = (positions[0] * mixture[0] + positions[1] * mixture[1]) / 8
            manual = samples[25] * sum(self.gains[position] for index, position in enumerate((8, 4))
                                       if down[index] and routes[index])
            expected_audio = float32((manual + pedal_output) * output_gain)
            targets = "".join("1" if pedal in pedals else "0" for pedal in range(1, 26))
            expected_discrete = {
                "frame": frame, "sample_rate": rate, "clock_after": frame + 1,
                "pedal_position_0": positions[0], "pedal_position_1": positions[1],
                "active_pedals": len(pedals), "upper_down": int(down[0]), "lower_down": int(down[1]),
                "upper_route": int(routes[0]), "lower_route": int(routes[1]),
                "upper_bank": 1, "lower_bank": 1, "upper_drawbar": 8, "lower_drawbar": 4,
            }
            for key, value in expected_discrete.items():
                self.assertEqual(int(row[key]), value, (scenario, rate, frame, key))
            self.assertEqual(row["pedal_targets"], targets, (scenario, rate, frame))
            self.assertEqual(row["contact_bits"], "".join(bit * 8 for bit in targets),
                             (scenario, rate, frame))
            self.assertEqual(float(row["expression"]), 1)
            self.assertLessEqual(abs(float(row["time_seconds"]) - frame / rate), 2e-17)
            expected_phase = (initial[24] + self.bases[24] + frame * self.frequencies[24] / rate) % 1
            phase_error = abs(float(row["source_phase_before"]) - expected_phase)
            phase_error = min(phase_error, 1 - phase_error)
            type(self).errors["phase"] = max(self.errors["phase"], phase_error)
            self.assertLessEqual(phase_error, 4e-12, (scenario, rate, frame, "phase"))
            comparisons = [("bus", key, expected, 2e-9)
                           for key, expected in zip(("brown", "red", "orange", "yellow"), buses)]
            comparisons += [("mixture", f"mixture_{i}", value, 2e-9) for i, value in enumerate(mixture)]
            comparisons += [("pedal", "pedal_output", pedal_output, 4e-9),
                            ("audio", "audio", expected_audio, 4e-7)]
            for category, key, expected, tolerance in comparisons:
                actual = float(row[key])
                self.assertTrue(math.isfinite(actual))
                error = abs(actual - expected)
                type(self).errors[category] = max(self.errors[category], error)
                self.assertLessEqual(error, tolerance, (scenario, rate, frame, key))
            if not pedals and not any(down[i] and routes[i] for i in range(2)):
                self.assertEqual(float(row["audio"]), 0.0)
            type(self).oracle_rows += 1
            type(self).contact_bits_checked += 200
        self.assertEqual(cursor, len(commands))
        self.assertEqual(len(rows), rate * 120 // 1000)
        self.assertEqual(metadata["seed"], str(seed))

    def test_all_scenarios_rates_against_independent_source_csv_and_voice_oracles(self):
        for (scenario, rate), path in self.traces.items():
            with self.subTest(scenario=scenario, rate=rate):
                self.check_oracle(path, scenario, rate)

    def test_exact_metadata_and_source_identities(self):
        for (scenario, rate), path in self.traces.items():
            metadata, _ = self.read_trace(path)
            expected = {
                "hammond_pedal_trace_schema": "1", "evidence_scope": "synthetic_engineering",
                "source_model": "ideal-shared-sine-v1", "manual_contact_model": "ideal-contacts-v1",
                "pedal_contact_model": "ideal-eight-contact-pedal-v1",
                "pedal_routing_model": "linear-pedal-bus-reference-v1",
                "pedal_voice_model": "nominal-static-pedal-mixture-v1",
                "pedal_gain_law": "linear-pedal-position-v1", "pedal_map_id": "atlas-derived-b3-c3-pedal-v1",
                "pedal_map_raw_sha256": hashlib.sha256(self.map_bytes).hexdigest(),
                "pedal_map_canonical_sha256": canonical_digest(json.loads(self.map_bytes)),
                "pedal_reference_a_sha256": hashlib.sha256(self.references[0]).hexdigest(),
                "pedal_reference_b_sha256": hashlib.sha256(self.references[1]).hexdigest(),
                "mixture_matrix": "0.5,0.25,0.125,0.125;0.125,0.5,0.25,0.125",
                "pedal_position_gains": "0,0.125,0.25,0.375,0.5,0.625,0.75,0.875,1",
                "pedal_weight_policy": "all-200-unit-positive-v1",
                "signal_units": "dimensionless_source_normalized", "scenario": scenario,
                "scenario_version": "1", "profile_id": "nominal-unmeasured-v1",
                "authoring_sha256": canonical_digest(self.authoring),
                "profile_digest_scope": "declared_authoring_not_compiled_hash", "sample_rate": str(rate),
                "seed": "0", "frames": str(rate * 120 // 1000),
                "timing": "events_then_pre_render_state_then_one_render_then_historical_record",
                "contact_bits_order": "pedal_1_to_25_each_contact_0_to_7",
                "pedal_targets_order": "pedal_1_to_25", "manual_midi": "48", "manual_drawbar_index": "2",
                "tracked_tone_id": "25", "percussion": "off", "row_count_limit": "11520",
                "byte_limit": str(MAX_BYTES),
            }
            for key, value in expected.items(): self.assertEqual(metadata[key], value, (scenario, rate, key))
            self.assertEqual(float(metadata["tracked_frequency_hz"]), self.frequencies[24])
            self.assertEqual(float(metadata["tracked_source_peak"]), self.peaks[24])
            self.assertEqual(float(metadata["profile_output_gain"]), self.output_gain)

    def test_all_five_null_contacts_and_all_pedal_targets_remain_visible(self):
        _, rows = self.read_trace(self.traces["routing", 96000])
        nulls = [pedal * 8 + contact for pedal, row in enumerate(self.routes)
                 for contact, tone in enumerate(row) if tone is None]
        self.assertEqual(len(nulls), 5)
        self.assertEqual(rows[0]["contact_bits"], "1" * 200)
        for index in nulls: self.assertEqual(rows[0]["contact_bits"][index], "1")
        for milliseconds in (20, 40, 60):
            row = rows[96000 * milliseconds // 1000]
            self.assertEqual(row["active_pedals"], "25")
            self.assertEqual(row["contact_bits"], "1" * 200)
        row = rows[96000 * 80 // 1000]
        self.assertEqual(row["contact_bits"], "0" * 200)
        self.assertEqual(row["upper_down"], "1")
        self.assertNotEqual(float(row["audio"]), 0)

    def test_muted_mixtures_exist_before_audio_unmute(self):
        _, rows = self.read_trace(self.traces["unmute", 48000])
        first = rows[:960]
        self.assertTrue(all(float(row["audio"]) == 0 and float(row["pedal_output"]) == 0 for row in first))
        self.assertTrue(any(abs(float(row["mixture_0"])) > .1 for row in first))
        self.assertEqual(rows[960]["active_pedals"], "2")
        self.assertEqual(rows[960]["pedal_position_0"], "8")
        self.assertTrue(any(float(row["audio"]) != 0 for row in rows[960:1920]))

    def test_max_seed_and_custom_profile_values_are_consumed(self):
        path = self.directory / "max-seed.csv"
        result = self.invoke(self.arguments(path, scenario="overlap", seed=MAX_SEED))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.check_oracle(path, "overlap", 48000, seed=MAX_SEED)
        text = self.profile.read_text("ascii").replace("output_gain 0.03\n", "output_gain 0.015\n")
        lines = text.splitlines()
        cells = lines[6 + 24].split()
        self.assertEqual(cells[0], "25")
        cells[2] = "0.5"
        lines[6 + 24] = " ".join(cells)
        profile = self.directory / "custom.b3p"
        profile.write_text("\n".join(lines) + "\n", encoding="ascii")
        path = self.directory / "custom.csv"
        result = self.invoke(self.arguments(path, scenario="overlap", profile=profile))
        self.assertEqual(result.returncode, 0, result.stderr)
        peaks = self.peaks.copy(); peaks[24] = .5
        self.check_oracle(path, "overlap", 48000, peaks=peaks, output_gain=.015)
        metadata, _ = self.read_trace(path)
        self.assertEqual(float(metadata["tracked_source_peak"]), .5)
        self.assertEqual(float(metadata["profile_output_gain"]), .015)
        self.assertEqual(metadata["profile_digest_scope"], "declared_authoring_not_compiled_hash")

    def test_deterministic_bytes_and_unsigned_leading_zero_arguments(self):
        path = self.directory / "repeat.csv"
        result = self.invoke(self.arguments(path, rate="048000", seed="00"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(path.read_bytes(), self.traces["unmute", 48000].read_bytes())
        self.assertEqual(result.stdout, b"")
        self.assertEqual(result.stderr, b"")

    def reject(self, arguments, output):
        before = {p.name for p in self.directory.iterdir()}
        result = self.invoke(arguments)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"hammond_pedal_trace:", result.stderr)
        self.assertFalse(output.exists())
        self.assertEqual({p.name for p in self.directory.iterdir()}, before)

    def test_strict_missing_duplicate_unknown_and_long_arguments(self):
        output = self.directory / "invalid-args.csv"
        valid = self.arguments(output)
        cases = [[], ["--help", "extra"], ["--unknown", "value"], ["--profile"],
                 valid + ["--seed", "0"], valid + ["position"], valid + ["--frames", "12"]]
        cases += [valid[:index] + valid[index + 2:] for index in range(0, len(valid), 2)]
        cases += [valid[:index + 1] + [""] + valid[index + 2:] for index in range(0, len(valid), 2)]
        cases.append(["--profile", "x" * 4097, *valid[2:]])
        for arguments in cases:
            with self.subTest(arguments=arguments[:3]): self.reject(arguments, output)

    def test_numeric_and_scenario_domain_rejections(self):
        output = self.directory / "bad-domain.csv"
        for scenario in ("partial", "UNMUTE", "unknown"):
            self.reject(self.arguments(output, scenario=scenario), output)
        for rate in (0, 48001, "48000.0", "-48000", "+48000", " 48000", "NaN", "inf", "9" * 21):
            self.reject(self.arguments(output, rate=rate), output)
        for seed in (-1, MAX_SEED + 1, "+0", "0.0", " 0", "nan", "9" * 21):
            self.reject(self.arguments(output, seed=seed), output)

    def test_profile_failure_and_route_anchor_reject_before_output(self):
        output = self.directory / "bad-profile.csv"
        bad = self.directory / "bad.b3p"
        for raw in (b"", b"B3PROFILE 9\n", b"x" * (128 * 1024 + 1)):
            bad.write_bytes(raw)
            self.reject(self.arguments(output, profile=bad), output)
        lines = self.profile.read_text("ascii").splitlines()
        map_line = lines.index("manual_map 61 9") + 1 + 12
        cells = lines[map_line].split()
        self.assertEqual(len(cells), 9)
        self.assertEqual(cells[2], "25")
        cells[2] = "26"
        lines[map_line] = " ".join(cells)
        bad.write_text("\n".join(lines) + "\n", encoding="ascii")
        self.reject(self.arguments(output, profile=bad), output)
        self.reject(self.arguments(output, profile=self.directory / "missing.b3p"), output)
        self.reject(self.arguments(output, profile=self.directory), output)

    def test_existing_destinations_and_input_are_preserved(self):
        existing = self.directory / "existing.csv"
        existing.write_bytes(b"keep exact bytes")
        before = self.profile.read_bytes()
        for path in (existing, self.directory, self.profile):
            result = self.invoke(self.arguments(path))
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b"")
        self.assertEqual(existing.read_bytes(), b"keep exact bytes")
        self.assertEqual(self.profile.read_bytes(), before)
        result = self.invoke(self.arguments(self.directory / "missing-parent" / "out.csv"))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.directory / "missing-parent").exists())
        self.assertFalse(list(self.directory.glob(".hammond-pedal-trace-*")))

    def test_simultaneous_publication_has_one_winner_and_no_temporaries(self):
        output = self.directory / "race.csv"
        command = [str(self.executable), *self.arguments(output, scenario="routing", rate=96000)]
        processes = [subprocess.Popen(command, cwd=self.directory, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE) for _ in range(2)]
        type(self).calls += len(processes)
        try:
            results = [process.communicate(timeout=30) for process in processes]
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill(); process.communicate()
        self.assertEqual(sorted(process.returncode for process in processes), [0, 1])
        self.assertTrue(all(stdout == b"" for stdout, _ in results))
        self.assertEqual(output.read_bytes(), self.traces["routing", 96000].read_bytes())
        self.assertFalse(list(self.directory.glob(".hammond-pedal-trace-*")))

    def test_symlink_outputs_are_preserved_and_profile_alias_is_resolved(self):
        link = self.directory / "profile-link.b3p"
        try:
            link.symlink_to(self.profile)
        except OSError as error:
            # Windows may not grant symbolic-link creation to the test account.
            # Report that exact unexecuted capability; do not claim its checks.
            if os.name == "nt" and getattr(error, "winerror", None) == 1314:
                type(self).symlink_permission_unavailable = True
                return
            raise
        dangling = self.directory / "dangling.csv"
        dangling.symlink_to(self.directory / "absent.csv")
        for output in (link, dangling):
            target = os.readlink(output)
            result = self.invoke(self.arguments(output))
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b"")
            self.assertTrue(output.is_symlink())
            self.assertEqual(os.readlink(output), target)
            type(self).symlink_cases += 1
        output = self.directory / "profile-alias.csv"
        result = self.invoke(self.arguments(output, profile=link))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(output.read_bytes(), self.traces["unmute", 48000].read_bytes())
        type(self).symlink_cases += 1
        self.assertFalse(list(self.directory.glob(".hammond-pedal-trace-*")))

    def test_help_is_separate_and_reports_fixed_evidence_limits(self):
        result = self.invoke(["--help"])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, b"")
        for value in (b"unmute|overlap|routing", b"11520", b"8 MiB", b"Synthetic engineering"):
            self.assertIn(value, result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
