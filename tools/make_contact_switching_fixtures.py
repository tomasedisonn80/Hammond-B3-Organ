#!/usr/bin/env python3
"""Materialize the predeclared synthetic M3 matrix in a new directory.

Authoring utility only; no Engine configuration or physical measurements.
The recipes are frozen in docs/CONTACT_SWITCHING_VALIDATION.md.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path


RATES = (44100, 48000, 96000)
ON = (.12, .22, .32, .42, .52, .62, .72, .82, .92)
OFF = (.04, .14, .24, .34, .44, .54, .64, .74, .84)


def fixture(number: int, rate: int) -> dict:
    if type(number) is not int or not 0 <= number < 12 or rate not in RATES:
        raise ValueError("expected fixture 0..11 and rate 44100/48000/96000")
    source = dict(source_id=7, frequency_hz=997.0, amplitude=1.0, phase_turns=.137)
    key = dict(key_id="A", press_seconds=.0004, release_seconds=.0006,
               on=list(ON), off=list(OFF), source_ids=[7] * 9,
               gains=[0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])
    keys = [key]
    gestures = [(0.0, "A", 1.0), (.0008, "A", 0.0)]
    host_gestures = None
    if number == 0:
        key["gains"] = [0.0] * 9
    elif number == 1:
        source.update(frequency_hz=0.0, phase_turns=.25)
    elif number in (2, 3):
        source["phase_turns"] = ((.25 if number == 2 else 0.0) - 997.0 * .000208) % 1.0
    elif number == 4:
        source["frequency_hz"] = .4 * rate
    elif number == 5:
        key["gains"] = [1.0 / 18.0] * 9
        second = copy.deepcopy(key)
        second.update(key_id="B", gains=[0.0, 0.0, 0.0, 0.0, .5, 0.0, 0.0, 0.0, 0.0])
        keys.append(second)
        gestures += [(.0001, "B", 1.0), (.0009, "B", 0.0)]
    elif number in (6, 7, 8):
        key["gains"] = [1.0 / 9.0] * 9
        gestures = {
            6: [(0.0, "A", .5), (.0016, "A", 0.0)],
            7: [(0.0, "A", 1.0), (.0006, "A", .5), (.0016, "A", 0.0)],
            8: [(0.0, "A", 1.0), (.00015, "A", 0.0), (.00024, "A", 1.0),
                (.00024, "A", 1.0), (.0012, "A", 0.0)],
        }[number]
    elif number == 9:
        key.update(press_seconds=1.0 / 2048.0, release_seconds=1.0 / 1024.0)
        key["on"][4], key["off"][4], key["gains"][4] = .5, .375, .5
        second = copy.deepcopy(key)
        second["key_id"], second["gains"][4] = "B", -.5
        keys.append(second)
        equality = 1.0 / 4096.0
        gestures = [(0.0, "A", 1.0), (0.0, "B", 1.0),
                    (equality, "A", 0.0), (equality, "A", 1.0),
                    (equality, "B", 1.0), (equality, "B", 0.0),
                    (.0012, "A", 0.0), (.0012, "B", 0.0)]
    elif number == 10:
        key.update(press_seconds=1.0 / 4096.0, release_seconds=1.0 / 2048.0)
        key["on"][4], key["off"][4] = .5, .375
        host_gestures = [(0.0, "A", .51), (64.25, "A", 0.0)]
    elif number == 11:
        key.update(press_seconds=12.0 / rate, release_seconds=16.0 / rate,
                   gains=[1.0 / 9.0] * 9)
        host_gestures = [(0.0, "A", 1.0), (256.0, "A", 0.0)]
    if host_gestures is None:
        host_gestures = [(seconds * rate, name, target) for seconds, name, target in gestures]
    targets = [dict(frame=math.floor(u), fraction=u - math.floor(u), key_id=name, target=target)
               for u, name, target in host_gestures]
    return dict(schema_version=1, model_id="fractional-contact-reference-v1",
                evidence_class="synthetic", fixture_id=f"F{number:02d}-{rate}-v1",
                sample_rate_hz=rate, frames=256, sources=[source], keys=keys, targets=targets)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="new directory in an existing parent")
    args = parser.parse_args()
    destination = args.output
    if not destination.parent.is_dir() or destination.exists() or destination.is_symlink():
        parser.error("output must be a new directory in an existing parent")
    payloads = {}
    for number in range(12):
        for rate in RATES:
            case = fixture(number, rate)
            payloads[case["fixture_id"] + ".json"] = (
                json.dumps(case, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    manifest = dict(schema_version=1, protocol_id="contact-switching-validation-v1",
                    evidence_class="synthetic", fixture_count=36,
                    files={name: dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
                           for name, raw in payloads.items()})
    destination.mkdir()
    for name, raw in payloads.items():
        (destination / name).write_bytes(raw)
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(output=str(destination), fixtures=36)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
