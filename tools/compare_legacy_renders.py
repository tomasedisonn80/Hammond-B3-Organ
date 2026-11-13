#!/usr/bin/env python3
"""Compare all eight retained scores with explicit baseline/current executables.

This invokes trusted, already-built project renderers; it does not acquire or
build code. Bounded input/log reads, fixed catalog count, process timeouts and a
fresh output directory keep the replay reproducible. Equality is byte-exact.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import threading
import wave


ROOT = Path(__file__).resolve().parents[1]
CATALOGS = (("examples/fixtures/catalog-v1.json", "nominal-engine-fixtures-v1", 5),
            ("examples/fixtures/console/console-catalog-v1.json", "nominal-console-fixtures-v1", 3))
LOG_LIMIT = 16384
MAX_FRAMES = 192000


class ComparisonError(ValueError):
    """The supplied evidence is incomplete, invalid or not byte-identical."""


def require(condition, message):
    if not condition:
        raise ComparisonError(message)


def stamp(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def read_file(path, limit, *, retain=True):
    """Reject nonregular/oversized/replaced inputs; hash with bounded storage."""
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and 0 <= before.st_size <= limit,
            f"not a regular file within {limit} bytes: {path}")
    digest = hashlib.sha256()
    chunks = []
    count = 0
    with path.open("rb") as stream:
        opened = os.fstat(stream.fileno())
        require(stat.S_ISREG(opened.st_mode) and opened.st_size == before.st_size,
                f"file changed before reading: {path}")
        if os.name == "posix":
            require((opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino),
                    f"file identity changed: {path}")
        while chunk := stream.read(min(65536, limit - count + 1)):
            count += len(chunk)
            require(count <= limit, f"file grew beyond limit: {path}")
            digest.update(chunk)
            if retain:
                chunks.append(chunk)
        require(stamp(opened) == stamp(os.fstat(stream.fileno())), f"file changed while reading: {path}")
    require(count == before.st_size and stamp(before) == stamp(path.lstat()),
            f"file changed after reading: {path}")
    return {"path": str(path), "sha256": digest.hexdigest(), "size_bytes": count}, b"".join(chunks)


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json(raw):
    def invalid(token):
        raise ComparisonError(f"non-JSON number: {token}")
    def finite(token):
        value = float(token)
        require(math.isfinite(value), "nonfinite JSON number")
        return value
    return json.loads(raw.decode("utf-8"), object_pairs_hook=object_pairs,
                      parse_constant=invalid, parse_float=finite)


def integer(value, low, high, label):
    require(type(value) is int and low <= value <= high, f"invalid {label}")
    return value


def score_plan(profile_digest):
    plans, catalogs = [], []
    identifiers = set()
    for relative, identity, count in CATALOGS:
        path = ROOT / relative
        record, raw = read_file(path, 256 * 1024)
        value = parse_json(raw)
        require(type(value) is dict, "catalog must be an object")
        require(value.get("schema_version") == 1 and type(value["schema_version"]) is int
                and value.get("catalog_id") == identity, f"unsupported catalog: {path}")
        require(value["profile"]["compiled_sha256"] == profile_digest,
                f"profile bytes differ from catalog: {path}")
        require(type(value["fixtures"]) is list and len(value["fixtures"]) == count,
                f"unexpected fixture count: {path}")
        catalogs.append(record)
        for fixture in value["fixtures"]:
            require(type(fixture) is dict, "fixture must be an object")
            name = fixture["id"]
            require(type(name) is str and re.fullmatch(r"[a-z0-9-]{1,80}", name)
                    and name not in identifiers, "invalid or duplicate fixture ID")
            identifiers.add(name)
            relative_score = fixture["events"]["path"]
            require(type(relative_score) is str and relative_score == name + ".events",
                    f"unexpected score filename: {name}")
            score = path.parent / relative_score
            score_record, _ = read_file(score, 16384)
            require(score_record["sha256"] == fixture["events"]["sha256"],
                    f"score differs from catalog: {name}")
            frames = integer(fixture["frames"], 1, MAX_FRAMES, "frames")
            rate = integer(fixture["sample_rate"], 48000, 48000, "catalog sample rate")
            block = integer(fixture["block_size"], 1, 65536, "block size")
            seed = integer(fixture["seed"], 0, 2**64 - 1, "seed")
            registration = fixture["registration"]
            require(type(registration) is str and re.fullmatch(r"[0-8]{9}", registration),
                    "invalid registration")
            controls = fixture.get("controls", {"contacts": "ideal", "percussion": "off",
                                                "percussion_volume": "normal", "percussion_decay": "slow"})
            choices = {"contacts": ("ideal", "nominal"), "percussion": ("off", "second", "third"),
                       "percussion_volume": ("normal", "soft"), "percussion_decay": ("slow", "fast")}
            require(type(controls) is dict and controls.keys() == choices.keys(), "invalid console controls")
            require(all(type(controls[key]) is str and controls[key] in choices[key] for key in choices),
                    "invalid console choice")
            plans.append({"id": name, "score": score_record, "frames": frames, "sample_rate": rate,
                          "block_size": block, "seed": seed, "drawbars": registration, "controls": controls})
    return plans, catalogs


def invoke(argv):
    """Drain both pipes concurrently, retain at most 16 KiB each, reject excess."""
    process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    captures = [{"bytes": bytearray(), "count": 0, "error": None} for _ in range(2)]

    def drain(stream, capture):
        try:
            with stream:
                while chunk := stream.read(4096):
                    capture["count"] += len(chunk)
                    capture["bytes"].extend(chunk[:max(0, LOG_LIMIT - len(capture["bytes"]))])
        except OSError as error:
            capture["error"] = str(error)

    threads = [threading.Thread(target=drain, args=(stream, capture), daemon=True)
               for stream, capture in zip((process.stdout, process.stderr), captures)]
    for thread in threads:
        thread.start()
    timed_out = False
    try:
        process.wait(timeout=30)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        process.wait(timeout=5)
    for thread in threads:
        thread.join(timeout=1)
    require(not timed_out and not any(thread.is_alive() for thread in threads), "renderer timed out")
    require(all(capture["count"] <= LOG_LIMIT and capture["error"] is None for capture in captures),
            "renderer log exceeded bound or failed capture")
    stdout, stderr = (bytes(capture["bytes"]) for capture in captures)
    require(process.returncode == 0 and not stderr, f"renderer failed: exit {process.returncode}, {stderr!r}")
    metrics = parse_json(stdout)
    require(type(metrics) is dict and metrics.get("status") == "ok", "renderer did not report success")
    return metrics, stdout


def wav_record(path, frames, rate):
    record, raw = read_file(path, 44 + MAX_FRAMES * 4)
    require(len(raw) == 44 + frames * 4, "unexpected WAV byte length")
    with wave.open(io.BytesIO(raw), "rb") as stream:
        require((stream.getnchannels(), stream.getsampwidth(), stream.getframerate(),
                 stream.getnframes(), stream.getcomptype()) == (2, 2, rate, frames, "NONE"),
                "unexpected WAV format")
        pcm = stream.readframes(frames)
    require(len(pcm) == frames * 4, "incomplete PCM payload")
    record["pcm_sha256"] = hashlib.sha256(pcm).hexdigest()
    record["pcm_bytes"] = len(pcm)
    return record, raw, pcm


def compare(baseline_renderer, baseline_profile, current_renderer, current_profile, output_dir):
    paths = [Path(path).resolve(strict=True) for path in
             (baseline_renderer, baseline_profile, current_renderer, current_profile)]
    records = [read_file(path, 512 * 1024 * 1024 if index in (0, 2) else 128 * 1024, retain=False)[0]
               for index, path in enumerate(paths)]
    require(records[1]["sha256"] == records[3]["sha256"], "baseline and current profiles differ")
    plans, catalogs = score_plan(records[1]["sha256"])
    output = Path(output_dir).absolute()
    require(not os.path.lexists(output) and output.parent.is_dir(), "output directory must be new with an existing parent")
    output.mkdir()
    results = []
    for plan in plans:
        rendered = []
        for variant, renderer, profile, explicit_zero in (
                ("baseline", paths[0], paths[1], False),
                ("current-default", paths[2], paths[3], False),
                ("current-zero", paths[2], paths[3], True)):
            wav_path = output / f"{plan['id']}-{variant}.wav"
            argv = [str(renderer), "--profile", str(profile), "--output", str(wav_path)]
            for name in ("frames", "sample_rate", "block_size", "seed", "drawbars"):
                argv.extend(("--" + name.replace("_", "-"), str(plan[name])))
            argv.extend(("--events", plan["score"]["path"]))
            for name, value in plan["controls"].items():
                argv.extend(("--" + name.replace("_", "-"), value))
            if explicit_zero:
                argv.extend(("--pedal-drawbars", "00"))
            argv.append("--fail-on-clip")
            metrics, stdout = invoke(argv)
            for key in ("frames", "sample_rate", "block_size", "seed"):
                require(type(metrics[key]) is int and metrics[key] == plan[key], f"metric differs: {key}")
            require(metrics["clipped_frames"] == 0 and metrics["clipped_channel_samples"] == 0,
                    "legacy render clipped")
            record, raw, pcm = wav_record(wav_path, plan["frames"], plan["sample_rate"])
            with (output / f"{plan['id']}-{variant}.stdout.json").open("xb") as stream:
                stream.write(stdout)
            rendered.append((raw, pcm, {"variant": variant, "argv": argv, "wav": record,
                                        "metrics": metrics, "stdout_sha256": hashlib.sha256(stdout).hexdigest()}))
        require(rendered[0][0] == rendered[1][0] == rendered[2][0], f"WAV bytes differ: {plan['id']}")
        require(rendered[0][1] == rendered[1][1] == rendered[2][1], f"PCM bytes differ: {plan['id']}")
        # Schema/model additions are intentional; every retained float/PCM claim must agree.
        common = set(rendered[0][2]["metrics"]) - {"render_schema_version"}
        for key in common:
            require(rendered[0][2]["metrics"][key] == rendered[1][2]["metrics"][key]
                    == rendered[2][2]["metrics"][key], f"legacy metric differs: {plan['id']} {key}")
        results.append({**plan, "wav_equal": True, "pcm_equal": True,
                        "renders": [item[2] for item in rendered]})
    for record in [*records, *catalogs, *(plan["score"] for plan in plans)]:
        path = Path(record["path"])
        require(read_file(path, record["size_bytes"], retain=False)[0] == record,
                f"input changed during replay: {path}")
    report = {"schema_version": 1, "status": "byte_identical", "scope": "same-toolchain-synthetic-replay",
              "baseline_renderer": records[0], "baseline_profile": records[1],
              "current_renderer": records[2], "current_profile": records[3], "catalogs": catalogs,
              "fixture_count": len(results), "render_invocations": len(results) * 3,
              "physical_fidelity": "not_established", "fixtures": results}
    with (output / "comparison.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    for name in ("baseline-renderer", "baseline-profile", "current-renderer", "current-profile", "output-dir"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    try:
        report = compare(**vars(args))
    except (ComparisonError, OSError, ValueError, KeyError, TypeError, RecursionError,
            subprocess.SubprocessError, wave.Error) as error:
        print(f"legacy comparison failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps({key: report[key] for key in ("status", "fixture_count", "render_invocations")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
