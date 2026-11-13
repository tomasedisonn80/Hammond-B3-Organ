# Assignment 13: prepared nominal scanner line

## Identity and ownership

- Assignment 13/60, wave 3/10; agent `/root/w03_a13_prepared_scanner_line`.
- Owned files: `include/hammond/ScannerLine.h`, `src/ScannerLine.cpp`,
  `docs/SCANNER_LINE.md`, and this note. The integrator owns CMake, the shared
  status/handoff/manifest, integration and publication. No Engine, controls,
  native adapter, other worker's tests, Git index or remote ref was modified
  by this assignment.
- Session starting revision was `6dc0702d5473912268e8af8f852b9b9984198ef3`,
  tree `a4f1d4b300de236436e22b748b1d4c46ed501ceb`. During this assignment
  the integrator committed the completed foundation as `74473fa`, followed by
  `abbd7b94dec7ba07a23e9dd7a626fa981af5bc3a`, tree
  `d98d9baf666f048629f5c817ed0f040b215df0e4`. The new line files remained
  uncommitted during the producer checks below; their hashes identify the
  compiled source precisely. These checks do not claim to qualify the whole
  concurrent worktree.
- Read the standing instructions, nominal graph, primary-source review,
  frozen numerical contract and assignment 03's separately derived physical
  equations. This assignment implemented and checked the runtime; it does not
  claim a second complete atlas or primary-paper reading.

| Input or source | Identity / SHA-256 |
| --- | --- |
| Model | `atlas-late-b3-nominal-line-v1` |
| Realization | `scaled-physical-trapezoidal-scanner-line-v1` |
| Authoring fixture | `1d236be5e6b63e938a9f147808386173949d167e09aee8e902c55002e4ea4604` |
| Generated `ScannerLineData.h` | `d508e3856e637a8e107364ad2a8fed09893a2e50ae05d99db3d4b3da37a5a082` |
| Frozen `scanner-numerics-v1` contract | `3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9` |
| New `ScannerLine.h` | `c249f7c5556d6a6c8c58978928f0b860be442cb1188d35e49c59575729af00c7` |
| New `ScannerLine.cpp` | `4280db3caa3f7aa225c58a0fa64ec4ca31add55ab8bb46a27aca2deba4544336` |

## Implemented contract and decisions

The [module contract](../../SCANNER_LINE.md) gives the complete equations,
API, scaling, rate set, bounds, clock and status semantics. The implementation
retains eighteen capacitor voltages, eighteen inductor currents, previous
input voltage and completed-interval count. It algebraically eliminates the
common return and six divider observations for this ideal graph, retaining
all 36 physical energy coordinates. The derivation is independent of the
offline nodal AC stamp and its LU implementation.

Currents are scaled by `sqrt(0.5 H / 4e-9 F)` during numerical preparation and
each matrix-vector update, then converted back to amperes in the public
checkpoint. Both return modes receive prepared double-precision trapezoidal
operators. Preparation uses fixed-size row-scaled partial-pivot LU with
explicit normalized residual checks. Per-frame processing uses fixed arrays,
bounded loops and a prepared 36-by-36 matrix-vector product. It performs no
allocation or factorization. These are source-level properties here; runtime
allocation and performance qualification have separate test owners.

`prepare` resets on success. A stopped `reconfigure_sample_rate` preserves
the exact physical checkpoint while rebuilding both operators. Mode selection
does not reinterpret state or retain an algebraic history. The selected mode
applies to the whole upcoming interval. An explicit `observe` reconstructs
the existing endpoint without an advance. Frame count is the number of
completed intervals: first processed frame 1 corresponds to contract input
knot 0 at `t=0`, with the cold checkpoint at `t=-1/fs`. Previous input is
retained across a rate change and belongs to replay state, not saved musical
controls.

Admission has explicit inclusive bounds: input 64 V, individual capacitor
65536 V, individual inductor 2 A, joint energy 1 J, output voltage 131072 V
and source current 4 A. They reject invalid or oversized candidates without
clipping. A failure preserves both state and destination. The checkpoint may
contain count `UINT64_MAX`; advancing it returns `TimelineOverflow`.

The offline `response` helper solves the actual recurrence at a requested
digital frequency including DC, exports all signed complex tap and return
gains and source admittance, and reports residual and infinity condition on
the same row-scaled matrix. It is not an analog-only answer or a replacement
for testing the frame path. Rates are exactly the 15 host/multiplier pairs
in the frozen research contract, representing 11 distinct numeric rates.
No host-rate or controls-format expansion was made.

The stable API, argument statuses and completed-interval convention were sent
to the integrator and assignment 15 before its independent build. Assignment
14 aligned its independent companion-circuit oracle's frame field to the same
count while retaining a separate zero-based physical knot/time label.

## Executed producer checks

Working directory: `/workspace/scratch/1742da7072be/Hammond-B3-Organ`.
Toolchain: GCC 14.2.0 (`Debian 14.2.0-19`), CMake 4.4.4, Ninja
`1.13.2.git.kitware.jobserver-pipe-1`, Python 3.12.14, Linux x86-64.
CMake/Ninja were exposed by adding
`/workspace/scratch/1742da7072be/build-tools/bin` to `PATH`.

### Strict core compilation

The final successful isolated configuration and build commands were:

```sh
PATH=/workspace/scratch/1742da7072be/build-tools/bin:$PATH \
  cmake -S . -B /workspace/scratch/1742da7072be/a13-build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF \
  -DCMAKE_INSTALL_DATADIR=share
PATH=/workspace/scratch/1742da7072be/build-tools/bin:$PATH \
  cmake --build /workspace/scratch/1742da7072be/a13-build \
  --target hammond_core --parallel 2
```

