#!/usr/bin/env python3
"""Independent offline motion and retarded-path reference for the nominal rotary model.

Motion uses a private 80-digit Decimal context and immutable command anchors.
Geometry uses Cartesian binary64 coordinates; propagation uses bisection of the
local delay, never the production solver. This is not a real-time renderer or a
measured cabinet model. See docs/ROTARY_REFERENCE.md for the exact boundary.
"""

from __future__ import annotations

import argparse
from bisect import bisect_right
from dataclasses import dataclass
from decimal import (Context, Decimal, DecimalException, DivisionByZero,
                     InvalidOperation, Overflow, ROUND_FLOOR, ROUND_HALF_EVEN, localcontext)
import hashlib
from itertools import groupby
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence


REFERENCE_ID = "decimal-motion-cartesian-bisection-rotary-reference-v1"
MODEL_ID = "nominal-effective-mouth-rotary-v1"
CONTRACT_ID = "rotary-numerics-v1"
PRECISION = 80
SCALAR_EXPONENT_LIMIT = 1000000
STATE_EXPONENT_LIMIT = 999999999 + PRECISION - 1
SUPPORTED_RATES = (44100, 48000, 96000, 192000)
MAX_SECONDS = Decimal(86400)
MIN_QUERY_SECONDS = Decimal(-86400)
MAX_EVENTS = 4096
MAX_QUERIES = 4096
MAX_EVENT_BYTES = 1024 * 1024
REFERENCE_RESIDUAL_S = 1e-14
REFERENCE_ITERATIONS = 96
TWO_PI = Decimal(
    "6.283185307179586476925286766559005768394338798750211641949889184615632812572417997256069650684234135964296173026564613294187689219101164463450718816256962234900568205403877042211119289245897909860763928857621951331866892256951296467573566330542403818291297133846920697220908653296426787214520498282547"
)
ZERO = Decimal(0)
ONE = Decimal(1)
_DECIMAL_TEXT = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")


class ReferenceError(ValueError):
    """Invalid reference input or an explicitly failed numerical check."""


def _context():
    # Use a fresh context so a caller's precision, rounding or traps cannot
    # silently change the oracle. The exponent range retains long decay tails.
    return localcontext(Context(prec=PRECISION, rounding=ROUND_HALF_EVEN,
                                Emin=-999999999, Emax=999999999, capitals=1, clamp=0,
                                flags=[], traps=[InvalidOperation, DivisionByZero, Overflow]))


def _decimal_text(value: Decimal) -> str:
    with _context():
        return str(value)


def decimal_value(value: Any) -> Decimal:
    """Read a finite scalar; floats retain their exact binary64 value.

    Strings/Decimal values retain decimal intent. Booleans, whitespace,
    underscores, nonfinite values and excessively large representations reject.
    """
    return _read_decimal(value, SCALAR_EXPONENT_LIMIT)


def _read_decimal(value: Any, exponent_limit: int) -> Decimal:
    # A computed state can retain a compact long-decay tail throughout the
    # private context's range. Ordinary scalar inputs keep their tighter
    # representation bound; both paths retain the same finite/digit checks.
    if isinstance(value, bool):
        raise ReferenceError("a boolean is not a physical scalar")
    if isinstance(value, Decimal):
        result = value
    elif isinstance(value, int):
        result = Decimal(value)
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ReferenceError("scalar must be finite")
        result = Decimal.from_float(value)
    elif isinstance(value, str) and len(value) <= 256 and _DECIMAL_TEXT.fullmatch(value):
        result = Decimal(value)
    else:
        raise ReferenceError("expected a finite number or decimal numeric string")
    if not result.is_finite() or len(result.as_tuple().digits) > 256:
        raise ReferenceError("scalar must be finite and contain at most 256 digits")
    if abs(result.as_tuple().exponent) > exponent_limit:
        raise ReferenceError("scalar exponent is outside the reference domain")
    return ZERO if result.is_zero() else result


def _bounded(value: Any, lower: Decimal | int, upper: Decimal | int, name: str,
             *, state_value: bool = False) -> Decimal:
    result = _read_decimal(value, STATE_EXPONENT_LIMIT if state_value else SCALAR_EXPONENT_LIMIT)
    if not Decimal(lower) <= result <= Decimal(upper):
        raise ReferenceError(f"{name} is outside [{lower}, {upper}]")
    return result


