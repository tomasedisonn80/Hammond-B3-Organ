"""Independent exact oracle for the admitted finite contact-grid conversion.

This test-only module imports neither production conversion/replay code nor the
old fractional/grid numerical kernels.  Its input is the original parser's
canonical Case, supplied by the caller.  It constructs each key's complete
target-change epochs first, then scans each contact independently over the
finished path.  No-op command observations do not split a motion anchor.

All expected facts are Fractions until serialized.  Fraction.__round__ provides
the independently exercised nearest/even operation.  Results concern synthetic
trajectory topology and numerical error, never audio or physical accuracy.
"""

from __future__ import annotations

from bisect import bisect_right
from collections import defaultdict
from dataclasses import dataclass, field
from fractions import Fraction
import hashlib
import struct


TICKS = 65536
TRAVEL = 1 << 48
POSITION_BUDGET = Fraction(1, 1 << 18)
ROOT_BUDGET = Fraction(1, 1 << 10)


class OracleRefusal(ValueError):
    def __init__(self, code: str, path: str, witness: dict):
        super().__init__(code + ": " + path)
        self.code, self.path, self.witness = code, path, witness


def _refuse(code, path, **witness):
    raise OracleRefusal(code, path, witness)


def checked(value: Fraction | int) -> Fraction:
    """Retained rational cap; binary products of these fit the 8192-bit cap."""
    value = Fraction(value)
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > 4096:
        _refuse("resource", "rational", reason="retained rational exceeds 4096 bits")
    return value


def plus(a, b):
    return checked(a + b)


def minus(a, b):
    return checked(a - b)


def times(a, b):
    return checked(a * b)


def over(a, b):
    return checked(a / b)


def binary(value: float) -> Fraction:
    return checked(Fraction.from_float(value))


def nearest_even(value: Fraction) -> int:
    return round(checked(value))


def rational(value: Fraction | int) -> dict:
    value = checked(value)
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def decode_rational(value: dict) -> Fraction:
    """Strict test-side decoder, including type, reduction and digit spelling."""
    if type(value) is not dict or set(value) != {"numerator", "denominator"}:
        raise ValueError("not an exact-rational record")
    n, d = value["numerator"], value["denominator"]
    if type(n) is not str or type(d) is not str or len(n) > 1235 or len(d) > 1234:
        raise ValueError("not bounded rational strings")
    try:
        result = checked(Fraction(int(n), int(d)))
    except (ValueError, ZeroDivisionError):
        raise ValueError("invalid rational") from None
    if rational(result) != value:
        raise ValueError("noncanonical or nonreduced rational")
    return result


def direction(value: Fraction) -> int:
    return (value > 0) - (value < 0)


def hex64(value: float) -> str:
    return struct.pack(">d", value).hex()


@dataclass
class Work:
    count: int = 0

    def visit(self, amount=1):
        self.count += amount
        if self.count > 1_000_000:
            _refuse("resource", "work", reason="oracle work exceeds 1000000 units")


@dataclass(frozen=True)
class KeyModel:
    press: Fraction
    release: Fraction
    off: tuple[Fraction, ...]
    on: tuple[Fraction, ...]


@dataclass(frozen=True)
class Command:
    time: Fraction
    ordinal: int
    key: int
    target: Fraction


@dataclass(frozen=True)
class Piece:
    begin: Fraction
    end: Fraction
    position: Fraction
    slope: Fraction
    anchor_time: Fraction
    anchor_position: Fraction
    target: Fraction

    def at(self, instant):
        return plus(self.position, times(self.slope, minus(instant, self.begin)))


@dataclass(frozen=True)
class Root:
    time: Fraction
    anchor_time: Fraction
    anchor_position: Fraction
    threshold: Fraction
    speed: Fraction