The generated scanner header and the new source compiled with the core's
`-std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion
-Wshadow -Werror`, Release `-O3 -DNDEBUG` flags. `compile_commands.json`
was inspected to confirm the actual source, flags and generated include path.

**Setup failure retained:** the first attempt to rebuild the shared
`scanner-build` stopped in `InstallHammondTools.cmake` because its cached
`CMAKE_INSTALL_DATADIR` was empty. The shared cache was left unchanged. A fresh
isolated `a13-build` configured and built successfully, but a later explicit
reconfigure reproduced the same empty-cache failure. Its cache had
`CMAKE_INSTALL_DATAROOTDIR=share` and an empty `CMAKE_INSTALL_DATADIR` under
CMake 4.4.4. Passing `-DCMAKE_INSTALL_DATADIR=share` repaired the isolated
configuration; configure and build then passed. The integrator received the
reproducer. This setup failure is separate from the successful compiler and
numerical checks and was not repaired by editing shared project files.

### Physical-state and process smoke

A temporary producer harness was compiled outside the repository:

```sh
c++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror \
  -I /workspace/scratch/1742da7072be/Hammond-B3-Organ/include \
  /workspace/scratch/1742da7072be/a13-smoke.cpp \
  /workspace/scratch/1742da7072be/a13-build/libhammond_core.a \
  -o /workspace/scratch/1742da7072be/a13-smoke
/workspace/scratch/1742da7072be/a13-smoke --response \
  > /workspace/scratch/1742da7072be/a13-response.csv
```

The temporary harness SHA-256 was
`0e96d27d454bd8b5394d669cf76e189f2d2ca00b19fac2c1645d9cd8721e274f`;
its response CSV SHA-256 was
`a009ec26e4f6532c74afc5a8ef0c7f07d05664a266050302594d8507d6d79ea3`.
These are session-local producer aids, not installed tools or durable
acceptance artifacts. The independent maintained state tests are owned by
assignment 15 and must be run from the eventual coherent integration tree.

Executed scope and result:

| Check | Actual coverage / result |
| --- | --- |
| Preparation and response | All 15 host/multiplier pairs, both return modes, frequencies 0, 20, 100, 997, 1000, 5000, 7000 and 20000 Hz: 240 responses passed. |
| Solve checks | Largest preparation/response normalized residual `8.7521587399752838e-16`; largest sampled response condition `605.55208405965811`. |
| Physical basis and energy | Every one of 36 coordinates, both polarities, all 15 host/multiplier pairs, both modes; capacitor seed 1 V, inductor seed 0.0001 A; 64 zero-input advances each, totaling 138240 passive frames. |
| Passivity bounds | Every step and cumulative energy check passed the frozen bounds; largest positive per-step change divided by initial energy was `1.2407709188295415e-15`. |
| Transaction and stopped rate | Precharged state, NaN input rejection, invalid preparation and max-count rejection preserved state/destination. Retune 48000 to 1536000 Hz preserved the complete checkpoint exactly. |
| Actual process-path sinusoid | At 48000 Hz, each mode processed a 1000 Hz cosine, removed 24000 startup frames and demodulated the following 9600 frames. All nineteen taps, return and source current normalized by 15000 ohms agreed with prepared response; largest complex error `2.6605366123254084e-14`. |

A further deterministic candidate-failure probe prepared 1536000 Hz, restored
an otherwise-zero state with `i1=2 A` and previous input 64 V, and observed
exactly 1 J in vibrato. `process_frame(64 V, Vibrato, ...)` rejected with
`InvalidBuffer` while preserving the checkpoint and existing destination.
This fixture was passed to the independent test worker to exercise a
post-computation rejection, as distinct from an invalid argument.

### Independent AC/DC spot comparison

A Python standard-library check read the 240 response rows, prepared the
admitted graph using `scanner_ac_reference.prepare_network`, and compared:

- At DC: `dc_reference`'s independent exact `Fraction` resistor result.
- At positive digital frequency `f`: `solve_ac` at analog frequency
  `fs/pi*tan(pi*f/fs)`, without changing polarity, gain, phase or latency.
- All nineteen taps, return and input current normalized by 15000 ohms.

It graded DC with `1e-10 + 1e-9*abs(expected)` and finite frequency with
`1e-8 + 1e-6*abs(expected)`. All 5040 complex transfer comparisons passed.
Largest absolute error was `1.039680984300428e-12`; largest DC error was
`1.900701818158268e-13`. Largest fraction of the applicable error budget was
`0.00013241932802801867`, at host 96000 Hz, factor 16, vibrato, DC, tap 19.
This is a spot comparison, not the required full 282-bin stationary report.
It does not grade same-hertz distortion or select oversampling.

All four owned files passed `git diff --no-index --check /dev/null FILE`
without whitespace diagnostics. Both new documents' relative Markdown links
resolved to existing repository files. Final source hashes still matched the
compiled header and implementation listed above. Concurrent assignment 14/15
files were observed and preserved.

## Limits and next required work

The implementation and stable API are ready for independent state, runtime,
transient and frequency qualification. Producer smoke alone does not close
G3. Run the maintained independent tests, qualify all frozen stationary bins
and actual process frequencies, compare independent companion-circuit
transients, retain same-hertz failures, and identify the exact integrated
source tree before claiming a gate pass. Assignments 14-16 and later waves
own those experiments; their results belong in the current scanner handoff.

No rotor, resampler, audible-rate policy, routing, Engine/native integration,
physical receiver load, measured voltage scale, winding loss or specimen
capture was introduced. The highest research rate has a fixed computational
cost but no real-time deadline claim from this assignment. A physical fidelity
claim requires acquired hardware evidence separately from numerical agreement.
The integrator must record independent outcomes, update shared status/next
steps, commit the coherent completed files and verify publication under the
owner's standing instructions.
