"""Bounded independent review arithmetic, not a converter or admission suite.

Run from the repository root with Python 3.10+ and -B. No candidate helpers,
author calculation_recipe, native executable, audio renderer or tests are run.
Only this worker's JSON receipt is written.
"""

import ast
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).with_suffix(".json")
T, Q = 2**16, 2**48
AUTHOR = "docs/development/2026-11-15-streaming-continuation/reports/A37-fraction-boundaries.json"
PROPOSAL = "docs/research/CONTACT_GRID_CONVERSION_NEXT.md"
PUBLISHED = "af2b74760ee195c9497b314a1a29172f5238dd44"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def binary(value):
    return F(*float(value).as_integer_ratio())


def encode(value):
    if isinstance(value, F):
        return {"numerator": str(value.numerator),
                "denominator": str(value.denominator)}
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


def read_fraction(value):
    return F(int(value["numerator"]), int(value["denominator"]))


author_bytes = (ROOT / AUTHOR).read_bytes()
author = json.loads(author_bytes)
bindings = {}
for path, original in author["input_sha256"].items():
    current = sha((ROOT / path).read_bytes())
    bindings[path] = {"author_sha256": original, "current_sha256": current,
                      "unchanged": current == original}
assert [p for p, row in bindings.items() if not row["unchanged"]] == [
    "tools/contact_switching_io.py"]

io_path = "tools/contact_switching_io.py"
old_io = subprocess.check_output(
    ["git", "show", PUBLISHED + ":" + io_path], cwd=ROOT)
new_io = (ROOT / io_path).read_bytes()
assert sha(old_io) == bindings[io_path]["author_sha256"]


def definitions(data):
    text = data.decode("utf-8")
    return {node.name: ast.get_source_segment(text, node)
            for node in ast.parse(text).body
            if isinstance(node, (ast.FunctionDef, ast.ClassDef))}


old_definitions, new_definitions = definitions(old_io), definitions(new_io)
changed = sorted(name for name in old_definitions
                 if old_definitions[name] != new_definitions.get(name))
added = sorted(set(new_definitions) - set(old_definitions))
assert changed == ["OutputPlan", "load_input", "preflight_paths"]
assert added == ["_preflight_input_signature"]
assert old_definitions["parse_input"] == new_definitions["parse_input"]

# Fraction.__round__ supplies exact ties-to-even independently of A37's helper.
midpoints = [(F(1, 2), 0), (F(3, 2), 2), (F(5, 2), 2),
             (F(7, 2), 4), (F(2 * Q - 1, 2), Q), (F(2 * Q + 1, 2), Q)]
for value, expected in midpoints:
    assert round(value) == expected

rate_rows = []
duration_rows = []
minimum_duration, maximum_duration = binary(0.0001), F(1)
for rate in (44100, 48000, 96000):
    odd, power = rate, 0
    while odd % 2 == 0:
        odd //= 2
        power += 1
    assert odd > 1 and rate == 2**power * odd
    rate_rows.append({"rate_hz": rate, "power_of_two": power, "odd_factor": odd,
                      "half_tick_seconds": F(1, 2 * T * rate)})
    for duration in (minimum_duration, maximum_duration):
        ideal = F(Q, T * rate) / duration
        speed = round(ideal)
        realized = F(Q, T * rate * speed)
        assert ideal.denominator > 1
        assert 1 <= speed <= 2**32 - 1
        assert abs(ideal - speed) <= F(1, 2)
        assert abs(realized - duration) / duration == abs(ideal - speed) / speed
        assert abs(F(T * speed, Q) - 1 / (rate * duration)) <= F(1, 2**33)
        duration_rows.append({"rate_hz": rate, "input_seconds": duration,
                              "ideal_units_per_tick": ideal,
                              "rounded_units_per_tick": speed,
                              "effective_seconds": realized,
                              "effective_seconds_within_original_range":
                                  minimum_duration <= realized <= maximum_duration,
                              "relative_duration_error": abs(ideal - speed) / speed})

half = F(1, 2)
lower = half - F(1, 2**54)
upper = half + F(1, 2**53)
early, late = half - F(1, 2**18), half + F(1, 2**18)
duration = F(1, 2048)
velocity = 1 / (48000 * duration)
ideal_speed = F(Q, T) * velocity
speed = round(ideal_speed)
for value in (half, lower, upper, early, late, duration, F(375, 32)):
    assert binary(value) == value
assert velocity == F(16, 375)

# 1: a target below the threshold is an open hold; grid rounding makes equality.
assert lower < half and round(Q * lower) == round(Q * half) == Q // 2
assert F(round(Q * lower), Q) - lower == F(1, 2**54)
example1 = {"name": "unreachable-target-becomes-equality", "source_target": lower,
            "source_on": half, "source_off": F(1, 4),
            "grid_target": round(Q * lower), "grid_on": round(Q * half),
            "position_error_travel": F(1, 2**54),
            "source_bit_after_arrival": False,
            "hypothetical_grid_bit_after_arrival": True,
            "required_rejection": "distinct threshold/target collision"}

