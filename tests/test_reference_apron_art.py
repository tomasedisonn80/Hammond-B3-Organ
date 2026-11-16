"""Author/compiler checks for the frozen, independently packaged apron pixels."""

from __future__ import annotations

import argparse
import copy
import gzip
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/compile_reference_apron.py"
SPEC = importlib.util.spec_from_file_location("reference_apron_compiler", TOOL)
apron = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(apron)


class ReferenceApronArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.manifest_bytes = apron.read_manifest(apron.DEFAULT_MANIFEST)
        cls.source = apron.read_source(apron.DEFAULT_SOURCE)
        cls.packed = (apron.DEFAULT_MANIFEST.parent / apron.ASSET_FILE).read_bytes()
        cls.pixels = apron.read_asset(apron.DEFAULT_MANIFEST.parent)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.manifest_path = self.directory / "inputs/manifest.json"
        self.manifest_path.parent.mkdir()
        self.manifest_path.write_bytes(self.manifest_bytes)
        self.source_path = self.directory / "inputs/source.jpg"
        self.source_path.write_bytes(self.source)
        self.asset_path = self.directory / "inputs" / apron.ASSET_FILE
        self.asset_path.write_bytes(self.packed)
        self.output = self.directory / "output/ReferenceApronData.h"
        self.output.parent.mkdir()
        self.output.write_bytes(b"retained previous output\n")

    def command(self, *arguments, stdlib=False):
        return subprocess.run(
            [sys.executable, "-B", *(["-S"] if stdlib else []), str(TOOL),
             "--input", str(self.manifest_path), "--source", str(self.source_path),
             *map(str, arguments)], capture_output=True, timeout=30, check=False)

    def assert_refused_unchanged(self, *arguments):
        before = self.output.read_bytes()
        mtime = self.output.stat().st_mtime_ns
        result = self.command(*arguments)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(b"Reference apron error:", result.stderr)
        self.assertNotIn(b"Traceback", result.stderr)
        self.assertEqual(self.output.read_bytes(), before)
        self.assertEqual(self.output.stat().st_mtime_ns, mtime)
        self.assertEqual(list(self.output.parent.glob(".reference-apron-*")), [])
        return result

    def args(self, **changes):
        values = dict(input=self.manifest_path, source=self.source_path,
                      output=None, verify_only=False, verify_source=False,
                      extract_to=None)
        values.update(changes)
        return argparse.Namespace(**values)

    def require_pillow(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("optional Pillow source decoder is not installed")
        return Image

    def test_frozen_source_manifest_packed_and_raw_identities(self):
        self.assertEqual(apron.sha256(self.manifest_bytes), apron.MANIFEST_SHA256)
        self.assertEqual(len(self.source), 412664)
        self.assertEqual(apron.sha256(self.source), apron.SOURCE_SHA256)
        self.assertEqual(len(self.packed), 61162)
        self.assertEqual(apron.sha256(self.packed), apron.PACKED_SHA256)
        self.assertEqual(len(self.pixels), 354240)
        self.assertEqual(apron.sha256(self.pixels), apron.PIXEL_SHA256)
        self.assertEqual(gzip.decompress(self.packed), self.pixels)
        self.assertEqual(self.manifest["asset"]["source_rect"], [16, 887, 1640, 54])
        self.assertEqual(self.manifest["asset"]["hole_rect"], [32, 2, 1556, 36])

    def test_every_masked_byte_is_zero_and_every_other_alpha_is_opaque(self):
        opaque = zero = 0
        for y in range(54):
            for x in range(1640):
                offset = (y * 1640 + x) * 4
                texel = self.pixels[offset:offset + 4]
                if 32 <= x < 1588 and 2 <= y < 38:
                    self.assertEqual(texel, b"\0\0\0\0", (x, y))
                    zero += 1
                else:
                    self.assertEqual(texel[3], 255, (x, y))
                    opaque += 1
        self.assertEqual((opaque, zero), (32544, 56016))

    def test_source_rgb_for_every_unmasked_texel_independent_of_crop_implementation(self):
        Image = self.require_pillow()
        with Image.open(io.BytesIO(self.source)) as opened:
            opened.load()
            rgb = opened.convert("RGB").tobytes()
        self.assertEqual(apron.sha256(rgb), apron.DECODED_SOURCE_SHA256)
        expected = bytearray(354240)
        for y in range(54):
            for x in range(1640):
                if 32 <= x < 1588 and 2 <= y < 38:
                    continue
                source_offset = ((y + 887) * 1672 + x + 16) * 3
                target_offset = (y * 1640 + x) * 4
                expected[target_offset:target_offset + 3] = rgb[source_offset:source_offset + 3]
                expected[target_offset + 3] = 255
        self.assertEqual(self.pixels, bytes(expected))

    def test_verify_only_works_without_site_packages(self):
        result = self.command("--verify-only", stdlib=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"354240 RGBA bytes", result.stdout)

    def test_header_compiles_without_pillow_and_retains_all_rgba_bytes(self):
        result = self.command("--output", self.output, stdlib=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        header = self.output.read_text("ascii")
        self.assertIn("namespace hammond::standalone::reference_apron", header)
        self.assertIn("struct RgbaImage", header)
        self.assertIn("1640, 54, 6560, kApronPixels, sizeof(kApronPixels)", header)
        body = header.split("kApronPixels[] = {\n", 1)[1].split("\n};", 1)[0]
        compiled = bytes(int(value, 16) for value in re.findall(r"0x([0-9a-f]{2})", body))
        self.assertEqual(compiled, self.pixels)
        self.assertLess(len(header), apron.MAX_HEADER_BYTES)

    def test_repeated_header_is_byte_stable_and_preserves_existing_timestamp(self):
        first = self.command("--output", self.output)
        self.assertEqual(first.returncode, 0, first.stderr)
        before = self.output.read_bytes()
        os.utime(self.output, ns=(1234567890000000000, 1234567890000000000))
        mtime = self.output.stat().st_mtime_ns
        second = self.command("--output", self.output)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn(b"Unchanged RGBA header", second.stdout)
        self.assertEqual(self.output.read_bytes(), before)
        self.assertEqual(self.output.stat().st_mtime_ns, mtime)

    def test_changed_manifest_is_refused_before_output_replacement(self):
        malformed = [b"", b"{", self.manifest_bytes + b"\n", b"\xff",
                     b"x" * (apron.MAX_MANIFEST_BYTES + 1)]
        for raw in malformed:
            with self.subTest(size=len(raw)):
                self.manifest_path.write_bytes(raw)
                self.assert_refused_unchanged("--output", self.output)

    def test_manifest_parser_rejects_duplicate_nonfinite_float_or_wrong_root(self):
        # Exercise parser defenses separately from the authoritative byte pin.
        for raw in (b'{"schema_version":1,"schema_version":1}', b'{"x":NaN}',
                    b'{"x":Infinity}', b'{"x":1.0}', b"[]", b"null"):
            with self.subTest(raw=raw):
                self.manifest_path.write_bytes(raw)
                with mock.patch.object(apron, "MANIFEST_SHA256", apron.sha256(raw)):
                    with self.assertRaises(apron.ReferenceApronError):
                        apron.read_manifest(self.manifest_path)

    def test_manifest_cannot_redirect_asset_path_or_change_dimensions(self):
        for key, value in (("file", "../../elsewhere.gz"), ("width", 1639),
                           ("hole_rect", [32, 2, 1556, 35]), ("pixel_bytes", 354241)):
            document = copy.deepcopy(self.manifest)
            document["asset"][key] = value
            raw = json.dumps(document).encode("utf-8")
            self.manifest_path.write_bytes(raw)
            with self.subTest(key=key):
                self.assert_refused_unchanged("--output", self.output)
                with mock.patch.object(apron, "MANIFEST_SHA256", apron.sha256(raw)):
                    with self.assertRaises(apron.ReferenceApronError):
                        apron.read_manifest(self.manifest_path)

    def test_changed_missing_or_oversized_source_preserves_output(self):
        for raw in (self.source[:-1], self.source + b"x",
                    bytes([self.source[0] ^ 1]) + self.source[1:],
                    b"x" * (apron.MAX_SOURCE_BYTES + 1)):
            with self.subTest(size=len(raw)):
                self.source_path.write_bytes(raw)
                self.assert_refused_unchanged("--output", self.output)
        self.source_path.unlink()
        self.assert_refused_unchanged("--output", self.output)

    def test_changed_missing_or_oversized_packed_bytes_preserve_output(self):
        for raw in (self.packed[:-1], self.packed + b"x", self.packed + self.packed,
                    bytes([self.packed[0] ^ 1]) + self.packed[1:],
                    b"x" * (apron.MAX_PACKED_BYTES + 1)):
            with self.subTest(size=len(raw)):
                self.asset_path.write_bytes(raw)
                self.assert_refused_unchanged("--output", self.output)
        self.asset_path.unlink()
        self.assert_refused_unchanged("--output", self.output)

    def test_decoder_rejects_truncation_extra_members_trailers_and_bad_crc(self):
        bad_crc = self.packed[:-8] + bytes([self.packed[-8] ^ 1]) + self.packed[-7:]
        bad_size = self.packed[:-1] + bytes([self.packed[-1] ^ 1])
        malformed = (b"not gzip", self.packed[:10], self.packed[:-1], bad_crc,
                     bad_size, self.packed + b"\0", self.packed + b"trailer",
                     self.packed + self.packed)
        for packed in malformed:
            with self.subTest(size=len(packed)):
                with self.assertRaises(apron.ReferenceApronError):
                    apron.decode_gzip(packed)

    def test_decoder_rejects_undersize_oversize_and_expansion_past_bound(self):
        for pixels in (b"x", bytes(354239), bytes(354241), bytes(2 * 1024 * 1024)):
            packed = apron.canonical_gzip(pixels)
            with self.subTest(decoded=len(pixels)):
                with self.assertRaises(apron.ReferenceApronError):
                    apron.decode_gzip(packed)
        for expected in (0, -1, True, 1.0, 354241):
            with self.subTest(expected=expected):
                with self.assertRaises(apron.ReferenceApronError):
                    apron.decode_gzip(self.packed, expected)

    def test_header_generator_refuses_changed_raw_bytes(self):
        for pixels in (self.pixels[:-1], bytes([self.pixels[0] ^ 1]) + self.pixels[1:]):
            with self.assertRaises(apron.ReferenceApronError):
                apron.make_header(pixels)

    def test_exact_and_normalized_input_aliases_are_refused(self):
        for path in (self.manifest_path, self.source_path, self.asset_path,
                     self.manifest_path.parent / ".." / "inputs" / "manifest.json"):
            with self.subTest(path=path):
                before = path.read_bytes()
                result = self.command("--output", path)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(b"alias", result.stderr)
                self.assertEqual(path.read_bytes(), before)

    def test_hardlink_aliases_cannot_replace_inputs(self):
        for index, path in enumerate((self.manifest_path, self.source_path, self.asset_path)):
            alias = self.directory / f"hardlink-{index}"
            try:
                os.link(path, alias)
            except OSError as exc:
                self.skipTest(f"hard links unavailable: {exc}")
            before = path.read_bytes()
            result = self.command("--output", alias)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn(b"alias", result.stderr)
            self.assertEqual(alias.read_bytes(), before)
            self.assertTrue(alias.samefile(path))

    def test_output_symlink_and_directory_are_refused(self):
        result = self.command("--output", self.directory)
        self.assertEqual(result.returncode, 1, result.stderr)
        alias = self.directory / "output-link"
        try:
            alias.symlink_to(self.output)
        except OSError as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        self.assert_refused_unchanged("--output", alias)
        self.assertTrue(alias.is_symlink())

    def test_replacement_io_error_preserves_output_and_cleans_temporary(self):
        before = self.output.read_bytes()
        with mock.patch.object(apron.os, "replace", side_effect=OSError("simulated replace failure")):
            with self.assertRaisesRegex(OSError, "simulated replace failure"):
                apron.write_atomic(self.output, b"new bytes", {self.source_path})
        self.assertEqual(self.output.read_bytes(), before)
        self.assertEqual(list(self.output.parent.glob(".reference-apron-*")), [])

    def test_verify_source_checks_exact_pixels(self):
        self.require_pillow()
        result = self.command("--verify-source")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b"exact source/mask equality", result.stdout)

    def test_source_verification_requires_full_decoded_image_hash(self):
        self.require_pillow()
        with mock.patch.object(apron, "DECODED_SOURCE_SHA256", "0" * 64):
            with self.assertRaisesRegex(apron.ReferenceApronError, "decoded source RGB"):
                apron.source_pixels(self.source)

    def test_extract_reproduces_locked_manifest_and_gzip(self):
        self.require_pillow()
        _, versions = apron.source_pixels(self.source)
        if versions != self.manifest["authoring"]:
            self.skipTest("exact frozen authoring toolchain is not installed")
        destination = self.directory / "reauthored"
        result = self.command("--extract-to", destination)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((destination / "manifest.json").read_bytes(), self.manifest_bytes)
        self.assertEqual((destination / apron.ASSET_FILE).read_bytes(), self.packed)
        self.assertEqual(self.packed[:10], b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff")

    def test_extract_rejects_toolchain_mismatch_without_creating_destination(self):
        self.require_pillow()
        destination = self.directory / "not-created"
        with mock.patch.object(apron.platform, "python_version", return_value="0.0.0"):
            with self.assertRaisesRegex(apron.ReferenceApronError, "toolchain differs"):
                apron.run(self.args(extract_to=destination))
        self.assertFalse(destination.exists())

    def test_extract_preflights_both_destinations_before_writing(self):
        self.require_pillow()
        pixels, versions = apron.source_pixels(self.source)
        destination = self.directory / "reauthored"
        destination.mkdir()
        packed_output = destination / apron.ASSET_FILE
        packed_output.write_bytes(b"must survive")
        try:
            os.link(self.manifest_path, destination / "manifest.json")
        except OSError as exc:
            self.skipTest(f"hard links unavailable: {exc}")
        # This alias gate is independent of the locally installed author versions.
        with mock.patch.object(apron, "source_pixels", return_value=(pixels, self.manifest["authoring"])), \
                mock.patch.object(apron, "canonical_gzip", return_value=self.packed):
            with self.assertRaisesRegex(apron.ReferenceApronError, "alias"):
                apron.run(self.args(extract_to=destination))
        self.assertEqual(packed_output.read_bytes(), b"must survive")
        self.assertEqual(self.manifest_path.read_bytes(), self.manifest_bytes)

    def test_author_destinations_cannot_alias_each_other(self):
        first = self.directory / "first"
        second = self.directory / "second"
        first.write_bytes(b"retained")
        try:
            os.link(first, second)
        except OSError as exc:
            self.skipTest(f"hard links unavailable: {exc}")
        with self.assertRaisesRegex(apron.ReferenceApronError, "each other"):
            apron.check_outputs([first, second], {self.source_path})
        self.assertEqual(first.read_bytes(), b"retained")

    def test_explicit_author_modes_explain_missing_optional_pillow(self):
        result = self.command("--verify-source", stdlib=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(b"needs Pillow", result.stderr)
        self.assertNotIn(b"Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
