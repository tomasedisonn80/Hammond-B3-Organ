"""Bounded, exact offline trajectory conversion to the causal contact grid.

This module certifies only the admitted finite synthetic trajectory subset.
It does not render audio, mutate the original reference, call a native process,
or import a test oracle. The binary64 sidecar is the canonical input authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
import platform
import re
import struct
import time

import contact_switching_io as admission
import fractional_contact_reference as reference


CONVERSION_ID = "fractional-to-contact-grid-rne-v1"
SOURCE_MODEL_ID = "fractional-contact-reference-v1"
TARGET_MODEL_ID = "causal-contact-grid-v1"
TICKS = 1 << 16
TRAVEL = 1 << 48
MAX_RATIONAL_BITS = 4096
MAX_TRANSIENT_BITS = 8192
MAX_SEGMENTS = 1032
MAX_EDGES = 4608
MAX_ARRIVALS = 512
MAX_EVENTS = 5634
MAX_UNION_KNOTS = 4096
MAX_WORK_UNITS = 1_000_000
MAX_CERTIFICATE_BYTES = 32 * 1024 * 1024
MAX_TRANSPORT_BYTES = 131072
MAX_REFUSAL_BYTES = 8192
IMPLEMENTATION_PATHS = (
    "tools/contact_grid_conversion.py", "tools/convert_contact_grid.py",
    "tools/contact_switching_io.py", "tools/fractional_contact_reference.py",
)
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", re.ASCII)
_HASH = re.compile(r"[0-9a-f]{64}", re.ASCII)
_BITS = re.compile(r"[0-9a-f]{16}", re.ASCII)
_INTEGER_TEXT = re.compile(r"(?:0|-[1-9][0-9]*|[1-9][0-9]*)", re.ASCII)
_POSITIVE_TEXT = re.compile(r"[1-9][0-9]*", re.ASCII)
_ZERO = Fraction(0)
_ONE = Fraction(1)
_POSITION_LIMIT = Fraction(1, 1 << 18)
_ROOT_LIMIT = Fraction(1, 1 << 10)


class ConversionRefusal(ValueError):
    """A deterministic stage/path and a bounded exact JSON witness."""

    def __init__(self, code: str, path: str, witness: dict):
        envelope = {"schema_version": 1, "conversion_id": CONVERSION_ID,
                    "status": "refused", "code": code, "path": path,
                    "witness": witness}
        try:
            size = len(json.dumps(envelope, sort_keys=True, separators=(",", ":"),
                                  ensure_ascii=True, allow_nan=False).encode("ascii")) + 1
        except (TypeError, ValueError, OverflowError, RecursionError):
            size = MAX_REFUSAL_BYTES + 1
        if size > MAX_REFUSAL_BYTES:
            code, path, witness = "resource", "diagnostic", {"reason": "diagnostic-size"}
        self.code, self.path, self.witness = code, path, witness
        super().__init__(f"{code} at {path}")


def _refuse(code, path, **witness):
    raise ConversionRefusal(code, path, witness)


def _r(value: Fraction) -> dict:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def _sign(value: Fraction) -> int:
    return (value > 0) - (value < 0)


class _Budget:
    def __init__(self, deadline):
        if deadline is not None:
            try:
                valid = type(deadline) in (int, float) and math.isfinite(deadline)
            except OverflowError:
                valid = False
            if not valid:
                _refuse("input", "deadline", reason="finite-monotonic-deadline-required")
        self.deadline = deadline
        self.work = 0
        self.check("start")

    def check(self, path):
        if self.deadline is not None and time.monotonic() >= self.deadline:
            _refuse("resource", path, reason="deadline")

    def step(self, path, count=1):
        self.check(path)
        if self.work + count > MAX_WORK_UNITS:
            _refuse("resource", path, reason="work-units", limit=MAX_WORK_UNITS)
        self.work += count

    def rational(self, value, path):
        if (abs(value.numerator).bit_length() > MAX_RATIONAL_BITS
                or value.denominator.bit_length() > MAX_RATIONAL_BITS):
            _refuse("resource", path, reason="rational-bits", limit=MAX_RATIONAL_BITS,
                    numerator_bits=abs(value.numerator).bit_length(),
                    denominator_bits=value.denominator.bit_length())
        return value

    def q(self, numerator, denominator=1, path="arithmetic"):
        if (abs(numerator).bit_length() > MAX_TRANSIENT_BITS
                or abs(denominator).bit_length() > MAX_TRANSIENT_BITS):
            _refuse("resource", path, reason="transient-bits", limit=MAX_TRANSIENT_BITS)
        return self.rational(Fraction(numerator, denominator), path)

    def f(self, value, path):
        return self.rational(Fraction.from_float(value), path)

    def calc(self, operation, left, right, path="arithmetic"):
        # Every operand was checked at construction. Fraction operations and
        # comparisons use products of at most two <=4096-bit operands, hence
        # no transient product can exceed the separate 8192-bit bound.
        self.rational(left, path)
        self.rational(right, path)
        if operation == "+":
            value = left + right
        elif operation == "-":
            value = left - right
        elif operation == "*":
            value = left * right
        else:
            value = left / right
        return self.rational(value, path)


class _SortKey:
    __slots__ = ("value", "budget", "path")

    def __init__(self, value, budget, path):
        self.value, self.budget, self.path = value, budget, path

    def __lt__(self, other):
        self.budget.step(self.path)
        return self.value < other.value


def _ordered(values, key, budget, path):
    def counted(value):
        budget.step(path)
        return _SortKey(key(value), budget, path)
    return sorted(values, key=counted)


def _rne(value: Fraction) -> int:
    quotient, remainder = divmod(value.numerator, value.denominator)
    doubled = 2 * remainder
    return quotient + (doubled > value.denominator
                       or (doubled == value.denominator and quotient % 2 == 1))


def _canonical_document(document):
    if type(document) is not admission.InputDocument:
        _refuse("input", "document", reason="InputDocument-required")
    if (type(document.fixture_id) is not str
            or _IDENTIFIER.fullmatch(document.fixture_id) is None):
        _refuse("input", "fixture_id", reason="invalid-identifier")
    if (type(document.input_sha256) is not str
            or _HASH.fullmatch(document.input_sha256) is None):
        _refuse("input", "input_sha256", reason="invalid-sha256")
    if type(document.input_size_bytes) is not int or not 0 < document.input_size_bytes <= admission.MAX_INPUT_BYTES:
        _refuse("input", "input_bytes", reason="invalid-input-size")
    try:
        case = reference.validate_case(document.case)
    except (ValueError, TypeError, OverflowError) as error:
        _refuse("input", "case", reason="invalid-case", detail=str(error)[:256])
    return case


def _binary64(value):
    return struct.pack(">d", value).hex()


def _sidecar(case):
    return {
        "sources": [{"source_id": source.source_id,
                     "frequency_hz": _binary64(source.frequency_hz),
                     "amplitude": _binary64(source.amplitude),
                     "phase_turns": _binary64(source.phase_turns)} for source in case.sources],
        "keys": [{"key_id": key.key_id, "press_seconds": _binary64(key.press_seconds),
                  "release_seconds": _binary64(key.release_seconds),
                  "on": list(map(_binary64, key.on9)), "off": list(map(_binary64, key.off9)),
                  "source_ids": list(key.source_ids9), "gains": list(map(_binary64, key.gains9))}
                 for key in case.keys],
        "targets": [{"frame": target.frame, "fraction": _binary64(target.fraction),
                     "key_id": target.key_id, "target": _binary64(target.target)}
                    for target in case.targets],
    }


@dataclass(frozen=True)
class _Key:
    press: Fraction
    release: Fraction
    off: tuple
    on: tuple


@dataclass(frozen=True)
class _Command:
    ordinal: int
    key: int
    time: Fraction
    position: Fraction


@dataclass(frozen=True)
class _Segment:
    start: Fraction
    end: Fraction
    position: Fraction
    velocity: Fraction


@dataclass(frozen=True)
class _Root:
    time: Fraction
    anchor_time: Fraction
    anchor_position: Fraction
    threshold: Fraction
    speed: Fraction


@dataclass
class _Replay:
    segments: list
    edges: dict
    arrivals: dict
    commands: dict
    final: list
    events: dict


def _replay(keys, commands, end, budget, name):
    replay = _Replay([[] for _ in keys], {}, {}, {}, [], {"B:0": _ZERO, "B:1": end})
    by_key = [[] for _ in keys]
    for command in commands:
        budget.check(name + ".commands")
        by_key[command.key].append(command)
    segment_count = 0

    def segment(key_index, start, stop, position, velocity):
        nonlocal segment_count
        budget.step(name + ".segments")
        if segment_count >= MAX_SEGMENTS:
            _refuse("resource", name + ".segments", reason="segments", limit=MAX_SEGMENTS)
        replay.segments[key_index].append(_Segment(start, stop, position, velocity))
        segment_count += 1

    def root(collection, label, when, anchor_time, anchor_position, threshold, speed):
        budget.step(name + ".roots")
        cap = MAX_EDGES if collection is replay.edges else MAX_ARRIVALS
        if len(collection) >= cap:
            _refuse("resource", name + ".roots", reason="edges" if collection is replay.edges else "arrivals", limit=cap)
        if len(replay.events) >= MAX_EVENTS:
            _refuse("resource", name + ".events", reason="labeled-events", limit=MAX_EVENTS)
        collection[label] = _Root(when, anchor_time, anchor_position, threshold, speed)
        replay.events[label] = when

    for key_index, key in enumerate(keys):
        budget.check(name + ".keys")
        current_time = position = target = anchor_time = anchor_position = _ZERO
        closed = [False] * 9
        edge_counts = [[0, 0] for _ in range(9)]
        arrival_counts = {-1: 0, 1: 0}

        def advance(stop):
            nonlocal current_time, position
            budget.check(name + ".advance")
            if stop <= current_time:
                return
            direction = _sign(budget.calc("-", target, position))
            if direction:
                speed = key.press if direction > 0 else key.release
                velocity = speed if direction > 0 else -speed
                distance = abs(budget.calc("-", target, anchor_position))
                arrival = budget.calc("+", anchor_time, budget.calc("/", distance, speed))
                moving_end = min(stop, arrival)
                next_position = (target if moving_end == arrival else
                                 budget.calc("+", anchor_position,
                                             budget.calc("*", velocity,
                                                         budget.calc("-", moving_end, anchor_time))))
                segment(key_index, current_time, moving_end, position, velocity)
                for contact in range(9):
                    budget.step(name + ".contacts")
                    threshold = key.on[contact] if direction > 0 else key.off[contact]
                    eligible = ((not closed[contact] and position <= threshold <= next_position)
                                if direction > 0 else
                                (closed[contact] and next_position <= threshold <= position))
                    if eligible:
                        when = budget.calc("+", anchor_time,
                                           budget.calc("/", abs(budget.calc("-", threshold, anchor_position)), speed))
                        bit = int(direction > 0)
                        occurrence = edge_counts[contact][bit]
                        label = f"E:{key_index}:{contact}:{bit}:{occurrence}"
                        root(replay.edges, label, when, anchor_time, anchor_position, threshold, speed)
                        edge_counts[contact][bit] += 1
                        closed[contact] = bool(bit)
                position, current_time = next_position, moving_end
                if moving_end == arrival:
                    label = f"A:{key_index}:{direction}:{arrival_counts[direction]}"
                    root(replay.arrivals, label, arrival, anchor_time, anchor_position, target, speed)
                    arrival_counts[direction] += 1
            if current_time < stop:
                segment(key_index, current_time, stop, position, _ZERO)
                current_time = stop

        for command in by_key[key_index]:
            advance(command.time)
            budget.step(name + ".commands")
            before = _sign(budget.calc("-", target, position))
            after = _sign(budget.calc("-", command.position, position))
            repeated = command.position == target
            replay.commands[command.ordinal] = (position, before, after, repeated)
            if len(replay.events) >= MAX_EVENTS:
                _refuse("resource", name + ".events", reason="labeled-events", limit=MAX_EVENTS)
            replay.events[f"C:{command.ordinal}"] = command.time
            if not repeated:
                anchor_time, anchor_position = command.time, position
            target = command.position
        advance(end)
        replay.final.append((position, target, tuple(closed)))
    return replay


def _preorder(replay, budget, path):
    ordered = _ordered(replay.events, lambda label: (replay.events[label], label), budget, path)
    groups = []
    last_time = None
    for label in ordered:
        budget.check(path)
        when = replay.events[label]
        if last_time is None or when != last_time:
            groups.append([])
            last_time = when
        groups[-1].append(label)
    return groups


def _positions(segments, knots, budget, path):
    result = []
    index = 0
    for when in knots:
        budget.step(path)
        while index + 1 < len(segments) and when > segments[index].end:
            budget.step(path + ".segments")
            index += 1
        if not segments:
            result.append(_ZERO)
        else:
            entry = segments[index]
            result.append(budget.calc("+", entry.position,
                                      budget.calc("*", entry.velocity,
                                                  budget.calc("-", when, entry.start))))
    return result


def _transport(grid, budget):
    partitions = [] if grid["frames"] == 0 else [grid["frames"]]
    lines = [f"CGGRID1 {grid['sample_rate_hz']} {len(grid['keys'])} {grid['frames']} {len(grid['targets'])} {len(partitions)}"]
    for key in grid["keys"]:
        budget.check("transport.keys")
        fields = [key["press_units_per_tick"], key["release_units_per_tick"]]
        for contact in key["contacts"]:
            fields.extend((contact["off"], contact["on"]))
        lines.append(" ".join(map(str, fields)))
    for target in grid["targets"]:
        budget.check("transport.targets")
        lines.append(f"{target['tick']} {target['key_index']} {target['position']}")
    if partitions:
        lines.append(str(partitions[0]))
    text = "\n".join(lines) + "\n"
    raw = text.encode("ascii")
    if len(raw) > MAX_TRANSPORT_BYTES:
        _refuse("resource", "transport.text", reason="transport-bytes", limit=MAX_TRANSPORT_BYTES)
    return {"format": "CGGRID1", "text": text, "sha256": hashlib.sha256(raw).hexdigest(), "partitions": partitions}


def convert_document(document, *, deadline=None) -> dict:
    """Return a complete exact certificate result, or a witnessed refusal."""
    budget = _Budget(deadline)
    case = _canonical_document(document)
    end = budget.q(case.frames)
    tick_scale, travel_scale = budget.q(TICKS), budget.q(TRAVEL)
    source_keys, grid_keys, key_rows, scalar = [], [], [], []
    key_indices = {key.key_id: index for index, key in enumerate(case.keys)}

    def scalar_row(path, unit, source, grid):
        difference = budget.calc("-", grid, source, path)
        scalar.append({"path": path, "unit": unit, "source": _r(source),
                       "grid": _r(grid), "difference": _r(difference)})

    # Domain validity precedes every scalar collision check.
    for index, key in enumerate(case.keys):
        budget.check("grid_domain.keys")
        source_speeds, grid_speeds, speeds = [], [], []
        for kind, duration_value in (("press", key.press_seconds), ("release", key.release_seconds)):
            path = f"keys[{index}].{kind}_units_per_tick"
            duration = budget.f(duration_value, path)
            velocity = budget.calc("/", _ONE, budget.calc("*", budget.q(case.sample_rate_hz), duration), path)
            exact_speed = budget.calc("/", budget.calc("*", velocity, travel_scale), tick_scale, path)
            speed = _rne(exact_speed)
            if not 1 <= speed <= (1 << 32) - 1:
                _refuse("grid_domain", path, source_speed=_r(exact_speed), rounded=speed)
            grid_velocity = budget.q(TICKS * speed, TRAVEL, path)
            effective = budget.q(TRAVEL, TICKS * case.sample_rate_hz * speed, path)
            relative = budget.calc("/", abs(budget.calc("-", effective, duration)), duration, path)
            scalar_row(f"keys[{index}].{kind}_speed", "travel/frame", velocity, grid_velocity)
            scalar_row(f"keys[{index}].{kind}_seconds", "seconds", duration, effective)
            scalar_row(f"keys[{index}].{kind}_relative_duration_error", "ratio", _ZERO, relative)
            source_speeds.append(velocity)
            grid_speeds.append(grid_velocity)
            speeds.append(speed)
        source_off, source_on, grid_off, grid_on, contacts = [], [], [], [], []
        for contact in range(9):
            budget.check("grid_domain.contacts")
            off = budget.f(key.off9[contact], f"keys[{index}].off[{contact}]")
            on = budget.f(key.on9[contact], f"keys[{index}].on[{contact}]")
            off_units = _rne(budget.calc("*", off, travel_scale))
            on_units = _rne(budget.calc("*", on, travel_scale))
            if not 0 <= off_units < on_units <= TRAVEL:
                _refuse("grid_domain", f"keys[{index}].contacts[{contact}]",
                        source_off=_r(off), source_on=_r(on), off=off_units, on=on_units)
            rounded_off, rounded_on = budget.q(off_units, TRAVEL), budget.q(on_units, TRAVEL)
            scalar_row(f"keys[{index}].off[{contact}]", "travel", off, rounded_off)
            scalar_row(f"keys[{index}].on[{contact}]", "travel", on, rounded_on)
            source_off.append(off); source_on.append(on)
            grid_off.append(rounded_off); grid_on.append(rounded_on)
            contacts.append({"off": off_units, "on": on_units})
        source_keys.append(_Key(*source_speeds, tuple(source_off), tuple(source_on)))
        grid_keys.append(_Key(*grid_speeds, tuple(grid_off), tuple(grid_on)))
        key_rows.append({"press_units_per_tick": speeds[0], "release_units_per_tick": speeds[1], "contacts": contacts})

    source_commands = []
    for ordinal, target in enumerate(case.targets):
        budget.check("commands.admission")
        when = budget.calc("+", budget.q(target.frame), budget.f(target.fraction, "targets.fraction"))
        source_commands.append(_Command(ordinal, key_indices[target.key_id], when,
                                        budget.f(target.target, "targets.target")))
    source_commands = _ordered(source_commands, lambda command: (command.time, command.ordinal), budget, "commands.sort")
    grid_commands, target_rows = [], []
    for command in source_commands:
        budget.check("commands.round")
        tick = _rne(budget.calc("*", command.time, tick_scale))
        position = _rne(budget.calc("*", command.position, travel_scale))
        grid_commands.append(_Command(command.ordinal, command.key,
                                      budget.q(tick, TICKS), budget.q(position, TRAVEL)))
        target_rows.append({"tick": tick, "key_index": command.key, "position": position})
    for index in range(1, len(source_commands)):
        budget.check("time_collision.commands")
        left, right = source_commands[index - 1], source_commands[index]
        if left.time != right.time and grid_commands[index - 1].time == grid_commands[index].time:
            _refuse("time_collision", f"targets[{right.ordinal}].time", left_ordinal=left.ordinal,
                    right_ordinal=right.ordinal, left=_r(left.time), right=_r(right.time),
                    tick=target_rows[index]["tick"])
    for source, grid in zip(source_commands, grid_commands):
        budget.check("time_collision.boundaries")
        if _ZERO < source.time < end and not _ZERO < grid.time < end:
            _refuse("time_collision", f"targets[{source.ordinal}].time", reason="interior-to-boundary",
                    source=_r(source.time), grid=_r(grid.time), end=_r(end))

    # Identity labels for colliding equal-valued entries are in the specified
    # implicit/off/on/caller order, independent of the chronological sort.
    for index, key in enumerate(source_keys):
        budget.check("position_collision.keys")
        values = [(_ZERO, "implicit:0"), (_ONE, "implicit:1")]
        for contact in range(9):
            values.extend(((key.off[contact], f"off:{contact}"), (key.on[contact], f"on:{contact}")))
        for ordinal, target in enumerate(case.targets):
            if key_indices[target.key_id] == index:
                values.append((budget.f(target.target, "position_collision.target"), f"target:{ordinal}"))
        grouped = {}
        for value, label in values:
            grouped.setdefault(value, []).append(label)
        previous = None
        for value in _ordered(grouped, lambda value: value, budget, "position_collision.sort"):
            budget.check("position_collision.values")
            rounded = _rne(budget.calc("*", value, travel_scale))
            if previous is not None and previous[1] == rounded:
                _refuse("position_collision", f"keys[{index}]", lower=_r(previous[0]), upper=_r(value),
                        lower_labels=grouped[previous[0]], upper_labels=grouped[value], rounded=rounded)
            previous = (value, rounded)
    for source, grid in zip(source_commands, grid_commands):
        scalar_row(f"targets[{source.ordinal}].time", "frames", source.time, grid.time)
        scalar_row(f"targets[{source.ordinal}].target", "travel", source.position, grid.position)

    source = _replay(source_keys, source_commands, end, budget, "source")
    grid = _replay(grid_keys, grid_commands, end, budget, "grid")
    commands = []
    for original, rounded in zip(source_commands, grid_commands):
        budget.check("dynamic_topology.commands")
        left, right = source.commands[original.ordinal], grid.commands[original.ordinal]
        for offset, name in ((1, "before_direction"), (2, "after_direction"), (3, "repeated_target")):
            if left[offset] != right[offset]:
                _refuse("dynamic_topology", f"commands[{original.ordinal}].{name}",
                        source=left[offset], grid=right[offset], source_position=_r(left[0]), grid_position=_r(right[0]))
        commands.append({"ordinal": original.ordinal, "key_index": original.key,
                         "source_time": _r(original.time), "grid_time": _r(rounded.time),
                         "source_position": _r(left[0]), "grid_position": _r(right[0]),
                         "before_direction": left[1], "after_direction": left[2], "repeated_target": left[3]})
    for index, (left, right) in enumerate(zip(source.final, grid.final)):
        budget.check("dynamic_topology.final")
        expected = budget.q(_rne(budget.calc("*", left[1], travel_scale)), TRAVEL)
        if expected != right[1]:
            _refuse("dynamic_topology", f"final_keys[{index}].target", source=_r(left[1]), grid=_r(right[1]), expected=_r(expected))

    root_labels = []
    paired = {}
    for kind in ("edges", "arrivals"):
        budget.check("event_identity." + kind)
        left, right = getattr(source, kind), getattr(grid, kind)
        left_labels = _ordered(left, lambda label: label, budget, "event_identity.sort")
        right_labels = _ordered(right, lambda label: label, budget, "event_identity.sort")
        if left_labels != right_labels:
            different = _ordered(set(left) ^ set(right), lambda label: label, budget, "event_identity.difference")
            _refuse("event_identity", kind, source_count=len(left), grid_count=len(right),
                    first_label=different[0], source_has=different[0] in left, grid_has=different[0] in right)
        root_labels.extend(left_labels)
        paired[kind] = []
        for label in left_labels:
            budget.check("event_identity.pairs")
            paired[kind].append({"label": label, "source_time": _r(left[label].time), "grid_time": _r(right[label].time)})
    source_groups = _preorder(source, budget, "source.event_sort")
    grid_groups = _preorder(grid, budget, "grid.event_sort")
    for index, (left, right) in enumerate(zip(source_groups, grid_groups)):
        budget.check("event_order.groups")
        if left != right:
            x = min(set(left) ^ set(right))
            y = min(right) if x in left else min(left)
            labels = sorted((x, y))
            _refuse("event_order", f"preorder[{index}]", labels=labels,
                    source_times=[_r(source.events[label]) for label in labels],
                    grid_times=[_r(grid.events[label]) for label in labels],
                    source_group_index=index, grid_group_index=index,
                    source_group_count=len(source_groups), grid_group_count=len(grid_groups))
    # Equal label universes make a proper-prefix group list impossible.
    if len(source_groups) != len(grid_groups):
        _refuse("event_order", "preorder", source_group_count=len(source_groups), grid_group_count=len(grid_groups))
    final_keys = []
    for index, (left, right) in enumerate(zip(source.final, grid.final)):
        budget.check("final_contacts.keys")
        for contact in range(9):
            if left[2][contact] != right[2][contact]:
                _refuse("final_contacts", f"final_keys[{index}].closed9[{contact}]", source=left[2][contact], grid=right[2][contact])
        final_keys.append({"key_index": index, "source_position": _r(left[0]), "grid_position": _r(right[0]),
                           "source_target": _r(left[1]), "grid_target": _r(right[1]), "closed9": list(left[2])})

    position_samples = []
    max_position = _ZERO
    position_witness = None
    common_knots = {_ZERO, end}
    common_knots.update(command.time for command in source_commands)
    common_knots.update(command.time for command in grid_commands)
    for index in range(len(source_keys)):
        budget.check("position_budget.keys")
        union = set(common_knots)
        for replay in (source, grid):
            for segment in replay.segments[index]:
                budget.step("position_budget.segments")
                union.update((segment.start, segment.end))
        if len(position_samples) + len(union) > MAX_UNION_KNOTS:
            _refuse("resource", "position_samples", reason="union-knots", limit=MAX_UNION_KNOTS,
                    retained=len(position_samples), next_key_count=len(union))
        knots = _ordered(union, lambda value: value, budget, "position_budget.sort")
        original_positions = _positions(source.segments[index], knots, budget, "source.knot_positions")
        grid_positions = _positions(grid.segments[index], knots, budget, "grid.knot_positions")
        for when, left, right in zip(knots, original_positions, grid_positions):
            budget.check("position_budget.samples")
            error = abs(budget.calc("-", right, left))
            if error > _POSITION_LIMIT:
                _refuse("position_budget", f"position_samples[{len(position_samples)}]", key_index=index,
                        time=_r(when), source=_r(left), grid=_r(right), error=_r(error), limit=_r(_POSITION_LIMIT))
            if position_witness is None or error > max_position:
                max_position, position_witness = error, len(position_samples)
            position_samples.append({"key_index": index, "time": _r(when), "source": _r(left), "grid": _r(right)})

    root_bounds = []
    for label in root_labels:
        budget.check("root_budget.roots")
        original = source.edges[label] if label.startswith("E:") else source.arrivals[label]
        rounded = grid.edges[label] if label.startswith("E:") else grid.arrivals[label]
        error = abs(budget.calc("-", rounded.time, original.time))
        anchor_error = abs(budget.calc("-", rounded.anchor_time, original.anchor_time))
        position_error = abs(budget.calc("-", rounded.anchor_position, original.anchor_position))
        threshold_error = abs(budget.calc("-", rounded.threshold, original.threshold))
        speed_error = abs(budget.calc("-", rounded.speed, original.speed))
        distance = abs(budget.calc("-", original.threshold, original.anchor_position))
        first = budget.calc("/", budget.calc("+", threshold_error, position_error), rounded.speed)
        second = budget.calc("/", budget.calc("*", distance, speed_error), budget.calc("*", original.speed, rounded.speed))
        bound = budget.calc("+", budget.calc("+", anchor_error, first), second)
        for condition, reason in ((error > _ROOT_LIMIT, "time-error"), (error > bound, "triangle-inequality"), (bound > _ROOT_LIMIT, "analytic-bound")):
            if condition:
                _refuse("root_budget", label, reason=reason, error=_r(error), bound=_r(bound), limit=_r(_ROOT_LIMIT))
        root_bounds.append({"label": label, "source_anchor_time": _r(original.anchor_time),
                            "grid_anchor_time": _r(rounded.anchor_time),
                            "source_anchor_position": _r(original.anchor_position),
                            "grid_anchor_position": _r(rounded.anchor_position),
                            "source_threshold": _r(original.threshold), "grid_threshold": _r(rounded.threshold),
                            "source_speed": _r(original.speed), "grid_speed": _r(rounded.speed),
                            "error": _r(error), "bound": _r(bound)})
    # Refusal precedence is edges then arrivals; certificate arrays themselves
    # use the separately specified canonical ASCII label order (A before E).
    root_bounds = _ordered(root_bounds, lambda row: row["label"], budget, "root_bounds.sort")
    max_root = _ZERO
    root_witness = None
    for index, row in enumerate(root_bounds):
        budget.check("root_bounds.summary")
        error = budget.q(int(row["error"]["numerator"]), int(row["error"]["denominator"]))
        if root_witness is None or error > max_root:
            max_root, root_witness = error, index
    grid_case = {"sample_rate_hz": case.sample_rate_hz, "frames": case.frames,
                 "keys": key_rows, "targets": target_rows}
    transport = _transport(grid_case, budget)
    budget.check("result")
    return {"schema_version": 1, "conversion_id": CONVERSION_ID, "status": "accepted",
            "evidence_class": "synthetic", "source_model_id": SOURCE_MODEL_ID,
            "target_model_id": TARGET_MODEL_ID, "audio_accuracy": "unqualified",
            "fixture_id": document.fixture_id, "input_sha256": document.input_sha256,
            "input_bytes": document.input_size_bytes, "grid_case": grid_case,
            "sidecar": _sidecar(case), "scalar_errors": scalar, "edges": paired["edges"],
            "arrivals": paired["arrivals"], "commands": commands, "final_keys": final_keys,
            "preorder": source_groups, "position_samples": position_samples, "root_bounds": root_bounds,
            "summary": {"max_position_error": _r(max_position), "position_witness": position_witness,
                        "max_root_error": _r(max_root), "root_witness": root_witness,
                        "work_units": budget.work}, "transport": transport}


_RESULT_FIELDS = frozenset((
    "schema_version", "conversion_id", "status", "evidence_class", "source_model_id", "target_model_id",
    "audio_accuracy", "fixture_id", "input_sha256", "input_bytes", "grid_case", "sidecar", "scalar_errors",
    "edges", "arrivals", "commands", "final_keys", "preorder", "position_samples", "root_bounds", "summary", "transport",
))


class _CertificateAdmission:
    """Admit bounded shapes before reconstructing or replaying any data."""

    def __init__(self, budget):
        self.budget, self.string_bytes = budget, 0

    def obj(self, value, fields, path):
        self.budget.check(path)
        if type(value) is not dict or len(value) != len(fields) or any(type(key) is not str or key not in fields for key in value):
            _refuse("certificate", path, reason="unknown-or-missing-fields")
        return value

    def array(self, value, low, high, path):
        self.budget.check(path)
        if type(value) is not list or not low <= len(value) <= high:
            _refuse("certificate", path, reason="invalid-array-size", minimum=low, maximum=high)
        return value

    def string(self, value, low, high, path, pattern=None):
        self.budget.check(path)
        if type(value) is not str or not low <= len(value) <= high or not value.isascii():
            _refuse("certificate", path, reason="invalid-ascii-string")
        if pattern is not None and pattern.fullmatch(value) is None:
            _refuse("certificate", path, reason="invalid-string-syntax")
        self.string_bytes += len(value)
        if self.string_bytes > MAX_CERTIFICATE_BYTES:
            _refuse("resource", path, reason="certificate-bytes", limit=MAX_CERTIFICATE_BYTES)
        return value

    def integer(self, value, low, high, path):
        if type(value) is not int or not low <= value <= high:
            _refuse("certificate", path, reason="invalid-integer", minimum=low, maximum=high)
        return value

    def rational(self, value, path):
        self.obj(value, ("numerator", "denominator"), path)
        numerator = self.string(value["numerator"], 1, 1235, path + ".numerator", _INTEGER_TEXT)
        denominator = self.string(value["denominator"], 1, 1234, path + ".denominator", _POSITIVE_TEXT)
        n, d = int(numerator), int(denominator)
        result = self.budget.q(n, d, path)
        if result.numerator != n or result.denominator != d:
            _refuse("certificate", path, reason="noncanonical-rational")
        return result

    def bits(self, value, path):
        self.string(value, 16, 16, path, _BITS)
        number = struct.unpack(">d", bytes.fromhex(value))[0]
        if not math.isfinite(number) or (number == 0 and value != "0000000000000000"):
            _refuse("certificate", path, reason="noncanonical-binary64")
        return number

    def boolean(self, value, path):
        if type(value) is not bool:
            _refuse("certificate", path, reason="boolean-required")


def _admit_certificate(result, budget):
    a = _CertificateAdmission(budget)
    a.obj(result, _RESULT_FIELDS, "result")
    a.integer(result["schema_version"], 1, 1, "schema_version")
    for name, expected in (("conversion_id", CONVERSION_ID), ("status", "accepted"),
                           ("evidence_class", "synthetic"), ("source_model_id", SOURCE_MODEL_ID),
                           ("target_model_id", TARGET_MODEL_ID), ("audio_accuracy", "unqualified")):
        a.string(result[name], len(expected), len(expected), name)
        if result[name] != expected:
            _refuse("certificate", name, reason="wrong-identity")
    a.string(result["fixture_id"], 1, 64, "fixture_id", _IDENTIFIER)
    a.string(result["input_sha256"], 64, 64, "input_sha256", _HASH)
    a.integer(result["input_bytes"], 1, admission.MAX_INPUT_BYTES, "input_bytes")
    grid = a.obj(result["grid_case"], ("sample_rate_hz", "frames", "keys", "targets"), "grid_case")
    a.integer(grid["sample_rate_hz"], 44100, 96000, "grid_case.sample_rate_hz")
    a.integer(grid["frames"], 0, 4096, "grid_case.frames")
    for index, key in enumerate(a.array(grid["keys"], 1, 4, "grid_case.keys")):
        path = f"grid_case.keys[{index}]"
        a.obj(key, ("press_units_per_tick", "release_units_per_tick", "contacts"), path)
        for field in ("press_units_per_tick", "release_units_per_tick"):
            a.integer(key[field], 1, (1 << 32) - 1, path + "." + field)
        for contact, value in enumerate(a.array(key["contacts"], 9, 9, path + ".contacts")):
            a.obj(value, ("off", "on"), path + f".contacts[{contact}]")
            for field in ("off", "on"):
                a.integer(value[field], 0, TRAVEL, path + f".contacts[{contact}].{field}")
    for index, target in enumerate(a.array(grid["targets"], 0, 512, "grid_case.targets")):
        path = f"grid_case.targets[{index}]"
        a.obj(target, ("tick", "key_index", "position"), path)
        a.integer(target["tick"], 0, 4096 * TICKS, path + ".tick")
        a.integer(target["key_index"], 0, 3, path + ".key_index")
        a.integer(target["position"], 0, TRAVEL, path + ".position")
    sidecar = a.obj(result["sidecar"], ("sources", "keys", "targets"), "sidecar")
    sources, keys, targets = [], [], []
    for index, source in enumerate(a.array(sidecar["sources"], 1, 36, "sidecar.sources")):
        path = f"sidecar.sources[{index}]"
        a.obj(source, ("source_id", "frequency_hz", "amplitude", "phase_turns"), path)
        sid = a.integer(source["source_id"], 1, 91, path + ".source_id")
        sources.append(reference.Source(sid, *(a.bits(source[name], path + "." + name)
                                              for name in ("frequency_hz", "amplitude", "phase_turns"))))
    for index, key in enumerate(a.array(sidecar["keys"], 1, 4, "sidecar.keys")):
        path = f"sidecar.keys[{index}]"
        a.obj(key, ("key_id", "press_seconds", "release_seconds", "on", "off", "source_ids", "gains"), path)
        name = a.string(key["key_id"], 1, 64, path + ".key_id", _IDENTIFIER)
        press = a.bits(key["press_seconds"], path + ".press_seconds")
        release = a.bits(key["release_seconds"], path + ".release_seconds")
        arrays = {}
        for field in ("on", "off", "source_ids", "gains"):
            values = a.array(key[field], 9, 9, path + "." + field)
            arrays[field] = tuple(a.integer(value, 1, 91, path + f".{field}[{contact}]") if field == "source_ids"
                                  else a.bits(value, path + f".{field}[{contact}]") for contact, value in enumerate(values))
        keys.append(reference.Key(name, press, release, arrays["on"], arrays["off"], arrays["source_ids"], arrays["gains"]))
    for index, target in enumerate(a.array(sidecar["targets"], 0, 512, "sidecar.targets")):
        path = f"sidecar.targets[{index}]"
        a.obj(target, ("frame", "fraction", "key_id", "target"), path)
        targets.append(reference.Target(a.integer(target["frame"], 0, 4096, path + ".frame"),
                                        a.bits(target["fraction"], path + ".fraction"),
                                        a.string(target["key_id"], 1, 64, path + ".key_id", _IDENTIFIER),
                                        a.bits(target["target"], path + ".target")))
    for index, row in enumerate(a.array(result["scalar_errors"], 0, 1120, "scalar_errors")):
        path = f"scalar_errors[{index}]"
        a.obj(row, ("path", "unit", "source", "grid", "difference"), path)
        a.string(row["path"], 1, 128, path + ".path")
        a.string(row["unit"], 1, 32, path + ".unit")
        for field in ("source", "grid", "difference"):
            a.rational(row[field], path + "." + field)
    for field, cap in (("edges", MAX_EDGES), ("arrivals", MAX_ARRIVALS)):
        for index, row in enumerate(a.array(result[field], 0, cap, field)):
            path = f"{field}[{index}]"
            a.obj(row, ("label", "source_time", "grid_time"), path)
            a.string(row["label"], 1, 64, path + ".label")
            a.rational(row["source_time"], path + ".source_time")
            a.rational(row["grid_time"], path + ".grid_time")
    for index, row in enumerate(a.array(result["commands"], 0, 512, "commands")):
        path = f"commands[{index}]"
        a.obj(row, ("ordinal", "key_index", "source_time", "grid_time", "source_position", "grid_position", "before_direction", "after_direction", "repeated_target"), path)
        a.integer(row["ordinal"], 0, 511, path + ".ordinal")
        a.integer(row["key_index"], 0, 3, path + ".key_index")
        for field in ("source_time", "grid_time", "source_position", "grid_position"):
            a.rational(row[field], path + "." + field)
        for field in ("before_direction", "after_direction"):
            a.integer(row[field], -1, 1, path + "." + field)
        a.boolean(row["repeated_target"], path + ".repeated_target")
    for index, row in enumerate(a.array(result["final_keys"], 1, 4, "final_keys")):
        path = f"final_keys[{index}]"
        a.obj(row, ("key_index", "source_position", "grid_position", "source_target", "grid_target", "closed9"), path)
        a.integer(row["key_index"], 0, 3, path + ".key_index")
        for field in ("source_position", "grid_position", "source_target", "grid_target"):
            a.rational(row[field], path + "." + field)
        for contact, bit in enumerate(a.array(row["closed9"], 9, 9, path + ".closed9")):
            a.boolean(bit, path + f".closed9[{contact}]")
    label_count = 0
    for index, group in enumerate(a.array(result["preorder"], 1, MAX_EVENTS, "preorder")):
        a.array(group, 1, MAX_EVENTS, f"preorder[{index}]")
        label_count += len(group)
        if label_count > MAX_EVENTS:
            _refuse("certificate", "preorder", reason="labeled-event-cap")
        for item in group:
            a.string(item, 1, 64, f"preorder[{index}]")
    for index, row in enumerate(a.array(result["position_samples"], 1, MAX_UNION_KNOTS, "position_samples")):
        path = f"position_samples[{index}]"
        a.obj(row, ("key_index", "time", "source", "grid"), path)
        a.integer(row["key_index"], 0, 3, path + ".key_index")
        for field in ("time", "source", "grid"):
            a.rational(row[field], path + "." + field)
    root_fields = ("source_anchor_time", "grid_anchor_time", "source_anchor_position", "grid_anchor_position",
                   "source_threshold", "grid_threshold", "source_speed", "grid_speed", "error", "bound")
    for index, row in enumerate(a.array(result["root_bounds"], 0, MAX_EDGES + MAX_ARRIVALS, "root_bounds")):
        path = f"root_bounds[{index}]"
        a.obj(row, ("label", *root_fields), path)
        a.string(row["label"], 1, 64, path + ".label")
        for field in root_fields:
            a.rational(row[field], path + "." + field)
    summary = a.obj(result["summary"], ("max_position_error", "position_witness", "max_root_error", "root_witness", "work_units"), "summary")
    for field in ("max_position_error", "max_root_error"):
        a.rational(summary[field], "summary." + field)
    for field, cap in (("position_witness", MAX_UNION_KNOTS), ("root_witness", MAX_EDGES + MAX_ARRIVALS)):
        if summary[field] is not None:
            a.integer(summary[field], 0, cap - 1, "summary." + field)
    a.integer(summary["work_units"], 0, MAX_WORK_UNITS, "summary.work_units")
    transport = a.obj(result["transport"], ("format", "text", "sha256", "partitions"), "transport")
    a.string(transport["format"], 7, 7, "transport.format")
    a.string(transport["text"], 1, MAX_TRANSPORT_BYTES, "transport.text")
    a.string(transport["sha256"], 64, 64, "transport.sha256", _HASH)
    for value in a.array(transport["partitions"], 0, 1, "transport.partitions"):
        a.integer(value, 1, 4096, "transport.partitions")
    case = reference.Case(grid["sample_rate_hz"], grid["frames"], tuple(sources), tuple(keys), tuple(targets))
    return admission.InputDocument(result["fixture_id"], case, result["input_sha256"], result["input_bytes"])


def _require_equal(actual, expected, budget, path="result"):
    budget.check(path)
    if type(actual) is not type(expected):
        _refuse("certificate", path, reason="typed-reconstruction-mismatch")
    if type(actual) is dict:
        if len(actual) != len(expected) or actual.keys() != expected.keys():
            _refuse("certificate", path, reason="reconstruction-fields")
        for name in expected:
            _require_equal(actual[name], expected[name], budget, path + "." + name)
    elif type(actual) is list:
        if len(actual) != len(expected):
            _refuse("certificate", path, reason="reconstruction-length", expected=len(expected), actual=len(actual))
        for index, (left, right) in enumerate(zip(actual, expected)):
            _require_equal(left, right, budget, path + f"[{index}]")
    elif actual != expected:
        _refuse("certificate", path, reason="reconstruction-value")


def encode_certificate(result, *, implementation_sha256, contract_sha256, deadline=None) -> bytes:
    """Strictly reconstruct/reconvert a result, bind provenance and encode it.

    Reconstruction proves internal consistency. Only the caller that read the
    original file can authenticate the retained original-byte hash and count.
    """
    budget = _Budget(deadline)
    document = _admit_certificate(result, budget)
    a = _CertificateAdmission(budget)
    a.obj(implementation_sha256, IMPLEMENTATION_PATHS, "provenance.implementation_sha256")
    for path in IMPLEMENTATION_PATHS:
        a.string(implementation_sha256[path], 64, 64, "provenance." + path, _HASH)
    a.string(contract_sha256, 64, 64, "provenance.contract_sha256", _HASH)
    try:
        reconstructed = convert_document(document, deadline=deadline)
    except ConversionRefusal as error:
        if error.code == "resource":
            raise
        _refuse("certificate", "sidecar", reason="reconstruction-refused", stage=error.code, source_path=error.path)
    _require_equal(result, reconstructed, budget)
    complete = dict(result)
    complete["provenance"] = {"implementation_sha256": dict(implementation_sha256),
                              "contract_sha256": contract_sha256, "python_version": platform.python_version()}
    encoder = json.JSONEncoder(sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    chunks, count = [], 1
    for chunk in encoder.iterencode(complete):
        budget.check("encoding")
        raw = chunk.encode("ascii")
        count += len(raw)
        if count > MAX_CERTIFICATE_BYTES:
            _refuse("resource", "encoding", reason="certificate-bytes", limit=MAX_CERTIFICATE_BYTES)
        chunks.append(raw)
    budget.check("encoding.complete")
    return b"".join(chunks) + b"\n"
