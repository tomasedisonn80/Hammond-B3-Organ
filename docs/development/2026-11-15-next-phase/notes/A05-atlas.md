# A05: atlas pages 334-416 and modern native recall

Assignment: `/root/w01_a05`, wave 1, 15 November 2026. Repository:
`/workspace/scratch/116ca0948095/Hammond-B3-Organ`; starting revision supplied
by root: `138fca9af7feca46d10b0e2b65d891f4751a3904`. This is a source and
design assessment, not implementation or executed product acceptance.

## Complete reading and source basis

I read all 83 pages, 334-416, from the form-feed extraction, including every
page's qualifications. A fresh `pdftotext -layout -f 334 -l 416` extraction from
the original PDF matched those segments byte for byte. I rendered and inspected
original pages 338, 381, 388, 399, 409, 412, 415 and 416, including their diagrams
and the actual reference artwork. I also viewed the retained product
`play-reference-1672x941.png`. The entire `AGENTS.md`, `docs/PLAN.md`, session
entry, current checkpoint and relevant assignment were read.

Pages 334-348 separate the optional stationary RV radiator, room response,
driver mechanisms and physical validation. Pages 349-378 require qualified
acquisition boundaries, immutable provenance, independent holdouts and bounded
listening claims. Pages 379-396 assign one audio owner, bounded communication,
off-thread preparation and separate musical snapshots from DSP checkpoints.
Pages 397-408 preserve control identities, migration semantics and independently
qualified packaging. Their proposed 62-parameter registry does not authorize
replacing this repository's accepted 47 identities. Pages 409-416 provide the
walnut/charcoal/brass direction and explicitly distinguish edited banks,
sounding routes, modern saved sounds and calibration profiles.

## Recommended dependency-ready M9 scope

Implement a **native named recall browser**, separate from the 24 reversed
preset keys and existing documentary fixed registrations. This supplies the
page-409 preset-name header affordance and page-416 Save Registration / Save
Performance workflow without duplicating completed fixed-preset work.

Freeze two explicit proposed scopes before coding:

| Scope | Recall contents |
| --- | --- |
| Registration | All 36 manual drawbars, two pedal drawbars, remembered banks, route-enable bits, fixed registrations and four percussion settings; preserve current expression. |
| Performance: current controls | The entire existing `ControlSnapshot`, including expression. |

The scope panel must enumerate these contents before recall. Neither scope
contains device names, MIDI calibration/routing, held-note ownership, editor
bank, camera, profile replacement or DSP history. Scanner, microphone and
rotary settings are absent from the current musical snapshot; do not label this
limited performance scope complete atlas performance recall. Calibration-profile
recall remains unavailable until its separate preparation/lifetime contract exists.

Use a small native-only catalog/entry module and a bounded, nonrecursive browser.
A separately versioned envelope can hold name, scope and an unchanged
`B3CONTROLS4` payload in one atomically replaced file. Legacy files import through
the existing readers 1-4; explicit legacy Save/Load retains its existing format
and `--state` destination. The new envelope is not readable by old controls-only
readers and must have its own extension/version. No new sound parameter,
automation selector, factory catalog or Engine route is required.

## Current flow and integration hazards

`main.cpp::request_save/complete_save` already waits for a coherent acknowledged
snapshot and cancels on changes, recovery, rejection, discard or timeout. Reuse
that discipline; never persist optimistic UI values. `StateFiles.cpp` already
validates regular-file destinations and uses temporary-file replacement.

For registration recall, merge the admitted fields into the latest desired
controls, preserving expression, then submit one complete `ControlSnapshot`.
Publish the active entry name only after the submitted sequence is acknowledged;
pending, rejected and staged-with-no-audio states remain visibly distinct.
`Engine::restore_controls` changes controls and coefficient dirtiness, without
resetting contact, percussion or source histories.

