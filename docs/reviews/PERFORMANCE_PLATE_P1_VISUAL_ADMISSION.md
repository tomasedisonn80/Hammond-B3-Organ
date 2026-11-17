# P1 performance plate — independent full-frame visual admission

Reviewer **A24**, actual worker `/root/w04_a24`, wave 4, 17 November 2026 UTC.

## Decision

**ADMIT the P1-only full-frame visual change at the captured source.** Direct
inspection of all fifteen actual P1 application frames, all fifteen matching
prior T3 frames, and the unchanged reference JPEG found no new scoped visual
blocker. The darker, more textured performance-plate interior fits the adjacent
rack metals. No new vertical seam, interpolation band, bright grain cluster,
detached lighting, clipping, unreadable control/eligibility text or altered child
appearance was observed in these retained views.

This is independent visual admission under the
[frozen P1 contract](../design/PERFORMANCE_PLATE_P1_CONTRACT.md) and
[A11 design admission](PERFORMANCE_PLATE_P1_DESIGN_ADMISSION.md). It does not
turn the original failed paired report into a pass, grade paint timing, or
accept the whole interface. **Literal whole-interface 1:1 remains unmet and
unwaived.** Root retains integration and the other acceptance gates.

## Evidence identity and method

The [machine-readable review](../development/2026-11-16-console-completion/reports/p1-visual-admission.json)
records every inspected candidate and prior path, complete file SHA-256,
decoded RGBA SHA-256, dimensions, per-frame finding, evidence limits and
remaining gates. Each image was opened as a complete frame with the image
viewer. No contact sheet, cropped quiet patch or fixture export substituted
for full-frame application inspection. In particular,
`reports/p1-after-case0.png` is a painter fixture, not one of these app captures.

| Input | SHA-256 |
| --- | --- |
| Unchanged [reference JPEG](../design/atlas-cover-reference.jpg), 1672×941 | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| Frozen P1 contract | `20c8839d38229bf24d983eac0baad7381f601c4e6763bbbe556bcdfa6c75ae45` |
| Captured P1 application | `7b812bbbfd86779bb01cb76fe225309dd2d3101d08c6bb7fe2d6730e9d02c2c9` |
| Captured P1 `InstrumentView.cpp` | `8ca5c05138ed4cd12fe8ef416ea35a3d78a8a3c4915645f53d8c0c0df2fcf927` |
| Prior T3 application | `010d43dc764d627733b29093cc8436010fba6922a98a547cc8a1ad69006dc8e3` |
| P1 [provenance](../design/native-gallery-console-p1/provenance.json) | `2ddb1e4acecfde83f0b804b313dc17c09e88411086007793fac3331e1c3ee614` |
| P1 [manifest](../design/native-gallery-console-p1/manifest.json) | `f1f37e334da3e3f083121b6323972124e8d915dd290e5a8adf7e1208a006423c` |
| Prior T3 [provenance](../design/native-gallery-ui-delivery-title/provenance.json) | `538c1eca336f7ccbb73a0b9bf4c9dcf330c50f4c59491f9f8e2315856646b5bd` |
| Prior T3 [manifest](../design/native-gallery-ui-delivery-title/manifest.json) | `78bb8e16abee45fd7c979a0f33b063d0fb2a19b065384c6384a913aba30880f7` |

A24 independently hashed the retained images, current application and painter
bytes. Both galleries' **69 manifest entries** match their retained sizes and
hashes, and all **15 decoded images per gallery** match provenance dimensions
and decoded identities. These are read-only identity checks, not execution or
an independent compilation attestation. The current base commit alone does
not identify the captured overlay.

P1 capture provenance reports **15/15 passed**, explicit replay scale **3**,
**5400 ms** duration and unchanged recorded source, build and input identities.
It identifies dummy SDL audio/video and the software renderer. The original
1800-ms capture failure remains separate. Native BMPs were removed after the
capture utility's recorded lossless conversion; this review inspected the
retained PNGs. Gallery runtime meters and inspection counters can differ from
the earlier captures. Their differences are not an exact-state preservation
test and are not mistaken for P1 changes.

### Complete inspected P1 inventory

Every row has a same-name prior T3 full frame, also directly inspected and
bound by exact file and decoded hashes in the machine-readable review.

