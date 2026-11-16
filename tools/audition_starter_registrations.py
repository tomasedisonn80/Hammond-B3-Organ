#!/usr/bin/env python3
"""Audition the admitted twelve proposed recipes with the real dry renderer.

Standard library only. Required --renderer/--profile/--pack/--output inputs are
explicit; output must be a missing child of an existing, non-aliased directory.
All clips are exactly one second at 48 kHz. Both suffixes use --controls FULL
STATE INCLUDING EXPRESSION, not Registration's expression-preserving recall.

run_auditions returns the saved manifest. Only status == 'succeeded' is success.
Preflight errors create nothing. After output creation, failures retain their
actual partial files and reports; this batch is not atomic and never resumes.
This is proposed nominal dry Engine software evidence, not specimen evidence.
"""

from __future__ import annotations

import argparse
from array import array
import hashlib
import io
import json
import math
import os
from pathlib import Path
import stat
import subprocess
import sys
import wave


ROOT = Path(__file__).resolve().parents[1]
FRAMES = SAMPLE_RATE = 48000
MAX_INPUT_BYTES = 512 * 1024 * 1024
MAX_LOG_BYTES = 1024 * 1024
NAMES = (
    "01 Quiet Foundation", "02 Warm Comp", "03 Clear Lead", "04 Reed Edge",
    "05 Bright Ensemble", "06 High Shimmer", "07 Percussive Pair", "08 Slow Accent",
    "09 Split Dialogue", "10 Pedal Study", "11 Fixed Contrast", "12 Manual Return",
)
SCORES = {
    "audition": "starter-audition.events",
    "banks-reveal": "starter-banks-reveal.events",
    "manual-return": "starter-manual-return.events",
}
RESTORE_POLICY = "full-state-including-expression"


class AuditionError(ValueError):
    """Refused input or incomplete audition evidence."""


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AuditionError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _nonfinite(token):
    raise AuditionError(f"nonfinite JSON number: {token}")


def _number(token):
    value = float(token)
    if not math.isfinite(value):
        _nonfinite(token)
    return value


def _json(raw):
    return json.loads(raw.decode("utf-8"), object_pairs_hook=_object,
                      parse_float=_number, parse_constant=_nonfinite)


def _stamp(value):
    return (value.st_dev, value.st_ino, value.st_mode, value.st_size,
            value.st_mtime_ns, value.st_ctime_ns)


def _file(path, limit, *, retain=False):
    """Hash actual bounded regular-file bytes, rejecting final symlinks/changes."""
    path = Path(path)
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or not 0 <= before.st_size <= limit:
        raise AuditionError(f"expected a regular, non-symlink file <= {limit} bytes: {path}")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    digest, count, raw = hashlib.sha256(), 0, bytearray()
    with os.fdopen(os.open(path, flags), "rb") as stream:
        opened = os.fstat(stream.fileno())
        if (not stat.S_ISREG(opened.st_mode) or opened.st_size != before.st_size
                or (os.name == "posix" and
                    (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino))):
            raise AuditionError(f"input changed before reading: {path}")
        while True:
            chunk = stream.read(min(65536, limit - count + 1))
            if not chunk:
                break
            count += len(chunk)
            if count > limit:
                raise AuditionError(f"file exceeds {limit} bytes: {path}")
            digest.update(chunk)
            if retain:
                raw.extend(chunk)
        if _stamp(opened) != _stamp(os.fstat(stream.fileno())):
            raise AuditionError(f"input changed while reading: {path}")
    if count != before.st_size or _stamp(before) != _stamp(path.lstat()):
        raise AuditionError(f"input changed while reading: {path}")
    return {"path": str(path.resolve(strict=True)), "size_bytes": count,
            "sha256": digest.hexdigest()}, bytes(raw) if retain else None


def _fresh_output(value):
    path = Path(value)
    if ".." in path.parts:
        raise AuditionError("output must not contain '..' aliases")
    path = Path(os.path.abspath(path))
    if os.path.lexists(path):
        raise AuditionError(f"output already exists; choose a fresh directory: {path}")
    parent = path.parent.resolve(strict=True)
    if parent != path.parent or not parent.is_dir():
        raise AuditionError("output parent must be an existing directory without symlink aliases")
    return path


