"""Bounded, source-identified A41 sanitizer qualification; no source edits."""
from __future__ import annotations

import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

REPORTS = Path(__file__).resolve().parent
ROOT = REPORTS.parents[3]
BUILD = ROOT.parent / "build-interface-asan"
TOOLS = Path("/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin")
PYTHON = "/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12"
TARGETS = [
    "test_standalone_ui",
    "test_standalone_preset_ui",
    "test_standalone_workspaces_author",
    "test_standalone_workspace_acceptance",
    "test_standalone_projection",
    "test_standalone_inspection_author",
    "test_standalone_inspection_acceptance",
    "test_standalone_workspace_continuity",
    "test_standalone_drawing",
    "test_standalone_quad_drawing",
    "test_standalone_workspace_raster",
    "test_standalone_scaled_view",
    "test_standalone_preset_raster",
]
RUNTIME_ENV = {
    "ASAN_OPTIONS": "detect_leaks=1:halt_on_error=1",
    "UBSAN_OPTIONS": "print_stacktrace=1:halt_on_error=1",
    "LSAN_OPTIONS": "exitcode=23",
    "SDL_VIDEODRIVER": "dummy",
    "SDL_AUDIODRIVER": "dummy",
    "SDL_RENDER_DRIVER": "software",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name: str, value: object) -> None:
    (REPORTS / ("a41-" + name + ".json")).write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def freeze(phase: str) -> None:
    peer = json.loads((REPORTS / "a40-source-freeze.json").read_text())
    boundary = json.loads((REPORTS / "a12-boundary-inventory.json").read_text())
    paths = set(peer["files"]) | {row[0] for row in boundary["files"]} | {
        "CMakePresets.json", "docs/INTERFACE_WORKSPACE_CONTRACT.md",
        "docs/INTERFACE_GEOMETRY_CONTRACT.md", "docs/INTERFACE_INSPECTION_CONTRACT.md",
    }
    files = {name: sha(ROOT / name) for name in sorted(paths)}
    peer_mismatches = [name for name, digest in peer["files"].items() if files[name] != digest]
    protected_mismatches = [row[0] for row in boundary["files"] if files[row[0]] != row[4]]
    before_path = REPORTS / "a41-source-before.json"
    before = json.loads(before_path.read_text()) if phase != "before" and before_path.exists() else None
    before_mismatches = [name for name, digest in before["files"].items() if files[name] != digest] if before else []
    record = {
        "agent": "/root/w07_a41_native_sanitizers", "assignment": 41, "wave": 7,
        "phase": phase, "captured_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "base_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "base_tree": subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip(),
        "file_count": len(files), "files": files,
        "source_digest_encoding": "sha256(sorted UTF-8 path + NUL + sha256 + LF)",
        "source_digest": hashlib.sha256("".join(name + "\0" + digest + "\n" for name, digest in files.items()).encode()).hexdigest(),
        "a40_source_digest": peer["source_digest"], "a40_mismatches": peer_mismatches,
        "protected_count": len(boundary["files"]), "protected_mismatches": protected_mismatches,
        "before_mismatches": before_mismatches,
    }
    write("source-" + phase, record)
    print(json.dumps({key: value for key, value in record.items() if key != "files"}), flush=True)
    if peer_mismatches or protected_mismatches or before_mismatches:
        raise SystemExit("Source identity changed; consult integrator before qualification")


def run(label: str, args: list[str], extra_env: dict[str, str] | None = None) -> int:
    env_delta = {"PYTHONDONTWRITEBYTECODE": "1", **(extra_env or {})}
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    stamp = time.monotonic()
    log = REPORTS / ("a41-" + label + ".txt")
    with log.open("w", encoding="utf-8") as stream:
        process = subprocess.run(args, cwd=ROOT, env={**os.environ, **env_delta},
                                 stdout=stream, stderr=subprocess.STDOUT, check=False)
    record = {
        "command": args, "cwd": str(ROOT), "environment_overrides": env_delta,
        "started_at_utc": started, "elapsed_seconds": round(time.monotonic() - stamp, 6),
        "returncode": process.returncode, "log": str(log.relative_to(ROOT)),
        "log_sha256": sha(log), "log_bytes": log.stat().st_size,
    }
    write(label, record)
    print(json.dumps(record), flush=True)
    print("\n".join(log.read_text(errors="replace").splitlines()[-25:]), flush=True)
    return process.returncode


