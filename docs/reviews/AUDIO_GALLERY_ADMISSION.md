# Independent admission of the audio continuation UI gallery

**Decision: admit the retained gallery as actual native software-capture
evidence for the bounded wide-percussion refinement. Whole-interface 1:1
reference matching remains unmet and unwaived.** A29 completed this independent
review on 15 November 2026. A28 authored the three additional state captures;
A29 inspected and checked them independently. A29 did not rebuild or rerun the
application, alter the screenshots, or replace the original capture receipts.

Read complete `AGENTS.md` and `docs/PLAN.md`, the
[percussion contract](../PERCUSSION_REFERENCE_CONTRACT.md),
[A11 contract review](PERCUSSION_REFERENCE_CONTRACT_REVIEW.md),
[A23 raster note](../development/2026-11-15-audio-continuation/notes/A23.md)
and the current README UI section. Directly viewed the original reference,
the previous wide application frame, all eight current full frames and all
three added full frames. The detailed [reference gap review](../design/AUDIO_REFERENCE_GAPS.md)
records material, vertical and broader composition findings; the
[A29 JSON receipt](../development/2026-11-15-audio-continuation/reports/A29-visual-review.json)
contains independent identity/state checks and measurements.

## Source identity and retained evidence

Both capture sets ran the executable with SHA-256:

`32cea4a90bfc3d742550ad3725c1bf007c2fdc72e111b8b5ab1e95026033daf6`

