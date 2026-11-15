"""Pure, bounded offline fractional contact reference (synthetic evidence).

Implements docs/FRACTIONAL_CONTACT_REFERENCE.md, model
``fractional-contact-reference-v1``.  This module has no file or command-line
interface and does not alter the nominal Engine.  Inputs and results are
immutable tuples.  Exact rational preparation determines event topology and
clipping; source and filter evaluations use binary64 arithmetic.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import hashlib
import math
import re
import struct
from typing import NamedTuple


MODEL_ID = "fractional-contact-reference-v1"
EVIDENCE_CLASS = "synthetic"
SAMPLE_RATES = (44100, 48000, 96000)
FACTORS = (32, 64, 128, 256)
H = 16
BETA = 0.45
MAX_WORK = 20_000_000
MAX_FRAMES = 4096
MAX_TARGETS = 512
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", re.ASCII)
_ZERO = Fraction(0)
_HALF = Fraction(1, 2)


class Source(NamedTuple):
    source_id: int
    frequency_hz: float
    amplitude: float
    phase_turns: float


class Key(NamedTuple):
    key_id: str
    press_seconds: float
    release_seconds: float
    on9: tuple[float, ...]
    off9: tuple[float, ...]
    source_ids9: tuple[int, ...]
    gains9: tuple[float, ...]


class Target(NamedTuple):
    frame: int
    fraction: float
    key_id: str
    target: float


class Case(NamedTuple):
    sample_rate_hz: int
    frames: int
    sources: tuple[Source, ...]
    keys: tuple[Key, ...]
    targets: tuple[Target, ...]


class Segment(NamedTuple):
    key_index: int
    u0: Fraction
    u1: Fraction
    q0: Fraction
    velocity_per_host_frame: Fraction
    target: Fraction


class Edge(NamedTuple):
    u: Fraction
    key_index: int
    contact_index: int
    closed_after: bool


class FinalKey(NamedTuple):
    position: Fraction
    target: Fraction
    closed9: tuple[bool, ...]


class Trajectory(NamedTuple):
    segments: tuple[Segment, ...]
    edges: tuple[Edge, ...]
    final_keys: tuple[FinalKey, ...]


class Render(NamedTuple):
    trajectory: Trajectory
    first_frame: int
    samples: tuple[float, ...]
    bound: float
    work: int


def _tuple(value: object, label: str, length: int | None = None) -> tuple:
    if not isinstance(value, tuple) or (length is not None and len(value) != length):
        raise ValueError(f"{label} must be an immutable tuple"
                         + (f" of length {length}" if length is not None else ""))
    return value


def _integer(value: object, label: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{label} must be an integer in [{low},{high}]")
    return value


def _number(value: object, label: str, low: float, high: float,
            *, upper_open: bool = False) -> float:
    if type(value) not in (int, float):
        raise ValueError(f"{label} must be a finite number, not a boolean")
    try:
        result = float(value)
    except (OverflowError, ValueError):
        raise ValueError(f"{label} must be a finite number") from None
    if (not math.isfinite(result) or result < low or result > high
            or (upper_open and result == high)):
        raise ValueError(f"{label} is outside its finite numeric domain")
    return result if result else 0.0


def _identifier(value: object, label: str) -> str:
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        raise ValueError(f"{label} must be a 1..64 character ASCII identifier")
    return value


def _factor(value: object) -> int:
    if type(value) is not int or value not in FACTORS:
        raise ValueError("factor must be one of 32, 64, 128, 256")
    return value


def _source(value: object, sample_rate_hz: int) -> Source:
    row = _tuple(value, "source", 4)
    return Source(_integer(row[0], "source_id", 1, 91),
                  _number(row[1], "frequency_hz", 0.0, 0.45 * sample_rate_hz),
                  _number(row[2], "amplitude", 0.0, 1.0),
                  _number(row[3], "phase_turns", 0.0, 1.0, upper_open=True))


def validate_case(case: object) -> Case:
    """Independently admit and canonicalize a pure tuple input.

    Only built-in integer/float numeric inputs are accepted; booleans, mutable
    arrays, nonfinite values, unknown routes and rounded time collisions fail.
    No sorting of the caller's source, key or target arrays is performed here.
    """
    row = _tuple(case, "case", 5)
    rate = _integer(row[0], "sample_rate_hz", 44100, 96000)
    if rate not in SAMPLE_RATES:
        raise ValueError("sample_rate_hz must be 44100, 48000 or 96000")
    frames = _integer(row[1], "frames", 0, MAX_FRAMES)
    source_rows = _tuple(row[2], "sources")
    key_rows = _tuple(row[3], "keys")
    target_rows = _tuple(row[4], "targets")
    if not 1 <= len(source_rows) <= 36:
        raise ValueError("sources must contain 1..36 records")
    if not 1 <= len(key_rows) <= 4:
        raise ValueError("keys must contain 1..4 records")
    if len(target_rows) > MAX_TARGETS:
        raise ValueError("targets must contain at most 512 records")

    sources = tuple(_source(source, rate) for source in source_rows)
    source_ids = {source.source_id for source in sources}
    if len(source_ids) != len(sources):
        raise ValueError("duplicate source_id")
    keys = []
    key_ids = set()
    for key_row in key_rows:
        key_row = _tuple(key_row, "key", 7)
        key_id = _identifier(key_row[0], "key_id")
        if key_id in key_ids:
            raise ValueError("duplicate key_id")
        key_ids.add(key_id)
        press = _number(key_row[1], "press_seconds", 0.0001, 1.0)
        release = _number(key_row[2], "release_seconds", 0.0001, 1.0)
        on = tuple(_number(v, "on", 0.0, 1.0)
                   for v in _tuple(key_row[3], "on9", 9))
        off = tuple(_number(v, "off", 0.0, 1.0)
                    for v in _tuple(key_row[4], "off9", 9))
        if any(not low < high for low, high in zip(off, on)):
            raise ValueError("each contact must satisfy 0 <= off < on <= 1")
        routes = tuple(_integer(v, "source_id", 1, 91)
                       for v in _tuple(key_row[5], "source_ids9", 9))
        if any(source_id not in source_ids for source_id in routes):
            raise ValueError("key route names an absent source_id")
        gains = tuple(_number(v, "gain", -1.0, 1.0)
                      for v in _tuple(key_row[6], "gains9", 9))
        keys.append(Key(key_id, press, release, on, off, routes, gains))

    targets = []
    rounded_times = {}
    for target_row in target_rows:
        target_row = _tuple(target_row, "target", 4)
        frame = _integer(target_row[0], "frame", 0, frames)
        fraction = _number(target_row[1], "fraction", 0.0, 1.0, upper_open=True)
        key_id = _identifier(target_row[2], "target key_id")
        if key_id not in key_ids:
            raise ValueError("target names an absent key_id")
        target = _number(target_row[3], "target", 0.0, 1.0)
        if frame == frames and fraction != 0.0:
            raise ValueError("only fraction zero is legal at frame N")
        rounded = frame + fraction
        if fraction != 0.0 and rounded == frame:
            raise ValueError("nonzero target fraction is lost at its frame")
        pair = (frame, fraction)
        previous = rounded_times.setdefault(rounded, pair)
        if previous != pair:
            raise ValueError("distinct target time pairs collide in binary64")
        targets.append(Target(frame, fraction, key_id, target))
    return Case(rate, frames, sources, tuple(keys), tuple(targets))


def _ordered_targets(case: Case) -> list[Target]:
    # Python's sort is stable: equal pairs retain the caller's exact order.
    return sorted(case.targets, key=lambda command: (command.frame, command.fraction))


def _build_trajectory(case: Case) -> Trajectory:
    segments = []
    edges = []
    final_keys = []
    end = Fraction(case.frames)
    commands_by_key = {key.key_id: [] for key in case.keys}
    for command in _ordered_targets(case):
        u = Fraction(command.frame) + Fraction.from_float(command.fraction)
        commands_by_key[command.key_id].append((u, Fraction.from_float(command.target)))

    for key_index, key in enumerate(case.keys):
        # Collapse only commands with no intervening time. Their last target
        # governs motion; no command in the group can itself switch a contact.
        grouped = []
        for u, target in commands_by_key[key.key_id]:
            if grouped and grouped[-1][0] == u:
                grouped[-1] = (u, target)
            else:
                grouped.append((u, target))
        changes = []
        previous_target = _ZERO
        for u, target in grouped:
            if target != previous_target:
                changes.append((u, target))
                previous_target = target

        on = tuple(Fraction.from_float(v) for v in key.on9)
        off = tuple(Fraction.from_float(v) for v in key.off9)
        up_velocity = 1 / (case.sample_rate_hz * Fraction.from_float(key.press_seconds))
        down_velocity = -1 / (case.sample_rate_hz * Fraction.from_float(key.release_seconds))
        closed = [False] * 9
        u0 = q0 = target = _ZERO

        # The final sentinel advances to N after resolving any commands at N.
        for u1, next_target in changes + [(end, None)]:
            if u1 > u0:
                if q0 != target:
                    velocity = up_velocity if target > q0 else down_velocity
                    arrival = u0 + (target - q0) / velocity
                    moving_end = min(arrival, u1)
                    q1 = target if moving_end == arrival else q0 + velocity * (moving_end - u0)
                    segments.append(Segment(key_index, u0, moving_end, q0, velocity, target))
                    for contact_index in range(9):
                        threshold = on[contact_index] if velocity > 0 else off[contact_index]
                        eligible = ((not closed[contact_index] and q0 <= threshold <= q1)
                                    if velocity > 0 else
                                    (closed[contact_index] and q1 <= threshold <= q0))
                        if eligible:
                            crossing = u0 + (threshold - q0) / velocity
                            closed[contact_index] = velocity > 0
                            edges.append(Edge(crossing, key_index, contact_index,
                                              closed[contact_index]))
                    u0, q0 = moving_end, q1
                if u0 < u1:
                    segments.append(Segment(key_index, u0, u1, q0, _ZERO, target))
                    u0 = u1
            if next_target is not None:
                target = next_target
        final_keys.append(FinalKey(q0, target, tuple(closed)))

    edges.sort(key=lambda edge: (edge.u, edge.key_index, edge.contact_index))
    return Trajectory(tuple(segments), tuple(edges), tuple(final_keys))


def build_trajectory(case: object) -> Trajectory:
    """Return exact segments, independent physical edges and the state at N."""
    return _build_trajectory(validate_case(case))


def _work_bound(case: Case, factor: int) -> int:
    if case.frames == 0:
        return len(case.targets) + 10 * len(case.keys) + len(case.sources)
    taps = 32 * factor + 1
    return ((case.frames + 33) * taps
            + (case.frames * factor + 1) * 9 * len(case.keys)
            + 18 * len(case.targets) + taps)


def work_bound(case: object, factor: object) -> int:
    """Return W without allocating numerical buffers; render enforces MAX_WORK."""
    return _work_bound(validate_case(case), _factor(factor))


def _raw_bound(case: Case) -> tuple[Fraction, float]:
    amplitudes = {source.source_id: Fraction.from_float(source.amplitude)
                  for source in case.sources}
    exact = sum((Fraction.from_float(abs(gain)) * amplitudes[source_id]
                 for key in case.keys
                 for source_id, gain in zip(key.source_ids9, key.gains9)), _ZERO)
    rounded = float(exact)
    if Fraction.from_float(rounded) < exact:
        rounded = math.nextafter(rounded, math.inf)
    return exact, rounded if rounded else 0.0


def raw_bound(case: object) -> float:
    """Smallest binary64 B at least the exact sum of absolute route products."""
    return _raw_bound(validate_case(case))[1]


def _sinc(z: float) -> float:
    x = math.pi * z
    if abs(x) < 1.0e-4:
        square = x * x
        return 1.0 + square * (-1.0 / 6.0 + square * (1.0 / 120.0 - square / 5040.0))
    return math.sin(x) / x


def sinc(z: object) -> float:
    """Normalized sinc, including a stable small-argument limit."""
    value = _number(z, "sinc argument", -math.inf, math.inf)
    # Avoid an overflow in pi*z for otherwise finite diagnostic arguments.
    if abs(value) > 1.0e300:
        raise ValueError("sinc argument is outside the supported diagnostic domain")
    return _sinc(value)


def _coordinate(value: object, label: str) -> Fraction:
    if isinstance(value, Fraction):
        result = value
    elif type(value) is int:
        result = Fraction(value)
    elif type(value) is float and math.isfinite(value):
        result = Fraction.from_float(value)
    else:
        raise ValueError(f"{label} must be a finite coordinate")
    if not -MAX_FRAMES - H <= result <= MAX_FRAMES + H:
        raise ValueError(f"{label} exceeds the bounded coordinate domain")
    return result


def _sine_integral(source: Source, rate: int, a: Fraction, b: Fraction,
                   scale: int = 1) -> float:
    # Subtract/add exact endpoints *before* binary64 conversion, including
    # intervals whose two endpoints have the same displayed binary64 value.
    width = b - a
    midpoint = float((a + b) / 2)
    frequency = source.frequency_hz / rate
    return (source.amplitude * float(width * scale)
            * math.sin(math.tau * (source.phase_turns + frequency * midpoint))
            * _sinc(frequency * float(width)))


def sine_integral(source: object, sample_rate_hz: object,
                  a: object, b: object) -> float:
    """Analytic unswitched source integral over exact host coordinates [a,b]."""
    rate = _integer(sample_rate_hz, "sample_rate_hz", 44100, 96000)
    if rate not in SAMPLE_RATES:
        raise ValueError("sample_rate_hz must be 44100, 48000 or 96000")
    source = _source(source, rate)
    left, right = _coordinate(a, "a"), _coordinate(b, "b")
    if right < left:
        raise ValueError("integral endpoints must be ordered")
    result = _sine_integral(source, rate, left, right)
    if not math.isfinite(result):
        raise ValueError("nonfinite sine integral")
    return result if result else 0.0


def source_value_and_slope(source: object, sample_rate_hz: object,
                           u: object) -> tuple[float, float]:
    """Absolute-origin source value and derivative per physical second."""
    rate = _integer(sample_rate_hz, "sample_rate_hz", 44100, 96000)
    if rate not in SAMPLE_RATES:
        raise ValueError("sample_rate_hz must be 44100, 48000 or 96000")
    source = _source(source, rate)
    coordinate = _coordinate(u, "u")
    angle = math.tau * (source.phase_turns + source.frequency_hz / rate * float(coordinate))
    value = source.amplitude * math.sin(angle)
    slope = source.amplitude * (math.tau * source.frequency_hz) * math.cos(angle)
    if not math.isfinite(value) or not math.isfinite(slope):
        raise ValueError("nonfinite source evaluation")
    return (value if value else 0.0, slope if slope else 0.0)


def _kernel(v: float) -> float:
    if abs(v) >= H:
        return 0.0
    window = 0.42 + 0.5 * math.cos(math.pi * v / H) + 0.08 * math.cos(math.tau * v / H)
    return 2.0 * BETA * _sinc(2.0 * BETA * v) * window


@lru_cache(maxsize=4)
def _filter_coefficients(factor: int) -> tuple[float, tuple[float, ...]]:
    radius = H * factor
    # Mirror the evaluated nonnegative half so the symmetry is exact in bytes.
    half = tuple(_kernel(r / factor) for r in range(radius + 1))
    raw = half[:0:-1] + half
    normalizer = math.fsum(raw)
    if not math.isfinite(normalizer) or normalizer <= 0.0:
        raise ValueError("filter normalizer must be positive and finite")
    coefficients = tuple(value / normalizer if value else 0.0 for value in raw)
    if not all(math.isfinite(value) for value in coefficients):
        raise ValueError("nonfinite filter coefficient")
    if abs(math.fsum(coefficients) - 1.0) > 2.0e-14:
        raise ValueError("filter DC residual exceeds 2e-14")
    return normalizer, coefficients


def filter_coefficients(factor: object) -> tuple[float, tuple[float, ...]]:
    """Return (Z_L, immutable weights in ascending r=-16L..16L order)."""
    return _filter_coefficients(_factor(factor))


def _contact_intervals(case: Case, trajectory: Trajectory):
    """Prepare each contact's exact connected intervals in one ledger pass."""
    starts = [[None] * 9 for _ in case.keys]
    intervals = [[[] for _ in range(9)] for _ in case.keys]
    end = Fraction(case.frames)
    for edge in trajectory.edges:
        if edge.closed_after:
            starts[edge.key_index][edge.contact_index] = edge.u
        else:
            start = starts[edge.key_index][edge.contact_index]
            if start is not None and start < min(edge.u, end):
                intervals[edge.key_index][edge.contact_index].append((start, min(edge.u, end)))
            starts[edge.key_index][edge.contact_index] = None
    for key_index, key_starts in enumerate(starts):
        for contact_index, start in enumerate(key_starts):
            if start is not None and start < end:
                intervals[key_index][contact_index].append((start, end))
    return intervals


