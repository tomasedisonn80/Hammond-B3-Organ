#!/usr/bin/env python3
"""Focused independent P1 parser/arithmetic/gate negatives; no native execution."""
from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock
import zlib


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("p1_compare", ROOT / "tools/compare_performance_plate.py")
p1 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(p1)


def stream_header(**changes):
    result = dict(schema=1, protocol=p1.PROTOCOL, case=0, width=2, height=2,
                  bytes=16, pixel_format="RGBA8", row_order="top-to-bottom", row_stride=8)
    result.update(changes)
    return result


def packed(header=None, pixels=bytes(range(16))):
    return json.dumps(header or stream_header(), separators=(",", ":")).encode() + b"\n" + pixels


class ParserTests(unittest.TestCase):
    def test_accepts_exact_packed_stream(self):
        h, rgba = p1.parse_frame(packed(), 0)
        self.assertEqual(h["width"], 2)
        self.assertEqual(rgba, bytes(range(16)))

    def test_rejects_duplicate_keys_and_nonfinite_numbers(self):
        for raw in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}', b'{"a":1e999}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                p1.strict_json(raw)

    def test_rejects_boolean_structural_integers(self):
        for field in ("schema", "case", "width", "height", "bytes", "row_stride"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                p1.parse_frame(packed(stream_header(**{field: True})), 0)

    def test_rejects_missing_header_truncation_and_trailer(self):
        for payload in (b"{}", b"x" * p1.MAX_HEADER + b"\n", packed()[:-1], packed() + b"\x00", packed() + b"\n{}"):
            with self.subTest(length=len(payload)), self.assertRaises(ValueError):
                p1.parse_frame(payload, 0)

    def test_rejects_wrong_case_packing_dimensions_and_stride(self):
        for change in ({"case": 1}, {"protocol": "other"}, {"pixel_format": "BGRA8"}, {"row_order": "bottom-to-top"},
                       {"width": 0}, {"height": -1}, {"width": p1.MAX_WIDTH + 1},
                       {"height": p1.MAX_HEIGHT + 1}, {"bytes": 12}, {"row_stride": 12}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                p1.parse_frame(packed(stream_header(**change)), 0)

    def test_boolean_semantics_do_not_compare_as_integer(self):
        self.assertFalse(p1.equal({"a": True}, {"a": 1}))
        self.assertTrue(p1.equal([1, 1.5], [1., 1.5]))

    def test_all_failures_retained_with_bounded_diagnostics(self):
        audit = p1.Audit()
        audit.check(False, "first", "x" * (p1.MAX_DIAGNOSTIC + 10))
        audit.guard("second", lambda: p1.require(False, "other failure"))
        self.assertEqual(len(audit.failures), 2)
        self.assertLess(len(audit.failures[0]["detail"]), p1.MAX_DIAGNOSTIC + 100)
        self.assertIn("other failure", audit.failures[1]["detail"])

    def test_cli_requires_explicit_paired_identities_and_bounds(self):
        for arguments in (["--after", "not-executed"], ["--candidate-only", "--after", "not-executed", "--timeout", "nan"],
                          ["--candidate-only", "--after", "not-executed", "--total-seconds", "1801"],
                          ["--candidate-only", "--after", "not-executed", "--before", "not-executed"]):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                p1.cli(arguments)

    def test_inventory_requires_all_exports_and_literal_fields(self):
        specs = p1.scenarios()
        value = dict(schema=1, protocol=p1.PROTOCOL, cases=34, main_cases=24, companions=5, repeats=2, eligibility_witnesses=3,
                     stream="one JSON line then bytes packed RGBA8; no trailer",
                     span_format="[physical output row, first x, exclusive end x]", inventory=specs)
        p1.validate_inventory(json.dumps(value).encode() + b"\n", specs)
        for mutant in ("missing", "duplicate", "state"):
            changed = copy.deepcopy(value)
            if mutant == "missing":
                changed["inventory"].pop()
            elif mutant == "duplicate":
                changed["inventory"][33] = changed["inventory"][0]
            else:
                changed["inventory"][5]["expression"] = .625
            with self.subTest(mutant=mutant), self.assertRaises(ValueError):
                p1.validate_inventory(json.dumps(changed).encode() + b"\n", specs)

    def test_span_and_fullscan_detect_extra_cyan(self):
        rgba = bytes(p1.CYAN) + bytes(12) + bytes(p1.CYAN) + bytes(12)
        self.assertEqual(p1.cyan_spans(rgba, 4), [[0, 0, 1], [1, 0, 1]])
        self.assertEqual(p1.color_mismatches(rgba, 4, [[0, 0, 2]], p1.CYAN), 1)

    def test_artifacts_refuse_overwrite_and_altered_raw_stream(self):
        with tempfile.TemporaryDirectory() as directory:
            store = p1.ArtifactStore(Path(directory))
            item = store.compressed("probe", packed())
            self.assertEqual(store.load_stdout({"stdout": item}), packed())
            with self.assertRaises(FileExistsError):
                store.compressed("probe", packed())
            altered = {**item, "raw_sha256": "0" * 64}
            with self.assertRaises(ValueError):
                store.load_stdout({"stdout": altered})


class WorkspaceFocusTests(unittest.TestCase):
    """Independent untouched-workspace expectations from genuine pre-P1 bytes."""

    @classmethod
    def setUpClass(cls):
        cls.specs = p1.scenarios()
        cls.headers = {}
        # Frozen failed v1 streams are evidence, not regenerated test fixtures.
        # Sizes and both hashes bound decoding and keep candidate bytes out.
        baselines = {
            22: (1198701, "ac0ee4d8f1477aa923d724a857ba610b5df73d663c28639608651586acb527ca",
                 "0e9c35f34d417ef8aee7631b203ee09a5f34d12d476a3962f91e7d342c1a2284"),
            23: (473984, "c362535babc2a81931823fc4f5c3d2d2012d87548473d14772b39509b6aed1ca",
                 "d36807a122cbff7453f93742358646c70bdedd62d7b41f1f80ffcdf2194657a8"),
        }
        for index, (compressed_bytes, compressed_sha256, raw_sha256) in baselines.items():
            path = ROOT / p1.SESSION / "reports/p1-paired-v1" / f"before-{index}.stdout.zlib"
            if path.stat().st_size != compressed_bytes:
                raise AssertionError("genuine-before compressed size changed")
            encoded = path.read_bytes()
            if hashlib.sha256(encoded).hexdigest() != compressed_sha256:
                raise AssertionError("genuine-before compressed identity changed")
            decoder = zlib.decompressobj()
            raw = decoder.decompress(encoded, 6560395)
            if (len(raw) != 6560394 or not decoder.eof or decoder.unused_data or
                    decoder.unconsumed_tail or hashlib.sha256(raw).hexdigest() != raw_sha256):
                raise AssertionError("genuine-before bounded raw identity changed")
            end = raw.find(b"\n", 0, 2 * 1024 * 1024)
            if end < 0:
                raise AssertionError("genuine-before bounded header missing")
            cls.headers[index] = json.loads(raw[:end])

    def test_workspace_tabs_preserve_literal_body_memories(self):
        for index, workspace in ((22, 1), (23, 2)):
            header = self.headers[index]
            for moment in ("before", "after"):
                with self.subTest(case=index, moment=moment):
                    model = header["model_" + moment]
                    self.assertEqual(model["view"]["focus"], [20, 0, 0, workspace])
                    self.assertEqual(model["view"]["workspace_focus"],
                                     [[4, 0, 1, 4], [0, 0, 0, 0], [0, 0, 0, 0]])
                    p1.validate_model(self.specs[index], model,
                                      header["session_" + moment], header["hit_" + moment])

    def test_rejects_workspace_tab_as_remembered_body_focus(self):
        for index, workspace in ((22, 1), (23, 2)):
            header = self.headers[index]
            mutant = copy.deepcopy(header["model_before"])
            mutant["view"]["workspace_focus"][workspace] = [20, 0, 0, workspace]
            with self.subTest(case=index), self.assertRaisesRegex(ValueError, "copied view workspace_focus differs"):
                p1.validate_model(self.specs[index], mutant, header["session_before"], header["hit_before"])

    def test_rejects_erased_or_changed_play_body_memory(self):
        for index in (22, 23):
            header = self.headers[index]
            for replacement in ([0, 0, 0, 0], [7, 0, 0, 0]):
                mutant = copy.deepcopy(header["model_before"])
                mutant["view"]["workspace_focus"][0] = replacement
                with self.subTest(case=index, replacement=replacement), self.assertRaisesRegex(ValueError, "copied view workspace_focus differs"):
                    p1.validate_model(self.specs[index], mutant, header["session_before"], header["hit_before"])

    def test_rejects_fabricated_unused_workspace_memory(self):
        for index, other_workspace in ((22, 2), (23, 1)):
            header = self.headers[index]
            mutant = copy.deepcopy(header["model_before"])
            mutant["view"]["workspace_focus"][other_workspace] = [11, 0, 0, 0]
            with self.subTest(case=index), self.assertRaisesRegex(ValueError, "copied view workspace_focus differs"):
                p1.validate_model(self.specs[index], mutant, header["session_before"], header["hit_before"])

    def test_rejects_wrong_visible_workspace_focus(self):
        for index, other_workspace in ((22, 2), (23, 1)):
            header = self.headers[index]
            for replacement in ([20, 0, 0, other_workspace], [4, 0, 1, 4]):
                mutant = copy.deepcopy(header["model_before"])
                mutant["view"]["focus"] = replacement
                with self.subTest(case=index, replacement=replacement), self.assertRaisesRegex(ValueError, "copied view focus differs"):
                    p1.validate_model(self.specs[index], mutant, header["session_before"], header["hit_before"])


class NumericalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference, cls.baseline, cls.historical = p1.frozen_references(ROOT)

    def test_preserves_all_baseline_decisions(self):
        self.assertEqual((self.historical["passed"], self.historical["failed"], self.historical["total"]), (28, 34, 62))
        self.assertEqual(self.historical["checks"][-2]["difference_ratio"], [6324946007329, 1418860800000])
        self.assertEqual(self.historical["checks"][-1]["difference"], 1.393726506397573)
        self.assertFalse(self.historical["all_passed"])

    def test_reference_self_has_exactly_62_zero_errors(self):
        result = p1.numerical_screens(self.reference, self.reference)
        self.assertTrue(result["all_passed"])
        self.assertEqual(result["total"], 62)
        self.assertTrue(all(r["difference"] == 0 for r in result["checks"]))

    def test_affine_plane_has_exactly_zero_residual(self):
        width, height = 7, 5
        pixels = bytearray()
        for y in range(height):
            for x in range(width):
                value = 10 + 2 * x + 3 * y
                pixels.extend((value, value, value, 255))
        result = p1.patch_measure(bytes(pixels), width, height, (0, 0, width, height))
        self.assertEqual(result["residual_mean_square_ratio"], [0, 1])
        self.assertEqual(result["residual_rms"], 0.)
        self.assertEqual(Fraction(*result["luma_mean_ratio"]), 22)

    def test_one_nonaffine_pixel_has_nonzero_exact_residual(self):
        rgba = bytearray([20, 20, 20, 255] * 25)
        rgba[12 * 4:12 * 4 + 3] = bytes([21, 21, 21])
        result = p1.patch_measure(bytes(rgba), 5, 5, (0, 0, 5, 5))
        self.assertEqual(Fraction(*result["residual_mean_square_ratio"]), Fraction(24, 625))
        self.assertGreater(result["residual_rms"], 0)

    def test_rejects_contradictory_statistics(self):
        for field in ("residual_mean_square_ratio", "luma_mean_ratio", "rgb_sum"):
            changed = copy.deepcopy(self.baseline["TL"])
            changed[field][0] += 1
            with self.subTest(field=field), self.assertRaises(ValueError):
                p1.exact_values(changed)

    def test_exact_luma_limit_is_not_rounded_display_decimal(self):
        self.assertEqual(p1.MEAN_LIMIT, Fraction(6324946007329, 2837721600000))
        self.assertNotEqual(p1.MEAN_LIMIT, Fraction("2.228881792818929"))


class IndependentGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs = p1.scenarios()
        cls.atlases = p1.font_atlases(ROOT / p1.FONT)

    def test_full_matrix_and_zero_support_classes(self):
        self.assertEqual(len(self.specs), 34)
        self.assertEqual([s["case"] for s in self.specs], list(range(34)))
        self.assertEqual(p1.support_box(self.specs[0]), [76, 129, 1112, 260])
        for i in (8, 9, 14, 15, 17, 18, 19, 20, 21, 22, 23):
            with self.subTest(case=i):
                self.assertEqual(p1.area(p1.support_box(self.specs[i])), 0)
                self.assertTrue(self.specs[i]["paired_whole_frame_equality_required"])
        self.assertEqual(p1.support_box(self.specs[16]), [0, 0, 64, 64])
        self.assertEqual(self.specs[16]["viewport_request"][2:], [16384, 16384])

    def test_exact_float32_scale_and_resource_geometry(self):
        self.assertEqual(struct.pack("=f", self.specs[8]["scale"][0]), struct.pack("=f", 2.01))
        for s in self.specs:
            self.assertLessEqual(s["output_size"][0], p1.MAX_WIDTH)
            self.assertLessEqual(s["output_size"][1], p1.MAX_HEIGHT)
        self.assertEqual(self.specs[0]["independent_inset"], [76., 129., 1036., 131.])

    def test_exterior_alpha_mutation_is_rejected(self):
        before = bytes([1, 2, 3, 255] * 16)
        after = bytearray(before); after[3] = 254
        result = p1.difference_regions(before, after, 4, 4, [1, 1, 3, 3])
        self.assertEqual(result["changed_pixels"], 1)
        self.assertEqual(result["forbidden_changed_pixels"], 1)
        after = bytearray(before); after[(1 * 4 + 1) * 4 + 3] = 254
        result = p1.difference_regions(before, after, 4, 4, [1, 1, 3, 3])
        self.assertEqual(result["forbidden_changed_pixels"], 0)
        self.assertEqual(result["changed_pixels"], 1)

    def test_all_child_and_text_inventories_are_independent_nonempty(self):
        witness = p1.expected_witnesses(self.specs[0], self.atlases)
        self.assertEqual(len(witness["opaque_probes"]), 19)
        self.assertEqual(len(witness["text_runs"]), 17)
        self.assertTrue(all(p["pixels"] > 0 for p in witness["opaque_probes"]))
        self.assertTrue(all(p["opaque_pixels"] > 0 for p in witness["text_runs"]))
        self.assertEqual(sum(p["pixels"] for p in witness["opaque_probes"]), 1354)
        self.assertEqual(sum(p["opaque_pixels"] for p in witness["text_runs"]), 1561)
        self.assertEqual(witness["focus"]["expected_pixels"], 956)

    def test_every_required_full_frame_has_nonempty_cores(self):
        for spec in self.specs:
            witness = p1.expected_witnesses(spec, self.atlases)
            if witness["full_required"]:
                with self.subTest(case=spec["case"]):
                    self.assertTrue(all(p["pixels"] > 0 for p in witness["opaque_probes"]))
                    self.assertTrue(all(p["opaque_pixels"] > 0 for p in witness["text_runs"]))
                    self.assertGreater(witness["focus"]["expected_pixels"], 0)

    def test_edge_and_disjoint_companion_quiet_domains(self):
        for index in (10, 11, 12, 13, 15):
            spec = self.specs[index]
            witness = p1.expected_witnesses(spec, self.atlases)
            count = p1.span_count(p1.quiet_intersection(spec, witness))
            with self.subTest(case=index):
                self.assertEqual(count == 0, index == 15)

    def test_baseline_metadata_reproduces_independent_witnesses_and_state(self):
        path = ROOT / p1.SESSION / "reports/p1-before-case0.json"
        # This is retained pre-candidate metadata, not a candidate fixture run.
        header = p1.strict_json(path.read_bytes())
        self.assertTrue(p1.equal(header["witnesses"], p1.expected_witnesses(self.specs[0], self.atlases)))
        p1.validate_model(self.specs[0], header["model_before"], header["session_before"], header["hit_before"])
        mutant = copy.deepcopy(header["model_before"])
        del mutant["layout"]["manual_keys"][0][0]
        with self.assertRaises(ValueError):
            p1.validate_model(self.specs[0], mutant, header["session_before"], header["hit_before"])

    def test_eligibility_never_replaces_stored_percussion(self):
        for index, route, fixed, bank in ((31, 1, 0, 0), (32, 0, 0, 1), (33, 1, 2, 1)):
            session = p1.expected_session(self.specs[index])
            self.assertEqual(session["controls"]["percussion"], [True, 0, 0, 0])
            self.assertEqual(session["controls"]["route_enabled"][0], route)
            self.assertEqual(session["controls"]["fixed_registrations"][0], fixed)
            self.assertEqual(session["controls"]["selected_banks"][0], bank)
            witness = p1.expected_witnesses(self.specs[index], self.atlases)
            self.assertEqual(witness["text_runs"][2]["text"], "REQUIRES UPPER B")


class FixtureSourceTransitionTests(unittest.TestCase):
    """Bind real whole-file portability edits without weakening historical pairs."""

    ORIGINAL = "4f1875270af71d08c27372944a4a9c8e4c10b6c31dbeb85b3841b6965915956c"
    PORTABLE = "026489d127d586c8c18384f7064e13f068f400cf08b87099d8c7f03066fe3ec5"
    HELPER_ELSE = "a446f44bf67768aa9d9885084c1809c99102cb24413c7e640485ad17d5b3888d"
    # Independent byte literals from the reviewed proposal, not imported from
    # the comparator. Complete whole-file hashes bind their exact placement.
    REPLACEMENTS = (
        ('constexpr-else', b'bool p1_fixture_invoke_helper(Drawer& drawing, UiRect bounds, ReferenceCompositionScale scale) {\n    if constexpr (p1_fixture_helper_present<Drawer>) {\n        reference_performance_p1_material(drawing, bounds, scale);\n        return true;\n    }\n    return false;\n}\n', b'bool p1_fixture_invoke_helper(Drawer& drawing, UiRect bounds, ReferenceCompositionScale scale) {\n    if constexpr (p1_fixture_helper_present<Drawer>) {\n        reference_performance_p1_material(drawing, bounds, scale);\n        return true;\n    } else {\n        return false;\n    }\n}\n'),
        ('indexed-array', b"void array(std::ostream& out, const Range& values, Writer write) {\n    out << '[';\n    bool first = true;\n    for (const auto& value : values) {\n        if (!first) out << ',';\n        first = false;\n        write(out, value);\n    }\n    out << ']';\n}\n", b"void array(std::ostream& out, const Range& values, Writer write) {\n    out << '[';\n    for (std::size_t index = 0; index < values.size(); ++index) {\n        if (index != 0) out << ',';\n        write(out, values[index]);\n    }\n    out << ']';\n}\n"),
    )

    @classmethod
    def setUpClass(cls):
        data = (ROOT / p1.FIXTURE).read_bytes()
        if hashlib.sha256(data).hexdigest() == cls.PORTABLE:
            for name, before, after in reversed(cls.REPLACEMENTS):
                if data.count(after) != 1:
                    raise AssertionError("portable fixture lacks exact replacement: " + name)
                data = data.replace(after, before, 1)
        elif hashlib.sha256(data).hexdigest() == cls.HELPER_ELSE:
            _, before, after = cls.REPLACEMENTS[0]
            if data.count(after) != 1:
                raise AssertionError("helper predecessor lacks its complete replacement")
            data = data.replace(after, before, 1)
        if hashlib.sha256(data).hexdigest() != cls.ORIGINAL:
            raise AssertionError("fixture is neither exact original nor admitted portability source")
        cls.original = data
        for name, before, after in cls.REPLACEMENTS:
            if data.count(before) != 1:
                raise AssertionError("original fixture replacement is not unique: " + name)
            data = data.replace(before, after, 1)
        if hashlib.sha256(data).hexdigest() != cls.PORTABLE:
            raise AssertionError("independent replacements do not reproduce admitted fixture")
        cls.portable = data

    def test_original_pin_and_both_original_modes_remain(self):
        self.assertEqual(p1.PINNED[p1.FIXTURE], self.ORIGINAL)
        for candidate_only in (False, True):
            with self.subTest(candidate_only=candidate_only):
                result = p1.admit_fixture_source(self.original, candidate_only=candidate_only)
                self.assertEqual(result["variant"], "original-fixture")
                self.assertEqual(result["accepted_sha256"], self.ORIGINAL)
                self.assertIsNone(result["transition"])

    def test_exact_helper_only_predecessor_retains_upstream_admission(self):
        _, before, after = self.REPLACEMENTS[0]
        helper_source = self.original.replace(before, after, 1)
        self.assertEqual(hashlib.sha256(helper_source).hexdigest(), self.HELPER_ELSE)
        result = p1.admit_fixture_source(helper_source, candidate_only=True)
        self.assertEqual(result["variant"], "p1-helper-constexpr-else")
        self.assertEqual(result["accepted_sha256"], self.HELPER_ELSE)
        self.assertEqual(result["transition"]["reversed_sha256"], self.ORIGINAL)
        indexed = p1.admit_fixture_source(self.portable, candidate_only=True)
        self.assertEqual(indexed["transition"]["intermediate_fixture_sha256"], self.HELPER_ELSE)
        self.assertEqual(indexed["transition"]["helper_transition"], result["transition"])

    def test_exact_candidate_binds_all_bytes_and_complete_reversal(self):
        result = p1.admit_fixture_source(self.portable, candidate_only=True)
        self.assertEqual(result["variant"], "p1-helper-constexpr-else-indexed-array")
        self.assertEqual(result["original_pinned_sha256"], self.ORIGINAL)
        self.assertEqual(result["observed_sha256"], self.PORTABLE)
        self.assertEqual(result["accepted_sha256"], self.PORTABLE)
        transition = result["transition"]
        self.assertEqual(transition["scope"], "candidate-only")
        self.assertEqual(transition["reversed_sha256"], self.ORIGINAL)
        self.assertTrue(transition["whole_file_reversal_verified"])
        self.assertEqual(set(transition["replacements"]), {item[0] for item in self.REPLACEMENTS})

    def test_portability_source_is_refused_for_paired_comparison(self):
        with self.assertRaisesRegex(ValueError, "paired mode requires original fixture"):
            p1.admit_fixture_source(self.portable, candidate_only=False)

    def test_index_only_and_unrelated_edits_are_refused(self):
        _, before, after = self.REPLACEMENTS[1]
        partial = [self.original.replace(before, after, 1)]
        edits = partial + [self.original + b"\n", self.portable + b"\n",
                           self.portable.replace(b"\n", b"\r\n"),
                           self.portable.replace(b"index < values.size()", b"index <= values.size()", 1),
                           self.portable.replace(b"main_count = 24", b"main_count = 23", 1)]
        for data in edits:
            with self.subTest(sha256=hashlib.sha256(data).hexdigest()), self.assertRaises(ValueError):
                p1.admit_fixture_source(data, candidate_only=True)

    def test_relocated_replacement_is_refused(self):
        _, _, block = self.REPLACEMENTS[0]
        moved = self.portable.replace(block, b"", 1) + block
        with self.assertRaisesRegex(ValueError, "fixture helper reversal"):
            p1.admit_fixture_source(moved, candidate_only=True)

    def test_reversal_independently_refuses_outside_change(self):
        changed = self.portable.replace(b"main_count = 24", b"main_count = 23", 1)
        self.assertNotEqual(changed, self.portable)
        with mock.patch.object(p1, "P1_INDEXED_ARRAY_SHA256", hashlib.sha256(changed).hexdigest()), \
                self.assertRaisesRegex(ValueError, "reversal does not reconstruct admitted helper source"):
            p1.admit_fixture_source(changed, candidate_only=True)

    def test_nonbyte_sources_and_nonboolean_modes_are_refused(self):
        for data, mode in ((self.portable.decode(), True), (bytearray(self.portable), True),
                           (self.portable, 1), (self.original, None)):
            with self.subTest(data_type=type(data).__name__, mode=mode), self.assertRaises(ValueError):
                p1.admit_fixture_source(data, candidate_only=mode)

    def test_registered_fixture_remains_subject_to_final_stability(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / p1.FIXTURE
            path.parent.mkdir(parents=True)
            path.write_bytes(self.portable)
            inputs = {}
            result = p1.pin_fixture_source(inputs, root, candidate_only=True)
            self.assertEqual(result["accepted_sha256"], self.PORTABLE)
            self.assertEqual(inputs[p1.FIXTURE]["expected_sha256"], self.PORTABLE)
            self.assertEqual(inputs[p1.FIXTURE]["original_pinned_sha256"], self.ORIGINAL)
            audit = p1.Audit()
            p1.check_inputs_unchanged(audit, inputs)
            self.assertEqual(audit.failures, [])
            path.write_bytes(self.portable + b"\n")
            p1.check_inputs_unchanged(audit, inputs)
            self.assertEqual(len(audit.failures), 1)
            self.assertEqual(audit.failures[0]["check"], "final-input-stability:" + p1.FIXTURE)

    def test_execute_refuses_changed_fixture_before_any_native_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "root"
            for relative in (*p1.PINNED, p1.RECALL_SOURCE_PATCH):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT / relative).read_bytes())
            (root / p1.FIXTURE).write_bytes(self.portable + b"\n")
            output = Path(directory) / "report"
            args = p1.cli(["--root", str(root), "--candidate-only",
                           "--after", str(root / "unrun-after"), "--output", str(output)])
            with mock.patch.object(p1.Runner, "command", side_effect=AssertionError("native launch forbidden")) as launch, \
                    mock.patch("builtins.print"):
                status = p1.execute(args)
            launch.assert_not_called()
            self.assertEqual(status, 1)
            report = json.loads((output / "report.json").read_bytes())
            self.assertFalse(report["passed"])
            self.assertEqual(report["commands"], [])
            self.assertIsNone(report["fixture_source_admission"])
            self.assertTrue(any("fixture helper reversal" in failure["detail"]
                                for failure in report["failures"]))


class UiModelSourceTransitionTests(unittest.TestCase):
    """Real complete source bytes; independent A26 literals and refusal edits."""

    HEADER = "apps/standalone/UiModel.h"
    IMPLEMENTATION = "apps/standalone/UiModel.cpp"
    ORIGINAL = {
        HEADER: "6d8c0b16ddb6f3059dc14aff41bfc615e37b43c53b2f6e88cc199255a6b674b1",
        IMPLEMENTATION: "0ecb0c4ee90d98cdb87c6f06b4685d368a7c12b72f9ea66e6c40228a4a855ecd",
    }
    RECALLED = {
        HEADER: "34337e5db254bfbc4e23ee4fadf76ecc8fe792f003bd13ab5b54d0a302b5bb15",
        IMPLEMENTATION: "b4889e0b5d1b6eb0b88b140b8af92815df4bf021158a902994db2c15ed798986",
    }
    PATCH = "docs/development/2026-11-16-console-completion/reports/UiModel-recall-controls.patch"
    PATCH_SHA256 = "d4fadc8ae85d9f3dd2aedb6cccc63977fe1c4516dcca47b758a0ec18c7792cf8"
    # These bytes are transcribed from A26's frozen proposal, not imported from
    # the admission implementation. Original and resulting whole files are pinned.
    ADDITIONS = {
        HEADER: b"""    // Named-library recall validates and emits one copied whole ControlSnapshot
    // even when unchanged. Unlike legacy file Load, it retains the clean-file
    // reference. Invalid input emits nothing and preserves state. Presentation
    // and held-note owners are preserved; normal submission/observation applies.
    [[nodiscard]] UiActions recall_controls(const ControlSnapshot& controls) noexcept;
""",
        IMPLEMENTATION: b"""UiActions UiModel::recall_controls(const ControlSnapshot& controls) noexcept {
    if (!is_valid_control_snapshot(controls)) return {};
    return publish_controls(view_, saved_controls_, pending_control_sequence_, controls, true);
}

""",
    }
    ANCHORS = {
        HEADER: b"    // Main-thread external controller edit. Uses the same desired snapshot and\n",
        IMPLEMENTATION: b"UiActions UiModel::external_parameter(std::uint32_t parameter_id,\n",
    }

    @classmethod
    def setUpClass(cls):
        cls.original, cls.recalled = {}, {}
        for path, expected in cls.ORIGINAL.items():
            data = (ROOT / path).read_bytes()
            if hashlib.sha256(data).hexdigest() == cls.RECALLED[path]:
                if data.count(cls.ADDITIONS[path]) != 1:
                    raise AssertionError("frozen recalled source lacks its complete insertion")
                data = data.replace(cls.ADDITIONS[path], b"", 1)
            if hashlib.sha256(data).hexdigest() != expected:
                raise AssertionError("test source is neither exact original nor exact A26 source")
            if data.count(cls.ANCHORS[path]) != 1:
                raise AssertionError("original insertion anchor is not unique")
            cls.original[path] = data
            cls.recalled[path] = data.replace(cls.ANCHORS[path], cls.ADDITIONS[path] + cls.ANCHORS[path], 1)
            if hashlib.sha256(cls.recalled[path]).hexdigest() != cls.RECALLED[path]:
                raise AssertionError("independent A26 insertion does not reproduce its frozen source")
        cls.patch_bytes = (ROOT / cls.PATCH).read_bytes()
        if hashlib.sha256(cls.patch_bytes).hexdigest() != cls.PATCH_SHA256:
            raise AssertionError("frozen A26 patch changed")

    def changed_addition(self, path, old, new):
        self.assertEqual(self.ADDITIONS[path].count(old), 1)
        changed = dict(self.recalled)
        changed[path] = changed[path].replace(self.ADDITIONS[path],
                                              self.ADDITIONS[path].replace(old, new, 1), 1)
        return changed

    def write_root(self, directory, sources, *, include_fixed=False, patch_bytes=None):
        root = Path(directory) / "root"
        root.mkdir()
        files = dict(sources)
        if include_fixed:
            files.update({path: (ROOT / path).read_bytes() for path in p1.PINNED if path not in sources})
        files[self.PATCH] = self.patch_bytes if patch_bytes is None else patch_bytes
        for path, data in files.items():
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        return root

    def test_original_pair_and_genuine_baseline_pins_remain_unchanged(self):
        self.assertEqual({path: p1.PINNED[path] for path in self.ORIGINAL}, self.ORIGINAL)
        self.assertEqual(p1.BEFORE_EXE_SHA,
                         "65d0cc74e53faf2d655cba5f6254d5087715c730f22556ec81940195ad18149e")
        self.assertEqual(p1.BEFORE_PAINTER_SHA,
                         "10865a6bad39bc0a254b8b3f4cf6b013bef48770a2b39c7e9f9a70f438d56366")
        self.assertEqual(p1.PINNED[p1.BASELINE_ADMISSION],
                         "fb3c4bc99d1534222d80f7263a82fef2f883bb584e2c646aae43a7c80c4993ea")
        for candidate_only in (False, True):
            with self.subTest(candidate_only=candidate_only):
                result = p1.admit_ui_model_sources(self.original, candidate_only=candidate_only)
                self.assertEqual(result["variant"], "original-coherent-pair")
                self.assertEqual(result["observed_sha256"], self.ORIGINAL)
                self.assertEqual(result["accepted_sha256"], self.ORIGINAL)
                self.assertIsNone(result["transition"])

    def test_exact_recall_pair_binds_complete_reversal_and_candidate_scope(self):
        result = p1.admit_ui_model_sources(self.recalled, candidate_only=True)
        self.assertEqual(result["variant"], "a26-recall-controls-coherent-pair")
        self.assertEqual(result["original_pinned_sha256"], self.ORIGINAL)
        self.assertEqual(result["observed_sha256"], self.RECALLED)
        self.assertEqual(result["accepted_sha256"], self.RECALLED)
        transition = result["transition"]
        self.assertEqual(transition["id"], "ui-model-recall-controls-a26-v1")
        self.assertEqual(transition["scope"], "candidate-only")
        self.assertEqual(transition["patch"], self.PATCH)
        self.assertEqual(transition["patch_sha256"], self.PATCH_SHA256)
        self.assertEqual(transition["reversed_sha256"], self.ORIGINAL)
        self.assertTrue(transition["whole_file_reversal_verified"])
        for path, block in self.ADDITIONS.items():
            self.assertEqual(transition["inserted_blocks"][path],
                             {"bytes": len(block), "sha256": hashlib.sha256(block).hexdigest(), "occurrences": 1})

    def test_both_mixed_old_new_pairs_are_refused(self):
        for path in self.ORIGINAL:
            changed = dict(self.original)
            changed[path] = self.recalled[path]
            with self.subTest(new_path=path), self.assertRaisesRegex(ValueError, "mixed original/recall"):
                p1.admit_ui_model_sources(changed, candidate_only=True)

    def test_new_pair_is_refused_in_paired_mode(self):
        with self.assertRaisesRegex(ValueError, "paired mode requires original UiModel pair"):
            p1.admit_ui_model_sources(self.recalled, candidate_only=False)

    def test_rejects_deleted_inverted_and_weakened_validation_guard(self):
        guard = b"    if (!is_valid_control_snapshot(controls)) return {};\n"
        for replacement in (b"", b"    if (is_valid_control_snapshot(controls)) return {};\n",
                            b"    if (!std::isfinite(controls.expression)) return {};\n"):
            changed = self.changed_addition(self.IMPLEMENTATION, guard, replacement)
            with self.subTest(replacement=replacement), self.assertRaisesRegex(ValueError, "one exact complete inserted block"):
                p1.admit_ui_model_sources(changed, candidate_only=True)

    def test_rejects_changed_force_rebased_saved_reference_and_legacy_load_route(self):
        publication = b"    return publish_controls(view_, saved_controls_, pending_control_sequence_, controls, true);\n"
        for replacement in (publication.replace(b", true);", b", false);"),
                            b"    saved_controls_ = controls;\n" + publication,
                            b"    return load_controls(controls);\n"):
            changed = self.changed_addition(self.IMPLEMENTATION, publication, replacement)
            with self.subTest(replacement=replacement), self.assertRaisesRegex(ValueError, "one exact complete inserted block"):
                p1.admit_ui_model_sources(changed, candidate_only=True)

    def test_rejects_changed_declaration_and_public_contract_comment(self):
        edits = ((b"recall_controls(const ControlSnapshot& controls) noexcept;",
                  b"recall_controls(const ControlSnapshot& controls);"),
                 (b"recall_controls(const ControlSnapshot& controls)",
                  b"recall_controls(ControlSnapshot controls)"),
                 (b"it retains the clean-file", b"it replaces the clean-file"))
        for old, new in edits:
            changed = self.changed_addition(self.HEADER, old, new)
            with self.subTest(old=old), self.assertRaisesRegex(ValueError, "one exact complete inserted block"):
                p1.admit_ui_model_sources(changed, candidate_only=True)

    def test_rejects_duplicate_and_removed_inserted_blocks(self):
        for path, block in self.ADDITIONS.items():
            for replacement in (block + block, b""):
                changed = dict(self.recalled)
                changed[path] = changed[path].replace(block, replacement, 1)
                with self.subTest(path=path, copies=len(replacement) // len(block)), self.assertRaises(ValueError):
                    p1.admit_ui_model_sources(changed, candidate_only=True)

    def test_rejects_relocation_even_when_whole_block_reversal_is_original(self):
        anchors = {
            self.HEADER: b"    // Called after an off-callback parser has validated the existing file\n",
            self.IMPLEMENTATION: b"UiActions UiModel::load_controls(const ControlSnapshot& controls) noexcept {\n",
        }
        for path, anchor in anchors.items():
            self.assertEqual(self.original[path].count(anchor), 1)
            moved = self.original[path].replace(anchor, self.ADDITIONS[path] + anchor, 1)
            self.assertEqual(moved.replace(self.ADDITIONS[path], b"", 1), self.original[path])
            changed = {**self.recalled, path: moved}
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "exact admitted placement/source identity"):
                p1.admit_ui_model_sources(changed, candidate_only=True)

    def test_rejects_unrelated_old_method_changes_in_both_variants(self):
        edits = ((b"    saved_controls_ = controls;\n", b"    saved_controls_ = view_.controls;\n"),
                 (b"    if (id.kind != UiControlKind::Workspace && valid_workspace(view.workspace) &&\n",
                  b"    if (valid_workspace(view.workspace) &&\n"),
                 (b"    view.controls_dirty = !(view.controls == saved);\n", b"    view.controls_dirty = false;\n"))
        for variant, sources in (("original", self.original), ("recall", self.recalled)):
            for old, new in edits:
                self.assertEqual(sources[self.IMPLEMENTATION].count(old), 1)
                changed = {**sources, self.IMPLEMENTATION: sources[self.IMPLEMENTATION].replace(old, new, 1)}
                with self.subTest(variant=variant, old=old), self.assertRaises(ValueError):
                    p1.admit_ui_model_sources(changed, candidate_only=True)

    def test_rejects_class_data_and_old_public_declaration_changes(self):
        edits = ((b"    UiViewState view_{};\n", b"    UiViewState view_{};\n    std::uint64_t recall_revision_{0};\n"),
                 (b"load_controls(const ControlSnapshot& controls) noexcept;",
                  b"load_controls(const ControlSnapshot& controls);"))
        for variant, sources in (("original", self.original), ("recall", self.recalled)):
            for old, new in edits:
                self.assertEqual(sources[self.HEADER].count(old), 1)
                changed = {**sources, self.HEADER: sources[self.HEADER].replace(old, new, 1)}
                with self.subTest(variant=variant, old=old), self.assertRaises(ValueError):
                    p1.admit_ui_model_sources(changed, candidate_only=True)

    def test_original_pinning_needs_no_recall_patch_and_records_old_expectations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.write_root(directory, self.original)
            (root / self.PATCH).unlink()
            for candidate_only in (False, True):
                inputs = {}
                result = p1.pin_ui_model_sources(inputs, root, candidate_only=candidate_only)
                self.assertEqual(result["variant"], "original-coherent-pair")
                self.assertEqual(set(inputs), set(self.ORIGINAL))
                for path in self.ORIGINAL:
                    self.assertEqual(inputs[path]["expected_sha256"], self.ORIGINAL[path])

    def test_new_pinning_binds_patch_and_detects_later_source_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.write_root(directory, self.recalled)
            inputs = {}
            result = p1.pin_ui_model_sources(inputs, root, candidate_only=True)
            self.assertEqual(result["transition"]["patch_sha256"], self.PATCH_SHA256)
            self.assertEqual(inputs["ui_model_recall_patch"]["expected_sha256"], self.PATCH_SHA256)
            for path in self.ORIGINAL:
                self.assertEqual(inputs[path]["sha256"], self.RECALLED[path])
                self.assertEqual(inputs[path]["expected_sha256"], self.RECALLED[path])
                self.assertEqual(inputs[path]["original_pinned_sha256"], self.ORIGINAL[path])
            audit = p1.Audit()
            p1.check_inputs_unchanged(audit, inputs)
            self.assertEqual(audit.failures, [])
            (root / self.IMPLEMENTATION).write_bytes(self.recalled[self.IMPLEMENTATION] + b"\n")
            p1.check_inputs_unchanged(audit, inputs)
            self.assertEqual(len(audit.failures), 1)
            self.assertEqual(audit.failures[0]["check"], "final-input-stability:" + self.IMPLEMENTATION)

    def test_new_pinning_refuses_changed_a26_patch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.write_root(directory, self.recalled, patch_bytes=self.patch_bytes + b"\n")
            with self.assertRaisesRegex(ValueError, "reviewed input SHA-256 mismatch: ui_model_recall_patch"):
                p1.pin_ui_model_sources({}, root, candidate_only=True)

    def test_execute_refuses_bad_sources_before_any_native_launch(self):
        mixed_header = {**self.original, self.HEADER: self.recalled[self.HEADER]}
        mixed_cpp = {**self.original, self.IMPLEMENTATION: self.recalled[self.IMPLEMENTATION]}
        bad_guard = self.changed_addition(self.IMPLEMENTATION,
                                          b"    if (!is_valid_control_snapshot(controls)) return {};\n", b"")
        cases = (("mixed-header", mixed_header, True, "mixed original/recall"),
                 ("mixed-implementation", mixed_cpp, True, "mixed original/recall"),
                 ("changed-guard", bad_guard, True, "one exact complete inserted block"),
                 ("paired-new-pair", self.recalled, False, "paired mode requires original UiModel pair"))
        for name, sources, candidate_only, expected_error in cases:
            with self.subTest(case=name), tempfile.TemporaryDirectory() as directory:
                root = self.write_root(directory, sources, include_fixed=True)
                output = Path(directory) / "report"
                arguments = ["--root", str(root), "--after", str(root / "unrun-after"), "--output", str(output)]
                if candidate_only:
                    arguments.append("--candidate-only")
                else:
                    arguments += ["--before", str(root / "unrun-before"),
                                  "--before-sha256", p1.BEFORE_EXE_SHA, "--after-sha256", "1" * 64,
                                  "--before-painter", str(root / "unrun-before-painter"),
                                  "--before-painter-sha256", p1.BEFORE_PAINTER_SHA,
                                  "--after-painter-sha256", "2" * 64,
                                  "--before-source-id", "retained-original-only",
                                  "--after-source-id", "unqualified-recall-source", "--sdl-root", str(root / "unrun-sdl")]
                args = p1.cli(arguments)
                with mock.patch.object(p1.Runner, "command", side_effect=AssertionError("native launch forbidden")) as launch, \
                        mock.patch("builtins.print"):
                    status = p1.execute(args)
                launch.assert_not_called()
                self.assertEqual(status, 1)
                report = json.loads((output / "report.json").read_bytes())
                self.assertFalse(report["passed"])
                self.assertEqual(report["commands"], [])
                self.assertIsNone(report["ui_model_source_admission"])
                self.assertTrue(any(expected_error in failure["detail"] for failure in report["failures"]))


class FixtureHelperTransitionTests(unittest.TestCase):
    ORIGINAL_SHA = "4f1875270af71d08c27372944a4a9c8e4c10b6c31dbeb85b3841b6965915956c"
    REPAIRED_SHA = "a446f44bf67768aa9d9885084c1809c99102cb24413c7e640485ad17d5b3888d"
    ORIGINAL_BLOCK = (b"    if constexpr (p1_fixture_helper_present<Drawer>) {\n"
        b"        reference_performance_p1_material(drawing, bounds, scale);\n"
        b"        return true;\n    }\n    return false;\n")
    REPAIRED_BLOCK = (b"    if constexpr (p1_fixture_helper_present<Drawer>) {\n"
        b"        reference_performance_p1_material(drawing, bounds, scale);\n"
        b"        return true;\n    } else {\n        return false;\n    }\n")

    @classmethod
    def setUpClass(cls):
        current = (ROOT / p1.FIXTURE).read_bytes()
        if hashlib.sha256(current).hexdigest() == FixtureSourceTransitionTests.PORTABLE:
            _, before, after = FixtureSourceTransitionTests.REPLACEMENTS[1]
            if current.count(after) != 1:
                raise AssertionError("indexed fixture lacks its complete array replacement")
            current = current.replace(after, before, 1)
            if hashlib.sha256(current).hexdigest() != cls.REPAIRED_SHA:
                raise AssertionError("indexed fixture does not recover the exact helper predecessor")
        if hashlib.sha256(current).hexdigest() == cls.REPAIRED_SHA:
            cls.original = current.replace(cls.REPAIRED_BLOCK, cls.ORIGINAL_BLOCK, 1)
        else:
            cls.original = current
        if hashlib.sha256(cls.original).hexdigest() != cls.ORIGINAL_SHA:
            raise AssertionError("fixture does not recover the genuine original")
        cls.repaired = cls.original.replace(cls.ORIGINAL_BLOCK, cls.REPAIRED_BLOCK, 1)
        if hashlib.sha256(cls.repaired).hexdigest() != cls.REPAIRED_SHA:
            raise AssertionError("fixture does not reproduce the exact reviewed repair")

    def test_original_fixture_remains_valid_in_both_modes_with_original_pin(self):
        self.assertEqual(p1.PINNED[p1.FIXTURE], self.ORIGINAL_SHA)
        for mode in (False, True):
            with self.subTest(candidate_only=mode):
                result = p1.admit_fixture_source(self.original, candidate_only=mode)
                self.assertEqual(result["variant"], "original-fixture")
                self.assertEqual(result["accepted_sha256"], self.ORIGINAL_SHA)
                self.assertIsNone(result["transition"])

    def test_exact_helper_repair_is_reversible_and_candidate_only(self):
        result = p1.admit_fixture_source(self.repaired, candidate_only=True)
        self.assertEqual(result["original_pinned_sha256"], self.ORIGINAL_SHA)
        self.assertEqual(result["accepted_sha256"], self.REPAIRED_SHA)
        self.assertEqual(result["observed_sha256"], self.REPAIRED_SHA)
        self.assertEqual(result["transition"]["scope"], "candidate-only")
        self.assertEqual(result["transition"]["reversed_sha256"], self.ORIGINAL_SHA)
        self.assertTrue(result["transition"]["whole_file_reversal_verified"])
        with self.assertRaisesRegex(ValueError, "paired mode requires original fixture"):
            p1.admit_fixture_source(self.repaired, candidate_only=False)

    def test_boolean_mode_and_complete_bytes_are_required(self):
        for mode in (0, 1, None, "candidate-only"):
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, "mode must be boolean"):
                p1.admit_fixture_source(self.original, candidate_only=mode)
        for value in (bytearray(self.repaired), self.repaired.decode(), None):
            with self.subTest(type=type(value)), self.assertRaisesRegex(ValueError, "complete byte source"):
                p1.admit_fixture_source(value, candidate_only=True)

    def test_malformed_missing_duplicate_or_changed_helper_is_rejected(self):
        cases = {
            "missing": self.repaired.replace(self.REPAIRED_BLOCK, b"", 1),
            "duplicate": self.repaired + self.REPAIRED_BLOCK,
            "old-block-added": self.repaired + self.ORIGINAL_BLOCK,
            "predicate": self.repaired.replace(b"if constexpr (p1_fixture_helper_present<Drawer>)", b"if constexpr (true)", 1),
            "missing-call": self.repaired.replace(b"        reference_performance_p1_material(drawing, bounds, scale);\n", b"", 1),
            "true-value": self.repaired.replace(b"        return true;\n", b"        return false;\n", 1),
            "false-value": self.repaired.replace(b"        return false;\n", b"        return true;\n", 1),
        }
        for name, payload in cases.items():
            with self.subTest(name=name), mock.patch.object(p1, "P1_HELPER_ELSE_SHA256", p1.sha(payload)):
                with self.assertRaisesRegex(ValueError, "one exact complete constexpr else"):
                    p1.admit_fixture_source(payload, candidate_only=True)

    def test_repinning_does_not_admit_unrelated_bytes_or_relocated_block(self):
        cases = {"unrelated": self.repaired + b"// unrelated source change\n",
                 "relocated": self.repaired.replace(self.REPAIRED_BLOCK, b"", 1) + self.REPAIRED_BLOCK}
        for name, payload in cases.items():
            with self.subTest(name=name), mock.patch.object(p1, "P1_HELPER_ELSE_SHA256", p1.sha(payload)):
                with self.assertRaisesRegex(ValueError, "does not reconstruct original bytes"):
                    p1.admit_fixture_source(payload, candidate_only=True)

    def test_reversal_alone_does_not_replace_the_complete_repair_identity(self):
        with mock.patch.object(p1, "P1_HELPER_ELSE_SHA256", "0" * 64):
            with self.assertRaisesRegex(ValueError, "exact admitted placement/source identity"):
                p1.admit_fixture_source(self.repaired, candidate_only=True)

    def test_pinning_records_actual_and_original_identities_and_detects_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / p1.FIXTURE
            path.parent.mkdir(parents=True)
            for source, expected, mode in ((self.original, self.ORIGINAL_SHA, False),
                                          (self.repaired, self.REPAIRED_SHA, True)):
                path.write_bytes(source)
                inputs = {}
                result = p1.pin_fixture_source(inputs, root, candidate_only=mode)
                self.assertEqual(result["accepted_sha256"], expected)
                self.assertEqual(inputs[p1.FIXTURE]["sha256"], expected)
                self.assertEqual(inputs[p1.FIXTURE]["expected_sha256"], expected)
                self.assertEqual(inputs[p1.FIXTURE]["original_pinned_sha256"], self.ORIGINAL_SHA)
                audit = p1.Audit()
                p1.check_inputs_unchanged(audit, inputs)
                self.assertEqual(audit.failures, [])
                path.write_bytes(source + b"\n")
                p1.check_inputs_unchanged(audit, inputs)
                self.assertEqual(len(audit.failures), 1)

    def test_source_change_between_identity_and_read_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / p1.FIXTURE
            path.parent.mkdir(parents=True)
            path.write_bytes(self.repaired)
            claimed = p1.identity(path)
            claimed["sha256"] = self.ORIGINAL_SHA
            with mock.patch.object(p1, "identity", return_value=claimed):
                with self.assertRaisesRegex(ValueError, "source changed while reading"):
                    p1.pin_fixture_source({}, root, candidate_only=True)

    def test_execute_rejects_bad_fixture_before_any_native_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (*p1.PINNED, p1.RECALL_SOURCE_PATCH):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT / name).read_bytes())
            (root / p1.FIXTURE).write_bytes(self.repaired + b"// unreviewed\n")
            output = root / "report"
            args = p1.cli(["--root", str(root), "--candidate-only", "--after", str(root / "unrun"),
                           "--output", str(output)])
            with mock.patch.object(p1.Runner, "command", side_effect=AssertionError("native launch forbidden")) as launch, \
                    mock.patch("builtins.print"):
                result = p1.execute(args)
            launch.assert_not_called()
            self.assertEqual(result, 1)
            report = json.loads((output / "report.json").read_bytes())
            self.assertFalse(report["passed"])
            self.assertEqual(report["commands"], [])
            self.assertIsNone(report["fixture_source_admission"])
            self.assertTrue(any("fixture helper reversal" in failure["detail"] for failure in report["failures"]))


