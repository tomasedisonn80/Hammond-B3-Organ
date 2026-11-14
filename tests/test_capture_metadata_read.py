#!/usr/bin/env python3
"""Independent acceptance of descriptor-sized confined metadata reads.

The oracles are original private-file bytes, literal admission boundaries and
observed fault events. No production file is modified. Existing admission suites
retain the broader JSON, alias, platform and publication matrix.
"""

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import capture_corpus
import capture_job


MODULES = (
    "capture_audio", "capture_common", "capture_corpus", "capture_job",
    "capture_readiness", "capture_study", "compare_capture", "make_capture_demo",
    "validate_capture", "verify_capture_report",
)
CLAIMS = (
    "boundary_equivalence", "synchronization", "authenticity", "specimen_identity",
    "calibration", "permissions", "independence", "preregistration",
    "final_holdout_history", "physical_fidelity",
)


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


def inventory(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file()}


def leaf_stamp(path):
    info = path.stat()
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


class ObservedStream:
    """Own a real stream and record the one metadata read without replacing I/O."""

    def __init__(self, stream, *, before_read=None, after_read=None, after_close=None):
        self.stream = stream
        self.before_read = before_read
        self.after_read = after_read
        self.after_close = after_close
        self.requests = []
        self.responses = []
        self.descriptor = stream.fileno()

    def __enter__(self):
        self.stream.__enter__()
        return self

    def __exit__(self, *args):
        result = self.stream.__exit__(*args)
        if self.after_close is not None:
            self.after_close()
        return result

    def fileno(self):
        return self.stream.fileno()

    def read(self, size=-1):
        self.requests.append(size)
        if self.before_read is not None:
            self.before_read()
        payload = self.stream.read(size)
        if self.after_read is not None:
            payload = self.after_read(payload)
        self.responses.append(payload)
        return payload


