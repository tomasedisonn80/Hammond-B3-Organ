# Final native gallery admission

**Accepted for the stated native application capture scope.** A50 independently
reviewed the eight frozen v4 frames, their retained diagnostics and named
source/build inputs. The gallery contains **41 files, 2,948,483 bytes**, including
eight PNGs totaling **2,722,450 bytes**. The read-only audit passes **611 checks**
with no failures. All eight original PNGs and the original reference JPEG were
opened directly with the image viewer; no new capture, composite or altered
image was used. [Audit report](../development/2026-11-14-reference-refinement/reports/A50-final-gallery-admission.json),
[reproducible checker](../development/2026-11-14-reference-refinement/reports/A50-check-final-gallery.py),
[actual gallery](../../examples/demos/standalone-interface-preview-v4/README.md).

## Exact admitted source and build boundary

| Identity | Admitted value |
|---|---|
| Published product commit | `0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b` |
| Published tree | `f8144b771cda1264a8788f8297f5bfec999f4a08` |
| Native executable | 3,860,368 bytes; SHA-256 `01fe78a55b7a9bc72228dafe175f5a8eb48481c063f217606474d4dff682320f` |
| Accepted `InstrumentView.cpp` | SHA-256 `f323c8c2f5529b03c25deccb74f482d8b6312487492a45d14b94ef0e24cfbb6a` |
| Captured producer | 29,923 bytes; SHA-256 `92ae0be31a6ef21eb696c87d4f9dacd8ea8a6732d6c1033e0d7457ca3a76d16b` |
| 111-file qualified source inventory | SHA-256 `bffd31d6a2caa65872ece2cb4614902608c30c3dffc9af0c21aa4bd0a3a110fd` |
| Gallery provenance | SHA-256 `f106efc20838c1acb3a392e3d39989ed34b770829a3859deaa95e64cd8a657be` |
| Gallery manifest | SHA-256 `2ed031aa1ecda5a67fa32a4268676602d709250c596ed2be0a24b69c682da5e8` |

A50 recomputed every one of the manifest's 39 payload identities, the two
additional gallery files, every PNG file identity, RGBA decoded hash and exact
dimensions. All 111 qualification entries match both current files and the
named published commit's blobs. The 100 production inputs, eleven CMake files,
seven font/atlas files, thirteen selected generated/profile/archive inputs,
and nine additional cache/build-plan/prepared-source files, selected configuration,
executable and producer match A46's before-build, after-build and after-capture
observations. All **123 files across v1/v2/v3** also match published blobs.
These checks preserve the raw historical evidence and do not substitute new
data for it. [A46 producer evidence](../development/2026-11-14-reference-refinement/notes/A46-final-native-gallery.md),
[copied source qualification](../../examples/demos/standalone-interface-preview-v4/inputs/source-qualification.json),
[publication receipt](../development/2026-11-14-reference-refinement/reports/root-header-publication.json).

A46's existing GCC 14.2.0/CMake 4.4.5 Release desktop target invocation completed
in 1.02 seconds. Ninja refreshed CMake after a test glob addition and reported
`no work to do`; no compile/link command ran and the existing executable stayed
unchanged. A50 ran no native process, build or CTest. The matching named inputs
and observed target invocation are **not an independent clean rebuild, hermetic
compiler/dependency closure or signed source-to-binary attestation**. Concurrent
documentation was present, so no clean whole-worktree claim follows. The audit
reads local published objects and records cached origin/main; root's separately
retained receipt establishes the observed publication. [Build log](../development/2026-11-14-reference-refinement/reports/A46-build.log),
[A50 exact observations](../development/2026-11-14-reference-refinement/reports/A50-final-gallery-admission.json).

## What the eight actual frames establish