@dataclass
class KeyPath:
    pieces: list[Piece] = field(default_factory=list)
    observations: dict = field(default_factory=dict)
    arrivals: dict[str, Root] = field(default_factory=dict)
    edges: dict[str, Root] = field(default_factory=dict)
    final_position: Fraction = Fraction(0)
    final_target: Fraction = Fraction(0)
    closed: tuple[bool, ...] = (False,) * 9
    starts: tuple[Fraction, ...] = ()

    def at(self, instant):
        if not self.pieces:
            return Fraction(0)
        index = max(0, bisect_right(self.starts, instant) - 1)
        piece = self.pieces[index]
        if not piece.begin <= instant <= piece.end:
            raise AssertionError("oracle path is not a complete continuous cover")
        return piece.at(instant)


@dataclass
class Replay:
    paths: list[KeyPath]
    observations: dict
    edges: dict[str, Root]
    arrivals: dict[str, Root]
    times: dict[str, Fraction]
    preorder: list[list[str]]


def canonical_sidecar(case) -> dict:
    """Preserve canonical source bits and original caller order independently."""
    return {
        "sources": [{"source_id": s.source_id, "frequency_hz": hex64(s.frequency_hz),
                     "amplitude": hex64(s.amplitude), "phase_turns": hex64(s.phase_turns)}
                    for s in case.sources],
        "keys": [{"key_id": k.key_id, "press_seconds": hex64(k.press_seconds),
                  "release_seconds": hex64(k.release_seconds),
                  "on": [hex64(v) for v in k.on9], "off": [hex64(v) for v in k.off9],
                  "source_ids": list(k.source_ids9), "gains": [hex64(v) for v in k.gains9]}
                 for k in case.keys],
        "targets": [{"frame": t.frame, "fraction": hex64(t.fraction),
                     "key_id": t.key_id, "target": hex64(t.target)} for t in case.targets],
    }


def _scalar_row(path, unit, source, grid):
    return {"path": path, "unit": unit, "source": rational(source),
            "grid": rational(grid), "difference": rational(minus(grid, source))}


