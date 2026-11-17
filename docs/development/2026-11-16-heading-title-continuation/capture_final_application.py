#!/usr/bin/env python3
"""Capture two actual final-source installed views, preserving original BMP bytes.

Root-owned reproducible delivery operation. Requires a coherently built and
installed application, Python and Pillow. The destination must not exist.
Uses the unchanged native gallery validator; never synthesizes app pixels.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--build-root", required=True, type=Path)
    parser.add_argument("--executable", required=True, type=Path)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root, build, app = (p.resolve(strict=True) for p in
                        (args.source_root, args.build_root, args.executable))
    sys.path.insert(0, str(root / "tools"))
    import capture_standalone_interface as capture
    from PIL import Image, __version__ as pillow_version

    output = args.output.absolute()
    if output.exists():
        raise ValueError("Refusing to overwrite an existing capture directory")
    app_before = capture.identity(app)
    capture.require(app_before["sha256"] == args.expected_sha256, "Wrong application identity")
    sources = capture.production_paths(root)
    builds = capture.build_paths(build)
    source_before = capture.inventory(sources, root)
    build_before = capture.inventory(builds, build)
    configuration = capture.configuration(build)
    output.mkdir()
    for name in ("inputs", "images", "diagnostics", "runs"):
        (output / name).mkdir()
    state = output / "inputs" / "controls.b3controls"
    script = output / "inputs" / "play-dimensional.b3uireplay"
    replay, event_count = capture.replay("play", "dimensional")
    state.write_text(capture.STATE, encoding="ascii")
    script.write_text(replay, encoding="ascii")
    inputs = capture.inventory([state, script], output)
    environment = {"SDL_AUDIODRIVER": "dummy", "SDL_VIDEODRIVER": "dummy",
                   "SDL_RENDER_DRIVER": "software"}
    report = {
        "schema_version": 1, "status": "incomplete",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Two actual relocated final-source application captures",
        "scope": "Dummy SDL audio/video and software rendering. No physical-device, native-accessibility, measured-model or whole-interface 1:1 claim.",
        "command": [sys.executable, *sys.argv], "platform": platform.platform(),
        "python": platform.python_version(), "pillow": pillow_version,
        "driver": capture.identity(Path(__file__)),
        "validator": capture.identity(Path(capture.__file__)),
        "executable": {"path": str(app), **app_before},
        "source": {"root": str(root), "files": source_before},
        "build": {"root": str(build), "files": build_before,
                  "selected_configuration": configuration},
        "inputs": inputs, "environment": environment, "cases": [],
    }
    report_path = output / "provenance.json"
    try:
        for name, width, height in (("play-reference-1672x941", 1672, 941),
                                    ("play-minimum-960x700", 960, 700)):
            working = output / "runs" / name
            working.mkdir()
            bmp, png = (output / "images" / (name + suffix) for suffix in (".bmp", ".png"))
            diagnostics = output / "diagnostics" / (name + ".json")
            command = [str(app), "--state", str(state), "--input-script", str(script),
                       "--workspace", "play", "--width", str(width), "--height", str(height),
                       "--sample-rate", "48000", "--buffer-frames", "512",
                       "--screenshot", str(bmp), "--diagnostics", str(diagnostics)]
            started = time.monotonic()
            process = subprocess.run(command, cwd=working, env={**os.environ, **environment},
                                     stdin=subprocess.DEVNULL, capture_output=True, timeout=12)
            case = {"name": name, "command": command, "returncode": process.returncode,
                    "seconds": time.monotonic() - started, "timeout_seconds": 12}
            report["cases"].append(case)
            (output / "diagnostics" / (name + ".stdout.log")).write_bytes(process.stdout)
            (output / "diagnostics" / (name + ".stderr.log")).write_bytes(process.stderr)
            capture.require(process.returncode == 0 and not process.stdout and not process.stderr,
                            "Native capture process failed; original outputs retained")
            case["validation"] = capture.validate(capture.read_json(diagnostics), width, height,
                                                   "play", "dimensional", event_count)
            case["diagnostics"] = capture.identity(diagnostics)
            original = bmp.read_bytes()
            with Image.open(bmp) as image:
                image.load()
                mode, size, pixels = image.mode, image.size, image.tobytes()
                capture.require(size == (width, height), "Unexpected native image size")
                image.save(png, format="PNG")
            with Image.open(png) as encoded:
                encoded.load()
                capture.require((encoded.mode, encoded.size, encoded.tobytes()) == (mode, size, pixels),
                                "PNG conversion changed native pixels")
            archive = bmp.with_suffix(".bmp.gz")
            archive.write_bytes(gzip.compress(original, mtime=0))
            capture.require(gzip.decompress(archive.read_bytes()) == original, "BMP archive mismatch")
            case["image"] = {"bmp": capture.identity(bmp), "bmp_archive": capture.identity(archive),
                             "png": capture.identity(png), "decoded_mode": mode,
                             "width": width, "height": height,
                             "decoded_sha256": hashlib.sha256(pixels).hexdigest(),
                             "png_preserves_native_pixels": True,
                             "original_bmp_preserved_losslessly": True}
            bmp.unlink()
            capture.require(capture.inventory([state, script], output) == inputs, "Capture changed inputs")
        capture.require(capture.inventory(sources, root) == source_before, "Production inputs changed")
        capture.require(capture.inventory(builds, build) == build_before, "Build inputs changed")
        capture.require(capture.identity(app) == app_before, "Installed application changed")
        report["all_recorded_inputs_unchanged"] = True
        report["status"] = "passed"
    finally:
        report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    files = capture.inventory([p for p in output.rglob("*") if p.is_file()], output)
    capture.write_json(output / "manifest.json", {"schema_version": 1, "files": files})
    print(json.dumps({"status": report["status"], "cases": len(report["cases"]),
                      "executable_sha256": app_before["sha256"], "output": str(output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