def _cells(case: Case, factor: int, trajectory: Trajectory) -> list[float]:
    """Sweep prepartitioned full-cell runs and exact partial-cell integrals.

    Rational work is bounded by intervals/edges, never by N*L.  Only one dense
    accumulated cell vector is stored. Histories and signed contact products
    remain separate; a shared source is evaluated only once per complete cell.
    """
    intervals = _contact_intervals(case, trajectory)
    source_indices = {source.source_id: i for i, source in enumerate(case.sources)}
    # Events enable/disable a contact at an integer complete-cell boundary.
    # Do not round combined gains first: a partial-cell route may cancel a
    # large complete-cell term and expose a tiny independent contribution.
    events = {}
    partials = {}
    route_sources = []
    route_gains = []
    for key_index, key in enumerate(case.keys):
        for contact_index, gain in enumerate(key.gains9):
            source_index = source_indices[key.source_ids9[contact_index]]
            source = case.sources[source_index]
            route_index = len(route_sources)
            route_sources.append(source_index)
            route_gains.append(gain)
            if gain == 0.0 or source.amplitude == 0.0:
                continue
            for left, right in intervals[key_index][contact_index]:
                first = math.floor(left * factor + _HALF)
                last = math.ceil(right * factor + _HALF) - 1
                full_start = math.ceil(left * factor + _HALF)
                full_stop = math.floor(right * factor - _HALF) + 1
                if full_start < full_stop:
                    events.setdefault(full_start, []).append((route_index, 1))
                    events.setdefault(full_stop, []).append((route_index, -1))
                for cell_index in (first,) if first == last else (first, last):
                    if full_start <= cell_index < full_stop:
                        continue
                    a = max(left, Fraction(2 * cell_index - 1, 2 * factor))
                    b = min(right, Fraction(2 * cell_index + 1, 2 * factor))
                    if a < b:
                        value = gain * _sine_integral(source, case.sample_rate_hz, a, b, factor)
                        partials.setdefault(cell_index, []).append(value)

    cell_count = case.frames * factor + 1
    cells = [0.0] * cell_count
    active = [0] * len(route_sources)
    boundaries = sorted(set(events) | {0, cell_count})
    for start, stop in zip(boundaries, boundaries[1:]):
        for route_index, delta in events.get(start, ()):
            active[route_index] += delta
        routes = []
        active_sources = {}
        for route_index, connected in enumerate(active):
            if connected:
                source_index = route_sources[route_index]
                source = case.sources[source_index]
                if source_index not in active_sources:
                    frequency = source.frequency_hz / case.sample_rate_hz
                    amplitude = source.amplitude * _sinc(frequency / factor)
                    active_sources[source_index] = (amplitude, source.phase_turns, frequency)
                routes.append((source_index, route_gains[route_index]))
        if not routes:
            continue
        for cell_index in range(start, stop):
            midpoint = cell_index / factor  # Exact: supported factors are powers of two.
            source_values = {
                source_index: amplitude * math.sin(math.tau * (phase + frequency * midpoint))
                for source_index, (amplitude, phase, frequency) in active_sources.items()}
            contributions = [gain * source_values[source_index] for source_index, gain in routes]
            contributions.extend(partials.pop(cell_index, ()))
            cells[cell_index] = math.fsum(contributions)
    for cell_index, contributions in partials.items():
        # Remaining cells have no complete-cell routes. Never round their
        # signed partial pieces into a prior running accumulated cell value.
        cells[cell_index] = math.fsum(contributions)
    if not all(math.isfinite(value) for value in cells):
        raise ValueError("nonfinite cell average")
    return cells


