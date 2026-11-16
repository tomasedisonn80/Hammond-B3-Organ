#!/usr/bin/env python3
"""Read-only admission of retained provider evidence and the repaired source.

This audits decoded GitHub responses already acquired by A58. It makes no
network call, runs no project test, and writes only its explicitly named receipt.
"""
from __future__ import annotations

import ast
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[4]
REPORTS = Path(__file__).resolve().parent
SOURCE = "2f57723d9ec806fe8f721c317ef8c1a38d63b532"
TREE = "cee5fdc4b07d95185ebd9e4d1c5f236f88a787f9"
PARENT = "af2b74760ee195c9497b314a1a29172f5238dd44"
EXPECTED_RUNS = {43785480005: 5, 43785480050: 5, 43785480026: 3}
CORE = {133032021212, 133032021368, 133032021576, 133032022089}
NATIVE_RELEASE = {133032021703, 133032021730, 133032021840, 133032021960}
NATIVE_SANITIZER = 133032021440
VST3 = {133032021170: 7, 133032021326: 8, 133032021360: 7}
R4 = 133032021399
CAUSAL_NAMES = {
    "test_causal_contact_grid", "test_causal_contact_grid_lifecycle",
    "test_causal_contact_grid_resources", "python_test_causal_contact_grid_cli",
    "python_test_causal_contact_grid_differential",
    "python_test_causal_contact_grid_reference",
}


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def json_file(name: str):
    return json.loads((REPORTS / name).read_bytes())


def source_blobs(commit: str, paths: list[str]) -> dict[str, bytes]:
    requests = "".join(f"{commit}:{path}\n" for path in paths).encode()
    data = subprocess.check_output(
        ["git", "cat-file", "--batch"], input=requests, cwd=ROOT)
    cursor = 0
    result = {}
    for path in paths:
        end = data.index(b"\n", cursor)
        header = data[cursor:end].decode().split()
        assert len(header) == 3 and header[1] == "blob", (path, header)
        count = int(header[2])
        cursor = end + 1
        result[path] = data[cursor:cursor + count]
        cursor += count
        assert data[cursor:cursor + 1] == b"\n"
        cursor += 1
    assert cursor == len(data)
    return result


def clean_line(line: str) -> str:
    return re.sub(r"^\d{4}-\d\d-\d\dT\S+Z ?", "", line)


