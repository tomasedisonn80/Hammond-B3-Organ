#!/usr/bin/env python3
"""Read-only source/evidence audit; writes only the explicitly named A60 receipt.

This is not the session strict checker or an external-dispatch attestation.
Re-execution records a new observation and must use a fresh output filename.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

REPAIR = "2f57723d9ec806fe8f721c317ef8c1a38d63b532"
BASE = "4aac394cde4da40906b615573a8779aee2d9a37a"
SESSION = Path("docs/development/2026-11-15-streaming-continuation")
CURRENT = ["AGENTS.md", "README.md", "docs/PLAN.md", "docs/PROJECT_GUIDE.md",
           "docs/STATUS.md", "docs/NEXT_STEPS.md", "docs/PRODUCT_HANDOFF.md",
           "docs/DEVELOPMENT_LOG.md", "docs/CAUSAL_CONTACT_GRID_GUIDE.md",
           "docs/CAUSAL_CONTACT_GRID_RESULTS.md", str(SESSION / "README.md"),
           str(SESSION / "CHECKPOINT.md")]
STABLE = ["docs/CAUSAL_CONTACT_GRID_CONTRACT.md",
          "docs/design/UPPER_RACK_MATERIAL_CONTRACT.md",
          "docs/FRACTIONAL_CONTACT_REFERENCE.md", "docs/CONTACT_SWITCHING_VALIDATION.md",
          "docs/research/chapter-index.json", "docs/design/atlas-cover-reference.jpg",
          "Hammond_B3_Leslie_Research_Atlas_500pp.pdf"]
ROUTES = ["docs/research/CONTACT_GRID_CONVERSION_NEXT.md",
          "docs/research/CAUSAL_CONTACT_AUDIO_NEXT.md",
          "docs/research/CAUSAL_CONTACT_CAPACITY_NEXT.md",
          "docs/design/WHOLE_WINDOW_REFERENCE_NEXT.md",
          "docs/design/REFERENCE_MATERIAL_TYPE_NEXT.md",
          "docs/design/NATIVE_ACCESSIBILITY_JOURNEY_NEXT.md",
          "docs/reviews/CONTACT_GRID_CONVERSION_NEXT_REVIEW.md",
          "docs/reviews/CAUSAL_CONTACT_AUDIO_NEXT_REVIEW.md",
          "docs/reviews/CAUSAL_CONTACT_CAPACITY_NEXT_REVIEW.md",
          "docs/reviews/REFERENCE_MATERIAL_NEXT_REVIEW.md",
          "docs/reviews/NATIVE_ACCESSIBILITY_JOURNEY_NEXT_REVIEW.md",
          "docs/reviews/STREAMING_FULL_PLAN_COVERAGE_REVIEW.md",
          "docs/reviews/STREAMING_SESSION_RECORD_ADMISSION.md",
          "docs/reviews/STREAMING_FUTURE_AGENT_RULES_REVIEW.md",
          "docs/reviews/STREAMING_STORAGE_RECOVERY_REVIEW.md"]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = args.output.resolve()
    if output.exists():
        parser.error("retain prior receipts; choose a fresh output filename")
    report_dir = (repo / SESSION / "reports").resolve()
    if output.parent != report_dir or not output.name.startswith("A60-"):
        parser.error("output must be a new A60-* file in the assigned reports directory")
    errors = []

    def check(condition: bool, label: str) -> None:
        if not condition:
            errors.append(label)

    def git(*args: str) -> bytes:
        return subprocess.check_output(["git", *args], cwd=repo)

    def read(name: str | Path) -> bytes:
        return (repo / name).read_bytes()

    def load(name: str | Path):
        return json.loads(read(name))

    def git_tree(commit: str):
        entries = {}
        for raw in git("ls-tree", "-r", "-z", commit).split(b"\0"):
            if not raw:
                continue
            prefix, path = raw.split(b"\t", 1)
            mode, kind, object_id = prefix.decode().split()
            entries[path.decode()] = {"mode": mode, "type": kind, "sha": object_id}
        return entries

    started = datetime.now(timezone.utc).isoformat()
    index_path = Path(git("rev-parse", "--git-path", "index").decode().strip())
    if not index_path.is_absolute():
        index_path = repo / index_path
    index_before = sha(index_path.read_bytes())
    ledger_raw = read(SESSION / "assignments.json")
    before = {p: sha(read(p)) for p in CURRENT + STABLE + ROUTES}
    head = git("rev-parse", "HEAD").decode().strip()
    check(head == REPAIR, "reviewed HEAD is not the repaired code revision")
    qualification = load(SESSION / "reports/windows-repair-qualification.json")
    packed = read(SESSION / "reports" / qualification["source_inventory"]["path"])
    raw = gzip.decompress(packed)
    check(sha(raw) == qualification["source_inventory"]["raw_sha256"], "source inventory raw identity")
    inputs = json.loads(raw)
    check(len(inputs) == 505, "505 source inputs")
    tree = git_tree(REPAIR)
    code_mismatches = []
    head_mismatches = []
    for path, expected in inputs.items():
        content = read(path)
        if sha(content) != expected:
            code_mismatches.append(path)
        object_id = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        if path not in tree or tree[path]["sha"] != object_id:
            head_mismatches.append(path)
    check(not code_mismatches and not head_mismatches, "code inputs match qualified and committed bytes")
    workflows = {}
    for path, expected in qualification["workflow_sha256"].items():
        content = read(path)
        workflows[path] = sha(content)
        check(sha(content) == expected, "workflow qualification: " + path)
        check(content == git("show", REPAIR + ":" + path), "workflow repaired-source identity: " + path)
    check(len(workflows) == 3, "three workflow identities")
    for path in STABLE:
        check(read(path) == git("show", REPAIR + ":" + path), "frozen input preserved: " + path)

    publications = []
    for stem, expected_count in [("implementation", 243), ("repair", 64)]:
        pub = load(SESSION / "reports" / (stem + "-publication.json"))
        raw_manifest = gzip.decompress(read(SESSION / "reports" / pub["published_manifest"]["path"]))
        manifest = json.loads(raw_manifest)
        check(sha(raw_manifest) == pub["published_manifest"]["raw_sha256"], stem + " manifest identity")
        observed_tree = git("rev-parse", pub["commit"] + "^{tree}").decode().strip()
        observed_parent = git("rev-parse", pub["commit"] + "^").decode().strip()
        published_tree = git_tree(pub["commit"])
        check(observed_tree == pub["tree"] == manifest["tree"], stem + " tree binding")
        check(observed_parent == pub["parent"] == manifest["parent"], stem + " parent binding")
        check(len(manifest["entries"]) == expected_count, stem + " manifest count")
        mismatches = [e["path"] for e in manifest["entries"] if published_tree.get(e["path"]) != {k:e[k] for k in ("mode", "type", "sha")}]
        check(not mismatches, stem + " published entries")
        publications.append({"commit":pub["commit"], "tree":observed_tree, "parent":observed_parent, "entries":len(manifest["entries"]), "mismatches":mismatches})

    preserved_reports = git("diff", "--name-only", "HEAD", "--", str(SESSION / "reports"), str(SESSION / "notes")).decode().splitlines()
    check(not preserved_reports, "no previously committed session note/report rewritten")
    gallery_paths = sorted((repo / "examples/demos/upper-rack-material-v1/images").glob("*.png"))
    check(len(gallery_paths) == 12, "twelve selected gallery PNGs")
    gallery = {}
    for path in gallery_paths:
        rel = path.relative_to(repo).as_posix()
        gallery[rel] = sha(path.read_bytes())
        check(path.read_bytes() == git("show", REPAIR + ":" + rel), "gallery unchanged: " + rel)
    reading = load(SESSION / "reports/atlas-reading-coverage.json")
    page_counts = Counter()
    for reader in reading["readers"]:
        page_counts.update(range(reader["first_page"], reader["last_page"] + 1))
        check(sha(read(reader["note"])) == reader["note_sha256"], "reader-note identity: " + reader["agent"])
    check(len(reading["readers"]) == 6 and set(page_counts) == set(range(1,501)) and set(page_counts.values()) == {1}, "six disjoint readers cover500pages")
    check(sha(read("Hammond_B3_Leslie_Research_Atlas_500pp.pdf")) == reading["pdf_sha256"], "original PDF identity")
    chapters = load("docs/research/chapter-index.json")["chapters"]
    check(len(chapters) == 80 and [c["number"] for c in chapters] == list(range(1,81)), "eighty chapter entries")
    check([(c["start_page"], c["end_page"]) for c in chapters] == [(13+6*i,18+6*i) for i in range(80)], "chapter page spans13through492")
    plan = read("docs/PLAN.md").decode()
    milestones = re.findall(r"^\| \*\*M([0-9]) [—-]",plan,re.M)
    check(milestones == [str(i) for i in range(10)], "allM0throughM9milestone rows")

    hosted = load(SESSION / "reports/hosted-2f57723-complete.json")
    jobs = [j for r in hosted["runs"] for j in r["jobs"]]
    check(len(hosted["runs"]) == 3 and len(jobs) == 13, "repaired three-run thirteen-job count")
    for run in hosted["runs"]:
        check(run["head_sha"] == REPAIR and run["status"] == "completed" and run["conclusion"] == "success" and run["event"] == "push" and run["head_branch"] == "main" and run["run_attempt"] == 1, "retained repaired run binding:" + str(run["id"]))
        for job in run["jobs"]:
            check(job["run_id"] == run["id"] and job["status"] == "completed" and job["conclusion"] == "success", "retained job binding:" + str(job["id"]))
    initial = load(SESSION / "reports/hosted-af2b747-complete.json")
    check(initial["successful_jobs"] == 12 and initial["total_jobs"] == 13 and initial["status"] == "completed_with_failure", "initial failure retained")
    logs = []
    for name,logkey,byteskey in [("windows-core-af2b747-failure.json","log","decoded_log_utf8_bytes"),("windows-core-2f57723-success.json","log_file","decoded_log_bytes")]:
        receipt = load(SESSION / "reports" / name)
        log = gzip.decompress(read(SESSION / "reports" / receipt[logkey]))
        check(len(log) == receipt[byteskey] and sha(log) == receipt["decoded_log_sha256"], "decoded log identity:" + name)
        logs.append({"receipt":name,"raw_bytes":len(log),"sha256":sha(log)})

    ledger = json.loads(ledger_raw)
    accepted = [r for r in ledger["assignments"] if r["status"] == "accepted"]
    matched_notes = 0
    for row in accepted:
        candidates = [p for p in row["owned_paths"] if "/notes/" in p and p.endswith(".md")]
        check(len(candidates) == 1, "one accepted note for" + str(row["number"]))
        if len(candidates) == 1 and sha(read(candidates[0])) == row["note_sha256"]:
            matched_notes += 1
        else:
            check(False, "accepted note identity:" + str(row["number"]))
    pending = [r["number"] for r in ledger["assignments"] if r["status"] != "accepted"]
    after = {p:sha(read(p)) for p in before}
    check(before == after, "reviewed inputs stable during audit")
    check(ledger_raw == read(SESSION / "assignments.json"), "ledger stable during audit")
    check(index_before == sha(index_path.read_bytes()), "index unchanged during audit")
    check(git("rev-parse", "HEAD").decode().strip() == head, "HEAD unchanged during audit")
    report = {"schema_version":1,"reviewer":"/root/w10_a60","started_utc":started,
              "finished_utc":datetime.now(timezone.utc).isoformat(),"head":head,
              "tree":git("rev-parse", "HEAD^{tree}").decode().strip(),
              "scope":"Read-only source, retained-evidence and preclosure consistency audit; no fresh remote/hosted fetch, build, broad test or product acceptance",
              "source_inputs":len(inputs),"source_mismatches":code_mismatches,"committed_input_mismatches":head_mismatches,
              "workflow_sha256":workflows,"publications":publications,
              "rewritten_old_notes_or_reports":preserved_reports,"gallery_sha256":gallery,
              "reading":{"readers":6,"pages":500,"chapters":80,"milestones":milestones,
                         "claim":"Checks retained identities/coverage, not a new whole-atlas reading or verification of all primary sources"},
              "hosted":{"source":"root retained connector receipts; independent fresh retrieval belongs to A58", "commit":REPAIR,
                        "runs":[{k:r[k] for k in ("id","name","head_sha","run_attempt","status","conclusion")} for r in hosted["runs"]],
                        "successful_jobs":13,"original_successful_jobs":12,"windows_logs":logs},
              "ledger":{"sha256":sha(ledger_raw),"records":len(ledger["assignments"]),"accepted":len(accepted),"matched_accepted_notes":matched_notes,
                        "unaccepted":pending,"missing_numbers":sorted(set(range(1,61))-{r["number"] for r in ledger["assignments"]}),
                        "strict_closure_run":False,"external_dispatch_attested":False},
              "input_sha256":before,"index_sha256":index_before,"errors":errors,"passed":not errors}
    output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"passed":not errors,"errors":errors,"source_inputs":len(inputs),"workflow_inputs":len(workflows),"ledger":report["ledger"],"receipt":str(output.relative_to(repo))},indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