def render(case: object, factor: object) -> Render:
    """Render all N+33 centered samples, after strict input/work admission."""
    case = validate_case(case)
    factor = _factor(factor)
    work = _work_bound(case, factor)
    if work > MAX_WORK:
        raise ValueError(f"work bound {work} exceeds {MAX_WORK}")
    exact_bound, bound = _raw_bound(case)
    trajectory = _build_trajectory(case)
    if case.frames == 0:
        return Render(trajectory, 0, (), bound, work)
    _, coefficients = _filter_coefficients(factor)
    if exact_bound == 0:
        return Render(trajectory, -H, (0.0,) * (case.frames + 2 * H + 1), bound, work)
    cells = _cells(case, factor, trajectory)
    radius = H * factor
    last_cell = len(cells) - 1
    samples = []
    for frame in range(-H, case.frames + H + 1):
        center = frame * factor
        first = max(0, center - radius)
        last = min(last_cell, center + radius)
        value = math.fsum(cells[j] * coefficients[center - j + radius]
                          for j in range(first, last + 1))
        if not math.isfinite(value):
            raise ValueError("nonfinite filtered sample")
        samples.append(value if value else 0.0)
    return Render(trajectory, -H, tuple(samples), bound, work)


def read_samples(rendered: object, first_frame: object, count: object) -> tuple[float, ...]:
    """Read immutable output by absolute host frame, allowing empty end reads."""
    row = _tuple(rendered, "render", 5)
    trajectory = _tuple(row[0], "trajectory", 3)
    for value in trajectory:
        _tuple(value, "trajectory records")
    samples = _tuple(row[2], "samples")
    if len(samples) > MAX_FRAMES + 2 * H + 1 or (samples and len(samples) < 2 * H + 2):
        raise ValueError("render sample count is outside its domain")
    origin = _integer(row[1], "render first_frame", -H, 0)
    if origin != (-H if samples else 0):
        raise ValueError("render first_frame does not match its empty/nonempty convention")
    _number(row[3], "render bound", 0.0, 36.0)
    _integer(row[4], "render work", 0, MAX_WORK)
    if any(type(sample) is not float or not math.isfinite(sample) for sample in samples):
        raise ValueError("render samples must be finite binary64 values")
    start = _integer(first_frame, "first_frame", origin, origin + len(samples))
    length = _integer(count, "count", 0, len(samples))
    if start + length > origin + len(samples):
        raise ValueError("requested interval extends beyond the complete render")
    offset = start - origin
    return samples[offset:offset + length]


