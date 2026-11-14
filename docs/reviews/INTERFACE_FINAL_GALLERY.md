# Final native interface gallery review

Actual assignment **A46/60**, logical wave 8, worker
`/root/w08_a46_final_native_gallery`, 14 November 2026. This review covers the
new [v2 native gallery](../../examples/demos/standalone-interface-preview-v2/README.md),
its exact build/source basis, independently read pixel identities, actual
visual comparison and the root README's native UI/UX section. It makes no
product-source, CMake, workflow or shared-status change. Root owns integration,
publication and the complete session's remaining assignments.

## Result and scope

**Eight native application processes exited 0; all eight gallery cases passed.**
Every frame belongs to the actual standalone using explicit dummy SDL audio
and video and the software renderer. The final A34 legend/title and A36
Load-feedback code are present in the product source. This is a new gallery;
the 41 files in v1 still match their published blobs. No screenshot from v1
was relabeled as current and no A31 injected-renderer frame substitutes for a
full-application capture.

| Gate executed by A46 | Result |
|---|---|
| Existing native executable and A44 source/build/report admission | Passed; same 3,707,640-byte MIDI-on executable |
| Product source versus published commit and A44 snapshot | All 98 observed files match; no product overlay |
| Capture input stability | 98 product files, 13 generated/library files, selected config, executable, harness, author report and input files unchanged |
| Actual native capture/replay/diagnostics | Eight runs passed; 66 events per dimensional case, 68 for Flat, 1,800 ms each |
| Held state and complete replay control state | Upper 60/64, Lower 67, pedal 3; retained Upper B 16-foot edit 7→8; fixed Upper C# and Lower bank A preserved |
| Painted frame and copied inspection | Requested workspace/presentation/dimensions, current snapshot, no pending controls, screenshot equals last painted and pre-shutdown presentation |
| Native progress and shutdown | Audio callbacks and rendered images present; clean joined shutdown clears owners/running state; no MIDI discovery/input use |
| Retained payload and decoded pixels | Separate reader recomputed all 39 manifest entries and eight RGBA PNG dimensions/pixel hashes |
| Visual inspection | All eight full images and the unchanged original reference viewed |
| Storage and historical preservation | Eight PNGs total 2,677,186 bytes; complete v2 below 3 MB; v1's 41 files unchanged; no BMP/binary/cache payload |

This keyboard scenario does not exercise all 47 parameters or every tool. The
47 parameter identities, `B3CONTROLS4`, readers 1–3, 91 sources, full 61+61
manuals, 25 pedals and 24 reversed presets are preserved by unchanged product
source and visible inventory. Existing separate
[A34 raster/legend evidence](../development/2026-11-14-interface-continuation/session34-preset-label-polish.md),
[A36 Load-feedback evidence](../development/2026-11-14-interface-continuation/session36-status-clarity.md)
and [A37 native operator journeys](../development/2026-11-14-interface-continuation/session37-final-operator-flow.md)
retain their own exact sources and observed controls. The gallery does not
upgrade those gates to physical display, pointer or device qualification.

## Exact source and build basis

Capture HEAD and committed tree stayed:

- Commit: `8673713a484c40e26ac7810c7c4cbc22fa874426`.
- Tree: `e11bd68d6051f663631579ef235325a8775f8133`.
- Executable: `../build-native/apps/standalone/hammond_standalone`.
- Executable SHA-256: `bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2`.
- Renderer `InstrumentView.cpp`: `920f58ca287eca607632698c52a1e1fa819eb623a0be4828f082b2c6b0701912`.
- Harness: `17aafb70e87a2fd557317e04802e62a4d935d2f2b93bf65a2df0d688c5a16545`.

A44 configured and invoked the native Release target build, exercised actual
install/relocation paths, and retained the identical executable. Its MIDI-on
target was already up to date; this is not a fresh independent compilation
claim. A46 received a read/capture lease and ran no configure or build command.
The executable also matched the frozen `../a36-status-bin/hammond_standalone`.
The supporting records are
[A44 build result](../development/2026-11-14-interface-continuation/reports/a44-build-result.json),
[post-build source](../development/2026-11-14-interface-continuation/reports/a44-midi-on-source-after-build.json),
[package refresh](../development/2026-11-14-interface-continuation/reports/a44-package-refresh.json)
and [final packages](../development/2026-11-14-interface-continuation/reports/a44-final-package-result.json).
Their file hashes are pinned in the compact
[A46 qualification](../development/2026-11-14-interface-continuation/reports/a46-source-qualification.json),
copied unchanged into the gallery.

The qualification's `source_sha256` map deliberately contains only ten
mandatory renderer/drawing/UI/inspection/main/reference files. Separately, the
[preflight](../development/2026-11-14-interface-continuation/reports/a46-source-before.json)
compared every one of the broader 98 observed product files to A44 and both
the actual HEAD and published source blobs. All matched. The
[post-capture snapshot](../development/2026-11-14-interface-continuation/reports/a46-source-after.json)
and provenance retain zero product or selected build drift.

