#!/usr/bin/env python3
"""Source-only regression tests for the exact MSVC fixture transitions.

Optional image imports are inert placeholders; no image/native code is called.
Baseline tests use the retained receipt schemas with simulated file identities
to isolate source admission. They do not validate those historical binaries or
qualify the current painter, Windows execution, or H1 comparison results.
"""

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
COMPARATOR = "tools/compare_header_material.py"
ORIGINAL_SHA = "a6b65d06067d8941e44ef8680f309433a3c82ce1d6bd54d6f3f5bf8d4bde82d2"
CORRECTED_SHA = "1e5ced9f7644506863a514ee06b452601b3861ab2e581c6dff7e67c5cf7c275d"
CAST_SHA = "96149cf482ad0a57512257a519b89198113f21b06c33b073b2861e13349d1809"
HELPER_ELSE_SHA = "86acc068fa23826fb39f245f9327e919c076660f315bed5d57f63e586d6d3ac6"
ORIGINAL_COMPARATOR_SHA = "ff3e9015364c1a773bfb8ea90a0138eb9df5f2b03075e49dc8ea4457b76b5760"
OLD_LINE = b"            c.width = shape == 0 ? 1920 : 1400; c.height = shape == 0 ? 820 : 1080;\n"
NEW_LINE = b"            c.width = shape == 0 ? 1920.0F : 1400.0F; c.height = shape == 0 ? 820.0F : 1080.0F;\n"
CAST_LINE = b"            c.width = static_cast<float>(shape == 0 ? 1920 : 1400); c.height = static_cast<float>(shape == 0 ? 820 : 1080);\n"
ORIGINAL_HELPER = (b"    if constexpr (h1_fixture_helper_present<Drawer>) {\n"
    b"        reference_header_h1_material(drawing, bounds, scale);\n"
    b"        return true;\n    }\n    return false;\n")
ELSE_HELPER = (b"    if constexpr (h1_fixture_helper_present<Drawer>) {\n"
    b"        reference_header_h1_material(drawing, bounds, scale);\n"
    b"        return true;\n    } else {\n        return false;\n    }\n")

# The comparator has optional authoring dependencies. Import its actual source
# with nonfunctional image placeholders so this small gate remains stdlib-only.
PIL_STUB = SimpleNamespace(Image=object(), ImageChops=object(), ImageDraw=object(),
                           __version__="source-test-only", features=object())
with mock.patch.dict(sys.modules, {"PIL": PIL_STUB}), mock.patch.object(sys, "path", [str(TOOLS), *sys.path]):
    SPEC = importlib.util.spec_from_file_location("header_source_transition", ROOT / COMPARATOR)
    HEADER = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(HEADER)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fixture_sources():
    """Recover original and dimension-only forms from any exact valid checkout."""
    current = (ROOT / HEADER.FIXTURE).read_bytes()
    line_source = current
    if digest(current) == HELPER_ELSE_SHA:
        line_source = current.replace(ELSE_HELPER, ORIGINAL_HELPER, 1)
        if digest(line_source) != CAST_SHA:
            raise AssertionError("helper reversal did not recover the cast source")
    lines = {CORRECTED_SHA: NEW_LINE, CAST_SHA: CAST_LINE}
    current_sha = digest(line_source)
    if current_sha not in lines:
        raise AssertionError("checkout does not contain either exact reviewed fixture")
    original = line_source.replace(lines[current_sha], OLD_LINE, 1)
    if digest(original) != ORIGINAL_SHA:
        raise AssertionError("fixture reversal did not recover the original source")
    return current, original, original.replace(OLD_LINE, NEW_LINE, 1), original.replace(OLD_LINE, CAST_LINE, 1)


class FixtureTransitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current, cls.original, cls.corrected, cls.cast = fixture_sources()
        cls.helper_else = cls.cast.replace(ORIGINAL_HELPER, ELSE_HELPER, 1)

    def check_temporary_source(self, payload):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / HEADER.FIXTURE
            path.parent.mkdir(parents=True)
            path.write_bytes(payload)
            return HEADER.fixture_portability_transition(root)

    def test_exact_transition_preserves_original_pin(self):
        self.assertEqual(HEADER.PINNED[HEADER.FIXTURE], ORIGINAL_SHA)
        self.assertEqual(HEADER.PORTABLE_FIXTURE_SHA, CORRECTED_SHA)
        self.assertEqual(HEADER.BASELINE_COMPARATOR_SHA, ORIGINAL_COMPARATOR_SHA)
        self.assertEqual(digest(self.corrected), CORRECTED_SHA)
        self.assertEqual(digest(self.original), ORIGINAL_SHA)
        self.assertEqual(self.corrected.count(NEW_LINE), 1)
        transition = self.check_temporary_source(self.corrected)
        self.assertEqual(transition["baseline_fixture_sha256"], ORIGINAL_SHA)
        self.assertEqual(transition["current_fixture_sha256"], CORRECTED_SHA)
        self.assertTrue(transition["exact_single_line_reversal"])
        self.assertFalse(transition["source_bytes_identical"])

    def test_cast_transition_has_its_own_pin_and_the_same_original_bytes(self):
        self.assertEqual(HEADER.CAST_FIXTURE_SHA, CAST_SHA)
        self.assertEqual(digest(self.cast), CAST_SHA)
        self.assertEqual(self.cast.count(CAST_LINE), 1)
        self.assertEqual(self.cast.replace(CAST_LINE, OLD_LINE, 1), self.original)
        transition = self.check_temporary_source(self.cast)
        self.assertEqual(transition["baseline_fixture_sha256"], ORIGINAL_SHA)
        self.assertEqual(transition["current_fixture_sha256"], CAST_SHA)
        self.assertEqual(transition["baseline_comparator_sha256"], ORIGINAL_COMPARATOR_SHA)
        self.assertEqual(transition["current_fixture_repair"], "explicit-float-casts")
        self.assertEqual(transition["reviewed_current_fixture_sha256"],
                         {"float-literals": CORRECTED_SHA, "explicit-float-casts": CAST_SHA})
        self.assertTrue(transition["exact_single_line_reversal"])
        self.assertTrue(transition["case_values_preserved"])
        self.assertFalse(transition["source_bytes_identical"])

    def test_current_checkout_reports_its_actual_admitted_identity(self):
        transition = HEADER.fixture_portability_transition(ROOT)
        current_sha = digest(self.current)
        self.assertIn(current_sha, (CORRECTED_SHA, CAST_SHA, HELPER_ELSE_SHA))
        self.assertEqual(transition["current_fixture_sha256"], current_sha)
        self.assertEqual(transition["current_fixture_repair"],
                         {CORRECTED_SHA: "float-literals", CAST_SHA: "explicit-float-casts",
                          HELPER_ELSE_SHA: "explicit-float-casts-and-constexpr-else"}[current_sha])

    def test_helper_else_reverses_through_exact_cast_and_original(self):
        self.assertEqual(HEADER.HELPER_ELSE_FIXTURE_SHA, HELPER_ELSE_SHA)
        self.assertEqual(digest(self.helper_else), HELPER_ELSE_SHA)
        self.assertEqual(self.helper_else.replace(ELSE_HELPER, ORIGINAL_HELPER, 1), self.cast)
        result = self.check_temporary_source(self.helper_else)
        self.assertEqual(result["current_fixture_sha256"], HELPER_ELSE_SHA)
        self.assertEqual(result["intermediate_fixture_sha256"], CAST_SHA)
        self.assertEqual(result["baseline_fixture_sha256"], ORIGINAL_SHA)
        self.assertEqual(result["baseline_comparator_sha256"], ORIGINAL_COMPARATOR_SHA)
        self.assertFalse(result["exact_single_line_reversal"])
        self.assertTrue(result["exact_helper_branch_reversal"])
        self.assertFalse(result["source_bytes_identical"])

    def test_helper_else_rejects_all_unreviewed_complete_files(self):
        cases = {
            "literal-combination": self.corrected.replace(ORIGINAL_HELPER, ELSE_HELPER, 1),
            "no-dimension-repair": self.original.replace(ORIGINAL_HELPER, ELSE_HELPER, 1),
            "false-changed": self.helper_else.replace(b"        return false;\n", b"        return true;\n", 1),
            "missing-call": self.helper_else.replace(b"        reference_header_h1_material(drawing, bounds, scale);\n", b"", 1),
            "unrelated-append": self.helper_else + b"// unrelated source change\n",
        }
        for name, payload in cases.items():
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "current pin"):
                self.check_temporary_source(payload)

    def test_repinning_helper_else_cannot_admit_missing_or_malformed_branch(self):
        cases = {
            "missing": self.helper_else.replace(ELSE_HELPER, b"", 1),
            "duplicate": self.helper_else + ELSE_HELPER,
            "old-block-added": self.helper_else + ORIGINAL_HELPER,
            "false-changed": self.helper_else.replace(b"        return false;\n", b"        return true;\n", 1),
            "predicate-changed": self.helper_else.replace(b"if constexpr (h1_fixture_helper_present<Drawer>)", b"if constexpr (true)", 1),
        }
        for name, payload in cases.items():
            with self.subTest(name=name), mock.patch.object(HEADER, "HELPER_ELSE_FIXTURE_SHA", digest(payload)):
                with self.assertRaisesRegex(ValueError, "exactly the reviewed constexpr else"):
                    self.check_temporary_source(payload)

    def test_repinning_helper_else_cannot_admit_other_changes_or_relocation(self):
        cases = {
            "unrelated-append": self.helper_else + b"// unrelated source change\n",
            "relocated-block": self.helper_else.replace(ELSE_HELPER, b"", 1) + ELSE_HELPER,
            "literal-combination": self.helper_else.replace(CAST_LINE, NEW_LINE, 1),
            "changed-value": self.helper_else.replace(CAST_LINE, CAST_LINE.replace(b"820", b"821"), 1),
        }
        for name, payload in cases.items():
            with self.subTest(name=name), mock.patch.object(HEADER, "HELPER_ELSE_FIXTURE_SHA", digest(payload)):
                with self.assertRaisesRegex(ValueError, "does not reproduce the reviewed cast"):
                    self.check_temporary_source(payload)

    def test_repinning_both_helper_and_cast_cannot_replace_original(self):
        payload = self.helper_else + b"// unrelated source change\n"
        intermediate = payload.replace(ELSE_HELPER, ORIGINAL_HELPER, 1)
        with mock.patch.object(HEADER, "HELPER_ELSE_FIXTURE_SHA", digest(payload)), \
                mock.patch.object(HEADER, "CAST_FIXTURE_SHA", digest(intermediate)):
            with self.assertRaisesRegex(ValueError, "does not reproduce the genuine baseline"):
                self.check_temporary_source(payload)

    def test_original_partial_and_unrelated_source_edits_are_rejected(self):
        cases = {
            "original": self.original,
            "width-only": self.original.replace(b"1920 : 1400", b"1920.0F : 1400.0F", 1),
            "changed-dimension": self.corrected.replace(b"1920.0F", b"1921.0F", 1),
            "unrelated-append": self.corrected + b"// unrelated source change\n",
        }
        for name, payload in cases.items():
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "current pin"):
                self.check_temporary_source(payload)

    def test_repinning_does_not_admit_unrelated_edits(self):
        payload = self.corrected + b"// unrelated source change\n"
        with mock.patch.object(HEADER, "PORTABLE_FIXTURE_SHA", digest(payload)):
            with self.assertRaisesRegex(ValueError, "does not reproduce the genuine baseline"):
                self.check_temporary_source(payload)

    def test_repinning_does_not_admit_missing_duplicate_or_changed_line(self):
        cases = {
            "missing": self.corrected.replace(NEW_LINE, b"", 1),
            "duplicate": self.corrected + NEW_LINE,
            "changed-value": self.corrected.replace(NEW_LINE, NEW_LINE.replace(b"820.0F", b"821.0F"), 1),
            "old-line-added": self.corrected + OLD_LINE,
        }
        for name, payload in cases.items():
            with self.subTest(name=name), mock.patch.object(HEADER, "PORTABLE_FIXTURE_SHA", digest(payload)):
                with self.assertRaisesRegex(ValueError, "exactly the reviewed MSVC"):
                    self.check_temporary_source(payload)

    def test_cast_partial_mixed_malformed_and_other_sources_are_rejected(self):
        width_cast = b"static_cast<float>(shape == 0 ? 1920 : 1400)"
        height_cast = b"static_cast<float>(shape == 0 ? 820 : 1080)"
        cases = {
            "width-cast-only": self.original.replace(b"shape == 0 ? 1920 : 1400", width_cast, 1),
            "height-cast-only": self.original.replace(b"shape == 0 ? 820 : 1080", height_cast, 1),
            "literal-width-cast-height": self.cast.replace(width_cast, b"shape == 0 ? 1920.0F : 1400.0F", 1),
            "cast-width-literal-height": self.cast.replace(height_cast, b"shape == 0 ? 820.0F : 1080.0F", 1),
            "changed-value": self.cast.replace(CAST_LINE, CAST_LINE.replace(b"1920", b"1921"), 1),
            "double-cast": self.cast.replace(b"static_cast<float>", b"static_cast<double>", 1),
            "missing-parenthesis": self.cast.replace(CAST_LINE, CAST_LINE.replace(b"1400)", b"1400"), 1),
            "commented-line": self.cast.replace(CAST_LINE, b"//" + CAST_LINE, 1),
            "unrelated-append": self.cast + b"// unrelated source change\n",
        }
        for name, payload in cases.items():
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "current pin"):
                self.check_temporary_source(payload)

    def test_repinning_cast_does_not_admit_mixed_or_malformed_complete_lines(self):
        cases = {
            "missing": self.cast.replace(CAST_LINE, b"", 1),
            "duplicate": self.cast + CAST_LINE,
            "changed-value": self.cast.replace(CAST_LINE, CAST_LINE.replace(b"820", b"821"), 1),
            "old-line-added": self.cast + OLD_LINE,
            "other-repair-added": self.cast + NEW_LINE,
            "mixed-width": self.cast.replace(CAST_LINE, CAST_LINE.replace(
                b"static_cast<float>(shape == 0 ? 1920 : 1400)", b"shape == 0 ? 1920.0F : 1400.0F"), 1),
            "mixed-height": self.cast.replace(CAST_LINE, CAST_LINE.replace(
                b"static_cast<float>(shape == 0 ? 820 : 1080)", b"shape == 0 ? 820.0F : 1080.0F"), 1),
            "comment-prefix": self.cast.replace(CAST_LINE, b"//" + CAST_LINE, 1),
            "crlf-line": self.cast.replace(CAST_LINE, CAST_LINE[:-1] + b"\r\n", 1),
        }
        for name, payload in cases.items():
            with self.subTest(name=name), mock.patch.object(HEADER, "CAST_FIXTURE_SHA", digest(payload)):
                with self.assertRaisesRegex(ValueError, "exactly the reviewed MSVC"):
                    self.check_temporary_source(payload)

    def test_repinning_either_form_does_not_admit_unrelated_edits_or_relocation(self):
        for pin, source, line in (("PORTABLE_FIXTURE_SHA", self.corrected, NEW_LINE),
                                  ("CAST_FIXTURE_SHA", self.cast, CAST_LINE)):
            cases = {"unrelated-append": source + b"// unrelated source change\n",
                     "relocated-line": source.replace(line, b"", 1) + line}
            for name, payload in cases.items():
                with self.subTest(pin=pin, name=name), mock.patch.object(HEADER, pin, digest(payload)):
                    with self.assertRaisesRegex(ValueError, "does not reproduce the genuine baseline"):
                        self.check_temporary_source(payload)


