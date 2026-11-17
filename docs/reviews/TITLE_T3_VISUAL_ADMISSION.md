# T3 revision 2: independent actual-frame visual admission

**A30, 17 November 2026; actual worker `/root/w05_a30`, wave 5.**

**Admit the scoped T3 visual gate for the identified revision-2 captures.**
The live title has visibly stronger strokes and a clearer brass edge than the
genuine pre-T3 title. At 1672×941, 1400×820 and 1920×1080, the complete words
remain readable, the `O` and both `A` counters remain open, and no clipping,
muddy overlap, detached halo or disproportionate brightness is apparent. The
subtitle, flanking rules and utility controls remain distinct. This decision
qualifies the actual-frame visual requirement only. **Literal whole-interface
1:1 remains unmet and unwaived.** Exact support/state comparison, coherent
integration, platform execution and publication retain separate acceptance.

## Scope and reviewed evidence

I read all standing instructions and the complete M0–M9 plan, the current
session README/checkpoint/actual ledger, the original
[T3 contract](../design/TITLE_T3_CONTRACT.md) and
[admission](TITLE_T3_ADMISSION.md), the
[revision-2 proposal](../design/TITLE_T3_REVISION_2.md) and
[admission](TITLE_T3_REVISION_2_ADMISSION.md), and the
[retained rejection](../development/2026-11-16-heading-title-continuation/reports/t3-v1-rejection.json).
The earlier T2 and whole-interface visual reviews supply their dated residuals;
the observations below come from directly opening the current original images.

The inspected `reference_header` retains the five ordered live Serif draws.
Comparing its complete bytes to the retained rejected painter confirms that
revision 2 changes only `y - 0.5F * scale.f` to `y - 0.125F * scale.f`.
The original fitting/anchor calculations, palette, order, caption and rules
remain present. This source inspection is not a new execution or compilation
attestation. I changed no production, test, capture or build input and ran no
native executable.

| Input or retained receipt | SHA-256 |
| --- | --- |
| Original T3 contract | `6e45c095331e4d2a32cb111ebe2be74b7fad3dd7f6fb89a675d68c4a0310cae7` |
| Revision-2 proposal | `e06ddb46f48a4d75c5c305474699223b41a0febc3e3db7d077048841356554e9` |
| Original reference JPEG | `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187` |
| Genuine pre-T3 painter | `94186192085435a756f9e1854e3aefe807407befa49e1cc978c07968436ca5db` |
| Revision-2 captured painter | `10865a6bad39bc0a254b8b3f4cf6b013bef48770a2b39c7e9f9a70f438d56366` |
| Genuine pre-T3 application | `e44eefc4fe37c879d2145e085f46f914f1703331aa32c72343f28a53d81eb56a` |
| Revision-2 captured application | `010d43dc764d627733b29093cc8436010fba6922a98a547cc8a1ad69006dc8e3` |
| Revision-2 gallery manifest | `f0c08dd473866057c615995daec5914b04065541ce7871037f216507d79fbe28` |
| Revision-2 gallery provenance | `6cbc5325ff17bc602796e9ecdd3ad394c08e774a3673fbd3413600b16f051268` |
| Revision-2 source qualification | `94d4a301732215e32a909dd73f027738b49831c9718e6eb6348e19934767aaad` |
| Seven title/caption crops' provenance | `94bb1f8e22334bba77952e66a1f2c92f5e9129206c24e2472b36d39047a9bb75` |

The completed [revision-2 provenance](../design/native-gallery-heading-title-v2/provenance.json)
records thirteen passed captures from **00:36:32 to 00:37:07 UTC on 17 November
2026**, with dummy SDL audio/video, software rendering and unchanged recorded
inputs. I independently verified every one of its **61 manifest payloads**
and all **13 decoded RGBA identities/dimensions**, with no mismatch. The same
checks pass for the genuine [T2 gallery](../design/native-gallery-heading-t2-v1/manifest.json)
and retained [rejected-v1 gallery](../design/native-gallery-heading-title-v1/manifest.json).
A gallery's capture status is not candidate acceptance; v1 remains rejected.

At identity inspection, all **148 capture-source entries** and all **229
source-qualification entries** matched their retained hashes. Comparing the
pre-T3 and revision-2 receipts finds only `InstrumentView.cpp` changed in both
inventories. All **213 protected inputs**, including the separately admitted
replay repair in `main.cpp`, are identical across T3. The current application
and the retained genuine `../t2-native/hammond_standalone` independently match
the executable identities above. These are bounded identity checks at the
captured source, not qualification of later integration changes.

The capture utility records lossless BMP-to-PNG verification followed by removal
of the BMPs. I inspected retained PNGs and checked decoded pixel identities;
I do not claim access to the removed BMP bytes. This is Linux software-renderer
evidence, with no real-display, physical-DPI, device or native-accessibility
admission.

## Exact images directly inspected

I directly opened the unchanged [reference](../design/atlas-cover-reference.jpg),
the three genuine T2 full frames below and all thirteen revision-2 full frames.

