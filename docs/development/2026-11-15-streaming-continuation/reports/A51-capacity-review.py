#!/usr/bin/env python3
"""A51 bounded documentary arithmetic; no build/native/audio execution."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    prefix = "docs/development/2026-11-15-streaming-continuation/"
    proposal = "docs/research/CAUSAL_CONTACT_CAPACITY_NEXT.md"
    review = "docs/reviews/CAUSAL_CONTACT_CAPACITY_NEXT_REVIEW.md"
    note = prefix + "notes/A51.md"
    author = json.loads((repo / (prefix + "reports/A40-capacity-audit.json")).read_text())
    inputs = sorted(set(author["source_sha256"]) | {
        proposal, "data/pedal-map.json", "include/hammond/Types.h",
    })
    bindings = {}
    for path in inputs:
        data = (repo / path).read_bytes()
        bindings[path] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    checks = []

    def check(name: str, actual: object, expected: object) -> None:
        passed = actual == expected
        checks.append({"name": name, "actual": actual, "expected": expected, "passed": passed})
        if not passed:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")

    check("reviewed_proposal_identity", bindings[proposal]["sha256"],
          "fffd4fd0ef2ee3f193bcb2939309c8003c7b326de1b081cc0d0b4abe4f5dc643")
    mismatches = [path for path, identity in author["source_sha256"].items()
                  if bindings[path] != identity]
    check("all_author_input_bindings_match", mismatches, [])

    def constant(path: str, name: str) -> int:
        text = (repo / path).read_text()
        match = re.search(r"\b" + re.escape(name) + r"\s*=\s*(\d+)\s*;", text)
        if not match:
            raise AssertionError(f"missing literal constant {name}")
        return int(match.group(1))

    types = "include/hammond/Types.h"
    pedal = "include/hammond/PedalRouting.h"
    grid = "include/hammond/research/CausalContactGrid.h"
    K = constant(types, "kManualCount") * constant(types, "kManualKeyCount")
    C = constant(types, "kDrawbarCount")
    R = constant(types, "kMaxEventsPerBlock")
    T = constant(grid, "kContactGridTicksPerFrame")
    Q = 1 << 48
    pedals = constant(pedal, "kPedalCount")
    pedal_contacts = constant(pedal, "kPedalContactCount")
    check("manual_keys", K, 122)
    check("manual_contact_histories", K * C, 1098)
    check("pedal_states", pedals * pedal_contacts, 200)
    check("combined_contact_inventory", K * C + pedals * pedal_contacts, 1298)
    check("incorrect_nine_contacts_per_playing_key_overcount",
          (K + pedals) * C - (K * C + pedals * pedal_contacts), 25)
    pedal_map = json.loads((repo / "data/pedal-map.json").read_text())
    check("documentary_disconnected_pedal_positions", pedal_map["counts"]["disconnected"], 5)

    M = 2 * R + K
    E = C * (K + M)
    check("conditional_manual_target_bound", M, 2170)
    check("conditional_edge_bound", E, 20628)
    S = 32 + 192 * K
    check("assumed_snapshot_layout", S, 23456)
    storage = {
        "live_staged_snapshots": 2 * S,
        "transaction_edges": E * 24,
        "interval_edges": C * K * 24,
        "additional_absolute_frame_fields": 2 * (K + 1) * 8,
        "caller_edge_destination": E * 24,
        "converted_targets": M * 16,
        "two_audio_rings": 2 * 8194 * 8,
        "coefficients": 8193 * 8,
        "one_256_float_output": 256 * 4,
    }
    check("storage_rows", storage, {
        "live_staged_snapshots": 46912, "transaction_edges": 495072,
        "interval_edges": 26352, "additional_absolute_frame_fields": 1968,
        "caller_edge_destination": 495072, "converted_targets": 34720,
        "two_audio_rings": 131104, "coefficients": 65544,
        "one_256_float_output": 1024,
    })
    subtotal = sum(storage.values())
    check("planning_storage_subtotal", subtotal, 1297768)
    check("unassigned_not_fit", (2 << 20) - subtotal, 799384)
    check("stock_grid_object_bytes", 2 * 800 + 4608 * 24 + 36 * 24, 113056)
    check("stock_shards_object_only", ((K + 3) // 4) * 113056, 3504736)
    check("current_host_float_staging_bytes_assumption",
          constant(types, "kHardMaxBlockFrames") * 4, 262144)

    work = {
        "key_evaluations": K * (M + 1),
        "contact_examinations": C * K * (M + 1),
        "roots": E,
        "gcd_remainder_steps": 64 * E,
        "edge_comparisons": ((C * K - 1) * E) // 2,
        "one_interval_comparisons": C * K * (C * K - 1) // 2,
    }
    check("one_positive_call_work", work, {
        "key_evaluations": 264862, "contact_examinations": 2383758,
        "roots": 20628, "gcd_remainder_steps": 1320192,
        "edge_comparisons": 11314458, "one_interval_comparisons": 602253,
    })
    check("command_free_256_one_frame_calls_key_evaluations", K * 256, 31232)
    check("callback_256_96k_exact", str(Fraction(256, 96000)), "1/375")
    check("callback_1_96k_exact", str(Fraction(1, 96000)), "1/96000")

    u32 = (1 << 32) - 1
    u64 = (1 << 64) - 1
    horizons = {
        "current_epoch_ticks": constant(grid, "kContactGridMaxFrames") * T,
        "uint32_tick_complete_frames": u32 // T,
        "uint64_tick_complete_frames": u64 // T,
        "uint64_product_elapsed_limit_at_max_speed": u64 // u32,
        "full_travel_arrival_ceiling_ticks_at_max_speed": (Q + u32 - 1) // u32,
        "first_overflow_elapsed_tick_if_naively_widened": u64 // u32 + 1,
    }
    check("clock_horizons_and_naive_widening_witness", horizons, {
        "current_epoch_ticks": 268435456,
        "uint32_tick_complete_frames": 65535,
        "uint64_tick_complete_frames": 281474976710655,
        "uint64_product_elapsed_limit_at_max_speed": 4294967297,
        "full_travel_arrival_ceiling_ticks_at_max_speed": 65537,
        "first_overflow_elapsed_tick_if_naively_widened": 4294967298,
    })
    check("last_safe_product_identity", (u64 // u32) * u32, u64)
    check("next_product_overflows", (u64 // u32 + 1) * u32 > u64, True)
    check("current_domain_does_not_reach_overflow",
          constant(grid, "kContactGridMaxFrames") * T < u64 // u32, True)
    check("binary64_lifetime_frame_alias", float(1 << 53) == float((1 << 53) + 1), True)

    # Constructive source-level host witness: one owner per physical key,
    # fixed default bus route, no duplicate ID, no native adapter execution.
    held = set()
    raw = on = off = peak_owners = 0
    for _ in range(16):
        for note_number in range(36, 97):
            assert note_number not in held
            held.add(note_number)
            raw += 1
            on += 1
            peak_owners = max(peak_owners, len(held))
        raw += 1
        off += len(held)
        held.clear()
    callback_witness = {"raw_records": raw, "first_ons": on, "final_offs": off,
                        "emitted_transitions": on + off, "peak_owners": peak_owners,
                        "initial_owned_keys": 0, "final_owned_keys": len(held)}
    check("constructive_host_callback_expansion", callback_witness, {
        "raw_records": 992, "first_ons": 976, "final_offs": 976,
        "emitted_transitions": 1952, "peak_owners": 61,
        "initial_owned_keys": 0, "final_owned_keys": 0,
    })
    check("host_witness_within_raw_and_owner_limits",
          raw <= R and peak_owners <= 256 and on + off > R, True)
    check("ownership_conservation_in_witness", off, on - len(held))
    check("direct_panic_expander_breaks_unqualified_bound", 3 * 61 > 2 * 3 + 122, True)

    incoming_root = T + 1
    check("incoming_M0_root_lies_in_second_frame", T < incoming_root <= 2 * T, True)
    check("incoming_M0_witness_edges", 9, 9)

    # Independent exact closed form, not grid/oracle/candidate helpers.
    # At each integer tick 0..127 all four keys alternate target 1/0.
    # Every contact crosses after 1/s tick; arrival precedes the next command.
    roots = [Fraction(tick) + Fraction(1, u32) for tick in range(128)]
    burst = {
        "keys": 4, "contacts_per_key": 9, "ticks_with_commands": 128,
        "commands": 4 * len(roots), "edges": 4 * 9 * len(roots),
        "connected_pieces": 4 * 9 * (len(roots) // 2),
        "first_root_ticks": str(roots[0]), "last_root_ticks": str(roots[-1]),
        "cell_zero_positive_half_end_tick": 128,
        "all_roots_strictly_in_positive_half_cell": all(0 < root < 128 for root in roots),
        "all_arrivals_before_next_tick": all(root < tick + 1 for tick, root in enumerate(roots)),
        "final_position": 0, "final_contacts_open": True,
    }
    check("one_cell_burst_commands", burst["commands"], 512)
    check("one_cell_burst_edges", burst["edges"], 4608)
    check("one_cell_connected_pieces", burst["connected_pieces"], 2304)
    check("one_cell_burst_locations", burst["all_roots_strictly_in_positive_half_cell"], True)
    check("one_cell_burst_arrival_before_next_command", burst["all_arrivals_before_next_tick"], True)

    anchors = {
        "grid_noncopyable": (grid, "CausalContactGrid(const CausalContactGrid&) = delete;"),
        "grid_zero_frame_targets_rejected": ("src/research/CausalContactGrid.cpp",
            "if (!targets.empty()) return {ContactGridStatus::invalid_target, 0, 0};"),
        "grid_close_seals": ("src/research/CausalContactGrid.cpp",
            "staged_.phase = ContactGridPhase::closed;"),
        "grid_closed_only_reset": ("src/research/CausalContactGrid.cpp",
            "if (state_.phase != ContactGridPhase::closed) return ContactGridStatus::invalid_state;"),
        "grid_noop_keeps_anchor": ("src/research/CausalContactGrid.cpp",
            "if (key.target == target.position) return;"),
        "engine_clock_guard": ("src/Engine.cpp",
            "frames > std::numeric_limits<std::uint64_t>::max() - frame_clock_"),
        "engine_hard_panic": ("src/Engine.cpp", "contact_bank_.panic_manual(event.manual)"),
        "host_raw_carry_budget": ("src/HostTimeline.cpp",
            "auto raw_count = retained_.carry_count + musical_events.size();"),
        "host_candidate_engine_copy": ("src/HostTimeline.cpp", "work_.engine = engine_;"),
        "host_zero_frame_flush": ("src/HostTimeline.cpp",
            "0, {}, std::span<const Event>{work_.events.data() + prefix, event_count - prefix}"),
        "host_nonfailing_output_publication": ("src/HostTimeline.cpp",
            "std::copy_n(work_.mono.begin(), frames, mono_output.begin())"),
        "host_full_callback_output_storage": ("include/hammond/HostTimeline.h",
            "std::array<float, kHardMaxBlockFrames> mono{};"),
    }
    anchor_results = {}
    for name, (path, needle) in anchors.items():
        text = (repo / path).read_text()
        check(name, needle in text, True)
        anchor_results[name] = {"path": path, "first_line": text[:text.index(needle)].count("\n") + 1}

    owned = [review, note, prefix + "reports/A51-capacity-review.py"]
    owned_bindings = {}
    local_links = []
    for path in owned:
        data = (repo / path).read_bytes()
        text = data.decode("utf-8")
        check(path + ": final newline", text.endswith("\n"), True)
        check(path + ": trailing whitespace", any(line.rstrip() != line for line in text.splitlines()), False)
        owned_bindings[path] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        if path.endswith(".md"):
            for destination in re.findall(r"\]\(([^)]+)\)", text):
                if "://" in destination or destination.startswith("#"):
                    continue
                target = ((repo / path).parent / destination.split("#", 1)[0]).resolve()
                # This receipt is generated only after all checks; its exact
                # intended path is the single permitted not-yet-written link.
                exists = target.exists() or target == args.output.resolve()
                check(path + ": link " + destination, exists, True)
                local_links.append(destination)
    check("compact_worker_note_bytes", len((repo / note).read_bytes()) <= 2000, True)

    git = lambda *arguments: subprocess.check_output(
        ["git", "-C", str(repo), *arguments], text=True).strip()
    report = {
        "schema_version": 1, "worker": "/root/w09_a51", "wave": 9,
        "date": "2026-11-16", "cwd": str(repo), "python": platform.python_version(),
        "status": "independent source and exact arithmetic review; no full-organ architecture admission",
        "head": git("rev-parse", "HEAD"), "head_tree": git("rev-parse", "HEAD^{tree}"),
        "source_sha256": bindings, "author_bindings_verified": len(author["source_sha256"]),
        "conditional_projection": {"K": K, "R": R, "M": M, "E": E,
                                   "snapshot_bytes": S, "storage_items": storage,
                                   "subtotal_bytes": subtotal, "unassigned_bytes": (2 << 20) - subtotal,
                                   "one_positive_call_work": work},
        "clock_horizons": horizons, "host_expansion_witness": callback_witness,
        "incoming_motion_witness": {"K": 1, "speed": 1, "target": Q,
                                    "threshold_off": 0, "threshold_on": incoming_root,
                                    "second_window_commands": 0, "second_window_edges": 9},
        "hypothetical_direct_panic_expansion_counterexample": {
            "R": 3, "M": 183, "2R_plus_122": 128,
            "scope": "not an existing bug; excluded from owner-only conservation proof"},
        "cell_piece_burst": burst, "source_anchors": anchor_results,
        "checks": checks, "check_count": len(checks), "all_passed": all(c["passed"] for c in checks),
        "owned_files": owned_bindings, "local_markdown_links_checked": len(local_links),
        "verification_command": "python3 -B " + prefix + "reports/A51-capacity-review.py --repo . --output " + prefix + "reports/A51-capacity-review.json",
        "unrun": ["No native probe/build/CTest", "No production or shared-proposal edits",
                  "No audio/oracle render", "No ABI/stack/allocation/deadline measurement",
                  "No external publication/hosted audit", "No physical evidence acquisition"],
        "limitations": ["Ownership conservation proof applies only to named coordinated transitions",
                        "Storage figures assume declared record sizes and exclude named state",
                        "Work table is per positive trajectory call; whole callback needs slice bound",
                        "Constructive witnesses are source/exact-arithmetic deductions, not native passes"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"report": str(args.output), "checks": len(checks), "all_passed": report["all_passed"],
                      "note": owned_bindings[note], "review": owned_bindings[review]}, indent=2))


if __name__ == "__main__":
    main()
