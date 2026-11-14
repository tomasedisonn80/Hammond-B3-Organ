#!/usr/bin/env python3
"""Focused A60 documentary audit; never executes project or session gates."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[4])
parser.add_argument("--output", type=Path)
args = parser.parse_args()
repo = args.repo.resolve()
session = Path("docs/development/2026-11-14-reference-refinement")
output = args.output or repo / session / "reports/A60-final-handoff-acceptance.json"
output = output.resolve()
commit = "0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b"
tree = "f8144b771cda1264a8788f8297f5bfec999f4a08"
checks = []
inputs = {}

def check(name, ok, detail=None):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

def raw(path):
    p = repo / path
    b = p.read_bytes()
    inputs[str(path)] = {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
    return b

def read(path):
    return raw(path).decode("utf-8")

def load(path):
    return json.loads(read(path))

def git(*args):
    return subprocess.check_output(["git", *args], cwd=repo)

observed_utc = datetime.now(timezone.utc).isoformat()
raw(session / "reports/A60-check-final-handoff.py")
head = git("rev-parse", "HEAD").decode().strip()
head_tree = git("rev-parse", "HEAD^{tree}").decode().strip()
check("local published HEAD/tree", head == commit and head_tree == tree)
manifest = load(session / "assignments.json")
rows = manifest["assignments"]
counts = Counter(row["status"] for row in rows)
check("A60 is an actual recorded row; this audit does not accept it", any(
    row["id"] == "A60" and row["agent"] == "/root/w10_a60_final_handoff_acceptance"
    and row["status"] in {"running", "accepted"} for row in rows))
coverage = []
covered = []
for number, start, end in [(1,1,84),(2,85,168),(3,169,252),(4,253,336),(5,337,420),(6,421,500)]:
    identifier = f"A{number:02d}"
    row = next(row for row in rows if row["id"] == identifier)
    note = read(row["note"])
    identity = inputs[row["note"]]
    check(identifier + " accepted note digest", row["status"] == "accepted" and
          identity["sha256"] == row["note_sha256"])
    check(identifier + " declared complete range", f"{start}-{end}" in row["scope"] and
          str(start) in note and str(end) in note and row["agent"].split("/")[-1] in note)
    coverage.append({"id": identifier, "agent": row["agent"], "start": start, "end": end,
                     "pages": end-start+1, "note": row["note"], **identity})
    covered.extend(range(start, end+1))
check("six distinct atlas reader identities", len({row["agent"] for row in coverage}) == 6)
check("exactly all 500 pages once", covered == list(range(1,501)))
raw("Hammond_B3_Leslie_Research_Atlas_500pp.pdf")
check("original PDF identity", inputs["Hammond_B3_Leslie_Research_Atlas_500pp.pdf"]["sha256"] ==
      "4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769")
for path in ["docs/PLAN.md", "docs/REFERENCE_REFINEMENT_HANDOFF.md"]:
    content = read(path)
    check(path + " all ten milestone rows", all(re.search(r"\| \*?\*?M"+str(n)+r" ", content) for n in range(10)))

selected = ["include/hammond/ParameterBridge.h", "src/ParameterBridge.cpp",
            "src/ControlStateIO.cpp", "src/ControlState.cpp", "src/Engine.cpp",
            "include/hammond/Engine.h", "apps/standalone/UiModel.cpp",
            "apps/standalone/Session.cpp", "apps/standalone/main.cpp",
            "apps/standalone/InstrumentView.cpp", "apps/standalone/InspectionModel.cpp",
            "src/RotaryMotion.cpp", "src/RotaryPropagation.cpp",
            "include/hammond/RotaryPropagation.h", "include/hammond/RotaryMotion.h"]
for path in selected:
    check("published selected source: " + path, raw(path) == git("show", commit+":"+path))
check("47 parameter registry", "kParameterCount = 47" in read("include/hammond/ParameterBridge.h"))
state = read("src/ControlStateIO.cpp")
check("state4 and readers 1 through 3", all(f"B3CONTROLS{n}" in state for n in range(1,5)))
engine = read("src/Engine.cpp")
check("preserved source advance and dry mix statements", "source_bank_.process_frame(source_samples)" in engine
      and "mixed * profile_.output_gain * controls_.expression()" in engine)

readme = read("README.md")
gallery = Path("examples/demos/standalone-interface-preview-v4")
provenance = load(gallery / "provenance.json")
qualification = load(gallery / "inputs/source-qualification.json")
binary = Path(provenance["executable"]["path"])
binary_bytes = binary.read_bytes()
binary_sha = hashlib.sha256(binary_bytes).hexdigest()
check("v4 exact source/tree", qualification["published_commit"] == commit and qualification["published_tree"] == tree)
check("v4 exact existing binary", binary_sha == qualification["binary_sha256"] ==
      provenance["executable"]["before"]["sha256"] == provenance["executable"]["after"]["sha256"])
check("README source/tree/binary agreement", all(value in readme for value in [commit, tree, binary_sha]))
check("v4 eight retained cases", len(provenance["cases"]) == 8)
check("README dummy and unmet-equality limits", "SDL dummy audio/video" in readme and
      "Literal whole-interface 1:1 equality remains unmet" in readme)

reports = session / "reports"
a49 = load(reports / "A49-coherent-final-build.json")
a50 = load(reports / "A50-final-gallery-admission.json")
a51 = load(reports / "A51-native-input-evidence.json")
a53 = load(reports / "A53-completion-checker-review.json")
a55 = load(reports / "A55-strict-ci-gate.json")
a56 = load(reports / "A56-published-header-hosted-audit.json")
a57 = load(reports / "A57-r4-plan-independent-review.json")
a58 = load(reports / "A58-release-evidence-closure.json")
check("A49 single full 157 pass", a49["target_published_commit"] == commit and
      a49["full_suite_executions"] == 1 and a49["result_counts"]["passed"] == 157 and a49["result_counts"]["failed"] == 0)
check("A50 611 retained checks", a50["checks"] == 611 and a50["status"] == "passed" and a50["qualified_commit"] == commit)
check("A51 bounded evidence review", a51["checks_passed"] == a51["checks_total"] == 33)
check("A53 does not claim strict completion", a53["strict_completion_claimed"] is False)
check("A55 is local wiring only", a55["actual_strict_completion_executed"] is False and a55["check_count"] == 16)
check("A56 all twelve exact-source primary results", len(a56["jobs"]) == 12 and all(
    job["conclusion"] == "success" and job["head_sha"] == commit and job["ctest"]["failed"] == 0 for job in a56["jobs"]))
check("A58 348 source-specific checks", a58["status"] == "passed" and a58["checks_passed"] == a58["checks_total"] == 348)
r4 = read("docs/reviews/ROTARY_RENDERER_IMPLEMENTATION_READINESS.md")
check("A57 four explicit preconditions", all(f"Required precondition {n}" in r4 for n in range(1,5)))
check("A57 failed-result observation boundary", "leaves `PathResult` untouched on failure" in r4)

workflow = raw(".github/workflows/ci.yml")
addition = ("      - name: Verify the completed refinement session\n"
            "        if: runner.os == 'Linux'\n"
            "        run: |\n"
            "          set -o pipefail\n"
            "          python tools/check_refinement_session.py --repo . --json | tee ci-logs/refinement-session-completion.json\n\n").encode()
check("exact additive strict Linux CI step", workflow.count(addition) == 1 and
      workflow.replace(addition,b"") == git("show",commit+":.github/workflows/ci.yml"))
check("preserved failure retention and historical checker", b"always() && !cancelled()" in workflow and
      b"tools/check_interface_session.py --repo . --json" in workflow)
checker = read("tools/check_refinement_session.py")
check("strict checker default source", 'parser.add_argument("--in-progress", action="store_true"' in checker and
      'report = check(args.repo, args.in_progress)' in checker)

link_docs = ["README.md", "docs/PLAN.md", "docs/REFERENCE_REFINEMENT_HANDOFF.md",
             "docs/RELEASE_READINESS.md", "docs/research/REFERENCE_REFINEMENT_ATLAS_REVIEW.md",
             "docs/reviews/ROTARY_RENDERER_IMPLEMENTATION_READINESS.md",
             "docs/reviews/REFERENCE_REFINEMENT_FINAL_HANDOFF.md",
             str(session / "notes/A60-final-handoff-acceptance.md")]
# Create the intended report target before checking links to this very output.
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text("{}\n", encoding="utf-8")
link_count = 0
missing = []
for path in link_docs:
    content = read(path)
    for target in re.findall(r"!?\[[^\]\n]*\]\(([^)\s]+)\)", content):
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
            continue
        target = target.split("#",1)[0].split("?",1)[0]
        if not target:
            continue
        link_count += 1
        if not (repo / Path(path).parent / target).exists():
            missing.append({"from": path, "target": target})
check("focused local links resolve", not missing, {"occurrences": link_count, "missing": missing})
note = read(session / "notes/A60-final-handoff-acceptance.md")
narrative = re.sub(r"```.*?```", "", note, flags=re.S)
words = re.findall(r"\b[\w]+(?:[’'-][\w]+)*\b", narrative)
check("A60 narrative at least 300 words", len(words) >= 300, len(words))
check("owned Markdown whitespace and final newline", all(
    (repo/path).read_bytes().endswith(b"\n") and not re.search(r"[ \t]+$", (repo/path).read_text(), re.M)
    for path in link_docs[-2:]))
check("observed manifest stable during focused audit", hashlib.sha256((repo/session/"assignments.json").read_bytes()).hexdigest() ==
      inputs[str(session/"assignments.json")]["sha256"])

report = {"schema":"a60-final-handoff-v1", "worker":"/root/w10_a60_final_handoff_acceptance",
          "observed_utc":observed_utc, "completed_utc":datetime.now(timezone.utc).isoformat(),
          "repo":str(repo), "python":sys.version.split()[0], "local_head":head, "local_tree":head_tree,
          "scope":"Focused retained-evidence/source/link/coverage review; not final repository integrity, strict completion, fresh remote or new product execution.",
          "manifest_observation":{"recorded":len(rows), "status_counts":dict(counts),
                                  "remaining": [{"id":r["id"],"agent":r["agent"],"status":r["status"]} for r in rows if r["status"] != "accepted"]},
          "coverage":coverage, "covered_page_count":len(covered),
          "selected_source_count":len(selected), "v4_executable":{"path":str(binary),"bytes":len(binary_bytes),"sha256":binary_sha},
          "retained_hosted_summary":[{"name":j["name"],"job_id":j["job_id"],"passed":j["ctest"]["passed"],"total":j["ctest"]["total"],"source":j["head_sha"]} for j in a56["jobs"]],
          "checks_total":len(checks), "checks_passed":sum(c["passed"] for c in checks), "checks":checks,
          "status":"passed_focused_review_with_root_owned_document_corrections" if all(c["passed"] for c in checks) else "focused_check_failed",
          "open_corrections":["README explicitly identifies waveform 2e161dc 155/155 baseline and later A49 157/157 scope", "ACCEPTANCE_MATRIX current authority paragraph and retained standalone heading", "Root updates stale A56/dispatch current navigation and links finalized A57 readiness"],
          "filesystem_free_bytes":shutil.disk_usage(repo).free, "cleanup_performed":False,
          "inputs":inputs, "actual_strict_checker_executed":False, "actual_progress_checker_executed":False,
          "repository_integrity_gate_executed":False, "build_ctest_native_or_capture_execution":False,
          "fresh_remote_observation":False, "publication_performed":False,
          "final_root_gates":"Actual remaining acceptance, stable shared corrections, affected integrity, strict sixty-record result, expected-head publication verification and actual final-source CI."}
output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print(json.dumps({"status":report["status"], "checks_passed":report["checks_passed"],
                  "checks_total":len(checks), "local_links":link_count,
                  "manifest":report["manifest_observation"], "output":str(output)},indent=2))
sys.exit(0 if all(c["passed"] for c in checks) else 1)
