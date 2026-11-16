"""Pre-implementation synthetic cases for contact-grid conversion v1.

This standard-library-only module imports no converter, replay, or oracle.
``cases()`` returns fresh complete input dictionaries and frozen dispositions.
Required row fields are name, input, expected_status, expected_code_or_stage,
and reason. Optional expected_grid_fields carry independently known scalar
answers, using a descriptive path into grid_case. source_path identifies the
unchanged existing F09 witness. The associated manifest binds canonical input
bytes and all 36 original reference fixtures; no original fixture is rewritten.

The expectations concern the proposed trajectory certificate, not audio,
physical fidelity, native resources, or universal binary64/grid equivalence.
"""

from __future__ import annotations

from copy import deepcopy
import json
import math
from pathlib import Path


CORPUS_ID = "contact-grid-conversion-fixtures-v1"
REPOSITORY = Path(__file__).resolve().parents[2]
TICKS = 1 << 16
TRAVEL = 1 << 48


def _key(name: str = "A") -> dict:
    return {
        "key_id": name,
        "press_seconds": 1 / 2048,
        "release_seconds": 1 / 1024,
        "on": [(index + 1) / 16 for index in range(9)],
        "off": [(2 * index + 1) / 32 for index in range(9)],
        "source_ids": [46] * 9,
        "gains": [0.125] * 9,
    }


def _target(time: float, value: float, key: str = "A") -> dict:
    frame = math.floor(time)
    return {"frame": frame, "fraction": time - frame,
            "key_id": key, "target": value}


def _input(*, rate: int = 48000, frames: int = 128, key_count: int = 1) -> dict:
    return {
        "schema_version": 1,
        "model_id": "fractional-contact-reference-v1",
        "evidence_class": "synthetic",
        "fixture_id": "CGC-unassigned",
        "sample_rate_hz": rate,
        "frames": frames,
        "sources": [{"source_id": 46, "frequency_hz": 440.0,
                     "amplitude": 0.5, "phase_turns": 0.125}],
        "keys": [_key(chr(ord("A") + index)) for index in range(key_count)],
        "targets": [_target(0.0, 1.0), _target(64.0, 0.0)],
    }


def _quiet_key(key: dict) -> None:
    key["on"] = [0.75] * 9
    key["off"] = [0.25] * 9


def canonical_input_bytes(value: dict) -> bytes:
    """Manifest encoding only: sorted compact UTF-8 JSON with one final LF."""
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


