"""A22 independent source/header admission; never imports the apron compiler."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import os
import platform
import re
import subprocess
import sys
import zlib
import PIL
from PIL import Image, features

ROOT = Path.cwd().resolve()
OUT = ROOT.parent / "a22-apron"
BASE = "54df95fe343d417dd89bb7a91f85e4f51c08dfe7"

def digest(data):
    return hashlib.sha256(data).hexdigest()

def identity(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": digest(data)}

source_path = ROOT / "docs/design/atlas-cover-reference.jpg"
asset_path = ROOT / "assets/standalone/reference-apron-v1/apron.rgba.gz"
manifest_path = asset_path.parent / "manifest.json"
compiler = ROOT / "tools/compile_reference_apron.py"
source = source_path.read_bytes()
packed = asset_path.read_bytes()
manifest_raw = manifest_path.read_bytes()
manifest = json.loads(manifest_raw)
assert len(source) == 412664
assert digest(source) == "9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187"
assert len(packed) == 61162
assert digest(packed) == "87387e6c0bbd54012f0e0b23560175781a6515483b047822e4b64e4adfaac06c"
assert len(manifest_raw) == 2416
assert digest(manifest_raw) == "41a8a503a8cef8c1df102599de83f6c2a3cf86c23cb2fbc8eedb18a6e52670d8"
decoder = zlib.decompressobj(31)
pixels = decoder.decompress(packed, 354241)
assert len(pixels) == 354240 and decoder.eof
assert not decoder.unused_data and not decoder.unconsumed_tail
assert digest(pixels) == "2646c6fe3fd813ae2907fb04dafacf504309247656860b7161d12ff2f85ded13"
assert packed[:10] == bytes.fromhex("1f8b08000000000002ff")
with Image.open(source_path) as opened:
    assert opened.format == "JPEG" and opened.size == (1672, 941)
    opened.load()
    rgb = opened.convert("RGB")
whole_rgb = rgb.tobytes()
assert len(whole_rgb) == 4720056
assert digest(whole_rgb) == "07a7e35a2fd6610d623bbc1da8c995f3f4d95c4b45a0a5c1f41ad1395584bbeb"
source_texels = rgb.load()
opaque = zero = 0
for n in range(88560):
    y, x = divmod(n, 1640)
    actual = tuple(pixels[4 * n:4 * n + 4])
    if x in range(32, 1588) and y in range(2, 38):
        assert actual == (0, 0, 0, 0), (x, y, actual)
        zero += 1
    else:
        assert actual == (*source_texels[x + 16, y + 887], 255), (x, y, actual)
        opaque += 1
assert (opaque, zero) == (32544, 56016)
versions = {
    "tool": "tools/compile_reference_apron.py", "tool_version": 1,
    "python": platform.python_version(), "pillow": PIL.__version__,
    "libjpeg_api": features.version("jpg"),
    "libjpeg_turbo": features.version("libjpeg_turbo"),
    "zlib_compile": zlib.ZLIB_VERSION, "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION,
}
assert versions == manifest["authoring"], versions
regenerated = io.BytesIO()
with gzip.GzipFile(fileobj=regenerated, mode="wb", filename="", compresslevel=9, mtime=0) as stream:
    stream.write(pixels)
assert regenerated.getvalue() == packed

commands = []
def compile_header(*args):
    argv = [sys.executable, "-B", "-S", str(compiler), *map(str, args)]
    result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=30)
    commands.append({"argv": argv, "returncode": result.returncode,
                     "stdout": result.stdout.decode(), "stderr": result.stderr.decode()})
    assert result.returncode == 0, commands[-1]
    return result

compile_header("--verify-only")
first = OUT / "first.h"
second = OUT / "second.h"
compile_header("--output", first)
compile_header("--output", second)
header = first.read_bytes()
assert header == second.read_bytes()
assert len(header) == 2215140
assert digest(header) == "06ab67289452e17b2254093b12f05f2b5e234323abfa1098e635abf8cf298091"
body = header.split(b"kApronPixels[] = {\n", 1)[1].split(b"\n};", 1)[0]
header_pixels = bytes(int(word, 16) for word in re.findall(rb"0x([0-9a-f]{2})", body))
assert header_pixels == pixels
assert b"1640, 54, 6560, kApronPixels, sizeof(kApronPixels)" in header
os.utime(first, ns=(1234567890000000000, 1234567890000000000))
before = first.stat().st_mtime_ns
result = compile_header("--output", first)
assert b"Unchanged RGBA header" in result.stdout
assert first.stat().st_mtime_ns == before and first.read_bytes() == header
assert not list(OUT.glob(".reference-apron-*"))

history = []
paths = ["tools/compile_reference_art.py", "docs/design/atlas-cover-reference.jpg",
         "docs/design/atlas-reference.json"]
paths += sorted(str(p.relative_to(ROOT)) for p in (ROOT / "assets/standalone/reference").iterdir() if p.is_file())
for relative in paths:
    baseline = subprocess.run(["git", "show", f"{BASE}:{relative}"], cwd=ROOT,
                              capture_output=True, timeout=30, check=True).stdout
    current = (ROOT / relative).read_bytes()
    assert current == baseline, relative
    history.append({"path": relative, **identity(ROOT / relative), "base_byte_equal": True})
baseline_drawing = subprocess.run(["git", "show", f"{BASE}:apps/standalone/Drawing.h"],
                                  cwd=ROOT, capture_output=True, timeout=30, check=True).stdout
current_drawing = (ROOT / "apps/standalone/Drawing.h").read_bytes()
pattern = rb"enum class ReferenceArt\s*\{[^}]+\};"
assert re.search(pattern, baseline_drawing).group() == re.search(pattern, current_drawing).group()

pdf = ROOT / "Hammond_B3_Leslie_Research_Atlas_500pp.pdf"
pdf_hash = hashlib.sha256()
with pdf.open("rb") as stream:
    while block := stream.read(1024 * 1024):
        pdf_hash.update(block)
assert pdf_hash.hexdigest() == "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769"
files = ["tools/compile_reference_apron.py", "tests/test_reference_apron_art.py",
         "docs/design/REFERENCE_APRON_CONTRACT.md", "assets/standalone/reference-apron-v1/manifest.json",
         "assets/standalone/reference-apron-v1/apron.rgba.gz", "assets/standalone/reference-apron-v1/README.md",
         "assets/standalone/reference-apron-v1/requirements-authoring.txt", "apps/standalone/CMakeLists.txt"]
report = {
    "reviewer": "A22", "base_commit": BASE, "cwd": str(ROOT),
    "script": identity(Path(__file__)), "inputs": {p: identity(ROOT / p) for p in files},
    "source_jpeg": identity(source_path),
    "whole_decoded_rgb": {"bytes": len(whole_rgb), "sha256": digest(whole_rgb)},
    "packed": identity(asset_path), "raw": {"bytes": len(pixels), "sha256": digest(pixels)},
    "texels_compared": 88560, "opaque_exact_source_texels": opaque, "all_zero_texels": zero,
    "gzip_single_member": True, "gzip_independently_regenerated_exactly": True,
    "header": identity(first), "header_all_raw_bytes_exact": True,
    "two_outputs_identical": True, "unchanged_header_mtime_preserved": True,
    "stdlib_only_subprocesses": commands, "authoring": versions,
    "historical_inputs_unchanged": history, "reference_art_enum_unchanged": True,
    "pdf": {"bytes": pdf.stat().st_size, "sha256": pdf_hash.hexdigest()},
}
(OUT / "independent-verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