def _command(value: Any) -> str:
    if type(value) is not str or value not in ("chorale", "tremolo"):
        raise ReferenceError("command must be exactly chorale or tremolo")
    return value


def _integer(value: Any, lower: int, upper: int, name: str) -> int:
    if type(value) is not int or not lower <= value <= upper:
        raise ReferenceError(f"{name} must be an integer in [{lower}, {upper}]")
    return value


def frame_time(frame: int, sample_rate: int) -> Decimal:
    """Exact integer frame/rate relation rounded only to the private context."""
    if type(sample_rate) is not int or sample_rate not in SUPPORTED_RATES:
        raise ReferenceError("unsupported sample rate")
    _integer(frame, -86400 * sample_rate, 86400 * sample_rate, "frame")
    with _context():
        return Decimal(frame) / Decimal(sample_rate)


@dataclass(frozen=True)
class MotionProfile:
    slow_rad_s: Decimal
    fast_rad_s: Decimal
    tau_up_s: Decimal
    tau_down_s: Decimal
    direction: int

    def __post_init__(self) -> None:
        for key in ("slow_rad_s", "fast_rad_s"):
            object.__setattr__(self, key, _bounded(getattr(self, key), 0, 200, key))
        for key in ("tau_up_s", "tau_down_s"):
            object.__setattr__(self, key, _bounded(getattr(self, key), Decimal("0.001"), 60, key))
        if self.slow_rad_s > self.fast_rad_s:
            raise ReferenceError("slow speed must not exceed fast speed")
        if type(self.direction) is not int or self.direction not in (-1, 1):
            raise ReferenceError("direction must be integer -1 or +1")

    def target(self, command: str) -> Decimal:
        return self.slow_rad_s if _command(command) == "chorale" else self.fast_rad_s


@dataclass(frozen=True)
class MotionState:
    # Unwrapped angle retains the physical history independently of phase display.
    angle_rad: Decimal
    speed_rad_s: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "angle_rad", _bounded(
            self.angle_rad, -(10**22), 10**22, "angle", state_value=True))
        object.__setattr__(self, "speed_rad_s", _bounded(
            self.speed_rad_s, 0, 200, "speed", state_value=True))

    def wrapped(self) -> tuple[Decimal, int]:
        with _context():
            turns = int((self.angle_rad / TWO_PI).to_integral_value(rounding=ROUND_FLOOR))
            phase = self.angle_rad - Decimal(turns) * TWO_PI
            # The branch accounts only for Decimal rounding at a mathematical
            # turn boundary; it does not reset the retained unwrapped angle.
            if phase < 0:
                phase += TWO_PI
                turns -= 1
            elif phase >= TWO_PI:
                phase -= TWO_PI
                turns += 1
            return ZERO if phase == 0 else +phase, turns

    def as_dict(self) -> dict[str, Any]:
        phase, turns = self.wrapped()
        return {"angle_rad": _decimal_text(self.angle_rad), "phase_rad": _decimal_text(phase),
                "turns": turns, "speed_rad_s": _decimal_text(self.speed_rad_s)}


@dataclass(frozen=True)
class CommandEvent:
    time_s: Decimal
    command: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "time_s", _bounded(self.time_s, 0, MAX_SECONDS, "event time"))
        object.__setattr__(self, "command", _command(self.command))


@dataclass(frozen=True)
class MotionSegment:
    time_s: Decimal
    initial: MotionState
    command: str
    target_rad_s: Decimal
    tau_s: Decimal


