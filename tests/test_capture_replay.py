#!/usr/bin/env python3
"""Independent acceptance of complete capture report replay.

The cleared contract supplies envelope, byte-comparison and outcome rules.
Earlier independent archive writers create literal inputs; their TestCases are
not imported or recounted. Existing public job/study executions supply the saved
artifacts under test, never expected output from the replay implementation.
"""

from __future__ import annotations

import copy
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import capture_common
import capture_corpus
import capture_job
import capture_study
import test_capture_job as job_author
import test_capture_study as study_author
import verify_capture_report as subject


TOOL = ROOT / "tools" / "verify_capture_report.py"
JOB_SOURCES = ("capture_audio.py", "capture_common.py", "capture_corpus.py",
               "capture_job.py", "compare_capture.py", "validate_capture.py")
STUDY_SOURCES = tuple(sorted((*JOB_SOURCES, "capture_study.py")))
CLAIMS = {"boundary_equivalence", "synchronization", "authenticity",
          "specimen_identity", "calibration", "permissions", "independence",
          "preregistration", "final_holdout_history", "physical_fidelity"}
SUMMARY_KEYS = {"schema_version", "replay_contract", "kind", "status",
                "verification_scope", "exact_report_match", "input",
                "saved_report", "replayed_report", "saved_engineering_status",
                "replayed_engineering_status", "context", "verifier_source",
                "verifier_runtime"} | CLAIMS
CONTEXT_KEYS = {"same_runtime", "same_tool_sources", "saved_runtime",
                "replayed_runtime", "saved_tool_sources", "replayed_tool_sources"}
RAW_REFERENCE = "fd801740524b1e1c23a61b5400725b76428652827ba1261b83243eb5ce551402"
RAW_QUARTER = "bac1c395abe23908b8c106a28b6c151bc25b9473d470f4d942775b5dfdf523e2"
DECODED_REFERENCE = "786665f3cf05b2f9b33e7cadee75e7176e122d62ad82133c72737c76261dd440"
DECODED_QUARTER = "79d8014af588d583abcc570598d3e073413543ef518b339cbca37dbb5eb6bd0c"


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def observation(payload):
    return {"size_bytes": len(payload), "sha256": sha(payload)}


def runtime():
    return {"python_implementation": sys.implementation.name,
            "python_version": platform.python_version(),
            "sys_platform": sys.platform, "machine": platform.machine()}


def shape(value):
    """Independent count: values are nodes; root container depth is zero."""
    nodes, maximum = 0, 0
    pending = [(value, 0)]
    while pending:
        item, depth = pending.pop()
        nodes += 1
        if type(item) in (dict, list):
            maximum = max(maximum, depth)
            children = item.values() if type(item) is dict else item
            pending.extend((child, depth + 1) for child in children)
    return nodes, maximum


def change_bytes(path, payload):
    """Make an actual write and a guaranteed observable mtime change."""
    before = path.stat()
    path.write_bytes(payload)
    os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns + 2_000_000_000))
    if path.stat().st_mtime_ns == before.st_mtime_ns:
        raise AssertionError("mutation timestamp did not change")


class ReplayCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hammond-replay-test-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name).resolve(strict=True)
        self.fixture = job_author.JobArchive(self.work / "archive")
        self.fixture.write()
        self.report = capture_job.run_job(self.fixture.path)
        self.saved = self.work / "saved-report.json"
        self.saved.write_bytes(encoded(self.report))

    def job_at(self, name, status="pass"):
        fixture = job_author.JobArchive(self.work / name)
        fixture.policy["criteria"][0]["upper_bound"] = {
            "pass": 0.375, "inconclusive": 0.25, "failed": 0.0625}[status]
        fixture.write()
        return fixture

    def study_at(self, name="study", statuses=("pass", "inconclusive", "failed"),
                 purpose="validation"):
        fixture = study_author.StudyArchive(self.work / name, statuses, purpose=purpose)
        fixture.write()
        return fixture

    def save_report(self, value, name="saved-report.json"):
        path = self.work / name
        path.write_bytes(encoded(value))
        return path

    def verify(self, *, kind="job", fixture=None, saved=None):
        return subject.verify_report(kind, (fixture or self.fixture).path,
                                     saved or self.saved)

    def expect_rejected_before_runner(self, report, *, kind="job", fixture=None):
        path = self.save_report(report)
        module = capture_job if kind == "job" else capture_study
        method = "run_job" if kind == "job" else "run_study"
        with mock.patch.object(module, method, side_effect=AssertionError("runner entered")) as runner:
            with self.assertRaises(subject.ReplayError):
                self.verify(kind=kind, fixture=fixture, saved=path)
            runner.assert_not_called()

    def assert_summary(self, result, saved, fresh, path, *, kind="job"):
        saved_bytes, fresh_bytes = encoded(saved), encoded(fresh)
        match = saved_bytes == fresh_bytes
        self.assertEqual(set(result), SUMMARY_KEYS)
        expected = {"schema_version": 1, "replay_contract": "capture-report-replay-v1",
                    "kind": kind, "status": "match" if match else "mismatch",
                    "verification_scope": "complete_canonical_report_bytes",
                    "exact_report_match": match, "input": observation(path.read_bytes()),
                    "saved_report": observation(saved_bytes),
                    "replayed_report": observation(fresh_bytes),
                    "saved_engineering_status": saved["status"],
                    "replayed_engineering_status": fresh["status"],
                    "context": {"same_runtime": saved["runtime"] == fresh["runtime"],
                                "same_tool_sources": saved["tool_sources"] == fresh["tool_sources"],
                                "saved_runtime": saved["runtime"],
                                "replayed_runtime": fresh["runtime"],
                                "saved_tool_sources": saved["tool_sources"],
                                "replayed_tool_sources": fresh["tool_sources"]},
                    "verifier_source": {"module": "verify_capture_report.py",
                                        **observation(TOOL.read_bytes())},
                    "verifier_runtime": runtime(),
                    **dict.fromkeys(CLAIMS, "not_established")}
        self.assertEqual(result, expected)
        self.assertEqual(set(result["context"]), CONTEXT_KEYS)
        self.assertIs(type(result["exact_report_match"]), bool)
        self.assertIs(type(result["context"]["same_runtime"]), bool)
        self.assertIs(type(result["context"]["same_tool_sources"]), bool)
        self.assertNotIn(str(self.work), encoded(result).decode("utf-8"))

    def main(self, flags, *, encoding="utf-8", newline=None):
        buffer = io.BytesIO()
        stdout = io.TextIOWrapper(buffer, encoding=encoding, newline=newline)
        stderr = io.StringIO()
        with mock.patch.object(sys, "stdout", stdout), mock.patch.object(sys, "stderr", stderr):
            code = subject.main(flags)
            stdout.flush()
        payload = buffer.getvalue()
        stdout.detach()
        return code, payload, stderr.getvalue()

    def arguments(self, *, kind="job", fixture=None, saved=None):
        return ["--kind", kind, "--input", str((fixture or self.fixture).path),
                "--report", str(saved or self.saved)]

    def cli(self, flags, *, cwd=None, env=None):
        return subprocess.run([sys.executable, "-B", str(TOOL), *flags],
                              cwd=cwd or self.work, env=env, capture_output=True,
                              timeout=45, check=False)