@lru_cache(maxsize=4)
def _filter_responses(factor: int) -> tuple[tuple[float, ...], ...]:
    _, coefficients = _filter_coefficients(factor)
    radius = H * factor
    rows = []
    for frequency in tuple(j / 256 for j in range(257)) + (1.5, 2.0):
        # Exact coefficient symmetry makes the imaginary component exactly zero.
        real = math.fsum([coefficients[radius]] + [
            2.0 * coefficients[radius + r] * math.cos(math.tau * frequency * (r / factor))
            for r in range(1, radius + 1)])
        average = _sinc(frequency / factor)
        rows.append((frequency, real if real else 0.0, average, real * average))
    return tuple(rows)


def filter_metadata(factor: object) -> dict:
    """Finite filter identity/response data for an external report writer.

    Responses use cycles per host frame and include the complete stationary
    renderer's cell-average sinc factor. Phase is null below magnitude 1e-8.
    The returned dictionary is fresh; cached internal data remains immutable.
    """
    factor = _factor(factor)
    normalizer, coefficients = _filter_coefficients(factor)
    digest = hashlib.sha256()
    for value in coefficients:
        digest.update(struct.pack(">d", value if value else 0.0))
    responses = []
    for frequency, real, average, complete in _filter_responses(factor):
        responses.append({
            "cycles_per_host_frame": frequency,
            "filter_real": real, "filter_imaginary": 0.0,
            "filter_magnitude": abs(real),
            "filter_phase_radians": (0.0 if real >= 0.0 else math.pi) if abs(real) >= 1e-8 else None,
            "cell_average_factor": average,
            "renderer_real": complete, "renderer_imaginary": 0.0,
            "renderer_magnitude": abs(complete),
            "renderer_phase_radians": ((0.0 if complete >= 0.0 else math.pi)
                                       if abs(complete) >= 1e-8 else None),
        })
    coefficient_sum = math.fsum(coefficients)
    return {"H": H, "beta": BETA, "normalizer": normalizer,
            "coefficient_count": len(coefficients), "coefficient_sha256": digest.hexdigest(),
            "sum": coefficient_sum, "absolute_sum": math.fsum(abs(v) for v in coefficients),
            "dc_residual": abs(coefficient_sum - 1.0), "responses": responses}


