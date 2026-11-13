# Development status

Foundation session started 2026-11-12 (America/Halifax), baseline `501c68b`.
The [console continuation](development/2026-11-13-continuation/README.md) started
2026-11-13 (UTC) from `9c8068c`; its new assignments are counted separately.

**Original requested session complete:** all 60 distinct worker assignments in
ten waves of six have finished. The [execution ledger](development/AGENT_LEDGER.md)
records every actual scope, outcome and limitation; the separate continuation's
workers are excluded. The final session record follows the qualified code/demo
checkpoint `61c6ecb`. Current product work continues at the scoped stage below.

## Current stage

The M0 engineering foundation and a scoped M1/M2 nominal dry engine are implemented.
The engine owns 91 shared sine sources, explicit manual routing, independent contacts,
manual drawbars and a linear expression surrogate. It consumes bounded sample-offset
events with atomic rejection, stable ties, zero-frame flushes and an independent
64-bit render clock. Source phase continues through silence and disconnected output.

The offline renderer writes actual stereo PCM16 WAV files, reports signal metrics,
subdivides dense event blocks and publishes without overwriting existing files.
Independent profile, generator, scheduler and renderer tests passed their assigned
Debug/Release scopes. Source pitch, coherent foldback, same-build block partition
identity and malformed-input behavior have retained software evidence.

M3 remains a partial nominal implementation. It includes four retained A/B banks,
hidden-bank edits, routing-only Cancel/reselect, 1,098 independent contacts and one
shared upper-B percussion readiness state. The optional linear-travel model has
separate make/break thresholds, partial-target support in ContactBank, incomplete
return and hysteresis. Its proposed times and thresholds are unmeasured. Percussion
uses the physical ninth contact detector, second/third harmonic routing, retained
normal/soft and slow/fast controls, finite recovery and upper-only one-foot masking.
Ideal contacts and percussion off preserve original renderer defaults.

Control serialization writes `B3CONTROLS2` and migrates `B3CONTROLS1` with percussion
Off/Second/Normal/Slow. It preserves 43 controls plus route-enable bits, excluding
key ownership, trajectories, readiness, source phases and time. All 39 earlier
registry records are unchanged; four new IDs append percussion controls. These
are proposed identities, without actual VST3 exports.

The typed host-input foundation now has a fixed 256-owner adapter with stable
channel/note-ID handling, FIFO anonymous releases and retained original manual
routing. The transactional facade commits ownership only after Engine accepts
its physical events. A native bridge maps all 43 normalized internal controls to
fixed Engine targets, including exact half-step boundaries under all four standard
rounding modes. JSON parsing stays outside processing. Native host exports, MIDI
byte decoding, automation curves, device operation and deadlines remain separate.
The native-input checkpoint `093d985` passed all 34 local Release suites on its
exact staged tree. Hosted [run 43371559575](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43371559575)
passed Linux GCC, macOS AppleClang and Windows MSVC Release plus Linux
ASan/UBSan with leak checking.

The [sample-rate lifecycle](SAMPLE_RATE_LIFECYCLE.md) now provides an explicit
stopped/same-thread transaction between 44.1, 48 and 96 kHz when the owned profile
supports the target rate. It preserves phases, contact position and hysteresis,
readiness, held targets, controls and frame count. Same-rate requests are exact
no-ops; rejected changes preserve state and future output. Mixed-rate elapsed
seconds require the caller's rate schedule. This core API provides no native
host/device transition or concurrent publication protocol. Its combined clean
Release archive passed all 39 CTest suites; the continuation ledger retains the
tested tree and tracks publication and hosted qualification separately.

Pedal mapping data contains 195 connections and five explicit disconnections;
runtime pedal audio remains open. Physical preset latching, continuous drawbar
travel, contact bounce/antialiasing, loaded expression, scanner, AO-28, Leslie DSP,
VST3, audio-device standalone and native UI remain unimplemented. Full M0 specimen
lock, factory gearing, source calibration and measured instrument fidelity remain
open despite the working nominal implementation.

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

The historical `7c2ad20` checkpoint exposed a Windows repository-diagnostic path
mismatch and a Linux sanitizer render-evidence mutation-test failure. The repairs
were incorporated in `6c3dd8b`; its hosted matrix passed. The
[CI audit](CI_QUALIFICATION.md) retains the earlier failure evidence.

The contact/percussion module checkpoint `7a24a30` passed all **24/24** suites in
a clean archive of its exact staged source tree. Hosted
[run 43366836424](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43366836424)
passed Linux GCC, macOS AppleClang, Windows MSVC Release, and Linux ASan/UBSan with
leak checking. This qualification predates the subsequent Engine/CLI integration.
The continuation ledger records the next checkpoint's complete checks separately;
focused integration tests alone do not establish a new full-matrix pass.

The new [OfflineTools local install](OFFLINE_INSTALL.md) passed actual installation,
relocation and same-build PCM identity checks on Linux. It consumes explicit
installed profile/event paths and rejects a missing profile. macOS/Windows install
qualification passed in the subsequent hosted integration. Later tool additions
require their own install/relocation checks.

The [factory runtime acceptance](FACTORY_RUNTIME_ACCEPTANCE.md), retained
[four-second demo](../examples/rendered/nominal-two-manual-v1/README.md),
[independent local replay](DEMO_REPLAY.md) and final persistence/evidence repairs
are now published in `61c6ecb`. Its exact clean staged source passed all 26
Release suites and 274 Python methods with zero skips. The route gate exercises
all 1,098 key/drawbar routes across both manuals with CSV-selected expected
sources. Their hosted gates passed in run 43368537860, independently audited in
the [final platform review](reviews/FINAL_PLATFORM_REVIEW.md). None establishes
physical fidelity. Those historical results predate this continuation's Engine/CLI extension.

The console integration `4ead769` passed **30/30** local Release suites on its
exact published tree. Hosted run 43369940466 passed Linux Release and sanitizer
checks; Windows and macOS each passed 29/30, failing the same producer test's
unresolved-versus-canonical temporary-path comparison. The
[CI repair review](reviews/CONSOLE_CI_REPAIR.md) retains the observed cause and
portable regression. All 28 producer methods pass locally after the test repair;
hosted [run 43370542634](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43370542634)
subsequently passed all four jobs at repair commit `72b5062`, including Linux
ASan/UBSan with leak checking. This closes that observed portability failure.

The callback audit observed zero C++ allocation/deallocation
calls in 96 recorded processing calls, including maximum and rejected requests.
Its static call-graph scope and limits are in [REALTIME.md](REALTIME.md). The
independent bundle verifier passed 34 test methods, including real render bundles
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
