"""Assemble source-bound review from retained CI results; no test execution."""
from pathlib import Path
from datetime import datetime, timezone
import gzip
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[4]
SOURCE = "523c1979334b0fbb624ce120128a0b8ada078383"


def read(name):
    return json.loads((BASE / name).read_text())


def latest(pattern):
    return json.loads(sorted(BASE.glob(pattern))[-1].read_text())


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write(name, record):
    path = BASE / name
    assert not path.exists(), path
    path.write_text(json.dumps(record, indent=2) + "\n")


source = read("api-source.json")
source_review = read("source-review.json")
for bound_file in source_review["files"]:
    assert digest((REPO / bound_file["path"]).read_bytes()) == bound_file["sha256"], bound_file["path"]
run = latest("api-run-*.json")
job_payload = latest("api-jobs-*.json")
artifact_payload = latest("api-artifacts-*.json")
required = source_review["required_families"]
assert run["id"] == 44043394024 and run["head_sha"] == SOURCE
assert run["status"] == "completed" and run["run_attempt"] == 1
assert job_payload["total_count"] == 6
assert {x["name"] for x in job_payload["jobs"]} == set(required)
assert {x["id"] for x in job_payload["jobs"]} == {x["id"] for x in read("api-jobs-001.json")["jobs"]}
assert all(x["status"] == "completed" and x["run_attempt"] == 1 and x["head_sha"] == SOURCE for x in job_payload["jobs"])
assert artifact_payload["total_count"] == 6
assert all(x["workflow_run"]["head_sha"] == SOURCE and x["workflow_run"]["id"] == run["id"] for x in artifact_payload["artifacts"])
artifact_names = {
    "Release (Linux GCC)": "ci-ubuntu-24.04-release-1",
    "Release (macOS AppleClang)": "ci-macos-15-release-1",
    "Release (macOS Intel AppleClang)": "ci-macos-15-intel-release-1",
    "Release (Windows MSVC)": "ci-windows-2022-release-1",
    "Linux GCC ASan + UBSan + leaks": "ci-linux-gcc-sanitizers-1",
    "Complete R4 waveform qualification (Linux GCC)": "rotary-waveform-full-linux-1",
}
workflow = (BASE / "workflow.yml").read_text()
required_registration = re.search(r"  HAMMOND_REGISTRATION_CTESTS: [^\n]+\n((?:    [^\n]+\n)+)", workflow)[1].split()
library = ["test_standalone_library_" + name for name in ("model", "recall", "roundtrip", "session", "storage")]
jobs = []
method_matrix = []
inventories = []
optional_skips = []
for family in required:
    job = next(dict(x) for x in job_payload["jobs"] if x["name"] == family)
    review = read("job-" + str(job["id"]) + ".review.json")
    log = read("job-" + str(job["id"]) + ".log.receipt.json")
    log_bytes = gzip.decompress((BASE / log["path"]).read_bytes())
    assert digest(log_bytes) == log["raw_sha256"] and len(log_bytes) == log["raw_bytes"]
    assert review["source_recorded_as_standalone_line"]
    artifact = next(x for x in artifact_payload["artifacts"] if x["name"] == artifact_names[family])
    aid = artifact["id"]
    ar = read("artifact-" + str(aid) + ".review.json")
    receipt = read("artifact-" + str(aid) + ".receipt.json")
    archive = (BASE / receipt["archive"]).read_bytes()
    assert digest(archive) == receipt["archive_sha256"] == artifact["digest"].removeprefix("sha256:")
    job["elapsed_seconds"] = (datetime.fromisoformat(job["completed_at"].replace("Z", "+00:00")) - datetime.fromisoformat(job["started_at"].replace("Z", "+00:00"))).total_seconds()
    job["complete_log"] = log
    job["log_review"] = "job-" + str(job["id"]) + ".review.json"
    job["artifact_id"] = aid
    job["artifact_receipt"] = "artifact-" + str(aid) + ".receipt.json"
    job["artifact_review"] = "artifact-" + str(aid) + ".review.json"
    job["platform_conditional_skipped_steps"] = [x["name"] for x in job["steps"] if x["conclusion"] == "skipped"]
    if "junit" in ar:
        records = review["ctest"]["records"]
        names = {x["name"] for x in records}
        passed_names = {x["name"] for x in records if x["result"] == "Passed"}
        assert names == {x["name"] for x in ar["junit"]["records"]}
        assert ar["discovery_matches_executed_names"] and not any(x["disabled"] for x in ar["discovered_ctests"])
        assert ar["requested_method_suites_all_present"]
        assert all(x["count_matches_exact_source"] and x["result"] == "OK" and x["skipped_methods"] == 0 for x in ar["requested_method_suites"])
        inventories.append(names)
        job["ctest"] = {key: value for key, value in review["ctest"].items() if key != "records"}
        job["junit"] = ar["junit"]["attributes"]
        job["all_twelve_registration_apron_gates_passed"] = set(required_registration) <= passed_names
        job["all_five_library_suites_passed"] = set(library) <= passed_names
        method_matrix.append({"job_id": job["id"], "family": family, "artifact_id": aid, "suites": ar["requested_method_suites"]})
        optional_skips.append({"family": family, "artifact_id": aid, "suites": [x for x in ar["internal_unittest_summaries"] if x["skipped_methods"]], "standard_library_step": ar["standard_library_apron"]})
    jobs.append(job)