class ReplayResults(ReplayCase):
    def test_all_three_job_outcomes_match_without_relabeling_engineering_result(self):
        for status in ("pass", "failed", "inconclusive"):
            fixture = self.job_at(status, status)
            report = capture_job.run_job(fixture.path)
            self.assertEqual(report["status"], status)
            self.assertEqual(report["evaluation"]["comparison"]["channels"][0]
                             ["metrics"]["rms_error_fs"]["value"], 0.25)
            self.assertEqual(report["reference"]["inspection"]["sha256"], RAW_REFERENCE)
            self.assertEqual(report["candidate"]["inspection"]["sha256"], RAW_QUARTER)
            self.assertEqual(report["reference"]["inspection"]["decoded_sha256"], DECODED_REFERENCE)
            self.assertEqual(report["candidate"]["inspection"]["decoded_sha256"], DECODED_QUARTER)
            saved = self.save_report(report, status + ".json")
            with self.subTest(status=status):
                result = self.verify(fixture=fixture, saved=saved)
                self.assert_summary(result, report, report, fixture.path)
                self.assertEqual(result["status"], "match")

    def test_mixed_study_matches_with_all_full_results_and_literal_counts(self):
        fixture = self.study_at()
        report = capture_study.run_study(fixture.path)
        self.assertEqual(report["status"], "failed")
        self.assertEqual([x["report"]["status"] for x in report["jobs"]],
                         ["pass", "inconclusive", "failed"])
        self.assertEqual(report["summary"], {"jobs": 3, "pass": 1, "failed": 1,
                         "inconclusive": 1, "roles": {"fit": 0, "validation": 3,
                                                     "final_test": 0, "unassigned": 0}})
        saved = self.save_report(report)
        self.assert_summary(self.verify(kind="study", fixture=fixture, saved=saved),
                            report, report, fixture.path, kind="study")

    def test_all_fit_study_match_retains_zero_final_coverage_and_unknown_claims(self):
        fixture = self.study_at(statuses=("pass", "pass"), purpose="fit")
        report = capture_study.run_study(fixture.path)
        self.assertEqual(report["summary"]["roles"]["final_test"], 0)
        saved = self.save_report(report)
        result = self.verify(kind="study", fixture=fixture, saved=saved)
        self.assert_summary(result, report, report, fixture.path, kind="study")
        self.assertEqual({result[k] for k in CLAIMS}, {"not_established"})

    def test_relocated_archive_and_saved_report_have_identical_summary(self):
        original = self.verify()
        moved = self.work / "déplacement-λ"
        shutil.copytree(self.fixture.root, moved)
        report_dir = self.work / "rapports-λ"
        report_dir.mkdir()
        saved = report_dir / "résultat.json"
        shutil.copyfile(self.saved, saved)
        self.assertEqual(subject.verify_report("job", moved / "job.json", saved), original)

    def test_repetition_fresh_ownership_and_all_original_bytes_preserved(self):
        before = {str(p): p.read_bytes() for p in self.work.rglob("*") if p.is_file()}
        result = self.verify()
        expected = copy.deepcopy(result)
        result["context"]["saved_tool_sources"][0]["sha256"] = "f" * 64
        result["input"]["sha256"] = "0" * 64
        self.assertEqual(self.verify(), expected)
        after = {str(p): p.read_bytes() for p in self.work.rglob("*") if p.is_file()}
        self.assertEqual(after, before)

    def test_every_retained_nested_area_participates_in_complete_byte_comparison(self):
        for area in ("policy", "reference", "candidate", "corpus_report", "evaluation"):
            altered = copy.deepcopy(self.report)
            altered[area]["independent_probe"] = "A changed retained value."
            with self.subTest(area=area):
                saved = self.save_report(altered)
                result = self.verify(saved=saved)
                self.assert_summary(result, altered, self.report, self.fixture.path)
                self.assertEqual(result["status"], "mismatch")
                self.assertTrue(result["context"]["same_runtime"])
                self.assertTrue(result["context"]["same_tool_sources"])

    def test_full_bytes_distinguish_equal_python_numbers_from_distinct_json_tokens(self):
        saved = copy.deepcopy(self.report)
        saved["corpus_report"]["independent_probe"] = 1.0
        fresh = copy.deepcopy(self.report)
        fresh["corpus_report"]["independent_probe"] = 1
        self.assertEqual(saved, fresh)
        self.assertNotEqual(encoded(saved), encoded(fresh))
        self.save_report(saved)
        original = capture_job.run_job
        called = []
        def return_integer_probe(path):
            result = original(path)
            called.append(path)
            result["corpus_report"]["independent_probe"] = 1
            return result
        with mock.patch.object(capture_job, "run_job", side_effect=return_integer_probe):
            result = self.verify()
        self.assertEqual(called, [self.fixture.path])
        self.assert_summary(result, saved, fresh, self.fixture.path)
        self.assertEqual(result["status"], "mismatch")

    def test_changed_metric_and_omitted_comparison_never_replay_as_success(self):
        cases = []
        altered = copy.deepcopy(self.report)
        altered["evaluation"]["comparison"]["channels"][0]["metrics"]["rms_error_fs"] = 0.5
        cases.append(altered)
        altered = copy.deepcopy(self.report)
        del altered["evaluation"]["comparison"]
        cases.append(altered)
        for altered in cases:
            with self.subTest(comparison_present="comparison" in altered["evaluation"]):
                self.save_report(altered)
                self.assert_summary(self.verify(), altered, self.report, self.fixture.path)

    def test_saved_source_difference_is_context_and_complete_mismatch(self):
        altered = copy.deepcopy(self.report)
        altered["tool_sources"][0]["sha256"] = "0" * 64
        self.save_report(altered)
        result = self.verify()
        self.assert_summary(result, altered, self.report, self.fixture.path)
        self.assertFalse(result["context"]["same_tool_sources"])
        self.assertTrue(result["context"]["same_runtime"])

    def test_saved_runtime_difference_and_empty_machine_are_admitted_context(self):
        for machine in ("", "ancienne-λ"):
            altered = copy.deepcopy(self.report)
            altered["runtime"]["machine"] = machine
            self.save_report(altered)
            with self.subTest(machine=machine):
                result = self.verify()
                self.assert_summary(result, altered, self.report, self.fixture.path)

    def test_consistently_changed_saved_status_remains_an_untrusted_declared_outcome(self):
        altered = copy.deepcopy(self.report)
        altered["status"] = "failed"
        altered["evaluation"]["numerical_verdict"] = "fail"
        self.save_report(altered)
        result = self.verify()
        self.assert_summary(result, altered, self.report, self.fixture.path)
        self.assertEqual(result["saved_engineering_status"], "failed")
        self.assertEqual(result["replayed_engineering_status"], "pass")

    def test_study_nested_metric_change_is_not_hidden_by_summary_or_status(self):
        fixture = self.study_at()
        fresh = capture_study.run_study(fixture.path)
        saved = copy.deepcopy(fresh)
        saved["jobs"][0]["report"]["evaluation"]["comparison"]["channels"][0]["metrics"]["bias_fs"] = 0.5
        path = self.save_report(saved)
        result = self.verify(kind="study", fixture=fixture, saved=path)
        self.assert_summary(result, saved, fresh, fixture.path, kind="study")

    def test_original_compact_policy_survives_replay_without_pretty_reparse(self):
        fixture = job_author.JobArchive(
            self.work / "compact-policy", rate=64, channels=3, frames=4,
            frequencies=tuple(range(32)),
            reference=[1, 2, 3, -1, -2, -3] * 2,
            candidate=[1.25, 2.25, 3.25, -.75, -1.75, -2.75] * 2)
        criteria = []
        for channel in range(3):
            for frequency in range(32):
                for metric in ("complex_abs_error_fs", "normalized_complex_error"):
                    item = job_author.criterion(
                        ident=f"c-{channel}-{frequency}-{len(criteria)}", metric=metric,
                        channel=channel, frequency=frequency, bound=1000000)
                    item["rationale"] = "Original byte fixture."
                    item["uncertainty"]["evidence"] = "Declared margin."
                    criteria.append(item)
        fixture.policy["criteria"] = criteria
        compact = (json.dumps(fixture.policy, sort_keys=True, ensure_ascii=False,
                              allow_nan=False, separators=(",", ":")) + "\n").encode("utf-8")
        self.assertLessEqual(len(compact), 65536)
        self.assertGreater(len(encoded(fixture.policy)), 65536)
        fixture.write(policy_bytes=compact)
        report = capture_job.run_job(fixture.path)
        self.assertEqual(report["evaluation"]["policy_sha256"], sha(compact))
        saved = self.save_report(report)
        result = self.verify(fixture=fixture, saved=saved)
        self.assert_summary(result, report, report, fixture.path)
        self.assertEqual(fixture.policy_path.read_bytes(), compact)


