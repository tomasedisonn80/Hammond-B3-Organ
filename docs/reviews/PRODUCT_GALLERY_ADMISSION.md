# Product gallery admission — 15 November 2026

**Admitted:** the eight normal views and three separately identified MIDI-overlay
views in [native product gallery v1](../../examples/demos/standalone-product-preview-v1/README.md).
A41 independently inspected every original PNG and the original atlas JPEG,
verified retained payload and pixel identities, and checked raw diagnostics,
replay intent, production inputs and the executable. No capture defect requiring
recapture remains. Admission covers the named native software captures using
dummy SDL; physical devices, displayed usability and literal reference equality
remain separate gates.

The [machine-readable audit](../development/2026-11-15-product-continuation/reports/A41-gallery-admission.json)
retains per-frame identities, observations, the initial review exceptions and
their source-based resolution. A40's author review was read as supplementary
prose; its pass was not used as independent admission.

## Exact inputs and manifest scopes

| Identity | Admitted value |
| --- | --- |
| Capture commit | `d556da017ea0a5d4f2d231416782dbc5066e58c2` |
| Capture tree | `a3150fd2489a50a430b02c01eadd5e0c180bc7f9` |
| Native executable SHA-256 | `7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852` |
| Normal capture tool SHA-256 | `83c214d6f0d6b0fc06910412f41f13a0f3286bebd034280a19d4e5e397875b1f` |
| Normal manifest SHA-256 | `3b3a05ff9d64eb3f14d79c4ce35041ff9e93045367619684960f181b45231d54` |
| Separate overlay manifest SHA-256 | `f9ffaea1363a2f7f2960d5f9e38de1d473548f4db2f3f9b1852e59931902dca4` |

The [normal manifest](../../examples/demos/standalone-product-preview-v1/manifest.json)
binds **39 files** under the normal capture contract. The
[overlay manifest](../../examples/demos/standalone-product-preview-v1/midi-overlay/manifest.json)
binds **18 files**, including its retained capture script, under a distinct modal
contract. The parent manifest is not a recursive attestation of the later overlay
directory. Both manifests exclude themselves and subsequent authored
README/review files; those review files are identified separately in A41's report.

A41 recomputed every listed file size/hash and both inventory digests. All
**108 qualified production files** match the retained build receipt, the current
files and the actual blobs in the named capture commit. All **13 selected
generated/library build inputs**, selected CMake settings, executable, tools,
controls, replay scripts and copied qualification reports match their recorded
identities. Recorded before/after inputs are unchanged. Linux Release has
`HAMMOND_ENABLE_MIDI=OFF`; raw runtime observations identify SDL 2.32.10,
dummy audio/video, software rendering, equal logical/drawable dimensions and
48 kHz / 512-frame stereo native-float32 audio.

The supplied [build receipt](../../examples/demos/standalone-product-preview-v1/inputs/source-qualification.json)
records an earlier target build at `b9d352a8`. Its production inputs and binary
are still identical. Its standalone CMake-rule hash predates the later test-probe
rule change; the root CMake hash still matches. This review does not promote that
earlier receipt into a complete later build-rule, compiler or dependency
attestation. A41 performed no build or application launch.

### Lossless-image evidence and unavailable original BMPs

For all eleven frames, A41 decoded the retained PNG, checked RGBA mode and exact
dimensions, and recomputed its decoded-pixel SHA-256 against provenance. PNG
file hashes also match both provenance and manifests. The recorded capture code
checks decoded BMP/PNG equality before removing each BMP.

**The eleven original native BMP files are unavailable.** Their recorded file
hashes and decoded-pixel hashes remain; A41 did not reconstruct raw files or
independently reopen the removed originals. The retained PNGs agree with the
recorded native-pixel identity. This supports the stated lossless conversion
within that retained-evidence boundary.

## Raw state and replay admission

