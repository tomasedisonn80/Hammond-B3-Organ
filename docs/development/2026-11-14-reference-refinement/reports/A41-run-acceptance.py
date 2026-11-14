"""A41 isolated native acceptance runner; no shared builds or product edits.

Run from repository root: python3 <this path> build|raster|timing|repeat
Timing is a separate explicitly coordinated quiet interval, one paired cell.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import shutil
import subprocess
import sys
import time

from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[4]
REPORTS = Path(__file__).resolve().parent
WORK = ROOT.parent / "a41-header-acceptance"
FINAL_SHA = "f323c8c2f5529b03c25deccb74f482d8b6312487492a45d14b94ef0e24cfbb6a"
OLD_COMMIT = "2e161dc3a60fc3442051799574feed37bffbfc5c"
SOURCE = ROOT / "apps/standalone/InstrumentView.cpp"
A25 = json.loads((REPORTS / "A25-material-performance.json").read_text())["build"]


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def identity(path):
    path = Path(path)
    data = path.read_bytes()
    return {"path": str(path), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def output(name, data):
    (REPORTS / name).write_text(json.dumps(data, indent=2) + "\n")


def command(argv, *, affinity=None):
    start = now()
    previous = resource.getrusage(resource.RUSAGE_CHILDREN)
    initial = time.monotonic()

    def pin():
        os.sched_setaffinity(0, affinity)
        assert os.sched_getaffinity(0) == set(affinity)

    run = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True,
                         preexec_fn=pin if affinity is not None else None)
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    row = {"argv": list(map(str, argv)), "start_utc": start, "end_utc": now(),
           "exit_code": run.returncode, "wall_seconds": time.monotonic() - initial,
           "stdout": run.stdout, "stderr": run.stderr,
           "user_seconds": usage.ru_utime - previous.ru_utime,
           "system_seconds": usage.ru_stime - previous.ru_stime,
           "involuntary_context_switches": usage.ru_nivcsw - previous.ru_nivcsw,
           "voluntary_context_switches": usage.ru_nvcsw - previous.ru_nvcsw,
           "children_max_rss_kib": usage.ru_maxrss}
    if affinity is not None:
        row["child_affinity_asserted"] = list(affinity)
    return row


def build():
    assert identity(SOURCE)["sha256"] == FINAL_SHA
    WORK.mkdir(exist_ok=True)
    old = subprocess.check_output(["git", "show", OLD_COMMIT + ":apps/standalone/InstrumentView.cpp"], cwd=ROOT)
    before = WORK / "InstrumentView-before.cpp"
    after = WORK / "InstrumentView-after.cpp"
    before.write_bytes(old)
    after.write_bytes(SOURCE.read_bytes())
    # Source-scope proof compares the complete prefix and suffix around the one
    # permitted function, without relying on the author test's assertions.
    def pieces(data):
        start = data.index(b"void paint_header(")
        end = data.index(b"[[nodiscard]] std::string focused_control_caption", start)
        return data[:start], data[end:]
    assert pieces(old) == pieces(after.read_bytes())
    dependencies = []
    for dep in A25["compiled_source_dependencies"]:
        if str(ROOT) not in dep["path"]:
            continue
        actual = identity(dep["path"])
        assert actual["sha256"] == dep["sha256"], actual
        dependencies.append(actual)
    selected_sources = []
    for name in ["UiModel.cpp", "Drawing.cpp", "FontData.h", "InspectionModel.cpp"]:
        path = ROOT / "apps/standalone" / name
        actual = identity(path)
        old_data = subprocess.check_output(["git", "show", OLD_COMMIT + ":" + path.relative_to(ROOT).as_posix()], cwd=ROOT)
        actual["equals_2e161dc"] = path.read_bytes() == old_data
        assert actual["equals_2e161dc"]
        selected_sources.append(actual)
    archives = []
    for archive in A25["archives"]:
        original = Path(archive["frozen"]["path"])
        assert identity(original)["sha256"] == archive["frozen"]["sha256"]
        copied = WORK / original.name
        shutil.copyfile(original, copied)
        archives.append(identity(copied))
    flags = ["/usr/bin/c++", *A25["compiler_flags"], *A25["include_flags"]]
    commands = []
    def compile_source(source, object_name, extra=()):
        obj = WORK / object_name
        row = command([*flags, *extra, "-MMD", "-MF", str(obj.with_suffix(".d")), "-c", str(source), "-o", str(obj)])
        commands.append(row)
        output("A41-build.json", {"commands_in_progress": commands})
        assert row["exit_code"] == 0, row
        return obj
    probe = compile_source(REPORTS / "A41-raster-probe.cpp", "raster.o")
    old_renamed = compile_source(before, "before-renamed.o", [
        "-Dpaint_instrument=paint_instrument_before", "-Daudio_overlay_layout=audio_overlay_layout_before",
        "-Dmidi_overlay_layout=midi_overlay_layout_before"])
    current = compile_source(after, "current.o")
    old_plain = compile_source(before, "before.o")
    benchmark_source = ROOT / "tests/benchmarks/standalone_material_timing.cpp"
    assert identity(benchmark_source)["sha256"] == A25["source_benchmark"]["sha256"]
    benchmark = compile_source(benchmark_source, "benchmark.o")
    libs = [str(WORK / "libhammond_standalone_drawing.a"), str(WORK / "libhammond_standalone_support.a"),
            str(WORK / "libSDL2.a"), "-lm", "-pthread", str(WORK / "libhammond_core.a")]
    binaries = []
    for name, objects in [("raster-probe", [probe, old_renamed, current]),
                          ("timing-before", [benchmark, old_plain]), ("timing-after", [benchmark, current])]:
        binary = WORK / name
        row = command(["/usr/bin/c++", "-O3", "-DNDEBUG", *map(str, objects), "-o", str(binary), *libs])
        commands.append(row)
        assert row["exit_code"] == 0, row
        binaries.append(identity(binary))
    assert identity(SOURCE)["sha256"] == FINAL_SHA
    report = {"schema": "a41-header-build-v1", "worker": "/root/w07_a41_header_independent_acceptance",
              "built_utc": now(), "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "tree": subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip(),
              "baseline_commit": OLD_COMMIT, "baseline": identity(before), "candidate": identity(after),
              "product_source": identity(SOURCE), "outside_paint_header_exactly_unchanged": True,
              "probe": identity(REPORTS / "A41-raster-probe.cpp"), "runner": identity(Path(__file__)),
              "benchmark": identity(benchmark_source), "selected_sources": selected_sources,
              "a25_project_dependencies_unchanged": dependencies, "archives": archives,
              "compiler": identity(Path("/usr/bin/c++").resolve()), "commands": commands,
              "binaries": binaries, "platform": platform.platform(), "python": sys.version,
              "pillow": pillow_version, "allowed_affinity": sorted(os.sched_getaffinity(0)),
              "sdl_version": "2.32.10", "sdl_commit": "5d249570393f7a37e037abf22cd6012a4cc56a71",
              "dynamic_libraries": command(["ldd", str(WORK / "raster-probe")])["stdout"]}
    output("A41-build.json", report)
    print(json.dumps({"build": "passed", "binaries": binaries}))


def ink(path, roi):
    image = Image.open(path).convert("RGB")
    points = [(x, y) for y in range(roi[1], roi[3]) for x in range(roi[0], roi[2])
              if (lambda p: p[0] >= 130 and p[1] >= 105 and p[0] >= p[1] and p[2] <= 0.9 * p[0])(image.getpixel((x, y)))]
    box = [min(p[0] for p in points), min(p[1] for p in points),
           max(p[0] for p in points) + 1, max(p[1] for p in points) + 1]
    columns = {x for x, _ in points}
    runs = sum(x - 1 not in columns for x in columns)
    return {"roi_half_open": roi, "bbox_half_open": box, "pixels": len(points),
            "width": box[2] - box[0], "height": box[3] - box[1],
            "center_x": (box[0] + box[2]) / 2, "occupied_column_runs": runs}


def raster():
    assert identity(SOURCE)["sha256"] == FINAL_SHA
    run = command([str(WORK / "raster-probe"), str(WORK)])
    (REPORTS / "A41-raster-results.jsonl").write_text(run.pop("stdout"))
    output("A41-raster-run.json", run)
    assert run["exit_code"] == 0, run
    rows = [json.loads(line) for line in (REPORTS / "A41-raster-results.jsonl").read_text().splitlines()]
    pictures = {}
    for source in sorted(WORK.glob("A41-*.bmp")):
        destination = REPORTS / source.with_suffix(".png").name
        with Image.open(source) as image:
            image.save(destination)
        pictures[destination.name] = identity(destination)
        with Image.open(destination) as image:
            pictures[destination.name].update(dimensions=list(image.size),
                decoded_rgba8_sha256=hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest())
        source.unlink()  # Own reproducible transient BMP; PNG retains identical pixels.
    reference = ROOT / "docs/design/atlas-cover-reference.jpg"
    v3 = ROOT / "examples/demos/standalone-interface-preview-v3/images/play-reference-1672x941.png"
    measures = {}
    for name, path in [("reference", reference), ("v3-original", v3),
                       ("before-fixed-state", REPORTS / "A41-reference-before.png"),
                       ("after-fixed-state", REPORTS / "A41-reference-after.png")]:
        measures[name] = {"image": identity(path), "title": ink(path, [595, 10, 1081, 65]),
                          "subtitle": ink(path, [600, 60, 1100, 106])}
    new = measures["after-fixed-state"]
    assert 461 <= new["title"]["width"] <= 467 and 32 <= new["title"]["height"] <= 34
    assert 19 <= new["title"]["bbox_half_open"][1] <= 21 and 833 <= new["title"]["center_x"] <= 837
    assert 367 <= new["subtitle"]["width"] <= 375 and 11 <= new["subtitle"]["height"] <= 13
    assert 70 <= new["subtitle"]["bbox_half_open"][1] <= 72 and 833.5 <= new["subtitle"]["center_x"] <= 837.5
    assert new["subtitle"]["occupied_column_runs"] == 15
    assert measures["before-fixed-state"]["title"] == measures["v3-original"]["title"]
    assert measures["before-fixed-state"]["subtitle"] == measures["v3-original"]["subtitle"]
    full = [row for row in rows if row["kind"] == "full"]
    frozen = [row for row in full if not row["sidebar"] or row["presentation"] == 1]
    changed = [row for row in full if row["sidebar"] and row["presentation"] == 0]
    result = {"schema": "a41-header-raster-v1", "completed_utc": now(), "summary": rows[-1],
              "complete_identical_frame_pairs": len(frozen), "changed_header_only_full_pairs": len(changed),
              "all_frozen_frames_identical": all(row["changed_pixels"] == 0 for row in frozen),
              "all_changes_header_only": all(row.get("outside_header", 0) == 0 for row in rows),
              "all_common_control_halos_unchanged": all(row.get("control_halo_changes", 0) == 0 for row in rows),
              "all_clips_contained": all(row.get("clip_leaks_after", 0) == 0 for row in rows),
              "measured_images": measures, "review_frames": pictures,
              "mask": "A36: R>=130, G>=105, R>=G, B<=0.9R inside named half-open ROI; no resampling or image registration.",
              "correction": "Root confirmed assignment old-caption x values were a transcription error. Original v3 is [769,93,888,100]. No target or budget changed.",
              "truthful_caption": "Source exact NOMINAL DRY ORGAN (17 characters, 15 nonspace glyphs); all 15 separate measured ink runs retained.",
              "limits": ["Fixed-state actual native software painter output, not a live app or physical display/DPI test.",
                         "Only four useful full-frame PNGs retained; comparison buffers are transient.",
                         "No literal whole-interface 1:1, audio/device/deadline or accessibility claim."]}
    output("A41-raster-acceptance.json", result)
    assert identity(SOURCE)["sha256"] == FINAL_SHA
    print(json.dumps({"raster": "passed", "summary": rows[-1], "identical_full_pairs": len(frozen),
                      "changed_header_only_full_pairs": len(changed), "new_ink": new}))


def timing():
    assert identity(SOURCE)["sha256"] == FINAL_SHA
    allowed = sorted(os.sched_getaffinity(0))
    assert 0 in allowed
    preflight = command([sys.executable, "-c", "import os,json;assert os.sched_getaffinity(0)=={0};print(json.dumps(sorted(os.sched_getaffinity(0))))"], affinity=[0])
    assert preflight["exit_code"] == 0
    report = {"schema": "a41-header-timing-v1", "started_utc": now(), "allowed_affinity": allowed,
              "actual_child_affinity": [0], "affinity_preflight": preflight, "runs": [],
              "same_a25_procedure": True, "cell": [1672, 941, "dimensional", "none"],
              "warmup_per_process": 30, "measured_draws_per_process": 300,
              "metric": "paint + explicit SDL flush + software surface present; capture/I/O excluded"}
    for label in ["before", "after"]:
        run = command([str(WORK / ("timing-" + label)), "1672", "941", "dimensional", "none"], affinity=[0])
        run["label"] = label
        report["runs"].append(run)
        output("A41-timing.json", report)
        assert run["exit_code"] == 0, run
        run["result"] = json.loads(run.pop("stdout"))
    old, new = [row["result"] for row in report["runs"]]
    stable = ["width", "height", "presentation", "overlay", "workspace", "warmup", "samples", "renderer",
              "renderer_flags", "sdl_version", "surface_format", "surface_bytes", "render_batching", "scale",
              "viewport", "clip", "clock", "clock_period", "layout_fnv1a64", "upper_c_hit_depth"]
    assert all(old[key] == new[key] for key in stable)
    change = new["total"]["p95_ms"] - old["total"]["p95_ms"]
    percentage = change / old["total"]["p95_ms"] * 100
    report.update(completed_utc=now(), identical_setting_keys=stable, p95_change_ms=change,
                  p95_change_percent=percentage, investigation_trigger=change > 2 and percentage > 15,
                  repeat_run=False, product_source_after=identity(SOURCE),
                  limits="One same-host software-raster cell; no display FPS, audio latency, deadline or cross-device guarantee.")
    output("A41-timing.json", report)
    print(json.dumps({"timing": "completed", "before": old["total"], "after": new["total"],
                      "p95_change_percent": percentage, "investigation_trigger": report["investigation_trigger"]}))


def repeat():
    # Sole authorized reversed repeat. Never replace or average away the first
    # threshold-triggering observation; a second repeat file is rejected.
    initial_path = REPORTS / "A41-timing.json"
    initial = json.loads(initial_path.read_text())
    assert initial["investigation_trigger"] is True
    assert not (REPORTS / "A41-timing-reverse-repeat.json").exists()
    assert identity(SOURCE)["sha256"] == FINAL_SHA
    build_report = json.loads((REPORTS / "A41-build.json").read_text())
    for item in build_report["binaries"]:
        assert identity(item["path"])["sha256"] == item["sha256"]
    report = {"schema": "a41-header-timing-reverse-repeat-v1", "started_utc": now(),
              "initial_trigger_report": identity(initial_path), "actual_child_affinity": [0],
              "order": ["after", "before"], "runs": [], "warmup_per_process": 30,
              "measured_draws_per_process": 300, "sole_authorized_repeat": True,
              "runner": identity(Path(__file__)),
              "quiet_scope": "Root and observed sibling workers suspended local work. A separate waveform-session checkout exists; exclusive host ownership is not claimed."}
    for label in ["after", "before"]:
        run = command([str(WORK / ("timing-" + label)), "1672", "941", "dimensional", "none"], affinity=[0])
        run["label"] = label
        report["runs"].append(run)
        output("A41-timing-reverse-repeat.json", report)
        assert run["exit_code"] == 0, run
        run["result"] = json.loads(run.pop("stdout"))
    new, old = [row["result"] for row in report["runs"]]
    stable = initial["identical_setting_keys"]
    assert all(old[key] == new[key] == initial["runs"][0]["result"][key] for key in stable)
    change = new["total"]["p95_ms"] - old["total"]["p95_ms"]
    percentage = change / old["total"]["p95_ms"] * 100
    report.update(completed_utc=now(), identical_setting_keys=stable, p95_change_ms=change,
                  p95_change_percent=percentage, investigation_trigger=change > 2 and percentage > 15,
                  product_source_after=identity(SOURCE),
                  limits="Retains both separate observations. Reversal cannot establish cause, statistical equivalence, FPS or audio deadline acceptance.")
    output("A41-timing-reverse-repeat.json", report)
    print(json.dumps({"reverse_repeat": "completed", "before": old["total"], "after": new["total"],
                      "p95_change_percent": percentage, "investigation_trigger": report["investigation_trigger"]}))


if __name__ == "__main__":
    {"build": build, "raster": raster, "timing": timing, "repeat": repeat}[sys.argv[1]]()