class ReplayAdmission(ReplayCase):
    def test_exact_kind_and_api_path_types_reject(self):
        class Text(str):
            pass
        path_text = str(self.fixture.path)
        class OtherPath:
            def __fspath__(self):
                return path_text
        for kind in (None, True, 1, "", "JOB", "job\n", Text("job")):
            with self.subTest(kind=repr(kind)), self.assertRaises(subject.ReplayError):
                subject.verify_report(kind, self.fixture.path, self.saved)
        for value in (None, True, 1, b"job.json", "", Text(str(self.fixture.path)), OtherPath()):
            for position in ("input", "report"):
                with self.subTest(value=type(value).__name__, position=position), \
                     self.assertRaises(subject.ReplayError):
                    subject.verify_report("job", value if position == "input" else self.fixture.path,
                                          value if position == "report" else self.saved)

    def test_saved_strict_bytes_reject_before_public_runner(self):
        good = encoded(self.report)
        cases = (b"", b"\xef\xbb\xbf" + good, b"\xff", good + b"{}", b"[]", b"null",
                 good.replace(b'"schema_version": 1', b'"schema_version": 1, "schema_version": 1', 1),
                 good.replace(b'"schema_version": 1', b'"schema_version": NaN', 1),
                 good.replace(b'"schema_version": 1', b'"schema_version": Infinity', 1),
                 b'{"probe":0.' + b"0" * 64 + b'1}', b'{"probe":"\\ud800"}',
                 b'{"probe":"raw\x00control"}')
        for payload in cases:
            self.saved.write_bytes(payload)
            with self.subTest(prefix=payload[:40]), \
                 mock.patch.object(capture_job, "run_job", side_effect=AssertionError("runner entered")) as runner:
                with self.assertRaises(subject.ReplayError):
                    self.verify()
                runner.assert_not_called()

    def test_noncanonical_equivalent_json_rejects_before_execution(self):
        good = encoded(self.report)
        variants = (json.dumps(self.report, separators=(",", ":")).encode(),
                    (json.dumps(self.report, indent=2, sort_keys=False) + "\n").encode(),
                    good.replace(b"\n", b"\r\n"), good[:-1], b" " + good, good + b"\n")
        for payload in variants:
            self.assertEqual(json.loads(payload), self.report)
            self.assertNotEqual(payload, good)
            self.saved.write_bytes(payload)
            with self.subTest(length=len(payload)), \
                 mock.patch.object(capture_job, "run_job", side_effect=AssertionError("runner entered")) as runner:
                with self.assertRaises(subject.ReplayError):
                    self.verify()
                runner.assert_not_called()

    def test_all_job_root_keys_required_and_unknown_root_rejected(self):
        for key in self.report:
            altered = copy.deepcopy(self.report)
            del altered[key]
            with self.subTest(missing=key):
                self.expect_rejected_before_runner(altered)
        altered = copy.deepcopy(self.report)
        altered["unknown"] = True
        self.expect_rejected_before_runner(altered)

    def test_job_root_literals_types_and_ids_are_strict(self):
        mutations = (("schema_version", True), ("schema_version", 1.0),
                     ("schema_version", 2), ("job_contract", "capture-job-v2"),
                     ("job_id", "other-id"), ("job_id", "bad\n"),
                     ("status", "fail"), ("status", True), ("self_comparison", 0),
                     ("self_comparison", True))
        for key, value in mutations:
            altered = copy.deepcopy(self.report)
            altered[key] = value
            with self.subTest(key=key, value=value):
                self.expect_rejected_before_runner(altered)

    def test_every_physical_claim_must_remain_exactly_unestablished(self):
        for key in CLAIMS:
            for value in ("pass", "verified", None, True):
                altered = copy.deepcopy(self.report)
                altered[key] = value
                with self.subTest(key=key, value=value):
                    self.expect_rejected_before_runner(altered)

    def test_embedded_job_and_required_objects_are_admitted(self):
        for key in ("job", "policy", "reference", "candidate", "corpus_report", "evaluation"):
            for value in (None, [], "object"):
                altered = copy.deepcopy(self.report)
                altered[key] = value
                with self.subTest(key=key, value=value):
                    self.expect_rejected_before_runner(altered)
        for key, value in (("pairing", "aligned"), ("transform", "gain"),
                           ("schema_version", True), ("job_id", "changed-id")):
            altered = copy.deepcopy(self.report)
            altered["job"][key] = value
            with self.subTest(job_key=key):
                self.expect_rejected_before_runner(altered)

    def test_input_observation_exact_fields_hashes_sizes_and_integer_types(self):
        for value in (None, [], {"sha256": "0" * 64},
                      {"sha256": "0" * 64, "size_bytes": 1, "extra": 0}):
            altered = copy.deepcopy(self.report)
            altered["inputs"]["job"] = value
            self.expect_rejected_before_runner(altered)
        for key, values in (("sha256", ["0" * 63, "A" * 64, "0" * 64 + "\n", None]),
                            ("size_bytes", [0, -1, True, 1.0, 65537])):
            for value in values:
                altered = copy.deepcopy(self.report)
                altered["inputs"]["job"][key] = value
                with self.subTest(key=key, value=value):
                    self.expect_rejected_before_runner(altered)
        for key in ("job", "policy", "corpus"):
            altered = copy.deepcopy(self.report)
            del altered["inputs"][key]
            self.expect_rejected_before_runner(altered)
        altered = copy.deepcopy(self.report)
        altered["inputs"]["extra"] = {}
        self.expect_rejected_before_runner(altered)

    def test_bound_corpus_and_policy_envelopes_are_consistent(self):
        for area, maximum in (("corpus", 1048576), ("policy", 65536)):
            for key, value in (("path", "other.json"), ("expected_sha256", "0" * 64),
                               ("observed_sha256", "f" * 64), ("size_bytes", 0),
                               ("size_bytes", maximum + 1), ("size_bytes", True)):
                altered = copy.deepcopy(self.report)
                altered["inputs"][area][key] = value
                with self.subTest(area=area, key=key, value=value):
                    self.expect_rejected_before_runner(altered)
            for field in ("path", "size_bytes", "expected_sha256", "observed_sha256"):
                altered = copy.deepcopy(self.report)
                del altered["inputs"][area][field]
                self.expect_rejected_before_runner(altered)

    def test_corpus_evaluation_context_and_status_precedence_are_checked(self):
        cases = (("corpus_report", "mode", "structure_only"),
                 ("corpus_report", "index_sha256", "0" * 64),
                 ("corpus_report", "status", "fail"),
                 ("evaluation", "policy_sha256", "0" * 64),
                 ("evaluation", "evaluation_role", "held_out"),
                 ("evaluation", "numerical_verdict", "failed"))
        for area, key, value in cases:
            altered = copy.deepcopy(self.report)
            altered[area][key] = value
            with self.subTest(area=area, key=key):
                self.expect_rejected_before_runner(altered)
        for corpus in ("pass", "failed", "inconclusive"):
            for numeric in ("pass", "fail", "inconclusive"):
                expected = ("failed" if corpus == "failed" or numeric == "fail" else
                            "inconclusive" if "inconclusive" in (corpus, numeric) else "pass")
                altered = copy.deepcopy(self.report)
                altered["corpus_report"]["status"] = corpus
                altered["evaluation"]["numerical_verdict"] = numeric
                altered["status"] = "pass" if expected != "pass" else "failed"
                with self.subTest(corpus=corpus, numeric=numeric):
                    self.expect_rejected_before_runner(altered)

    def test_runtime_envelope_rejects_missing_extra_type_length_and_controls(self):
        for key in self.report["runtime"]:
            altered = copy.deepcopy(self.report)
            del altered["runtime"][key]
            self.expect_rejected_before_runner(altered)
            for value in (None, 1, True, "x" * 129, "control\n", "control\x7f", "control\x85"):
                altered = copy.deepcopy(self.report)
                altered["runtime"][key] = value
                self.expect_rejected_before_runner(altered)
            if key != "machine":
                altered = copy.deepcopy(self.report)
                altered["runtime"][key] = ""
                self.expect_rejected_before_runner(altered)
        altered = copy.deepcopy(self.report)
        altered["runtime"]["hostname"] = "invented"
        self.expect_rejected_before_runner(altered)

    def test_source_inventory_requires_exact_order_names_shape_and_limits(self):
        cases = []
        altered = copy.deepcopy(self.report)
        altered["tool_sources"].reverse()
        cases.append(altered)
        for replacement in ([], self.report["tool_sources"][:-1], self.report["tool_sources"] * 2):
            altered = copy.deepcopy(self.report)
            altered["tool_sources"] = replacement
            cases.append(altered)
        for key, value in (("module", "unknown.py"), ("module", "capture_audio.py\n"),
                           ("sha256", "A" * 64), ("sha256", "0" * 63),
                           ("size_bytes", 0), ("size_bytes", 1048577),
                           ("size_bytes", True), ("size_bytes", 1.0)):
            altered = copy.deepcopy(self.report)
            altered["tool_sources"][0][key] = value
            cases.append(altered)
        for key in ("module", "sha256", "size_bytes"):
            altered = copy.deepcopy(self.report)
            del altered["tool_sources"][0][key]
            cases.append(altered)
        altered = copy.deepcopy(self.report)
        altered["tool_sources"][0]["path"] = "/invented/path"
        cases.append(altered)
        for index, altered in enumerate(cases):
            with self.subTest(case=index):
                self.expect_rejected_before_runner(altered)

    def test_generic_nested_control_strings_and_keys_are_rejected(self):
        for bad in ("\x00", "\x1f", "\x7f", "\x85", "\x9f"):
            for key_case in (False, True):
                altered = copy.deepcopy(self.report)
                altered["policy"][bad if key_case else "probe"] = "okay" if key_case else bad
                with self.subTest(bad=repr(bad), key=key_case):
                    self.expect_rejected_before_runner(altered)

    def test_study_envelope_and_nested_binding_counts_work_and_status_are_exact(self):
        fixture = self.study_at()
        report = capture_study.run_study(fixture.path)
        cases = []
        for key in report:
            altered = copy.deepcopy(report)
            del altered[key]
            cases.append(("missing " + key, altered))
        paths_values = ((('schema_version',), True), (('study_id',), 'other-study'),
                        (('study_contract',), 'capture-study-v2'),
                        (('input', 'size_bytes'), True), (('input', 'sha256'), '0' * 64),
                        (('corpus', 'observed_sha256'), '0' * 64),
                        (('work', 'window_samples'), 13), (('work', 'spectral_terms'), True),
                        (('summary', 'jobs'), 2), (('summary', 'pass'), 0),
                        (('summary', 'failed'), True), (('summary', 'roles', 'validation'), 2),
                        (('status',), 'pass'), (('jobs', 0, 'job_id'), 'other-job'),
                        (('jobs', 0, 'path'), 'other.json'),
                        (('jobs', 0, 'expected_sha256'), '0' * 64),
                        (('jobs', 0, 'observed_sha256'), '0' * 64),
                        (('jobs', 0, 'size_bytes'), 1),
                        (('jobs', 0, 'report', 'physical_fidelity'), 'pass'),
                        (('jobs', 0, 'report', 'runtime', 'machine'), 'different'),
                        (('jobs', 0, 'report', 'tool_sources', 0, 'sha256'), '0' * 64))
        for path, value in paths_values:
            altered = copy.deepcopy(report)
            cursor = altered
            for part in path[:-1]:
                cursor = cursor[part]
            cursor[path[-1]] = value
            cases.append((str(path), altered))
        altered = copy.deepcopy(report)
        altered["jobs"].reverse()
        cases.append(("reordered jobs", altered))
        altered = copy.deepcopy(report)
        altered["summary"]["roles"]["held_out"] = 0
        cases.append(("extra role", altered))
        for label, altered in cases:
            with self.subTest(case=label):
                self.expect_rejected_before_runner(altered, kind="study", fixture=fixture)

    def test_changed_original_input_bytes_reject_before_artifact_work(self):
        original = self.fixture.path.read_bytes()
        self.fixture.path.write_bytes(original + b" ")
        with mock.patch.object(capture_job, "run_job", side_effect=AssertionError("runner entered")) as runner:
            with self.assertRaises(subject.ReplayError):
                self.verify()
            runner.assert_not_called()

    def test_changed_original_study_identity_rejects_before_public_runner(self):
        fixture = self.study_at()
        report = capture_study.run_study(fixture.path)
        saved = self.save_report(report)
        fixture.path.write_bytes(fixture.path.read_bytes() + b" ")
        with mock.patch.object(capture_study, "run_study", side_effect=AssertionError("runner entered")) as runner:
            with self.assertRaises(subject.ReplayError):
                self.verify(kind="study", fixture=fixture, saved=saved)
            runner.assert_not_called()

    def test_current_archive_rejection_is_not_a_fabricated_mismatch(self):
        audio = self.fixture.archive.file_path("candidate", "raw")
        change_bytes(audio, b"changed artifact")
        with self.assertRaises(subject.ReplayError):
            self.verify()


