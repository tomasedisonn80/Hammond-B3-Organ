#!/usr/bin/env python3
"""Independent contract arithmetic; no candidate, native process or waveform.

Run from the repository root. Writes only this reviewer's JSON receipt.
"""
from fractions import Fraction as F
from itertools import product, combinations
from pathlib import Path
import hashlib
import json
import platform


REPO = Path(__file__).resolve().parents[4]
SESSION = REPO / "docs/development/2026-11-16-conversion-material"
T, Q = 1 << 16, 1 << 48


def rational(value):
    value = F(value)
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def quotient_rne(value):
    q, r = divmod(value.numerator, value.denominator)
    return q + int(2 * r > value.denominator or
                   (2 * r == value.denominator and q % 2 == 1))


def ordering(times):
    return tuple(tuple(sorted(k for k, v in times.items() if v == at))
                 for at in sorted(set(times.values())))


def sign(value):
    return (value > 0) - (value < 0)


def main():
    paths = [
        "docs/CONTACT_GRID_CONVERSION_CONTRACT.md",
        "docs/reviews/CONTACT_GRID_CONVERSION_NEXT_REVIEW.md",
        "tools/fractional_contact_reference.py",
        "tools/contact_switching_io.py",
        "src/research/CausalContactGrid.cpp",
        "tools/causal_contact_grid_probe.cpp",
        "data/contact-switching/reference-v1/F09-48000-v1.json",
    ]
    hashes = {p: hashlib.sha256((REPO / p).read_bytes()).hexdigest() for p in paths}
    endpoints = []
    for rate in (44100, 48000, 96000):
        for duration in (0.0001, 1.0):
            p = F.from_float(duration)
            exact_speed = F(Q, T * rate) / p
            speed = round(exact_speed)
            assert quotient_rne(exact_speed) == speed
            assert 1 <= speed <= (1 << 32) - 1
            actual_duration = F(Q, T * rate * speed)
            relative_error = abs(actual_duration - p) / p
            assert relative_error == abs(exact_speed - speed) / speed
            assert relative_error <= F(1, 2 * speed)
            endpoints.append({"rate_hz": rate, "duration_hex": duration.hex(),
                              "rounded_speed": speed,
                              "relative_duration_error": rational(relative_error)})

    rounding_cases = 0
    for integer in (0, 1, 2, 32767, 32768, Q - 1):
        for offset in (F(0), F(1, 4), F(1, 2), F(3, 4)):
            x = F(integer) + offset
            assert round(x) == quotient_rne(x)
            assert abs(round(x) - x) <= F(1, 2)
            rounding_cases += 1
    fragments = {
        "unreachable_target_collision": round(Q * (F(1, 2) - F(1, 1 << 54))) == Q // 2,
        "collapsed_hysteresis": round(Q * (F(1, 2) + F(1, 1 << 53))) == Q // 2,
        "command_time_collision": round(T * (F(1, 2) - F(1, 1 << 18))) ==
                                  round(T * (F(1, 2) + F(1, 1 << 18))) == 32768,
        "threshold_order_collision": round(Q * F(1, 2)) ==
                                     round(Q * (F(1, 2) + F(1, 1 << 53))),
    }
    assert all(fragments.values())
    f09 = json.loads((REPO / paths[-1]).read_text())
    duration = F.from_float(f09["keys"][0]["press_seconds"])
    threshold = F.from_float(f09["keys"][0]["on"][4])
    rate = f09["sample_rate_hz"]
    speed = round(F(Q, T * rate) / duration)
    source_edge = threshold * rate * duration
    grid_edge = F(round(Q * threshold), T * speed)
    command = f09["targets"][2]
    command_time = command["frame"] + F.from_float(command["fraction"])
    assert source_edge == command_time == F(375, 32)
    assert source_edge - grid_edge == F(7, 2932031008)

    # Every total preorder of four distinct labels, independently reconstructed
    # from all integer time assignments. No converter/preorder helper is imported.
    preorders = {}
    for values in product(range(4), repeat=4):
        times = dict(zip("ABCD", values))
        preorders.setdefault(ordering(times), times)
    checked_pairs = witnesses = 0
    for sp, st in preorders.items():
        for gp, gt in preorders.items():
            equivalent = all(sign(st[a] - st[b]) == sign(gt[a] - gt[b])
                             for a, b in combinations("ABCD", 2))
            assert equivalent == (sp == gp)
            checked_pairs += 1
            if sp == gp:
                continue
            sg, gg = next((set(s), set(g)) for s, g in zip(sp, gp) if s != g)
            x = min(sg ^ gg)
            y = min(gg) if x in sg - gg else min(sg)
            a, b = sorted((x, y))
            assert a != b
            assert sign(st[a] - st[b]) != sign(gt[a] - gt[b])
            witnesses += 1

    root_checks = 0
    for direction in (-1, 1):
        for i in range(1, 65):
            a, ap = F(i, 7), F(i, 7) + F(1, 1 << 17)
            p = F(1, 2)
            theta = p + direction * F(1, 4)
            pp = p + F(i, 1 << 30)
            thetap = theta - F(1, 1 << 29)
            v, vp = F(1, 4) + F(i, 4096), F(1, 4) + F(i, 4096) + F(1, 1 << 33)
            d, dp = abs(theta - p), abs(thetap - pp)
            left = abs((ap + dp / vp) - (a + d / v))
            bound = abs(ap - a) + (abs(thetap - theta) + abs(pp - p)) / vp + d * abs(vp - v) / (v * vp)
            assert left <= bound
            root_checks += 1

    report = {
        "scope": "independent contract arithmetic and finite preorder lemma checks only",
        "candidate_imported": False, "native_process_executed": False,
        "python": platform.python_version(), "input_sha256": hashes,
        "rounding_cases": rounding_cases, "duration_endpoints": endpoints,
        "scalar_counterexamples": fragments,
        "f09": {"source_edge_and_command": rational(source_edge),
                "grid_edge": rational(grid_edge), "early_by_frames": rational(source_edge - grid_edge),
                "rounded_speed": speed},
        "preorders": len(preorders), "preorder_pairs": checked_pairs,
        "changed_relation_witnesses": witnesses,
        "analytic_root_inequality_cases": root_checks,
        "chosen_budgets": {
            "position_travel": rational(F(1, 1 << 18)),
            "root_frames": rational(F(1, 1 << 10)),
            "root_ticks": 64,
            "root_nanoseconds_by_rate": {str(r): rational(F(10**9, (1 << 10) * r))
                                          for r in (44100, 48000, 96000)},
        },
        "all_checks_passed": True,
        "limits": "Does not qualify candidate implementation, native agreement, complete corpus outcomes, I/O, resource instrumentation, audio, physical fidelity or publication.",
    }
    (SESSION / "reports/A10-independent-arithmetic.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: report[k] for k in ("rounding_cases", "preorders", "preorder_pairs",
                                           "changed_relation_witnesses", "analytic_root_inequality_cases",
                                           "all_checks_passed")}, sort_keys=True))


if __name__ == "__main__":
    main()
