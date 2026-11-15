#!/usr/bin/env python3
"""Freeze, then apply, the independently declared wide-composition raster mask.

This developer utility compares genuine historical/current native executables;
it never builds either side or reconstructs a baseline picture. Pillow is used
only for bounded pixel accounting. Run --freeze before any --case comparison,
then run without --freeze against that immutable, source-bound JSON mask.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import struct
import subprocess
import sys
import tempfile
import time

from PIL import Image, ImageChops, ImageDraw, __version__ as PILLOW_VERSION

from qualify_percussion_raster import frame, run


MODEL = "whole-reference-identical-state-raster-v1"
BASE = "33fa95d51e44234eef47ee21c03d29b2b311a5ee"
CONTRACT = "docs/WHOLE_REFERENCE_LAYOUT_CONTRACT.md"
CONTRACT_SHA = "55cc841d10dc65004cbfcca83d0fb84dcf54dda779e1d82a376534e2650b730f"
SESSION = "docs/development/2026-11-15-execution-continuation"
HARNESS = "apps/standalone/native_tests/test_standalone_percussion_raster.cpp"
SOURCE_PATHS = tuple(f"apps/standalone/{name}{suffix}"
                     for name in ("UiModel", "InstrumentView", "Drawing", "InspectionModel")
                     for suffix in (".cpp", ".h")) + (
    "apps/standalone/FontData.h", "docs/design/atlas-cover-reference.jpg",
    "docs/design/atlas-reference.json", HARNESS)
MUTABLE_SOURCE_PATHS = {
    "apps/standalone/UiModel.cpp", "apps/standalone/UiModel.h",
    "apps/standalone/InstrumentView.cpp", HARNESS,
}


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def write_new(path: Path, value: dict) -> None:
    """Publish a complete file exclusively, preserving any competing destination."""
    require(path.parent.is_dir(), "output parent must already exist")
    require(not path.exists() and not path.is_symlink(), "output already exists")
    payload = (json.dumps(value, indent=2, allow_nan=False) + "\n").encode()
    require(len(payload) <= 4 * 1024 * 1024, "bounded report exceeds 4 MiB")
    descriptor, temporary = tempfile.mkstemp(prefix=".raster-", suffix=".tmp", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


class F32(float):
    """Reproduce only the old allocation's declared binary32 arithmetic."""

    def __new__(cls, value: float):
        return float.__new__(cls, struct.unpack("f", struct.pack("f", value))[0])

    def __add__(self, other):
        return F32(float(self) + float(other))

    __radd__ = __add__

    def __sub__(self, other):
        return F32(float(self) - float(other))

    def __rsub__(self, other):
        return F32(float(other) - float(self))

    def __mul__(self, other):
        return F32(float(self) * float(other))

    __rmul__ = __mul__

    def __truediv__(self, other):
        return F32(float(self) / float(other))


def rect(x, y, width, height):
    return [float(x), float(y), float(x + width), float(y + height)]


def fixture_cases() -> list[dict]:
    """Independent literal copy of the admitted 66-state fixture inventory."""
    result = []

    def add(w=1672, h=941, scale=1, values=0, focus=0, route=0,
            pending=False, presentation=0, workspace=0, clip=0):
        offset = 7 if clip else 0
        active = w >= 1400 and h >= 820 and presentation == 0 and workspace == 0
        result.append({
            "case": len(result), "fixture": [w, h, values, focus, route,
                                                int(pending), presentation, workspace, clip],
            "scale": scale, "offset": offset, "active": active,
            "size": [math.ceil(w * scale) + 2 * offset,
                     math.ceil(h * scale) + 2 * offset],
        })

    for value in range(16):
        add(values=value, focus=value % 4, route=value % 4, pending=value % 2 != 0)
    for scale in (1.5, 2):
        add(scale=scale, values=15, focus=3, pending=True)
    for w, h in ((1400, 820), (1920, 1080)):
        for scale in (1, 1.5, 2):
            add(w, h, scale, 9, 1, 1)
    for w, h in ((1399, 820), (1400, 819)):
        for scale in (1, 1.5, 2):
            add(w, h, scale, 6, 2, 2, True)
    for w, h in ((960, 700), (1280, 900)):
        for scale in (1, 2):
            add(w, h, scale, 5, 0, 3)
    for w, h in ((1672, 941), (1920, 1080)):
        for scale in (1, 1.5, 2):
            add(w, h, scale, 10, 3, 0, True, 1)
    for workspace in (1, 2):
        for presentation in (0, 1):
            for scale in (1, 1.5, 2):
                add(scale=scale, values=11, focus=1, route=2,
                    presentation=presentation, workspace=workspace)
    for w, h in ((1400.25, 820.75), (1672.5, 941.25)):
        add(w, h, 1.5, 14, 2)
    for scale in (1, 1.5, 2):
        for clip in (1, 2):
            add(scale=scale, values=13, pending=True, clip=clip)
    for h in (933.25, 933.5):
        for scale in (1, 1.5, 2):
            add(h=h, scale=scale, values=3, focus=2, route=3, pending=True)
    assert len(result) == 66 and sum(item["active"] for item in result) == 38
    return result


