#!/usr/bin/env python3
"""Read-only source audit plus bounded owned dry/crop observations for A18."""

from __future__ import annotations

import argparse
import ast
import ctypes
import datetime
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import struct
import subprocess
import sys
import tempfile
import time
import wave


ROOT = Path(__file__).resolve().parents[4]
BASE = "a411268fd498f65c083203137831bf5afed83bd8"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(path):
    data = path.read_bytes()
    return {"path": str(path), "bytes": len(data), "sha256": sha(data)}


def git(*arguments):
    return subprocess.run(["git", *arguments], cwd=ROOT, check=True,
                          capture_output=True, timeout=30).stdout


def f32(value):
    return struct.unpack("<f", struct.pack("<f", value))[0]


def source_audit():
    rows = []
    for raw in git("ls-tree", "-r", "-z", BASE).split(b"\0"):
        if not raw:
            continue
        info, name = raw.split(b"\t", 1)
        mode, kind, blob = info.decode().split()
        path = name.decode()
        source = ROOT / path
        if kind != "blob":
            raise AssertionError((kind, path))
        if not source.is_file() or source.is_symlink():
            rows.append({"path": path, "same": False, "reason": "missing-or-nonregular"})
            continue
        data = source.read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        rows.append({"path": path, "same": actual == blob, "base_git_blob": blob,
                     "current_git_blob": actual, "sha256": sha(data), "bytes": len(data)})
    groups = {
        "core_headers": lambda p: p.startswith(("src/", "include/")),
        "plugin": lambda p: p.startswith("plugins/"),
        "original_tests": lambda p: p.startswith("tests/"),
        "original_data": lambda p: p.startswith("data/"),
        "original_examples": lambda p: p.startswith("examples/"),
        "standalone_other_than_painter_and_cmake": lambda p: p.startswith("apps/standalone/")
            and p not in ("apps/standalone/InstrumentView.cpp", "apps/standalone/CMakeLists.txt"),
        "art_font_assets": lambda p: any(s in p.lower() for s in ("/assets/", "/art/", "fontdata", "atlas-cover-reference")),
    }
    summaries = {}
    for name, predicate in groups.items():
        selected = [row for row in rows if predicate(row["path"])]
        summaries[name] = {"count": len(selected), "equal": sum(r["same"] for r in selected),
                           "differences": [r["path"] for r in selected if not r["same"]]}
    payload = ["tools/" + name for name in (
        "fractional_contact_reference.py", "contact_switching_io.py",
        "contact_switching_reference.py", "contact_switching_oracle.py",
        "contact_switching_study.py", "make_contact_switching_fixtures.py")]
    payload += ["docs/" + name for name in (
        "FRACTIONAL_CONTACT_REFERENCE.md", "CONTACT_SWITCHING_VALIDATION.md",
        "CONTACT_SWITCHING_GUIDE.md", "CONTACT_REFERENCE_INSTALL.md")]
    payload += [f"data/contact-switching/reference-v1/F{recipe:02d}-{rate}-v1.json"
                for recipe in range(12) for rate in (44100, 48000, 96000)]
    payload += ["data/contact-switching/reference-v1/" + name
                for name in ("manifest.json", "probes.json")]
    assert len(payload) == 48 and len(set(payload)) == 48
    by_path = {row["path"]: row for row in rows}
    selected = [by_path[path] for path in payload]
    critical_paths = ["Hammond_B3_Leslie_Research_Atlas_500pp.pdf",
        "include/hammond/Types.h", "include/hammond/Engine.h", "src/Engine.cpp",
        "include/hammond/ControlStateIO.h", "src/ControlStateIO.cpp",
        "src/TonewheelBank.cpp", "src/ContactBank.cpp", "src/ParameterBridge.cpp",
        "include/hammond/ParameterBridge.h", "data/parameter-registry.json",
        "plugins/vst3/PluginIds.h", "apps/standalone/UiModel.h",
        "apps/standalone/UiModel.cpp", "cmake/InstallContactReferenceTools.cmake"]
    critical = [by_path[path] for path in critical_paths]
    assert all(r["same"] for r in selected + critical)
    assert all(v["equal"] == v["count"] for v in summaries.values())
    descriptors = re.findall(r'\{([0-9]+)U, "([^"\n]+)"', (ROOT / "src/ParameterBridge.cpp").read_text())
    assert len(descriptors) == 47 and len({r[0] for r in descriptors}) == 47
    return {"base": BASE, "head": git("rev-parse", "HEAD").decode().strip(),
            "tree": git("rev-parse", "HEAD^{tree}").decode().strip(),
            "tracked_count": len(rows), "equal_count": sum(r["same"] for r in rows),
            "differences": [r for r in rows if not r["same"]], "groups": summaries,
            "critical_identities": critical, "parameter_descriptors": descriptors,
            "original_contact_reference_payload": selected,
            "tracked_overlay_diff_sha256": sha(git("diff", BASE, "--")),
            "scope": "Audit-time original Git blobs; newly added files are inventoried separately."}


