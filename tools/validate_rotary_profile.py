#!/usr/bin/env python3
"""Strict offline admission for the nominal effective-mouth rotary model.

Public API: validate_profile(value) returns the original object without mutation;
load_profile(path) and load_profile_with_digest(path) parse bounded UTF-8 bytes;
normalized_profile(value) returns a fresh SI mapping for offline consumers;
canonical_json(value) and authoring_sha256(value) identify admitted authoring.
Every failure raises RotaryProfileError. This is a semantic validator, not a
general JSON Schema interpreter or evidence of measured instrument fidelity.
The CLI emits one JSON admission/error result, returning 0 or 2 respectively;
explicit --help prints ordinary argparse help text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any


MODEL_ID = "nominal-effective-mouth-rotary-v1"
CONTRACT_ID = "rotary-numerics-v1"
VARIANT = "synthetic-rotary-research"
ATLAS_PATH = "Hammond_B3_Leslie_Research_Atlas_500pp.pdf"
ATLAS_SHA256 = "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769"
MAX_INPUT_BYTES = 128 * 1024
MAX_DEPTH = 16
MAX_VALUES = 8192
MAX_STRING_LENGTH = 1024
MAX_COLLECTION_LENGTH = 64
MIN_CLEARANCE_M = 0.02
MAX_PATH_M = 20.0
MAX_RIM_SPEED_RATIO = 0.25
COORDINATE_FRAME = {
    "handedness": "right",
    "x_axis": "right-when-facing-cabinet-front",
    "y_axis": "toward-cabinet-rear",
    "z_axis": "up",
    "angle_zero": "+x",
    "positive_angle": "counterclockwise-viewed-from-positive-z",
}
OMITTED_EFFECTS = (
    "organ-and-leslie-electronics", "electrical-crossover", "driver-response",
    "internal-horn-transit", "measured-directivity", "cabinet-reflections",
    "room-response", "microphone-response", "physical-brake",
)
UNKNOWN_UNITS = {
    "selected_cabinet": "identifier",
    "measured_rotor_geometry": "m",
    "measured_rotor_speed": "rad/s",
    "measured_transition_constants": "s",
    "measured_directivity": "1",
    "radiation_amplitude_scale": "Pa/normalized-unit",
    "m6_input_transfer": "Pa/V",
    "cabinet_room_microphone_response": "identifier",
}
EVIDENCE_KEYS = {
    "evidence_class", "applicable_variant", "source_pages", "source_role",
    "uncertainty", "measurement_reference", "reason",
}
PROVENANCE_PAGES = {
    "speed": (292, 320), "tau": (292, 320), "direction": (290, 314, 319),
    "geometry": (301, 302, 314), "initial": (319, 322),
    "microphone": (301, 314), "sound_speed": (301, 302),
    "gain": (308, 419), "unknown": (2, 289, 301, 323, 343, 449),
}


class RotaryProfileError(ValueError):
    """The input cannot be admitted under this named model contract."""


def _fail(path: str, message: str) -> None:
    raise RotaryProfileError(f"{path}: {message}")


def _keys(value: Any, expected: set[str], path: str) -> dict:
    if type(value) is not dict:
        _fail(path, "must be an object")
    if set(value) != expected:
        _fail(path, f"expected exactly fields {sorted(expected)}")
    return value


def _constant(value: Any, expected: Any, path: str) -> None:
    if type(value) is not type(expected) or value != expected:
        _fail(path, f"must be {expected!r}")


def _number(value: Any, low: float, high: float, path: str) -> float:
    if type(value) not in (int, float):
        _fail(path, "must be a finite number; booleans are not numbers")
    try:
        result = float(value)
    except (OverflowError, ValueError):
        _fail(path, "number is not representable as binary64")
    if not math.isfinite(result) or not low <= result <= high:
        _fail(path, f"must be finite and in [{low}, {high}]")
    return result


def _text(value: Any, path: str) -> str:
    if type(value) is not str or not value.strip():
        _fail(path, "must be a nonempty string")
    return value


def _tree_bounds(value: Any) -> None:
    active: set[int] = set()
    count = 0

    def visit(item: Any, depth: int, path: str) -> None:
        nonlocal count
        count += 1
        if count > MAX_VALUES or depth > MAX_DEPTH:
            _fail(path, "exceeds JSON nesting or value-count bound")
        if type(item) in (dict, list):
            identity = id(item)
            if identity in active or len(item) > MAX_COLLECTION_LENGTH:
                _fail(path, "cyclic or oversized collection")
            active.add(identity)
            if type(item) is dict:
                for key, child in item.items():
                    if type(key) is not str:
                        _fail(path, "object names must be strings")
                    visit(key, depth + 1, f"{path}.<key>")
                    visit(child, depth + 1, f"{path}.{key}")
            else:
                for index, child in enumerate(item):
                    visit(child, depth + 1, f"{path}[{index}]")
            active.remove(identity)
        elif type(item) is str:
            if len(item) > MAX_STRING_LENGTH or any(ord(c) < 32 for c in item):
                _fail(path, "oversized or control-character string")
            try:
                item.encode("utf-8")
            except UnicodeEncodeError:
                _fail(path, "invalid Unicode surrogate")
        elif type(item) in (int, float):
            try:
                finite = math.isfinite(item)
            except OverflowError:
                finite = False
            if not finite:
                _fail(path, "number must be finite and representable as binary64")
        elif item is not None:
            _fail(path, "unsupported value type; booleans are not admitted")

    visit(value, 0, "profile")


def _evidence(value: Any, kind: str, pages: tuple[int, ...], path: str) -> None:
    record = _keys(value, EVIDENCE_KEYS, path)
    _constant(record["evidence_class"], kind, f"{path}.evidence_class")
    _constant(record["applicable_variant"], VARIANT, f"{path}.applicable_variant")
    expected_role = "missing-acquisition" if kind == "unknown" else "algorithm-and-boundary-only"
    _constant(record["source_role"], expected_role, f"{path}.source_role")
    _constant(record["uncertainty"], None, f"{path}.uncertainty")
    _constant(record["measurement_reference"], None, f"{path}.measurement_reference")
    _text(record["reason"], f"{path}.reason")
    actual_pages = record["source_pages"]
    if type(actual_pages) is not list or any(type(p) is not int for p in actual_pages):
        _fail(f"{path}.source_pages", "must contain integer page numbers")
    if actual_pages != list(pages):
        _fail(f"{path}.source_pages", f"expected the fixed model basis {list(pages)}")


def _quantity(value: Any, unit: str, low: float, high: float,
              pages: tuple[int, ...], path: str, vector: bool = False) -> float | list[float]:
    record = _keys(value, {"value", "unit", "evidence"}, path)
    _constant(record["unit"], unit, f"{path}.unit")
    _evidence(record["evidence"], "proposed", pages, f"{path}.evidence")
    if vector:
        data = record["value"]
        if type(data) is not list or len(data) != 3:
            _fail(f"{path}.value", "must be exactly three coordinates")
        return [_number(v, low, high, f"{path}.value[{i}]") for i, v in enumerate(data)]
    return _number(record["value"], low, high, f"{path}.value")


def _admit(profile: Any) -> dict:
    """Validate without mutation and build a fresh normalized SI representation."""
    _tree_bounds(profile)
    root = _keys(profile, {
        "schema_version", "profile_id", "model_id", "contract_id", "evidence_class",
        "applicable_variant", "source", "coordinate_frame", "signal_boundary",
        "speed_of_sound", "rotors", "microphones", "startup", "unknowns",
    }, "profile")
    for key, expected in (("schema_version", 1), ("model_id", MODEL_ID),
                          ("contract_id", CONTRACT_ID), ("evidence_class", "proposed"),
                          ("applicable_variant", VARIANT)):
        _constant(root[key], expected, f"profile.{key}")
    profile_id = _text(root["profile_id"], "profile.profile_id")
    if re.fullmatch(r"[a-z][a-z0-9-]{0,62}", profile_id) is None:
        _fail("profile.profile_id", "must be a 1-63 character lowercase ASCII identifier")
    source = _keys(root["source"], {"document", "sha256", "basis"}, "profile.source")
    _constant(source["document"], ATLAS_PATH, "profile.source.document")
    _constant(source["sha256"], ATLAS_SHA256, "profile.source.sha256")
    _constant(source["basis"], "algorithm-proposals-not-measured-values", "profile.source.basis")
    frame = _keys(root["coordinate_frame"], set(COORDINATE_FRAME), "profile.coordinate_frame")
    for key, expected in COORDINATE_FRAME.items():
        _constant(frame[key], expected, f"profile.coordinate_frame.{key}")
    boundary = _keys(root["signal_boundary"], {
        "input", "output", "directivity", "distance_gain", "reference_distance", "omitted_effects",
    }, "profile.signal_boundary")
    for key, expected in (("input", "normalized-effective-mouth-amplitude"),
                          ("output", "normalized-propagated-amplitude"),
                          ("directivity", "unity-omnidirectional-diagnostic"),
                          ("distance_gain", "reference-distance-over-path-distance")):
        _constant(boundary[key], expected, f"profile.signal_boundary.{key}")
    _constant(boundary["omitted_effects"], list(OMITTED_EFFECTS), "profile.signal_boundary.omitted_effects")
    reference_distance = _quantity(boundary["reference_distance"], "m", 0.02, 10.0,
                                   PROVENANCE_PAGES["gain"], "profile.signal_boundary.reference_distance")
    sound_speed = _quantity(root["speed_of_sound"], "m/s", 300.0, 380.0,
                            PROVENANCE_PAGES["sound_speed"], "profile.speed_of_sound")
    startup = _keys(root["startup"], {"motion_prehistory", "audio_prehistory"}, "profile.startup")
    _constant(startup["motion_prehistory"], "constant-initial-speed-before-zero", "profile.startup.motion_prehistory")
    _constant(startup["audio_prehistory"], "zero-before-sample-zero", "profile.startup.audio_prehistory")

    normalized = {
        "schema_version": 1, "profile_id": profile_id, "model_id": MODEL_ID,
        "contract_id": CONTRACT_ID, "sound_speed_m_s": sound_speed,
        "reference_distance_m": reference_distance, "rotors": {}, "microphones": [],
        "motion_prehistory": startup["motion_prehistory"],
        "audio_prehistory": startup["audio_prehistory"],
        "directivity": boundary["directivity"], "distance_gain": boundary["distance_gain"],
    }
    rotors = _keys(root["rotors"], {"horn", "drum"}, "profile.rotors")
    for name in ("horn", "drum"):
        path = f"profile.rotors.{name}"
        rotor = _keys(rotors[name], {"motion", "geometry", "initial_state", "initial_command"}, path)
        motion = _keys(rotor["motion"], {"slow_speed", "fast_speed", "tau_up", "tau_down", "direction"}, f"{path}.motion")
        values = {}
        for key, target, unit, low, high, basis in (
            ("slow_speed", "slow_rad_s", "rad/s", 0.0, 200.0, "speed"),
            ("fast_speed", "fast_rad_s", "rad/s", 0.0, 200.0, "speed"),
            ("tau_up", "tau_up_s", "s", 0.001, 60.0, "tau"),
            ("tau_down", "tau_down_s", "s", 0.001, 60.0, "tau"),
            ("direction", "direction", "1", -1.0, 1.0, "direction"),
        ):
            values[target] = _quantity(motion[key], unit, low, high, PROVENANCE_PAGES[basis], f"{path}.motion.{key}")
        if values["direction"] not in (-1.0, 1.0):
            _fail(f"{path}.motion.direction", "must be exactly -1 or +1")
        values["direction"] = int(values["direction"])
        if values["slow_rad_s"] > values["fast_rad_s"]:
            _fail(f"{path}.motion", "slow speed cannot exceed fast speed")
        geometry = _keys(rotor["geometry"], {"axis_origin", "radius"}, f"{path}.geometry")
        origin = _quantity(geometry["axis_origin"], "m", -10.0, 10.0,
                           PROVENANCE_PAGES["geometry"], f"{path}.geometry.axis_origin", vector=True)
        radius = _quantity(geometry["radius"], "m", 0.0, 1.0,
                           PROVENANCE_PAGES["geometry"], f"{path}.geometry.radius")
        initial = _keys(rotor["initial_state"], {"angle", "speed"}, f"{path}.initial_state")
        angle = _quantity(initial["angle"], "rad", 0.0, math.tau,
                          PROVENANCE_PAGES["initial"], f"{path}.initial_state.angle")
        if angle >= math.tau:
            _fail(f"{path}.initial_state.angle", "must be less than 2*pi")
        speed = _quantity(initial["speed"], "rad/s", 0.0, 200.0,
                          PROVENANCE_PAGES["initial"], f"{path}.initial_state.speed")
        if type(rotor["initial_command"]) is not str or rotor["initial_command"] not in ("chorale", "tremolo"):
            _fail(f"{path}.initial_command", "must be chorale or tremolo; no STOP command exists")
        if radius * max(speed, values["slow_rad_s"], values["fast_rad_s"]) > MAX_RIM_SPEED_RATIO * sound_speed:
            _fail(path, "maximum rim speed exceeds 0.25 of sound speed")
        normalized["rotors"][name] = {
            "origin_m": origin, "radius_m": radius, "motion": values,
            "initial_phase_rad": angle, "initial_speed_rad_s": speed,
            "initial_command": rotor["initial_command"],
        }

    microphones = root["microphones"]
    if type(microphones) is not list or len(microphones) != 2:
        _fail("profile.microphones", "must contain left and right records in that order")
    for i, name in enumerate(("left", "right")):
        path = f"profile.microphones[{i}]"
        microphone = _keys(microphones[i], {"id", "position"}, path)
        _constant(microphone["id"], name, f"{path}.id")
        position = _quantity(microphone["position"], "m", -10.0, 10.0,
                             PROVENANCE_PAGES["microphone"], f"{path}.position", vector=True)
        for rotor_name, rotor in normalized["rotors"].items():
            dx, dy, dz = [position[k] - rotor["origin_m"][k] for k in range(3)]
            horizontal = math.hypot(dx, dy)
            minimum = math.hypot(horizontal - rotor["radius_m"], dz)
            maximum = math.hypot(horizontal + rotor["radius_m"], dz)
            if minimum < MIN_CLEARANCE_M:
                _fail(path, f"{rotor_name} full-orbit clearance is below 0.02 m")
            if maximum > MAX_PATH_M:
                _fail(path, f"{rotor_name} full-orbit path exceeds 20 m")
        normalized["microphones"].append({"id": name, "position_m": position})

    unknowns = _keys(root["unknowns"], set(UNKNOWN_UNITS), "profile.unknowns")
    for key, unit in UNKNOWN_UNITS.items():
        path = f"profile.unknowns.{key}"
        record = _keys(unknowns[key], {"value", "unit", "evidence", "required_acquisition"}, path)
        _constant(record["value"], None, f"{path}.value")
        _constant(record["unit"], unit, f"{path}.unit")
        _evidence(record["evidence"], "unknown", PROVENANCE_PAGES["unknown"], f"{path}.evidence")
        _text(record["required_acquisition"], f"{path}.required_acquisition")
    return normalized


def validate_profile(profile: Any) -> dict:
    _admit(profile)
    return profile


def normalized_profile(profile: Any) -> dict:
    return _admit(profile)


def canonical_json(profile: Any) -> bytes:
    validate_profile(profile)
    return json.dumps(profile, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def authoring_sha256(profile: Any) -> str:
    return hashlib.sha256(canonical_json(profile)).hexdigest()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            _fail("JSON", f"duplicate object key {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    _fail("JSON", f"nonfinite constant {value!r} is forbidden")


def load_profile_with_digest(path: str | Path) -> tuple[dict, str]:
    """Read at most 128 KiB plus one byte from a regular file, once."""
    if not isinstance(path, (str, Path)):
        _fail("input", "path must be a string or pathlib.Path")
    try:
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NONBLOCK", 0)
        fd = os.open(path, flags)
        with os.fdopen(fd, "rb") as stream:
            metadata = os.fstat(stream.fileno())
            if not stat.S_ISREG(metadata.st_mode):
                _fail("input", "must be a regular file")
            if metadata.st_size > MAX_INPUT_BYTES:
                _fail("input", f"exceeds {MAX_INPUT_BYTES} bytes")
            data = stream.read(MAX_INPUT_BYTES + 1)
    except (OSError, ValueError) as error:
        if isinstance(error, RotaryProfileError):
            raise
        raise RotaryProfileError(f"input: {error}") from error
    if not data or len(data) > MAX_INPUT_BYTES:
        _fail("input", "empty or oversized file")
    try:
        text = data.decode("utf-8")
        profile = json.loads(text, object_pairs_hook=_unique_object,
                             parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
        if isinstance(error, RotaryProfileError):
            raise
        raise RotaryProfileError(f"input: invalid bounded UTF-8 JSON ({error})") from error
    return validate_profile(profile), hashlib.sha256(data).hexdigest()


def load_profile(path: str | Path) -> dict:
    return load_profile_with_digest(path)[0]


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise RotaryProfileError(f"arguments: {message}")


def main(argv: list[str] | None = None) -> int:
    try:
        parser = _Parser(description=__doc__)
        parser.add_argument("--input", required=True, type=Path)
        parser.add_argument("--normalized", action="store_true",
                            help="include a fresh normalized SI mapping in the result")
        args = parser.parse_args(argv)
        profile, digest = load_profile_with_digest(args.input)
        result = {"status": "admitted", "schema_version": 1,
                  "model_id": MODEL_ID, "contract_id": CONTRACT_ID,
                  "profile_id": profile["profile_id"], "source_file_sha256": digest,
                  "authoring_sha256": authoring_sha256(profile),
                  "physical_status": "unmeasured"}
        if args.normalized:
            result["normalized"] = normalized_profile(profile)
        print(json.dumps(result, sort_keys=True, allow_nan=False))
        return 0
    except RotaryProfileError as error:
        print(json.dumps({"status": "rejected", "error": str(error)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
