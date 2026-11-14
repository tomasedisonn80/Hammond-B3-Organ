# Full-plan reconciliation after the standalone implementation

**The next integrated deliverable is a qualified native adapter around the
preserved nominal dry organ. The complete B-3/AO-28/Leslie product remains a
larger M0–M9 program.** This review identifies the software work that can proceed
now and the particular source, measurement and product evidence needed later.
It does not turn a completed development wave into a physical-fidelity pass.

Assignment **54/60**, wave **9**, actual worker
`/root/w09_a54_milestone_reconciliation`, inspected the repository on
13 November 2026. The [assignment note](../development/2026-11-13-next-phases/54-milestone-reconciliation.md)
records actual inspection commands and the separate evidence scopes.

## Exact assessment boundary

The principal published source is
`649b12c7d1faa7601fde1019e913347c65a6634a`, tree
`cf63327d857b02029e8c5c6f406cab3d3c6890d1`. The review separately considers the
accepted, then unpublished timing repair from assignment 47 and reader-progress
repair from assignment 50. Their maintained source hashes were independently
recomputed:

| Reviewed overlay | SHA-256 |
| --- | --- |
| `apps/standalone/main.cpp` | `d5728ab172e53cdb99e0f7d739ae2bc90344ff44f34140749812be1bb34fe26e` |
| `apps/standalone/native_tests/test_standalone_app.py` | `6f1841c3effcbf1d9996cd72269182a0b5b9aaa5e30403f4708ac2f6b93022ef` |
| `apps/standalone/native_tests/test_standalone_workflows.py` | `46f6e354f25082524c50034bc69a645322876bf2e9912932002b87b527864fc4` |
| `apps/standalone/tests/test_standalone_concurrency.cpp` | `a309882bb248add7d2dc1e6bbec679482d66d162c2d1eb54b4c455d5194355e3` |

The [timing review](STANDALONE_TIMING_REPAIR.md) records a fresh ASan/UBSan
3/3 focused gate, 38 methods and 210 native processes, with actual held-key
pixels and separate acknowledged held/released resize endpoints. The
[reader-progress review](STANDALONE_READER_PROGRESS.md) records normal Release,
one-CPU Release and coherent TSAN passes. It requires twelve exact initial/final
reader checkpoints while retaining the concurrent workloads. These are inherited
executed results, not tests rerun by assignment 54. They do not yet qualify the
whole subsequently integrated tree.

At published `649b12c`, the [platform follow-up](STANDALONE_PLATFORM_FOLLOWUP.md)
records 14/14 standalone suites and packaging on Linux, Windows and macOS,
successful VST3 jobs, 90/90 core suites on Windows/macOS and the SDK-free Linux
sanitizer configuration, and a retained 89/90 Linux Release result. The latter
reader-activity assertion motivated assignment 50. The earlier fully
instrumented native **92/94 failed gate** remains in its
[own report](STANDALONE_NATIVE_SANITIZERS.md); absence of a sanitizer diagnostic
does not erase failed acceptance assertions or establish a leak pass.

## What the entire atlas asks for

The [project plan](../PLAN.md) describes one inspectable C++ engine serving
offline rendering, VST3 and standalone use. Its physical target is an identified
vintage B-3/AO-28 and Leslie 122; Leslie 147 and other assemblies retain separate
profiles. The atlas's ten research waves organize eighty chapters. M0–M9 is its
implementation sequence. This session's ten groups of six actual assignments
organize development work. These are three distinct structures.