def direct_diagnostic(name: str) -> int:
    """One integrator-authorized completion probe, separate from the failed gate."""
    allowed = {
        "test_standalone_workspace_raster": "direct-workspace-raster",
        "test_standalone_scaled_view": "direct-scaled-view",
        "test_standalone_preset_raster": "direct-preset-raster",
    }
    assert name in allowed
    label = allowed[name]
    assert not (REPORTS / ("a41-" + label + ".json")).exists(), "One attempt only"
    original = json.loads((REPORTS / "a41-instrumentation.json").read_text())["executables"][name]
    executable = Path(original["path"])
    assert sha(executable) == original["sha256"]
    log = REPORTS / ("a41-" + label + ".txt")
    env_delta = {"PYTHONDONTWRITEBYTECODE": "1", **RUNTIME_ENV,
                 "ASAN_OPTIONS": "detect_leaks=0:halt_on_error=1"}
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    stamp = time.monotonic()
    timed_out = False
    with log.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen([str(executable)], cwd=BUILD / "apps/standalone",
                                   env={**os.environ, **env_delta}, stdout=stream,
                                   stderr=subprocess.STDOUT)
        try:
            returncode = process.wait(timeout=240)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            returncode = process.wait()
    elapsed = time.monotonic() - stamp
    output = log.read_text(errors="replace")
    diagnostics = [line for line in output.splitlines() if re.search(
        r"ERROR: AddressSanitizer|UndefinedBehaviorSanitizer|runtime error:|SUMMARY:.*Sanitizer", line)]
    record = {
        "test_name": name, "command": [str(executable)], "cwd": str(BUILD / "apps/standalone"),
        "environment_overrides": env_delta, "started_at_utc": started,
        "elapsed_seconds": round(elapsed, 6), "timeout_seconds": 240, "timed_out": timed_out,
        "returncode": returncode, "executable_sha256_before": original["sha256"],
        "executable_sha256_after": sha(executable), "log": str(log.relative_to(ROOT)),
        "log_sha256": sha(log), "log_bytes": log.stat().st_size,
        "asan_ubsan_diagnostics": diagnostics,
        "scope": "One separately authorized bounded direct diagnostic. Original CTest 10 PASS/3 TIMEOUT is unchanged. Leak qualification remains blocked.",
    }
    write(label, record)
    print(json.dumps(record), flush=True)
    print(output, flush=True)
    return returncode


if __name__ == "__main__":
    action = sys.argv[1]
    if action == "freeze":
        freeze(sys.argv[2])
    elif action == "configure":
        assert not BUILD.exists(), "Only one newly configured A41 build is authorized"
        raise SystemExit(run("configure", [
            str(TOOLS / "cmake"), "-S", str(ROOT), "-B", str(BUILD), "-G", "Unix Makefiles",
            "-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_C_COMPILER=/usr/bin/gcc",
            "-DCMAKE_CXX_COMPILER=/usr/bin/g++", "-DBUILD_TESTING=ON",
            "-DHAMMOND_ENABLE_SANITIZERS=ON", "-DHAMMOND_BUILD_STANDALONE=ON",
            "-DHAMMOND_ENABLE_MIDI=OFF", "-DHAMMOND_BUILD_VST3=OFF",
            "-DHAMMOND_SDL2_ROOT=/workspace/scratch/7ffc2842608b/SDL2", "-DSDL_ALSA=OFF",
            "-DCMAKE_C_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer",
            "-DPython3_EXECUTABLE=" + PYTHON,
        ]))
    elif action == "build":
        raise SystemExit(run("build", [str(TOOLS / "cmake"), "--build", str(BUILD),
                                      "--parallel", "2", "--target", *TARGETS]))
    elif action == "discover":
        raise SystemExit(run("discovery", [str(TOOLS / "ctest"), "--test-dir", str(BUILD),
                                          "-C", "Release", "--show-only=json-v1"]))
    elif action == "direct-diagnostic":
        raise SystemExit(direct_diagnostic(sys.argv[2]))
    elif action in ("test", "test-asan-ubsan"):
        names = sys.argv[3:] if len(sys.argv) > 3 else TARGETS
        assert all(name in TARGETS for name in names)
        label = sys.argv[2]
        raise SystemExit(run(label, [str(TOOLS / "ctest"), "--test-dir", str(BUILD),
                                    "-C", "Release", "--output-on-failure", "--no-tests=error",
                                    "--parallel", "1", "-V", "-R", "^(" + "|".join(names) + ")$",
                                    "--output-junit", str(REPORTS / ("a41-" + label + ".xml"))],
                             RUNTIME_ENV if action == "test" else {
                                 **RUNTIME_ENV,
                                 "ASAN_OPTIONS": "detect_leaks=0:halt_on_error=1",
                             }))
    else:
        raise SystemExit("Unknown evidence action")