def _preflight(renderer, profile, pack, output, timeout_seconds):
    if (isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float))
            or not math.isfinite(timeout_seconds) or not 0.1 <= timeout_seconds <= 30):
        raise AuditionError("timeout must be finite and between 0.1 and 30 seconds")
    destination = _fresh_output(output)
    executable, _ = _file(renderer, MAX_INPUT_BYTES)
    if not os.access(executable["path"], os.X_OK):
        raise AuditionError("renderer is not executable")
    profile_record, _ = _file(profile, 1024 * 1024)
    pack = Path(pack)
    if pack.is_symlink() or not pack.is_dir() or (pack / "entries").is_symlink():
        raise AuditionError("pack and its entries must be real directories")
    pack = pack.resolve(strict=True)
    manifest_record, raw = _file(pack / "recipes.json", 128 * 1024, retain=True)
    source = _json(raw)
    if (not isinstance(source, dict) or type(source.get("schema_version")) is not int
            or source["schema_version"] != 1
            or source.get("pack_id") != "starter-registration-pack-v1"
            or source.get("evidence_status") != "proposed-unmeasured"
            or not isinstance(source.get("recipes"), list) or len(source["recipes"]) != 12):
        raise AuditionError("expected the admitted starter-registration-pack-v1 manifest")
    recipes, payload_bytes, expected_files = [], {}, set()
    for name, recipe in zip(NAMES, source["recipes"]):
        if (not isinstance(recipe, dict) or recipe.get("name") != name
                or not isinstance(recipe.get("purpose"), str)):
            raise AuditionError(f"unexpected recipe name/order/purpose: {name}")
        item = {"name": name, "purpose": recipe["purpose"]}
        for scope in ("registration", "performance"):
            filename = f"{name}.b3{scope}"
            if recipe.get(f"{scope}_file") != filename:
                raise AuditionError(f"unexpected payload filename: {name} {scope}")
            expected_files.add(filename)
            item[scope], raw = _file(pack / "entries" / filename, 16384, retain=True)
            if not raw.startswith(b"B3CONTROLS4\n") or not raw.endswith(b"\n"):
                raise AuditionError(f"expected canonical state4 payload: {filename}")
            raw.decode("utf-8")
            payload_bytes[item[scope]["path"]] = raw
        if item["registration"]["sha256"] != item["performance"]["sha256"]:
            raise AuditionError(f"paired payload bytes differ: {name}")
        recipes.append(item)
    if {path.name for path in (pack / "entries").iterdir()} != expected_files:
        raise AuditionError("entries must contain exactly the admitted 24 payloads")
    score_records, score_bytes = {}, {}
    for key, filename in SCORES.items():
        score_records[key], score_bytes[key] = _file(
            ROOT / "examples/registrations" / filename, 8192, retain=True)
    tool_record, _ = _file(Path(__file__), 128 * 1024)
    inputs = {"renderer": executable, "profile": profile_record,
              "pack_manifest": manifest_record, "tool": tool_record,
              "scores": score_records, "recipes": recipes}
    return destination, inputs, payload_bytes, score_bytes


def _write_new(path, raw):
    with Path(path).open("xb") as output:
        output.write(raw)


def _artifact(path, limit):
    if not os.path.lexists(path):
        return None
    try:
        return _file(path, limit)[0]
    except (OSError, ValueError) as error:
        return {"path": str(path), "present": True, "inspection_error": str(error)}


def _check_wav(path):
    _, raw = _file(path, FRAMES * 4 + 4096, retain=True)
    with wave.open(io.BytesIO(raw), "rb") as wav:
        if (wav.getnchannels(), wav.getsampwidth(), wav.getframerate(),
                wav.getnframes(), wav.getcomptype()) != (2, 2, SAMPLE_RATE, FRAMES, "NONE"):
            raise AuditionError("unexpected WAV format, rate or frame count")
        pcm = array("h", wav.readframes(FRAMES))
    if sys.byteorder != "little":
        pcm.byteswap()
    if len(pcm) != FRAMES * 2 or not any(pcm):
        raise AuditionError("incomplete or silent audition WAV")
    return {"frames": FRAMES, "sample_rate": SAMPLE_RATE, "channels": 2,
            "nonzero_channel_samples": sum(sample != 0 for sample in pcm),
            "peak_pcm16": max(abs(sample) for sample in pcm)}


def _jobs(destination, inputs):
    jobs = []
    for number, recipe in enumerate(inputs["recipes"], 1):
        scores = ["audition"]
        if 9 <= number <= 11:
            scores.append("banks-reveal")
        elif number == 12:
            scores.append("manual-return")
        for score in scores:
            for scope in ("registration", "performance"):
                stem = f"{number:02d}-{score}-{scope}"
                wav = destination / f"{stem}.wav"
                jobs.append({
                    "id": stem, "recipe": recipe["name"], "scope": scope,
                    "score": score, "status": "not-run", "returncode": None,
                    "argv": [inputs["renderer"]["path"], "--profile", inputs["profile"]["path"],
                             "--controls", recipe[scope]["path"], "--events",
                             str(destination / "scores" / SCORES[score]), "--output", str(wav),
                             "--sample-rate", str(SAMPLE_RATE), "--frames", str(FRAMES),
                             "--block-size", "64", "--seed", "73", "--contacts", "nominal",
                             "--fail-on-clip"],
                    "outputs": {"wav": None, "stdout_json": None, "stderr": None},
                })
    return jobs


