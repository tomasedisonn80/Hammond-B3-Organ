# Product continuation: setup and recovery handoff

**A59 recovery audit: 15 November 2026, during wave 10.** The active session advances
native M9 MIDI channel modes, expression-controller calibration and measured
visual refinement, plus an independent M6 passive crossover. The observed
published source is **`d8c39f7986746eacc991747153c7dbb012bb9a32`**, tree
`edf67b978f93e8dbea6537ce92d3928c171bc1f3`, parent
`d556da017ea0a5d4f2d231416782dbc5066e58c2`. The
[publication receipt](development/2026-11-15-product-continuation/reports/gallery-publication.json)
retains the verified non-force update; A59's read-only live main query agrees.
All thirteen hosted jobs qualify **d8**. The later **180/180 local result**
qualifies **d8 plus accepted A46/A48 checker/admission changes**. Those later
working files, final strict actual-sixty closure and final publication remain
pending at this audit. They do not inherit d8's hosted qualification.

The [recovery acceptance](reviews/PRODUCT_RECOVERY_ACCEPTANCE.md) and
[bounded receipt](development/2026-11-15-product-continuation/reports/A59-recovery-audit.json)
record exact observations and checks. This is a dated snapshot; the live
checkpoint owns subsequent publication, worker counts and observed outcomes.

## Recover the actual state first

Read the whole [AGENTS.md](../AGENTS.md), [M0–M9 plan](PLAN.md),
[README](../README.md), [status](STATUS.md), [next steps](NEXT_STEPS.md), latest
[development log](DEVELOPMENT_LOG.md) entry and the active session's
[entry](development/2026-11-15-product-continuation/README.md),
[checkpoint](development/2026-11-15-product-continuation/CHECKPOINT.md) and
[actual assignments](development/2026-11-15-product-continuation/assignments.json).
Then inspect current source, index and evidence. The checkpoint owns subsequent
observations; dated snapshots do not override later source or accepted outcomes.

Recover **three distinct inputs**: published commit/tree and hosted receipts;
the frozen code/test/build/data set in the later local receipt; and accepted or
unfinished working files identified by the actual manifest. A59 observed an
unstaged working overlay with an empty staged diff. Do not reset, checkout over,
clean, or bulk-stage those files to make the checkout match a dated source.
Inspect each owner's delivery and let the integrator select accepted paths.
A clean clone of d8 cannot recover unpublished A46/A48 files or later notes.
If the workspace disappears before publication, retrieve surviving originals or
the integrator's later verified publication; hashes alone cannot reconstruct
missing bytes. Record unrecovered work explicitly instead of claiming that a
fresh d8 clone reproduces the later 180-test input set.

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

### Validate this session's actual records

The accepted [A46 checker](development/2026-11-15-product-continuation/notes/A46-session-validator.md)
is present in this working checkout. From its repository root, while actual
acceptance is still in progress:

```sh
python3 -B tools/check_product_session.py --repo . --allow-incomplete --json
```

This checks declared record consistency and explicitly declines closure. It
does not attest dispatch, substantive implementation/review, product readiness
or fidelity. Only after **A01–A60** are actually accepted in their ten six-worker
waves does the integrator run and retain the strict result:

```sh
python3 -B tools/check_product_session.py --repo . --json
```

The integrator then switches the product CI record step from progress to strict,
publishes the accepted source and observes that exact source's hosted result.
A59 inspects these commands and retained evidence without running either gate.
Historical checkers and earlier partial snapshots cannot close this session.
Until the later files are published, a clean d8 checkout lacks this checker;
that is a publication boundary, not a reason to substitute an older script.

## Where the product is

