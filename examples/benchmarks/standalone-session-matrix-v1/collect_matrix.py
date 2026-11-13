#!/usr/bin/env python3
"""Run the fixed sixty-case matrix once; preserve every raw result and interval."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import shlex
import stat
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from verify_matrix import (BUFFERS, RATES, SHARED_KEYS, WORKLOADS, loads, require,
                           semantic_sha256, verify_matrix, verify_report)


def file_identity(path):
    payload = path.read_bytes()
    return {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("repo", "source-root", "binary", "profile", "source-manifest", "output", "raw-dir"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--origin", default="caller-supplied coherent SDK-free Release build")
    args = parser.parse_args()
    for name in ("repo", "source_root", "binary", "profile", "source_manifest"):
        setattr(args, name, getattr(args, name).resolve(strict=True))
    require(not args.output.exists() and not args.raw_dir.exists(), "use fresh output and raw directory")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.raw_dir.mkdir(parents=True)
    def git(*arguments):
        return subprocess.check_output(["git", "-C", str(args.repo), *arguments])
    commit = git("rev-parse", args.commit + "^{commit}").decode().strip()
    tree = git("rev-parse", commit + "^{tree}").decode().strip()
    tracked = []
    for item in git("ls-tree", "-rz", commit).split(b"\0"):
        if not item:
            continue
        meta, raw_path = item.split(b"\t", 1)
        mode, kind, blob = meta.decode().split()
        require(kind == "blob" and mode in ("100644", "100755"), "ordinary tracked source files")
        tracked.append((raw_path.decode(), mode, blob))
    def verify_source():
        entries = []
        for name, mode, blob in tracked:
            path = args.source_root / name
            metadata = path.lstat()
            require(stat.S_ISREG(metadata.st_mode), "source must be regular: " + name)
            content = path.read_bytes()
            actual_blob = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
            require(actual_blob == blob and bool(metadata.st_mode & 0o111) == (mode == "100755"),
                    "source bytes/mode differ: " + name)
            entries.append({"path": name, "mode": mode, "blob": blob,
                            "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)})
        return entries
    inventory = verify_source()
    manifest = loads(args.source_manifest.read_text(encoding="utf-8"))
    for entry in manifest["entries"]:
        require(file_identity(args.source_root / entry["path"])["sha256"] == entry["sha256"],
                "manifest source identity: " + entry["path"])
    binary_identity, profile_identity = file_identity(args.binary), file_identity(args.profile)
    build_root = args.profile.parent
    cache = (build_root / "CMakeCache.txt").read_text(encoding="utf-8")
    require("HAMMOND_BUILD_STANDALONE:BOOL=OFF" in cache and "HAMMOND_BUILD_VST3:BOOL=OFF" in cache,
            "this collection is an ordinary SDK-free build")
    compile_commands = loads((build_root / "compile_commands.json").read_text(encoding="utf-8"))
    relevant_commands = [entry for entry in compile_commands if any(token in entry["command"] for token in
                         ("hammond_core.dir/", "hammond_standalone_support.dir/", "hammond_standalone_benchmark.dir/"))]
    require(len(relevant_commands) == 23, "expected 19 core plus three Session-library plus benchmark objects")
    for entry in relevant_commands:
        command = shlex.split(entry["command"])
        require("-O3" in command and "-DNDEBUG" in command and
                not any("sanitize" in token for token in command), "Release compilation identity")
    overrides = {"LC_ALL": "C.UTF-8", "SDL_AUDIODRIVER": "hammond_matrix_missing_driver",
                 "SDL_VIDEODRIVER": "hammond_matrix_missing_driver"}
    environment = dict(os.environ, **overrides)
    matrix = {
        "schema": "hammond-session-matrix-evidence-v1",
        "source": {"commit": commit, "tree": tree, "tracked_files_verified": len(inventory),
                   "source_inventory_sha256": semantic_sha256(inventory), "benchmark_manifest": manifest},
        "execution": {
            "utc_start": datetime.now(timezone.utc).isoformat(), "origin": args.origin,
            "binary": dict(path=str(args.binary), **binary_identity),
            "profile": dict(path=str(args.profile), **profile_identity),
            "source_root": str(args.source_root), "cwd": str(args.raw_dir.resolve()),
            "host": {"system": platform.system(), "release": platform.release(), "machine": platform.machine(),
                     "libc": list(platform.libc_ver()), "python": platform.python_version(),
                     "allowed_cpus": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None},
            "environment_overrides": overrides, "other_environment": "inherited; shared host with concurrent agent work",
            "cache": file_identity(build_root / "CMakeCache.txt"),
            "compile_commands": file_identity(build_root / "compile_commands.json"),
            "relevant_compile_commands": relevant_commands,
            "affinity_changed": False, "power_or_thermal_control": False,
            "retries": 0, "per_process_watchdog_seconds": 30,
        },
        "common_report": None, "cases": [],
    }
    errors = []
    for number, (work, rate, block) in enumerate(itertools.product(WORKLOADS, RATES, BUFFERS), 1):
        case_id = f"{number:02d}-{work}-{rate}-{block}"
        argv = [str(args.binary), "--profile", str(args.profile), "--sample-rate", str(rate),
                "--buffer-frames", str(block), "--iterations", "100", "--warmup", "16", "--workload", work]
        started_utc = datetime.now(timezone.utc).isoformat()
        started = time.perf_counter_ns()
        process = subprocess.run(argv, cwd=args.raw_dir, env=environment, capture_output=True, timeout=30, check=False)
        elapsed = time.perf_counter_ns() - started
        (args.raw_dir / (case_id + ".stdout.json")).write_bytes(process.stdout)
        (args.raw_dir / (case_id + ".stderr.txt")).write_bytes(process.stderr)
        metadata = {"id": case_id, "argv": argv, "utc_start": started_utc, "wall_elapsed_ns": elapsed,
                    "returncode": process.returncode, "stdout_bytes": len(process.stdout),
                    "stdout_sha256": hashlib.sha256(process.stdout).hexdigest(),
                    "stderr_bytes": len(process.stderr), "stderr_sha256": hashlib.sha256(process.stderr).hexdigest()}
        (args.raw_dir / (case_id + ".process.json")).write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        report = loads(process.stdout.decode("utf-8"))
        shared = {key: report[key] for key in SHARED_KEYS}
        if matrix["common_report"] is None:
            matrix["common_report"] = shared
        require(shared == matrix["common_report"], "common source/identity/claim fields changed")
        metadata["parsed_report_sha256"] = semantic_sha256(report)
        metadata["report"] = {key: value for key, value in report.items() if key not in SHARED_KEYS}
        matrix["cases"].append(metadata)
        try:
            require(process.returncode == 0 and process.stderr == b"", "actual process success")
            verify_report(report)
        except (ValueError, KeyError) as error:
            errors.append({"case": case_id, "error": str(error)})
        if number % 15 == 0:
            print(f"Collected {number}/60; verification errors={len(errors)}", flush=True)
    matrix["execution"]["utc_end"] = datetime.now(timezone.utc).isoformat()
    require(verify_source() == inventory, "source changed during collection")
    require(file_identity(args.binary) == binary_identity and file_identity(args.profile) == profile_identity,
            "benchmark or profile changed during collection")
    matrix["execution"]["source_binary_profile_unchanged"] = True
    matrix["verification_errors"] = errors
    args.output.write_text(json.dumps(matrix, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n",
                           encoding="utf-8")
    require(not errors, "retained verification errors: " + repr(errors))
    print(json.dumps({"status": "passed", **verify_matrix(matrix)}, indent=2))


if __name__ == "__main__":
    main()
