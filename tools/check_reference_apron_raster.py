#!/usr/bin/env python3
"""Independent, bounded consumer of the frozen reference-apron-v1 fixtures.

Requires Pillow and NumPy only for offline raster admission. No producer mask,
production Python helper, generated art or reconstructed baseline is consumed.
All case arguments are zero based; report contract_case values are one based.
"""
from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import re
import struct
import subprocess
import sys
import threading
from typing import BinaryIO


PROTOCOL = "reference-apron-v1"
HEADER_MAX = 65536
DIMENSION_MAX = 4096
PAYLOAD_MAX = 67108864
BASELINE_SHA256 = "8391cb06222f7f9eb61381f86631dce364752022dbc4faa14c22fab4ae7f35e6"
FIXTURE_SHA256 = "59cecf6ba99bf9361f506954758a500845f2298bf934ceef27ba69d995743f73"
MANIFEST_SHA256 = "6a75548862cd7d313e07b7a21827f5acfd3d97533e02e7fccecf73611d7d832e"
LIST_SHA256 = "be9bacfd9bfa3b53a0f60eaaf37fd5ccb811babcf556ad94b9c79fe536c51793"
CONTRACT_SHA256 = "c07c08895d8f985a95c34630ddc19c51ed1a3d3771cac4918a614de90bc879d0"
JPEG_SHA256 = "9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187"
RGB_SHA256 = "07a7e35a2fd6610d623bbc1da8c995f3f4d95c4b45a0a5c1f41ad1395584bbeb"
SESSION = "docs/development/2026-11-16-preset-library-continuation"
FIXTURE = "apps/standalone/native_tests/test_standalone_reference_apron_raster.cpp"
MANIFEST = "docs/design/reference-apron-fixtures.json"
CONTRACT = "docs/design/REFERENCE_APRON_CONTRACT.md"
JPEG = "docs/design/atlas-cover-reference.jpg"
EXACT_CASES = frozenset((13, 14, 15, 20, 21, 22, 23, 24))
# Contract rectangles are endpoints here, not a producer-supplied allowance.
R = (16, 887, 1656, 941)
F = (48, 889, 1604, 925)
HEADER_KEYS = frozenset("schema protocol case contract_case name logical_size width height "
    "output_size scale viewport clip logical_viewport logical_clip clip_enabled blend "
    "clip_kind renderer model info bytes".split())
VIEW_KEYS = frozenset("controls applied edited_banks focus roving_manual_keys roving_pedal_key "
    "keyboard_target manual_base_midi pedal_octave controls_pending controls_dirty text_entry_active "
    "pointer_captured input_recovery last_submit_status workspace presentation workspace_focus".split())
LAYOUT_RECT_KEYS = ("header", "performance_panel", "keyboard_toolbar", "pedal_panel", "footer",
                    "cabinet_panel", "cabinet_art", "workspace_panel")
LAYOUT_PAIR_KEYS = ("registration_panels", "manual_panels", "manual_rail_panels", "preset_key_panels")
LAYOUT_KEYS = frozenset(LAYOUT_RECT_KEYS + LAYOUT_PAIR_KEYS + ("width", "height", "show_cabinet",
    "bank_controls_in_cheeks", "sidebar_pedals", "control_count", "workspace", "presentation"))
RENDERER_KEYS = frozenset("name flags texture_formats max_texture_size compiled_sdl runtime_sdl surface_format".split())