| Area | Implemented behavior and retained boundary |
| --- | --- |
| Native MIDI and expression | Scoped CC120, expression reset CC121 and retained CC123 semantics; immutable per-epoch CC11 endpoint/inversion calibration; native CLI and eleven-stop modal with distinct selected/configured/active/pending state. See the [operating guide](MIDI_EXPRESSION_GUIDE.md) and [channel-mode contract](MIDI_CHANNEL_MODE_CONTRACT.md). Calibration remains volatile adapter configuration. |
| Native interface | Wide Dimensional footage/caps, edited versus sounding registrations and key materials are refined. The admitted [product gallery](../examples/demos/standalone-product-preview-v1/README.md) contains eight normal and three separate MIDI-overlay frames at `d556da01`; README has been promoted to these captures. The [independent admission](reviews/PRODUCT_GALLERY_ADMISSION.md) retains source, replay, state and pixel checks. |
| Musical compatibility | **47 sound parameters**, **`B3CONTROLS4` and readers 1–3**, **91 shared free-running sources**, note ownership and the nominal dry Engine remain unchanged. Interface inventory remains 61 Upper + 61 Lower + 25 pedals, 24 presets and 68 ordinary controls including those presets. See the [compatibility review](PRODUCT_COMPATIBILITY.md). |
| Independent M6 foundation | Four-state ideal passive crossover, fixed documentary registry, independent analog references, native probe and numerical/lifecycle/allocation evidence. [CrossoverTools](CROSSOVER_INSTALL.md) is a separate six-file component. Ideal 16-ohm loads and documentary component values do not supply physical driver/source/loss data; no crossover route enters Engine. |
| Other model and product gates | Scanner G5's same-Hz failure remains open. The waveform owner retains R4 acceptance; R5 audible policy and R6 runtime/Engine integration remain separate. Complete AO-28/Leslie graphs, acquisition, real-device/DAW/display journeys, semantic accessibility, callback deadlines, rights and signed release require their own evidence. |

The user's literal whole-interface **1:1 objective remains unmet and unwaived**.
The [A54 UI acceptance](reviews/PRODUCT_UI_ACCEPTANCE.md) and
[reference-gap review](design/PRODUCT_REFERENCE_GAPS.md) distinguish actual
native controls from concept art and identify remaining material/small-text
differences, rack offsets and native-display/performance gaps. Scoped raster
acceptance is complete for its named inputs; it does not close the user's full
objective. Dummy SDL captures are not physical display or controller acceptance.

## What the retained checks establish

