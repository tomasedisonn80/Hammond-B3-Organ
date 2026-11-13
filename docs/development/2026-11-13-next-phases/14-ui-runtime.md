# Assignment 14 — standalone UI runtime

Actual assignment: `/root/w03_a14_ui_runtime`, wave 3 of the independent
2026-11-13 standalone session. Owned `apps/standalone/UiModel.cpp` and this note.
Inspected HEAD `2e917509b378d48c85cc1d52c3aa446eef9552c8`; the integrator owns
concurrent changes, shared status, acceptance, commits and publication.

## Implemented

- SDK-free, fixed-capacity main-thread model against `UiModel.h`, `Session.h`
  and `docs/STANDALONE_UI.md`; no live Engine access or core/header/CMake edits.
- One shared layout for painting/hits: 61 Upper, 61 Lower and 25 pedal keys,
  accidental precedence, half-open natural edges, and 45 visible controls.
  Invalid dimensions/banks preserve the destination; dimensions above 8192
  reject using the limit added to the contract by the integrator.
- Exact 45 retained parameter identities, all four manual banks, 18 visible
  manual drawbars, independent EDIT/SOUNDING, routing-only Cancel, percussion,
  pedal mixtures and nominal expression. Bridge conversion and ControlState
  validation supply the existing laws; no new registry identities or DSP.
- Original target/note/owner capture for computer keys, pointer and Space;
  repeat/duplicate rejection, text/modifier suppression, original releases,
  target/octave changes, pedal range rejection, capture loss and glissando
  Off-before-On across manual/pedal namespaces.
- Captured parameter/bank/track identity; bank changes and valid resize close
  a drag without retriggering. Pointer movement outside keys releases that
  owner, retains capture and allows re-entry until Up.
- Scoped focus/Escape release, global Panic, submission-failure suppression,
  one InvalidCommand release request, out-of-band overflow recovery, desired
  versus applied controls, sequence acknowledgments, clean-file references,
  and recovery snapshot adoption without replaying notes or echoing actions.
- Forty-eight Tab stops: every visible control plus three roving key groups;
  semitone/octave/Home/End navigation, Space audition, integer drawbar edits,
  0.05/Shift-0.01 expression adjustment, and main-thread app requests.

## Final geometry decisions

Contract margins/gaps/panel heights are preserved: manuals are 146 high at
1280×900 and 86 high at 960×700. Header buttons are 36 high; registration and
toolbar buttons are 32 high; percussion buttons are 40 high. Each registration
has a 28-high footage label band, a separate 18-high value band and a vertical
track whose endpoints are cap centers (0 top, 8 bottom). Track heights are
80/40 at reference/minimum; pedal tracks are 60/20, retaining cap clearance.
The lower performance row reads EXPRESSION, MIX 1, MIX 2, matching Tab order.
Expression uses a horizontal 0-left/1-right center track. Keyboards have an
8-unit side/bottom inset and 22-unit name strip. No independent hit geometry.

## Executed verification

Working directory: `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.
Toolchain: Debian GCC 14.2.0 (`14.2.0-19`), C++20. Production compilation passed
`-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror`.
The focused harness remains outside the repository, as assigned:

```sh
g++ -std=c++20 -Wall -Wextra -Wpedantic -Werror -Iinclude -Iapps/standalone \
  /workspace/scratch/5ba97739b54c/ui-model-smoke.cpp apps/standalone/UiModel.cpp \
  ../build-baseline/libhammond_core.a -o /workspace/scratch/5ba97739b54c/ui-model-smoke
/workspace/scratch/5ba97739b54c/ui-model-smoke
```

Result: **8,320 assertions passed**. Covered minimum/reference/breakpoint/maximum
sizes, counts/bounds/nonoverlap/hit edges, every registry identity, original
releases and overlapping owner IDs, target/octave/text gates, audition,
glissando/capture, bank/resize drag closure, bridge half thresholds, control
acknowledgments, malformed load preservation, rejection/recovery and Tab reach.
The first scratch-harness compile had an unparenthesized macro argument with
braced commas; fixed only that harness, then compiled and ran successfully.
`git diff --check` passed. No actual SDL/device/assistive workflow is claimed.

SHA-256 inputs at verification:

- `UiModel.cpp`: `c42aee8edcd3663f5925581cd738997bf83438a2fdcc13072b8a40f5407997c1`
- `UiModel.h`: `55affdc2df63918909c6412763abc26dd15a57601263faca97c8007d8def9f93`
- `Session.h`: `0eed6c82d0cf5ffbeb0206f6f9702a93ef5a75cde6fd669b2862705dc7af84a0`
- Existing core archive: `6d6f6a92c4f5a826dacff1314b984c1b28cdcdf021751f8d8770eab780cc9dd8`
- Scratch harness: `35abaad4c02e5c4c774b8b3a465f35a4734c3ee8f989499b67b30b39b9474775`

Next: assignment 17 independently accepts the UI contract; integrate Session
and actual SDL dispatch/rendering, then inspect labels, focus and high-DPI at
the named sizes. Physical fidelity, audio-device timing, native accessibility
and publication remain separate gates. Source basis/limits remain the frozen
UI contract and atlas reviews 05/06; this implementation adds no measured model.
