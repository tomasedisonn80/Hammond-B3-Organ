# Reference refinement: setup and continuation handoff

The current playable instrument is a **nominal dry organ**. This continuation
adds the reference-led wide layout, material and inspection repairs, copied
input observations, and independently tested native **R2 motion / R3 historical
propagation**. The numerical primitives return motion/path facts; they do not
render Leslie audio or enter Engine. The 47 parameter identities,
`B3CONTROLS4` writer, readers 1–3, 91 shared sources, two 61-key manuals and
25 pedals retain their meanings. [Scope](REFERENCE_REFINEMENT_SCOPE.md) ·
[audio/state isolation](development/2026-11-14-reference-refinement/notes/A34-audio-state-isolation.md)

Start each continuation with [AGENTS.md](../AGENTS.md),
[current status](STATUS.md), [next steps](NEXT_STEPS.md), the
[live checkpoint](development/2026-11-14-reference-refinement/CHECKPOINT.md)
and [actual manifest](development/2026-11-14-reference-refinement/assignments.json).
Those records own progress after this source-specific handoff. The requested
sixty workers in ten logical waves are still being completed at A37; historical
workers do not count toward this session. All 500 atlas pages have already been
read in six complete assignments; use the
[retained full review](research/REFERENCE_REFINEMENT_ATLAS_REVIEW.md) rather
than restarting it after a context reset.

## Source and qualification to resume

| Item | Retained identity or evidence |
| --- | --- |
| Session starting source | `8bd999efc13e309b932e6ac41d72ceb7b9b80a5f` |
| Published native/acceptance checkpoint | [`2e161dc3a60fc3442051799574feed37bffbfc5c`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/2e161dc3a60fc3442051799574feed37bffbfc5c), tree `17f8e4d698f903c37bff09deee196ea73e0da108`; [independent publication receipt](development/2026-11-14-reference-refinement/reports/root-native-publication.json) |
| PDF | `Hammond_B3_Leslie_Research_Atlas_500pp.pdf`, 500 pages; SHA-256 `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| Original visual target | [Cover/page-409 reference](design/atlas-cover-reference.jpg), 1672×941; SHA-256 `9d802c3577367a904516fdd90dd51effb73bc3d0c692c1c7a2fa29699d54a187`; [ancestry](design/atlas-reference.json) |
| Actual native v3 gallery | [Eight views and reproduction](../examples/demos/standalone-interface-preview-v3/README.md), captured from `2e161dc`; executable SHA-256 `97ed35cbf618792155c15106862d8bc5f416b7cf6d073c9e37e94babdf8bc9a9` |

The [A31 capture](development/2026-11-14-reference-refinement/notes/A31-native-gallery.md)
matched all 111 qualified product/build-source entries before and after its
incremental target build and eight native processes. The
[A32 independent audit](development/2026-11-14-reference-refinement/notes/A32-gallery-independent.md)
checks retained payloads, decoded pixels, input identities and exact painted
2/1/1 held targets. This is source-identified capture evidence, not a hermetic
build attestation. A changed executable needs new qualification and a fresh
gallery directory; preserve v1/v2/v3 and their original provenance.

The integrated GCC Release run passed **154/155** suites. Its sole failure was
the capture-install fixture omitting the two newly declared native probe files
from its private source copy. Adding those files closed the affected gate in a
separate **1/1** recheck; [both results and the source delta](development/2026-11-14-reference-refinement/reports/coherent-result.json)
remain retained. This was not a second complete 155-suite run. Test counts
change with configuration and new registered sources; discover the current set.

The local allocation/lifetime workload passes, while its complete local
sanitizer process still has the original LSan thread-attachment EPERM failure.
At `2e161dc`, the hosted
[core sanitizer job](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43641918154/job/132591142914)
and [sixteen-target native sanitizer job](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43641918142/job/132591142854)
completed successfully with their leak-enabled workflow steps. A37 independently
observed those job statuses; its [report](development/2026-11-14-reference-refinement/reports/A37-setup-handoff.json)
retains the metadata and limits. Preserve the local failure and inspect the
exact revision's full matrix before reporting broader hosted completion.

The same checkpoint's Windows core Release run retains **135/136**, with
`test_rotary_propagation_allocation` reporting a segmentation fault after
0.02 seconds in the [primary job log](development/2026-11-14-reference-refinement/reports/root-windows-2e.log).
A38 owns the bounded fixture-stack investigation; no product failure is
established by that symptom alone. Preserve this original result and qualify
any repair separately. The manifest and current status own its later outcome.

## Build a fresh checkout

The following POSIX commands run from the repository root. Use CMake 3.21+,
a C++20 compiler and Python 3.10+. A native SDL window also needs a C compiler,
Git and the platform desktop/audio development libraries listed in the
[platform setup](MIDI_UI_RUNBOOK.md#prerequisites-and-platform-backends).
Windows uses a configured Visual Studio developer terminal, `.exe` suffixes
and the selected `Release/` executable subdirectory. The build/test commands
retain `--config Release` / `-C Release` for multi-configuration generators.

### Core, offline tools and independent numerical tests

```sh
cmake -S . -B build-core -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_ENABLE_MIDI=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --build build-core --config Release --parallel 3
ctest --test-dir build-core -C Release --output-on-failure --no-tests=error
```

This configuration needs no SDL, RtMidi or VST3 SDK. CMake generates the nominal
profile and documentary tables. R2/R3 use the standard-library decimal oracle
and the two built native probes; CTest provides their exact executable paths.
Missing probes are errors. Preserve gradual underflow and avoid fast-math or
reassociation; the [numerical contract](ROTARY_NUMERICAL_CONTRACT.md) owns the
admission and error budgets. The [R2/R3 runbook](ROTARY_PROPAGATION.md#reproduce-the-native-and-python-gates)
also supplies focused builds and fresh report commands.

### Native window

Acquire the locked SDL source into a **new external directory**. If it already
exists, use `--verify-existing ../hammond-SDL2` instead of `--destination`.
The helper and CMake verify the dependency; configuration does not download it.

```sh
python3 tools/acquire_sdl2.py --destination ../hammond-SDL2
cmake -S . -B build-ui -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_SDL2_ROOT="$PWD/../hammond-SDL2" \
  -DHAMMOND_ENABLE_MIDI=OFF -DHAMMOND_BUILD_VST3=OFF
