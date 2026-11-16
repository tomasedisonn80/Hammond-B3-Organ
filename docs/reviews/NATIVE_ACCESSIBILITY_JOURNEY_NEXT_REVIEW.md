# Independent review of the next native accessibility journey

**Disposition: admit A42's source inventory and bounded journey plan, with the
operator and bridge prerequisites below.** It is not an implemented accessibility
contract or a native acceptance result. No source defect is established merely
by the percussion controls changing their Tab positions. The current model
preserves their semantic focus identities, and an existing focused test covers
that behavior. The remaining gap is an observed journey on the current native
build. Native semantic providers, reduced-motion preference integration and
numeric text editing remain absent from the inspected standalone implementation.

A53 inspected commit `2f57723d9ec806fe8f721c317ef8c1a38d63b532`, tree
`cee5fdc4b07d95185ebd9e4d1c5f236f88a787f9`, on 16 November 2026. The standalone
and current gallery Git subtrees are identical to A42's `af2b74760ee195c9497b314a1a29172f5238dd44`
inputs. The filesystem-only repair therefore changes none of this review's
application findings. Current repaired hosted execution is a separate root-owned
gate; no outcome is inferred here. A53 opened no application, OS/browser/CUA
session or device and ran no build, native executable or product test.

The [independent receipt](../development/2026-11-15-streaming-continuation/reports/A53-native-accessibility-audit.json)
binds the actual source, A42 proposal, retained X11 evidence, selected historical
test log and this review. Full [AGENTS](../../AGENTS.md), [M0–M9 plan](../PLAN.md),
active ownership/recovery records and the existing
[desktop acceptance contract](../REFERENCE_REFINEMENT_DESKTOP.md) were read.
The [A42 proposal](../design/NATIVE_ACCESSIBILITY_JOURNEY_NEXT.md) remains
unchanged by this review.

## Verified inventory and current ownership

The [model declarations](../../apps/standalone/UiModel.h),
[layout/input implementation](../../apps/standalone/UiModel.cpp),
[application dispatcher](../../apps/standalone/main.cpp),
[painter](../../apps/standalone/InstrumentView.cpp) and
[target/link inventory](../../apps/standalone/CMakeLists.txt) support A42's counts:

| Inventory | Source-grounded result |
| --- | --- |
| Ordinary Play controls | 10 common header controls + 2 × (2 edit-bank selectors + 12 presets + 9 visible drawbars) + 4 percussion + 1 expression + 2 pedal mixtures + 3 computer-key targets + 2 octave buttons = **68**. |
| Playing keys | **61 + 61 + 25 = 147** separate note identities. Three roving note groups make **71 Play Tab stops**, not 147 extra Tab stops. Rotary/Service expose the ten common stops. |
| Retained musical controls | Four drawbar banks, 36 retained manual drawbar positions and eighteen visible at once; 24 presets. Presentation and edited-bank state are outside the saved sound snapshot. The existing 47 sound parameter identities and state4/readers 1–3 remain required. |
| Modal focus | Audio: six stops. MIDI: eleven. Help: one effective Close, stored in shared modal slot 5; its early keyboard branch ignores Tab. These are modal-local positions, not `UiControlId` values. |
| Semantic access | `UiControlId` and the visible footer are internal canvas data. The inspected production sources/link composition supply no native control provider or role/value/action/event export. A native tree result still needs S0 observation; source absence is not an observed empty OS tree. |
| Motion and numeric input | Dimensional/Flat and immediate view changes exist. No reduced-motion preference query/option or SDL text-input handler/editor was found. `text_entry_active` suppresses musical shortcuts while a modal is open; its name does not establish a text editor. |

A42 correctly distinguishes desired controls from `view.applied.controls`, and
EDIT from the applied sounding route. The provider must retain that distinction.
An applied held-key flag is a logical note target: it neither counts all input
owners nor proves audible output. Existing physical-key owners begin at 1,
pointer owner is 100, and Space audition owner is 101. `activate` on a playing
key focuses it without producing a note; a future native Invoke cannot simply
assume it already has a momentary note lifetime.

### Percussion ordinals do not establish an identity-transfer defect

The current mappings are:

| Semantic control | `UiControlId.index` | Sound parameter ID | Wide Dimensional Tab position | Compact/Flat Tab position |
| --- | --- | --- | --- | --- |
| Enable | 0 | 12288 | 57 | 57 |
| Harmonic | 1 | 12289 | 60 | 58 |
| Volume | 2 | 12290 | 58 | 59 |
| Decay | 3 | 12291 | 59 | 60 |