| Inventory algorithm and boundary | Digest |
|---|---|
| A44: sorted `path + NUL + SHA + newline`, 98 files | `ddf4f7658cfa9ed49ddac87902788c65531697551faab4dadd1dd57709d9e9ad` |
| Harness: compact sorted JSON of path→size/SHA, same 98 files | `6addb1ff056e07a8dd50d587552814a99fd05921a1512ace39396a232efdfd4c` |
| Harness: same size/SHA encoding, 13 selected build inputs | `7188e8d9a7c994e3072bda1cd52d4b200cf26dc16a776d34cc0476d869e70b67` |

These differently encoded inventory digests must not be compared as though
they hash the same serialization. An initial ad hoc preflight mistakenly did
so; it stopped before creating qualification/gallery files or launching a
native process. The corrected derivation and explicit failure boundary are
retained in
[preflight correction](../development/2026-11-14-interface-continuation/reports/a46-preflight-correction.json)
and [preflight program](../development/2026-11-14-interface-continuation/reports/a46-prepare-capture.py).
The application and capture harness were not modified.

The 13 files cover selected generated embedded headers, compiled nominal
profile and native/core/SDL static libraries. Eight overlap A44's selected
build identities and match exactly. Four additional cache/link/flags/capability
identities also stayed unchanged through capture. Recorded configuration is
Release, standalone and MIDI ON, pinned SDL/RtMidi roots and SDL_ALSA OFF.
The process actually reported SDL 2.32.10, dummy audio/video, software rendering,
48 kHz stereo float and 512-frame buffers; MIDI was available as ALSA but its
source remained `none` and discovery requests stayed zero.

Concurrent workflow, CMake test-budget and documentation edits existed outside
the product inventory. The 98 product files exclude tests, build/install rules
and unrelated docs; selected configuration/library snapshots do not describe
the entire dependency/compiler graph. The generic harness text refers to an
observed production overlay, but the additional blob comparison establishes
that these captured **product** files were committed. It does not claim the
whole worktree was clean, every source/dependency was built afresh, hermetic
reproducibility or signed provenance.

## Native state, pixels and independent readback

The exact commands and environment are in the
[capture process record](../development/2026-11-14-interface-continuation/reports/a46-capture-process.json)
and [gallery provenance](../../examples/demos/standalone-interface-preview-v2/provenance.json).
The immutable input holds Upper 60/64, Lower 67 and pedal 3, then makes the
real keyboard drawbar edit while retaining fixed C# sounding and Lower bank A
selected by A#. Final memories are
`UA 123456780 / UB 865434253 / LA 765434242 / LB 008000000`.
Expression stays 0.75, pedal positions 8/0 and stored percussion
On/Second/Normal/Slow with Upper B ineligible. No Save is sent.

Every case checks pre-edit held observation, all desired/applied controls,
final owners and command acknowledgment. The screenshot is the final painted
frame at or after 1,800 ms with current copied inspection and no pending
controls. Later shutdown clears owners/running state and leaves MIDI closed,
quiescent and diagnostically stable. The eight native processes took about
1.88–2.02 seconds each; these wall times are observations, not deadline claims.

The producer hashes each native BMP, converts to PNG and verifies decoded mode,
dimensions and all pixel bytes before removing that run's BMP. A separate
[reader](../development/2026-11-14-interface-continuation/reports/a46-verify-gallery.py)
then recomputes PNG bytes, RGBA pixels and all manifest entries without importing
the producer's validation. Its
[result](../development/2026-11-14-interface-continuation/reports/a46-gallery-verification.json)
records every image's exact file/pixel hashes, size, event count and native
progress counters. That is independent artifact readback, not a second native
execution or independent source build. Original BMP identities remain in the
producer record; no removed BMP was reconstructed as evidence.

| Native frame | Dimensions | PNG bytes |
|---|---:|---:|
| Play reference | 1672 × 941 | 643,593 |
| Play default | 1280 × 900 | 172,776 |
| Play minimum | 960 × 700 | 131,668 |
| Service reference | 1672 × 941 | 410,393 |
| Service minimum | 960 × 700 | 166,148 |
| Rotary reference | 1672 × 941 | 783,040 |
| Rotary minimum | 960 × 700 | 319,947 |
| Flat Play minimum | 960 × 700 | 49,621 |
| **Total PNGs** | **8** | **2,677,186** |

