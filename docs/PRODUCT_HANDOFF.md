# Product continuation: setup and recovery handoff

**Audit snapshot: 15 November 2026, during wave 8.** The active session advances
native M9 MIDI channel modes, expression-controller calibration and measured
visual refinement, plus an independent M6 passive crossover. Its latest retained
publication is **`d556da017ea0a5d4f2d231416782dbc5066e58c2`**, tree
`a3150fd2489a50a430b02c01eadd5e0c180bc7f9`, parent
`b9d352a82ac1afdec70c76ec5b1987785a37762e`; the
[publication receipt](development/2026-11-15-product-continuation/reports/portability-guides-publication.json)
records the verified update. Accepted gallery files and later fixture/install
work were still being integrated at this audit. This is a dated recovery record,
not a claim that every working file is published or that the session is complete.

## Recover the actual state first

Read the whole [AGENTS.md](../AGENTS.md), [M0–M9 plan](PLAN.md),
[README](../README.md), [status](STATUS.md), [next steps](NEXT_STEPS.md), latest
[development log](DEVELOPMENT_LOG.md) entry and the active session's
[entry](development/2026-11-15-product-continuation/README.md),
[checkpoint](development/2026-11-15-product-continuation/CHECKPOINT.md) and
[actual assignments](development/2026-11-15-product-continuation/assignments.json).
Then inspect current source, index and evidence. The checkpoint owns subsequent
observations; dated snapshots do not override later source or accepted outcomes.

The requested **60 actual workers in ten waves** belong only to this product
session. Planned IDs, follow-ups and completed historical workers do not count.
The integrator updates dispatch/acceptance and owns shared documentation,
publication and the primary build. Workers use only their assigned paths. The
separate [waveform session](development/2026-11-14-waveform-continuation/README.md)
and its [checkpoint](development/2026-11-14-waveform-continuation/CHECKPOINT.md)
retain R4 ownership and unfinished work in another checkout.