def cases() -> list[dict]:
    result: list[dict] = []

    def add(name: str, document: dict, stage: str, reason: str,
            fields: dict | None = None, *, source_path: str | None = None) -> None:
        if source_path is None:
            document["fixture_id"] = "CGC-" + name
        row = {"name": name, "input": deepcopy(document),
               "expected_status": "accepted" if stage == "accepted" else "refused",
               "expected_code_or_stage": stage, "reason": reason}
        if fields is not None:
            row["expected_grid_fields"] = fields
        if source_path is not None:
            row["source_path"] = source_path
        result.append(row)

    for rate in (44100, 96000):
        add(f"ordinary-{rate}", _input(rate=rate), "accepted",
            "Separated dyadic contacts and ordinary press/release; the 96 kHz "
            "observation ends during release, so final partial travel is retained.")

    for parity, half_ticks, expected in (("even", 0.5, 32768),
                                        ("odd", 1.5, 32770)):
        value = _input()
        value["targets"][0] = _target(0.5 + half_ticks / TICKS, 1.0)
        add(f"time-midpoint-{parity}", value, "accepted",
            "Exact half-tick rounds to the even integer, with no collision or "
            "event equality at the shifted start.", {"targets[0].tick": expected})

    for parity, half_units, expected in (("even", 0.5, TRAVEL // 2),
                                        ("odd", 1.5, TRAVEL // 2 + 2)):
        value = _input()
        _quiet_key(value["keys"][0])
        value["targets"] = [_target(0.0, 0.5 + half_units / TRAVEL)]
        add(f"target-midpoint-{parity}", value, "accepted",
            "Interior target midpoint has no distinct threshold at its rounded "
            "value; complete arrival and hold are certified.",
            {"targets[0].position": expected})

    for parity, half_units, increment in (("even", 0.5, 0), ("odd", 1.5, 2)):
        value = _input()
        key = value["keys"][0]
        key["on"] = [0.75] * 9
        key["off"] = [0.125] * 9
        key["on"][0] = 0.5 + half_units / TRAVEL
        key["off"][0] = 0.25 + half_units / TRAVEL
        add(f"threshold-midpoint-{parity}", value, "accepted",
            "Independent make/break midpoints exercise even and odd integer "
            "parity without a per-key collision.",
            {"keys[0].contacts[0].on": TRAVEL // 2 + increment,
             "keys[0].contacts[0].off": TRAVEL // 4 + increment})

    value = _input()
    _quiet_key(value["keys"][0])
    value["keys"][0]["on"][0] = 0.5
    value["targets"] = [_target(0.0, 0.5 - 2.0 ** -54)]
    add("reviewed-target-threshold", value, "position_collision",
        "Distinct target 1/2-2^-54 and make 1/2 map to Q/2, turning an "
        "unreachable make into a reached threshold if admitted.")

    value = _input()
    _quiet_key(value["keys"][0])
    value["keys"][0]["off"][0] = 0.5
    value["keys"][0]["on"][0] = 0.5 + 2.0 ** -53
    add("reviewed-hysteresis-collapse", value, "grid_domain",
        "Positive source hysteresis rounds to off==on; grid-domain refusal "
        "precedes the general position-collision stage.")

    value = _input(frames=1)
    value["targets"] = [_target(0.5 - 2.0 ** -18, 1.0),
                         _target(0.5 + 2.0 ** -18, 0.0)]
    add("reviewed-time-collision", value, "time_collision",
        "The exact reviewed 1/2 +/- 2^-18 frame pair both map to tick 32768.")

    value = _input()
    _quiet_key(value["keys"][0])
    value["keys"][0]["on"][0] = 0.5 + 2.0 ** -53
    value["keys"][0]["on"][1] = 0.5
    add("reviewed-threshold-order", value, "position_collision",
        "Contact 1 precedes contact 0 before rounding; distinct make thresholds "
        "would become one equality group, so scalar admission refuses first.")

    original = "data/contact-switching/reference-v1/F09-48000-v1.json"
    value = json.loads((REPOSITORY / original).read_bytes())
    add("reviewed-f09-equality", value, "event_order",
        "The unchanged F09 contact-4 make equals command 375/32 in the source; "
        "the grid make is 7/2932031008 frames earlier despite final-bit agreement.",
        source_path=original)

    value = _input(frames=2, key_count=2)
    value["targets"] = [_target(1.0 - 2.0 ** -18, 1.0, "A"),
                         _target(1.0 + 2.0 ** -18, 1.0, "B")]
    add("cross-key-frame-boundary-collision", value, "time_collision",
        "Different keys on opposite sides of frame 1 collide at its tick; "
        "whole-epoch conversion must detect what per-block conversion can hide.")

    value = _input()
    value["targets"] = [_target(0.0, math.ulp(0.0))]
    add("positive-subnormal-target", value, "position_collision",
        "The smallest positive binary64 target collides with implicit initial "
        "zero; it cannot silently become a no-op.")

    value = _input()
    value["targets"] = [_target(0.0, math.nextafter(1.0, 0.0))]
    add("target-full-travel-collision", value, "position_collision",
        "The distinct predecessor of 1 rounds to Q and collides with the "
        "implicit full-travel endpoint even without a threshold at 1.")

    value = _input()
    value["keys"][0]["off"][0] = math.ulp(0.0)
    add("subnormal-break-threshold", value, "position_collision",
        "A positive subnormal break threshold maps to implicit zero while "
        "off<on remains valid; topology must not redefine that endpoint.")

    value = _input(frames=1)
    value["targets"] = [_target(2.0 ** -18, 1.0)]
    add("interior-time-to-start", value, "time_collision",
        "A strictly interior quarter-tick command cannot be rounded onto 0.")

    value = _input(frames=1)
    value["targets"] = [_target(1.0 - 2.0 ** -18, 1.0)]
    add("interior-time-to-close", value, "time_collision",
        "A strictly interior quarter-tick-before-N command cannot become "
        "closure-only at N.")

    value = _input(key_count=2)
    value["keys"][1]["gains"] = [-0.125] * 9
    value["targets"] = [_target(0.0, 1.0, "B"), _target(0.0, 1.0, "A"),
                         _target(32.0, 0.0, "A"), _target(32.0, 1.0, "A"),
                         _target(32.0, 0.0, "B"), _target(32.0, 1.0, "B")]
    add("tied-caller-order-shared-cancel", value, "accepted",
        "Tied caller changes and independent shared-source histories survive "
        "even when equal signed gains cancel audio; zero-time reversals travel nowhere.")

    value = _input()
    value["targets"] = [_target(0.0, 1.0), _target(7.0, 1.0),
                         _target(14.0, 1.0), _target(64.0, 0.0)]
    add("repeated-target-anchor", value, "accepted",
        "Repeated targets before arrival are quota-visible commands and retain "
        "the persistent motion anchor instead of restarting travel.")

    value = _input()
    value["targets"] = [_target(0.0, 0.375), _target(32.0, 0.875),
                         _target(64.0, 0.0)]
    add("partial-arrival-and-hold", value, "accepted",
        "Partial targets reach/hold before retargeting; an existing make/target "
        "equality remains an edge-arrival tie in both exact models.")

    value = _input()
    value["targets"] = [_target(0.0, 1.0), _target(4.0, 0.0),
                         _target(6.0, 1.0), _target(12.0, 0.25),
                         _target(20.0, 0.625)]
    add("incomplete-return-reversal", value, "accepted",
        "Repress during incomplete return preserves position and hysteresis; "
        "later partial holds exercise propagated anchors.")

    value = _input()
    value["targets"] = [_target(0.0, 1.0), _target(375 / 16, 0.0)]
    add("arrival-command-equality", value, "event_order",
        "Source full-travel arrival at 375/16 exactly equals a release command; "
        "rounded positive speed reaches slightly earlier, losing that equality.")

    value = _input(frames=375)
    value["keys"][0]["press_seconds"] = 1 / 128
    value["targets"] = [_target(0.0, 1.0)]
    add("arrival-at-observation-end", value, "event_identity",
        "Source reaches 1 exactly at N=375; rounded speed is smaller, so the "
        "grid has no reached-target arrival inside the closed observation.")

    value = _input(frames=375)
    _quiet_key(value["keys"][0])
    value["keys"][0]["on"][0] = 0.5
    value["keys"][0]["press_seconds"] = 1 / 64
    value["targets"] = [_target(0.0, 1.0)]
    add("edge-at-observation-end", value, "event_identity",
        "Source make at N=375 is included; a slightly smaller rounded speed "
        "moves it beyond N, changing the edge set before any error-budget test.")

    value = _input()
    value["targets"] = [_target(0.0, 1.0), _target(375 / 32, 0.5)]
    add("dynamic-arrived-target-direction", value, "dynamic_topology",
        "At 375/32 source position equals the new target while grid position "
        "is larger; source holds and grid releases, preceding event-order refusal.")

    value = _input(rate=96000, frames=4096)
    _quiet_key(value["keys"][0])
    value["keys"][0]["press_seconds"] = 1.0
    value["keys"][0]["on"][0] = 1 / 32
    value["keys"][0]["off"][0] = 1 / 64
    value["targets"] = [_target(0.0, 1.0)]
    add("root-budget-slow-travel", value, "root_budget",
        "The source root at 3000 frames and its matched grid root preserve "
        "topology but differ by over 2^-10 frames; position stays below 2^-18.")

    for changes, name, stage in ((2, "position-budget-below", "accepted"),
                                 (8, "position-budget-above", "position_budget")):
        value = _input(rate=44100, frames=4)
        key = value["keys"][0]
        key["press_seconds"] = key["release_seconds"] = 0.0001
        key["on"] = [0.875] * 9
        key["off"] = [0.125] * 9
        delta = 1 / (4 * TICKS)
        value["targets"] = [_target(0.0, 1.0)] + [
            _target(2.0 + index / 8 + (-delta if index % 2 == 0 else delta),
                    0.0 if index % 2 == 0 else 1.0)
            for index in range(changes)
        ]
        add(name, value, stage,
            "Quarter-tick rounding biases alternating short moves without "
            "crossing contacts or reaching targets; the two- versus eight-change "
            "cases bracket the continuous 2^-18 position limit.")

    value = _input(frames=0)
    value["targets"] = []
    add("empty-epoch", value, "accepted",
        "N=0 retains both equal boundary labels, no edges/arrivals and no "
        "process partition; initial contacts stay open.", {"frames": 0})

    value = _input(frames=0)
    value["targets"] = [_target(0.0, 1.0), _target(0.0, -0.0),
                         _target(0.0, 0.5)]
    add("zero-frame-closure-ties", value, "accepted",
        "Closure-only tied targets have no travel or instantaneous arrival; "
        "original input admission canonicalizes signed zero.",
        {"targets[1].position": 0, "targets[2].position": TRAVEL // 2})

    value = _input()
    tiny = math.ulp(0.0)
    value["sources"][0].update(frequency_hz=tiny, amplitude=tiny, phase_turns=tiny)
    value["keys"][0]["gains"] = [-tiny, tiny] + [0.0] * 7
    add("subnormal-canonical-sidecar", value, "accepted",
        "Permitted source/gain/phase subnormals survive canonical binary64 "
        "sidecar encoding; silent or muted routes still retain every contact.")

    value = _input(frames=0)
    value["targets"] = [_target(0.0, 0.0) for _ in range(512)]
    add("maximum-command-noops", value, "accepted",
        "All 512 supplied tied no-ops count and remain separately labeled; "
        "none is deduplicated despite an unchanged final state.")

    value = _input(key_count=4)
    value["targets"] = [_target(0.0, 1.0, name) for name in ("D", "B", "A", "C")]
    for index, key in enumerate(value["keys"]):
        key["gains"] = [0.0 if index % 2 else 0.125] * 9
    add("four-key-independent-ties", value, "accepted",
        "All four keys share one source and equal travel but keep 36 independent "
        "contact identities, including two wholly muted keys and caller order.")

    assert len(result) == 35
    assert len({row["name"] for row in result}) == len(result)
    return result
