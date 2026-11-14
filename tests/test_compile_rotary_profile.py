#!/usr/bin/env python3
"""Portable rotary compiler tests; add --cxx PATH for the native all-field audit.

The ordinary suite needs only Python's standard library. The explicit native
audit compiles and runs independent C++20 observers with strict warning flags;
a missing or failing requested compiler is a failure, never a skipped success.
Expected physical fields come directly from authoring JSON, without importing
the validator's normalized mapping or the compiler's formatting helpers.
"""

from __future__ import annotations

import argparse
import copy
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
import time
import unittest
from unittest import mock


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import compile_rotary_profile as compiler

PROFILE_PATH = ROOT / "data/rotary/nominal-research-v1.json"
COMPILER_PATH = ROOT / "tools/compile_rotary_profile.py"
SOURCE_BYTES = PROFILE_PATH.read_bytes()
SOURCE = json.loads(SOURCE_BYTES)
NATIVE_COMPILER = None
NATIVE_WORK = None
NATIVE_RECORDS = []


def binary64(value):
    return struct.pack(">d", float(value)).hex()


def expected_fields(source):
    """Independent source-to-public-member map, including every physical field."""
    result = {
        "sound_speed_m_s": binary64(source["speed_of_sound"]["value"]),
        "reference_distance_m": binary64(source["signal_boundary"]["reference_distance"]["value"]),
    }
    for index, name in enumerate(("horn", "drum")):
        rotor = source["rotors"][name]
        prefix = f"rotors.{index}."
        for axis, value in zip("xyz", rotor["geometry"]["axis_origin"]["value"]):
            result[prefix + "origin_m." + axis] = binary64(value)
        result[prefix + "radius_m"] = binary64(rotor["geometry"]["radius"]["value"])
        for authoring, native in (("slow_speed", "slow_rad_s"), ("fast_speed", "fast_rad_s"),
                                  ("tau_up", "tau_up_s"), ("tau_down", "tau_down_s")):
            result[prefix + "motion." + native] = binary64(rotor["motion"][authoring]["value"])
        result[prefix + "motion.direction"] = str(int(rotor["motion"]["direction"]["value"]))
        result[prefix + "initial_phase_rad"] = binary64(rotor["initial_state"]["angle"]["value"])
        result[prefix + "initial_speed_rad_s"] = binary64(rotor["initial_state"]["speed"]["value"])
        result[prefix + "initial_command"] = str(("chorale", "tremolo").index(rotor["initial_command"]))
    for index, microphone in enumerate(source["microphones"]):
        for axis, value in zip("xyz", microphone["position"]["value"]):
            result[f"microphones.{index}.position_m.{axis}"] = binary64(value)
    return result


def distinctive_source():
    result = copy.deepcopy(SOURCE)
    result["profile_id"] = "distinct-admitted-values"
    result["speed_of_sound"]["value"] = math.nextafter(344.25, math.inf)
    result["signal_boundary"]["reference_distance"]["value"] = 0.12345678901234567
    for name, values in {
        "horn": ([-0.0, math.ulp(0.0), 0.8123456789012345], math.nextafter(0.125, math.inf),
                 1.125, 27.875, 0.125, 0.875, -1, 2.25, 2.625, "tremolo"),
        "drum": ([-0.375, 0.25, -0.0], math.nextafter(0.25, 0.0),
                 2.375, 45.125, 1.375, 4.625, 1, 5.125, 3.875, "chorale"),
    }.items():
        rotor = result["rotors"][name]
        rotor["geometry"]["axis_origin"]["value"], rotor["geometry"]["radius"]["value"] = values[:2]
        for key, value in zip(("slow_speed", "fast_speed", "tau_up", "tau_down", "direction"), values[2:7]):
            rotor["motion"][key]["value"] = value
        rotor["initial_state"]["angle"]["value"] = values[7]
        rotor["initial_state"]["speed"]["value"] = values[8]
        rotor["initial_command"] = values[9]
    result["microphones"][0]["position"]["value"] = [-1.5625, -1.25, 1.1875]
    result["microphones"][1]["position"]["value"] = [1.6875, -1.4375, 0.75]
    return result


