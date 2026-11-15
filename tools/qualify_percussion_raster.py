#!/usr/bin/env python3
"""Compare genuine historical/current deterministic percussion raster helpers.

Compile the same native test harness separately with the historical and current
UiModel/InstrumentView sources. This tool does not build, modify sources, or
substitute a reconstructed baseline. One pair of RGBA frames is held at a time;
only metadata, hashes and measured differences are retained.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(executable: Path, *arguments: str) -> bytes:
    result = subprocess.run([str(executable), *arguments], capture_output=True, timeout=45)
    if result.returncode:
        raise ValueError(f"{executable.name} {arguments}: exit {result.returncode}: "
                         f"{result.stderr.decode('utf-8', errors='replace')[:4096]}")
    if result.stderr:
        raise ValueError(f"Unexpected helper stderr: {result.stderr[:4096]!r}")
    return result.stdout


def frame(executable: Path, index: int) -> tuple[dict, bytes]:
    payload = run(executable, "--case", str(index))
    boundary = payload.find(b"\n", 0, 16384)
    if boundary < 0:
        raise ValueError("Missing bounded frame header")
    header = json.loads(payload[:boundary])
    if not isinstance(header, dict) or header.get("schema") != 1 or header.get("case") != index:
        raise ValueError("Wrong frame schema or index")
    width, height = header.get("width"), header.get("height")
    if type(width) is not int or type(height) is not int or not (1 <= width <= 3900 and 1 <= height <= 2200):
        raise ValueError("Frame dimensions exceed the declared memory bound")
    pixels = payload[boundary + 1:]
    if len(pixels) != width * height * 4 or header.get("bytes") != len(pixels):
        raise ValueError("Frame byte count mismatch or unexpected trailing data")
    if type(header.get("active")) is not bool or header.get("scale") not in (1, 1.5, 2):
        raise ValueError("Invalid active flag or drawable scale")
    regions = header.get("regions")
    if not isinstance(regions, list) or not (13 <= len(regions) <= 15):
        raise ValueError("Unexpected region inventory")
    for rectangle in regions:
        if not isinstance(rectangle, list) or len(rectangle) != 4 or any(
                type(value) not in (int, float) or not math.isfinite(value) for value in rectangle):
            raise ValueError("Malformed permitted rectangle")
        if rectangle[2] <= 0 or rectangle[3] <= 0:
            raise ValueError("Empty permitted rectangle")
    return header, pixels


def compare(before: tuple[dict, bytes], after: tuple[dict, bytes]) -> dict:
    old, old_bytes = before
    new, new_bytes = after
    if {k: v for k, v in old.items() if k != "regions"} != {
            k: v for k, v in new.items() if k != "regions"}:
        raise ValueError("Historical/current fixture, state selection or coordinate mismatch")
    size = new["width"], new["height"]
    old_image = Image.frombytes("RGBA", size, old_bytes)
    new_image = Image.frombytes("RGBA", size, new_bytes)
    channels = ImageChops.difference(old_image, new_image).split()
    difference = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]),
                                    ImageChops.lighter(channels[2], channels[3]))
    changed = difference.point(lambda value: 255 if value else 0)
    allowed = Image.new("L", size, 0)
    if new["active"]:
        draw = ImageDraw.Draw(allowed)
        # Frozen admission: precisely the old/new tablets, captions, value/focus
        # ink and heading/eligibility rectangles, with one outward device pixel.
        # Pixel centers x+0.5 must be in [left-1, right+1); enclosing
        # integer rectangles must not add a further half-pixel allowance.
        # No whole-panel masks or post hoc exceptions are admitted.
        for x, y, width, height in old["regions"] + new["regions"]:
            scale, offset = new["scale"], new["offset"]
            left = math.ceil(x * scale + offset - 1.5)
            top = math.ceil(y * scale + offset - 1.5)
            right = math.ceil((x + width) * scale + offset + 0.5)
            bottom = math.ceil((y + height) * scale + offset + 0.5)
            draw.rectangle((left, top, right - 1, bottom - 1), fill=255)
    escaped = ImageChops.subtract(changed, allowed)
    changed_count = changed.histogram()[255]
    escaped_count = escaped.histogram()[255]
    nonvacuous = not new["active"] or new["fixture"][-1] != 0 or changed_count > 0
    return {
        "case": new["case"], "fixture": new["fixture"], "scale": new["scale"],
        "size": list(size), "active": new["active"], "compared_pixels": size[0] * size[1],
        "before_rgba_sha256": hashlib.sha256(old_bytes).hexdigest(),
        "after_rgba_sha256": hashlib.sha256(new_bytes).hexdigest(),
        "changed_pixels": changed_count, "difference_bounds": changed.getbbox(),
        "escaped_pixels": escaped_count, "escaped_bounds": escaped.getbbox(),
        "nonvacuous": nonvacuous, "passed": escaped_count == 0 and nonvacuous,
        "before_regions": old["regions"], "after_regions": new["regions"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--baseline-commit", required=True)
    parser.add_argument("--output", required=True, type=Path, help="new JSON report; never replaced")
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error("output already exists; choose a new report path")
    if not re.fullmatch(r"[0-9a-f]{40}", args.baseline_commit):
        parser.error("baseline commit must be an exact lowercase 40-hex commit")
    before, after, repo = args.before.resolve(strict=True), args.after.resolve(strict=True), args.repo.resolve(strict=True)
    started = time.monotonic()
    report = {
        "schema": 1, "qualification": "percussion-identical-state-paired-raster-v1",
        "status": "failed", "baseline_commit": args.baseline_commit,
        "before_executable": {"path": str(before), "sha256": digest(before)},
        "after_executable": {"path": str(after), "sha256": digest(after)},
        "tool_sha256": digest(Path(__file__)),
        "source_sha256": {}, "baseline_source_sha256": {}, "cases": [],
        "build_attestation": "Compile provenance is a separate caller-retained receipt; hashes alone do not prove compilation.",
        "mask_policy": "Union of contracted old/new rectangles, expanded exactly1 physical pixel using pixel centers; inactive mask is empty.",
        "limits": "Fixed copied state, SDL software surfaces; no native display, audio device or whole-interface 1:1 claim.",
    }
    error = None
    try:
        for path in ("apps/standalone/UiModel.cpp", "apps/standalone/InstrumentView.cpp",
                     "apps/standalone/UiModel.h", "apps/standalone/InstrumentView.h",
                     "apps/standalone/Drawing.cpp", "apps/standalone/Drawing.h", "apps/standalone/FontData.h",
                     "apps/standalone/InspectionModel.cpp", "apps/standalone/InspectionModel.h"):
            historical = subprocess.check_output(["git", "show", f"{args.baseline_commit}:{path}"], cwd=repo)
            report["baseline_source_sha256"][path] = hashlib.sha256(historical).hexdigest()
            report["source_sha256"][path] = digest(repo / path)
            if path not in ("apps/standalone/UiModel.cpp", "apps/standalone/InstrumentView.cpp") and historical != (repo / path).read_bytes():
                raise ValueError(f"Common source/ABI changed: {path}")
        harness = "apps/standalone/native_tests/test_standalone_percussion_raster.cpp"
        report["source_sha256"][harness] = digest(repo / harness)
        count_before, count_after = json.loads(run(before, "--list")), json.loads(run(after, "--list"))
        if count_before != count_after or count_after.get("schema") != 1 or type(count_after.get("cases")) is not int:
            raise ValueError("Mismatched case inventory")
        count = count_after["cases"]
        if count != 66:
            raise ValueError("Expected the frozen 66-case orthogonal inventory")
        for index in range(count):
            report["cases"].append(compare(frame(before, index), frame(after, index)))
            if index % 10 == 9:
                print(f"Compared {index + 1}/{count} identical-state pairs", flush=True)
        if digest(before) != report["before_executable"]["sha256"] or digest(after) != report["after_executable"]["sha256"]:
            raise ValueError("Helper executable changed during qualification")
        if any(digest(repo / p) != sha for p, sha in report["source_sha256"].items()):
            raise ValueError("Candidate/common source changed during qualification")
        report["status"] = "passed" if all(row["passed"] for row in report["cases"]) else "failed"
    except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        error = str(exc)
    report["error"] = error
    report["elapsed_seconds"] = time.monotonic() - started
    report["totals"] = {
        "pairs": len(report["cases"]),
        "compared_pixels": sum(c["compared_pixels"] for c in report["cases"]),
        "changed_pixels": sum(c["changed_pixels"] for c in report["cases"]),
        "escaped_pixels": sum(c["escaped_pixels"] for c in report["cases"]),
        "identical_inactive_pairs": sum(not c["active"] and c["changed_pixels"] == 0 for c in report["cases"]),
        "failed_pairs": sum(not c["passed"] for c in report["cases"]),
    }
    with args.output.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(report, output, indent=2, allow_nan=False)
        output.write("\n")
    print(json.dumps({"status": report["status"], "error": error, **report["totals"]}))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
