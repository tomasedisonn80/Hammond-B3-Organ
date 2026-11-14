#!/usr/bin/env python3
"""A49's one-shot qualification recorder; does not change product or test code."""

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET


REPORTS = Path(__file__).resolve().parent
REPO = REPORTS.parents[3]
BUILD = REPO.parent / "build-native"
BIN = Path("/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin")
EXPECTED_HEAD = "cdbb2beaa28bf136f9a8db6213819129514e2ae9"
PRODUCT_PARENT = "8673713a484c40e26ac7810c7c4cbc22fa874426"
EXPECTED_APP = "bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2"
ENVIRONMENT = {
    "SDL_VIDEODRIVER": "dummy",
    "SDL_AUDIODRIVER": "dummy",
    "PYTHONDONTWRITEBYTECODE": "1",
}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def identity(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": digest(data)}


def read(name):
    return json.loads((REPORTS / name).read_text())


def write(name, data):
    with (REPORTS / name).open("x", encoding="utf-8") as stream:
        json.dump(data, stream, sort_keys=True, indent=2)
        stream.write("\n")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO)


def inventory_digest(rows):
    # Same stable encoding used by the protected inventory and A44 product set.
    return digest("".join(
        path + "\0" + rows[path]["sha256"] + "\n" for path in sorted(rows)
    ).encode())


def observed_inputs(paths, compare_commit=None):
    rows = {path: identity(REPO / path) for path in sorted(paths)}
    mismatches = []
    if compare_commit:
        for path, row in rows.items():
            try:
                committed = git("show", f"{compare_commit}:{path}")
                if digest(committed) != row["sha256"]:
                    mismatches.append(path)
            except subprocess.CalledProcessError:
                mismatches.append(path)
    return {
        "count": len(rows),
        "identity_encoding": "sorted UTF-8 path + NUL + SHA-256 + LF",
        "inventory_sha256": inventory_digest(rows),
        "compare_commit": compare_commit,
        "mismatches": mismatches,
        "files": rows,
    }