def _exponential_remainders(z: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    """Return exp(-z), 1-exp(-z), z+exp(-z)-1 without small-z cancellation."""
    exponential = (-z).exp()
    if z == 0:
        return ONE, ZERO, ZERO
    if z >= Decimal("0.5"):
        return exponential, ONE - exponential, z + exponential - ONE
    # Independently sum q=z-z^2/2!+... and g=z^2/2!-z^3/3!+...
    term = z
    q = term
    g = ZERO
    for order in range(2, 2049):
        term *= -z / Decimal(order)
        next_q = q + term
        next_g = g - term
        if next_q == q and next_g == g:
            return exponential, q, g
        q, g = next_q, next_g
    raise ReferenceError("Decimal remainder series did not converge within its offline bound")


def evaluate_segment(initial: MotionState, target_rad_s: Any, tau_s: Any,
                     direction: int, elapsed_s: Any) -> MotionState:
    """Analytical speed/angle evaluation; no recursive sample integration."""
    if not isinstance(initial, MotionState):
        raise ReferenceError("initial must be a MotionState")
    target = _bounded(target_rad_s, 0, 200, "target speed")
    tau = _bounded(tau_s, Decimal("0.001"), 60, "time constant")
    elapsed = _bounded(elapsed_s, 0, MAX_SECONDS, "elapsed time")
    if type(direction) is not int or direction not in (-1, 1):
        raise ReferenceError("direction must be integer -1 or +1")
    if elapsed == 0:
        return initial
    with _context():
        z = elapsed / tau
        exponential, q, g = _exponential_remainders(z)
        difference = target - initial.speed_rad_s
        if z < Decimal("0.5"):
            speed = initial.speed_rad_s + difference * q
            distance = initial.speed_rad_s * elapsed + difference * tau * g
        else:
            # Preserve a tiny decaying residual rather than subtracting two
            # nearly equal speeds. The long-time angle form avoids cancellation.
            speed = target + (initial.speed_rad_s - target) * exponential
            distance = target * elapsed + (initial.speed_rad_s - target) * tau * q
        return MotionState(+(initial.angle_rad + Decimal(direction) * distance), +speed)


@dataclass(frozen=True, init=False)
class RotorTimeline:
    """Immutable complete offline history, not a bounded real-time history ring.

    Equal-time commands resolve in caller order; only the last command at that
    time has a positive-duration effect. Repeating the current command retains
    the existing anchor. Negative time extrapolates the initial speed uniformly.
    """

    profile: MotionProfile
    initial: MotionState
    initial_command: str
    events: tuple[CommandEvent, ...]
    segments: tuple[MotionSegment, ...]
    _times: tuple[Decimal, ...]

    def __init__(self, profile: MotionProfile, initial_phase_rad: Any,
                 initial_speed_rad_s: Any, initial_command: str = "chorale",
                 events: Iterable[CommandEvent] = (), *, initial_turns: int = 0) -> None:
        if not isinstance(profile, MotionProfile):
            raise ReferenceError("profile must be a MotionProfile")
        phase = decimal_value(initial_phase_rad)
        if not ZERO <= phase < TWO_PI:
            raise ReferenceError("initial phase must lie in [0, 2*pi)")
        turns = _integer(initial_turns, -(2**63), 2**63 - 1, "initial turns")
        with _context():
            angle = phase + Decimal(turns) * TWO_PI
        initial = MotionState(angle, _bounded(initial_speed_rad_s, 0, 200, "initial speed"))
        command = _command(initial_command)
        retained: list[CommandEvent] = []
        previous = ZERO
        for event in events:
            if len(retained) == MAX_EVENTS:
                raise ReferenceError("too many offline events")
            if not isinstance(event, CommandEvent) or event.time_s < previous:
                raise ReferenceError("events must be CommandEvent objects in nondecreasing time order")
            retained.append(event)
            previous = event.time_s
        object.__setattr__(self, "profile", profile)
        object.__setattr__(self, "initial", initial)
        object.__setattr__(self, "initial_command", command)
        object.__setattr__(self, "events", tuple(retained))
        segments = [self._anchor(ZERO, initial, command)]
        for time_s, group in groupby(retained, key=lambda event: event.time_s):
            final_command = list(group)[-1].command
            if final_command == command:
                continue
            previous_segment = segments[-1]
            with _context():
                elapsed = time_s - previous_segment.time_s
            state = evaluate_segment(previous_segment.initial, previous_segment.target_rad_s,
                                     previous_segment.tau_s, profile.direction, elapsed)
            anchor = self._anchor(time_s, state, final_command)
            if time_s == segments[-1].time_s:
                segments[-1] = anchor
            else:
                segments.append(anchor)
            command = final_command
        object.__setattr__(self, "segments", tuple(segments))
        object.__setattr__(self, "_times", tuple(segment.time_s for segment in segments))

    def _anchor(self, time_s: Decimal, state: MotionState, command: str) -> MotionSegment:
        target = self.profile.target(command)
        tau = self.profile.tau_up_s if target >= state.speed_rad_s else self.profile.tau_down_s
        return MotionSegment(time_s, state, command, target, tau)

    def state_at(self, time_s: Any) -> MotionState:
        time = _bounded(time_s, MIN_QUERY_SECONDS, MAX_SECONDS, "query time")
        if time < 0:
            with _context():
                angle = self.initial.angle_rad + Decimal(self.profile.direction) * self.initial.speed_rad_s * time
                return MotionState(+angle, self.initial.speed_rad_s)
        segment = self.segments[bisect_right(self._times, time) - 1]
        with _context():
            elapsed = time - segment.time_s
        return evaluate_segment(segment.initial, segment.target_rad_s, segment.tau_s,
                                self.profile.direction, elapsed)

    def command_at(self, time_s: Any) -> str:
        time = _bounded(time_s, MIN_QUERY_SECONDS, MAX_SECONDS, "query time")
        return self.initial_command if time < 0 else self.segments[bisect_right(self._times, time) - 1].command


def _float(value: Any, minimum: float, maximum: float, name: str) -> float:
    result = float(decimal_value(value))
    if not math.isfinite(result) or not minimum <= result <= maximum:
        raise ReferenceError(f"{name} is outside [{minimum}, {maximum}]")
    return result


def _vector(value: Any, name: str) -> tuple[float, float, float]:
    if not isinstance(value, (tuple, list)) or len(value) != 3:
        raise ReferenceError(f"{name} must contain three coordinates")
    return tuple(_float(component, -10.0, 10.0, name) for component in value)  # type: ignore[return-value]


@dataclass(frozen=True)
class CircularGeometry:
    origin_m: tuple[float, float, float]
    radius_m: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "origin_m", _vector(self.origin_m, "axis origin"))
        object.__setattr__(self, "radius_m", _float(self.radius_m, 0.0, 1.0, "radius"))