class BaselineTransitionTests(unittest.TestCase):
    def setUp(self):
        self.current, self.original, self.corrected, self.cast = fixture_sources()
        self.helper_else = self.cast.replace(ORIGINAL_HELPER, ELSE_HELPER, 1)
        self.current_sha = digest(self.current)
        self.receipt_path = ROOT / HEADER.BASELINE
        self.receipt = json.loads(self.receipt_path.read_bytes())
        self.receipt_sha = digest(self.receipt_path.read_bytes())
        self.supplement = json.loads((self.receipt_path.parent / "h1-fixture-baseline-identity.json").read_bytes())
        protected_record = json.loads((ROOT / HEADER.PROTECTED).read_bytes())
        protected = {name: row for group in protected_record["groups"].values()
                     for name, row in group["files"].items()}
        self.identities = {
            str(ROOT / name): {"path": str(ROOT / name), "sha256": sha,
                              "bytes": protected.get(name, {}).get("bytes", 1)}
            for name, sha in self.receipt["source_sha256"].items()
        }
        self.before = Path(self.supplement["binary"]["path"])
        self.after = ROOT / "simulated-after-header-fixture"
        self.identities[str(self.before)] = deepcopy(self.supplement["binary"])
        self.identities[str(self.after)] = {"path": str(self.after), "bytes": 1, "sha256": "1" * 64}
        self.identities[str(self.before.parent / "hammond_standalone")] = deepcopy(
            self.receipt["files"]["hammond_standalone"])
        for row in [*self.supplement["inputs"], self.supplement["object"]]:
            self.identities[row["path"]] = deepcopy(row)
        self.source_files = {
            HEADER.FIXTURE: HEADER.identity(ROOT / HEADER.FIXTURE),
            HEADER.PAINTER: HEADER.identity(ROOT / HEADER.PAINTER),
            COMPARATOR: HEADER.identity(ROOT / COMPARATOR),
        }
        self.before_painter = {"sha256": HEADER.BEFORE_PAINTER_SHA}
        self.real_identity = HEADER.identity

    def identity(self, path):
        result = self.identities.get(str(path))
        return deepcopy(result) if result is not None else self.real_identity(path)

    def admit(self, supplement=None, source_files=None, fixture_payload=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "supplement.json"
            path.write_text(json.dumps(self.supplement if supplement is None else supplement), encoding="utf-8")
            root = ROOT
            sources = deepcopy(self.source_files if source_files is None else source_files)
            if fixture_payload is not None:
                root = Path(directory) / "source"
                for name, data in ((HEADER.FIXTURE, fixture_payload),
                                   (HEADER.PROTECTED, (ROOT / HEADER.PROTECTED).read_bytes())):
                    target = root / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
                if source_files is None:
                    sources[HEADER.FIXTURE] = HEADER.identity(root / HEADER.FIXTURE)

            def identity(source):
                source = Path(source)
                if root != ROOT and source.is_relative_to(root):
                    source = ROOT / source.relative_to(root)
                return self.identity(source)

            with mock.patch.object(HEADER, "identity", side_effect=identity):
                return HEADER.baseline_inputs(root, self.receipt_path, self.receipt_sha, path,
                    self.before, self.after, self.before_painter, sources, False)

    def test_original_baseline_identities_are_admitted_with_exact_transition(self):
        result = self.admit()
        transition = result["fixture_portability_transition"]
        self.assertEqual(transition["baseline_fixture_sha256"], ORIGINAL_SHA)
        self.assertEqual(transition["current_fixture_sha256"], self.current_sha)
        self.assertEqual(transition["baseline_comparator_sha256"], ORIGINAL_COMPARATOR_SHA)
        retained = {row["sha256"] for row in result["retained_build_inputs"]}
        self.assertIn(ORIGINAL_SHA, retained)
        self.assertNotIn(CORRECTED_SHA, retained)
        self.assertNotIn(CAST_SHA, retained)
        self.assertNotIn(HELPER_ELSE_SHA, retained)

    def test_helper_else_current_identity_cannot_replace_original_or_other_current(self):
        result = self.admit(fixture_payload=self.helper_else)
        self.assertEqual(result["fixture_portability_transition"]["current_fixture_sha256"], HELPER_ELSE_SHA)
        for wrong in (ORIGINAL_SHA, CORRECTED_SHA, CAST_SHA):
            sources = deepcopy(self.source_files)
            sources[HEADER.FIXTURE]["sha256"] = wrong
            with self.subTest(wrong=wrong), self.assertRaisesRegex(ValueError, "current fixture identity"):
                self.admit(source_files=sources, fixture_payload=self.helper_else)
        supplement = deepcopy(self.supplement)
        supplement["source_sha256"][HEADER.FIXTURE] = HELPER_ELSE_SHA
        with self.assertRaisesRegex(ValueError, "exact original"):
            self.admit(supplement=supplement, fixture_payload=self.helper_else)

    def test_helper_else_preserves_original_paired_uimodel_and_main_pins(self):
        for name in ("apps/standalone/UiModel.cpp", "apps/standalone/UiModel.h", "apps/standalone/main.cpp"):
            key = str(ROOT / name)
            changed = deepcopy(self.identities[key])
            changed["sha256"] = "0" * 64
            with self.subTest(path=name), mock.patch.dict(self.identities, {key: changed}):
                with self.assertRaisesRegex(ValueError, "protected pre/post-H1 source differs"):
                    self.admit(fixture_payload=self.helper_else)

    def test_both_fixture_forms_keep_the_genuine_original_baseline(self):
        for payload, expected in ((self.corrected, CORRECTED_SHA), (self.cast, CAST_SHA)):
            with self.subTest(current=expected):
                result = self.admit(fixture_payload=payload)
                transition = result["fixture_portability_transition"]
                self.assertEqual(transition["current_fixture_sha256"], expected)
                self.assertEqual(transition["baseline_fixture_sha256"], ORIGINAL_SHA)
                self.assertEqual(transition["baseline_comparator_sha256"], ORIGINAL_COMPARATOR_SHA)
                retained = {row["sha256"] for row in result["retained_build_inputs"]}
                self.assertIn(ORIGINAL_SHA, retained)
                self.assertTrue(retained.isdisjoint((CORRECTED_SHA, CAST_SHA)))

    def test_missing_current_or_arbitrary_baseline_identities_are_rejected(self):
        for name, current_sha in ((HEADER.FIXTURE, CORRECTED_SHA),
                                  (COMPARATOR, self.source_files[COMPARATOR]["sha256"]),
                                  (HEADER.PAINTER, "2" * 64)):
            for value in (None, current_sha, "0" * 64):
                supplement = deepcopy(self.supplement)
                if value is None:
                    del supplement["source_sha256"][name]
                else:
                    supplement["source_sha256"][name] = value
                with self.subTest(name=name, value=value), self.assertRaisesRegex(ValueError, "exact original"):
                    self.admit(supplement)

    def test_stale_current_fixture_identity_is_rejected(self):
        sources = deepcopy(self.source_files)
        sources[HEADER.FIXTURE]["sha256"] = ORIGINAL_SHA
        with self.assertRaisesRegex(ValueError, "current fixture identity"):
            self.admit(source_files=sources)

    def test_changed_retained_fixture_and_object_identities_are_rejected(self):
        for target in ("fixture", "object"):
            supplement = deepcopy(self.supplement)
            row = (next(row for row in supplement["inputs"] if row["sha256"] == ORIGINAL_SHA)
                   if target == "fixture" else supplement["object"])
            row["sha256"] = "0" * 64
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, "retained baseline build input changed"):
                self.admit(supplement)

    def test_missing_retained_original_fixture_is_rejected(self):
        supplement = deepcopy(self.supplement)
        supplement["inputs"] = [row for row in supplement["inputs"] if row["sha256"] != ORIGINAL_SHA]
        with self.assertRaisesRegex(ValueError, "genuine original fixture input bytes"):
            self.admit(supplement)

    def test_other_reviewed_current_identity_cannot_replace_actual_or_original(self):
        for payload, other in ((self.corrected, CAST_SHA), (self.cast, CORRECTED_SHA)):
            sources = deepcopy(self.source_files)
            sources[HEADER.FIXTURE]["sha256"] = other
            with self.subTest(other_current=other), self.assertRaisesRegex(ValueError, "current fixture identity"):
                self.admit(source_files=sources, fixture_payload=payload)
            for baseline_sha in (CORRECTED_SHA, CAST_SHA):
                supplement = deepcopy(self.supplement)
                supplement["source_sha256"][HEADER.FIXTURE] = baseline_sha
                with self.subTest(other_current=other, baseline=baseline_sha):
                    with self.assertRaisesRegex(ValueError, "exact original"):
                        self.admit(supplement=supplement, fixture_payload=payload)

    def test_original_paired_uimodel_and_main_source_pins_remain_required(self):
        for payload in (self.corrected, self.cast):
            for name in ("apps/standalone/UiModel.cpp", "apps/standalone/UiModel.h", "apps/standalone/main.cpp"):
                key = str(ROOT / name)
                changed = deepcopy(self.identities[key])
                changed["sha256"] = "0" * 64
                with self.subTest(current=digest(payload), path=name), mock.patch.dict(self.identities, {key: changed}):
                    with self.assertRaisesRegex(ValueError, "protected pre/post-H1 source differs"):
                        self.admit(fixture_payload=payload)


if __name__ == "__main__":
    unittest.main()