class ReplayLimits(ReplayCase):
    def test_actual_sixteen_mib_saved_report_boundary_precedes_execution(self):
        class Reached(BaseException):
            pass
        altered = copy.deepcopy(self.report)
        altered["policy"]["independent_padding"] = ""
        altered["policy"]["independent_padding"] = "x" * (16777216 - len(encoded(altered)))
        payload = encoded(altered)
        self.assertEqual(len(payload), 16777216)
        self.saved.write_bytes(payload)
        with mock.patch.object(capture_job, "run_job", side_effect=Reached) as runner:
            with self.assertRaises(Reached):
                self.verify()
            runner.assert_called_once_with(self.fixture.path)
        self.saved.write_bytes(payload + b" ")
        with mock.patch.object(capture_job, "run_job", side_effect=AssertionError("runner entered")) as runner:
            with self.assertRaises(subject.ReplayError):
                self.verify()
            runner.assert_not_called()

    def test_saved_report_node_and_depth_limits_at_independently_counted_boundary(self):
        nodes, depth = shape(self.report)
        with mock.patch.object(subject, "MAX_REPORT_NODES", nodes):
            self.assertEqual(self.verify()["status"], "match")
        with mock.patch.object(subject, "MAX_REPORT_NODES", nodes - 1), \
             mock.patch.object(capture_job, "run_job", side_effect=AssertionError("runner entered")) as runner:
            with self.assertRaises(subject.ReplayError):
                self.verify()
            runner.assert_not_called()
        with mock.patch.dict(subject.REPORT_DEPTHS, {"job": depth}):
            self.assertEqual(self.verify()["status"], "match")
        with mock.patch.dict(subject.REPORT_DEPTHS, {"job": depth - 1}), \
             mock.patch.object(capture_job, "run_job", side_effect=AssertionError("runner entered")) as runner:
            with self.assertRaises(subject.ReplayError):
                self.verify()
            runner.assert_not_called()

    def test_nested_job_retains_its_own_depth_bound_inside_larger_study_envelope(self):
        fixture = self.study_at(statuses=("pass",))
        report = capture_study.run_study(fixture.path)
        nested = report["jobs"][0]["report"]
        chain = []
        nested["policy"]["independent_depth_probe"] = chain
        while shape(nested)[1] < 33:
            child = []
            chain.append(child)
            chain = child
        self.assertEqual(shape(nested)[1], 33)
        self.assertLessEqual(shape(report)[1], 40)
        self.expect_rejected_before_runner(report, kind="study", fixture=fixture)

    def test_numeric_magnitude_exact_integer_boundary_is_not_float_rounded(self):
        for value, admitted in ((4_000_000_000_000_000_000, True),
                                (-4_000_000_000_000_000_000, True),
                                (4_000_000_000_000_000_001, False),
                                (-4_000_000_000_000_000_001, False)):
            altered = copy.deepcopy(self.report)
            altered["policy"]["independent_number"] = value
            with self.subTest(value=value):
                if admitted:
                    self.save_report(altered)
                    self.assert_summary(self.verify(), altered, self.report, self.fixture.path)
                else:
                    self.expect_rejected_before_runner(altered)

    def test_actual_input_64k_boundary_and_one_byte_excess(self):
        original = self.fixture.path.read_bytes()
        padded = original + b" " * (65536 - len(original))
        self.fixture.path.write_bytes(padded)
        report = capture_job.run_job(self.fixture.path)
        self.assertEqual(report["inputs"]["job"]["size_bytes"], 65536)
        self.save_report(report)
        self.assert_summary(self.verify(), report, report, self.fixture.path)
        self.fixture.path.write_bytes(padded + b" ")
        with mock.patch.object(capture_job, "run_job", side_effect=AssertionError("runner entered")) as runner:
            with self.assertRaises(subject.ReplayError):
                self.verify()
            runner.assert_not_called()

    def test_actual_associated_source_one_mib_boundary_and_excess(self):
        directory = self.work / "observed-source"
        directory.mkdir()
        source = directory / "capture_job.py"
        original = (ROOT / "tools" / "capture_job.py").read_bytes()
        source.write_bytes(original + b"\n#" + b"x" * (1048576 - len(original) - 3) + b"\n")
        self.assertEqual(source.stat().st_size, 1048576)
        with mock.patch.object(capture_job, "__file__", str(source)):
            fresh = capture_job.run_job(self.fixture.path)
            result = self.verify()
            self.assert_summary(result, self.report, fresh, self.fixture.path)
            self.assertEqual(result["status"], "mismatch")
            self.assertFalse(result["context"]["same_tool_sources"])
            source.write_bytes(source.read_bytes() + b"x")
            with mock.patch.object(capture_job, "run_job", side_effect=AssertionError("runner entered")) as runner:
                with self.assertRaises(subject.ReplayError):
                    self.verify()
                runner.assert_not_called()

    def test_summary_bytes_nodes_and_depth_use_independent_reduced_boundaries(self):
        baseline = self.verify()
        nodes, depth = shape(baseline)
        limits = (("MAX_SUMMARY_BYTES", len(encoded(baseline))),
                  ("MAX_SUMMARY_NODES", nodes), ("MAX_SUMMARY_DEPTH", depth))
        for constant, exact in limits:
            with self.subTest(constant=constant):
                with mock.patch.object(subject, constant, exact):
                    self.assertEqual(self.verify(), baseline)
                with mock.patch.object(subject, constant, exact - 1):
                    with self.assertRaises(subject.ReplayError):
                        self.verify()

    def test_replay_snapshot_capacity_bounds_actual_nine_and_ten_observations(self):
        with mock.patch.object(subject, "MAX_REPLAY_SNAPSHOTS", 9):
            self.assertEqual(self.verify()["status"], "match")
        with mock.patch.object(subject, "MAX_REPLAY_SNAPSHOTS", 8):
            with self.assertRaises(subject.ReplayError):
                self.verify()
        fixture = self.study_at(statuses=("pass",))
        report = capture_study.run_study(fixture.path)
        saved = self.save_report(report)
        with mock.patch.object(subject, "MAX_REPLAY_SNAPSHOTS", 10):
            self.assertEqual(self.verify(kind="study", fixture=fixture, saved=saved)["status"], "match")
        with mock.patch.object(subject, "MAX_REPLAY_SNAPSHOTS", 9):
            with self.assertRaises(subject.ReplayError):
                self.verify(kind="study", fixture=fixture, saved=saved)


