# Develop and qualify the independent Leslie crossover

`hammond::LeslieCrossover` is an independent M6 electrical research primitive.
It implements the atlas's selected Leslie 122 divider with ideal L/C elements
and two constant resistor loads. It has no Engine route, amplifier, loudspeaker
or acoustic response. The playable organ's 47 sound parameter identities,
`B3CONTROLS4` writer and readers 1–3 retain their existing meanings.

Use the [frozen contract](LESLIE_CROSSOVER_CONTRACT.md) for the normative circuit,
signs, numerical budgets and rejection precedence; the
[same-Hz characterization](LESLIE_CROSSOVER_CHARACTERIZATION.md) for observed
frequency-response limitations; and [CROSSOVER_INSTALL.md](CROSSOVER_INSTALL.md)
for the explicit, relocatable `CrossoverTools` component. This guide covers
development from a source checkout. The installed component supplies the probe
and analog reference, not a public C++ SDK or the source acceptance suite.

## 1. Build the research targets

From the repository root, use CMake 3.21+, a C++20 compiler and Python 3.10+.
The crossover targets require no SDL, MIDI backend or VST3 SDK. Configure a
separate build directory and build the probe and its three native tests:

```sh
cmake -S . -B build-crossover -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --build build-crossover --config Release --target \
  hammond_crossover_probe test_leslie_crossover \
  test_leslie_crossover_lifecycle test_leslie_crossover_allocation
```

These target names and test registration come from
[CMakeLists.txt](../CMakeLists.txt). Building the native tests also builds their
declared generated core/profile dependencies. Configuration alone does not
build the executables required by CTest. Use the same configuration name for
build and test with a multi-configuration generator; `CMAKE_BUILD_TYPE` selects
the configuration only for a single-configuration generator.

The commands below use `cmake` and `ctest` from a normal developer's `PATH`.
The [2026-11-15 session checkpoint](development/2026-11-15-product-continuation/CHECKPOINT.md)
records a managed-workspace fallback at
`/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/` and the integrator's
shared `/workspace/scratch/5b7d983ac078/build-native` tree. Those absolute paths
are session setup, not checkout prerequisites. Coordinate ownership before
configuring, rebuilding or testing a shared tree.

## 2. Keep electrical quantities and history explicit

The [public header](../include/hammond/LeslieCrossover.h),
[implementation](../src/LeslieCrossover.cpp) and
[registry](../data/crossover/leslie-122-ideal-v1.json) identify the same fixed model:

| Identity or input | Admitted value |
| --- | --- |
| Model | `atlas-leslie-122-ideal-crossover-v1` |
| Numerical realization | `physical-trapezoidal-leslie-crossover-v1` |
| Documentary assembly | Leslie 122, 1971 divider **052803**, atlas pp. 271–276 |
| Sample rates | **44100, 48000, 96000, 192000 Hz**, exactly |
| Default loads | **16 ohm** treble and **16 ohm** bass |
| Alternative loads | Each finite resistance in **[1, 1024] ohm**, an explicit resistor experiment |
| Fixed elements | L2 = 0.0032 H; L3 = 0.0052 H; C16A = 0.0000078 F; C16B = 0.0000125 F |

The treble resistor is floating across **A–H**, in parallel with L2; C16A
connects H–B. L3 connects A–W, with C16B and the bass resistor across W–B.
Grounding the treble return changes this network. The imposed input is
`u = V(A) - V(B)` in volts. Its ideal zero source impedance and the zero-loss
elements are numerical assumptions. Actual component losses, driver impedances
and specimen applicability remain unknown, as the contract and registry state.

The physical checkpoint contains:

| `LeslieCrossoverState` member | Meaning |
| --- | --- |
| `capacitor_volts[0]` | V(H) − V(B), across C16A |
| `capacitor_volts[1]` | V(W) − V(B), across C16B |
| `inductor_amps[0]` | L2 current, positive A → H |
| `inductor_amps[1]` | L3 current, positive A → W |
| `previous_input_volts` | Input at the existing endpoint; required for exact replay |
| `frames` | Number of completed trapezoidal intervals |

`LeslieCrossoverFrame` reports `treble_volts = u - capacitor_volts[0]`,
`bass_volts = capacitor_volts[1]`, the two resistor currents, source current
entering A, stored energy in joules and the completed endpoint frame. The source
current includes both inductor currents and the treble resistor current. These
are electrical ports with defined signs; they do not establish speaker polarity
or a complementary acoustic sum. Input and output values use SI units, without
an implicit normalized-audio conversion.

### Lifecycle and replay