class MetadataReadAcceptance(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="capture-metadata-")
        self.addCleanup(temporary.cleanup)
        # Match real roots on systems where TEMP itself contains an OS alias.
        self.work = Path(temporary.name).resolve(strict=True)
        self.root = self.work / "archive"
        self.parent = self.root / "metadata"
        self.parent.mkdir(parents=True)
        self.path = self.parent / "original.json"
        self.payload = b'{ "unmodified" : "caf\xc3\xa9", "values" : [3, 1, 2] }\r\n  '
        self.path.write_bytes(self.payload)

    def read(self, ceiling=16_777_216):
        return capture_corpus._read_confined_bytes(
            self.root, ["metadata", "original.json"], max_bytes=ceiling)

    @contextmanager
    def observe(self, *, on_wrap=None, **actions):
        original = capture_corpus._stream
        seen = []

        def wrap(descriptor):
            stream = ObservedStream(original(descriptor), **actions)
            seen.append(stream)
            if on_wrap is not None:
                on_wrap()
            return stream

        with mock.patch.object(capture_corpus, "_stream", wrap):
            yield seen
        self.assertEqual(len(seen), 1, "the actual metadata stream must be reached")
        self.assertTrue(seen[0].stream.closed, "the real stream must be closed")
        with self.assertRaises(OSError):
            os.fstat(seen[0].descriptor)

    def reject(self, operation=None, contains="changed"):
        with self.assertRaises(capture_corpus.CorpusError) as caught:
            (operation or self.read)()
        self.assertIn(contains, str(caught.exception))
        return caught.exception

    def append(self, suffix):
        with self.path.open("ab") as writer:
            writer.write(suffix)

    def changed_mtime(self):
        before = self.path.stat()
        os.utime(self.path, ns=(before.st_atime_ns,
                               before.st_mtime_ns + 2_000_000_000))
        self.assertNotEqual(self.path.stat().st_mtime_ns, before.st_mtime_ns,
                            "the metadata mutation must be observable")

    def test_original_bytes_hash_and_descriptor_bound_ignore_looser_ceiling(self):
        for payload in (b"", b"\x00", self.payload, bytes(range(256)) * 32):
            self.path.write_bytes(payload)
            for ceiling in (len(payload), len(payload) + 23, 16_777_216):
                with self.subTest(length=len(payload), ceiling=ceiling):
                    snapshots = capture_job._Snapshots()
                    with self.observe() as seen:
                        result, observed = capture_job._read_observed(
                            self.root, ["metadata", "original.json"],
                            max_bytes=ceiling, snapshots=snapshots)
                    self.assertEqual(result, payload)
                    self.assertEqual(observed, {"size_bytes": len(payload),
                                                "sha256": digest(payload)})
                    self.assertEqual(seen[0].requests, [len(payload) + 1])
                    self.assertEqual(seen[0].responses, [payload])
                    snapshots.verify()
                    self.assertEqual(self.path.read_bytes(), payload)

    def test_one_byte_over_cap_rejects_before_opening_any_descriptor(self):
        for payload, ceiling in ((b"x", 0), (self.payload, len(self.payload) - 1)):
            self.path.write_bytes(payload)
            with self.subTest(ceiling=ceiling), mock.patch.object(
                    capture_corpus, "_open_confined",
                    side_effect=AssertionError("over-cap metadata was opened")) as opening:
                self.reject(lambda: self.read(ceiling), "input byte limit exceeded")
                opening.assert_not_called()
            self.assertEqual(self.path.read_bytes(), payload)

    def test_growth_between_path_and_descriptor_admission_uses_descriptor_size(self):
        reached = []

        def grow():
            self.append(b"extra")
            reached.append(self.path.stat().st_size)

        with self.observe(on_wrap=grow) as seen:
            self.reject()
        self.assertEqual(reached, [len(self.payload) + 5])
        self.assertEqual(seen[0].requests, [len(self.payload) + 6])
        self.assertEqual(seen[0].responses, [self.payload + b"extra"])

    def test_descriptor_growth_over_cap_rejects_before_read(self):
        reached = []

        def grow():
            self.append(b"!")
            reached.append(True)

        with self.observe(on_wrap=grow) as seen:
            self.reject(lambda: self.read(len(self.payload)), "opened input byte limit exceeded")
        self.assertEqual(reached, [True])
        self.assertEqual(seen[0].requests, [])

    def test_extra_byte_detects_growth_even_under_a_loose_admitted_cap(self):
        for ceiling in (len(self.payload), 16_777_216):
            self.path.write_bytes(self.payload)
            reached = []

            def grow():
                self.append(b"new bytes")
                reached.append(True)

            with self.subTest(ceiling=ceiling), self.observe(before_read=grow) as seen:
                self.reject(lambda: self.read(ceiling), "input size changed")
            self.assertEqual(reached, [True])
            self.assertEqual(seen[0].requests, [len(self.payload) + 1])
            self.assertEqual(seen[0].responses, [self.payload + b"n"])

    def test_growth_after_consumption_rejects_even_when_returned_length_matches(self):
        reached = []

        def grow(payload):
            self.append(b"!")
            reached.append(True)
            return payload

        with self.observe(after_read=grow) as seen:
            self.reject()
        self.assertEqual(reached, [True])
        self.assertEqual(seen[0].responses, [self.payload])

    def test_actual_truncation_after_admission_rejects(self):
        reached = []

        def truncate():
            self.path.write_bytes(self.payload[:-1])
            reached.append(self.path.stat().st_size)

        with self.observe(before_read=truncate) as seen:
            self.reject(contains="input size changed")
        self.assertEqual(reached, [len(self.payload) - 1])
        self.assertEqual(seen[0].responses, [self.payload[:-1]])

    def test_short_stream_result_rejects_without_fabricating_full_bytes(self):
        reached = []

        def shorten(payload):
            reached.append(payload)
            return payload[:-1]

        with self.observe(after_read=shorten):
            self.reject(contains="input size changed")
        self.assertEqual(reached, [self.payload])
        self.assertEqual(self.path.read_bytes(), self.payload)

    def test_same_size_content_change_rejects_at_descriptor_recheck(self):
        reached = []

        def change(payload):
            self.path.write_bytes(b"!" + self.payload[1:])
            self.changed_mtime()
            reached.append(True)
            return payload

        with self.observe(after_read=change) as seen:
            self.reject()
        self.assertEqual(reached, [True])
        self.assertEqual(seen[0].responses, [self.payload])
        self.assertEqual(self.path.stat().st_size, len(self.payload))

    def test_metadata_only_change_after_close_rejects_final_path_check(self):
        reached = []

        def change():
            self.changed_mtime()
            reached.append(True)

        with self.observe(after_close=change) as seen:
            self.reject()
        self.assertEqual(reached, [True])
        self.assertEqual(seen[0].responses, [self.payload])
        self.assertEqual(self.path.read_bytes(), self.payload)

    def test_replacement_between_path_observation_and_open_rejects_before_read(self):
        replacement = self.parent / "replacement.json"
        replacement.write_bytes(self.payload)
        before = self.path.stat()
        opening = capture_corpus._open_confined
        reached = []

        def replace(*args):
            replacement.replace(self.path)
            after = self.path.stat()
            self.assertNotEqual((before.st_dev, before.st_ino),
                                (after.st_dev, after.st_ino))
            reached.append(True)
            return opening(*args)

        with mock.patch.object(capture_corpus, "_open_confined", replace), \
                self.observe() as seen:
            self.reject(contains="identity mismatch")
        self.assertEqual(reached, [True])
        self.assertEqual(seen[0].requests, [])
        self.assertEqual(self.path.read_bytes(), self.payload)

    def test_same_bytes_leaf_replacement_after_close_rejects(self):
        replacement = self.parent / "replacement.json"
        replacement.write_bytes(self.payload)
        reached = []

        def replace():
            replacement.replace(self.path)
            reached.append(True)

        with self.observe(after_close=replace) as seen:
            self.reject()
        self.assertEqual(reached, [True])
        self.assertEqual(seen[0].responses, [self.payload])
        self.assertEqual(self.path.read_bytes(), self.payload)

    def test_changed_parent_identity_rejects_even_with_the_same_leaf_inode(self):
        # Precreate the hard link before admission: link-count metadata is then
        # stable, and directory swaps leave the leaf's entire stamp unchanged.
        alternate = self.root / "alternate"
        alternate.mkdir()
        try:
            os.link(self.path, alternate / self.path.name)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"native hardlink capability unavailable: {error}")
        before = leaf_stamp(self.path)
        reached = []

        def replace():
            self.parent.rename(self.root / "previous-parent")
            alternate.rename(self.parent)
            self.assertEqual(leaf_stamp(self.path), before)
            reached.append(True)

        with self.observe(after_close=replace):
            self.reject(contains="directory replaced")
        self.assertEqual(reached, [True])

    def test_changed_root_identity_rejects_even_with_the_same_leaf_inode(self):
        alternate = self.work / "alternate-root"
        (alternate / "metadata").mkdir(parents=True)
        try:
            os.link(self.path, alternate / "metadata" / self.path.name)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"native hardlink capability unavailable: {error}")
        before = leaf_stamp(self.path)
        reached = []

        def replace():
            self.root.rename(self.work / "previous-root")
            alternate.rename(self.root)
            self.assertEqual(leaf_stamp(self.path), before)
            reached.append(True)

        with self.observe(after_close=replace):
            self.reject(contains="directory replaced")
        self.assertEqual(reached, [True])

    def test_unrelated_sibling_creation_preserves_exact_metadata_bytes(self):
        reached = []

        def sibling():
            (self.parent / "unrelated.txt").write_bytes(b"not part of this read")
            reached.append(True)

        with self.observe(after_close=sibling):
            self.assertEqual(self.read(), self.payload)
        self.assertEqual(reached, [True])

    def test_shared_snapshot_retains_first_observation_after_read_returns(self):
        snapshots = capture_job._Snapshots()
        result, observed = capture_job._read_observed(
            self.root, ["metadata", "original.json"],
            max_bytes=16_777_216, snapshots=snapshots)
        self.assertEqual(result, self.payload)
        self.assertEqual(observed["sha256"], digest(self.payload))
        self.changed_mtime()
        self.reject(snapshots.verify)
        self.assertEqual(self.path.read_bytes(), self.payload)

    def test_read_error_and_cancellation_keep_primary_exception_and_close_stream(self):
        for primary in (OSError("primary read failure"), KeyboardInterrupt("cancel read"),
                        SystemExit("stop read")):
            reached = []

            def fail():
                reached.append(True)
                raise primary

            with self.subTest(exception=type(primary).__name__), \
                    self.observe(before_read=fail) as seen:
                with self.assertRaises(type(primary)) as caught:
                    self.read()
            self.assertIs(caught.exception, primary)
            self.assertEqual(reached, [True])
            self.assertEqual(seen[0].requests, [len(self.payload) + 1])
            self.assertEqual(self.path.read_bytes(), self.payload)

    def test_close_failure_cannot_be_reported_as_a_successful_read(self):
        primary = OSError("real stream closed; injected close failure")
        reached = []

        def fail():
            reached.append(True)
            raise primary

        with self.observe(after_close=fail):
            with self.assertRaises(OSError) as caught:
                self.read()
        self.assertIs(caught.exception, primary)
        self.assertEqual(reached, [True])
        self.assertEqual(self.path.read_bytes(), self.payload)

    def check_failed_wrap(self, primary, cleanup_fails):
        opening, closing = capture_corpus._open_confined, os.close
        leaves, wraps, cleanups = [], [], []

        def open_leaf(*args):
            descriptor = opening(*args)
            leaves.append(descriptor)
            return descriptor

        def failed_wrap(descriptor, *args, **kwargs):
            wraps.append(descriptor)
            raise primary

        def close(descriptor):
            closing(descriptor)
            if descriptor in leaves:
                cleanups.append(descriptor)
                if cleanup_fails:
                    raise OSError("secondary cleanup failure after actual close")

        expected = (capture_corpus.CorpusError if cleanup_fails
                    and isinstance(primary, Exception) else type(primary))
        with mock.patch.object(capture_corpus, "_open_confined", open_leaf), \
                mock.patch.object(os, "fdopen", failed_wrap), \
                mock.patch.object(os, "close", close):
            with self.assertRaises(expected) as caught:
                self.read()
        self.assertEqual(len(leaves), 1)
        self.assertEqual(wraps, leaves, "the failed wrapper must receive the actual leaf")
        self.assertEqual(cleanups, leaves, "the owned leaf must be closed once")
        with self.assertRaises(OSError):
            os.fstat(leaves[0])
        self.assertIn(str(primary), str(caught.exception))
        if cleanup_fails and isinstance(primary, Exception):
            self.assertIn("secondary cleanup failure", str(caught.exception))
            self.assertIs(caught.exception.__cause__, primary)
        else:
            self.assertIs(caught.exception, primary)
        if cleanup_fails and not isinstance(primary, Exception):
            self.assertIn("secondary cleanup failure", str(primary.__cause__))
        self.assertEqual(self.path.read_bytes(), self.payload)

    def test_failed_stream_construction_releases_leaf_and_preserves_primary(self):
        self.check_failed_wrap(OSError("primary wrapper failure"), False)

    def test_wrapper_and_cleanup_failures_retain_both_reasons(self):
        self.check_failed_wrap(OSError("primary wrapper failure"), True)

    def test_cancellation_survives_failed_wrapper_cleanup(self):
        for primary in (KeyboardInterrupt("cancel wrapper"), SystemExit("stop wrapper")):
            with self.subTest(exception=type(primary).__name__):
                self.check_failed_wrap(primary, True)


