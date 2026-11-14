# Offline nominal rotary developer renderer

`hammond_rotary_render` applies the independent [R4 renderer](ROTARY_RENDERER_CONTRACT.md)
to two explicitly supplied radiation-boundary waveforms. It produces raw stereo
binary64 samples and an inspectable JSON report. It does not route the dry Engine
through a cabinet or change any musical parameter or saved-state identity.

The only profile is the compiled
[`nominal-research-v1`](../data/rotary/nominal-research-v1.json). Its proposed
geometry and mechanics are a synthetic research model, not measurements from a
Leslie specimen. R5 audible reconstruction/alias policy, R6 integration and device
deadlines, complete M5/M6 electronics, and physical M7 fidelity remain separate
gates. The [whole project plan](PLAN.md) retains their dependencies.

## Command and output

```text
hammond_rotary_render --horn FILE --drum FILE \
  --sample-rate 44100|48000|96000|192000 \
  --output-dir NEW_DIRECTORY [--block-size 1..4096] [--events FILE]
```

All four principal options are required; block size defaults to 64. Unknown,
duplicate, missing, empty or oversized arguments reject. Numbers use unsigned
decimal digits only. Each argument is limited to 4,096 bytes; Windows `wmain`
converts validated UTF-16 arguments to UTF-8 through `tools/CliArguments.h`.
Paths containing spaces or Unicode characters must be passed as single shell
arguments. `--help` is accepted by itself and includes the formats, limits,
compiled profile ID/SHA-256, tail policy and gain warning.

The output parent must already exist. The final directory name must be new,
with no trailing separator, `.` or `..` final component. Directory creation is
exclusive: existing files, directories and symbolic links reject. The two files
inside it are also opened exclusively in binary mode:

| File | Content |
| --- | --- |
| `stereo.f64le` | Raw little-endian IEEE-754 binary64, interleaved left then right; 16 bytes per output frame. |
| `report.json` | UTF-8 JSON under `rotary-offline-render-v1`, schema version 1, with the profile identity, separate counts, physical bounds, final motion state and solver diagnostics. |

Successful exit is zero. An admission, renderer, read, write or close failure
returns nonzero and reports an error to stderr. On an ordinary caught failure,
cleanup removes only files this invocation successfully created, then its new
directory. It never recursively removes pre-existing or unrelated content.
Abrupt termination and external permission or directory changes can prevent
cleanup; no crash-recovery or concurrent-writer protocol is claimed. Inputs
must remain unchanged while the command runs. Truncated or extended files
detected during reading reject, but an in-place same-size rewrite is not a
supported concurrent operation.

## Input format and resource bounds

Each input is a readable regular file containing one mono stream. No header,
WAV container, PCM conversion, channel extraction or sample-rate metadata is
accepted. The selected rate describes both supplied streams; the CLI never
resamples them. The byte representation is explicitly decoded and encoded in
little-endian order, independent of the host's byte order.

Both files must have equal lengths divisible by eight. Every sample must be
finite and in the closed interval `[-1,1]`, including both endpoints and signed
zero. NaN, infinities and out-of-range values reject. Empty inputs are valid and
still run the explicit zero-input tail. Input streams may name the same file.

The fixed maximum is 60 seconds **per input**, excluding the subsequent tail:

| Sample rate | Maximum input frames | Maximum bytes per input |
| ---: | ---: | ---: |
| 44,100 Hz | 2,646,000 | 21,168,000 |
| 48,000 Hz | 2,880,000 | 23,040,000 |
| 96,000 Hz | 5,760,000 | 46,080,000 |
| 192,000 Hz | 11,520,000 | 92,160,000 |

The CLI streams at most 4,096 frames at a time. Its audio/byte/event workspace
is a fixed heap allocation, separate from the renderer's fixed heap storage.
It never loads the entire audio file. The optional event file is bounded to
64 KiB and 1,024 events; paths, the report and ordinary library stream buffers
are also independent of the audio duration. File-size preflight occurs before
output creation. Sample admission occurs during streaming, so a malformed
late sample exercises the same partial-output cleanup as other render errors.