def distance_bounds(geometry: CircularGeometry, microphone_m: Sequence[float]) -> tuple[float, float]:
    microphone = _vector(microphone_m, "microphone")
    dx, dy, dz = (microphone[i] - geometry.origin_m[i] for i in range(3))
    horizontal = math.hypot(dx, dy)
    return (math.hypot(horizontal - geometry.radius_m, dz),
            math.hypot(horizontal + geometry.radius_m, dz))


def circular_state(geometry: CircularGeometry, state: MotionState,
                   direction: int) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    if type(direction) is not int or direction not in (-1, 1):
        raise ReferenceError("direction must be integer -1 or +1")
    phase, _ = state.wrapped()
    cosine, sine = math.cos(float(phase)), math.sin(float(phase))
    radius = geometry.radius_m
    signed_speed = direction * float(state.speed_rad_s)
    position = (geometry.origin_m[0] + radius * cosine,
                geometry.origin_m[1] + radius * sine, geometry.origin_m[2])
    velocity = (-radius * signed_speed * sine, radius * signed_speed * cosine, 0.0)
    return position, velocity


def microphone_incidence(forward_axis: Sequence[float], source_to_microphone: Sequence[float]) -> float:
    """Cosine of the incoming bearing, with the sign required by atlas p.314."""
    axis = _vector(forward_axis, "microphone forward axis")
    outgoing = _vector(source_to_microphone, "source-to-microphone unit vector")
    if abs(math.hypot(*axis) - 1.0) > 1e-12 or abs(math.hypot(*outgoing) - 1.0) > 1e-12:
        raise ReferenceError("incidence arguments must be unit vectors")
    return -math.fsum(axis[i] * outgoing[i] for i in range(3))


@dataclass(frozen=True)
class PathResult:
    observation_time_s: Decimal
    emission_time_s: Decimal
    delay_s: float
    distance_m: float
    residual_s: float
    derivative: float
    doppler_ratio: float
    pressure_gain: float
    position_m: tuple[float, float, float]
    velocity_m_s: tuple[float, float, float]
    source_to_microphone_unit: tuple[float, float, float]
    emission_state: MotionState
    iterations: int
    bracket_width_s: float

    def as_dict(self) -> dict[str, Any]:
        return {"observation_time_s": _decimal_text(self.observation_time_s),
                "emission_time_s": _decimal_text(self.emission_time_s), "delay_s": self.delay_s,
                "distance_m": self.distance_m, "residual_s": self.residual_s,
                "retarded_derivative": self.derivative, "doppler_ratio": self.doppler_ratio,
                "pressure_gain": self.pressure_gain, "position_m": self.position_m,
                "velocity_m_s": self.velocity_m_s,
                "source_to_microphone_unit": self.source_to_microphone_unit,
                "microphone_incoming_bearing": tuple(-v for v in self.source_to_microphone_unit),
                "emission_state": self.emission_state.as_dict(), "iterations": self.iterations,
                "bracket_width_s": self.bracket_width_s}


