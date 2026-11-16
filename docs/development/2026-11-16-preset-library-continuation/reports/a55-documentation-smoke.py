#!/usr/bin/env python3
"""Bounded README observation: existing inputs, eight native calls, two renders.

No configure, build, installer, generator, CTest or existing audition is run.
Refuses existing work/evidence destinations. Original streams and WAVs survive.
"""
import argparse
import array
import datetime
import gzip
import hashlib
import io
import json
import math
import pathlib
import platform
import shlex
import shutil
import stat
import subprocess
import sys
import tarfile
import time
import wave


def identity(path):
    payload = path.read_bytes()
    metadata = path.stat()
    return {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(),
            "mode": stat.S_IMODE(metadata.st_mode), "mtime_ns": metadata.st_mtime_ns}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=pathlib.Path, required=True)
    parser.add_argument("--build", type=pathlib.Path, required=True)
    parser.add_argument("--work", type=pathlib.Path, required=True)
    parser.add_argument("--report-stem", default="a55-documentation-smoke")
    args = parser.parse_args()
    repo, build, work = (p.resolve() for p in (args.repo, args.build, args.work))
    reports = repo / "docs/development/2026-11-16-preset-library-continuation/reports"
    report_path = reports / (args.report_stem + ".json")
    archive_path = reports / (args.report_stem + "-originals.tar.gz")
    if work.exists() or report_path.exists() or archive_path.exists():
        raise SystemExit("Use absent work, report and archive destinations; nothing was changed.")
    for path in (build / "hammond_registration", build / "hammond_render", build / "nominal.b3p"):
        if not path.is_file():
            raise SystemExit("Required existing input absent: " + str(path))
    work.mkdir()
    evidence = work / "evidence"
    evidence.mkdir()
    shutil.copyfile(__file__, evidence / "observer.py")
    original_manifest_path = reports / "a38-headless-source-test.json"
    original_manifest = json.loads(original_manifest_path.read_text())
    watched = {name: identity(repo / name) for name in original_manifest["files"]}
    build_names = ["hammond_registration", "hammond_render", "nominal.b3p",
                   "CMakeCache.txt", "compile_commands.json", "build.ninja"]
    build_before = {name: identity(build / name) for name in build_names}
    def git(*tokens):
        return subprocess.check_output(["git", *tokens], cwd=repo).decode().strip()
    source = {"head": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}"),
              "status": git("status", "--short"), "a38_source_manifest": identity(original_manifest_path),
              "a38_head": original_manifest["head"], "current_files": watched,
              "different_from_a38": {name: {"a38": original_manifest["files"][name], "current": now}
                                    for name, now in watched.items()
                                    if now["sha256"] != original_manifest["files"][name]["sha256"]}}
    write_json(evidence / "source-before.json", source)
    documentation = {}
    for name in ["README.md", "docs/REGISTRATION_GUIDE.md", "CMakeLists.txt",
                 "cmake/InstallRegistrationTools.cmake", "apps/standalone/CMakeLists.txt",
                 "tools/registration.cpp", "tools/render.cpp", "tools/CliArguments.h",
                 "apps/standalone/RegistrationLibrary.cpp"]:
        documentation[name] = identity(repo / name)
    shutil.copyfile(repo / "README.md", evidence / "README-observed.md")
    shutil.copyfile(repo / "docs/REGISTRATION_GUIDE.md", evidence / "REGISTRATION_GUIDE-observed.md")
    pack = "data/registrations/starter-v1/entries"
    warm = "02 Warm Comp.b3registration"
    quiet = "01 Quiet Foundation.b3performance"
    for name in (warm, quiet):
        shutil.copyfile(repo / pack / name, evidence / name)
    tool, renderer = (str(build / name) for name in ("hammond_registration", "hammond_render"))
    destination = str(work / "prepared")
    prepared = work / "prepared/Warm Current.b3performance"
    materialize = [tool, "materialize", "--library", pack, "--key", warm,
                   "--current", pack + "/" + quiet, "--destination", destination, "--name", "Warm Current"]
    render = [renderer, "--profile", str(build / "nominal.b3p"), "--controls", str(prepared),
              "--output", str(work / "warm.wav"), "--frames", "24000", "--sample-rate", "48000",
              "--block-size", "64", "--seed", "0", "--note", "60", "--fail-on-clip"]
    direct = render.copy()
    direct[direct.index("--controls") + 1] = pack + "/" + warm
    direct[direct.index("--output") + 1] = str(work / "warm-original.wav")
    commands = [
        ("01-list", [tool, "list", "--library", pack], 0),
        ("02-inspect-current", [tool, "inspect", "--library", pack, "--key", quiet], 0),
        ("03-inspect-original", [tool, "inspect", "--library", pack, "--key", warm], 0),
        ("04-materialize", materialize, 0),
        ("05-inspect-prepared", [tool, "inspect", "--library", destination, "--key", prepared.name], 0),
        ("06-collision", materialize, 3),
        ("07-render-current", render, 0),
        ("08-render-original", direct, 0),
    ]
    environment = {"LC_ALL": "C", "TZ": "UTC", "PATH": ""}
    records = []
    def products():
        return {str(p.relative_to(work)): identity(p) for p in sorted(work.rglob("*"))
                if p.is_file() and evidence not in p.parents}
    failed = None
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for label, argv, expected_exit in commands:
        before = products()
        begin = time.monotonic()
        result = subprocess.run(argv, cwd=repo, env=environment, capture_output=True, timeout=30)
        elapsed = time.monotonic() - begin
        streams = {}
        for stream in ("stdout", "stderr"):
            path = evidence / (label + "." + stream)
            path.write_bytes(getattr(result, stream))
            streams[stream] = {"member": "evidence/" + path.name, **identity(path)}
        record = {"label": label, "argv": argv, "shell": shlex.join(argv), "cwd": str(repo),
                  "environment": environment, "returncode": result.returncode,
                  "expected_returncode": expected_exit, "seconds": elapsed,
                  "streams": streams, "products_before": before, "products_after": products()}
        records.append(record)
        write_json(evidence / "commands.json", records)
        if result.returncode != expected_exit:
            failed = label + " returned an unexpected exit; later native calls were not attempted."
            break
    checks = {}
    details = {}
    try:
        if failed:
            raise AssertionError(failed)
        outputs = {label: json.loads((evidence / (label + ".stdout")).read_bytes()) for label, _, _ in commands}
        current_raw = (repo / pack / quiet).read_bytes()
        warm_raw = (repo / pack / warm).read_bytes()
        expected = warm_raw.replace(b"expression 0.625\n", b"expression 0.5\n")
        checks["all_eight_expected_exits_empty_stderr"] = all(
            r["returncode"] == r["expected_returncode"] and r["streams"]["stderr"]["bytes"] == 0 for r in records)
        catalog = outputs["01-list"]["catalog"]
        checks["complete_exact_24_entry_list"] = (
            catalog["complete"] and catalog["candidate_count"] == 24 and catalog["warning_count"] == 0
            and sorted(x["key"] for x in catalog["entries"]) == sorted(p.name for p in (repo / pack).iterdir()))
        checks["read_only_commands_create_nothing"] = all(not r["products_after"] for r in records[:3])
        checks["quiet_inspection_full_bytes_expression_half"] = outputs["02-inspect-current"]["entry"]["canonical_controls"].encode() == current_raw and b"expression 0.5\n" in current_raw
        checks["warm_inspection_full_bytes_expression_five_eighths"] = outputs["03-inspect-original"]["entry"]["canonical_controls"].encode() == warm_raw and b"expression 0.625\n" in warm_raw
        checks["materialize_only_expression_changes"] = prepared.read_bytes() == expected and expected != warm_raw
        checks["prepared_inspection_full_bytes"] = outputs["05-inspect-prepared"]["entry"]["canonical_controls"].encode() == expected
        saved, collision = outputs["04-materialize"], outputs["06-collision"]
        checks["create_only_save_and_preserving_collision"] = (saved["committed"] is True
            and collision["code"] == "NameExists" and collision["committed"] is False
            and records[5]["products_before"] == records[5]["products_after"])
        for label, control_path, expected_bytes, wav in [
            ("07-render-current", prepared, expected, work / "warm.wav"),
            ("08-render-original", repo / pack / warm, warm_raw, work / "warm-original.wav")]:
            result = outputs[label]
            controls = result["controls"]
            checks[label + "_full_schema6_provenance"] = (result["render_schema_version"] == 6
                and result["status"] == "ok" and result["evidence_status"] == "unmeasured"
                and controls == {"schema_version": 1, "restore_policy": "full-state-including-expression",
                                 "path": str(control_path), "source_version": 4,
                                 "source_bytes": len(expected_bytes), "canonical_b3controls4": expected_bytes.decode()})
            with wave.open(str(wav), "rb") as stream:
                params = stream.getparams()
                pcm = stream.readframes(params.nframes)
            samples = array.array("h", pcm)
            if sys.byteorder != "little":
                samples.byteswap()
            pcm_peak = max(abs(x) for x in samples)
            checks[label + "_audio_and_clip"] = (params.nchannels == 2 and params.sampwidth == 2
                and params.framerate == 48000 and params.nframes == 24000 and params.comptype == "NONE"
                and len(pcm) == 96000 and samples[::2] == samples[1::2] and 0 < pcm_peak < 32767
                and result["frames"] == 24000 and result["sample_rate"] == 48000
                and result["block_size"] == 64 and result["seed"] == 0
                and result["clipped_frames"] == result["clipped_channel_samples"] == 0
                and math.isfinite(result["peak"]) and math.isfinite(result["rms"]))
            details[label] = {"renderer_report": result, "wav": identity(wav), "pcm_peak": pcm_peak,
                              "pcm_sha256": hashlib.sha256(pcm).hexdigest(), "sample_frames": params.nframes}
        checks["different_audio_for_different_expression"] = details["07-render-current"]["pcm_sha256"] != details["08-render-original"]["pcm_sha256"]
        checks["exact_three_products_without_sidecars"] = sorted(products()) == ["prepared/Warm Current.b3performance", "warm-original.wav", "warm.wav"]
    except Exception as error:
        failed = type(error).__name__ + ": " + str(error)
    watched_after = {name: identity(repo / name) for name in watched}
    build_after = {name: identity(build / name) for name in build_names}
    checks["all_540_watched_source_files_unchanged"] = watched == watched_after
    checks["existing_binaries_profile_and_build_metadata_unchanged"] = build_before == build_after
    changed = {name: {"before": before, "after": watched_after[name]} for name, before in watched.items() if before != watched_after[name]}
    write_json(evidence / "checks.json", {"checks": checks, "details": details, "observer_failure": failed})
    write_json(evidence / "source-after.json", {"changed": changed, "build_before": build_before, "build_after": build_after})
    members = {}
    with archive_path.open("xb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for path in sorted(work.rglob("*")):
                    if not path.is_file():
                        continue
                    name = path.relative_to(work).as_posix()
                    payload = path.read_bytes()
                    entry = tarfile.TarInfo(name)
                    entry.size, entry.mode, entry.mtime = len(payload), 0o644, 0
                    archive.addfile(entry, io.BytesIO(payload))
                    members[name] = {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
    receipt = {"schema": "a55-documented-commands-observation-v1", "started_utc": started,
               "finished_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "observer": "/root/w10_a55", "repo": str(repo), "build": str(build), "work": str(work),
               "source": {k: v for k, v in source.items() if k != "current_files"},
               "documentation": documentation, "build_inputs": build_before,
               "runtime": {"system": platform.system(), "machine": platform.machine(),
                           "release": platform.release(), "libc": platform.libc_ver(), "python": sys.version},
               "commands": records, "checks": checks, "audio": details,
               "observer_failure": failed, "result": "pass" if not failed and all(checks.values()) else "fail",
               "archive": {"path": archive_path.name, **identity(archive_path), "members": members},
               "execution_boundary": "Existing A38 SDK-free Linux executables; exactly eight native calls and two new half-second renders. No configure/build/install/generator/CTest/UI/32-clip rerun; no Windows/macOS execution or fresh remote/CI observation."}
    write_json(report_path, receipt)
    print(json.dumps({"result": receipt["result"], "report": str(report_path),
                      "native_calls": len(records), "checks": checks, "observer_failure": failed,
                      "archive_bytes": archive_path.stat().st_size}, indent=2))
    return 0 if receipt["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
