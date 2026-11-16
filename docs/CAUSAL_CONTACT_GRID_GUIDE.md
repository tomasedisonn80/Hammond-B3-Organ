# Causal contact grid: developer guide

`causal-contact-grid-v1` is an isolated C++20 research trajectory. It accepts explicitly quantized key targets and returns exact rational contact crossing times. It does not generate audio. The [frozen contract](CAUSAL_CONTACT_GRID_CONTRACT.md) defines its complete domain; [source review](reviews/CAUSAL_CONTACT_GRID_IMPLEMENTATION_REVIEW.md) records the arithmetic argument. The [results page](CAUSAL_CONTACT_GRID_RESULTS.md) connects the source-bound numerical, lifecycle, transport, resource and compatibility evidence. The current [session checkpoint](development/2026-11-15-streaming-continuation/CHECKPOINT.md) owns later acceptance and publication.

## What this phase adds

Each configured key has nine independent hysteretic contacts, a target position, a persistent command anchor and separate press/release speeds. Commands arrive on an integer grid of 65,536 ticks per frame. Travel between commands is continuous and linear, clamped at the target. A contact closes at its `on` threshold while rising and opens at its `off` threshold while falling. Each threshold has `0 <= off < on <= 2^48`.

Crossing times are a whole tick plus a reduced proper fraction. Ordering uses exact unsigned products, then key index and contact index for equal times. Equal targets preserve the original anchor; tied target changes retain their caller order. Incoming crossings at a command time resolve before commands there. Block boundaries do not rebase travel.

This grid has a distinct identity from the [offline binary64-input reference](FRACTIONAL_CONTACT_REFERENCE.md). There is no implicit float converter and no assertion that quantizing the earlier reference preserves its topology or audio error. Sample rate identifies one of 44,100, 48,000 or 96,000 Hz; target ticks and speed values remain explicit caller inputs in that rate's frame grid.

## Build and run the native probe

The normal core build needs a C++20 compiler, CMake 3.21+ and Python 3.10+. SDL, RtMidi and the VST3 SDK are unnecessary for this research module. From the repository root in a clean checkout containing this implementation, use the [standard preset setup](BUILD.md). On Windows, run CMake in a Visual Studio developer terminal with Python available:

```sh
cmake --preset release
cmake --build --preset release --target hammond_causal_contact_grid_probe --parallel 2
```