class AdmissionError(ValueError):
    """Rejected evidence, rather than an admitted partial result."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AdmissionError(message)


def numpy_module():
    """Pure transport/mask consumers do not acquire offline pixel dependencies."""
    try:
        import numpy
        return numpy
    except ImportError as error:
        raise AdmissionError("offline pixel comparisons require optional NumPy") from error


def offline_dependencies():
    try:
        import numpy
        import PIL
        from PIL import Image
        return numpy, PIL, Image
    except ImportError as error:
        raise AdmissionError(
            "paired raster admission requires optional NumPy and Pillow; "
            "use an offline verification environment with both installed. "
            "Transport and geometry tests do not require these packages."
        ) from error


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        result = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def _object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON member: {key}")
        result[key] = value
    return result


def strict_json(data: bytes):
    def reject_constant(value):
        raise AdmissionError(f"nonfinite JSON constant: {value}")

    def finite_tree(value, depth=0):
        require(depth <= 32, "JSON nesting exceeds 32")
        if isinstance(value, float):
            require(math.isfinite(value), "nonfinite JSON number")
        elif isinstance(value, dict):
            for item in value.values():
                finite_tree(item, depth + 1)
        elif isinstance(value, list):
            for item in value:
                finite_tree(item, depth + 1)

    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_object, parse_constant=reject_constant)
        finite_tree(value)
        return value
    except (UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
        raise AdmissionError(f"invalid UTF-8 JSON: {error}") from error


def integer(value, minimum=0, maximum=2**64 - 1) -> bool:
    return type(value) is int and minimum <= value <= maximum


def number(value) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def same(actual, expected) -> bool:
    """JSON numbers may vary in spelling; booleans never alias zero or one."""
    if isinstance(expected, bool) or expected is None or isinstance(expected, str):
        return type(actual) is type(expected) and actual == expected
    if number(expected):
        return number(actual) and actual == expected
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(
            same(a, b) for a, b in zip(actual, expected))
    if isinstance(expected, dict):
        return isinstance(actual, dict) and actual.keys() == expected.keys() and all(
            same(actual[key], value) for key, value in expected.items())
    return False


def keys(value, expected, where):
    require(isinstance(value, dict) and value.keys() == expected, f"{where}: missing or extra members")


@dataclass
class Frame:
    header: dict
    header_bytes: bytes
    pixels: bytes

    def array(self):
        np = numpy_module()
        return np.frombuffer(self.pixels, dtype=np.uint8).reshape(
            self.header["height"], self.header["width"], 4)

    def identity(self):
        return {"header_sha256": sha256(self.header_bytes), "rgba_sha256": sha256(self.pixels),
                "header_bytes": len(self.header_bytes), "rgba_bytes": len(self.pixels)}


def read_frame(stream: BinaryIO) -> Frame:
    """Read only the bounded header, exact declared payload, and one EOF probe."""
    line = stream.readline(HEADER_MAX + 1)
    require(len(line) <= HEADER_MAX, "header exceeds 64 KiB including LF")
    require(line.endswith(b"\n") and b"\r" not in line, "header needs one LF, not CRLF or EOF")
    header = strict_json(line)
    keys(header, HEADER_KEYS, "header")
    require(header["schema"] == 1 and type(header["schema"]) is int and
            header["protocol"] == PROTOCOL, "wrong schema or protocol")
    width, height, count = header["width"], header["height"], header["bytes"]
    require(integer(width, 1, DIMENSION_MAX) and integer(height, 1, DIMENSION_MAX),
            "output dimensions must be integers from 1 through 4096")
    require(integer(count, 1, PAYLOAD_MAX) and count == width * height * 4, "incorrect RGBA byte extent")
    require(same(header["output_size"], [width, height]), "output_size contradicts dimensions")
    pixels = bytearray()
    while len(pixels) < count:
        block = stream.read(min(65536, count - len(pixels)))
        require(bool(block), f"short RGBA payload: expected {count}, got {len(pixels)}")
        pixels.extend(block)
    require(stream.read(1) == b"", "extra bytes after exact RGBA payload")
    return Frame(header, line, bytes(pixels))


def run_bounded(command: list[str], limit: int, timeout: float) -> bytes:
    """Bound both pipes while running; neither communicate() nor a disk spool is unbounded."""
    require(0 < limit <= HEADER_MAX + PAYLOAD_MAX, "invalid subprocess output limit")
    output, diagnostic = bytearray(), bytearray()
    faults = []
    with subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE) as process:
        def collect(pipe, target, maximum, name):
            try:
                while True:
                    chunk = pipe.read(min(65536, maximum - len(target) + 1))
                    if not chunk:
                        return
                    if len(target) + len(chunk) > maximum:
                        faults.append(f"{name} exceeds {maximum} bytes")
                        process.kill()
                        return
                    target.extend(chunk)
            except (OSError, ValueError) as error:
                faults.append(f"{name} read failed: {error}")

        readers = [threading.Thread(target=collect, args=(process.stdout, output, limit, "stdout"), daemon=True),
                   threading.Thread(target=collect, args=(process.stderr, diagnostic, HEADER_MAX, "stderr"), daemon=True)]
        for reader in readers:
            reader.start()
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            faults.append(f"subprocess exceeded {timeout:g} seconds")
            process.kill()
            process.wait(timeout=5)
        for reader in readers:
            reader.join(timeout=5)
        require(not any(reader.is_alive() for reader in readers), "subprocess pipe failed to close")
        require(not faults, "; ".join(faults))
        require(process.returncode == 0, f"subprocess exit {process.returncode}: " +
                diagnostic.decode("utf-8", errors="replace")[:4096])
        require(not diagnostic, "unexpected fixture stderr: " + diagnostic.decode("utf-8", errors="replace")[:4096])
    return bytes(output)


def f32(value):
    return struct.unpack("=f", struct.pack("=f", value))[0]


def mapped_rect(rect, logical_size):
    """Binary32 endpoint mapping in the frozen public UI contract, including stored extents."""
    sx, sy = f32(f32(logical_size[0]) / 1672.0), f32(f32(logical_size[1]) / 941.0)
    left, top = f32(rect[0] * sx), f32(rect[1] * sy)
    right, bottom = f32(rect[2] * sx), f32(rect[3] * sy)
    return left, top, f32(right - left), f32(bottom - top)


def physical_edges(rect, header):
    left, top, width, height = mapped_rect(rect, header["logical_size"])
    sx, sy = header["scale"]
    vx, vy = header["viewport"][:2]
    return (vx + f32(left * sx), vy + f32(top * sy),
            vx + f32(f32(left + width) * sx), vy + f32(f32(top + height) * sy))


def intersect(*boxes):
    left, top = max(b[0] for b in boxes), max(b[1] for b in boxes)
    right, bottom = min(b[2] for b in boxes), min(b[3] for b in boxes)
    return left, top, max(left, right), max(top, bottom)


def area(box):
    return (box[2] - box[0]) * (box[3] - box[1])


def extent_rect(rect):
    return rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3]


def center_box(edges):
    # x+.5 >= left and x+.5 < right, with no tolerance or extra boundary pixel.
    return tuple(math.ceil(value - 0.5) for value in edges)


def masks(header):
    output = (0, 0, header["width"], header["height"])
    viewport = extent_rect(header["viewport"])
    visible = intersect(output, viewport)
    if header["clip_enabled"]:
        cx, cy, cw, ch = header["clip"]
        vx, vy = header["viewport"][:2]
        visible = intersect(visible, (vx + cx, vy + cy, vx + cx + cw, vy + cy + ch))
    view = header["model"]["view"]
    width, height = header["logical_size"]
    active = view["workspace"] == 0 and view["presentation"] == 0 and 1400 <= width <= 4096 and 820 <= height <= 4096
    r, footer = physical_edges(R, header), physical_edges(F, header)
    envelope = (math.floor(r[0]), math.floor(r[1]), math.ceil(r[2]), math.ceil(r[3]))
    empty = (0, 0, 0, 0)
    allowed = intersect(envelope, visible) if active else empty
    interior = intersect(center_box(r), visible) if active else empty
    protected_footer = intersect(center_box(footer), output) if active else empty
    footer_visible = intersect(protected_footer, visible)
    return {"active": active, "mapped_R_edges": list(r), "mapped_F_edges": list(footer),
            "visible_box": visible, "allowed_box": allowed, "apron_center_box": interior,
            "footer_center_box": protected_footer, "frame_pixels": area(output),
            "visible_pixels": area(visible), "allowed_pixels": area(allowed),
            "apron_center_pixels": area(interior), "visible_exterior_pixels": area(visible) - area(interior),
            "visible_outside_allowance_pixels": area(visible) - area(allowed),
            "protected_outside_pixels": area(output) - area(allowed),
            "footer_center_pixels": area(protected_footer), "footer_visible_center_pixels": area(footer_visible)}


def box_count(changed, box):
    np = numpy_module()
    return int(np.count_nonzero(changed[box[1]:box[3], box[0]:box[2]]))


def difference_counts(before, after, mask):
    np = numpy_module()
    changed = np.any(before != after, axis=2)
    total = int(np.count_nonzero(changed))
    return {"changed_pixels": total,
            "outside_allowed_changed_pixels": total - box_count(changed, mask["allowed_box"]),
            "footer_changed_pixels": box_count(changed, mask["footer_center_box"])}


def _set_path(value, path, replacement):
    require(re.fullmatch(r"[a-z_]+(?:\[\d+\])*(?:\.[a-z_]+(?:\[\d+\])*)*", path) is not None,
            "invalid frozen state path")
    parts = [int(p) if p.isdecimal() else p for p in re.findall(r"[a-z_]+|\d+", path)]
    for part in parts[:-1]:
        value = value[part]
    value[parts[-1]] = replacement


def expected_state(manifest, spec):
    applied = copy.deepcopy(manifest["state_defaults"]["session"])
    # The frozen C++ serializer writes these two boolean routing flags as 0/1.
    applied["controls"]["route_enabled"] = list(map(int, applied["controls"]["route_enabled"]))
    profile = manifest["state_profiles"][spec["state_profile"]]
    for path, value in profile["session_changes"].items():
        _set_path(applied, path, value)
    info = copy.deepcopy(manifest["state_defaults"]["info"])
    info.update(profile["info_changes"])
    desired = copy.deepcopy(applied["controls"])
    pending = spec["state_profile"] == "pending"
    recovery = spec["state_profile"] == "recovery"
    focus = [0, 0, 0, 0]
    if spec["workspace"]:
        focus = [20, 0, 0, spec["workspace"]]
    if pending:
        focus = profile["expected"]["focus"]
        desired["selected_banks"] = profile["expected"]["desired_selected_banks"]
        desired["drawbars"][1][1][4] = profile["expected"]["desired_lower_B_drawbar4"]
    view = {"controls": desired, "applied": applied, "edited_banks": [1, 1], "focus": focus,
            "roving_manual_keys": [24, 24], "roving_pedal_key": 0, "keyboard_target": 0,
            "manual_base_midi": 60, "pedal_octave": 0, "controls_pending": pending,
            "controls_dirty": pending or spec["state_profile"] == "running", "text_entry_active": False,
            "pointer_captured": False, "input_recovery": recovery, "last_submit_status": 11 if recovery else 0,
            "workspace": spec["workspace"], "presentation": spec["presentation"],
            "workspace_focus": [focus if pending else [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]}
    return view, info


def validate_metadata(header, manifest, index):
    spec = manifest["cases"][index]
    for key in ("case", "contract_case", "name", "logical_size", "output_size", "scale", "viewport",
                "clip", "clip_enabled", "blend", "clip_kind"):
        require(same(header[key], spec[key]), f"case {index}: {key} differs from frozen inputs")
    require(integer(header["case"], 0, 24) and integer(header["contract_case"], 1, 25), "invalid case numbering")
    for key in ("viewport", "clip", "logical_viewport", "logical_clip"):
        require(isinstance(header[key], list) and len(header[key]) == 4 and
                all(integer(v, 0, 8192) for v in header[key]), f"invalid {key}")
    for physical, logical in (("viewport", "logical_viewport"), ("clip", "logical_clip")):
        expected = [int(f32(value / header["scale"][i % 2])) for i, value in enumerate(header[physical])]
        require(same(header[logical], expected), f"{logical} contradicts queried physical transform")
    renderer = header["renderer"]
    keys(renderer, RENDERER_KEYS, "renderer")
    require(renderer["name"] == "software" and integer(renderer["flags"], 1, 2**32 - 1)
            and renderer["flags"] & 1, "not the declared software renderer")
    require(isinstance(renderer["texture_formats"], list) and 0 < len(renderer["texture_formats"]) <= 16
            and all(integer(v, 1, 2**32 - 1) for v in renderer["texture_formats"]), "invalid texture formats")
    for key, size in (("max_texture_size", 2), ("compiled_sdl", 3), ("runtime_sdl", 3)):
        require(isinstance(renderer[key], list) and len(renderer[key]) == size and
                all(integer(v, 0, 65535) for v in renderer[key]), f"invalid renderer {key}")
    require(renderer["surface_format"] in ("SDL_PIXELFORMAT_ABGR8888", "SDL_PIXELFORMAT_RGBA8888"), "not RGBA32")
    keys(header["model"], {"view", "layout"}, "model")
    keys(header["model"]["view"], VIEW_KEYS, "model.view")
    view, info = expected_state(manifest, spec)
    require(same(header["model"]["view"], view), "complete copied view/session differs from frozen state")
    require(same(header["info"], info), "complete view info differs from frozen state")
    layout = header["model"]["layout"]
    keys(layout, LAYOUT_KEYS, "model.layout")
    require(same([layout["width"], layout["height"]], spec["logical_size"]) and
            same(layout["workspace"], spec["workspace"]) and same(layout["presentation"], spec["presentation"])
            and type(layout["control_count"]) is int and layout["control_count"] == 68, "layout identity differs")
    for key in ("show_cabinet", "bank_controls_in_cheeks", "sidebar_pedals"):
        require(type(layout[key]) is bool, f"invalid layout {key}")
    for key in LAYOUT_RECT_KEYS + LAYOUT_PAIR_KEYS:
        rectangles = layout[key] if key in LAYOUT_PAIR_KEYS else [layout[key]]
        require(isinstance(rectangles, list) and len(rectangles) == (2 if key in LAYOUT_PAIR_KEYS else 1),
                f"invalid layout {key} extent")
        for rect in rectangles:
            require(isinstance(rect, list) and len(rect) == 4 and all(number(v) for v in rect)
                    and rect[2] >= 0 and rect[3] >= 0, f"invalid layout rectangle {key}")
    mask = masks(header)
    if mask["active"]:
        require(tuple(map(f32, layout["footer"])) == mapped_rect(F, header["logical_size"]),
                "actual footer does not follow frozen binary32 endpoint mapping")
    if 8 <= index <= 14:
        bottom = mask["mapped_R_edges"][3]
        require(header["height"] >= bottom + 2 and header["viewport"][1] + header["viewport"][3] >= bottom + 2,
                "translated viewport/output lost required bottom exterior")
    if 9 <= index <= 12:
        require(mask["apron_center_pixels"] > 0 and mask["visible_outside_allowance_pixels"] > 0,
                "edge strip has vacuous interior or protected exterior")


def frozen_inputs(repo, receipt_path):
    np, _, Image = offline_dependencies()
    for path, expected in ((FIXTURE, FIXTURE_SHA256), (MANIFEST, MANIFEST_SHA256),
                           (CONTRACT, CONTRACT_SHA256), (JPEG, JPEG_SHA256)):
        require(digest(repo / path) == expected, f"frozen input differs: {path}")
    manifest = strict_json((repo / MANIFEST).read_bytes())
    receipt = strict_json(receipt_path.read_bytes())
    for field, expected in (("executable_sha256", BASELINE_SHA256), ("fixture_sha256", FIXTURE_SHA256),
                            ("manifest_sha256", MANIFEST_SHA256), ("list_sha256", LIST_SHA256)):
        require(receipt.get(field) == expected, f"genuine baseline receipt differs: {field}")
    require(manifest["case_count"] == 25 and len(manifest["cases"]) == 25, "not frozen25")
    require((repo / JPEG).stat().st_size == 412664, "source JPEG extent differs")
    with Image.open(repo / JPEG) as source:
        source.load()
        rgb = source.convert("RGB")
    require(rgb.size == (1672, 941) and sha256(rgb.tobytes()) == RGB_SHA256, "decoded source RGB differs")
    return manifest, np.asarray(rgb), receipt


def source_identity(repo):
    paths = (FIXTURE, MANIFEST, CONTRACT, JPEG, "docs/design/atlas-reference.json", "apps/standalone/Drawing.cpp",
             "apps/standalone/Drawing.h", "apps/standalone/InstrumentView.cpp", "apps/standalone/InstrumentView.h",
             "apps/standalone/UiModel.cpp", "apps/standalone/UiModel.h", "assets/standalone/reference-apron-v1/manifest.json",
             "apps/standalone/native_tests/reference_apron_unavailable_texture.cpp", "tools/compile_reference_apron.py")
    return {path: digest(repo / path) for path in paths}


def compare_source(frame, source):
    np = numpy_module()
    actual = frame.array()[887:941, 16:1656]
    expected = np.empty((54, 1640, 4), dtype=np.uint8)
    expected[:, :, :3] = source[887:941, 16:1656]
    expected[:, :, 3] = 255
    retained = np.ones((54, 1640), dtype=bool)
    retained[2:38, 32:1588] = False
    return {"source_pixels": int(np.count_nonzero(retained)),
            "unequal_source_pixels": int(np.count_nonzero(np.any(actual != expected, axis=2) & retained)),
            "candidate_R_minus_F_rgba_sha256": sha256(actual[retained].tobytes()),
            "source_R_minus_F_rgba_sha256": sha256(expected[retained].tobytes())}


def admission(args):
    np, pillow, _ = offline_dependencies()
    repo = args.repo.resolve()
    receipt_path = args.receipt.resolve() if args.receipt else repo / SESSION / "reports/apron-genuine-baseline.json"
    manifest, source, receipt = frozen_inputs(repo, receipt_path)
    executables = {"before": (args.before or repo.parent / "baseline-native/test_standalone_reference_apron_raster").resolve(),
                   "candidate": (args.candidate or repo.parent / "build-native/apps/standalone/test_standalone_reference_apron_raster").resolve(),
                   "unavailable": (args.unavailable or repo.parent / "build-native/apps/standalone/test_standalone_reference_apron_unavailable").resolve()}
    identities = {key: {"path": str(path), "sha256": digest(path), "bytes": path.stat().st_size}
                  for key, path in executables.items()}
    require(identities["before"]["sha256"] == BASELINE_SHA256, "actual genuine baseline executable differs")
    require(len({item["sha256"] for item in identities.values()}) == 3, "three distinct executable identities are required")
    sources = source_identity(repo)
    report = {"schema": 1, "protocol": "reference-apron-independent-raster-admission-v1", "status": "running",
              "observed_utc": datetime.now(timezone.utc).isoformat(), "cwd": str(Path.cwd()), "command": sys.argv,
              "scope": "Frozen25 genuine-before/candidate/unavailable; dummy SDL software pixels only",
              "checker_sha256": digest(Path(__file__)), "receipt_sha256": digest(receipt_path),
              "baseline_main": receipt["baseline_main"], "source_sha256": sources, "executables": identities,
              "decoder": {"python": platform.python_version(), "pillow": pillow.__version__, "numpy": np.__version__,
                          "full_source_rgb_sha256": RGB_SHA256}, "lists": {}, "cases": [], "clip_companions": [], "failures": []}
    for label, executable in executables.items():
        listing = run_bounded([str(executable), "--list"], HEADER_MAX, args.timeout)
        require(same(strict_json(listing), manifest) and sha256(listing) == LIST_SHA256, f"{label}: frozen --list differs")
        report["lists"][label] = {"bytes": len(listing), "sha256": sha256(listing)}
    selected = sorted(set(args.case if args.case is not None else range(25)))
    # A requested clipped diagnostic also obtains its full companion, without granting full admission.
    if any(9 <= index <= 14 for index in selected) and 8 not in selected:
        selected.append(8)
        selected.sort()
    full = {}
    keep = args.keep_streams.resolve() if args.keep_streams else None
    if keep:
        keep.mkdir(parents=True, exist_ok=True)
    for index in selected:
        spec = manifest["cases"][index]
        record = {"case": index, "contract_case": index + 1, "name": spec["name"], "status": "failed"}
        report["cases"].append(record)
        try:
            frames = {}
            for label, executable in executables.items():
                data = run_bounded([str(executable), "--case", str(index)],
                                   HEADER_MAX + spec["output_size"][0] * spec["output_size"][1] * 4, args.timeout)
                if keep:
                    path = keep / f"{label}-case{index:02d}.rgba-stream"
                    with path.open("xb") as output:
                        output.write(data)
                frame = read_frame(io.BytesIO(data))
                validate_metadata(frame.header, manifest, index)
                frames[label] = frame
            before, candidate, unavailable = (frames[label] for label in executables)
            record["frames"] = {label: frame.identity() for label, frame in frames.items()}
            require(same(candidate.header, before.header) and same(unavailable.header, before.header), "paired complete metadata differs")
            mask = masks(before.header)
            record["mask"] = mask
            counts = difference_counts(before.array(), candidate.array(), mask)
            counts["unavailable_changed_pixels"] = int(np.count_nonzero(np.any(before.array() != unavailable.array(), axis=2)))
            record["comparison"] = counts
            problems = []
            for key in ("outside_allowed_changed_pixels", "footer_changed_pixels", "unavailable_changed_pixels"):
                if counts[key]:
                    problems.append(f"{key}={counts[key]}")
            if index in EXACT_CASES and counts["changed_pixels"]:
                problems.append("required whole-frame equality failed")
            if index not in EXACT_CASES and not counts["changed_pixels"]:
                problems.append("visible active apron has no changed pixels")
            if index == 0:
                report["canonical_source"] = compare_source(candidate, source)
                if report["canonical_source"]["source_pixels"] != 32544 or report["canonical_source"]["unequal_source_pixels"]:
                    problems.append("canonical source equality failed")
            if index == 8:
                full = frames
            elif 9 <= index <= 14:
                companion = {"case": index, "contract_case": index + 1, "full_case": 8,
                             "visible_pixels": mask["visible_pixels"], "apron_center_pixels": mask["apron_center_pixels"]}
                for label, frame in frames.items():
                    require(label in full, "full companion is unavailable")
                    for field in ("renderer", "model", "info", "scale", "viewport", "output_size"):
                        require(same(frame.header[field], full[label].header[field]), f"{label} companion {field} differs")
                    different = np.any(frame.array() != full[label].array(), axis=2)
                    companion[label] = {"visible_changed_pixels": box_count(different, mask["visible_box"]),
                                        "apron_center_changed_pixels": box_count(different, mask["apron_center_box"])}
                report["clip_companions"].append(companion)
            require(not problems, "; ".join(problems))
            record["status"] = "passed"
        except (AdmissionError, OSError) as error:
            record["failure"] = str(error)
            report["failures"].append({"case": index, "contract_case": index + 1, "message": str(error)})
        if args.progress:
            print(f"contract case {index + 1}/25 ({spec['name']}): {record['status']}", file=sys.stderr, flush=True)
    report["totals"] = {key: sum(case.get("mask", {}).get(key, 0) for case in report["cases"])
                         for key in ("frame_pixels", "allowed_pixels", "apron_center_pixels", "visible_exterior_pixels",
                                     "protected_outside_pixels", "footer_center_pixels")}
    report["totals"].update({key: sum(case.get("comparison", {}).get(key, 0) for case in report["cases"])
                             for key in ("changed_pixels", "outside_allowed_changed_pixels", "footer_changed_pixels", "unavailable_changed_pixels")})
    report["totals"].update({"checked_cases": len(selected), "passed_cases": sum(c["status"] == "passed" for c in report["cases"]),
                              "required_whole_equal_cases": len(EXACT_CASES.intersection(selected))})
    if source_identity(repo) != sources or any(digest(path) != identities[label]["sha256"] for label, path in executables.items()):
        report["failures"].append({"message": "source or executable changed during admission"})
    report["status"] = "failed" if report["failures"] else "passed" if selected == list(range(25)) else "partial"
    report["limits"] = ["Cross-clip sampling differences are reported, not required to equal zero.",
                         "Direct pre-footer alpha/state probe and same-Drawing repeat qualification are separate native gates.",
                         "Source-package admission, genuine application visual inspection and real display/DPI/input/accessibility remain separate.",
                         "Literal whole-interface 1:1 remains unqualified."]
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--before", type=Path, help="retained genuine executable; pinned SHA-256 is mandatory")
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--unavailable", type=Path, help="candidate fixture linked with unavailable apron texture")
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--case", type=int, choices=range(25), action="append", help="zero-based diagnostic subset; never full admission unless all 25")
    parser.add_argument("--timeout", type=float, default=20.0, help="per-process seconds, 0 < timeout <= 60")
    parser.add_argument("--report", type=Path, help="new JSON report path; existing reports are never replaced")
    parser.add_argument("--keep-streams", type=Path, help="optional directory for exact streams; filenames must not exist")
    parser.add_argument("--progress", action="store_true", help="one progress line per case on stderr")
    args = parser.parse_args(argv)
    if not math.isfinite(args.timeout) or not 0 < args.timeout <= 60:
        parser.error("--timeout must be finite, positive, and no greater than 60")
    try:
        if args.report:
            require(not args.report.exists(), "report already exists; select a new name to retain original evidence")
        report = admission(args)
    except (AdmissionError, OSError, KeyError, TypeError) as error:
        report = {"schema": 1, "protocol": "reference-apron-independent-raster-admission-v1",
                  "status": "blocked", "failures": [{"message": str(error)}]}
    encoded = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.report:
        try:
            with args.report.open("x", encoding="utf-8") as output:
                output.write(encoded)
        except OSError as error:
            print(f"Cannot preserve report: {error}", file=sys.stderr)
            return 2
        print(json.dumps({"status": report["status"], "report": str(args.report),
                          "sha256": sha256(encoded.encode("utf-8")), "totals": report.get("totals", {})}))
    else:
        print(encoded, end="")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