r4 = read("r4-full-review.json")
windows = read("windows-unicode-generator-review.json")
sanitizers = read("sanitizer-execution-review.json")
prior = read("prior-evidence-before.json")
prior_checks = []
for entry in prior["files"]:
    raw = (REPO / entry["path"]).read_bytes()
    assert len(raw) == entry["bytes"] and digest(raw) == entry["sha256"], entry["path"]
    prior_checks.append({**entry, "unchanged": True})
write("prior-evidence-final-verification.json", {"recorded_utc": datetime.now(timezone.utc).isoformat(), "all_unchanged": True, "files": prior_checks})
observations = [json.loads(p.read_text()) for p in sorted(BASE.glob("poll-*-observation.json"))]
receipts = [read("artifact-" + str(x["id"]) + ".receipt.json") for x in artifact_payload["artifacts"]]
all_success = all(x["conclusion"] == "success" for x in jobs)
report = {
    "schema_version": 1, "worker": "A56", "agent": "/root/w10_a56", "continuation_of_accepted_worker": True, "additional_agent_credit": 0,
    "recorded_utc": datetime.now(timezone.utc).isoformat(),
    "status": "COMPLETE_EXACT_SOURCE_CORE_REVIEW_SIX_SUCCESSES" if all_success else "COMPLETE_EXACT_SOURCE_CORE_REVIEW_WITH_FAILURES",
    "decision": "All six required Core families independently reviewed at exact published 523c1979, attempt 1. Results remain source-specific; root owns final acceptance and other workflow qualification.",
    "published_source": {"commit": SOURCE, "tree": source["tree"]["sha"], "parents": [x["sha"] for x in source["parents"]], "url": source["html_url"], "api_url": source["url"]},
    "workflow": {"path": ".github/workflows/ci.yml", "source_url": "https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/" + SOURCE + "/.github/workflows/ci.yml", **next(x for x in source_review["files"] if x["path"] == ".github/workflows/ci.yml"), "unchanged_from_d2ed03b9": source_review["workflow_unchanged_from_d2ed03b9"], **source_review["workflow_bounds"]},
    "source_review": "source-review.json", "source_method_inventory": "source-method-inventory.json", "source_files_stable_during_review": True, "protected_roots": source_review["protected_roots"], "protected_scope": source_review["protected_scope"],
    "run": {key: run.get(key) for key in ("id", "name", "path", "head_sha", "head_branch", "event", "status", "conclusion", "run_number", "run_attempt", "created_at", "run_started_at", "updated_at", "html_url", "url", "jobs_url", "artifacts_url")},
    "required_families": required, "terminal_jobs": len(jobs), "successful_jobs": sum(x["conclusion"] == "success" for x in jobs), "failed_jobs": sum(x["conclusion"] == "failure" for x in jobs), "cancelled_jobs": sum(x["conclusion"] == "cancelled" for x in jobs), "retried_jobs": 0,
    "all_first_attempt_job_ids_retained": True, "all_five_ctest_inventories_identical": all(x == inventories[0] for x in inventories), "required_registration_apron_gates": required_registration, "required_library_suites": library,
    "jobs": jobs, "actual_source_method_results": method_matrix, "optional_internal_method_skips": optional_skips,
    "windows_unicode_generator": {"review": "windows-unicode-generator-review.json", "artifact_id": windows["artifact_id"], "source_commit": windows["qualification"]["source_commit"], "source_tree": windows["qualification"]["source_tree"], "qualification_sha256": windows["qualification_sha256"], "payloads_saved": windows["payloads_saved"], "all_payloads_match_exact_published_source": windows["all_payloads_match_exact_published_source"], "actual_generation_records": windows["actual_generation_records"], "generation_summary": windows["generation_summary"], "protected_source_refusal": windows["qualification"]["protected_source_refusal"], "source_pack_unchanged": windows["qualification"]["source_pack_unchanged"], "generator_sha256": windows["qualification"]["generator_sha256"], "source_archive_sha256": windows["qualification"]["source_archive_sha256"], "compile_groups_all_utf8": windows["compile_groups_all_utf8"], "compiled_source_definition_verified": windows["compiled_source_definition_verified"], "stdout_lf_only": windows["stdout_lf_only"], "generate_and_protected_stderr_empty": windows["generate_and_protected_stderr_empty"], "scope": windows["scope"]},
    "sanitizer_execution": {"review": "sanitizer-execution-review.json", "checks": sanitizers["checks"], "ctest_seconds": sanitizers["ctest_seconds"], "passed_ctests": sanitizers["passed_ctests"], "scope": sanitizers["scope"]},
    "r4_execution": {"review": "r4-full-review.json", **{key: r4[key] for key in ("artifact_id", "status", "completed", "mode", "wall_seconds", "failures", "groups", "native_totals", "report_admission_self_test_methods", "report_admission_self_test_seconds", "scope", "separate_gates", "native_report_totals_match_qualification", "original_stdout_stderr_digests_verified", "source_stability_verified")}, "native_process_exit_code": r4["native_process"]["exit_code"], "native_process_timed_out": r4["native_process"]["timed_out"], "source_before": {key: r4["source_before"][key] for key in ("git_head", "git_tree", "dirty_overlay")}, "source_after": {key: r4["source_after"][key] for key in ("git_head", "git_tree", "dirty_overlay")}},
    "artifacts": artifact_payload,
    "retention": {"complete_primary_logs": len(jobs), "complete_job_steps_and_timings": True, "raw_log_bytes": sum(x["complete_log"]["raw_bytes"] for x in jobs), "gzip_log_bytes": sum(x["complete_log"]["gzip_bytes"] for x in jobs), "log_gzip_roundtrips_verified": True, "downloaded_original_zip_count": len(receipts), "downloaded_original_zip_bytes": sum(x["archive_bytes"] for x in receipts), "all_downloaded_zip_digests_match_API": True, "job_observations": [p.name for p in sorted(BASE.glob("api-jobs-*.json"))], "poll_interval_seconds": [x["seconds_since_previous"] for x in observations if x["seconds_since_previous"] is not None], "final_poll_timing_note": "The final request start was not saved after one optional endpoint rejection; final successful run/jobs/artifact payloads and the explicit observation note are retained.", "optional_read_only_connector_error": "optional-individual-job-read-error.json"},
    "prior_evidence_preservation": {"manifest": "prior-evidence-before.json", "final_verification": "prior-evidence-final-verification.json", "verified_unchanged_files": len(prior_checks), "accepted_A56_note_and_all_prior_A56_evidence_unchanged": True, "original_cf87_Core": "5 success/1 Windows failure; 207/209 Windows CTests;Unicode generator skipped. This failure remains a failure.", "d2ed_Core": "Six source-specific successes remain bound to d2ed; separate native Windows 75/78 failure remains historical failure.", "old_passes_promoted": False},
    "historical_outcomes_not_promoted": ["Original console full local 246/247 run remains failed.", "Earlier local build, affected-test and capture passes retain their own frozen inputs.", "Earlier A56 array and combined regression receipts remain immutable source-specific Python evidence.", "Prior hosted failures, cancellations and successes retain their original sources and attempts."],
    "execution_authority": {"root_final_acceptance_and_publication": True, "reviewer_git_or_ci_mutation": False, "reviewer_retries": 0, "reviewer_source_changes": False, "reviewer_local_product_build_test_or_native_execution": False, "writes": "Only new reports/A56-final-hosted evidence; no original note/report/evidence edits."},
    "remaining_limits": ["These six Core families do not replace independently owned native standalone or VST3 workflow reviews.", "The actual 71/41/45 method receipts are source/comparator Python suites; native raster execution is a separate workflow.", "CTest 209/209 does not erase disclosed optional internal-method skips.", "Real devices, display/DPI/accessibility, callback deadlines/retirement, measured physical fidelity, rights and signed distribution remain separate.", "Literal whole-interface 1:1 remains unmet and unwaived.", "Any later changed source requires its own execution qualification."],
}
assert all_success and run["conclusion"] == "success"
assert len(inventories) == 5 and report["all_five_ctest_inventories_identical"]
assert all(x["ctest"]["count"] == x["ctest"]["passed"] == 209 and not x["ctest"]["nonpassed"] and x["all_twelve_registration_apron_gates_passed"] and x["all_five_library_suites_passed"] for x in jobs if "ctest" in x)
write("core-523c1979-admission.json", report)