def main() -> None:
    packed = (REPORTS / "A58-provider-evidence.json.gz").read_bytes()
    unpacked = gzip.decompress(packed)
    provider = json.loads(unpacked)
    commit = provider["commit"]
    assert commit["sha"] == SOURCE and commit["tree"]["sha"] == TREE
    assert [p["sha"] for p in commit["parents"]] == [PARENT]
    assert subprocess.check_output(
        ["git", "rev-parse", SOURCE + "^{tree}"], cwd=ROOT, text=True).strip() == TREE

    qualification = json_file("windows-repair-qualification.json")
    inventory_bytes = gzip.decompress(
        (REPORTS / "windows-repair-code-inputs.json.gz").read_bytes())
    inventory = json.loads(inventory_bytes)
    assert len(inventory) == 505
    assert digest(inventory_bytes) == qualification["source_inventory"]["raw_sha256"]
    paths = sorted(inventory)
    committed = source_blobs(SOURCE, paths)
    old = source_blobs(PARENT, paths)
    changed = []
    for path, expected in inventory.items():
        assert digest((ROOT / path).read_bytes()) == expected, ("worktree", path)
        assert digest(committed[path]) == expected, ("published", path)
        if old[path] != committed[path]:
            changed.append(path)
    assert sorted(changed) == [
        "tests/test_contact_switching_io.py", "tools/contact_switching_io.py"]

    workflows = qualification["workflow_sha256"]
    workflow_new = source_blobs(SOURCE, sorted(workflows))
    workflow_old = source_blobs(PARENT, sorted(workflows))
    for path, expected in workflows.items():
        assert digest(workflow_new[path]) == expected
        assert workflow_new[path] == workflow_old[path] == (ROOT / path).read_bytes()
    source_checks = {
        "input_count": 505,
        "inventory_raw_sha256": digest(inventory_bytes),
        "all_worktree_and_published_inputs_match_inventory": True,
        "changed_inputs_from_initial_publication": sorted(changed),
        "unchanged_other_inputs_from_initial_publication": 503,
        "workflow_sha256": workflows,
        "all_three_workflows_match_parent_and_worktree": True,
    }

    prior = json_file("A48-hosted-audit.json")
    native_workflow = workflow_new[".github/workflows/standalone.yml"].decode()
    mapping_text = native_workflow.split("HAMMOND_SANITIZER_TEST_TARGETS: >-", 1)[1].split("    steps:", 1)[0]
    mappings = dict(re.findall(r"^\s+(test_\S+)=(\S+)\s*$", mapping_text, re.M))
    assert len(mappings) == 22
    assert mappings == prior["source_checks"]["audited_sanitizer_mappings"]
    required_match = re.search(
        r'required = (\{"test_standalone_midi_cli".*?\})', native_workflow, re.S)
    assert required_match
    required_release = ast.literal_eval(required_match.group(1))
    assert len(required_release) == 32
    for path, row in prior["source_checks"]["source_files"].items():
        assert digest(source_blobs(SOURCE, [path])[path]) == row["audited_sha256"]
    source_checks.update({
        "native_sanitizer_mappings": mappings,
        "native_release_required_names": sorted(required_release),
        "all_six_A48_selection_sources_unchanged_at_repaired_commit": True,
        "selection_and_timeout_preservation": "Exact six-source identity retains A48's separately audited prior-gate and timeout comparison; this script does not repeat that earlier comparison.",
    })

    counts = {row["run_id"]: row for row in json_file("A58-job-counts.json")}
    root_receipt = json_file("hosted-2f57723-complete.json")
    root_runs = {row["id"]: row for row in root_receipt["runs"]}
    assert root_receipt["commit"] == SOURCE
    assert root_receipt["successful_jobs"] == root_receipt["total_jobs"] == 13
    jobs = []
    run_summaries = []
    test_re = re.compile(
        r"\b(\d+)/(\d+)\s+Test\s+#(\d+):\s+(\S+)\s+\.+\s+(Passed)\s+([0-9.]+)\s+sec")
    seen_runs = set()
    for run in provider["runs"]:
        meta = run["metadata"]
        run_id = meta["id"]
        assert run_id in EXPECTED_RUNS and run_id not in seen_runs
        seen_runs.add(run_id)
        assert meta["head_sha"] == SOURCE and meta["head_branch"] == "main"
        assert meta["event"] == "push" and meta["run_attempt"] == 1
        assert meta["status"] == "completed" and meta["conclusion"] == "success"
        observed_jobs = run["jobs"]["jobs"]
        assert len(observed_jobs) == EXPECTED_RUNS[run_id] == counts[run_id]["total_count"]
        assert sorted(j["id"] for j in observed_jobs) == sorted(counts[run_id]["job_ids"])
        assert sorted(j["id"] for j in observed_jobs) == sorted(j["id"] for j in root_runs[run_id]["jobs"])
        run_summaries.append({key: meta[key] for key in [
            "id", "name", "head_sha", "head_branch", "event", "run_attempt",
            "status", "conclusion", "html_url", "created_at", "updated_at"]})
        for job in observed_jobs:
            job_id = job["id"]
            assert job["run_id"] == run_id
            assert job["status"] == "completed" and job["conclusion"] == "success"
            assert all(s["status"] == "completed" and s["conclusion"] in {"success", "skipped"}
                       for s in job["steps"])
            log = provider["logs"][str(job_id)]
            lines = log.splitlines()
            actual = [(n, clean_line(line)) for n, line in enumerate(lines, 1)
                      if "\x1b" not in line]
            assert any(line == SOURCE for _, line in actual), (job_id, "recorded revision")
            results = []
            for number, line in actual:
                match = test_re.search(line)
                if match:
                    a, total, index, name, status, seconds = match.groups()
                    results.append({"line": number, "ordinal": int(a), "total": int(total),
                                    "test_index": int(index), "name": name,
                                    "status": status, "seconds": float(seconds)})
            totals = [(n, line, int(m.group(1))) for n, line in actual
                      if (m := re.search(r"100% tests passed(?:, 0 tests failed)? out of (\d+)", line))]
            wall = [(n, line, float(m.group(1))) for n, line in actual
                    if (m := re.search(r"Total Test time \(real\) =\s*([0-9.]+) sec", line))]
            row = {"job_id": job_id, "run_id": run_id, "name": job["name"],
                   "url": f"https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/{run_id}/job/{job_id}",
                   "conclusion": job["conclusion"],
                   "decoded_log_bytes": len(log.encode()), "decoded_log_sha256": digest(log.encode()),
                   "decoded_log_lines": len(lines), "actual_recorded_revision_matches": True,
                   "steps": job["steps"], "ctest_results": results,
                   "summary_lines": [{"line": n, "text": line} for n, line, _ in totals + wall]}
            names = {x["name"] for x in results}
            if job_id != R4:
                expected = (185 if job_id in CORE else 53 if job_id in NATIVE_RELEASE
                            else 22 if job_id == NATIVE_SANITIZER else VST3[job_id])
                assert len(results) == len(names) == expected, (job_id, len(results), expected)
                assert len(totals) == len(wall) == 1 and totals[0][2] == expected
                assert {x["ordinal"] for x in results} == set(range(1, expected + 1))
                assert all(x["total"] == expected for x in results)
                row.update({"ctest_passed": expected, "ctest_total": expected,
                            "ctest_wall_seconds": wall[0][2]})
            if job_id in CORE:
                assert CAUSAL_NAMES <= names
                row["six_causal_suites_pass"] = True
            if job_id in NATIVE_RELEASE:
                assert required_release <= names
                row["all_32_required_native_names_executed"] = True
            if job_id == NATIVE_SANITIZER:
                assert names == set(mappings)
                assert any("Discovered exactly 22 built interface" in line for _, line in actual)
                assert any("Verified the instrumented native probe completed 10 subprocesses and all 7 lifecycle scenarios." == line
                           for _, line in actual)
                for source in ["native_tests/test_standalone_upper_rack_material_raster.cpp", "InstrumentView.cpp"]:
                    assert any("-c " in line and source in line and "-fsanitize=address,undefined" in line
                               for _, line in actual), source
                row["sanitizer_observations"] = {
                    "exact_22_mapped_names_executed": True,
                    "upper_fixture_and_painter_compile_commands_instrumented": True,
                    "native_driver_10_subprocesses_and_7_lifecycle_scenarios_reported": True,
                    "configuration": "Release; MIDI OFF; dummy SDL execution",
                    "policy": prior["source_checks"]["sanitizer_runtime_policy"],
                }
            if job_id in NATIVE_RELEASE | {NATIVE_SANITIZER}:
                fixture_lines = [(n, line[line.index('{'):]) for n, line in actual
                                 if '{"schema":1,"protocol":"upper-rack-material-v1.1"' in line]
                assert len(fixture_lines) == 1
                fixture = json.loads(fixture_lines[0][1])
                assert fixture["status"] == "passed" and fixture["cases"] == 30 and fixture["checks"] == 58876889
                row["upper_fixture"] = {"line": fixture_lines[0][0], "result": fixture}
                row["packaging_lines"] = [{"line": n, "text": line} for n, line in actual
                                          if re.search(r"Verified \d+ installed files, MIDI", line)]
            if job_id in VST3:
                validator = [(n, line) for n, line in actual if "Result: 47 tests passed, 0 tests failed" in line]
                assert len(validator) == 1
                row["vst3_validator"] = {"passed": 47, "failed": 0, "line": validator[0][0], "text": validator[0][1]}
            if job_id == R4:
                records = [(n, json.loads(line)) for n, line in actual if line.startswith('{"status": "pass", "mode": "full"')]
                assert len(records) == 1 and records[0][1]["failures"] == []
                row["full_R4"] = {"line": records[0][0], "result": records[0][1]}
            row["toolchain_lines"] = [{"line": n, "text": line} for n, line in actual
                                      if re.search(r"(CXX compiler identification is|cmake version |ctest version |^Python 3\.)", line)]
            jobs.append(row)
    assert seen_runs == set(EXPECTED_RUNS) and len(jobs) == 13
    native_sets = [{x["name"] for x in job["ctest_results"]} for job in jobs if job["job_id"] in NATIVE_RELEASE]
    assert all(values == native_sets[0] for values in native_sets)

    retained_windows = gzip.decompress((REPORTS / "windows-core-2f57723.log.gz").read_bytes())
    assert retained_windows == provider["logs"]["133032022089"].encode()
    failure = gzip.decompress((REPORTS / "windows-core-af2b747.log.gz").read_bytes())
    assert digest(failure) == "2858f8f90bb79736630bf72b0fdaca93156baf9f8496afe83cb7500adc47ba6d"
    assert b"input changed after path preflight" in failure
    assert b"1 tests failed out of 185" in failure
    windows_job = next(job for job in jobs if job["job_id"] == 133032022089)
    windows_tests = {row["name"]: row for row in windows_job["ctest_results"]}
    affected = {name: windows_tests[name] for name in [
        "python_test_contact_switching_io", "python_test_contact_reference_install", "python_test_contact_switching_study"]}

    result = {
        "schema_version": 1, "reviewer": "A58", "wave": 10,
        "audit_kind": "Independent repaired-source hosted admission; retained decoded provider responses",
        "source_commit": SOURCE, "source_tree": TREE, "parent": PARENT,
        "observed_utc": provider["observed_utc"], "total_jobs": 13, "successful_jobs": 13,
        "run_summaries": run_summaries, "job_list_completeness": list(counts.values()),
        "jobs": sorted(jobs, key=lambda row: row["job_id"]), "source_checks": source_checks,
        "root_completion_receipt_independently_agrees": True,
        "windows_repair": {"log_matches_roots_retained_bytes": True,
                           "decoded_bytes": len(retained_windows), "decoded_sha256": digest(retained_windows),
                           "affected_ctest_results": affected,
                           "initial_failure_retained_unchanged": True,
                           "initial_failed_source": PARENT, "initial_failed_log_sha256": digest(failure)},
        "retained_evidence": {
            "A58-provider-evidence.json.gz": {"raw_bytes": len(unpacked), "raw_sha256": digest(unpacked),
                                               "gzip_bytes": len(packed), "gzip_sha256": digest(packed)},
            "A58-job-counts.json": {"sha256": digest((REPORTS / "A58-job-counts.json").read_bytes())},
            "auditor_sha256": digest(Path(__file__).read_bytes()),
        },
        "limits": [
            "No local build, test rerun, workflow retry, artifact bundle download or publication by A58.",
            "Provider content is decoded log text, not original HTTP/archive bytes.",
            "Step echoes are not treated as execution results; actual result lines and provider step outcomes are checked.",
            "505 recorded inputs plus three workflows are source-identical to the repaired publication; this is not an exhaustive identity claim about all documentation.",
            "No device/display/DAW, callback deadline or OS retirement qualification follows from dummy fixtures and validators.",
            "No causal audio/converter/live Engine route, full-window audio grade, physical fidelity or literal whole-interface 1:1 acceptance.",
            "A later final documentation publication still requires its own remote verification and observed hosted outcomes.",
        ],
    }
    target = REPORTS / "A58-hosted-audit.json"
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "pass", "successful_jobs": 13, "inputs": 505,
                      "receipt_sha256": digest(target.read_bytes()),
                      "receipt_bytes": target.stat().st_size}))


if __name__ == "__main__":
    main()
