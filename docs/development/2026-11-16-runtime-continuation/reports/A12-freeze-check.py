#!/usr/bin/env python3
"""Read-only fixture-definition integrity/count check; --write retains receipt.

This is not a trajectory/audio oracle.  It checks input domains, immutable
identities, elementary published fixture witnesses and prospective count bounds.
No candidate, grid oracle, converter, renderer, convolution or quadrature runs.
"""

from __future__ import annotations

import argparse
import datetime
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[4]
REPORT = Path(__file__).with_name("A12-fixture-freeze.json")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    module_path = ROOT / "tests/reference/contact_audio_cases.py"
    spec = importlib.util.spec_from_file_location("frozen_audio_cases", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    nominal, stress = module.nominal_cases(), module.stress_cases()
    cases = nominal + stress
    assert len(nominal) == 36 and len(stress) == 39 and len(cases) == 75
    assert len({case["fixture_id"] for case in cases}) == 75
    assert all(case["frames"] == 256 for case in nominal)
    assert [(case["recipe_id"], case["sample_rate_hz"]) for case in cases] == [
        (recipe, rate) for recipe in module.NOMINAL_IDS + module.STRESS_IDS
        for rate in module.RATES]
    for case in cases:
        assert type(case["frames"]) is int and 0 <= case["frames"] <= 256
        assert type(case["origin_frame"]) is int and abs(case["origin_frame"]) <= 2**48
        assert 1 <= len(case["keys"]) <= 4
        assert len(case["targets"]) <= 512
        ids = {source["source_id"] for source in case["sources"]}
        assert len(ids) == len(case["sources"]) and 1 <= len(ids) <= 36
        for source in case["sources"]:
            assert type(source["source_id"]) is int and 1 <= source["source_id"] <= 91
            for field in ("frequency_hz", "amplitude", "phase_turns"):
                assert type(source[field]) is float and math.isfinite(source[field])
            assert 0 <= source["frequency_hz"] <= .45 * case["sample_rate_hz"]
            assert 0 <= source["amplitude"] <= 1 and 0 <= source["phase_turns"] < 1
        for key in case["keys"]:
            for field in ("press_units_per_tick", "release_units_per_tick"):
                assert type(key[field]) is int and 1 <= key[field] <= 2**32 - 1
            assert len(key["contacts"]) == len(key["source_ids"]) == len(key["gains"]) == 9
            assert all(type(value) is int and value in ids for value in key["source_ids"])
            assert all(type(value) is float and math.isfinite(value) and -1 <= value <= 1
                       for value in key["gains"])
            for threshold in key["contacts"]:
                assert type(threshold["off"]) is type(threshold["on"]) is int
                assert 0 <= threshold["off"] < threshold["on"] <= 2**48
        assert [target["tick"] for target in case["targets"]] == sorted(
            target["tick"] for target in case["targets"])
        for target in case["targets"]:
            assert all(type(value) is int for value in target.values())
            assert 0 <= target["tick"] <= case["frames"] * 65536
            assert 0 <= target["position"] <= 2**48
            assert 0 <= target["key_index"] < len(case["keys"])
        raw = module.canonical_bytes(case)
        assert raw.endswith(b"\n") and not raw.endswith(b"\n\n")
        assert json.loads(raw)["fixture_id"] == case["fixture_id"]
    assert module.canonical_bytes(module.all_cases()) == module.canonical_bytes(cases)

    # Direct algebraic input witnesses, not generalized path reconstruction.
    p, r, tick = 2**32 - 1, 2**32 - 2, 65536
    a = (Fraction(255 * tick - 1) + Fraction(p - 1, p)) / tick
    b = (Fraction(255 * tick) + Fraction(1, r)) / tick
    start = 256 * 65535 - 128
    c = (Fraction(start) + Fraction(1, p)) / tick
    d = (Fraction(start + 255) + Fraction(1, r)) / tick
    assert a < b and float(a) == float(b) == 255.0
    assert ((d - c).numerator.bit_length(), (d - c).denominator.bit_length()) == (72, 80)
    assert (((c + d) / 2).numerator.bit_length(), ((c + d) / 2).denominator.bit_length()) == (89, 81)
    assert sum(on <= 2**47 for on in module.ON) == 4
    assert sum(off < 2**47 for off in module.OFF) == 5
    assert Fraction(63, 64) + Fraction(17, 64) == Fraction(5, 4)
    assert Fraction(47, 64) + Fraction(17, 64) == 1
    assert 4 * 128 == 512 and 36 * 128 == 4608 and 36 * 64 == 2304
    assert all(0 < Fraction(t) + Fraction(1, p) < 128 for t in range(128))

    original_root = ROOT / "data/contact-switching/reference-v1"
    original_manifest_path = original_root / "manifest.json"
    original_manifest = json.loads(original_manifest_path.read_bytes())
    assert original_manifest["fixture_count"] == 36
    originals = []
    original_bindings = {}
    for name, declared in original_manifest["files"].items():
        path = original_root / name
        data = path.read_bytes()
        assert len(data) == declared["bytes"] and sha(path) == declared["sha256"]
        originals.append(json.loads(data))
        original_bindings[name] = {"bytes": len(data), "sha256": sha(path)}
    assert len(originals) == 36 and all(case["frames"] == 256 for case in originals)

    def gl8_upper(case, inverse_widths):
        n = case["frames"]
        if not n:
            return 0
        edges = 9 * len(case["targets"])
        return (n + 33) * 8 * sum(min(n, 32) * factor + edges + 1
                                  for factor in inverse_widths)

    fir = sum((case["frames"] + 33) * 8193 for case in cases if case["frames"])
    routes = sum((case["frames"] * 256 + 1) * 9 * len(case["keys"])
                 for case in cases if case["frames"])
    grid_gl8 = sum(gl8_upper(case, (1, 2, 4)) for case in cases)
    original_gl8 = sum(gl8_upper(case, (1, 2, 4)) for case in originals)
    ceil_gl8 = sum(gl8_upper(case, (2, 4)) for case in originals)
    grid_four = 36 * 289 * sum(32 * factor + 1 for factor in (32, 64, 128, 256))
    stress_fir = sum((case["frames"] + 33) * 8193 for case in stress if case["frames"])
    responses = 259 * sum(32 * factor + 1 for factor in (32, 64, 128, 256))
    response_gl8 = (259 + 1) * 8 * (32 + 64 + 128)
    assert (fir, routes, grid_gl8) == (123509475, 38127456, 47998224)
    assert (original_gl8, ceil_gl8) == (25635456, 20641536)
    assert fir < 180000000 and routes < 180000000
    assert grid_four + stress_fir + responses < 256000000
    assert grid_four + 36 * 289 * 8193 + responses < 256000000
    assert grid_gl8 + response_gl8 < 64000000
    assert original_gl8 + ceil_gl8 + response_gl8 < 64000000

    inputs = [
        "AGENTS.md", "docs/PLAN.md",
        "docs/development/2026-11-16-runtime-continuation/SCOPE.md",
        "docs/development/2026-11-16-runtime-continuation/ROOT_DECISIONS.md",
        "docs/research/CAUSAL_CONTACT_AUDIO_NEXT.md",
        "docs/reviews/CAUSAL_CONTACT_AUDIO_NEXT_REVIEW.md",
        "docs/CAUSAL_CONTACT_GRID_CONTRACT.md",
        "docs/CONTACT_SWITCHING_VALIDATION.md",
        "docs/CAUSAL_CONTACT_AUDIO_CONTRACT.md",
        "docs/CAUSAL_CONTACT_AUDIO_VALIDATION.md",
        "tests/reference/contact_audio_cases.py",
        str(Path(__file__).resolve().relative_to(ROOT)),
    ]
    manifest = module.manifest()
    result = {
        "schema_version": 1,
        "worker": "/root/w02_a12",
        "protocol_id": module.PROTOCOL_ID,
        "evidence_class": "synthetic",
        "record_type": "preimplementation-input-freeze-and-integrity-only",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cwd": str(ROOT),
        "command": "python3 -B docs/development/2026-11-16-runtime-continuation/reports/A12-freeze-check.py --write",
        "python": sys.version,
        "platform": platform.platform(),
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "head_tree": subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip(),
        "input_hashes": {name: sha(ROOT / name) for name in inputs},
        "fixture_manifest_sha256": hashlib.sha256(module.canonical_bytes(manifest)).hexdigest(),
        "fixture_manifest": manifest,
        "original_F_manifest_sha256": sha(original_manifest_path),
        "original_F_files": original_bindings,
        "structural_integrity": {"passed": True, "nominal_rows": 36, "stress_rows": 39,
                                 "audio_or_candidate_executed": False,
                                 "general_trajectory_oracle_executed": False,
                                 "original_F_bytes_unchanged": True},
        "direct_input_witnesses": {
            "thin_equal_binary64_host_endpoints": [float(a).hex(), float(b).hex()],
            "thin_width_positive": b > a,
            "thin_width_bits": [(b - a).numerator.bit_length(), (b - a).denominator.bit_length()],
            "wide_width_bits": [(d - c).numerator.bit_length(), (d - c).denominator.bit_length()],
            "wide_midpoint_bits": [((c + d) / 2).numerator.bit_length(), ((c + d) / 2).denominator.bit_length()],
            "burst_constructive_counts": {"commands": 512, "edges": 4608, "pieces": 2304},
        },
        "prospective_counts_not_execution": {
            "all_grid_L256_FIR_terms_upper": fir,
            "all_grid_cell_route_visits_upper": routes,
            "all_grid_GL8_three_width_upper": grid_gl8,
            "original_F_GL8_three_width_upper": original_gl8,
            "original_F_ceil_GL8_two_width_upper": ceil_gl8,
            "normalizer_response_GL8_upper": response_gl8,
            "grid_nominal_fourfactor_plus_stress_L256_FIR_upper": grid_four + stress_fir,
            "original_F_fourfactor_plus_36converted_L256_FIR_upper": grid_four + 36 * 289 * 8193,
            "fourfactor_response_FIR_products": responses,
        },
        "status": "inputs_frozen_numerical_and_resource_execution_unrun",
        "unrun_gates": ["independent contract admission", "independent audio oracle",
                        "native discrete parity", "same-build partitions and causal prefixes",
                        "transaction/lifecycle/resource measurements",
                        "grid full-window continuous grade", "original F full-window expansion",
                        "original conversion/native full-window grade"],
    }
    rendered = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.write:
        REPORT.write_text(rendered, encoding="utf-8")
        print(json.dumps({"receipt": str(REPORT.relative_to(ROOT)),
                          "fixture_manifest_sha256": result["fixture_manifest_sha256"],
                          "validation_sha256": result["input_hashes"]["docs/CAUSAL_CONTACT_AUDIO_VALIDATION.md"],
                          "fixture_module_sha256": result["input_hashes"]["tests/reference/contact_audio_cases.py"],
                          "receipt_sha256": sha(REPORT), "rows": len(cases),
                          "status": result["status"]}, sort_keys=True))
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