class ReplayIdentity(ReplayCase):
    def test_original_saved_report_is_read_once_input_twice_and_public_runner_once(self):
        original_read = capture_corpus._read_confined_bytes
        original_run = capture_job.run_job
        reads = []
        def observe(root, parts, **kwargs):
            reads.append(Path(root).joinpath(*parts))
            return original_read(root, parts, **kwargs)
        with mock.patch.object(capture_corpus, "_read_confined_bytes", side_effect=observe), \
             mock.patch.object(capture_job, "run_job", wraps=original_run) as runner:
            result = self.verify()
        self.assertEqual(result["status"], "match")
        self.assertEqual(reads.count(self.saved), 1)
        self.assertEqual(reads.count(self.fixture.path), 2)
        runner.assert_called_once_with(self.fixture.path)

    def test_saved_report_and_original_input_survive_through_final_return(self):
        for target_name in ("saved", "input"):
            fixture = self.job_at("late-" + target_name)
            report = capture_job.run_job(fixture.path)
            saved = self.save_report(report, "late-" + target_name + ".json")
            target = saved if target_name == "saved" else fixture.path
            original_run = capture_job.run_job
            reached = []
            def mutate_after_run(path):
                result = original_run(path)
                reached.append(target)
                change_bytes(target, target.read_bytes() + b" ")
                return result
            with self.subTest(target=target_name), \
                 mock.patch.object(capture_job, "run_job", side_effect=mutate_after_run):
                with self.assertRaises(subject.ReplayError):
                    self.verify(fixture=fixture, saved=saved)
            self.assertEqual(reached, [target])

    def test_same_bytes_leaf_replacement_after_run_is_observed(self):
        original_run = capture_job.run_job
        reached = []
        def replace_after_run(path):
            result = original_run(path)
            replacement = self.work / "replacement.json"
            replacement.write_bytes(self.saved.read_bytes())
            os.replace(replacement, self.saved)
            reached.append(True)
            return result
        with mock.patch.object(capture_job, "run_job", side_effect=replace_after_run):
            with self.assertRaises(subject.ReplayError):
                self.verify()
        self.assertEqual(reached, [True])

    def test_unrelated_sibling_creation_does_not_invalidate_directory_timestamp(self):
        original_run = capture_job.run_job
        reached = []
        def sibling_after_run(path):
            result = original_run(path)
            (self.work / "unrelated-sibling.txt").write_text("Preserve harmless sibling.\n")
            reached.append(True)
            return result
        with mock.patch.object(capture_job, "run_job", side_effect=sibling_after_run):
            self.assertEqual(self.verify()["status"], "match")
        self.assertEqual(reached, [True])

    def test_public_runner_race_checks_consumed_input_after_bounded_actual_work(self):
        original_run = capture_job.run_job
        reached = []
        def change_before_public_read(path):
            change_bytes(path, path.read_bytes() + b" ")
            report = original_run(path)
            reached.append(report["inputs"]["job"]["sha256"])
            return report
        with mock.patch.object(capture_job, "run_job", side_effect=change_before_public_read):
            with self.assertRaises(subject.ReplayError):
                self.verify()
        self.assertEqual(len(reached), 1)
        self.assertNotEqual(reached[0], self.report["inputs"]["job"]["sha256"])

    def test_fresh_input_sources_runtime_and_envelope_cannot_disagree_with_preflight(self):
        mutations = (
            lambda r: r["inputs"]["job"].update(sha256="0" * 64),
            lambda r: r["job"].update(job_id="other-job"),
            lambda r: r["tool_sources"][0].update(sha256="0" * 64),
            lambda r: r["runtime"].update(machine="changed-machine"),
            lambda r: r.update(physical_fidelity="verified"),
        )
        original_run = capture_job.run_job
        for index, mutate in enumerate(mutations):
            reached = []
            def alter_return(path):
                result = original_run(path)
                mutate(result)
                reached.append(True)
                return result
            with self.subTest(case=index), \
                 mock.patch.object(capture_job, "run_job", side_effect=alter_return):
                with self.assertRaises(subject.ReplayError):
                    self.verify()
            self.assertEqual(reached, [True])

    def test_runtime_is_rechecked_after_public_runner_returns(self):
        actual_machine = platform.machine()
        flag = [False]
        original_run = capture_job.run_job
        def machine():
            return "changed-after-return" if flag[0] else actual_machine
        def flip_after_run(path):
            result = original_run(path)
            flag[0] = True
            return result
        with mock.patch.object(platform, "machine", side_effect=machine), \
             mock.patch.object(capture_job, "run_job", side_effect=flip_after_run):
            with self.assertRaises(subject.ReplayError):
                self.verify()
        self.assertTrue(flag[0])

    def source_change(self, filename, *, kind="job", phase="after"):
        directory = self.work / ("sources-" + kind + "-" + phase + "-" + filename)
        directory.mkdir()
        for name in (*STUDY_SOURCES, "verify_capture_report.py"):
            shutil.copyfile(ROOT / "tools" / name, directory / name)
        if kind == "study":
            fixture = self.study_at("source-study-" + phase)
            report = capture_study.run_study(fixture.path)
            saved = self.save_report(report, "source-study-saved.json")
        else:
            fixture, saved = self.fixture, self.saved
        script = r'''
import json, os, pathlib, sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import capture_job, capture_study, verify_capture_report as replay
kind, input_name, saved_name, filename, phase = sys.argv[2:]
module = capture_job if kind == "job" else capture_study
name = "run_job" if kind == "job" else "run_study"
original = getattr(module, name)
target = pathlib.Path(sys.argv[1]) / filename
reached = []
def mutate():
    before = target.stat()
    target.write_bytes(target.read_bytes() + b"\n# independent replay mutation\n")
    os.utime(target, ns=(before.st_atime_ns, before.st_mtime_ns + 2000000000))
    assert target.stat().st_mtime_ns != before.st_mtime_ns
    reached.append(filename)
def wrapped(path):
    if phase == "before":
        mutate()
    result = original(path)
    if phase == "after":
        mutate()
    return result
setattr(module, name, wrapped)
try:
    replay.verify_report(kind, pathlib.Path(input_name), pathlib.Path(saved_name))
except replay.ReplayError as error:
    assert reached == [filename], reached
    print(json.dumps({"rejected": True, "reached": reached, "error": str(error)}))
else:
    raise AssertionError("changed source was accepted")
'''
        result = subprocess.run([sys.executable, "-B", "-c", script, str(directory), kind,
                                 str(fixture.path), str(saved), filename, phase],
                                cwd=self.work, capture_output=True, timeout=45, check=False)
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
        value = json.loads(result.stdout)
        self.assertTrue(value["rejected"])
        self.assertEqual(value["reached"], [filename])

    def test_every_job_source_and_verifier_source_is_retained_after_runner_return(self):
        for filename in (*JOB_SOURCES, "verify_capture_report.py"):
            with self.subTest(filename=filename):
                self.source_change(filename)

    def test_study_additional_source_is_retained_after_runner_return(self):
        self.source_change("capture_study.py", kind="study")

    def test_source_changed_between_inventory_and_runner_is_rejected(self):
        self.source_change("capture_common.py", phase="before")

    def test_missing_and_invalid_associated_source_reject_before_public_runner(self):
        for value in (None, str(self.work / "capture_job.py"), str(self.work / "wrong.py")):
            with self.subTest(value=value), mock.patch.object(capture_job, "__file__", value), \
                 mock.patch.object(capture_job, "run_job", side_effect=AssertionError("runner entered")) as runner:
                with self.assertRaises(subject.ReplayError):
                    self.verify()
                runner.assert_not_called()

    def test_directory_and_missing_input_or_report_reject(self):
        for target in (self.work, self.work / "absent.json"):
            for which in ("input", "report"):
                with self.subTest(target=target.name, which=which), self.assertRaises(subject.ReplayError):
                    subject.verify_report("job", target if which == "input" else self.fixture.path,
                                          target if which == "report" else self.saved)

    def test_native_selected_report_leaf_and_parent_links_reject(self):
        leaf = self.work / "linked.json"
        parent = self.work / "linked-parent"
        try:
            leaf.symlink_to(self.saved)
            parent.symlink_to(self.work, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"native symlink creation unavailable: {error}")
        for saved in (leaf, parent / self.saved.name):
            with self.subTest(saved=saved.name), self.assertRaises(subject.ReplayError):
                self.verify(saved=saved)

    def test_ordinary_ancestor_alias_above_selected_root_is_admitted(self):
        real = self.work / "real"
        reports = real / "reports"
        reports.mkdir(parents=True)
        saved = reports / "saved.json"
        saved.write_bytes(encoded(self.report))
        alias = self.work / "ancestor-alias"
        try:
            alias.symlink_to(real, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"native ancestor symlink creation unavailable: {error}")
        self.assertEqual(self.verify(saved=alias / "reports" / "saved.json"), self.verify())

    def test_native_fifo_report_rejects_without_waiting(self):
        fifo = self.work / "report.fifo"
        try:
            os.mkfifo(fifo)
        except (AttributeError, OSError, NotImplementedError) as error:
            self.skipTest(f"native FIFO creation unavailable: {error}")
        with self.assertRaises(subject.ReplayError):
            self.verify(saved=fifo)