| Original retained frame | Independent visual observation |
|---|---|
| Play, 1672×941 | The larger wide title and spaced nominal caption fit. Both complete manuals, reversed preset rails, retained drawbar values and four held marks remain visible. The focused Upper B drawbar is cyan; sidebar pedals remain clear of cabinet/status ink. |
| Play, 1280×900 | The compact header, both manuals, preset rails, performance controls, computer-key row and bottom pedalboard fit. Focus, four held marks and the unsaved footer remain visible. |
| Play, 960×700 | Edit A/B moves into each rack. Full manuals, preset rails, pedal row and footer remain present. Small accidental legends are visible but require physical display/DPI assessment for usability. |
| Service, 1672×941 | All six cards and 28 rows fit. The held values read **2 targets / 1 target / 1 target**. Applied sound, Edit B, all four bank memories, availability and evidence remain distinct. |
| Service, 960×700 | All six cards remain complete. Bank-memory text wraps within its card, and the singular held labels and truthful unavailable facts remain visible. No row collision was observed. |
| Rotary, 1672×941 | The cabinet artwork and all six read-only facts fit. Decorative artwork, unavailable rotor speeds, unacquired geometry, unmodeled stop/brake and unconnected cabinet audio remain explicit. |
| Rotary, 960×700 | All six facts, the cabinet image, wrapped audio/fidelity caption and footer stay inside their panels. The image is not evidence of a rendered cabinet signal. |
| Flat Play, 960×700 | Plain controls and rectangular manuals/pedals retain the complete playing inventory, values, focus and four held marks. No panel or key cropping was observed. |

The preserved [workspace](../INTERFACE_WORKSPACE_CONTRACT.md) and
[layout](../REFERENCE_REFINEMENT_LAYOUT.md) inventories explain these frames:

| Inventory | Preserved count and meaning |
|---|---|
| Playing keys | Upper 61 + Lower 61 + 25 pedals = **147**, separate from preset controls. |
| Reversed presets | **24**, twelve per manual: C Cancel, nine fixed C#–A choices, A# selects adjustable bank A, B selects bank B. |
| Ordinary controls | **68**, including ten common header controls: three workspace tabs, six tools and Flat. Play retains 18 visible drawbars, four Edit A/B buttons, four percussion choices, expression, two pedal mixtures, three keyboard targets and two octave buttons, plus the 24 presets. |
| Focus inventory | **71** Play stops: 68 controls plus three roving playing-key stops. Rotary/Service retain the ten common stops. The gallery visibly exercises one drawbar focus and workspace focus; it does not rerun complete focus traversal. |
| Retained sound state | Four nine-drawbar banks, **47** sound parameter identities, `B3CONTROLS4` and readers 1–3 retain their meanings. This admission changes no product or state source. |
| Service rows | Generator 4; Contacts/routing 6; Scanner 3; AO-28 4; Leslie 5; Retained controls 6: **28** total in six cards. |
| Rotary facts | Audio path, documentary target, artwork, rotor speeds, microphone geometry and stop/brake: **six**, all read-only. |

## Typed replay, copied state and cleanup

Each native run loads the same retained state and uses keyboard replay. Four
original owners hold Upper MIDI 60/64, Lower MIDI 67 and pedal ID 3 through a
live Upper B 16-foot drawbar **7→8** edit. Upper fixed C# keeps sounding; Lower
sounds adjustable bank A selected by A#, while its independent edit choice
remains B. Twenty-five Tab presses reach the edited drawbar. Seven replays
deliver 66 events; Flat delivers 68. There is no Save operation.
[Retained inputs and provenance](../../examples/demos/standalone-interface-preview-v4/provenance.json).

A50 independently checks exact integer **2/1/1** held values and all six pointer
capture fields in each screenshot, last-painted and before-shutdown copy.
The flags are literal false and the four counters are integer zero, with no
missing or extra fields. Complete desired, applied and final controls match
the independently stated values with their JSON types. An actual pre-edit
held observation remains in every diagnostic. Running the pinned producer's
pure validator over all eight retained diagnostics also reproduces its recorded
result, including the acknowledged current copied state, requested frame/view,
four held owners, progression, MIDI inactivity and joined cleanup. This is
read-only diagnostic validation, not a new native or synthetic-mutation run.
[A50 report](../development/2026-11-14-reference-refinement/reports/A50-final-gallery-admission.json),
[earlier validator acceptance](../development/2026-11-14-reference-refinement/notes/A32-gallery-independent.md).

All stdout/stderr files are empty. Diagnostics retain dummy SDL audio/video,
software rendering, SDL 2.32.10, 48 kHz stereo native float32 and 512-frame
buffers. The MIDI-enabled build exposes ALSA, but no MIDI input or discovery
was requested. Reported sample/render faults, queue overflow, rejected
commands and session faults are zero. Shutdown clears held owners, stops the
Session and leaves MIDI closed and quiescent. Each diagnostic also retains
one discarded shutdown command; the acceptance does not incorrectly describe
every counter as zero. [Original diagnostics](../../examples/demos/standalone-interface-preview-v4/manifest.json).