def solve_retarded_path(timeline: RotorTimeline, geometry: CircularGeometry,
                        microphone_m: Sequence[float], observation_time_s: Any,
                        sound_speed_m_s: Any = 343, reference_distance_m: Any = 1,
                        *, residual_tolerance_s: float = REFERENCE_RESIDUAL_S,
                        max_iterations: int = REFERENCE_ITERATIONS) -> PathResult:
    """Bracket and bisect d - norm(m-q(t-d))/c = 0; no Newton iteration.

    Absolute time subtraction is done at Decimal precision; the root variable
    is local binary64 delay. The returned residual uses that local equation.
    A failed residual or causality check raises instead of returning a pass.
    """
    observation = _bounded(observation_time_s, -1, MAX_SECONDS, "observation time")
    microphone = _vector(microphone_m, "microphone")
    c = _float(sound_speed_m_s, 300.0, 380.0, "sound speed")
    reference_distance = _float(reference_distance_m, 0.02, 10.0, "reference distance")
    tolerance = _float(residual_tolerance_s, math.ulp(0.0), 1e-7, "residual tolerance")
    _integer(max_iterations, 1, REFERENCE_ITERATIONS, "iteration budget")
    minimum, maximum = distance_bounds(geometry, microphone)
    if minimum < 0.02 or maximum > 20.0:
        raise ReferenceError("full-orbit path must remain between 0.02 and 20 metres")
    speed_bound = float(max(timeline.initial.speed_rad_s, timeline.profile.slow_rad_s,
                            timeline.profile.fast_rad_s))
    if geometry.radius_m * speed_bound > 0.25 * c:
        raise ReferenceError("tangential speed exceeds the admitted quarter-sound-speed bound")

    def evaluate(delay: float) -> tuple[float, Decimal, MotionState, tuple, tuple, float, tuple, float]:
        with _context():
            emission = observation - Decimal.from_float(delay)
        state = timeline.state_at(emission)
        position, velocity = circular_state(geometry, state, timeline.profile.direction)
        difference = tuple(microphone[i] - position[i] for i in range(3))
        distance = math.hypot(*difference)
        if not distance > 0.0 or not math.isfinite(distance):
            raise ReferenceError("nonpositive or nonfinite propagation distance")
        unit = tuple(value / distance for value in difference)
        derivative = 1.0 - math.fsum(unit[i] * velocity[i] for i in range(3)) / c
        if not 0.75 - 2e-15 <= derivative <= 1.25 + 2e-15:
            raise ReferenceError("retarded derivative violates the admitted subsonic bound")
        return delay - distance / c, emission, state, position, velocity, distance, unit, derivative

    # Widen only the analytical distance bracket by roundoff; neither geometry
    # nor a computed residual is clamped. This covers Cartesian norm rounding
    # at a turning-point endpoint and is retained in bracket_width_s.
    margin = 32.0 * math.ulp(max(1.0, maximum))
    lo = max(0.0, minimum - margin) / c
    hi = (maximum + margin) / c
    low_result, high_result = evaluate(lo), evaluate(hi)
    if low_result[0] > 0.0 or high_result[0] < 0.0:
        raise ReferenceError("analytical delay bracket does not enclose a root")
    selected = (lo, low_result) if abs(low_result[0]) <= abs(high_result[0]) else (hi, high_result)
    iterations = 0
    for iteration in range(max_iterations):
        if abs(selected[1][0]) <= tolerance:
            break
        middle = lo + (hi - lo) * 0.5
        if middle == lo or middle == hi:
            break
        result = evaluate(middle)
        iterations = iteration + 1
        if abs(result[0]) < abs(selected[1][0]):
            selected = middle, result
        if result[0] < 0.0:
            lo = middle
        else:
            hi = middle
    delay, result = selected
    residual, emission, state, position, velocity, distance, unit, derivative = result
    if abs(residual) > tolerance or delay <= 0.0 or emission >= observation:
        raise ReferenceError(f"retarded reference did not meet its residual/causality gate: {residual!r} s")
    return PathResult(observation, emission, delay, distance, residual, derivative,
                      1.0 / derivative, reference_distance / distance,
                      position, velocity, unit, state, iterations, hi - lo)


