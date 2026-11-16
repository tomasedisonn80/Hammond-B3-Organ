# Hammond B-3 Organ

A C++20 Hammond B-3/AO-28 and Leslie research instrument, guided by the repository's **500-page atlas**. The playable instrument is a **nominal dry organ** with a native standalone application, an offline renderer and an optional VST3 adapter. Its musical core has 91 continuously running sources, two 61-key manuals, 25 pedals, eighteen documentary fixed registrations, four retained drawbar banks, percussion and shared expression.

<!-- preset-library-continuation-summary:start -->
## Current continuation: portable registrations and reference apron

The [current session](docs/development/2026-11-16-preset-library-continuation/README.md)
read all 500 atlas pages afresh and advances M9 with a headless registration tool,
saved-control rendering, twelve original starter recipes in 24 canonical files,
explicit installation components, and reproducible auditions. The first five
waves have delivered 30 distinct workers; the requested ten-wave/60-worker
continuation remains active in the [actual ledger](docs/development/2026-11-16-preset-library-continuation/assignments.json)
and [recovery checkpoint](docs/development/2026-11-16-preset-library-continuation/CHECKPOINT.md).

[Registration setup and commands](docs/REGISTRATION_GUIDE.md) ·
[Starter pack](data/registrations/starter-v1/README.md) ·
[Actual new UI gallery](docs/design/native-gallery-preset-v1/README.md) ·
[Full M0–M9 plan](docs/PLAN.md)

The wide Dimensional Play apron now uses the reference's exact exposed RGB
pixels with a transparent hole for the live footer. Independent comparison of
25 genuine before/candidate cases covers 61,780,011 pixels with no changes outside
the declared apron, no protected-footer changes, and exact procedural fallback.
The source-matched apron is a scoped design improvement; **literal whole-interface
1:1 remains unmet and unwaived**. The native gallery includes thirteen real views,
including 1672×941, minimum-active 1400×820 and 1920×1080.

![Actual native application at 1672×941, with the reference apron and live controls](docs/design/native-gallery-preset-v1/images/play-reference-1672x941.png)

*Actual SDL software capture with dummy audio/video. The nominal dry Engine,
live status and correct musical controls remain visible; this is not a rendered
mockup or physical-device qualification.*

Root's complete configured native suite passed **230/230**; later independent
recipe, installer, audition and portability regressions pass their scoped gates.
[Coherent source-bound results](docs/development/2026-11-16-preset-library-continuation/reports/w04-coherent-qualification.json)
and [paired UI evidence](docs/development/2026-11-16-preset-library-continuation/reports/apron-paired-final.json)
retain original failures and exact identities. Current-source hosted platform
qualification and the remaining worker reviews are still in progress.
<!-- preset-library-continuation-summary:end -->

**Parallel runtime/interface continuation (separate owner):** [this session](docs/development/2026-11-16-runtime-continuation/README.md) has freshly covered all 500 PDF pages and is developing isolated causal contact audio plus reference-derived manual key materials. Its own [sixty-worker ledger](docs/development/2026-11-16-runtime-continuation/assignments.json) and [checkpoint](docs/development/2026-11-16-runtime-continuation/CHECKPOINT.md) record actual progress, validation and next actions. The recovered conversion/typography checkpoint is published as `f56b0f3`. New contracts receive independent admission before implementation; current progress is not final acceptance.

**Earlier conversion/interface continuation:** [this session](docs/development/2026-11-16-conversion-material/README.md)
has completed a fresh reading of all 500 atlas pages and implemented an explicit,
certified offline conversion from the fractional-contact model to the native
integer grid. The Lower drawbar rack now has its own directional material field;
both manual racks now use measured mixed-fraction footage typography. The requested sixty
workers in ten waves are tracked in the [actual ledger](docs/development/2026-11-16-conversion-material/assignments.json),
with recoverable progress in the [checkpoint](docs/development/2026-11-16-conversion-material/CHECKPOINT.md).
This continuation is still in progress; the ledger records actual accepted work.

[Conversion contract](docs/CONTACT_GRID_CONVERSION_CONTRACT.md) ·
[Install the converter](docs/CONTACT_GRID_CONVERSION_INSTALL.md) ·
[Current application captures](examples/demos/footage-typography-v1/README.md) ·
[Current scope](docs/development/2026-11-16-conversion-material/SCOPE.md) ·
[Full M0–M9 plan](docs/PLAN.md).

The converter's independent calculation retains all 71 tested inputs: 51 accepted
with exact agreement and 20 explicit refusals. Native comparison passes 557
processes with complete padded state and 19,233 block-count checks. The Lower
comparison preserves all pixels outside its declared surface across 98 genuine
pairs. Its original sampling failure and independently admitted correction are
retained separately. **Literal whole-interface 1:1 remains unmet and unwaived.**

The preceding [streaming/material session](docs/STREAMING_CONTINUATION_CLOSURE.md)
delivered the isolated causal trajectory and Upper-rack material. Its sixty
workers, 210-test gate and published platform results retain their own identities;
they do not count toward this continuation's staffing or current-source qualification.

The preceding [execution continuation](docs/development/2026-11-15-execution-continuation/README.md)
supplies the offline fractional-contact reference and canonical wide composition.
Its [36-fixture/four-factor study](docs/CONTACT_SWITCHING_RESULTS.md) and
[original composition gallery](examples/demos/whole-reference-layout-v1/README.md)
retain their own source identities and limits.

The earlier [audio continuation](docs/development/2026-11-15-audio-continuation/README.md)
adds prepared sparse source leakage with explicit offline gain (M2). Its
[six-file audition](examples/demos/source-leakage-audition-v1/README.md),
independent numerical/lifecycle/CLI checks and
[percussion-stage captures](examples/demos/standalone-audio-preview-v1/README.md)
retain their own source identities. The default dry sound and musical state
remain compatible. Separate harmonic-source work and its original 183-test
baseline remain in the [playable checkpoint](docs/development/2026-11-15-playable-continuation/CHECKPOINT.md)
and [reading record](docs/research/PLAYABLE_ATLAS_REVIEW.md).

The earlier [product continuation](docs/development/2026-11-15-product-continuation/README.md) delivered three practical areas:

| Area | Available now |
| --- | --- |
| **Native MIDI expression and channel modes — M9** | Set CC11 minimum, maximum and Normal/Inverted direction in the MIDI dialog or CLI. Scoped CC120, expression reset CC121 and the existing CC123 preserve distinct ownership and control behavior. [Operating guide](docs/MIDI_EXPRESSION_GUIDE.md) |
| **Live controls and copied state — M9** | Complete fitted footage labels, separate **EDIT BANK** / **SOUNDING** captions, retained drawbar banks and explicit pending/applied state. The current composition relocates these live elements; the MIDI dialog retains explicit calibration and connection state. [Earlier design and evidence](docs/PRODUCT_VISUAL_REFINEMENT.md) |
| **Independent passive crossover — M6** | A four-state ideal Leslie 122 electrical model, native probe, independent analog reference and numerical/lifecycle checks. It remains separate from the playable Engine. [Developer guide](docs/CROSSOVER_DEVELOPER_GUIDE.md) |

