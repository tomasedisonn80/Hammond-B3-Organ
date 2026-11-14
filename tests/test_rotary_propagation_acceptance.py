#!/usr/bin/env python3
"""Independent native R3 numerical acceptance, using one persistent batch probe.

The geometry oracle is a 100-digit Cartesian Taylor/square-root calculation.
The independent root oracle bisects for at most 96 steps, querying native motion
in batches to isolate propagation error. The separately authored 80-digit motion
reference then quantifies motion's additional phase and root contributions.
Missing HAMMOND_ROTARY_PROPAGATION_PROBE_EXECUTABLE is an error, never a skip.
"""

from __future__ import annotations

import argparse
from collections import Counter
from decimal import Context, Decimal, ROUND_FLOOR, localcontext
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import queue
import subprocess
import sys
import tempfile
import threading
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import rotary_reference as ref

D = Decimal
CONTEXT = Context(prec=100, Emin=-999999999, Emax=999999999)
RADII = (0.0, 0.02, 0.18, 1.0)
RATES = (44100, 48000, 96000, 192000)
SOUND_SPEEDS = (300.0, 343.0, 380.0)
PHASES = (0.0, math.pi / 2, math.pi, 3 * math.pi / 2, math.nextafter(math.tau, 0.0))
ORACLE_BISECTIONS = 96
ORACLE_TARGET = 5e-15  # Margin below the frozen independent 1e-14 s gate.
REPORT_PATH = None
PROBE_PATH = None