Include `hammond/LeslieCrossover.h` and link an existing research target to
`hammond_core`. Externally serialize all access. Prepare, restore, stopped rate
changes and frequency response belong outside processing. Check each returned
`Status` before consuming a destination or advancing a caller's timeline.

| Operation | Successful behavior |
| --- | --- |
| `prepare(rate, loads)` | Builds and checks the fixed operators; starts at zero capacitor/current state, previous input 0 and frame 0. Calling it again starts a new experiment. |
| `state()` | Returns a copy of the physical checkpoint. Record the model/realization IDs, loads and rate separately; they are not members of the checkpoint. |
| `restore_state(checkpoint)` | Replaces physical coordinates, previous input and frame count on an already prepared object; retains that object's operators, rate and loads. |
| `observe(destination)` | Observes the current endpoint using its stored previous input; advances no interval. |
| `process_frame(input, destination)` | Completes one interval and commits its right endpoint. The first success after fresh preparation reports frame 1. |
| `process(input_span, destination_span)` | Processes one bounded, whole-block transaction; agrees with scalar calls and legal block partitions. |
| `reconfigure_sample_rate(rate)` | Rebuilds the operators while preserving every checkpoint coordinate and frame count exactly; introduces no artificial sample. |
| `response(frequency, destination)` | Computes complex unit-input gains and input admittance of the actual prepared recurrence, without reading or changing the transient history. |

For exact replay in another object, prepare it with the same admitted rate and
loads, then restore the complete checkpoint. A deliberate rate-change experiment
uses the new rate with the preserved physical state. Retain a separate rate
timeline if elapsed seconds matter: a frame count spanning several rates is not
time at one fixed rate. There is no musical-preset serialization for this state.
A load change requires fresh preparation and resets history.

The recurrence uses both input endpoints:
`x_next = F*x_previous + G*(u_next + u_previous)`. Preparation factors the
four-state system and admits a normalized operator residual at most `1e-12`.
Processing uses fixed storage and deterministic bounded loops, with no
factorization, allocation, deallocation, locks or I/O. Block processing first
validates the entire candidate trajectory and then replays it to write outputs;
the caller must keep both spans valid and the input unchanged through both passes.

### Bounds and transactional failures

Both spans must have equal counts, contain at most **4096** frames and occupy
nonoverlapping byte ranges. Equal empty spans succeed after preparation without
advancing history, including at `UINT64_MAX`. Nonempty processing at that restored
endpoint rejects with `TimelineOverflow`. No method clips a rejected input.

| Numerical admission | Bound |
| --- | --- |
| Input and checkpoint previous input | Finite, absolute value ≤ 64 V |
| Each capacitor coordinate | Finite, absolute value ≤ 65536 V |
| Each inductor coordinate | Finite, absolute value ≤ 256 A |
| Stored energy | Finite and between 0 and 1e6 J |
| Every emitted port | Finite |

These are computational limits, not device ratings. A precharged fixture may
emit more than 64 V or reach a state limit after initially valid intervals; an
admitted checkpoint is not a promise that every later drive is admissible.
Finite subnormals are admitted without a v1 flush-to-zero policy.

Every failure preserves the previous object and caller destination, including a
numerical failure at the last frame of a block. Blocks reject in this order:
unprepared (`NotPrepared`), unequal counts (`InvalidBuffer`), capacity
(`BlockTooLarge`), frame overflow (`TimelineOverflow`), alias/buffer admission
(`InvalidBuffer`), then input/state numerical admission (`InvalidBuffer`).
Scalar processing checks preparation, overflow, then numerical admission.
Invalid prepare/rate/response specifications return `InvalidSpec`; invalid
checkpoint data returns `InvalidProfile`. An unprepared object takes precedence
for every operation requiring preparation. See the
[lifecycle tests](../tests/test_leslie_crossover_lifecycle.cpp) for bit-preserving
rejections and next-valid-call continuation.

## 3. Observe the native recurrence and independent analog circuit

For a single-configuration POSIX build, select the freshly built probe and a new
report directory. For a multi-configuration generator, use its configuration
subdirectory, commonly `build-crossover/Release/`; Windows executables also have
the `.exe` suffix. CTest resolves its executable path from the selected target.

```sh
hammond_probe="$PWD/build-crossover/hammond_crossover_probe"
hammond_reports="$PWD/out/crossover/run-001"
cmake -E make_directory "$hammond_reports"
"$hammond_probe" --help
"$hammond_probe" --operation response --sample-rate 48000 \
  --frequencies 0,400,800,1600,20000
"$hammond_probe" --operation sine --sample-rate 48000 --frequency 800 \
  --amplitude 0.25 --warmup-frames 65536 --measurement-frames 8192
python3 -B tools/crossover_reference.py \
  --output "$hammond_reports/analog-reference.json"
```