def python_imports():
    local = {"contact_grid_conversion", "contact_switching_io", "fractional_contact_reference"}
    paths = ["tools/contact_grid_conversion.py", "tools/convert_contact_grid.py",
             "tools/contact_switching_io.py", "tools/fractional_contact_reference.py"]
    rows = []
    for name in paths:
        path = ROOT / name
        tree = ast.parse(path.read_text(), filename=name)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert node.level == 0
                imports.append(node.module)
        other = sorted(set(m for m in imports if m.split(".")[0] not in sys.stdlib_module_names | local))
        assert not other, (name, other)
        dynamic = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Name) and node.func.id == "__import__"]
        assert not dynamic
        rows.append({**identity(path), "imports": sorted(set(imports)),
                     "nonstdlib_nonlocal_imports": other, "direct_dynamic_import_calls": len(dynamic)})
    # No native runtime file refers to either new Python converter module.
    references = []
    for directory in ("src", "include", "apps", "plugins"):
        for path in (ROOT / directory).rglob("*"):
            if path.is_file() and path.suffix in (".h", ".cpp", ".cmake", ".txt"):
                text = path.read_text(errors="replace")
                if "contact_grid_conversion" in text or "convert_contact_grid" in text:
                    references.append(str(path.relative_to(ROOT)))
    assert not references
    return {"files": rows, "native_runtime_references": references,
            "scope": "Static import graph for both new tools and their two unchanged local dependencies."}


def dry_comparison(work):
    profile = ROOT.parent / "baseline/nominal.b3p"
    names = {"before": ROOT.parent / "baseline/hammond_render",
             "candidate": ROOT.parent / "build-native/hammond_render"}
    rows, waves, pcm = {}, {}, {}
    for name, executable in names.items():
        output = work / (name + ".wav")
        command = [str(executable), "--profile", str(profile), "--output", str(output),
                   "--frames", "8192", "--sample-rate", "48000", "--block-size", "64",
                   "--seed", "0", "--drawbars", "888000000", "--note", "60", "--fail-on-clip"]
        start = time.monotonic()
        run = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30)
        elapsed = time.monotonic() - start
        assert run.returncode == 0 and not run.stderr
        data = output.read_bytes()
        assert len(data) < 65536
        with wave.open(str(output), "rb") as reader:
            params = {"channels": reader.getnchannels(), "sample_width": reader.getsampwidth(),
                      "sample_rate": reader.getframerate(), "frames": reader.getnframes(),
                      "compression": reader.getcomptype()}
            samples = reader.readframes(reader.getnframes())
        assert params == {"channels": 2, "sample_width": 2, "sample_rate": 48000,
                          "frames": 8192, "compression": "NONE"}
        waves[name], pcm[name] = data, samples
        rows[name] = {"command": command, "executable": identity(executable),
                      "exit_code": run.returncode, "process_seconds": elapsed,
                      "stdout": run.stdout.decode(), "stderr": run.stderr.decode(),
                      "wav_bytes": len(data), "wav_sha256": sha(data),
                      "pcm_bytes": len(samples), "pcm_sha256": sha(samples), "metadata": params}
    before = struct.unpack("<16384h", pcm["before"])
    after = struct.unpack("<16384h", pcm["candidate"])
    differences = [abs(a-b) for a, b in zip(before, after)]
    assert waves["before"] == waves["candidate"] and max(differences) == 0
    return {"profile": identity(profile), "current_profile": identity(ROOT.parent / "build-native/nominal.b3p"),
            "runs": rows, "whole_wav_equal": True, "decoded_sample_count": len(differences),
            "different_samples": sum(x != 0 for x in differences), "maximum_absolute_pcm_difference": max(differences),
            "temporary_wavs": "Both original outputs hashed and decoded before owned TemporaryDirectory cleanup; raw WAV bytes not retained."}