def old_parents(width: float, height: float) -> tuple[dict, F32]:
    """Old wide Play equations, independently transcribed from the frozen base."""
    w, h = F32(width), F32(height)
    margin = min(F32(72), max(F32(48), w * F32(.043)))
    content = w - F32(2) * margin
    cabinet = content * F32(.311)
    player = content - cabinet - F32(10)
    performance = min(F32(110), max(F32(76), F32(76) + F32(.12) * (h - F32(700))))
    rack = min(F32(236), max(F32(168), F32(168) + F32(.24) * (h - F32(700)))) + F32(6)
    pedal = min(F32(114), max(F32(86), F32(86) + F32(.08) * (h - F32(700))))
    manual = (h - F32(32) - F32(100) - performance - rack - F32(28) - F32(36) -
              F32(6) * F32(10)) / F32(2)
    rack_y = F32(126) + performance + F32(10)
    rack_w = (player - F32(10)) / F32(2)
    toolbar_y = rack_y + rack + F32(10)
    manual_y = toolbar_y + F32(28) + F32(10)
    cheek_w = min(F32(168), max(F32(156), player * F32(.15)))
    key_x = margin + cheek_w + F32(10)
    key_w = player - cheek_w - F32(10)
    footer_y = h - F32(52)
    pedal_y = footer_y - F32(10) - pedal
    cabinet_x = margin + player + F32(10)
    parents = {
        "header": rect(margin, F32(16), content, F32(100)),
        "performance": rect(margin, F32(126), player, performance),
        "upper_rack": rect(margin, rack_y, rack_w, rack),
        "lower_rack": rect(margin + rack_w + F32(10), rack_y, rack_w, rack),
        "toolbar": rect(margin, toolbar_y, player, F32(28)),
        "cabinet": rect(cabinet_x, F32(126), cabinet, pedal_y - F32(10) - F32(126)),
        "pedals": rect(cabinet_x, pedal_y, cabinet, pedal),
        "footer": rect(margin, footer_y, content, F32(36)),
    }
    for i, name in enumerate(("upper", "lower")):
        y = manual_y + F32(i) * (manual + F32(10))
        parents[name + "_cheek"] = rect(margin, y, cheek_w, manual)
        parents[name + "_manual"] = rect(key_x, y, key_w, manual)
    return parents, margin


NEW_PARENTS = {
    "header": [72, 10, 1528, 102], "performance": [72, 125, 1044, 139],
    "upper_rack": [72, 269, 528, 239], "lower_rack": [600, 269, 516, 239],
    "upper_manual": [232, 528, 890, 170], "lower_manual": [224, 698, 898, 172],
    "upper_cheek": [48, 528, 184, 170], "lower_cheek": [32, 698, 192, 172],
    "cabinet": [1126, 125, 478, 745], "toolbar": [1140, 614, 448, 64],
    "pedals": [1138, 752, 450, 110], "footer": [48, 889, 1556, 36],
}
SHADOW_PARENTS = {"header", "performance", "upper_rack", "lower_rack",
                  "upper_manual", "lower_manual", "cabinet", "pedals"}


def mapped(xywh: list[float], sx: F32, sy: F32) -> list[float]:
    x, y, width, height = map(F32, xywh)
    return list(map(float, (x * sx, y * sy, (x + width) * sx, (y + height) * sy)))