rows = []
for job in jobs:
    result = "209/209 CTests" if "ctest" in job else "Full R4; 24/24 partitions"
    seconds = job["ctest"]["wall_seconds"][0] if "ctest" in job else r4["wall_seconds"]
    rows.append("| [" + job["name"] + "](" + job["html_url"] + ") | Success | " + result + " | " + format(seconds, ".2f") + " |")
method_rows = []
for item in method_matrix:
    suites = {x["name"]: x for x in item["suites"]}
    values = [str(suites[name]["methods"]) + " / " + format(suites[name]["seconds"], ".3f") + " s" for name in ("python_test_compare_performance_plate", "python_test_compare_header_material", "python_test_capture_standalone_interface")]
    method_rows.append("| " + item["family"] + " | " + " | ".join(values) + " |")
readme = """# A56 final published-source Core qualification

All six required Core families passed on their original attempt for published commit `523c1979334b0fbb624ce120128a0b8ada078383`, tree `893441fe87859b9dbad81a5d81a453f7c96030f8`. This is the same accepted A56 worker continuation, with no additional agent credit. Root owns final acceptance and the separate native standalone/VST3 results.

The source has ordered parents `8189a49eacab5d4e6ce6c178862e83b03bdec437` and `54859886268ce83c36f359c43327f7c72a77ae82`. GitHub commit metadata and local Git objects agree. The workflow and the protected core, plugin, data and build-definition objects remain identical to the reviewed predecessor. Current P1/header/capture source inventories are 71/41/45 methods. Earlier execution results were not used as passes for this source.

## Six terminal jobs

Run: [CI 44043394024, attempt 1](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/44043394024).

| Required family | Outcome | Actual gate result | Execution seconds |
| --- | --- | --- | ---: |
""" + "\n".join(rows) + """

Execution seconds are the CTest wall time, or the full R4 qualification wall time in the R4 row. Exact job/step starts, completions and durations are retained in the API payloads and admission report. The initially queued Intel job and every observation remain in the evidence. There were no retries, cancellations or replaced outcomes.

All five unfiltered CTest inventories contain the same 209 names. Each includes the twelve required registration/apron gates and five library suites, all passing. Complete original job logs and every original artifact ZIP are retained; each ZIP SHA-256 matches the GitHub artifact digest.

## Actual Python method executions

Each cell shows the hosted method count and reported unittest duration. All fifteen suite executions below ended `OK` with zero method skips, matching the exact published-source inventories.

| Core family | P1 | Header | Capture |
| --- | ---: | ---: | ---: |
""" + "\n".join(method_rows) + """

These source/comparator suites do not substitute for the native raster workflow. Other Python suites have optional method skips, retained explicitly in `optional_internal_method_skips` and the full artifact reviews. No CTest was skipped or disabled. The Linux standard-library-only apron step passed its 25- and 14-method suites while disclosing six and two optional skips.

## Windows Unicode generator

The actual MSVC generator ran from a Unicode source checkout bound to this exact commit and tree. Its build metadata contains `/utf-8` and the intended compiled Unicode source definition. It emitted 25 JSON records and saved all 24 payloads; every payload byte count and digest matches the committed starter pack. Output is LF-only, and generation/refusal stderr is empty. A protected-source destination was refused with zero attempted or committed files, and the source pack remained unchanged. Complete command records, executable/archive identities and payload inventories are retained in `windows-unicode-generator-review.json` and the original Windows ZIP.

## Strict sanitizer and full R4 evidence

The sanitizer job built Debug with ASan and UBSan, with leak detection and halt-on-error options enabled and LSAN exit code 23. Retained compiler/linker lines prove instrumentation of Engine, LibraryModel and its test. All 209 registered tests passed. This covers the Core/headless sanitizer job; native SDL sanitizer qualification is separate.

The R4 run completed full mode with four rates and 24 partitions. Its 38,010,000 partition comparisons all matched; all 16 qualification groups passed. The strict report-admission suite passed 14 methods. Original native stdout/stderr digests match the retained receipt, native totals match the qualification, and source commit/tree are unchanged before and after. The artifact retains selected decimal crosschecks and static-grid evidence. Transaction lifecycle, R5 audible policy, R6 device deadlines and physical fidelity remain separate gates.

## Retention and preserved history

`core-523c1979-admission.json` is the source-bound six-job admission record. `source-review.json` and `source-method-inventory.json` bind the workflow and reviewed source. `job-*.log.gz` preserve complete connector log text losslessly, including BOM/carriage returns; corresponding receipts record raw and compressed hashes and round-trip verification. `artifact-*.zip` are the original archives with receipt and entry-level reviews. API snapshots retain all steps, attempts and timings. `evidence-inventory.json` hashes all evidence files except itself.

All 128 prior A56 evidence files and accepted records were rehashed and remain unchanged. The original cf87 Core Windows failure remains 207/209 with its skipped Unicode generator. The d2ed native Windows 75/78 failure remains historical failure. The original local 246/247 failure and all prior source-specific results remain intact. No accepted A56 note was rewritten.

A56 performed read-only GitHub/source inspection and evidence retention, with no source changes, local product tests/builds/native execution, Git mutation or CI mutation. Literal whole-interface 1:1 remains unmet and unwaived. Real-device, display/DPI/accessibility, callback, measured physical fidelity, rights and signed-distribution limits remain separate. Any later source change requires new qualification.
"""
(BASE / "README.md").write_text(readme)
inventory = []
for path in sorted(BASE.iterdir()):
    if path.is_file() and path.name != "evidence-inventory.json":
        raw = path.read_bytes()
        inventory.append({"path": path.name, "bytes": len(raw), "sha256": digest(raw)})
write("evidence-inventory.json", {"recorded_utc": datetime.now(timezone.utc).isoformat(), "scope": "All evidence files in this directory except this inventory; no recursive self-hash.", "files": inventory, "total_files": len(inventory), "total_bytes": sum(x["bytes"] for x in inventory)})
print(json.dumps({"status": report["status"], "terminal_jobs": 6, "successes": 6, "prior_files_unchanged": len(prior_checks), "retention": report["retention"], "final_artifacts": [{"path": name, "bytes": (BASE / name).stat().st_size, "sha256": digest((BASE / name).read_bytes())} for name in ("core-523c1979-admission.json", "README.md", "evidence-inventory.json")]}, indent=2))