class ReplayCommandLine(ReplayCase):
    def test_actual_cli_matches_pass_failed_inconclusive_and_mixed_study(self):
        for status in ("pass", "failed", "inconclusive"):
            fixture = self.job_at("cli-" + status, status)
            report = capture_job.run_job(fixture.path)
            saved = self.save_report(report, "cli-" + status + ".json")
            result = self.cli(self.arguments(fixture=fixture, saved=saved))
            with self.subTest(status=status):
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, b"")
                self.assert_summary(json.loads(result.stdout), report, report, fixture.path)
                self.assertEqual(result.stdout, encoded(json.loads(result.stdout)))
        fixture = self.study_at("cli-study")
        report = capture_study.run_study(fixture.path)
        saved = self.save_report(report, "cli-study.json")
        result = self.cli(self.arguments(kind="study", fixture=fixture, saved=saved))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")
        self.assert_summary(json.loads(result.stdout), report, report, fixture.path, kind="study")

    def test_actual_cli_mismatch_emits_complete_summary_with_empty_stderr(self):
        altered = copy.deepcopy(self.report)
        altered["candidate"]["independent_probe"] = "changed field"
        self.save_report(altered)
        result = self.cli(self.arguments())
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stderr, b"")
        self.assert_summary(json.loads(result.stdout), altered, self.report, self.fixture.path)

    def test_foreign_cwd_unicode_paths_ascii_environment_and_publication(self):
        foreign = self.work / "cwd-λ"
        foreign.mkdir()
        saved = foreign / "résultat-λ.json"
        altered = copy.deepcopy(self.report)
        altered["runtime"]["machine"] = "machine-λ"
        saved.write_bytes(encoded(altered))
        output = foreign / "reproduction-é.json"
        args = self.arguments(saved=saved) + ["--output", output.name]
        environment = dict(os.environ, PYTHONIOENCODING="ascii", PYTHONUTF8="0")
        result = self.cli(args, cwd=foreign, env=environment)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stderr, b"")
        self.assertEqual(result.stdout, output.read_bytes())
        self.assertIn("machine-λ".encode("utf-8"), result.stdout)
        self.assert_summary(json.loads(result.stdout), altered, self.report, self.fixture.path)

    def test_binary_utf8_lf_bypasses_ascii_crlf_text_translation(self):
        altered = copy.deepcopy(self.report)
        altered["runtime"]["machine"] = "machine-λ"
        self.save_report(altered)
        code, stdout, stderr = self.main(self.arguments(), encoding="ascii", newline="\r\n")
        self.assertEqual(code, 1)
        self.assertEqual(stderr, "")
        self.assertIn("machine-λ".encode("utf-8"), stdout)
        self.assertNotIn(b"\r", stdout)
        self.assertEqual(stdout, encoded(json.loads(stdout)))

    def test_text_only_stdout_and_main_none_preserve_values_and_integer_return(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, "stdout", stdout), mock.patch.object(sys, "stderr", stderr), \
             mock.patch.object(sys, "argv", ["verify_capture_report.py", *self.arguments()]):
            code = subject.main(None)
        self.assertIs(type(code), int)
        self.assertEqual(code, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assert_summary(json.loads(stdout.getvalue()), self.report, self.report, self.fixture.path)

    def test_strict_usage_duplicate_empty_abbreviated_unknown_and_overrides(self):
        good = self.arguments()
        cases = [[], ["--kind", "job"],
                 ["--ki", "job", *good[2:]], ["--kind", "JOB", *good[2:]],
                 good + ["--gain", "1"], good + ["--role", "fit"],
                 good + ["--window", "rectangular"], good + ["--unknown"]]
        for option in ("--kind", "--input", "--report", "--output"):
            value = "job" if option == "--kind" else "path.json"
            if option == "--output":
                cases.append(good + [option, value, option + "=" + value])
            else:
                cases.append(good + [option, value])
            cases.append(good + [option, ""])
        for flags in cases:
            with self.subTest(flags=flags):
                code, stdout, stderr = self.main(flags)
                self.assertEqual(code, 2, stderr)
                self.assertEqual(stdout, b"")
                self.assertTrue(stderr)
        code, stdout, stderr = self.main(["--help"])
        self.assertEqual(code, 0)
        self.assertIn(b"--report", stdout)
        self.assertEqual(stderr, "")

    def test_argv_exact_list_and_string_types(self):
        class ListSubclass(list):
            pass
        class Text(str):
            pass
        for flags in ("--help", ("--help",), ListSubclass(["--help"]), [Text("--help")],
                      [Path("--help")], [None], 1):
            with self.subTest(kind=type(flags).__name__):
                code, stdout, stderr = self.main(flags)
                self.assertEqual(code, 2)
                self.assertEqual(stdout, b"")
                self.assertTrue(stderr)

    def test_existing_file_directory_input_and_report_destinations_preserved(self):
        existing = self.work / "existing.json"
        existing.write_bytes(b"Existing unrelated content.\n")
        directory = self.work / "existing-directory"
        directory.mkdir()
        original_input, original_report = self.fixture.path.read_bytes(), self.saved.read_bytes()
        for target in (existing, directory, self.fixture.path, self.saved):
            with self.subTest(target=target.name):
                code, stdout, stderr = self.main(self.arguments() + ["--output", str(target)])
                self.assertEqual(code, 1)
                self.assertEqual(stdout, b"")
                self.assertTrue(stderr.startswith("replay error:"), stderr)
                self.assertEqual(existing.read_bytes(), b"Existing unrelated content.\n")
                self.assertEqual(self.fixture.path.read_bytes(), original_input)
                self.assertEqual(self.saved.read_bytes(), original_report)
                self.assertTrue(directory.is_dir())
        self.assertEqual(list(self.work.glob(".capture-json-*")), [])

    def test_native_hardlinked_output_alias_is_preserved(self):
        target = self.work / "hardlink.json"
        try:
            os.link(self.saved, target)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"native hardlink creation unavailable: {error}")
        original = self.saved.read_bytes()
        code, stdout, stderr = self.main(self.arguments() + ["--output", str(target)])
        self.assertEqual(code, 1)
        self.assertEqual(stdout, b"")
        self.assertTrue(stderr.startswith("replay error:"))
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(self.saved.read_bytes(), original)

    def test_native_dangling_output_link_is_preserved(self):
        target = self.work / "dangling.json"
        absent = self.work / "absent.json"
        try:
            target.symlink_to(absent)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"native symlink creation unavailable: {error}")
        code, stdout, stderr = self.main(self.arguments() + ["--output", str(target)])
        self.assertEqual(code, 1)
        self.assertEqual(stdout, b"")
        self.assertTrue(stderr.startswith("replay error:"))
        self.assertTrue(target.is_symlink())
        self.assertFalse(absent.exists())

    def test_missing_output_parent_is_not_created(self):
        target = self.work / "absent-parent" / "result.json"
        code, stdout, stderr = self.main(self.arguments() + ["--output", str(target)])
        self.assertEqual(code, 1)
        self.assertEqual(stdout, b"")
        self.assertTrue(stderr.startswith("replay error:"))
        self.assertFalse(target.parent.exists())

    def test_concurrent_destination_creation_wins_unchanged(self):
        target = self.work / "raced.json"
        original_link = os.link
        reached = []
        def race(source, destination, *args, **kwargs):
            if Path(destination) == target:
                target.write_bytes(b"Other writer wins.\n")
                reached.append(True)
            return original_link(source, destination, *args, **kwargs)
        with mock.patch.object(capture_common.os, "link", side_effect=race):
            code, stdout, stderr = self.main(self.arguments() + ["--output", str(target)])
        self.assertEqual(reached, [True])
        self.assertEqual(code, 1)
        self.assertEqual(stdout, b"")
        self.assertTrue(stderr.startswith("replay error:"))
        self.assertEqual(target.read_bytes(), b"Other writer wins.\n")

    def test_complete_publication_is_retained_if_temporary_cleanup_fails(self):
        target = self.work / "published.json"
        original_unlink = Path.unlink
        reached = []
        def fail_cleanup(path, *args, **kwargs):
            if path.parent == target.parent and path.name.startswith(".capture-json-"):
                reached.append(path)
                raise OSError("independent temporary cleanup failure")
            return original_unlink(path, *args, **kwargs)
        with mock.patch.object(Path, "unlink", fail_cleanup):
            code, stdout, stderr = self.main(self.arguments() + ["--output", str(target)])
        self.assertEqual(len(reached), 1)
        self.assertEqual(code, 1)
        self.assertEqual(stdout, b"")
        self.assertIn("published and remains complete", stderr)
        self.assert_summary(json.loads(target.read_bytes()), self.report, self.report, self.fixture.path)

    def test_stdout_failure_after_publication_retains_complete_file(self):
        target = self.work / "published-before-stdout.json"
        class FailedOutput:
            def write(self, payload):
                raise OSError("independent stdout failure")
            def flush(self):
                pass
        stderr = io.StringIO()
        with mock.patch.object(sys, "stdout", FailedOutput()), mock.patch.object(sys, "stderr", stderr):
            code = subject.main(self.arguments() + ["--output", str(target)])
        self.assertEqual(code, 1)
        self.assertIn("stdout", stderr.getvalue())
        self.assert_summary(json.loads(target.read_bytes()), self.report, self.report, self.fixture.path)

    def test_short_stdout_and_failed_diagnostics_never_become_success(self):
        class ShortOutput:
            def __init__(self):
                self.received = ""
            def write(self, payload):
                self.received += payload[:7]
                return min(7, len(payload))
            def flush(self):
                pass
        stdout, stderr = ShortOutput(), io.StringIO()
        with mock.patch.object(sys, "stdout", stdout), mock.patch.object(sys, "stderr", stderr):
            code = subject.main(self.arguments())
        self.assertEqual(code, 1)
        self.assertTrue(stdout.received)
        self.assertIn("stdout", stderr.getvalue())
        class FailedStream:
            def write(self, payload):
                raise OSError("stream unavailable")
            def flush(self):
                raise OSError("stream unavailable")
        with mock.patch.object(sys, "stdout", FailedStream()), mock.patch.object(sys, "stderr", FailedStream()):
            self.assertNotEqual(subject.main(["--help"]), 0)
            self.assertNotEqual(subject.main(self.arguments(saved=self.work / "missing.json")), 0)

    def test_cancellation_propagates_without_publication_or_summary(self):
        target = self.work / "cancelled.json"
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(capture_job, "run_job", side_effect=KeyboardInterrupt), \
             mock.patch.object(sys, "stdout", stdout), mock.patch.object(sys, "stderr", stderr):
            with self.assertRaises(KeyboardInterrupt):
                subject.main(self.arguments() + ["--output", str(target)])
        self.assertFalse(target.exists())
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
