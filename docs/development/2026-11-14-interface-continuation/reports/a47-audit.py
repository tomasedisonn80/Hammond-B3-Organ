#!/usr/bin/env python3
"""Read-only A47 source/log audit; writes only explicitly owned evidence files."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

PUBLISHED = "8673713a484c40e26ac7810c7c4cbc22fa874426"
JOB_IDS = (132451604200, 132451604376, 132451604377)
RUN_ID = 43596362881


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--logs", type=Path, required=True)
    parser.add_argument("--sdk", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    out = repo / "docs/development/2026-11-14-interface-continuation/reports"
    git = lambda *xs: subprocess.check_output(["git", "-C", str(repo), *xs])
    text = lambda path: (repo / path).read_text()
    frozen = lambda path, rev=PUBLISHED: git("show", f"{rev}:{path}")
    write = lambda name, value: (out / name).write_text(json.dumps(value, indent=2) + "\n")
    observed = datetime.now(timezone.utc).isoformat()
    head = git("rev-parse", "HEAD").decode().strip()
    inventory_path = "docs/development/2026-11-14-interface-continuation/reports/a12-boundary-inventory.json"
    inventory = json.loads(text(inventory_path))
    rows = []
    for path, group, size, blob, expected_sha in inventory["files"]:
        current = (repo / path).read_bytes()
        versions = {"baseline": frozen(path, inventory["baseline_commit"]),
                    "published": frozen(path), "head": frozen(path, head), "worktree": current}
        digests = {name: sha(data) for name, data in versions.items()}
        rows.append({"path": path, "group": group, "bytes": len(current),
                     "baseline_sha256": expected_sha, "baseline_git_blob": blob,
                     "current_sha256": digests["worktree"],
                     "all_four_byte_identical": all(data == current for data in versions.values()),
                     "all_hashes_equal_inventory": set(digests.values()) == {expected_sha},
                     "published_git_blob": git("rev-parse", f"{PUBLISHED}:{path}").decode().strip()})
    mismatches = [row for row in rows if not row["all_four_byte_identical"] or not row["all_hashes_equal_inventory"]]
    assert len(rows) == 114 and not mismatches, mismatches
    groups = {}
    for group in sorted({row["group"] for row in rows}):
        selected = [row for row in rows if row["group"] == group]
        identity = sha("".join(row["path"] + "\0" + row["current_sha256"] + "\n"
                               for row in sorted(selected, key=lambda x: x["path"])).encode())
        assert identity == inventory["groups"][group]["identity_sha256"]
        groups[group] = {"files": len(selected), "identity_sha256": identity, "unchanged": True}

    registry = json.loads(text("data/parameter-registry.json"))
    descriptor_re = re.compile(r'\{(\d+)U,\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)",\s*([\d.]+),\s*([\d.]+),\s*(\d+),\s*EventType::(\w+),\s*Manual::(\w+),\s*(\d+)\}')
    compiled = descriptor_re.findall(text("src/ParameterBridge.cpp"))
    expected_re = re.compile(r'\{(\d+)U,\s*"([^"]+)",\s*"([^"]+)",\s*([\d.]+),\s*([\d.]+),\s*(\d+)\}')
    controller_oracle = expected_re.findall(text("plugins/vst3/tests/test_native_controller.cpp"))
    parameters = registry["parameters"]
    assert len(parameters) == len(compiled) == len(controller_oracle) == 47
    parameter_rows = []
    for record, source, oracle in zip(parameters, compiled, controller_oracle):
        ident, path, kind, unit, maximum, default, steps, event, manual, index = source
        actual = (int(ident), path, kind, unit, float(maximum), float(default), int(steps))
        expected = tuple(record[key] for key in ("id", "path", "kind", "unit", "maximum", "default", "step_count"))
        assert actual == expected, (actual, expected)
        assert (int(oracle[0]), oracle[1], oracle[2], float(oracle[3]), float(oracle[4]), int(oracle[5])) == (
            record["id"], record["path"], record["unit"], record["maximum"], record["default"], record["step_count"])
        parameter_rows.append({key: record[key] for key in ("id", "path", "minimum", "maximum", "default", "step_count")})
    native_paths = sorted(p.relative_to(repo).as_posix() for p in (repo / "plugins/vst3").rglob("*") if p.is_file())
    assert native_paths == sorted(row["path"] for row in rows if row["group"] == "vst3")
    core_paths = sorted(p.relative_to(repo).as_posix() for base in ("src", "include/hammond")
                        for p in (repo / base).rglob("*") if p.is_file())
    assert core_paths == sorted(row["path"] for row in rows if row["group"] == "core")
    native_cmake = text("plugins/vst3/CMakeLists.txt")
    assert "target_link_libraries(HammondB3 PRIVATE hammond_core sdk)" in native_cmake
    assert "set(SMTG_ENABLE_VSTGUI_SUPPORT OFF" in native_cmake
    native_mentions = [p for p in native_paths if re.search(r"SDL|apps[/\\]standalone|hammond_standalone_support", text(p))]
    assert not native_mentions, native_mentions
    independent_inputs = ["CMakeLists.txt", ".github/workflows/native-vst3.yml", "cmake/VerifyVst3Sdk.cmake",
                          "tools/acquire_vst3_sdk.py", "tools/embed_profile.py", "tools/compile_profile.py",
                          "tools/compile_pedal_routing.py", "tools/compile_scanner_line.py"]
    additional = [{"path": p, "sha256": sha((repo / p).read_bytes()),
                   "equals_published": (repo / p).read_bytes() == frozen(p),
                   "equals_baseline": (repo / p).read_bytes() == frozen(p, inventory["baseline_commit"])}
                  for p in independent_inputs]
    assert all(r["equals_published"] and r["equals_baseline"] for r in additional)
    source = {
        "schema": "interface-vst3-boundary-a47-v1", "agent": "/root/w08_a47_vst3_boundary",
        "observed_utc": observed, "evidence_kind": "read-only source/hash and exact hosted-log audit; no new build or runtime execution",
        "baseline_commit": inventory["baseline_commit"], "published_commit": PUBLISHED,
        "published_tree": git("rev-parse", f"{PUBLISHED}^{{tree}}").decode().strip(),
        "observed_head": head, "observed_head_tree": git("rev-parse", "HEAD^{tree}").decode().strip(),
        "inventory_path": inventory_path, "inventory_sha256": sha((repo / inventory_path).read_bytes()),
        "protected_files_checked": len(rows), "protected_mismatches": mismatches, "groups": groups,
        "protected_vst3_and_core": [row for row in rows if row["group"] in ("vst3", "core")],
        "additional_native_inputs": additional,
        "parameter_registry_sha256": sha((repo / "data/parameter-registry.json").read_bytes()),
        "parameter_registry_schema": registry["schema_version"], "parameters": parameter_rows,
        "compiled_and_independent_controller_oracle_match_registry": True,
        "state_writer": "B3CONTROLS4", "state_readers": ["B3CONTROLS1", "B3CONTROLS2", "B3CONTROLS3", "B3CONTROLS4"],
        "native_source_count": len(native_paths), "native_standalone_or_sdl_mentions": native_mentions,
        "core_source_count": len(core_paths), "native_or_core_added_or_removed_paths": [],
        "native_link_targets": ["hammond_core", "sdk"], "custom_editor": False,
        "build_scope": "hammond_core uses src/*.cpp; HammondB3 lists Processor/Controller/Factory/StateStream and embedded profile; standalone support is a separate consumer of core",
        "published_to_head_changed_paths": git("diff", "--name-only", PUBLISHED, head).decode().splitlines(),
        "read_scope": ["AGENTS.md", "docs/PLAN.md", "docs/INTERFACE_CONTINUATION_SCOPE.md",
                       "docs/INTERFACE_WORKSPACE_CONTRACT.md", "docs/INTERFACE_INSPECTION_CONTRACT.md",
                       "docs/development/2026-11-14-interface-continuation/CHECKPOINT.md",
                       "docs/VST3_ABI_ACCEPTANCE.md", "plugins/vst3", "include/hammond/ParameterBridge.h",
                       "src/ParameterBridge.cpp", "src/ControlStateIO.cpp", "CMakeLists.txt",
                       "apps/standalone/CMakeLists.txt", ".github/workflows/native-vst3.yml"],
    }
    write("a47-source-boundary.json", source)

    jobs = json.loads((args.logs / "jobs.json").read_text())
    commit = json.loads((args.logs / "commit.json").read_text())
    assert commit["sha"] == PUBLISHED and commit["tree"] == source["published_tree"]
    root_record = json.loads(text("docs/development/2026-11-14-interface-continuation/reports/root-ui-polish-hosted.json"))
    root_jobs = {j["id"]: j for j in root_record["jobs"]}
    records, excerpt_lines = [], []
    sdk_lock = json.loads(text("data/dependencies/vst3-sdk-lock.json"))
    for job in jobs:
        ident = job["id"]
        assert ident in JOB_IDS and job["run_id"] == RUN_ID and job["head_sha"] == PUBLISHED
        assert job["status"] == "completed" and job["conclusion"] == "success"
        assert all(job[key] == root_jobs[ident][key] for key in ("name", "head_sha", "conclusion", "run_id"))
        data = (args.logs / f"{ident}.log").read_bytes()
        lines = data.decode("utf-8-sig").splitlines()
        normalized = [re.sub(r"^\S+\s+", "", line) for line in lines]
        tests = []
        for line in normalized:
            match = re.match(r"(\d+)/(\d+) Test #(\d+): (\S+)\s+\.+\s+(Passed)\s+([\d.]+) sec", line)
            if match:
                ordinal, total, test_id, name, status, seconds = match.groups()
                tests.append({"name": name, "status": status, "seconds": float(seconds)})
        expected_count = 8 if ident == 132451604200 else 7
        assert len(tests) == expected_count and all(t["status"] == "Passed" for t in tests)
        validator = [line.removeprefix("111: ") for line in normalized if line.startswith("111: ")]
        assert "Result: 47 tests passed, 0 tests failed" in validator
        counts = {"teardown_messages": sum("Failed to teardown test!" in line for line in validator),
                  "unsupported_rate_errors": sum("ERROR: IAudioProcessor::setupProcessing (..) failed for samplerate" in line for line in validator),
                  "unsupported_float64_notices": sum("64bit Audio Processing not supported." in line for line in validator)}
        assert list(counts.values()) == [16, 9, 15]
        unsupported = [float(re.search(r"samplerate ([\d.]+) Hz", line).group(1)) for line in validator if "ERROR: IAudioProcessor::setupProcessing (..) failed for samplerate" in line]
        declared = []
        for line in validator:
            m = re.search(r'Parameter (\d+) \(id=(\d+)\): \[title="([^"]+)"\] \[unit="([^"]+)"\] \[type = (\w+), default = ([\d.]+), unit = 0\]', line)
            if m:
                idx, param_id, path, unit, kind, default = m.groups()
                p = parameters[int(idx)]
                assert (int(param_id), path, unit, float(default)) == (p["id"], p["path"], p["unit"], p["normalized"]["default"])
                declared.append(int(param_id))
        assert len(declared) == 47
        reports = [json.loads(line.split(": ", 1)[1]) for line in normalized if re.match(r"11[03]: \{", line)]
        install = next(r for r in reports if r.get("suite") == "native-install-v1")
        abi = next(r for r in reports if r.get("suite") == "native-abi-v1")
        assert abi["descriptors"] == 47 and abi["state_round_trips"] == 3207 and abi["maximum_audio_error"] == 0
        assert install["relocated_abi"] == abi
        sdk_records = [json.loads(line[line.index("{"):]) for line in normalized if '"verified_checkouts"' in line and line.startswith("{")]
        assert len(sdk_records) == 2
        required = [{"path": ".", "commit": sdk_lock["commit"]}] + [{"path": p["path"], "commit": p["commit"]} for p in sdk_lock["required_submodules"]]
        assert all(r["verified_checkouts"] == required for r in sdk_records)
        forbidden = [line for line in normalized if re.search(r"SDL|apps[/\\]standalone", line)]
        assert not forbidden
        summary = [line for line in normalized if "100% tests passed" in line or "Total Test time (real)" in line]
        suite_summaries = [line for line in normalized if re.match(r"11[2-7]: (native[- ]|regions=|Scope:)", line)]
        capability = Counter(line for line in validator if re.search(r"not support|not export|No .*interface|no units|no bypass|does not have a bypass|No snapshots|ProcessContextRequirements|^Info:   - None", line, re.I))
        excerpt = [line for line in normalized if re.search(r"compiler identification|Complete job name|^\d+/\d+ Test|^111: Result:|100% tests passed|Total Test time", line)]
        excerpt += suite_summaries
        excerpt += [f"validator diagnostic count: {k}={v}" for k, v in counts.items()]
        excerpt += [f"validator capability ({n}): {line}" for line, n in capability.items()]
        excerpt_lines += [f"JOB {ident} | {job['name']} | {PUBLISHED}", *excerpt, ""]
        records.append({"id": ident, "run_id": RUN_ID, "head_sha": PUBLISHED, "name": job["name"],
                        "url": job["html_url"], "conclusion": job["conclusion"],
                        "started_at": job["started_at"], "completed_at": job["completed_at"],
                        "log_sha256": sha(data), "log_bytes": len(data), "tests": tests, "ctest_summary": summary,
                        "module_validator": {"passed": 47, "failed": 0, **counts, "unsupported_rates_hz": unsupported,
                                             "capability_messages": dict(capability)},
                        "native_abi": abi, "installed_bundle": install, "suite_summaries": suite_summaries,
                        "sdk_verified_checkouts": required, "native_ui_or_sdl_log_mentions": len(forbidden),
                        "skipped_workflow_steps": [s["name"] for s in job["steps"] if s["conclusion"] == "skipped"]})
    sdk_sources = ["public.sdk/source/vst/testsuite/processing/process.cpp", "public.sdk/source/vst/testsuite/processing/processformat.cpp",
                   "public.sdk/source/vst/testsuite/state/validstatetransition.cpp", "public.sdk/source/vst/testsuite/state/repeatidenticalstatetransition.cpp",
                   "public.sdk/samples/vst-hosting/validator/source/validator.cpp"]
    sdk_commit = subprocess.check_output(["git", "-C", str(args.sdk / "public.sdk"), "rev-parse", "HEAD"], text=True).strip()
    assert sdk_commit == required[-1]["commit"]
    hosted = {"schema": "interface-vst3-hosted-a47-v1", "observed_utc": observed, "published_commit": commit,
              "run_id": RUN_ID, "primary_source": "GitHub connector github_fetch run jobs and git commit; github_fetch_workflow_job_logs with repo_full_name",
              "jobs": records, "raw_log_directory_outside_repository": str(args.logs.resolve()),
              "cross_check_root_record": "all three exact job IDs/names/run/head/conclusions match root-ui-polish-hosted.json",
              "sdk_primary_source_commit": sdk_commit,
              "sdk_diagnostic_sources": [{"path": p, "sha256": sha((args.sdk / p).read_bytes())} for p in sdk_sources],
              "capability_limits": ["Float32 stereo only, at 44100/48000/96000 Hz; 64-bit processing and mono are not advertised.",
                                    "No IUnitInfo/units/programs, MIDI mapping/learn, note-expression or keyswitch interfaces; no bypass or custom editor.",
                                    "Validator 47/0 retains 16 teardown diagnostics, 9 unsupported-rate ERROR lines and 15 float64 notices per platform.",
                                    "test_native_realtime is registered only on Linux: its new/delete interception does not qualify macOS or Windows allocation behavior or device deadlines.",
                                    "No CTest-level skips; alternate-platform configure steps are conditional skips.",
                                    "No DAW project/device session, physical audio, clean-machine installation, accessibility, signing or measured hardware-fidelity acceptance.",
                                    "These hosted jobs qualify 8673713 only; later standalone sanitizer/guide metadata has separate hosted evidence."]}
    write("a47-hosted-vst3.json", hosted)
    (out / "a47-hosted-excerpts.txt").write_text("\n".join(excerpt_lines))
    print(json.dumps({"protected_files": len(rows), "mismatches": len(mismatches), "parameters": len(parameter_rows),
                      "observed_head": head, "hosted_source": PUBLISHED,
                      "native_jobs": [{"id": r["id"], "tests_passed": len(r["tests"]), "validator": [47, 0]} for r in records]}))


if __name__ == "__main__":
    main()