def dec(value):
    return D.from_float(value) if isinstance(value, float) else D(value)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe(value):
    if isinstance(value, D):
        return str(value)
    if isinstance(value, dict):
        return {key: safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [safe(item) for item in value]
    return value


def sincos(angle):
    """Converged Decimal series, independent of native libm trigonometry."""
    angle %= ref.TWO_PI
    if angle > ref.TWO_PI / 2:
        angle -= ref.TWO_PI
    if angle < -ref.TWO_PI / 2:
        angle += ref.TWO_PI
    square = -angle * angle
    sine = sine_term = angle
    cosine = cosine_term = D(1)
    for order in range(1, 200):
        sine_term *= square / D((2 * order) * (2 * order + 1))
        cosine_term *= square / D((2 * order - 1) * (2 * order))
        next_sine, next_cosine = sine + sine_term, cosine + cosine_term
        if next_sine == sine and next_cosine == cosine:
            return sine, cosine
        sine, cosine = next_sine, next_cosine
    raise RuntimeError("independent trigonometric series did not converge")


def geometry(scene, phase, speed):
    """100-digit Cartesian norm and signed radial velocity, with no hypot."""
    sine, cosine = sincos(dec(phase))
    radius, signed_speed = dec(scene["radius"]), scene["direction"] * dec(speed)
    origin, microphone = [tuple(map(dec, scene[key])) for key in ("origin", "mic")]
    source = (origin[0] + radius * cosine, origin[1] + radius * sine, origin[2])
    velocity = (-radius * signed_speed * sine, radius * signed_speed * cosine, D(0))
    displacement = tuple(microphone[i] - source[i] for i in range(3))
    distance = sum(value * value for value in displacement).sqrt()
    radial = sum(displacement[i] * velocity[i] for i in range(3)) / distance
    ratio = 1 / (1 - radial / dec(scene["c"]))
    return {"distance": distance, "radial": radial, "ratio": ratio,
            "position": source, "velocity": velocity}


def cartesian_float(scene, state):
    """Independent binary64 Cartesian norm for inexpensive bisection steps."""
    phase, _, speed = state
    sine, cosine = math.sin(phase), math.cos(phase)
    radius = scene["radius"]
    position = (scene["origin"][0] + radius * cosine,
                scene["origin"][1] + radius * sine, scene["origin"][2])
    displacement = tuple(scene["mic"][i] - position[i] for i in range(3))
    distance = math.sqrt(math.fsum(value * value for value in displacement))
    velocity = (-radius * scene["direction"] * speed * sine,
                radius * scene["direction"] * speed * cosine, 0.0)
    radial = math.fsum(displacement[i] * velocity[i] for i in range(3)) / distance
    return distance, 1.0 / (1.0 - radial / scene["c"])


def distance_bounds(scene):
    difference = [dec(scene["mic"][i]) - dec(scene["origin"][i]) for i in range(3)]
    horizontal = (difference[0] ** 2 + difference[1] ** 2).sqrt()
    radius = dec(scene["radius"])
    lower = ((horizontal - radius) ** 2 + difference[2] ** 2).sqrt()
    upper = ((horizontal + radius) ** 2 + difference[2] ** 2).sqrt()
    beta = radius * max(map(dec, (scene["speed"], scene["slow"], scene["fast"]))) / dec(scene["c"])
    return lower, upper, beta


def split_samples(samples):
    frame = int(samples.to_integral_value(rounding=ROUND_FLOOR))
    fraction = float(samples - frame)
    if fraction == 1.0:
        frame, fraction = frame + 1, 0.0
    return frame, fraction


def seconds(position, rate):
    return (D(position[0]) + dec(position[1])) / rate


def subtract_delay(position, delay, rate):
    # Exact Decimal arithmetic on a bounded local duration; no native split-
    # subtraction implementation is copied and no absolute float time is formed.
    return split_samples(D(position[0]) + dec(position[1]) - dec(delay) * rate)


def timeline_for(scene):
    profile = ref.MotionProfile(*(dec(scene[key]) for key in ("slow", "fast", "up", "down")),
                                scene["direction"])
    events = [ref.CommandEvent(ref.frame_time(frame, scene["rate"]),
                              "tremolo" if command else "chorale")
              for frame, command in scene["events"]]
    return ref.RotorTimeline(profile, dec(scene["phase"]), dec(scene["speed"]),
                             "tremolo" if scene["command"] else "chorale", events)


class Measurements:
    def __init__(self):
        self.metrics = {}
        self.failures = []
        self.counts = Counter()

    def check(self, condition, group, metric, where, **details):
        if not condition:
            self.failures.append(safe({"group": group, "metric": metric, "inputs": where, **details}))

    def measure(self, group, name, error, where, bound=None, **details):
        error = abs(dec(error))
        key = group + ":" + name
        metric = self.metrics.setdefault(key, {"count": 0, "sum_squared": D(0),
            "maximum_absolute_error": D(-1), "maximum_budget_fraction": D(0), "worst_case": None})
        metric["count"] += 1
        metric["sum_squared"] += error * error
        if error > metric["maximum_absolute_error"]:
            metric["maximum_absolute_error"] = error
            metric["worst_case"] = safe({"inputs": where, "absolute_error": error,
                                          "budget": bound, **details})
        if bound is not None:
            bound = dec(bound)
            metric["maximum_budget_fraction"] = max(metric["maximum_budget_fraction"], error / bound)
            self.check(error <= bound, group, name, where, absolute_error=error, budget=bound, **details)

    def export(self):
        result = {}
        for name, original in sorted(self.metrics.items()):
            metric = dict(original)
            metric["rms_error"] = (metric.pop("sum_squared") / metric["count"]).sqrt()
            result[name] = safe(metric)
        return result


class BatchProbe:
    """One process for all scenes/roots and all adaptive bisection rounds."""
    def __init__(self, executable):
        self.executable = executable
        self.stderr = tempfile.TemporaryFile(mode="w+")
        self.process = subprocess.Popen([str(executable)], text=True, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=self.stderr, bufsize=1)
        self.queue = queue.Queue()
        self.requests = 0
        self.batches = 0
        self.input_hash, self.output_hash = hashlib.sha256(), hashlib.sha256()

        def read():
            for line in self.process.stdout:
                self.queue.put(line)
            self.queue.put(None)

        self.reader = threading.Thread(target=read, daemon=True)
        self.reader.start()

    def batch(self, requests):
        if not requests:
            return []
        first = self.requests
        self.batches += 1
        lines = []
        for operation, fields in requests:
            fields = [operation, self.requests, *fields]
            lines.append(" ".join(repr(value) if isinstance(value, float) else str(value)
                                  for value in fields) + "\n")
            self.requests += 1
        text = "".join(lines)
        self.input_hash.update(text.encode())
        self.process.stdin.write(text)
        self.process.stdin.flush()
        rows = []
        for identifier in range(first, self.requests):
            line = self.queue.get(timeout=90)
            if line is None:
                self.stderr.seek(0)
                raise RuntimeError("native probe ended before its response: " + self.stderr.read())
            self.output_hash.update(line.encode())
            row = json.loads(line, parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError("nonfinite native result " + value)))
            if row.get("id") != identifier:
                raise RuntimeError("native probe omitted, repeated or reordered a record")
            rows.append(row)
        return rows

    def finish(self):
        self.process.stdin.close()
        code = self.process.wait(timeout=30)
        self.reader.join(timeout=30)
        self.process.stdout.close()
        self.stderr.seek(0)
        errors = self.stderr.read()
        self.stderr.close()
        if code or errors:
            raise RuntimeError(f"native probe failed ({code}): {errors}")
        return {"path": str(self.executable), "sha256": digest(self.executable),
                "native_processes": 1, "requests": self.requests, "batches": self.batches,
                "stdin_sha256": self.input_hash.hexdigest(), "stdout_sha256": self.output_hash.hexdigest()}

    def abort(self):
        if self.process.poll() is None:
            self.process.kill()
            self.process.wait(timeout=30)
        if not self.process.stdin.closed:
            self.process.stdin.close()
        self.reader.join(timeout=30)
        self.process.stdout.close()
        self.stderr.close()