The Release preset configures `build-release` inside the repository. This session instead uses the already configured sibling `../build-native`; its complete dummy-SDL configuration is in the [checkpoint](development/2026-11-15-streaming-continuation/CHECKPOINT.md#local-build-recipe). For that existing build, the corresponding build command is:

```sh
cmake --build ../build-native --config Release --target hammond_causal_contact_grid_probe --parallel 2
```

The probe reads one bounded ASCII case from standard input and writes one JSON report. Choose the executable from the build actually configured:

| Configuration | Example executable path from the repository root |
| --- | --- |
| This session's Linux single-configuration build | `../build-native/hammond_causal_contact_grid_probe` |
| Release preset, Linux/macOS single-configuration generator | `build-release/hammond_causal_contact_grid_probe` |
| Release preset, Windows Ninja | `build-release/hammond_causal_contact_grid_probe.exe` |
| Release preset, Windows Visual Studio | `build-release/Release/hammond_causal_contact_grid_probe.exe` |

Run the following Python example from the repository root, setting `exe` to the matching path above. It creates a synthetic one-frame positive control: all nine contacts close at tick 32,768, exactly half a frame. These small position units are a numerical fixture, not a measured key travel. Passing ASCII bytes keeps the input transport explicit; `json.loads` accepts the returned bytes and either LF or CRLF whitespace.

```python
import json
import subprocess
from pathlib import Path

exe = Path("../build-native/hammond_causal_contact_grid_probe").resolve()
thresholds = " ".join(["0 32768"] * 9)
wire = f"CGGRID1 48000 1 1 1 1\n1 1 {thresholds}\n0 0 65536\n1\n"
completed = subprocess.run([str(exe)], input=wire.encode("ascii"),
                           capture_output=True, check=True, timeout=10)
assert completed.stderr == b""
report = json.loads(completed.stdout)
assert report["model_id"] == "causal-contact-grid-v1"
assert report["edges"] == [
    {"time": {"tick": 32768, "numerator": 0, "denominator": 1},
     "key_index": 0, "contact_index": i, "closed_after": True}
    for i in range(9)
]
assert report["snapshot"]["phase"] == "closed"
assert report["snapshot"]["cursor_frames"] == 1
print(report["model_id"], len(report["edges"]), report["snapshot"]["cursor_frames"])
```

Expected printed summary: `causal-contact-grid-v1 9 1`. The [independent guide receipt](development/2026-11-15-streaming-continuation/reports/A35-guide-smoke.json) records this example against the source-identified Linux executable; it is a positive control, not a replacement for the acceptance suites.

### Wire format

```text
CGGRID1 F K N C P
K records: press release off0 on0 ... off8 on8
C records: absolute_tick key_index position
P positive frame-block lengths summing N
```

| Field | Meaning and bound |
| --- | --- |
| `F` | 44100, 48000 or 96000 |
| `K` | 1–4 configured keys |
| `N` | 0–4096 observed frames |
| `C` | 0–512 total targets, including ties, repeated targets and endpoint targets |
| `P` | 1–N positive processing blocks when N > 0; exactly zero when N = 0 |
| Speeds | Integer position units per tick, 1–4294967295 |
| Positions and thresholds | Unsigned integers in 0–281474976710656; each off must be below on |
| Targets | Globally nondecreasing absolute ticks in 0–N×65536; indices 0–K−1 |

Targets at the final endpoint are passed to `close_observation`. They change target/anchor state without advancing travel or emitting an edge. The probe always closes, including N=0. Its final snapshot therefore has phase `closed`. It reports exact edges, complete padded configuration/key state and per-block counts. The maximum input is 131,072 bytes and maximum JSON report is 2 MiB. Signs, floating-point tokens, nondecimal digits, overflow, missing/trailing tokens and invalid partitions are rejected with exit 2 and no success JSON. `--help` prints the transport summary.

The [Windows transport correction](reviews/CAUSAL_CONTACT_GRID_PORTABILITY.md) selects binary stdin before reading, so CRLF bytes count individually and Ctrl-Z cannot hide trailing data. Stdout remains text and may end with CRLF; identical raw stdout bytes across platforms are not promised. [Initial hosted admission](reviews/STREAMING_INITIAL_HOSTED_ADMISSION.md) observes all six causal suites passing on Windows and the other three core jobs at `af2b747`; its separate installed-reference failure remains recorded. [Repaired `2f57723`](development/2026-11-15-streaming-continuation/reports/hosted-2f57723-complete.json) passes Windows 185/185. The forced mode-failure branch still has no observed execution. For exact byte-limit cases, supply bytes as above instead of a shell text pipeline.

This is a development transport, not an audio file format or a saved musical state. The probe has no path arguments and is not added to the older frozen `ContactReferenceTools` installation component. Its input/JSON strings and process I/O are outside the trajectory API's allocation-free scope.

## Use the C++ API

Include `hammond/research/CausalContactGrid.h` and link `hammond_core`. Construct and own the object outside a callback, prepare a valid `ContactGridConfig`, then supply `std::span` commands and caller-owned edge storage. Access must be serialized and non-reentrant; input/output spans must be valid, stable and mutually disjoint, including from the object itself.

| Operation | Accepted phase | Successful effect |
| --- | --- | --- |
| `prepare(config)` | Unprepared, ready or closed | Validates/copies active configuration; canonical fresh ready epoch |
| `process(frames, targets, output)` | Ready or active | Advances travel; emits edges; positive calls become active |
| `process(0, {}, output)` | Ready or active | Exact identity, including phase |
| `close_observation(targets)` | Ready or active | Applies only current-endpoint targets; marks closed without travel |
| `reset()` | Closed | Retains configuration and clears the epoch to ready |
| `snapshot()` | Every phase | Copies state without advancing it |

For a processing interval, commands belong to `[begin,end)` and edges to `(begin,end]`. Therefore commands on a block endpoint belong to the next positive call or final closure; the incoming equality edge belongs to the completed call. Do not submit the same endpoint target twice.

Closure is an observation boundary, not release or drain: to release, submit a target toward zero and process the required travel before closing. Close an active epoch before resetting or reconfiguring; repeated closure and even empty processing while closed return `invalid_state`. Nonempty commands on `process(0, ...)` are invalid after the higher-precedence checks.

Every failure preserves live state and every caller-output byte. A short output returns `output_too_small`, zero `edgesWritten` and the actual `requiredEdges`; retry the same call with enough storage. Other process failures return zero counts; success returns `{ok,E,E}` and touches only the written prefix. Errors have frozen precedence: phase, remaining frames, remaining command capacity, all target domains, target ordering, arithmetic and actual output capacity. Invalid preparation, closure and reset are also transactional.

The object embeds live/staged snapshots, 4,608 staged edges and 36 interval edges. The [resource admission](reviews/CAUSAL_CONTACT_GRID_RESOURCE_ADMISSION.md) observes **113,056 bytes per object**, including **112,256 bytes of embedded scratch**, on Linux x86-64 GCC 14.2.0; this is not a byte-size promise for every compiler. Place large objects and fixture buffers in prepared owner storage rather than accumulating them on a small thread stack. Compiler stack use and actual callback deadlines remain unmeasured.

## Run the checks

Build the native inputs for the selected tests before CTest. Regenerate CMake when test discovery or configuration changes; preserve the existing build's cache/dependency settings. Root coordinates this session's configured build. Its focused commands are:

```sh
cmake --build ../build-native --config Release --parallel 3 --target hammond_causal_contact_grid_probe test_causal_contact_grid test_causal_contact_grid_lifecycle test_causal_contact_grid_resources
ctest --test-dir ../build-native -C Release --output-on-failure --no-tests=error -R "^(python_)?test_causal_contact_grid"
```

For a fresh Release preset build, use those same target names with `cmake --build --preset release`, then `ctest --preset release -R "^(python_)?test_causal_contact_grid"`. The focused selection currently contains six CTests; it is distinct from the retained all-target gate.

CTest supplies the selected configuration's native probe path to Python. A direct differential/CLI invocation requires `HAMMOND_CAUSAL_CONTACT_GRID_PROBE_EXECUTABLE`; unset, empty, missing or nonexecutable paths must fail setup. For example, in a POSIX shell:

```sh
HAMMOND_CAUSAL_CONTACT_GRID_PROBE_EXECUTABLE=../build-native/hammond_causal_contact_grid_probe python3 -B tests/test_causal_contact_grid_differential.py -v
HAMMOND_CAUSAL_CONTACT_GRID_PROBE_EXECUTABLE=../build-native/hammond_causal_contact_grid_probe python3 -B tests/test_causal_contact_grid_cli.py -v
```

On PowerShell, set `$env:HAMMOND_CAUSAL_CONTACT_GRID_PROBE_EXECUTABLE` to the actual `.exe` path, then run each script with `python -B`. Earlier A21/A24 notes retain an unset-environment skip observed before the fail-closed setup correction; those historical skips do not qualify native behavior. See the [results page](CAUSAL_CONTACT_GRID_RESULTS.md) for the source boundary and subsequent gate status.

The independent Python oracle constructs per-key affine paths and uses `Fraction`; it does not call the candidate's crossing helpers. Known answers, exact native/oracle comparisons, lifecycle rollback, strict transport behavior, allocation/resource receipts and platform builds qualify different risks. The session's reports retain their actual source identities and outcomes.

## Next implementation boundary

The 4-key, 4096-frame epoch is deliberately bounded research infrastructure. It cannot yet run an indefinite full-organ performance. Before a causal audio stage, independently specify integer conversion/error policy, absolute source phase, partial-cell integration, the proposed D=16 schedule, latency, a 33-sample nonempty drain, full-window reference grading, reset/tail ownership and callback deadlines. Preserve exact edge ordering through that design.

Full-organ/indefinite capacity, Engine/standalone/VST3 integration and physical contact calibration remain separate work. The existing ContactBank, nominal dry Engine, 91 shared sources, 47 sound parameters and `B3CONTROLS4`/readers 1–3 are unchanged by this research API. Bounce, resistance, tap loading and specimen timing require identified synchronized contact/source/dry captures; synthetic tests supply no such measurements.
