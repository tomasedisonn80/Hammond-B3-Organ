#!/usr/bin/env python3
"""Independent fixed-study acceptance from the cleared capture-study-v1 contract.

Expected identities, ordered outcomes, work, roles and counts are literal or
independently calculated. The archive author reuses only earlier independent
fixture construction. No producer helper calculates expected acceptance.
"""

from __future__ import annotations

from contextlib import ExitStack
import copy
import hashlib
import io
import itertools
import json
import os
from pathlib import Path
import platform
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))
import capture_audio
import capture_common
import capture_corpus
import capture_job
import compare_capture
import capture_study as subject
import test_capture_job as fixture_author

TOOL = ROOT / "tools" / "capture_study.py"
SOURCES = ("capture_audio.py", "capture_common.py", "capture_corpus.py",
           "capture_job.py", "capture_study.py", "compare_capture.py",
           "validate_capture.py")
CLAIMS = {"boundary_equivalence", "synchronization", "authenticity",
          "specimen_identity", "calibration", "permissions", "independence",
          "preregistration", "final_holdout_history", "physical_fidelity"}
REPORT_KEYS = {"schema_version", "study_contract", "study_id", "status", "input",
               "study", "corpus", "work", "summary", "jobs", "runtime",
               "tool_sources"} | CLAIMS
ENTRY_KEYS = {"job_id", "path", "expected_sha256", "observed_sha256", "size_bytes", "report"}
ROLES = ("fit", "validation", "final_test", "unassigned")


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def encoded(value, *, compact=False):
    style = {"separators": (",", ":")} if compact else {"indent": 2}
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                       **style) + "\n").encode("utf-8")


def raw(values):
    return struct.pack("<" + "f" * len(values), *values)


def shape(value):
    """Independent value-node and container-depth traversal; keys are excluded."""
    total, maximum, pending = 0, 0, [(value, 0)]
    while pending:
        item, depth = pending.pop()
        total += 1
        if type(item) in (list, dict):
            maximum = max(maximum, depth)
            children = item.values() if type(item) is dict else item
            pending.extend((child, depth + 1) for child in children)
    return total, maximum


def outcome(statuses):
    if "failed" in statuses:
        return "failed"
    if "inconclusive" in statuses:
        return "inconclusive"
    return "pass"


class StudyArchive:
    """One actual tiny corpus plus independently authored policies/job/study bytes."""

    def __init__(self, root, statuses=("pass",), *, names=None, purpose="validation"):
        base = fixture_author.JobArchive(root, purpose=purpose)
        self.root = base.root
        self.archive = base.archive
        self.template = copy.deepcopy(base.job)
        self.policy_template = copy.deepcopy(base.policy)
        self.jobs, self.policies, self.paths, self.policy_paths = {}, {}, {}, {}
        self.order = []
        self.path = self.root / "study.json"
        self.study = {"schema_version": 1,
                      "contract_origin": "project-proposed-capture-study-v1",
                      "study_id": "independent-study-v1", "corpus_sha256": "0" * 64,
                      "jobs": []}
        names = names or [f"job-{i}" for i in range(len(statuses))]
        for ident, status_value in zip(names, statuses):
            self.add(ident, status_value)

    def add(self, ident, status_value="pass"):
        position = len(self.order)
        self.order.append(ident)
        job = copy.deepcopy(self.template)
        policy = copy.deepcopy(self.policy_template)
        job["job_id"] = ident
        policy["policy_id"] = f"policy-{position}"
        policy["criteria"][0]["upper_bound"] = {
            "pass": 0.375, "inconclusive": 0.25, "failed": 0.0625}[status_value]
        job["policy"]["path"] = f"policy-{position}.json"
        self.jobs[ident], self.policies[ident] = job, policy
        self.paths[ident] = self.root / f"job-{position}.json"
        self.policy_paths[ident] = self.root / job["policy"]["path"]

    def write(self):
        self.archive.write()
        corpus_hash = sha(self.archive.path.read_bytes())
        self.study["corpus_sha256"] = corpus_hash
        self.study["jobs"] = []
        for ident in self.order:
            self.policy_paths[ident].write_bytes(encoded(self.policies[ident]))
            job = self.jobs[ident]
            job["corpus"]["sha256"] = corpus_hash
            job["policy"]["sha256"] = sha(self.policy_paths[ident].read_bytes())
            self.paths[ident].write_bytes(encoded(job))
            self.study["jobs"].append({"job_id": ident,
                                       "path": self.paths[ident].relative_to(self.root).as_posix(),
                                       "sha256": sha(self.paths[ident].read_bytes())})
        self.write_study()
        return self.path

    def write_study(self, payload=None):
        self.path.write_bytes(encoded(self.study) if payload is None else payload)

    def bind_job(self, ident, payload=None):
        self.paths[ident].write_bytes(encoded(self.jobs[ident]) if payload is None else payload)
        entry = next(item for item in self.study["jobs"] if item["job_id"] == ident)
        entry["sha256"] = sha(self.paths[ident].read_bytes())
        self.write_study()

    def bind_policy(self, ident, payload=None):
        self.policy_paths[ident].write_bytes(encoded(self.policies[ident]) if payload is None else payload)
        self.jobs[ident]["policy"]["sha256"] = sha(self.policy_paths[ident].read_bytes())
        self.bind_job(ident)


class StudyCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hammond-study-test-")
        self.addCleanup(self.temp.cleanup)
        # Canonical targets keep injected hooks valid under macOS /private/var
        # and Windows expanded TEMP paths as well as the current Linux runner.
        self.work = Path(self.temp.name).resolve()
        self.fixture = StudyArchive(self.work / "archive")
        self.fixture.write()

    def fixture_at(self, name, statuses=("pass",), **options):
        fixture = StudyArchive(self.work / name, statuses, **options)
        fixture.write()
        return fixture

    def run_study(self, fixture=None):
        return subject.run_study((fixture or self.fixture).path)

    def cli(self, fixture=None, *flags, cwd=None, env=None):
        return subprocess.run([sys.executable, "-B", str(TOOL), "--input",
                               str((fixture or self.fixture).path), *flags],
                              cwd=cwd or self.work, env=env, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=45, check=False)

    def main(self, flags):
        raw_stdout = io.BytesIO()
        stdout = io.TextIOWrapper(raw_stdout, encoding="ascii", errors="strict")
        stderr = io.StringIO()
        try:
            with mock.patch.object(sys, "stdout", stdout), mock.patch.object(sys, "stderr", stderr):
                result = subject.main(flags)
            stdout.flush()
            return result, raw_stdout.getvalue(), stderr.getvalue()
        finally:
            stdout.detach()

    def assert_rejected_before_artifacts(self, fixture=None):
        with ExitStack() as stack:
            traps = []
            for module, method in ((capture_corpus, "_verify_artifact"),
                                   (capture_audio, "inspect_audio"),
                                   (capture_audio, "read_audio_window")):
                traps.append(stack.enter_context(mock.patch.object(
                    module, method, side_effect=AssertionError("artifact work before study preflight"))))
            with self.assertRaises(subject.StudyError):
                self.run_study(fixture)
            for trap in traps:
                self.assertEqual(trap.call_count, 0)

    def assert_report(self, report, fixture=None, statuses=("pass",), roles=None):
        fixture = fixture or self.fixture
        roles = roles or ["validation"] * len(statuses)
        self.assertEqual(set(report), REPORT_KEYS)
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["study_contract"], "capture-study-v1")
        self.assertEqual(report["study_id"], fixture.study["study_id"])
        self.assertEqual(report["study"], fixture.study)
        self.assertEqual(report["status"], outcome(statuses))
        payload = fixture.path.read_bytes()
        self.assertEqual(report["input"], {"sha256": sha(payload), "size_bytes": len(payload)})
        corpus_hash = sha(fixture.archive.path.read_bytes())
        self.assertEqual(report["corpus"], {"expected_sha256": corpus_hash,
                                           "observed_sha256": corpus_hash})
        samples = sum(job["analysis"]["channel_count"] * job["analysis"]["frame_count"]
                      for job in fixture.jobs.values())
        terms = sum(job["analysis"]["channel_count"] * job["analysis"]["frame_count"]
                    * len(job["analysis"]["frequencies_hz"]) for job in fixture.jobs.values())
        self.assertEqual(report["work"], {"window_samples": samples, "spectral_terms": terms})
        self.assertEqual(report["summary"], {
            "jobs": len(statuses), "pass": statuses.count("pass"),
            "failed": statuses.count("failed"), "inconclusive": statuses.count("inconclusive"),
            "roles": {role: roles.count(role) for role in ROLES}})
        self.assertEqual(len(report["jobs"]), len(fixture.order))
        for item, ident, status_value in zip(report["jobs"], fixture.order, statuses):
            self.assertEqual(set(item), ENTRY_KEYS)
            self.assertEqual(item["job_id"], ident)
            entry = next(e for e in fixture.study["jobs"] if e["job_id"] == ident)
            original = fixture.paths[ident].read_bytes()
            self.assertEqual(item["path"], entry["path"])
            self.assertEqual(item["expected_sha256"], sha(original))
            self.assertEqual(item["observed_sha256"], sha(original))
            self.assertEqual(item["size_bytes"], len(original))
            self.assertEqual(item["report"]["status"], status_value)
            self.assertEqual(item["report"]["job"], fixture.jobs[ident])
            self.assertEqual(item["report"]["policy"], fixture.policies[ident])
            self.assertEqual(item["report"]["inputs"]["job"],
                             {"sha256": sha(original), "size_bytes": len(original)})
            self.assertEqual(item["report"]["runtime"], report["runtime"])
            self.assertEqual(len(item["report"]["tool_sources"]), 6)
            for field in CLAIMS:
                self.assertEqual(item["report"][field], "not_established")
        self.assertEqual(set(report["runtime"]),
                         {"python_implementation", "python_version", "sys_platform", "machine"})
        self.assertEqual(report["runtime"], {
            "python_implementation": sys.implementation.name,
            "python_version": platform.python_version(), "sys_platform": sys.platform,
            "machine": platform.machine()})
        self.assertEqual([item["module"] for item in report["tool_sources"]], list(SOURCES))
        for item in report["tool_sources"]:
            self.assertEqual(set(item), {"module", "sha256", "size_bytes"})
            original = (ROOT / "tools" / item["module"]).read_bytes()
            self.assertEqual(item["sha256"], sha(original))
            self.assertEqual(item["size_bytes"], len(original))
        for field in CLAIMS:
            self.assertEqual(report[field], "not_established")
        text = encoded(report).decode("utf-8")
        self.assertNotIn(str(fixture.root), text)
        self.assertNotIn('"samples":', text)