The unchanged source has 500 pages and 21,248,265 bytes; independently rehashed
SHA-256 is `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
This session's six fresh readers cover **1–84, 85–168, 169–252, 253–336,
337–420 and 421–500**, with selected actual page images. Their
[six records](../development/2026-11-13-next-phases/README.md) retain full text
coverage and visual limits. This assignment reviews those records; it does not
claim another independent full-PDF reading or verification of every external
source. Atlas page 2's absence of newly acquired target measurements remains
material to every physical claim. See the [source review](../research/ATLAS_REVIEW.md).

## M0–M9 evidence and unfinished exits

| Milestone | Engineering position at the named boundary | Remaining exit and dependency |
| --- | --- | --- |
| **M0: references and contracts** | Preserved source, explicit evidence classes/unknowns, model/profile identities, source maps, bounded authoring and durable agent rules exist. | Identify the actual organ, generator, AO-28 revision and cabinet, condition/modifications and permitted acquisitions. Documentary agreement and a source hash do not identify a specimen. [Capture protocol](../CAPTURE_PROTOCOL.md). |
| **M1: testable engine and transport** | Prepared SDK-free core, bounded events, offline renderer, atomic rejection and stopped lifecycle have executed evidence. Standalone adds a bounded main-to-audio Session, copied coherent observations, recovery and joined device teardown. | Qualify actual device deadlines, scheduling/underruns and lifecycle on named hardware. Current copied control restores do not authorize a new concurrent profile-replacement protocol. [Session contract](../STANDALONE_SESSION.md). |
| **M2: shared generator** | One continuously advancing bank of 91 nominal sine sources feeds both manuals and pedals. Documentary factory routing is independently compared; nominal profiles and original source identities remain intact. | Production gearing, mechanical/source phases, pickup waveforms/levels, filtering/load and leakage need admitted evidence and separately identified replacements. Preserve the nominal reference. [Factory comparison](../FACTORY_REFERENCE.md), [preservation audit](STANDALONE_CORE_PRESERVATION.md). |
| **M3: console behavior** | Four retained A/B banks, routing-only Cancel, nominal contact travel/percussion, 25 pedal owners, two named nominal pedal mixtures and scalar expression exist. The new catalog admits all 162 atlas chapel taps; explicit export writes ordinary B3CONTROLS3. | Fixed-key selection, simultaneous physical latches, loaded drawbar/transformer gains, switching bandwidth, loaded expression and the persistent pedal reactor are still separate work. Neither catalog nor exported bank implements a fixed-preset latch or its percussion interlock. [Remaining M3 contract](../M3_REMAINING_AND_SCANNER_GATE.md), [chapel catalog](../CHAPEL_PRESETS_CATALOG.md). |
| **M4: scanner** | Reconstructed graph/compiler, primary comparison, independent AC references, prepared 36-coordinate line, transient reference and continuing rotor exist. G3 discrete frequency/process and G4 rotor evidence are retained. | **G5 same-hertz accuracy fails at every investigated rate, including 1,536,000 Hz.** An alternative realization or explicitly justified policy must satisfy the frozen gate before audible integration; converged transients/sidebands and real interpolation/filter/latency evidence remain separate. Specimen loading and captures remain unknown. [Frequency qualification](../SCANNER_AC_PARITY.md), [handoff](../SCANNER_HANDOFF.md). |
| **M5: organ electronics** | The current Engine remains normalized nominal dry mixing; the supplied component/valve descriptions are not a connected AO-28 netlist. | Choose one drawing revision, independently trace complete terminals/nets, resolve active values and transformer/source/load/feedback boundaries, then operating-point and loaded linear references before nonlinear/alias qualification. Validate the complete dry G-G organ before cabinet fitting. [Electronics reading](../development/2026-11-13-next-phases/03-atlas-electronics.md). |
| **M6: Leslie electronics** | No connected 122 amplifier/transformer/crossover/driver-load model is inserted into the instrument. | Keep 122 differential and 147 single-ended variants distinct. Admit the exact floating treble-return topology, signed ports and real driver loading; qualify linear polarity/admittance and then coupled nonlinear behavior. Nominal resistor loads can test mathematics but cannot stand for measured drivers. [Leslie reading](../development/2026-11-13-next-phases/04-atlas-leslie.md). |
| **M7: rotary acoustics** | The independent rotary track has a strict proposed profile, high-precision reference and native motion foundation. It does not change dry Engine output. | Complete its independently qualified motion, historical emission-time paths, causal interpolation and transactional renderer under the frozen R1–R6 contract. Horn/drum remain separate trajectories shared across receivers. Actual geometry/directivity/cabinet/room captures and upstream M5/M6 boundaries precede calibrated integration. [Rotary scope](../ROTARY_SCOPE.md). |
| **M8: calibration** | `649b12c` contains capture metadata/byte tools and the calibration JSON/session foundations. A later independent published implementation is described below. | Raw acquired masters, calibrated clocks/levels/loads, whole-group ancestry, frozen criteria and untouched held-out data are still absent physical prerequisites. A synthetic corpus or successful metric cannot establish acquisition, identifiability, a physical fit or listening equivalence. [Calibration scope](../CALIBRATION_SCOPE.md). |
| **M9: product and release** | Actual VST3 and standalone adapters expose the same nominal core. The standalone has keyboard/pointer controls, resizable rendering, Audio/Help, explicit Save/Load, scripted workflows, installation and hosted dummy-driver evidence. | External MIDI transport, native semantic accessibility, actual desktop/device/DAW workflows, high-DPI capture, deadline/latency evidence, clean-target runtimes and signed release remain separate. Keyboard-operable canvas and matching L/R dry channels do not establish screen-reader support or Leslie stereo acoustics. [Standalone handoff](../STANDALONE_HANDOFF.md), [UI contract](../STANDALONE_UI.md). |

The [independent compatibility audit](STANDALONE_CORE_PRESERVATION.md) compares
baseline `ba0d9c9` with `649b12c`: 196 protected existing files, all 45 parameter
records and generated inputs match; both revisions passed eleven selected suites.
Forty actual renders over 3,241,200 frames retained exact WAV/PCM and applicable
metrics, and the renderer binaries themselves match on the tested toolchain.
This is strong nominal compatibility evidence. It is not a physical tone match
or automatic qualification of later changes to those protected inputs.

### Separately observed calibration integration

During this review the independent calibration track published
`779fb6e13b8f60236cad4aedb9999ba16198f920`, tree
`f9baccbb54f51063b01a0859d2c10cdadfbd238b`. Assignment 54 inspected that immutable
commit's [handoff](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/779fb6e13b8f60236cad4aedb9999ba16198f920/docs/CALIBRATION_HANDOFF.md)
and [wave-4 integration report](https://github.com/tomasedisonn80/Hammond-B3-Organ/blob/779fb6e13b8f60236cad4aedb9999ba16198f920/docs/reviews/CALIBRATION_WAVE4_INTEGRATION.md)
using local Git objects. They document audio decoding/full-stream admission,
corpus lineage/split auditing, array metrics and fixed policy evaluation through
24 accepted calibration assignments. The file-job composition and readiness
work remain later tasks at that checkpoint.

The report retains 11/11 focused suites at its earlier frozen source and
**96/96 SDK-free suites** in 177.43 seconds at the combined local commit
`45f875d80b6cc78c89ecc8b665bf2aedf058a97c`, tree
`2dcfc0e8071cdc30d75f8fb9be340826296fcbaf`. Those are the calibration integrator's
executed results. This worker did not rerun them, and neither gate covers the
accepted 47/50 standalone overlays or SDL/VST3 execution. Root owns the next
coherent integration and publication; the M8 physical limits above remain open.

## Prioritized continuation with concrete exits

### 1. Close the present integrated software checkpoint

Root should combine accepted 47/50 changes, the current independently owned
remote work and any subsequently accepted build/install repairs in a new frozen
source. Run the complete registered gate with actual inputs built, then inspect
the exact-source hosted core/standalone/VST3 jobs and actual package bytes.
Retain both earlier failures and their source identities. Check the final
manifest only after all sixty real results are accepted. Final publication
requires expected-head protection and fetched tree equality, not merely an
API success or workflow dispatch. This work belongs to the integrator and final
qualification assignments, not an uncoordinated second production branch.

Include the concrete SDL notice correction identified below. The installed
layout can remain nine files by retaining applicable additional notices inside
the already installed root notice file. Verify the resulting notice bytes in
the staged and downloaded packages. A current candidate needs its own result;
the older package audits remain historical.

### 2. Advance independent product interfaces against the unchanged core

Two useful M9 tasks can begin without guessing circuit measurements:

- **External MIDI adapter:** freeze the exact backend/version/notice and event
  timestamp/late-event policy before implementation. Serialize producers into
  the declared Session ownership; a hardware callback cannot become a second
  writer to the existing SPSC queue. Reserve independent note ownership so UI
  focus loss releases only UI notes. Qualify parsing/translation, velocity-zero
  release, duplicate/channel ownership, disconnect, overflow and device
  restart with independent event streams, then actual named MIDI hardware.
  Existing files under `apps/standalone/` and the
  [performance-input contract](../PERFORMANCE_INPUT.md) are the starting boundary.
- **Native accessibility adapter:** expose semantic names, roles, values,
  selection/focus and bounded actions for the existing controls, without live
  Engine access. Choose one supported platform bridge and retain its
  dependency contract. Verify actual screen-reader navigation, editing,
  status/error announcement, keyboard-only operation and scale changes. The
  present ASCII glyph atlas and keyboard navigation are useful UI work but do
  not satisfy that semantic bridge or localization. Start from
  [UI ownership](../STANDALONE_UI.md) and [font limits](../STANDALONE_FONTS.md).

Neither task's synthetic event tests establish device latency, physical MIDI
timing or assistive-technology success. Name the backend, hardware/OS and actual
user-agent versions in their later evidence.

### 3. Complete the next M3 behavior contract without replacing nominal physics

The data admission/export work is already implemented. The next bounded model
slice is a typed **exclusive fixed-registration selector**, with all four A/B
banks retained, Cancel separate, existing note owners unchanged and explicit
upper-B percussion eligibility/history. Coordinate ownership of Engine,
ControlSnapshot, parameter registry, HostTimeline, StateExchange, native
wrappers and their fixed-size structures before changing them. Specify
append-only IDs and control-state migration before adding saved fields; preserve
the meaning of every existing ID and v1/v2/v3 reader.

Use the existing eighteen catalog rows as documentary inputs. Independently
acquire and compare the named factory Table IV before upgrading its primary-source
status. For engineering acceptance, compare each exclusive registration with
an independently initialized equivalent bank at the same continuing source state;
exercise held chords, inactive-bank edits, upper B→fixed→B transitions, partly
recovered percussion, Cancel, zero-frame changes, same-offset ordering,
partition invariance and failed-call rollback. Loading a control snapshot must
not restore notes or reset source phases. Simultaneous eleven-contact physical
latches, branch impedances and loaded gains need a separate network/measurement
contract; summing independent preset programs is not that contract.

### 4. Continue the scanner numerical gate under its existing owner

Do not restart graph admission or erase the known G5 failure. Use
[scanner-numerics-v1](../SCANNER_NUMERICAL_CONTRACT.md), exact graph/profile
identities and complete failed-bin reports to evaluate a separately identified
alternative realization or justified audible policy. Freeze any new method's
contract before grading it; a looser retrospective threshold is not closure.
Retain G3 process parity, converged nonzero-state transients, one continuous
rotor, signed common return once and all U/L/P/Q routing obligations. Only then
propose Engine integration with exact disabled-path legacy arithmetic and a
coherent migration/rebuild of all consumers. Physical scanner loading and
captures remain a distinct exit. [Handoff](../SCANNER_HANDOFF.md).

### 5. Admit connected electronics and continue independent research

M5 can begin with a revision-specific AO-28 terminal/net trace and independent
second reading, explicit unresolved values, source/load/transformer/feedback
contracts and strict graph admission. A parts roster or functional diagram is
insufficient. M6 can independently admit a named 122 divider/load reference,
retaining its floating treble return and a separately labeled ideal-load
fixture; 147 must keep its own boundary. Start numerical solving only for
resolved admitted graphs and values. Connected dry-organ qualification precedes
cabinet fitting. The [electronics](../development/2026-11-13-next-phases/03-atlas-electronics.md)
and [Leslie](../development/2026-11-13-next-phases/04-atlas-leslie.md) readings name
the exact source pages and missing inputs.

Meanwhile the existing rotary owner can finish its independent R1–R6 pipeline,
and the calibration owner can complete file-job/readiness composition under the
new handoff. Do not duplicate their active modules or treat a source inventory,
metric threshold or ideal acoustic fixture as acquired hardware evidence.
Actual captures follow the [acquisition protocol](../CAPTURE_PROTOCOL.md), with
whole related takes/derivatives kept together and held-out criteria fixed before
fitting. No acquisition or recording was performed by this review.

## Dependencies, notices and actual product limits

SDL is explicitly pinned to **2.32.10**, commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`, with read-only source verification.
The primary Zlib notice is 884 bytes, SHA-256
`97f35b302b361680ec1e891e95d2d52097bb95abff361434916d99dc1305f127`.
The two DejaVu 2.37 TTFs and their complete 2,345-byte notice were independently
rehash-checked against the retained source manifest. Their generated glyphs
require no runtime Pillow, FreeType, SDL_ttf or source font files. This review
did not rerun rasterization. [Dependency](../STANDALONE_DEPENDENCY.md),
[fonts](../STANDALONE_FONTS.md).