def snapshot(phase):
    original = read("root-ui-coherent-source-before.json")
    source_paths = {row["path"] for row in original["files"]}
    tracked = git("ls-files", "-z").decode().split("\0")[:-1]
    selected = {
        path for path in tracked
        if path == "CMakeLists.txt" or path.startswith((
            ".github/workflows/", "apps/", "cmake/", "include/", "src/", "tests/", "tools/"
        ))
    }
    source_paths.update(selected)
    product_basis = read("a46-source-before.json")
    product_paths = set(product_basis["production_files"])
    boundary = read("a12-boundary-inventory.json")
    protected_paths = {row[0] for row in boundary["files"]}
    package_basis = read("a44-midi-on-source-after-build.json")
    installed_paths = {
        path for path in package_basis["installed_sources_sha256"]
        if not Path(path).is_absolute()
    }
    sources = observed_inputs(source_paths, EXPECTED_HEAD)
    product = observed_inputs(product_paths, EXPECTED_HEAD)
    product["mismatches_from_parent"] = [
        path for path, row in product["files"].items()
        if digest(git("show", f"{PRODUCT_PARENT}:{path}")) != row["sha256"]
    ]
    protected = observed_inputs(protected_paths, boundary["baseline_commit"])
    protected["inventory_basis"] = {
        "path": "a12-boundary-inventory.json",
        **identity(REPORTS / "a12-boundary-inventory.json"),
    }
    protected["mismatches_from_recorded_hash"] = [
        row[0] for row in boundary["files"]
        if protected["files"][row[0]]["sha256"] != row[4]
    ]
    protected["groups"] = {}
    for group, baseline in boundary["groups"].items():
        rows = {
            row[0]: protected["files"][row[0]]
            for row in boundary["files"] if row[1] == group
        }
        protected["groups"][group] = {
            "count": len(rows),
            "inventory_sha256": inventory_digest(rows),
            "equals_baseline": inventory_digest(rows) == baseline["identity_sha256"],
        }
    supplemental = observed_inputs(
        (product_paths | protected_paths | installed_paths) - source_paths,
        EXPECTED_HEAD,
    )
    cache = {}
    for line in (BUILD / "CMakeCache.txt").read_text().splitlines():
        if line.startswith(("#", "//")) or "=" not in line or ":" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.split(":", 1)[0]
        if key.startswith(("CMAKE_", "HAMMOND_", "SDL_", "ALSA_")) or key in (
            "BUILD_TESTING", "_Python3_EXECUTABLE", "DART_TESTING_TIMEOUT"
        ):
            cache[key] = value
    build_paths = set(product_basis["build_files"])
    build_paths.update(product_basis["additional_build_identity"])
    build_paths.update({
        "CTestTestfile.cmake", "apps/standalone/CTestTestfile.cmake",
        "apps/standalone/CMakeFiles/hammond_rtmidi.dir/flags.make",
        "apps/standalone/CMakeFiles/hammond_standalone.dir/flags.make",
    })
    generated_and_libraries = {
        path: identity(BUILD / path) for path in sorted(build_paths)
        if (BUILD / path).is_file()
    }
    executable_paths = []
    for directory in (BUILD, BUILD / "apps/standalone"):
        for path in directory.iterdir():
            if path.is_file() and os.access(path, os.X_OK):
                executable_paths.append(path.relative_to(BUILD).as_posix())
    executables = {
        path: identity(BUILD / path) for path in sorted(executable_paths)
    }
    changed_tracked = git("diff", "--name-only", "HEAD", "--").decode().splitlines()
    overlay = {
        path: identity(REPO / path) if (REPO / path).is_file() else {"missing": True}
        for path in changed_tracked
    }
    untracked = git("ls-files", "--others", "--exclude-standard", "-z").decode().split("\0")[:-1]
    untracked_without_a49 = [
        path for path in untracked
        if not path.startswith(REPORTS.relative_to(REPO).as_posix() + "/a49-")
        and path not in (
            "docs/reviews/INTERFACE_FINAL_COHERENT_GATE.md",
            "docs/development/2026-11-14-interface-continuation/session49-final-coherent-gate.md",
        )
    ]
    dependencies = {}
    for name, root in {
        "sdl2": Path(cache["HAMMOND_SDL2_ROOT"]),
        "rtmidi": Path(cache["HAMMOND_RTMIDI_ROOT"]),
    }.items():
        selected_files = (
            ("CMakeLists.txt", "include/SDL_version.h", "LICENSE.txt")
            if name == "sdl2" else ("RtMidi.cpp", "RtMidi.h", "CMakeLists.txt", "LICENSE")
        )
        dependencies[name] = {
            "root": str(root),
            "lock": identity(REPO / f"data/dependencies/{name}-lock.json"),
            "selected_files": {
                path: identity(root / path) for path in selected_files
                if (root / path).is_file()
            },
        }
    result = {
        "schema": "interface-final-coherent-snapshot-a49-v1",
        "agent": "/root/w09_a49_final_coherent_gate",
        "recorded_at_utc": now(),
        "phase": phase,
        "git": {
            "head": git("rev-parse", "HEAD").decode().strip(),
            "tree": git("rev-parse", "HEAD^{tree}").decode().strip(),
            "expected_source_commit": EXPECTED_HEAD,
            "tracked_overlay": overlay,
            "untracked_non_a49_overlay_paths": untracked_without_a49,
        },
        "source_test_build_workflow_inputs": sources,
        "new_source_paths_since_original_gate": sorted(selected - {row["path"] for row in original["files"]}),
        "production_inputs": product,
        "protected_boundary": protected,
        "supplemental_inputs": supplemental,
        "selected_configuration": cache,
        "generated_and_libraries": generated_and_libraries,
        "generated_and_libraries_inventory_sha256": inventory_digest(generated_and_libraries),
        "executables": executables,
        "executables_inventory_sha256": inventory_digest(executables),
        "native_application": identity(BUILD / "apps/standalone/hammond_standalone"),
        "dependencies": dependencies,
        "scope": "327 original source/test/build/workflow inputs, 98 production inputs, 114 protected inputs and supplemental installed/source inputs are independently identified. Concurrent documentation/gallery/report changes are recorded separately. Dependency checks use pinned configure verifiers plus selected byte identities; this is not a universal system dependency graph.",
    }
    write(f"a49-source-{phase}.json", result)
    return result


def execute(name, command, environment=None):
    start = now()
    monotonic = time.monotonic()
    env = os.environ.copy()
    if environment:
        env.update(environment)
    print(f"START {name}: {' '.join(map(str, command))}", flush=True)
    with (REPORTS / f"a49-{name}.log").open("xb") as stream:
        result = subprocess.run(command, cwd=REPO, env=env, stdout=stream, stderr=subprocess.STDOUT)
    record = {
        "command": list(map(str, command)), "cwd": str(REPO),
        "environment_overrides": environment or {}, "started_at_utc": start,
        "finished_at_utc": now(), "seconds": round(time.monotonic() - monotonic, 6),
        "returncode": result.returncode,
        "log": {"path": f"a49-{name}.log", **identity(REPORTS / f"a49-{name}.log")},
    }
    write(f"a49-{name}-process.json", record)
    print(f"END {name}: rc={result.returncode} seconds={record['seconds']}", flush=True)
    return record