def _rms(values: tuple[float, ...]) -> float:
    largest = max(abs(value) for value in values)
    if largest == 0.0:
        return 0.0
    return largest * math.sqrt(math.fsum((value / largest) ** 2 for value in values) / len(values))


def error_metrics(reference: object, candidate: object, bound: object) -> dict:
    """Scaled error statistics; no implicit convergence or fidelity decision.

    Squares are formed only after division by B. A normalized reference RMS
    below 1e-8 is explicitly ineligible for NRMSE. Zero-B violations remain
    reportable failures rather than being silently declared exact silence.
    """
    if not isinstance(reference, (tuple, list)) or not isinstance(candidate, (tuple, list)):
        raise ValueError("metric inputs must be finite sample sequences")
    if len(reference) != len(candidate) or len(reference) > MAX_FRAMES + 2 * H + 1:
        raise ValueError("metric sequences must have equal bounded lengths")
    ref = tuple(_number(v, "reference sample", -math.inf, math.inf) for v in reference)
    cand = tuple(_number(v, "candidate sample", -math.inf, math.inf) for v in candidate)
    b = _number(bound, "bound", 0.0, 36.0)
    empty = {"count": len(ref), "status": "empty", "max_absolute_error": None,
             "rms_error": None, "reference_rms": None, "peak_B": None,
             "normalized_rms_error": None, "normalized_reference_rms": None, "nrmse": None}
    if not ref:
        return empty
    errors = tuple(y - x for x, y in zip(ref, cand))
    if not all(math.isfinite(value) for value in errors):
        raise ValueError("nonfinite sample difference")
    peak = max(abs(value) for value in errors)
    if b == 0.0:
        exact = all(value == 0.0 for value in ref + cand)
        return dict(empty, status="zero_bound_exact" if exact else "zero_bound_violation",
                    max_absolute_error=peak, rms_error=_rms(errors), reference_rms=_rms(ref))
    scaled_ref = tuple(value / b for value in ref)
    scaled_errors = tuple(value / b for value in errors)
    if not all(math.isfinite(value) for value in scaled_ref + scaled_errors):
        raise ValueError("nonfinite normalized metric")
    error_rms = _rms(scaled_errors)
    ref_rms = _rms(scaled_ref)
    eligible = ref_rms >= 1.0e-8
    result = dict(empty, status="eligible" if eligible else "absolute_only",
                  max_absolute_error=peak, rms_error=error_rms * b, reference_rms=ref_rms * b,
                  peak_B=max(abs(value) for value in scaled_errors),
                  normalized_rms_error=error_rms, normalized_reference_rms=ref_rms,
                  nrmse=error_rms / ref_rms if eligible else None)
    if any(type(value) is float and not math.isfinite(value) for value in result.values()):
        raise ValueError("nonfinite error metric")
    return result
