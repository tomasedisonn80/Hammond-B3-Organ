#!/usr/bin/env python3
"""Archive smoke and focused mutations, using tiny sources for all small cases."""

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/check_repository.py"
SPEC = importlib.util.spec_from_file_location("check_repository", TOOL)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


class RepositoryMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Small structured navigation is reused; never copy/hard-link the PDF.
        cls.original_index = json.loads((ROOT / CHECKER.INDEX).read_text(encoding="utf-8"))

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="hammond-integrity-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        raw = b"tiny synthetic bytes for integrity mutation tests\n"
        self.manifest = {"schema_version": 1, "path": "atlas.pdf", "sha256": sha(raw),
                         "bytes": len(raw), "pages": 500, "edition": "test-fixture"}
        self.write("atlas.pdf", raw)
        self.write_json(CHECKER.MANIFEST, self.manifest)
        self.index = copy.deepcopy(self.original_index)
        self.index["source"] = {key: self.manifest[key] for key in ("path", "sha256", "bytes", "pages", "edition")}
        self.write_json(CHECKER.INDEX, self.index)
        for record in self.index["review_ranges"]:
            relative = (Path("docs/research") / record["note"]).as_posix()
            self.write(relative, f"# Review {record['review']}\n")
        self.source = {key: self.manifest[key] for key in ("path", "sha256", "edition")}
        self.profile = {"profile_id": "test-profile", "source_document": self.source,
                        "logical_parameter": {"path": "manual.upper.bank.A.drawbar.16ft"}}
        self.write_json(CHECKER.PROFILE, self.profile)
        self.write_json("data/pedal-map.json", {"provenance": {"source_document": self.source}})
        self.write_json("data/profile.schema.json", {"properties": {"source_document": {
            "properties": {key: {"const": value} for key, value in self.source.items()}}}})
        score = b"0 note_on upper 60 100\n20 note_off upper 60 0\n"
        self.write("examples/fixtures/tiny.events", score)
        self.catalog = {"schema_version": 1, "profile": {
            "id": "test-profile", "authoring_path": CHECKER.PROFILE,
            "authoring_sha256": sha(canonical(self.profile)), "compiled_sha256": "0" * 64},
            "fixtures": [{"id": "tiny", "events": {"path": "tiny.events", "sha256": sha(score)}}]}
        self.write_json(CHECKER.CATALOG, self.catalog)
        self.write("README.md", "# Test archive\n\n[Source](atlas.pdf#page=1)\n"
                   "[Index](docs/research/chapter-index.json)\n[Notes](docs/development/agent-notes/)\n")

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))

    def write_json(self, relative, value):
        self.write(relative, json.dumps(value, indent=2, ensure_ascii=False) + "\n")

    def report(self, **kwargs):
        return CHECKER.check_repository(self.root, **kwargs)

    def assert_passes(self, **kwargs):
        result = self.report(**kwargs)
        self.assertEqual(result["status"], "passed", result["errors"])
        return result

    def assert_fails(self, check, text=None):
        result = self.report()
        self.assertEqual(result["status"], "failed", result)
        self.assertEqual(result["checks"][check]["status"], "failed", result)
        errors = [error["message"] for error in result["errors"] if error["check"] == check]
        self.assertTrue(errors)
        if text:
            self.assertTrue(any(text in message for message in errors), errors)
        return result

    def test_minimal_archive_passes_without_git_or_build_inputs(self):
        result = self.assert_passes(expected_agents=6)
        self.assertFalse((self.root / ".git").exists())
        self.assertLess((self.root / "atlas.pdf").stat().st_size, 100)
        self.assertEqual(result["checks"]["chapter_index"]["pages"], 500)
        self.assertEqual(result["physical_fidelity"], "not_established")

    def test_changed_source_bytes_fail_even_with_unchanged_length(self):
        path = self.root / "atlas.pdf"
        raw = path.read_bytes()
        path.write_bytes(b"X" + raw[1:])
        self.assert_fails("source_identity", "source SHA-256")

    def test_missing_source_fails(self):
        (self.root / "atlas.pdf").unlink()
        self.assert_fails("source_identity", "atlas.pdf")

    def test_wrong_manifest_byte_count_fails(self):
        self.manifest["bytes"] += 1
        self.write_json(CHECKER.MANIFEST, self.manifest)
        self.assert_fails("source_identity", "source byte length")

    def test_manifest_page_count_is_not_self_validating(self):
        self.manifest["pages"] = 499
        self.write_json(CHECKER.MANIFEST, self.manifest)
        self.assert_fails("source_identity", "pages")

    def test_missing_manifest_fields_produce_check_failures_not_exceptions(self):
        original = dict(self.manifest)
        for key in ("path", "sha256", "bytes", "pages", "edition"):
            with self.subTest(key=key):
                value = dict(original)
                del value[key]
                self.write_json(CHECKER.MANIFEST, value)
                self.assert_fails("source_identity", key)

    def test_inconsistent_index_source_identity_fails(self):
        self.index["source"]["sha256"] = "0" * 64
        self.write_json(CHECKER.INDEX, self.index)
        self.assert_fails("chapter_index", "source: sha256")

    def test_missing_chapter_fails(self):
        del self.index["chapters"][42]
        self.write_json(CHECKER.INDEX, self.index)
        self.assert_fails("chapter_index", "chapter count")

    def test_chapter_gap_overlap_and_duplicate_id_fail(self):
        original = copy.deepcopy(self.index)
        for key, value in (("start_page", 14), ("end_page", 19), ("number", 2), ("chapter_id", "002")):
            with self.subTest(key=key):
                self.index = copy.deepcopy(original)
                self.index["chapters"][0][key] = value
                self.write_json(CHECKER.INDEX, self.index)
                self.assert_fails("chapter_index", f"chapter 1.{key}")

    def test_front_matter_directory_and_chapter_section_ranges_fail(self):
        original = copy.deepcopy(self.index)
        for position, key, value in ((0, "end_page", 11), (1, "chapter_count", 79), (2, "start_page", 492)):
            with self.subTest(position=position):
                self.index = copy.deepcopy(original)
                self.index["sections"][position][key] = value
                self.write_json(CHECKER.INDEX, self.index)
                self.assert_fails("chapter_index", "section ")

    def test_review_coverage_gap_overlap_and_missing_tail_fail(self):
        original = copy.deepcopy(self.index)
        for position, key, value in ((1, "start_page", 86), (1, "start_page", 84), (5, "end_page", 499)):
            with self.subTest(position=position, value=value):
                self.index = copy.deepcopy(original)
                self.index["review_ranges"][position][key] = value
                if key == "end_page":
                    self.index["review_ranges"][position]["page_count"] -= 1
                self.write_json(CHECKER.INDEX, self.index)
                self.assert_fails("chapter_index", "review")

    def test_chapter_note_must_cover_its_pages(self):
        self.index["chapters"][0]["review_note"] = self.index["review_ranges"][1]["note"]
        self.write_json(CHECKER.INDEX, self.index)
        self.assert_fails("chapter_index", "review_note")

    def test_missing_index_note_is_an_actual_local_data_reference(self):
        self.index["review_ranges"][0]["note"] = "../development/agent-notes/01-missing.md"
        self.write_json(CHECKER.INDEX, self.index)
        self.assert_fails("chapter_index", "01-missing.md")

    def test_research_wave_cannot_silently_change_chapter_or_page_coverage(self):
        self.index["research_waves"][9]["last_chapter"] = 79
        self.write_json(CHECKER.INDEX, self.index)
        self.assert_fails("chapter_index", "research wave 10.last_chapter")

    def test_reconstruction_status_and_strict_integer_types_are_preserved(self):
        original = copy.deepcopy(self.index)
        self.index["index_provenance"]["status"] = "recovered_original_companion"
        self.write_json(CHECKER.INDEX, self.index)
        self.assert_fails("chapter_index", "index_provenance.status")
        self.index = original
        self.index["chapters"][0]["number"] = True
        self.write_json(CHECKER.INDEX, self.index)
        self.assert_fails("chapter_index", "chapter 1.number")

    def test_missing_markdown_file_reports_origin_and_line(self):
        self.write("docs/guide.md", "# Guide\n\n[missing](missing.md)\n")
        self.assert_fails("markdown_links", "docs/guide.md:3: missing.md")

    def test_wrong_relative_link_fails_despite_same_name_at_root(self):
        self.write("docs/guide.md", "[wrong relative root](atlas.pdf)\n")
        self.assert_fails("markdown_links", "docs/guide.md:1: atlas.pdf")

    def test_external_urls_anchors_and_literal_paths_are_skipped(self):
        self.write("docs/guide.md", "[web](https://invalid.example/not-here.md)\n"
                   "[mail](mailto:someone@example.invalid)\n[cdn](//invalid.example/file)\n"
                   "[heading](#not-a-validated-anchor)\n`absent/factory-manual.pdf` is not supplied.\n")
        result = self.assert_passes()
        self.assertEqual(result["checks"]["markdown_links"]["external_links_skipped"], 3)

    def test_fences_inline_code_and_comments_do_not_create_links(self):
        self.write("docs/guide.md", "```md\n[missing](missing-a.md)\n```\n"
                   "~~~~md\n~~~\n[missing](missing-b.md)\n~~~~\n"
                   "> ```md\n> [missing](missing-c.md)\n> ```\n"
                   "`[missing](missing-d.md)` and ``[missing](missing-e.md)``\n"
                   "<!-- [missing](missing-f.md) -->\n[real `code` label](../atlas.pdf)\n")
        self.assert_passes()
        self.write("docs/guide.md", "```md\n[ignored](missing.md)\n```\n[actual](absent.md)\n")
        self.assert_fails("markdown_links", "docs/guide.md:4: absent.md")

    def test_images_are_local_links(self):
        self.write("docs/guide.md", "![image](missing.png)\n")
        self.assert_fails("markdown_links", "missing.png")

    def test_encoded_angle_balanced_and_escaped_destinations(self):
        self.write("docs/a b.md", "# Space\n")
        self.write("docs/a(b).md", "# Parentheses\n")
        self.write("docs/a&b.md", "# Entity\n")
        self.write("docs/guide.md", "[encoded](a%20b.md#section)\n[angle](<a b.md> 'title')\n"
                   "[balanced](a(b).md \"title\")\n[escaped](a\\(b\\).md)\n"
                   "[entity](a&amp;b.md)\n[root](/atlas.pdf?download=1)\n[root directory](/)\n")
        self.assert_passes()

    def test_used_full_collapsed_and_shortcut_references_are_checked(self):
        self.write("docs/guide.md", "[Full][Missing ID]\n[Collapsed][]\n[Shortcut]\n\n"
                   "[missing id]: missing-full.md \"title\"\n"
                   "[Collapsed]: <missing-collapsed.md>\n[Shortcut]: missing-shortcut.md\n")
        result = self.assert_fails("markdown_links", "missing-full.md")
        messages = "\n".join(error["message"] for error in result["errors"])
        self.assertIn("missing-collapsed.md", messages)
        self.assertIn("missing-shortcut.md", messages)

    def test_unused_and_fenced_reference_definitions_are_not_links(self):
        self.write("docs/guide.md", "[Unused]: missing.md\n\n```md\n[Example]: missing.md\n```\n"
                   "[ordinary bracket text] and [Example]\n[used][valid]\n\n[valid]:\n  ../atlas.pdf\n")
        self.assert_passes()

    def test_local_link_cannot_escape_the_archive(self):
        self.write("docs/guide.md", "[escape](../../outside.md)\n")
        self.assert_fails("markdown_links", "escapes repository")

    def test_partial_note_progress_allows_gaps_by_default(self):
        self.write(CHECKER.NOTES + "/12-later-task.md", "# Later assignment\n")
        result = self.assert_passes()
        self.assertIn(12, result["checks"]["agent_notes"]["ids"])
        failed = self.report(expected_agents=12)
        self.assertEqual(failed["checks"]["agent_notes"]["status"], "failed")
        self.assertIn("missing=[7, 8, 9, 10, 11]", failed["errors"][0]["message"])

    def test_duplicate_note_id_fails(self):
        self.write(CHECKER.NOTES + "/01-second-assignment.md", "# Duplicate\n")
        self.assert_fails("agent_notes", "duplicate agent-note ID 1")

    def test_invalid_zero_and_noncanonical_note_ids_fail(self):
        for name in ("00-invalid.md", "1-missing-padding.md", "001-extra-padding.md", "report.md"):
            with self.subTest(name=name):
                self.write(CHECKER.NOTES + "/" + name, "# Invalid\n")
                self.assert_fails("agent_notes", name)
                (self.root / CHECKER.NOTES / name).unlink()

    def test_changed_event_bytes_and_wrong_hash_fail(self):
        path = self.root / "examples/fixtures/tiny.events"
        original = path.read_bytes()
        path.write_bytes(original.replace(b"100", b"101"))
        self.assert_fails("data_references", "event SHA-256")
        path.write_bytes(original)
        self.catalog["fixtures"][0]["events"]["sha256"] = "0" * 64
        self.write_json(CHECKER.CATALOG, self.catalog)
        self.assert_fails("data_references", "event SHA-256")

    def test_missing_or_traversing_event_path_fails(self):
        for path in ("missing.events", "../outside.events"):
            with self.subTest(path=path):
                self.catalog["fixtures"][0]["events"]["path"] = path
                self.write_json(CHECKER.CATALOG, self.catalog)
                self.assert_fails("data_references")

    def test_canonical_profile_hash_ignores_formatting_but_detects_content(self):
        self.write(CHECKER.PROFILE, canonical(self.profile))
        self.assert_passes()
        self.profile["logical_parameter"]["path"] = "different.logical.control"
        self.write_json(CHECKER.PROFILE, self.profile)
        self.assert_fails("data_references", "canonical authoring SHA-256")

    def test_catalog_profile_path_is_required(self):
        self.catalog["profile"]["authoring_path"] = "data/profiles/absent.json"
        self.write_json(CHECKER.CATALOG, self.catalog)
        self.assert_fails("data_references", "absent.json")

    def test_absent_profile_ids_cannot_agree_by_omission(self):
        del self.profile["profile_id"]
        del self.catalog["profile"]["id"]
        self.catalog["profile"]["authoring_sha256"] = sha(canonical(self.profile))
        self.write_json(CHECKER.PROFILE, self.profile)
        self.write_json(CHECKER.CATALOG, self.catalog)
        self.assert_fails("data_references", "profile ID is missing")

    def test_pedal_and_schema_source_references_must_match_manifest(self):
        wrong = dict(self.source, sha256="0" * 64)
        self.write_json("data/pedal-map.json", {"provenance": {"source_document": wrong}})
        self.assert_fails("data_references", "pedal source_document: sha256")
        self.write_json("data/pedal-map.json", {"provenance": {"source_document": self.source}})
        self.write_json("data/profile.schema.json", {"properties": {"source_document": {
            "properties": {key: {"const": value} for key, value in wrong.items()}}}})
        self.assert_fails("data_references", "schema source sha256")

    def test_json_duplicate_keys_nonfinite_and_deep_input_fail_clearly(self):
        for content in ('{"schema_version":1,"schema_version":1}', '{"pages":NaN}',
                        '{"nested":' + '[' * 2000 + '0' + ']' * 2000 + '}'):
            with self.subTest(prefix=content[:50]):
                self.write(CHECKER.MANIFEST, content)
                self.assert_fails("source_identity", "source-manifest.json")

    def test_oversized_source_score_and_markdown_fail_without_full_read(self):
        with (self.root / "atlas.pdf").open("wb") as output:
            output.truncate(CHECKER.MAX_SOURCE_BYTES + 1)
        self.assert_fails("source_identity", "byte read bound")
        self.write("examples/fixtures/tiny.events", b"x" * 16385)
        self.assert_fails("data_references", "byte read bound")
        with (self.root / "README.md").open("wb") as output:
            output.truncate(CHECKER.MAX_TEXT_BYTES + 1)
        self.assert_fails("markdown_links", "byte read bound")

    def test_inventory_and_total_read_bounds_are_enforced(self):
        with mock.patch.object(CHECKER, "MAX_ENTRIES", 2):
            self.assert_fails("markdown_links", "inventory exceeds")
        with mock.patch.object(CHECKER, "MAX_TOTAL_BYTES", 10):
            self.assert_fails("source_identity", "total bound")

    def test_build_and_output_trees_are_not_read(self):
        for path in ("build/broken.md", "unrelated-build/broken.md", "out/broken.md",
                     "docs/build-debug/broken.md", "docs/generated/broken.md"):
            self.write(path, b"\xff [bad](absent.md)\n")
        self.write("docs/generated/CMakeCache.txt", "not interpreted\n")
        self.assert_passes()

    def test_cli_succeeds_without_git_on_path_and_does_not_write_archive(self):
        before = {str(path.relative_to(self.root)): path.read_bytes()
                  for path in self.root.rglob("*") if path.is_file()}
        result = subprocess.run([sys.executable, "-B", str(TOOL), "--root", str(self.root),
                                 "--expected-agents", "6", "--json"], cwd=self.temporary.name,
                                env=dict(os.environ, PATH=""), capture_output=True, text=True,
                                encoding="utf-8", timeout=10, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "passed")
        self.assertEqual(result.stderr, "")
        after = {str(path.relative_to(self.root)): path.read_bytes()
                 for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(after, before)

    def test_cli_failures_are_nonzero_and_machine_readable(self):
        self.write("README.md", "[wrong](absent.md)\n")
        result = subprocess.run([sys.executable, "-B", str(TOOL), "--root", str(self.root), "--json"],
                                capture_output=True, text=True, encoding="utf-8", timeout=10, check=False)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "failed")
        self.assertIn("README.md:1", report["errors"][0]["message"])
        self.assertEqual(result.stderr, "")

    def test_invalid_expected_agent_argument_has_readable_usage_failure(self):
        result = subprocess.run([sys.executable, "-B", str(TOOL), "--expected-agents", "0"],
                                capture_output=True, text=True, encoding="utf-8", timeout=10, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("expected_agents", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


class RealRepositorySmokeTests(unittest.TestCase):
    def test_current_source_tree_and_supplied_pdf(self):
        # The only test that reads the supplied 21 MB PDF; no archive copy needed.
        result = CHECKER.check_repository(ROOT)
        self.assertEqual(result["status"], "passed", result["errors"])
        self.assertEqual(result["checks"]["source_identity"]["declared_pages"], 500)
        self.assertEqual(result["checks"]["chapter_index"]["chapters"], 80)
        self.assertGreater(result["checks"]["agent_notes"]["count"], 0)
        self.assertEqual(result["physical_fidelity"], "not_established")


if __name__ == "__main__":
    unittest.main()