### Concrete secondary-notice finding

The inspected `649b12c` root notice is 10,792 bytes, SHA-256
`ff72e873f84c98ce843bdcbe527ce4a5de9647aa67d5a703165093c04b9ab060`.
It and the nine-file installed payload lack the pinned SDL yuv2rgb notice and
an identified HIDAPI option. The dependency guide had already flagged these
secondary-source notices. This is a specific correction for the final package,
not a claim of a complete legal or transitive-dependency audit.

Actual read-only inspection of assignment 49's installed Linux ELF, SHA-256
`f967f5fdab79e25d366d011b1f5e1fe719a8597f87265aa2d139a5c21079deed`, found thirteen
`yuv420` symbols, including `rgb24_yuv420_std` and `yuv420_argb_sseu`. Its actual
SDL build contains the corresponding standard/SSE objects. The pinned
`src/video/yuv2rgb/LICENSE` is **1,480 bytes**, SHA-256
`f7d74004cc75778cae46c5f0139f244d67c07ef64cf51937e8272352197dcb18`; its binary
distribution paragraph requires the stated notice, conditions and disclaimer
in accompanying materials. Root accepted the finding and preserved the complete
text in the repository notice; subsequent payload verification remains a final
integration responsibility.

The ELF also contains SDL HIDAPI wrappers and joystick-driver symbols; those
do not prove that every platform-specific HIDAPI backend is linked. Upstream
`src/hidapi/LICENSE.txt` names three alternatives. The inspected BSD option is
**1,534 bytes**, SHA-256
`30eb1bef29b46f8ba7ab8b416035dbd93cb034a45481dd97815b944284582cd2`.
Root recorded the BSD option for any included HIDAPI code, with its
complete text and source identity; this worker does not select a project-wide
license or infer the compiled set of an uninspected platform.

