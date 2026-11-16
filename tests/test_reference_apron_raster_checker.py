#!/usr/bin/env python3
"""Adversarial transport and independently enumerated boundary samples."""
from __future__ import annotations

import copy
import io
import json
from pathlib import Path
import sys
import unittest

try:
    import numpy as np
except ImportError:
    np = None

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import check_reference_apron_raster as checker


def small_header():
    # Transport-only record: detailed frozen metadata is a separate mandatory gate.
    return {"schema": 1, "protocol": "reference-apron-v1", "case": 0, "contract_case": 1,
            "name": "small transport adversary", "logical_size": [2, 3], "width": 2, "height": 3,
            "output_size": [2, 3], "scale": [1, 1], "viewport": [0, 0, 2, 3], "clip": [0, 0, 0, 0],
            "logical_viewport": [0, 0, 2, 3], "logical_clip": [0, 0, 0, 0], "clip_enabled": False,
            "blend": 1, "clip_kind": "disabled", "renderer": {}, "model": {}, "info": {}, "bytes": 24}


def encode(header=None, payload=bytes(range(24))):
    return json.dumps(header or small_header(), separators=(",", ":")).encode() + b"\n" + payload


def geometry_header(index=0):
    manifest = json.loads((Path(__file__).resolve().parents[1] / checker.MANIFEST).read_text())
    spec = manifest["cases"][index]
    header = copy.deepcopy(spec)
    header.update(width=spec["output_size"][0], height=spec["output_size"][1],
                  model={"view": {"workspace": spec["workspace"], "presentation": spec["presentation"]}})
    return header


class TransportAdversaries(unittest.TestCase):
    def reject(self, data, message=None):
        with self.assertRaisesRegex(checker.AdmissionError, message or ".*"):
            checker.read_frame(io.BytesIO(data))

    def test_exact_binary_payload_preserves_newlines_and_control_bytes(self):
        payload = b"\n\r\x1a\x00\xff\x80" * 4
        frame = checker.read_frame(io.BytesIO(encode(payload=payload)))
        self.assertEqual(frame.pixels, payload)
        self.assertEqual(len(frame.header_bytes) + len(frame.pixels), len(encode(payload=payload)))

    def test_short_and_extra_streams_are_never_admitted(self):
        for count in (0, 1, 20, 23):
            with self.subTest(short=count):
                self.reject(encode(payload=bytes(count)), "short RGBA")
        for suffix in (b"\x00", b"\n", encode()):
            with self.subTest(extra=len(suffix)):
                self.reject(encode() + suffix, "extra bytes")

    def test_malformed_utf8_json_and_duplicate_members(self):
        header = encode().split(b"\n", 1)[0]
        malformed = (b"\xff\n", b"{\n", b"[]\n", b"\xef\xbb\xbf" + header + b"\n",
                     header.replace(b'"width":2', b'"width":2,"width":2') + b"\n",
                     header.replace(b'"renderer":{}', b'"renderer":{"name":"software","name":"other"}') + b"\n",
                     header.replace(b'"scale":[1,1]', b'"scale":[NaN,1]') + b"\n",
                     header.replace(b'"scale":[1,1]', b'"scale":[1e9999,1]') + b"\n")
        for data in malformed:
            with self.subTest(data=data[:70]):
                self.reject(data + bytes(24))

    def test_header_lf_and_extent_limits(self):
        line, payload = encode().split(b"\n", 1)
        self.reject(line + b"\r\n" + payload, "one LF")
        self.reject(line, "one LF")
        self.reject(b" " * checker.HEADER_MAX + b"\n", "exceeds 64 KiB")
        # Exactly 64 KiB including the terminal LF is legal JSON whitespace.
        padded = line + b" " * (checker.HEADER_MAX - len(line) - 1) + b"\n" + payload
        self.assertEqual(len(checker.read_frame(io.BytesIO(padded)).header_bytes), checker.HEADER_MAX)

    def test_bad_extents_are_rejected_before_payload_read(self):
        class NoPayload(io.BytesIO):
            def read(self, count=-1):
                raise AssertionError("invalid header reached payload allocation/read")

        for key, value in (("width", 0), ("width", -1), ("width", True), ("width", 2.0),
                           ("height", 4097), ("bytes", 23), ("bytes", 25),
                           ("bytes", 67108865), ("bytes", True), ("bytes", "24")):
            with self.subTest(key=key, value=value):
                header = small_header()
                header[key] = value
                with self.assertRaises(checker.AdmissionError):
                    checker.read_frame(NoPayload(encode(header)))

    def test_missing_extra_or_wrong_protocol_metadata(self):
        for mutation in ("missing", "allowance", "schema", "protocol", "dimensions"):
            header = small_header()
            if mutation == "missing":
                del header["renderer"]
            elif mutation == "allowance":
                header["permitted_change_mask"] = [[0, 0, 2, 3]]
            elif mutation == "schema":
                header["schema"] = True
            elif mutation == "protocol":
                header["protocol"] = "reference-apron-v2"
            else:
                header["output_size"] = [2, 2]
            with self.subTest(mutation=mutation):
                self.reject(encode(header))

    def test_zero_based_identity_and_incomplete_state_are_rejected(self):
        manifest = json.loads((Path(__file__).resolve().parents[1] / checker.MANIFEST).read_text())
        header = geometry_header()
        header["case"] = 1
        with self.assertRaisesRegex(checker.AdmissionError, "case differs"):
            checker.validate_metadata(header, manifest, 0)
        header["case"] = 0
        header["contract_case"] = 0
        with self.assertRaisesRegex(checker.AdmissionError, "contract_case differs"):
            checker.validate_metadata(header, manifest, 0)
        frame = checker.read_frame(io.BytesIO(encode()))
        with self.assertRaises(checker.AdmissionError):
            checker.validate_metadata(frame.header, manifest, 0)

    def test_subprocess_pipes_and_wall_time_are_bounded(self):
        commands = (("import sys; sys.stdout.buffer.write(b'x'*100000)", 100, "stdout exceeds"),
                    ("import sys; sys.stderr.buffer.write(b'x'*100000)", 100, "stderr exceeds"),
                    ("import time; time.sleep(5)", 100, "exceeded"))
        for source, limit, message in commands:
            with self.subTest(message=message):
                timeout = 0.2 if "sleep" in source else 3.0
                with self.assertRaisesRegex(checker.AdmissionError, message):
                    checker.run_bounded([sys.executable, "-c", source], limit, timeout)
        help_text = checker.run_bounded([sys.executable, "-B", "-S", checker.__file__, "--help"], 65536, 3.0)
        self.assertIn(b"--candidate", help_text)


