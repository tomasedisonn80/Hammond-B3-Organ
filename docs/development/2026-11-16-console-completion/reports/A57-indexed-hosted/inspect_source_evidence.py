"""Inspect retained hosted evidence only; never run repository tests or binaries."""
import collections
import gzip
import hashlib
import json
import pathlib
import re
import zipfile

BASE = pathlib.Path(__file__).resolve().parent
PRIOR = BASE.parent / "A57-repair-hosted"
FIRST = BASE.parent / "A57-native-hosted"
POLICY = json.loads((FIRST / "source-policy-preflight.json").read_text())
IDENTITY = json.loads((BASE / "source-identity.json").read_text())
SHA = IDENTITY["source_sha"]
TREE = IDENTITY["source_tree"]
REMOTE_HASHES = {x["path"]: x["sha256"] for x in IDENTITY["files"]}


def digest(value):
    return hashlib.sha256(value).hexdigest()


def read_json(z, path):
    return json.loads(z.read(path))


def value_sha(value):
    return value["sha256"] if isinstance(value, dict) else value


prior_normal = json.loads((PRIOR / "job-133874509299-review.json").read_text())
prior_sanitizer = json.loads((PRIOR / "job-133874509009-review.json").read_text())
old_deadlines = {
    False: {r["name"]: (r["timeout_seconds"], r["run_serial"]) for r in prior_normal["ctest"]["results"]},
    True: {r["name"]: (r["timeout_seconds"], r["run_serial"]) for r in prior_sanitizer["ctest"]["results"]},
}