The [native probe](../tools/crossover_probe.cpp) has only `response` and `sine`
operations. `response` accepts 1–512 comma-separated finite frequencies with
`0 <= f < rate/2`; it includes the exact DC limits HT = 0, HW = 1 and
Yin = 1/RW. `sine` accepts `0 < f < rate/2`, amplitude in `(0, 64]` V, at least
8 measurement frames and at most **16777216** warmup-plus-measurement frames.
The command above spells out the sine defaults. Unknown, repeated, missing or
operation-inapplicable options reject. Real numeric tokens are complete finite
decimal values of at most 128 bytes; an option value is at most 32768 bytes.

The probe stages its JSON before emitting it to stdout, caps the report at
**2 MiB**, and returns 2 on rejected experiments or output errors. It has no
`--output` option. Capture stdout through a subprocess and retain it only after
checking exit 0; a shell redirection may create or truncate its destination even
if the command fails. A sine fit reports actual `process_frame` outputs and
first/second-half consistency, but does not independently qualify startup decay.
The acceptance harness supplies that bound.

The [Python reference](../tools/crossover_reference.py) independently compares
series/parallel algebra with edge-stamped nodal KCL. Its CLI uses 121 logarithmic
points from 10–20000 Hz plus 400/800/1600 Hz, for 124 points with DC separately;
it does not accept the probe's `--sample-rate` or `--frequencies` options.
Omitting `--output`, or giving `--output -`, emits JSON to stdout. Exit 0 means
the analog comparison passed, 1 means its comparison failed, and 2 indicates
invalid input or an I/O error. Python's standard library is sufficient.

Its default registry is resolved relative to the script. `--registry` still
requires the exact fixed v1 contract: the reader caps input at 64 KiB and rejects
duplicate keys, nonfinite values, missing/extra fields, changed graph/values and
false evidence claims. Both tools admit `--treble-ohms` and `--bass-ohms` in the
stated range; alternative resistors are not measured drivers. The reference's
file output atomically replaces an existing ordinary file after report creation,
requires an existing parent and refuses its own script or selected registry as
destination. Use fresh names outside source and installed payloads to retain
earlier evidence. An output file's existence alone does not establish a pass.

## 4. Run the affected acceptance gates

After the build above, run the native lifecycle/resource tests and independent
reference tests, then retain a fresh native/reference acceptance report:

```sh
ctest --test-dir build-crossover -C Release --output-on-failure \
  --no-tests=error \
  -R '^(test_leslie_crossover(_lifecycle|_allocation)?|python_test_crossover_reference)$'
cmake -E env "HAMMOND_CROSSOVER_ACCEPTANCE_REPORT=$hammond_reports/acceptance.json" \
  ctest --test-dir build-crossover -C Release --output-on-failure \
  --no-tests=error -R '^python_test_crossover_acceptance$'
```

CTest supplies `HAMMOND_CROSSOVER_PROBE_EXECUTABLE` using the selected built
target. For a direct invocation of the same acceptance script, use this
**alternative** to its CTest command:

```sh
cmake -E env "HAMMOND_CROSSOVER_PROBE_EXECUTABLE=$hammond_probe" \
  "HAMMOND_CROSSOVER_ACCEPTANCE_REPORT=$hammond_reports/acceptance.json" \
  python3 -B tests/test_crossover_acceptance.py
```

