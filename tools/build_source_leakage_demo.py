#!/usr/bin/env python3
"""Build a bounded, synthetic leakage audition in a new directory (stdlib only).

Rendering and verification finish in private staging. Publication reserves a new
directory, creates files exclusively, and publishes provenance last. Handled
failures roll back only this invocation's files; directory visibility is not an
atomic transaction. No existing output, input, or raced destination is replaced.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import stat
import struct
import subprocess
import sys
import tempfile
import threading
import wave

ROOT = Path(__file__).resolve().parents[1]
RATE, FRAMES, BLOCK, SEED = 48000, 96000, 127, 1939
GAIN = 0.75
MAX_BUNDLE_BYTES = 4 * 1024 * 1024
MAX_STREAM_BYTES = 64 * 1024
SOURCE_PATHS = (
    "tools/build_source_leakage_demo.py", "tools/compile_profile.py",
    "tools/compile_source_leakage.py", "tools/render.cpp",
    "data/profiles/nominal-unmeasured-v1.json",
    "data/source-leakage/synthetic-pair-demo-v1.json",
    "data/source-leakage/synthetic-identity-v1.json",
    "docs/SOURCE_LEAKAGE_CONTRACT.md", "docs/SOURCE_LEAKAGE_AUDITION_CONTRACT.md",
)
SOLO = """# Synthetic C3/C4 single-8-foot-source fixture; 48000 Hz, 96000 frames.
# Source25 sounds at MIDI48; source37 sounds at MIDI60. Donor key stays released.
# Cancel/reconnect preserves the held C3 and free-running source phases.
0 expression upper 0 1
0 note_on upper 48 100
24000 cancel upper 0 0
36000 select_bank upper 0 1
48000 note_off upper 48 0
48000 note_on upper 60 100
84000 all_notes_off upper 0 0
"""
PHRASE = """# Original synthetic gesture, not a transcription or instrument recording.
# Nominal travel, Upper percussion, Lower sustain and both pedal mixtures.
0 expression upper 0 0.65
0 drawbar lower 2 6
0 note_on upper 48 100
0 note_on lower 60 100
0 pedal_on lower 1 100
12000 note_on upper 55 100
24000 all_notes_off upper 0 0
24000 all_notes_off lower 0 0
24000 pedal_all_notes_off lower 0 0
28800 note_on upper 48 100
28800 note_on lower 60 100
28800 pedal_on lower 13 100
48000 cancel upper 0 0
60000 select_bank upper 0 1
72000 all_notes_off upper 0 0
72000 all_notes_off lower 0 0
72000 pedal_all_notes_off lower 0 0
"""


class DemoError(ValueError):
    """Inputs, execution, verification or exclusive publication failed."""


def _json(raw: bytes) -> object:
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise DemoError(f"duplicate JSON member: {key}")
            out[key] = value
        return out

    def finite(token):
        value = float(token)
        if not math.isfinite(value):
            raise DemoError("nonfinite JSON value")
        return value

    def reject(token):
        raise DemoError(f"invalid JSON constant: {token}")

    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                          parse_float=finite, parse_constant=reject)
    except (UnicodeError, ValueError, RecursionError) as error:
        raise DemoError(f"invalid JSON receipt: {error}") from error


def _bytes(path: Path, maximum: int) -> bytes:
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise DemoError(f"expected a regular file of at most {maximum} bytes: {path}")
        raw = stream.read(maximum + 1)
        after = os.fstat(stream.fileno())
    if (len(raw) > maximum or len(raw) != before.st_size or
            (before.st_size, before.st_mtime_ns, before.st_ino) !=
            (after.st_size, after.st_mtime_ns, after.st_ino)):
        raise DemoError(f"input changed or exceeded its bound: {path}")
    return raw


def _identity(path: Path, maximum: int = 2 * 1024 * 1024) -> dict:
    raw = _bytes(path, maximum)
    return {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def _run(argv: list[str], timeout: float) -> dict:
    """Bound both child streams in memory; terminate on excess or timeout."""
    process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    buffers = [bytearray(), bytearray()]
    overflow = threading.Event()

    def read(stream, destination):
        with stream:
            while chunk := stream.read(4096):
                remaining = MAX_STREAM_BYTES - len(destination)
                destination.extend(chunk[:max(0, remaining)])
                if len(chunk) > remaining:
                    overflow.set()
                    process.kill()

    readers = [threading.Thread(target=read, args=(stream, target), daemon=True)
               for stream, target in zip((process.stdout, process.stderr), buffers)]
    for reader in readers:
        reader.start()
    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        process.wait()
    finally:
        for reader in readers:
            reader.join(timeout=2)
    if any(reader.is_alive() for reader in readers):
        raise DemoError("child output pipe did not close")
    if timed_out or overflow.is_set():
        raise DemoError("child exceeded its time or 64 KiB stream limit")
    stdout, stderr = (bytes(value).decode("utf-8", errors="strict") for value in buffers)
    record = {"argv": argv, "returncode": process.returncode,
              "stdout": stdout, "stderr": stderr}
    if process.returncode:
        raise DemoError(f"command failed ({process.returncode}): {stderr.strip()[:1000]}")
    return record


def _write_json(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def inspect_pcm(path: Path) -> tuple[list[int], dict]:
    raw = _bytes(path, 44 + 4 * FRAMES)
    if len(raw) != 44 + 4 * FRAMES or raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise DemoError("unexpected WAV byte structure")
    with wave.open(str(path), "rb") as stream:
        if (stream.getnchannels(), stream.getsampwidth(), stream.getframerate(),
                stream.getnframes(), stream.getcomptype()) != (2, 2, RATE, FRAMES, "NONE"):
            raise DemoError("unexpected WAV format")
        pairs = list(struct.iter_unpack("<hh", stream.readframes(FRAMES)))
        if stream.readframes(1):
            raise DemoError("unexpected WAV trailing frames")
    if any(left != right for left, right in pairs):
        raise DemoError("dry stereo channels differ")
    samples = [left for left, _ in pairs]
    return samples, {"frames": FRAMES, "sample_rate": RATE, "channels": 2,
                     "sample_format": "pcm_s16le", "identical_channels": True,
                     "peak_pcm": max(abs(value) for value in samples),
                     "nonzero_frames": sum(value != 0 for value in samples)}


def _phase(seed: int, tone_id: int) -> float:
    # Independent direct-index SplitMix64 offset from the declared phase policy.
    # No production source or compiler module is imported as an oracle.
    mask = (1 << 64) - 1
    word = (seed + tone_id * 0x9E3779B97F4A7C15) & mask
    word = ((word ^ (word >> 30)) * 0xBF58476D1CE4E5B9) & mask
    word = ((word ^ (word >> 27)) * 0x94D049BB133111EB) & mask
    return ((word ^ (word >> 31)) >> 11) / (1 << 53)


def pcm_oracle(samples: list[int], profile: dict, gain: float, pair: bool) -> dict:
    """Independent direct-time sine/route/PCM check, never a physical oracle."""
    if (profile["manual_map"]["tone_ids"][12][2] != 25 or
            profile["manual_map"]["tone_ids"][24][2] != 37 or
            profile["drawbar_gains"]["values"][8] != 1.0):
        raise DemoError("solo oracle requires the declared nominal C3/C4 routing")
    sources = {tone: profile["sources"][tone - 1] for tone in (25, 37)}
    starts = {tone: (row["base_phase_turns"] + _phase(SEED, tone)) % 1.0
              for tone, row in sources.items()}
    worst, checked, silent = 0, 0, 0
    for n, actual in enumerate(samples):
        destination = 25 if n < 24000 or 36000 <= n < 48000 else 37 if 48000 <= n < 84000 else None
        value = 0.0
        if destination is not None:
            x = {tone: row["peak_amplitude"] * math.sin(math.tau *
                 ((starts[tone] + n * row["frequency_hz"] / RATE) % 1.0))
                 for tone, row in sources.items()}
            value = gain * x[destination]
            if pair:
                donor, coefficient = (37, 0.0625) if destination == 25 else (25, -0.03125)
                value += coefficient * (gain * x[donor])
            value *= profile["output_gain"]["value"]
        else:
            silent += 1
            if actual != 0:
                raise DemoError("cancelled or released solo route is not exactly silent")
        # The output boundary is binary32, followed by ties-away PCM rounding.
        converted = struct.unpack("<f", struct.pack("<f", value))[0]
        quantized = int(math.copysign(math.floor(abs(converted) * 32768.0 + 0.5), converted))
        expected = max(-32768, min(32767, quantized))
        worst = max(worst, abs(actual - expected))
        checked += 1
    if worst > 1:
        raise DemoError(f"independent PCM oracle exceeded frozen 1-LSB bound: {worst}")
    return {"status": "passed", "oracle": "direct-time-sine-and-literal-two-edge-routing-v1",
            "frames_checked": checked, "channel_samples_checked": 2 * checked,
            "exact_silent_frames": silent, "maximum_integer_error": worst,
            "maximum_allowed_integer_error": 1,
            "phase_method": "direct-index SplitMix64 plus n*frequency/rate; no recurrence reuse"}


def _publish(staging: Path, output: Path) -> None:
    """Reserve once, link exclusively, commit provenance last; roll back ours."""
    created: list[Path] = []
    output.mkdir(exist_ok=False)
    try:
        files = sorted(staging.iterdir(), key=lambda path: (path.name == "provenance.json", path.name))
        for source in files:
            destination = output / source.name
            os.link(source, destination)
            created.append(destination)
    except BaseException:
        for path in reversed(created):
            # Do not remove a link someone replaced after our exclusive create.
            try:
                if stat.S_ISREG(path.lstat().st_mode) and os.path.samefile(path, staging / path.name):
                    path.unlink()
            except FileNotFoundError:
                pass
        try:
            output.rmdir()
        except OSError:
            pass  # Preserve a concurrently introduced file/directory.
        raise


def _readme(results: list[dict], comparisons: dict) -> str:
    rows = "\n".join(
        f"| [{r['id']}.wav]({r['id']}.wav) | {r['description']} | {r['summary']['peak']:.6f} |"
        for r in results)
    return f"""# Synthetic source-leakage audition v1