def convert_scalars(case):
    """Round once, then enforce domain, global time and per-key value collisions."""
    source_keys, grid_keys, grid_rows, errors = [], [], [], []
    for index, key in enumerate(case.keys):
        speeds, original_speeds = [], []
        for kind, duration in (("press", key.press_seconds), ("release", key.release_seconds)):
            duration = binary(duration)
            original_speed = over(Fraction(1), times(case.sample_rate_hz, duration))
            ideal_units = times(original_speed, Fraction(TRAVEL, TICKS))
            units = nearest_even(ideal_units)
            if not 1 <= units <= (1 << 32) - 1:
                _refuse("grid_domain", f"keys[{index}].{kind}", rounded_speed=units)
            speed = Fraction(TICKS * units, TRAVEL)
            effective = over(Fraction(1), times(case.sample_rate_hz, speed))
            relative = over(abs(minus(effective, duration)), duration)
            errors.extend((
                _scalar_row(f"keys[{index}].{kind}_speed", "travel/frame", original_speed, speed),
                _scalar_row(f"keys[{index}].{kind}_seconds", "seconds", duration, effective),
                _scalar_row(f"keys[{index}].{kind}_relative_duration_error", "ratio", Fraction(0), relative),
            ))
            assert abs(minus(speed, original_speed)) <= Fraction(TICKS, 2 * TRAVEL)
            assert relative == over(abs(minus(ideal_units, units)), Fraction(units))
            speeds.append(units)
            original_speeds.append(original_speed)
        offs, ons, contacts = [], [], []
        for contact, (off, on) in enumerate(zip(key.off9, key.on9)):
            old_off, old_on = binary(off), binary(on)
            new_off, new_on = nearest_even(times(TRAVEL, old_off)), nearest_even(times(TRAVEL, old_on))
            if not 0 <= new_off < new_on <= TRAVEL:
                _refuse("grid_domain", f"keys[{index}].contacts[{contact}]", off=new_off, on=new_on)
            offs.append(Fraction(new_off, TRAVEL))
            ons.append(Fraction(new_on, TRAVEL))
            contacts.append({"off": new_off, "on": new_on})
            for kind, original, rounded in (("off", old_off, offs[-1]), ("on", old_on, ons[-1])):
                assert abs(minus(rounded, original)) <= Fraction(1, 2 * TRAVEL)
                errors.append(_scalar_row(f"keys[{index}].{kind}[{contact}]", "travel", original, rounded))
        source_keys.append(KeyModel(*original_speeds, tuple(map(binary, key.off9)), tuple(map(binary, key.on9))))
        grid_keys.append(KeyModel(Fraction(TICKS * speeds[0], TRAVEL),
                                  Fraction(TICKS * speeds[1], TRAVEL), tuple(offs), tuple(ons)))
        grid_rows.append({"press_units_per_tick": speeds[0], "release_units_per_tick": speeds[1],
                          "contacts": contacts})

    key_indices = {key.key_id: index for index, key in enumerate(case.keys)}
    source_commands = sorted((Command(plus(t.frame, binary(t.fraction)), ordinal,
                                     key_indices[t.key_id], binary(t.target))
                              for ordinal, t in enumerate(case.targets)),
                             key=lambda c: (c.time, c.ordinal))
    grid_commands, target_rows = [], []
    previous = None
    for command in source_commands:
        tick = nearest_even(times(TICKS, command.time))
        if previous is not None and previous[0] != command.time and previous[1] == tick:
            _refuse("time_collision", f"targets[{command.ordinal}].time", tick=tick,
                    source_times=[rational(previous[0]), rational(command.time)])
        previous = command.time, tick
        units = nearest_even(times(TRAVEL, command.target))
        converted = Command(Fraction(tick, TICKS), command.ordinal, command.key, Fraction(units, TRAVEL))
        grid_commands.append(converted)
        target_rows.append({"tick": tick, "key_index": command.key, "position": units})
        errors.extend((
            _scalar_row(f"targets[{command.ordinal}].time", "frames", command.time, converted.time),
            _scalar_row(f"targets[{command.ordinal}].target", "travel", command.target, converted.target),
        ))
        assert abs(minus(converted.time, command.time)) <= Fraction(1, 2 * TICKS)
        assert abs(minus(converted.target, command.target)) <= Fraction(1, 2 * TRAVEL)
    for original, converted in zip(source_commands, grid_commands):
        if 0 < original.time < case.frames and not 0 < converted.time < case.frames:
            _refuse("time_collision", f"targets[{original.ordinal}].time", reason="interior to endpoint",
                    source=rational(original.time), grid=rational(converted.time))

    for index, key in enumerate(case.keys):
        values = {Fraction(0), Fraction(1), *map(binary, key.off9), *map(binary, key.on9)}
        values.update(c.target for c in source_commands if c.key == index)
        previous = None
        for value in sorted(values):
            rounded = nearest_even(times(TRAVEL, value))
            if previous is not None and previous[1] == rounded:
                _refuse("position_collision", f"keys[{index}]", grid=rounded,
                        source_values=[rational(previous[0]), rational(value)])
            previous = value, rounded
    grid_case = {"sample_rate_hz": case.sample_rate_hz, "frames": case.frames,
                 "keys": grid_rows, "targets": target_rows}
    return source_keys, grid_keys, source_commands, grid_commands, grid_case, errors


