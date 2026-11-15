# Hammond B-3 Organ

A C++20 Hammond B-3/AO-28 and Leslie research instrument, guided by the repository's **500-page atlas**. The playable instrument is a **nominal dry organ** with a native standalone application, an offline renderer and an optional VST3 adapter. Its musical core has 91 continuously running sources, two 61-key manuals, 25 pedals, eighteen documentary fixed registrations, four retained drawbar banks, percussion and shared expression.

The current [product continuation](docs/development/2026-11-15-product-continuation/README.md) advances three practical areas:

| Area | Available now |
| --- | --- |
| **Native MIDI expression and channel modes — M9** | Set CC11 minimum, maximum and Normal/Inverted direction in the MIDI dialog or CLI. Scoped CC120, expression reset CC121 and the existing CC123 preserve distinct ownership and control behavior. [Operating guide](docs/MIDI_EXPRESSION_GUIDE.md) |
| **Wide Dimensional interface — M9** | Complete fitted footage labels, larger manual drawbar caps, separate **EDIT BANK** / **SOUNDING** captions and restrained natural-key lighting. The MIDI dialog adds explicit calibration and connection state. [Design and evidence](docs/PRODUCT_VISUAL_REFINEMENT.md) |
| **Independent passive crossover — M6** | A four-state ideal Leslie 122 electrical model, native probe, independent analog reference and numerical/lifecycle checks. It remains separate from the playable Engine. [Developer guide](docs/CROSSOVER_DEVELOPER_GUIDE.md) |

The **47 sound parameters**, **`B3CONTROLS4`** writer and readers for versions **1–3** retain their meanings. MIDI calibration is native adapter configuration; it adds no sound parameter or VST3 mapping. Scanner, AO-28 and Leslie audio are not connected to the dry Engine. The [compatibility review](docs/PRODUCT_COMPATIBILITY.md) and [full plan](docs/PLAN.md) preserve these boundaries.