def assert_frozen(snapshot_data):
    for key in ("source_test_build_workflow_inputs", "production_inputs", "protected_boundary", "supplemental_inputs"):
        assert not snapshot_data[key]["mismatches"], (key, snapshot_data[key]["mismatches"])
    assert not snapshot_data["protected_boundary"]["mismatches_from_recorded_hash"]
    assert not snapshot_data["production_inputs"]["mismatches_from_parent"]
    assert snapshot_data["source_test_build_workflow_inputs"]["count"] == 327
    assert snapshot_data["production_inputs"]["count"] == 98
    assert snapshot_data["protected_boundary"]["count"] == 114
    assert snapshot_data["native_application"]["sha256"] == EXPECTED_APP


def prepare():
    before = snapshot("before-configure")
    assert_frozen(before)
    configure = execute("configure", [
        str(BIN / "cmake"), "-S", str(REPO), "-B", str(BUILD),
        "-DCMAKE_BUILD_TYPE=Release", "-DBUILD_TESTING=ON",
        "-DHAMMOND_BUILD_STANDALONE=ON", "-DHAMMOND_BUILD_VST3=OFF",
        "-DHAMMOND_ENABLE_SANITIZERS=OFF", "-DHAMMOND_ENABLE_MIDI=ON",
        "-DSDL_ALSA=OFF", "-DHAMMOND_SDL2_ROOT=/workspace/scratch/7ffc2842608b/SDL2",
        "-DHAMMOND_RTMIDI_ROOT=/workspace/scratch/cd4bd06ce68f/rtmidi",
        "-DALSA_INCLUDE_DIR=/workspace/scratch/641ca55ce6de/native-sysroot/usr/include",
        "-DALSA_LIBRARY=/workspace/scratch/641ca55ce6de/native-sysroot/usr/lib/x86_64-linux-gnu/libasound.so",
    ])
    if configure["returncode"]:
        raise SystemExit(configure["returncode"])
    build = execute("build", [str(BIN / "cmake"), "--build", str(BUILD), "--parallel", "2"])
    if build["returncode"]:
        raise SystemExit(build["returncode"])
    after = snapshot("after-build")
    assert_frozen(after)
    inventory_command = [str(BIN / "ctest"), "--test-dir", str(BUILD), "-C", "Release", "--show-only=json-v1"]
    with (REPORTS / "a49-ctest-inventory.json").open("xb") as stream:
        inventory_process = subprocess.run(inventory_command, cwd=REPO, stdout=stream, stderr=subprocess.PIPE)
    assert inventory_process.returncode == 0, inventory_process.stderr.decode()
    inventory = read("a49-ctest-inventory.json")
    assert len(inventory["tests"]) == 147, len(inventory["tests"])
    tests = {test["name"]: test for test in inventory["tests"]}
    properties = {
        name: {row["name"]: row["value"] for row in test["properties"]}
        for name, test in tests.items()
    }
    expected_timeouts = {
        "test_standalone_workspace_raster": 60,
        "test_standalone_scaled_view": 60,
        "test_standalone_preset_raster": 30,
        "test_standalone_native_midi_replay": 90,
        "test_standalone_workflows": 90,
        "test_standalone_workspace_replay": 90,
    }
    for name, seconds in expected_timeouts.items():
        assert properties[name]["TIMEOUT"] == seconds, (name, properties[name])
    assert "-D__LINUX_ALSA__" in (BUILD / "apps/standalone/CMakeFiles/hammond_rtmidi.dir/flags.make").read_text()
    toolchain = {}
    for name, command in {
        "cmake": [str(BIN / "cmake"), "--version"],
        "ctest": [str(BIN / "ctest"), "--version"],
        "cxx": ["/usr/bin/c++", "--version"],
        "python": [after["selected_configuration"]["_Python3_EXECUTABLE"], "--version"],
    }.items():
        toolchain[name] = subprocess.check_output(command, text=True).strip()
    result = {
        "schema": "interface-final-coherent-prepare-a49-v1", "recorded_at_utc": now(),
        "configure": configure, "build": build,
        "inventory_command": inventory_command,
        "inventory_file": {"path": "a49-ctest-inventory.json", **identity(REPORTS / "a49-ctest-inventory.json")},
        "discovered_tests": len(tests), "ordinary_release_timeouts": expected_timeouts,
        "source_inputs_unchanged": before["source_test_build_workflow_inputs"]["files"] == after["source_test_build_workflow_inputs"]["files"],
        "application_byte_identical": before["native_application"] == after["native_application"],
        "native_application": after["native_application"],
        "toolchain": toolchain, "platform": platform.platform(),
        "ctest_parallelism": 1,
        "parallelism_basis": "Existing standalone CI uses --parallel 1. Original complete gate's workflow suite consumed 64.69 of its 90-second limit; no parallel native timing contract was established. Preserve serial execution and existing per-test limits.",
    }
    assert result["source_inputs_unchanged"] and result["application_byte_identical"]
    write("a49-prepare-result.json", result)
    print(json.dumps({k: result[k] for k in ("discovered_tests", "ordinary_release_timeouts", "source_inputs_unchanged", "application_byte_identical", "native_application")}), flush=True)