At root's request, a bounded libm check inspected all **twenty compiled fallback
objects** and their twenty-one defined text symbols. None of those symbols
occurs in this installed ELF. Its `SDL_sin_REAL` jumps to system `sin@plt`.
The compiled fallback sources and `math_private.h` retain the 1993 Sun/SunPro
permission notice, but this Linux executable does not demonstrate linked
fallback code. Other configurations need their own inclusion check; retaining
that short notice for configurations using the fallback must preserve this
distinction. The complete observed symbol comparison is retained privately.

**Observed repair, separate from the published baseline:** at local commit
`fa6df9d04916da8e23938cc3e85f524e3707e7d8`, tree
`19c763503f67e1f054d2d27b6ec3d8fca2e36474`, this worker reread the root
[notice additions](../../THIRD_PARTY_NOTICES.md): complete yuv2rgb, selected
HIDAPI BSD and Sun fallback texts, exact source/hash citations and bounded
inclusion language are present. This closes the identified source-notice
omissions. It does not claim new staged/downloaded package verification or
full qualification/publication of that local commit.

No project-root LICENSE exists in the reviewed published tree. The supplied
atlas and its embedded material, future physical recordings and intended
branding retain the unresolved decisions in the
[rights inventory](../DEPENDENCIES_AND_RIGHTS.md) and
[source record](../research/RIGHTS_AND_SOURCES.md). The VST3 Windows SDK-default
icon has separate recorded provenance and branding conditions. This review
grants no new permission and does not change that asset. Actual signed
installers, clean-machine runtime availability, update/uninstall behavior and
physical device/DAW/accessibility qualification remain future product evidence.

