#!/usr/bin/env python3
"""Read-only identity/state audit of the original eight and three percussion captures.

This repeats retained capture validators. It is not an independent build or
visual-fidelity attestation, and it never launches the application or writes files.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from PIL import Image

sys.dont_write_bytecode = True


def identity(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Expected regular non-symlink file: {path}")
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def check_image(root: Path, record: dict) -> dict:
    path = root / record["path"]
    require(identity(path) == record["png"], f"PNG bytes changed: {path}")
    with Image.open(path) as image:
        image.load()
        digest = hashlib.sha256(image.tobytes()).hexdigest()
        require(image.mode == record["decoded_mode"] and
                image.size == (record["width"], record["height"]) and
                digest == record["decoded_sha256"], f"Decoded pixels changed: {path}")
    return {"path": record["path"], "png_sha256": record["png"]["sha256"],
            "decoded_sha256": digest, "width": record["width"], "height": record["height"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--exe", type=Path, required=True)
    args = parser.parse_args()
    repo, build, exe = (p.resolve(strict=True) for p in (args.repo, args.build, args.exe))
    old_root = repo / "examples/demos/standalone-audio-preview-v1"
    new_root = old_root / "percussion-states"
    old = json.loads((old_root / "provenance.json").read_text())
    new = json.loads((new_root / "provenance.json").read_text())
    require(old["status"] == new["status"] == "passed", "Capture receipt did not pass")
    for name, digest in {
        "manifest.json": "06fda1510542714ec1121bc8f4d2bbc65ce9be29d175ea16777d9666fb070050",
        "provenance.json": "2af9b3a573116c19ffc86633c59a19f4a382c219603a906d5c2d82342b02968e",
    }.items():
        require(identity(old_root / name)["sha256"] == digest, f"Original receipt changed: {name}")
    manifest_counts = []
    for root in (old_root, new_root):
        manifest = json.loads((root / "manifest.json").read_text())
        for relative, expected in manifest["files"].items():
            require(identity(root / relative) == expected, f"Manifest file changed: {relative}")
        manifest_counts.append(len(manifest["files"]))
    require(new["source_files"] == old["source"]["files"] and
            new["build_files"] == old["build"]["files"], "Capture source/build sets differ")
    for root, records in ((repo, new["source_files"]), (build, new["build_files"])):
        for relative, expected in records.items():
            require(identity(root / relative) == expected, f"Frozen input changed: {relative}")
    expected_exe = {key: new["executable"][key] for key in ("bytes", "sha256")}
    require(identity(exe) == expected_exe == old["executable"]["before"] ==
            old["executable"]["after"], "Frozen executable changed")
    author_path = repo / "docs/development/2026-11-15-audio-continuation/reports/w03-source.json"
    require(identity(author_path) == identity(old_root / "inputs/source-qualification.json"),
            "Original source receipt copy changed")
    author = json.loads(author_path.read_text())
    for relative, digest in author["source_sha256"].items():
        require(identity(repo / relative)["sha256"] == digest, f"Author source changed: {relative}")
    require(author["binary_sha256"] == expected_exe["sha256"], "Author binary differs")
    require(old["inputs"]["before"] == old["inputs"]["after"], "Original inputs were changed")
    for relative, expected in old["inputs"]["before"].items():
        require(identity(old_root / relative) == expected, f"Original input changed: {relative}")
    require(identity(new_root / "inputs/controls.b3controls") == new["state_before"], "New input state changed")
    capture_path = repo / "tools/capture_standalone_interface.py"
    require(identity(capture_path) == old["tool"]["before"] == old["tool"]["after"], "Capture utility changed")
    require(identity(new_root / "reproduce.py") == new["script"], "Percussion capture utility changed")
    original_capture = module(capture_path, "original_capture")
    percussion_capture = module(new_root / "reproduce.py", "percussion_capture")
    result = {"status": "passed", "original_manifest_files": manifest_counts[0],
              "percussion_manifest_files": manifest_counts[1],
              "production_files": len(new["source_files"]), "build_files": len(new["build_files"]),
              "author_receipt_sources": len(author["source_sha256"]), "executable": expected_exe,
              "original_cases": [], "percussion_cases": [],
              "limits": "Reuses retained validators; BMP bytes were removed after original lossless conversion. No compiler, physical-device or full-reference-fidelity attestation."}
    require(len(old["cases"]) == 8 and len(new["cases"]) == 3, "Unexpected gallery case count")
    for case in old["cases"]:
        diag = json.loads((old_root / case["diagnostics"]["path"]).read_text())
        observed = original_capture.validate(diag, case["width"], case["height"],
            case["workspace"], case["presentation"], case["validation"]["ui_events"])
        require(observed == case["validation"], f"Original state changed: {case['name']}")
        result["original_cases"].append({"name": case["name"], **check_image(old_root, case["image"]),
                                         "recorded_state_validated": True})
    for case in new["cases"]:
        diag_path = new_root / "diagnostics" / f"{case['name']}.json"
        require(identity(diag_path) == case["diagnostics"], "Percussion diagnostics changed")
        replay_path = new_root / "inputs" / f"{case['name']}.b3uireplay"
        require(identity(replay_path) == case["script"], "Percussion replay changed")
        replay, events = percussion_capture.script(case["name"])
        require(replay_path.read_text() == replay, "Percussion event definition changed")
        observed = percussion_capture.validate(json.loads(diag_path.read_text()),
            case["validation"]["full_control_snapshot"], case["image"]["width"],
            case["image"]["height"], events)
        require(observed == case["validation"], f"Percussion state changed: {case['name']}")
        image_record = check_image(new_root, case["image"])
        x, y, w, h = case["expected_focus"]["contracted_bounds"]
        with Image.open(new_root / case["image"]["path"]) as image:
            cyan = [(px, py) for py in range(max(0, int(y)-3), min(image.height, int(y+h)+4))
                    for px in range(max(0, int(x)-3), min(image.width, int(x+w)+4))
                    if image.getpixel((px, py))[:3] == (165, 228, 223)]
        require(len(cyan) == case["expected_focus"]["observed_cyan_pixels"] > 150,
                f"Focused cap ink changed: {case['name']}")
        result["percussion_cases"].append({"name": case["name"], **image_record,
            "recorded_state_validated": True, "observed_cyan_pixels": len(cyan)})
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