cmake --build build-ui --config Release --parallel 3
ctest --test-dir build-ui -C Release --output-on-failure --no-tests=error
build-ui/apps/standalone/hammond_standalone --help
build-ui/apps/standalone/hammond_standalone \
  --state "$HOME/hammond-controls.b3controls" --workspace play --width 1672 --height 941
```

The full build above creates every registered test input. For UI-only work,
`hammond_standalone_test_inputs` is the focused build aggregate, followed by
the required `^test_standalone_` CTest filter with `--no-tests=error`.
Building only the application is not a complete acceptance build.

The application initially requests the default audio output at 48 kHz and
512 frames. Select a device in Audio when needed. An existing valid state file
loads; an absent path starts the documented nominal audition registration.
Save is explicit, and exit does not save. F1/F2/F3 chooses Upper/Lower/Pedals;
F4/F5/F6 selects Play/Rotary/Service; F7 toggles Flat. The complete
[operating guide](INTERFACE_RUNBOOK.md) explains held-note ownership, presets,
modal release behavior, copied observations and Save/Load.

For physical MIDI, acquire locked RtMidi with
`python3 tools/acquire_rtmidi.py --destination ../hammond-rtmidi`, or verify
an existing clean checkout. Choose MIDI ON in the initial native configuration
by replacing its MIDI flag with `-DHAMMOND_ENABLE_MIDI=ON` and adding
`-DHAMMOND_RTMIDI_ROOT="$PWD/../hammond-rtmidi"`. Follow the
[RtMidi setup](RTMIDI_BUILD.md) for ALSA, WinMM or CoreMIDI prerequisites and
the recorded prepared-source correction. No input is selected automatically;
connect one exact port in MIDI. Backend compilation and synthetic replay do
not establish a working physical connection.

Optional VST3 uses a separate pinned SDK and CMake 3.25+; follow
[VST3_BUILD.md](VST3_BUILD.md) and its `check_vst3` aggregate. Its actual host
interfaces expose 47 controls. A custom plugin editor, DAW/device acceptance
and signed distribution remain separate from the standalone interface.

## Install and move a built payload

After the native full build above, choose a fresh writable staging prefix.
Leave `CMAKE_INSTALL_MODE` unset or `COPY`; installation does not build missing
inputs. These are the actual independent CMake component names:

```sh
hammond_stage="$HOME/hammond-refinement-stage"
cmake --install build-ui --config Release --component Standalone --prefix "$hammond_stage"
cmake --install build-ui --config Release --component OfflineTools --prefix "$hammond_stage"
cmake --install build-ui --config Release --component CaptureTools --prefix "$hammond_stage"
```

Keep the complete prefix together when moving it. Run the installed app at
`bin/hammond_standalone`; pass the moved compiled profile explicitly to the
offline renderer/traces. Capture scripts require Python 3.10+ and all their
copied modules. The [standalone](STANDALONE_INSTALL.md),
[offline](OFFLINE_INSTALL.md) and [capture](CAPTURE_TOOLS_INSTALL.md) guides
define exact inventories, refusal behavior and moved-prefix examples.
CaptureTools refuses an existing package leaf; it is not selected by another
component. These components do not install the rotary C++ headers as a public SDK.

[A35](development/2026-11-14-reference-refinement/reports/A35-install-relocation.json)
co-installed the MIDI-off configuration's 95 disjoint files, moved them through
Unicode/space paths and checked sixteen command outcomes. The actual render,
trace/plot, capture study/replay and bounded dummy application smoke passed;
missing installed resources refused without output. Its source/payload byte
identities predate A37's two guide corrections. That same-machine evidence
does not become a clean-OS or cross-platform binary distribution qualification.

## Resume this managed workspace

The retained working directory is
`/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ`. Inspect `git status --short`,
HEAD and the current remote before work. Local transient paths may disappear;
the committed handoff, source and reports are the resumption authority.

| Existing input | Exact location or configuration |
| --- | --- |
| CMake / CTest | `../build-tools/cmake/data/bin/cmake` and `../build-tools/cmake/data/bin/ctest`, version 4.4.5; use these actual executables, not the unconfigured Python entry-point wrapper |
| Ninja / compiler / Python | `../build-tools/bin/ninja`, `1.13.2.git.kitware.jobserver-pipe-1`; Debian GCC 14.2.0-19; Python 3.12.14 |
| SDL2 | `../SDL2`, release 2.32.10, commit `5d249570393f7a37e037abf22cd6012a4cc56a71` |
| RtMidi | `../rtmidi`, 6.0.0, commit `1e5b49925aa60065db52de44c366d446a902547b`; the [lock](../data/dependencies/rtmidi-lock.json) also fixes prepared-source bytes |
| `../build-native` | GCC Release, standalone ON, MIDI OFF, VST3 OFF; dummy native fixtures, effective X11/SDL ALSA OFF |
| `../build-desktop` | GCC Release, standalone and MIDI ON, VST3 OFF, X11 capable, SDL ALSA OFF; extracted development inputs under `../native-sysroot` |

Coordinate exclusive configure/build/CTest access to each shared tree. Reuse its
existing configuration instead of substituting another compiler or header set.
After ownership is granted, from the repository root:

```sh
../build-tools/cmake/data/bin/cmake --build ../build-native --config Release --parallel 3
../build-tools/cmake/data/bin/ctest --test-dir ../build-native -C Release \
  --output-on-failure --no-tests=error --parallel 3