def extreme_source():
    result = copy.deepcopy(SOURCE)
    result["profile_id"] = "admitted-endpoints"
    result["speed_of_sound"]["value"] = 380
    result["signal_boundary"]["reference_distance"]["value"] = 10
    for index, name in enumerate(("horn", "drum")):
        rotor = result["rotors"][name]
        rotor["geometry"]["axis_origin"]["value"] = [-10, index, -0.0]
        rotor["geometry"]["radius"]["value"] = -0.0
        for key, value in (("slow_speed", 200), ("fast_speed", 200),
                           ("tau_up", 0.001), ("tau_down", 60)):
            rotor["motion"][key]["value"] = value
        rotor["initial_state"]["angle"]["value"] = math.nextafter(math.tau, 0.0) if index else -0.0
        rotor["initial_state"]["speed"]["value"] = 200
        rotor["initial_command"] = "tremolo" if index else "chorale"
        result["microphones"][index]["position"]["value"] = [0, index, -0.0]
    return result


def hostile_prose_source():
    result = copy.deepcopy(SOURCE)
    payload = '\"; }; static_assert(false); #include "injected.h" // \\ ??/ café Δ 😀'
    result["speed_of_sound"]["evidence"]["reason"] = payload
    result["unknowns"]["selected_cabinet"]["required_acquisition"] = payload
    return result


def reverse_objects(value):
    if isinstance(value, dict):
        return {key: reverse_objects(child) for key, child in reversed(value.items())}
    if isinstance(value, list):
        return [reverse_objects(child) for child in value]
    return value


def header_fields(payload):
    """Inspect assigned public members; native audit separately checks C++ meaning."""
    result = {}
    for member, expression in re.findall(r"^    profile\.([^ =]+) = ([^;]+);$", payload.decode("ascii"), re.M):
        member = re.sub(r"\[(\d+)\]", r".\1", member)
        if expression.startswith("{"):
            values = expression[1:-1].split(", ")
            if len(values) != 3:
                raise AssertionError("generated coordinate does not have three components")
            additions = {member + "." + axis: binary64(float.fromhex(value))
                         for axis, value in zip("xyz", values)}
        elif expression.startswith("SpeedCommand::"):
            additions = {member: str(("SpeedCommand::Chorale", "SpeedCommand::Tremolo").index(expression))}
        elif member.endswith(".direction"):
            additions = {member: str(int(expression))}
        else:
            additions = {member: binary64(float.fromhex(expression))}
        if result.keys() & additions.keys():
            raise AssertionError("public member assigned more than once")
        result.update(additions)
    return result


class CompilerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="rotary profile compiler ")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)
        self.source = self.work / "source café.json"
        self.output = self.work / "RotaryNominalProfile.h"

    def write_source(self, source):
        payload = json.dumps(source, ensure_ascii=False, allow_nan=False, indent=2).encode("utf-8") + b"\n"
        self.source.write_bytes(payload)
        return payload

    def assert_source_fields(self, source):
        raw = self.write_source(source)
        header, identity = compiler.compile_header(self.source)
        expected = expected_fields(source)
        self.assertEqual(len(expected), 32)
        self.assertEqual(header_fields(header), expected)
        self.assertEqual(identity, {
            "profile_id": source["profile_id"], "model_id": source["model_id"],
            "contract_id": source["contract_id"], "source_file_sha256": hashlib.sha256(raw).hexdigest(),
        })
        for cpp_name, key in (("kProfileId", "profile_id"), ("kModelId", "model_id"),
                              ("kContractId", "contract_id"), ("kProfileSha256", "source_file_sha256")):
            self.assertIn(f'{cpp_name} = "{identity[key]}";', header.decode("ascii"))
        return header

    def test_nominal_all_fields_and_exact_source_identity(self):
        payload, identity = compiler.compile_header(PROFILE_PATH)
        self.assertEqual(header_fields(payload), expected_fields(SOURCE))
        self.assertEqual(identity["source_file_sha256"], hashlib.sha256(SOURCE_BYTES).hexdigest())
        self.assertNotIn(b"\r", payload)
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))

    def test_distinct_values_preserve_binary64_sign_zero_subnormal_and_order(self):
        self.assert_source_fields(distinctive_source())

    def test_admitted_endpoints_integer_quantities_and_commands(self):
        self.assert_source_fields(extreme_source())

    def test_raw_byte_identity_changes_but_field_projection_does_not(self):
        original = self.assert_source_fields(SOURCE)
        changed = self.assert_source_fields(reverse_objects(SOURCE))
        without_digest = lambda header: re.sub(rb'kProfileSha256 = "[0-9a-f]{64}"', b"kProfileSha256", header)
        self.assertNotEqual(original, changed)
        self.assertEqual(without_digest(original), without_digest(changed))
        compact = json.dumps(SOURCE, separators=(",", ":")).encode("utf-8")
        self.source.write_bytes(compact)
        second, identity = compiler.compile_header(self.source)
        self.assertEqual(identity["source_file_sha256"], hashlib.sha256(compact).hexdigest())
        self.assertEqual(without_digest(original), without_digest(second))

    def test_metadata_strings_are_admitted_and_never_interpolated_into_code(self):
        header = self.assert_source_fields(hostile_prose_source())
        for forbidden in (b"injected.h", b"static_assert(false)", b"??/", "café".encode("utf-8")):
            self.assertNotIn(forbidden, header)

    def test_literal_escaping_is_ascii_and_fixed_width(self):
        self.assertEqual(compiler._cpp_string_literal('"\\?\x00\n9é'),
                         '"\\042\\134\\077\\000\\0129\\303\\251"')
        with self.assertRaises(UnicodeEncodeError):
            compiler._cpp_string_literal("\ud800")

    def test_compile_header_reads_source_once_through_existing_validator(self):
        with mock.patch.object(compiler.admission, "load_profile_with_digest",
                               wraps=compiler.admission.load_profile_with_digest) as load:
            compiler.compile_header(PROFILE_PATH)
        load.assert_called_once_with(PROFILE_PATH)

    def test_output_is_atomic_and_source_unchanged(self):
        raw = self.write_source(SOURCE)
        before = self.source.stat()
        self.output.write_bytes(b"previous output\n")
        identity = compiler.compile_profile(self.source, self.output)
        self.assertEqual(self.output.read_bytes(), compiler.compile_header(self.source)[0])
        self.assertEqual(self.source.read_bytes(), raw)
        self.assertEqual(self.source.stat().st_mtime_ns, before.st_mtime_ns)
        self.assertEqual(identity["source_file_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(set(self.work.iterdir()), {self.source, self.output})

    def test_rejected_authoring_preserves_existing_output(self):
        mutations = [
            (("schema_version",), 2), (("model_id",), "other-model"),
            (("contract_id",), "other-contract"), (("profile_id",), 'bad"; static_assert(false);'),
            (("profile_id",), "unicode-é"), (("extra",), 1),
            (("speed_of_sound", "value"), 299.0), (("speed_of_sound", "unit"), "km/h"),
            (("rotors", "horn", "motion", "direction", "value"), 0),
            (("rotors", "drum", "motion", "tau_up", "value"), 0),
            (("rotors", "horn", "initial_state", "angle", "value"), math.tau),
            (("rotors", "drum", "initial_command"), "STOP"),
            (("rotors", "horn", "geometry", "axis_origin", "value"), [11, 0, 0]),
            (("microphones", 0, "id"), "right"),
            (("speed_of_sound", "evidence", "reason"), "line\nbreak"),
            (("speed_of_sound", "evidence", "reason"), "\ud800"),
        ]
        self.output.write_bytes(b"prior valid output\x00\xff")
        before = (self.output.read_bytes(), self.output.stat().st_mtime_ns)
        for path, value in mutations:
            with self.subTest(path=path, value=repr(value)):
                source = copy.deepcopy(SOURCE)
                node = source
                for key in path[:-1]:
                    node = node[key]
                node[path[-1]] = value
                self.source.write_bytes(json.dumps(source, ensure_ascii=True).encode("ascii"))
                with self.assertRaises(compiler.RotaryProfileError):
                    compiler.compile_profile(self.source, self.output)
                self.assertEqual((self.output.read_bytes(), self.output.stat().st_mtime_ns), before)
                self.assertEqual(set(self.work.iterdir()), {self.source, self.output})

    def test_bad_json_duplicate_keys_nonfinite_boolean_and_bounded_input(self):
        compact = json.dumps(SOURCE, separators=(",", ":")).encode("ascii")
        invalid = [b"", b"\xff", b"{}", b"[]", b"null", b"true", b"{" + compact,
                   b'{"schema_version":1,' + compact[1:],
                   compact.replace(b'"value":343.0', b'"value":343.0,"value":344.0', 1),
                   b" " * (compiler.admission.MAX_INPUT_BYTES + 1)]
        for token in (b"NaN", b"Infinity", b"-Infinity", b"1e9999", b"true", b'"343"'):
            invalid.append(compact.replace(b'"value":343.0', b'"value":' + token, 1))
        self.output.write_bytes(b"keep this header")
        before = (self.output.read_bytes(), self.output.stat().st_mtime_ns)
        for index, payload in enumerate(invalid):
            with self.subTest(case=index):
                self.source.write_bytes(payload)
                with self.assertRaises(compiler.RotaryProfileError):
                    compiler.compile_profile(self.source, self.output)
                self.assertEqual((self.output.read_bytes(), self.output.stat().st_mtime_ns), before)
                self.assertEqual(set(self.work.iterdir()), {self.source, self.output})

    def test_rejected_source_creates_no_output_or_parent(self):
        self.source.write_bytes(b"{}")
        destination = self.work / "absent parent" / "profile.h"
        with self.assertRaises(compiler.RotaryProfileError):
            compiler.compile_profile(self.source, destination)
        self.assertFalse(destination.parent.exists())
        self.assertEqual(set(self.work.iterdir()), {self.source})

    def test_source_alias_and_hardlink_are_preserved(self):
        raw = self.write_source(SOURCE)
        with self.assertRaises(compiler.RotaryProfileError):
            compiler.compile_profile(self.source, self.source)
        self.assertEqual(self.source.read_bytes(), raw)
        os.link(self.source, self.output)
        with self.assertRaises(compiler.RotaryProfileError):
            compiler.compile_profile(self.source, self.output)
        self.assertEqual(self.source.read_bytes(), raw)
        self.assertEqual(self.output.read_bytes(), raw)

    def test_nonregular_output_and_missing_parent_reject_cleanly(self):
        self.write_source(SOURCE)
        self.output.mkdir()
        sentinel = self.output / "keep.txt"
        sentinel.write_bytes(b"keep")
        with self.assertRaises(compiler.RotaryProfileError):
            compiler.compile_profile(self.source, self.output)
        self.assertEqual(sentinel.read_bytes(), b"keep")
        with self.assertRaises(compiler.RotaryProfileError):
            compiler.compile_profile(self.source, self.work / "absent" / "profile.h")
        self.assertFalse((self.work / "absent").exists())

    def test_write_flush_and_replace_failures_leave_no_partial_output(self):
        self.write_source(SOURCE)
        self.output.write_bytes(b"unchanged header")
        before = (self.output.read_bytes(), self.output.stat().st_mtime_ns)
        for operation in ("fsync", "replace"):
            with self.subTest(operation=operation):
                with mock.patch.object(compiler.os, operation, side_effect=OSError("injected output failure")):
                    with self.assertRaises(compiler.RotaryProfileError):
                        compiler.compile_profile(self.source, self.output)
                self.assertEqual((self.output.read_bytes(), self.output.stat().st_mtime_ns), before)
                self.assertEqual(set(self.work.iterdir()), {self.source, self.output})

    def test_cli_deterministic_across_paths_and_hash_seeds(self):
        self.write_source(SOURCE)
        observed = []
        for seed in ("1", "90210"):
            directory = self.work / ("different café " + seed)
            directory.mkdir()
            source, output = directory / "other.json", directory / "other.h"
            source.write_bytes(self.source.read_bytes())
            child = subprocess.run([sys.executable, str(COMPILER_PATH), "--input", str(source),
                                    "--output", str(output)], env={**os.environ, "PYTHONHASHSEED": seed},
                                   capture_output=True, text=True, timeout=30, check=False)
            self.assertEqual(child.returncode, 0, child.stdout + child.stderr)
            self.assertEqual(json.loads(child.stdout)["status"], "compiled")
            self.assertEqual(child.stderr, "")
            observed.append(output.read_bytes())
        self.assertEqual(observed[0], observed[1])
        self.assertEqual(observed[0], compiler.compile_header(self.source)[0])

    def test_cli_rejections_are_structured_and_preserve_output(self):
        self.source.write_bytes(b"{}")
        self.output.write_bytes(b"keep")
        before = (self.output.read_bytes(), self.output.stat().st_mtime_ns)
        cases = [[], ["--input", str(self.source)], ["--bogus"],
                 ["--input", str(self.source), "--output", str(self.output)],
                 ["--in", str(self.source), "--output", str(self.output)]]
        for arguments in cases:
            with self.subTest(arguments=arguments):
                child = subprocess.run([sys.executable, str(COMPILER_PATH), *arguments],
                                       capture_output=True, text=True, timeout=30, check=False)
                self.assertEqual(child.returncode, 2)
                self.assertEqual(json.loads(child.stdout)["status"], "rejected")
                self.assertEqual(child.stderr, "")
                self.assertEqual((self.output.read_bytes(), self.output.stat().st_mtime_ns), before)


OBSERVER_SOURCE = r'''#include "RotaryNominalProfile.h"
#include "RotaryNominalProfile.h"
#include <bit>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <string>

void number(const std::string& key, double value) {
    std::cout << key << ' ' << std::hex << std::setw(16) << std::setfill('0')
              << std::bit_cast<std::uint64_t>(value) << '\n';
}
void integer(const std::string& key, int value) {
    std::cout << key << ' ' << std::dec << value << '\n';
}
int main() {
    namespace generated = hammond::rotary::generated;
    static_assert(noexcept(generated::nominal_profile()));
    const auto profile = generated::nominal_profile();
    number("sound_speed_m_s", profile.sound_speed_m_s);
    number("reference_distance_m", profile.reference_distance_m);
    for (std::size_t i = 0; i < profile.rotors.size(); ++i) {
        const auto prefix = "rotors." + std::to_string(i) + ".";
        const auto& rotor = profile.rotors[i];
        number(prefix + "origin_m.x", rotor.origin_m.x);
        number(prefix + "origin_m.y", rotor.origin_m.y);
        number(prefix + "origin_m.z", rotor.origin_m.z);
        number(prefix + "radius_m", rotor.radius_m);
        number(prefix + "motion.slow_rad_s", rotor.motion.slow_rad_s);
        number(prefix + "motion.fast_rad_s", rotor.motion.fast_rad_s);
        number(prefix + "motion.tau_up_s", rotor.motion.tau_up_s);
        number(prefix + "motion.tau_down_s", rotor.motion.tau_down_s);
        integer(prefix + "motion.direction", static_cast<int>(rotor.motion.direction));
        number(prefix + "initial_phase_rad", rotor.initial_phase_rad);
        number(prefix + "initial_speed_rad_s", rotor.initial_speed_rad_s);
        integer(prefix + "initial_command", static_cast<int>(rotor.initial_command));
    }
    for (std::size_t i = 0; i < profile.microphones.size(); ++i) {
        const auto prefix = "microphones." + std::to_string(i) + ".position_m.";
        number(prefix + "x", profile.microphones[i].position_m.x);
        number(prefix + "y", profile.microphones[i].position_m.y);
        number(prefix + "z", profile.microphones[i].position_m.z);
    }
    std::cout << "id.profile " << generated::kProfileId << '\n'
              << "id.source_sha256 " << generated::kProfileSha256 << '\n'
              << "id.model " << generated::kModelId << '\n'
              << "id.contract " << generated::kContractId << '\n';
}
'''


class NativeCompilerTests(unittest.TestCase):
    def setUp(self):
        if NATIVE_WORK is None:
            temporary = tempfile.TemporaryDirectory(prefix="rotary native profile ")
            self.addCleanup(temporary.cleanup)
            self.work = Path(temporary.name)
        else:
            NATIVE_WORK.mkdir(parents=True, exist_ok=True)
            self.work = Path(tempfile.mkdtemp(prefix=self._testMethodName + "-", dir=NATIVE_WORK))

    def compile_run(self, directory, sources):
        native_sources = []
        for name, text in sources.items():
            path = directory / name
            path.write_text(text, encoding="utf-8", newline="\n")
            native_sources.append(path)
        executable = directory / ("observer.exe" if os.name == "nt" else "observer")
        if Path(NATIVE_COMPILER).name.lower() in ("cl", "cl.exe", "clang-cl", "clang-cl.exe"):
            options = ["/nologo", "/std:c++20", "/W4", "/WX", "/permissive-", "/Zc:__cplusplus", "/EHsc",
                       "/I" + str(ROOT / "include"), "/I" + str(directory)]
            command = [NATIVE_COMPILER, *options, *(str(path) for path in native_sources), "/Fe:" + str(executable)]
        else:
            options = ["-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion",
                       "-Wsign-conversion", "-Wshadow", "-Werror", "-I", str(ROOT / "include"), "-I", str(directory)]
            command = [NATIVE_COMPILER, *options, *(str(path) for path in native_sources), "-o", str(executable)]
        child = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(child.returncode, 0, child.stdout + child.stderr)
        execution = subprocess.run([str(executable)], capture_output=True, text=True, timeout=30, check=False)
        self.assertEqual(execution.returncode, 0, execution.stdout + execution.stderr)
        self.assertEqual(execution.stderr, "")
        record = {
            "compile_command": command, "compile_exit": child.returncode, "run_exit": execution.returncode,
            "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
            "source_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in native_sources},
            "stdout_sha256": hashlib.sha256(execution.stdout.encode("utf-8")).hexdigest(),
        }
        NATIVE_RECORDS.append(record)
        return execution.stdout, record

    def test_native_all_physical_fields_and_identities(self):
        cases = {"nominal": SOURCE, "distinct": distinctive_source(),
                 "endpoints": extreme_source(), "hostile-prose": hostile_prose_source()}
        for name, source in cases.items():
            with self.subTest(case=name):
                directory = self.work / name
                directory.mkdir()
                source_path = directory / "source.json"
                raw = SOURCE_BYTES if name == "nominal" else json.dumps(source, ensure_ascii=False).encode("utf-8")
                source_path.write_bytes(raw)
                header_path = directory / "RotaryNominalProfile.h"
                compiler.compile_profile(source_path, header_path)
                output, record = self.compile_run(directory, {"observe.cpp": OBSERVER_SOURCE})
                observed = dict(line.split(" ", 1) for line in output.splitlines())
                expected = expected_fields(source)
                self.assertEqual(len(expected), 32)
                expected.update({"id.profile": source["profile_id"], "id.model": source["model_id"],
                                 "id.contract": source["contract_id"], "id.source_sha256": hashlib.sha256(raw).hexdigest()})
                self.assertEqual(len(output.splitlines()), len(expected))
                self.assertEqual(observed, expected)
                record.update({"case": name, "observed": observed, "physical_fields_checked": 32,
                               "header_sha256": hashlib.sha256(header_path.read_bytes()).hexdigest(),
                               "authoring_sha256": hashlib.sha256(raw).hexdigest()})

    def test_native_escaped_strings_round_trip_as_data(self):
        values = ['', '\"; }; static_assert(false); //', "\\0777?9", "\x00\n\r\t9", "café Δ 😀\u2028"]
        lines = ["#include <cstddef>", "#include <iomanip>", "#include <iostream>", "#include <string_view>",
                 "int main() {", "    const std::string_view values[] = {"]
        for value in values:
            lines.append(f"        {{{compiler._cpp_string_literal(value)}, {len(value.encode('utf-8'))}}},")
        lines.extend(["    };", "    for (auto value : values) {", "        for (char byte : value) {",
                      "            std::cout << std::hex << std::setw(2) << std::setfill('0')",
                      "                      << static_cast<unsigned int>(static_cast<unsigned char>(byte));",
                      "        }", "        std::cout << '\\n';", "    }", "}", ""])
        output, record = self.compile_run(self.work, {"escaping.cpp": "\n".join(lines)})
        self.assertEqual(output.splitlines(), [value.encode("utf-8").hex() for value in values])
        record.update({"case": "escaping", "utf8_payloads_checked": len(values)})

    def test_native_header_only_multiple_translation_units_and_factory_values(self):
        compiler.compile_profile(PROFILE_PATH, self.work / "RotaryNominalProfile.h")
        other = '''#include "RotaryNominalProfile.h"
hammond::rotary::Profile other_profile() { return hammond::rotary::generated::nominal_profile(); }
const std::string_view* other_id() { return &hammond::rotary::generated::kProfileId; }
'''
        main = '''#include "RotaryNominalProfile.h"
#include <iostream>
hammond::rotary::Profile other_profile();
const std::string_view* other_id();
int main() {
    auto one = hammond::rotary::generated::nominal_profile();
    const auto two = other_profile();
    if (!(one == two) || other_id() != &hammond::rotary::generated::kProfileId) return 1;
    one.sound_speed_m_s = 0.0;
    if (two.sound_speed_m_s == 0.0 || other_profile().sound_speed_m_s == 0.0) return 2;
    std::cout << "header-only-independent-values\\n";
}
'''
        output, record = self.compile_run(self.work, {"other.cpp": other, "main.cpp": main})
        self.assertEqual(output, "header-only-independent-values\n")
        record.update({"case": "multiple-translation-units"})


def load_tests(loader, tests, pattern):
    del tests, pattern
    suite = loader.loadTestsFromTestCase(CompilerTests)
    if NATIVE_COMPILER is not None:
        suite.addTests(loader.loadTestsFromTestCase(NativeCompilerTests))
    return suite


def main():
    global NATIVE_COMPILER, NATIVE_WORK
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--cxx", help="explicit C++20 compiler executable for the additional native audit")
    parser.add_argument("--native-work-dir", type=Path)
    parser.add_argument("--report", type=Path)
    args, unittest_args = parser.parse_known_args()
    NATIVE_COMPILER = args.cxx
    NATIVE_WORK = args.native_work_dir.resolve() if args.native_work_dir else None
    if NATIVE_WORK is not None and NATIVE_COMPILER is None:
        parser.error("--native-work-dir requires --cxx")
    started = time.monotonic()
    program = unittest.main(argv=[sys.argv[0], *unittest_args], exit=False)
    if args.report:
        report = {
            "status": "pass" if program.result.wasSuccessful() else "fail",
            "tests_run": program.result.testsRun,
            "failures": len(program.result.failures), "errors": len(program.result.errors),
            "skipped": len(program.result.skipped), "elapsed_seconds": time.monotonic() - started,
            "python": sys.version, "command": [sys.executable, *sys.argv],
            "native_audit_requested": NATIVE_COMPILER is not None,
            "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in (COMPILER_PATH, Path(__file__).resolve(), PROFILE_PATH,
                                           ROOT / "tools/validate_rotary_profile.py", ROOT / "include/hammond/RotaryTypes.h")},
            "native_records": NATIVE_RECORDS,
        }
        args.report.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0 if program.result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