def _key_path(key_index, model, commands, end, work):
    """Build genuine-target-change epochs independently of contact traversal."""
    path = KeyPath()
    anchor, anchor_position, target = Fraction(0), Fraction(0), Fraction(0)
    arrival_counts = defaultdict(int)

    def moving_speed():
        sign = direction(minus(target, anchor_position))
        magnitude = model.press if sign > 0 else model.release
        return sign, magnitude

    def current(instant):
        sign, speed = moving_speed()
        if not sign:
            return anchor_position
        distance = min(abs(minus(target, anchor_position)), times(speed, minus(instant, anchor)))
        return plus(anchor_position, times(sign, distance))

    def finish_epoch(stop):
        if stop == anchor:
            return
        work.visit()
        sign, speed = moving_speed()
        if not sign:
            path.pieces.append(Piece(anchor, stop, anchor_position, Fraction(0), anchor, anchor_position, target))
            return
        arrival = plus(anchor, over(abs(minus(target, anchor_position)), speed))
        moving_end = min(arrival, stop)
        path.pieces.append(Piece(anchor, moving_end, anchor_position, times(sign, speed),
                                 anchor, anchor_position, target))
        if arrival <= stop:
            occurrence = arrival_counts[sign]
            arrival_counts[sign] += 1
            label = f"A:{key_index}:{sign}:{occurrence}"
            path.arrivals[label] = Root(arrival, anchor, anchor_position, target, speed)
            work.visit()
            if arrival < stop:
                path.pieces.append(Piece(arrival, stop, target, Fraction(0), anchor, anchor_position, target))

    for command in commands:
        work.visit()
        position = current(command.time)
        repeated = command.target == target
        path.observations[command.ordinal] = {
            "time": command.time, "key": key_index, "position": position,
            "before": direction(minus(target, position)),
            "after": direction(minus(command.target, position)), "repeated": repeated,
        }
        if not repeated:
            finish_epoch(command.time)
            anchor, anchor_position, target = command.time, position, command.target
    finish_epoch(Fraction(end))
    path.final_position, path.final_target = current(Fraction(end)), target
    path.starts = tuple(piece.begin for piece in path.pieces)

    # Contact-major traversal deliberately differs from an online merged event
    # sweep. Inclusive right endpoints settle incoming crossings before commands.
    closed_bits = []
    for contact, (off, on) in enumerate(zip(model.off, model.on)):
        closed = False
        occurrences = {0: 0, 1: 0}
        for piece in path.pieces:
            work.visit()
            if not piece.slope:
                continue
            stop_position = piece.at(piece.end)
            makes = piece.slope > 0 and not closed and piece.position < on <= stop_position
            breaks = piece.slope < 0 and closed and stop_position <= off < piece.position
            if not (makes or breaks):
                continue
            closed = bool(makes)
            state = int(closed)
            threshold = on if closed else off
            event_time = plus(piece.anchor_time, over(abs(minus(threshold, piece.anchor_position)), abs(piece.slope)))
            if not piece.begin < event_time <= piece.end:
                raise AssertionError("oracle root outside its emitting moving piece")
            label = f"E:{key_index}:{contact}:{state}:{occurrences[state]}"
            occurrences[state] += 1
            path.edges[label] = Root(event_time, piece.anchor_time, piece.anchor_position, threshold, abs(piece.slope))
            work.visit()
        closed_bits.append(closed)
    path.closed = tuple(closed_bits)
    return path


def reconstruct(frames, keys, commands, work=None):
    """Complete source or grid model; requires exact already-admitted values."""
    work = Work() if work is None else work
    own_commands = [[] for _ in keys]
    for command in commands:
        own_commands[command.key].append(command)
    paths = [_key_path(index, model, own_commands[index], frames, work)
             for index, model in enumerate(keys)]
    observations = {ordinal: value for path in paths for ordinal, value in path.observations.items()}
    edges = {label: root for path in paths for label, root in path.edges.items()}
    arrivals = {label: root for path in paths for label, root in path.arrivals.items()}
    if sum(len(path.pieces) for path in paths) > 1032:
        _refuse("resource", "segments", reason="more than 1032 affine pieces")
    if len(edges) > 4608 or len(arrivals) > 512:
        _refuse("resource", "events", reason="edge or arrival cap")
    times_by_label = {"B:0": Fraction(0), "B:1": Fraction(frames)}
    times_by_label.update({f"C:{c.ordinal}": c.time for c in commands})
    times_by_label.update({label: root.time for label, root in edges.items()})
    times_by_label.update({label: root.time for label, root in arrivals.items()})
    if len(times_by_label) > 5634:
        _refuse("resource", "events", reason="more than 5634 labeled records")
    groups = defaultdict(list)
    for label, instant in times_by_label.items():
        work.visit()
        groups[instant].append(label)
    preorder = []
    for instant in sorted(groups):
        work.visit()
        preorder.append(sorted(groups[instant]))
    return Replay(paths, observations, edges, arrivals, times_by_label, preorder)


