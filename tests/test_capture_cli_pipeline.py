#!/usr/bin/env python3
"""Independent real-process capture CLI delivery and preservation acceptance.

These tests close a real pipe's read end before child launch. They qualify the
actual interpreter exit, including its final flush, rather than replacing a
Python stream object. All sources and fixtures used by children are private.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULES = (
    "capture_audio", "capture_common", "capture_corpus", "capture_job",
    "capture_readiness", "capture_study", "compare_capture", "make_capture_demo",
    "validate_capture", "verify_capture_report",
)
CLIS = (
    "capture_audio", "capture_corpus", "capture_job", "capture_readiness",
    "capture_study", "verify_capture_report", "make_capture_demo", "validate_capture",
)
WRITERS = ("capture_readiness", "capture_job", "capture_study", "verify_capture_report")
MARKER = "Independent Unicode declaration: Ω — 東京."


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical(value) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


def inventory(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): (len(p.read_bytes()), digest(p.read_bytes()))
            for p in sorted(root.rglob("*")) if p.is_file() and not p.is_symlink()}


class CaptureCliPipeline(unittest.TestCase):
    observations = []

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="capture-cli-process-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name).resolve() / "private Ω 東京"
        cls.root.mkdir()
        cls.tools = cls.root / "tools"
        cls.tools.mkdir()
        before = {name: (ROOT / "tools" / (name + ".py")).read_bytes() for name in MODULES}
        for name, payload in before.items():
            (cls.tools / (name + ".py")).write_bytes(payload)
        if before != {name: (ROOT / "tools" / (name + ".py")).read_bytes() for name in MODULES}:
            raise AssertionError("Production sources changed while copying private closure")
        cls.tool_inventory = inventory(cls.tools)
        cls.source_context = {name + ".py": {"size_bytes": len(payload), "sha256": digest(payload)}
                              for name, payload in before.items()}
        cls.foreign = cls.root / "foreign working directory"
        cls.foreign.mkdir()
        cls.outputs = cls.root / "reports"
        cls.outputs.mkdir()
        cls.archive = cls.root / "archive Ω"
        cls.environment = dict(os.environ, PYTHONIOENCODING="ascii:strict")
        cls.observations = []
        generated = cls.invoke("make_capture_demo", ["--output", cls.archive], "setup-demo")
        cls.require_exit(generated, 0)
        cls.original_demo_inventory = inventory(cls.archive)
        cls.generated_inventory = generated.stdout
        # Keep the literal numerical inputs and thresholds unchanged. Unicode
        # rationale text deliberately tests real bytes through an ASCII terminal.
        study_path = cls.archive / "study.json"
        study = json.loads(study_path.read_bytes())
        for label, entry in zip(("pass", "inconclusive", "fail"), study["jobs"]):
            policy_path = cls.archive / f"policy-{label}.json"
            policy = json.loads(policy_path.read_bytes())
            policy["criteria"][0]["rationale"] += " " + MARKER
            policy_path.write_bytes(canonical(policy))
            job_path = cls.archive / f"job-{label}.json"
            job = json.loads(job_path.read_bytes())
            job["policy"]["sha256"] = digest(policy_path.read_bytes())
            job_path.write_bytes(canonical(job))
            entry["sha256"] = digest(job_path.read_bytes())
        study_path.write_bytes(canonical(study))
        cls.plan = cls.root / "planned Ω.json"
        plan = json.loads((ROOT / "data/capture-planned-example.json").read_bytes())
        plan["stimulus"]["description"]["value"] += " " + MARKER
        cls.plan.write_bytes(canonical(plan))
        cls.input_inventory = inventory(cls.archive)
        cls.plan_bytes = cls.plan.read_bytes()
        cls.controls = {}
        cls.saved = {}
        ordinary = (
            ("readiness", "capture_readiness", 3),
            ("corpus", "capture_corpus", 0),
            ("audio", "capture_audio", 0),
            ("validation", "validate_capture", 0),
            ("job-pass", "capture_job", 0),
            ("job-inconclusive", "capture_job", 3),
            ("job-fail", "capture_job", 1),
            ("study", "capture_study", 1),
        )
        for label, module, expected in ordinary:
            target = cls.outputs / ("control-" + label + ".json") if module in WRITERS else None
            result = cls.invoke(module, cls.success_args(module, target, label), "ordinary-" + label)
            cls.require_exit(result, expected)
            if result.stderr:
                raise AssertionError(result.stderr.decode("utf-8", "replace"))
            cls.controls[label] = result.stdout
            if target is not None:
                if target.read_bytes() != result.stdout:
                    raise AssertionError("Published control differs from actual stdout")
                cls.saved[label] = target
        for label in ("job-pass", "job-inconclusive", "job-fail", "study"):
            target = cls.outputs / ("control-replay-" + label + ".json")
            result = cls.invoke("verify_capture_report", cls.replay_args(label, target),
                                "ordinary-replay-" + label)
            cls.require_exit(result, 0)
            if result.stderr or target.read_bytes() != result.stdout:
                raise AssertionError("Replay control did not publish exactly its quiet stdout")
            cls.controls["replay-" + label] = result.stdout
        cls.output_inventory = inventory(cls.outputs)

    @staticmethod
    def require_exit(result, expected):
        if result.returncode != expected:
            raise AssertionError(f"Expected exit {expected}, observed {result.returncode}: "
                                 + (result.stderr or b"").decode("utf-8", "replace"))

    @classmethod
    def invoke(cls, module, args, label, closed=None, script_path=None):
        command = [sys.executable, "-B", "-S", str(script_path or cls.tools / (module + ".py")),
                   *map(str, args)]
        kwargs = dict(stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                      cwd=cls.foreign, env=cls.environment, check=False, timeout=30)
        if script_path is not None:
            kwargs["env"] = dict(cls.environment, PYTHONPATH="")
        writer = None
        if closed is not None:
            reader, writer = os.pipe()
            os.close(reader)
            kwargs[closed] = writer
        try:
            result = subprocess.run(command, **kwargs)
        finally:
            if writer is not None:
                os.close(writer)
        cls.observations.append({
            "label": label, "module": module, "argv": command, "closed_stream": closed,
            "returncode": result.returncode,
            "stdout_size": None if result.stdout is None else len(result.stdout),
            "stdout_sha256": None if result.stdout is None else digest(result.stdout),
            "stderr": None if result.stderr is None else result.stderr.decode("utf-8", "replace"),
        })
        return result

    @classmethod
    def replay_args(cls, label="study", output=None):
        kind = "study" if label == "study" else "job"
        args = ["--kind", kind, "--input", cls.archive / (label + ".json"),
                "--report", cls.saved[label]]
        return args + (["--output", output] if output is not None else [])

    @classmethod
    def success_args(cls, module, output=None, label=None):
        if module == "capture_audio":
            args = ["--input", cls.archive / "corpus/audio/reference.f32", "--raw-format",
                    "raw_float32_le", "--sample-rate-hz", "4", "--channel-count", "1"]
        elif module == "capture_corpus":
            args = ["--input", cls.archive / "corpus/corpus.json", "--check-files", "--check-audio"]
        elif module == "validate_capture":
            args = ["--input", cls.archive / "corpus/reference.json", "--check-files"]
        elif module == "capture_readiness":
            args = ["--input", cls.plan]
        elif module == "capture_job":
            args = ["--input", cls.archive / ((label or "job-pass") + ".json")]
        elif module == "capture_study":
            args = ["--input", cls.archive / "study.json"]
        elif module == "verify_capture_report":
            return cls.replay_args("study", output)
        else:
            return ["--output", output]
        return args + (["--output", output] if output is not None and module in WRITERS else [])

    def assert_inputs_preserved(self):
        self.assertEqual(inventory(self.archive), self.input_inventory)
        self.assertEqual(self.plan.read_bytes(), self.plan_bytes)
        self.assertEqual(inventory(self.tools), self.tool_inventory)
        for relative, identity in self.output_inventory.items():
            payload = (self.outputs / relative).read_bytes()
            self.assertEqual((len(payload), digest(payload)), identity)

    def test_ordinary_pipeline_retains_literal_outcomes_and_utf8_bytes(self):
        self.assertEqual(len(self.controls), 12)
        for label, payload in self.controls.items():
            with self.subTest(label=label):
                self.assertTrue(payload.endswith(b"\n"))
                if label != "validation":
                    self.assertNotIn(b"\r", payload)
                value = json.loads(payload)
                if label == "audio":
                    expected = (json.dumps(value, sort_keys=True, separators=(",", ":"),
                                           ensure_ascii=True, allow_nan=False) + "\n").encode()
                elif label == "validation":
                    # Legacy v1 keeps its native text newline convention.
                    expected = (json.dumps(value, sort_keys=True, allow_nan=False) + os.linesep).encode()
                else:
                    expected = canonical(value)
                self.assertEqual(payload, expected)
        self.assertEqual(json.loads(self.controls["readiness"])["status"], "planned")
        self.assertIn(MARKER.encode("utf-8"), self.controls["readiness"])
        self.assertEqual(json.loads(self.controls["corpus"])["status"], "pass")
        for label, status, rms in (("job-pass", "pass", .25),
                                   ("job-inconclusive", "inconclusive", .25),
                                   ("job-fail", "failed", .5)):
            value = json.loads(self.controls[label])
            self.assertEqual(value["status"], status)
            self.assertEqual(value["evaluation"]["comparison"]["channels"][0]
                             ["metrics"]["rms_error_fs"]["value"], rms)
            self.assertIn(MARKER.encode("utf-8"), self.controls[label])
            replay = json.loads(self.controls["replay-" + label])
            self.assertEqual((replay["status"], replay["exact_report_match"],
                              replay["saved_engineering_status"], replay["replayed_engineering_status"]),
                             ("match", True, status, status))
        study = json.loads(self.controls["study"])
        self.assertEqual(study["status"], "failed")
        self.assertEqual({key: study["summary"][key] for key in ("jobs", "pass", "inconclusive", "failed")},
                         {"jobs": 3, "pass": 1, "inconclusive": 1, "failed": 1})
        replay = json.loads(self.controls["replay-study"])
        self.assertEqual((replay["status"], replay["exact_report_match"],
                          replay["saved_engineering_status"], replay["replayed_engineering_status"]),
                         ("match", True, "failed", "failed"))
        self.assertEqual(struct.unpack("<4f", (self.archive / "corpus/audio/reference.f32").read_bytes()),
                         (1., -1., 1., -1.))
        self.assert_inputs_preserved()

    def test_closed_stdout_during_help_exits_one_without_finalizer_noise(self):
        for module in CLIS:
            with self.subTest(module=module):
                result = self.invoke(module, ["--help"], "closed-help-" + module, "stdout")
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertTrue(result.stderr, "Writable stderr must describe failed help delivery")
                self.assertNotIn(b"Traceback", result.stderr)
                self.assertNotIn(b"Exception ignored", result.stderr)
        self.assert_inputs_preserved()

    def test_closed_stdout_preserves_complete_reports_and_generated_demo(self):
        labels = {"capture_audio": "audio", "capture_corpus": "corpus",
                  "capture_job": "job-pass", "capture_readiness": "readiness",
                  "capture_study": "study", "verify_capture_report": "replay-study",
                  "validate_capture": "validation"}
        for module in CLIS:
            with self.subTest(module=module):
                target = self.outputs / ("closed-stdout-" + module + ".json")
                result = self.invoke(module, self.success_args(module, target),
                                     "closed-report-" + module, "stdout")
                # Inspect publication even if the process result is wrong.
                if module in WRITERS:
                    self.assertEqual(target.read_bytes(), self.controls[labels[module]])
                elif module == "make_capture_demo":
                    self.assertEqual(inventory(target), self.original_demo_inventory)
                    self.assertEqual(len(inventory(target)), 16)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertTrue(result.stderr)
                self.assertNotIn(b"Traceback", result.stderr)
                self.assertNotIn(b"Exception ignored", result.stderr)
        self.assert_inputs_preserved()

    def test_closed_stderr_preserves_rejection_exit_and_empty_stdout(self):
        for module in CLIS:
            with self.subTest(module=module):
                if module == "make_capture_demo":
                    args = ["--output", self.archive]
                elif module == "verify_capture_report":
                    args = ["--kind", "study", "--input", self.root / "missing Ω.json",
                            "--report", self.saved["study"]]
                else:
                    args = ["--input", self.root / "missing Ω.json"]
                result = self.invoke(module, args, "closed-error-" + module, "stderr")
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, b"")
        self.assert_inputs_preserved()

    def test_both_closed_streams_do_not_destroy_completed_outputs(self):
        for module in WRITERS:
            with self.subTest(module=module):
                target = self.outputs / ("both-closed-" + module + ".json")
                command = [sys.executable, "-B", "-S", str(self.tools / (module + ".py")),
                           *map(str, self.success_args(module, target))]
                reader, writer = os.pipe()
                os.close(reader)
                try:
                    result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=writer,
                                            stderr=writer, env=self.environment, cwd=self.foreign,
                                            check=False, timeout=30)
                finally:
                    os.close(writer)
                self.observations.append({"label": "both-closed-" + module, "module": module,
                                          "argv": command, "closed_stream": "both",
                                          "returncode": result.returncode})
                label = {"capture_readiness": "readiness", "capture_job": "job-pass",
                         "capture_study": "study", "verify_capture_report": "replay-study"}[module]
                self.assertEqual(target.read_bytes(), self.controls[label])
                self.assertEqual(result.returncode, 1)
        self.assert_inputs_preserved()

    def test_output_collisions_preserve_original_inputs_sources_and_reports(self):
        for module in WRITERS:
            args = self.success_args(module)
            input_path = Path(args[args.index("--input") + 1])
            targets = [input_path, self.tools / (module + ".py"), self.saved["study"]]
            for index, target in enumerate(targets):
                with self.subTest(module=module, collision=index):
                    before = target.read_bytes()
                    result = self.invoke(module, self.success_args(module, target),
                                         f"collision-{module}-{index}")
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertEqual(result.stdout, b"")
                    self.assertTrue(result.stderr)
                    self.assertNotIn(b"Traceback", result.stderr)
                    self.assertEqual(target.read_bytes(), before)
            self.assert_inputs_preserved()

    def test_dangling_output_destinations_and_existing_hardlinks_remain_unchanged(self):
        for module in WRITERS:
            for kind in ("hardlink", "dangling"):
                with self.subTest(module=module, kind=kind):
                    path = self.outputs / (kind + "-" + module)
                    missing = self.outputs / ("absent-" + module)
                    try:
                        if kind == "hardlink":
                            os.link(self.saved["study"], path)
                            before = path.read_bytes()
                        else:
                            path.symlink_to(missing)
                            before = path.readlink()
                    except (OSError, NotImplementedError) as error:
                        self.skipTest(f"Native {kind} capability unavailable: {error}")
                    result = self.invoke(module, self.success_args(module, path),
                                         f"collision-{kind}-{module}")
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertEqual(result.stdout, b"")
                    if kind == "hardlink":
                        self.assertEqual(path.read_bytes(), before)
                    else:
                        self.assertTrue(path.is_symlink())
                        self.assertEqual(path.readlink(), before)
                        self.assertFalse(missing.exists())
            self.assert_inputs_preserved()

    def assert_independent_script(self, module):
        # The demo's frozen contract and the original v1 validator both retain
        # a standalone standard-library-only script, with no sibling import.
        directory = self.root / ("independent-" + module)
        directory.mkdir()
        script = directory / (module + ".py")
        script.write_bytes((self.tools / script.name).read_bytes())
        identity = script.read_bytes()
        for case in ("help", "ordinary", "closed-help", "closed-output", "closed-error"):
            with self.subTest(module=module, case=case):
                closed = None
                target = self.outputs / ("independent-" + module + "-" + case)
                if "help" in case:
                    args = ["--help"]
                elif case == "closed-error":
                    args = (["--output", self.archive] if module == "make_capture_demo"
                            else ["--input", self.root / "missing Ω.json"])
                else:
                    args = self.success_args(module, target)
                if case in ("closed-help", "closed-output"):
                    closed = "stdout"
                elif case == "closed-error":
                    closed = "stderr"
                result = self.invoke(module, args, "independent-" + module + "-" + case,
                                     closed, script_path=script)
                if case in ("ordinary", "closed-output") and module == "make_capture_demo":
                    self.assertEqual(inventory(target), self.original_demo_inventory)
                self.assertEqual(result.returncode, 1 if closed else 0, result.stderr)
                if closed is None:
                    self.assertEqual(result.stderr, b"")
                    if case == "help":
                        self.assertIn(b"usage:", result.stdout)
                    elif module == "make_capture_demo":
                        self.assertEqual(result.stdout, self.generated_inventory)
                    else:
                        self.assertEqual(result.stdout, self.controls["validation"])
                elif closed == "stderr":
                    self.assertEqual(result.stdout, b"")
                else:
                    self.assertTrue(result.stderr)
                    self.assertNotIn(b"Traceback", result.stderr)
                    self.assertNotIn(b"Exception ignored", result.stderr)
                self.assertEqual(script.read_bytes(), identity)
                self.assertEqual({p.name for p in directory.iterdir()}, {script.name})
        self.assert_inputs_preserved()

    def test_generator_remains_independent_without_sibling_capture_modules(self):
        self.assert_independent_script("make_capture_demo")

    def test_legacy_validator_remains_independent_without_sibling_capture_modules(self):
        self.assert_independent_script("validate_capture")


if __name__ == "__main__":
    unittest.main()