Six actual two-second renders demonstrate the separately identified static source
coupling layer. The paired comparisons use **the same explicit input gain 0.75**,
nominal profile, seed 1939, event bytes, rate 48000 Hz and block size 127. They are
stereo PCM16 with identical dry channels. No file is separately normalized.

| Recording | What to listen for | Pre-PCM peak |
| --- | --- | ---: |
{rows}

## Listening sequence

Compare the two **solo g075** files first. MIDI 48/C3 opens source 25 at the 8-foot
drawbar. The synthetic pair adds source 37/C4 at **+1/16**, although its own key is
released. From 0.50–0.75s the Upper route is cancelled: the output is exactly silent
while phases continue. At 0.75s it reconnects the held C3. At 1.00s the score releases
C3 and plays C4/source 37; this recipient instead receives source 25 at **−1/32**.
All notes release at 1.75s. These signs and gains are invented numerical fixtures,
not estimates of physical generator adjacency or measured pickup coupling.

Then compare the **phrase g075** files. This original two-second gesture uses
Upper nominal contact travel and second-harmonic percussion, Lower sustain and
both nominal pedal mixtures. Upper Cancel/reconnect does not mute independently
sounding Lower/pedal routes. The phrase is a listening/behavior demonstration;
it is not the independently quantified solo oracle.