[Get started](#getting-started) · [Play and configure MIDI](docs/MIDI_EXPRESSION_GUIDE.md) · [Interface guide](docs/INTERFACE_RUNBOOK.md) · [Current status](docs/STATUS.md) · [Next steps](docs/NEXT_STEPS.md) · [M0–M9 plan](docs/PLAN.md) · [Active session handoff](docs/development/2026-11-15-product-continuation/CHECKPOINT.md)

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
./build-native-midi/apps/standalone/hammond_standalone
```

This uses **SDL 2.32.10** and **RtMidi 6.0.0**. Use the acquisition tools' `--verify-existing` option for an existing dependency checkout. Windows/PowerShell commands, platform packages and multi-configuration executable paths are in the [setup guide](docs/MIDI_EXPRESSION_GUIDE.md#build-the-native-application). For keyboard/pointer operation without a physical MIDI backend, omit RtMidi acquisition and `HAMMOND_RTMIDI_ROOT`, and configure with `-DHAMMOND_ENABLE_MIDI=OFF`; SDL is still required. The [Standalone installation guide](docs/STANDALONE_INSTALL.md) describes an explicit relocatable install.

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

Other development paths have their own setup: [optional VST3 and pinned SDK](docs/VST3_BUILD.md), [independent crossover targets](docs/CROSSOVER_DEVELOPER_GUIDE.md), [CrossoverTools installation](docs/CROSSOVER_INSTALL.md), [rotary waveform CLI](docs/ROTARY_RENDER_CLI.md) and [capture/calibration tools](docs/CALIBRATION_RUNBOOK.md). VST3 requires CMake 3.25+ and its separately acquired SDK; the native interface shown here is the standalone application.

## Native interface and UI/UX

The application follows the atlas's walnut, charcoal and brass [cover/page-409 concept](docs/design/atlas-cover-reference.jpg), with [retained source provenance](docs/design/atlas-reference.json). Controls, labels, drawbar positions, held notes and focus are live application output. The cabinet image supplies decoration; it does not indicate connected Leslie audio.

**Current wide Dimensional refinement** applies when width is at least **1400** and height at least **820**. Manual racks use complete fitted footage, **32-pixel caps**, distinct numeric readouts and separate **EDIT BANK** and **SOUNDING** rows. Sounding captions come from copied applied controls; pending edits keep their own cue. Idle natural keys gain subtle lighting within their existing projected surfaces. This manual-rack/key treatment preserves the accepted header, layout, compact and Flat rendering; the MIDI overlay is a separate change. [Scoped implementation and acceptance](docs/PRODUCT_VISUAL_REFINEMENT.md) · [Reference comparison and remaining gaps](docs/design/PRODUCT_REFERENCE_GAPS.md)

The functional inventory remains **68 ordinary controls, including 24 reversed preset keys**, plus **147 playing keys: 61 Upper + 61 Lower + 25 pedals**. The correct `1 3/5'` footage and drawbar travel from **0 at the top to 8 toward the player** take precedence over errors in the concept image. Keyboard navigation has **71 Play stops**, **ten common stops** in Rotary/Service and **eleven stops** in the MIDI dialog. These counts describe separate views, not additional sound parameters. [Workspace](docs/INTERFACE_WORKSPACE_CONTRACT.md) · [Geometry](docs/INTERFACE_GEOMETRY_CONTRACT.md) · [MIDI dialog](docs/MIDI_EXPRESSION_GUIDE.md#edit-the-midi-dialog)

| Surface | What it does |
| --- | --- |
| **Play** | Two complete manuals, all presets and pedals, nine visible drawbars per manual, independent Edit A/B, four retained banks, percussion, expression and two nominal pedal mixtures. Wide/tall Play places the pedalboard beneath the cabinet; compact Play uses its lower pedal row. |
| **Rotary** | Cabinet reference artwork and read-only facts about the audio path, documentary target, rotor speeds, microphone geometry and brake. Unconnected or unacquired values remain explicit. |
| **Service** | Six copied-state cards and 28 rows for generator, contacts/routing, scanner, AO-28, Leslie and controls. Applied sound, retained memory, pending requests and unavailable evidence remain distinguishable. |
| **Common tools** | Save, Load, Help, Audio, MIDI, Panic and Flat remain available across workspaces. F4/F5/F6 selects Play/Rotary/Service; F7 toggles Flat. |
| **Flat and resize** | Flat retains the complete controls with rectangular keys and plain surfaces. Default size is 1280×900; minimum is 960×700. Shared hit/paint geometry and original note-release ownership survive workspace and presentation changes. |
| **MIDI settings** | Port and channel selection, expression minimum/maximum/direction, Apply, Disconnect and Close. Selected, configured, active and pending states are explicitly different; staged edits are not reported as applied. |

### Current native interface

**These are actual captures of the current product interface**, recorded at [`d556da01`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/d556da017ea0a5d4f2d231416782dbc5066e58c2). The wide Play frame shows the larger caps, complete footage, separate edited/sounding registrations and keyboard materials. It retains four held notes while a retained drawbar is edited; the sounding fixed registrations remain explicitly identified.

![Current native Play at 1672 by 941 with complete footage, larger drawbar caps and explicit edited versus sounding registrations](examples/demos/standalone-product-preview-v1/images/play-reference-1672x941.png)

The calibration dialog at the minimum 960×700 window shows illustrative raw endpoints **20 / 100 / Inverted**, keyboard focus on Direction, and **no active MIDI connection**. All eleven modal focus stops were witnessed in the native painted history. These captures use the MIDI-disabled build; the setup above explains how to enable a physical backend.

![Current native MIDI calibration dialog at 960 by 700 with endpoint and direction controls and truthful inactive connection state](examples/demos/standalone-product-preview-v1/midi-overlay/images/midi-minimum-960x700.png)

| More actual views | Capture and review evidence |
| --- | --- |
| [Play at the default size](examples/demos/standalone-product-preview-v1/images/play-default-1280x900.png) · [minimum size](examples/demos/standalone-product-preview-v1/images/play-minimum-960x700.png) · [Flat](examples/demos/standalone-product-preview-v1/images/flat-minimum-960x700.png) | [Eight-view gallery](examples/demos/standalone-product-preview-v1/README.md) · [normal provenance](examples/demos/standalone-product-preview-v1/provenance.json) |
| [Rotary](examples/demos/standalone-product-preview-v1/images/rotary-reference-1672x941.png) · [Service](examples/demos/standalone-product-preview-v1/images/service-reference-1672x941.png) | [Three MIDI views](examples/demos/standalone-product-preview-v1/midi-overlay/README.md) · [modal provenance](examples/demos/standalone-product-preview-v1/midi-overlay/provenance.json) |
| [Original reference image](docs/design/atlas-cover-reference.jpg) · [reference comparison](docs/design/PRODUCT_REFERENCE_GAPS.md) | [Independent admission of all eleven frames](docs/reviews/PRODUCT_GALLERY_ADMISSION.md) · [machine-readable review](docs/development/2026-11-15-product-continuation/reports/A41-gallery-admission.json) |

The captures use SDL dummy audio/video, a software renderer and equal logical/drawable dimensions. Source, executable, replay, control state and decoded image identities are retained. The admission records the earlier build-receipt boundary and the unavailable original BMP intermediates; retained PNGs match their recorded native-pixel hashes. The [historical v5 gallery at `487064d2`](examples/demos/standalone-interface-preview-v5/README.md) and all earlier galleries remain preserved.

**Literal whole-interface 1:1 equality remains unproved.** The [reference-gap review](docs/design/PRODUCT_REFERENCE_GAPS.md) identifies remaining rack composition, deck/rim shading, key material and small-text differences. Complete manuals, 24 presets, 25 pedals, real utilities and the **NOMINAL DRY ORGAN** caption preserve correct product meaning. The existing relative paint-cost check does not establish an interactive frame rate; native display usability, semantic accessibility, physical devices and measured cabinet fidelity remain separate gates.

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

Native/reference comparisons qualify the declared trapezoidal frequency mapping and numerical/lifecycle behavior. **Same-Hz electrical accuracy remains an open gate** with its observed errors retained in the [characterization and plots](docs/LESLIE_CROSSOVER_CHARACTERIZATION.md). Actual component losses, source behavior, driver impedances and cabinet applicability require physical evidence. The separate [CrossoverTools component](docs/CROSSOVER_INSTALL.md) packages the probe and reference; it is not a public C++ SDK.

There is **no crossover route in Engine**, amplifier model, loudspeaker response or acoustic cabinet output from this work. M6 still requires a coupled, revision-specific electronics model. The independent [R4 waveform continuation](docs/development/2026-11-14-waveform-continuation/CHECKPOINT.md) retains its own implementation and acceptance ownership.

## Whole project plan and what comes next

The objective remains one inspectable engine for an identified B-3/AO-28 and Leslie 122, exposed through standalone and VST3 products. Leslie 147 and other hardware variants need separate profiles. The [complete M0–M9 plan](docs/PLAN.md), [acceptance matrix](docs/ACCEPTANCE_MATRIX.md) and [release assessment](docs/RELEASE_READINESS.md) distinguish implemented engineering from measured fidelity and product release.

| Milestone | Current foundation | Required continuation |
| --- | --- | --- |
| **M0 — Reference and contracts** | Preserved atlas, source identities, nominal profiles, evidence classes and acquisition planning. | Identify specimen/revisions, applicable primary sources, permissions and measured inputs. |
| **M1 — Testable core** | Prepared framework-independent core, bounded event handling, offline render and diagnostics. | Preserve timing, transactional failure, lifetime and coherent-source acceptance as models expand. |
| **M2 — Shared generator** | 91 free-running nominal sources and independently corroborated documentary routing. | Acquire geared tuning, pickup waves/levels/phases, loading and leakage evidence. |
| **M3 — Console** | Manuals, pedals, fixed registrations, four retained banks, Cancel, percussion, expression and state4. | Measure contacts, loaded gains, preset behavior, percussion and expression circuits. Adapter calibration is a separate feature. |
| **M4 — Scanner** | Graph/compiler, independent references and prepared numerical modules. | Resolve the retained [G5 same-hertz failure](docs/SCANNER_HANDOFF.md) under its frozen contract before Engine integration. |
| **M5 — Organ electronics** | Documentary inventory and signal-boundary work. | Complete revision-specific AO-28 connectivity, operating points, transformers and loaded/nonlinear dry-output validation. |
| **M6 — Leslie electronics** | Independent ideal passive crossover and numerical/lifecycle evidence. | Declare same-Hz criteria, evaluate a separately identified numerical candidate, acquire real loads/losses, then qualify the coupled amplifier/transformer/crossover/driver model. |
| **M7 — Rotary acoustics** | Independent R2 motion/R3 propagation and implemented R4 waveform renderer/CLI. | Complete the waveform owner's remaining independent acceptance; R5 audible policy, R6 runtime integration and physical cabinet evidence remain separate. |
| **M8 — Calibration** | Capture/corpus/split tools, declared comparison policies, studies and report replay. | Execute the [physical acquisition sequence](docs/CALIBRATION_NEXT_ACQUISITION.md), then fit and evaluate held-out evidence with uncertainty. |
| **M9 — Product and release** | Standalone workspaces, MIDI calibration/channel modes, optional VST3, stable automation/state and install components. | Admit current captures; qualify real displays/devices/hosts, accessibility, callback deadlines, platform payloads, licensing and distribution. |

The next concrete work is:

1. **Finish current native evidence and qualification.** Capture and independently admit the actual changed application at reference/default/minimum sizes, Flat and the separate MIDI overlay. Qualify the expanded modal, native recovery, installation and the exact published source. Refresh README from admitted captures while preserving v1–v5.
2. **Assess display usability before further decoration.** Check the smallest legends and status/helper text on an identified native display/DPI; exercise focus, held-note resize, drawbar endpoints, pending/applied captions and calibration. The [gap review](docs/design/PRODUCT_REFERENCE_GAPS.md) identifies deck/rim lighting as a later bounded material candidate.
3. **Continue M6 through an explicit numerical and physical protocol.** Freeze frequency band, load family, magnitude/phase/complex-error criteria and independent check grid before comparing a new realization. Preserve the current same-Hz results and fixed documentary registry. [Crossover next gates](docs/CROSSOVER_DEVELOPER_GUIDE.md#5-continue-m6-through-explicit-gates)
4. **Preserve the independent model tracks.** Resolve scanner G5; continue R4 acceptance with its owner; acquire complete AO-28/Leslie electrical and cabinet inputs. Validate the dry organ before fitting downstream cabinet or room effects.
5. **Complete release gates with observed evidence.** Actual DAW/device journeys, native semantic accessibility, deadlines, rights and signed distribution need their own results. Completed worker ledgers, numerical tests and screenshots do not establish physical completion.

The [active session handoff](docs/development/2026-11-15-product-continuation/CHECKPOINT.md) records current source, shared build ownership and immediate commands; its [actual manifest](docs/development/2026-11-15-product-continuation/assignments.json) records real work and acceptance. The [waveform checkpoint](docs/development/2026-11-14-waveform-continuation/CHECKPOINT.md) owns R4. The atlas's research waves, M0–M9 milestones and each development session's worker waves are different organizations.

## Source-specific qualification

At this documentation checkpoint, published source **`b9d352a82ac1afdec70c76ec5b1987785a37762e`** retains the feature implementation and the later native-lifecycle fixture, crossover install and characterization work. Its [publication receipt](docs/development/2026-11-15-product-continuation/reports/calibration-install-publication.json) verifies the commit/tree/parent. The [b9 Linux Release result](docs/development/2026-11-15-product-continuation/reports/b9-linux-crossover-install-failure.txt) exposed a CMake portability failure in crossover installation. The subsequent repair needs its own source-specific hosted result; follow the [active checkpoint](docs/development/2026-11-15-product-continuation/CHECKPOINT.md) for current repair and qualification. Later fixture/install changes do not inherit an earlier full-suite or hosted pass.

The main feature source **`ff41d412d03f2c5767aa4057b29fa8ec1627449b`** has a [coherent all-target Release build and 176/176 local CTest result](docs/development/2026-11-15-product-continuation/reports/wave4-coherent-build.json): GCC 14.2, standalone enabled, physical MIDI backend and VST3 disabled, with explicit dummy SDL for native tests. All **13 hosted job statuses** at that source report success in the [retained status receipt](docs/development/2026-11-15-product-continuation/reports/implementation-hosted-status.json); the source-specific primary-log audit remains separate. These observations do not qualify later changed fixtures or installation code, physical hardware or runtime deadlines.

The current [visual acceptance](docs/development/2026-11-15-product-continuation/notes/A23-visual-acceptance.md), [native CLI/replay acceptance](docs/development/2026-11-15-product-continuation/notes/A24-native-midi-acceptance.md), [real-main calibration fixture](docs/development/2026-11-15-product-continuation/notes/A26-native-calibration-lifecycle.md) and [crossover response evidence](docs/development/2026-11-15-product-continuation/reports/crossover-response-acceptance.json) retain their own inputs and limits. Local leak-enabled sanitizer execution was blocked by the environment's ptrace restriction; its [original failure and control](docs/development/2026-11-15-product-continuation/notes/A25-crossover-allocation.md) remain distinct from hosted results. Follow [Status](docs/STATUS.md) and the live checkpoint for later observed outcomes.

### Historical evidence retained

| Record | What it qualifies |
| --- | --- |
| [Reference-refinement closure](docs/REFERENCE_REFINEMENT_CLOSURE.md) | The completed earlier sixty-agent session and `fd2f6060` source: 166/166 local tests and thirteen hosted jobs, with its exact receipts and retained earlier failures. |
| [v5 native gallery](examples/demos/standalone-interface-preview-v5/README.md) | Eight actual views at `487064d2`, independently admitted with their original source, executable, state and pixels. It predates current product refinement. |
| [v4 native gallery](examples/demos/standalone-interface-preview-v4/README.md) and [header audit](docs/reviews/REFERENCE_REFINEMENT_HEADER_HOSTED.md) | The earlier `0881d1f4` header source and its separate capture/platform evidence. |
| [Earlier interface recovery](docs/INTERFACE_RECOVERY_HANDOFF.md) | The completed interface session, named-revision qualification and unavailable original local evidence; recovery prose is not replacement artifact bytes. |
| [Full waveform experiment](docs/development/2026-11-14-waveform-continuation/reports/full-waveform/qualification.json) | Its four-rate/24-partition frozen numerical workload. It does not replace remaining R4 lifecycle/symmetry/allocation/CLI or live integration gates. |
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
| [Active product session](docs/development/2026-11-15-product-continuation/README.md) and [checkpoint](docs/development/2026-11-15-product-continuation/CHECKPOINT.md) | Current M9/M6 scope, actual assignment ownership, setup and recovery. |
| [Complete M0–M9 plan](docs/PLAN.md), [acceptance matrix](docs/ACCEPTANCE_MATRIX.md), [release readiness](docs/RELEASE_READINESS.md) | Whole-project dependencies and evidence required to finish. |
| [Interface guide](docs/INTERFACE_RUNBOOK.md), [expression guide](docs/MIDI_EXPRESSION_GUIDE.md), [preset guide](docs/PRESET_RUNBOOK.md) | Current standalone operation, controller calibration and registration/state behavior. |
| [Parameters](docs/PARAMETERS.md), [control state](docs/CONTROL_STATE_FORMAT.md), [Engine API](docs/ENGINE_API.md) | Stable sound identities, state4/readers 1–3 and core timing/ownership. |
| [Scanner handoff](docs/SCANNER_HANDOFF.md), [crossover guide](docs/CROSSOVER_DEVELOPER_GUIDE.md), [waveform checkpoint](docs/development/2026-11-14-waveform-continuation/CHECKPOINT.md) | Separate model implementations, source-specific evidence and remaining numerical gates. |
| [Calibration handoff](docs/CALIBRATION_HANDOFF.md) and [next acquisition](docs/CALIBRATION_NEXT_ACQUISITION.md) | Existing capture tooling and missing real inputs. |
| [Build instructions](docs/BUILD.md), [VST3 build](docs/VST3_BUILD.md), [core CI](docs/CI.md), [native CI](docs/VST3_CI.md) | Reproducible configurations and separate platform/adapter qualification. |
| [Complete atlas review](docs/research/ATLAS_REVIEW.md), [chapter index](docs/research/chapter-index.json), [source manifest](docs/research/source-manifest.json) | Full 500-page coverage, source identity, interpretations and missing companion assets. |
| [Original session handoff](docs/SESSION_HANDOFF.md), [earlier refinement handoff](docs/REFERENCE_REFINEMENT_HANDOFF.md) | Preserved dated commands and evidence; use the active checkpoint for current work. |
| [Agent instructions](AGENTS.md), [repository checks](docs/REPOSITORY_CHECKS.md) | Standing continuation/publication workflow and read-only source/link integrity checks. |

The unchanged [research atlas](Hammond_B3_Leslie_Research_Atlas_500pp.pdf) contains 80 chapters across 500 pages. The original [complete review](docs/research/ATLAS_REVIEW.md) and the current session's six readings, recorded in its [checkpoint](docs/development/2026-11-15-product-continuation/CHECKPOINT.md), cover every page. Coverage does not independently validate all underlying manufacturer sources or supply physical measurements. Referenced companion files absent from the baseline remain absent; new code/data retain reconstruction identities.

The nominal generator uses 12-TET, ideal shared sine sources, proposed phases and normalized amplitude. Two independent direct-image factory-table transcriptions corroborate the retained routing in the [factory comparison](docs/FACTORY_REFERENCE.md). They do not calibrate tuning, pickup levels, contact timing, circuits, rotors or acoustics. Historical G-G service readings are not oscillator amplitudes.

The [dependency and rights inventory](docs/DEPENDENCIES_AND_RIGHTS.md) and [third-party notices](THIRD_PARTY_NOTICES.md) retain provenance and unresolved permissions. **No project-wide license has been selected.** Future work follows [AGENTS.md](AGENTS.md): recover the whole plan, preserve concurrent work, continue a dependency-ready phase, retain actual verification, update setup/status/next steps/log and current UI captures, then commit and publish authorized completed work with a verified revision.
