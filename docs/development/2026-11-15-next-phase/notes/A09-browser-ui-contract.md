# A09 — native registration browser visual/input contract

Actual worker `/root/w02_a09`, Wave 2, 15 November 2026. Owned files:
`docs/REGISTRATION_BROWSER_UI_CONTRACT.md` and this note only. This is contract
authorship and source/geometry review; no implementation, build, runtime test,
Git operation, publication, shared-navigation edit or child dispatch occurred.
The supplied session baseline is `138fca9af7feca46d10b0e2b65d891f4751a3904`;
root owns live source/index/remote verification and coordinated builds.

## Recovery and inspected evidence

Read the complete AGENTS.md and PLAN.md, the current next-phase session README
and checkpoint, own/neighboring actual assignments, the full current A05/A06
atlas notes, current navigation/handoff front matter and relevant historical
product A05/A06 notes. PLAN/navigation retain older operational pointers; current
AGENTS/session routing and this explicit assignment govern ownership.

Read actual `UiModel.h` and relevant geometry, semantic validation, focus,
parameter-drag, keyboard/pointer, recall/clean-state and observation code in
`UiModel.cpp`; inspected `InstrumentView.h`, header/overlay/control paint in
`InstrumentView.cpp`, and Save/Load, modal, input/capture and event dispatch in
`main.cpp`. Also inspected `ControlSnapshot`, existing layout/reference-gap
records and native fixture inventory. Directly read atlas extracted pages 409,
410, 416, 418, 433 and 437; complete atlas coverage is the six Wave 1 readers'
work, not a new A09 500-page reading claim.

Directly viewed the unaltered cover/page-409 JPEG and actual current product
PNGs: Play 1672×941, Play 960×700 and Flat 960×700. These are retained earlier
application captures with their original identities. No new capture is claimed.

| Inspected input | SHA-256 |
| --- | --- |
| `UiModel.h` | `d94e90be25812c6d21b61f37f2b0547704d14866c45fbbb21131ec70b6389bd3` |
| `UiModel.cpp` | `49c68995aad96aa5e316613412c93931a1082d0e4a3ad3758ac63484af963064` |
| `InstrumentView.h` | `b334ba3b085ec63fbbd715e4d2ae5fcecfc41a00dcdf7f4d079b7076c254c1f0` |
| `InstrumentView.cpp` | `3687f96db4490e600d6107e6b39d7b7d568bdeb183f16f6aa397535a5f688567` |
| `main.cpp` | `937b837d4ef4317d02ea2862ac34dc95031c73f0f32719b0924de29f4b721027` |
| Reference JPEG | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| Actual product reference-size Play PNG | `4dcb8e55dcfbc5f3e5d524bf0ea426312083f8f56e922716e6d0513fe08b9d19` |

## Authored result and coordination

[REGISTRATION_BROWSER_UI_CONTRACT.md](../../../REGISTRATION_BROWSER_UI_CONTRACT.md)
specifies an explicitly modern native named-control browser, preserving all 47
sound IDs, state4/readers1–3 and legacy Save/Load. It coordinates with A08's
library contract: Registration restores all current snapshot fields except
expression; Performance includes expression; suffixes encode the displayed
scope around unchanged state4 bytes. Selection is presentation-only and only
the focused/clicked Recall action requests controls. Save new is create-only,
with a real bounded SDL name editor and Registration as the default scope.

The reference-style name field moves into the top right, with semantic
previous/next selection buttons. All legacy utilities remain reachable inside
the unchanged header extent. Three UI-only kinds append at 22–24; ordinary
control slots become 71, common controls 13, Play focus stops 74, with seven
separate browser stops and unchanged eleven MIDI stops. Explicit shared
rectangles cover minimum/default/reference sizes and both skins. This is no
permission to alter deck/rack/key/cabinet geometry or another session's paint,
Drawing optimization, M6, native MIDI-close or R4 work.

The contract separates selected entry, proven current named reference and
operation target. Pending, Applied, Saved/current, Saved with warning,
Modified, stale, failed, superseded and unconfirmed states cannot be collapsed
into a success flag. A failed refresh after committed save does not turn that
save into failure. Header and modal remain truthful when selection changes
while a request is pending. A08's main-thread-only synchronous bounded file I/O
rule is retained; it does not imply a filesystem or physical release-latency
bound. Queued releases must still reach original ownership paths.

## Source hazards made explicit

1. Existing `open_overlay()` calls `lose_input(FocusLost)`, releasing UI owners.
   Browser entry needs its own parameter-gesture-only closure and must retain a
   playing pointer's SDL capture until its actual Up/capture loss.
2. `UiModel::key()` handles Escape before its text-entry gate. Simply calling
   it first for browser Down would release notes. The proposed browser input
   flag suppresses activation after physical bookkeeping but before Escape;
   all actual Up events still precede modal gates.
3. `load_controls()` replaces the legacy clean reference. A separate
   `recall_controls()` publication operation preserves it, as A08 requires.
4. Current header title/caption fitting infers boundaries from SAVE and Flat.
   Moving those controls requires explicit text allocations; leaving the old
   `flat_left` calculation would make the wide caption allowance negative.

The new `RegistrationBrowserModel/View` APIs separate A15's model/view work
from A18's main/UiModel integration. LibraryModel remains the single catalog
and operation authority. Root owns CMake and shared documentation.

## Executed checks and limits

Executed file/source reads, image inspection and SHA-256 commands above. A
small in-memory Python arithmetic check independently constructed the proposed
13 header-control rectangles and seven modal focus regions for 960×700,
1280×900, 1672×941, 1399×819, 1400×700 and 1400×820. Every set had positive,
contained, pairwise nonoverlapping hits. This checks the written formulas only;
it does not validate implemented code, glyph fit, pixels, accessibility or
native event dispatch. No build or executable test was run. An initial
filename-glob search for old native fixtures found no matching standalone files;
the actual fixture inventory was then read under `apps/standalone/`.

Read the authored A08 library contract and aligned scope, current/applied
reference, receipt lifecycle, no-audio refusal, create-only save, finite name
policy and main-thread I/O. The two authored contracts still need independent
A11/A12 review and freeze. A11's pending receipt hardening can retain these
visual semantics without broadening this slice.

## Next action and remaining gaps

A12 independently reviews the UI/API/geometry/input contract, cross-checks A11's
final library contract and freezes corrections before A15/A18 implementation.
Required implementation evidence includes original held-note Up/capture
journeys, source-bound acknowledgment and storage failures, both-way focus,
literal geometry/text checks, actual minimum/default/reference/Flat captures,
and independent reference comparison/admission. Root then updates README and
handoff with the admitted actual application images.

The proposed header is visibly directed toward the reference's selected-name
structure, while retained utilities and scope/outcome text remain necessary
differences. Broader deck/material/key composition, correct-versus-concept
inventory differences, real display/device journeys, native accessibility and
physical model acceptance remain separate. Literal whole-interface 1:1 remains
unmet and unwaived; this authored document closes none of those gates.
