# A22 — Independent workspace replay repair review

Assignment: A22, wave 4 of the waveform continuation's sixty actual assignments.
Agent: `/root/w04_a22_replay_fix_review`. Date: 14 November 2026.

## Owned deliverables and outcome

Owned [the independent review](../../../reviews/WAVEFORM_REPLAY_FIX.md), this
note and, with root's explicit coordination, the
[per-case admission report](../reports/a22-replay-evidence-review.json).
**Accepted:** the fixture-only 600 ms observation dwell addresses the retained
initial-Play observation failure without dropping or weakening its behavioral
gate. All thirty retained successful cases pass offline admission through the
unchanged six method bodies. A22 launched zero native processes, builds or
CTests and changed no product/test/shared-status/manifest files.

The observed failure is precise: the original 320 ms Space press precedes
500 ms navigation by only 180 ms. At reference size, the copied state at 426 ms
has sequence 5 submitted but only 4 applied; the first observed applied sequence
5 and both held notes appear at 527 ms in Rotary. The first Play visit therefore
lacks required `(1,1,0)`. This is a sampled observation, not the exact callback
application time. Current unchanged `assert_views` still rejects the original
diagnostics with that same missing-initial-Play message.

## Actual work and validation

Read `AGENTS.md`, the complete M0–M9 plan, session scope/checkpoint/assignment,
current status and relevant atlas/evidence boundaries. Inspected the complete
workspace fixture, its common schema/lifecycle helpers, original failure log
and diagnostics, actual four-hunk diff, root's repair record, targeted raw log,
A18's timing report and every retained case. Root owns publication and shared
status; this review did not inspect or change Git status or the manifest.

Executed from `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ`:

```sh
PYTHONDONTWRITEBYTECODE=1 python /workspace/scratch/e3cacb90cc81/a22-replay-review.py
```

This temporary review driver replaces the native invocation with read-only
retained-case admission. It compares exact generated UI/MIDI bytes, process
arguments, input/output controls and recorded process results; invokes the
strict original diagnostic validators and unchanged test method assertions;
and records all source/evidence identities in the durable JSON. It does not
recreate missing process output or screenshot pixels. The original and current
schedules are enumerated separately in memory against retained data solely to
compare their requested events; this is not a rerun of the old native schedule.

Results:

- Reverse-applied the exact four-hunk patch and matched the original fixture
  hash. All 132 assertion-call ASTs and six test methods remain unchanged.
- Enumerated all thirty original/current requests: 23 identical and seven
  complete header journeys changed only by the intended timing transformation.
  Each complete script retains 24 commands in the same order: six early events
  unchanged, eighteen later events shifted exactly 600 ms. Startup/Upper-only
  durations, all coordinates/options and the 9.0-second process timeout remain.
- Admitted all 122 files across thirty cases: 21 header, four hidden-control,
  two MIDI/UI, one focus-memory and two capture-refusal cases. Every common
  schema/lifecycle and retained per-method gate passes. The executable hash is
  identical across all process records, initial failure output, targeted output
  and the currently retained binary, and remains unchanged during review.
- All seven header Save outputs equal the canonical fixed-state bytes; the
  fourteen short prefixes retain exactly their noncanonical input bytes. All six
  painted visits retain both original held targets; exact 2 On / 2 Off and +4
  command growth, original releases and capture refusals remain required.
- Native elapsed times in the retained records are 0.326539–3.851062 seconds.
  The seven repaired first-both-to-Rotary observed gaps are 677–770 ms; reference
  size is 432 ms first both-held paint, 1109 ms first Rotary paint.

## Identities and separate execution results

Original fixture SHA-256:
`28b61802b99233e5f7ee14d01f5456b15bdff235309038b2943e75863d6097f7`.
Reviewed fixture SHA-256:
`9a226a6b17b1d7eb84a079a113f5ef97a6f37935ba16d1d3f55876bed907d6f3`.
Actual executable SHA-256:
`677acfa6a0244d3f7085eb96fa0737306a9f9e74febabb34f55fea99b303c51c`
(3,628,544 bytes). Aggregate of all 122 retained case-file identities:
`6ef5733eae159768c0347af2288b6796341b8a56fb1506355d4ce6694850270b`.
Retained targeted raw LastTest log SHA-256:
`9d22f530fd6d9fb99e23f486a4f2f5ae7498956ce6da94cc40425aeb00b5d66a`.
The report records source-helper hashes, each case-file hash and the temporary
review driver's identity; these qualify the inspected bytes without pretending
an uncommitted worktree already has a published frozen-tree identity.

The root's original full suite is **160/161 in 226.45 seconds**. The subsequent
targeted result is **2/2 in 48.92 seconds**, including workspace replay in
48.91 seconds and the final A17 streaming-path gate. The raw workspace log
records six methods and thirty actual native processes in 48.829 seconds.
A22's offline admission is a third, explicitly separate check. None is combined
into an invented final full-suite pass. Root's earlier private-include build
failure/repair remains an unrelated setup event.

## Concrete handoff and limits

Root can accept this bounded fixture repair and preserve its review/report with
the exact diff. The next required evidence is a final frozen-source full build
and CTest, followed by actual hosted platform results. Retain all failures and
these distinct successes. The fixed dwell is not an acknowledgment barrier or a
portable worst-case latency proof; finite later intervals and 250 ms prefixes
can still be sensitive to a sufficiently slow runner. Temporary screenshot BMPs
cannot be re-decoded from their retained metadata. Dummy drivers do not qualify
physical devices, OS capture, image equality or real-time deadlines. R4, R5/R6
and measured cabinet fidelity remain separate gates.