The **47 sound parameters**, **`B3CONTROLS4`** writer and readers for versions **1–3** retain their meanings. MIDI calibration is native adapter configuration; it adds no sound parameter or VST3 mapping. Scanner, AO-28 and Leslie audio are not connected to the dry Engine. The [current compatibility review](docs/reviews/CONVERSION_MATERIAL_COMPATIBILITY.md), [earlier product review](docs/PRODUCT_COMPATIBILITY.md) and [full plan](docs/PLAN.md) preserve these boundaries.

[Get started](#getting-started) · [Play and configure MIDI](docs/MIDI_EXPRESSION_GUIDE.md) · [Interface guide](docs/INTERFACE_RUNBOOK.md) · [Contact reference guide](docs/CONTACT_SWITCHING_GUIDE.md) · [Current status](docs/STATUS.md) · [Next steps](docs/NEXT_STEPS.md) · [M0–M9 plan](docs/PLAN.md) · [Current recovery checkpoint](docs/development/2026-11-16-runtime-continuation/CHECKPOINT.md)

The earlier [product batch record](docs/PRODUCT_CONTINUATION_CLOSURE.md) preserves
its accepted development, strict accounting and remaining requirements. Literal
whole-interface 1:1 matching remains unmet; the actual screenshots below make the
current implementation reviewable.

## Getting started

Use a C++20 compiler, CMake **3.21+** and Python **3.10+**. The native application also needs a C compiler, Git and the platform development packages listed in the [MIDI setup guide](docs/MIDI_EXPRESSION_GUIDE.md). Dependencies are explicitly acquired at locked revisions; ordinary CMake configuration does not download them.

### Build and launch the native application

For a fresh Linux/macOS single-configuration build, run from the repository root:

```sh
python3 tools/acquire_sdl2.py --destination ../SDL2
python3 tools/acquire_rtmidi.py --destination ../rtmidi-6.0.0
cmake -S . -B build-native-midi -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_BUILD_VST3=OFF \
  -DHAMMOND_SDL2_ROOT="$PWD/../SDL2" \
  -DHAMMOND_ENABLE_MIDI=ON -DHAMMOND_RTMIDI_ROOT="$PWD/../rtmidi-6.0.0"
cmake --build build-native-midi --config Release \
  --target hammond_standalone --parallel 3
./build-native-midi/apps/standalone/hammond_standalone --width 1672 --height 941
```

This uses **SDL 2.32.10** and **RtMidi 6.0.0**. Use the acquisition tools' `--verify-existing` option for an existing dependency checkout. Windows/PowerShell commands, platform packages and multi-configuration executable paths are in the [setup guide](docs/MIDI_EXPRESSION_GUIDE.md#build-the-native-application). For keyboard/pointer operation without a physical MIDI backend, omit RtMidi acquisition and `HAMMOND_RTMIDI_ROOT`, and configure with `-DHAMMOND_ENABLE_MIDI=OFF`; SDL is still required. The [Standalone installation guide](docs/STANDALONE_INSTALL.md) describes an explicit relocatable install.

The launch command opens the new composition at its **1672×941 reference size**.
It is active only in **Dimensional Play at width ≥1400 and height ≥820**.
Launching without size options still opens the **1280×900 compact layout**;
Flat, Rotary, Service and smaller windows keep their established arrangements.

No MIDI input is selected automatically. Open **MIDI / Ctrl+M**, choose one exact input name and three distinct channels, then Apply. Alternatively, list inputs before selecting one with `--midi-port`:

```sh
./build-native-midi/apps/standalone/hammond_standalone --list-midi
```

Open **AUDIO / Ctrl+,** to choose audio settings. The initial request is the default output, 48 kHz and a 512-frame buffer; obtained buffer size is not a physical latency measurement. The [interface guide](docs/INTERFACE_RUNBOOK.md) covers playback, state paths, audio recovery and keyboard/pointer controls.

To build the native acceptance inputs before running their tests:

```sh
cmake --build build-native-midi --config Release \
  --target hammond_standalone_test_inputs --parallel 3
ctest --test-dir build-native-midi -C Release --output-on-failure \
  --no-tests=error -R '^test_standalone_'
```

### Build the core and render audio

The default core/offline build needs no downloaded audio, GUI or host framework:

```sh
cmake --preset debug
cmake --build --preset debug --parallel 2
ctest --preset debug
```

The build validates the authoring profile and generates `build/nominal.b3p`. For a two-second dry registration on a Linux/macOS single-configuration build:

```sh
cmake -E make_directory out
./build/hammond_render --profile build/nominal.b3p --output out/dry-organ.wav \
  --frames 96000 --sample-rate 48000 --block-size 64 --seed 0 \
  --drawbars 888000000 --note 60 --fail-on-clip
```

The output is stereo PCM16 with identical dry channels. Existing output files are preserved, so choose a new filename for another render. The renderer reports profile identity, peak, RMS and clipping. See [general builds](docs/BUILD.md), the [offline format](docs/RENDER_FORMAT.md) and [OfflineTools installation](docs/OFFLINE_INSTALL.md).

### Run the offline fractional-contact reference

The M3 research tool resolves continuous key travel and nine independent
hysteretic contacts per key before reducing bandwidth. It produces JSON samples
and exact event records with complete filter tails. It uses Python's standard
library and runs independently of the native application:

```sh
mkdir -p ../contact-reports
python3 -B tools/contact_switching_reference.py \
  --input data/contact-switching/reference-v1/F02-48000-v1.json \
  --factor 256 --output ../contact-reports/F02-48000-L256.json
```

The fixed study covers twelve synthetic recipes at 44.1, 48 and 96 kHz, each at
factors 32, 64, 128 and 256. Convergence is checked across **all 289 output samples**;
the independent continuous reference admits **64 frozen probes per fixture**.
The [qualified installed run](docs/CONTACT_SWITCHING_RESULTS.md) passes in
**21.728 s external process wall time** with **35.262 MiB peak resident memory**.
These observations qualify the named offline experiment. They establish no
causal streaming implementation, full-window atlas `1e-4` grade, physical contact
model or change to Engine/native/VST3 audio.

[Operating guide and full-study command](docs/CONTACT_SWITCHING_GUIDE.md) ·
[Install and relocate ContactReferenceTools](docs/CONTACT_REFERENCE_INSTALL.md) ·
[Frozen model](docs/FRACTIONAL_CONTACT_REFERENCE.md) ·
[Frozen validation protocol](docs/CONTACT_SWITCHING_VALIDATION.md).

### Run the causal contact grid

The new C++20 research module returns exact rational crossing times for nine
hysteretic contacts per key. It supports four keys, three sample rates, explicit
integer targets, persistent anchors, transactional failures and bounded storage.
It is separate from audio synthesis and does not change the nominal dry Engine.

```sh
cmake --preset release
cmake --build --preset release --target hammond_causal_contact_grid_probe --parallel 2
```

The [developer guide](docs/CAUSAL_CONTACT_GRID_GUIDE.md) includes a verified
one-frame example, strict ASCII transport, C++ lifecycle, test commands and the
next audio/filter boundary. Single-frame and irregular blocks preserve exact
results. The original offline model remains a separate, acausal reference;
integer-input exactness does not establish universal binary64 equivalence or a
full-window audio grade.

### Convert a fractional-contact input explicitly

The separate Python utility converts only inputs whose rounded grid preserves
contact/arrival identities, command relationships, complete event ordering and
final contact state within the admitted position and root-time budgets. It emits
a deterministic certificate containing the exact source bits, errors, witnesses,
module hashes and native `CGGRID1` transport. It does not change the live Engine.

```sh
mkdir -p ../contact-grid-reports
python3 -B tools/convert_contact_grid.py \
  --input data/contact-switching/reference-v1/F02-48000-v1.json \
  --output ../contact-grid-reports/F02-48000-grid.json
```

Success is silent with exit 0. A refused conversion returns exit 2 and one JSON
diagnostic; the existing output remains intact before publication. The original
F09 input is intentionally refused at all three rates because rounding changes
an edge/command equality. A certificate proves a bounded synthetic trajectory
comparison; audio reconstruction and physical calibration retain separate gates.

The [five-file installation guide](docs/CONTACT_GRID_CONVERSION_INSTALL.md)
provides copy-only installation and relocation commands. The original 48-file
`ContactReferenceTools` package remains unchanged.

### Audition synthetic source leakage

The optional M2 layer mixes a prepared sparse graph over the same 91 original
source samples before contact routing. Signed donors can contribute while their
own keys are released. Coefficients are **synthetic numerical fixtures**; this
does not claim measured generator coupling. The default renderer and standalone
remain on their existing dry path.

```sh
python3 tools/compile_source_leakage.py \
  --input data/source-leakage/synthetic-pair-demo-v1.json \
  --output out/pair.b3leakage
./build/hammond_source_leakage_probe --input out/pair.b3leakage
./build/hammond_render --profile build/nominal.b3p --output out/leakage-organ.wav \
  --frames 96000 --sample-rate 48000 --block-size 64 --seed 1939 \
  --drawbars 008000000 --note 48 --source-leakage out/pair.b3leakage \
  --leakage-input-gain 0.75 --fail-on-clip
```

The two leakage options are required together. Unsafe source headroom rejects
before output creation; the renderer never reduces the requested gain for you.
The selected path emits schema-5 provenance and bound facts. Musical controls,
parameter identities and control-state files are unchanged.

The [six-file audition](examples/demos/source-leakage-audition-v1/README.md)
compares pair and empty graphs at the **same gain 0.75**, includes a byte-identical
default/empty-gain-one control, and preserves all commands, profiles, scores,
hashes and receipts. Its independent solo PCM calculation observed zero error
within the frozen one-step allowance. [Core/data contract](docs/SOURCE_LEAKAGE_CONTRACT.md)
· [Engine/offline contract](docs/SOURCE_LEAKAGE_AUDITION_CONTRACT.md).
[Install and run the relocatable tools](docs/SOURCE_LEAKAGE_INSTALL.md).

Other development paths have their own setup: [optional VST3 and pinned SDK](docs/VST3_BUILD.md), [independent crossover targets](docs/CROSSOVER_DEVELOPER_GUIDE.md), [CrossoverTools installation](docs/CROSSOVER_INSTALL.md), [rotary waveform CLI](docs/ROTARY_RENDER_CLI.md) and [capture/calibration tools](docs/CALIBRATION_RUNBOOK.md). VST3 requires CMake 3.25+ and its separately acquired SDK; the native interface shown here is the standalone application.

<a id="native-interface-and-uiux-design"></a>

## Native interface and UI/UX

The application follows the atlas's walnut, charcoal and brass [cover/page-409 concept](docs/design/atlas-cover-reference.jpg), with [retained source provenance](docs/design/atlas-reference.json). Controls, labels, drawbar positions, held notes and focus are live application output. The cabinet image supplies decoration; it does not indicate connected Leslie audio.

**The current composition uses a 1672×941 reference canvas**, active only in
**Dimensional Play at width ≥1400 and height ≥820**. The performance band, adjacent
racks, both manuals and cabinet now follow one canonical arrangement. Shared
endpoints drive paint, pointer targets and focus; the keyboard toolbar and
25-note pedalboard sit in the cabinet's right panel. The
[frozen composition contract](docs/WHOLE_REFERENCE_LAYOUT_CONTRACT.md),
[independent geometry/input evidence](docs/development/2026-11-15-execution-continuation/notes/A18.md)
and [current gallery review](docs/reviews/UPPER_RACK_GALLERY_ADMISSION.md)
separate chosen geometry from observed shaded pixels.

| Landmark | Current canonical geometry at 1672×941 |
| --- | --- |
| Performance band | Top **y125**, bottom **y264**. Percussion and nominal expression/pedal mixtures share this band. |
| Percussion caps | **y177**, **74×52** bounds, at x164/256/337/418; live values above exterior **PERC / VOL / DECAY / HARM** captions. |
| Manual drawbar racks | **y269–508**, sharing x600; slots at y311–461, complete footage **below the rails**, with separate numeric readouts. |
| Upper manual | Panel begins **y528**; playing-key tops begin **y548**. |
| Lower manual | Panel begins **y698**; playing-key tops begin **y718**. |
| Cabinet artwork | **(x1132, y174, width466, height397)** at the reference size; its aspect ratio is preserved when resized. |
| Keyboard toolbar and pedals | Right-panel toolbar **(1140,614,448,64)**; pedalboard **(1138,752,450,110)** below the status rows. |

The previous percussion-row allocation offset is removed in this active layout.
Cap bounds and panel endpoints are software geometry, not measurements of every
bevel or bright photographic edge. The correct ON/OFF, NORM/SOFT, SLOW/FAST and
2ND/3RD meanings remain live. Eligibility follows the applied Upper B route,
independently of the stored ON switch. **EDIT BANK** and **SOUNDING** captions
now sit in the corresponding preset cheek; copied applied controls and pending
edits retain separate cues. Captions and gaps remain inert.

The functional inventory remains **68 ordinary controls, including 24 reversed preset keys**, plus **147 playing keys: 61 Upper + 61 Lower + 25 pedals**. The correct `1 3/5'` footage and drawbar travel from **0 at the top to 8 toward the player** take precedence over errors in the concept image. Keyboard navigation has **71 Play stops**, **ten common stops** in Rotary/Service and **eleven stops** in the MIDI dialog. These counts describe separate views, not additional sound parameters. [Workspace](docs/INTERFACE_WORKSPACE_CONTRACT.md) · [Geometry](docs/INTERFACE_GEOMETRY_CONTRACT.md) · [MIDI dialog](docs/MIDI_EXPRESSION_GUIDE.md#edit-the-midi-dialog)

| Surface | What it does |
| --- | --- |
| **Play** | Two complete manuals, all presets and pedals, nine visible drawbars per manual, independent Edit A/B, four retained banks, percussion, expression and two nominal pedal mixtures. Active wide Dimensional Play places the toolbar and pedalboard in the right cabinet panel; compact Play uses its lower pedal row. |
| **Rotary** | Cabinet reference artwork and read-only facts about the audio path, documentary target, rotor speeds, microphone geometry and brake. Unconnected or unacquired values remain explicit. |
| **Service** | Six copied-state cards and 28 rows for generator, contacts/routing, scanner, AO-28, Leslie and controls. Applied sound, retained memory, pending requests and unavailable evidence remain distinguishable. |
| **Common tools** | Save, Load, Help, Audio, MIDI, Panic and Flat remain available across workspaces. F4/F5/F6 selects Play/Rotary/Service; F7 toggles Flat. |
| **Flat and resize** | Flat retains the complete controls with rectangular keys and plain surfaces. Default size is 1280×900; minimum is 960×700. Shared hit/paint geometry and original note-release ownership survive workspace and presentation changes. |
| **MIDI settings** | Port and channel selection, expression minimum/maximum/direction, Apply, Disconnect and Close. Selected, configured, active and pending states are explicitly different; staged edits are not reported as applied. |

### Current native interface

**This is actual application output at 1672×941 after the Lower-material change.**
The Lower rack has its own rightward darkening and deterministic grain. Controls,
complete labels, held keys, registration captions and focus retain their existing
geometry and behavior. The [two-size gallery](examples/demos/lower-rack-material-v2/README.md)
and [capture provenance](examples/demos/lower-rack-material-v2/provenance.json)
bind the executable, source overlay, copied state, replay, diagnostics and pixels.

![Actual native Play at 1672 by 941 with independent Upper and Lower material fields and live controls](examples/demos/footage-typography-v1/images/play-reference-1672x941.png)

| Design evidence | View |
| --- | --- |
| Original concept | [Unmodified atlas cover/page-409 image](docs/design/atlas-cover-reference.jpg) |
| Current Lower stage | [1672×941](examples/demos/lower-rack-material-v2/images/play-reference-1672x941.png) · [1400×820 minimum active](examples/demos/lower-rack-material-v2/images/play-minimum-active-1400x820.png) |
| Retained earlier auxiliary views | [Upper-stage compact, Flat, Rotary, Service and focus gallery](examples/demos/upper-rack-material-v1/README.md) |
| Retained MIDI dialog | [960×700 calibration view](examples/demos/standalone-product-preview-v1/midi-overlay/images/midi-minimum-960x700.png) |

These captures use dummy SDL and a MIDI-disabled build. They are actual app
pixels and scripted input, with their own source identities. Physical displays,
DPI, audio hardware and semantic accessibility require separate observed journeys.
Runtime counters vary between captures; identical-state raster fixtures supply
the preservation evidence.

### Current manual footage typography

The [three actual T1 views](examples/demos/footage-typography-v1/README.md) show
1672×941, minimum-active 1400×820 and wide 1920×820 layouts. All eighteen manual
labels retain their correct musical strings. Mixed fractions use separate whole
numeral, raised numerator, slash, denominator and apostrophe runs. This changes
painted text only; control geometry and audio state remain unchanged.

The [independent comparison](docs/reviews/FOOTAGE_TYPOGRAPHY_COMPARISON.md)
passes 110 paired frames with zero changed pixels outside the admitted glyph
support, 44 exact whole frames, preserved focus pixels and unchanged material
samples. The [visual admission](docs/reviews/FOOTAGE_TYPOGRAPHY_VISUAL_ADMISSION.md)
checks every label at all three sizes. The [material fixtures](docs/reviews/FOOTAGE_MATERIAL_FIXTURE_TRANSITION.md)
and [product fixture](docs/reviews/FOOTAGE_PRODUCT_FIXTURE_TRANSITION.md)
explicitly version their affected expectations while retaining their original
contrast, state, geometry and other visual requirements. Their original failures
remain available.

The earlier Lower gallery and its failed v1/corrected v2 sampling results remain
historical evidence. The decorative keyboard rim has a separate admitted
contract and genuine pre-edit baseline. Whole-interface 1:1 remains unmet.

### Lower-rack material and measurement correction

The [frozen Lower field](docs/design/LOWER_RACK_MATERIAL_CONTRACT.md) changes only
the inset metal of the Lower registration rack. Its independent comparison
covers 98 genuine pairs and 313,612,634 pixels, with zero changed pixels/channels
outside the source-derived allowance and 37 required whole frames identical.
All 252 opaque-child probes and 25,508 cyan focus pixels are preserved.

The first measurement remains **failed: 33 of 35 screens pass**. An unchanged
opaque drawbar border lies in one supposedly quiet strip. The [independently
admitted amendment](docs/reviews/LOWER_RACK_MATERIAL_V2_ADMISSION.md) removes that
one column from the three affected rectangular samples, retains all original
results and numerical limits, and adds exact checks for 150 border pixels and
16 focus pixels. The [versioned result](docs/reviews/LOWER_RACK_COMPARISON_V2_RESULT.md)
records **98/98 passing pairs and 35/35 corrected inequalities**, with all 166 added foreground pixels preserved. The warmer lower reflection remains an
unmatched residual; corrected sampling cannot establish whole-window equality.

### Retained Upper-rack material comparison

The [frozen material contract](docs/design/UPPER_RACK_MATERIAL_CONTRACT.md)
changes only the inner metal of the Upper rack in active wide Dimensional Play.
A source-derived physical mask was fixed before comparing the genuine old and
new binaries. The [complete compressed result](docs/development/2026-11-15-streaming-continuation/reports/A20-raster-run1/report.json.gz)
records **96 pairs and 307,095,606 pixels**, **zero changed pixels or channels
outside the allowance**, and **37 required whole frames exactly equal**.
There are 216 unchanged opaque child probes and 21,864 unchanged cyan focus
pixels. The smallest ordinary active full frame protects 1,059,289 pixels;
the three tiny resource crops protect zero outside pixels and do not supply
containment evidence for a full view.

The original JPEG and actual reference-size material use the same two frozen
quiet patches. Values below are encoded-image statistics, not physical metal
measurements; the report retains full precision, raw sums and original failures.

| Image screen | Original reference | Previous material | Current material | Allowed absolute error |
| --- | ---: | ---: | ---: | ---: |
| Left patch mean | 18.291 | 31.841 | 18.334 | 2.0 |
| Right patch mean | 25.323 | 31.819 | 25.408 | 2.0 |
| Left detrended residual RMS | 1.377 | 0.487 | 1.608 | 0.4 |
| Right detrended residual RMS | 1.563 | 0.622 | 1.468 | 0.4 |
| Right-minus-left mean | 7.032 | −0.023 | 7.074 | 1.5 |

All five screens pass for the current material; the baseline fails all five.
The [independent comparison admission](docs/reviews/UPPER_RACK_COMPARISON_ADMISSION.md)
separates these narrow measurements from visual acceptance. Earlier composition
comparisons and their original failures remain in the
[previous gallery](examples/demos/whole-reference-layout-v1/README.md).

**Literal whole-interface 1:1 equality remains unmet and unwaived.** Comparing
the [original reference](docs/design/atlas-cover-reference.jpg) with the new
capture still shows different panel/wood lighting, dark wells and rims, key/cap
shading and bevels, and typography. Correct footage, the 0–8 drawbar direction,
24 real presets, expression, pedals, utility controls and truthful unconnected
model labels also differ from the concept's illustrative contents. The
[current gallery review](docs/reviews/UPPER_RACK_GALLERY_ADMISSION.md)
records these residuals separately from the improved Upper-rack material. Native display
usability, semantic accessibility, physical devices, callback deadlines and
measured audio/cabinet fidelity require their own evidence.

The [earlier percussion gallery](examples/demos/standalone-audio-preview-v1/README.md),
[product and MIDI galleries](examples/demos/standalone-product-preview-v1/README.md),
[earlier MIDI views](examples/demos/standalone-product-preview-v1/midi-overlay/README.md)
and [v5 gallery at `487064d2`](examples/demos/standalone-interface-preview-v5/README.md)
retain their historical source and admission boundaries.

## Playing, expression and external MIDI

Computer keys `A W S E D F T G Y H U J K O L P ;` play notes. **F1/F2/F3** selects Upper/Lower/Pedals; `[` and `]` change octave. Computer-piano playing remains available across workspaces. **EDIT A/B** chooses the bank being edited; reversed preset **A#** sounds bank A and **B** sounds bank B. **C#–A** selects one of nine fixed rows per manual. **C** cancels that route while retaining its selection, bank memory and held-note ownership. Enabled Upper percussion sounds only on the adjustable Upper B route. See the [preset operating guide](docs/PRESET_RUNBOOK.md).

The optional physical MIDI input uses ALSA on Linux, CoreMIDI on macOS and WinMM on Windows. Choose three distinct wire channels from 1–16:

| Division | Default channel | Accepted notes | Drawbar controllers |
| --- | ---: | --- | --- |
| Upper | 1 | MIDI 36–96 | CC16–24 edits retained Upper B. |
| Lower | 2 | MIDI 36–96 | CC16–24 edits retained Lower B. |
| Pedals | 3 | MIDI 36–60 maps to pedal IDs 1–25. | CC16–17 edits the two nominal mixtures. |

Steady organ gain does not follow Note On velocity. MIDI and UI have separate note owners, and admitted events apply in arrival order at the next audio callback boundary. MIDI receipt timestamps are not sample-offset automation. [Exact input mapping](docs/MIDI_INPUT.md) · [Backend lifecycle](docs/MIDI_BACKEND.md)

### Set CC11 endpoints and direction

Open **MIDI / Ctrl+M**, choose **EXPRESSION MIN**, **EXPRESSION MAX** and **EXPRESSION DIRECTION**, then Apply. Minimum and maximum are raw controller numbers, with **0 ≤ minimum < maximum ≤ 127**. Normal maps those endpoints to expression 0 and 1 and clamps values outside them; Inverted reverses the result. Defaults **0 / 127 / Normal** preserve the previous mapping exactly. One global expression value is shared by all mapped divisions.

For reproducible startup, append these illustrative options to the native command:

```sh
--expression-min 20 --expression-max 100 --expression-invert
```

With these example endpoints, raw CC11 **40** maps to **0.75** when inverted and **0.25** when normal. These are example settings, not measured physical pedal endpoints. The [expression guide](docs/MIDI_EXPRESSION_GUIDE.md) gives complete launch commands, all eleven modal stops, invalid-input behavior and bounded synthetic reproductions.

Editing or closing the dialog does not apply staged values. Invalid Apply preserves the existing configuration and connection. A healthy identical port/channel/calibration request keeps its connection; changing one retires the old MIDI input, releases MIDI owners, waits for acknowledgment and opens a fresh epoch. **Applying calibration sends no expression change**: the next admitted CC11 uses it. Read the active connection result separately from selected settings. Reconnect after a fault, Panic or audio restart is explicit.

### Channel-mode behavior

| Message on a mapped channel | Accepted value | Native standalone behavior |
| --- | --- | --- |
| **CC11 — Expression** | 0–127 | Uses the active endpoint/direction calibration to update shared expression. |
| **CC120 — All Sound Off** | **0 only** | Retires that division's MIDI owners. In the admitted ideal-contact standalone, contributions with no surviving owner disappear from the first sample after application. Other owners can keep the same key sounding. |
| **CC121 — Reset All Controllers** | **0 only** | Sets global expression to **1.0**, bypassing calibration/inversion. Notes, calibration, routing and the other musical controls remain. |
| **CC123 — All Notes Off** | 0–127 | Releases that division's MIDI owners. Value 0 is the MIDI-defined value; accepting other values is the receiver's retained compatibility extension. |

This is a declared native subset. CC120's immediate-contribution behavior applies to this ideal-contact model; it does not establish finite-contact, effect-tail or VST3 channel-mode support. Global **Panic** retains its separate all-owner scope. The [channel-mode contract](docs/MIDI_CHANNEL_MODE_CONTRACT.md) records admission, ownership and failure behavior.

**Save/Load stores musical controls, including expression, in `B3CONTROLS4`.** MIDI ports, channels and endpoint/direction calibration are volatile adapter settings and are not stored there. Calibration survives ordinary reconnect and audio restart within the process; CLI arguments reproduce it after quitting. Opening MIDI has its existing UI-note release policy; disconnecting MIDI itself preserves independently owned UI notes. [Persistence and recovery](docs/MIDI_EXPRESSION_GUIDE.md#save-disconnect-and-recover)

## Independent Leslie crossover foundation

The implemented **`atlas-leslie-122-ideal-crossover-v1`** models the atlas's selected four-element passive divider with **16-ohm nominal resistor loads**. Its four physical state coordinates track capacitor voltages and inductor currents. The public research API and native probe support bounded processing, checkpoint/restore, stopped sample-rate transitions and frequency-response observations; an independent Python circuit reference checks the electrical topology. [Frozen contract](docs/LESLIE_CROSSOVER_CONTRACT.md) · [Developer workflow](docs/CROSSOVER_DEVELOPER_GUIDE.md)

Native/reference comparisons qualify the declared trapezoidal frequency mapping and numerical/lifecycle behavior. **Same-Hz electrical accuracy remains an open gate** with its observed errors retained in the [characterization and plots](docs/LESLIE_CROSSOVER_CHARACTERIZATION.md). The [report-admission review](docs/reviews/PRODUCT_NUMERICAL_ADMISSION_REVIEW.md) preserves the numerical source, probe and thresholds; the corrected grid count is **126 in-band points out of 130 per response group**. A later plot metadata refresh preserves every decoded pixel. Actual component losses, source behavior, driver impedances and cabinet applicability require physical evidence. The separate [CrossoverTools component](docs/CROSSOVER_INSTALL.md) packages the probe and reference; it is not a public C++ SDK.

There is **no crossover route in Engine**, amplifier model, loudspeaker response or acoustic cabinet output from this work. M6 still requires a coupled, revision-specific electronics model. The independent [R4 waveform continuation](docs/development/2026-11-14-waveform-continuation/CHECKPOINT.md) retains its own implementation and acceptance ownership.

## Whole project plan and what comes next

The objective remains one inspectable engine for an identified B-3/AO-28 and Leslie 122, exposed through standalone and VST3 products. Leslie 147 and other hardware variants need separate profiles. The [complete M0–M9 plan](docs/PLAN.md), [acceptance matrix](docs/ACCEPTANCE_MATRIX.md) and [release assessment](docs/RELEASE_READINESS.md) distinguish implemented engineering from measured fidelity and product release.

| Milestone | Current foundation | Required continuation |
| --- | --- | --- |
| **M0 — Reference and contracts** | Preserved atlas, source identities, nominal profiles, evidence classes and acquisition planning. | Identify specimen/revisions, applicable primary sources, permissions and measured inputs. |
| **M1 — Testable core** | Prepared framework-independent core, bounded event handling, offline render and diagnostics. | Preserve timing, transactional failure, lifetime and coherent-source acceptance as models expand. |
| **M2 — Shared generator** | 91 free-running nominal sources, corroborated documentary routing, and optional prepared synthetic sparse leakage with explicit offline gain. | Acquire geared tuning, pickup waves/levels/phases, loading and leakage evidence. |
| **M3 — Console** | Manuals, pedals, fixed registrations, four retained banks, Cancel, percussion, expression and state4; separately qualified offline fractional-contact reference, explicit certified conversion and isolated causal integer-grid trajectory. | Admit causal audio reconstruction and full-window reference grading, then qualify full-organ capacity and Engine/host integration; measure contacts, loaded gains, preset behavior, percussion and expression circuits. |
| **M4 — Scanner** | Graph/compiler, independent references and prepared numerical modules. | Resolve the retained [G5 same-hertz failure](docs/SCANNER_HANDOFF.md) under its frozen contract before Engine integration. |
| **M5 — Organ electronics** | Documentary inventory and signal-boundary work. | Complete revision-specific AO-28 connectivity, operating points, transformers and loaded/nonlinear dry-output validation. |
| **M6 — Leslie electronics** | Independent ideal passive crossover and numerical/lifecycle evidence. | Declare same-Hz criteria, evaluate a separately identified numerical candidate, acquire real loads/losses, then qualify the coupled amplifier/transformer/crossover/driver model. |
| **M7 — Rotary acoustics** | Independent R2 motion/R3 propagation and implemented R4 waveform renderer/CLI. | Complete the waveform owner's remaining independent acceptance; R5 audible policy, R6 runtime integration and physical cabinet evidence remain separate. |
| **M8 — Calibration** | Capture/corpus/split tools, declared comparison policies, studies and report replay. | Execute the [physical acquisition sequence](docs/CALIBRATION_NEXT_ACQUISITION.md), then fit and evaluate held-out evidence with uncertainty. |
| **M9 — Product and release** | Canonical wide Play composition and scoped Upper/Lower material work, complete live controls, standalone workspaces, MIDI calibration/channel modes, optional VST3, stable state, actual current captures and explicit install components. | Continue the requested 1:1 visual match and qualify native callback retirement, real displays/devices/hosts, accessibility, callback deadlines, licensing and distribution. |

The next visual work is reviewed live typography and the keyboard rim, using
separate current baselines and frozen comparison support. The [footage contract
candidate](docs/design/FOOTAGE_TYPOGRAPHY_CONTRACT.md) specifies full correct
labels, fraction runs and unequal-scale behavior before implementation. The
[whole-window plan](docs/design/WHOLE_WINDOW_REFERENCE_NEXT.md) retains every
remaining visual and semantic difference. Actual use follows the [native journey
proposal](docs/design/NATIVE_ACCESSIBILITY_JOURNEY_NEXT.md) and its
[independent review](docs/reviews/NATIVE_ACCESSIBILITY_JOURNEY_NEXT_REVIEW.md).

The next concrete work is:

1. **Continue toward the requested 1:1 interface.** The canonical composition and material stages have source-bound evidence; the [Lower implementation review](docs/reviews/LOWER_RACK_IMPLEMENTATION_REVIEW.md) retains other panel/wood lighting, key/cap shading, typography and semantic differences. Declare the next material/text comparison and execute an identified native display/DPI journey for small legends, focus, held-note resize, drawbar endpoints, pending/applied captions and calibration. Preserve the [current actual gallery](examples/demos/lower-rack-material-v2/README.md) and earlier [UI acceptance requirements](docs/reviews/PRODUCT_UI_ACCEPTANCE.md); the five local material screens do not waive whole-interface equality.
2. **Continue M3 from the admitted integer-grid trajectory.** The [causal-grid guide](docs/CAUSAL_CONTACT_GRID_GUIDE.md) describes the implemented four-key, 4096-frame research epoch and its exact event/state acceptance. Freeze and independently admit the next causal audio/filter contract: use of the explicit conversion certificate, absolute source phase, partial-cell integration, latency, full-window grading and reset/tail/flush ownership. Full-organ capacity and Engine/native/VST3 scheduling, lifecycle, allocation and deadlines need separate integration acceptance. A later atlas `1e-4` grade needs an independently admitted full-window reference; the [offline study's](docs/CONTACT_SWITCHING_RESULTS.md) 64 continuous probes cannot supply it. Synchronized gesture/contact/source/dry captures remain a separate physical gate.
3. **Continue M6 through an explicit numerical and physical protocol.** Freeze frequency band, load family, magnitude/phase/complex-error criteria and independent check grid before comparing a new realization. Preserve the current same-Hz results and fixed documentary registry. [Crossover next gates](docs/CROSSOVER_DEVELOPER_GUIDE.md#5-continue-m6-through-explicit-gates)
4. **Preserve the independent model tracks.** Resolve scanner G5; continue R4 integration/publication/final acceptance with its owner; acquire complete AO-28/Leslie electrical and cabinet inputs. Validate the dry organ before fitting downstream cabinet or room effects.
5. **Complete native and release gates with observed evidence.** The [recovery review](docs/reviews/PRODUCT_NATIVE_RECOVERY_REVIEW.md) identifies a source-proven WinMM/CoreMIDI close-error observability gap. Its below-RtMidi fault-injection and checked-close task requires platform callback-retirement evidence; the review observed no hardware failure or use-after-free. Actual DAW/device journeys, native semantic accessibility, deadlines, rights and signed distribution retain separate requirements.

The [active checkpoint](docs/development/2026-11-16-conversion-material/CHECKPOINT.md)
and [actual ledger](docs/development/2026-11-16-conversion-material/assignments.json)
record current work, ownership and acceptance. The [product handoff](docs/PRODUCT_HANDOFF.md)
and separate [waveform checkpoint](docs/development/2026-11-14-waveform-continuation/CHECKPOINT.md)
retain their broader operating and ownership boundaries. Atlas research waves,
M0–M9 milestones and development staffing waves are distinct.

## Source-specific qualification

| Current continuation evidence | Observed scope |
| --- | --- |
| [Genuine starting gate](docs/development/2026-11-16-conversion-material/reports/baseline-qualification.json) | 210/210 CTests passed before production edits; original binaries/source retained. |
| [Wave-three coherent gate](docs/development/2026-11-16-conversion-material/reports/wave03-qualification.json) | 212/213 passed with 495 source inputs unchanged. The sole archived-link failure remains recorded; its [documentation-only repair](docs/development/2026-11-16-conversion-material/reports/wave03-integrity-repair.json) passes the focused integrity gate. |
| [Repaired converter integration](docs/development/2026-11-16-conversion-material/reports/wave04-converter-qualification.json) | All five registered converter CTest suites pass in 4.41 seconds. Independent numerical, transaction, resource and native scopes remain separately inspectable. |
| [Native converted-input comparison](docs/reviews/CONTACT_GRID_CONVERSION_NATIVE_REVIEW.md) | 557 native processes, 557 complete padded snapshots and 19,233 exact block-count comparisons pass; all 71 input outcomes remain visible. |
| [Resource boundary review](docs/reviews/CONTACT_GRID_CONVERSION_RESOURCE_REVIEW.md) | Actual 4,608 edges, 512 arrivals, 5,634 labels and 4,096 union knots exercised; larger admitted-input knot demand refuses within its bound. |
| [Transaction review](docs/reviews/CONTACT_GRID_CONVERSION_TRANSACTION_REVIEW.md) | Real process interruption and closed-output-pipe checks, strict certificate forgeries and preserved initial failures. |
| [Compatibility](docs/reviews/CONVERSION_MATERIAL_COMPATIBILITY.md) | Original core/state/plugin/reference-package identities preserved; a genuine before/current dry WAV is byte-identical with zero difference across 16,384 PCM samples. |
| [Separate installation](docs/reviews/CONTACT_GRID_CONVERSION_INSTALL_REVIEW.md) | 13 methods and 93 processes pass, including a relocated converter after deleting its private source/build fixture. The original 48-file component remains isolated. |
| [T1 composite local qualification](docs/development/2026-11-16-conversion-material/reports/rim-before-qualified.json) | Fresh all-target build; 218/219 in the initial full run. The sole historical product-label assertion was precisely transitioned, rebuilt, then passed all 76 cases. Every other tracked input remained unchanged. |
| [First published platform matrix](docs/development/2026-11-16-conversion-material/reports/wave04-hosted-complete.json) | 11/13 jobs pass at `3520c96`. All native standalone and VST3 jobs pass; two core jobs expose test path assumptions. [A33 repair](docs/reviews/CONTACT_GRID_CONVERSION_PLATFORM_REPAIR.md) passes locally; exact repaired hosted results are pending. |

The current local build uses Linux GCC Release, SDL 2.32.10 dummy audio/video,
and MIDI/VST3/sanitizers OFF. Subsequent exact-source hosted qualification will be recorded
after publication. These local results do not imply physical fidelity, native
accessibility, callback deadlines or literal whole-interface 1:1.

### Previous streaming publication

The earlier implementation `af2b747` and Windows I/O repair `2f57723` retain their
[completed 13-job hosted receipt](docs/development/2026-11-15-streaming-continuation/reports/hosted-2f57723-complete.json),
[210-test local qualification](docs/development/2026-11-15-streaming-continuation/reports/final-coherent-qualification.json)
and [closure handoff](docs/STREAMING_CONTINUATION_CLOSURE.md). Original failures
remain available. Those named revisions qualify their own source, not the new
conversion or Lower changes. The earlier platform history below is also retained.

### Earlier product platform qualification

The published repaired product source was **[`80b8cce1773e4c31bf64cb6c2b7f43e8445ec3fe`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/80b8cce1773e4c31bf64cb6c2b7f43e8445ec3fe)**,
tree **`d310be065db2bb9b0012c11a0c5ec2beda4c9384`**, with parent c4486ba.
The [publication receipt](docs/development/2026-11-15-product-continuation/reports/checker-portability-publication.json)
records the guarded nonforced update and fetched identity. Its
[required primary hosted qualification](docs/development/2026-11-15-product-continuation/reports/root-final-hosted.json)
passes **all thirteen required jobs** at that exact source. The closing commit
contains documentation and evidence only; the tested code remains 80b8cce.

| Required gate at 80b8cce | Actual result |
| --- | --- |
| Core Release — Linux, Windows and macOS | **157/157 on each platform** |
| Linux core ASan/UBSan/leak checks | **157/157** |
| Native Release — Linux MIDI ON/OFF, Windows and macOS | **48/48 in each of four configurations** |
| Linux native ASan/UBSan/leak checks | **21/21**, with verified instrumented inputs/runtime links |
| Native VST3 — Linux / macOS / Windows | **8/8 / 7/7 / 7/7**; **47/47 plug-in-validator checks** on each platform |
| Complete R4 waveform experiment | **Full mode passed**, with 14 report-admission checks |
| Actual product-session records — Linux Release | **60 accepted/verified agents and notes, ten waves, zero errors** |

[Core and full R4 CI](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43674212267) · [Native standalone CI](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43674212230) · [Native VST3 CI](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43674212303)

The previous c448 matrix completed **11 successful / two failed jobs**. Its new
record checker exposed a macOS temporary-path alias in the failure-injection
tests and incompatible Windows path/descriptor timestamp meanings. The
[macOS reproduction](docs/development/2026-11-15-product-continuation/reports/final-source-macos-portability-repair.json),
[Windows repair](docs/development/2026-11-15-product-continuation/reports/final-source-windows-portability-repair.json)
and [independent review](docs/development/2026-11-15-product-continuation/reports/final-checker-portability-independent-review.json)
retain the original failures and narrow fixes. Four new reader methods cover
30 synthetic subcases; that 23-method module passed locally. The retained
strict ledger still verifies **60 accepted agents, 60 notes, ten waves and zero
errors**, with unchanged manifest/note identities.

The earlier [coherent local build](docs/development/2026-11-15-product-continuation/reports/wave8-coherent-build.json)
passed **180/180 in 507.55 s** over its 366 recorded inputs. The portable checker
and test module now differ in two files; **364 inputs and all three recorded
binaries remain unchanged**. The [affected registered CTest](docs/development/2026-11-15-product-continuation/reports/checker-portability-root-verification.json)
passes in **1.31 s**. No application, model, build or workflow code changed in
this repair. The old 180-test result is not attributed to changed inputs.

That product revision's native material evidence is **1,293 assertions / 109
frames**, and its installed Standalone payloads contain **16 files MIDI-OFF /
20 MIDI-ON**.
Original b9 installation failures, d556 sanitizer build failure and c448 checker
failures remain in [Status](docs/STATUS.md) and the source-specific reports.
Local leak-enabled execution was blocked by ptrace; the
[failure and empty-main control](docs/development/2026-11-15-product-continuation/notes/A25-crossover-allocation.md)
remain separate from hosted success. No new leak exception was added. Dummy SDL,
software raster and synchronous MIDI fixtures do not establish physical devices,
OS callback races, native accessibility, DAW journeys or runtime deadlines.

### Historical evidence retained

| Record | What it qualifies |
| --- | --- |
| [Reference-refinement closure](docs/REFERENCE_REFINEMENT_CLOSURE.md) | The completed earlier sixty-agent session and `fd2f6060` source: 166/166 local tests and thirteen hosted jobs, with its exact receipts and retained earlier failures. |
| [v5 native gallery](examples/demos/standalone-interface-preview-v5/README.md) | Eight actual views at `487064d2`, independently admitted with their original source, executable, state and pixels. It predates current product refinement. |
| [v4 native gallery](examples/demos/standalone-interface-preview-v4/README.md) and [header audit](docs/reviews/REFERENCE_REFINEMENT_HEADER_HOSTED.md) | The earlier `0881d1f4` header source and its separate capture/platform evidence. |
| [Earlier interface recovery](docs/INTERFACE_RECOVERY_HANDOFF.md) | The completed interface session, named-revision qualification and unavailable original local evidence; recovery prose is not replacement artifact bytes. |
| [Full waveform experiment](docs/development/2026-11-14-waveform-continuation/reports/full-waveform/qualification.json) | Its four-rate/24-partition frozen numerical workload. It does not replace the waveform owner’s integration, publication and final acceptance of its separate R4 results, or live integration gates. |
| [Standalone platform audit](docs/reviews/STANDALONE_FINAL_PLATFORM_AUDIT.md), [pedal audit](docs/reviews/PEDAL_FINAL_PLATFORM.md) and [calibration audit](docs/reviews/CALIBRATION_FINAL_HOSTED.md) | Earlier exact-source platform/package and toolchain observations, including their failures, repairs and scope limits. |

Older [v1](examples/demos/standalone-interface-preview-v1/README.md), [v2](examples/demos/standalone-interface-preview-v2/README.md), [v3](examples/demos/standalone-interface-preview-v3/README.md), [original window](examples/demos/standalone-window-v1/README.md) and [chapel audition](examples/demos/standalone-chapel-v1/README.md) remain historical evidence. No older capture or test result is retagged as a current run.

## Repeatable audio examples

These recordings demonstrate the named nominal models and retained inputs; they are synthetic engineering examples.

| Audio | Retained package |
| --- | --- |
| [Three-second two-manual and pedal phrase](examples/demos/pedal-phrase-v1/bundle/render.wav) | [Score, profile, schema-3 evidence and replay](examples/demos/pedal-phrase-v1/README.md); [independent acceptance](docs/reviews/PEDAL_DEMO_ACCEPTANCE.md). |
| [Two-second nominal console example](examples/rendered/nominal-console-v2/bundle/render.wav) | [Partial key travel, shared percussion, Cancel/reselection and schema-2 evidence](examples/rendered/nominal-console-v2/README.md). Its partial-key plot is a separate diagnostic scenario. |
| [Original four-second dry organ](examples/rendered/nominal-two-manual-v1/bundle/render.wav) | [Earlier ideal-contact, percussion-off evidence and replay](examples/rendered/nominal-two-manual-v1/README.md). |

[Event fixtures](examples/README.md), [render evidence](docs/RENDER_EVIDENCE.md), the [independent PCM analyzer](docs/AUDIO_MEASUREMENTS.md) and [bundle verifier](docs/RENDER_VERIFICATION.md) explain reproducible rendering and inspection.

## Documentation and source

| Start here | Purpose |
| --- | --- |
| [Project guide](docs/PROJECT_GUIDE.md) | Reading order and the wider technical/documentary index. |
| [Status](docs/STATUS.md), [Next steps](docs/NEXT_STEPS.md), [development log](docs/DEVELOPMENT_LOG.md) | Implemented work, observed checks, open gates and concrete continuation. |
| [Active contact/material session](docs/development/2026-11-15-streaming-continuation/README.md), [scope](docs/development/2026-11-15-streaming-continuation/SCOPE.md) and [checkpoint](docs/development/2026-11-15-streaming-continuation/CHECKPOINT.md) | Current M3/M9 scope, actual assignment ownership, exact setup and future-agent recovery. |
| [Complete M0–M9 plan](docs/PLAN.md), [acceptance matrix](docs/ACCEPTANCE_MATRIX.md), [release readiness](docs/RELEASE_READINESS.md) | Whole-project dependencies and evidence required to finish. |
| [Interface guide](docs/INTERFACE_RUNBOOK.md), [expression guide](docs/MIDI_EXPRESSION_GUIDE.md), [preset guide](docs/PRESET_RUNBOOK.md) | Current standalone operation, controller calibration and registration/state behavior. |
| [Contact reference guide](docs/CONTACT_SWITCHING_GUIDE.md), [installation](docs/CONTACT_REFERENCE_INSTALL.md), [results](docs/CONTACT_SWITCHING_RESULTS.md) | Offline M3 operation, relocated package, frozen numerical admission and remaining causal/physical gates. |
| [Causal contact grid guide](docs/CAUSAL_CONTACT_GRID_GUIDE.md), [contract](docs/CAUSAL_CONTACT_GRID_CONTRACT.md) | Exact integer-input trajectories, lifecycle, native transport, tests and remaining filter/integration work. |
| [Parameters](docs/PARAMETERS.md), [control state](docs/CONTROL_STATE_FORMAT.md), [Engine API](docs/ENGINE_API.md) | Stable sound identities, state4/readers 1–3 and core timing/ownership. |
| [Scanner handoff](docs/SCANNER_HANDOFF.md), [crossover guide](docs/CROSSOVER_DEVELOPER_GUIDE.md), [waveform checkpoint](docs/development/2026-11-14-waveform-continuation/CHECKPOINT.md) | Separate model implementations, source-specific evidence and remaining numerical gates. |
| [Calibration handoff](docs/CALIBRATION_HANDOFF.md) and [next acquisition](docs/CALIBRATION_NEXT_ACQUISITION.md) | Existing capture tooling and missing real inputs. |
| [Build instructions](docs/BUILD.md), [VST3 build](docs/VST3_BUILD.md), [core CI](docs/CI.md), [native CI](docs/VST3_CI.md) | Reproducible configurations and separate platform/adapter qualification. |
| [Complete atlas review](docs/research/ATLAS_REVIEW.md), [chapter index](docs/research/chapter-index.json), [source manifest](docs/research/source-manifest.json) | Full 500-page coverage, source identity, interpretations and missing companion assets. |
| [Original session handoff](docs/SESSION_HANDOFF.md), [earlier refinement handoff](docs/REFERENCE_REFINEMENT_HANDOFF.md) | Preserved dated commands and evidence; use the active checkpoint for current work. |
| [Agent instructions](AGENTS.md), [repository checks](docs/REPOSITORY_CHECKS.md) | Standing continuation/publication workflow and read-only source/link integrity checks. |

The unchanged [research atlas](Hammond_B3_Leslie_Research_Atlas_500pp.pdf) contains 80 chapters across 500 pages. The original [complete review](docs/research/ATLAS_REVIEW.md) and the current session's [six direct reading records](docs/development/2026-11-15-streaming-continuation/reports/atlas-reading-coverage.json) cover every page. Coverage does not independently validate all underlying manufacturer sources or supply physical measurements. Referenced companion files absent from the baseline remain absent; new code/data retain reconstruction identities.

The nominal generator uses 12-TET, ideal shared sine sources, proposed phases and normalized amplitude. Two independent direct-image factory-table transcriptions corroborate the retained routing in the [factory comparison](docs/FACTORY_REFERENCE.md). They do not calibrate tuning, pickup levels, contact timing, circuits, rotors or acoustics. Historical G-G service readings are not oscillator amplitudes.

The [dependency and rights inventory](docs/DEPENDENCIES_AND_RIGHTS.md) and [third-party notices](THIRD_PARTY_NOTICES.md) retain provenance and unresolved permissions. **No project-wide license has been selected.** Future work follows [AGENTS.md](AGENTS.md): recover the whole plan, preserve concurrent work, continue a dependency-ready phase, retain actual verification, update setup/status/next steps/log and current UI captures, then commit and publish authorized completed work with a verified revision.