A missing probe is an error, not a skipped test. The report's parent must exist;
the report writer replaces an existing destination and can retain a failed run.
Preserve both its exit status/log and JSON. Use the separate
[installation acceptance](CROSSOVER_INSTALL.md#failure-boundary-and-acceptance)
when changing the component; it does not replace numerical acceptance.

| Gate | Meaningful checks |
| --- | --- |
| [Native author tests](../tests/test_leslie_crossover.cpp) | Independent impedance response, processed sine, exact partition agreement, transactional rejection, midpoint energy balance and ten-second nominal decay at all four rates |
| [Independent lifecycle](../tests/test_leslie_crossover_lifecycle.cpp) | All sixteen ordered rate pairs across seven resistor pairs; precharged charge/flux/energy checks; exact state/output preservation, boundaries, aliasing and overflow |
| [Allocation observer](../tests/test_leslie_crossover_allocation.cpp) | Calibrated global C++ allocation/deallocation calls on the observed thread, including first processing and rejecting paths; it does not measure arbitrary C/system allocation or callback deadlines |
| [Reference tests](../tests/test_crossover_reference.py) | Strict registry, separate reduced polynomials, port signs, DC/near-DC conditioning, ideal power balance and CLI/output behavior |
| [Native/reference acceptance](../tests/test_crossover_acceptance.py) | Four rates and six resistor pairs; actual recurrence and processed sine compared with independent nodal KCL; independently bounded settling and rejected CLI inputs |

### Read the report with its exact source identity

The native acceptance uses the trapezoidal mapping
`f_analog = fs/pi * tan(pi*f_digital/fs)`. It requires normalized complex error
`abs(actual-reference)/max(1,abs(reference)) <= 2e-10` for response and `2e-8`
for settled sine fits, separately for both V/V gains and A/V admittance.
Frequency response accepts finite `0 <= f < fs/2`, factors its own offline
recurrence solve, and leaves history unchanged. Its numerical residual is not a
physical error bound.

The [retained acceptance](development/2026-11-15-product-continuation/reports/crossover-response-acceptance.json)
and characterization distinguish this warped agreement from ordinary same-Hz
differences. For example, with nominal loads at 48 kHz/20 kHz, the retained bass
magnitude difference is **−18.201744 dB** relative to the already attenuated
analog bass port. The characterization includes absolute complex and phase
errors to interpret this result. No audible same-Hz threshold or physical pass
has been declared. Increasing the circuit's test rate is not itself a verified
oversampling pipeline.

Before accepting evidence, check the following identities and scopes:

- Probe JSON identifies schema 1, `leslie-crossover-public-api-probe-v1`, the
  model/realization, operation, rate and loads. It contains no source or binary
  digest. The acceptance harness checks these fields, requested observations,
  finite complex ports and duplicate/nonfinite JSON rejection.
- The analog report identifies `leslie-crossover-independent-analog-reference-v1`,
  raw and canonical registry SHA-256, reference source SHA-256 and experiment
  loads. Its recorded atlas hash is documentary provenance; the tool does not
  read or verify the PDF bytes.
- The acceptance report identifies `leslie-crossover-native-nodal-acceptance-v1`,
  the probe binary SHA-256 and six source hashes: probe, reference, acceptance
  script, public header, native implementation and registry. The harness checks
  these inputs again at teardown and fails if they changed. Require successful
  exit, `passed: true`, zero failures/errors and the complete expected test
  scope. Preserve original failed reports instead of replacing their history.
- Retain the actual commit or frozen source tree, worktree changes, compiler,
  CMake configuration, commands and logs with the report. These six hashes do
  not attest every linked core/build input or prove that the executable was
  compiled from the named source. Rebuild changed dependencies coherently before
  qualifying a new result.

For source identity, start with `git rev-parse HEAD 'HEAD^{tree}'` and
`git status --short`; a commit ID alone does not describe uncommitted code.
The characterization plotter refuses source mismatches in the retained report
and existing output paths. Its metadata and plotted checkpoints remain evidence
for those inputs, not a continuous error envelope or an additional native test.

## 5. Continue M6 through explicit gates

The next ordered work follows the
[characterization's numerical/physical gate](LESLIE_CROSSOVER_CHARACTERIZATION.md#next-numerical-and-physical-gates)
and the [whole-project dependency plan](PLAN.md):

1. **Freeze an electrical-accuracy protocol.** Name input reconstruction,
   external sample rates, frequency band, resistor/load family and signal
   boundaries. Predeclare magnitude/phase criteria above a stated gain floor,
   absolute complex criteria below it, and an independent admittance criterion.
   Select tolerances from intended use and evidence; keep a separate check grid
   and preserve the current same-Hz shortfall.
2. **Evaluate a separately identified numerical candidate.** Compare steady
   ports, precharged transients, stopped rate transitions, energy behavior and
   runtime cost. An increased circuit rate needs explicit reconstruction,
   conversion filters, latency and state semantics. A 44.1→176.4 kHz path is
   outside v1's admitted rates. Prewarping or another discretization needs its
   own reviewed realization identity; preserve the documentary L/C registry
   and the reproducible v1 baseline.
3. **Acquire the missing physical model inputs.** Independently transcribe the
   applicable primary drawing; identify the assembly/specimen and acquire
   component/loss values and complex driver impedances with uncertainty. Keep
   052803 and later 113860 context distinct. Retain null physical fields until
   evidence supports replacing them. Use the
   [acquisition sequence](CALIBRATION_NEXT_ACQUISITION.md) for capture ancestry
   and held-out evidence.
4. **Qualify the coupled M6 model.** Specify differential amplifier/transformer/
   crossover/driver ports, source/load feedback and ownership before evaluating
   loaded AC, polarity and nonlinear stability. Complete dry-organ validation
   precedes downstream cabinet fitting; M7 acoustic ownership, M8 calibration
   and runtime integration retain their separate acceptance requirements.

This workflow leaves the crossover independent of Engine. A numerical improvement,
install pass or software test result does not authorize a new live audio route.