The two **solo g100** files retain an explicit default-path control: legacy with
no leakage flags and empty graph at gain 1. Their complete WAV bytes are identical.
Their higher level must not be confused with the g075 coupling comparison.

## Reproduce into a new directory

From the repository root, after building `hammond_render`:

```sh
python3 tools/build_source_leakage_demo.py \\
  --renderer build/hammond_render --output out/source-leakage-audition
```

On multi-configuration builds use `build/Release/hammond_render.exe` (Windows)
or the corresponding configuration directory. The output parent must already
exist; an existing file, directory or dangling symlink at the output is refused.
The builder uses only Python 3.10+ standard-library code. It invokes the actual
nominal-profile and leakage compilers and renderer, verifies all six WAVs and
receipts, then publishes the new bundle from private staging. Publication uses
exclusive directory/file creation with rollback and provenance last; visibility
of the whole directory is not atomic. Source inputs and the executable are
hashed before/after. Filesystems without hard-link support fail safely.

For an individual repeat, choose a new WAV filename and use these retained inputs:

```sh
build/hammond_render --profile examples/demos/source-leakage-audition-v1/nominal.b3p \\
  --events examples/demos/source-leakage-audition-v1/solo.events --frames 96000 \\
  --sample-rate 48000 --block-size 127 --seed 1939 --drawbars 008000000 \\
  --contacts ideal --percussion off --pedal-drawbars 00 \\
  --source-leakage examples/demos/source-leakage-audition-v1/pair.b3leakage \\
  --leakage-input-gain 0.75 --output out/solo-repeat.wav --fail-on-clip
```

