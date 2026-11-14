#!/usr/bin/env python3
"""Native R2 qualification against the separately implemented 80-digit oracle.

Run with HAMMOND_ROTARY_MOTION_PROBE_EXECUTABLE naming the compiled batch probe.
Optional --report PATH retains measured maxima/RMS, exact fixtures and identities.
There is no Python-only fallback: a missing native executable fails this gate.
"""

from __future__ import annotations

import argparse
from collections import Counter
from decimal import Context, Decimal, localcontext
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import rotary_reference as ref

D = Decimal
MEASUREMENT_CONTEXT = Context(prec=120, Emin=-999999999, Emax=999999999)
TAUS = (0.001, 0.01, 0.1, 1.0, 10.0, 60.0)
RATIOS = (0.0,) + tuple(10.0 ** exponent for exponent in range(-12, 3))
RATES = (44100, 48000, 96000, 192000)
SEED = 20261114016
SEMIGROUP_CASES = 1024
REPORT_PATH = None
PROBE_PATH = None


def decimal_input(value):
    """Keep binary inputs, with 40 guard digits beyond the oracle precision.

    Decimal.from_float can have >256 significant digits for very small normal
    binary64 values. Round only to 120 digits so those inputs satisfy the
    independent reference's scalar-admission cap without changing its 80-digit
    numerical result. Ordinary binary inputs remain exact.
    """
    with localcontext(MEASUREMENT_CONTEXT):
        return +D.from_float(value) if isinstance(value, float) else D(value)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def angle_from_state(state, seed_turns=0, seed_phase=0):
    # Use the reference's high-precision pi, not the production wrap constant.
    # Subtract integer turns first so huge inherited counters never lose a turn.
    return (decimal_input(state[0]) - decimal_input(seed_phase)
            + D(state[1] - seed_turns) * ref.TWO_PI)


def budgets(speed, angle):
    return (D("5e-12") + D("4e-14") * abs(speed),
            D("5e-12") + D("4e-15") * abs(angle))


class Measurements:
    def __init__(self):
        self.metrics = {}
        self.failures = []
        self.counts = Counter()

    def compare(self, group, name, actual, expected, bound, where):
        actual, expected, bound = map(decimal_input, (actual, expected, bound))
        error = abs(actual - expected)
        key = group + ":" + name
        metric = self.metrics.setdefault(key, {
            "count": 0, "sum_squared_error": D(0), "maximum_absolute_error": D(-1),
            "maximum_budget_fraction": D(0), "worst_case": None,
        })
        metric["count"] += 1
        metric["sum_squared_error"] += error * error
        ratio = error / bound
        metric["maximum_budget_fraction"] = max(metric["maximum_budget_fraction"], ratio)
        if error > metric["maximum_absolute_error"]:
            metric["maximum_absolute_error"] = error
            metric["worst_case"] = {
                "inputs": where, "actual": str(actual), "reference": str(expected),
                "absolute_error": str(error), "budget": str(bound),
            }
        if error > bound:
            self.failures.append({"group": group, "metric": name, **metric["worst_case"],
                                  "inputs": where, "actual": str(actual),
                                  "reference": str(expected), "absolute_error": str(error),
                                  "budget": str(bound)})

    def observable(self, group, name, actual, expected, where):
        # The absolute floor cannot conceal a zero in place of a representable
        # positive magnitude. Truly unrepresentable (< half-min-subnormal)
        # results are not asserted positive.
        if expected != 0 and float(abs(expected)) != 0.0:
            self.counts[group + ":observable_" + name] += 1
            if actual == 0.0 or (actual < 0) != (expected < 0):
                self.failures.append({"group": group, "metric": "observable_" + name,
                                      "inputs": where, "actual": repr(actual),
                                      "reference": str(expected),
                                      "reason": "representable nonzero magnitude/sign was lost"})

    def export(self):
        result = {}
        for name, original in sorted(self.metrics.items()):
            metric = dict(original)
            squared = metric.pop("sum_squared_error")
            metric["rms_error"] = str((squared / metric["count"]).sqrt())
            for key in ("maximum_absolute_error", "maximum_budget_fraction"):
                metric[key] = str(metric[key])
            result[name] = metric
        return result


