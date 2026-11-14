# A52 — bounded native input and acknowledged startup baseline

Actual assignment **52/60**, logical wave **9**, worker
`/root/w09_a52_bounded_native_burst`, 14 November 2026.

## Ownership and outcome

Initially owned the bounded-input review, this note and `reports/a52-*`. After
A49's complete serial gate finished 146/147, root assigned the concrete
workspace replay startup-baseline failure and released CPU. Root later expanded
ownership only to the shared MIDI helper's zero-packet timestamp branch.
Read AGENTS, the current session/checkpoint, complete M0–M9 plan, workspace
contract, replay grammar and implementation, and A21/A37/A46 source-identified
native ownership, operator and gallery evidence before preparing the scenario.

**Completed:** corrected workspace suite **6/6 methods, 16/16 native processes**;
the original A49 trace passes the repaired complete method with a separately
observed startup prefix; seven meaningful corrupted traces fail; one native
**256-action** burst passes. The [review](../../reviews/INTERFACE_BOUNDED_INPUT.md)
and [final result](reports/a52-final-result.json) give commands, exact identities,
scope and retained failures.

Changed only these two test sources plus assigned evidence:

- `apps/standalone/native_tests/test_standalone_workspace_replay.py`: complete
  the original pre-note UI/MIDI startup prefix for 250 ms, require its exact
  pre-shutdown acknowledgment, then use that measured sequence for the unchanged
  full journey's +10 command delta. Original script timing, holds, packet counts,
  view/state assertions and timeouts remain.
- `apps/standalone/native_tests/test_standalone_midi_replay.py`: a zero-offered-
  packet replay requires timestamp exactly zero; any offered packet retains the
  existing positive timestamp assertion and all other transport checks.

No product, parameter/state/model, CMake, timeout, README, build or index change.
Root owns shared status, integration, commit and publication.

## Exact source and preserved failure

Executable SHA-256 is
`bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2`,
using the existing `../a36-status-bin/hammond_standalone`. All 98 product entries
match the actual current files and committed blobs at `8673713` and `cdbb2be`;
all 96 applicable A36 build inputs also match. Before/after product, executable
and phase-specific helper/fixture identities are unchanged. No shared build was
accessed or rebuilt. Source/test overlay identities are explicit in each report.

A49's 191 ms first trace row had applied/resolved 3 and submitted 4. It could not
satisfy a `<180 ms` pre-action assumption. Its original log, JUnit, UI/MIDI inputs
and diagnostics remain unchanged. A52's first authoring attempt also remains:
five methods passed; its valid connect-only prefix was rejected by the old
shared timestamp assertion. All 15 applications exited zero, but that suite
failed and did not reach the original combined journey. The diagnosed correction
and one explicitly authorized fresh full-suite run are recorded separately.

The corrected suite completed in 40.346 s. The one burst completed in 5.511 s:
256 actions, 5,673 bytes, 121 intended F4–F7 activations including 228 equal-time
records, three On/three Off and exactly six post-startup Session commands. It
preserves Upper 60 / Lower 62, proves remembered Lower C4 through Space, then
acknowledges the original modified-key releases before clean shutdown. All
controls and state bytes stay exact. A52 launched 32 applications total across
both documented suite attempts and the one burst; no application failed.

## Reproduction and handoff

Use the review's `a52-qualification.py` commands with fresh repository-local
`reports/a52-*` paths, the pinned executable and retained A36/A46/A49 evidence.
The `suite`, `retained` and `burst` phases run serially. The retained phase
launches no native process. Original 9-second child / 90-second suite limits and
the product's 2-second replay drain remain unchanged; burst has a 20-second cap.

Explicit dummy SDL audio/video is used throughout. Synthetic MIDI in the
existing suite opens no native port or discovery operation; the burst uses MIDI
source `none`. No burst pointer, screenshot or giant surface is involved. Dummy
capture failure does not qualify persistent OS capture. RSS/time are single-run
observations, with no performance, deadline, leak, display, accessibility,
host, acoustic or specimen-fidelity claim.

CPU was released immediately after the burst. Root should review and integrate
the exact fixture diff and focused evidence while preserving both original
failures. The 146/147 full gate is not relabeled 147/147. A57's display/pointer
qualification, final source publication/accounting and the full M0–M9 plan keep
their separate next actions. No further native execution is requested by A52.