| Active view | Genuine pre-T3 PNG SHA-256 | Revision-2 PNG SHA-256 |
| --- | --- | --- |
| [1672×941 before](../design/native-gallery-heading-t2-v1/images/play-reference-1672x941.png) / [revision 2](../design/native-gallery-heading-title-v2/images/play-reference-1672x941.png) | `96a9fb295200307ffb7b459ee8a146d83579a881aafcd54b1cc73a7ed1b2b55c` | `fd4f92cfc0ad18fea020b3a2d8ce2142159089b18be3302f3d84f082aac9862b` |
| [1400×820 before](../design/native-gallery-heading-t2-v1/images/play-minimum-active-1400x820.png) / [revision 2](../design/native-gallery-heading-title-v2/images/play-minimum-active-1400x820.png) | `5ce28ab35d96b721f2ee31fe8ae48dd5ecd9667a455302e7ca29fb7bbdd3baa4` | `c2e602279814bab473afdf66b9e8a10f787e3bb6dfe87039600388c497f7a062` |
| [1920×1080 before](../design/native-gallery-heading-t2-v1/images/play-wide-1920x1080.png) / [revision 2](../design/native-gallery-heading-title-v2/images/play-wide-1920x1080.png) | `811fb42f55d017eba3c731d38f05a3d1993ec31379e556cc2b473a76a543509e` | `48ee9ea576ad267c02ff96e959cc21cd59f8d0738ddf95d3cbe95aa0b761c6e1` |

The ten additional revision-2 images are identified in the checked
[manifest](../design/native-gallery-heading-title-v2/manifest.json):

- Play default 1280×900 and compact minimum 960×700.
- Play toolbar-focus and pedal-focus variants at 1672×941.
- Flat reference 1672×941 and minimum 960×700.
- Rotary reference 1672×941 and minimum 960×700.
- Service reference 1672×941 and minimum 960×700.

I also directly viewed all **seven lossless RGB title/caption crops**: one
reference and before/after pairs at the three active sizes. Every source hash,
crop PNG hash, decoded RGB hash, dimension and pixel-for-pixel equality to the
recorded source rectangle passes independent verification. The
[crop provenance](../development/2026-11-16-heading-title-continuation/images/title-r2-crops/provenance.json)
records the exact rectangles and explicitly identifies these as derived
inspection images without resizing or retouching. The full frames remain
authoritative. Gallery frames retain runtime meter/counter differences and do
not replace the controlled same-state comparison.

## Direct visual findings

| View or feature | Observed result |
| --- | --- |
| Canonical 1672×941 | `TONEWHEEL ATLAS` has thicker, brighter strokes than the genuine before image. The round `O`, triangular `A` interiors, gaps between adjacent letters and the word space remain distinct. The narrow light edge and dark lower edge add relief without a detached glow or duplicated-looking outline. The complete first `T` and final `S` remain inside the header. |
| Minimum active 1400×820 | The complete title remains legible with open counters and separate serifs. No upper-row clipping or cut first/final letter is visible. Its edges are naturally coarser at this smaller raster size, but the additional weight does not close the small interiors. `NOMINAL DRY ORGAN` remains separated below it. Existing small utility and footer text is compressed at this size; that remains a broader readability/DPI limitation. |
| Wide 1920×1080 | The stronger strokes scale coherently, with clean spaces and no muddy doubled edge. Title size and placement still balance the navigation and utility groups. The warm face is prominent without visually overwhelming the selected Play button or the ivory manuals. |
| Caption, rules and controls | The truthful subtitle remains complete in all three active frames. Both title rules terminate clear of the glyphs; no stroke reaches a navigation or utility button. Save, Load, Help, Audio, MIDI, Panic and Flat remain visible. Three descriptive caption-strip comparisons, starting at the source's `67.5*sy` caption position, are byte-identical between genuine before and revision 2. This strip check is not a support mask. |
| Focus variants | The ordinary frame retains the cyan Upper 16-foot drawbar outline. The toolbar variant shows the cyan `PEDALS` button outline and its matching footer; the pedal variant shows the final pedal's cyan outline and `Pedal 25 of 25` context. The stronger title obscures none of those cues. Stills do not execute input or focus transitions. |
| Compact Play and Flat | The existing lighter title treatment remains visible in the inactive composition. Compact layouts retain their control arrangement; Flat retains its rectangular keys, caps and controls. The supplied screens show no added T3 outline or overlap in those paths. Exact whole-frame inactive equality remains the separate paired comparator's responsibility. |
| Rotary and Service | Both retain their lighter header treatment and explicit read-only/availability wording. Rotary distinguishes unavailable speeds from unacquired microphone geometry and says cabinet audio is not connected. Service still identifies the nominal generator, contacts/routing, disconnected Scanner/AO-28/Leslie and retained controls. Minimum Service remains dense; no new title-related obstruction is visible. |