The session's A01–A06 notes retain complete textual coverage of all 500 atlas
pages; use the [reading map](PROJECT_GUIDE.md#source-and-reading-records).
Readings and context recovery do not supply missing physical measurements.
The original PDF remains **21,248,265 bytes**, SHA-256
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
Do not duplicate or rewrite it.

## Where the product is

| Area | Implemented behavior and retained boundary |
| --- | --- |
| Native MIDI and expression | Scoped CC120, expression reset CC121 and retained CC123 semantics; immutable per-epoch CC11 endpoint/inversion calibration; native CLI and eleven-stop modal with distinct selected/configured/active/pending state. See the [operating guide](MIDI_EXPRESSION_GUIDE.md) and [channel-mode contract](MIDI_CHANNEL_MODE_CONTRACT.md). Calibration remains volatile adapter configuration. |
| Native interface | Wide Dimensional footage/caps, edited versus sounding registrations and key materials are refined. The admitted [product gallery](../examples/demos/standalone-product-preview-v1/README.md) contains eight normal and three separate MIDI-overlay frames at `d556da01`; README has been promoted to these captures. The [independent admission](reviews/PRODUCT_GALLERY_ADMISSION.md) retains source, replay, state and pixel checks. |
| Musical compatibility | **47 sound parameters**, **`B3CONTROLS4` and readers 1–3**, **91 shared free-running sources**, note ownership and the nominal dry Engine remain unchanged. Interface inventory remains 61 Upper + 61 Lower + 25 pedals, 24 presets and 68 ordinary controls including those presets. See the [compatibility review](PRODUCT_COMPATIBILITY.md). |
| Independent M6 foundation | Four-state ideal passive crossover, fixed documentary registry, independent analog references, native probe and numerical/lifecycle/allocation evidence. [CrossoverTools](CROSSOVER_INSTALL.md) is a separate six-file component. Ideal 16-ohm loads and documentary component values do not supply physical driver/source/loss data; no crossover route enters Engine. |
| Other model and product gates | Scanner G5's same-Hz failure remains open. The waveform owner retains R4 acceptance; R5 audible policy and R6 runtime/Engine integration remain separate. Complete AO-28/Leslie graphs, acquisition, real-device/DAW/display journeys, semantic accessibility, callback deadlines, rights and signed release require their own evidence. |

Literal whole-interface **1:1 equality remains unproved**. The
[reference-gap review](design/PRODUCT_REFERENCE_GAPS.md) distinguishes actual
native controls from concept art and identifies remaining material/small-text
differences. Dummy SDL captures are not physical display or controller acceptance.

## What the retained checks establish

| Exact source or observation | Result and scope |
| --- | --- |
| Main feature `ff41d412` | [Coherent GCC 14.2 Release build](development/2026-11-15-product-continuation/reports/wave4-coherent-build.json) and [176/176 CTest result](development/2026-11-15-product-continuation/reports/wave4-full-ctest.txt) passed in 177.92 s. Standalone ON, native MIDI backend OFF, VST3 OFF. Its [13 successful hosted statuses](development/2026-11-15-product-continuation/reports/implementation-hosted-status.json) remain source-specific; later fixture/install changes do not inherit that full-suite result. |
| Gallery at `d556da01` | A41 admits all eleven actual native frames. The [108 production inputs and executable receipt](development/2026-11-15-product-continuation/reports/capture-qualified-build.json) still match at this audit. That receipt records an earlier `b9d352a8` target build, and its standalone build-rule hash predates later test-probe changes; it is not a complete later build attestation. |
| Expanded native sanitizers at `d556da01` | The [original hosted failure](development/2026-11-15-product-continuation/reports/d556-native-sanitizer-build-failure.json) occurred while GCC 13 built the test-only RtMidi facade with instrumentation and warnings as errors. The 21 selected gates did **not execute**. The [clear/push-back repair](development/2026-11-15-product-continuation/reports/gcc13-facade-repair.json) keeps the same API value and all policies; ordinary local native calibration passed in 20.50 s. A repaired-source hosted sanitizer run is still required. |
| A42 expanded modal raster fixture | The [first failure and diagnosis](development/2026-11-15-product-continuation/notes/A42-calibration-modal-raster.md) remain retained. Root's final literal-plate oracle passed **1,293/1,293 assertions, 109 paint frames, in 6.63 s**: all 212 differing pixels are explained exactly by 38 boundary-crossing glyphs, with zero unexplained differences. The [receipt](development/2026-11-15-product-continuation/reports/A42-calibration-modal-raster.json) binds all attempts and inputs. Production painter/application are unchanged. |
| A43 installed guide | [Six private checks](development/2026-11-15-product-continuation/notes/A43-installed-workflows.md) passed in 4.379 s. Root then reconfigured and passed the [complete installed gate](development/2026-11-15-product-continuation/reports/A43-root-installed-ctest.txt): **eight methods / one CTest in 5.31 s**. The inventory is 16 files MIDI-OFF / 20 MIDI-ON. Source-independent guide/calibration behavior and namespace preservation are qualified in the recorded MIDI-OFF configuration; local MIDI-ON/platform execution is separate. |
| Local leak-enabled sanitizers | The [fixture and empty-main control](development/2026-11-15-product-continuation/notes/A25-crossover-allocation.md) were blocked by ptrace. They are not local passes. Preserve hosted evidence separately and retain only the existing named core quarantine exception; no new global leak exception is authorized. |

The [final `d556da01` status receipt](development/2026-11-15-product-continuation/reports/d556-hosted-status.json)
records **12 successful jobs and one failed native sanitizer build**. Core
Linux Release/sanitizers, Windows and macOS, the full R4 waveform job, all three
VST3 jobs and four native Release configurations report success. The expanded
native sanitizer gates did not execute. Source-specific primary-log review
remains separate; this is not a fully green matrix or qualification of later
working changes. Read the checkpoint and subsequent primary receipts before
making a later claim.

The gallery's original eleven BMP intermediates are unavailable. Retained PNGs
match the recorded decoded native-pixel hashes; the independent admission states
that precise boundary. Do not recreate BMP files and label them originals.
Original failures, historical galleries and named-source reports remain intact.

## Clean checkout with a normal toolchain

These commands are for a fresh developer checkout. Use a C++20 compiler, a C
compiler for SDL, **CMake/CTest 3.21+**, **Python 3.10+**, Git and a supported build
tool. Linux needs the desktop/audio development packages and ALSA prerequisites
listed in the [native setup guide](MIDI_EXPRESSION_GUIDE.md#build-the-native-application)
and [platform package recipe](MIDI_UI_RUNBOOK.md#prerequisites-and-platform-backends).
macOS requires its Apple SDK; Windows instructions and multi-configuration paths
are in the same guide. Optional VST3 uses its separate [SDK recipe](VST3_BUILD.md)
and CMake 3.25+.

On a machine with network access, clone into a new destination:

```sh
git clone https://github.com/tomasedisonn80/Hammond-B3-Organ.git
cd Hammond-B3-Organ
git status --short
git rev-parse HEAD 'HEAD^{tree}'
```

From that repository root, acquire the locked sources into new sibling
directories whose parent exists, then configure a native build:

```sh
python3 tools/acquire_sdl2.py --destination ../SDL2
python3 tools/acquire_rtmidi.py --destination ../rtmidi-6.0.0
cmake -S . -B ../build-product-native -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=ON \
  -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_ENABLE_MIDI=ON \
  -DHAMMOND_SDL2_ROOT="$PWD/../SDL2" \
  -DHAMMOND_RTMIDI_ROOT="$PWD/../rtmidi-6.0.0"
cmake --build ../build-product-native --config Release --parallel 3 \
  --target hammond_standalone hammond_standalone_test_inputs
ctest --test-dir ../build-product-native -C Release --output-on-failure \
  --no-tests=error -R '^test_standalone_'
../build-product-native/apps/standalone/hammond_standalone --help
../build-product-native/apps/standalone/hammond_standalone
```

For already acquired dependencies, use `--verify-existing` instead of
`--destination`. The locks pin **SDL 2.32.10** at
`5d249570393f7a37e037abf22cd6012a4cc56a71` and **RtMidi 6.0.0** at
`1e5b49925aa60065db52de44c366d446a902547b`; ordinary CMake configuration verifies
sources offline. The RtMidi correction is applied only to its prepared build
copy. Keep the original dependency checkouts clean. Keyboard/pointer-only builds
use `-DHAMMOND_ENABLE_MIDI=OFF` and omit RtMidi acquisition/root; SDL remains
required. Do not assume such a build can open a physical MIDI port.

No physical MIDI input is selected automatically. Use `--list-midi`, then select
one exact port name and three distinct wire channels through MIDI / Ctrl+M or
the documented CLI. Audio / Ctrl+, selects audio settings. Save/Load persists
musical controls; endpoint/direction calibration stays outside musical state.
The [operating guide](MIDI_EXPRESSION_GUIDE.md) explains reconnect, fault and
pending/active behavior. The [Standalone install guide](STANDALONE_INSTALL.md)
owns the installed workflow and exact payload for the chosen revision.

For core/offline work without external dependencies, choose the existing default
build instead, from the repository root:

```sh
cmake --preset debug
cmake --build --preset debug --parallel 2
ctest --preset debug
```

Those are reproducible setup instructions, not newly executed results in A45.
Record the actual source, selected configuration and discovered tests when run.

## This workspace's recovery setup

Only `/workspace/scratch/5b7d983ac078/Hammond-B3-Organ` is writable by this session.
The integrator exclusively coordinates configure/build/CTest/capture use of
`/workspace/scratch/5b7d983ac078/build-native`. Do not operate that tree while
another owner has frozen it for capture or qualification. Other workers may
inspect source/cache/hashes without configuring, building or launching tests.

| Observed tool or input | Recovery identity |
| --- | --- |
| CMake and CTest | `/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/cmake` and adjacent `ctest`, both **4.4.5**. No system `cmake` was on PATH at this audit. |
| Ninja | `/workspace/scratch/1bb6ee17ad7e/build-tools/bin/ninja`, **1.13.2.git.kitware.jobserver-pipe-1**. |
| C/C++ | `/usr/bin/cc`, `/usr/bin/c++`, **GCC 14.2.0**. |
| Python selected by CMake | `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12`, **3.12.14**. |
| SDL and RtMidi | `/workspace/scratch/1bb6ee17ad7e/SDL2` and `/workspace/scratch/1bb6ee17ad7e/rtmidi`; both lock verifiers passed offline during this audit. These and the shared toolchain are read-only borrowed inputs. |
| Existing configuration | Ninja, Release, BUILD_TESTING ON, standalone ON, native MIDI backend OFF, VST3 OFF, sanitizers OFF, static SDL; X11, Wayland and ALSA OFF. Native qualification uses explicit dummy drivers. |
| Captured native application | `/workspace/scratch/5b7d983ac078/build-native/apps/standalone/hammond_standalone`; SHA-256 `7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`. A45 rechecked this and all 108 receipt-bound production inputs without executing the application. |

Start with read-only recovery in a POSIX shell:

```sh
b3_repo=/workspace/scratch/5b7d983ac078/Hammond-B3-Organ
b3_build=/workspace/scratch/5b7d983ac078/build-native
b3_cmake=/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/cmake
b3_ctest=/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/ctest
b3_ninja=/workspace/scratch/1bb6ee17ad7e/build-tools/bin/ninja
b3_sdl=/workspace/scratch/1bb6ee17ad7e/SDL2
b3_rtmidi=/workspace/scratch/1bb6ee17ad7e/rtmidi
cd "$b3_repo"
git status --short
git diff --stat
git diff --cached --stat
git rev-parse HEAD 'HEAD^{tree}' origin/main
python3 -B tools/acquire_sdl2.py --verify-existing "$b3_sdl"
python3 -B tools/acquire_rtmidi.py --verify-existing "$b3_rtmidi"
df -h /workspace/scratch/5b7d983ac078
du -sh "$b3_repo" "$b3_build"
```

`origin/main` above is the locally fetched reference. The integrator fetches and
inspects the actual remote before publication, preserving concurrent files.
If a context reset loses shell variables, rerun this block before the next one.

After the integrator has released any source/build freeze and confirmed the
relevant owners' delivered inputs, recover the existing dummy-SDL configuration:

```sh
"$b3_cmake" -S "$b3_repo" -B "$b3_build" -G Ninja \
  -DCMAKE_MAKE_PROGRAM="$b3_ninja" -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/usr/bin/cc -DCMAKE_CXX_COMPILER=/usr/bin/c++ \
  -DPython3_EXECUTABLE=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12 \
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=ON \
  -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_ENABLE_MIDI=OFF \
  -DHAMMOND_ENABLE_SANITIZERS=OFF -DHAMMOND_SDL2_ROOT="$b3_sdl" \
  -DSDL_X11=OFF -DSDL_WAYLAND=OFF -DSDL_ALSA=OFF
"$b3_cmake" --build "$b3_build" --config Release --parallel 3 \
  --target hammond_standalone_test_inputs
"$b3_ctest" --test-dir "$b3_build" -C Release --output-on-failure \
  --no-tests=error -R '^test_standalone_install$'
```

This block reproduces A43's already completed installed gate if a later input
change requires it; the retained result above is 1/1 in 5.31 s. CTest supplies
the fixture's required environment. The additional named gates
`test_standalone_native_calibration` and `test_standalone_material_acceptance`
cover the facade repair and A42's final oracle respectively; their retained
results are 20.50 s and 6.63 s. Preserve those observations instead of repeating
them just to write a handoff. A later full coherent gate requires building all
selected targets first; a standalone-only aggregate does not prepare every
core/offline executable. Never infer a test count from history.

## Resource ownership and bounded continuation

The read-only `du`/`df` audit observed approximately **309 MiB** in this session's
workspace: **177 MiB** for the repository, **92 MiB** for the primary build and
about **40 MiB** of existing extracts, previews and private fixture/evidence
directories. About **57 GiB remained available**. These are rounded observations
at the audit time; concurrent work can change them. **No cleanup was needed or
performed.** A45 created only this handoff, its short note and AGENTS changes.

| Protected resource | Ownership and rule |
| --- | --- |
| `/workspace/scratch/5b7d983ac078/build-native` | Product integrator's single primary build, approximately 92 MiB. Reuse it with exclusive coordination; preserve its configuration and evidence before any later owner-approved reproducible cleanup. |
| `/workspace/scratch/1bb6ee17ad7e` | Another session's workspace, approximately 862 MiB total. Borrow only the verified tools, SDL (about 79 MiB) and RtMidi (about 2.2 MiB) read-only. Its checkout, builds and evidence are not cleanup candidates for this session. |
| `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ` | Separate R4 checkout, approximately 189 MiB, with its own index and unfinished work. Preserve it and its sibling build; integrate published compatible changes through Git. |
| Atlas, admitted captures and compact reports | Preserve their original identities and source-specific failures. Keep the single original PDF; use existing bounded extracts and selected lossless PNGs. Do not duplicate whole galleries, source trees or dependency trees for every worker. |

Checkpoint each wave and before a long run, context change or cleanup. Keep one
current summary with the actual source, owners, accepted/unfinished work,
verification limits and next command; retain superseded observations under dated
headings. A compact note/report is sufficient for a worker; long raw outputs
belong only where required to reproduce or assess the observation. If space ever
becomes constrained, inspect exact paths and ownership first, retain needed
original evidence and list bounded reproducible candidates before removal.
There is no authority to delete another session's files or blanket-clean scratch.

## What to do next

1. **Publish and qualify the repaired source.** Preserve A40/A41's admitted
   eleven frames and their README promotion, A42's final exact literal-plate
   oracle and A43's full installed-guide pass. Integrate those accepted inputs
   with the facade repair in a coherent checkpoint. Preserve the failed GCC 13
   build, then observe a repaired-source hosted build and execution of all 21
   selected native sanitizer gates with unchanged leak/warning policies. This
   is the immediate qualification gap; ordinary GCC 14 Release cannot close it.
2. **Finish actual waves 8–10.** Complete provenance/resource/recovery,
   fault-lifecycle and numerical-boundary reviews; implement and independently
   accept the product session's own strict actual-60-record validator. A46 is
   the named next checker task at this audit; no command or file is assumed
   before delivery. Then audit exact-source hosted platform/VST3 logs, current
   documentation and final product/next-phase evidence. Keep every worker real.
3. **Publish coherent accepted checkpoints.** Root owns shared status, next
   steps, log and the actual manifest. Review the diff, build the required
   inputs and run necessary affected/coherent gates. Fetch/inspect concurrent
   main, use a fresh expected head with no force, then fetch and verify exact
   commit/tree/parent. This session's prior publication used connected Git Data
   because shell push lacked credentials; preserve the same exact-tree checks
   if that route is still required. Never reset unfinished files to synchronize
   a local branch. Observe required hosted results before claiming them.
4. **Close only the actual requested session.** After all sixty distinct workers
   and ten waves are accepted, run its accepted strict checker against exact
   retained records, keep the result and verify final publication. A historical
   checker or partial mode cannot close this session. Update this handoff and
   the current navigation to the observed closing source and remaining limits.
5. **Continue the next dependency-ready project phase.** The independent M6
   next task is to freeze a versioned same-Hz electrical-accuracy protocol,
   then evaluate a separately identified numerical candidate using the
   [fixed v1 contract](LESLIE_CROSSOVER_CONTRACT.md),
   [characterization](LESLIE_CROSSOVER_CHARACTERIZATION.md) and
   [developer guide](CROSSOVER_DEVELOPER_GUIDE.md#5-continue-m6-through-explicit-gates).
   Declare band, loads, signal boundaries, hold/reconstruction, magnitude/phase
   criteria above a gain floor, complex-error criteria below it and admittance
   criteria before comparing methods. Preserve v1 values/results and test
   processed/transient output, state/rate/partition/rollback and bounded costs.
   Physical loads/losses, coupled M6, dry-organ validation and live integration
   retain their separate prerequisites in the [complete next steps](NEXT_STEPS.md).

Every future agent follows the standing authorized workflow in AGENTS: recover
the full plan and current source, continue useful dependency-ready work, retain
actual evidence, update setup/status/next steps/log/notes and actual README UI
captures, then commit and publish accepted work with exact verification. A later
user instruction or repository protection may change that workflow; this handoff
adds no new permission requirement and claims no authority over unrelated work.