| Exact source or observation | Result and scope |
| --- | --- |
| Published `d8c39f7` | [All thirteen hosted jobs succeeded](development/2026-11-15-product-continuation/reports/d8-hosted-status.json). Independent primary [Linux](reviews/PRODUCT_LINUX_HOSTED_REVIEW.md), [Windows](reviews/PRODUCT_WINDOWS_HOSTED_REVIEW.md), [macOS](reviews/PRODUCT_MACOS_HOSTED_REVIEW.md) and [VST3](reviews/PRODUCT_VST3_HOSTED_REVIEW.md) audits qualify that source. The expanded native sanitizer selection actually passed **21/21 in 342.06 s**; native material evidence is **1,293 assertions / 109 frames**, and installed inventories are **16 files MIDI-OFF / 20 MIDI-ON**. No physical device, deadline, DAW or literal 1:1 result follows. |
| Later local d8 + A46/A48 | Root's [coherent receipt](development/2026-11-15-product-continuation/reports/wave8-coherent-build.json) and [original full log](development/2026-11-15-product-continuation/reports/wave8-full-ctest.txt) retain **180/180 in 507.55 s** after reconfigure and an all-target build. All **366 frozen code/test/build/data inputs**, three recorded binaries and the cache still match during A59. This is hash applicability, not repeated execution. The added Python checker/admission sources need final publication and their own required hosted results. |
| Accepted checker/admission repairs | A46 retains **19 passing focused methods**; A48 retains **11** in the [numerical admission review](reviews/PRODUCT_NUMERICAL_ADMISSION_REVIEW.md). The latter rejects incomplete/contradictory replacement reports. Original numerical source, probe, report and thresholds remain unchanged; the [plot refresh](development/2026-11-15-product-continuation/reports/crossover-plot-admission-refresh.json) changes only generator-hash metadata with identical decoded pixels. The grid is **126 in-band / 130 total points per group**. |
| Main feature `ff41d412` | [Coherent GCC 14.2 Release build](development/2026-11-15-product-continuation/reports/wave4-coherent-build.json) and [176/176 CTest result](development/2026-11-15-product-continuation/reports/wave4-full-ctest.txt) passed in 177.92 s. Standalone ON, native MIDI backend OFF, VST3 OFF. Its [13 successful hosted statuses](development/2026-11-15-product-continuation/reports/implementation-hosted-status.json) remain source-specific; later fixture/install changes do not inherit that full-suite result. |
| Gallery at `d556da01` | A41 admits all eleven actual native frames. The [108 production inputs and executable receipt](development/2026-11-15-product-continuation/reports/capture-qualified-build.json) still match at this audit. That receipt records an earlier `b9d352a8` target build, and its standalone build-rule hash predates later test-probe changes; it is not a complete later build attestation. |
| Expanded native sanitizers at `d556da01` | The [original hosted failure](development/2026-11-15-product-continuation/reports/d556-native-sanitizer-build-failure.json) occurred while GCC 13 built the test-only RtMidi facade with instrumentation and warnings as errors. The 21 selected gates did **not execute**. The [clear/push-back repair](development/2026-11-15-product-continuation/reports/gcc13-facade-repair.json) keeps the same API value and all policies; ordinary local native calibration passed in 20.50 s. A45 recorded replacement hosted execution as pending; d8's later **21/21** closes that specific build/selection gap without rewriting d556. |
| A42 expanded modal raster fixture | The [first failure and diagnosis](development/2026-11-15-product-continuation/notes/A42-calibration-modal-raster.md) remain retained. Root's final literal-plate oracle passed **1,293/1,293 assertions, 109 paint frames, in 6.63 s**: all 212 differing pixels are explained exactly by 38 boundary-crossing glyphs, with zero unexplained differences. The [receipt](development/2026-11-15-product-continuation/reports/A42-calibration-modal-raster.json) binds all attempts and inputs. Production painter/application are unchanged. |
| A43 installed guide | [Six private checks](development/2026-11-15-product-continuation/notes/A43-installed-workflows.md) passed in 4.379 s. Root then reconfigured and passed the [complete installed gate](development/2026-11-15-product-continuation/reports/A43-root-installed-ctest.txt): **eight methods / one CTest in 5.31 s**. The inventory is 16 files MIDI-OFF / 20 MIDI-ON. Source-independent guide/calibration behavior and namespace preservation are qualified in the recorded MIDI-OFF configuration; local MIDI-ON/platform execution is separate. |
| Local leak-enabled sanitizers | The [fixture and empty-main control](development/2026-11-15-product-continuation/notes/A25-crossover-allocation.md) were blocked by ptrace. They are not local passes. Preserve hosted evidence separately and retain only the existing named core quarantine exception; no new global leak exception is authorized. |

### Historical A45 snapshot and original failures