class AdditionalArrayAdmissionTests(unittest.TestCase):
    """Additional repinning/race risks beyond the complete published suite."""

    @classmethod
    def setUpClass(cls):
        cls.indexed = (ROOT / p1.FIXTURE).read_bytes()
        _, cls.original_array, cls.indexed_array = FixtureSourceTransitionTests.REPLACEMENTS[1]
        cls.helper = cls.indexed.replace(cls.indexed_array, cls.original_array, 1)
        if hashlib.sha256(cls.indexed).hexdigest() != FixtureSourceTransitionTests.PORTABLE:
            raise AssertionError("fixture is not the complete published indexed source")
        if hashlib.sha256(cls.helper).hexdigest() != FixtureSourceTransitionTests.HELPER_ELSE:
            raise AssertionError("array reversal did not recover the exact helper predecessor")

    def test_public_array_constants_match_independent_reviewed_bytes(self):
        self.assertEqual(p1.P1_INDEXED_ARRAY_SHA256, FixtureSourceTransitionTests.PORTABLE)
        self.assertEqual(p1.P1_ORIGINAL_ARRAY, self.original_array)
        self.assertEqual(p1.P1_INDEXED_ARRAY, self.indexed_array)
        self.assertEqual(p1.PINNED[p1.FIXTURE], FixtureSourceTransitionTests.ORIGINAL)

    def test_memoryview_and_byte_subclasses_are_not_complete_source_bytes(self):
        class BytesSubclass(bytes):
            pass
        for payload in (memoryview(self.indexed), BytesSubclass(self.indexed)):
            with self.subTest(type=type(payload)), self.assertRaisesRegex(ValueError, "complete byte source"):
                p1.admit_fixture_source(payload, candidate_only=True)

    def test_repinning_indexed_source_cannot_admit_structural_mutations(self):
        cases = {
            "missing": self.indexed.replace(self.indexed_array, b"", 1),
            "duplicate": self.indexed + self.indexed_array,
            "old-block-added": self.indexed + self.original_array,
            "changed-element": self.indexed.replace(b"write(out, values[index]);", b"write(out, values[0]);", 1),
            "changed-bound": self.indexed.replace(b"index < values.size()", b"index <= values.size()", 1),
        }
        for name, payload in cases.items():
            with self.subTest(name=name), mock.patch.object(p1, "P1_INDEXED_ARRAY_SHA256", p1.sha(payload)):
                with self.assertRaisesRegex(ValueError, "one exact complete indexed array block"):
                    p1.admit_fixture_source(payload, candidate_only=True)

    def test_repinning_indexed_source_cannot_admit_relocation_or_other_bytes(self):
        cases = {"append": self.indexed + b"// unrelated\n",
                 "relocation": self.indexed.replace(self.indexed_array, b"", 1) + self.indexed_array}
        for name, payload in cases.items():
            with self.subTest(name=name), mock.patch.object(p1, "P1_INDEXED_ARRAY_SHA256", p1.sha(payload)):
                with self.assertRaisesRegex(ValueError, "reversal does not reconstruct admitted helper source"):
                    p1.admit_fixture_source(payload, candidate_only=True)

    def test_repinning_indexed_and_intermediate_files_cannot_replace_original(self):
        payload = self.indexed + b"// unrelated\n"
        intermediate = payload.replace(self.indexed_array, self.original_array, 1)
        with mock.patch.object(p1, "P1_INDEXED_ARRAY_SHA256", p1.sha(payload)), \
                mock.patch.object(p1, "P1_HELPER_ELSE_SHA256", p1.sha(intermediate)):
            with self.assertRaisesRegex(ValueError, "does not reconstruct original bytes"):
                p1.admit_fixture_source(payload, candidate_only=True)

    def test_unrecognized_complete_indexed_pin_is_rejected(self):
        with mock.patch.object(p1, "P1_INDEXED_ARRAY_SHA256", "0" * 64):
            with self.assertRaises(ValueError):
                p1.admit_fixture_source(self.indexed, candidate_only=True)

    def test_indexed_identity_read_race_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / p1.FIXTURE
            path.parent.mkdir(parents=True)
            path.write_bytes(self.indexed)
            claimed = p1.identity(path)
            path.write_bytes(self.indexed + b"\n")
            with mock.patch.object(p1, "identity", return_value=claimed):
                with self.assertRaisesRegex(ValueError, "source changed while reading"):
                    p1.pin_fixture_source({}, root, candidate_only=True)


if __name__ == "__main__":
    unittest.main()
