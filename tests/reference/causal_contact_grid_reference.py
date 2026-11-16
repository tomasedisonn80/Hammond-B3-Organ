"""Independent exact oracle for the synthetic ``causal-contact-grid-v1`` model.

Public API: ``evaluate_case(case, *, close_observation=True) -> dict``.  ``case``
is a mapping with the following JSON-compatible, normalized snake_case fields::

    {
        "sample_rate_hz": 48000,
        "frames": 1,
        "keys": [{
            "press_units_per_tick": 3,
            "release_units_per_tick": 2,
            "contacts": [{"off": 1, "on": 4}, ...]  # exactly nine
        }],  # one through four active keys
        "targets": [{"tick": 0, "key_index": 0, "position": 10}]
    }

``targets`` may be omitted, meaning no commands.  Extra mapping fields are
ignored, permitting fixture names and provenance.  Lists or tuples are accepted;
all numeric fields must be plain Python integers (booleans are rejected).  The
entire input is validated before trajectory reconstruction.  Invalid inputs
raise ``OracleInputError``, a ``ValueError`` carrying ``path`` and ``reason``.

The default observes ``frames * 65536`` ticks and closes the observation.  Targets
at that endpoint are closure commands: they count and may change target/anchor,
but produce no travel or edges.  This also defines a zero-frame observation.
With ``close_observation=False``, endpoint targets are rejected; the snapshot is
``ready`` for zero frames or ``active`` otherwise.  The function describes one
whole epoch, not the native lifecycle, call capacity or failure-status API.

The result has ``model_id``, ``edges`` and ``snapshot``.  Each edge contains
``time: {tick, numerator, denominator}``, ``key_index``, ``contact_index`` and
``closed_after``.  Time is a reduced proper mixed fraction; integral times use
0/1.  The full contract snapshot uses snake_case names, including
``cursor_frames``, ``command_count``, ``edge_count`` and key ``anchor_position`` /
``anchor_tick``.  Its configuration has ``sample_rate_hz``, ``key_count`` and four
keys.  Inactive configuration and key snapshots are independently zero-padded.

Independence: reconstruct each key's whole piecewise affine path from its own
commands, splitting travel at exact arrivals.  Replay each contact over that
path, interpolate its crossings from segment endpoints using Fraction, then
globally sort all edges.  There is no native implementation import, crossing
helper, streaming interval staging, float converter, waveform or audio model.
This allocating offline oracle makes no native resource or physical claim.

Authority: docs/CAUSAL_CONTACT_GRID_CONTRACT.md and its independent admission.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

MODEL_ID = "causal-contact-grid-v1"
TICKS_PER_FRAME = 65536
FULL_TRAVEL = 1 << 48
MAX_SPEED = (1 << 32) - 1
MAX_KEYS = 4
CONTACTS_PER_KEY = 9
MAX_FRAMES = 4096
MAX_COMMANDS = 512
MAX_EDGES = 4608
SAMPLE_RATES = (44100, 48000, 96000)


class OracleInputError(ValueError):
    """A rejected explicit-grid input; no rounding or clamping is attempted."""

    def __init__(self, path: str, reason: str) -> None:
        self.path = path
        self.reason = reason
        super().__init__(f"{path}: {reason}")


def _mapping(value: Any, path: str) -> Mapping:
    if not isinstance(value, Mapping):
        raise OracleInputError(path, "expected a mapping")
    return value


def _field(value: Mapping, name: str, path: str) -> Any:
    if name not in value:
        raise OracleInputError(f"{path}.{name}", "required field is missing")
    return value[name]


def _sequence(value: Any, path: str) -> list | tuple:
    if not isinstance(value, (list, tuple)):
        raise OracleInputError(path, "expected a bounded list or tuple")
    return value


def _integer(value: Any, path: str, lower: int, upper: int) -> int:
    if type(value) is not int:
        raise OracleInputError(path, "expected an integer, excluding bool")
    if not lower <= value <= upper:
        raise OracleInputError(path, f"must be in [{lower}, {upper}]")
    return value


def _validate(case: Any, close_observation: bool) -> dict:
    if type(close_observation) is not bool:
        raise OracleInputError("close_observation", "expected bool")
    case = _mapping(case, "case")
    rate = _integer(_field(case, "sample_rate_hz", "case"),
                    "sample_rate_hz", 0, MAX_SPEED)
    if rate not in SAMPLE_RATES:
        raise OracleInputError("sample_rate_hz", f"expected one of {SAMPLE_RATES}")
    source_keys = _sequence(_field(case, "keys", "case"), "keys")
    if not 1 <= len(source_keys) <= MAX_KEYS:
        raise OracleInputError("keys", "expected one through four active keys")
    keys = []
    for index, source in enumerate(source_keys):
        path = f"keys[{index}]"
        source = _mapping(source, path)
        key = {}
        for name in ("press_units_per_tick", "release_units_per_tick"):
            key[name] = _integer(_field(source, name, path),
                                 f"{path}.{name}", 1, MAX_SPEED)
        contacts = _sequence(_field(source, "contacts", path), f"{path}.contacts")
        if len(contacts) != CONTACTS_PER_KEY:
            raise OracleInputError(f"{path}.contacts", "expected exactly nine contacts")
        key["contacts"] = []
        for contact_index, source_contact in enumerate(contacts):
            contact_path = f"{path}.contacts[{contact_index}]"
            source_contact = _mapping(source_contact, contact_path)
            off = _integer(_field(source_contact, "off", contact_path),
                           f"{contact_path}.off", 0, FULL_TRAVEL)
            on = _integer(_field(source_contact, "on", contact_path),
                          f"{contact_path}.on", 0, FULL_TRAVEL)
            if off >= on:
                raise OracleInputError(contact_path, "requires off < on")
            key["contacts"].append({"off": off, "on": on})
        keys.append(key)

    frames = _integer(_field(case, "frames", "case"), "frames", 0, MAX_FRAMES)
    source_targets = _sequence(case.get("targets", []), "targets")
    if len(source_targets) > MAX_COMMANDS:
        raise OracleInputError("targets", "at most 512 commands per epoch")
    end_tick = frames * TICKS_PER_FRAME
    if source_targets and not close_observation and frames == 0:
        raise OracleInputError("targets", "zero-frame processing cannot carry targets")
    targets = []
    for index, source in enumerate(source_targets):
        path = f"targets[{index}]"
        source = _mapping(source, path)
        targets.append({
            "tick": _integer(_field(source, "tick", path), f"{path}.tick", 0,
                             end_tick if close_observation else end_tick - 1),
            "key_index": _integer(_field(source, "key_index", path),
                                  f"{path}.key_index", 0, len(keys) - 1),
            "position": _integer(_field(source, "position", path),
                                 f"{path}.position", 0, FULL_TRAVEL),
        })
    # Domain validation of every command precedes ordering validation.
    for index in range(1, len(targets)):
        if targets[index]["tick"] < targets[index - 1]["tick"]:
            raise OracleInputError(f"targets[{index}].tick", "targets must be nondecreasing")
    return {"sample_rate_hz": rate, "frames": frames, "keys": keys, "targets": targets}


@dataclass(frozen=True)
class _Piece:
    """One nonconstant affine piece; arrivals may end at fractional ticks."""

    begin: Fraction
    end: Fraction
    first_position: int
    last_position: int


def _key_path(key: dict, commands: list[dict], end_tick: int) -> tuple[list[_Piece], dict]:
    pieces: list[_Piece] = []
    cursor = 0
    position = target = anchor_tick = anchor_position = 0

    def advance(until: int) -> None:
        nonlocal cursor, position
        if until > cursor and target != position:
            speed = key["press_units_per_tick" if target > position
                        else "release_units_per_tick"]
            duration = Fraction(abs(target - position), speed)
            moving_until = min(Fraction(until), cursor + duration)
            direction = 1 if target > position else -1
            destination = position + direction * speed * (moving_until - cursor)
            # Every segment ends at an integer command position or integer target.
            assert destination.denominator == 1
            pieces.append(_Piece(Fraction(cursor), moving_until, position,
                                 destination.numerator))
            position = destination.numerator
        cursor = until

    for command in commands:
        advance(command["tick"])
        if command["position"] != target:
            anchor_position, anchor_tick = position, command["tick"]
            target = command["position"]
    advance(end_tick)
    return pieces, {
        "position": position, "target": target,
        "anchor_position": anchor_position, "anchor_tick": anchor_tick,
        "closed": [False] * CONTACTS_PER_KEY,
    }


def _mixed_time(value: Fraction) -> dict:
    whole = value.numerator // value.denominator
    fraction = value - whole
    return {"tick": whole, "numerator": fraction.numerator,
            "denominator": fraction.denominator}


def _zero_key_config() -> dict:
    return {"press_units_per_tick": 0, "release_units_per_tick": 0,
            "contacts": [{"off": 0, "on": 0} for _ in range(CONTACTS_PER_KEY)]}


def _zero_key_snapshot() -> dict:
    return {"position": 0, "target": 0, "anchor_position": 0,
            "anchor_tick": 0, "closed": [False] * CONTACTS_PER_KEY}


def evaluate_case(case: Mapping, *, close_observation: bool = True) -> dict:
    """Return exact globally ordered edges and the canonical final snapshot.

    This pure batch function does not mutate the input or retain history between
    invocations.  For prefix checks, submit only commands actually observed at
    that cursor; ``close_observation=False`` excludes its endpoint commands.
    """
    normalized = _validate(case, close_observation)
    keys, targets = normalized["keys"], normalized["targets"]
    end_tick = normalized["frames"] * TICKS_PER_FRAME
    key_commands = [[] for _ in keys]
    for command in targets:
        key_commands[command["key_index"]].append(command)

    paths = [_key_path(key, commands, end_tick)
             for key, commands in zip(keys, key_commands)]
    exact_edges = []
    snapshots = []
    for key_index, (key, (pieces, snapshot)) in enumerate(zip(keys, paths)):
        for contact_index, contact in enumerate(key["contacts"]):
            closed = False
            for piece in pieces:
                first, last = piece.first_position, piece.last_position
                if not closed and first < contact["on"] <= last:
                    threshold, after = contact["on"], True
                elif closed and last <= contact["off"] < first:
                    threshold, after = contact["off"], False
                else:
                    continue
                # Interpolation from the independently reconstructed endpoints,
                # rather than a native anchor/remainder crossing helper.
                proportion = Fraction(threshold - first, last - first)
                time = piece.begin + (piece.end - piece.begin) * proportion
                exact_edges.append((time, key_index, contact_index, after))
                closed = after
            snapshot["closed"][contact_index] = closed
        snapshots.append(snapshot)
    exact_edges.sort(key=lambda edge: edge[:3])
    assert len(exact_edges) <= MAX_EDGES
    edges = [{"time": _mixed_time(time), "key_index": key_index,
              "contact_index": contact_index, "closed_after": after}
             for time, key_index, contact_index, after in exact_edges]
    phase = "closed" if close_observation else (
        "active" if normalized["frames"] else "ready")
    return {
        "model_id": MODEL_ID,
        "edges": edges,
        "snapshot": {
            "phase": phase,
            "config": {
                "sample_rate_hz": normalized["sample_rate_hz"],
                "key_count": len(keys),
                "keys": keys + [_zero_key_config() for _ in range(MAX_KEYS - len(keys))],
            },
            "cursor_frames": normalized["frames"],
            "command_count": len(targets),
            "edge_count": len(edges),
            "keys": snapshots + [_zero_key_snapshot() for _ in range(MAX_KEYS - len(keys))],
        },
    }