### Gain and signed output

Normalized inputs do **not** bound output samples to `[-1,1]`. The cubic
interpolator can overshoot, each path applies
`reference_distance_m / distance_m`, and the horn/drum contributions add with
their signs. There is no clipping, normalization, limiting, resampling or
automatic listening-level conversion. The report retains per-channel absolute
peaks and the count of samples whose absolute value exceeds one.

The raw output is an engineering interchange format. A later audition/export
step must choose its own explicit level and audio format; such a conversion is
not part of this renderer's result or numerical evidence.

## Event grammar and ordering

Each nonempty event file contains one command per line:

```text
0 horn chorale
1200 horn tremolo
2400 drum tremolo
4800 horn chorale
```

Exactly three fields are required: an unsigned decimal frame number, `horn` or
`drum`, then `chorale` or `tremolo`. Tokens are case sensitive and use ASCII,
which is a strict UTF-8 subset. One or more spaces or tabs separate fields;
leading and trailing spaces/tabs are permitted. LF and CRLF line endings are
accepted, and the final line may omit a line ending. A bare CR is invalid.
Each line has at most 64 ASCII bytes excluding its LF/CRLF terminator.

An empty event file means no commands. Blank or whitespace-only lines, comments,
a UTF-8 BOM, non-ASCII bytes, control characters, extra tokens, negative or
fractional frames, unknown commands and more than 1,024 events reject. Frame
numbers must be stable and nondecreasing in the inclusive range
`[0,input_frames]`. The tool never sorts, merges or discards same-frame events.

Commands at an internal block's ending boundary are delivered at offset `N`
of that block. They therefore precede any subsequent block processing. All
commands at the input's final frame are accepted before the tail starts. For
empty inputs, the admitted frame-zero commands are applied through a zero-frame
renderer call before flushing. Equal-frame events retain their file order;
the last command for a rotor controls its following evolution. A common cabinet
switch requires one explicit command for each rotor.

## Explicit tail and delay reporting

After all input frames, the CLI always appends exactly
`RotaryRenderer::tail_flush_frames()` zero-input frames, in legal blocks, while
both rotors continue moving. It does not stop when an output happens to be zero,
trim startup silence, or discard output latency. The report's counts satisfy:

```text
output_frames = input_frames + tail_flush_frames
output_bytes = output_frames * 2 * 8
```

`algorithmic_latency_frames` is two. Physical propagation remains separate:
the report gives each path's full-orbit minimum/maximum distance and the
corresponding travel-time bounds, and the final actual path solves retain
their own `delay_s`. No single fitted delay replaces these values.

For the current nominal JSON bytes, the observed tail counts are 222, 242, 479
and 953 at 44.1, 48, 96 and 192 kHz respectively. These counts are derived from
the compiled profile and renderer; callers should read the report rather than
hard-code them. The [A25 author report](development/2026-11-14-waveform-continuation/reports/a25-author-cli.json)
binds this observation to exact sources and the nominal profile hash.

## Compiled profile and build boundary

The Python standard-library compiler validates the existing strict profile and
generates `RotaryNominalProfile.h`; the native CLI does not parse arbitrary
runtime profiles or carry a JSON dependency. Its generated interface is:

```cpp
namespace hammond::rotary::generated {
inline constexpr std::string_view kProfileId = /* admitted ID */;
inline constexpr std::string_view kProfileSha256 = /* exact input byte SHA-256 */;
inline Profile nominal_profile() noexcept;
}
```

The report records those ID/hash fields and the full function name
`hammond::rotary::generated::nominal_profile`. The generated header additionally
binds its model/numerical-contract IDs to the runtime types. The source profile
at this implementation is SHA-256
`c0473cb20604726d989d7c280700109f647f7b227edb71c61d275ed9bfd67443`.