Two traps require explicit owner-coordinated integration. First,
`UiModel::load_controls` immediately replaces `saved_controls_`: using it blindly
for a partial merge would mark unsaved expression and unrelated legacy-file
changes clean. Named-entry dirty comparison must use its declared scope, while
the legacy file's clean reference remains separately meaningful. Second,
`main.cpp::open_overlay` calls `lose_input(FocusLost)` and releases UI notes.
The browser needs an opening path that closes a drawbar gesture while retaining
note owners. Continue forwarding physical key/pointer Up events; existing
`handle_key` already sends Up through `UiModel` before modal gates. Genuine window
deactivation retains the existing recovery policy.

## Header direction and honest acceptance

Page 409 shows a restrained top-right name field with previous/next arrows and
settings; the current capture shows six utility buttons instead. Add the real
selected entry name, scope and pending/modified indication there, with arrows
changing browser selection and an explicit Recall action. Browsing must not
change sound. Keep sounding-route and edited-bank captions independent. Preserve
legible compact and Flat access, keyboard focus and the truthful nominal-dry
caption. Coordinate all header/layout/paint integration with their current owners.

Required verification includes scope merges with expression changing, all four
banks and cancelled fixed routes, unchanged historical state fixtures, malformed
and future entries, failed writes preserving originals, delayed acknowledgments,
recovery cancellation and stopped-audio staging. Exercise browsing and recall
during independent keyboard/pointer/MIDI holds; inspect retained owners, source
phase and percussion readiness. Check original gesture identity and no callback
filesystem work. Verify legacy-file dirty state independently of catalog state.

Capture the actual changed application at 1672x941, 1280x900 and 960x700,
including Flat, long names and pending/error states. Retain source, executable,
replay/state and pixel identities; compare header structure with original page
409 and semantic inventory with pages 410/415/416. This can close a scoped
browser/header gate. It cannot close literal whole-interface 1:1 equality,
native assistive-technology qualification, hardware usability or acoustic fidelity.

## Independent scanner continuation

`ScannerLineFoh` is a compatible second research scope, preserving the existing
line and its failed G5 record. `SCANNER_AC_PARITY.md` records same-Hz failure
even at 1,536,000 Hz. Freeze a new realization identity and first-order-hold input
convention; retain the original grid/bounds and compare actual recurrence with
independent same-Hz, transient and rotating references. Changing reconstruction
creates a named experiment, not a retrospective pass. Resampling, filtering,
latency, G6 integration and physical M4 remain separate. This does not take M6
FOH or R4 ownership.

## Executed checks and identities

Executed: source reads, complete extraction comparison, original-PDF rendering,
image inspection and SHA-256 calculation. No build, test suite, git operation,
publication or shared source edit was performed. Only this note changes the
repository; review renders are disposable scratch intermediates.

| Input | SHA-256 |
| --- | --- |
| Original PDF | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| Full form-feed text | `e6ed8ed76663a8f12c487ae1e4d3ab69facc36971df240a15b1ba36eeb22485d` |
| Pages 334-416, including final form feed | `3ba1ff50e66f37adc06cdddf51f1908926b6e30becf9106764ef94582b2ed19b` |
| `apps/standalone/main.cpp` | `937b837d4ef4317d02ea2862ac34dc95031c73f0f32719b0924de29f4b721027` |
| `apps/standalone/UiModel.cpp` | `49c68995aad96aa5e316613412c93931a1082d0e4a3ad3758ac63484af963064` |
| `apps/standalone/UiModel.h` | `d94e90be25812c6d21b61f37f2b0547704d14866c45fbbb21131ec70b6389bd3` |
| `apps/standalone/StateFiles.cpp` | `6cd0d2f26bb2f938781561d278f15f9230e5d84b6052e8554761dc8e96dfd3b6` |
| `include/hammond/ControlState.h` | `aab82b082f9cf77dadf763148cade9eae04f6f7df68b302b1832f21f78034856` |
| `src/Engine.cpp` | `ea94f27be2ce6e374537c616bdde34c32c3276df6f7f24e112f52a35d1a4bd3a` |
| `src/ControlStateIO.cpp` | `3a95b6750fc615b7218da5dd9cb540b30d8a83984374d441f2754c7e66de34fb` |
| `docs/SCANNER_NUMERICAL_CONTRACT.md` | `3999a3a409d397401e135e8285704092bad130911468802370bf6da404d58ff9` |
