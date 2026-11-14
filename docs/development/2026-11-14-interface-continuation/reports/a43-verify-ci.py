#!/usr/bin/env python3
"""Inspect the A43 workflow without configuring, building or executing tests."""

import argparse
import ast
import collections
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import sys

import yaml


REPO = pathlib.Path(__file__).resolve().parents[4]
REPORTS = REPO / "docs/development/2026-11-14-interface-continuation/reports"
EXPECTED = [
    "test_standalone_ui", "test_standalone_preset_ui",
    "test_standalone_workspaces_author", "test_standalone_workspace_acceptance",
    "test_standalone_projection", "test_standalone_inspection_author",
    "test_standalone_inspection_acceptance", "test_standalone_workspace_continuity",
    "test_standalone_drawing", "test_standalone_quad_drawing",
    "test_standalone_workspace_raster", "test_standalone_scaled_view",
    "test_standalone_preset_raster",
]
BASELINE_SHA256 = "527d1cdb692cd5d837f0436ee68b2026878b10c5db1553459ca623060e4c1d34"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_step(job, name):
    matches = [step for step in job["steps"] if step["name"] == name]
    assert len(matches) == 1, (name, matches)
    return matches[0]


def expanded_jobs(workflow):
    return sum(len(job.get("strategy", {}).get("matrix", {}).get("include", [None]))
               for job in workflow["jobs"].values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", type=pathlib.Path,
                        default=REPO / ".github/workflows/standalone.yml")
    parser.add_argument("--output", type=pathlib.Path,
                        default=REPORTS / "a43-native-sanitizer-ci.json")
    args = parser.parse_args()
    original = json.loads((REPORTS / "a39-ci-inventory.json").read_text())
    workflow_bytes = args.workflow.read_bytes()
    marker = b"\n  native-sanitizers:\n"
    assert workflow_bytes.count(marker) == 1
    prefix, _ = workflow_bytes.split(marker)
    assert hashlib.sha256(prefix).hexdigest() == BASELINE_SHA256, "A39 Release workflow changed"
    baseline = yaml.safe_load(prefix)
    workflow = yaml.safe_load(workflow_bytes)
    assert set(workflow["jobs"]) == {"native", "native-sanitizers"}
    assert workflow["jobs"]["native"] == baseline["jobs"]["native"]
    assert {key: value for key, value in workflow.items() if key != "jobs"} == {
        key: value for key, value in baseline.items() if key != "jobs"}
    native, job = workflow["jobs"]["native"], workflow["jobs"]["native-sanitizers"]
    assert native["strategy"]["matrix"]["include"] == original["standalone_matrix"]
    assert job["runs-on"] == "ubuntu-24.04" and job["timeout-minutes"] == 20
    assert "permissions" not in job and "continue-on-error" not in job
    assert "if" not in job and "strategy" not in job
    assert job["env"]["HAMMOND_SANITIZER_TARGETS"].split() == EXPECTED
    assert len(EXPECTED) == len(set(EXPECTED)) == 13
    ci = yaml.safe_load((REPO / ".github/workflows/ci.yml").read_text())
    for name in ("ASAN_OPTIONS", "UBSAN_OPTIONS", "LSAN_OPTIONS"):
        assert job["env"][name] == ci["jobs"]["sanitizers"]["env"][name]
    assert job["env"]["ASAN_OPTIONS"] == "detect_leaks=1:halt_on_error=1"
    assert {name: job["env"][name] for name in
            ("SDL_AUDIODRIVER", "SDL_VIDEODRIVER", "SDL_RENDER_DRIVER")} == {
                "SDL_AUDIODRIVER": "dummy", "SDL_VIDEODRIVER": "dummy", "SDL_RENDER_DRIVER": "software"}
    old_actions = {step["uses"] for step in native["steps"] if "uses" in step}
    new_actions = {step["uses"] for step in job["steps"] if "uses" in step}
    assert new_actions <= old_actions
    assert all(re.fullmatch(r"[^@]+@[0-9a-f]{40}", action) for action in new_actions)
    for step in job["steps"]:
        assert "continue-on-error" not in step
        assert "secrets." not in json.dumps(step)
        if "if" in step:
            assert step["name"] == "Retain native sanitizer diagnostics" and step["if"] == "${{ always() }}"
    checkout = find_step(job, "Check out the exact tested revision")
    assert checkout["with"] == {"ref": "${{ github.sha }}", "persist-credentials": False}
    acquire_name = "Explicitly acquire and locally verify locked external SDL2"
    assert find_step(job, acquire_name)["run"].replace("standalone-sanitizer-logs", "standalone-ci-logs") == (
        find_step(native, acquire_name)["run"])
    package_name = "Install Ubuntu desktop and audio development headers"
    def without_comments(value):
        return "\n".join(line for line in value.splitlines() if not line.lstrip().startswith("#"))
    assert without_comments(find_step(job, package_name)["run"].replace(
        "standalone-sanitizer-logs", "standalone-ci-logs")) == without_comments(find_step(native, package_name)["run"])
    configure = find_step(job, "Configure native Release with project and SDL sanitizers")["run"]
    for flag in ("-DCMAKE_BUILD_TYPE=Release", "-DBUILD_TESTING=ON", "-DCMAKE_C_COMPILER=gcc",
                 "-DCMAKE_CXX_COMPILER=g++", "-DHAMMOND_BUILD_STANDALONE=ON", "-DHAMMOND_BUILD_VST3=OFF",
                 "-DHAMMOND_ENABLE_MIDI=OFF", "-DHAMMOND_ENABLE_SANITIZERS=ON",
                 "-DCMAKE_C_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer"):
        assert flag in configure, flag
    assert "SDL_ALSA" not in configure
    build = find_step(job, "Build only the thirteen interface acceptance targets")["run"]
    assert '--target "${targets[@]}" --parallel 2 --verbose' in build
    assert "hammond_standalone_test_inputs" not in build and "--target all" not in build
    execute = find_step(job, "Discover exactly thirteen gates and run with leak checking")["run"]
    assert "--parallel 1" in execute and "--timeout 180" in execute
    assert execute.count("--no-tests=error") == 2
    assert "set(names) == set(required)" in execute and "len(set(names)) == 13" in execute
    assert "--output-junit" in execute and "ctest-discovered.json" in execute
    assert '"ASAN_OPTIONS=", "UBSAN_OPTIONS=", "LSAN_OPTIONS="' in execute
    upload = find_step(job, "Retain native sanitizer diagnostics")
    assert upload["if"] == "${{ always() }}" and upload["with"]["retention-days"] == 14
    for path in ("standalone-sanitizer-logs/", "CMakeCache.txt", "compile_commands.json", "LastTest.log", "LastTestsFailed.log"):
        assert path in upload["with"]["path"], path

    parsed = []
    hosted = {}
    for name in ("ci.yml", "native-vst3.yml", "standalone.yml"):
        path = args.workflow if name == "standalone.yml" else REPO / ".github/workflows" / name
        document = yaml.safe_load(path.read_text())
        shell_count = python_count = 0
        for job_name, item in document["jobs"].items():
            for step in item["steps"]:
                if "run" not in step:
                    continue
                script = step["run"]
                shell = re.sub(r"\$\{\{.*?\}\}", "A43_STATIC_EXPRESSION", script, flags=re.S)
                syntax = subprocess.run(["bash", "-n"], input=shell, text=True, capture_output=True)
                assert syntax.returncode == 0, (name, job_name, step["name"], syntax.stderr)
                shell_count += 1
                blocks = re.findall(r"^python(?:3)? - <<'PY'\n(.*?)^PY$", script, re.S | re.M)
                assert len(blocks) == script.count("<<'PY'"), (name, step["name"])
                for block in blocks:
                    ast.parse(block, filename=name + ":" + job_name + ":" + step["name"])
                    python_count += 1
        hosted[name] = expanded_jobs(document)
        parsed.append({"path": ".github/workflows/" + name, "sha256": sha256(path),
                       "yaml_parsed": True, "bash_run_blocks_parsed": shell_count,
                       "python_blocks_parsed": python_count})
    assert sum(hosted.values()) == 12 and hosted["standalone.yml"] == 5
    for name in ("ci.yml", "native-vst3.yml"):
        relative = ".github/workflows/" + name
        assert sha256(REPO / relative) == original["source_sha256"][relative]

    cmake = (REPO / "CMakeLists.txt").read_text()
    app_cmake = (REPO / "apps/standalone/CMakeLists.txt").read_text()
    assert "target_compile_options(${target} PRIVATE\n            -fsanitize=address,undefined -fno-omit-frame-pointer)" in cmake
    assert "target_link_options(${target} PUBLIC -fsanitize=address,undefined)" in cmake
    assert 'file(GLOB HAMMOND_STANDALONE_CPP_TESTS CONFIGURE_DEPENDS' in app_cmake
    assert '"${CMAKE_CURRENT_SOURCE_DIR}/tests/test_*.cpp"' in app_cmake
    assert "hammond_configure_target(${test_name})" in app_cmake
    assert "add_test(NAME ${test_name} COMMAND ${test_name})" in app_cmake
    assert "if(HAMMOND_BUILD_STANDALONE)" in app_cmake and "enable_language(C)" in app_cmake
    assert 'add_subdirectory("${HAMMOND_SDL2_ROOT}" "${CMAKE_BINARY_DIR}/_sdl2" EXCLUDE_FROM_ALL)' in app_cmake
    assert "hammond_configure_target(hammond_standalone_support)" in app_cmake
    assert "hammond_configure_target(hammond_standalone_drawing)" in app_cmake
    mappings = {}
    for name in EXPECTED:
        plain = REPO / "apps/standalone/tests" / (name + ".cpp")
        native_source = REPO / "apps/standalone/native_tests" / (name + ".cpp")
        source = plain if plain.is_file() else native_source
        assert source.is_file(), name
        if source == native_source:
            for declaration in ("add_executable(" + name, "hammond_configure_target(" + name + ")",
                                "add_test(NAME " + name + " COMMAND " + name + ")"):
                assert declaration in app_cmake, declaration
        mappings[name] = {"source": source.relative_to(REPO).as_posix(), "sha256": sha256(source),
                          "registration": "SDK-free C++ glob" if source == plain else "Explicit native target"}
    discovery_path = REPORTS / "a41-discovery.txt"
    discovery = json.loads(discovery_path.read_text())
    names = [test["name"] for test in discovery["tests"]]
    assert len(names) == len(set(names)) and set(EXPECTED) <= set(names)
    pattern = "^(" + "|".join(re.escape(name) for name in EXPECTED) + ")$"
    selected = [test for test in discovery["tests"] if re.search(pattern, test["name"])]
    assert len(selected) == 13 and {test["name"] for test in selected} == set(EXPECTED)
    historical_timeouts = {}
    for test in selected:
        properties = {item["name"]: item["value"] for item in test.get("properties", [])}
        historical_timeouts[test["name"]] = properties.get("TIMEOUT")
    freeze = json.loads((REPORTS / "a41-source-after-test.json").read_text())
    assert not freeze["before_mismatches"] and not freeze["protected_mismatches"]
    post = json.loads((REPORTS / "a41-post-run.json").read_text())
    assert post["workflow_freeze_release_ready"]
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    tree = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=REPO, text=True).strip()
    result = {
        "schema_version": 1, "assignment": 43, "wave": 8,
        "worker": "/root/w08_a43_native_leak_ci", "observed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "head_at_validation": commit, "head_tree": tree, "result": "pass_static_validation_hosted_pending",
        "runtime": {"python": sys.version.split()[0], "pyyaml": yaml.__version__},
        "workflow_sha256": sha256(args.workflow), "baseline_workflow_sha256": BASELINE_SHA256,
        "release_workflow_prefix_byte_identical": True, "release_matrix_rows_preserved": 4,
        "release_required_names_preserved": original["discovery"]["required_names"],
        "release_packages_preserved": {"common_files": 15, "midi_enabled_files": 19},
        "syntax": parsed, "hosted_job_inventory_after": hosted, "hosted_jobs_before": 11, "hosted_jobs_after": 12,
        "job": {"key": "native-sanitizers", "name": job["name"], "runner": job["runs-on"],
                "timeout_minutes": job["timeout-minutes"], "environment": job["env"],
                "required_names": EXPECTED, "build_parallelism": 2, "test_parallelism": 1,
                "ctest_default_timeout_seconds": 180, "discovery_exact_set_and_count": True,
                "no_tests_error": True, "test_sanitizer_environment_overrides_rejected": True,
                "sdl_alsa": "Automatic detection with the unchanged Ubuntu development packages",
                "sanitizer_compile_c": "-fsanitize=address,undefined -fno-omit-frame-pointer",
                "sanitizer_compile_cpp": "HAMMOND_ENABLE_SANITIZERS=ON -> hammond_configure_target",
                "runtime_verification": ["All selected compiled object flags and nonempty files",
                                         "ASan/UBSan references in SDL/core/support/drawing static archives",
                                         "ASan/UBSan link flags and dynamic runtimes for all thirteen binaries"],
                "artifact": upload["with"], "actions": sorted(new_actions)},
        "cmake_source_sha256": {"CMakeLists.txt": sha256(REPO / "CMakeLists.txt"),
                               "apps/standalone/CMakeLists.txt": sha256(REPO / "apps/standalone/CMakeLists.txt")},
        "test_source_mapping": mappings,
        "a41_frozen_discovery": {"path": discovery_path.relative_to(REPO).as_posix(),
                                "sha256": sha256(discovery_path), "all_count": len(names),
                                "matched_count": len(selected), "original_timeouts_seconds": historical_timeouts,
                                "no_new_discovery_execution": True},
        "a41_workflow_freeze_release": {"path": "a41-source-after-test.json", "sha256": sha256(REPORTS / "a41-source-after-test.json"),
                                        "observed_utc": freeze["captured_at_utc"], "input_count": freeze["file_count"],
                                        "protected_count": freeze["protected_count"], "source_digest": freeze["source_digest"]},
        "a41_original_limit_outcome": {"path": "a41-post-run.json", "sha256": sha256(REPORTS / "a41-post-run.json"),
                                       "result": post["result"], "scope": post["scope"]},
        "executed_by_a43": {"configure": 0, "build": 0, "application_or_test": 0, "hosted_dispatch": 0,
                            "index_update": 0, "commit": 0},
        "pending": ["A41 direct raster diagnostics and root's review of any sanitizer-only timeout allowance",
                    "Publish the reviewed exact source through root's guarded checkpoint",
                    "A48/A58 observe setup, instrumentation, exact 13-name discovery and 13/13 leak-enabled passes",
                    "Retain the successful hosted job identity and diagnostics before making a leak qualification claim"],
        "limits": ["Static parsing and retained configured-name discovery are not test execution.",
                   "The original local leak-enabled run failed LSan thread attachment (exit 23/errno 1).",
                   "A41's separately approved detect_leaks=0 run is not a leak pass and retained three original-limit timeouts.",
                   "This job does not run the application, Python wall-time suites, VST3, real devices or package smoke.",
                   "System libraries are not rebuilt; instrumented SDL and selected project paths do not qualify every native path.",
                   "No performance, native accessibility, physical fidelity, literal reference match or signed-release claim follows."],
    }
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"result": result["result"], "workflow_sha256": result["workflow_sha256"],
                      "syntax": parsed, "hosted_jobs_after": 12, "required_tests": 13,
                      "report": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