| Actual application image | P1 PNG SHA-256 |
| --- | --- |
| [Canonical Play, 1672×941](../design/native-gallery-console-p1/images/play-reference-1672x941.png) | `a8c9bcb9b35910e09dc040766693553e6385f57e94e144118dcb3bb4eae2b56c` |
| [Minimum active Play, 1400×820](../design/native-gallery-console-p1/images/play-minimum-active-1400x820.png) | `09aa6e39ab64758cd271fd09534d942d2f1f645bcc10b6339b31a93f424f5815` |
| [Wide Play, 1920×1080](../design/native-gallery-console-p1/images/play-wide-1920x1080.png) | `b29711df483649262feafaa33324a80848938153e789c04877f7d8181d36aaec` |
| [Short/wide Play, 1920×820](../design/native-gallery-console-p1/images/play-header-wide-1920x820.png) | `ef747f7d07c7f83ed71e085492bc925a382b32e366a8c73886c18b2a769a72f9` |
| [Tall Play, 1400×1080](../design/native-gallery-console-p1/images/play-header-tall-1400x1080.png) | `c9c058b3b7b42be1f67149afc9ae486c30aa71a30df077326446f60bb6c5e569` |
| [Pedal focus, 1672×941](../design/native-gallery-console-p1/images/play-pedal-focus-1672x941.png) | `029283927a32361a00579a76cd110127d2aa0587c41eccfc8378ab0d93a6f08d` |
| [Toolbar focus, 1672×941](../design/native-gallery-console-p1/images/play-toolbar-focus-1672x941.png) | `11f72e268a80994030e105edfc29a207e1dfa1f64b3d4d5fb61547e132920e37` |
| [Default Play, 1280×900](../design/native-gallery-console-p1/images/play-default-1280x900.png) | `2b5e0c332f0114b70cc320e885de84290f2cec9e8443e97b8233a53b6fb60f6d` |
| [Minimum compact Play, 960×700](../design/native-gallery-console-p1/images/play-minimum-960x700.png) | `b110da6eb0ed0b97477e7e4cf7bc1f8f29c3997b59c17dcc640fff62993789b5` |
| [Flat, 1672×941](../design/native-gallery-console-p1/images/flat-reference-1672x941.png) | `f1f3aacf81169d38869fb525f3725c3afaa1d2d99cac0485b319eb09c50716eb` |
| [Flat minimum, 960×700](../design/native-gallery-console-p1/images/flat-minimum-960x700.png) | `dfa5c156c856048ec3de28e4d3affebbdb5257943fe6313b06c6cb949d690214` |
| [Rotary, 1672×941](../design/native-gallery-console-p1/images/rotary-reference-1672x941.png) | `91c4fab22d2e3d5b34909d570873b12fd29ca1578be213e1e456e884063edf8d` |
| [Rotary minimum, 960×700](../design/native-gallery-console-p1/images/rotary-minimum-960x700.png) | `05c307f91e477d3d080e6d316ba1c06c477ac3f181d561b342e24ec18ed3b46e` |
| [Service, 1672×941](../design/native-gallery-console-p1/images/service-reference-1672x941.png) | `ae206e1179aa85636d73d9d0d5738388479c2a8c3ebab4ec6c95a953b41aa708` |
| [Service minimum, 960×700](../design/native-gallery-console-p1/images/service-minimum-960x700.png) | `9230a1399ba1addb0ab4f2775f26481351eec880491912f50d6ab254c281699f` |

## Direct visual findings

**Material and attachment.** In all seven active Dimensional Play views, the
left side is darker than the prior smooth plate, while the upper middle has a
restrained light lift. The fine, scattered grain reads as part of the metal
surface. It does not form a bright focal cluster, vertical seam or horizontal
interpolation band in the complete inspected frames. The existing perimeter,
screws, rules, divider and control shadows continue to seat the surface within
the instrument. The plate is still an artistic approximation, with different
microtexture from the reference; a local visual improvement is not pixel parity.

**Controls and eligibility.** The four button faces, headings and underlabels
remain distinct from the background at canonical, minimum-active, wide and
both unequal-aspect sizes. The expression track/handle and `75%` readout remain
visible; both mixture wells, caps and `8`/`0` values remain clear. The small
`REQUIRES UPPER B` line stays complete below the percussion captions. No new
overlap or clipping was observed. This is a retained-frame reading judgment,
not a measured contrast, comfortable-reading or real-DPI admission.

The canonical frame visibly retains stored percussion On while Upper sounds
fixed C#, so the eligibility message matters independently of the On button.
Service likewise retains `On / Second / Normal / Slow / Upper B ineligible`.
These visible distinctions are not evidence that A24 exercised the underlying
musical behavior.

**Focus and held notes.** Cyan focus around the Upper 16-foot control remains
complete in the standard views. In the two dedicated scenes, the far-right
pedal's cyan rectangle and the selected `PEDALS` toolbar control's cyan border
are visible and contained. Gold held-note cues remain distinguishable on both
manuals and the pedalboard. The darkened plate creates no competing cyan or
held-note-like marks.