In the active full frames, the complete mixed-fraction footage rows, numeric
drawbar values, Edit B selections, held-note highlights and pedalboard remain
visible. `NOMINAL DRY ORGAN`, `REQUIRES UPPER B`, `SOUNDING FIXED C#`,
`ROTARY AUDIO NOT CONNECTED`, `SCANNER / CHORUS: NOT CONNECTED`, audio/MIDI
status, `UNSAVED` and contextual footer text preserve their visible meanings.
Appearance does not establish complete state preservation or musical behavior;
those retain their model and interaction gates.

## Independent frozen-region observations

I decoded the original JPEG and genuine before/revision-2 PNGs to RGB without
resampling or color adjustment. The only density region was the original
half-open ROI `(590,14,490,46)` in `xywh` form. The predicate remains exactly
`2126*R + 7152*G + 722*B >= threshold*10000`, with **no hue restriction**.
Bounds below are half-open `xyxy` and accompany every required threshold.

| Encoded Y′ threshold | Reference count / bounds | Genuine pre-T3 count / bounds | Revision-2 count / bounds |
| --- | --- | --- | --- |
| 80 | 5,639 / `(603,20,1067,53)` | 4,150 / `(602,20,1066,53)` | 5,774 / `(602,19,1067,53)` |
| 100 | 5,415 / `(603,20,1067,53)` | 3,863 / `(602,20,1065,53)` | 5,512 / `(602,19,1066,53)` |
| 120 | 4,991 / `(603,20,1067,53)` | 3,601 / `(602,20,1065,53)` | 5,304 / `(602,19,1066,53)` |
| 140 | 4,502 / `(603,20,1066,53)` | 3,200 / `(603,20,1065,53)` | 5,029 / `(602,19,1066,53)` |
| 160 | 3,785 / `(603,21,1066,53)` | 2,690 / `(603,20,1065,53)` | 4,694 / `(602,19,1066,53)` |

The genuine baseline reproduces 3,863. Revision 2's **5,512** lies inside the
unchanged inclusive **[4,500,6,000]** band; its absolute count error against
5,415 is 97 instead of 1,552, a **93.75% reduction**. These are encoded-image
statistics, not physical luminance, font identity or whole-image similarity.
The higher-threshold excess also exposes a remaining difference: the live face
is more uniformly bright than the reference's varied metallic shading.

The canonical title/caption crop is pixel-identical to rejected v1, consistent
with the admitted revision's unchanged integer destinations at that transform.
This does not qualify v1: its minimum-size geometry failure remains in the
original rejection. The separate revision-2
[native material result](../development/2026-11-16-heading-title-continuation/reports/t3-r2-material-complete.json),
SHA-256 `59effaaf7cac03122d420f21543577b961a0f9342fe9946815cd14fa48f8417d`,
records **1,317 checks, zero failures**, including the unchanged 24 complete
header and 16 clipped-header cases. Its 1400×820 warm-ink top is 17 at renderer
scale 1 and 16.8 at scale 1.25. I inspected that result and the existing test
assertions; I did not rerun the native suite. The density observation and
warm-ink geometry remain distinct predicates with unchanged thresholds.

## Whole-frame residuals and remaining acceptance

| Region | Residual directly visible against the original reference |
| --- | --- |
| Title and other legends | T3 improves weight and introduces a brass edge, but its face remains more uniform and its relief shallower than the source. It does not reproduce the source's exact letter shapes, antialiasing or local lighting. Rack, performance and cabinet legends remain finer and flatter. |
| Header and panels | The broad header/performance/cabinet fields remain smoother, flatter and more evenly lit. Thin panel edges and rules differ from the reference's reflected light. The separate H1 proposal is not painted in these captures. |
| Wells, shafts and caps | The live wells remain hard rectangular recesses with narrow straight shafts; cap faces and bevels have less rounded reflection and shadow. Actual registration values and cyan focus introduce purposeful visible content. |
| Manuals and furniture | The two real 61-key manuals retain denser key divisions, regular fronts and shadows, straight rims and dark gaps. Reversed preset octaves, Edit A/B buttons and sounding labels differ from the illustrated cheek controls. |
| Layout, cabinet surround and apron | Utility buttons, nominal expression/mixtures, keyboard targeting, runtime notices, the pedalboard and opaque live footer differ from the concept's preset selector, vibrato/chorus and microphone/rotor controls. Decorative cabinet/reference-apron pixels do not make their surrounding live interface equal. |
| Small and alternate views | Minimum active utility/footer strokes and minimum Service information remain small or dense. Compact, Flat, Rotary and Service have functional layouts for which the single concept supplies no corresponding operative screen. |

These differences retain the actual musical inventory and truthful unconnected
labels; they are not permission to hide working controls or imply connected
models. Real display/DPI/input, native semantic accessibility, measured audio,
device/host/platform qualification and signed release remain separate exits.

At this review's handoff, the **full 158-case revision-2 support/state comparison
is pending**. Root must admit that stable-input report, required inactive
equalities and original default clip assertions, then complete affected coherent
UI/control qualification and refresh the README with accepted actual captures.
The current source-specific material pass and this scoped visual admission do
not bypass those gates. Preserve the rejected painter, six binaries, original
failure report and v1 gallery. Later painter/material changes require their own
source-bound review; this admission does not extend to H1 or whole-interface 1:1.