def logical_regions(width: float, height: float) -> list[dict]:
    sx, sy = F32(width) / F32(1672), F32(height) / F32(941)
    before, margin = old_parents(width, height)
    after = {name: mapped(box, sx, sy) for name, box in NEW_PARENTS.items()}
    result = []

    def add(name, bounds, reason):
        require(bounds[2] > bounds[0] and bounds[3] > bounds[1], "empty declaration")
        result.append({"name": name, "logical_edges": list(map(float, bounds)), "reason": reason})

    for era, parents, dx, dy in (("before", before, 1.0, 1.0),
                                 ("after", after, float(sx), float(sy))):
        for name, bounds in parents.items():
            l, t, r, b = bounds
            shadow = name in SHADOW_PARENTS
            add(era + ":" + name,
                [l - 5 * dx, t - 3 * dy, r + 5 * dx, b + 7 * dy] if shadow else bounds,
                "parent plus declared 5-layer shadow (-5,-3,+5,+7)" if shadow else "parent paint bounds")

    # Wood/art changes have declared furniture ownership. Do not admit the
    # entire outer frame: its common, uniformly black interior stays protected.
    new_margin = float(F32(72) * sx)
    for era, m in (("before", float(margin)), ("after", new_margin)):
        add(era + ":left_wood_art", [0, 0, m, height], "retained art destination resizes with header margin")
        add(era + ":right_wood_art", [width - m, 0, width, height], "retained art destination resizes with header margin")

    frames = (("before", [float(margin - F32(7)), 8.0,
                           float(F32(width) - margin + F32(7)), height - 16.0], 9.0),
              ("after", mapped([65, 8, 1542, 917], sx, sy), 9.0 * min(float(sx), float(sy))))
    for era, (left, top, right, bottom), radius in frames:
        add(era + ":frame_top_edge", [left, top, right, top + radius], "rounded outer-frame edge, not full fill")
        add(era + ":frame_bottom_edge", [left, bottom - radius, right, bottom], "rounded outer-frame edge, not full fill")
        add(era + ":frame_left_edge", [left, top, left + radius, bottom], "rounded outer-frame edge and brass line")
        add(era + ":frame_right_edge", [right - radius, top, right, bottom], "rounded outer-frame edge and brass line")
        add(era + ":exposed_top_wood", [0, 0, width, top], "visible background wood above outer frame")
        add(era + ":exposed_bottom_wood", [0, bottom, width, height], "visible background wood below outer frame")
    add("after:lower_plinth", mapped([16, 887, 1640, 54], sx, sy), "contract lower furniture")
    add("after:manual_rim", mapped([48, 510, 1074, 18], sx, sy), "contract manual rim")
    return result


def visible_box(case: dict) -> list[int]:
    w, h, *_, clip = case["fixture"]
    s, o = case["scale"], case["offset"]
    viewport = [o, o, o + math.ceil(w * s), o + math.ceil(h * s)]
    if not clip:
        return viewport
    if clip == 1:
        x, y, width, height = (int(180 * s), int(138 * s), int(275 * s), int(77 * s))
    else:
        # Pinned SDL stores scaled clip coordinates in doubles; its physical
        # getters and queued software clip use floor for origin and extent.
        x, y, width, height = (math.floor(value * s) for value in (161, 174, 252, 41))
    return [max(viewport[0], o + x), max(viewport[1], o + y),
            min(viewport[2], o + x + width), min(viewport[3], o + y + height)]


def declared_case(case: dict) -> dict:
    result = dict(case, visible_device_box=visible_box(case), regions=[])
    if not case["active"]:
        return result
    w, h = case["fixture"][:2]
    s, o = case["scale"], case["offset"]
    vl, vt, vr, vb = result["visible_device_box"]
    for region in logical_regions(w, h):
        l, t, r, b = region["logical_edges"]
        # Pixel centers x+.5 belong to [mapped-left-1, mapped-right+1).
        # These ceilings introduce no extra half-pixel enclosure allowance.
        box = [max(vl, math.ceil(l * s + o - 1.5)),
               max(vt, math.ceil(t * s + o - 1.5)),
               min(vr, math.ceil(r * s + o + .5)),
               min(vb, math.ceil(b * s + o + .5))]
        result["regions"].append(dict(region, device_box=box))
    return result