class ContractBoundaryAdversaries(unittest.TestCase):
    def test_canonical_regions_have_exact_half_open_populations(self):
        mask = checker.masks(geometry_header())
        self.assertEqual(mask["allowed_box"], (16, 887, 1656, 941))
        self.assertEqual(mask["footer_center_box"], (48, 889, 1604, 925))
        self.assertEqual(mask["allowed_pixels"], 88560)
        self.assertEqual(mask["footer_center_pixels"], 56016)
        self.assertEqual(mask["allowed_pixels"] - mask["footer_center_pixels"], 32544)

    def test_translated_scale_uses_physical_origin_and_center_boundary(self):
        mask = checker.masks(geometry_header(8))
        self.assertEqual(mask["allowed_box"], (37, 1347, 2497, 1429))
        self.assertEqual(mask["apron_center_box"], (37, 1347, 2497, 1428))
        self.assertEqual(mask["footer_center_box"], (85, 1350, 2419, 1404))
        self.assertEqual(mask["allowed_pixels"], 201720)
        self.assertEqual(mask["apron_center_pixels"], 199260)
        self.assertEqual(mask["footer_center_pixels"], 126036)

    def test_four_clip_strips_keep_both_interior_and_exterior(self):
        # Hand-enumerated physical rectangles: viewport (13,17), scale 1.5.
        expected = {9: ((37, 1347, 39, 1429), 164, 162, 182),
                    10: ((2495, 1347, 2497, 1429), 164, 162, 182),
                    11: ((37, 1347, 2497, 1349), 4920, 4920, 4936),
                    12: ((37, 1427, 2497, 1429), 4920, 2460, 7396)}
        for index, (box, allowed, interior, exterior) in expected.items():
            with self.subTest(contract_case=index + 1):
                mask = checker.masks(geometry_header(index))
                self.assertEqual(mask["allowed_box"], box)
                self.assertEqual(mask["allowed_pixels"], allowed)
                self.assertEqual(mask["apron_center_pixels"], interior)
                self.assertEqual(mask["visible_exterior_pixels"], exterior)
                self.assertGreater(mask["visible_outside_allowance_pixels"], 0)

    def test_empty_disjoint_cropped_and_inactive_have_zero_allowance(self):
        for index in (13, 14, 15, 20, 21, 22, 23, 24):
            with self.subTest(contract_case=index + 1):
                self.assertEqual(checker.masks(geometry_header(index))["allowed_pixels"], 0)
        self.assertEqual(checker.masks(geometry_header(13))["visible_pixels"], 0)
        self.assertEqual(checker.masks(geometry_header(14))["visible_pixels"], 256)

    @unittest.skipIf(np is None, "optional NumPy is unavailable; offline pixel comparisons remain unqualified")
    def test_single_pixel_escapes_and_footer_mutations_are_detected(self):
        mask = checker.masks(geometry_header())
        before = np.zeros((941, 1672, 4), dtype=np.uint8)
        after = before.copy()
        # Each sample's classification follows the contract's literal endpoints.
        samples = ((16, 887, 0, 0), (15, 887, 1, 0), (1656, 887, 1, 0),
                   (16, 886, 1, 0), (48, 889, 0, 1), (1603, 924, 0, 1),
                   (1604, 924, 0, 0), (48, 925, 0, 0))
        for x, y, outside, footer in samples:
            with self.subTest(x=x, y=y):
                after[y, x, 3] = 1
                counts = checker.difference_counts(before, after, mask)
                self.assertEqual(counts, {"changed_pixels": 1, "outside_allowed_changed_pixels": outside,
                                          "footer_changed_pixels": footer})
                after[y, x, 3] = 0

    @unittest.skipIf(np is None, "optional NumPy is unavailable; offline pixel comparisons remain unqualified")
    def test_source_gate_includes_alpha_and_excludes_only_footer_hole(self):
        header = geometry_header()
        pixels = np.zeros((941, 1672, 4), dtype=np.uint8)
        pixels[:, :, 3] = 255
        source = np.zeros((941, 1672, 3), dtype=np.uint8)
        pixels[889, 48] = [9, 9, 9, 0]  # F is protected by paired equality, not source replacement.
        pixels[887, 16, 3] = 254       # One otherwise identical source pixel has wrong alpha.
        result = checker.compare_source(checker.Frame(header, b"", pixels.tobytes()), source)
        self.assertEqual(result["source_pixels"], 32544)
        self.assertEqual(result["unequal_source_pixels"], 1)


if __name__ == "__main__":
    unittest.main()