def fixture_set():
    cases = []

    def add(operation, group, **values):
        cases.append({"id": len(cases), "operation": operation, "group": group, **values})

    regimes = (("rest", 0.0, 0.0), ("acceleration_from_rest", 0.0, 200.0),
               ("acceleration", 4.0, 40.0), ("equal_speed", 37.0, 37.0),
               ("decay_to_rest", 200.0, 0.0), ("decay", 200.0, 4.0))
    for sign in (-1, 1):
        for tau in TAUS:
            for ratio in RATIOS:
                for name, start, target in regimes:
                    add("segment", "frozen_grid", regime=name, phase=0.0, turns=0,
                        speed=start, target=target, tau=tau, direction=sign,
                        elapsed=tau * ratio, requested_h_over_tau=ratio,
                        relative_angle=start == 0 and target > 0 and ratio > 0,
                        relative_speed=target == 0 and start > 0 and ratio >= 10)

    for sign in (-1, 1):
        for tau in TAUS:
            for ratio in (1e-14, 1e-30, 1e-60, 1e-100, 1e-150):
                for target in (1.0, 200.0):
                    add("segment", "tiny_and_long", regime="tiny_acceleration",
                        phase=0.0, turns=0, speed=0.0, target=target, tau=tau,
                        direction=sign, elapsed=tau * ratio,
                        relative_angle=True, relative_speed=True)
            for ratio in (20, 40, 100, 300, 600, 700, 730, 740, 746, 750, 1000):
                for start in (1.0, 200.0):
                    add("segment", "tiny_and_long", regime="long_decay",
                        phase=0.0, turns=0, speed=start, target=0.0, tau=tau,
                        direction=sign, elapsed=tau * ratio, relative_speed=True)
            for elapsed in (math.ulp(0.0), 4 * math.ulp(0.0), 100 * math.ulp(0.0), 1e-310):
                for target in (1.0, 200.0):
                    add("segment", "tiny_and_long", regime="subnormal_elapsed",
                        phase=0.0, turns=0, speed=0.0, target=target, tau=tau,
                        direction=sign, elapsed=elapsed,
                        relative_angle=True, relative_speed=True)
        for tau in (0.001, 1.0, 60.0):
            for elapsed in (1e-150, 1e-155, 1e-158, 1e-160, 1e-161, 1e-162):
                add("segment", "tiny_and_long", regime="subnormal_increment",
                    phase=0.0, turns=0, speed=0.0, target=200.0, tau=tau,
                    direction=sign, elapsed=elapsed,
                    relative_angle=True, relative_speed=True)

    for sign in (-1, 1):
        for tau in TAUS:
            for name, start, target in regimes:
                for phase in (0.0, math.nextafter(math.tau, 0.0)):
                    add("segment", "day_and_wrap", regime=name, phase=phase,
                        turns=19 * sign, speed=start, target=target, tau=tau,
                        direction=sign, elapsed=86400.0)
            for ratio in (math.nextafter(0.125, 0.0), 0.125,
                          math.nextafter(0.125, math.inf), 0.5):
                add("segment", "day_and_wrap", regime="kernel_boundary",
                    phase=0.7, turns=-11, speed=0.0, target=200.0, tau=tau,
                    direction=sign, elapsed=tau * ratio, relative_angle=True)
        for phase in (0.0, math.nextafter(math.tau, 0.0), math.pi):
            for elapsed in (math.nextafter(math.tau / 200.0, 0.0),
                            math.tau / 200.0, math.nextafter(math.tau / 200.0, math.inf)):
                add("segment", "day_and_wrap", regime="wrap_boundary", phase=phase,
                    turns=17, speed=200.0, target=200.0, tau=1.0,
                    direction=sign, elapsed=elapsed)
        for elapsed in (0.0, -1e-12, -0.25, -60.0, -86400.0):
            for speed in (0.0, 4.0, 200.0):
                add("prehistory", "prehistory", phase=0.7, turns=-17, speed=speed,
                    direction=sign, elapsed=elapsed)

    rng = random.Random(SEED)
    for index in range(SEMIGROUP_CASES):
        duration = 10.0 ** rng.uniform(-12, math.log10(60.0))
        fraction = rng.random()
        first = duration * fraction
        speed, target = rng.uniform(0, 200), rng.uniform(0, 200)
        if index % 5 == 0:
            speed = 0.0
        elif index % 5 == 1:
            target = 0.0
        elif index % 5 == 2:
            target = speed
        add("split", "semigroup", phase=rng.uniform(0, math.tau),
            turns=rng.randrange(-500, 501), speed=speed, target=target,
            tau=10.0 ** rng.uniform(-3, math.log10(60.0)),
            direction=rng.choice((-1, 1)), first=first, second=duration - first,
            elapsed=first + (duration - first))

    for rate in RATES:
        maximum = 86400 * rate
        for sign in (-1, 1):
            for tau in (0.001, 1.0, 60.0):
                for fraction in (math.ulp(0.0), 4 * math.ulp(0.0), 100 * math.ulp(0.0), 1e-310):
                    add("sample", "sample_positions", regime="subnormal_fraction",
                        phase=0.0, turns=0, speed=0.0, target=200.0, tau=tau,
                        direction=sign, rate=rate, anchor=0, frame=0, fraction=fraction,
                        relative_speed=True)
            add("sample", "sample_positions", regime="subnormal_constant_fraction",
                phase=0.0, turns=0, speed=200.0, target=200.0, tau=1.0,
                direction=sign, rate=rate, anchor=0, frame=0, fraction=1e-319)
            for tau in (0.001, 60.0):
                for anchor in (0, maximum - rate - 1, maximum - 17):
                    for frame, fraction in ((maximum - 1, 0.0), (maximum - 1, 1e-8),
                                            (maximum - 1, 0.12345678901234566), (maximum - 1, 0.25),
                                            (maximum - 1, 0.5),
                                            (maximum - 1, math.nextafter(1.0, 0.0)),
                                            (maximum, 0.0)):
                        for start, target in ((0.0, 200.0), (200.0, 0.0)):
                            add("sample", "sample_positions", phase=0.7, turns=13,
                                speed=start, target=target, tau=tau, direction=sign,
                                rate=rate, anchor=anchor, frame=frame, fraction=fraction)
            for frame, fraction in ((-maximum, 0.0), (-maximum, 0.5),
                                    (-maximum + 1, 0.25), (-rate - 1, 0.75),
                                    (-1, 0.75), (0, 0.0)):
                add("presample", "sample_positions", phase=0.7, turns=-23,
                    speed=200.0, direction=sign, rate=rate, frame=frame, fraction=fraction)

            for start, up, down in ((0.0, 0.001, 60.0), (200.0, 60.0, 0.001),
                                    (20.0, 0.7, 1.1)):
                events = [(0, 1), (0, 0), (0, 1), (1, 0), (1, 0), (2, 1),
                          (17, 0), (128, 1), (129, 0), (rate // 10, 1),
                          (rate // 5, 0), (rate, 1), (rate + 1, 0),
                          (3 * rate, 1), (5 * rate, 0), (maximum - rate, 1),
                          (maximum - 17, 0), (maximum, 1)]
                queries = {(-maximum, 0.0), (-1, 0.75), (maximum - 1, 0.25),
                           (maximum - 1, 0.75), (maximum, 0.0)}
                for frame, _ in events:
                    queries.update((frame + offset, fraction)
                                   for offset, fraction in ((-1, 0.5), (0, 0.0), (0, 0.5), (1, 0.0))
                                   if 0 <= frame + offset < maximum)
                add("timeline", "command_reversals", rate=rate, slow=4.0, fast=40.0,
                    up=up, down=down, direction=sign, phase=0.3, speed=start,
                    command=0, events=events, queries=sorted(queries))
    return cases


def request_text(case):
    operation = case["operation"]
    prefix = [operation, case["id"]]
    if operation in ("segment", "sample", "split"):
        prefix += [case[key] for key in ("phase", "turns", "speed", "target", "tau", "direction")]
        if operation == "segment":
            prefix += [case["elapsed"]]
        elif operation == "sample":
            prefix += [case[key] for key in ("anchor", "frame", "fraction", "rate")]
        else:
            prefix += [case["first"], case["second"]]
    elif operation in ("prehistory", "presample"):
        prefix += [case[key] for key in ("phase", "turns", "speed", "direction")]
        prefix += ([case["elapsed"]] if operation == "prehistory"
                   else [case[key] for key in ("frame", "fraction", "rate")])
    elif operation == "timeline":
        prefix += [case[key] for key in ("rate", "slow", "fast", "up", "down",
                                        "direction", "phase", "speed", "command")]
        prefix += [len(case["events"]), len(case["queries"])]
        prefix += [value for pair in case["events"] for value in pair]
        prefix += [value for pair in case["queries"] for value in pair]
    return " ".join(repr(value) if isinstance(value, float) else str(value) for value in prefix)


def grade_state(measured, case, actual, expected_speed, expected_increment, *, relative=False):
    group = case["group"]
    speed_budget, angle_budget = budgets(expected_speed, expected_increment)
    measured.compare(group, "speed_rad_s", actual[2], expected_speed, speed_budget, case)
    angle = angle_from_state(actual, case.get("turns", 0), case["phase"])
    measured.compare(group, "reconstructed_increment_rad", angle, expected_increment, angle_budget, case)
    if case.get("regime") == "subnormal_constant_fraction" and case["direction"] == 1:
        measured.observable(group, "phase", actual[0], expected_increment, case)
    if relative or case.get("relative_speed"):
        measured.compare(group, "relative_speed", actual[2], expected_speed,
                         D("1e-300") + D("2e-12") * abs(expected_speed), case)
        measured.observable(group, "speed", actual[2], expected_speed, case)


def qualify(executable):
    if ref.PRECISION < 80:
        raise RuntimeError("R2 requires at least 80 decimal digits in the independent reference")
    cases = fixture_set()
    requests = "\n".join(map(request_text, cases)) + "\n"
    completed = subprocess.run([str(executable)], input=requests, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               timeout=90, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"native batch probe failed ({completed.returncode}): {completed.stderr}")
    if completed.stderr:
        raise RuntimeError(f"native batch probe emitted unexpected stderr: {completed.stderr}")
    rows = [json.loads(line, parse_constant=lambda value: (_ for _ in ()).throw(
        ValueError(f"nonfinite probe JSON {value}"))) for line in completed.stdout.splitlines()]
    if len(rows) != len(cases) or [row.get("id") for row in rows] != list(range(len(cases))):
        raise RuntimeError("native batch probe returned missing, repeated or reordered records")

    measured = Measurements()
    with localcontext(MEASUREMENT_CONTEXT):
        for case, row in zip(cases, rows):
            measured.counts[case["group"] + ":fixtures"] += 1
            if row["status"] != "ok":
                measured.failures.append({"group": case["group"], "metric": "native_status",
                                          "inputs": case, "actual": row["status"]})
                continue
            operation = case["operation"]
            if operation == "timeline":
                profile = ref.MotionProfile(*(decimal_input(case[key]) for key in
                    ("slow", "fast", "up", "down")), case["direction"])
                events = [ref.CommandEvent(ref.frame_time(frame, case["rate"]),
                                          "tremolo" if command else "chorale")
                          for frame, command in case["events"]]
                timeline = ref.RotorTimeline(profile, decimal_input(case["phase"]),
                                             decimal_input(case["speed"]),
                                             "tremolo" if case["command"] else "chorale", events)
                if len(row["states"]) != len(case["queries"]):
                    raise RuntimeError("native timeline returned incomplete query data")
                for (frame, fraction), actual in zip(case["queries"], row["states"]):
                    time = (D(frame) + decimal_input(fraction)) / case["rate"]
                    expected = timeline.state_at(time)
                    query = {key: value for key, value in case.items() if key != "queries"}
                    query.update(frame=frame, fraction=fraction)
                    grade_state(measured, query, actual, expected.speed_rad_s,
                                expected.angle_rad - decimal_input(case["phase"]))
                    measured.counts[case["group"] + ":queries"] += 1
                continue

            if operation in ("sample", "presample"):
                elapsed = (D(case["frame"] - case.get("anchor", 0))
                           + decimal_input(case["fraction"])) / case["rate"]
            else:
                elapsed = decimal_input(case["elapsed"])
            if operation in ("prehistory", "presample"):
                expected_speed = decimal_input(case["speed"])
                expected_increment = case["direction"] * expected_speed * elapsed
            else:
                expected = ref.evaluate_segment(ref.MotionState(0, decimal_input(case["speed"])),
                                                decimal_input(case["target"]),
                                                decimal_input(case["tau"]), case["direction"], elapsed)
                expected_speed, expected_increment = expected.speed_rad_s, expected.angle_rad
            grade_state(measured, case, row["state"], expected_speed, expected_increment)
            if "increment" in row:
                measured.compare(case["group"], "angle_increment_rad", row["increment"],
                                 expected_increment, budgets(expected_speed, expected_increment)[1], case)
                if case.get("relative_angle"):
                    measured.compare(case["group"], "relative_increment", row["increment"],
                                     expected_increment,
                                     D("1e-300") + D("2e-12") * abs(expected_increment), case)
                    measured.observable(case["group"], "increment", row["increment"], expected_increment, case)
            if operation == "split":
                measured.compare("semigroup", "split_angle_rad",
                                 angle_from_state(row["split_state"], row["state"][1], row["state"][0]),
                                 D(0), D("2e-10"), case)
                measured.compare("semigroup", "split_speed_rad_s", row["split_state"][2],
                                 row["state"][2], D("2e-11"), case)

        metrics = measured.export()

    identities = {path: digest(ROOT / path) for path in (
        "include/hammond/RotaryTypes.h", "include/hammond/RotaryMotion.h",
        "src/RotaryMotion.cpp", "tools/rotary_reference.py",
        "tests/probes/rotary_motion_probe.cpp", "tests/test_rotary_motion_acceptance.py",
        "docs/ROTARY_NUMERICAL_CONTRACT.md", "docs/ROTARY_PROPAGATION_CONTRACT.md")}
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    return {
        "schema_version": 1, "gate": "R2 native numerical qualification",
        "fixture_profile_id": "native-r2-synthetic-grid-v1",
        "status": "pass" if not measured.failures else "fail",
        "contract_id": ref.CONTRACT_ID, "model_id": ref.MODEL_ID,
        "reference_id": ref.REFERENCE_ID, "motion_precision_digits": ref.PRECISION,
        "source_head_observed": revision.stdout.strip(), "source_sha256": identities,
        "probe": {"path": str(executable), "sha256": digest(executable),
                  "native_processes": 1, "requests": len(cases),
                  "stdin_sha256": hashlib.sha256(requests.encode()).hexdigest(),
                  "stdout_sha256": hashlib.sha256(completed.stdout.encode()).hexdigest()},
        "runtime": {"python": sys.version, "platform": platform.platform()},
        "fixtures": {"taus_s": TAUS, "requested_h_over_tau": RATIOS,
                     "directions": [-1, 1], "rates_hz": RATES,
                     "semigroup_seed": SEED, "semigroup_cases": SEMIGROUP_CASES,
                     "semigroup_maximum_total_s": 60,
                     "counts": dict(sorted(measured.counts.items()))},
        "budgets": {"speed_rad_s": "5e-12 + 4e-14*abs(reference)",
                    "angle_increment_rad": "5e-12 + 4e-15*abs(reference)",
                    "near_zero_relative": "2e-12*abs(reference) + 1e-300",
                    "semigroup_angle_rad": "2e-10", "semigroup_speed_rad_s": "2e-11",
                    "observable_nonzero": "require sign/nonzero when the reference rounds to nonzero binary64"},
        "metrics": metrics, "failure_count": len(measured.failures),
        "failures": measured.failures,
        "independence": "80-digit Decimal reference uses its converged series/exponential; no production polynomial is copied",
        "input_policy": "binary64 inputs converted to Decimal with 120 digits; frame fractions divided at 120 digits",
        "scope": "native motion only; lifecycle and exact partition checks are the separate test_rotary_motion target",
        "exclusions": ["R3 propagation", "R4 waveform rendering", "R5 audible policy", "R6 integration",
                       "physical calibration", "hardware or real-time deadline qualification"],
    }


class NativeMotionAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = PROBE_PATH or os.environ.get("HAMMOND_ROTARY_MOTION_PROBE_EXECUTABLE")
        if not value or not Path(value).is_file():
            raise RuntimeError("R2 requires HAMMOND_ROTARY_MOTION_PROBE_EXECUTABLE to name an existing native probe")
        cls.report = qualify(Path(value).resolve())
        if REPORT_PATH:
            Path(REPORT_PATH).parent.mkdir(parents=True, exist_ok=True)
            Path(REPORT_PATH).write_text(json.dumps(cls.report, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    def assert_group(self, group):
        failures = [item for item in self.report["failures"] if item["group"] == group]
        self.assertFalse(failures, json.dumps(failures[:5], indent=2))

    def test_complete_frozen_tau_sign_time_grid(self):
        self.assertEqual(self.report["fixtures"]["counts"]["frozen_grid:fixtures"], 2 * 6 * 16 * 6)
        self.assert_group("frozen_grid")

    def test_tiny_acceleration_and_long_decay_relative_budgets(self):
        self.assert_group("tiny_and_long")

    def test_full_day_wraps_and_kernel_boundaries(self):
        self.assert_group("day_and_wrap")

    def test_seeded_semigroup(self):
        self.assertGreaterEqual(self.report["fixtures"]["counts"]["semigroup:fixtures"], 1000)
        self.assert_group("semigroup")

    def test_all_rates_and_late_epoch_split_fractions(self):
        self.assert_group("sample_positions")

    def test_constant_negative_time_prehistory(self):
        self.assert_group("prehistory")

    def test_rapid_command_reversals_and_ties_against_oracle(self):
        self.assert_group("command_reversals")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--probe", type=Path)
    arguments, remaining = parser.parse_known_args()
    REPORT_PATH, PROBE_PATH = arguments.report, arguments.probe
    result = unittest.main(argv=[sys.argv[0], *remaining], exit=False, verbosity=2)
    sys.exit(not result.result.wasSuccessful())