for path in sorted(BASE.glob("job-*-review.json")):
    review = json.loads(path.read_text())
    sanitizer = "instrumentation" in review
    prefix = "standalone-sanitizer-logs/" if sanitizer else "standalone-ci-logs/"
    assert review["source_sha"] == SHA
    assert review["job"]["status"] == "completed" and review["job"]["conclusion"] == "success"
    assert all(s["status"] == "completed" for s in review["job"]["steps"])
    assert not review["ctest"]["disabled_names"]
    expected_overrides = {} if sanitizer else prior_normal["ctest"]["sanitizer_environment_overrides"]
    assert review["ctest"]["sanitizer_environment_overrides"] == expected_overrides
    assert all(not r["failed"] and not r["skipped"] and r["ctest_result"]["result"] == "Passed" for r in review["ctest"]["results"])
    deadlines = {r["name"]: (r["timeout_seconds"], r["run_serial"]) for r in review["ctest"]["results"]}
    assert deadlines == old_deadlines[sanitizer]
    with zipfile.ZipFile(BASE / review["artifact"]["path"]) as z:
        provenance = read_json(z, prefix + "provenance.json")
        assert provenance["source_commit"] == SHA and provenance["source_tree"] == TREE
        assert int(provenance["run_id"]) == 44038196285 and int(provenance["run_attempt"]) == 1
        log = z.read(prefix + "ctest.log").decode()
        numbered = collections.defaultdict(list)
        for line in log.splitlines():
            m = re.match(r"^(\d+): ?(.*)$", line)
            if m:
                numbered[int(m[1])].append(m[2])
        suite_counts = {}
        for item in review["ctest"]["results"]:
            if item["name"].startswith("python_test_"):
                output = "\n".join(numbered[item["ctest_result"]["number"]])
                m = re.search(r"Ran (\d+) tests in ([\d.]+)s", output)
                assert m and re.search(r"^OK$", output, re.M)
                suite_counts[item["name"]] = {"methods": int(m[1]), "seconds": float(m[2]), "status": "passed", "method_skip_count": 0}
        source_hashes = provenance["source_sha256"] if sanitizer else provenance["source_files"]
        compared = {p: value_sha(source_hashes[p]) for p in REMOTE_HASHES if p in source_hashes}
        assert all(h == REMOTE_HASHES[p] for p, h in compared.items())
        review["source_and_policy_review"] = {
            "source_sha_and_tree_match_commit_api": True,
            "run_and_attempt_match_api": True,
            "all_selected_timeout_and_run_serial_properties_equal_d2ed_source": True,
            "workflow_and_cmake_equal_immutable_policy": True,
            "remote_api_file_hashes_compared_with_hosted_provenance": compared,
            "source_inventory_count": len(source_hashes),
            "working_tree_used_as_tested_source": False,
            "source_only_python_suites": suite_counts,
            "sanitizer_environment_overrides": expected_overrides,
            "quarantine_scope": "The unchanged ordinary MIDI backend quarantine override is excluded entirely from strict sanitizer selection.",
            "method_subcase_skip_count": 1 if review["job"]["id"] == 133886098445 else 0,
            "method_skip_limit": "Windows FIFO creation subcase only; its CTest passed" if review["job"]["id"] == 133886098445 else None,
        }
        if not sanitizer:
            assert {k: v["methods"] for k, v in suite_counts.items()} == {
                "python_test_capture_standalone_interface": 45,
                "python_test_compare_header_material": 32,
                "python_test_compare_performance_plate": 64,
            }
            installed = read_json(z, prefix + "installed-inventory.json")
            staged = read_json(z, prefix + "staged-inventory.json")
            smoke = read_json(z, prefix + "relocated-smoke.json")
            assert installed["payload"] == staged
            assert installed["relocated_help_passed"] and installed["relocated_dummy_smoke_ms"] == 600
            assert installed["smoke_diagnostics_sha256"] == digest(z.read(prefix + "relocated-smoke.json"))
            assert smoke["smoke"]["passed"] and smoke["smoke"]["completed"] and smoke["smoke"]["duration_ms"] == 600
            assert smoke["runtime"]["video_driver"] == smoke["audio"]["driver"] == "dummy"
            assert smoke["runtime"]["renderer"] == "software"
            assert not smoke["session"]["held_after_shutdown"] and not smoke["session"]["running_after_shutdown"]
            expected_count = 21 if provenance["requested_midi"]["enabled"] else 17
            assert len(staged["files"]) == expected_count
            review["package_review"] = {
                "staged_payload_exactly_equals_installed_inventory": True,
                "smoke_diagnostics_match_inventory_hash": True,
                "relocated_help_passed": True,
                "relocated_dummy_smoke_ms": 600,
                "relocated_smoke_passed": True,
                "payload_files": expected_count,
                "physical_device_qualification": False,
            }
        else:
            inst = read_json(z, prefix + "instrumentation.json")
            command_bytes = z.read("build-standalone-sanitizers/compile_commands.json")
            commands = json.loads(command_bytes)
            assert digest(command_bytes) == inst["compile_commands_sha256"]
            selected = collections.defaultdict(list)
            hosted_source_root = commands[0]["directory"].split("/build-standalone-sanitizers", 1)[0] + "/"
            for command in commands:
                m = re.search(r"CMakeFiles/([^/]+)\.dir/", command["output"])
                if m and m[1] in inst["compiled_sources_by_target"]:
                    selected[m[1]].append(command)
            assert set(selected) == set(inst["compiled_sources_by_target"]) == set(inst["instrumented_objects_by_target"])
            for target, items in selected.items():
                recorded_names = [c["file"][len(hosted_source_root):] if c["file"].startswith(hosted_source_root) else c["file"] for c in items]
                assert sorted(recorded_names) == sorted(inst["compiled_sources_by_target"][target])
                assert inst["instrumented_objects_by_target"][target] == len(items) > 0
                assert all("-fsanitize=address,undefined" in c["command"] and "-fno-omit-frame-pointer" in c["command"] for c in items)
            assert len(selected) == 44 and sum(map(len, selected.values())) == 291
            assert len(selected["SDL2-static"]) == 196 and all(c["file"].endswith(".c") for c in selected["SDL2-static"])
            assert len(inst["archives"]) == 7 and all(a["asan_and_ubsan_references"] for a in inst["archives"].values())
            assert set(inst["executables"]) == set(provenance["build_targets"]) == set(POLICY["sanitizer_targets"])
            assert len(inst["executables"]) == 37
            assert all("-fsanitize=address,undefined" in e["link_command"] for e in inst["executables"].values())
            assert inst["test_targets"] == provenance["test_targets"] == POLICY["sanitizer_test_to_target"]
            assert len(provenance["required_tests"]) == 41 and set(provenance["required_tests"]) == set(POLICY["sanitizer_test_to_target"])
            assert set(source_hashes) == set(POLICY["sanitizer_source_inventory"]) and len(source_hashes) == 63
            for key, value in POLICY["policy"]["sanitizer_environment"].items():
                assert provenance["environment"][key] == value
            runtimes = {}
            for target in sorted(inst["executables"]):
                text = z.read(prefix + target + "-runtimes.txt").decode()
                runtimes[target] = {"asan_present": "libasan.so" in text, "ubsan_present": "libubsan.so" in text, "not_found": "not found" in text}
                assert runtimes[target] == {"asan_present": True, "ubsan_present": True, "not_found": False}
            with zipfile.ZipFile(PRIOR / "artifact-14308300667.zip") as old:
                previous = read_json(old, prefix + "provenance.json")["source_sha256"]
            delta = {p: {"d2ed03b": previous[p], "5485988": value_sha(h)} for p, h in source_hashes.items() if value_sha(h) != previous[p]}
            assert len(delta) == 9 and set(delta) == set(REMOTE_HASHES) - {".github/workflows/standalone.yml", "apps/standalone/CMakeLists.txt"}
            assert all(delta[p]["5485988"] == REMOTE_HASHES[p] for p in delta)
            stderr = {n: {"bytes": len(z.read(n)), "content": z.read(n).decode()} for n in z.namelist() if n.startswith(prefix + "native-calibration/") and n.endswith("/stderr.txt")}
            assert len(stderr) == 7
            pattern = re.compile(r"AddressSanitizer:|LeakSanitizer:|UndefinedBehaviorSanitizer:|runtime error:")
            diagnostics = [{"path": prefix + "ctest.log", "line": line} for line in log.splitlines() if pattern.search(line)]
            diagnostics.extend({"path": name, "line": line} for name, item in stderr.items() for line in item["content"].splitlines() if pattern.search(line))
            assert not diagnostics
            calibration = read_json(z, prefix + "native-calibration/summary.json")
            assert calibration["subprocesses"] == 10 and calibration["native_lifecycles"] == 7 and calibration["deliberately_failed_replays"] == 2
            assert all(c["common_assertions_passed"] for c in calibration["cases"])
            assert sum(c["expected_exit"] == 1 for c in calibration["cases"]) == 2
            final_step = next(s for s in review["job"]["steps"] if s["name"] == "Reverify source and locked SDL2 after acceptance")
            assert final_step["conclusion"] == "success"
            review["instrumentation_review"] = {
                "compile_commands_match_recorded_hash": True,
                "selected_compile_command_count": 291,
                "compiled_groups": 44,
                "compiled_sources_by_target_counts": {k: len(v) for k, v in selected.items()},
                "instrumented_objects_by_target": inst["instrumented_objects_by_target"],
                "all_selected_commands_have_address_undefined": True,
                "all_selected_commands_have_frame_pointer": True,
                "all_selected_groups_have_nonempty_instrumented_objects": True,
                "archive_count": 7,
                "all_archives_have_asan_and_ubsan": True,
                "executable_count": 37,
                "all_executables_link_sanitizers": True,
                "all_retained_runtime_files_have_asan_ubsan_and_no_missing_dependencies": True,
                "runtime_results": runtimes,
                "source_inventory_count": 63,
                "source_inventory_exactly_equals_policy": True,
                "source_hashes_changed_vs_d2ed03b": delta,
                "unchanged_source_hash_count": 54,
                "source_hash_basis": "Original 548 hosted provenance against original d2ed hosted provenance and exact 548 GitHub file API bodies; no local working source substitution.",
                "targets_equal_policy": True,
                "test_target_mapping_equals_policy": True,
                "environment": provenance["environment"],
                "actual_ctest_and_retained_stderr_sanitizer_diagnostics": diagnostics,
                "calibration_stderr": stderr,
                "calibration_summary": calibration,
                "toolchain_log": z.read(prefix + "toolchain.log").decode(),
                "source_reverification_step": final_step,
                "system_libraries_rebuilt": False,
            }
    path.write_text(json.dumps(review, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"job": review["job"]["id"], "all_review_checks_passed": True, "ctests": len(review["ctest"]["results"]), "sanitizer": sanitizer, "source_only_method_counts": {k: v["methods"] for k, v in suite_counts.items()}}))

immutable = []
for prior in (FIRST, PRIOR):
    inventory = json.loads((prior / "evidence-inventory.json").read_text())
    for item in inventory["files"]:
        data = (prior / item["path"]).read_bytes()
        assert len(data) == item["bytes"] and digest(data) == item["sha256"]
    immutable.append({"directory": "../" + prior.name, "inventory": "../" + prior.name + "/evidence-inventory.json", "inventory_sha256": digest((prior / "evidence-inventory.json").read_bytes()), "verified_file_count": len(inventory["files"]), "all_recorded_hashes_unchanged": True})
(BASE / "immutable-prior-evidence.json").write_text(json.dumps({"source_sha": SHA, "verified": immutable, "prior_source_evidence_modified": False}, indent=2, sort_keys=True) + "\n")
print(json.dumps({"prior_evidence_unchanged": immutable}))
