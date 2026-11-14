#!/usr/bin/env python3
"""Focused A55 wiring audit; never executes the real session checker."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile

import yaml


ROOT = Path(__file__).resolve().parents[4]
SESSION = Path("docs/development/2026-11-14-reference-refinement")
BASE = "0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b"
WORKFLOW = ".github/workflows/ci.yml"
NOTE = SESSION / "notes/A55-strict-ci-gate.md"
REPORT = SESSION / "reports/A55-strict-ci-gate.json"
NAME = "Verify the completed refinement session"
COMMAND = (
    "set -o pipefail\n"
    "python tools/check_refinement_session.py --repo . --json | "
    "tee ci-logs/refinement-session-completion.json\n"
)
ADDITION = (
    "      - name: Verify the completed refinement session\n"
    "        if: runner.os == 'Linux'\n"
    "        run: |\n"
    "          set -o pipefail\n"
    "          python tools/check_refinement_session.py --repo . --json | "
    "tee ci-logs/refinement-session-completion.json\n\n"
)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def identity(path):
    raw = (ROOT / path).read_bytes()
    return {"path": str(path), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest()}


checks = []


def require(name, condition, detail):
    checks.append({"name": name, "passed": bool(condition), "detail": detail})
    if not condition:
        raise AssertionError(name)


started = datetime.now(timezone.utc).isoformat()
original = git("show", f"{BASE}:{WORKFLOW}")
current = (ROOT / WORKFLOW).read_bytes()
original_text, current_text = original.decode(), current.decode()
before = yaml.load(original_text, Loader=yaml.BaseLoader)
after = yaml.load(current_text, Loader=yaml.BaseLoader)
require("only_six_line_addition", current_text.count(ADDITION) == 1
        and current_text.replace(ADDITION, "", 1) == original_text,
        "Removing the exact six added lines restores every published workflow byte.")
steps = after["jobs"]["release"]["steps"]
matches = [index for index, step in enumerate(steps) if step.get("name") == NAME]
require("one_refinement_step", len(matches) == 1,
        "Exactly one dedicated completion step is in Release.")
index = matches[0]
step = steps[index]
require("strict_linux_command", step == {
    "name": NAME, "if": "runner.os == 'Linux'", "run": COMMAND},
    "The only step fields are name, Linux condition and the exact strict pipefail pipeline.")
require("after_historical_interface_before_upload",
        steps[index - 1]["name"] == "Verify the completed interface session"
        and steps[index + 1]["name"] == "Retain configure, build, and test diagnostics",
        "The historical checker immediately precedes the new gate and retention immediately follows.")
without_addition = copy.deepcopy(after)
del without_addition["jobs"]["release"]["steps"][index]
require("all_existing_workflow_structure_preserved", without_addition == before,
        "All earlier jobs, matrices, timeouts, pins, commands, sanitizer policy and budgets are unchanged.")
require("historical_interface_strict_command_preserved", steps[index - 1]["run"] ==
        "set -o pipefail\npython tools/check_interface_session.py --repo . --json | "
        "tee ci-logs/interface-session-completion.json\n",
        "The separate completed historical interface gate remains required on Linux.")
upload = steps[index + 1]
require("failed_step_artifact_retention_preserved",
        upload["if"] == "${{ always() && !cancelled() }}"
        and "ci-logs/" in upload["with"]["path"].splitlines()
        and upload["with"]["retention-days"] == "14"
        and upload["with"]["if-no-files-found"] == "warn",
        "Existing retention includes the exact JSON on success or failure; cancellation remains excluded.")
require("bash_and_log_directory_available",
        after["defaults"]["run"]["shell"] == "bash"
        and any("mkdir -p ci-logs" in item.get("run", "") for item in steps[:index]),
        "Existing Bash shell and earlier ci-logs creation serve the added pipeline.")
syntax = subprocess.run(["bash", "-n"], input=COMMAND, text=True, capture_output=True,
                        cwd=ROOT, check=False)
require("bash_syntax", syntax.returncode == 0,
        "bash -n parsed the extracted run block without invoking any command.")

# This shell function replaces python only inside the private child shell. No
# checker source or ledger is copied into the disposable transport directory.
probe_function = r'''python() {
  if [[ "$#" -ne 4 || "$1" != "tools/check_refinement_session.py" || "$2" != "--repo" || "$3" != "." || "$4" != "--json" ]]; then
    return 97
  fi
  printf '%s' "$A55_PROBE_STDOUT"
  printf '%s' "$A55_PROBE_STDERR" >&2
  return "$A55_PROBE_EXIT"
}
'''
probes = []
for expected_exit in (0, 31):
    synthetic_stdout = json.dumps({"A55_synthetic_transport_probe": True,
                                   "producer_exit": expected_exit}) + "\n"
    synthetic_stderr = "A55 synthetic stderr remains outside the JSON artifact.\n"
    with tempfile.TemporaryDirectory(prefix="a55-ci-transport-") as temporary:
        sandbox = Path(temporary)
        (sandbox / "ci-logs").mkdir()
        environment = dict(os.environ, A55_PROBE_EXIT=str(expected_exit),
                           A55_PROBE_STDOUT=synthetic_stdout,
                           A55_PROBE_STDERR=synthetic_stderr)
        result = subprocess.run(["bash", "-e", "-c", probe_function + COMMAND],
                                cwd=sandbox, env=environment, text=True,
                                capture_output=True, check=False)
        retained = (sandbox / "ci-logs/refinement-session-completion.json").read_text()
        passed = (result.returncode == expected_exit and retained == synthetic_stdout
                  and result.stdout == synthetic_stdout and result.stderr == synthetic_stderr)
        probes.append({"producer_exit": expected_exit, "pipeline_exit": result.returncode,
                       "stdout": result.stdout, "stderr": result.stderr,
                       "retained_json": retained,
                       "artifact_sha256": hashlib.sha256(retained.encode()).hexdigest(),
                       "exact_stdout_retained": retained == synthetic_stdout,
                       "stderr_kept_separate": result.stderr == synthetic_stderr,
                       "actual_checker_executed": False})
        require(f"synthetic_transport_exit_{expected_exit}", passed,
                "The literal pipeline preserves producer exit and exact JSON through tee in a private directory.")

protected = ["tools/check_refinement_session.py", "tests/test_refinement_session.py",
             "tools/check_interface_session.py",
             "docs/development/2026-11-14-interface-continuation/assignments.json"]
protected_records = []
for path in protected:
    record = identity(path)
    record["matches_published_source"] = (ROOT / path).read_bytes() == git("show", f"{BASE}:{path}")
    protected_records.append(record)
require("checker_tests_and_historical_ledger_preserved",
        all(record["matches_published_source"] for record in protected_records),
        "Refinement checker/tests and historical interface checker/manifest match the named published source.")

diff_check = subprocess.run(["git", "diff", "--check", "--", WORKFLOW], cwd=ROOT,
                            text=True, capture_output=True, check=False)
require("workflow_diff_check", diff_check.returncode == 0,
        "git diff --check -- .github/workflows/ci.yml returned zero with no diagnostics.")
note = (ROOT / NOTE).read_text()
narrative = re.sub(r"```.*?```", "", note, flags=re.DOTALL)
word_count = len(narrative.split())
require("assigned_note_substance", word_count >= 300,
        f"The A55 note contains {word_count} whitespace-separated narrative words excluding fenced code.")
require("owned_text_whitespace", all(
        raw.endswith(b"\n") and all(line.rstrip() == line for line in raw.splitlines())
        for raw in (current, (ROOT / NOTE).read_bytes(), Path(__file__).read_bytes())),
        "Workflow, new note and audit source have final newlines and no trailing whitespace.")

review = json.loads((ROOT / SESSION / "reports/A53-completion-checker-review.json").read_text())
require("A53_has_no_blocking_defect",
        review["decision"] == "reviewed_no_blocking_defect_for_declared_record_consistency_scope",
        "A53 supports checker use within record consistency; its 54/51 snapshot remains explicitly partial.")

report = {
    "schema_version": 1,
    "agent": "/root/w10_a55_strict_ci_gate",
    "started_utc": started,
    "completed_utc": datetime.now(timezone.utc).isoformat(),
    "working_directory": str(ROOT),
    "source_head": git("rev-parse", "HEAD").decode().strip(),
    "source_tree": git("rev-parse", "HEAD^{tree}").decode().strip(),
    "observed_remote_tracking_head": git("rev-parse", "refs/remotes/origin/main").decode().strip(),
    "fresh_remote_query_performed": False,
    "environment": {"python": sys.version, "platform": platform.platform(),
                    "PyYAML": yaml.__version__,
                    "bash": subprocess.check_output(["bash", "--version"], text=True).splitlines()[0]},
    "reproduce_command": "PYTHONDONTWRITEBYTECODE=1 python3 " + str(Path(__file__).relative_to(ROOT)),
    "result": "passed_focused_local_wiring_checks",
    "check_count": len(checks),
    "checks": checks,
    "baseline_workflow": {"commit": BASE, "path": WORKFLOW, "bytes": len(original),
                          "sha256": hashlib.sha256(original).hexdigest()},
    "modified_workflow": identity(WORKFLOW),
    "workflow_diff": git("diff", BASE, "--", WORKFLOW).decode(),
    "new_step": step,
    "artifact_retention": upload,
    "synthetic_transport_probes": probes,
    "protected_source_records": protected_records,
    "A53_observed_snapshot": {
        "as_of_utc": review["actual_progress_observation"]["as_of_utc"],
        "recorded": review["actual_progress_observation"]["counts"]["recorded"],
        "accepted": review["actual_progress_observation"]["counts"]["accepted"],
        "completion_valid": review["actual_progress_observation"]["completion_valid"],
    },
    "input_records": [identity(path) for path in [
        SESSION / "notes/A39-refinement-ledger-checker.md",
        SESSION / "notes/A53-completion-checker-review.md",
        SESSION / "reports/A53-completion-checker-review.json",
        Path("docs/reviews/REFERENCE_REFINEMENT_COMPLETION_GATE.md"),
        NOTE, Path(__file__).relative_to(ROOT)]],
    "note_narrative_words_excluding_fences": word_count,
    "actual_strict_completion_executed": False,
    "actual_progress_checker_executed": False,
    "new_checker_suite_runs": 0,
    "build_or_ctest_runs": 0,
    "hosted_workflow_executed_or_dispatched": False,
    "publication_performed": False,
    "publication_prerequisite": "Root acceptance of all sixty actual results and successful strict completion on stable final records.",
    "limits": [
        "Local YAML structure and shell transport probes do not prove hosted runner execution or artifact upload.",
        "An earlier failed step can skip this ordinary required step; cancellation is excluded by the unchanged retention condition.",
        "A53's earlier 54-record/51-accepted snapshot is partial and does not describe later live counts.",
        "Completion consistency cannot authenticate dispatch, acceptance truth, product readiness or physical/visual fidelity.",
        "The concurrent session owns R4; no product, checker, test, manifest or current shared documentation was edited by A55.",
    ],
}
(ROOT / REPORT).write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"result": report["result"], "checks": len(checks),
                  "report": str(REPORT), "workflow_sha256": report["modified_workflow"]["sha256"],
                  "note_sha256": identity(NOTE)["sha256"],
                  "note_narrative_words": word_count}, indent=2))