```

For a desktop/gallery rebuild, the corresponding command is
`../build-tools/cmake/data/bin/cmake --build ../build-desktop --config Release --parallel 3 --target hammond_standalone`.
The [A31 report](development/2026-11-14-reference-refinement/reports/A31-native-gallery.json)
and gallery provenance retain actual build options, qualified source entries,
commands and pre/post executable identities. Do not copy its qualification
report onto later source or overwrite its gallery.

The shell and desktop share `/workspace` but have different display/process
namespaces. Root's real X11 journey launched through the desktop terminal and
used Sky; a shell without a display does not prove that native windows are
unavailable. [Retained desktop evidence](development/2026-11-14-reference-refinement/reports/root-desktop-acceptance-review.json)
proves held-pedal breakpoint resize, persistent mouse capture outside/inside/
outside, release and ordinary Alt+F4 cleanup for its identified executable.
Its keyboard chords show holds after view transitions without an independent
painted pre-held keyboard frame. The replay/model tests cover that separate
sequence. The later Flat-modal fix has its own
[A26 raster evidence](development/2026-11-14-reference-refinement/notes/A26-material-boundary-repair.md).
Dummy gallery pixels, genuine pending rendering-harness images and OS input
observations remain distinct evidence.

At the retained resource checkpoint, approximately 58 GB was free; the checkout
was about 120 MB and the two shared builds about 74/26 MB. Check disk use at wave
boundaries. Preserve compact logs, original failures, source hashes and lossless
selected images before removing only session-owned reproducible intermediates.
Do not duplicate dependency trees or remove another session's checkout/index.

## Where this sits in the whole plan

The atlas's ten research waves, [M0–M9 implementation plan](PLAN.md) and this
session's sixty actual assignments are separate organizations of work.

| Milestone | Current engineering boundary and concrete continuation |
| --- | --- |
| M0 — reference/contracts | Atlas, profiles, provenance and explicit unknowns are retained. Identify specimens, revisions, rights and acquisition inputs; software metadata cannot supply them. |
| M1 — testable core | Prepared core, event scheduling, offline tools and lifecycle tests exist. Preserve bounded processing and coherent source/test identities. |
| M2 — shared generator | 91 free-running nominal sources and reviewed routing exist. Acquire pickup waveforms, levels, phases and leakage before physical generator claims. |
| M3 — console | Manuals, pedals, four banks, fixed selections, Cancel, percussion and saved controls operate. Contact/loading/expression/percussion circuit calibration remains separate. |
| M4 — scanner | Documentary graph and numerical modules exist. Resolve the retained **G5 same-hertz failure** under the [frozen scanner contract](SCANNER_NUMERICAL_CONTRACT.md) before Engine integration. |
| M5 — AO-28 | Build and validate revision-specific connectivity, loading, operating points and dry outputs before fitting downstream effects. |
| M6 — Leslie electronics | Preserve separate 122/147 electrical identities and acquire amplifier, transformer, crossover and driver boundaries. |
| M7 — rotary acoustics | Native R2/R3 primitives now pass their named numerical workloads. Implement R4 waveform rendering next; R5 audible policy and R6 integration have separate gates. |
| M8 — calibration | Movable capture/corpus/comparison/study/replay tooling exists. Acquire immutable real captures and declared held-out groups; synthetic pass/fail examples are engineering fixtures. |
| M9 — product/release | Native workspaces, complete controls, Flat mode, copied inspection and VST3 adapter exist. Measured visual refinement, physical devices/DAWs, accessibility, callback deadlines, packaging rights and signing remain separate qualification. |

### Next numerical implementation: R4

Read [ROTARY_PROPAGATION.md](ROTARY_PROPAGATION.md), the immutable-view lifetime
rules and sections 4–6 of the [frozen numerical contract](ROTARY_NUMERICAL_CONTRACT.md).
Implement a separately owned renderer with independent horn/drum waveform and
streaming motion histories. Prepare storage and rollback resources outside
processing; the immutable 4,097-segment fixture view is not a growing event queue.
The waveform capacity is `ceil(Fs*rmax/c)+2+4`, bounded by 16,384 frames.

Write input sample `n`, observe at `n-2`, solve all four paths and read cubic
nodes `k-1,k,k+1,k+2` at the solved emission fraction. Negative audio is zero;
never invent future support. Apply the declared distance gain and signed
Horn-then-Drum sum. Validate buffers, finite inputs, aliasing, events and timeline
before mutation; late failure must preserve state, histories, diagnostics and
caller audio with zero events consumed. Reset, stopped rate changes, discarded
tails and zero-input flush need explicit behavior.

Qualify static-delay/interpolation cases and independent same-cubic parity at
every admitted rate, normalized error at most `2e-5`, bit-identical audio/state
across blocks 1/7/64/257/4096 and irregular partitions, nonzero-history rejection,
stereo/separate-input symmetry and all stopped rate pairs. R5 then defines its
audible reconstruction/filter/alias policy. R6 owns actual runtime and
Engine/host/device integration. Connecting the present R2/R3 diagnostic
primitives directly to dry Engine output would skip these required signal,
transaction, latency and effect-ownership contracts.

### Next interface and session closure

Use the exact reference and native v3 views for measured comparison. The wide
branch gives both full manuals 144.12-pixel key depth at 1672×941 and moves all
25 pedals beneath the disjoint cabinet. Functional completeness, real header
tools, status text and unconnected-model labels differ from the concept.
**Literal 1:1 visual equality remains unmet.** Material, lighting, bevel and
readability changes must preserve shared hit/paint geometry, Flat operation,
all 24 presets, 147 playing keys and owner release semantics.

Finish dependency-ready assignments under the actual manifest, retain concrete
review outcomes, qualify any changed product source, update README with accepted
native captures and execute the session's own strict accounting check once all
sixty actual results are accepted. The old session's checker cannot count this
one. Root owns shared status, next steps, log, manifest and publication.

For every later task, agree owned paths, preserve historical evidence, verify the
affected coherent source, update setup/status/next actions and publish completed
authorized work to main under [the standing owner rule](../AGENTS.md). Use a
fresh expected remote head and no force push. In this workspace, CLI Git writes
lacked credentials; root successfully published exact staged trees through the
connected GitHub Git-data tools, then independently fetched and checked the
remote parent/tree before advancing local main without resetting worker files.
Never claim publication from an API request alone or discard unfinished work.