A45's wave-8 recovery source was `d556da017ea0a5d4f2d231416782dbc5066e58c2`,
tree `a3150fd2489a50a430b02c01eadd5e0c180bc7f9`, parent
`b9d352a82ac1afdec70c76ec5b1987785a37762e`, retained in its
[publication receipt](development/2026-11-15-product-continuation/reports/portability-guides-publication.json).
Gallery and later fixture/install integration, A46 delivery and repaired hosted
sanitizers were then pending. Those historical pending states remain in
[A45's note](development/2026-11-15-product-continuation/notes/A45-recovery-resources.md);
the later rows above describe their observed outcomes.

The [final `d556da01` status receipt](development/2026-11-15-product-continuation/reports/d556-hosted-status.json)
records **12 successful jobs and one failed native sanitizer build**. Core
Linux Release/sanitizers, Windows and macOS, the full R4 waveform job, all three
VST3 jobs and four native Release configurations report success. The expanded
native sanitizer gates did not execute at d556. Later primary-log reviews
qualify d8, not a retrospective all-green d556 matrix. Earlier b9 installation
and Windows calibration failures, their CMake-policy/environment-string/newline
repairs, original thresholds and timings remain in
[STATUS](STATUS.md#earlier-product-checkpoints-and-retained-failures). Preserve
the local ptrace-blocked sanitizer/control evidence and the existing named core
quarantine-only leak exception; no general exception is introduced.

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

For a Linux/macOS single-configuration build, acquire the locked sources from
that repository root into new sibling directories whose parent exists, then
configure a native build. These are ordinary desktop/backend settings, without
this workspace's dummy-SDL restrictions. Use the linked native guide for
Windows/PowerShell and multi-configuration executable paths.

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

Those are reproducible setup instructions, not newly executed results in A45
or A59. A59 checked command syntax and actual CMake/preset/target definitions.
Record the actual source, selected configuration and discovered tests when run.

## This workspace's recovery setup

This session's source checkout is
`/workspace/scratch/5b7d983ac078/Hammond-B3-Organ`; workers edit only assigned paths.
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
| Captured native application | `/workspace/scratch/5b7d983ac078/build-native/apps/standalone/hammond_standalone`; SHA-256 `7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`. A45 and A59 independently rechecked this and all 108 receipt-bound production inputs without executing the application. |
| Later coherent build identity | A59 also rechecked all 366 local-receipt inputs and three binary hashes. Current `CMakeCache.txt` SHA-256 `94735cbc53d80045da267e2d1451b92fc2e2a11bb53838f3b1dab2a3b50b2a35` matches that receipt. A later reconfigure may legitimately change the cache; it needs its own recorded scope. |

Start with read-only recovery in a POSIX shell:

```sh
b3_repo=/workspace/scratch/5b7d983ac078/Hammond-B3-Organ
b3_build=/workspace/scratch/5b7d983ac078/build-native
b3_cmake=/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/cmake
b3_ctest=/workspace/scratch/1bb6ee17ad7e/build-tools/cmake/data/bin/ctest
b3_ninja=/workspace/scratch/1bb6ee17ad7e/build-tools/bin/ninja
b3_python=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12
b3_sdl=/workspace/scratch/1bb6ee17ad7e/SDL2
b3_rtmidi=/workspace/scratch/1bb6ee17ad7e/rtmidi
cd "$b3_repo"
GIT_OPTIONAL_LOCKS=0 git status --short
git diff --stat
git diff --cached --stat
git rev-parse HEAD 'HEAD^{tree}' origin/main
git ls-remote origin refs/heads/main
"$b3_python" -B tools/acquire_sdl2.py --verify-existing "$b3_sdl"
"$b3_python" -B tools/acquire_rtmidi.py --verify-existing "$b3_rtmidi"
df -h /workspace/scratch/5b7d983ac078
du -sh "$b3_repo" "$b3_build"
```

`origin/main` above is the locally fetched reference; `ls-remote` is a new
read-only query and must retain any failure honestly. The integrator fetches
and inspects the actual remote before publication, preserving concurrent files.
If a context reset loses shell variables, rerun this block before the next one.

After the integrator has released any source/build freeze and confirmed the
relevant owners' delivered inputs, recover the existing dummy-SDL configuration:

```sh
"$b3_cmake" -S "$b3_repo" -B "$b3_build" -G Ninja \
  -DCMAKE_MAKE_PROGRAM="$b3_ninja" -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/usr/bin/cc -DCMAKE_CXX_COMPILER=/usr/bin/c++ \
  -DPython3_EXECUTABLE="$b3_python" \
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=ON \
  -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_ENABLE_MIDI=OFF \
  -DHAMMOND_ENABLE_SANITIZERS=OFF -DHAMMOND_SDL2_ROOT="$b3_sdl" \
  -DSDL_X11=OFF -DSDL_WAYLAND=OFF -DSDL_ALSA=OFF
"$b3_cmake" --build "$b3_build" --config Release --parallel 3 \
  --target hammond_standalone_test_inputs
"$b3_ctest" --test-dir "$b3_build" -C Release --output-on-failure \
  --no-tests=error -R '^test_standalone_install$'
```

This optional block reproduces A43's already completed installed gate if a
later input change requires it; the retained result above is 1/1 in 5.31 s.
CTest supplies the fixture's required environment. The additional named gates
`test_standalone_native_calibration` and `test_standalone_material_acceptance`
cover the facade repair and A42's final oracle respectively; their retained
results are 20.50 s and 6.63 s. Preserve those observations instead of repeating
them just to write a handoff. A later full coherent gate requires building all
selected targets first; a standalone-only aggregate does not prepare every
core/offline executable. Never infer a test count from history.
The later full **180/180** receipt already records an all-target build and all
registered tests. Current documentation and final ledger changes call for
affected integrity checks; they do not justify repeating that full run while
its code inputs still match. Neither A59 nor this recipe launches a physical
MIDI backend from the current MIDI-OFF/dummy configuration.

## Resource ownership and bounded continuation

At A45's earlier read-only `du`/`df` audit, approximately **309 MiB** was in this
session's workspace: **177 MiB** for the repository, **92 MiB** for the primary build and
about **40 MiB** of existing extracts, previews and private fixture/evidence
directories. About **57 GiB remained available**. These are rounded observations
at that audit time, preserved as history. A45 created only this handoff, its
short note and AGENTS changes.

A59's own read-only allocated-size audit observed about **320 MiB** total,
**181 MiB** for this repository and **93 MiB** for the primary build, with about
**56 GiB available**. The receipt retains exact byte observations and commands;
concurrent reports can change these rounded values. **No cleanup was needed or
performed.** No PDF, dependency, build or gallery copy was created for this audit.

| Protected resource | Ownership and rule |
| --- | --- |
| `/workspace/scratch/5b7d983ac078/build-native` | Product integrator's single primary build. Reuse it with exclusive coordination; preserve its configuration and evidence before any later owner-approved reproducible cleanup. |
| `/workspace/scratch/1bb6ee17ad7e` | Another session's workspace; A45's earlier observation was approximately 862 MiB total, SDL about 79 MiB and RtMidi about 2.2 MiB. A59 only reverified the borrowed tools/dependencies read-only. Its checkout, builds and evidence are not cleanup candidates for this session. |
| `/workspace/scratch/e3cacb90cc81/Hammond-B3-Organ` | Separate R4 checkout with its own index and unfinished work; A45's earlier size was approximately 189 MiB. [A56's dated observation](development/2026-11-15-product-continuation/reports/A56-phase-readiness.json) retains HEAD `fd2f6060b1f03b6d902ff0547441c07d6e74ba4f`, **151 staged and four untracked entries**, and later owner-local lifecycle/allocation/CLI results. A59 does not operate that checkout or its build. Preserve it; integration, publication and final acceptance of the overlay remain with that owner. The d8 hosted R4 pass qualifies only published inputs. |
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

1. **Finish actual acceptance and strict accounting.** Use the live checkpoint
   for remaining assigned owners and their delivered note hashes. A46 is already
   accepted; after all sixty real results and ten six-worker waves are accepted,
   root retains its strict output and removes `--allow-incomplete` from the
   product CI record step. Partial mode and historical checkers cannot close
   this session. Preserve A40/A41's eleven-frame admission, A42/A43 results,
   A49–A54's platform/document/UI reviews and each later substantive audit.
2. **Publish and qualify the final accepted inputs.** Root owns source freeze,
   shared status/next steps/log/README/manifest and publication. Preserve the
   180-test local receipt, inspect owned diffs and run only necessary affected
   or coherent gates if their inputs change. Fetch/inspect concurrent main, use
   a fresh expected head with no force, then fetch and verify exact commit/tree/
   parent and intended bytes. Earlier publication used connected Git Data
   because shell push lacked credentials; preserve the same guards if that
   route is required. Never reset unfinished files to synchronize a branch.
   Observe final-source hosted jobs, including the added Python modules and
   strict record step. The d8 all-thirteen pass cannot qualify those additions.
3. **Reconcile closure evidence after observing it.** Root updates current
   navigation, this handoff, checkpoint, status/next steps/log and final summary
   to the exact published source and retained strict/hosted results. An evidence-
   only follow-up commit identifies its previously tested source. Preserve all
   original failures, source-specific galleries and physical/product limits;
   do not mark the user's full 1:1 objective passed or waived to close this batch.
4. **Freeze the M6 same-Hz protocol before choosing a candidate.** Use
   [A56 work order 1](reviews/PRODUCT_PHASE_READINESS.md#work-order-1--freeze-the-next-m6-electrical-experiment),
   the [fixed v1 contract](LESLIE_CROSSOVER_CONTRACT.md), registry, independent
   reference/probe and [characterization](LESLIE_CROSSOVER_CHARACTERIZATION.md).
   Assign protocol and independent-review paths before editing. Freeze rates,
   band, loads, signed electrical boundaries, hold/reconstruction and independent
   grid; justify gain floors, magnitude/phase criteria above them, absolute
   complex V/V criteria below them and separate A/V admittance limits. No such
   same-Hz acceptance policy is supplied by the current finite-grid report.
   Then grade a separately identified candidate's processed/transient output,
   state/rate/partition/rollback and bounded costs. Preserve v1/documentary
   values and the dry Engine; physical/coupled/live integration gates stay open.
5. **Establish native close and callback retirement in parallel.** Use
   [A47-N1](reviews/PRODUCT_NATIVE_RECOVERY_REVIEW.md#a47-n1-native-close-failures-can-evade-quarantine-admission)
   and [A56 work order 2](reviews/PRODUCT_PHASE_READINESS.md#work-order-2--establish-the-native-retirement-boundary).
   Assign an isolated source-identified prepared-dependency fault harness before
   changes. Inject WinMM reset/stop/close and CoreMIDI disposal failures below
   RtMidi while a callback is parked before wrapper entry; first retain current
   behavior. Review checked close that observes failure before cleanup and keeps
   native handles, dependency storage, adapter context and inbox alive. Require
   poison/no-reopen/no-reset and ordinary leak-free teardown, then separate
   platform callback-retirement evidence even for successful closes. This is a
   source-proven observability gap and risk model, not an observed hardware
   failure or use-after-free. Synchronous fixtures do not establish OS lifetime.
6. **Continue the actual display, accessibility and acquisition gates.** Follow
   [A54's concrete native-display journey](reviews/PRODUCT_UI_ACCEPTANCE.md#precise-next-visual-gate)
   before further material work; declare absolute response targets and inspect
   small text, live state, focus, resize and release/shutdown at identified sizes
   and backends. Fix observed usability defects before a bounded deck/rim
   candidate, then recapture and independently compare the changed application
   and update README. Accessibility semantics, physical acquisition, DAW/device
   deadlines, rights and signed distribution retain distinct inputs/exits in
   [the complete next steps](NEXT_STEPS.md) and [A56 readiness](reviews/PRODUCT_PHASE_READINESS.md).

Every future agent follows the standing authorized workflow in AGENTS: recover
the full plan and current source, continue useful dependency-ready work, retain
actual evidence, update setup/status/next steps/log/notes and actual README UI
captures, then commit and publish accepted work with exact verification. A later
user instruction or repository protection may change that workflow; this handoff
adds no new permission requirement and claims no authority over unrelated work.