def fixture_set():
    scenes, jobs, history_queries, geometry_cases = [], [], [], []

    def add_scene(group, **values):
        scene = {"id": len(scenes), "group": group, "rate": 48000, "slow": 0.0,
                 "fast": 0.0, "up": 0.001, "down": 60.0, "direction": 1,
                 "phase": 0.0, "speed": 0.0, "command": 0, "events": [],
                 "origin": (0.0, 0.0, 0.0), "radius": 1.0,
                 "mic": (2.0, 0.0, 0.0), "c": 343.0, "reference_distance": 1.0, **values}
        scene.setdefault("through", 86400 * scene["rate"])
        scenes.append(scene)
        return scene

    def add_job(scene, position, label, **values):
        job = {"id": len(jobs), "scene": scene["id"], "group": scene["group"],
               "position": position, "label": label, **values}
        jobs.append(job)
        return job

    for radius in RADII:
        clearance = math.nextafter(radius + 0.02, math.inf)
        tangent_y = math.sqrt((radius + 0.021) ** 2 - radius ** 2)
        poses = (("right", (0., 0., 0.), (clearance, 0., 0.)),
                 ("left", (0., 0., 0.), (-clearance, 0., 0.)),
                 ("above_minimum", (0., 0., 0.), (radius, 0., 0.02)),
                 ("below_minimum", (0., 0., 0.), (radius, 0., -0.02)),
                 ("tangent", (0., 0., 0.), (radius, tangent_y, 0.)),
                 ("maximum_distance", (-10., 0., 0.), (10. - radius, 0., 0.)))
        for direction in (-1, 1):
            for phase in PHASES:
                for c in SOUND_SPEEDS:
                    maximum_speed = min(200., 0.25 * c / radius) if radius else 200.
                    for speed in (0., maximum_speed):
                        for pose, origin, microphone in poses:
                            scene = add_scene("frozen_grid", radius=radius, direction=direction,
                                phase=phase, c=c, speed=speed, slow=speed, fast=speed,
                                pose=pose, origin=origin, mic=microphone,
                                speed_regime="zero" if speed == 0 else "admitted_maximum")
                            geometry_cases.append(scene)
                            crossing = geometry(scene, phase, speed)["distance"] / dec(c)
                            add_job(scene, split_samples(crossing * scene["rate"]), "emission_at_zero")
                            add_job(scene, (5925, 0.73125), "running")

    for rate in RATES:
        maximum = 86400 * rate
        for direction in (-1, 1):
            for radius in (0.18, 1.0):
                for c in SOUND_SPEEDS:
                    maximum_speed = min(200., 0.25 * c / radius)
                    for regime, start, up, down in (("fast_ramps", 0., 0.001, 0.01),
                        ("fast_decay", maximum_speed, 60., 0.001)):
                        anchors = [rate // 10, rate // 5, rate, maximum - rate // 10]
                        events = [(0, 1), (0, 0), (0, 1), (1, 1), (17, 0),
                                  (anchors[0], 1), (anchors[0], 1), (anchors[1], 0),
                                  (anchors[2], 1), (anchors[3], 0)]
                        scene = add_scene("historical", rate=rate, direction=direction,
                            radius=radius, c=c, speed=start, slow=0., fast=maximum_speed,
                            up=up, down=down, phase=0.7, events=events,
                            mic=(radius + 0.37, -0.63, 0.2), regime=regime)
                        timeline = timeline_for(scene)
                        for position in ((-1, 0.25), (0, 0.), (1, 0.75)):
                            add_job(scene, position, "startup", startup=True)
                        for anchor in (anchors[0], anchors[1], anchors[3]):
                            time = D(anchor) / rate
                            state = timeline.state_at(time)
                            delay = geometry(scene, state.wrapped()[0], state.speed_rad_s)["distance"] / dec(c)
                            for side in (-1, 1):
                                observation = time + delay + D(side) * D("1e-8")
                                add_job(scene, split_samples(observation * rate), "command_crossing",
                                        crossing_anchor=anchor, side=side)
                        for fraction in (0., 0.25, 0.5, math.nextafter(1., 0.)):
                            add_job(scene, (maximum - 1, fraction), "late_split_fraction")
                        add_job(scene, (maximum, 0.), "epoch_endpoint")
                        for anchor in (0, 17, *anchors):
                            for offset, fraction in ((-1, 0.5), (0, 0.), (0, 0.5)):
                                history_queries.append({"scene": scene["id"],
                                    "position": (anchor + offset, fraction), "anchor": anchor})
                        other = add_scene("historical", **{key: value for key, value in scene.items()
                            if key not in ("id", "group", "mic")},
                            mic=(-radius - 1.3, 0.2, -0.17), borrowed_from=scene["id"])
                        pair_position = (rate // 3, 0.625)
                        left = add_job(scene, pair_position, "distinct_receiver", receiver_pair=other["id"])
                        add_job(other, pair_position, "distinct_receiver", paired_job=left["id"])

    for direction in (-1, 1):
        scene = add_scene("derivative", direction=direction, phase=0.73, radius=1.,
                          slow=75., fast=75., speed=75., c=300., mic=(1.41, 0.83, 0.27))
        base = D("0.231")
        add_job(scene, split_samples(base * scene["rate"]), "derivative_center")
        for h in (0.002, 0.001, 0.0005, 0.00025, 0.000125, 0.0000625):
            for multiplier in (-2, -1, 1, 2):
                add_job(scene, split_samples((base + D(str(h)) * multiplier) * scene["rate"]),
                        "derivative_stencil", h=h, multiplier=multiplier)

    rejection = []
    for label, changes in (
        ("orbit_collision", {"mic": (1., 0., 0.)}),
        ("clearance_below_minimum", {"mic": (1., 0., math.nextafter(0.02, 0.))}),
        ("path_above_maximum", {"origin": (-10., 0., 0.), "mic": (10., 0., 0.)}),
        ("cross_field_mach", {"speed": 200., "fast": 200., "c": 300.}),
        ("coordinate_above_maximum", {"mic": (math.nextafter(10., math.inf), 0., 0.)}),
        ("sound_speed_below_minimum", {"c": math.nextafter(300., 0.)}),
        ("radius_above_maximum", {"radius": math.nextafter(1., math.inf)}),
    ):
        scene = add_scene("rejection", rejection=label, expected_status="invalid_profile", **changes)
        rejection.append(scene)
    return scenes, jobs, history_queries, geometry_cases, rejection


def scene_request(scene):
    if "borrowed_from" in scene:
        return "receiver", [scene["id"], scene["borrowed_from"], *scene["mic"], scene["c"],
                            scene["reference_distance"]]
    return "scene", [scene["id"], *(scene[key] for key in ("rate", "slow", "fast", "up", "down",
                    "direction", "phase", "speed", "command", "through")), len(scene["events"]),
                    *(value for event in scene["events"] for value in event),
                    *scene["origin"], scene["radius"], *scene["mic"], scene["c"], scene["reference_distance"]]


def where_job(scene, job):
    return {"scene": scene, "query": job}


def circular_error(native_phase, reference_phase):
    difference = dec(native_phase) - reference_phase
    while difference > ref.TWO_PI / 2:
        difference -= ref.TWO_PI
    while difference < -ref.TWO_PI / 2:
        difference += ref.TWO_PI
    return difference


def grade_motion(measured, scene, actual, expected, where, group="motion_contribution"):
    phase_error = circular_error(actual[0], expected.wrapped()[0])
    increment = expected.angle_rad - dec(scene["phase"])
    measured.measure(group, "phase_rad", phase_error, where, D("5e-12") + D("4e-15") * abs(increment))
    measured.measure(group, "speed_rad_s", dec(actual[2]) - expected.speed_rad_s, where,
                     D("5e-12") + D("4e-14") * abs(expected.speed_rad_s))
    beta = distance_bounds(scene)[2]
    contribution = dec(scene["radius"]) * abs(phase_error) / (dec(scene["c"]) * (1 - beta))
    measured.measure(group, "root_contribution_bound_s", contribution, where)
    return contribution


def native_trajectory_bisection(probe, scenes, jobs, measured):
    """Independent pure bisection with exact split queries and Cartesian norm.

    Native history evaluation supplies identical motion to both solvers. It
    supplies neither geometry nor a root update to this reference algorithm.
    The midpoint count excludes its two endpoints, unlike the native total.
    """
    roots = []
    for job in jobs:
        scene = scenes[job["scene"]]
        minimum, maximum, _ = distance_bounds(scene)
        margin = 32 * math.ulp(max(1., float(maximum)))
        roots.append({"job": job, "lo": max(0., float(minimum) - margin) / scene["c"],
                      "hi": (float(maximum) + margin) / scene["c"], "bisections": 0, "best": None})

    def evaluate(candidates):
        requests = []
        for root, delay in candidates:
            job, scene = root["job"], scenes[root["job"]["scene"]]
            emission = subtract_delay(job["position"], delay, scene["rate"])
            requests.append(("state", [scene["id"], *emission]))
        rows = probe.batch(requests)
        for (root, delay), row in zip(candidates, rows):
            scene = scenes[root["job"]["scene"]]
            if row["status"] != "ok":
                raise RuntimeError("native trajectory oracle query failed: " + json.dumps(row))
            distance, ratio = cartesian_float(scene, row["state"])
            result = {"delay": delay, "residual": delay - distance / scene["c"],
                      "state": row["state"], "distance": distance, "ratio": ratio}
            if root["best"] is None or abs(result["residual"]) < abs(root["best"]["residual"]):
                root["best"] = result
            yield root, result

    for endpoint in ("lo", "hi"):
        for root, result in evaluate([(root, root[endpoint]) for root in roots]):
            measured.check(result["residual"] <= 0 if endpoint == "lo" else result["residual"] >= 0,
                "oracle", "independent_bracket", root["job"], endpoint=endpoint, residual=result["residual"])
    for iteration in range(ORACLE_BISECTIONS):
        active = [root for root in roots if abs(root["best"]["residual"]) > ORACLE_TARGET]
        if not active:
            break
        for root, result in evaluate([(root, (root["lo"] + root["hi"]) / 2) for root in active]):
            root["bisections"] = iteration + 1
            if result["residual"] < 0:
                root["lo"] = result["delay"]
            else:
                root["hi"] = result["delay"]
    return {root["job"]["id"]: root for root in roots}


def derivative_convergence(scenes, jobs, native_rows, measured):
    tables = []
    for scene in scenes:
        if scene["group"] != "derivative":
            continue
        timeline = timeline_for(scene)
        shape = ref.CircularGeometry(scene["origin"], scene["radius"])
        center = D("0.231")
        exact = ref.solve_retarded_path(timeline, shape, scene["mic"], center, scene["c"],
                                        residual_tolerance_s=1e-16, max_iterations=96)
        selected = [job for job in jobs if job["scene"] == scene["id"]]
        native_center = native_rows[next(job["id"] for job in selected if job["label"] == "derivative_center")]
        table = {"scene": scene["id"], "direction": scene["direction"], "steps": []}
        for h in (0.002, 0.001, 0.0005, 0.00025, 0.000125, 0.0000625):
            samples = {job["multiplier"]: native_rows[job["id"]] for job in selected
                       if job.get("h") == h}
            emitted = {key: seconds(row["emission"], scene["rate"]) for key, row in samples.items()}
            native_derivative = (emitted[-2] - 8 * emitted[-1] + 8 * emitted[1] - emitted[2]) / (12 * D(str(h)))
            entry = {"h_s": h, "native_four_point_error": str(abs(native_derivative - dec(native_center["ratio"]))),
                     "independent_error_by_residual_target": {}}
            for target in (1e-10, 1e-12, 1e-14, 1e-16):
                points = {key: ref.solve_retarded_path(timeline, shape, scene["mic"],
                    center + key * D(str(h)), scene["c"], residual_tolerance_s=target,
                    max_iterations=96).emission_time_s for key in (-2, -1, 1, 2)}
                derivative = (points[-2] - 8 * points[-1] + 8 * points[1] - points[2]) / (12 * D(str(h)))
                entry["independent_error_by_residual_target"][str(target)] = str(abs(derivative - dec(exact.doppler_ratio)))
            table["steps"].append(entry)
        coarse, fine = table["steps"][0], table["steps"][-1]
        measured.check(dec(fine["native_four_point_error"]) < dec(coarse["native_four_point_error"]) / 100,
                       "derivative", "native_stencil_convergence", table)
        measured.check(dec(fine["independent_error_by_residual_target"]["1e-16"]) <
                       dec(fine["independent_error_by_residual_target"]["1e-10"]) / 100,
                       "derivative", "root_precision_convergence", table)
        tables.append(table)
    return tables


def qualify(executable):
    started = time.monotonic()
    identities = {path: digest(ROOT / path) for path in (
        "include/hammond/RotaryTypes.h", "include/hammond/RotaryMotion.h", "include/hammond/RotaryPropagation.h",
        "src/RotaryMotion.cpp", "src/RotaryPropagation.cpp", "tools/rotary_reference.py",
        "tests/probes/rotary_propagation_probe.cpp", "tests/test_rotary_propagation_acceptance.py",
        "docs/ROTARY_NUMERICAL_CONTRACT.md", "docs/ROTARY_PROPAGATION_CONTRACT.md")}
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL, check=False).stdout.strip()
    measured = Measurements()
    probe = BatchProbe(executable)
    try:
        with localcontext(CONTEXT):
            scenes, jobs, history_queries, geometry_cases, rejection = fixture_set()
            admitted = {}
            for scene, row in zip(scenes, probe.batch([scene_request(scene) for scene in scenes])):
                expected = scene.get("expected_status", "ok")
                measured.check(row["status"] == expected, scene["group"], "prepare_status", scene,
                               actual=row["status"], expected=expected)
                admitted[scene["id"]] = row["status"] == "ok"
                measured.counts[scene["group"] + ":scenes"] += 1
                if row["status"] == "ok":
                    for name, actual, reference in zip(("minimum_distance_m", "maximum_distance_m", "maximum_mach"),
                                                       row["bounds"], distance_bounds(scene)):
                        measured.measure("admission", name, dec(actual) - reference, scene, D("2e-12"))

            geometry_requests = [("geometry", [*scene["origin"], scene["radius"], scene["phase"],
                scene["speed"], scene["direction"], *scene["mic"]]) for scene in geometry_cases]
            for scene, row in zip(geometry_cases, probe.batch(geometry_requests)):
                measured.check(row["status"] == "ok", "geometry", "native_status", scene, actual=row["status"])
                if row["status"] != "ok":
                    continue
                expected = geometry(scene, scene["phase"], scene["speed"])
                measured.measure("geometry", "distance_m", dec(row["distance"]) - expected["distance"], scene, D("2e-12"))
                for key in ("position", "velocity"):
                    for coordinate in range(3):
                        measured.measure("geometry", key + "_" + "xyz"[coordinate],
                            dec(row[key][coordinate]) - expected[key][coordinate], scene, D("2e-12"))

            timelines = {scene["id"]: timeline_for(scene) for scene in scenes if admitted[scene["id"]]}
            history_queries = [query for query in history_queries if admitted[query["scene"]]]
            history_rows = probe.batch([("state", [query["scene"], *query["position"]]) for query in history_queries])
            for query, row in zip(history_queries, history_rows):
                scene = scenes[query["scene"]]
                measured.check(row["status"] == "ok", "history", "native_status", query, actual=row["status"])
                if row["status"] == "ok":
                    expected = timelines[scene["id"]].state_at(seconds(query["position"], scene["rate"]))
                    grade_motion(measured, scene, row["state"], expected, where_job(scene, query), "history")

            valid_jobs = [job for job in jobs if admitted[job["scene"]]]
            rows = probe.batch([("solve", [job["scene"], *job["position"]]) for job in valid_jobs])
            native_rows = {job["id"]: row for job, row in zip(valid_jobs, rows)}
            successful_jobs = []
            for job, row in zip(valid_jobs, rows):
                measured.counts[job["group"] + ":roots"] += 1
                measured.check(row["status"] == "ok", job["group"], "native_solve_status",
                               where_job(scenes[job["scene"]], job), actual=row["status"])
                if row["status"] == "ok":
                    successful_jobs.append(job)
            roots = native_trajectory_bisection(probe, scenes, successful_jobs, measured)
            max_native_evaluations = max((row.get("evaluations", 0) for row in rows), default=0)
            max_oracle_bisections = 0
            max_independent_bisections = 0
            receiver_pairs = []
            for job in successful_jobs:
                scene, row = scenes[job["scene"]], native_rows[job["id"]]
                where = where_job(scene, job)
                group = job["group"]
                root = roots[job["id"]]
                common = root["best"]
                max_oracle_bisections = max(max_oracle_bisections, root["bisections"])
                exact_geometry = geometry(scene, row["state"][0], row["state"][2])
                common_geometry = geometry(scene, common["state"][0], common["state"][2])
                true_residual = dec(row["delay"]) - exact_geometry["distance"] / dec(scene["c"])
                actual_split_delay = seconds(job["position"], scene["rate"]) - seconds(row["emission"], scene["rate"])
                measured.measure(group, "true_residual_s", true_residual, where, D("1e-11"))
                measured.measure(group, "split_time_residual_s", actual_split_delay - exact_geometry["distance"] / dec(scene["c"]),
                                 where, D("1e-11"))
                measured.measure(group, "retained_residual_recalculation_s", dec(row["residual"]) - true_residual,
                                 where, D("1e-14"))
                measured.measure(group, "split_delay_roundoff_s", actual_split_delay - dec(row["delay"]), where, D("1e-15"))
                measured.measure(group, "distance_identical_motion_m", dec(row["distance"]) - exact_geometry["distance"],
                                 where, D("2e-12"))
                measured.measure(group, "delay_identical_motion_s", dec(row["delay"]) - dec(common["delay"]), where, D("2e-11"))
                measured.measure(group, "ratio_identical_motion", dec(row["ratio"]) - common_geometry["ratio"], where, D("2e-10"))
                measured.measure(group, "ratio_formula", dec(row["ratio"]) - exact_geometry["ratio"], where, D("2e-10"))
                measured.measure("oracle", "native_trajectory_true_residual_s",
                                 dec(common["delay"]) - common_geometry["distance"] / dec(scene["c"]), where, D("1e-14"))
                measured.check(2 <= row["evaluations"] <= 48, group, "all_native_evaluations_bounded", where,
                               actual=row["evaluations"], maximum=48)
                measured.check(actual_split_delay > 0 and row["delay"] > 0, group, "causality", where)
                measured.check(D("0.8") - D("2e-15") <= dec(row["ratio"]) <= D(4) / 3 + D("2e-15"),
                               group, "subsonic_ratio_range", where, actual=row["ratio"])
                if job.get("startup"):
                    measured.check(row["emission"][0] < 0, group, "constant_seed_startup", where, emission=row["emission"])
                if "crossing_anchor" in job:
                    side = (D(row["emission"][0] - job["crossing_anchor"]) + dec(row["emission"][1])) * job["side"]
                    measured.check(side > 0, group, "historical_command_side", where, emission=row["emission"])
                expected_state = timelines[scene["id"]].state_at(seconds(row["emission"], scene["rate"]))
                motion_bound = grade_motion(measured, scene, row["state"], expected_state, where)
                independent = ref.solve_retarded_path(timelines[scene["id"]],
                    ref.CircularGeometry(scene["origin"], scene["radius"]), scene["mic"],
                    seconds(job["position"], scene["rate"]), scene["c"], scene["reference_distance"],
                    residual_tolerance_s=ORACLE_TARGET, max_iterations=ORACLE_BISECTIONS)
                max_independent_bisections = max(max_independent_bisections, independent.iterations)
                independent_geometry = geometry(scene, independent.emission_state.wrapped()[0],
                                                 independent.emission_state.speed_rad_s)
                measured.measure("oracle", "independent_motion_true_residual_s",
                    dec(independent.delay_s) - independent_geometry["distance"] / dec(scene["c"]), where, D("1e-14"))
                measured.measure("motion_contribution", "total_independent_delay_discrepancy_s",
                    dec(row["delay"]) - dec(independent.delay_s), where, D("2e-11") + motion_bound,
                    motion_root_contribution_bound_s=motion_bound)
                measured.measure("motion_contribution", "total_independent_ratio_discrepancy",
                                 dec(row["ratio"]) - independent_geometry["ratio"], where)
                if "paired_job" in job:
                    other = native_rows[job["paired_job"]]
                    difference = abs(dec(row["delay"]) - dec(other["delay"]))
                    measured.check(difference > D("1e-7"), "historical", "distinct_receiver_emissions", where,
                                   emission_difference_s=difference)
                    receiver_pairs.append({"scene": scene["id"], "other_scene": scene["borrowed_from"],
                                           "delay_difference_s": str(difference)})

            derivative_jobs_passed = all(native_rows.get(job["id"], {}).get("status") == "ok"
                                         for job in jobs if job["group"] == "derivative")
            derivative_tables = derivative_convergence(scenes, jobs, native_rows, measured) if derivative_jobs_passed else []
            measured.check(derivative_jobs_passed, "derivative", "complete_native_stencil", {})
            metrics = measured.export()
        probe_report = probe.finish()
    except BaseException:
        probe.abort()
        raise

    for path, before in identities.items():
        measured.check(digest(ROOT / path) == before, "identity", "source_stable_during_qualification", {"path": path})
    return {"schema_version": 1, "gate": "R3 independent native geometry and retarded-path qualification",
        "status": "pass" if not measured.failures else "fail", "contract_id": ref.CONTRACT_ID,
        "model_id": ref.MODEL_ID, "source_head_observed": revision, "source_sha256": identities,
        "reference_id": ref.REFERENCE_ID, "geometry_precision_digits": CONTEXT.prec,
        "motion_precision_digits": ref.PRECISION, "probe": probe_report,
        "runtime": {"python": sys.version, "platform": platform.platform(),
                    "wall_seconds": time.monotonic() - started, "invocation": sys.argv},
        "fixtures": {"radii_m": RADII, "directions": [-1, 1], "phase_extrema_rad": PHASES,
            "sound_speeds_m_s": SOUND_SPEEDS, "rates_hz": RATES, "deterministic_seed": "no random inputs",
            "core_poses": ["right", "left", "above_minimum", "below_minimum", "tangent", "maximum_distance"],
            "geometry_fixtures": len(geometry_cases), "history_queries": len(history_queries),
            "native_root_queries": len(jobs), "rejection_fixtures": len(rejection),
            "shared_history_receiver_pairs": len(receiver_pairs), "counts": dict(sorted(measured.counts.items()))},
        "budgets": {"geometry_distance_m": "2e-12", "native_true_residual_s": "1e-11",
            "delay_identical_motion_s": "2e-11", "frequency_ratio_identical_motion": "2e-10",
            "independent_true_residual_s": "1e-14", "oracle_internal_target_s": ORACLE_TARGET,
            "motion_root_contribution": "radius*abs(phase_error)/(c*(1-beta))"},
        "iterations": {"native_total_evaluations_maximum": max_native_evaluations,
            "native_total_evaluations_limit": 48, "same_trajectory_bisections_maximum": max_oracle_bisections,
            "independent_motion_bisections_maximum": max_independent_bisections,
            "oracle_bisections_limit": ORACLE_BISECTIONS, "oracle_endpoint_evaluations_separate": 2},
        "metrics": metrics, "derivative_convergence": derivative_tables,
        "receiver_emission_differences": receiver_pairs,
        "failure_count": len(measured.failures), "failures": measured.failures,
        "independence": "Converged 100-digit sin/cos series and Cartesian square root; independent batched bisection on native states; original independent 80-digit Decimal timeline and offline solver; no production approximation copied",
        "scope": "R3 numerical primitives; R2 prerequisites and API/rejection lifetime coverage are separate native suites",
        "exclusions": ["R4 waveform rendering", "R5 audible policy", "R6 integration and deadlines",
                       "physical cabinet calibration", "host and audio device qualification"]}


class NativePropagationAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = PROBE_PATH or os.environ.get("HAMMOND_ROTARY_PROPAGATION_PROBE_EXECUTABLE")
        if not value or not Path(value).is_file():
            raise RuntimeError("R3 requires HAMMOND_ROTARY_PROPAGATION_PROBE_EXECUTABLE to name an existing native probe")
        cls.report = qualify(Path(value).resolve())
        if REPORT_PATH:
            Path(REPORT_PATH).parent.mkdir(parents=True, exist_ok=True)
            Path(REPORT_PATH).write_text(json.dumps(cls.report, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    def assert_groups(self, *groups):
        failures = [item for item in self.report["failures"] if item["group"] in groups]
        self.assertFalse(failures, json.dumps(failures[:5], indent=2))

    def test_frozen_geometry_grid(self):
        self.assertEqual(self.report["fixtures"]["geometry_fixtures"], 4 * 2 * 5 * 3 * 2 * 6)
        self.assert_groups("geometry", "admission")

    def test_frozen_native_roots_and_evaluation_cap(self):
        self.assert_groups("frozen_grid")
        self.assertLessEqual(self.report["iterations"]["native_total_evaluations_maximum"], 48)

    def test_historical_crossings_startup_all_rates_and_late_fractions(self):
        self.assertEqual(self.report["fixtures"]["shared_history_receiver_pairs"], 4 * 2 * 2 * 3 * 2)
        self.assert_groups("history", "historical")

    def test_independent_oracles_and_separate_motion_contribution(self):
        self.assert_groups("oracle", "motion_contribution", "identity")

    def test_derivative_stencil_and_root_precision_convergence(self):
        self.assertEqual(len(self.report["derivative_convergence"]), 2)
        self.assert_groups("derivative")

    def test_full_orbit_and_cross_field_rejections(self):
        self.assertEqual(self.report["fixtures"]["rejection_fixtures"], 7)
        self.assert_groups("rejection")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--probe", type=Path)
    arguments, remaining = parser.parse_known_args()
    REPORT_PATH, PROBE_PATH = arguments.report, arguments.probe
    result = unittest.main(argv=[sys.argv[0], *remaining], exit=False, verbosity=2)
    sys.exit(not result.result.wasSuccessful())
