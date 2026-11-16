#!/usr/bin/env python3
"""Read-only source/evidence admission; writes only the named A43 receipt.

Run from the repository root with python3 -B. Does not build, run test bodies,
capture images, fetch, stage, commit, or edit any subject/evidence file.
"""
from __future__ import annotations

from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[4]
REPORTS = ROOT / "docs/development/2026-11-15-streaming-continuation/reports"
COMMIT = "af2b74760ee195c9497b314a1a29172f5238dd44"
TREE = "fb7d9ef7d1fcf24a70395c0671b75eb9c31558d4"
BASE = "4aac394cde4da40906b615573a8779aee2d9a37a"
GALLERY = ROOT / "examples/demos/upper-rack-material-v1"
errors: list[str] = []
bindings: dict[str, dict] = {}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def check(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def json_bytes(raw: bytes):
    return json.loads(raw, object_pairs_hook=unique_object)


def load(path: Path):
    raw = path.read_bytes()
    bindings[str(path.relative_to(ROOT))] = {"bytes": len(raw), "sha256": sha(raw)}
    return json_bytes(raw)


def git(*arguments: str) -> bytes:
    return subprocess.check_output(["git", *arguments], cwd=ROOT)


def git_blobs(paths: list[str], revision: str = COMMIT) -> dict[str, bytes]:
    request = "".join(f"{revision}:{path}\n" for path in paths).encode()
    completed = subprocess.run(["git", "cat-file", "--batch"], cwd=ROOT,
                               input=request, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, check=True)
    stream = io.BytesIO(completed.stdout)
    result = {}
    for path in paths:
        fields = stream.readline().split()
        if len(fields) != 3 or fields[1] != b"blob":
            raise ValueError(f"not a published blob: {path}: {fields!r}")
        raw = stream.read(int(fields[2]))
        if stream.read(1) != b"\n":
            raise ValueError(f"bad batch boundary: {path}")
        result[path] = raw
    if stream.read():
        raise ValueError("unexpected trailing batch data")
    return result


def compressed(path: str, expected: str | None = None) -> bytes:
    packed = (REPORTS / path).read_bytes()
    raw = gzip.decompress(packed)
    bindings[str((REPORTS / path).relative_to(ROOT))] = {
        "bytes": len(packed), "sha256": sha(packed),
        "raw_bytes": len(raw), "raw_sha256": sha(raw)}
    if expected is not None:
        check(sha(raw) == expected, f"decompressed identity: {path}")
    return raw


publication = load(REPORTS / "publication-source-qualification.json")
original = load(REPORTS / "coherent-qualification.json")
final = load(REPORTS / "final-coherent-qualification.json")
setup = load(REPORTS / "post-review-setup-qualification.json")
whitespace = load(REPORTS / "publication-whitespace-qualification.json")
published = load(REPORTS / "implementation-publication.json")
hosted = load(REPORTS / "hosted-initial-observation.json")
inventories = {}
for label, filename, expected in (
        ("original", original["source_inventory"]["path"],
         original["source_inventory"]["raw_sha256"]),
        ("post_review", final["source_inventory"]["path"],
         final["source_inventory"]["raw_sha256"]),
        ("publication", publication["inventory"], publication["raw_sha256"])):
    inventories[label] = json_bytes(compressed(filename, expected))
    check(len(inventories[label]) == 505, f"505 entries: {label}")

all_published = git("ls-tree", "-r", "--name-only", COMMIT).decode().splitlines()
prefixes = ("include/", "src/", "tests/", "tools/", "apps/", "plugins/",
            "cmake/", "assets/", "data/")
publication_scope = {path for path in all_published
                     if path.startswith(prefixes) or
                     path in {"CMakeLists.txt", "CMakePresets.json"}}
check(publication_scope == set(inventories["publication"]),
      "publication inventory covers every tracked file in its stated scope")
paths = sorted(publication_scope | set(publication["workflow_sha256"]))
blobs = git_blobs(paths)
for path, expected in {**inventories["publication"],
                       **publication["workflow_sha256"]}.items():
    check(sha(blobs[path]) == expected, f"published source: {path}")
    check(sha((ROOT / path).read_bytes()) == expected, f"working source: {path}")
check(publication["workflow_sha256"] == final["workflow_sha256"],
      "final and publication workflow identities agree")
check(git("rev-parse", f"{COMMIT}^{{tree}}").decode().strip() == TREE, "Git tree")
check(git("rev-parse", f"{COMMIT}^").decode().strip() == BASE, "Git parent")
check(published["commit"] == COMMIT and published["tree"] == TREE and
      published["parent"] == BASE, "publication receipt Git identity")


def differences(left: dict, right: dict):
    return {path: {"before": left.get(path), "after": right.get(path)}
            for path in sorted(left.keys() | right.keys())
            if left.get(path) != right.get(path)}


first_changes = differences(inventories["original"], inventories["post_review"])
last_changes = differences(inventories["post_review"], inventories["publication"])
check(set(first_changes) == {"tests/test_causal_contact_grid_cli.py",
                             "tests/test_causal_contact_grid_differential.py"},
      "only the two native Python suites changed before full rerun")
check(set(last_changes) == {whitespace["path"]} ==
      set(publication["changed_paths_after_full_suite"]), "sole post-suite path")
resource = (ROOT / whitespace["path"]).read_bytes()
check(sha(resource) == whitespace["after_sha256"], "current resource fixture")
check(sha(resource + b"\n") == whitespace["before_sha256"],
      "exactly one trailing newline reconstructs historical resource fixture")
check(whitespace["removed_suffix_hex"] == "0a", "newline suffix")
check(whitespace["before_binary_sha256"] == whitespace["after_binary_sha256"],
      "recorded resource binary equality")
resource_binary = ROOT / "../build-native/test_causal_contact_grid_resources"
check(sha(resource_binary.read_bytes()) == whitespace["after_binary_sha256"],
      "present resource binary identity")

log_summaries = {}
raw_logs = {}
for receipt in (original, final, whitespace):
    for name, entry in receipt["logs"].items():
        text = compressed(entry["path"], entry["raw_sha256"]).decode()
        raw_logs[name] = text
        log_summaries[name] = {
            "raw_sha256": sha(text.encode()),
            "passed_result_lines": len(re.findall(
                r"^\s*\d+/\d+ Test\s+#\d+:.*\bPassed\b.*$", text, re.M)),
            "summary": re.findall(r"100% tests passed, 0 tests failed out of \d+", text),
            "wall_seconds": re.findall(r"Total Test time \(real\) =\s*([0-9.]+) sec", text)}
for name, count, seconds in (("wave5-coherent-ctest", 210, "191.89"),
                             ("final-coherent-ctest", 210, "191.90"),
                             ("publication-whitespace-ctest", 1, "0.01")):
    summary = log_summaries[name]
    check(summary["passed_result_lines"] == count, f"pass line count: {name}")
    check(summary["summary"] == [f"100% tests passed, 0 tests failed out of {count}"],
          f"summary count: {name}")
    check(summary["wall_seconds"] == [seconds], f"wall seconds: {name}")
check("[131/131]" in raw_logs["wave5-coherent-build"], "original 131-step build")
check("ninja: no work to do." in raw_logs["final-coherent-build"], "final coherent no-op build")
check("[1/2] Building CXX object CMakeFiles/test_causal_contact_grid_resources.dir/" in
      raw_logs["publication-whitespace-build"] and
      "[2/2] Linking CXX executable test_causal_contact_grid_resources" in
      raw_logs["publication-whitespace-build"], "affected two-step rebuild")
for path, expected in final["binary_sha256"].items():
    check(sha((ROOT / path).read_bytes()) == expected, f"final binary: {path}")
check(original["binary_sha256"] == final["binary_sha256"],
      "named binaries retained across original and post-review full suite")

negative = []
for case in setup["negative_cases"]:
    text = compressed(case["log"], case["raw_sha256"]).decode()
    verified = (case["exit_code"] == 5 and case["explicit_RuntimeError"] is True and
                case["skipped"] is False and "RuntimeError:" in text and
                "Ran 0 tests" in text and "FAILED (errors=1)" in text and
                "skipped=" not in text)
    check(verified, f"negative setup evidence: {case['source']} / {case['mode']}")
    negative.append({"source": case["source"], "mode": case["mode"],
                     "recorded_exit_code": case["exit_code"], "log_verified": verified})
check(len(negative) == 8 and len({(r["source"], r["mode"]) for r in negative}) == 8,
      "eight distinct negative setup cases")
positive = setup["positive_ctest"]
positive_text = compressed(positive["log"], positive["raw_sha256"]).decode()
check("100% tests passed, 0 tests failed out of 2" in positive_text and
      "Total Test time (real) =   1.80 sec" in positive_text,
      "both positive configured suites")
for name in ("cli", "differential"):
    check(f"python_test_causal_contact_grid_{name}" in positive_text,
          f"configured suite included: {name}")

# Source inspection backs the continued fail-closed setup after the later
# documented CLI docstring revision; do not relabel old logs as new-source runs.
for name in ("cli", "differential"):
    text = (ROOT / f"tests/test_causal_contact_grid_{name}.py").read_text()
    setup_body = text.split("    def setUpClass(cls):", 1)[1].split("    def ", 1)[0]
    check("raise RuntimeError" in setup_body and "SkipTest" not in setup_body,
          f"current setup fails closed: {name}")

resource_audit = load(REPORTS / "A28-resource-audit.json")
resource_report = load(REPORTS / "A23-resources.json")
resource_rebased = []
for path, record in resource_audit["identities"].items():
    actual = (ROOT / path).read_bytes()
    if path == whitespace["path"]:
        check(sha(actual + b"\n") == record["sha256"] and
              len(actual) + 1 == record["bytes"], "A28 original fixture binding")
        resource_rebased.append(path)
    else:
        check(sha(actual) == record["sha256"] and len(actual) == record["bytes"],
              f"A28 unchanged retained identity: {path}")
check(resource_report["calls_checked"] == 192 and resource_report["passed"] is True,
      "resource report's finite 192-scope result")

gallery = load(GALLERY / "provenance.json")
manifest = load(GALLERY / "manifest.json")
gallery_admission = load(REPORTS / "A26-gallery-admission.json")
check(len(manifest["files"]) == 57, "57 original gallery payload members")
for path, record in manifest["files"].items():
    raw = (GALLERY / path).read_bytes()
    check(sha(raw) == record["sha256"] and len(raw) == record["bytes"],
          f"gallery payload: {path}")
gallery_checks = {}
for kind, expected_count in (("source", 117), ("build", 13)):
    section = gallery[kind]
    check(len(section["files"]) == expected_count, f"gallery {kind} input count")
    aggregate = sha(json.dumps(section["files"], sort_keys=True,
                               separators=(",", ":")).encode())
    check(aggregate == section["inventory_sha256_before"] ==
          section["inventory_sha256_after"], f"gallery {kind} aggregate")
    for path, record in section["files"].items():
        raw = (Path(section["root"]) / path).read_bytes()
        check(sha(raw) == record["sha256"] and len(raw) == record["bytes"],
              f"gallery {kind}: {path}")
        if kind == "source":
            published_raw = blobs.get(path)
            if published_raw is None:
                published_raw = git_blobs([path])[path]
            check(sha(published_raw) == record["sha256"], f"published gallery source: {path}")
    gallery_checks[kind] = {"files": expected_count, "inventory_sha256": aggregate}
for kind in ("executable", "tool"):
    section = gallery[kind]
    check(section["before"] == section["after"], f"gallery stable {kind}")
    check(sha(Path(section["path"]).read_bytes()) == section["after"]["sha256"],
          f"current gallery {kind}")
source_report = load(GALLERY / "inputs/source-qualification.json")
check(sha((GALLERY / "inputs/source-qualification.json").read_bytes()) ==
      gallery["source"]["checked_author_report"]["sha256"], "copied qualification identity")
for path, expected in source_report["source_sha256"].items():
    check(sha((ROOT / path).read_bytes()) == expected, f"ten-source gallery qualification: {path}")
changed_tests = set(first_changes) | set(last_changes)
check(not (changed_tests & set(gallery["source"]["files"])),
      "later test changes do not intersect gallery production inventory")
check(len(gallery["cases"]) == 12 and all(c["exit_code"] == 0 for c in gallery["cases"]),
      "twelve recorded successful genuine app captures")
check(gallery_admission["checks"] == 641 and gallery_admission["errors"] == [],
      "retained independent 641-check admission")

paired_raw = compressed("A20-raster-run1/report.json.gz",
    "20651ce04553a3cfd1d56c9c8e997765072d3d0223b1b5cc28aff0816cb0bbf9")
paired = json_bytes(paired_raw)
check(len(paired["cases"]) == 96 and paired["status"] == "passed" and
      paired["errors"] == [], "retained 96-pair report")
check(sum(case["compared_pixels"] for case in paired["cases"]) == 307095606,
      "paired pixel total")

# Existing production code/data is compared directly with its base objects.
# The only altered common production implementation is the private UI painter.
base_names = git("ls-tree", "-r", "--name-only", BASE).decode().splitlines()
protected = [path for path in base_names
             if path.startswith(("include/", "src/", "plugins/", "assets/", "data/"))]
old_blobs = git_blobs(protected, BASE)
protected_changes = [path for path in protected if (ROOT / path).read_bytes() != old_blobs[path]]
check(not protected_changes, "all original core/plugin/asset/data bytes preserved")
production_references = []
for path in paths:
    if path.startswith(("include/", "src/", "apps/", "plugins/")) and path.endswith((".h", ".cpp")):
        if b"CausalContactGrid" in blobs[path]:
            production_references.append(path)
check(production_references == ["include/hammond/research/CausalContactGrid.h",
                                "src/research/CausalContactGrid.cpp"],
      "no Engine/adapter research-grid reference")

# Bind all retained original receipts/logs used here to their published blobs.
# Implementation-publication and hosted observations necessarily postdate it.
published_evidence = [path for path in bindings if path in set(all_published)]
evidence_blobs = git_blobs(sorted(published_evidence))
for path, raw in evidence_blobs.items():
    check(sha(raw) == bindings[path]["sha256"], f"preserved published evidence: {path}")
check(hosted["commit"] == COMMIT and len(hosted["runs"]) == 3, "hosted snapshot source/runs")
jobs = [job for run in hosted["runs"] for job in run["jobs"]]
check(len(jobs) == 13, "thirteen current-source job records")

report = {
    "schema_version": 1,
    "reviewer": "A43 /root/w08_a43",
    "recorded_utc": datetime.now(timezone.utc).isoformat(),
    "cwd": str(ROOT),
    "method": "Independent Git-blob/current-file SHA-256 comparison and retained-log inspection; no build, test-body execution, capture, fetch or original evidence edits.",
    "git": {"commit": COMMIT, "tree": TREE, "parent": BASE,
            "observed_local_head": git("rev-parse", "HEAD").decode().strip(),
            "publication_receipt": "implementation-publication.json",
            "remote_verification_boundary": "Remote publication/fetch is root's retained observation; A43 independently verified local published Git objects and their input bytes."},
    "publication_inputs": {"files": 505, "complete_tracked_scope": True,
        "inventory_raw_sha256": publication["raw_sha256"],
        "all_match_published_and_working_bytes": not any("source:" in e for e in errors),
        "workflows": publication["workflow_sha256"]},
    "lineage": {"original_to_post_review": first_changes,
                "post_review_to_publication": last_changes,
                "resource_original_reconstructed_by_appending_hex": "0a",
                "resource_binary_sha256": whitespace["after_binary_sha256"],
                "original_seconds": original["ctest_wall_seconds"],
                "post_review_seconds": final["ctest_wall_seconds"],
                "setup_source_sha256": setup["source_sha256"],
                "setup_source_boundary": "The CLI setup receipt binds 015a1ef3..., followed by the documented docstring correction to cda3e12e...; the post-review full suite qualifies final bytes. Older A21/A24 test-source claims are historical. A23/A28 fixture fcb153c8... remains original; the newline/binary/affected-test bridge admits 201a0772... without rewriting it."},
    "logs": log_summaries,
    "negative_setup": negative,
    "positive_setup": positive,
    "resource": {"A28_identities_checked": len(resource_audit["identities"]),
                 "historical_fixture_exception": resource_rebased,
                 "api_scopes": resource_report["calls_checked"],
                 "allocation_totals": resource_report["allocation_totals"],
                 "sizes": resource_report["sizes"]},
    "gallery": {**gallery_checks, "payload_members": 57, "captures": 12,
                "admission_checks": 641, "binary_sha256": source_report["binary_sha256"],
                "later_test_changes_overlap_production": [],
                "paired_cases": 96, "paired_pixels": 307095606,
                "limits": "No recapture or renewed full-frame inspection; original BMP bytes unavailable; masks, metrics and visual judgments retain A25/A26/A29 scopes."},
    "preserved_original_production_inputs": len(protected),
    "protected_production_changes": protected_changes,
    "production_grid_references": production_references,
    "retained_published_evidence_checked": len(published_evidence),
    "evidence_bindings": bindings,
    "hosted_snapshot": {"source": COMMIT, "runs": 3, "jobs": 13,
        "run_statuses": [{"id": r["id"], "name": r["name"],
                          "status": r["status"], "conclusion": r["conclusion"]}
                         for r in hosted["runs"]],
        "boundary": "Retained initial observation only, not a fresh hosted query; in-progress jobs are not passes. Exact-source final hosted gates remain with root."},
    "limitations": ["Finite synthetic grid, no converter/filter/audio/Engine route, full-organ indefinite capacity or callback deadline.",
                    "Upper-rack inset scope only; whole-interface literal 1:1, physical display/input/accessibility and calibrated fidelity remain open.",
                    "Hashes and retained logs support evidence lineage, not a hermetic rebuild or newly executed test/visual/platform qualification."],
    "errors": errors,
    "status": "passed" if not errors else "failed",
}
destination = REPORTS / "A43-source-audit.json"
destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
print(json.dumps({"status": report["status"], "errors": errors,
                  "report": str(destination.relative_to(ROOT)),
                  "report_sha256": sha(destination.read_bytes()),
                  "publication_inputs": 505, "workflows": 3,
                  "preserved_production_inputs": len(protected),
                  "published_evidence": len(published_evidence)}, indent=2))
raise SystemExit(bool(errors))
