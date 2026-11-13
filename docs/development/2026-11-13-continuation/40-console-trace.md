# Assignment 40 — bounded nominal console trace

Agent: `/root/w07_a40_console_trace`

Wave: 07, assignment 40 of this continuation's 60 new agents

Date: 2026-11-13 UTC

## Scope and implemented contract

Added `hammond_console_trace`, a standard-library offline client of public Engine
APIs. It accepts exactly five required option/value pairs: explicit compiled
profile, one of three named scenarios, supported sample rate, unsigned 64-bit
seed and output filename. Exclusive `--help` is also supported. The three fixed
120 ms schedules expose partial-key hysteresis, overlapping legato keys and
Cancel/bank/percussion routing transitions. Their exact commands and sample-grid
conversion are retained in [CONSOLE_TRACE.md](../../CONSOLE_TRACE.md).

Every run prepares the nominal linear-contact factory, explicitly enables
Second/Normal/Fast percussion and leaves all sustained drawbars zero. It tracks
upper MIDI 60 and 67, including each key's target, position and nine contacts.
Source IDs come from the owned profile's second-harmonic routes; they are not
hard-coded physical terminals. Shared readiness, physical and routed detectors,
eligibility, gains, routing controls and both current source phases accompany the
actual floating output sample.

Each row represents state after that frame's commands and before rendering or
advancing the sample. The tool flushes scheduled events without elapsed time,
copies public diagnostics, renders one sample, then formats the saved state and
that sample. It never reconstructs or mutates a private DSP history. All string
formatting, allocation and file access occur outside Engine processing calls.

CSV schema 1 has 28 explicit metadata comments and 36 numeric columns. Model IDs,
profile ID, declared authoring digest, scenario version, rate, seed, units and
row convention are documented. The declared digest is not presented as an
independently authenticated authoring or compiled-file hash. No timestamps or
paths enter CSV output. Same-input replay is deterministic on the same build;
cross-platform libm byte identity is not promised.

The complete trace is bounded to 11520 rows and 8 MiB before any temporary output
is created. Argument, profile and path checks precede generation. A private
sibling directory is reserved atomically; the file is written, flushed and
closed, then published with a hard link that cannot replace an existing target.
Existing files, directories and dangling symlinks are preserved. Output errors
return nonzero and temporary cleanup is attempted. Successful file generation
prints no stdout status that could fail after a valid file is published.

CMake builds the strict-warning executable and supplies
`HAMMOND_CONSOLE_TRACE_EXECUTABLE` to Python tests. The `check` target includes the
trace executable. No installation rules, core algorithms, saved-state formats,
parameter IDs, existing tools or shared handoff files were changed.

## Source basis

Read the standing instructions, current README/status/next steps/log, project
plan, consolidated atlas review and console contract. Read the complete extracted
atlas pages 115-120, 133-135, 389 and 401. Those pages motivate separate contact
histories, phase preservation, shared continuous percussion and the distinction
between routing controls and DSP history. The implementation exposes the already
named nominal models; it does not implement measured bounce, switching
antialiasing, a complete AO-28 circuit, loaded preset latches or acquired hardware
traces. No additional physical values were invented by this assignment.

## Coherent qualification and observations

A separate source tree was extracted from lifecycle commit
`53bb6e1e37eedf84f566ffb8bd9037b50f123a20`, then overlaid only with assignment 37's
three frozen public/core files and this assignment's CMake, tool and contract.
Every overlay was hashed before building and rechecked against the live file
before completion. The core and executable were built together; no later live
header was linked against an older library.

Strict GCC 14.2.0 Release configuration and compilation passed on the first build.
The scratch implementation smoke exercised the following actual runs:

| Check | Observed result |
| --- | --- |
| All three scenarios at all three rates | 9 successful runs; 67716 rows total |
| CSV shape and values | Exactly 28 metadata comments and 36 columns; contiguous frames, finite numeric values, LF endings and declared row counts |
| Largest observed output | 2392173 bytes, partial scenario at 96 kHz, below 8388608-byte limit |
| Partial hold | At 0.5, four closed contacts from below and five from above; initial harmonic audio precedes the physical detector |
| Legato join | Companion target changes while shared readiness remains below one and the held detector remains closed |
| Routing | Cancel preserves position/contact closure while output and eligibility stop; A and B selection restore the documented route states |
| Panic | Every scenario's 112 ms row has zero position, target, contacts and output, while readiness remains continuous and below one |
| Identical replay | Second 48 kHz partial run byte-identical to the first |
| Maximum seed | `18446744073709551615` accepted, finite valid CSV, differing from seed zero |
| Invalid and protected-output cases | 22 nonzero rejection results; no unexpected final output or temporary residue |
| Help | Exclusive help succeeds; Linux `/dev/full` help-output failure returns nonzero |

The 22 rejections cover missing/unknown/duplicate options, mixed help, invalid
scenario, unsupported/fractional rate, signed/overflowing/overlong seed, existing
file/directory, dangling symlink, absent output parent, input/output collision,
malformed/missing profile and help write failure. The protected file and profile
bytes remained unchanged. Actual disk exhaustion, the 128-attempt reservation
limit and an adversarial concurrent destination race were not injected in this
smoke; assignment 41 owns independent permanent failure and numerical acceptance.
No build failure, production defect or failing smoke assertion occurred.

Commands actually run, with paths identifying this scoped local qualification:

```sh
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  -S /workspace/scratch/60e8291da354/a40-trace-qualification/source \
  -B /workspace/scratch/60e8291da354/a40-trace-qualification/build \
  -DCMAKE_BUILD_TYPE=Release
/workspace/scratch/c871510c69b2/build-tools/cmake/data/bin/cmake \
  --build /workspace/scratch/60e8291da354/a40-trace-qualification/build \
  --target hammond_console_trace --parallel 4
python /workspace/scratch/60e8291da354/a40-trace-qualification/smoke.py
```

The temporary smoke script is not a permanent repository test or a dependency of
future builds. Assignment 41 supplies the independent retained suite. Snapshot
metadata and detailed observed output hashes were recorded beside that smoke.

| Frozen file | SHA-256 |
| --- | --- |
| `include/hammond/Types.h` | `a8f86c3b0910a5e0921b1ff583b4c947573dfecb955bff2c8341613ffdf95fe0` |
| `include/hammond/Engine.h` | `efb8f0eb36dccbe5f0416186ef9478091be48e5634cfd6a8f0155b3dfd1c81c0` |
| `src/Engine.cpp` | `53c07390447796f4c57e96e58b9d6720df76094e14a0e6240b284f62e4310ccf` |
| `CMakeLists.txt` | `f37c6bd8dedb1325db4f79ed15162b837139254b1f1c2ac100e105b8a2dbfeac` |
| `tools/console_trace.cpp` | `810574b16848ba34ccf3d1e26be10339357230deffc5df4fbb8bab23891b7f75` |
| `docs/CONSOLE_TRACE.md` | `a954a1670131e215e322fa2806c1527efb6998c3f15e6f2776dd056592863996` |
| Qualified executable | `0334f85343477c427c3de094b3e81802eb2d18d7df664b9f8596ced6cfb66a5c` |
| Generated `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Scratch smoke script | `ba3ecba9d51615255f2ac0fb70a65004e920c283887e4ab411a3f0c3cb55facf` |
| Scratch smoke summary | `548790888be3c06aac310d7620d573ec6080794392834f7529e08d99076f5fbc` |

## Files, handoff and limits

Only [console_trace.cpp](../../../tools/console_trace.cpp),
[CMakeLists.txt](../../../CMakeLists.txt),
[CONSOLE_TRACE.md](../../CONSOLE_TRACE.md) and this note were added/edited. All
changes remain unstaged; no commits, pushes, index operations or subagents were
used. CMake changes are limited to this executable and its test environment.

Assignment 41 received the exact contract and frozen identities for independent
schedule/numeric/CLI tests. Assignment 42 received a coherent executable/profile
and actual CSVs for the precise plotter. The integrator owns the combined staged
build, current shared status, authorized expected-head publication and actual
hosted checks. Installation/relocation of the trace is a later packaging task.
This local smoke makes no cross-platform, sanitizer, physical-fidelity, native
host/device, live diagnostic transport or callback-deadline claim.