def crops():
    executables = {"before": ROOT.parent / "baseline/test_standalone_lower_rack_material_raster",
                   "candidate": ROOT.parent / "build-native/apps/standalone/test_standalone_lower_rack_material_raster"}
    identities = {name: identity(path) for name, path in executables.items()}
    results = []
    for index, scale in ((24, 1.0), (25, 1.5), (26, 2.0)):
        pair = {"case": index, "expected_logical_size": [8192, 8192], "expected_renderer_scale": [scale, scale], "runs": {}}
        headers, pixels = {}, {}
        for name, executable in executables.items():
            command = [str(executable), "--case", str(index)]
            start = time.monotonic()
            run = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=30)
            elapsed = time.monotonic() - start
            assert run.returncode == 0 and not run.stderr and len(run.stdout) < 131072
            raw, rgba = run.stdout.split(b"\n", 1)
            header = json.loads(raw)
            assert header["case"] == index and header["output_size"] == [64, 64]
            assert header["scale"] == [scale, scale] and header["resource_crop"] is True
            assert len(rgba) == 64*64*4 and header["bytes"] == len(rgba)
            headers[name], pixels[name] = header, rgba
            pair["runs"][name] = {"command": command, "exit_code": run.returncode,
                                  "process_seconds": elapsed, "header": header,
                                  "header_sha256": sha(raw), "rgba_sha256": sha(rgba),
                                  "rgba_bytes": len(rgba), "stderr": run.stderr.decode()}
        assert headers["before"] == headers["candidate"]
        pair["metadata_equal"] = True
        pair["different_rgba_bytes"] = sum(a != b for a,b in zip(pixels["before"], pixels["candidate"]))
        results.append(pair)
    height = 8192
    sy = f32(height/941)
    by = f32(269*sy)
    bh = f32(f32(508*sy)-by)
    dy = f32(4*sy)
    iy, ih = f32(by+dy), max(0, f32(bh-f32(2*dy)))
    rows = math.ceil((float(iy)+float(ih))*2-.5) - math.ceil(float(iy)*2-.5)
    assert rows <= 4028
    return {"executables": identities, "pairs": results,
            "source_bounds": {"columns": 127, "edge_array_ints": 128,
                "int_bytes_on_observed_python_abi": ctypes.sizeof(ctypes.c_int),
                "grain_pairs": 2304, "grain_marks": 4608, "mix_calls": 9216,
                "contract_max_visible_rows": 4028, "max_geometry_unclipped_rows": rows,
                "contract_drawing_primitive_bound": 127*4028+4608,
                "crop_drawing_primitive_bound": 127*64+4608},
            "scope": "Six isolated process/crop observations, including startup and whole fixture paint. No full-size allocation, frame deadline, SDL allocation, callback or exterior-containment claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("choose a new output path; original evidence is never overwritten")
    watched = [ROOT / name for name in ("tools/contact_grid_conversion.py", "tools/convert_contact_grid.py",
               "apps/standalone/InstrumentView.cpp", "apps/standalone/native_tests/test_standalone_lower_rack_material_raster.cpp")]
    initial = [identity(path) for path in watched]
    report = {"schema_version": 1, "worker": "/root/w03_a18", "cwd": str(ROOT),
              "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "command": [sys.executable, *sys.argv], "python": platform.python_version(),
              "platform": platform.platform(), "script": identity(Path(__file__).resolve()),
              "watched_before": initial, "source_audit": source_audit(), "imports": python_imports()}
    with tempfile.TemporaryDirectory(prefix="A18-compatibility-", dir=ROOT.parent) as owned:
        report["dry_fixture"] = dry_comparison(Path(owned))
        report["resource_crops"] = crops()
    report["watched_after"] = [identity(path) for path in watched]
    assert initial == report["watched_after"], "production inputs changed during the audit"
    report["status"] = "passed-scoped-compatibility"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": report["status"], "tracked": report["source_audit"]["tracked_count"],
                      "equal": report["source_audit"]["equal_count"],
                      "different_samples": report["dry_fixture"]["different_samples"],
                      "crop_pairs": len(report["resource_crops"]["pairs"]),
                      "output": str(args.output)}))


if __name__ == "__main__":
    main()
