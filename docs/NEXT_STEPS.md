# Next steps

## Active new session

Follow the [pedal-session ledger](development/2026-11-13-pedals/README.md) and its actual worker states. The full atlas reread, prepared routing kernel and nominal pedal Engine/state/parameter integration are complete. The next concrete work is a separate typed pedal-note ownership adapter, a single-clock transaction merging manuals/pedals/controls, offline pedal score commands and versioned independent render evidence. Preserve the existing eight fixture inputs and compare their actual serialized output with the frozen baseline.

After that gate, add actual pedal diagnostics and enabled-path allocation checks, then implement the [minimal native VST3 contract](VST3_SPIKE_CONTRACT.md). Its pinned headless SDK machinery is available, but a plugin, automation bridge and race-free active state handoff require their own implementation and evidence. The requested session still comprises sixty actual new workers in ten waves; completed earlier sessions are not counted again.

## Completed continuation and current baseline

The [continuation ledger](development/2026-11-13-continuation/README.md) and
[actual-state manifest](development/2026-11-13-continuation/assignments.json)
record **60 completed distinct workers in ten waves of six**, with sixty retained
notes and no planned/running assignments. The original session's sixty remain
separate. Both explicit final record gates pass under
[CONTINUATION_CHECKS.md](CONTINUATION_CHECKS.md).

The implemented nominal console, typed input, phase-preserving rate lifecycle,
partial-key input, trace/plot tooling, 16-file offline install and retained demo
are ready for the next dependency-ready product task. The final reviews corrected
renderer stdout reporting, stale host/ownership instructions and Windows CRLF
handling in the accounting checker. Qualified code `7469ebf759ced820cc34fc9012beff6f772e4b89`
passes all 46 suites and 372 Python methods in every job of
[run 43380966473](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43380966473),
with zero failed/disabled/skipped tests. The
[final platform audit](reviews/FINAL_CONTINUATION_PLATFORM.md) retains full evidence
and the earlier failed run. Final Markdown/assignment result publication preserves
these code/test/data identities and requires observed remote/CI verification.

Preserve the original ideal-contact/percussion-off behavior as a compatibility
case. Subagents own scoped files and one evidence note; the integrator owns shared
handoff updates and publication. Follow [AGENTS.md](../AGENTS.md). There is no
remaining assignment from this sixty-worker session to invent or count again.

## Next product milestone

Complete the playable pedal input/evidence gate against [PEDAL_INTEGRATION_CONTRACT.md](PEDAL_INTEGRATION_CONTRACT.md). The prepared-kernel scope in [M3_NEXT_GATE.md](M3_NEXT_GATE.md) is now implemented and retained as its original acceptance contract. All new inputs must retain first-owner/final-release semantics, bounded whole-call rejection, source phase, separate pedal identity and stable ordering. A merged facade must render the elapsed frames once, including disconnected output. Extend the renderer and evidence verifier with explicit new versions; keep historical evidence replayable under its original grammar.

The following host checkpoint needs bounded sample-linear automation with the previous sample at -1, correct offset-N interpolation/carry, and a UI/audio state queue whose payload publication is actually race-free. Keep SDK allocation, file parsing and UI operations off the callback. Run the actual built Hammond module through the pinned SDK validator and an independent native harness before claiming that smoke gate.

Physical preset latches, switching bandwidth, continuous drawbars and loaded expression remain additional M3 gates. Do not create a second tone generator, infer physical pedal tuning from a software controller map, reuse manual contact timings for pedals, silently fill unknown reactor/mixture values, or change existing parameter/event/control identities.

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
