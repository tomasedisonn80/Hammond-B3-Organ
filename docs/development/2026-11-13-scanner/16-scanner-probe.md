# Assignment 16 — native scanner line probe

- **Worker:** `/root/w03_a16_scanner_probe`
- **Wave:** 3, assignment 16 of this session's requested 60.
- **Status:** completed for integrator review on 13 November 2026.
- **Owned paths:** `tools/scanner_line_probe.cpp`, `docs/SCANNER_PROBE.md`, this note.
- **Repository base inspected:** `80ea8cd2d7febe12fc4dd382e475a00ff4181eac`;
  the live prepared line from assignment 13 was an explicitly coordinated,
  uncommitted dependency. No claim that the base commit already contained it.
- **Shared changes:** none. Root owns CMake wiring, current status, manifest,
  integration snapshots, commit and publication. This worker did not use Git
  mutations, spawn workers or change Engine/native/controls.

## Delivered behavior

The new `hammond_scanner_line_probe` links `hammond_core` and emits versioned
JSON for three separately labeled experiments:

1. A batch of actual prepared-recurrence responses with nineteen complex taps,
   common return, input admittance, residual and conditioning diagnostics.
2. Actual `process_frame` cosine excitation, non-bin-centered cosine/sine/DC
   least-squares estimates, separate half-window estimates, fit-residual
   diagnostics and the final physical checkpoint.
3. Bounded stdin endpoint traces including complete initial/restored physical
   coordinates, initial observation and every actual processed endpoint/state.

All responses retain nominal model, realization and compiled fixture identities,
physical units, fixed signed tap order, operation method and endpoint convention.
Response and sine operations never silently substitute for one another. The
trace counter is independent of its explicit relative time origin.

The CLI validates required/duplicate/unknown/inapplicable options, finite
decimal syntax and bounded numeric dimensions. It rejects invalid physical
checkpoints through the public line API and prevents completed-counter overflow.
The full report is buffered until successful completion; stdout remains empty
for input/processing failures. It opens no output path and cannot truncate a
file itself. Callers must still publish captured stdout safely; shell redirection
has independent overwrite behavior.

Limits are 1,024 response frequencies, 16,384 trace input knots, 128 bytes per
numeric token, 32,768 bytes per option value, 16,777,216 sine frames and a
64 MiB report. Offline allocation is deliberate and does not claim callback
qualification. Root added the executable target and its MinGW Unicode startup
option; the implementation uses existing `CliArguments.h`/`wmain` conventions.

## Source identities and toolchain

| Input | SHA-256 |
| --- | --- |
| Final `tools/scanner_line_probe.cpp` | `4a283205949a837df8835f2b86874ee66624631d05fbdf8a6ccce7ff54e16fdb` |
| `include/hammond/ScannerLine.h` | `c249f7c5556d6a6c8c58978928f0b860be442cb1188d35e49c59575729af00c7` |
| `src/ScannerLine.cpp` | `4280db3caa3f7aa225c58a0fa64ec4ca31add55ab8bb46a27aca2deba4544336` |
| Compiled scanner fixture | `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604` |
| Final local smoke executable | `8432e5b099559429ac87909c72a498bb9ba9d5c0760a433188b7106ced5f688e` |

The worker used GCC 14.2.0 and Python 3.12.14 on Linux. The smoke executable
linked the assignment-13 `a13-build/libhammond_core.a`, after confirming the
stable public header/implementation identities above. It was placed at
`/workspace/scratch/1742da7072be/a16-scanner-line-probe`. This is producer
evidence, not a coherent whole-repository or hosted platform qualification.

Actual compile command, from the repository root:

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror -I include \
  tools/scanner_line_probe.cpp \
  /workspace/scratch/1742da7072be/a13-build/libhammond_core.a \
  -o /workspace/scratch/1742da7072be/a16-scanner-line-probe