From the repository root, this explicit GCC build needs no shared build tree or
third-party dependency. The output directory below is newly selected by the
operator; replace it as needed:

```sh
mkdir -p /tmp/hammond-rotary-developer/generated
python3 tools/compile_rotary_profile.py \
  --input data/rotary/nominal-research-v1.json \
  --output /tmp/hammond-rotary-developer/generated/RotaryNominalProfile.h
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror \
  -I include -I /tmp/hammond-rotary-developer/generated \
  tools/rotary_render.cpp src/RotaryMotion.cpp src/RotaryPropagation.cpp \
  src/RotaryHistory.cpp src/RotaryStreamingPath.cpp src/RotaryRenderer.cpp \
  -o /tmp/hammond-rotary-developer/hammond_rotary_render
```

The project integrator owns the `hammond_rotary_render` CMake target, generated
header dependency, strict flags, Windows startup wiring and acceptance-test
environment. That integration is separate from the source-specific standalone
GCC author checks below. This is a build-tree research tool; the existing
OfflineTools, CaptureTools, Standalone and NativeVST3 install inventories are
not expanded by the CLI implementation.

## Reproducible synthetic example

The following creates 4,800 normalized samples per branch at 48 kHz. These are
chosen test tones, not organ output or instrument captures. It refuses to reuse
the input directory:

```sh
python3 - <<'PY'
import math
from pathlib import Path
import struct

directory = Path("rotary-example-inputs")
directory.mkdir(exist_ok=False)
for name, frequency, amplitude in (("horn", 220, 0.2), ("drum", 110, 0.3)):
    with (directory / (name + ".f64le")).open("xb") as stream:
        for frame in range(4800):
            stream.write(struct.pack("<d", amplitude * math.sin(2 * math.pi * frequency * frame / 48000)))
(directory / "events.txt").write_text(
    "0 horn chorale\n1200 horn tremolo\n2400 drum tremolo\n4800 horn chorale\n",
    encoding="ascii")
PY
/tmp/hammond-rotary-developer/hammond_rotary_render \
  --horn rotary-example-inputs/horn.f64le \
  --drum rotary-example-inputs/drum.f64le \
  --sample-rate 48000 --block-size 64 \
  --events rotary-example-inputs/events.txt \
  --output-dir rotary-example-render
```

To inspect the report and the first interleaved samples without choosing an
audition level:

```sh
python3 - <<'PY'
import json
from pathlib import Path
import struct

directory = Path("rotary-example-render")
report = json.loads((directory / "report.json").read_text(encoding="utf-8"))
print(json.dumps(report, indent=2))
with (directory / "stereo.f64le").open("rb") as stream:
    print(list(struct.iter_unpack("<dd", stream.read(16 * 8))))
PY
```

`paths` contains resolved input and output locations. Valid UTF-8 names remain
readable; invalid native POSIX path bytes are escaped for valid JSON, with exact
bytes retained in `path_bytes_hex`. On Windows those byte strings are UTF-8,
matching the CLI path conversion; they are not UTF-16 storage dumps.

## Executed evidence and remaining acceptance

The [A25 implementation note](development/2026-11-14-waveform-continuation/notes/A25-offline-renderer.md)
and [83-case author report](development/2026-11-14-waveform-continuation/reports/a25-author-cli.json)
record a strict GCC 14.2 native build and actual execution. They cover all four
rates with blocks 1/7/64/257/4096, exact audio/final-state/diagnostic equality,
terminal/tied/1,024 events, signed unclipped output, malformed/late samples,
strict event errors, Unicode/native POSIX paths, preserved existing destinations
and an injected write failure with cleanup.

Those author checks are not the separate independent CLI acceptance, the full
independent R4 reference campaign or actual Windows/macOS execution. A successful
full 60-second render, big-endian host execution, audible R5 policy, R6 device
deadlines and specimen-specific fidelity are not claimed by them. Their exact
source hashes and unrun scopes remain in the report; later changes require the
affected checks to be rerun.