@dataclass(frozen=True)
class ReferenceScene:
    model_id: str
    profile_id: str
    timelines: Mapping[str, RotorTimeline]
    geometries: Mapping[str, CircularGeometry]
    microphones: Mapping[str, tuple[float, float, float]]
    sound_speed_m_s: float
    reference_distance_m: float


def scene_from_normalized(profile: Mapping[str, Any],
                          events: Mapping[str, Iterable[CommandEvent]] | None = None) -> ReferenceScene:
    """Adapt an admitted SI mapping; mathematical implementations stay independent."""
    if profile.get("model_id") != MODEL_ID or profile.get("contract_id") != CONTRACT_ID:
        raise ReferenceError("profile model or numerical contract does not match this reference")
    commands = {"horn": (), "drum": ()} if events is None else events
    if set(commands) != {"horn", "drum"}:
        raise ReferenceError("events must provide exactly horn and drum histories")
    timelines, geometries = {}, {}
    for rotor in ("horn", "drum"):
        data = profile["rotors"][rotor]
        parameters = MotionProfile(**data["motion"])
        timelines[rotor] = RotorTimeline(parameters, data["initial_phase_rad"],
                                         data["initial_speed_rad_s"], data["initial_command"], commands[rotor])
        geometries[rotor] = CircularGeometry(data["origin_m"], data["radius_m"])
    microphones = {item["id"]: _vector(item["position_m"], "microphone") for item in profile["microphones"]}
    if set(microphones) != {"left", "right"} or len(profile["microphones"]) != 2:
        raise ReferenceError("scene must have one left and one right microphone")
    c = _float(profile["sound_speed_m_s"], 300, 380, "sound speed")
    reference_distance = _float(profile["reference_distance_m"], 0.02, 10, "reference distance")
    for rotor in ("horn", "drum"):
        speed = max(timelines[rotor].initial.speed_rad_s, timelines[rotor].profile.fast_rad_s)
        if geometries[rotor].radius_m * float(speed) > 0.25 * c:
            raise ReferenceError("scene exceeds the subsonic envelope")
        for microphone in microphones.values():
            lower, upper = distance_bounds(geometries[rotor], microphone)
            if lower < 0.02 or upper > 20.0:
                raise ReferenceError("scene path is outside the admitted geometry")
    return ReferenceScene(MODEL_ID, profile["profile_id"], MappingProxyType(timelines), MappingProxyType(geometries),
                          MappingProxyType(microphones), c, reference_distance)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReferenceError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ReferenceError(f"nonfinite JSON constant: {value}")


def load_events(path: str | Path, sample_rate: int) -> tuple[dict[str, tuple[CommandEvent, ...]], str]:
    """Load strict frame-stamped per-rotor events, preserving input tie order."""
    frame_time(0, sample_rate)
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NONBLOCK", 0)
    fd = os.open(path, flags)
    with os.fdopen(fd, "rb") as stream:
        metadata = os.fstat(stream.fileno())
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_EVENT_BYTES:
            raise ReferenceError("event input must be a bounded regular file")
        data = stream.read(MAX_EVENT_BYTES + 1)
    if not data or len(data) > MAX_EVENT_BYTES:
        raise ReferenceError("event file is empty or oversized")
    try:
        parsed = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object,
                            parse_constant=_reject_constant)
    except (UnicodeDecodeError, ValueError, RecursionError) as error:
        if isinstance(error, ReferenceError):
            raise
        raise ReferenceError(f"invalid event JSON: {error}") from error
    if type(parsed) is not dict or set(parsed) != {"schema_version", "events"}:
        raise ReferenceError("event object must contain only schema_version and events")
    if type(parsed["schema_version"]) is not int or parsed["schema_version"] != 1:
        raise ReferenceError("unsupported event schema version")
    rows = parsed["events"]
    if type(rows) is not list or len(rows) > MAX_EVENTS:
        raise ReferenceError("events must be a bounded list")
    result: dict[str, list[CommandEvent]] = {"horn": [], "drum": []}
    previous_frame = 0
    for row in rows:
        if type(row) is not dict or set(row) != {"frame", "rotor", "command"}:
            raise ReferenceError("each event needs exactly frame, rotor and command")
        frame = _integer(row["frame"], 0, 86400 * sample_rate, "event frame")
        if frame < previous_frame or type(row["rotor"]) is not str or row["rotor"] not in result:
            raise ReferenceError("events must be globally ordered and select horn or drum")
        result[row["rotor"]].append(CommandEvent(frame_time(frame, sample_rate), _command(row["command"])))
        previous_frame = frame
    return {rotor: tuple(values) for rotor, values in result.items()}, hashlib.sha256(data).hexdigest()


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ReferenceError(f"arguments: {message}")


