# Next steps

## Active new session

Follow the [pedal-session ledger](development/2026-11-13-pedals/README.md) and its actual worker states. Four waves and 24 actual new workers are complete: full atlas review, prepared routing, nominal Engine/state/parameter integration, bounded pedal ownership, one combined input transaction, offline score commands and schema-3 evidence. All eight retained scores have exact local baseline/current WAV compatibility.

Wave 5 adds same-frame diagnostics, compiled pedal model metadata, independently checked musical fixtures, sample-linear automation and a bounded race-free UI/audio state handoff. The host contract requires the previous-sample anchor at -1, correct offset-N interpolation/carry, stable event ordering, candidate rendering with whole-callback rollback, and state 1/2/3 loading during active processing. Enabled-path allocation instrumentation must cover these actual paths.

Wave 6 then implements and independently qualifies the [minimal native VST3 contract](VST3_SPIKE_CONTRACT.md). Use the pinned SDK and existing core; leave ordinary builds SDK-free. Later waves cover workload/package compatibility, retained audio, operational handoff, platform qualification and final audits. The requested session still requires sixty actual new workers in ten waves. Earlier completed sessions are not counted again.

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

Implement the host timeline and state-handoff foundations against [VST3_SPIKE_CONTRACT.md](VST3_SPIKE_CONTRACT.md), using the now implemented [PERFORMANCE_INPUT.md](PERFORMANCE_INPUT.md). The unified facade provides one atomic call; a multi-slice wrapper must encompass all slices, owners, pending state, curve anchors, boundary carry and caller output in one callback transaction. Slice lengths must sum to the original frame count. Parse files and construct SDK objects off the audio callback.

Build the actual Hammond module with its frozen UUIDs, three native event buses, forty-five existing parameter identities and generic host controls. Verify the exact module with the pinned SDK validator and an independent ABI harness; SDK selftests alone are insufficient. Test lifecycle, phase-preserving rate changes, connected/disconnected buffers, active state migration and callback allocation behavior. A native smoke gate remains distinct from actual DAW/device use, signed distribution and the custom interface.

Physical preset latches, switching bandwidth, continuous drawbars and loaded expression remain additional M3 gates. The selected pedal matrix/gain are explicit nominal fixtures; the documentary 25-by-8 routing evidence does not establish reactor loading, physical tuning or measured timbre. Keep every existing parameter/event/control identity and original fixture unchanged.

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