The capture manifest hashes 39 payload/provenance files. Its own identity and
the subsequently authored README are outside that manifest, explicitly stated
in its scope. Provenance SHA-256 is
`361b61decc1b8b5e756ca3755db2bb340f76e70ec5f1f82e115045e31a92926b`;
manifest SHA-256 is
`d2e6c6308eea5aa04948dcc282ae0552e71f943a0501ba1283c2736cb6fe84fe`.
The final assignment report records complete delivered file sizes including
the gallery README and review. No application binary, cache or raw BMP is added.

## Comparison with the original reference

All eight full PNGs were viewed, including reference/default/minimum Play,
reference/minimum Service and Rotary, and minimum Flat. The unchanged original
[atlas cover/page-409 JPEG](../design/atlas-cover-reference.jpg) was viewed
separately at 1672 × 941. Its SHA-256 remains
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`;
[source provenance](../design/atlas-reference.json) identifies the embedded
original JPEG stream and source PDF. The concept is design intent rather than
measured geometry or an application screenshot.

**Literal 1:1 equality remains unmet.** The following are observed composition
and material differences, not a quantified pixel-error score:

| Area | Final native observation | Remaining reference difference |
|---|---|---|
| Frame, panel and light | Walnut border, charcoal surfaces, brass rules, screw details and shallow gradients remain visible. Flat removes most depth and wood decoration. | The source has richer rough surface texture, stronger rounded rim reflections, softer cast shadows and more complex light falloff. Native bevels and gradients are simpler and more uniform. |
| Header | Final serif title is centered; Play/Rotary/Service and the six real tools plus Flat are visible at minimum size. | Native tool rows replace the concept's preset/settings block and its large letter-spaced subtitle. The title scale and surrounding spacing differ. |
| Main control row | Correct percussion enable/harmonic/volume/decay, expression and two nominal pedal mixtures are present. | The source's vibrato/chorus bank occupies this space; it is not supplied as fake live controls while scanner audio remains unconnected. Tablet arrangement, captions and row height consequently differ. |
| Drawbar racks | Adjacent racks show verified footage, cap colors, 0–8 positions and sounding/edit distinctions. The held-state edit has a visible focus outline. | The concept places footage and numeric scales differently and uses different slot/cap lighting and rack proportions. Correct footage and actual values take precedence over its incorrect legends. |
| Manual rows | Both complete 61-key manuals have sloped sides/fronts and retain held highlighting; minimum rows are visibly shallow. | The application adds a separate computer-key target row, full preset octaves and a pedalboard. Its full manuals occupy shallower rows with denser playing-key spacing than the concept. |
| Reversed presets | All 24 keys remain visible; accidental legends now use two lines, with separate natural-key labels. | The source shows large BASS/LOWER/UPPER tablets in these left blocks. It cannot represent the correct Cancel/fixed/A#/B inventory. Native preset labels remain small and need physical display/DPI review. |
| Cabinet | Wide Play shows a cropped source cabinet image above explicit device/model status. Rotary labels its enlarged image decorative. | Native panel size/crop and below-image content differ from the source's microphone knobs and STOP/SLOW/FAST row. Cabinet audio, rotor speed, geometry and brake are not modeled as live controls. Play hides the column below width 1400. |
| Added inventory and evidence | 25 pedals, status/dirty state and honest unavailable-model captions are visible. Service has six copied-state cards; Rotary has six read-only rows. | The cover concept does not show those complete playing/evidence surfaces. Exact composition equality is incompatible with copying its reduced inventory unchanged. |

Minimum Service visibly contains all six cards and 28 rows without observed
card/header collision. The four-bank row wraps within its card. It displays
Upper/Lower/pedal held counts 2/1/1, fixed versus edited selection, unavailable
voltage/rotor values, unacquired geometry and nominal/unconnected model labels.
Rotary has no fake sensor values or interactive microphone/speed/brake controls.
Minimum Flat keeps the same notes, caps, focus and inventory with rectangular
keys and plain surfaces. These are visual observations on the saved images;
they do not establish native semantic accessibility or high-DPI readability.

## Handoff and remaining gates

The root README's native UI/UX section now uses only actual v2 image paths and
links to the exact source/capability boundary. Its surrounding text was
preserved by A46; [the scoped edit record](../development/2026-11-14-interface-continuation/reports/a46-readme-scope.json)
retains before/after hashes. Root may update other shared guide/status/index
sections and publish after review. A46 did not stage, commit, push, rerun the
whole test suite, alter product code or acquire a new build tree.

The current complete [M0–M9 plan](../PLAN.md) remains open beyond this M9
presentation/capture result. A fresh real display/SDL backend is needed for
persistent pointer capture and physical display/DPI qualification; physical
audio/MIDI, screen-reader semantics, callback deadlines, DAW/host use,
source/dependency rights and signed release each need their own evidence.
Scanner integration and complete AO-28/Leslie electronics/acoustics require
their numerical, graph and acquisition prerequisites. No saved image closes
specimen-specific fidelity or literal reference equality.
