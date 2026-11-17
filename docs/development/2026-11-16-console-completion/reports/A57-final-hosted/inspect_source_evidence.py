"""Inspect retained hosted evidence only; never run repository tests or binaries."""
import collections
import gzip
import hashlib
import json
import pathlib
import re
import zipfile

BASE = pathlib.Path(__file__).resolve().parent
PRIOR = BASE.parent / "A57-indexed-hosted"
REPAIR = BASE.parent / "A57-repair-hosted"
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


prior_normal = json.loads((PRIOR / "job-133886098757-review.json").read_text())
prior_sanitizer = json.loads((PRIOR / "job-133886098061-review.json").read_text())
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
    skip_lines = review["ctest"]["method_skip_lines"]
    skipped_subcases = [x for x in skip_lines if "... skipped " in x["line"]]
    if review["job"]["id"] == 133903129277:
        assert len(skipped_subcases) == 1 and len(skip_lines) == 2
        assert skipped_subcases[0]["test"] == "test_standalone_replay_boundaries"
        assert "(case='fifo')" in skipped_subcases[0]["line"]
        assert "FIFO creation is not supported on this platform" in skipped_subcases[0]["line"]
    else:
        assert not skip_lines
    with zipfile.ZipFile(BASE / review["artifact"]["path"]) as z:
        provenance = read_json(z, prefix + "provenance.json")
        assert provenance["source_commit"] == SHA and provenance["source_tree"] == TREE
        assert int(provenance["run_id"]) == 44043394005 and int(provenance["run_attempt"]) == 1
        full_numerical = json.loads(gzip.decompress((BASE / review["numerical_reports"]["path"]).read_bytes()))
        title_admission = full_numerical["test_standalone_title_density"]["fixture_source_admission"]
        header_admission = full_numerical["test_standalone_header_statistics"]["identities"]["fixture_source_admission"]
        assert full_numerical["test_standalone_title_density"]["fixture_source_sha256"] == title_admission["observed_sha256"]
        header_identities = full_numerical["test_standalone_header_statistics"]["identities"]
        assert header_identities["test_source_sha256"] == REMOTE_HASHES["apps/standalone/native_tests/test_standalone_header_statistics.py"]
        assert header_identities["frozen_fixture_source_sha256"] == header_admission["observed_sha256"]
        admission_rows = [
            (title_admission, "apps/standalone/native_tests/test_standalone_footage_typography_raster.cpp", "facc85f516454964ed55e406f95db4046923d7a2441fdf72e65719b3685fec4f"),
            (header_admission, "apps/standalone/native_tests/test_standalone_header_material.cpp", "86acc068fa23826fb39f245f9327e919c076660f315bed5d57f63e586d6d3ac6"),
        ]
        for admission, fixture_path, original in admission_rows:
            assert admission["variant"] == "indexed-array-v1" and admission["candidate_only"] is True
            assert admission["whole_file_reversal_verified"] is True
            assert admission["observed_sha256"] == REMOTE_HASHES[fixture_path]
            assert admission["original_sha256"] == admission["reversed_sha256"] == original
        review["numerical"]["test_standalone_title_density"]["fixture_source_admission"] = title_admission
        review["canonical_reader_source_admission"] = {
            "title": title_admission,
            "header": header_admission,
            "both_active_indexed_sources_and_distinct_original_reversals_observed": True,
        }
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
            "all_selected_timeout_and_run_serial_properties_equal_548_source": True,
            "workflow_and_cmake_equal_immutable_policy": True,
            "remote_api_file_hashes_compared_with_hosted_provenance": compared,
            "source_inventory_count": len(source_hashes),
            "working_tree_used_as_tested_source": False,
            "source_only_python_suites": suite_counts,
            "sanitizer_environment_overrides": expected_overrides,
            "quarantine_scope": "The unchanged ordinary MIDI backend quarantine override is excluded entirely from strict sanitizer selection.",
            "method_subcase_skip_count": len(skipped_subcases),
            "method_skip_limit": "Windows FIFO creation subcase only; its CTest passed" if review["job"]["id"] == 133903129277 else None,
        }
        if not sanitizer:
            assert {k: v["methods"] for k, v in suite_counts.items()} == {
                "python_test_capture_standalone_interface": 45,
                "python_test_compare_header_material": 41,
                "python_test_compare_performance_plate": 71,
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
            with zipfile.ZipFile(PRIOR / "artifact-14309322631.zip") as old:
                previous = read_json(old, prefix + "provenance.json")["source_sha256"]
            delta = {p: {"5485988": previous[p], "523c197": value_sha(h)} for p, h in source_hashes.items() if value_sha(h) != previous[p]}
            assert len(delta) == 5 and set(delta) == {x["path"] for x in IDENTITY["files"] if not x["matches_source_548_hash"]}
            assert all(delta[p]["523c197"] == REMOTE_HASHES[p] for p in delta)
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
                "source_hashes_changed_vs_5485988": delta,
                "unchanged_source_hash_count": 58,
                "source_hash_basis": "Original 523 hosted provenance against original 548 hosted provenance and exact 523 GitHub file API bodies; no local working source substitution.",
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
for prior in (FIRST, REPAIR, PRIOR):
    inventory = json.loads((prior / "evidence-inventory.json").read_text())
    for item in inventory["files"]:
        data = (prior / item["path"]).read_bytes()
        assert len(data) == item["bytes"] and digest(data) == item["sha256"]
    immutable.append({"directory": "../" + prior.name, "inventory": "../" + prior.name + "/evidence-inventory.json", "inventory_sha256": digest((prior / "evidence-inventory.json").read_bytes()), "verified_file_count": len(inventory["files"]), "all_recorded_hashes_unchanged": True})
accepted_external = [
    (BASE.parent / "A57-native-hosted.json", "075276398b54b7145cdecfe4a251964646224306bf880288a9d0af1c73851b25"),
    (BASE.parents[4] / "docs/reviews/CONSOLE_NATIVE_HOSTED_ADMISSION.md", "e77da54e5b6ec6d4fe9258e24ce44551dfbe11dd7060bf1098a7e7310e1831b9"),
    (BASE.parent.parent / "notes/A57.md", "39e2bc05675af526bf972a720d817bb0a6b315f080b63f817fa03cf7e9c95764"),
]
external_verified = []
for path, expected in accepted_external:
    data = path.read_bytes()
    assert digest(data) == expected
    external_verified.append({"path": str(path.relative_to(BASE.parents[4])), "bytes": len(data), "sha256": expected, "unchanged": True})
(BASE / "immutable-prior-evidence.json").write_text(json.dumps({"source_sha": SHA, "verified": immutable, "accepted_external_records": external_verified, "prior_source_evidence_modified": False}, indent=2, sort_keys=True) + "\n")
print(json.dumps({"prior_evidence_unchanged": immutable, "accepted_external_records_unchanged": external_verified}))