## Direct header measurement on v4 pixels

The original 412,664-byte JPEG matches SHA-256
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`.
A50 also verifies its exact embedded image object in PDF pages 1 and 409, and
the unchanged 500-page PDF identity. Its evidence class remains a generated
design concept. [Reference ancestry](../design/atlas-reference.json).

A50 reapplied A41's unchanged warm mask `R≥130, G≥105, R≥G, B≤0.9R`, without
resampling or registration, in the original half-open title ROI
`[595,10,1081,65)` and caption ROI `[600,60,1100,106)`. **All three actual v4
reference-size workspaces** reproduce A41's measured ink, including pixel
count and occupied-column runs. They pass the same title width 461–467,
height 32–34, top 19–21 and center 833–837 budgets, and caption width 367–375,
height 11–13, top 70–72 and center 833.5–837.5 budgets. All fifteen nonspace
caption runs remain present. [A41 fixed thresholds](../development/2026-11-14-reference-refinement/reports/A41-run-acceptance.py),
[independent v4 measurements](../development/2026-11-14-reference-refinement/reports/A50-final-gallery-admission.json).

| Half-open ink bounds at 1672×941 | Original reference | Actual v4 Play, Service and Rotary |
|---|---|---|
| Title | `[603,20,1067,53)`, 464×33; center 835 | `[602,20,1065,53)`, 463×33; center 833.5 |
| Subtitle/caption | `[650,71,1021,83)`, 371×12; center 835.5 | `[650,71,1020,83)`, 370×12; center 835 |

Matching these measured targets does not mean equal images. The title remains
one pixel narrower and centered 1.5 pixels left; the caption is one pixel
narrower and uses truthful **NOMINAL DRY ORGAN** instead of the reference's
different wording. A41's separate differential, clipping, focus and timing
acceptance remains source-specific. Its first timing threshold trigger and sole
nonreproducing reverse-order repeat are preserved; this gallery admission adds
no timing or performance equivalence claim. [A40 implementation](../development/2026-11-14-reference-refinement/notes/A40-reference-header-refinement.md),
[A41 acceptance](../development/2026-11-14-reference-refinement/notes/A41-header-independent-acceptance.md).

## Separate evidence and remaining work

Every v4 frame has overlay `none`, current copied inspection and controls pending
false. Modal Help/Audio/MIDI appearance and interaction are not demonstrated
here. [A18's six-frame pending harness](../development/2026-11-14-reference-refinement/notes/A18-pending-raster-implementation.md)
uses a real Session queue and native painter without an application window or
audio device; it retains its own source and acceptance. The earlier
[real X11 input journey](../development/2026-11-14-reference-refinement/reports/root-desktop-acceptance-review.json)
has another executable and its stated pre-held and desktop-boundary limits.
Neither is relabeled as an action observed in these settled v4 captures.

**Literal whole-interface 1:1 equality remains unmet.** Live tools replace the
concept's preset/settings block; the complete 61+61+25 playing inventory,
24 preset keys, computer-key row and truthful status change composition.
Rack/manual placement, key-edge light, bevels and wood/charcoal material still
differ. No distinct exact Service or Rotary concept image exists in this
reference. Small text and real DPI remain separate display/usability work.
Cabinet artwork is decoration; this nominal dry path renders no Leslie audio.
Scanner/AO-28/Leslie integration, physical devices, accessibility, callback
deadlines and specimen-specific fidelity remain separately evidenced gates.
[Measured composition review](REFERENCE_REFINEMENT_VISUAL.md),
[full M0–M9 plan](../PLAN.md).

The original BMP bytes were removed only after the producer's recorded decoded
comparison. A50 verifies the retained lossless PNG identities and does not
claim to recheck absent BMP bytes. Next, A47 may use this admitted v4 gallery
in current README/runbook guidance; root owns final build/test acceptance,
publication and session closure. Future overlapping visual work must preserve
v1–v4, qualify its own exact source/binary and compare new native frames against
this reference and the retained admission before making stronger claims.