def mask_image(case: dict) -> Image.Image:
    result = Image.new("L", tuple(case["size"]), 0)
    draw = ImageDraw.Draw(result)
    for region in case["regions"]:
        left, top, right, bottom = region["device_box"]
        if left < right and top < bottom:
            draw.rectangle((left, top, right - 1, bottom - 1), fill=255)
    return result


def source_identity(repo: Path, base: str) -> dict:
    old, new = {}, {}
    for name in SOURCE_PATHS:
        historical = subprocess.check_output(["git", "show", f"{base}:{name}"], cwd=repo)
        current = (repo / name).read_bytes()
        old[name], new[name] = digest_bytes(historical), digest_bytes(current)
        if name not in MUTABLE_SOURCE_PATHS:
            require(historical == current, f"unchanged renderer/font/art/source differs: {name}")
    return {"baseline": old, "current": new,
            "contract_sha256": digest(repo / CONTRACT),
            "tool_sha256": digest(Path(__file__)),
            "framing_tool_sha256": digest(Path(__file__).with_name("qualify_percussion_raster.py"))}


def normalize_cpp(value: str) -> str:
    return re.sub(r"\s+", "", re.sub(r"//[^\n]*|/\*.*?\*/", "", value, flags=re.S))


def harness_identity(repo: Path, base: str) -> dict:
    old = subprocess.check_output(["git", "show", f"{base}:{HARNESS}"], cwd=repo).decode()
    new = (repo / HARNESS).read_text()
    regions = (("cases", "std::vector<Case> cases()", "UiModel state_for"),
               ("state", "UiModel state_for", "bool active"),
               ("stream", "void stream(", "} // namespace"))
    result = {}
    for name, start, end in regions:
        before = normalize_cpp(old[old.index(start):old.index(end, old.index(start))])
        after = normalize_cpp(new[new.index(start):new.index(end, new.index(start))])
        require(before == after, f"fixture/state/stream contract changed: {name}")
        result[name + "_normalized_sha256"] = digest_bytes(before.encode())
    return result


def freeze(args) -> dict:
    require(args.baseline_commit == BASE, "this version declares only the admitted baseline commit")
    require(digest(args.repo / CONTRACT) == CONTRACT_SHA, "frozen contract differs")
    identities = source_identity(args.repo, args.baseline_commit)
    before_files = {"apps/standalone/UiModel.cpp": args.before_model,
                    "apps/standalone/InstrumentView.cpp": args.before_painter}
    for name, path in before_files.items():
        require(path is not None and digest(path) == identities["baseline"][name],
                "preserved baseline source bytes do not match the declared commit")
    baseline_receipt = json.loads((args.repo / SESSION / "reports/baseline-inputs.json").read_text())
    require(digest(args.before) == baseline_receipt["binaries"]["percussion-raster"]["sha256"],
            "before executable does not match the original baseline build receipt")
    inventory = {"schema": 1, "cases": 66}
    require(json.loads(run(args.before, "--list")) == inventory and
            json.loads(run(args.after, "--list")) == inventory, "66-case inventory mismatch")
    cases = [declared_case(case) for case in fixture_cases()]
    for case in cases:
        allowed = mask_image(case).histogram()[255]
        total = math.prod(case["size"])
        case["allowed_pixels"] = allowed
        case["protected_pixels"] = total - allowed
        require(allowed == 0 if not case["active"] else 0 < allowed < total,
                "inactive mask must be empty and active mask must protect pixels")
    return {
        "schema": 1, "model_id": MODEL, "stage": "declared-before-paired-pixels",
        "declared_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "baseline_commit": args.baseline_commit,
        "policy": "Union of named old/new parents with actual shadows, furniture edges, side art, exposed background and contract rim/plinth; uniformly black outer-frame interior is not a blanket allowed region.",
        "pixel_membership": "Centers x+0.5,y+0.5 in each transformed logical rectangle expanded exactly one DEVICE pixel, then intersected with actual viewport/caller clip. No integer-enclosure half-pixel or logical-unit allowance.",
        "inactive_policy": "Whole-frame RGBA equality; empty permitted mask.",
        "source_identity": identities,
        "harness_identity": harness_identity(args.repo, args.baseline_commit),
        "before_executable": {"path_at_declaration": str(args.before), "sha256": digest(args.before)},
        "after_executable": {"path_at_declaration": str(args.after), "sha256": digest(args.after)},
        "baseline_build_receipt_sha256": digest(args.repo / SESSION / "reports/baseline-inputs.json"),
        "new_build_receipt_sha256": digest(args.repo / SESSION / "reports/wave4-migration-build.log.gz"),
        "cases": cases,
        "limits": "An independent change-region test, not original-art equality or material correctness. Panel content/readability and live controls have separate literal native tests. Fixed copied states, SDL software surfaces, no physical display/device or audio claim.",
    }