class StudyAdmission(StudyCase):
    def test_validate_is_io_free_and_load_reads_no_job(self):
        before = copy.deepcopy(self.fixture.study)
        for path in self.fixture.paths.values():
            path.unlink()
        loaded = subject.load_study(self.fixture.path)
        self.assertEqual(loaded, before)
        self.assertIsNot(loaded, self.fixture.study)
        shutil.rmtree(self.fixture.root)
        self.assertIsNone(subject.validate_study(before))
        self.assertEqual(before, self.fixture.study)

    def test_every_missing_unknown_root_and_entry_key_rejects(self):
        for position in (None, 0):
            target = self.fixture.study if position is None else self.fixture.study["jobs"][position]
            for key in (*target, None):
                value = copy.deepcopy(self.fixture.study)
                changed = value if position is None else value["jobs"][position]
                if key is None:
                    changed["unrecognized"] = "reject"
                else:
                    del changed[key]
                with self.subTest(position=position, key=key), self.assertRaises(subject.StudyError):
                    subject.validate_study(value)

    def test_exact_types_cycles_and_numeric_substitutes_reject(self):
        class DictSubclass(dict):
            pass
        class StringSubclass(str):
            pass
        class IntSubclass(int):
            pass
        cases = [DictSubclass(self.fixture.study), []]
        for key, bad in (("schema_version", True), ("schema_version", 1.0),
                         ("schema_version", IntSubclass(1)), ("study_id", StringSubclass("fixture")),
                         ("jobs", tuple(self.fixture.study["jobs"])), ("jobs", {}),
                         ("corpus_sha256", b"0" * 64)):
            item = copy.deepcopy(self.fixture.study)
            item[key] = bad
            cases.append(item)
        cyclic = copy.deepcopy(self.fixture.study)
        cyclic["jobs"] = [cyclic]
        cases.append(cyclic)
        for bad in (float("nan"), float("inf"), -float("inf"), 1e13):
            item = copy.deepcopy(self.fixture.study)
            item["schema_version"] = bad
            cases.append(item)
        for index, item in enumerate(cases):
            with self.subTest(index=index), self.assertRaises(subject.StudyError):
                subject.validate_study(item)

    def test_literals_ids_digests_and_portable_path_domains(self):
        for field, value in (("contract_origin", "capture-study-v1"), ("schema_version", 2),
                             ("study_id", "A"), ("study_id", "a" * 65),
                             ("study_id", "a\n"), ("study_id", ""),
                             ("corpus_sha256", "A" * 64), ("corpus_sha256", "0" * 63),
                             ("corpus_sha256", "0" * 64 + "\n")):
            item = copy.deepcopy(self.fixture.study)
            item[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(subject.StudyError):
                subject.validate_study(item)
        bad_paths = ("", ".", "..", "../job.json", "/job.json", "a//b", "a/./b",
                     "C:job.json", "\\\\server\\job", "a\\job", "con", "NUL.json", "a/com1.wav",
                     "job.", "réel.json", "a/" * 8 + "z", "a" * 65, ".hidden", "job\n")
        for path in bad_paths:
            item = copy.deepcopy(self.fixture.study)
            item["jobs"][0]["path"] = path
            with self.subTest(path=path), self.assertRaises(subject.StudyError):
                subject.validate_study(item)
        for path in ("a" * 64, "/".join(["a"] * 8),
                     "a" * 64 + "/" + "b" * 64 + "/" + "c" * 64 + "/" + "d" * 45):
            item = copy.deepcopy(self.fixture.study)
            item["jobs"][0]["path"] = path
            self.assertIsNone(subject.validate_study(item))
        item = copy.deepcopy(self.fixture.study)
        item["study_id"] = "a" * 64
        self.assertIsNone(subject.validate_study(item))

    def test_job_ids_case_folded_paths_and_hashes_are_separately_unique(self):
        base = self.fixture_at("two", ("pass", "pass")).study
        for field, value in (("job_id", base["jobs"][0]["job_id"]),
                             ("path", base["jobs"][0]["path"].upper()),
                             ("sha256", base["jobs"][0]["sha256"])):
            item = copy.deepcopy(base)
            item["jobs"][1][field] = value
            with self.subTest(field=field), self.assertRaises(subject.StudyError):
                subject.validate_study(item)

    def test_one_and_eight_entry_admission_and_zero_nine_rejection(self):
        self.assertIsNone(subject.validate_study(self.fixture.study))
        eight = self.fixture_at("eight", ("pass",) * 8)
        self.assertIsNone(subject.validate_study(eight.study))
        for count in (0, 9):
            item = copy.deepcopy(eight.study)
            item["jobs"] = item["jobs"][:count] if count == 0 else item["jobs"] + [{
                "job_id": "ninth", "path": "ninth.json", "sha256": "1" * 64}]
            with self.subTest(count=count), self.assertRaises(subject.StudyError):
                subject.validate_study(item)

    def test_strict_original_json_rejects_malformed_bytes(self):
        valid = encoded(self.fixture.study)
        cases = [b"\xef\xbb\xbf" + valid, b"\xff", valid + b"{}", b"null", b"[]",
                 valid.replace(b'"schema_version": 1', b'"schema_version": 1, "schema_version": 1'),
                 valid.replace(b'"schema_version": 1', b'"schema_version": NaN'),
                 valid.replace(b'"schema_version": 1', b'"schema_version": 1e999'),
                 valid.replace(b'"schema_version": 1', b'"schema_version": ' + b"1" * 65),
                 valid.replace(b'independent-study-v1', b'bad\\ud800'),
                 valid.replace(b'independent-study-v1', b'bad\\u0085'),
                 valid.replace(b'independent-study-v1', b'bad\\n')]
        for index, payload in enumerate(cases):
            self.fixture.write_study(payload)
            with self.subTest(index=index), self.assertRaises(subject.StudyError):
                subject.load_study(self.fixture.path)

    def test_actual_64_kib_study_admits_and_one_extra_byte_rejects(self):
        payload = encoded(self.fixture.study)
        padded = payload + b" " * (65536 - len(payload))
        self.fixture.write_study(padded)
        self.assertEqual(subject.load_study(self.fixture.path), self.fixture.study)
        report = self.run_study()
        self.assertEqual(report["input"], {"sha256": sha(padded), "size_bytes": 65536})
        self.fixture.write_study(padded + b" ")
        self.assert_rejected_before_artifacts()

    def test_invalid_input_path_types_reject_contextually(self):
        class StringSubclass(str):
            pass
        class PathLike:
            def __fspath__(inner):
                return str(self.fixture.path)
        for path in (None, 1, True, b"study.json", StringSubclass(str(self.fixture.path)), PathLike(), ""):
            for call in (subject.load_study, subject.run_study):
                with self.subTest(path=type(path).__name__, api=call.__name__), self.assertRaises(subject.StudyError):
                    call(path)

    def test_last_bad_job_hash_id_corpus_or_geometry_rejects_before_first_artifact(self):
        for index, failure in enumerate(("hash", "id", "corpus", "shape", "geometry")):
            fixture = self.fixture_at(f"bad-last-{index}", ("pass", "pass"))
            ident = fixture.order[-1]
            if failure == "hash":
                fixture.study["jobs"][-1]["sha256"] = "0" * 64
                fixture.write_study()
            else:
                if failure == "id":
                    fixture.jobs[ident]["job_id"] = "different-id"
                elif failure == "corpus":
                    fixture.jobs[ident]["corpus"]["sha256"] = "0" * 64
                elif failure == "shape":
                    fixture.jobs[ident]["extra"] = "reject"
                else:
                    fixture.jobs[ident]["analysis"]["channel_count"] = 17
                fixture.bind_job(ident)
            with self.subTest(failure=failure):
                self.assert_rejected_before_artifacts(fixture)

    def test_last_invalid_job_bytes_reject_before_first_artifact(self):
        fixture = self.fixture_at("bad-late-json", ("pass", "pass"))
        fixture.bind_job(fixture.order[-1], b'{"job_id":NaN}')
        self.assert_rejected_before_artifacts(fixture)

    def test_exact_64_kib_bound_job_and_original_whitespace_are_retained(self):
        ident = self.fixture.order[0]
        payload = encoded(self.fixture.jobs[ident])
        payload += b" " * (65536 - len(payload))
        self.fixture.bind_job(ident, payload)
        report = self.run_study()
        self.assertEqual(report["jobs"][0]["observed_sha256"], sha(payload))
        self.assertEqual(report["jobs"][0]["size_bytes"], 65536)
        self.assertEqual(report["jobs"][0]["report"]["inputs"]["job"]["sha256"], sha(payload))
        self.fixture.bind_job(ident, payload + b" ")
        self.assert_rejected_before_artifacts()

    def test_cumulative_spectral_limit_is_enforced_before_any_job_execution(self):
        fixture = self.fixture_at("spectral", ("pass", "pass"))
        for ident in fixture.order:
            fixture.jobs[ident]["analysis"].update(
                sample_rate_hz=48000, channel_count=4, frame_count=65536,
                frequencies_hz=list(range(64)))
            fixture.bind_job(ident)
        class ReachedCore(Exception):
            pass
        with mock.patch.object(capture_job, "_run_bound_job", side_effect=ReachedCore) as core:
            with self.assertRaises(ReachedCore):
                self.run_study(fixture)
            self.assertEqual(core.call_count, 1)
        fixture.add("one-more-term")
        fixture.jobs["one-more-term"]["analysis"].update(frame_count=1, frequencies_hz=[0])
        fixture.write()
        self.assert_rejected_before_artifacts(fixture)
        with mock.patch.object(capture_job, "_run_bound_job", side_effect=AssertionError("core after work excess")) as core:
            with self.assertRaises(subject.StudyError):
                self.run_study(fixture)
            self.assertEqual(core.call_count, 0)

    def test_maximum_declared_window_sum_admits_without_executing_maximum_work(self):
        fixture = self.fixture_at("window-header-max", ("pass",) * 8)
        for ident in fixture.order:
            fixture.jobs[ident]["analysis"].update(sample_rate_hz=48000, channel_count=4,
                                                  frame_count=262144, frequencies_hz=[])
            fixture.bind_job(ident)
        class ReachedCore(Exception):
            pass
        with mock.patch.object(capture_job, "_run_bound_job", side_effect=ReachedCore) as core:
            with self.assertRaises(ReachedCore):
                self.run_study(fixture)
            self.assertEqual(core.call_count, 1)


class StudyResults(StudyCase):
    def test_literal_quarter_offset_report_and_four_original_identities_are_retained(self):
        report = self.run_study()
        self.assert_report(report)
        job = report["jobs"][0]["report"]
        self.assertEqual(job["reference"]["inspection"]["sha256"],
                         "fd801740524b1e1c23a61b5400725b76428652827ba1261b83243eb5ce551402")
        self.assertEqual(job["candidate"]["inspection"]["sha256"],
                         "bac1c395abe23908b8c106a28b6c151bc25b9473d470f4d942775b5dfdf523e2")
        self.assertEqual(job["reference"]["inspection"]["decoded_sha256"],
                         "786665f3cf05b2f9b33e7cadee75e7176e122d62ad82133c72737c76261dd440")
        self.assertEqual(job["candidate"]["inspection"]["decoded_sha256"],
                         "79d8014af588d583abcc570598d3e073413543ef518b339cbca37dbb5eb6bd0c")
        self.assertEqual(job["evaluation"]["comparison"]["channels"][0]["metrics"]["rms_error_fs"],
                         {"value": 0.25, "unit": "FS", "undefined_reason": None})

    def test_all_27_ordered_status_combinations_keep_every_complete_job(self):
        totals = {"pass": 0, "failed": 0, "inconclusive": 0}
        for index, statuses in enumerate(itertools.product(("pass", "failed", "inconclusive"), repeat=3)):
            fixture = self.fixture_at(f"statuses-{index}", statuses, names=["zeta", "alpha", "middle"])
            report = self.run_study(fixture)
            with self.subTest(statuses=statuses):
                self.assert_report(report, fixture, statuses=list(statuses))
                self.assertEqual([entry["job_id"] for entry in report["jobs"]], ["zeta", "alpha", "middle"])
            totals[report["status"]] += 1
        self.assertEqual(totals, {"pass": 1, "failed": 19, "inconclusive": 7})

    def test_eight_actual_jobs_complete_without_inferred_role_requirements(self):
        fixture = self.fixture_at("eight-complete", ("pass",) * 8, purpose="fit")
        report = self.run_study(fixture)
        self.assert_report(report, fixture, statuses=["pass"] * 8, roles=["fit"] * 8)
        self.assertEqual(report["summary"]["roles"]["final_test"], 0)
        self.assertEqual(report["status"], "pass")

    def test_empty_frequency_lists_contribute_zero_spectral_terms(self):
        fixture = self.fixture_at("no-frequencies", ("pass", "pass"))
        for ident in fixture.order:
            fixture.jobs[ident]["analysis"]["frequencies_hz"] = []
            fixture.policies[ident]["analysis"]["frequencies_hz"] = []
        fixture.write()
        report = self.run_study(fixture)
        self.assert_report(report, fixture, statuses=["pass", "pass"])
        self.assertEqual(report["work"], {"window_samples": 8, "spectral_terms": 0})

    def test_all_four_roles_are_counted_without_changing_whole_corpus_outcomes(self):
        fixture = self.fixture_at("all-roles", ())
        for position, purpose in enumerate(("fit", "validation", "final", "unassigned")):
            ref, cand = f"{purpose}-ref", f"{purpose}-cand"
            values = [4.0 * (position + 1) + x for x in (1, -1, 1, -1)]
            fixture.archive.add(ref, purpose, raw=raw(values), rate=4, channels=1,
                                format_name="raw_float32_le")
            fixture.archive.add(cand, purpose, raw=raw([x + 0.25 for x in values]), rate=4,
                                channels=1, format_name="raw_float32_le")
            fixture.add(f"role-{position}")
            job = fixture.jobs[f"role-{position}"]
            job["reference"]["capture_id"], job["candidate"]["capture_id"] = ref, cand
            fixture.policies[f"role-{position}"]["evaluation_role"] = {
                "final": "final_test"}.get(purpose, purpose)
        fixture.write()
        report = self.run_study(fixture)
        self.assert_report(report, fixture, statuses=["inconclusive"] * 4,
                           roles=list(ROLES))
        self.assertEqual(report["summary"]["roles"], dict.fromkeys(ROLES, 1))

    def test_unselected_leakage_is_retained_even_when_every_pair_passes(self):
        fixture = self.fixture_at("leak", ("pass", "pass"))
        fixture.archive.add("fit-copy", "fit", raw=raw([1, -1, 1, -1]), rate=4,
                            channels=1, format_name="raw_float32_le")
        fixture.write()
        report = self.run_study(fixture)
        self.assert_report(report, fixture, statuses=["failed", "failed"])
        for entry in report["jobs"]:
            self.assertEqual(entry["report"]["evaluation"]["numerical_verdict"], "pass")
            self.assertIn("cross_purpose_component",
                          [f["code"] for f in entry["report"]["corpus_report"]["findings"]])

    def test_unrelated_plan_stays_inconclusive_beside_a_failed_job(self):
        fixture = self.fixture_at("plan-and-failure", ("pass", "failed"))
        fixture.archive.add("future", "unassigned", planned=True)
        fixture.write()
        report = self.run_study(fixture)
        self.assert_report(report, fixture, statuses=["inconclusive", "failed"])
        for entry in report["jobs"]:
            self.assertIn("planned_capture", [f["code"] for f in entry["report"]["corpus_report"]["findings"]])

    def test_complete_subordinate_reports_are_preserved_without_projection(self):
        fixture = self.fixture_at("complete-nested", ("failed", "inconclusive"))
        real = capture_job._run_bound_job
        observed = []
        def record(*args, **kwargs):
            report = real(*args, **kwargs)
            observed.append(copy.deepcopy(report))
            return report
        with mock.patch.object(capture_job, "_run_bound_job", side_effect=record) as called:
            report = self.run_study(fixture)
            self.assertEqual(called.call_count, 2)
        self.assertEqual([entry["report"] for entry in report["jobs"]], observed)
        self.assert_report(report, fixture, statuses=["failed", "inconclusive"])

    def test_corpus_copies_with_one_identity_are_allowed_and_individually_audited(self):
        fixture = self.fixture_at("copies", ("pass", "pass"))
        shutil.copytree(fixture.archive.root, fixture.root / "other-corpus")
        fixture.jobs[fixture.order[1]]["corpus"]["path"] = "other-corpus/corpus.json"
        fixture.bind_job(fixture.order[1])
        report = self.run_study(fixture)
        self.assert_report(report, fixture, statuses=["pass", "pass"])
        target = fixture.root / "other-corpus/captures/candidate/raw.bin"
        target.write_bytes(target.read_bytes() + b"\x00")
        with self.assertRaises(subject.StudyError):
            self.run_study(fixture)

    def test_original_compact_policy_bytes_survive_study_composition(self):
        ident = self.fixture.order[0]
        self.fixture.policies[ident]["analysis"].update(channel_count=3, frequencies_hz=list(range(32)))
        self.fixture.policies[ident]["analysis"]["sample_rate_hz"] = 64
        self.fixture.jobs[ident]["analysis"] = copy.deepcopy(self.fixture.policies[ident]["analysis"])
        # A separate tiny three-channel archive exercises every declared target.
        archive = self.fixture.archive
        for capture_id, values in (("reference", [1, 2, 3, -1, -2, -3] * 2),
                                   ("candidate", [1.25, 2.25, 3.25, -.75, -1.75, -2.75] * 2)):
            record = archive.manifests[capture_id]
            record["digital"]["sample_rate_hz"]["value"] = 64
            record["digital"]["channel_count"]["value"] = 3
            record["digital"]["channels"] = [fixture_author.fixtures._channel(i) for i in range(3)]
            item = record["files"][0]
            payload = raw(values)
            archive.file_path(capture_id, "raw").write_bytes(payload)
            item.update(size_bytes=len(payload), sha256=sha(payload))
        criteria = []
        for channel in range(3):
            for frequency in range(32):
                for metric in ("complex_abs_error_fs", "normalized_complex_error"):
                    item = fixture_author.criterion(
                        ident=f"c-{channel}-{frequency}-{len(criteria)}", metric=metric,
                        channel=channel, frequency=frequency, bound=1000000)
                    item["rationale"] = "Original byte fixture."
                    item["uncertainty"]["evidence"] = "Declared margin."
                    criteria.append(item)
        self.fixture.policies[ident]["criteria"] = criteria
        self.fixture.write()
        compact = encoded(self.fixture.policies[ident], compact=True)
        self.assertLessEqual(len(compact), 65536)
        # Deliberately use a compact document whose formatted equivalent exceeds admission.
        self.assertGreater(len(encoded(self.fixture.policies[ident])), 65536)
        self.fixture.bind_policy(ident, compact)
        seen = []
        real = compare_capture.evaluate_policy
        def observe(comparison, policy_bytes):
            seen.append(policy_bytes)
            return real(comparison, policy_bytes)
        with mock.patch.object(compare_capture, "evaluate_policy", side_effect=observe):
            report = self.run_study()
        self.assertEqual(seen, [compact])
        self.assertEqual(report["jobs"][0]["report"]["evaluation"]["policy_sha256"], sha(compact))

    def test_relocation_original_whitespace_and_returned_copy_independence(self):
        self.fixture.policies[self.fixture.order[0]]["criteria"][0]["rationale"] = "Déclaration λ remains unchanged."
        self.fixture.write()
        first = self.run_study()
        moved = self.work / "relocated-λ"
        shutil.copytree(self.fixture.root, moved)
        relocated = subject.run_study(moved / self.fixture.path.name)
        self.assertEqual(encoded(first), encoded(relocated))
        first["study"]["study_id"] = "mutated-output"
        first["jobs"][0]["report"]["policy"]["policy_id"] = "mutated-policy"
        self.assertEqual(encoded(self.run_study()), encoded(relocated))
        payload = self.fixture.path.read_bytes() + b" "
        self.fixture.write_study(payload)
        changed = self.run_study()
        self.assertEqual(changed["study"], relocated["study"])
        self.assertNotEqual(changed["input"]["sha256"], relocated["input"]["sha256"])


class StudyComposition(StudyCase):
    def test_all_headers_precede_execution_and_each_job_is_read_exactly_twice(self):
        fixture = self.fixture_at("read-order", ("pass", "pass", "pass"))
        events, shared = [], []
        real_read, real_core = capture_corpus._read_confined_bytes, capture_job._run_bound_job
        def read(root, parts, *args, **kwargs):
            target = root.joinpath(*parts).resolve()
            events.append(("read", target))
            return real_read(root, parts, *args, **kwargs)
        def core(path, *args, **kwargs):
            selected = Path(path).resolve()
            events.append(("core", selected))
            shared.append(kwargs["snapshots"])
            entry = next(e for e in fixture.study["jobs"]
                         if (fixture.root / e["path"]).resolve() == selected)
            self.assertEqual(kwargs["expected_job_sha256"], entry["sha256"])
            return real_core(path, *args, **kwargs)
        with mock.patch.object(capture_corpus, "_read_confined_bytes", side_effect=read), \
             mock.patch.object(capture_job, "_run_bound_job", side_effect=core), \
             mock.patch.object(capture_job, "run_job", side_effect=AssertionError("unbound public job called")):
            report = self.run_study(fixture)
        self.assert_report(report, fixture, statuses=["pass"] * 3)
        first_core = next(i for i, event in enumerate(events) if event[0] == "core")
        for ident in fixture.order:
            selected = fixture.paths[ident].resolve()
            self.assertEqual(events[:first_core].count(("read", selected)), 1)
            self.assertEqual(events.count(("read", selected)), 2)
        self.assertEqual([p for action, p in events if action == "core"],
                         [fixture.paths[ident].resolve() for ident in fixture.order])
        self.assertEqual(len(shared), 3)
        self.assertTrue(all(item is shared[0] for item in shared))

    def test_each_job_performs_fresh_whole_corpus_audit_and_selected_windows(self):
        fixture = self.fixture_at("fresh-each", ("pass", "pass"))
        with mock.patch.object(capture_corpus, "_verify_artifact", wraps=capture_corpus._verify_artifact) as files, \
             mock.patch.object(capture_audio, "inspect_audio", wraps=capture_audio.inspect_audio) as audio, \
             mock.patch.object(capture_audio, "read_audio_window", wraps=capture_audio.read_audio_window) as windows:
            self.run_study(fixture)
        self.assertEqual(files.call_count, 4)
        self.assertEqual(audio.call_count, 4)
        self.assertEqual(windows.call_count, 4)

    def test_changed_bound_job_rejects_before_its_corpus_or_policy_read(self):
        fixture = self.fixture_at("changed-job", ("pass", "pass"))
        real_core, real_bound = capture_job._run_bound_job, capture_job._bound_input
        calls, dependency_labels = [], []
        def core(path, *args, **kwargs):
            result = real_core(path, *args, **kwargs)
            calls.append(Path(path).resolve())
            if len(calls) == 1:
                target = fixture.paths[fixture.order[1]]
                target.write_bytes(target.read_bytes() + b" ")
            return result
        def dependency(*args, **kwargs):
            dependency_labels.append(kwargs["label"])
            return real_bound(*args, **kwargs)
        with mock.patch.object(capture_job, "_run_bound_job", side_effect=core) as invoked, \
             mock.patch.object(capture_job, "_bound_input", side_effect=dependency):
            with self.assertRaises(subject.StudyError):
                self.run_study(fixture)
        self.assertEqual(invoked.call_count, 2)
        self.assertEqual(len(calls), 1)
        self.assertEqual(dependency_labels, ["corpus", "policy"])

    def test_later_invalid_policy_follows_earlier_work_but_never_publishes(self):
        fixture = self.fixture_at("late-policy", ("pass", "pass"))
        fixture.bind_policy(fixture.order[1], b"{")
        destination = self.work / "unpublished.json"
        before = {p.relative_to(fixture.root): p.read_bytes()
                  for p in fixture.root.rglob("*") if p.is_file()}
        with mock.patch.object(capture_corpus, "_verify_artifact", wraps=capture_corpus._verify_artifact) as files:
            code, stdout, stderr = self.main(["--input", str(fixture.path), "--output", str(destination)])
        self.assertEqual(files.call_count, 2)
        self.assertEqual(code, 1)
        self.assertEqual(stdout, b"")
        self.assertTrue(stderr.startswith("study error:"), stderr)
        self.assertFalse(destination.exists())
        after = {p.relative_to(fixture.root): p.read_bytes()
                 for p in fixture.root.rglob("*") if p.is_file()}
        self.assertEqual(after, before)

    def test_reduced_window_sum_cap_is_inclusive_and_rejects_before_core(self):
        fixture = self.fixture_at("window-cap", ("pass", "pass"))
        with mock.patch.object(subject, "MAX_WINDOW_SAMPLES", 8):
            report = self.run_study(fixture)
            self.assertEqual(report["work"]["window_samples"], 8)
        with mock.patch.object(subject, "MAX_WINDOW_SAMPLES", 7), \
             mock.patch.object(capture_job, "_run_bound_job", side_effect=AssertionError("core after excess")) as core:
            self.assert_rejected_before_artifacts(fixture)
            self.assertEqual(core.call_count, 0)

    def test_complete_eight_job_max_reference_layout_respects_snapshot_derivation(self):
        fixture = self.fixture_at("snapshot-max-layout", ("pass",) * 8)
        for index in range(62):
            fixture.archive.add(f"extra-{index:02}", "validation", raw=raw([index + 2.0]),
                                rate=4, channels=1, format_name="raw_float32_le")
        for ident in fixture.archive.manifests:
            for n in range(3):
                fixture.archive.file(ident, f"notes-{n}", f"{ident} support {n}".encode(), kind="support")
        fixture.write()
        self.assertEqual(len(fixture.archive.manifests), 64)
        self.assertEqual(sum(len(m["files"]) for m in fixture.archive.manifests.values()), 256)
        real = capture_job._run_bound_job
        seen = []
        def core(*args, **kwargs):
            result = real(*args, **kwargs)
            seen.append(kwargs["snapshots"])
            return result
        with mock.patch.object(capture_job, "_run_bound_job", side_effect=core):
            report = self.run_study(fixture)
        self.assertEqual(len(seen), 8)
        self.assertTrue(all(value is seen[0] for value in seen))
        self.assertLessEqual(len(seen[0].leaves), 2642)
        self.assertLessEqual(len(seen[0].roots), 58)
        self.assertEqual(len(report["jobs"]), 8)
        self.assertEqual(report["status"], "pass")
        for entry in report["jobs"]:
            self.assertEqual(len(entry["report"]["corpus_report"]["captures"]), 64)
            self.assertEqual(sum(len(c["files"]) for c in entry["report"]["corpus_report"]["captures"]), 256)

    def test_snapshot_caps_reject_before_appending_excess_observations(self):
        real = subject._StudySnapshots
        for constant, attribute in (("MAX_LEAF_SNAPSHOTS", "leaves"),
                                    ("MAX_ROOT_SNAPSHOTS", "roots")):
            created = []
            def snapshots():
                instance = real()
                created.append(instance)
                return instance
            with self.subTest(constant=constant), mock.patch.object(subject, constant, 1), \
                 mock.patch.object(subject, "_StudySnapshots", side_effect=snapshots):
                with self.assertRaises(subject.StudyError):
                    self.run_study()
            self.assertEqual(len(created), 1)
            self.assertLessEqual(len(getattr(created[0], attribute)), 1)

    def test_runtime_and_source_disagreement_are_not_silently_chosen(self):
        fixture = self.fixture_at("version-disagreement", ("pass", "pass"))
        original_runtime = capture_job._runtime
        count = 0
        def runtime():
            nonlocal count
            value = original_runtime()
            count += 1
            if count == 2:
                value["python_version"] = "different-version"
            return value
        with mock.patch.object(capture_job, "_runtime", side_effect=runtime):
            with self.assertRaises(subject.StudyError):
                self.run_study(fixture)
        self.assertEqual(count, 2)
        original_sources = capture_job._source_observations
        count = 0
        def sources(*args, **kwargs):
            nonlocal count
            value = original_sources(*args, **kwargs)
            count += 1
            if count == 2:
                value[0]["sha256"] = "0" * 64
            return value
        with mock.patch.object(capture_job, "_source_observations", side_effect=sources):
            with self.assertRaises(subject.StudyError):
                self.run_study(fixture)
        self.assertEqual(count, 2)

    def test_returned_job_identity_size_and_common_corpus_postconditions_are_checked(self):
        real = capture_job._run_bound_job
        variants = (("job_id",), ("inputs", "job", "sha256"),
                    ("inputs", "job", "size_bytes"), ("inputs", "corpus", "observed_sha256"),
                    ("corpus_report", "index_sha256"))
        for path in variants:
            reached = []
            def corrupt(*args, **kwargs):
                report = real(*args, **kwargs)
                reached.append(True)
                target = report
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = 1 if path[-1] == "size_bytes" else (
                    "different-id" if path[-1] == "job_id" else "0" * 64)
                return report
            with self.subTest(path=path), mock.patch.object(capture_job, "_run_bound_job", side_effect=corrupt):
                with self.assertRaises(subject.StudyError):
                    self.run_study()
            self.assertEqual(reached, [True])


class StudySnapshotsAndLimits(StudyCase):
    def test_final_study_snapshot_rechecks_all_earlier_input_categories(self):
        categories = ("study", "first-job", "first-policy", "index", "first-manifest",
                      "candidate-manifest", "selected-audio", "unselected-audio", "unselected-support")
        real = capture_job._run_bound_job
        for number, category in enumerate(categories):
            fixture = self.fixture_at(f"late-{number}", ("pass", "pass"))
            fixture.archive.add("other", "validation", raw=raw([9.0, -9.0]), rate=4,
                                channels=1, format_name="raw_float32_le")
            fixture.archive.file("other", "notes", b"Actual supporting bytes.", kind="support")
            fixture.write()
            targets = {
                "study": fixture.path,
                "first-job": fixture.paths[fixture.order[0]],
                "first-policy": fixture.policy_paths[fixture.order[0]],
                "index": fixture.archive.path,
                "first-manifest": fixture.archive.root / fixture.archive.entries["reference"]["manifest_path"],
                "candidate-manifest": fixture.archive.root / fixture.archive.entries["candidate"]["manifest_path"],
                "selected-audio": fixture.archive.file_path("reference", "raw"),
                "unselected-audio": fixture.archive.file_path("other", "raw"),
                "unselected-support": fixture.archive.file_path("other", "notes"),
            }
            completed = []
            def mutate(*args, **kwargs):
                report = real(*args, **kwargs)
                completed.append(True)
                if len(completed) == 2:
                    selected = targets[category]
                    selected.write_bytes(selected.read_bytes() + b" ")
                return report
            with self.subTest(category=category), mock.patch.object(capture_job, "_run_bound_job", side_effect=mutate):
                with self.assertRaises(subject.StudyError):
                    self.run_study(fixture)
            self.assertEqual(completed, [True, True], "the late mutation hook must be reached after both jobs")

    def test_change_to_earlier_policy_between_jobs_is_not_forgotten(self):
        fixture = self.fixture_at("between-jobs", ("pass", "pass"))
        real = capture_job._run_bound_job
        completed = []
        def mutate(*args, **kwargs):
            report = real(*args, **kwargs)
            completed.append(True)
            if len(completed) == 1:
                path = fixture.policy_paths[fixture.order[0]]
                path.write_bytes(path.read_bytes() + b" ")
            return report
        with mock.patch.object(capture_job, "_run_bound_job", side_effect=mutate) as called:
            with self.assertRaises(subject.StudyError):
                self.run_study(fixture)
        self.assertEqual(called.call_count, 2)
        self.assertEqual(completed, [True])

    def test_same_bytes_leaf_and_parent_replacement_reject_after_last_job(self):
        for replace_parent in (False, True):
            fixture = self.fixture_at("replacement-" + str(replace_parent))
            target = fixture.archive.file_path("candidate", "raw")
            payload = target.read_bytes()
            real = capture_job._run_bound_job
            reached = []
            def mutate(*args, **kwargs):
                report = real(*args, **kwargs)
                reached.append(True)
                if replace_parent:
                    parent = target.parent
                    moved = parent.with_name("old-candidate")
                    parent.rename(moved)
                    parent.mkdir()
                    shutil.copyfile(moved / target.name, target)
                else:
                    replacement = target.with_name("replacement.bin")
                    replacement.write_bytes(payload)
                    os.replace(replacement, target)
                return report
            with self.subTest(parent=replace_parent), mock.patch.object(capture_job, "_run_bound_job", side_effect=mutate):
                with self.assertRaises(subject.StudyError):
                    self.run_study(fixture)
            self.assertEqual(reached, [True])
            self.assertEqual(target.read_bytes(), payload)

    def test_unrelated_sibling_creation_after_last_job_preserves_pass(self):
        real = capture_job._run_bound_job
        reached = []
        def sibling(*args, **kwargs):
            report = real(*args, **kwargs)
            reached.append(True)
            (self.fixture.root / "unrelated.txt").write_bytes(b"Sibling does not alter an admitted input.")
            (self.fixture.archive.root / "captures/candidate/unrelated.txt").write_bytes(b"Another sibling.")
            return report
        with mock.patch.object(capture_job, "_run_bound_job", side_effect=sibling):
            report = self.run_study()
        self.assertEqual(reached, [True])
        self.assertEqual(report["status"], "pass")

    def test_all_seven_sources_remain_bound_between_jobs_and_at_final_return(self):
        fixture = self.fixture_at("source-phases", ("pass", "pass"))
        script = r'''
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
import capture_job, capture_study
real = capture_job._run_bound_job
reached = []
invoked = 0
def mutate(*args, **kwargs):
    global invoked
    invoked += 1
    result = real(*args, **kwargs)
    reached.append(True)
    if len(reached) == int(sys.argv[4]):
        target = Path(sys.argv[1]) / sys.argv[3]
        target.write_bytes(target.read_bytes() + b"\n# controlled source mutation\n")
    return result
capture_job._run_bound_job = mutate
try:
    capture_study.run_study(sys.argv[2])
except capture_study.StudyError as error:
    assert reached == [True] * int(sys.argv[4])
    assert invoked == 2
    print("StudyError: " + str(error))
else:
    raise SystemExit("late source mutation was accepted")
'''
        for phase in (1, 2):
            for name in SOURCES:
                copied = self.work / (f"sources-{phase}-" + name)
                copied.mkdir()
                for source in SOURCES:
                    shutil.copyfile(ROOT / "tools" / source, copied / source)
                result = subprocess.run([sys.executable, "-B", "-c", script, str(copied),
                                         str(fixture.path), name, str(phase)], cwd=self.work,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        timeout=45, check=False)
                with self.subTest(source=name, after_job=phase):
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertTrue(result.stdout.startswith(b"StudyError:"), result.stdout)
                    self.assertEqual(result.stderr, b"")

    def test_study_source_must_be_bounded_regular_and_have_the_expected_basename(self):
        for mode in ("oversized", "directory", "wrong-name"):
            folder = self.work / ("source-" + mode)
            folder.mkdir()
            path = folder / ("other.py" if mode == "wrong-name" else "capture_study.py")
            if mode == "directory":
                path.mkdir()
            else:
                path.write_bytes(b"#" * (1048577 if mode == "oversized" else 1))
            with self.subTest(mode=mode), mock.patch.object(subject, "__file__", str(path)):
                self.assert_rejected_before_artifacts()

    def test_study_root_job_leaf_and_descendant_links_are_rejected(self):
        if not hasattr(os, "symlink"):
            self.skipTest("native symlinks unavailable")
        for variant in ("study-leaf", "study-root", "job-leaf", "job-parent"):
            fixture = self.fixture_at("links-" + variant)
            try:
                if variant == "study-leaf":
                    target = fixture.path
                    moved = target.with_name("real-study.json")
                    target.rename(moved)
                    target.symlink_to(moved)
                elif variant == "study-root":
                    old_root = fixture.root
                    moved = old_root.with_name(old_root.name + "-real")
                    old_root.rename(moved)
                    old_root.symlink_to(moved, target_is_directory=True)
                elif variant == "job-leaf":
                    target = fixture.paths[fixture.order[0]]
                    moved = target.with_name("real-job.json")
                    target.rename(moved)
                    target.symlink_to(moved)
                else:
                    folder = fixture.root / "jobs"
                    folder.mkdir()
                    target = folder / "job.json"
                    shutil.copyfile(fixture.paths[fixture.order[0]], target)
                    moved = fixture.root / "actual-jobs"
                    folder.rename(moved)
                    folder.symlink_to(moved, target_is_directory=True)
                    fixture.study["jobs"][0]["path"] = "jobs/job.json"
                    fixture.write_study()
            except (OSError, NotImplementedError) as error:
                self.skipTest(f"native symlink creation unavailable: {error}")
            with self.subTest(variant=variant), mock.patch.object(
                    capture_job, "_run_bound_job",
                    side_effect=AssertionError("linked input reached job execution")) as core:
                self.assert_rejected_before_artifacts(fixture)
                self.assertEqual(core.call_count, 0)

    def test_alias_above_study_root_is_allowed(self):
        alias = self.work / "ordinary-alias"
        try:
            alias.symlink_to(self.work / "archive", target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"native symlink creation unavailable: {error}")
        # The selected root must itself be real; place an ordinary directory below the alias.
        nested = self.fixture_at("archive/nested")
        report = subject.run_study(alias / "nested/study.json")
        self.assertEqual(report, self.run_study(nested))

    def test_nonregular_study_and_job_inputs_reject_without_waiting(self):
        for which in ("study", "job"):
            fixture = self.fixture_at("nonregular-" + which)
            target = fixture.path if which == "study" else fixture.paths[fixture.order[0]]
            target.unlink()
            target.mkdir()
            with self.subTest(which=which):
                self.assert_rejected_before_artifacts(fixture)

    def test_native_fifo_study_input_rejects_without_waiting(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("native FIFO creation unavailable")
        fixture = self.fixture_at("fifo-study")
        fixture.path.unlink()
        try:
            os.mkfifo(fixture.path)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"native FIFO creation unavailable: {error}")
        self.assert_rejected_before_artifacts(fixture)

    def test_descriptor_wrap_failure_and_cancellation_close_the_opened_study_file(self):
        for failure in (OSError("injected wrapping failure"), KeyboardInterrupt("injected cancellation")):
            descriptors = []
            def fail(descriptor, *args, **kwargs):
                descriptors.append(descriptor)
                raise failure
            with self.subTest(kind=type(failure).__name__), mock.patch.object(os, "fdopen", side_effect=fail):
                with self.assertRaises(KeyboardInterrupt if isinstance(failure, KeyboardInterrupt) else subject.StudyError):
                    self.run_study()
            self.assertEqual(len(descriptors), 1, "the real opened file must reach the failure hook")
            with self.assertRaises(OSError):
                os.fstat(descriptors[0])

    def test_growing_report_limits_reject_before_later_jobs_and_never_truncate(self):
        fixture = self.fixture_at("growing", ("pass", "pass", "pass"))
        baseline = self.run_study(fixture)
        baseline_bytes = len(encoded(baseline))
        nodes, depth = shape(baseline)
        for constant, exact in (("MAX_REPORT_BYTES", baseline_bytes),
                                ("MAX_REPORT_NODES", nodes), ("MAX_REPORT_DEPTH", depth)):
            with self.subTest(constant=constant), mock.patch.object(subject, constant, exact):
                self.assertEqual(self.run_study(fixture), baseline)
            with self.subTest(excess=constant), mock.patch.object(subject, constant, exact - 1):
                with self.assertRaises(subject.StudyError):
                    self.run_study(fixture)
        real = capture_job._run_bound_job
        reached = []
        def core(*args, **kwargs):
            result = real(*args, **kwargs)
            reached.append(True)
            return result
        output = self.work / "too-large-report.json"
        with mock.patch.object(subject, "MAX_REPORT_BYTES", 1), \
             mock.patch.object(capture_job, "_run_bound_job", side_effect=core):
            code, stdout, stderr = self.main(["--input", str(fixture.path), "--output", str(output)])
        self.assertEqual(reached, [True], "the growing envelope rejects after the first full job")
        self.assertEqual(code, 1)
        self.assertEqual(stdout, b"")
        self.assertTrue(stderr.startswith("study error:"))
        self.assertFalse(output.exists())


class StudyCommandLine(StudyCase):
    def test_actual_cli_all_statuses_emit_complete_utf8_lf_reports(self):
        for status_value, exit_code in (("pass", 0), ("failed", 1), ("inconclusive", 3)):
            fixture = self.fixture_at("cli-" + status_value, (status_value,))
            result = self.cli(fixture)
            with self.subTest(status=status_value):
                self.assertEqual(result.returncode, exit_code, result.stderr)
                self.assertEqual(result.stderr, b"")
                self.assertEqual(result.stdout, encoded(self.run_study(fixture)))
                self.assertNotIn(b"\r", result.stdout)
                self.assertTrue(result.stdout.endswith(b"\n"))

    def test_foreign_cwd_unicode_archive_and_ascii_terminal_preserve_utf8(self):
        fixture = self.fixture_at("Unicode-λ")
        fixture.policies[fixture.order[0]]["criteria"][0]["rationale"] = "Déclaration λ remains unchanged."
        fixture.write()
        foreign = self.work / "unrelated-cwd"
        foreign.mkdir()
        destination = foreign / "résultat.json"
        environment = dict(os.environ, PYTHONIOENCODING="ascii", PYTHONUTF8="0")
        result = self.cli(fixture, "--output", str(destination), cwd=foreign, env=environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b"")
        self.assertIn("Déclaration λ".encode("utf-8"), result.stdout)
        self.assertEqual(result.stdout, destination.read_bytes())
        self.assertEqual(result.stdout, encoded(self.run_study(fixture)))

    def test_main_none_and_text_only_streams_preserve_exact_values(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(sys, "argv", ["capture_study.py", "--input", str(self.fixture.path)]), \
             mock.patch.object(sys, "stdout", stdout), mock.patch.object(sys, "stderr", stderr):
            result = subject.main(None)
        self.assertEqual(result, 0)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(stdout.getvalue().encode("utf-8"), encoded(self.run_study()))

    def test_usage_missing_unknown_abbreviated_duplicate_empty_and_override_flags(self):
        good = ["--input", str(self.fixture.path)]
        bad = ([], ["--in", str(self.fixture.path)], ["--input"], ["--input", ""],
               good + ["--output", ""], good + ["--input", str(self.fixture.path)],
               good + ["--input=" + str(self.fixture.path)],
               good + ["--output", "one.json", "--output=two.json"],
               good + ["--gain", "1"], good + ["--role", "fit"],
               good + ["--corpus", "replacement.json"], good + ["--bound", "1"],
               good + ["--alignment", "automatic"], good + ["--unknown"])
        for flags in bad:
            with self.subTest(flags=flags):
                code, stdout, stderr = self.main(flags)
                self.assertEqual(code, 2, stderr)
                self.assertEqual(stdout, b"")
                self.assertTrue(stderr)
        code, stdout, stderr = self.main(["--help"])
        self.assertEqual(code, 0)
        self.assertIn(b"--input", stdout)
        self.assertEqual(stderr, "")

    def test_exact_argv_types_reject_without_leaking_parser_exceptions(self):
        class ListSubclass(list):
            pass
        class StringSubclass(str):
            pass
        for value in ("--help", ("--help",), ListSubclass(["--help"]), [Path("--help")],
                      [True], [StringSubclass("--help")], 5):
            with self.subTest(value=type(value).__name__):
                code, stdout, stderr = self.main(value)
                self.assertEqual(code, 2, stderr)
                self.assertEqual(stdout, b"")
                self.assertTrue(stderr)

    def test_valid_failed_and_inconclusive_files_equal_stdout(self):
        for status_value, exit_code in (("failed", 1), ("inconclusive", 3)):
            fixture = self.fixture_at("publish-" + status_value, (status_value,))
            target = self.work / (status_value + ".json")
            code, stdout, stderr = self.main(["--input", str(fixture.path), "--output", str(target)])
            self.assertEqual(code, exit_code)
            self.assertEqual(stderr, "")
            self.assertEqual(target.read_bytes(), stdout)
            self.assertEqual(json.loads(stdout)["status"], status_value)
            self.assertEqual(list(self.work.glob(".capture-json-*")), [])

    def test_existing_file_directory_and_input_are_preserved(self):
        existing = self.work / "existing.json"
        existing.write_bytes(b"Preserve this exact result.\n")
        directory = self.work / "existing-directory"
        directory.mkdir()
        targets = [existing, directory, self.fixture.path]
        original_study = self.fixture.path.read_bytes()
        for target in targets:
            with self.subTest(target=target.name):
                code, stdout, stderr = self.main(["--input", str(self.fixture.path), "--output", str(target)])
                self.assertEqual(code, 1)
                self.assertEqual(stdout, b"")
                self.assertTrue(stderr.startswith("study error:"), stderr)
                self.assertEqual(self.fixture.path.read_bytes(), original_study)
                self.assertEqual(existing.read_bytes(), b"Preserve this exact result.\n")
                self.assertTrue(directory.is_dir())
        self.assertEqual(list(self.work.glob(".capture-json-*")), [])

    def test_native_hardlink_input_alias_is_preserved(self):
        target = self.work / "hardlinked-study.json"
        try:
            os.link(self.fixture.path, target)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"native hardlink creation unavailable: {error}")
        self.assertTrue(os.path.samefile(self.fixture.path, target))
        original = self.fixture.path.read_bytes()
        code, stdout, stderr = self.main(["--input", str(self.fixture.path), "--output", str(target)])
        self.assertEqual(code, 1)
        self.assertEqual(stdout, b"")
        self.assertTrue(stderr.startswith("study error:"), stderr)
        self.assertEqual(self.fixture.path.read_bytes(), original)
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(list(self.work.glob(".capture-json-*")), [])

    def test_native_dangling_output_link_is_preserved(self):
        target = self.work / "dangling.json"
        absent = self.work / "absent.json"
        try:
            target.symlink_to(absent)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"native symlink creation unavailable: {error}")
        code, stdout, stderr = self.main(["--input", str(self.fixture.path), "--output", str(target)])
        self.assertEqual(code, 1)
        self.assertEqual(stdout, b"")
        self.assertTrue(stderr.startswith("study error:"), stderr)
        self.assertTrue(target.is_symlink())
        self.assertFalse(target.exists())
        self.assertFalse(absent.exists())
        self.assertEqual(list(self.work.glob(".capture-json-*")), [])

    def test_missing_parent_is_not_created(self):
        destination = self.work / "absent-parent/report.json"
        code, stdout, stderr = self.main(["--input", str(self.fixture.path), "--output", str(destination)])
        self.assertEqual(code, 1)
        self.assertEqual(stdout, b"")
        self.assertTrue(stderr.startswith("study error:"), stderr)
        self.assertFalse(destination.parent.exists())

    def test_publication_precedes_stdout_and_raced_destination_wins(self):
        destination = self.work / "ordered.json"
        real_publish = capture_common.write_json_new
        real_stream = subject._write_stream
        published = []
        def publish(*args, **kwargs):
            result = real_publish(*args, **kwargs)
            published.append(True)
            return result
        def stream(output, payload, label):
            if output is sys.stdout:
                self.assertEqual(published, [True])
            return real_stream(output, payload, label)
        with mock.patch.object(capture_common, "write_json_new", side_effect=publish), \
             mock.patch.object(subject, "_write_stream", side_effect=stream):
            code, stdout, stderr = self.main(["--input", str(self.fixture.path), "--output", str(destination)])
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
        self.assertEqual(destination.read_bytes(), stdout)
        race_target = self.work / "raced.json"
        original_link = os.link
        reached = []
        def race(source, target, *args, **kwargs):
            if Path(target).resolve() == race_target:
                reached.append(True)
                race_target.write_bytes(b"The concurrent destination wins.")
            return original_link(source, target, *args, **kwargs)
        with mock.patch.object(os, "link", side_effect=race):
            code, stdout, stderr = self.main(["--input", str(self.fixture.path), "--output", str(race_target)])
        self.assertEqual(reached, [True])
        self.assertEqual(code, 1)
        self.assertEqual(stdout, b"")
        self.assertTrue(stderr.startswith("study error:"), stderr)
        self.assertEqual(race_target.read_bytes(), b"The concurrent destination wins.")
        self.assertEqual(list(self.work.glob(".capture-json-*")), [])

    def test_completed_publication_cleanup_failure_is_disclosed_and_preserved(self):
        destination = self.work / "published-before-cleanup-error.json"
        original = Path.unlink
        reached = []
        def cleanup(path, *args, **kwargs):
            if path.name.startswith(".capture-json-"):
                reached.append(path)
                original(path, *args, **kwargs)
                raise OSError("injected cleanup failure after real unlink")
            return original(path, *args, **kwargs)
        with mock.patch.object(Path, "unlink", autospec=True, side_effect=cleanup):
            code, stdout, stderr = self.main(["--input", str(self.fixture.path), "--output", str(destination)])
        self.assertEqual(len(reached), 1)
        self.assertEqual(code, 1)
        self.assertEqual(stdout, b"")
        self.assertIn("published", stderr)
        self.assertIn("cleanup", stderr)
        self.assertEqual(json.loads(destination.read_bytes())["status"], "pass")
        self.assertEqual(list(self.work.glob(".capture-json-*")), [])

    def test_stdout_failure_after_publication_preserves_the_complete_file(self):
        class BrokenStdout:
            def write(self, value):
                raise OSError("injected stdout failure")
            def flush(self):
                raise OSError("injected stdout flush failure")
        destination = self.work / "published-before-stream-error.json"
        stderr = io.StringIO()
        with mock.patch.object(sys, "stdout", BrokenStdout()), mock.patch.object(sys, "stderr", stderr):
            code = subject.main(["--input", str(self.fixture.path), "--output", str(destination)])
        self.assertEqual(code, 1)
        self.assertIn("stdout", stderr.getvalue())
        self.assertEqual(json.loads(destination.read_bytes())["status"], "pass")

    def test_short_stdout_and_failed_stderr_or_help_never_return_success(self):
        class ShortStdout(io.BytesIO):
            @property
            def buffer(self):
                return self
            def write(self, value):
                return super().write(value[:11])
        stream = ShortStdout()
        stderr = io.StringIO()
        with mock.patch.object(sys, "stdout", stream), mock.patch.object(sys, "stderr", stderr):
            code = subject.main(["--input", str(self.fixture.path)])
        self.assertEqual(code, 1)
        self.assertEqual(len(stream.getvalue()), 11)
        self.assertIn("stdout", stderr.getvalue())
        class BrokenStream:
            def write(self, value):
                raise OSError("injected unavailable stream")
            def flush(self):
                raise OSError("injected unavailable stream")
        with mock.patch.object(sys, "stderr", BrokenStream()):
            self.assertNotEqual(subject.main(["--input", str(self.work / "missing.json")]), 0)
        with mock.patch.object(sys, "stdout", BrokenStream()), mock.patch.object(sys, "stderr", io.StringIO()):
            self.assertNotEqual(subject.main(["--help"]), 0)

    def test_cancellation_propagates_without_report_or_publication(self):
        destination = self.work / "cancelled.json"
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.object(capture_job, "_run_bound_job", side_effect=KeyboardInterrupt("cancel")) as core, \
             mock.patch.object(sys, "stdout", stdout), mock.patch.object(sys, "stderr", stderr):
            with self.assertRaises(KeyboardInterrupt):
                subject.main(["--input", str(self.fixture.path), "--output", str(destination)])
        self.assertEqual(core.call_count, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")
        self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