## Resume commands and required handoff

Run from a coherent repository checkout. These are recipes for the next owner;
assignment 54 did not configure, build or execute these product gates.

```sh
git status --short
git rev-parse HEAD HEAD^{tree}
git fetch origin main
git log --oneline -8 origin/main
python3 tools/check_standalone_session.py --repo . --json
python3 tools/check_repository.py --root . --json
```

For a fresh optional native build, first verify the explicitly acquired pinned
SDL checkout, select a new build directory and use the documented actual inputs:

```sh
python3 tools/acquire_sdl2.py --verify-existing ../SDL2
cmake -S . -B build-final -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON \
  -DHAMMOND_BUILD_STANDALONE=ON -DHAMMOND_SDL2_ROOT=/absolute/verified/SDL2
cmake --build build-final --config Release --parallel 2
cmake --build build-final --target hammond_standalone_test_inputs --config Release --parallel 2
ctest --test-dir build-final -C Release --output-on-failure --no-tests=error
```

The absolute SDL path is a placeholder to replace with the verified checkout.
Discover actual registered tests and build configuration; do not reuse a stale
suite count. A multi-configuration generator needs the selected configuration
in executable paths and install commands. Use
[STANDALONE_HANDOFF.md](../STANDALONE_HANDOFF.md) for replay, explicit chapel
export, benchmark and installation recipes. The new calibration handoff owns
its tools; its planned corpus deliberately reports inconclusive rather than
pretending acquired audio exists.

Every successor reads [AGENTS.md](../../AGENTS.md), takes explicit owned paths,
preserves concurrent tracks and unknowns, records exact source/data/toolchain
identity and actual failures/results, updates status/next steps/log/affected
contracts, and commits/pushes completed authorized work without force. Do not
request `--expected-complete 60` until sixty actual results are accepted. A
future session's new work gets its own ledger; this session's workers and
historical successes are never recounted.

## Documentation corrections identified for the integrator

At inspection, the pedal-era release assessment and acceptance matrix still
presented scanner/compiler/rotary/standalone absence as current. The original
M3/scanner contract still introduced graph admission as the next task, and some
README/lower STATUS navigation still called the completed pedal session
current. The dependency inventory had a later SDL/font update but earlier
sentences still said no GUI/audio library was selected. Root was informed of
these exact contradictions. By the local repair checkpoint above, this worker
observed RELEASE_READINESS's current pointer and explicit preserved historical
section. Root reports corresponding dependency/M3 corrections and owns the
remaining matrix/navigation updates. Preserve their original named test results
while making the current source scope unambiguous. This report is a dated
reconciliation, not a replacement for the next source-qualified status and final
integration.
