# A46 — Final actual native gallery and README visual section

Actual assignment **46/60**, logical wave **8**, worker
`/root/w08_a46_final_native_gallery`, 14 November 2026.

## Owned work and result

Created `examples/demos/standalone-interface-preview-v2/` without modifying v1,
updated only the root README's **Native interface and UI/UX design** section,
and authored [the final visual/provenance review](../../reviews/INTERFACE_FINAL_GALLERY.md)
and `reports/a46-*` evidence. No product, CMake, workflow, shared status/index,
publication or other worker-owned files were changed. Root retains the commit
and publication step.

**Eight actual native captures passed.** The existing A44-qualified MIDI-on
binary is 3,707,640 bytes, SHA-256
`bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2`.
HEAD/tree remained `8673713a484c40e26ac7810c7c4cbc22fa874426` /
`e11bd68d6051f663631579ef235325a8775f8133` through capture. All 98 product
inputs match both the published blobs and A44's observed source. There was no
uncommitted product overlay; concurrent metadata/test-budget/docs changes were
outside that inventory.

The 98 product files, 13 selected generated/profile/library files, selected
configuration, executable, capture harness, report and state/replay inputs
remained unchanged through the matrix. Four additional cache/link/flags/
capability identities also matched before and immediately after. A46 used a
read/capture lease on `../build-native`, then explicitly released it; no
configure, rebuild, whole-suite execution or application-binary copy was needed.

## Exact commands and evidence

Working directory:
`/workspace/scratch/601951e27dc3/Hammond-B3-Organ`.
Python 3.12.14/Pillow 13.0.0 authored the output. The executable/build already
existed; dependencies were shared rather than copied.

```sh
python3 -B docs/development/2026-11-14-interface-continuation/reports/a46-prepare-capture.py
python3 -B tools/capture_standalone_interface.py \
  --exe /workspace/scratch/601951e27dc3/build-native/apps/standalone/hammond_standalone \
  --source-root . --build-root /workspace/scratch/601951e27dc3/build-native \
  --source-qualification docs/development/2026-11-14-interface-continuation/reports/a46-source-qualification.json \
  --expected-exe-sha256 bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2 \
  --dummy-sdl --output examples/demos/standalone-interface-preview-v2
python3 -B docs/development/2026-11-14-interface-continuation/reports/a46-verify-gallery.py
```

The preflight is a one-time authoring step that exclusively creates its report
files. Reproduction uses the preserved qualification and a fresh output
directory, as described in the gallery README. The verification reader does
not require a live build and launches no new native process.

The initial ad hoc preflight compared two differently encoded inventory
digests and failed before writing its report or launching the application.
The subsequent harness admission therefore exited 2 for a missing report.
No native or failed-gallery output existed. Reading A44's actual path/NUL/SHA/
newline digest implementation resolved the authoring mistake; the corrected
preflight passed with every individual source hash already matching. The
[correction record](reports/a46-preflight-correction.json) preserves this
failure boundary. Neither product nor harness needed repair.

| Evidence | Result or scope |
|---|---|
| [Source preflight](reports/a46-source-before.json) and [after snapshot](reports/a46-source-after.json) | Full observed 98 product/13 selected build file maps; exact git/executable/configuration; no capture drift |
| [Compact source qualification](reports/a46-source-qualification.json) | Derived from A44 actual records; ten required source files plus exact binary; clear subset/full-build limits |
| [Capture process](reports/a46-capture-process.json) | Harness exit 0, eight cases, exact command/environment/time and source identity |
| [Gallery provenance](../../../examples/demos/standalone-interface-preview-v2/provenance.json) | All eight actual runs, controls, replay, original BMP and decoded PNG identity |
| [Separate reader result](reports/a46-gallery-verification.json) | 39 manifest files and all eight RGBA PNG hashes/dimensions checked; retained native records rechecked; v1's 41 files equal published blobs |
| [README scope](reports/a46-readme-scope.json) | Native visual section changed; prefix and suffix preserved at A46 edit time |
| [Final review](../../reviews/INTERFACE_FINAL_GALLERY.md) | Source/build boundary, exact image sizes, visual observations, concrete reference differences and remaining gates |

Capture uses SDL 2.32.10 dummy audio/video/software rendering, 48 kHz stereo
float and 512-frame buffers. RtMidi ALSA is compiled but source is `none`, with
zero input/discovery use. Every case holds Upper 60/64, Lower 67 and pedal 3;
changes the retained Upper B 16-foot drawbar 7→8 through real Tab/Up events;
and keeps Upper fixed C# and Lower bank A (preset A#) sounding. All four bank
memories stay distinct; expression, pedals and stored percussion stay correct.
Seven cases deliver 66 events, Flat delivers 68, and each lasts 1,800 ms.
The input state file never changes and no Save is sent.

All cases had actual callback/render progress, zero application errors, final
acknowledgment, exact complete desired/applied replay control state, requested
painted view/size, current copied inspection, no pending control/save, and
joined cleanup with no held/running owners. The screenshot paint record is
equal to last-painted/pre-shutdown presentation; cleared shutdown state does
not stand in for the image's state.

## Images, review and remaining visual differences

The eight PNGs total **2,677,186 bytes**, and the complete gallery stays below
3 MB. Raw BMPs were removed only after producer verification of lossless decoded
equality. A separate reader recomputed PNG identities and manifest hashes;
no BMP, executable or build cache is added. The gallery manifest excludes itself
and the later README, explicitly stated. The final assignment result retains
complete delivered-file sizes.

Viewed the original reference and **all eight full application PNGs**. Play
retains 61+61 keys, 25 pedals, 24 reversed presets, held highlights and focused
live drawbar state. The final centered title and two-line accidental labels
are visible. Minimum Service fits six cards/28 rows, including wrapped bank
memories and unavailable V/rpm/unacquired m labels. Minimum Rotary has six
read-only rows, decorative artwork and explicit unconnected cabinet audio.
Flat keeps the same state/inventory on rectangular keys and plain panels.

The original cover/page-409 image remains SHA-256
`9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`.
**Literal 1:1 equality remains unmet.** The detailed review records smoother
panel materials, simpler bevel/light treatment, different header/control
composition, shallower full manuals, complete preset/pedal inventory and a
different cabinet crop/status arrangement. Missing vibrato/rotor/microphone/
brake controls are not fabricated. Small text still needs real display/DPI
review. A31's injected renderer proof remains separate from this native gallery.

## Root handoff

Review the new gallery and scoped README diff, then publish under the standing
expected-head workflow. Product inputs are already committed; this assignment's
capture/docs payload requires its own root commit. Root may update links in
shared plan/status/setup/index files and retain final hosted qualification with
its exact source; A46's README section has the current v2 identity.

No full-suite, physical-device, native display/pointer, screen-reader, timing,
host, signed-release, connected scanner/AO-28/Leslie or specimen-fidelity gate
is claimed. All 47 sound parameters, state4/readers 1–3 and existing model/source
identities remain unchanged. Continue the complete M0–M9 plan and remaining
actual assignments without reclassifying this bounded gallery as full product
completion.