`UiViewState::focus` stores the full ID. `resize` and `set_presentation` replace
layout and close/suppress pointer gestures without replacing that focus.
`move_tab_focus` searches the new list for the existing ID before advancing.
The painter likewise compares IDs, and `focused_control_caption` derives the
percussion name from the semantic index. Therefore Harmonic can move from
position 60 to 58 while remaining Harmonic; its next Tab neighbor legitimately
changes with the visible order. `set_workspace` separately restores remembered
visible IDs or the destination workspace tab. None of these operations should
be rewritten to retain an ordinal.

This is already covered at model level by
[`test_standalone_percussion_reference.cpp`](../../apps/standalone/tests/test_standalone_percussion_reference.cpp),
function `tab_cycle_and_semantic_reflow`. It checks all four IDs across
1399×820, 1400×819, 1400×820 and fractional reference size, Flat/Dimensional,
forward/reverse traversal and Rotary/Service return; it also rejects hidden
activation. The unchanged source is included in the retained local
[qualification](../development/2026-11-15-streaming-continuation/reports/final-coherent-qualification.json).
Its original log records `test_standalone_percussion_reference` passing in
0.01 seconds. Reading that historical log is not a new execution or an OS-input
result. A duplicate test or speculative production fix is not the next task.

**Focused next native subcase, P1:** on the assigned ordinary 1672×941
Dimensional Play launch, start without a client click and use distinct Tab
press/release pairs to reach Harmonic at position 60. Retain the focus outline,
full footer name and four percussion values. Toggle F7 with a real press/release;
Harmonic must remain focused at its new position 58. Tab must now reach Volume;
Shift+Tab must return to Harmonic. Return to Dimensional: Harmonic remains
focused, with Expression as the next Tab stop. Repeat the identity check across
1399↔1400 at height 820 and 819↔820 at width 1400, recording the exact native
resize operation and actual client size.

In a separate fresh baseline trial for each transition, activate the retained
Harmonic with Enter after the transition. Only harmonic may change; enable,
volume, decay and other sound controls must remain unchanged. Retain settled
painted values and the final copied controls or acknowledged saved-state copy.
Repeat for Volume and Decay, whose ordinals also move, plus Enable as a stable
ordinal control. No note should be acquired by focus or layout changes. A footer
and control-change observation can qualify this behavioral journey; they must
not be labeled a queried native focused object when no provider exists.

## Corrections before executing or grading the plan

These are additions to the operator record and future bridge contract, not new
release thresholds and not evidence that a failure occurred.

| Priority | Concrete correction or clarification | Reason and acceptance consequence |
| --- | --- | --- |
| 1 | Separate **current source behavior**, **existing model-test evidence**, **new native observation**, and **future provider requirement** in each result. Add P1 above without calling changed Tab ordinals a defect. | Otherwise an already-covered identity rule can be confused with an unexecuted OS journey or a missing provider. |
| 1 | Make the fresh-output launch fail closed on a failed `mkdir`, state copy or hash command. An existing directory must stop the sequence before any copy/redirection. Capture the application's numeric exit even if the launcher uses shell `errexit`. | A42's text requires fresh directories, but its sequential shell block does not itself stop after `mkdir` failure. Use explicit checked setup commands and an `if app ...; then journey_exit=0; else journey_exit=$?; fi` pattern in the assigned launcher. Never overwrite a previous run while recovering setup. |
| 1 | State the healthy ordinary-close pass conditions explicitly: exit 0, no supervisor timeout/signal, available final snapshot, stopped/unheld state, positive callback/frame counts when audio was opened, zero render/format/nonfinite/overrange failures and zero unexpected application/Session faults, overflows, rejections or recoveries. | `Application::run` can return 0 on an ordinary run despite a nonfatal `error_count_`; numeric exit alone is insufficient. Retain all discard counts and sequence gaps without inventing their command identities. A discard is not automatically proof of a stuck note, nor permission to claim every command applied. |
| 1 | Keep invalid MIDI Apply and other intentional error cases separate from the fresh healthy-close case, as A42 already requests. Declare the expected error and unchanged configured/active state before the negative trial. | An expected validation error is evidence for that negative case; it must not be erased or silently exempt every later error. A MIDI-OFF/No-input run cannot prove preservation of an actual connected device. |
| 2 | Qualify “hidden controls cannot acquire new holds.” It applies to hidden pointer targets, focus/Space and direct control activation, not the documented global computer-piano shortcuts. | The [workspace contract](../INTERFACE_WORKSPACE_CONTRACT.md) and `UiModel::key` intentionally allow computer playing and F1–F3/octave outside Play. All underlying workspace/note shortcuts are suppressed while a modal is open. Do not grade legal Service keyboard playing as an accessibility regression. |
| 2 | Treat S0 inspector or screen-reader setup failure separately from an observed application tree without controls. Establish that the selected inspector can query the correct process and a known accessible surface in the same session. | No bus, wrong process or inaccessible inspector is a blocked prerequisite, not an observed instrument-provider result. Record versions, mode and actual errors; do not infer speech from text rendered on screen. |

