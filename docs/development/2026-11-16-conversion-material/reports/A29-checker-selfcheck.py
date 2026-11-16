#!/usr/bin/env python3
"""Bounded independent-comparator selfchecks; no candidate pair qualification."""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace

from PIL import Image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--before", type=Path, default=Path("../baseline-lower/test_standalone_footage_typography_raster"))
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("existing selfcheck output refused")
    repo = Path(__file__).resolve().parents[4]
    path = repo / "tools/compare_footage_typography.py"
    spec = importlib.util.spec_from_file_location("a29_comparator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    start = time.monotonic()
    checks, frames = [], []

    def check(name, condition):
        checks.append({"name": name, "passed": bool(condition)})
        if not condition:
            raise AssertionError(name)

    report = {"schema": 1, "status": "incomplete", "scope": "checker arithmetic/inventory/corruption selfchecks and genuine before-only frame preflight; zero candidate pairs", "checks": checks, "before_frames": frames,
              "checker": module.file_identity(path), "source": module.file_identity(Path(__file__)), "before_executable": module.file_identity(args.before)}
    try:
        glyphs = module.font_metrics(repo / module.FONT)
        mask = module.declare_mask(glyphs)
        check("110 independently declared pairs", len(mask["cases"]) == 110)
        check("66 original plus44 supplemental", [c["suite"] for c in mask["cases"]] == ["percussion"] * 66 + ["typography"] * 44)
        check("44 exact whole-frame cases", sum(c["whole_frame_equality_required"] for c in mask["cases"]) == 44)
        check("286098649 bounded compared pixels", sum(c["compared_pixels"] for c in mask["cases"]) == 286098649)
        canonical = mask["cases"][66]
        check("canonical allowance is7928 pixels", canonical["allowed_pixels"] == 7928)
        check("glyph union narrower than label boxes", canonical["allowed_pixels"] < 18 * 46 * 23)
        check("eighteen complete strings", [r["text"] for r in canonical["labels"]] == list(module.LABELS) * 2)
        check("correct1 3/5 string", canonical["labels"][6]["text"] == canonical["labels"][15]["text"] == "1 3/5'")
        check("62 old glyph copies", sum(len(r["before"]) for r in canonical["labels"]) == 62)
        check("62 new glyph copies", sum(len(r["after"]) for r in canonical["labels"]) == 62)
        total_calls = sum(len(module.runs(r["text"], r["label_box_binary32"], 1, 1, glyphs, True)) for r in canonical["labels"])
        check("50 actual text calls", total_calls == 50)
        for c in mask["cases"]:
            if c["suite"] != "typography":
                continue
            if 34 <= c["case"] <= 41:
                check(f"case{c['case']} requires exact frame", c["allowed_pixels"] == 0)
            if c["case"] in (42, 43):
                check(f"case{c['case']} has bounded64x64 crop", c["output_size"] == [64, 64])
        # A union is order-independent; no bounding-box collapse is permitted.
        reordered = dict(canonical)
        reordered["allowed_rectangles"] = list(reversed(canonical["allowed_rectangles"]))
        check("rectangle union order does not change pixels", module.allowance_mask(canonical).tobytes() == module.allowance_mask(reordered).tobytes())
        old5 = canonical["labels"][1]["before"][0]
        check("independent clipping failure pixel lies inside old glyph", old5["device_copy_box"] == [199, 489, 206, 499])
        logical_clip = mask["cases"][66 + 30]
        check("logical clip scales before integer query", logical_clip["clip"] == [237, 586, 5, 28])
        clipmask = module.allowance_mask(mask["cases"][66 + 26])
        check("one-pixel envelope never escapes caller clip", clipmask.getpixel((202, 492)) == 0 and clipmask.getpixel((203, 492)) == 255)

        # Destination COPY conversion uses truncation, not floor at negative origins.
        check("negative fractional COPY truncates independently", module.device_box([-1.9, -2.9, 3.9, 4.9], [1, 1], [0, 0]) == [-1, -2, 2, 2])
        check("zero COPY extent paints no area", module.area(module.device_box([1, 2, .1, .1], [1, 1], [0, 0])) == 0)
        tiny = {"text": "1", "x": 0.0, "top": 0.0, "size": .5, "requested_baseline": None}
        check("subpixel gutters retained in both dimensions", module.glyph_quads(tiny, glyphs)[0]["gutter"] == [2, 2])
        check("metadata rejects bool/int substitution", not module.typed_equal(True, 1))
        check("binary32 nextafter remains distinguishable", not module.f32_equal(module.typography_cases()[40]["logical_size"][0], 1400))

        header, raw, header_sha = module.frame(args.before, 0, 45)
        check("real canonical before metadata matches independent matrix", module.metadata_errors(canonical, header) == [])
        before = Image.frombytes("RGBA", tuple(canonical["output_size"]), raw)
        allowance = module.allowance_mask(canonical)
        empty_delta, _ = module.difference_metrics(before, before, allowance)
        check("identical actual frame has zero differences", empty_delta["different_pixels"] == empty_delta["outside_pixels"] == 0)
        for channel in range(4):
            changed = before.copy()
            pixel = list(changed.getpixel((0, 0)))
            pixel[channel] ^= 1
            changed.putpixel((0, 0), tuple(pixel))
            delta, _ = module.difference_metrics(before, changed, allowance)
            check(f"one-bit protected channel{channel} rejected", not delta["passed"] and delta["outside_pixels"] == delta["outside_channels"] == 1)
        inside = before.copy()
        box = canonical["allowed_rectangles"][0]
        point = (box[0], box[1])
        pixel = list(inside.getpixel(point)); pixel[0] ^= 1; inside.putpixel(point, tuple(pixel))
        delta, _ = module.difference_metrics(before, inside, allowance)
        check("inside pixel is admitted only by containment subcheck", delta["passed"] and delta["different_pixels"] == 1 and delta["outside_pixels"] == 0)
        check("same pixel rejected by exact whole-frame requirement", not module.difference_metrics(before, inside, Image.new("L", before.size, 0))[0]["passed"])
        observations = module.label_observations(canonical, before, "before")
        check("all before full-label glyphs retain ink", all(r["passed"] for r in observations))
        no_glyph = before.copy()
        box = old5["device_copy_box"]
        no_glyph.paste((0, 0, 0, 255), tuple(box))
        check("removed complete glyph rejected by content guard", not module.label_observations(canonical, no_glyph, "before")[1]["passed"])
        focus = module.focus_equality(canonical, before, before)
        check("actual full-focus mask is nonempty and exact", focus["passed"] and focus["before_pixels"] > 0)
        altered_focus = before.copy()
        focus_pixels = module.cyan_mask(before)
        focus_point = next((x, y) for y in range(before.height) for x in range(before.width) if focus_pixels.getpixel((x, y)))
        altered_focus.putpixel(focus_point, (165, 227, 223, 255))
        check("one changed focus pixel rejected", not module.focus_equality(canonical, before, altered_focus)["passed"])
        for name, mutate in (
            ("protocol", lambda h: h.__setitem__("protocol", "fabricated-v2")),
            ("focus", lambda h: h["focus"].__setitem__(3, 8)),
            ("route", lambda h: h.__setitem__("route", "B")),
            ("model clock", lambda h: h["model"]["view"]["applied"].__setitem__("frame_clock", 1)),
            ("complete inventory", lambda h: h["model"]["layout"].__setitem__("control_count", 67)),
            ("geometry", lambda h: next(c for c in h["model"]["layout"]["controls"] if c["id"][0] == 4)["label_bounds"].__setitem__(0, -1))):
            bad = copy.deepcopy(header); mutate(bad)
            check("tampered " + name + " rejected", bool(module.metadata_errors(canonical, bad)))
        material = module.material_equality(canonical, before, before)
        check("all12 exact material patches accepted", material["passed"] and len(material["patches"]) == 12)
        altered_material = before.copy(); altered_material.putpixel((101, 337), (255, 255, 255, 255))
        check("one changed material pixel rejected", not module.material_equality(canonical, before, altered_material)["passed"])
        frames.append({"case": 0, "metadata_sha256": header_sha, "rgba_sha256": module.sha(raw), "metadata_errors": []})
        # Separate before-only transform checks do not execute a candidate painter.
        for index in (18, 22, 23, 25, 26, 30, 40, 42, 43):
            case = mask["cases"][66 + index]
            h, pixels, hs = module.frame(args.before, index, 45)
            errors = module.metadata_errors(case, h)
            frames.append({"case": index, "metadata_sha256": hs, "rgba_sha256": module.sha(pixels), "metadata_errors": errors})
            check(f"genuine before case{index} independent transform/metadata", not errors)
        with tempfile.TemporaryDirectory(prefix="A29-checker-") as temp:
            temp = Path(temp)
            badfont = temp / "FontData.h"; badfont.write_bytes((repo / module.FONT).read_bytes() + b"\n")
            try:
                module.font_metrics(badfont)
            except ValueError:
                refused = True
            else:
                refused = False
            check("altered font provenance refused", refused)
            report_path = temp / "already.json"; report_path.write_text("preserve")
            try:
                module.write_new(report_path, {"fabricated": True})
            except FileExistsError:
                refused = True
            else:
                refused = False
            check("existing evidence is never overwritten", refused and report_path.read_text() == "preserve")
        report["status"] = "passed"
        report["mask_summary"] = {"sha256": module.sha(module.canonical_json(mask)), "pairs": 110,
                                  "compared_pixels": 286098649, "required_exact_frames": 44,
                                  "canonical_allowed_pixels": 7928}
    except Exception as error:
        report["status"] = "failed"
        report["error"] = {"type": type(error).__name__, "message": str(error)}
    report["checks_passed"] = sum(c["passed"] for c in checks)
    report["checks_total"] = len(checks)
    report["seconds"] = time.monotonic() - start
    module.write_new(args.output, report)
    print(json.dumps({key: report.get(key) for key in ("status", "checks_passed", "checks_total", "seconds", "error")}, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