def compare_case(spec: dict, before: tuple[dict, bytes], after: tuple[dict, bytes]) -> dict:
    old, old_bytes = before
    new, new_bytes = after
    require({k: v for k, v in old.items() if k != "regions"} ==
            {k: v for k, v in new.items() if k != "regions"}, "paired state/transform/header differs")
    expected = {"case": spec["case"], "fixture": spec["fixture"], "scale": spec["scale"],
                "offset": spec["offset"], "active": spec["active"],
                "width": spec["size"][0], "height": spec["size"][1]}
    for key, value in expected.items():
        require(new[key] == value, "stream does not match frozen independent case: " + key)
    # frombuffer avoids retaining a second full RGBA copy for each side.
    size = tuple(spec["size"])
    old_image = Image.frombuffer("RGBA", size, old_bytes, "raw", "RGBA", 0, 1)
    new_image = Image.frombuffer("RGBA", size, new_bytes, "raw", "RGBA", 0, 1)
    channels = ImageChops.difference(old_image, new_image).split()
    difference = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]),
                                    ImageChops.lighter(channels[2], channels[3]))
    changed = difference.point(lambda value: 255 if value else 0)
    allowed = mask_image(spec)
    require(allowed.histogram()[255] == spec["allowed_pixels"], "frozen mask pixel count differs")
    escaped = ImageChops.subtract(changed, allowed)
    changed_count = changed.histogram()[255]
    escaped_count = escaped.histogram()[255]
    locations = []
    bounds = escaped.getbbox()
    if bounds:
        pixels = escaped.load()
        for y in range(bounds[1], bounds[3]):
            for x in range(bounds[0], bounds[2]):
                if pixels[x, y]:
                    offset = (y * size[0] + x) * 4
                    locations.append({"x": x, "y": y,
                                      "before_rgba": list(old_bytes[offset:offset + 4]),
                                      "after_rgba": list(new_bytes[offset:offset + 4])})
                    if len(locations) == 12:
                        break
            if len(locations) == 12:
                break
    nonvacuous = not spec["active"] or changed_count > 0
    return {
        "case": spec["case"], "fixture": spec["fixture"], "scale": spec["scale"],
        "size": spec["size"], "active": spec["active"],
        "compared_pixels": math.prod(size), "allowed_pixels": spec["allowed_pixels"],
        "protected_pixels": spec["protected_pixels"],
        "before_rgba_sha256": digest_bytes(old_bytes), "after_rgba_sha256": digest_bytes(new_bytes),
        "before_metadata_sha256": digest_bytes(json.dumps(old, sort_keys=True).encode()),
        "after_metadata_sha256": digest_bytes(json.dumps(new, sort_keys=True).encode()),
        "changed_pixels": changed_count, "difference_bounds": changed.getbbox(),
        "escaped_pixels": escaped_count, "escaped_bounds": bounds,
        "first_escaped_pixels": locations, "nonvacuous": nonvacuous,
        "passed": escaped_count == 0 and nonvacuous,
    }