The healthy-close requirements carry forward the desktop contract. A display-only
run may use explicitly identified dummy audio and MIDI OFF; it qualifies that
scope only. An unavailable audio device may still permit a useful modal/display
observation, but cannot pass a journey requiring an operating callback path.
Audio Apply is an explicit restart: it releases notes, preserves acknowledged
controls, resets source phase and requires explicit MIDI reconnect. It must not
be graded against the presentation-only no-phase-reset requirement.

## Held input, capture and modal evidence

A42's J2/J3 sequence fills the actual missing OS evidence. The application source
preserves keyboard/Space holds by captured press identity; key Up runs before
modal/modifier gates. A real resize or presentation/workspace change closes a
parameter drag and suppresses further pointer Move interpretation while retaining
an existing pointer note until Up or cleanup. Ordinary unsuppressed in/out
movement is a different path that can release and reacquire note targets while
SDL capture remains admitted. Both deserve their own recorded cases.

Use keyboard shortcuts to open Help/Audio/MIDI while the primary pointer is
still physically held. A click on the opener after releasing the pointer does
not execute the held-modal case. `open_overlay` releases UI owners, turns on
modal suppression, and copies configured settings into staged modal values.
Closing removes the suppression mode while preserving actual physical-key
records until Up. Consequently a still-down A must not retrigger on close;
release/repress must work. Test Audio six-stop and MIDI eleven-stop wrapping,
Help's single Close, restoration of the underlying focused ID, and rejection of
underlying F4–F7/playing actions while modal. A shortcut opener need not be the
underlying focused object. Digits must not be claimed to edit a numeric field.

For pointer-held resize, first document a window-manager operation that keeps
the primary button down and the app focused. If that operation or the capture
method releases the button, deactivates the window or loses capture, retain that
cleanup observation but mark uninterrupted continuity unobserved. Keyboard-held
resize via an ordinary pointer resize edge proves only keyboard-held resize.
Require a real post-release button-up return and a fresh press, not merely the
released endpoint of an atomic drag. Repeat with pointer-held pedal 25 because
its position moves. Layout change during a named drawbar drag must not cause
subsequent motion to edit a different parameter or newly displayed bank.

Escape/focus loss release UI owners; Panic has all-owner scope and also triggers
the application's MIDI retirement workflow. Distinct UI/MIDI overlap requires
separately identified physical or synthetic inputs and both release orders.
Neither cleanup nor held-count agreement establishes device callback retirement;
the [native recovery review](PRODUCT_NATIVE_RECOVERY_REVIEW.md) retains its
separate platform/dependency gates.

### What the retained X11 run actually contributes

Independent reading and hashing of the original JSON agree with the
[retained review](REFERENCE_REFINEMENT_NATIVE_INPUT.md): executable
`6eea84ba830ea8710b550c14561b4dd887bea8aac489fa82a467e3708e071b13`,
X11/software, dummy 48 kHz stereo audio, 512-frame callbacks and 19 untruncated
paint observations. Its keyboard pedal survives 1400×820→1180×820; the pointer
sequence retains capture through Upper held-count 1→0→1→0. Final capture
attempt/success/loss/release-call counts are 1/1/0/1. Joined state is stopped and
unheld with 7,420 callbacks and one discarded command of unknown identity.

The old run lacks a painted pre-held prefix for the two keyboard view changes,
pointer-held resize/suppressed return/fresh press, a separate numeric exit
receipt, a close-control click and retained per-step lossless desktop frames.
Its startup app image is not a later desktop journey image; the contemporaneous
review also retains a window/desktop fit limitation. These omissions remain
open. Neither current dummy-gallery pixels nor unchanged source retrospectively
supplies the missing observations.