def gate():
    prepared = read("a49-prepare-result.json")
    assert prepared["discovered_tests"] == 147
    before = snapshot("before-ctest")
    assert_frozen(before)
    after_build = read("a49-source-after-build.json")
    assert before["executables"] == after_build["executables"]
    assert before["generated_and_libraries"] == after_build["generated_and_libraries"]
    command = [
        str(BIN / "ctest"), "--test-dir", str(BUILD), "-C", "Release",
        "--verbose", "--output-on-failure", "--no-tests=error", "--parallel", "1",
        "--output-junit", str(REPORTS / "a49-release-junit.xml"),
    ]
    assert not (REPORTS / "a49-release-junit.xml").exists()
    process = execute("release-ctest", command, ENVIRONMENT)
    after = snapshot("after-ctest")
    tests = []
    junit_path = REPORTS / "a49-release-junit.xml"
    if junit_path.exists():
        root = ET.parse(junit_path).getroot()
        for case in root.iter("testcase"):
            tests.append({
                "name": case.get("name"), "seconds": float(case.get("time", 0)),
                "status": "failed" if case.find("failure") is not None else (
                    "skipped" if case.find("skipped") is not None else "passed"
                ),
            })
    failure_file = BUILD / "Testing/Temporary/LastTestsFailed.log"
    if process["returncode"] and failure_file.exists():
        with (REPORTS / "a49-last-tests-failed.log").open("xb") as stream:
            stream.write(failure_file.read_bytes())
    stability = {}
    for key in ("source_test_build_workflow_inputs", "production_inputs", "protected_boundary", "supplemental_inputs"):
        stability[key] = before[key]["files"] == after[key]["files"]
    stability["executables"] = before["executables"] == after["executables"]
    stability["generated_and_libraries"] = before["generated_and_libraries"] == after["generated_and_libraries"]
    stability["dependencies"] = before["dependencies"] == after["dependencies"]
    result = {
        "schema": "interface-final-coherent-gate-a49-v1", "recorded_at_utc": now(),
        "source_commit": EXPECTED_HEAD,
        "source_tree": git("rev-parse", f"{EXPECTED_HEAD}^{{tree}}").decode().strip(),
        "configuration": "Linux GCC 14.2 Release; native MIDI ON; SDL_ALSA OFF; RtMidi ALSA ON; sanitizers OFF; dummy video/audio; serial complete CTest",
        "process": process,
        "discovered": prepared["discovered_tests"], "executed": len(tests),
        "passed": sum(test["status"] == "passed" for test in tests),
        "failed": sum(test["status"] == "failed" for test in tests),
        "skipped": sum(test["status"] == "skipped" for test in tests),
        "tests": tests, "stability": stability,
        "native_application": after["native_application"],
        "junit": {"path": junit_path.name, **identity(junit_path)} if junit_path.exists() else None,
        "historical_gate": "root-ui-coherent-gate.json remains the original 146/147 result; no retries or relabeling",
        "limitations": [
            "No VST3 target is built here; its unchanged boundary and hosted qualification remain separate.",
            "No physical audio/MIDI device, DAW, desktop pointer/display, accessibility, deadline, literal pixel equality or physical fidelity claim follows.",
            "SDK-free tests execute within the combined native-enabled tree; a separately configured SDK-free platform gate has its own evidence.",
        ],
    }
    result["accepted"] = process["returncode"] == 0 and result["passed"] == 147 and all(stability.values())
    write("a49-final-result.json", result)
    print(json.dumps({k: result[k] for k in ("accepted", "discovered", "executed", "passed", "failed", "skipped", "stability", "native_application")}), flush=True)
    raise SystemExit(0 if result["accepted"] else 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("prepare", "gate"))
    args = parser.parse_args()
    {"prepare": prepare, "gate": gate}[args.phase]()