```

## Executed checks

| Experiment | Observed result |
| --- | --- |
| Strict GCC build | Passed with all configured warnings treated as errors. |
| Six response bins, chorus at 48 kHz | Valid JSON, correct fixture identity; largest residual `2.4508225317807103e-16`. |
| Actual 997 Hz chorus processing, 65,536 warmup plus 65,536 measured frames, 1 V | Largest tap complex error against the separately invoked response operation `4.577566798522237e-16`; half-window maximum `1.1102230246251565e-16`. |
| Same sine residual diagnostic | Largest tap residual RMS `2.4336111188262165e-9` V. This sum-of-squares diagnostic is roundoff-limited at near-exact fits; it is not a pass threshold. |
| Twelve matched-step independent nodal traces | Three host rates × two modes × cold/charged initial state, 64 frames each (768 frames total); largest voltage/current-normalized tap/state difference `3.630429290524262e-14`. |
| Trace clock and checkpoint | First returned frame was initial count plus one; initial observation at `-1/fs`, first knot at zero; restored nonzero count and previous input retained. |
| Eleven distinct research rates | Each admitted and returned DC/1 kHz response JSON. Fifteen host/multiplier labels remain the external experiment's responsibility. |
| Repeated response invocation | Identical stdout bytes in the local executable/toolchain. |
| Twenty-nine malformed argument/stdin/checkpoint cases | Every case returned nonzero and empty stdout. |

The nodal trace experiment used assignment 14's `TransientLine` with the
admitted fixture, no runtime matrices or reconstruction helpers. For each
mode/rate it compared a cold checkpoint and a charged checkpoint with
`x1=1 V`, `i18=-1e-4 A`, previous input `0.125 V`, frame count 917.
Input was `0.25*sin(0.1*n)` for 64 knots. All nineteen tap values, eighteen
capacitor volts and eighteen inductor amps were compared at matching counters;
current-coordinate differences were normalized by `1e-4 A`. This is a
matched-step smoke, not the frozen full basis or converged continuous-time gate.

The malformed cases included missing/duplicate/unknown CLI data,
unsupported/nonfinite rates, negative/Nyquist/trailing-comma/oversized frequency
lists, empty/blank/whitespace/nonfinite/oversized stdin, input just beyond 64 V,
wrong coordinate count, joint energy overflow, nonfinite prior input, uint64
overflow and a valid maximum counter with an impossible next interval.

### Portability review and repair

Root identified that the first draft used floating `std::from_chars`, which
would reintroduce an already documented libc++ compatibility problem. Before
source freeze, this worker replaced it with `detail::parse_decimal` and added
the same `DecimalRounding` guard used by existing metadata tools. The strict
build passed again. Four accepted decimal-list probes (leading plus, exact zero
with a huge exponent, leading/trailing decimal points and padded integers) and
ten rejected decimal probes (nonfinite, overflow, unrepresentable underflow,
hexadecimal, whitespace, separators, control/trailing characters and empty
input) all behaved as specified. The actual 997 Hz sine comparison was rerun
after this repair and retained its `4.577566798522237e-16` maximum tap error.
Two additional final-parser probes rejected operation-inapplicable options
(response warmup and trace frequency) with empty stdout.

The broader producer smoke above preceded this parser-only repair; the final
parser and sine checks identify the final source/executable hashes. Root and
assignment 17 own coherent integration and independent numerical acceptance of
the final frozen source. Local compilation does not establish macOS, Windows,
MinGW or hosted execution.

## Coordination and next step

The response/sine JSON contract was sent to assignment 17 before implementation
completed, and the final source hash was sent before its coherent independent
build. Its early startup observation already demonstrates why the probe never
self-certifies convergence: a shorter warmup can leave a transient even when
the later settled estimate agrees. The JSON always preserves the explicit
`caller_must_compare_longer_warmup` status.

Next, run the frozen full-grid warp-aware and same-hertz comparison against the
independent AC reference, qualify actual processing at all required sine
frequencies with longer-startup convergence evidence, and consume the trace
path for full physical-basis and transient comparison. Retain failed and
inconclusive cases. The probe does not implement rotor, route U/L/P/Q, add
controls, select an audible resampler/filter policy, close G5/G6 or supply
physical scanner evidence. See [SCANNER_PROBE.md](../../SCANNER_PROBE.md) for
the stable invocation and exact schema.
