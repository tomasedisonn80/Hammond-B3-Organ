#!/usr/bin/env python3
"""Generate an auditable scratch-only grid counter build and check its receipt.

The production translation unit and header are never edited. Root owns compiler
invocation; this tool generates inputs or runs already-built normal/diagnostic
executables. Measured operation counts describe these fixtures, not deadlines.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/CAUSAL_CONTACT_GRID_CONTRACT.md"
FROZEN_CONTRACT_SHA256 = "ba851e6af0601b52aef73d4b9effb64dffac3ef5e230eff7015e10e58a4ecb4e"
SOURCE = ROOT / "src/research/CausalContactGrid.cpp"
HEADER = ROOT / "include/hammond/research/CausalContactGrid.h"
FIXTURE = ROOT / "tests/test_causal_contact_grid_resources.cpp"
FIELDS = (
    "target_validations", "target_applications", "position_evaluations",
    "contact_examinations", "reached_roots", "gcd_normalizations",
    "euclidean_remainders", "edge_comparisons", "committed_edge_copies",
)
ABSOLUTE_CEILINGS = dict(zip(FIELDS, (512, 512, 2052, 18468, 4608, 4608, 294912, 80640, 4608)))

# Every source anchor must occur exactly once in the unchanged source. The
# retained manifest includes the complete original anchor, its line, and the
# exact inserted statement, making this transformation independently replayable.
ANCHORS = (
    ("process_target_validation",
     "    for (const auto& target : targets) {\n        if (target.keyIndex >= state_.config.keyCount",
     "    for (const auto& target : targets) {\n        ++work_receipt::counters.target_validations;\n        if (target.keyIndex >= state_.config.keyCount",
     "One entered process target-domain validation, including the failing target."),
    ("close_target_validation",
     "    for (const auto& target : endpointTargets) {\n        if (target.keyIndex >= state_.config.keyCount",
     "    for (const auto& target : endpointTargets) {\n        ++work_receipt::counters.target_validations;\n        if (target.keyIndex >= state_.config.keyCount",
     "One entered close target-domain validation, including the failing target."),
    ("target_application",
     "    auto& key = state.keys[target.keyIndex];",
     "    ++work_receipt::counters.target_applications;\n    auto& key = state.keys[target.keyIndex];",
     "One apply_target invocation, including unchanged targets and caller ties."),
    ("position_evaluation",
     "                                std::uint64_t& position) noexcept {",
     "                                std::uint64_t& position) noexcept {\n    ++work_receipt::counters.position_evaluations;",
     "One position_at invocation, including holds."),
    ("contact_examination",
     "             contactIndex < kContactGridContactsPerKey; ++contactIndex) {",
     "             contactIndex < kContactGridContactsPerKey; ++contactIndex) {\n            ++work_receipt::counters.contact_examinations;",
     "One entered contact loop body, including candidates rejected by bit/range checks."),
    ("reached_root",
     "    if (remainder == 0) {\n        time =",
     "    ++work_receipt::counters.reached_roots;\n    if (remainder == 0) {\n        time =",
     "One interval-admitted root after overflow checks; integer roots also count."),
    ("gcd_normalization",
     "    std::uint32_t larger = speed;",
     "    ++work_receipt::counters.gcd_normalizations;\n    std::uint32_t larger = speed;",
     "One noninteger root entering Euclid; integer roots canonicalize directly to 0/1."),
    ("euclidean_remainder",
     "        const std::uint32_t next = larger % smaller;",
     "        ++work_receipt::counters.euclidean_remainders;\n        const std::uint32_t next = larger % smaller;",
     "One actual Euclidean remainder, after its defensive 64-step guard."),
    ("edge_comparison",
     "                                const ContactGridEdge& right) noexcept {",
     "                                const ContactGridEdge& right) noexcept {\n    ++work_receipt::counters.edge_comparisons;",
     "One edge_before call, including comparisons returning false."),
    ("committed_edge_copy",
     "        output[index] = stagedEdges_[index];",
     "        ++work_receipt::counters.committed_edge_copies;\n        output[index] = stagedEdges_[index];",
     "One edge copied into caller output after capacity/admission; staging/sort copies excluded."),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(path: Path) -> dict:
    resolved = path.resolve(strict=True)
    return {"path": str(resolved), "sha256": sha256(resolved), "bytes": resolved.stat().st_size}


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def inputs() -> dict:
    require(sha256(CONTRACT) == FROZEN_CONTRACT_SHA256, "frozen contract hash mismatch")
    return {
        "production_cpp": identity(SOURCE), "production_header": identity(HEADER),
        "resource_fixture": identity(FIXTURE), "contract": identity(CONTRACT),
        "generator": identity(Path(__file__)),
    }


def generate(scratch: Path) -> dict:
    scratch = scratch.resolve()
    require(not scratch.is_relative_to(ROOT), "scratch generation directory must be outside the repository")
    original_inputs = inputs()
    source = SOURCE.read_text(encoding="utf-8")
    modified = source
    anchors = []
    for name, anchor, replacement, meaning in ANCHORS:
        require(source.count(anchor) == 1, f"{name}: expected exactly one source anchor, got {source.count(anchor)}")
        require(modified.count(anchor) == 1, f"{name}: earlier insertion changed its unique anchor")
        anchors.append({
            "name": name, "original_occurrences": 1,
            "source_line": source[:source.index(anchor)].count("\n") + 1,
            "anchor": anchor, "replacement": replacement, "meaning": meaning,
        })
        modified = modified.replace(anchor, replacement, 1)
    prologue = (
        "// GENERATED scratch diagnostic; do not substitute for production.\n"
        f"// Production SHA-256: {original_inputs['production_cpp']['sha256']}\n"
        '#include "CausalContactGridWorkCounters.h"\n'
    )
    scratch.mkdir(parents=True, exist_ok=True)
    generated_cpp = scratch / "CausalContactGrid.instrumented.cpp"
    generated_header = scratch / "CausalContactGridWorkCounters.h"
    generated_cpp.write_text(prologue + modified, encoding="utf-8")
    generated_header.write_text(
        "#pragma once\n#include <cstdint>\n"
        "namespace hammond::research::work_receipt {\nstruct Counts {\n"
        + "".join(f"    std::uint64_t {field}{{}};\n" for field in FIELDS)
        + "};\ninline thread_local Counts counters{};\n"
        "inline void begin() noexcept { counters = {}; }\n"
        "[[nodiscard]] inline Counts end() noexcept { return counters; }\n"
        "} // namespace hammond::research::work_receipt\n", encoding="utf-8")
    require(inputs() == original_inputs, "production inputs changed during scratch generation")
    manifest = {
        "schema_version": 1, "kind": "scratch-instrumentation-source-map",
        "inputs": original_inputs, "generated_cpp": identity(generated_cpp),
        "generated_header": identity(generated_header), "anchors": anchors,
        "compile_requirement": {
            "define": "HAMMOND_GRID_WORK_RECEIPT=1", "include": str(scratch),
            "translation_units": [str(FIXTURE), str(generated_cpp)],
            "link": "Do not link production hammond_core or the production grid TU into this diagnostic.",
            "other_definitions": "Use the coordinated test target's HAMMOND_TEST_PROFILE and HAMMOND_SOURCE_DIR definitions.",
        },
        "scope": "Instrumentation adds plain thread-local counter increments only; production source/header are unchanged.",
    }
    write_json(scratch / "instrumentation-manifest.json", manifest)
    return manifest


def run_binary(path: Path, raw_path: Path) -> tuple[dict, dict]:
    binary = identity(path)
    started = time.perf_counter()
    child = subprocess.run([binary["path"]], cwd=ROOT, capture_output=True, timeout=90, check=False)
    seconds = time.perf_counter() - started
    raw_path.write_bytes(child.stdout)
    stderr_path = raw_path.with_suffix(".stderr.txt")
    stderr_path.write_bytes(child.stderr)
    require(identity(path) == binary, "executable changed during observation")
    execution = {
        "binary": binary, "cwd": str(ROOT), "argv": [binary["path"]],
        "exit_code": child.returncode, "external_wall_seconds": seconds,
        "stdout": identity(raw_path), "stderr": identity(stderr_path),
    }
    require(child.returncode == 0, f"{path.name} failed ({child.returncode}); retained {raw_path} and {stderr_path}")
    data = json.loads(child.stdout)
    require(data.get("passed") is True, f"{path.name} did not report success")
    return data, execution


def compare_receipts(normal: dict, instrumented: dict) -> dict:
    require(normal["work_instrumented"] is False, "normal fixture unexpectedly instrumented")
    require(instrumented["work_instrumented"] is True, "scratch fixture lacks counters")
    left, right = copy.deepcopy(normal), copy.deepcopy(instrumented)
    for receipt in (left, right):
        del receipt["work_instrumented"]
        for call in receipt["calls"]:
            del call["work"]
    require(left == right, "normal and instrumented semantic/allocation/size receipts differ")
    require(normal["calibrations"] == 6, "expected before/after calibration at all three rates")
    observed_maxima = dict.fromkeys(FIELDS, 0)
    totals = dict.fromkeys(FIELDS, 0)
    for call in instrumented["calls"]:
        name = f"{call['rate']}/{call['api']}/{call['scenario']}"
        require(call["allocations"] == 0 and call["deallocations"] == 0, f"allocation gate: {name}")
        work = call["work"]
        require(set(work) == set(FIELDS), f"counter schema: {name}")
        k, m = call["configured_keys"], min(call["supplied_commands"], 512)
        e = call["required_edges"]
        per_call = {
            "target_validations": m, "target_applications": m,
            "position_evaluations": k * (m + 1),
            "contact_examinations": 9 * k * (m + 1),
            "reached_roots": e, "gcd_normalizations": e,
            "euclidean_remainders": 64 * e,
            "edge_comparisons": max(0, (9 * k - 1) * e // 2),
            "committed_edge_copies": call["edges_written"],
        }
        for field in FIELDS:
            value = work[field]
            require(type(value) is int and value >= 0, f"nonnegative integer counter: {name}/{field}")
            require(value <= per_call[field], f"per-call ceiling exceeded: {name}/{field}")
            require(value <= ABSOLUTE_CEILINGS[field], f"absolute ceiling exceeded: {name}/{field}")
            totals[field] += value
            observed_maxima[field] = max(observed_maxima[field], value)
        require(work["reached_roots"] == e, f"root/output semantic count disagreement: {name}")
        require(work["committed_edge_copies"] == call["edges_written"], f"committed-copy disagreement: {name}")
        require(work["euclidean_remainders"] <= 64 * work["gcd_normalizations"], f"gcd ceiling: {name}")
        if call["api"] not in ("process", "close_observation"):
            require(all(value == 0 for value in work.values()), f"unexpected work outside process/close: {name}")

    # Exact expected counts are constructive fixture predictions, checked here
    # against measured counters, never substituted for those observations.
    predictions = {
        "maximum_capacity_short": (512, 512, 512, 4608, 4608, 0, 0, 80640, 0),
        "maximum_capacity_retry": (512, 512, 512, 4608, 4608, 0, 0, 80640, 4608),
        "maximum_traversal": (512, 512, 2052, 18378, 0, 0, 0, 0, 0),
        "fibonacci_roots": (4, 4, 4, 36, 36, 36, 1620, 35, 36),
        "maximum_speed": (4, 4, 4, 36, 36, 36, 108, 35, 36),
        "zero_epoch_maximum_close": (512, 512, 0, 0, 0, 0, 0, 0, 0),
    }
    for scenario, values in predictions.items():
        selected = [call for call in instrumented["calls"] if call["scenario"] == scenario]
        require(sorted(call["rate"] for call in selected) == [44100, 48000, 96000], f"missing rate: {scenario}")
        for call in selected:
            require(call["work"] == dict(zip(FIELDS, values)), f"constructive count prediction differs: {scenario}/{call['rate']}")
    return {
        "calls_checked": len(instrumented["calls"]), "api_counts": normal["api_counts"],
        "allocation_totals": {"allocations": 0, "deallocations": 0},
        "sizes": normal["sizes"], "semantic_hash_fnv1a64": normal["semantic_hash_fnv1a64"],
        "edge_assertions_each_build": normal["edge_assertions"],
        "snapshot_assertions_each_build": normal["snapshot_assertions"],
        "measured_operation_maxima_per_call": observed_maxima,
        "measured_operation_totals_all_calls": totals,
        "frozen_absolute_ceilings": ABSOLUTE_CEILINGS,
        "constructive_predictions_verified_by_counters": {
            scenario: dict(zip(FIELDS, values)) for scenario, values in predictions.items()},
    }


def verify(args: argparse.Namespace) -> dict:
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    require(inputs() == manifest["inputs"], "source/header/fixture/contract/generator changed since generation")
    for key in ("generated_cpp", "generated_header"):
        require(identity(Path(manifest[key]["path"])) == manifest[key], f"generated input changed: {key}")
    report_path = args.report.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    stem = report_path.with_suffix("")
    normal, normal_execution = run_binary(args.normal_binary, Path(str(stem) + "-normal.json"))
    instrumented, diagnostic_execution = run_binary(args.instrumented_binary, Path(str(stem) + "-instrumented.json"))
    checked = compare_receipts(normal, instrumented)
    require(inputs() == manifest["inputs"], "source inputs changed during observations")
    build_evidence = identity(args.build_evidence)
    result = {
        "schema_version": 1, "kind": "causal-contact-grid-resource-receipt", "passed": True,
        "manifest": manifest, "manifest_file": identity(args.manifest),
        "build_evidence": build_evidence,
        "build_evidence_text": args.build_evidence.read_text(encoding="utf-8"),
        "normal_execution": normal_execution, "instrumented_execution": diagnostic_execution,
        **checked,
        "measurement_scope": (
            "Current-thread global C++ scalar/array, sized, nothrow and aligned new/delete calls; "
            "12-allocation/12-deallocation explicit function-pointer calibration before and after each rate. "
            "Heap buffers, object backing, assertions, hashing, formatting and final backing deallocation "
            "are outside armed public API scopes. Constructor and explicit destructor are separately armed. "
            "Counters belong to the generated scratch implementation; normal fixture expected edges, "
            "semantic snapshot assertions and field-wise semantic hash match its normal core run."),
        "source_derived_bounds_not_measurements": {
            "epoch_contact_examinations": 165888,
            "epoch_derivation": "At most 4096 positive calls plus 512 command-delimited intervals; 36*(4096+512).",
            "per_call_derivation": (
                "One process validation/application traversal; at most M+1 nonempty intervals; "
                "K position evaluations and at most 9K contact visits per interval. Each movement "
                "crosses each contact at most once; E<=9*(A+M)<=4608. Gcd normalizes reached "
                "noninteger roots only, with a 64-step guard. Insertion sort operates on <=36 "
                "interval edges: sum(n*(n-1)/2)<=floor((9K-1)*E/2). One committed copy per edge."),
        },
        "limits": [
            "Storage values are actual sizeof results on the recorded compiler/ABI; scratch payload follows the private member arrays in the hashed header.",
            "Compiler stack-frame bytes, arbitrary C/system allocation, other threads, locks and I/O are not observed by these hooks.",
            "The defensive arithmetic_overflow branch is not injected; it is unreachable for admitted inputs under the frozen arithmetic proof.",
            "These measured fixture counts and source-derived ceilings are not elapsed callback deadlines, host/device evidence, physical calibration or Engine integration.",
            "External child wall time covers a complete test executable and is not a callback duration.",
        ],
    }
    write_json(report_path, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generated = commands.add_parser("generate", help="write only a source-hashed scratch counter translation unit/header/map")
    generated.add_argument("--scratch-dir", type=Path, required=True)
    checked = commands.add_parser("verify", help="run both already-built fixtures, compare semantics, retain measured receipts")
    checked.add_argument("--manifest", type=Path, required=True)
    checked.add_argument("--normal-binary", type=Path, required=True)
    checked.add_argument("--instrumented-binary", type=Path, required=True)
    checked.add_argument("--build-evidence", type=Path, required=True)
    checked.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "generate":
            result = generate(args.scratch_dir)
            print(json.dumps({"generated_cpp": result["generated_cpp"], "anchors": len(result["anchors"])}))
        else:
            result = verify(args)
            print(json.dumps({"passed": result["passed"], "report": str(args.report), "calls_checked": result["calls_checked"]}))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(f"resource receipt failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