def _execute(job, destination, payload_bytes, timeout_seconds):
    stdout_path = destination / f"{job['id']}.stdout.json"
    stderr_path = destination / f"{job['id']}.stderr.txt"
    wav_path = Path(job["argv"][job["argv"].index("--output") + 1])
    job["status"] = "failed"
    # Files retain exact child bytes, including partial stdout on timeout/error.
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        try:
            result = subprocess.run(job["argv"], cwd=destination, stdin=subprocess.DEVNULL,
                                    stdout=stdout, stderr=stderr, timeout=timeout_seconds,
                                    check=False, shell=False)
            job["returncode"] = result.returncode
            if result.returncode != 0:
                job["error"] = f"renderer exited {result.returncode}"
        except subprocess.TimeoutExpired:
            job["error"] = f"renderer exceeded {timeout_seconds:g} second timeout"
            job["timed_out"] = True
        except OSError as error:
            job["error"] = f"renderer could not start: {error}"
        except KeyboardInterrupt:
            job["error"] = "interrupted during renderer invocation"
    job["outputs"] = {"wav": _artifact(wav_path, FRAMES * 4 + 4096),
                      "stdout_json": _artifact(stdout_path, MAX_LOG_BYTES),
                      "stderr": _artifact(stderr_path, MAX_LOG_BYTES)}
    job["stdout_is_json"] = False
    try:
        _, raw = _file(stdout_path, MAX_LOG_BYTES, retain=True)
        summary = _json(raw)
        job["stdout_is_json"] = True
        if "error" in job:
            return
        payload_path = job["argv"][job["argv"].index("--controls") + 1]
        controls = {"schema_version": 1, "restore_policy": RESTORE_POLICY,
                    "path": payload_path, "source_version": 4,
                    "source_bytes": len(payload_bytes[payload_path]),
                    "canonical_b3controls4": payload_bytes[payload_path].decode("utf-8")}
        if (not isinstance(summary, dict) or summary.get("render_schema_version") != 6
                or summary.get("status") != "ok" or summary.get("evidence_status") != "unmeasured"
                or summary.get("controls") != controls):
            raise AuditionError("renderer schema6/full-state provenance differs from the actual payload")
        job["wav"] = _check_wav(wav_path)
        job["canonical_controls_match_payload"] = True
        job["status"] = "succeeded"
    except (OSError, ValueError, EOFError, wave.Error) as error:
        job.setdefault("error", str(error))


def _report(manifest):
    lines = ["# Proposed starter registration auditions", "",
             f"Status: **{manifest['status']}**. {manifest['completed_jobs']} of "
             f"{len(manifest['jobs'])} renders succeeded.", "",
             "These are proposed, unmeasured recipes for the nominal dry Engine. "
             "They are not specimen measurements, factory recipes, or live-app evidence.", "",
             "Each WAV is stereo PCM16, 48 kHz, exactly one second, with nominal contacts, "
             "seed 73, block size 64 and fail-on-clip. No normalization is applied.", "",
             "Both suffixes use `--controls`: full state **including saved expression**. "
             "This does not perform Registration's expression-preserving library recall. "
             "Matching suffix pairs must produce identical complete WAV bytes.", "",
             "## Listening order", "",
             "`audition` is note-only: Upper C4/G4 at frames 0/9000, Lower C3 at 16000, "
             "pedal ID 1 at 26000, then Upper E4 + Lower G3 + pedal ID 8 at 36000. "
             "Manual notes use MIDI numbers; pedals use one-based IDs. Recipe 10's manual "
             "passages are silent; its pedals sound. Recipe 12's Upper remains cancelled.", "",
             "`banks-reveal` (09–11) starts with the saved routes/fixed modes, selects both "
             "A banks at 12000, then both B banks at 24000. Selection reconnects routes "
             "and clears fixed modes. Recipe 11 initially sounds its saved D#/F modes.", "",
             "`manual-return` (12) holds Upper C silently, reselects retained G# at 8000, "
             "selects both A banks at 18000, then both B banks at 30000. The later Upper-B "
             "attack makes saved percussion eligible. These explicitly named companion "
             "scores change selections; the initial-state provenance remains unchanged.", "",
             "## Results", "", "| Render | Result | WAV |", "| --- | --- | --- |"]
    for job in manifest["jobs"]:
        wav = job["outputs"]["wav"]
        link = f"[{job['id']}.wav]({job['id']}.wav)" if wav and "sha256" in wav else "—"
        lines.append(f"| {job['id']} | {job['status']} | {link} |")
    lines += ["", "`manifest.json` records exact argv, actual executable/profile/payload/score "
              "SHA-256, raw stdout JSON/stderr and WAV identities, input recheck, and each "
              "attempt's status. A failed JSON capture may contain incomplete/non-JSON bytes; "
              "`stdout_is_json` states what was observed. Hashes identify files, not physical fidelity.",
              "", "The batch stops on its first failure and retains actual partial outputs. "
              "There is no overwrite, rollback, automatic retry, or resume; choose another fresh "
              "output directory for a new run.", ""]
    if manifest.get("error"):
        lines += ["Failure: " + manifest["error"], ""]
    return "\n".join(lines).encode("utf-8")