class MetadataPipelineAcceptance(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="metadata-pipeline-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name).resolve(strict=True)
        self.archive = self.work / "demo"
        shutil.copytree(ROOT / "examples" / "capture-demo", self.archive)
        self.original = inventory(self.archive)
        self.original_sources = {name: (ROOT / "tools" / (name + ".py")).read_bytes()
                                 for name in MODULES}

    def tearDown(self):
        self.assertEqual(inventory(self.archive), self.original)
        self.assertEqual({name: (ROOT / "tools" / (name + ".py")).read_bytes()
                          for name in MODULES}, self.original_sources)

    def invoke(self, name, arguments, *, tools=None, expected=0):
        tools = tools or ROOT / "tools"
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        for key in ("PYTHONPATH", "PYTHONHOME"):
            environment.pop(key, None)
        result = subprocess.run([sys.executable, "-B", "-S", str(tools / (name + ".py")),
                                 *map(str, arguments)], cwd=self.work, env=environment,
                                capture_output=True, check=False, timeout=30)
        self.assertEqual(result.returncode, expected,
                         (result.stdout + result.stderr).decode("utf-8", "replace"))
        self.assertEqual(result.stderr, b"")
        value = json.loads(result.stdout)
        self.assertEqual(result.stdout, canonical(value))
        return value, result.stdout

    def assert_unknown(self, report):
        for name in CLAIMS:
            self.assertEqual(report[name], "not_established")

    def test_fresh_jobs_and_replays_preserve_all_three_engineering_outcomes(self):
        for filename, status, exit_code, error in (
                ("job-pass.json", "pass", 0, 0.25),
                ("job-inconclusive.json", "inconclusive", 3, 0.25),
                ("job-fail.json", "failed", 1, 0.5)):
            with self.subTest(status=status):
                path = self.archive / filename
                report, payload = self.invoke("capture_job", ["--input", path],
                                              expected=exit_code)
                self.assertEqual(report["status"], status)
                self.assertEqual(report["evaluation"]["comparison"]["channels"][0]
                                 ["metrics"]["rms_error_fs"]["value"], error)
                self.assert_unknown(report)
                saved = self.work / (status + ".json")
                saved.write_bytes(payload)
                summary, _ = self.invoke("verify_capture_report", [
                    "--kind", "job", "--input", path, "--report", saved])
                self.assertEqual(summary["status"], "match")
                self.assertTrue(summary["exact_report_match"])
                self.assertEqual(summary["saved_engineering_status"], status)
                self.assertEqual(summary["replayed_engineering_status"], status)
                self.assertEqual(summary["saved_report"],
                                 {"size_bytes": len(payload), "sha256": digest(payload)})
                self.assertEqual(summary["saved_report"], summary["replayed_report"])
                self.assertTrue(summary["context"]["same_runtime"])
                self.assertTrue(summary["context"]["same_tool_sources"])
                self.assert_unknown(summary)
                self.assertEqual(saved.read_bytes(), payload)

    def test_fresh_study_replay_retains_failed_and_inconclusive_nested_reports(self):
        path = self.archive / "study.json"
        report, payload = self.invoke("capture_study", ["--input", path], expected=1)
        self.assertEqual(report["status"], "failed")
        self.assertEqual([job["report"]["status"] for job in report["jobs"]],
                         ["pass", "inconclusive", "failed"])
        self.assert_unknown(report)
        for job in report["jobs"]:
            self.assert_unknown(job["report"])
        saved = self.work / "study-report.json"
        saved.write_bytes(payload)
        summary, _ = self.invoke("verify_capture_report", [
            "--kind", "study", "--input", path, "--report", saved])
        self.assertEqual(summary["status"], "match")
        self.assertTrue(summary["exact_report_match"])
        self.assertEqual(summary["saved_engineering_status"], "failed")
        self.assertEqual(summary["replayed_engineering_status"], "failed")
        self.assertEqual(summary["saved_report"], summary["replayed_report"])
        self.assert_unknown(summary)
        self.assertEqual(saved.read_bytes(), payload)

    def test_private_changed_source_reports_mismatch_without_rewriting_saved_report(self):
        # Two fresh interpreters observe actual copied source bytes. The fixture
        # edit is a harmless comment, never a mutation of a loaded/repository module.
        tools = self.work / "private-tools"
        tools.mkdir()
        for name, payload in self.original_sources.items():
            (tools / (name + ".py")).write_bytes(payload)
        path = self.archive / "study.json"
        old, saved_bytes = self.invoke("capture_study", ["--input", path],
                                       tools=tools, expected=1)
        saved = self.work / "original-saved-report.json"
        saved.write_bytes(saved_bytes)
        old_corpus = self.original_sources["capture_corpus"]
        changed = old_corpus + b"\n# Private acceptance fixture: changed source identity.\n"
        (tools / "capture_corpus.py").write_bytes(changed)
        summary, _ = self.invoke("verify_capture_report", [
            "--kind", "study", "--input", path, "--report", saved],
            tools=tools, expected=1)
        self.assertEqual(summary["status"], "mismatch")
        self.assertFalse(summary["exact_report_match"])
        self.assertTrue(summary["context"]["same_runtime"])
        self.assertFalse(summary["context"]["same_tool_sources"])
        self.assertEqual(summary["saved_engineering_status"], "failed")
        self.assertEqual(summary["replayed_engineering_status"], "failed")
        self.assertEqual(summary["saved_report"],
                         {"size_bytes": len(saved_bytes), "sha256": digest(saved_bytes)})
        saved_sources = {row["module"]: row for row in old["tool_sources"]}
        new_sources = {row["module"]: row
                       for row in summary["context"]["replayed_tool_sources"]}
        self.assertEqual(saved_sources["capture_corpus.py"]["sha256"], digest(old_corpus))
        self.assertEqual(new_sources["capture_corpus.py"], {
            "module": "capture_corpus.py", "size_bytes": len(changed), "sha256": digest(changed)})
        self.assertEqual({k: v for k, v in saved_sources.items() if k != "capture_corpus.py"},
                         {k: v for k, v in new_sources.items() if k != "capture_corpus.py"})
        self.assert_unknown(summary)
        self.assertEqual(saved.read_bytes(), saved_bytes)
        self.assertEqual(inventory(tools), {
            name + ".py": changed if name == "capture_corpus" else payload
            for name, payload in self.original_sources.items()})


if __name__ == "__main__":
    unittest.main()
