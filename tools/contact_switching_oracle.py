"""Independent continuous oracle for contact-switching-validation-v1.

This module consumes already admitted fixture dictionaries.  It deliberately
imports no candidate implementation.  A global exact event frontier evolves
all keys; direct GL8 integration then evaluates the unsampled switched signal.
It is an offline synthetic reference, not a model of measured contact physics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
import math
from typing import NamedTuple


PROTOCOL_ID = "contact-switching-validation-v1"
ORACLE_ID = "independent-frontier-gl8-v1"
H = 16
PANEL_WIDTHS = (1.0, 0.5, 0.25)

# Positive abscissae and corresponding weights on [-1, 1].  The author checks
# verify every polynomial moment through degree 15 independently of rendering.
_GL8 = (
    (0.183434642495649804939476, 0.362683783378361982965150),
    (0.525532409916328985817739, 0.313706645877887287337962),
    (0.796666477413626739591554, 0.222381034453374470544356),
    (0.960289856497536231683561, 0.101228536290376259152531),
)


class Edge(NamedTuple):
    u: Fraction
    key_index: int
    contact_index: int
    closed_after: bool


class FinalKey(NamedTuple):
    position: Fraction
    target: Fraction
    closed: tuple[bool, ...]


class OracleTrajectory(NamedTuple):
    edges: tuple[Edge, ...]
    final_keys: tuple[FinalKey, ...]


class Evaluation(NamedTuple):
    values: tuple[float, ...]
    normalizer: float
    integrand_evaluations: int


class OracleBudgetExceeded(RuntimeError):
    """The experiment is incomplete; this is never a numerical pass."""


@dataclass
class EvaluationBudget:
    """Share one instance across the entire study, including responses.

    A real or complex quadrature integrand at one GL8 node counts once.  Exact
    zero signal intervals require no nodes.  Cached independent normalizers
    are charged once per width in this object, never silently recalculated.
    """

    limit: int = 10_000_000
    count: int = field(default=0, init=False)
    _normalizers: dict[float, float] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        if type(self.limit) is not int or not 0 <= self.limit <= 10_000_000:
            raise ValueError("oracle evaluation limit must be an integer in [0, 10000000]")

    def consume(self, count: int) -> None:
        if type(count) is not int or count < 0:
            raise ValueError("invalid oracle evaluation count")
        if self.count + count > self.limit:
            raise OracleBudgetExceeded(
                f"oracle evaluation cap {self.limit} would be exceeded at {self.count + count}")
        self.count += count


def _q(value: int | float) -> Fraction:
    if type(value) is int:
        return Fraction(value)
    if type(value) is float and math.isfinite(value):
        return Fraction.from_float(value)
    raise ValueError("oracle requires finite admitted numeric values")


def trajectory(raw: dict) -> OracleTrajectory:
    """Independently evolve all keys at command/arrival/threshold frontiers.

    This event-driven formulation never builds or consumes candidate segments.
    Incoming threshold events precede commands, including at the observation
    end.  Identical-time commands consume no time and retain caller order.
    """
    rate, frames = raw["sample_rate_hz"], raw["frames"]
    keys = raw["keys"]
    if rate not in (44100, 48000, 96000) or type(frames) is not int or not 0 <= frames <= 4096:
        raise ValueError("oracle requires an admitted rate and frame count")
    if not 1 <= len(keys) <= 4 or len(raw["targets"]) > 512:
        raise ValueError("oracle fixture capacity exceeded")
    key_lookup = {key["key_id"]: index for index, key in enumerate(keys)}
    commands = sorted(
        ((_q(row["frame"]) + _q(row["fraction"]), ordinal,
          key_lookup[row["key_id"]], _q(row["target"]))
         for ordinal, row in enumerate(raw["targets"])), key=lambda row: (row[0], row[1]))
    if any(not 0 <= row[0] <= frames or not 0 <= row[3] <= 1 for row in commands):
        raise ValueError("oracle requires admitted target coordinates")
    on = [tuple(_q(v) for v in key["on"]) for key in keys]
    off = [tuple(_q(v) for v in key["off"]) for key in keys]
    rise = [1 / (rate * _q(key["press_seconds"])) for key in keys]
    fall = [-1 / (rate * _q(key["release_seconds"])) for key in keys]
    positions = [Fraction(0) for _ in keys]
    targets = [Fraction(0) for _ in keys]
    closed = [[False] * 9 for _ in keys]
    edges = []
    cursor = 0
    now = Fraction(0)
    finish = Fraction(frames)

    while True:
        # Events on entry have already resolved under the incoming velocity.
        while cursor < len(commands) and commands[cursor][0] == now:
            _, _, key_index, value = commands[cursor]
            targets[key_index] = value
            cursor += 1
        if now == finish:
            break

        next_time = finish
        if cursor < len(commands):
            next_time = min(next_time, commands[cursor][0])
        velocities = []
        pending = []
        for key_index, (position, target) in enumerate(zip(positions, targets)):
            velocity = (rise[key_index] if target > position else
                        fall[key_index] if target < position else Fraction(0))
            velocities.append(velocity)
            if not velocity:
                continue
            arrival = now + (target - position) / velocity
            next_time = min(next_time, arrival)
            for contact_index in range(9):
                if velocity > 0:
                    threshold = on[key_index][contact_index]
                    eligible = not closed[key_index][contact_index] and position < threshold <= target
                else:
                    threshold = off[key_index][contact_index]
                    eligible = closed[key_index][contact_index] and target <= threshold < position
                if eligible:
                    hit = now + (threshold - position) / velocity
                    pending.append(Edge(hit, key_index, contact_index, velocity > 0))
                    next_time = min(next_time, hit)
        if next_time <= now:
            raise ValueError("oracle frontier failed to advance; input is not admitted")
        duration = next_time - now
        for key_index, velocity in enumerate(velocities):
            positions[key_index] += duration * velocity
        for edge in pending:  # Nested key/contact traversal already supplies tie order.
            if edge.u == next_time:
                closed[edge.key_index][edge.contact_index] = edge.closed_after
                edges.append(edge)
        now = next_time

    final = tuple(FinalKey(position, target, tuple(bits))
                  for position, target, bits in zip(positions, targets, closed))
    return OracleTrajectory(tuple(edges), final)


def _sources(raw: dict) -> dict:
    return {source["source_id"]: source for source in raw["sources"]}


def raw_bound(raw: dict) -> float:
    """Smallest binary64 number at least the exact admitted raw bound."""
    sources = _sources(raw)
    exact = sum((abs(_q(gain)) * _q(sources[source_id]["amplitude"])
                 for key in raw["keys"]
                 for gain, source_id in zip(key["gains"], key["source_ids"])), Fraction(0))
    rounded = float(exact)
    return math.nextafter(rounded, math.inf) if _q(rounded) < exact else rounded


def probe_indices(raw: dict, path: OracleTrajectory) -> tuple[int, ...]:
    """Frozen protocol insertion order; never select probes from audio errors."""
    frames = raw["frames"]
    if frames == 0:
        return ()
    sources = _sources(raw)
    audible = []
    for edge in path.edges:
        key = raw["keys"][edge.key_index]
        amplitude = sources[key["source_ids"][edge.contact_index]]["amplitude"]
        if key["gains"][edge.contact_index] != 0 and amplitude != 0 and edge.u < frames:
            audible.append(edge.u)
    selected = []
    seen = set()

    def add(index: int) -> None:
        if -H <= index <= frames + H and index not in seen:
            selected.append(index)
            seen.add(index)

    for index in (-16, -15, -1, 0, 1, frames - 1, frames, frames + 15, frames + 16):
        add(index)
    for edge_u in audible:
        add(math.floor(edge_u))
        add(math.ceil(edge_u))
    if audible:
        for endpoint in (audible[0] - H, audible[-1] + H):
            add(math.floor(endpoint))
            add(math.ceil(endpoint))
    if len(selected) > 64:
        raise ValueError("mandatory oracle probes exceed the frozen capacity")
    for index in (-H + i * (frames + 2 * H) // 63 for i in range(64)):
        if len(selected) == 64:
            break
        add(index)
    for index in range(-H, frames + H + 1):
        if len(selected) == 64:
            break
        add(index)
    if len(selected) != 64:
        raise ValueError("nonempty fixture has fewer than 64 distinct output indices")
    return tuple(selected)


def kernel(v: float) -> float:
    """Independent continuous kernel; never a candidate coefficient lookup."""
    distance = abs(v)
    if distance >= H:
        return 0.0
    carrier = 0.9 if distance == 0.0 else math.sin(0.9 * math.pi * distance) / (math.pi * distance)
    angle = math.pi * distance / H
    return carrier * (0.42 + 0.5 * math.cos(angle) + 0.08 * math.cos(2 * angle))


def _width(value: float) -> float:
    if type(value) not in (int, float) or value not in PANEL_WIDTHS:
        raise ValueError("oracle panel width must be 1, 0.5 or 0.25")
    return float(value)


def _nodes(left: Fraction, right: Fraction, width: float):
    # Exact lengths retain a tiny interval even if its endpoint displays agree.
    panels = math.ceil((right - left) / _q(width))
    if panels <= 0:
        return
    step = (right - left) / panels
    half = float(step / 2)
    for panel in range(panels):
        midpoint = float(left + (Fraction(2 * panel + 1, 2) * step))
        for node, weight in _GL8:
            yield midpoint - half * node, half * weight
            yield midpoint + half * node, half * weight


def normalizer(panel_width: float, *, budget: EvaluationBudget | None = None) -> float:
    width = _width(panel_width)
    budget = budget if budget is not None else EvaluationBudget()
    if width not in budget._normalizers:
        nodes = tuple(_nodes(Fraction(-H), Fraction(H), width))
        budget.consume(len(nodes))
        value = math.fsum(weight * kernel(v) for v, weight in nodes)
        if not math.isfinite(value) or value <= 0:
            raise ValueError("oracle continuous normalizer is not positive finite")
        budget._normalizers[width] = value
    return budget._normalizers[width]


def _spans(raw: dict, path: OracleTrajectory, ceil_edges: bool):
    """Partition at every independent edge, including muted contact events."""
    finish = Fraction(raw["frames"])
    sources = _sources(raw)
    state = [[False] * 9 for _ in raw["keys"]]
    last = Fraction(0)
    edges = ((Fraction(math.ceil(e.u)) if ceil_edges else e.u, e) for e in path.edges)
    for coordinate, edge in list(edges) + [(finish, None)]:
        coordinate = min(coordinate, finish)
        if coordinate > last:
            routes = []
            for key_index, key in enumerate(raw["keys"]):
                for contact_index, is_closed in enumerate(state[key_index]):
                    gain = key["gains"][contact_index]
                    source = sources[key["source_ids"][contact_index]]
                    if is_closed and gain != 0 and source["amplitude"] != 0:
                        routes.append((gain, source["source_id"]))
            yield last, coordinate, tuple(routes)
            last = coordinate
        if edge is not None:
            state[edge.key_index][edge.contact_index] = edge.closed_after


def evaluate(raw: dict, path: OracleTrajectory, indices: tuple[int, ...] | list[int],
             panel_width: float, *, ceil_edges: bool = False,
             budget: EvaluationBudget | None = None) -> Evaluation:
    """Direct unsampled signal convolution at fixed integer observation probes.

    ceil_edges preserves original exact-event order when multiple edges collide.
    Its sole change is the declared physical edge-time quantization diagnostic.
    """
    width = _width(panel_width)
    if raw["frames"] == 0:
        raise ValueError("empty fixtures have no continuous quadrature grade")
    if any(type(n) is not int or not -H <= n <= raw["frames"] + H for n in indices):
        raise ValueError("oracle index outside the complete output range")
    budget = budget if budget is not None else EvaluationBudget()
    start_count = budget.count
    dc = normalizer(width, budget=budget)
    spans = tuple(_spans(raw, path, ceil_edges))
    sources = _sources(raw)
    rate = raw["sample_rate_hz"]
    values = []
    for index in indices:
        pieces = []
        for begin, end, routes in spans:
            if not routes:
                continue  # Algebraic zero, not uncounted numerical quadrature.
            left, right = max(begin, Fraction(index - H)), min(end, Fraction(index + H))
            if left >= right:
                continue
            source_ids = tuple(dict.fromkeys(source_id for _, source_id in routes))
            terms = []
            for u, weight in _nodes(left, right, width):
                budget.consume(1)
                signal = {source_id: sources[source_id]["amplitude"] * math.sin(
                    2 * math.pi * (sources[source_id]["phase_turns"]
                                   + sources[source_id]["frequency_hz"] * u / rate))
                          for source_id in source_ids}
                # Keep independent signed routes until the final sum at a node.
                value = math.fsum(gain * signal[source_id] for gain, source_id in routes)
                terms.append(weight * value * kernel(index - u))
            pieces.append(math.fsum(terms))
        value = math.fsum(pieces) / dc
        if not math.isfinite(value):
            raise ValueError("nonfinite continuous oracle result")
        values.append(value if value else 0.0)
    return Evaluation(tuple(values), dc, budget.count - start_count)


def continuous_response(frequencies, panel_width: float = 0.25, *,
                        budget: EvaluationBudget | None = None) -> dict:
    """Independent finite-grid continuous response, charged to the shared cap."""
    width = _width(panel_width)
    frequencies = tuple(frequencies)
    if len(frequencies) > 259 or any(type(nu) not in (int, float) or
                                    not math.isfinite(nu) or not 0 <= nu <= 2
                                    for nu in frequencies):
        raise ValueError("invalid bounded response grid")
    budget = budget if budget is not None else EvaluationBudget()
    start_count = budget.count
    dc = normalizer(width, budget=budget)
    nodes = tuple(_nodes(Fraction(-H), Fraction(H), width))
    rows = []
    for nu in frequencies:
        budget.consume(len(nodes))
        real = math.fsum(weight * kernel(v) * math.cos(2 * math.pi * nu * v)
                         for v, weight in nodes) / dc
        imaginary = math.fsum(-weight * kernel(v) * math.sin(2 * math.pi * nu * v)
                              for v, weight in nodes) / dc
        magnitude = math.hypot(real, imaginary)
        rows.append({"frequency_cycles_per_frame": nu, "real": real,
                     "imaginary": imaginary, "magnitude": magnitude,
                     "phase_radians": math.atan2(imaginary, real) if magnitude >= 1e-8 else None})
    return {"panel_width": width, "normalizer": dc, "responses": rows,
            "integrand_evaluations": budget.count - start_count}


def _source_value_slope(raw: dict, source: dict, u: Fraction) -> tuple[float, float]:
    phase = float(_q(source["phase_turns"]) + _q(source["frequency_hz"]) * u / raw["sample_rate_hz"])
    angle = 2 * math.pi * phase
    return (source["amplitude"] * math.sin(angle),
            source["amplitude"] * (2 * math.pi * source["frequency_hz"]) * math.cos(angle))


def edge_observations(raw: dict, path: OracleTrajectory) -> tuple[dict, ...]:
    """Independent exact edge identity and signed physical value/slope jumps."""
    sources = _sources(raw)
    rows = []
    for edge in path.edges:
        key = raw["keys"][edge.key_index]
        source = sources[key["source_ids"][edge.contact_index]]
        value, slope = _source_value_slope(raw, source, edge.u)
        multiplier = key["gains"][edge.contact_index] * (1 if edge.closed_after else -1)
        rows.append({"exact_u": {"numerator": str(edge.u.numerator), "denominator": str(edge.u.denominator)},
                     "key_index": edge.key_index, "contact_index": edge.contact_index,
                     "closed_after": edge.closed_after, "inside_observation": edge.u < raw["frames"],
                     "value_jump": multiplier * value,
                     "slope_jump_per_second": multiplier * slope})
    return tuple(rows)


def gate_jumps(raw: dict, path: OracleTrajectory) -> tuple[dict, ...]:
    """Observation boundary jumps use ungated limits, not physical N edges."""
    if raw["frames"] == 0:
        return ()
    sources = _sources(raw)
    closed = [[False] * 9 for _ in raw["keys"]]
    for edge in path.edges:
        if edge.u < raw["frames"]:
            closed[edge.key_index][edge.contact_index] = edge.closed_after
    value_terms, slope_terms = [], []
    for key_index, key in enumerate(raw["keys"]):
        for contact_index, is_closed in enumerate(closed[key_index]):
            if is_closed:
                value, slope = _source_value_slope(raw, sources[key["source_ids"][contact_index]],
                                                 Fraction(raw["frames"]))
                gain = key["gains"][contact_index]
                value_terms.append(gain * value)
                slope_terms.append(gain * slope)
    return ({"frame": 0, "value_jump": 0.0, "slope_jump_per_second": 0.0},
            {"frame": raw["frames"], "value_jump": -math.fsum(value_terms),
             "slope_jump_per_second": -math.fsum(slope_terms)})
