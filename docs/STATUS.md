# Development status

Session started 2026-11-12 (America/Halifax). Baseline: `501c68b`.

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
and five explicit disconnections; it is not connected to runtime pedal audio. No scanner, AO-28,
Leslie DSP, physical contact model, percussion, pedal audio, VST3, audio-device
standalone application or native UI is implemented at this checkpoint. No measured
instrument-fidelity claim is made. Full M0 specimen lock and factory M2 evidence
remain open despite the useful nominal engineering implementation.

## Reproducible software evidence

Five versioned musical/event fixtures cover both manuals, nominal A4, low/high
coherent foldback, and held-note bank/Cancel transitions. All five passed their
assigned actual-render checks with no reported clipping. A reproducible wrapper
retains input/compiled/WAV hashes, raw logs, actual float metrics and separate PCM
statistics. An independent PCM analyzer provides bounded window measurements and
qualified crossing-rate estimates. None authenticates a physical instrument.

The CI workflow defines Linux/macOS/Windows Release jobs and a Linux sanitizer
job with leak checking enabled. Hosted execution is pending at this checkpoint;
local results do not qualify unrun platforms. Callback allocation checks and an
independent evidence-bundle verifier are the remaining wave-05 work.

## Evidence boundary

- All 500 source pages were read across six complete page-range assignments;
  their notes retain coverage and visual checks.
- Companion JSON, reference code, source catalogs, original verification outputs
  and measured captures referenced by the atlas are absent from the baseline.
- Reconstruction from PDF formulas/printed tables is labeled as such.
- Specimen identity, AO-28 revision, tuning/phase/pickup calibration, contact and
  circuit response, Leslie measurements and host qualification remain open.

See [PLAN.md](PLAN.md), [IMPLEMENTATION_CONTRACT.md](IMPLEMENTATION_CONTRACT.md),
[DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) and [NEXT_STEPS.md](NEXT_STEPS.md).