def peak_rss() -> dict:
    try:
        import resource
        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return {"bytes": int(value if sys.platform == "darwin" else value * 1024),
                "scope": "comparison Python process lifetime; child helpers measured separately by OS", "method": "getrusage(RUSAGE_SELF).ru_maxrss"}
    except (ImportError, OSError, AttributeError):
        return {"bytes": None, "scope": "unavailable", "method": None}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--baseline-commit", default=BASE)
    parser.add_argument("--mask", required=True, type=Path)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--before-model", type=Path)
    parser.add_argument("--before-painter", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        args.repo, args.before, args.after = (value.resolve(strict=True) for value in
                                              (args.repo, args.before, args.after))
        if args.freeze:
            require(args.output is None, "freeze takes --mask only, not --output")
            require(not args.mask.exists() and not args.mask.is_symlink(), "mask already exists")
            report = freeze(args)
            write_new(args.mask, report)
            unclip = [row for row in report["cases"] if row["active"] and row["fixture"][-1] == 0]
            print(json.dumps({"stage": report["stage"], "cases": 66,
                              "mask_sha256": digest(args.mask),
                              "minimum_active_unclipped_protected_pixels": min(r["protected_pixels"] for r in unclip)}))
            return 0
        require(args.output is not None, "comparison requires --output")
        require(not args.output.exists() and not args.output.is_symlink(), "report already exists")
        require(args.output.parent.is_dir(), "report parent must already exist")
        mask_bytes = args.mask.read_bytes()
        require(len(mask_bytes) <= 4 * 1024 * 1024, "mask exceeds bound")
        declaration = json.loads(mask_bytes)
        require(declaration.get("model_id") == MODEL and declaration.get("schema") == 1 and
                declaration.get("stage") == "declared-before-paired-pixels", "unknown mask")
        require(declaration["baseline_commit"] == args.baseline_commit == BASE, "baseline differs")
        require(source_identity(args.repo, BASE) == declaration["source_identity"], "source changed after declaration")
        require(digest(args.before) == declaration["before_executable"]["sha256"] and
                digest(args.after) == declaration["after_executable"]["sha256"], "executable changed after declaration")
        require(harness_identity(args.repo, BASE) == declaration["harness_identity"], "fixture functions changed")
        for actual, expected in zip(declaration["cases"], fixture_cases(), strict=True):
            for name, value in expected.items():
                require(actual[name] == value, "declared case inventory changed")
            derived = declared_case(expected)
            require(actual["regions"] == derived["regions"] and
                    actual["visible_device_box"] == derived["visible_device_box"], "declared region geometry changed")
        started = time.monotonic()
        report = {
            "schema": 1, "model_id": MODEL, "status": "incomplete",
            "mask_sha256": digest_bytes(mask_bytes), "mask_path_at_run": str(args.mask.resolve()),
            "source_identity": declaration["source_identity"],
            "before_executable": declaration["before_executable"],
            "after_executable": declaration["after_executable"],
            "python": platform.python_version(), "platform": platform.platform(),
            "Pillow": PILLOW_VERSION, "cases": [], "error": None,
            "build_attestation": "Original baseline and current coherent build receipts are separately retained; executable hashes alone do not prove compilation.",
            "limits": declaration["limits"],
        }
        try:
            for spec in declaration["cases"]:
                result = compare_case(spec, frame(args.before, spec["case"]), frame(args.after, spec["case"]))
                report["cases"].append(result)
                if len(report["cases"]) % 10 == 0:
                    print(f"Compared {len(report['cases'])}/66 source-bound pairs", flush=True)
            require(digest(args.mask) == digest_bytes(mask_bytes), "mask changed during comparison")
            require(source_identity(args.repo, BASE) == declaration["source_identity"], "source changed during comparison")
            require(digest(args.before) == declaration["before_executable"]["sha256"] and
                    digest(args.after) == declaration["after_executable"]["sha256"], "executable changed during comparison")
            report["status"] = "passed" if all(row["passed"] for row in report["cases"]) else "failed"
        except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError) as error:
            report["error"] = str(error)[:2000]
        report["elapsed_seconds"] = time.monotonic() - started
        report["peak_resident"] = peak_rss()
        report["totals"] = {
            "pairs": len(report["cases"]),
            "active_pairs": sum(row["active"] for row in report["cases"]),
            "inactive_pairs": sum(not row["active"] for row in report["cases"]),
            "compared_pixels": sum(row["compared_pixels"] for row in report["cases"]),
            "changed_pixels": sum(row["changed_pixels"] for row in report["cases"]),
            "protected_pixels": sum(row["protected_pixels"] for row in report["cases"]),
            "escaped_pixels": sum(row["escaped_pixels"] for row in report["cases"]),
            "identical_inactive_pairs": sum(not row["active"] and row["changed_pixels"] == 0 for row in report["cases"]),
            "max_raw_pair_bytes": max((row["compared_pixels"] * 8 for row in report["cases"]), default=0),
            "retained_raw_frames": 0,
        }
        write_new(args.output, report)
        print(json.dumps({"status": report["status"], **report["totals"],
                          "elapsed_seconds": report["elapsed_seconds"]}))
        return 0 if report["status"] == "passed" else 1
    except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(f"Raster comparison admission failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