Their recorded Git base is `276664ee8570c208bb007cca59f496963ca13ef5`, tree
`295abfec00bdd874b89eea159f816400f994f7b6`. The implementation was an uncommitted
overlay at capture. **That base commit does not identify the changed UI.**
The [author's build receipt](../development/2026-11-15-audio-continuation/reports/w03-source.json)
pins 16 sources and the binary; the capture observes a broader 115-file
production inventory and 13 build inputs. A29 independently rehashed all of
these against the current files and executable. They matched. This review
does not turn an author build receipt into a hermetic independent compilation
attestation.

| Critical input | SHA-256 |
| --- | --- |
| `UiModel.cpp` | `aa4fa2e06c4a8ccb17ba1b1cdfed498372b3626152bb2b8c6c53682b775931c9` |
| `InstrumentView.cpp` | `97971753c23e7da93d84586cf66ede2a3d9a04f319ddaf4831ba83ea7955f7d6` |
| Original reference JPEG | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| Contract version 1 | `3d7e9414a6159b6c7ad966312f0d11d03ccc9e3122242735ea1df116851735d8` |
| Current wide Play PNG | `265a6b718ffb85e67be0ea0920bb7b4a40bb5233add71bfd05bec9f55c85f149` |
| Current wide Play decoded RGBA | `cdce20bc98b031a34ff5dca44311759ea9766e74b6f892ed6ebfa4ee0dbc418e` |

All **39 original manifest files** and **18 additional manifest files** matched
their recorded sizes and SHA-256 identities. Every PNG decoded to its recorded
RGBA identity and dimensions. The original 39 files plus their manifest remain
byte-identical to the integrator's preserved capture directory. The earlier
published product wide frame still matches its historical Git bytes. The
discarded native BMPs cannot be rehashed now; their recorded lossless conversion
receipts are retained, while the PNG bytes and decoded pixels were independently
verified. The [original provenance](../../examples/demos/standalone-audio-preview-v1/provenance.json)
correctly keeps its historical “visual review not performed by this utility”
statement; this independent review is a separate artifact.

## Eight original full application frames

| Actual figure | Size | Independent visual finding |
| --- | --- | --- |
| [Play reference](../../examples/demos/standalone-audio-preview-v1/images/play-reference-1672x941.png) | 1672×941 | New narrow percussion bodies and exterior legends; ON / NORM / SLOW / 2ND; REQUIRES UPPER B; fixed C-sharp Upper sound while editing B. |
| [Play default](../../examples/demos/standalone-audio-preview-v1/images/play-default-1280x900.png) | 1280×900 | Existing compact percussion layout with interior captions; full-width lower pedalboard. |
| [Play minimum](../../examples/demos/standalone-audio-preview-v1/images/play-minimum-960x700.png) | 960×700 | Compact controls, combined eligibility heading, both manual/preset areas and pedalboard visible. |
| [Flat minimum](../../examples/demos/standalone-audio-preview-v1/images/flat-minimum-960x700.png) | 960×700 | Flat materials and existing percussion order; visible held notes and focus. |
| [Rotary reference](../../examples/demos/standalone-audio-preview-v1/images/rotary-reference-1672x941.png) | 1672×941 | Decorative cabinet with explicit read-only/disconnected audio and unavailable physical quantities. |
| [Rotary minimum](../../examples/demos/standalone-audio-preview-v1/images/rotary-minimum-960x700.png) | 960×700 | Responsive read-only cabinet/status layout; content remains visibly separate from the concept's controls. |
| [Service reference](../../examples/demos/standalone-audio-preview-v1/images/service-reference-1672x941.png) | 1672×941 | Six information panels, live copied holds/controls, and explicit unconnected/unmeasured module status. |
| [Service minimum](../../examples/demos/standalone-audio-preview-v1/images/service-minimum-960x700.png) | 960×700 | Same information roles in smaller panels; smaller type merits physical-display readability review. |

For every case, A29 independently asserted the diagnostic data against explicit
expected controls. Desired controls, final applied controls and the native
control report match. The final screenshot record equals the last painted and
before-shutdown presentation records, with current acknowledged copied state,
no pending controls and the requested workspace/presentation/dimensions. Four
targets remain held: Upper MIDI notes **60 and 64**, Lower **67**, and pedal ID
**3**. The original replays also retain a held-state observation before the Upper
B 16-foot drawbar edit from 7 to 8, while the applied Upper fixed C-sharp route
remains selected. These are real control/ownership facts; held targets alone do
not prove audibility or physical-organ fidelity.

## Three additional actual percussion states

| Actual figure | Applied route / retained values | Independently observed focus |
| --- | --- | --- |
| [Eligible Upper B](../../examples/demos/standalone-audio-preview-v1/percussion-states/images/eligible-upper-b.png), 1672×941 | Enabled adjustable B; ON / SOFT / FAST / 3RD; UPPER B ROUTE ACTIVE | HARM: 472 cyan pixels; bounds `(418,150)`–`(492,198)` |
| [Fixed D, OFF](../../examples/demos/standalone-audio-preview-v1/percussion-states/images/fixed-d-off.png), 1400×820 | Fixed D with remembered B; OFF / NORM / SLOW / 2ND; REQUIRES UPPER B | PERC: 420 cyan pixels; bounds `(137,150)`–`(199,197)` |
| [Cancel, stored ON](../../examples/demos/standalone-audio-preview-v1/percussion-states/images/cancel-stored-on.png), 1400×820 | Disabled Upper route with remembered B; ON / SOFT / FAST / 3RD; REQUIRES UPPER B | DECAY: 420 cyan pixels; bounds `(282,150)`–`(344,197)` |

Focus rectangles above are exclusive on the right/bottom. A29 counted exact
RGBA `(165,228,223,255)` pixels independently and inspected the actual cap
outline and footer. The replay navigation supports the intended focus target;
normal semantic focus IDs are **not** present in the diagnostic schema and are
not claimed as directly logged. This capture set shows three focus positions;
all-four-slot behavior is covered by separate geometry/input/raster evidence.

All three frames pass the same independent final-state, painted-hold and
acknowledgement checks. Applied Upper eligibility is derived from route enabled,
no fixed registration and selected bank B; stored percussion ON is a separate
value. The cancelled route therefore correctly retains ON. Both values of each
switch domain appear across this set, with correct HARM and DECAY meanings.
The recorded [provenance](../../examples/demos/standalone-audio-preview-v1/percussion-states/provenance.json)
and [reproduction guide](../../examples/demos/standalone-audio-preview-v1/percussion-states/README.md)
retain exact replay, controls, diagnostics and image identities.

The two 1400×820 combined headings are byte-for-byte identical in the checked
RGBA region `(62,126)`–`(460,150)`. No Cancel-specific heading corruption is
demonstrated. Their small type remains a general readability consideration,
separate from pixel correctness and desktop accessibility qualification.

## What the separate raster evidence establishes

A29 checked the [A23 final report](../development/2026-11-15-audio-continuation/reports/w04-a23-paired-final.json),
[build receipt](../development/2026-11-15-audio-continuation/reports/w04-a23-build-receipt.json)
and [comparison implementation](../../tools/qualify_percussion_raster.py).
Independently resummed totals are **66 pairs, 208,102,766 compared pixels,
1,297,684 changed pixels, zero escaped pixels and 28 exactly identical inactive
pairs**. Current source and comparison-tool hashes match; historical source
hashes also match `git show` of the recorded base. The report uses genuine
old/current UI objects with shared drawing inputs and a separately retained
build receipt. Its 11 retained input/output identities, including both helper
executables, also matched on rehash. A29 reviewed this evidence and did not
rerun its helper builds.

The final mask uses pixel-center arithmetic for exactly one outward device
pixel around the union of the permitted old/new percussion regions. Inactive
cases have an empty mask. This supports the scoped unchanged-neighbor and
inactive-output claim under identical state, including the reported scale/clip
cases. It does not compare the whole application to the reference artwork.
The time-running actual galleries have callback/frame/status variation and
cannot independently establish the same pixel-containment result. Earlier
evidence and the tightened final report remain retained.

## Limits and publication requirements

The eleven actual frames use SDL dummy audio/video with the software renderer,
equal logical/drawable sizes and no native MIDI backend. Their retained
diagnostics show audio/render progress, zero reported render/nonfinite/overrange,
queue or rejected-command failures, and clear held/running state after joined
shutdown. These facts qualify the recorded software runs. They do not qualify
physical devices, a native desktop display, high-DPI usability, deadline margin,
semantic accessibility, connected scanner/Leslie processing or instrument
fidelity.

The approximate **27-pixel vertical gap**, differing bright face/material
profile, and wider header/rack/manual/cabinet composition remain explicit in
the [gap review](../design/AUDIO_REFERENCE_GAPS.md). No inventory count, passing
test total, source-art crop or admitted subset establishes whole-interface 1:1.

The integrator should link the current gallery, state guide and this review
from README and bind the eventual published production files to the recorded
source hashes. Preserve the original images/receipts and the old gallery.
Future source changes need newly qualified captures. A later material-only
experiment or coordinated panel reflow requires its own bounded contract and
independent review; neither is already approved or proved by this admission.