def main(argv: list[str] | None = None) -> int:
    try:
        parser = _Parser(description=__doc__)
        parser.add_argument("--profile", type=Path, required=True)
        parser.add_argument("--events", type=Path)
        parser.add_argument("--sample-rate", type=int, choices=SUPPORTED_RATES, default=48000)
        parser.add_argument("--time", action="append", help="exact observation time in seconds; repeatable")
        parser.add_argument("--start-frame", type=int)
        parser.add_argument("--frames", type=int)
        parser.add_argument("--step", type=int)
        parser.add_argument("--paths", action="store_true", help="also solve all four horn/drum-to-mic paths")
        args = parser.parse_args(argv)
        if args.time is not None and any(value is not None for value in (args.start_frame, args.frames, args.step)):
            raise ReferenceError("--time cannot be combined with frame-range arguments")
        if args.time is not None:
            if len(args.time) > MAX_QUERIES:
                raise ReferenceError("too many query times")
            times = [_bounded(value, -1, MAX_SECONDS, "query time") for value in args.time]
        else:
            count = _integer(1 if args.frames is None else args.frames, 1, MAX_QUERIES, "query count")
            first = _integer(0 if args.start_frame is None else args.start_frame,
                             -args.sample_rate, 86400 * args.sample_rate, "start frame")
            step = _integer(1 if args.step is None else args.step, 1, 86400 * args.sample_rate, "step")
            times = [frame_time(first + index * step, args.sample_rate) for index in range(count)]
        if __package__:
            from .validate_rotary_profile import load_profile_with_digest, normalized_profile
        else:
            from validate_rotary_profile import load_profile_with_digest, normalized_profile
        profile, digest = load_profile_with_digest(args.profile)
        commands, event_digest = ({"horn": (), "drum": ()}, None) if args.events is None else load_events(args.events, args.sample_rate)
        scene = scene_from_normalized(normalized_profile(profile), commands)
        rows = []
        for time_s in times:
            row = {"observation_time_s": _decimal_text(time_s),
                   "states": {rotor: scene.timelines[rotor].state_at(time_s).as_dict() for rotor in ("horn", "drum")}}
            if args.paths:
                row["paths"] = {
                    f"{rotor}:{microphone}": solve_retarded_path(
                        scene.timelines[rotor], scene.geometries[rotor], scene.microphones[microphone], time_s,
                        scene.sound_speed_m_s, scene.reference_distance_m).as_dict()
                    for rotor in ("horn", "drum") for microphone in ("left", "right")}
            rows.append(row)
        print(json.dumps({"status": "complete", "schema_version": 1, "reference_id": REFERENCE_ID,
                          "model_id": scene.model_id, "contract_id": CONTRACT_ID, "profile_id": scene.profile_id,
                          "profile_file_sha256": digest, "event_file_sha256": event_digest,
                          "motion_precision_digits": PRECISION, "path_geometry_precision": "binary64",
                          "algorithmic_latency_applied": False, "sample_rate": args.sample_rate,
                          "path_residual_budget_s": REFERENCE_RESIDUAL_S if args.paths else None,
                          "physical_status": "unmeasured", "queries": rows}, allow_nan=False, sort_keys=True))
        return 0
    except (ReferenceError, ValueError, TypeError, KeyError, OSError, DecimalException) as error:
        print(json.dumps({"status": "rejected", "reference_id": REFERENCE_ID,
                          "error": str(error)}, allow_nan=False, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