### Evidence collection must not exceed the diagnostics

`presentation.observations` is a deduplicated history of selected painted state,
not one record per operator action. It omits ordinary focus IDs, individual note
identities/owners, pointer coordinates, full controls and per-step drawable sizes.
Changing focus alone need not add a record; exchanging two notes with the same
held count may also leave no distinguishing entry. Require an action/time log
and lossless full desktop/client frames that identify the relevant key/control,
plus actual native tree/event/speech records when those exist. Keep expectation
and observation separate. An inferred model ID is not an exported provider ID.

Preserve the final runtime drawable dimensions separately from each platform
DPI observation. The 512-record limit and `observations_truncated` must be
retained; split long runs before losing required transitions. Capture methods
that change focus belong in the action log and cannot be edited out of a held
journey. `sdl_captured` is the application's admitted flag, not independent OS
delivery proof; `release_calls` does not report the release API's return status.
The ordinary `--screenshot` startup BMP cannot serve as a per-step recorder.

## First dependency-ready work and bridge prerequisites

**Assign one native display owner first:** freeze the intended application source
and prepare a separately assigned native-backend build without altering the
coordinated dummy build. Use one fitting display, fresh state/outputs and an
ordinary launch. Execute D1/J1 plus P1, then J2/J3 with actual retained holds,
J4/J5 and a separate healthy J6 close-control run. Begin with one working native
configuration; unavailable fractional/high-density/cross-display rows stay
blocked. Real MIDI and a semantic provider are not prerequisites for this
keyboard/pointer evidence. Root must admit only the exact steps and binary
observed. No new native execution is authorized by this review itself.

On that same assigned platform, S0 is the first accessibility task. Retain the
actual tree/events and screen-reader behavior, including a verified negative
result if controls are absent. Then freeze a concrete one-platform bridge design
before implementation. A42's mapping table is a good starting inventory, but
the following are still implementation prerequisites:

1. **Object identity and visibility:** key objects by complete semantic tuples,
   including manual/bank/index, plus distinct dialog/control identities. Rebinding
   the edited bank must not silently reuse a stale bank object's value action.
   Hidden Play controls must reject actions; read-only cards may be discoverable
   without adding musical Tab stops. Tree object count and keyboard Tab count
   are different measures.
2. **Action and lifetime ownership:** native callbacks must enter the existing
   main-thread model/dispatch path, respect modal and input gates, and never read
   or mutate the live audio Engine. Specify ordering, rejection, shutdown and
   cancellation of pending provider requests. Resolve momentary note press/
   release or bounded audition before exposing a note Invoke; no indefinite
   latch or unreviewed new input-owner namespace follows from this proposal.
3. **Snapshot and announcement semantics:** publish coherent copied desired/
   pending/applied state, effective sounding/eligibility and availability. Define
   focus/selection/value/error/status events for modal entry/exit and bank/view
   changes. Live counters/meters must not generate unsolicited frame-rate speech.
   A deterministic ordering harness can supplement missed transient acknowledgments,
   but cannot be reported as ordinary native timing.
4. **Observed accessibility acceptance:** S1–S4 require the named inspector and
   screen reader, actual keyboard delivery mode, correct full labels/roles/
   ranges/actions, hidden-object protection, modal focus restriction/restoration,
   stable identity through P1 and release-safe Space/shortcut behavior. Failed
   delivery remains failed/unobserved. Flat alone does not satisfy automatic
   reduced-motion support; numeric text entry remains a separately scoped feature.

This ordering closes concrete missing evidence without inventing a new product
pass. Real display/DPI, devices, semantic access, reduced motion, DAW hosting,
callback deadlines, signed distribution, physical fidelity and literal
whole-interface 1:1 retain their separate M0–M9 requirements.

## Reproduce the bounded audit

From the repository root, this source/evidence/document check launches no native
program and performs no build or product tests:

```sh
python3 -B docs/development/2026-11-15-streaming-continuation/reports/A53-native-accessibility-audit.py \
  --repo . --output /tmp/A53-native-accessibility-recheck.json
```

The retained receipt records exact checks, hashes and limitations. Its pass means
the named source/evidence bindings and owned-document integrity agree; the
reasoned review and future native acceptance remain distinct.
