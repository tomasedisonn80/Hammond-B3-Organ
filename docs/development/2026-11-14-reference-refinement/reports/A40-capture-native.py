"""Capture two actual frozen native endpoints; preserve all decoded pixels.

Usage: python A40-capture-native.py EXE SCRATCH_OUTPUT
The historical v3 inputs are read-only. This is not a new published gallery.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time

from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parents[4]
REPORTS = Path(__file__).resolve().parent
EXE = Path(sys.argv[1]).resolve()
OUTPUT = Path(sys.argv[2]).resolve()
FROZEN = {
    "apps/standalone/InstrumentView.cpp": "f323c8c2f5529b03c25deccb74f482d8b6312487492a45d14b94ef0e24cfbb6a",
    "apps/standalone/native_tests/test_standalone_material_acceptance.cpp": "66963058652bd0673a043e03f342c94d71fd3c07e2f37a0d1d94093cc4d4a134",
}


def identity(path):
    data = path.read_bytes()
    return {"path": str(path), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def freeze():
    for name, digest in FROZEN.items():
        assert identity(ROOT / name)["sha256"] == digest, name


def ink(path, roi):
    with Image.open(path) as original:
        image = original.convert("RGB")
    points = [(x, y) for y in range(roi[1], roi[3]) for x in range(roi[0], roi[2])
              if (lambda p: p[0] >= 130 and p[1] >= 105 and p[0] >= p[1]
                  and p[2] * 10 <= p[0] * 9)(image.getpixel((x, y)))]
    box = [min(x for x, _ in points), min(y for _, y in points),
           max(x for x, _ in points) + 1, max(y for _, y in points) + 1]
    return {"roi": roi, "bbox_half_open": box, "width": box[2] - box[0],
            "height": box[3] - box[1], "ink_pixels": len(points)}


freeze()
OUTPUT.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location("capture", ROOT / "tools/capture_standalone_interface.py")
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
inputs = ROOT / "examples/demos/standalone-interface-preview-v3/inputs"
state, script = OUTPUT / "controls.b3controls", OUTPUT / "play-dimensional.b3uireplay"
state.write_bytes((inputs / state.name).read_bytes())
script.write_bytes((inputs / script.name).read_bytes())
state_before = identity(state)
binary_before = identity(EXE)
environment = os.environ | {"SDL_AUDIODRIVER": "dummy", "SDL_VIDEODRIVER": "dummy",
                            "SDL_RENDER_DRIVER": "software"}
record = {"source_sha256": FROZEN, "executable": binary_before, "pillow": pillow_version,
          "base_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
          "input_state": state_before, "input_script": identity(script), "cases": []}
for width, height in ((1672, 941), (1400, 820)):
    freeze()
    name = f"A40-native-play-{width}x{height}"
    bmp, png = OUTPUT / (name + ".bmp"), REPORTS / (name + ".png")
    diagnostics = REPORTS / (name + ".json")
    command = [str(EXE), "--state", str(state), "--input-script", str(script), "--workspace", "play",
               "--width", str(width), "--height", str(height), "--sample-rate", "48000", "--buffer-frames", "512",
               "--screenshot", str(bmp), "--diagnostics", str(diagnostics)]
    started = time.monotonic()
    process = subprocess.run(command, cwd=OUTPUT, env=environment, stdin=subprocess.DEVNULL,
                             capture_output=True, timeout=30, check=False)
    (REPORTS / (name + ".stdout")).write_bytes(process.stdout)
    (REPORTS / (name + ".stderr")).write_bytes(process.stderr)
    assert process.returncode == 0, process.stderr.decode(errors="replace")
    checked = capture.validate(json.loads(diagnostics.read_text()), width, height, "play", "dimensional", 66)
    with Image.open(bmp) as original:
        rgba = original.convert("RGBA")
        rgba.save(png)
        digest = hashlib.sha256(rgba.tobytes()).hexdigest()
    with Image.open(png) as encoded:
        assert hashlib.sha256(encoded.convert("RGBA").tobytes()).hexdigest() == digest
    offset = (width - 1672) // 2
    title = ink(png, [595 + offset, 10, 1081 + offset, 65])
    caption = ink(png, [640 + offset, 65, 1030 + offset, 105])
    record["cases"].append({"size": [width, height], "command": command, "exit_code": process.returncode,
        "elapsed_seconds": time.monotonic() - started, "validated_native_endpoint": checked,
        "bmp": identity(bmp), "png": identity(png), "diagnostics": identity(diagnostics),
        "decoded_rgba8_sha256": digest, "title": title, "caption": caption})
freeze()
assert binary_before == identity(EXE)
assert state_before == identity(state)
record["source_executable_and_input_state_unchanged"] = True
record["boundaries"] = ["Actual native dummy-video/dummy-audio/software-renderer endpoints.",
    "PNG conversion preserves every decoded RGBA pixel; no edited image, generated artwork or v4 gallery.",
    "No physical-device, display/DPI, accessibility, deadline or literal 1:1 qualification."]
print(json.dumps(record, indent=2))