def _transport(case):
    partitions = [case["frames"]] if case["frames"] else []
    lines = [f"CGGRID1 {case['sample_rate_hz']} {len(case['keys'])} {case['frames']} "
             f"{len(case['targets'])} {len(partitions)}"]
    for key in case["keys"]:
        row = [key["press_units_per_tick"], key["release_units_per_tick"]]
        row.extend(value for contact in key["contacts"] for value in (contact["off"], contact["on"]))
        lines.append(" ".join(map(str, row)))
    lines.extend(" ".join(str(command[name]) for name in ("tick", "key_index", "position"))
                 for command in case["targets"])
    lines.extend(str(count) for count in partitions)
    text = "\n".join(lines) + "\n"
    if len(text.encode("ascii")) > 131072:
        _refuse("resource", "transport", reason="CGGRID1 exceeds 131072 bytes")
    return {"format": "CGGRID1", "text": text,
            "sha256": hashlib.sha256(text.encode("ascii")).hexdigest(), "partitions": partitions}


def evaluate_case(case) -> dict:
    """Return all expected numerical facts, or the first mathematical refusal.

    Original input admission and raw-byte metadata belong to the caller. The
    oracle's operation count is deliberately not a candidate expected value.
    """
    source_keys, grid_keys, source_commands, grid_commands, grid_case, scalar_errors = convert_scalars(case)
    work = Work()
    source = reconstruct(case.frames, source_keys, source_commands, work)
    grid = reconstruct(case.frames, grid_keys, grid_commands, work)
    command_rows = []
    for command in source_commands:
        left, right = source.observations[command.ordinal], grid.observations[command.ordinal]
        for member in ("before", "after", "repeated"):
            if left[member] != right[member]:
                _refuse("dynamic_topology", f"commands[{command.ordinal}].{member}",
                        source=left[member], grid=right[member])
        command_rows.append({
            "ordinal": command.ordinal, "key_index": command.key,
            "source_time": rational(left["time"]), "grid_time": rational(right["time"]),
            "source_position": rational(left["position"]), "grid_position": rational(right["position"]),
            "before_direction": left["before"], "after_direction": left["after"],
            "repeated_target": left["repeated"],
        })
    for index, (left, right) in enumerate(zip(source.paths, grid.paths)):
        if right.final_target != Fraction(nearest_even(times(TRAVEL, left.final_target)), TRAVEL):
            _refuse("dynamic_topology", f"final_keys[{index}].target", reason="final target mapping")
    paired = {}
    for kind in ("edges", "arrivals"):
        left, right = getattr(source, kind), getattr(grid, kind)
        if sorted(left) != sorted(right):
            _refuse("event_identity", kind, source_count=len(left), grid_count=len(right),
                    first_difference=min(set(left).symmetric_difference(right)))
        paired[kind] = [{"label": label, "source_time": rational(left[label].time),
                         "grid_time": rational(right[label].time)} for label in sorted(left)]
    if source.preorder != grid.preorder:
        index = next(i for i, (s, g) in enumerate(zip(source.preorder, grid.preorder)) if s != g)
        left, right = set(source.preorder[index]), set(grid.preorder[index])
        x = min(left.symmetric_difference(right))
        y = min(right) if x in left else min(left)
        labels = sorted((x, y))
        _refuse("event_order", f"preorder[{index}]", group=index,
                source_group_count=len(left), grid_group_count=len(right), labels=labels,
                source_times=[rational(source.times[label]) for label in labels],
                grid_times=[rational(grid.times[label]) for label in labels])
    for index, (left, right) in enumerate(zip(source.paths, grid.paths)):
        for contact, (s, g) in enumerate(zip(left.closed, right.closed)):
            if s != g:
                _refuse("final_contacts", f"keys[{index}].contacts[{contact}]", source=s, grid=g)

    samples, position_max, position_witness = [], Fraction(0), None
    # Every global command is a knot on every key, even if that key did not move.
    shared_knots = {Fraction(0), Fraction(case.frames)}
    shared_knots.update(c.time for c in source_commands)
    shared_knots.update(c.time for c in grid_commands)
    for index, (left, right) in enumerate(zip(source.paths, grid.paths)):
        knots = set(shared_knots)
        for path in (left, right):
            knots.update(v for p in path.pieces for v in (p.begin, p.end))
            knots.update(root.time for root in path.arrivals.values())
        if len(samples) + len(knots) > 4096:
            _refuse("resource", "position_samples", reason="more than 4096 union knots across keys")
        for instant in sorted(knots):
            work.visit(2)
            s, g = left.at(instant), right.at(instant)
            error = abs(minus(g, s))
            samples.append({"key_index": index, "time": rational(instant),
                            "source": rational(s), "grid": rational(g)})
            if position_witness is None or error > position_max:
                position_max, position_witness = error, len(samples) - 1
            if error > POSITION_BUDGET:
                _refuse("position_budget", f"position_samples[{len(samples) - 1}]", key_index=index,
                        time=rational(instant), source=rational(s), grid=rational(g), error=rational(error))

    roots = []
    for kind in ("edges", "arrivals"):
        for label in sorted(getattr(source, kind)):
            work.visit()
            s, g = getattr(source, kind)[label], getattr(grid, kind)[label]
            error = abs(minus(g.time, s.time))
            anchor_error = abs(minus(g.anchor_time, s.anchor_time))
            position_error = abs(minus(g.anchor_position, s.anchor_position))
            threshold_error = abs(minus(g.threshold, s.threshold))
            speed_error = abs(minus(g.speed, s.speed))
            distance = abs(minus(s.threshold, s.anchor_position))
            bound = plus(plus(anchor_error, over(plus(threshold_error, position_error), g.speed)),
                         over(times(distance, speed_error), times(s.speed, g.speed)))
            for stage, failed in (("error", error > ROOT_BUDGET), ("triangle", error > bound),
                                  ("bound", bound > ROOT_BUDGET)):
                if failed:
                    _refuse("root_budget", f"{kind}.{label}.{stage}", label=label, stage=stage,
                            source_time=rational(s.time), grid_time=rational(g.time),
                            error=rational(error), bound=rational(bound))
            roots.append({
                "label": label, "source_anchor_time": rational(s.anchor_time),
                "grid_anchor_time": rational(g.anchor_time),
                "source_anchor_position": rational(s.anchor_position),
                "grid_anchor_position": rational(g.anchor_position),
                "source_threshold": rational(s.threshold), "grid_threshold": rational(g.threshold),
                "source_speed": rational(s.speed), "grid_speed": rational(g.speed),
                "error": rational(error), "bound": rational(bound),
            })
    # Refusal precedence above is edges then arrivals. Certificate ordering is
    # combined ASCII label order, with the witness indexing that public array.
    roots.sort(key=lambda row: row["label"])
    root_max, root_witness = Fraction(0), None
    for index, row in enumerate(roots):
        error = decode_rational(row["error"])
        if root_witness is None or error > root_max:
            root_max, root_witness = error, index
    return {
        "grid_case": grid_case, "sidecar": canonical_sidecar(case), "scalar_errors": scalar_errors,
        "edges": paired["edges"], "arrivals": paired["arrivals"], "commands": command_rows,
        "final_keys": [{"key_index": index, "source_position": rational(s.final_position),
                        "grid_position": rational(g.final_position), "source_target": rational(s.final_target),
                        "grid_target": rational(g.final_target), "closed9": list(s.closed)}
                       for index, (s, g) in enumerate(zip(source.paths, grid.paths))],
        "preorder": source.preorder, "position_samples": samples, "root_bounds": roots,
        "summary": {"max_position_error": rational(position_max), "position_witness": position_witness,
                    "max_root_error": rational(root_max), "root_witness": root_witness},
        "transport": _transport(grid_case),
    }
