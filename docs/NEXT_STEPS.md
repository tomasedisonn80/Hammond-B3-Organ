# Next steps

## Active continuation

Read the [current session ledger](development/2026-11-13-continuation/README.md)
for the sixty new assignments in ten waves. The earlier session completed all
sixty original assignments at `7bbd8e7`; its assignments,
source reviews and evidence remain intact and are not counted again.

The nominal console, typed input and sample-rate lifecycle checkpoints are
published. `9a5c99a` passes all 43 local Release suites and all four hosted jobs.
Wave 08 is published as `2046b93`, with all 45 local suites and all four hosted
jobs passing. Wave 09 retains the current-model demo, precise next M3 gate,
developer handoff, compatibility review and separate assignment accounting.
Preserve the original ideal/off audio as a compatibility case.
Publication requires a clean staged source build, applicable tests, an
expected-head push and observed CI.
The corrected combined candidate is published as `6bdce06`. Its 46-suite local
Release gate and 371 Python methods passed. Hosted Linux/macOS/sanitizer jobs
passed, while Windows exposed CRLF handling in the new accounting checker. That
issue is now corrected and all 13 accounting methods pass locally; qualify the
repaired archive and observe its new hosted run before final completion. All
sixty workers are dispatched; 58 are complete and two final reviews are running.

The remaining session work is the six independent wave-10 reviews: runtime,
input/persistence, offline evidence, handoff/atlas alignment, platform qualification,
and final publication/accounting. Record actual dispatch and completion in the
[separate manifest](development/2026-11-13-continuation/assignments.json), retain
all findings, fix observed defects, and run the
[explicit final continuation gate](CONTINUATION_CHECKS.md) before claiming all
sixty new assignments complete. The completed enabled-path, install and demo
work does not need to be repeated merely to close another wave.

Subagents own scoped files and one evidence note. The integrator owns shared
status/next-step/log updates, integration and publication. Follow `AGENTS.md`.

## Next product milestone

Implement the first checkpoint in [M3_NEXT_GATE.md](M3_NEXT_GATE.md): a prepared
pedal routing/reference kernel consuming the current 91-source frame and returning
four normalized bus excitations. The first concrete change is a typed pedal
runtime contract plus an executable admission fixture for the existing 25-by-8
map, preserving every position and explicit disconnection. The plan names the
files/APIs to create, ordered steps, independent CSV comparisons, phase/atomicity/
allocation gates, and the later playable-integration boundary.

Use [CONTINUATION_HANDOFF.md](CONTINUATION_HANDOFF.md) for a current coherent
checkout and tool commands. Do not create a second tone generator, infer a pedal
MIDI octave, reuse manual contact timings, silently fill unknown reactor/mixture
values, or change existing parameter/event/control identities. Physical preset
latches, switching bandwidth, continuous drawbars and loaded expression remain
additional M3 gates.

## Acquisition work that can proceed in parallel

Use [CAPTURE_PROTOCOL.md](CAPTURE_PROTOCOL.md) and its planned metadata example:

1. Identify the organ/generator, AO-28 revision, cabinet model/revision, condition,
   modifications and measurement permissions. Keep missing fields explicitly unknown.
2. Retain the completed [factory routing comparison](FACTORY_REFERENCE.md), then
   acquire calibrated source, contact, percussion and expression evidence at named
   boundaries. Documentary wiring agreement is separate from actual specimen tuning,
   waveform/level/phase and loading measurements.
3. Record units, loading, raw digital rate versus physical clock, calibration,
   uncertainty, rights and raw/derived ancestry. Admit real captures with the stated
   physical checks; a metadata or byte-hash pass cannot perform that admission.
4. Keep whole takes and related channels/derivatives together. Maintain an external
   corpus ledger for fitting, validation and untouched final holdouts; the per-file
   validator does not establish corpus-wide independence.

M4 scanner, M5 AO-28, M6 Leslie electronics and M7 rotary acoustics retain the
specific source/topology/acquisition dependencies in [PLAN.md](PLAN.md). Native
VST3/device audio, accessible UI, platform distribution and rights are separate
M9 gates. The [host proposal](HOST_INTEGRATION.md) supplies unrun adapter criteria,
not an implemented plugin or device application.

## Required handoff for every future agent

Follow [AGENTS.md](../AGENTS.md): inspect current code and both session ledgers,
select dependency-ready work, state its evidence boundary, execute the necessary
checks, update status/next steps/log and affected contracts, then commit and push
completed authorized work. Preserve others' commits, use an expected-head guard,
and observe the actual remote result. Retain failures and unrun gates. Workers
report to the integrator; they do not compete to rewrite shared status documents.
