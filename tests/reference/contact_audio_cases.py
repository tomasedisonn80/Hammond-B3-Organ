"""Frozen input definitions for the isolated causal contact audio study.

Authority: docs/CAUSAL_CONTACT_AUDIO_VALIDATION.md.  This module defines inputs,
canonical bytes and their identities only.  It imports no trajectory, waveform,
filter, converter, native probe or numerical oracle.  G01--G12 are NEW integer-
grid fixtures; they are not conversions or replacements of the retained Fxx
binary64 fixtures.  All histories start at zero/open, as the grid contract says.

Public API:
    nominal_cases()     -> tuple of 36 fresh JSON-compatible dictionaries
    stress_cases()      -> tuple of 39 fresh JSON-compatible dictionaries
    all_cases()         -> nominal_cases() + stress_cases()
    canonical_bytes(x)  -> stable UTF-8 JSON with binary64 values tagged by hex
    manifest()         -> exact canonical input hashes, no computed expectations

Grid fields use the existing independent grid oracle's snake_case vocabulary.
Each key additionally contains source_ids and gains (exactly nine entries).
origin_frame is an exact host-frame LABEL; phase_turns is phase at that epoch's
origin, and the label must not be added to the waveform phase.  targets includes
closing targets at frames*65536; consumers separate them without reordering.

The definitions are synthetic engineering inputs, not measured contact data.
Importing or hashing them gives no numerical, resource, platform or audio grade.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math


MODEL_ID = "causal-contact-audio-grid-v1"
PROTOCOL_ID = "contact-audio-exact-grid-validation-v1"
CORPUS_ID = "contact-audio-exact-grid-fixtures-v1"
RATES = (44100, 48000, 96000)
TICKS_PER_FRAME = 65536
FULL_TRAVEL = 1 << 48
MAX_SPEED = (1 << 32) - 1
NOMINAL_FRAMES = 256
NOMINAL_IDS = tuple(f"G{number:02d}" for number in range(1, 13))
STRESS_IDS = tuple(f"S{number:02d}" for number in range(13))
PROCESS_PATTERNS = ((256,), (1,), (1, 7, 3, 32, 2, 19))
DRAIN_PLANS = ((33,), (1,) * 33, (0, 7, 0, 13, 13, 0))
CAUSAL_PREFIX_FRAMES = (1, 16, 64, 128, 255)

# Dyadic thresholds deliberately give four closed contacts at half travel when
# approached from below, and five when approached from above.  There is no float
# conversion in these grid quantities.
ON = tuple(n * (FULL_TRAVEL // 32) for n in (4, 7, 10, 13, 17, 20, 23, 26, 29))
OFF = tuple(n * (FULL_TRAVEL // 32) for n in (1, 4, 7, 10, 13, 16, 19, 22, 25))


def _source(source_id: int = 7, frequency_hz: float = 997.0,
            amplitude: float = 1.0, phase_turns: float = 0.137) -> dict:
    return {"source_id": source_id, "frequency_hz": frequency_hz,
            "amplitude": amplitude, "phase_turns": phase_turns}


def _key() -> dict:
    return {
        "press_units_per_tick": 1 << 28,
        "release_units_per_tick": 1 << 27,
        "contacts": [{"off": off, "on": on} for off, on in zip(OFF, ON)],
        "source_ids": [7] * 9,
        "gains": [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
    }


def _target(tick: int, position: int, key_index: int = 0) -> dict:
    return {"tick": tick, "key_index": key_index, "position": position}


def _base(recipe_id: str, rate: int, *, frames: int = NOMINAL_FRAMES) -> dict:
    return {
        "schema_version": 1,
        "model_id": MODEL_ID,
        "corpus_id": CORPUS_ID,
        "evidence_class": "synthetic",
        "fixture_id": f"{recipe_id}-{rate}-v1",
        "recipe_id": recipe_id,
        "sample_rate_hz": rate,
        "frames": frames,
        "origin_frame": 0,
        "sources": [_source()],
        "keys": [_key()],
        "targets": [_target(0, FULL_TRAVEL),
                    _target(48 * TICKS_PER_FRAME, 0)],
    }


def _identical_contacts(key: dict, off: int, on: int) -> None:
    key["contacts"] = [{"off": off, "on": on} for _ in range(9)]


def _ordered(targets: list[dict]) -> list[dict]:
    # Python's stable sort preserves the supplied order of tied commands.
    return sorted(targets, key=lambda target: target["tick"])


def _nominal(number: int, rate: int) -> dict:
    case = _base(f"G{number:02d}", rate)
    key, source = case["keys"][0], case["sources"][0]
    q, tick = FULL_TRAVEL, TICKS_PER_FRAME
    if number == 1:
        key["gains"] = [0.0] * 9
    elif number == 2:
        source.update(frequency_hz=0.0, phase_turns=0.25)
    elif number in (3, 4):
        # Default contact 4 makes at exactly 17/2 host frames.  These phases
        # make the mathematical phase 5/4 or 1 turn there, without a rounded
        # duration or a rate-dependent decimal phase construction.
        source.update(frequency_hz=rate / 32.0,
                      phase_turns=63 / 64 if number == 3 else 47 / 64)
    elif number == 5:
        source["frequency_hz"] = float(2 * rate // 5)
    elif number == 6:
        key["gains"] = [1 / 18] * 9
        second = _key()
        second["gains"][4] = 0.5
        case["keys"].append(second)
        case["targets"] = _ordered([
            _target(16 * tick, q), _target(64 * tick, 0),
            _target(128 * tick, q), _target(192 * tick, 0),
            _target(23 * tick + 128, q, 1), _target(83 * tick + 128, 0, 1),
        ])
    elif number == 7:
        key["gains"] = [1 / 9] * 9
        case["targets"] = [_target(0, q // 2), _target(128 * tick, 0)]
    elif number == 8:
        key["gains"] = [1 / 9] * 9
        case["targets"] = [_target(0, q), _target(32 * tick, q // 2),
                           _target(128 * tick, 0)]
    elif number == 9:
        key["gains"] = [1 / 9] * 9
        case["targets"] = [_target(0, q), _target(6 * tick, 0),
                           _target(12 * tick, q), _target(12 * tick, q),
                           _target(17 * tick, q), _target(72 * tick, 0)]
    elif number == 10:
        key["contacts"][4] = {"off": 3 * q // 8, "on": q // 2}
        key["gains"][4] = 0.5
        second = copy.deepcopy(key)
        second["gains"][4] = -0.5
        case["keys"].append(second)
        case["targets"] = [
            _target(0, q), _target(0, q, 1),
            _target(8 * tick, 0), _target(8 * tick, q),
            _target(8 * tick, q, 1), _target(8 * tick, 0, 1),
            _target(72 * tick, 0), _target(72 * tick, 0, 1),
        ]
    elif number == 11:
        key["contacts"][4] = {"off": 3 * q // 8, "on": 2049 * (q // 4096)}
        case["targets"] = [_target(0, 513 * (q // 1024)),
                           _target(64 * tick + tick // 4, 0)]
    elif number == 12:
        key["press_units_per_tick"] = 1 << 29
        key["release_units_per_tick"] = 1 << 28
        key["gains"] = [1 / 9] * 9
        case["targets"] = [_target(0, q), _target(256 * tick, 0)]
    else:
        raise ValueError("nominal recipe must be G01..G12")
    return case


def _stress(number: int, rate: int) -> dict:
    frames = (0, 1, 1, 1, 256, 4, 256, 64, 1, 64, 256, 256, 1)[number]
    case = _base(f"S{number:02d}", rate, frames=frames)
    key, source = case["keys"][0], case["sources"][0]
    q, tick, speed = FULL_TRAVEL, TICKS_PER_FRAME, MAX_SPEED
    if number == 0:
        case["origin_frame"] = -q
        case["targets"] = [_target(0, q), _target(0, 0), _target(0, q)]
    elif number == 1:
        case["origin_frame"] = q
        key.update(press_units_per_tick=speed, release_units_per_tick=speed)
        _identical_contacts(key, 0, 1)
        case["targets"] = [_target(0, 1), _target(tick, 0)]
    elif number == 2:
        key.update(press_units_per_tick=1 << 20, release_units_per_tick=1 << 20)
        _identical_contacts(key, (tick // 2) * (1 << 20), tick * (1 << 20))
        source.update(frequency_hz=0.0, phase_turns=0.25)
        case["targets"] = [_target(0, q), _target(tick, 0)]
    elif number == 3:
        key.update(press_units_per_tick=1 << 20, release_units_per_tick=1 << 20)
        _identical_contacts(key, 0, 128 * (1 << 20))
        source.update(frequency_hz=0.0, phase_turns=0.25)
        case["targets"] = [_target(0, q), _target(tick // 2, 0)]
    elif number == 4:
        key.update(press_units_per_tick=1, release_units_per_tick=1)
        _identical_contacts(key, q - 1, q)
        key["contacts"][0] = {"off": 0, "on": 1}
        key["gains"] = [1.0] + [0.0] * 8
        case["targets"] = [_target(0, q), _target(128 * tick, 0)]
    elif number == 5:
        key.update(press_units_per_tick=speed, release_units_per_tick=speed)
        key["contacts"] = [{"off": on - 1, "on": on}
                           for on in (9, 1, 9, 5, 2, 8, 3, 7, 4)]
        key["gains"] = [1 / 9] * 9
        source["frequency_hz"] = float(9 * rate // 20)
        case["targets"] = [_target(0, q), _target(2 * tick, 0)]
    elif number == 6:
        # Reverse configuration order and include ID91 to expose treating a
        # public source ID as an array index or assuming sorted source entries.
        ids = tuple(range(1, 36)) + (91,)
        case["sources"] = list(reversed([
            _source(source_id, rate * (i + 1) / 128,
                    1 / (1 + i % 4), (i % 16) / 16)
            for i, source_id in enumerate(ids)
        ]))
        case["keys"] = [_key() for _ in range(4)]
        targets = []
        for k, route_key in enumerate(case["keys"]):
            route_key["source_ids"] = list(ids[9 * k:9 * (k + 1)])
            route_key["gains"] = [(-1.0 if (k + c) % 3 == 0 else 1.0) / 36
                                  for c in range(9)]
            targets.extend([_target(k * (3 * tick + 128), q, k),
                            _target((128 + k) * tick, 0, k)])
        case["targets"] = _ordered(targets)
    elif number in (7, 8, 9):
        key.update(press_units_per_tick=speed, release_units_per_tick=speed)
        _identical_contacts(key, 0, 1)
        source.update(frequency_hz=0.0, phase_turns=0.25)
        case["targets"] = [_target(0, 1), _target(frames * tick, 0)]
        if number == 7:
            key["gains"] = [1.0, 2.0 ** -54, -1.0] + [0.0] * 6
        elif number == 8:
            source["amplitude"] = float.fromhex("0x0.0000000000001p-1022")
            key["gains"][4] = float.fromhex("0x0.0000000000001p-1022")
        else:
            source["amplitude"] = float.fromhex("0x1.0000000000000p-1022")
    elif number == 10:
        # Constructive A50 equal-display roots, retained as new grid inputs.
        start = 255 * tick - 1
        key.update(press_units_per_tick=speed, release_units_per_tick=speed - 1)
        _identical_contacts(key, speed - 2, speed - 1)
        source.update(frequency_hz=0.0, phase_turns=0.25)
        case["origin_frame"] = -q
        case["targets"] = [_target(start, speed - 1), _target(start + 1, 0)]
    elif number == 11:
        # A50's wide exact interval inside centered cell 65535.
        start = 256 * 65535 - 128
        key.update(press_units_per_tick=speed, release_units_per_tick=speed - 1)
        _identical_contacts(key, 0, 1)
        source.update(frequency_hz=0.0, phase_turns=0.25)
        case["origin_frame"] = q
        case["targets"] = [_target(start, 1), _target(start + 255, 0)]
    elif number == 12:
        key.update(press_units_per_tick=speed, release_units_per_tick=speed)
        _identical_contacts(key, 0, 1)
        key["gains"] = [1 / 36] * 9
        case["keys"] = [copy.deepcopy(key) for _ in range(4)]
        case["targets"] = [_target(t, 1 if t % 2 == 0 else 0, k)
                           for t in range(128) for k in range(4)]
    else:
        raise ValueError("stress recipe must be S00..S12")
    return case


def nominal_cases() -> tuple[dict, ...]:
    """Return the 12 recipes x three rates, in recipe then rate order."""
    return tuple(_nominal(number, rate) for number in range(1, 13) for rate in RATES)


def stress_cases() -> tuple[dict, ...]:
    """Return the 13 explicit stress recipes x three rates in frozen order."""
    return tuple(_stress(number, rate) for number in range(13) for rate in RATES)


def all_cases() -> tuple[dict, ...]:
    return nominal_cases() + stress_cases()


def _canonical(value):
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("canonical fixture floats must be finite")
        return {"binary64": value.hex()}
    if isinstance(value, dict):
        if any(type(key) is not str for key in value):
            raise TypeError("canonical fixture mapping keys must be strings")
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if value is None or type(value) in (str, int, bool):
        return value
    raise TypeError(f"unsupported canonical fixture type: {type(value).__name__}")


def canonical_bytes(value) -> bytes:
    """Sorted keys, compact separators, binary64 hex tags, exactly one LF."""
    return (json.dumps(_canonical(value), sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def manifest() -> dict:
    cases = all_cases()
    return {
        "schema_version": 1,
        "corpus_id": CORPUS_ID,
        "protocol_id": PROTOCOL_ID,
        "evidence_class": "synthetic",
        "canonical_encoding": "sorted-compact-ascii-json-binary64-hex-tags-LF-v1",
        "nominal_count": 36,
        "stress_count": 39,
        "fixture_count": len(cases),
        "rates_hz": list(RATES),
        "cases": [{"fixture_id": case["fixture_id"],
                   "bytes": len(canonical_bytes(case)),
                   "sha256": hashlib.sha256(canonical_bytes(case)).hexdigest()}
                  for case in cases],
    }


if __name__ == "__main__":
    # A read-only identity listing.  No files, numerical expectations or renders.
    print(json.dumps(manifest(), sort_keys=True, indent=2))
