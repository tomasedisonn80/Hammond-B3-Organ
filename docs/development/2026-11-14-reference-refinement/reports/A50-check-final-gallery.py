#!/usr/bin/env python3
"""Read-only admission of retained v4 evidence; never runs a native executable.

Run with Python/Pillow/PyMuPDF and the frozen source/build inputs available:
  python3 -B A50-check-final-gallery.py --repo /path/to/repo --output audit.json
Only the requested output JSON is written. Original captures are never changed.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import fitz
import PIL
from PIL import Image

COMMIT = "0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b"
TREE = "f8144b771cda1264a8788f8297f5bfec999f4a08"
EXE = "01fe78a55b7a9bc72228dafe175f5a8eb48481c063f217606474d4dff682320f"
PAINTER = "f323c8c2f5529b03c25deccb74f482d8b6312487492a45d14b94ef0e24cfbb6a"
PRODUCER = "92ae0be31a6ef21eb696c87d4f9dacd8ea8a6732d6c1033e0d7457ca3a76d16b"
GALLERY = "examples/demos/standalone-interface-preview-v4"
REPORTS = "docs/development/2026-11-14-reference-refinement/reports"
CASES = [
    ("play-reference-1672x941", 1672, 941, "play", "dimensional"),
    ("play-default-1280x900", 1280, 900, "play", "dimensional"),
    ("play-minimum-960x700", 960, 700, "play", "dimensional"),
    ("service-reference-1672x941", 1672, 941, "service", "dimensional"),
    ("service-minimum-960x700", 960, 700, "service", "dimensional"),
    ("rotary-reference-1672x941", 1672, 941, "rotary", "dimensional"),
    ("rotary-minimum-960x700", 960, 700, "rotary", "dimensional"),
    ("flat-minimum-960x700", 960, 700, "play", "flat"),
]
INITIAL = {
    "manual_drawbars": [[[1, 2, 3, 4, 5, 6, 7, 8, 0], [7, 6, 5, 4, 3, 4, 2, 5, 3]],
                        [[7, 6, 5, 4, 3, 4, 2, 4, 2], [0, 0, 8, 0, 0, 0, 0, 0, 0]]],
    "selected_banks": [1, 0], "fixed_registrations": [1, 0], "preset_selections": [1, 10],
    "route_enabled": [True, True], "expression": 0.75, "pedal_drawbars": [8, 0],
    "percussion": {"enabled": True, "harmonic": 0, "volume": 0, "decay": 0},
}
FINAL = deepcopy(INITIAL)
FINAL["manual_drawbars"][0][1][0] = 8


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def ident(path):
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": digest(data)}


def inv_digest(value):
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def read(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON member: {key}")
            result[key] = value
        return result
    def reject(value):
        raise ValueError(f"non-JSON numeric token: {value}")
    return json.loads(path.read_text(), object_pairs_hook=pairs, parse_constant=reject)


def typed_equal(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(right, dict):
        return left.keys() == right.keys() and all(typed_equal(left[k], v) for k, v in right.items())
    if isinstance(right, list):
        return len(left) == len(right) and all(typed_equal(a, b) for a, b in zip(left, right))
    return left == right


def ink(path, roi):
    with Image.open(path) as original:
        image = original.convert("RGB")
    points = [(x, y) for y in range(roi[1], roi[3]) for x in range(roi[0], roi[2])
              if (lambda p: p[0] >= 130 and p[1] >= 105 and p[0] >= p[1] and p[2] <= 0.9 * p[0])
              (image.getpixel((x, y)))]
    box = [min(x for x, _ in points), min(y for _, y in points),
           max(x for x, _ in points) + 1, max(y for _, y in points) + 1]
    columns = {x for x, _ in points}
    return {"roi_half_open": roi, "bbox_half_open": box, "pixels": len(points),
            "width": box[2] - box[0], "height": box[3] - box[1],
            "center_x": (box[0] + box[2]) / 2,
            "occupied_column_runs": sum(x - 1 not in columns for x in columns)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.repo.resolve()
    gallery, reports = root / GALLERY, root / REPORTS
    started, clock = now(), time.monotonic()
    failures, counts = [], Counter()
    def check(group, label, condition):
        counts[group] += 1
        if not condition:
            failures.append({"group": group, "check": label})
    def git(*arguments):
        return subprocess.check_output(["git", "-C", str(root), *arguments], stdin=subprocess.DEVNULL)
    def blob_id(path):
        data = git("show", f"{COMMIT}:{path}")
        return {"bytes": len(data), "sha256": digest(data)}
    p, m, q = (read(gallery / name) for name in ("provenance.json", "manifest.json", "inputs/source-qualification.json"))
    a46 = read(reports / "A46-final-native-gallery.json")
    a41 = read(reports / "A41-raster-acceptance.json")
    publication = read(reports / "root-header-publication.json")
    check("source", "published commit tree", git("rev-parse", f"{COMMIT}^{{tree}}").decode().strip() == TREE)
    check("source", "publication receipt", publication["commit"] == COMMIT and publication["tree"] == TREE)
    check("source", "qualification revision", q["published_commit"] == COMMIT and q["published_tree"] == TREE)
    check("source", "capture observed revision", p["source"]["git_before"] == p["source"]["git_after"] == {"head": COMMIT, "committed_tree": TREE})
    check("gallery", "manifest/provenance positive status", m["status"] == p["status"] == a46["status"] == "passed")
    files = {str(x.relative_to(gallery)): ident(x) for x in sorted(gallery.rglob("*")) if x.is_file()}
    check("gallery", "41 files / 2,948,483 bytes", len(files) == 41 and sum(x["bytes"] for x in files.values()) == 2948483)
    check("gallery", "exact 39-file payload set", set(m["files"]) == set(files) - {"manifest.json", "README.md"} and len(m["files"]) == 39)
    for path, expected in m["files"].items():
        check("payload", path, files.get(path) == expected)
    check("gallery", "manifest byte sum", sum(v["bytes"] for v in m["files"].values()) == m["total_bytes_excluding_manifest"])
    for name, key in (("manifest.json", "gallery_manifest"), ("provenance.json", "gallery_provenance"), ("README.md", "gallery_readme")):
        expected = {k: a46[key][k] for k in ("bytes", "sha256")}
        check("gallery", f"A46 frozen {name}", files[name] == expected)
    snapshots = {}
    for name, expected in a46["snapshots"].items():
        path = root / expected["path"]
        check("retained_records", name, ident(path) == {k: expected[k] for k in ("bytes", "sha256")})
        snapshots[name] = read(path)
    for name in ("build", "capture"):
        expected = a46[name]["log"]
        check("retained_records", f"A46 {name} log", ident(root / expected["path"]) == {k: expected[k] for k in ("bytes", "sha256")})
    after = snapshots["after_capture"]["inputs"]
    check("retained_records", "before/build/capture named input equality", snapshots["before_build"]["inputs"] == snapshots["after_build"]["inputs"] == after)
    merged = {**after["production"], **after["cmake_sources"]}
    check("source", "111-file qualification coverage", len(merged) == len(q["source_sha256"]) == 111 and set(merged) == set(q["source_sha256"]))
    check("source", "qualification inventory digest", inv_digest(merged) == q["source_inventory_sha256"] == "bffd31d6a2caa65872ece2cb4614902608c30c3dffc9af0c21aa4bd0a3a110fd")
    for path, expected in merged.items():
        check("source_current", path, ident(root / path) == expected and expected["sha256"] == q["source_sha256"][path])
        check("source_published", path, blob_id(path) == expected)
    check("source", "100 production inputs", len(p["source"]["files"]) == 100 and p["source"]["files"] == after["production"])
    check("source", "production digest before/after", inv_digest(p["source"]["files"]) == p["source"]["inventory_sha256_before"] == p["source"]["inventory_sha256_after"])
    check("source", "CMake/font counts", len(after["cmake_sources"]) == 11 and len(after["font_sources_and_atlas"]) == 7)
    for path, expected in after["font_sources_and_atlas"].items():
        check("fonts", path, ident(root / path) == expected)
    check("source", "accepted painter", ident(root / "apps/standalone/InstrumentView.cpp")["sha256"] == PAINTER)
    check("source", "no capture source changes", p["all_recorded_inputs_unchanged"] is True and not p["source"]["changed_paths"] and not p["build"]["changed_paths"])
    build = Path(p["build"]["root"])
    check("build", "13 selected build inputs", len(p["build"]["files"]) == 13 and p["build"]["files"] == after["selected_build_inputs"])
    check("build", "selected build digest", inv_digest(p["build"]["files"]) == p["build"]["inventory_sha256_before"] == p["build"]["inventory_sha256_after"])
    for group, entries in (("selected_build_inputs", p["build"]["files"]), ("extra_build_inputs", after["extra_build_inputs"])):
        for path, expected in entries.items():
            check(group, path, ident(build / path) == expected)
    check("build", "nine extra build inputs", len(after["extra_build_inputs"]) == 9)
    cache = {}
    for line in (build / "CMakeCache.txt").read_text().splitlines():
        if line and not line.startswith(("#", "//")) and ":" in line and "=" in line:
            name_type, value = line.split("=", 1)
            cache[name_type.split(":", 1)[0]] = value
    selected = p["build"]["selected_configuration_before"]
    check("build", "selected cache configuration", {k: cache[k] for k in selected} == selected == p["build"]["selected_configuration_after"] == after["selected_configuration"])
    executable = ident(Path(p["executable"]["path"]))
    check("build", "exact executable", executable == {"bytes": 3860368, "sha256": EXE} == p["executable"]["before"] == p["executable"]["after"] == after["executable"])
    check("build", "binary qualification", q["binary_sha256"] == EXE and q["binary_bytes"] == executable["bytes"])
    producer_path = root / "tools/capture_standalone_interface.py"
    producer_id = ident(producer_path)
    check("producer", "exact captured producer", producer_id == {"bytes": 29923, "sha256": PRODUCER} == p["tool"]["before"] == p["tool"]["after"] == after["capture_producer"])
    check("producer", "published producer", blob_id("tools/capture_standalone_interface.py") == producer_id)
    spec = importlib.util.spec_from_file_location("a50_frozen_producer", producer_path)
    producer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(producer)  # Only the pinned pure validation/replay functions are called.
    check("inputs", "input before/after identity", p["inputs"]["before"] == p["inputs"]["after"])
    for path, expected in p["inputs"]["before"].items():
        check("inputs", path, ident(gallery / path) == expected)
    check("inputs", "exact state input", (gallery / "inputs/controls.b3controls").read_text() == producer.STATE)
    check("inputs", "independent expected control values", typed_equal(INITIAL, producer.INITIAL_CONTROLS) and typed_equal(FINAL, producer.FINAL_CONTROLS))
    check("inputs", "explicit dummy environment", all(p["environment"][key] == value for key, value in {"SDL_AUDIODRIVER": "dummy", "SDL_VIDEODRIVER": "dummy", "SDL_RENDER_DRIVER": "software"}.items()))
    check("cases", "exact eight named cases", [(c["name"], c["width"], c["height"], c["workspace"], c["presentation"]) for c in p["cases"]] == CASES)
    case_results = []
    for c, (name, width, height, workspace, presentation) in zip(p["cases"], CASES):
        d = read(gallery / c["diagnostics"]["path"])
        expected_events = 68 if presentation == "flat" else 66
        replay_name = f"inputs/{workspace}-{presentation}.b3uireplay"
        replay_text, producer_events = producer.replay(workspace, presentation)
        check("replay", name, (gallery / replay_name).read_text() == replay_text and producer_events == expected_events)
        command = [p["executable"]["path"], "--state", str(gallery / "inputs/controls.b3controls"), "--input-script", str(gallery / replay_name), "--workspace", "play", "--width", str(width), "--height", str(height), "--sample-rate", "48000", "--buffer-frames", "512", "--screenshot", str(gallery / f"images/{name}.bmp"), "--diagnostics", str(gallery / f"diagnostics/{name}.json")]
        check("commands", name, c["command"] == command and c["exit_code"] == 0 and c["status"] == "passed")
        for stream in ("stdout", "stderr"):
            check("streams", f"{name} {stream}", (gallery / f"diagnostics/{name}.{stream}.txt").read_bytes() == b"")
        check("diagnostics", f"{name} identity", ident(gallery / c["diagnostics"]["path"]) == {k: c["diagnostics"][k] for k in ("bytes", "sha256")})
        for stage in ("screenshot", "last_painted", "before_shutdown"):
            painted = d["presentation"][stage]
            check("typed_holds", f"{name} {stage}", typed_equal(painted["held_targets"], {"upper": 2, "lower": 1, "pedals": 1}))
            check("typed_capture", f"{name} {stage}", typed_equal(painted["pointer_capture"], {"sdl_captured": False, "ui_captured": False, "attempts": 0, "successes": 0, "losses": 0, "release_calls": 0}))
        check("typed_state", f"{name} full controls", all(typed_equal(item, FINAL) for item in (d["controls"], d["replay"]["desired_controls_before_shutdown"], d["replay"]["before_shutdown"]["controls"])))
        check("typed_state", f"{name} observed pre-edit holds", any(typed_equal(o["controls"], INITIAL) and typed_equal(o["manual_notes"], [[60, 64], [67]]) and typed_equal(o["pedal_ids"], [3]) for o in d["replay"]["observations"]))
        check("cleanup", f"{name} joined endpoint", d["session"]["held_after_shutdown"] is False and d["session"]["running_after_shutdown"] is False and d["midi"]["quiescent_after_shutdown"] is True and d["midi"]["active_after_shutdown"] is False and d["midi"]["diagnostics_stable_after_shutdown"] is True)
        try:
            result = producer.validate(d, width, height, workspace, presentation, expected_events)
            check("producer_endpoint", name, typed_equal(result, c["validation"]))
        except Exception as exc:
            check("producer_endpoint", f"{name}: {exc}", False)
        path = gallery / c["image"]["path"]
        with Image.open(path) as image:
            decoded = digest(image.convert("RGBA").tobytes())
            dimensions, image_format = list(image.size), image.format
        check("pixels", name, ident(path) == c["image"]["png"] and dimensions == [width, height] and image_format == "PNG" and decoded == c["image"]["decoded_sha256"])
        check("pixels", f"{name} BMP retention boundary", c["image"]["lossless_bmp_to_png"] is True and c["image"]["native_bmp_removed_after_verification"] is True and not path.with_suffix(".bmp").exists())
        painted = d["presentation"]["screenshot"]
        case_results.append({"name": name, "png": ident(path), "dimensions": dimensions, "decoded_rgba8_sha256": decoded, "ui_events": expected_events, "callbacks": d["audio"]["callback_count"], "rendered_frames": d["audio"]["rendered_frames"], "painted": painted, "session_discarded_commands_after_shutdown": d["session"]["discarded_commands"]})
    check("pixels", "total PNG bytes", sum(c["png"]["bytes"] for c in case_results) == 2722450)
    reference_info = read(root / "docs/design/atlas-reference.json")
    reference_path = root / reference_info["image"]
    check("reference", "JPEG original identity", ident(reference_path) == {"bytes": reference_info["bytes"], "sha256": reference_info["sha256"]})
    check("reference", "PDF original identity", ident(root / reference_info["source"])["sha256"] == reference_info["source_sha256"])
    with fitz.open(root / reference_info["source"]) as pdf:
        check("reference", "500 PDF pages", len(pdf) == 500)
        for page in reference_info["pdf_pages"]:
            refs = [item[0] for item in pdf[page - 1].get_images(full=True)]
            check("reference", f"page {page} exact JPEG object", reference_info["pdf_image_object"] in refs and pdf.extract_image(reference_info["pdf_image_object"])["image"] == reference_path.read_bytes())
    measurements = {}
    for name, path in [("reference", reference_path)] + [(c[0], gallery / f"images/{c[0]}.png") for c in CASES if c[1] == 1672]:
        measures = {"title": ink(path, [595, 10, 1081, 65]), "subtitle": ink(path, [600, 60, 1100, 106])}
        measurements[name] = {"image": ident(path), **measures}
        expected = a41["measured_images"]["reference" if name == "reference" else "after-fixed-state"]
        check("header", f"{name} measured A41 ink", all(measures[k] == expected[k] for k in ("title", "subtitle")))
        if name != "reference":
            title, subtitle = measures["title"], measures["subtitle"]
            check("header", f"{name} unchanged A41 title thresholds", 461 <= title["width"] <= 467 and 32 <= title["height"] <= 34 and 19 <= title["bbox_half_open"][1] <= 21 and 833 <= title["center_x"] <= 837)
            check("header", f"{name} unchanged A41 caption thresholds", 367 <= subtitle["width"] <= 375 and 11 <= subtitle["height"] <= 13 and 70 <= subtitle["bbox_half_open"][1] <= 72 and 833.5 <= subtitle["center_x"] <= 837.5 and subtitle["occupied_column_runs"] == 15)
    historical = {}
    for version in (1, 2, 3):
        directory = root / f"examples/demos/standalone-interface-preview-v{version}"
        entries = {str(path.relative_to(root)): ident(path) for path in sorted(directory.rglob("*")) if path.is_file()}
        check("history", f"v{version} 41 files", len(entries) == 41)
        for path, expected in entries.items():
            check("historical_blobs", path, blob_id(path) == expected)
        historical[f"v{version}"] = {"files": len(entries), "bytes": sum(v["bytes"] for v in entries.values()), "inventory_sha256": inv_digest(entries), "compared_to_commit": COMMIT}
    sources = ["A46-final-native-gallery.json", "A46-before-build.json", "A46-after-build.json", "A46-after-capture.json", "A46-build.log", "A46-capture.log", "A32-gallery-independent.json", "A40-reference-header-refinement.json", "A41-raster-acceptance.json", "A41-final-acceptance.json", "root-header-publication.json"]
    report = {
        "schema": "a50-final-gallery-admission-v1", "worker": "/root/w09_a50_final_gallery_admission",
        "scope": "Read-only independent retained-file/source/build-input/decoded-pixel and typed endpoint admission; no native run, compile, CTest, synthetic mutation, image composite or hermetic rebuild.",
        "started_at_utc": started, "finished_at_utc": now(), "elapsed_seconds": time.monotonic() - clock,
        "status": "passed" if not failures else "failed", "checks": sum(counts.values()), "check_groups": dict(sorted(counts.items())), "failures": failures,
        "command": [sys.executable, "-B", str(Path(__file__).resolve()), "--repo", str(root), "--output", str(args.output.resolve())],
        "checker_identity": ident(Path(__file__)), "runtime": {"python": platform.python_version(), "pillow": PIL.__version__, "pymupdf": fitz.VersionBind},
        "git_observed": {"head": git("rev-parse", "HEAD").decode().strip(), "tree": git("rev-parse", "HEAD^{tree}").decode().strip(), "cached_origin_main": git("rev-parse", "refs/remotes/origin/main").decode().strip()},
        "qualified_commit": COMMIT, "qualified_tree": TREE, "whole_worktree_clean_claimed": False,
        "gallery": {"path": GALLERY, "files": len(files), "bytes": sum(x["bytes"] for x in files.values()), "payload_files": len(m["files"]), "all_files_inventory_sha256": inv_digest(files), "manifest": files["manifest.json"], "provenance": files["provenance.json"], "readme": files["README.md"]},
        "source": {"qualified_files": len(merged), "inventory_sha256": inv_digest(merged), "production_files": len(p["source"]["files"]), "production_inventory_sha256": inv_digest(p["source"]["files"]), "cmake_files": len(after["cmake_sources"]), "font_files": len(after["font_sources_and_atlas"]), "painter_sha256": PAINTER},
        "build": {"root": str(build), "selected_files": len(p["build"]["files"]), "selected_inventory_sha256": inv_digest(p["build"]["files"]), "extra_files": len(after["extra_build_inputs"]), "selected_configuration": selected, "executable": executable, "producer": producer_id, "producer_build": a46["build"], "producer_capture": a46["capture"]},
        "cases": case_results, "reference": {"provenance": ident(root / "docs/design/atlas-reference.json"), "pdf": ident(root / reference_info["source"]), "jpeg": ident(reference_path), "pages": reference_info["pdf_pages"], "object": reference_info["pdf_image_object"]},
        "header_measurement": {"mask": a41["mask"], "unchanged_A41_thresholds": {"title_width": [461,467], "title_height": [32,34], "title_top": [19,21], "title_center_x": [833,837], "caption_width": [367,375], "caption_height": [11,13], "caption_top": [70,72], "caption_center_x": [833.5,837.5], "caption_nonspace_runs": 15}, "images": measurements, "limit": "Ink measures match the cited A41 observations; no whole-frame or literal source-reference equality follows."},
        "historical_galleries": historical, "retained_evidence": {f"{REPORTS}/{name}": ident(reports / name) for name in sources},
        "limits": ["Raw native BMPs were removed by the producer after its recorded lossless comparison; only retained PNG decoding is independently rechecked here.", "The existing desktop target build refreshed CMake and reported no work to do; this audit does not establish independent compilation/linking or a hermetic source-to-binary proof.", "Current named input hashes and local published blobs are checked; cached origin/main is not an independent network observation.", "All v4 frames are acknowledged, overlay-free keyboard-replay endpoints under dummy SDL/software rendering; pending harness, modal overlays and real OS-window/input evidence retain separate scope.", "One discarded shutdown command is retained in each diagnostic; zero faults/rejections and clear joined endpoints do not mean every counter is zero.", "No physical audio/MIDI device, real display/DPI, semantic accessibility, audio deadline, connected Leslie render or measured physical fidelity is established."],
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"status": report["status"], "checks": report["checks"], "failures": failures, "output": str(args.output), "header_bounds": {k: {n: v[n]["bbox_half_open"] for n in ("title", "subtitle")} for k, v in measurements.items()}}, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
