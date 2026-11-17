#!/usr/bin/env python3
"""One root-coordinated coherent build, affected gate, and separately bound gallery.

Never retries, changes a threshold, or rewrites the earlier integrated run.
Source inputs are frozen before building and rechecked after every phase.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
SESSION = Path(__file__).resolve().parent
REPORTS = SESSION / "reports"
BUILD = ROOT.parent / "build-native"
CMAKE = Path("/workspace/scratch/3edffb787db3/build-tools/cmake/data/bin/cmake")
CTEST = CMAKE.with_name("ctest")
SELECTION = r"^(test_standalone_|python_test_(compare_header_material|compare_performance_plate|capture_standalone_interface)$)"
EXPECTED = {
    "apps/standalone/InstrumentView.cpp": "6cf932e7216bcab4b14ab45e1b957281b749bcef068dd9562493652c25767105",
    "apps/standalone/main.cpp": "0c02c619bd04e69ed70aa7c50cbb8345cbc41a188619e94ca6b8a56a24547537",
    "apps/standalone/CMakeLists.txt": "927f48c1feba27889a63c73d7b8223b40b33c8851a07ac3b7feec9a88e713e07",
    ".github/workflows/standalone.yml": "d298ac55d78ae242b97c5de73be138b4a87c4d4fb343872e58a5c0bd5dc08659",
    "apps/standalone/native_tests/test_standalone_header_material.cpp": "96149cf482ad0a57512257a519b89198113f21b06c33b073b2861e13349d1809",
    "tools/compare_header_material.py": "8c49bad85ff311d0cc598e8bbe1c951f8013661ea123b49abb2d367d969eac5e",
    "tests/test_compare_header_material.py": "2ef6f296b56cad306012178b05a11555f966d770cfbe23432dcbe05095d168a5",
}

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write(name, data):
    (REPORTS / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def run(command, log, env=None):
    start = time.monotonic()
    with (REPORTS / log).open("wb") as output:
        result = subprocess.run([str(x) for x in command], cwd=ROOT, env=env,
                                stdout=output, stderr=subprocess.STDOUT)
    return {"command": [str(x) for x in command], "exit_code": result.returncode,
            "seconds": time.monotonic() - start, "log": log,
            "log_sha256": digest(REPORTS / log)}

def main():
    os.chdir(ROOT)
    for path, expected in EXPECTED.items():
        assert digest(ROOT / path) == expected, path
    files = set()
    for folder in ["include", "src", "apps", "plugins", "tools", "tests", "cmake", "data", ".github"]:
        for path in (ROOT / folder).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                files.add(path.relative_to(ROOT).as_posix())
    files.update(["CMakeLists.txt", "docs/design/atlas-cover-reference.jpg",
                  "docs/design/PERFORMANCE_PLATE_P1_CONTRACT.md"])
    inputs = {path: digest(ROOT / path) for path in sorted(files)}
    def unchanged():
        changed = [path for path, sha in inputs.items() if digest(ROOT / path) != sha]
        assert not changed, changed
    record = {"schema_version": 1, "started_utc": utc(),
              "source_base": "9d60dbf462a90fe422fd4e69757fe202264acb7c",
              "local_recovery": "3263b177d42e96309dcc23a287c586150ab2378e",
              "reconciled_remote": "03c70c103a4a0dd72b323529416b909c19a4e139",
              "source_sha256": inputs, "selection": SELECTION,
              "scope": "Combined source affected qualification; original 246/247 full run remains unchanged. Core, plugin and physical/product acceptance are separate.",
              "status": "running"}
    write("combined-qualification.json", record)
    print("Building coherent combined native targets", flush=True)
    record["build"] = run([CMAKE, "--build", BUILD, "--parallel", "3"], "combined-build.log")
    unchanged()
    write("combined-qualification.json", record)
    if record["build"]["exit_code"]:
        record["status"] = "build_failed"; write("combined-qualification.json", record); return 1
    for label, selection in [("all", []), ("affected", ["-R", SELECTION])]:
        command = [str(CTEST), "--test-dir", str(BUILD), "--show-only=json-v1", "--no-tests=error", *selection]
        found = subprocess.run(command, cwd=ROOT, capture_output=True)
        assert found.returncode == 0, found.stderr.decode(errors="replace")
        data = json.loads(found.stdout)
        (REPORTS / ("combined-" + label + "-discovery.json")).write_bytes(found.stdout)
        names = [test["name"] for test in data["tests"]]
        assert len(names) == len(set(names)) and names
        record[label + "_test_names"] = names
    write("combined-qualification.json", record)
    print("Running " + str(len(record["affected_test_names"])) + " combined affected CTests", flush=True)
    env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy", SDL_RENDER_DRIVER="software")
    record["affected_ctest"] = run([CTEST, "--test-dir", BUILD, "--output-on-failure", "--parallel", "1", "--no-tests=error", "-R", SELECTION,
        "--output-junit", REPORTS / "combined-affected-ctest.xml"], "combined-affected-ctest.log", env)
    detail = BUILD / "Testing/Temporary/LastTest.log"
    shutil.copy2(detail, REPORTS / "combined-affected-detail.log")
    cases = ET.parse(REPORTS / "combined-affected-ctest.xml").getroot().findall("testcase")
    record["affected_counts"] = {"tests": len(cases), "failed": sum(case.find("failure") is not None for case in cases),
                                 "skipped": sum(case.find("skipped") is not None for case in cases)}
    unchanged()
    record["input_stability_after_affected"] = True
    write("combined-qualification.json", record)
    if record["affected_ctest"]["exit_code"]:
        record["status"] = "affected_failed"; write("combined-qualification.json", record); return 1
    executable = BUILD / "apps/standalone/hammond_standalone"
    prior = json.loads((REPORTS / "integrated-application-qualification.json").read_text())
    q = {"schema_version": 1, "binary_sha256": digest(executable),
         "base_commit": record["source_base"], "reconciled_remote": record["reconciled_remote"],
         "source_sha256": {path: digest(ROOT / path) for path in prior["source_sha256"]},
         "build": "Coherent combined H1/P1 Release build; GCC14.2, SDL2.32.10, MIDI/VST3 OFF",
         "build_logs": ["combined-build.log"], "affected_result": "combined-qualification.json",
         "meaning": "Root source-to-build qualification following the passing affected selection. Capture and visual review remain separate."}
    write("combined-application-qualification.json", q)
    output = ROOT / "docs/design/native-gallery-console-combined"
    print("Capturing new combined application: " + q["binary_sha256"], flush=True)
    record["capture"] = run(["python3", "-B", ROOT / "tools/capture_standalone_interface.py",
        "--exe", executable, "--source-root", ROOT, "--build-root", BUILD,
        "--source-qualification", REPORTS / "combined-application-qualification.json",
        "--expected-exe-sha256", q["binary_sha256"], "--output", output,
        "--dummy-sdl", "--include-header-aspects", "--replay-time-scale", "3", "--timeout-seconds", "30"],
        "combined-capture.log", env)
    unchanged()
    record["input_stability_after_capture"] = True
    record["completed_utc"] = utc()
    record["status"] = "passed" if record["capture"]["exit_code"] == 0 else "capture_failed"
    write("combined-qualification.json", record)
    print(json.dumps({"status": record["status"], "affected": record["affected_counts"], "application_sha256": q["binary_sha256"]}), flush=True)
    return int(record["status"] != "passed")

if __name__ == "__main__":
    raise SystemExit(main())