**Other layouts.** P1 is inactive in eight inspected views: default and minimum
compact Play, two Flat frames, two Rotary frames and two Service frames. They
retain the prior arrangements and child appearance. Compact layouts keep
explicit percussion labels and the eligibility line; Flat retains its distinct
rectangular controls and keys. Rotary retains the decorative-cabinet disclaimer
and six read-only rows. Service keeps all six cards, including the minimum-size
bank-memory wrapping and percussion eligibility. Rotary and Service tab focus
is visibly complete. Runtime snapshot text and footer meters differ without
indicating a structural visual change.

## Reference legibility and semantic caveat

The unchanged reference is generated design concept art from the cover/page
409, as recorded in its [provenance](../design/atlas-reference.json). It provides
material and composition direction, not measured geometry or an authoritative
control specification. Its large button legends are visually clear, but
`NORM` above `DECAY` and `FAST` above `HARM` are incorrect semantic targets.
The app correctly retains `ON`/`PERC`, `NORM`/`VOL`, `SLOW`/`DECAY` and
`2ND`/`HARM` in the wide presentation. Do not reverse those corrections to make
the art match.

The app's nominal expression and pedal mixtures, real preset inventory,
runtime state and unconnected-model notices also remain truthful despite their
visible differences from the illustration. Correct inventory and live meanings
must survive any later visual work. The reference does not supply corresponding
operational Flat, Rotary or Service screens.

## Whole-interface residuals and practical next targets

These observations retain the broader
[whole-interface admission boundary](WHOLE_INTERFACE_DELIVERY_ADMISSION.md)
while recognizing that T2/T3 and P1 are now present in the inspected source.
They are not a request to reassign other owners' unfinished work.

| Region | Remaining difference | Concrete next work |
| --- | --- | --- |
| Metal fields and surrounds | P1's sampled grain is not the source microtexture. Header and cabinet surrounds still differ in grain, bevel, rules and light falloff. | Reconcile the separate H1 owner and its timing evidence before header edits. Independently freeze a cabinet-surround or other bounded material slice against a genuine current baseline. |
| Wood, cheeks and apron joins | Straight rails, thin joins, side grain and cheek illumination differ from the reference's sculpted furniture. The live footer remains a prominent functional band. | Recover rim/apron ownership, then isolate one illumination or join region with protected controls and exterior containment. |
| Caps, wells and manuals | Hard rectangular wells, sharp cap bevels and regular key-front shadows differ from the source relief. Real 61-key manuals are denser than the illustration. | Review one cap/well or manual-lighting slice while preserving positions, hit geometry, numeric direction, key count, focus and held cues. |
| Type and small legends | T2/T3 are retained, but embossing/spacing still differs. Minimum-size utility labels, presets, eligibility, footer and Service rows remain small. | Run real display/DPI and keyboard journeys; separately freeze any small-type or hierarchy change with clipping and semantic checks. |
| Composition and meaning | Utility actions, expression/mixtures, 24 reversed presets, runtime notices, toolbar and pedals differ from the concept. Unequal-aspect cabinet letterboxing and empty spacing remain. | Preserve truthful nominal/unconnected labels and the actual inventory. Any layout refinement needs its own composition contract and matching state/focus journeys. |

For the README, use the admitted canonical P1 app image and matching gallery
provenance together. Describe this as a revised **inner performance-plate
material**, name the remaining differences above, and retain the unmet literal
1:1 statement. A heading or caption must not promote fixture case 0, a concept
image, the older T3 gallery, or a numerical pass into a current app capture or
whole-interface result. README editing remains with root or its assigned owner.

## Independent gate boundaries and handoff

The original [paired v1 report](../development/2026-11-16-console-completion/reports/p1-paired-v1/report.json),
SHA-256 `4895fdbb8f79e07cc4ad2b6d672807433a98e5a08689c323547432ca88725ab7`,
reports all **62 candidate numerical screens passed**, but **overall failure**:
both before and after Rotary and Service fail the remembered-workspace-focus
metadata oracle. These are four recorded failures across 34 pairs. A22/root
owns the independently reviewed focus-memory correction and any subsequent
paired admission. This visual review neither repairs nor supersedes v1 and
does not use its passing quiet patches as proof of visual quality.

The frozen eight-process timing comparison remains a separate gate; A24 ran no
benchmark and grades no timing result. Root must complete the corrected paired
evidence, affected existing suites and independent timing admission, preserve
any HOLD/failure, then integrate the admitted captures into current guidance.
Publication and hosted results must qualify the exact accepted source.

Still frames do not establish temporal shimmer, display smoothness, native
input, hardware behavior, audio correctness, physical calibration, semantic
accessibility, host compatibility, rights/packaging or signed release. All
M0–M9 exits and the standing 47 parameters, state 4/readers 1–3, 91 sources,
plugin UUIDs, nominal dry Engine and control/key inventory remain binding.
A24 changed only this review, its JSON and its worker note; no production
source, capture, build, native execution, benchmark, subagent, commit or push
was performed.