A41 independently read the replay files and modeled their keyboard intent,
compared complete desired/applied controls with the original state and single
live edit, checked obtained runtime facts and shutdown relationships, and applied
the strict native presentation/MIDI schemas directly to all eleven diagnostic
files. The normal capture predicate was rerun on eight raw diagnostic files as
one secondary check. The overlay author's validator was not executed as the
independent oracle.

**Normal views:** all eight recorded native processes exited 0 with empty
stdout/stderr. The 1,800 ms scripts deliver 66 events, or 68 for Flat. Upper
60/64, Lower 67 and pedal 3 remain held at the captured endpoint. Retained Upper
B 16-foot changes from 7 to 8; Upper fixed C# still sounds and Lower uses bank A
(A# preset), while both visible editor banks are B. Expression remains 0.75,
pedal mixtures 8/0 and percussion On/Second/Normal/Slow. Complete final controls
match, command acknowledgment is current, no controls/save request remains
pending, and the original state-file bytes are unchanged.

**MIDI overlay:** all three processes exited 0 with empty stdout/stderr. Their
4,800 ms scripts deliver 98 events, or 100 for Flat. Raw observations witness
the same four held owners before and after the drawbar edit, then their
acknowledged release after Ctrl+M. Modal entry uses scoped `ReleaseUiNotes`;
the individual Note Off counter remains zero. The independently reconstructed
and recorded focus sequence is
`0,1,2,3,4,5,6,7,8,9,10,0,10,9,8,7`. All eleven indices occur in actual painted
observations; direction is focused in the final image.

In every case, the screenshot observation equals the last painted and
before-shutdown presentation. Copied state is current, pointer capture is absent,
and no audio failure, Session overflow/rejection/recovery or fault is recorded.
MIDI is explicitly **unavailable** before and after shutdown, with generation
zero and no device, discovery, packet or decoder activity.

The modal's illustrative CLI settings are selected/configured **20/100,
Inverted**, with active calibration null and no reconnect/release pending.
The visible **ACTIVE CALIBRATION: none (inactive)** caption agrees with those
facts. These captures do not exercise selected/configured divergence, Apply,
reconnection or active controller decoding.

### Initial audit exceptions retained

The first independent audit incorrectly required post-join
`discarded_commands == 0`. Every capture instead records one discard, with
`resolved_sequence - last_applied_sequence == 1`. Source inspection shows that
main records the acknowledged replay endpoint, queues an ordinary final
window-close release, then closes audio; `Session::stop` clears owners and
discards remaining queued commands. The existing native shutdown contract
explicitly allows this relationship. All replay commands were applied before
close; normal final sequences are resolved/applied **7/6**, and overlay **8/7**.
Stopped state has no owners. The corrected source-based checks pass all eleven
unchanged diagnostics.

The first audit also excluded only Markdown prose and therefore flagged the
later `author-review.json`. Its explicit outside-manifest review scope is
consistent with the capture contracts. Its identity is retained separately;
it is not raw capture evidence or an admission oracle. Both initial exceptions
remain in the JSON audit history. No native failure or image was rewritten.

After A40 completed, the integrator explicitly authorized A41 to replace the
overlay README's “independent validator” wording with “overlay validator” and
refresh only its corresponding byte/hash entry in the author review. A41
rechecked all 57 native payload files and both manifests afterward; they remain
unchanged. This correction distinguishes author validation from this admission.

## Direct visual review

| Original frame inspected | Observation |
| --- | --- |
| [Play 1672×941](../../examples/demos/standalone-product-preview-v1/images/play-reference-1672x941.png) | Complete manual footage, including correct `1 3/5'`; distinct EDIT BANK / SOUNDING rows, separated caps/readouts, cyan live-edit focus and four held markers. Cabinet and sidebar pedals fit. |
| [Play 1280×900](../../examples/demos/standalone-product-preview-v1/images/play-default-1280x900.png) | Compact rack captions, manuals/presets and lower pedal row fit; focused retained edit and held targets remain visible. |
| [Play 960×700](../../examples/demos/standalone-product-preview-v1/images/play-minimum-960x700.png) | Complete control groups fit with shallow manuals and small preset legends. No obvious crop; comfortable native-display reading remains untested. |
| [Service 1672×941](../../examples/demos/standalone-product-preview-v1/images/service-reference-1672x941.png) | Six copied-state cards show current snapshot, 91 sources, 2/1/1 held targets and explicit unavailable/unconnected models. |
| [Service 960×700](../../examples/demos/standalone-product-preview-v1/images/service-minimum-960x700.png) | Six cards remain inside their allocations; bank memories wrap. Small labels and evidence text are dense, with no obvious crop in the inspected image. |
| [Rotary 1672×941](../../examples/demos/standalone-product-preview-v1/images/rotary-reference-1672x941.png) | Cabinet artwork is explicitly decorative; dry audio, unavailable rotor speeds, unacquired microphone geometry and unmodeled brake remain clear. |
| [Rotary 960×700](../../examples/demos/standalone-product-preview-v1/images/rotary-minimum-960x700.png) | Both columns and read-only facts fit; unavailable status is retained. |
| [Flat 960×700](../../examples/demos/standalone-product-preview-v1/images/flat-minimum-960x700.png) | Flat keys and controls preserve the complete visible groups, held markers and focused edit. |
| [MIDI 1672×941](../../examples/demos/standalone-product-preview-v1/midi-overlay/images/midi-reference-1672x941.png) | Centered modal shows all channels, endpoints, direction and actions, with inactive backend/calibration and direction focus. |
| [MIDI 960×700](../../examples/demos/standalone-product-preview-v1/midi-overlay/images/midi-minimum-960x700.png) | The 740×600 source-defined panel fits at (110,50), including both helper rows and Close. No modal crop or field overlap is apparent. |
| [MIDI Flat 960×700](../../examples/demos/standalone-product-preview-v1/midi-overlay/images/midi-flat-minimum-960x700.png) | The same values, truthful status and cyan focus remain visible in Flat presentation. |

Inventory was checked from `UiModel` constants, construction loops, visibility
and focus geometry, together with raw state and the inspected controls—not by
claiming a pixel count of every key. The **68 ordinary controls** comprise ten
common controls, four edit-bank buttons, 24 presets, 18 manual drawbars, four
percussion controls, expression, two pedal mixtures, three keyboard targets
and two octave controls. Playing arrays contain **61+61+25 = 147 keys**.
Play has 68 ordinary plus three roving-key focus stops; other workspaces expose
ten common stops. MIDI has eleven separate modal targets. The gallery's modal
traversal witnesses all eleven; it does not traverse all 71 Play stops.

## Reference relation and remaining work

A41 directly viewed the [original reference](../design/atlas-cover-reference.jpg)
and repeated the bounded warm-ink measurement on the new reference-size Play
PNG without resampling or registration. Title bounds are native
`[602,20,1065,53]` versus reference `[603,20,1067,53]`; subtitle bounds are
`[650,71,1020,83]` versus `[650,71,1021,83]`. The subtitle intentionally says
NOMINAL DRY ORGAN. Similar bounds do not establish identical lettering or
whole-frame equality.

The [existing gap review](../design/PRODUCT_REFERENCE_GAPS.md) remains relevant:
racks are higher/shorter than the concept; track wells, deck/rims and repeated
key transitions look more regular; full correct manuals produce narrower
individual keys; actual presets, pedals, utilities and device facts differ
from the concept's furniture. Minimum Service text, preset labels and modal
helpers remain a displayed-usability gate. The wide painter's containment and
relative-cost qualifications remain those of
[the frozen visual contract](../PRODUCT_VISUAL_REFINEMENT.md); this gallery
does not rerun that raster experiment or establish an interactive frame rate.

The next visual gate is an identified native display/DPI journey that reads the
smallest text, edits through endpoints, traverses focus, resizes with held owners
and observes real response. Preserve the stated model/device limits.
**Literal whole-interface 1:1 equality, semantic accessibility, real MIDI/audio,
physical display response, callback deadlines and measured instrument/cabinet
fidelity remain unproved.**
