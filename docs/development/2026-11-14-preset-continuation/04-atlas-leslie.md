# A04: complete atlas reading, pages 253-336

## Assignment, source and actual coverage

- Session: `2026-11-14-preset-continuation`, wave 1, assignment A04.
- Actual worker: `/root/w01_a04_atlas_leslie`.
- Inspected repository HEAD: `b79086f6bb0c42b97130c721c5c73c7c97a13887`.
- Source: [unchanged 500-page atlas](../../../Hammond_B3_Leslie_Research_Atlas_500pp.pdf), 21,248,265 bytes.
- PDF SHA-256: `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Complete text coverage: **all 84 pages, 253 through 336 inclusive**, chapters 041-054. This is not a keyword-only review.
- `pdftotext` version: Poppler **25.03.0**. The complete default-order extraction of this range is 189,102 bytes, 26,060 whitespace-separated words and 84 form feeds; SHA-256 `63d8845e2bcca69b3c51a322d5cdaa053dec3e1b9eee63070185efa30598a978`.
- Actual original-page visual inspection: **272, 278, 322 and 326**, rendered with `pdftoppm -singlefile -scale-to 1600 -png` and inspected as images.

The complete text was read in bounded ranges: 253-266, 267-278, 279-290,
291-302, 303-314, 315-326 and 327-336. The first combined tool display was
truncated; pages 254-259 were reread separately before counting coverage. The
source PDF was not edited. Rendered page images are temporary review aids, not
new reference measurements or application screenshots.

Read `AGENTS.md`, the [project plan](../../PLAN.md), the existing
[rotary scope](../../ROTARY_SCOPE.md), the current status/next-step entries and
the latest development-log entry. Inspected the current Engine's source-clock,
control-restore and percussion ownership locations. The current worktree's new
session notes were preserved; this assignment owns only this report.

## Complete chapter coverage and implications

| Chapter / pages | Complete reading finding | Consequence for this continuation |
|---|---|---|
| 041 / 253-258 | The selected vintage 122 reference is the 1971 036616 amplifier. Audio, the one-leg control detector, shared bias and mechanical motion are separate coupled responsibilities. Full differential volts differ from per-leg volts. | A new organ registration is not a 122 electrical-profile selection. Keep the current dry output and all electrical calibration limits explicit. |
| 042 / 259-264 | The 147 has its own single-ended input/loading and winding-feedback topology; the older and 1979 drawings remain separate evidence sets. Imported profiles retain revision and parameter hash. | Do not introduce a generic 122/147 brightness switch or silently replace an existing profile on save/load. |
| 043 / 265-270 | The 6550 stage, transformer, reactive load, bias, screen demand and supply form a coupled network. Numerical agreement, physical electrical agreement and listening evidence are separate gates. | Nominal preset taps cannot establish calibrated output voltage, overdrive, power-stage fidelity or speaker loading. |
| 044 / 271-276 | The four documented crossover values belong to a particular floating-treble topology and combined amplifier load. Ideal 16-ohm calculations are mathematical fixtures, not measured driver/cabinet responses. | Leave electrical crossover integration outside this M3 selector. Do not substitute an arbitrary 800 Hz split or infer a loaded gain law from the catalog. |
| 045 / 277-282 | A stationary compression driver feeds one rotating horn mouth; the opposite horn is a counterbalance. One mechanical trajectory drives all receivers. Source photographs and Leslie 600 measurements are not selected-122 calibration. | Preserve separate visual, geometric and acoustic evidence. A cabinet image cannot make a dry preset acoustically connected. |
| 046 / 283-288 | The lower loudspeaker is fixed while the deflector rotates. Complex angular filtering, delay and interference need distinct ownership. A stopped angle still emits bass. | Do not use organ-preset changes as motion resets or infer drum behavior from an independent tremolo. |
| 047 / 289-294 | Horn and drum have independent drives, profiles and continuous phase/speed. Slow/Fast is the vintage baseline; coast/brake requires a named extension. The 5-8 second bass service observation is not a universal time constant. | Selection must not create motion, stopping or speed parameters that the present engine does not implement. |
| 048 / 295-300 | Visible cabinet appearance is separate from measured hidden geometry. Cabinet, panel, room and driver effects need one owner each; intact and altered-panel captures are different profiles. | UI refinement can proceed without claiming acoustic geometry or specimen matching. Keep existing unconnected-cabinet status visible. |
| 049 / 301-306 | Retarded emission time, historical angles, causal interpolation support, bandwidth and declared algorithmic latency are required for a moving-path renderer. Printed source formulas/listings contain identified sign and interpolation issues. | A control event must not erase histories or bypass the independently owned rotary numerical work. Atlas-reported companion checks are not executed repository results. |
| 050 / 307-312 | Directivity is a complex, boundary-qualified response. Shared geometry sets delay and amplitude, fixed cabinet responses cannot simply rotate, and per-angle normalization erases real modulation. | Never normalize or recolor the organ merely to make a preset resemble an uncalibrated cabinet picture or example recording. |
| 051 / 313-318 | A microphone scene has separate identity, timing, polarity and geometry. Stereo channels share physical source/motion states; mono fold-down and a one-microphone scene are distinct outputs. | Adding registration controls must not alter stereo/dry routing or invent microphone coloration. Future scene state requires its own explicit identity. |
| 052 / 319-324 | The engine owns persistent independent rotor histories. UI snapshots cannot advance the audio clock. Notes, editor closure and repeated unchanged commands do not restart motion; ordinary presets differ from full offline checkpoints. | Preserve existing phase, contact/readiness histories, note owners and clock on selection and control restore. Store musical selection, not DSP history. |
| 053 / 325-330 | Input-time and observation-time angular weights define different time-varying convolutions. Filter states remain persistent; profile replacement needs prepared, warmed histories and a defined transition. | A registration selector is a routing change, not a reason to reconstruct unrelated stateful processors or clear their histories. |
| 054 / 331-336 | Direct electrical output, cabinet/microphone output and studio reverb are distinct modes. Room MIMO paths retain crossfeed/timing; optional 122RV spring electronics feed a fixed separate speaker. | Retain the nominal dry product boundary. Do not add a room, generic reverb, rotary processing or RV claim through preset names or UI decoration. |

## Actionable requirements for the M3 preset implementation

### Preserve musical selection separately from processor state

Pages 319-322 require clocks and histories to remain under the audio owner's
control, independent of note activity, GUI refresh and ordinary musical presets.
Although these pages discuss rotors, they provide the explicit downstream
contract that this new selector must not break. In the current
[Engine](../../../src/Engine.cpp), the source bank advances once per rendered
sample through silence and disconnected output, while a zero-frame control edit
consumes no elapsed time. The fixed-selector implementation should preserve
those existing semantics and the old dry arithmetic for old selections.

Selection and restore must not call preparation, reset the source seed, clear
held keys/pedals, erase contact travel, reset percussion readiness, or reset the
frame clock. A new fixed route may change the routing coefficients and
percussion eligibility; it does not acquire permission to replace the whole
engine. Failed requests still need complete preflight before mutation.

The current engine owns the dry source/contact/percussion/pedal path and does
not include the separate `RotaryMotion` or scanner research modules in its
rendering graph. The [existing rotary scope](../../ROTARY_SCOPE.md) specifically
preserves separate horn/drum radiation-boundary inputs and independent ownership.
This session should not insert that module merely because a reference cabinet
is visible in the UI.

### Give the fixed catalog a stable saved identity

Pages 258 and 262 require exact profile/parameter identities to accompany renders
and survive reload; a newer transcription must not silently change an older
project. Pages 313 and 319 similarly separate microphone/mechanical identities
from ordinary performance controls. For this bounded M3 phase, retain the exact
admitted chapel catalog identity/hash with the new save grammar, or implement an
equivalently explicit immutable-catalog contract. Unknown or unsupported identity
must not quietly fall back to a different sounding registration.

Append new control IDs while preserving all existing mappings. Page 321 explicitly
requires stable parameter/state mappings and actual host-adapter timing tests;
a core event test alone cannot qualify parameter-queue translation. Keep fixed
registration keys distinct from bank A/B controls and preserve inactive-bank
values so legacy state migrations can remain deterministic.

### Keep visual identity separate from sound and geometry

Pages 295, 299 and 300 explicitly allow convincing appearance while hidden
dimensions remain unknown, and require a rendered UI mesh to remain separate
from measured CAD. Pages 258, 294, 318 and 322 say displayed mechanical motion
must follow actual model state; UI animation cannot supply its own audio clock.

The new preset UI should paint selection/focus/held-note state from copied
application state, and retain the unconnected scanner/rotary status. The actual
application capture must remain distinguishable from the atlas concept art.
Do not display live-looking rotor RPM, microphone controls or hardware-fidelity
scores when those systems are not connected and qualified. Literal reference
matching requires observed comparison, not merely use of the same cabinet image.

## Selected visual observations

| Original page | Observed diagram detail | Preservation decision |
|---|---|---|
| 272 | L2 and the treble load are parallel between A and H; C16A returns H to B. The bass branch is A-L3-W with C16B and its load between W and B. The printed figure distinguishes electrical reference from protective earth and acoustic polarity. | Preserve the floating treble return and combined input load when M6 is later implemented; no generic split in this preset phase. |
| 278 | The diagram identifies one driven route through a stationary driver and rotating horn, with the dummy counterbalance explicitly assigned mechanical coupling. | Never treat the visible paired horn shape as two driven audio sources. |
| 322 | The ownership drawing and its prose assign trajectory histories to the audio clock and snapshots to UI consumers. The adjacent prose requires separate horn and drum histories; the compact diagram is not a specification for driving one rotor from the other. | Preserve independent histories and copied display state; do not literalize an illustrative diagram into a serial dependency. |
| 326 | Two separate rows place angular weights before or after persistent FIR processing. The caption says identical frozen-angle responses do not establish moving equivalence. | Preserve each subsystem's declared time convention; a UI/preset change cannot relocate weights or reset convolution history as an optimization. |

## Concrete acceptance recommendations

These are proposed checks for later assignments, **not tests executed by A04**.

1. Compare legacy A/B/Cancel renders against the unchanged baseline, including
   silence, disconnected output and several block partitions. The new catalog
   must not alter old arithmetic or source timing when unused.
2. Exercise zero-frame selection and restore at nonzero phase/contact/readiness
   state. Verify complete dynamic-state preservation, then compare subsequent
   output under equivalent independently initialized routing.
3. Exercise held-note selection, Cancel and reselection without releasing note
   owners. Keep the ordinary preset representation separate from a full DSP
   checkpoint; do not serialize history to obtain an apparent pass.
4. Round-trip the new fixed catalog identity and all retained bank data; reject
   unsupported identity before replacing destination controls. Verify old state
   migrations produce the exact old bank/route meaning.
5. Test actual parameter/state publication and host event timing, including
   same-offset clusters and both sides of a block boundary. Preserve the
   declared deterministic ordering and whole-call rollback.
6. Verify drawing, resize, focus and editor-related state changes cannot alter
   rendered output. Preserve real live controls while making the reference-led
   visual improvements; screenshots alone cannot qualify audio behavior.

## Dependencies that remain open

M5 connected dry-organ validation still precedes end-to-end cabinet fitting.
M6 needs a reviewed revision-specific electrical graph, calibrated port scales,
transformer/winding/feedback evidence, operating-point and convergence results,
and actual driver impedance and electrical captures (pp. 255-276). M7 needs
identified geometry, common-clock horn/drum motion and complex angular/position
captures, declared propagation/response ownership, validated interpolation and
alias budgets, and held-out scene comparisons (pp. 279-336). A new nominal fixed
registration does not resolve these inputs.

The source repeatedly says no new instrument captures were made. Its reported
synthetic companion results at pp. 306, 312, 318, 324, 330 and 336 are distinct
from this repository's actual source-identified runs. A04 did not obtain those
companions, rerun their fixtures, execute production/audio tests, or verify the
underlying external service manuals. The only completed result claimed here is
the complete assigned source reading, selected visual inspection, limited current
source-boundary inspection and this preservation/handoff report.