def run_auditions(*, renderer, profile, pack, output, timeout_seconds=15):
    destination, inputs, payload_bytes, score_bytes = _preflight(
        renderer, profile, pack, output, timeout_seconds)
    manifest = {"schema_version": 1, "workflow": "starter-registration-audition-v1",
                "evidence_status": "proposed-unmeasured", "engine": "nominal-dry",
                "restore_policy": RESTORE_POLICY, "status": "failed", "inputs": inputs,
                "settings": {"sample_rate": SAMPLE_RATE, "frames": FRAMES, "block_size": 64,
                             "seed": 73, "contacts": "nominal", "fail_on_clip": True,
                             "timeout_seconds": timeout_seconds},
                "output": str(destination), "jobs": _jobs(destination, inputs),
                "completed_jobs": 0, "attempted_jobs": 0, "paired_wavs_equal": [],
                "copied_scores": {}, "inputs_unchanged": None}
    # mkdir is the final no-replace authority, including a destination racing preflight.
    destination.mkdir(mode=0o700)
    try:
        (destination / "scores").mkdir()
        for key, raw in score_bytes.items():
            path = destination / "scores" / SCORES[key]
            _write_new(path, raw)
            manifest["copied_scores"][key] = _file(path, 8192)[0]
        for job in manifest["jobs"]:
            manifest["attempted_jobs"] += 1
            _execute(job, destination, payload_bytes, timeout_seconds)
            if job["status"] != "succeeded":
                raise AuditionError(f"{job['id']}: {job.get('error', 'incomplete render')}")
            if job["scope"] == "performance":
                previous = manifest["jobs"][manifest["attempted_jobs"] - 2]
                if job["outputs"]["wav"]["sha256"] != previous["outputs"]["wav"]["sha256"]:
                    job["status"] = "failed"
                    job["error"] = "paired suffix renders have different WAV bytes"
                    raise AuditionError(f"{job['id']}: {job['error']}")
                manifest["paired_wavs_equal"].append([previous["id"], job["id"]])
            manifest["completed_jobs"] += 1
        manifest["status"] = "succeeded"
    except (OSError, ValueError, KeyboardInterrupt) as error:
        manifest["error"] = str(error) or "interrupted"
    # These are observed file hashes before/after the batch, not invented runtime hashes.
    records = [inputs[key] for key in ("renderer", "profile", "pack_manifest", "tool")]
    records += list(inputs["scores"].values())
    records += list(manifest["copied_scores"].values())
    records += [recipe[scope] for recipe in inputs["recipes"]
                for scope in ("registration", "performance")]
    changed = []
    for record in records:
        try:
            if _file(record["path"], MAX_INPUT_BYTES)[0] != record:
                changed.append(record["path"])
        except (OSError, ValueError):
            changed.append(record["path"])
    manifest["inputs_unchanged"] = not changed
    if changed:
        manifest["status"] = "failed"
        manifest["changed_inputs"] = changed
        manifest.setdefault("error", "one or more input files changed during the batch")
    _write_new(destination / "manifest.json", (json.dumps(
        manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8"))
    _write_new(destination / "report.md", _report(manifest))
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("renderer", "profile", "pack", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=float, default=15,
                        help="per renderer call, 0.1..30 seconds (default: 15)")
    args = parser.parse_args(argv)
    try:
        manifest = run_auditions(**vars(args))
    except (OSError, ValueError, RuntimeError) as error:
        print(f"audition refused: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"status": manifest["status"], "completed_jobs": manifest["completed_jobs"],
                      "manifest": str(Path(manifest["output"]) / "manifest.json")}))
    return 0 if manifest["status"] == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