# 2: a valid positive hysteresis width becomes an invalid grid configuration.
assert half < upper and round(Q * half) == round(Q * upper)
example2 = {"name": "hysteresis-collapse", "source_off": half, "source_on": upper,
            "source_width_travel": upper - half,
            "grid_off": round(Q * half), "grid_on": round(Q * upper),
            "required_rejection": "grid off must remain strictly below on"}

# 3: two distinct host times collide even when they are commands for different keys.
assert round(T * early) == round(T * late) == 32768
assert late - early == F(1, 2**17)
example3 = {"name": "distinct-command-collision", "source_times_frames": [early, late],
            "unrounded_ticks": [T * early, T * late], "rounded_ticks": [32768, 32768],
            "lost_interval_frames": late - early,
            "required_rejection": "distinct exact times collide across the whole epoch"}

# 4: distinct upward roots become a tie, then index serialization reverses the list.
source_c0, source_c1 = upper / velocity, half / velocity
assert source_c1 < source_c0 and source_c0 - source_c1 == F(375, 2**57)
grid_root = F(Q // 2, T * speed)
example4 = {"name": "contact-order-change", "source_roots_frames": [source_c0, source_c1],
            "source_gap_frames": source_c0 - source_c1, "source_order": [1, 0],
            "hypothetical_grid_roots_frames": [grid_root, grid_root],
            "hypothetical_grid_order": [0, 1],
            "required_rejection": "threshold collision before any topology certificate"}

# 5: read actual F09 bytes; compute its first contact-4 make from the equations.
f09_path = "data/contact-switching/reference-v1/F09-48000-v1.json"
f09 = json.loads((ROOT / f09_path).read_bytes())
assert f09["sample_rate_hz"] == 48000 and f09["frames"] == 256
assert all(binary(key["press_seconds"]) == duration for key in f09["keys"])
assert all(binary(key["on"][4]) == half for key in f09["keys"])
source_times = [F(row["frame"]) + binary(row["fraction"]) for row in f09["targets"]]
command = source_times[2]
assert command == F(375, 32) == half / velocity
assert all(u == command for u in source_times[2:6])
rounded_ticks = [round(T * u) for u in source_times]
assert len({round(T * u) for u in set(source_times)}) == len(set(source_times))
assert all(u in (0, f09["frames"]) or 0 < tick < T * f09["frames"]
           for u, tick in zip(source_times, rounded_ticks))
for key in f09["keys"]:
    values = {F(0), F(1), *(binary(x) for x in key["on"] + key["off"])}
    values.update(binary(row["target"]) for row in f09["targets"]
                  if row["key_id"] == key["key_id"])
    assert len({round(Q * x) for x in values}) == len(values)
    assert all(round(Q * binary(off)) < round(Q * binary(on))
               for off, on in zip(key["off"], key["on"]))
    assert all(binary(off) > 0 and round(Q * binary(off)) > 0 for off in key["off"])
    final_command = [row for row in f09["targets"] if row["key_id"] == key["key_id"]][-1]
    assert binary(final_command["target"]) == 0
    assert F(final_command["frame"]) + binary(final_command["fraction"]) == source_times[-1]
assert ideal_speed == F(2**36, 375) and speed == 183251938
assert F(speed) - ideal_speed == F(14, 375)
advance = command - grid_root
assert advance == F(7, 2932031008)
command_tick = round(T * command)
overshoot = command_tick * speed - Q // 2
assert command_tick == 768000 and overshoot == 28672
release_duration = binary(f09["keys"][0]["release_seconds"])
release_speed = round(F(Q, T * 48000) / release_duration)
latest_source_arrival = source_times[-1] + 48000 * release_duration
latest_grid_arrival = F(rounded_ticks[-1], T) + F(Q, T * release_speed)
assert latest_source_arrival < 256 and latest_grid_arrival < 256
example5 = {"name": "F09-command-equality-lost", "source_edge_frames": command,
            "command_frames": command, "command_tick": command_tick,
            "ideal_units_per_tick": ideal_speed, "rounded_units_per_tick": speed,
            "speed_error_units_per_tick": F(speed) - ideal_speed,
            "grid_edge_frames": grid_root, "grid_edge_ticks": grid_root * T,
            "edge_advance_frames": advance, "edge_advance_seconds": advance / 48000,
            "position_overshoot_units_at_command": overshoot,
            "position_overshoot_travel_at_command": F(overshoot, Q),
            "edge_command_sign_original": 0, "edge_command_sign_grid": -1,
            "scalar_collision_checks_pass_for_actual_F09": True,
            "rounded_command_ticks_in_original_ordinal_order": rounded_ticks,
            "latest_full_release_arrival_frames_source": latest_source_arrival,
            "latest_full_release_arrival_frames_grid": latest_grid_arrival,
            "both_final_contact_vectors_all_open": True,
            "final_bit_reason": "Both final targets are zero, release completes before N, and all off thresholds are positive.",
            "required_rejection": "exact edge-versus-command equality changed"}

# Compare derived results to selected author receipt fields only after deriving them.
ae = author["examples"]
assert ae[0]["grid_on"] == example1["grid_on"]
assert read_fraction(ae[0]["position_error"]) == example1["position_error_travel"]
assert ae[1]["grid_off"] == ae[1]["grid_on"] == example2["grid_on"]
assert read_fraction(ae[2]["lost_interval_frames"]) == example3["lost_interval_frames"]
assert read_fraction(ae[3]["source_gap_frames"]) == example4["source_gap_frames"]
assert ae[3]["source_order"] == example4["source_order"]
assert read_fraction(ae[4]["edge_advance_frames"]) == advance
assert read_fraction(ae[4]["grid_edge_tick"]) == grid_root * T
assert ae[4]["overshoot_position_units_at_command"] == overshoot

tiny = F(1, 2**1074)
assert binary(tiny) == tiny and round(Q * tiny) == round(T * tiny) == 0
for path, row in bindings.items():
    assert sha((ROOT / path).read_bytes()) == row["current_sha256"]

report = {
    "schema_version": 1, "worker": "/root/w09_a49", "wave": 9,
    "evidence_class": "synthetic", "receipt_kind": "independent-prospective-arithmetic-review",
    "command": "python3 -B docs/development/2026-11-15-streaming-continuation/reports/A49-independent-arithmetic.py",
    "cwd": str(ROOT), "python": sys.version.split()[0], "platform": platform.platform(),
    "observed_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "observed_head_tree": subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip(),
    "source_identity_note": "Individual current input hashes bind this calculation; HEAD alone does not describe concurrent work.",
    "script_sha256": sha(Path(__file__).read_bytes()), "proposal_sha256": sha((ROOT / PROPOSAL).read_bytes()),
    "author_receipt_sha256": sha(author_bytes), "author_bindings": bindings,
    "filesystem_boundary": {"historical_commit": PUBLISHED, "historical_io_sha256": sha(old_io),
                            "current_io_sha256": sha(new_io), "changed_definitions": changed,
                            "added_definitions": added, "parser_text_unchanged": True,
                            "scope": "A49 only checks source separation; A47 owns I/O admission and root owns current-platform qualification."},
    "units": {"ticks_per_frame": T, "units_per_full_travel": Q,
              "half_tick_frames": F(1, 2 * T), "half_position_unit_travel": F(1, 2 * Q),
              "half_speed_unit_travel_per_frame": F(T, 2 * Q)},
    "rate_factorizations": rate_rows, "duration_endpoint_checks": duration_rows,
    "no_exact_speed_argument": "For reduced P=p/2^k in the admitted duration range and F=2^a*m, m odd>1, ideal speed is 2^(32+k-a)/(m*p). Its odd denominator cannot cancel into a power-of-two numerator. No positive moving slope is exactly embedded by this direct integer-speed mapping.",
    "midpoint_checks": [{"exact": value, "rne_integer": expected} for value, expected in midpoints],
    "examples": [example1, example2, example3, example4, example5],
    "subnormal_boundary": {"exact_positive_binary64": tiny, "position_rounds_to": 0,
                           "time_rounds_to_tick": 0,
                           "finding": "Preserve admitted binary64 subnormals; explicitly reject new initial-target no-ops/interior-to-zero time collisions. Sidecar gains/amplitudes must not be flushed to zero."},
    "conditional_root_bound": {"formula": "Ea + (Etheta + Ep)/vprime + d*Ev/(v*vprime)",
                               "conditions": "Matched eligible roots, same direction, positive speeds, d=original threshold distance; Ep is propagated anchor error, not only input rounding.",
                               "status": "Correct conditional inequality; no acceptance threshold is provided or admitted."},
    "pairwise_topology_work_at_domain_max": {"edges": 4608, "commands": 512,
                                           "edge_pairs": 4608 * 4607 // 2,
                                           "edge_command_and_endpoint_pairs": 4608 * 514},
    "outcome": "All bounded exact assertions and source checks completed; five author fragments independently reproduced. Proposal arithmetic accepted for planning only; converter protocol remains unadmitted.",
    "not_executed": ["converter implementation", "36-fixture conversion admission", "native probe",
                     "build", "broad tests", "audio rendering", "full-window numerical admission", "platform or physical qualification"]
}
OUT.write_text(json.dumps(encode(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({"receipt": str(OUT.relative_to(ROOT)), "sha256": sha(OUT.read_bytes()),
                  "bytes": OUT.stat().st_size, "independent_fragments": 5,
                  "source_binding_matches": 9, "filesystem_only_binding_changes": 1,
                  "outcome": "bounded exact assertions passed"}, sort_keys=True))