## Retained evidence and limits

[provenance.json](provenance.json) retains every actual command and receipt,
source/executable/input/output SHA-256, data format, unchanged-input result and
comparison. The builder's source inventory identifies inspected bytes; it is
not an independent attestation that a supplied executable was built from them.
The integrating session owns coherent build qualification.

All four solo files were checked against an independent Python direct-time sine,
literal routing and PCM16 oracle, including exact cancellation/release silence.
The permitted difference was fixed at **one integer quantization step per channel
sample**; the observed maximum is **{comparisons['maximum_solo_pcm_error']}**.
The unconfigured/empty-gain-one WAV control is byte-exact. The two gain-matched
pairs contain nonzero differences; detailed counts are in provenance.

The model is synthetic and unmeasured, with no scanner, AO-28 or Leslie audio
connected here. This bundle does not establish physical fidelity, contact
bandwidth, a host callback deadline, or harmonic-source composition. Review the
[frozen audition contract](../../../docs/SOURCE_LEAKAGE_AUDITION_CONTRACT.md)
and [core/data contract](../../../docs/SOURCE_LEAKAGE_CONTRACT.md) for exact
scope, source pages, safety limits and separate acceptance requirements.
"""


def build_demo(renderer: Path, output: Path, timeout: float = 30.0) -> dict:
    if type(timeout) not in (int, float) or not math.isfinite(timeout) or not 1 <= timeout <= 120:
        raise DemoError("timeout must be finite in [1,120] seconds")
    renderer = renderer.resolve(strict=True)
    renderer_before = _identity(renderer, 512 * 1024 * 1024)
    absolute = Path(os.path.abspath(output))
    output = absolute.parent.resolve(strict=True) / absolute.name
    if os.path.lexists(output):
        raise DemoError("output must be a new directory, including no dangling symlink")
    names = sorted(set(SOURCE_PATHS) | {p.relative_to(ROOT).as_posix() for folder, pattern in
                   ((ROOT / "src", "*.cpp"), (ROOT / "include/hammond", "**/*.h"))
                   for p in folder.glob(pattern)})
    inputs = {name: _identity(ROOT / name) for name in names}
    if output == renderer or any(output == (ROOT / name).resolve() for name in names):
        raise DemoError("output aliases an input")
    invocations, results, samples = [], [], {}
    started = datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix=".hammond-leakage-demo-", dir=output.parent) as temporary:
        stage = Path(temporary)
        for source, name in (
            ("data/profiles/nominal-unmeasured-v1.json", "nominal-authoring.json"),
            ("data/source-leakage/synthetic-pair-demo-v1.json", "pair-authoring.json"),
            ("data/source-leakage/synthetic-identity-v1.json", "identity-authoring.json"),
        ):
            (stage / name).write_bytes(_bytes(ROOT / source, 256 * 1024))
        (stage / "solo.events").write_text(SOLO, encoding="utf-8", newline="\n")
        (stage / "phrase.events").write_text(PHRASE, encoding="utf-8", newline="\n")
        invocations.append(_run([sys.executable, str(ROOT / "tools/compile_profile.py"),
                                "--input", str(stage / "nominal-authoring.json"),
                                "--output", str(stage / "nominal.b3p")], timeout))
        compilers = {}
        for name in ("pair", "identity"):
            record = _run([sys.executable, str(ROOT / "tools/compile_source_leakage.py"),
                           "--input", str(stage / f"{name}-authoring.json"),
                           "--output", str(stage / f"{name}.b3leakage")], timeout)
            invocations.append(record)
            receipt = _json(record["stdout"].encode())
            if (receipt["status"] != "compiled" or
                    receipt["input_sha256"] != _identity(stage / f"{name}-authoring.json")["sha256"] or
                    receipt["compiled_sha256"] != _identity(stage / f"{name}.b3leakage")["sha256"]):
                raise DemoError("compiler receipt does not identify actual retained bytes")
            compilers[name] = receipt
        configurations = [
            ("solo-identity-g075", "solo", "identity", GAIN, "Ideal-contact C3/C4, empty graph at0.75."),
            ("solo-pair-g075", "solo", "pair", GAIN, "Same solo with signed synthetic donor contribution."),
            ("solo-legacy-g100", "solo", None, None, "Legacy no-flags reference, gain1."),
            ("solo-identity-g100", "solo", "identity", 1.0, "Explicit identity at gain1; byte-identical to legacy."),
            ("phrase-identity-g075", "phrase", "identity", GAIN, "Manuals, percussion and pedals; empty graph at0.75."),
            ("phrase-pair-g075", "phrase", "pair", GAIN, "Same full phrase with signed synthetic coupling."),
        ]
        profile = _json(_bytes(stage / "nominal-authoring.json", 256 * 1024))
        for ident, score, graph, gain, description in configurations:
            argv = [str(renderer), "--profile", str(stage / "nominal.b3p"), "--output", str(stage / f"{ident}.wav"),
                    "--events", str(stage / f"{score}.events"), "--frames", str(FRAMES), "--sample-rate", str(RATE),
                    "--block-size", str(BLOCK), "--seed", str(SEED), "--drawbars", "008000000",
                    "--contacts", "ideal" if score == "solo" else "nominal", "--percussion",
                    "off" if score == "solo" else "second", "--percussion-volume", "normal",
                    "--percussion-decay", "fast", "--pedal-drawbars", "00" if score == "solo" else "43", "--fail-on-clip"]
            if graph:
                argv += ["--source-leakage", str(stage / f"{graph}.b3leakage"), "--leakage-input-gain", str(gain)]
            invocation = _run(argv, timeout)
            invocations.append(invocation)
            summary = _json(invocation["stdout"].encode())
            if (summary.get("status") != "ok" or summary.get("clipped_frames") != 0 or
                    summary.get("render_schema_version") != (5 if graph else 3) or
                    summary.get("model") != "ideal-shared-sine-v1"):
                raise DemoError("renderer did not report an unclipped expected-source render")
            if graph:
                if (summary.get("source_leakage_input_gain") != gain or
                        summary.get("source_leakage_authoring_sha256") != compilers[graph]["input_sha256"] or
                        summary.get("source_leakage_profile_id") != compilers[graph]["profile_id"] or
                        summary.get("source_leakage_edge_count") != compilers[graph]["edge_count"] or
                        summary.get("source_leakage_evidence_status") != "synthetic" or
                        summary.get("source_leakage_identity_bypass") != (graph == "identity" and gain == 1.0)):
                    raise DemoError("renderer leakage facts disagree with actual graph/gain")
            pcm, facts = inspect_pcm(stage / f"{ident}.wav")
            samples[ident] = pcm
            result = {"id": ident, "description": description.replace("at0.75", "at 0.75").replace("gain1", "gain 1"),
                      "score": f"{score}.events", "graph": graph, "input_gain": gain,
                      "summary": summary, "wav": facts}
            if score == "solo":
                result["independent_pcm_oracle"] = pcm_oracle(pcm, profile, gain if gain is not None else 1.0, graph == "pair")
            results.append(result)
            _write_json(stage / f"{ident}.json", result)
        legacy = _bytes(stage / "solo-legacy-g100.wav", MAX_BUNDLE_BYTES)
        if legacy != _bytes(stage / "solo-identity-g100.wav", MAX_BUNDLE_BYTES):
            raise DemoError("legacy and empty-gain-one WAV bytes differ")
        comparisons = {"legacy_identity_wav_byte_exact": True, "pairs": [],
                       "maximum_solo_pcm_error": max(r["independent_pcm_oracle"]["maximum_integer_error"]
                       for r in results if "independent_pcm_oracle" in r)}
        for score in ("solo", "phrase"):
            difference = [a - b for a, b in zip(samples[f"{score}-pair-g075"], samples[f"{score}-identity-g075"])]
            changed = sum(value != 0 for value in difference)
            if not changed:
                raise DemoError("gain-matched nonempty graph produced no audible-data difference")
            comparisons["pairs"].append({"score": score, "same_input_gain": GAIN, "changed_frames": changed,
                                         "maximum_pcm_difference": max(abs(value) for value in difference),
                                         "rms_pcm_difference": math.sqrt(math.fsum(value * value for value in difference) / FRAMES)})
        (stage / "README.md").write_text(_readme(results, comparisons), encoding="utf-8", newline="\n")
        if inputs != {name: _identity(ROOT / name) for name in names} or renderer_before != _identity(renderer, 512 * 1024 * 1024):
            raise DemoError("source inputs or renderer changed during generation")
        artifacts = {path.name: _identity(path, MAX_BUNDLE_BYTES) for path in sorted(stage.iterdir())}
        provenance = {"schema_version": 1, "bundle_id": "source-leakage-audition-v1", "status": "verified_synthetic_demonstration",
                      "started_at_utc": started, "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                      "python": platform.python_version(), "platform": platform.platform(),
                      "renderer": {"path_at_capture": str(renderer), **renderer_before}, "source_sha256": inputs,
                      "source_root_at_capture": str(ROOT), "build_attestation": "not supplied by this tool; integrator qualification required",
                      "unchanged_inputs_and_executable": True, "compiler_receipts": compilers, "invocations": invocations,
                      "renders": results, "comparisons": comparisons, "artifacts": artifacts,
                      "publication": "private staging, exclusive mkdir and hardlinks; provenance last; handled-failure rollback",
                      "limits": ["synthetic coefficients and unmeasured source profile", "phrase is a listening demonstration",
                                 "no physical calibration, scanner/AO-28/Leslie or harmonic composition claim",
                                 "no atomic directory-visibility or power-loss durability claim"]}
        _write_json(stage / "provenance.json", provenance)
        total = sum(path.stat().st_size for path in stage.iterdir())
        if total > MAX_BUNDLE_BYTES:
            raise DemoError(f"bundle exceeds 4 MiB: {total}")
        _publish(stage, output)
    return {"status": "published", "output": str(output), "files": len(artifacts) + 1,
            "bytes": total, "renders": len(results), "comparisons": comparisons,
            "provenance_sha256": _identity(output / "provenance.json")["sha256"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], allow_abbrev=False)
    parser.add_argument("--renderer", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    args_list = sys.argv[1:] if argv is None else argv
    for option in ("--renderer", "--output", "--timeout-seconds"):
        if sum(token == option or token.startswith(option + "=") for token in args_list) > 1:
            parser.error(f"duplicate {option}")
    args = parser.parse_args(args_list)
    try:
        result = build_demo(args.renderer, args.output, args.timeout_seconds)
        print(json.dumps(result, sort_keys=True, allow_nan=False))
        return 0
    except (DemoError, OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"source-leakage demo: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
