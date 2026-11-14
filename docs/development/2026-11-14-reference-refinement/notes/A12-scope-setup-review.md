# A12 — Independent scope and setup review

Actual worker `/root/w02_a12_scope_setup_review`, wave 2. Owned outputs are this
note and `reports/A12-setup-review.json`. I reviewed current AGENTS, scope,
checkpoint, PLAN, A01–A06 summaries, reviewed layout/material/desktop contracts,
the proposed propagation contract, existing rotary types/motion implementation,
and relevant native source. This review adds no production change or execution
claim to the earlier atlas readers' results.

## Exact local baseline

The starting product is `8bd999efc13e309b932e6ac41d72ceb7b9b80a5f`, tree
`c37da16cedbb91573476a44bd4eafe5a5e30134a`. All initially recorded 162 baseline
hashes matched: 159 tracked inputs and three generated Python cache files.
The caches are incidental, not required product sources; root was notified and
owns their exclusion from the published inventory. A separate `git diff` against
the starting commit initially found no changes across root CMake, include, src,
apps, cmake, assets, data, tests or tools. During final handoff, root published
the documentation-only `d2972a5` while wave-3 UiModel and UI-test edits appeared.
The report separates those later unqualified worktree changes from this initial
audit; the earlier 147-suite result does not qualify changed source.

The native executable is 3,624,104 bytes and matches baseline SHA-256
`eb979f273466ffbcb7fee0b7c7e71c075ef1b8f5a001dbddaa3f96da13434976`.
The separate desktop executable is 3,851,832 bytes; its different hash is retained
in the report. Both use GCC 14.2.0 Release and disable VST3; MIDI is OFF in
`build-native` and ON in `build-desktop`. Although both caches request X11,
generated SDL configuration proves X11 **OFF** in the baseline and **ON** in the
desktop build. SDL ALSA audio is disabled in both; desktop RtMidi separately
compiles its ALSA backend. Backend selection is not hardware qualification.

Actual CMake/CTest 4.4.5 live in `../build-tools/cmake/data/bin/`; Ninja is
`../build-tools/bin/ninja`, version `1.13.2.git.kitware.jobserver-pipe-1`.
The retained baseline log establishes 147/147 suites in 145.26 seconds.
Fresh CTest discovery found 147 registrations in each build and the four desktop
contract selections. Discovery does not transfer the baseline pass to the
desktop binary. I ran no build or test suite.

SDL2 2.32.10 and RtMidi 6.0.0 are clean checkouts at their locked commits.
License/source checks, the prepared RtMidi patch hash, and all 25 recorded Debian
archive size/hash pairs match. VST3's lock identity was inspected; no SDK was
configured or independently qualified. Original PDF, reference art and retained
native image hashes also match. The task occupies approximately 0.564 GiB;
57.991 GiB remain available. Both build trees and shared dependencies fit the
bounded-storage plan; nothing was removed.

## Feasibility and whole-application invariants

No blocking setup or UI allocation hole was found. Independent formula
evaluation reproduces reference key depth 144.12 pixels, cabinet x1124.831312,
and minimum active art/status heights 287.4/116 pixels, including extreme-size
corners without giant captures. The two-axis breakpoint and unchanged compact
branch are essential. Keep cabinet and pedal surfaces disjoint.

Current source confirms 47 parameter records, state4/readers 1–3, 91 sources,
two 61-key manuals, 25 pedals, 24 presets, 68 ordinary controls and 71/10 focus
stops. `paint_header` runs before workspace branching. Preserve that common
header across Play/Rotary/Service and both presentations; move Flat's paint and
hit points together and update literal replay points. Original held owners,
four banks, source/percussion histories and dry Engine behavior remain fixed.

Material timing requires a layout-only before-image executable with the same
geometry/backend as its after measurement. The unchanged baseline alone would
confound geometry and paint costs. Native captures, real pointer holds/releases,
capture return and ordinary close still require their named observations.

## Independent M7 API review

No blocking API hole was found. The 4,097-anchor borrowed immutable view is an
explicit offline-fixture limit, not streaming history. Canonical continuity,
equal-frame replacement, inclusive coverage, copied-view lifetime, transactional
reprepare and preserved destinations fit the existing helpers. Split frame/time
arithmetic avoids large absolute subtraction. Full-orbit clearance/Mach checks
include the actual epoch seed. Counting both endpoints within 48 evaluations
still leaves 46 midpoint evaluations, sufficient for the frozen residual budget.

A10 incorporated the requested helper coordinate/radius limits and negative-epoch
error wording before freeze. Its tighter internal `1e-14 s` solve target preserves
the frozen acceptance budget while leaving frequency-ratio margin. R2 must
precede R3 acceptance;
independent phase error must remain separate from root error. Streaming waveform
history, two-frame rendering latency, tails, audible policy, R6 integration and
physical M7 remain later gates. Next: accept the clarified contracts, implement
disjoint slices, retain the material baseline, and qualify changed source with
the specified independent numerical, geometry, replay and native evidence.
