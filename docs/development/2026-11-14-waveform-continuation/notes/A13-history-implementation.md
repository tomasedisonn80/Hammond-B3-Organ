# A13 — Bounded waveform and motion history implementation

## Actual assignment and source boundary

- Actual worker: `/root/w03_a13_history_implementation`, wave 3, 2026-11-14.
- Inspected starting/current HEAD:
  `26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8`.
- Working directory: `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`.
- Owned deliverables: `src/RotaryHistory.cpp`,
  `tests/test_rotary_history.cpp`, and this note. No public header, contract,
  CMake, shared build, shared status/manifest, Engine, UI or unrelated source
  was changed. No commit or push was attempted by this worker.
- Read standing instructions, current scope/checkpoint/assignment manifest,
  complete M0–M9 plan, current status/next-step/log entry, atlas review and A04's
  rotary reading, frozen renderer/numerical contracts, history/renderer/motion
  headers, existing motion implementation and transaction review. This is not
  another independent full-atlas reading.

## Implemented behavior

`WaveformHistory` owns its fixed 16,384-slot array, admits active capacities
1–16,384, clears every slot on successful prepare/reset, and retains exactly
the active nonnegative interval. Negative sample indices within the signed
one-day epoch return declared positive zero. Retired/future positive samples
are unavailable; neither becomes implicit silence. Preparation, input-range,
epoch and query failures publish no mutation or output.

The cubic kernel checks all four finite normalized support values, admits the
closed fraction interval [0,1], preserves exact endpoint samples including
signed zero, and accumulates the four Lagrange terms in support order. It stages
the result before publication, so an output may alias any input sample. It
does not clip the 1.25 overshoot fixture. History interpolation admits only
canonical [0,1) fractions, checks the whole signed support-index domain before
forming offsets, and requires all four nodes even when their weights are zero.

`MotionFrameHistory` copies epoch metadata and complete original command
segments into a fixed interval ring. Append validates owner preparation,
rate/profile/seed/frame, exact native-state continuity and the next endpoint
before writing. Its active append limit is checked without requiring that an
owner's limit equal it, retaining the reviewed private shortened-limit seam.
It never replaces a command anchor with an observation/interval anchor.
Positive fractional queries choose their owning floor interval; the exact
final endpoint uses the last retained segment; an empty history admits its
frame-zero seed. Negative queries always use the epoch's constant-speed seed,
including after positive intervals retire. Copies own independent bytes and
retain no reference to a motion owner.

All implementation methods have bounded storage/work and use no allocation.
Prepare/reset clear fixed storage; append/push/query work is constant with
respect to duration and lifetime event count. The allocation statement here
is source inspection, not the later calibrated R6 allocation experiment.

## Focused executed verification

Toolchain: `g++ (Debian 14.2.0-19) 14.2.0`, C++20. The direct test links only
the unchanged motion implementation and the new history implementation.
`TestSupport.h` requires profile/source macros; the profile macro is empty
because these synthetic fixtures do not read any profile file.

Commands actually executed from the working directory above:
The stack-limited commands used separate shell invocations and did not lower
the limits of subsequent compiler or sanitizer invocations.

```sh
mkdir -p /workspace/scratch/e3cacb90cc81/Hammond-B3-Organ/tmp/a13-history
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror -Iinclude -c src/RotaryHistory.cpp -o tmp/a13-history/RotaryHistory.o
g++ --version
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror -Iinclude -Itests '-DHAMMOND_TEST_PROFILE=""' '-DHAMMOND_SOURCE_DIR="."' src/RotaryMotion.cpp src/RotaryHistory.cpp tests/test_rotary_history.cpp -o tmp/a13-history/test_rotary_history
tmp/a13-history/test_rotary_history
ulimit -s 512 && tmp/a13-history/test_rotary_history
g++ -std=c++20 -O1 -g -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror -fsanitize=address,undefined -fno-omit-frame-pointer -fstack-usage -Iinclude -Itests '-DHAMMOND_TEST_PROFILE=""' '-DHAMMOND_SOURCE_DIR="."' src/RotaryMotion.cpp src/RotaryHistory.cpp tests/test_rotary_history.cpp -o tmp/a13-history/test_rotary_history_sanitized
tmp/a13-history/test_rotary_history_sanitized
ASAN_OPTIONS=detect_leaks=0 tmp/a13-history/test_rotary_history_sanitized
test ! -e /workspace/scratch/e3cacb90cc81/a13-history && mv tmp/a13-history /workspace/scratch/e3cacb90cc81/a13-history
ulimit -s 1024 && /workspace/scratch/e3cacb90cc81/a13-history/test_rotary_history
```

Both strict compilations succeeded with zero warnings. Optimized ordinary,
512 KiB stack, 1 MiB stack and ASan/UBSan-with-leaks-disabled runs exited zero
and printed this identical observed line:

```text
rotary_history: rejected_calls=399 retained_queries=80269 lifetime_events=46200 rate_epochs=16 waveform_bytes=131112 motion_bytes=917608
```

The **default sanitizer run exited 1**, with this actual diagnostic:

```text
==2==LeakSanitizer has encountered a fatal error.
==2==HINT: For debugging, try setting environment variable LSAN_OPTIONS=verbosity=1:log_threads=1
==2==HINT: LeakSanitizer does not work under ptrace (strace, gdb, etc)
```

The successful separate `ASAN_OPTIONS=detect_leaks=0` repeat establishes only
the executed address/undefined-behavior scope. It does not turn the failed
default run into a leak pass. A43 owns later full sanitizer/integration work;
this worker did not change sanitizer configuration or acceptance gates.

The focused suite covers:

- Alias-safe cubic endpoints/interior, signed endpoint zeros, invalid unused
  endpoint supports, all-support validation, and unclipped overshoot.
- Capacities 1, 4, 7 and 16,384; maximum-capacity repeated wraps; negative
  history, retired/future slots, both zero-weight support boundaries, canonical
  fraction rejection and signed one-day/`int64_t` overflow admission.
- All four rates and both directions; 5,005 intervals per rate/direction
  with 5,775 actual accepted commands each, including unchanged commands and
  same-frame ties. Storage does not grow after 4,097 lifetime events.
- Exact final-boundary ownership, old/new command intervals, original anchor
  retention after its command slot retires, negative history after retirement,
  independent history copies, and owner destruction after copying its history.
- Wrong/unprepared owner, mismatched rate/profile/seed, a matching-metadata
  but discontinuous trajectory, wrong frame, invalid preparation and shortened
  private append-limit rejection. The shortened-limit cases exercise the
  private guard; they do not claim to have processed a full day of samples.
- All sixteen old/new rate pairs, including equal rates, with nonzero retained
  turns, current-state epoch seeds, capacity-one wraps, reset and complete
  clearing on replacement preparation.

Rejection snapshots are heap allocated and compare every numeric field and
every backing slot by floating bit representation, including inactive slots;
struct padding is not compared. Motion-routing expected values use the already
qualified public motion primitives, so these are focused ownership/behavior
checks, not a second independent numerical motion oracle. A14 owns independent
polynomial, analytic motion and full complex-delay acceptance.

On this ABI `WaveformHistory` is 131,112 bytes and `MotionFrameHistory` is
917,608 bytes. No full history or history snapshot is placed on the test stack.
The retained sanitizer-build `.su` reports list a largest history-production
frame of **592 bytes** (`MotionFrameHistory::append`) and a largest focused
test frame of **4,832 bytes**. Those figures describe this instrumented build,
not an unmeasured target or device deadline. Owned binaries/object/stack reports
were moved out of the repository at the integrator's request; their final
scratch directory `/workspace/scratch/e3cacb90cc81/a13-history` totals **1.2 MiB**.

## Exact qualified input hashes

SHA-256 values observed after the executed tests; source/header inputs were
unchanged between those commands:

| Input | SHA-256 |
| --- | --- |
| `src/RotaryHistory.cpp` | `4f3c4fbd957f7cc9131b1f4e7c6e77f69df1b7e85c9ba4073de59fe52322a0f5` |
| `tests/test_rotary_history.cpp` | `297b66cf67adcd24e4f33fed15001400d8c70255ec3e3341dae79ba732c57102` |
| `src/RotaryMotion.cpp` | `a3f986892078254f6dfae936bbbf1b5e1c4967882d06c13b3b28649f2273cfa1` |
| `include/hammond/RotaryHistory.h` | `9e6930342a5c83bdcf99102aaeb0dc9b0714e85561bd8205a53155a7fca4a25b` |
| `include/hammond/RotaryMotion.h` | `7bc81331f84b7ce490bf9047114336e633f3da91a39bbfd2a13e3fd406f61d36` |
| `include/hammond/RotaryTypes.h` | `b27ce4934188c24ebe557469fa5191dd7cdcd98a1c3fdbe274b0d7585e4578b4` |
| `include/hammond/RotaryRenderer.h` | `5f74af0a7ca629b433fe7f3d72a44a2b39daf90fd2d64afa579aecd26f48ccd0` |
| `docs/ROTARY_RENDERER_CONTRACT.md` | `52eaaeda293376abd47af3f788e3bd5967452b176cba021f23ab7bc3b1e141a9` |
| `docs/ROTARY_NUMERICAL_CONTRACT.md` | `4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63` |
| `tests/TestSupport.h` | `8869acab1e7492699b656984c7b24eb6d33f09dad6f989814a8a0c04e3c86be5` |

## Handoff and remaining gates

Integrate this unchanged API implementation with the streaming path and
transactional renderer, accept A14's independent history/cubic evidence, then
qualify the complete renderer's four-rate same-cubic parity, block/event
partitioning, lifecycle, tails and actual partial-write/multiple-wrap rollback.
The existing source/test globs can discover these files when root reconfigures
its shared build; this worker did not touch that build. Repeat qualified tests
after any source or frozen-header change and retain the new identities.

R5 audible reconstruction/alias policy, calibrated R6 allocation/deallocation
and deadline/integration evidence, default leak-enabled sanitizer execution,
complete M5/M6 signal graphs and physical M7 calibration remain separate.
This history implementation neither connects Engine audio nor changes musical
state, parameters, model identity or physical-fidelity claims.
