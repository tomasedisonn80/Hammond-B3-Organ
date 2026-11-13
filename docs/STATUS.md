# Development status

Session started 2026-11-12 (America/Halifax). Baseline: `501c68b`.

**Original requested session complete:** all 60 distinct worker assignments in
ten waves of six have finished. The [execution ledger](development/AGENT_LEDGER.md)
records every actual scope, outcome and limitation; the separate continuation's
workers are excluded. The final session record follows the qualified code/demo
checkpoint `61c6ecb`. Current product work continues at the scoped stage below.

## Current stage

The M0 engineering foundation and a scoped M1/M2 nominal dry engine are implemented.
The engine owns 91 shared sine sources, explicit manual routing, ideal key gates,
manual drawbars and a linear expression surrogate. It consumes bounded sample-offset
events with atomic rejection, stable ties, zero-frame flushes and an independent
64-bit render clock. Source phase continues through silence and disconnected output.

The offline renderer writes actual stereo PCM16 WAV files, reports signal metrics,
subdivides dense event blocks and publishes without overwriting existing files.
Independent profile, generator, scheduler and renderer tests passed their assigned
Debug/Release scopes. Source pitch, coherent foldback, same-build block partition
identity and malformed-input behavior have retained software evidence.

Early M3 console behavior is implemented: four retained A/B banks, direct hidden
bank edits, routing-only Cancel/reselect and validated control snapshots. Control
serialization preserves all 39 controls plus route-enable bits; it excludes keys,
source phases and time. The internal parameter registry has 39 proposed identities,
without claiming actual VST3 exports. Pedal mapping data contains 195 connections
and five explicit disconnections; it is not connected to runtime pedal audio.

The preserved continuation commit `7a24a30` adds separately tested nominal
`ContactBank` and shared `PercussionState` components, a `ConsoleModel` contract
and the `hammond_model_info` diagnostic. Their identities, proposed parameters and
limits are in [console dynamics](CONSOLE_DYNAMICS.md) and
[model metadata](MODEL_METADATA.md). They are not yet connected to `Engine` or
the renderer at that commit; rendered audio still uses ideal manual key gates.
No scanner, AO-28, Leslie DSP, pedal audio, VST3, audio-device
standalone application or native UI is implemented at this checkpoint. No measured
instrument-fidelity claim is made. Full M0 specimen lock, factory gearing and
source calibration remain open despite the useful nominal implementation.

Two independently frozen factory Table III transcriptions now agree with all
549 manual assignments and all 200 pedal positions in the existing data. The
[factory comparison](FACTORY_REFERENCE.md) records the exact source, page locators,
hashes and five disconnections. This later documentary attestation leaves the
original nominal profile identity and its original authoring provenance unchanged.

The proposed [capture contract](CAPTURE_FORMAT.md) and validator distinguish
planned work, declared recorded metadata and optional artifact-byte verification.
The committed example is a plan with no invented specimen, recording, timestamp
or calibration. Its 41-method software suite passes locally and in the hosted
matrix at `6c3dd8b`. Actual acquisitions,
physical admission and corpus-wide holdout independence remain open.
The [acquisition protocol](CAPTURE_PROTOCOL.md) provides prioritized dry-organ
tasks, explicit evidence gates and whole-take holdout grouping for that work.

## Reproducible software evidence

Five versioned musical/event fixtures cover both manuals, nominal A4, low/high
coherent foldback, and held-note bank/Cancel transitions. All five passed their
assigned actual-render checks with no reported clipping. A reproducible wrapper
retains input/compiled/WAV hashes, raw logs, actual float metrics and separate PCM
statistics. An independent PCM analyzer provides bounded window measurements and
qualified crossing-rate estimates. None authenticates a physical instrument.

[Hosted CI run 43368537860](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43368537860)
passed all 26 CTest suites at `61c6ecb` on Linux GCC, macOS AppleClang and Windows
MSVC Release, plus Linux ASan/UBSan with leak detection enabled. Each complete
diagnostic archive contains 274 Python methods and zero test skips. Qualification
applies to this offline software and those runners; native audio-device and
plugin-host gates remain open.

The [CI audit](CI_QUALIFICATION.md) preserves the earlier failures and subsequent
repairs, including the repository diagnostic path mismatch and executable-mutation
test at `7c2ad20`. The original mutation exception remains unestablished; its
replacement still requires a successful renderer and the exact integrity failure.

The [OfflineTools local install](OFFLINE_INSTALL.md) passed actual installation,
relocation and same-build PCM identity checks in that hosted matrix. It consumes
explicit installed profile/event paths and rejects a missing profile.

The [factory runtime acceptance](FACTORY_RUNTIME_ACCEPTANCE.md), retained
[four-second demo](../examples/rendered/nominal-two-manual-v1/README.md),
[independent local replay](DEMO_REPLAY.md) and final persistence/evidence repairs
are now published in `61c6ecb`. Its exact clean staged source passed all 26
Release suites and 274 Python methods with zero skips. The route gate exercises
all 1,098 key/drawbar routes across both manuals with CSV-selected expected
sources. Their hosted gates passed in run 43368537860, independently audited in
the [final platform review](reviews/FINAL_PLATFORM_REVIEW.md). None establishes
physical fidelity or makes the nominal components integrated audio behavior.

The callback audit observed zero C++ allocation/deallocation
calls in 96 recorded processing calls, including maximum and rejected requests.
Its static call-graph scope and limits are in [REALTIME.md](REALTIME.md). The
independent bundle verifier passed 27 test methods, including real render bundles
and mutated evidence. It reports retained-bundle integrity separately from
unestablished authenticity, build provenance and physical fidelity.

Preparation also rejects increments too small to advance the binary64 source
phase reliably. [Numerical bounds](NUMERICAL_BOUNDS.md) record the exact support
floor, atomic rejection and bounded nominal drift checks. The
[benchmark](BENCHMARKING.md) reports observed processing intervals without a timing
pass threshold. The [repository checker](REPOSITORY_CHECKS.md) verifies retained
source/index/link/data identities and supports an explicit final agent count.

## Evidence boundary

The separate [console continuation](development/2026-11-13-continuation/README.md)
is actively integrating M3. Its review, standing instructions and independently
tested model modules were preserved in this session's history. Inspect its newest
code and ledger before starting overlapping integration work. The original
[assignment ledger](development/AGENT_LEDGER.md), [acceptance matrix](ACCEPTANCE_MATRIX.md)
and [operational handoff](SESSION_HANDOFF.md) retain session-specific evidence.

- All 500 source pages were read across six complete page-range assignments;
  their notes retain coverage and visual checks.
- Companion JSON, reference code, source catalogs, original verification outputs
  and measured captures referenced by the atlas are absent from the baseline.
- Reconstruction from PDF formulas/printed tables is labeled as such.
- Specimen identity, AO-28 revision, tuning/phase/pickup calibration, contact and
  circuit response, Leslie measurements and host qualification remain open.

See [PLAN.md](PLAN.md), [IMPLEMENTATION_CONTRACT.md](IMPLEMENTATION_CONTRACT.md),
[DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) and [NEXT_STEPS.md](NEXT_STEPS.md).
